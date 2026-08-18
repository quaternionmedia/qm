"""Tests for the published-docs audit.

Each case builds a tiny site in a temp directory. The audit's value is that the
rebuild dimension fails the run and the accuracy dimensions report without
failing it by default -- a link typo should not block a merge, and a site that
cannot build should.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from docs_audit import audit  # noqa: E402

TOOL = CI_DIR / "docs_audit.py"
GOOD_CONFIG = '[project]\nname = "site"\n'


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def site(tmp_path: Path, page: str = "# Home\n", config: str = GOOD_CONFIG) -> Path:
    write(tmp_path / "zensical.toml", config)
    write(tmp_path / "docs" / "index.md", page)
    (tmp_path / "handbook").mkdir(exist_ok=True)
    return tmp_path


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


# --- rebuild ---------------------------------------------------------------


def test_a_config_only_one_parser_accepts_fails_the_run(tmp_path: Path):
    """zensical's own parser accepts this file today and nothing else does."""
    site(tmp_path, config='[project]\nname = "site"\n  {bad = 1}\n')
    result = run(tmp_path)
    assert result.returncode == 1
    assert "not valid TOML" in result.stdout


def test_a_missing_config_fails_the_run(tmp_path: Path):
    site(tmp_path)
    (tmp_path / "zensical.toml").unlink()
    assert run(tmp_path).returncode == 1


def test_a_valid_config_passes(tmp_path: Path):
    site(tmp_path)
    assert run(tmp_path).returncode == 0


def test_no_docs_directory_is_a_rebuild_failure(tmp_path: Path):
    write(tmp_path / "zensical.toml", GOOD_CONFIG)
    result = run(tmp_path)
    assert result.returncode == 1
    assert "nothing to publish" in result.stdout


def test_an_empty_docs_directory_is_a_failure_not_a_clean_site(tmp_path: Path):
    """An empty site publishes green and says nothing, which is the worst pass."""
    write(tmp_path / "zensical.toml", GOOD_CONFIG)
    (tmp_path / "docs").mkdir()
    result = run(tmp_path)
    assert result.returncode == 1
    assert "publish clean" in result.stdout


# --- accuracy: links -------------------------------------------------------


def test_a_dangling_link_is_reported(tmp_path: Path):
    site(tmp_path, page="See [the thing](missing.md).\n")
    assert audit(tmp_path)["accuracy: links"]


def test_a_link_to_a_sibling_page_resolves(tmp_path: Path):
    root = site(tmp_path, page="See [other](other.md).\n")
    write(root / "docs" / "other.md", "# Other\n")
    assert audit(root)["accuracy: links"] == []


def test_a_link_to_a_corpus_file_resolves(tmp_path: Path):
    root = site(tmp_path, page="See [agents](AGENTS.md).\n")
    write(root / "AGENTS.md", "# Agents\n")
    assert audit(root)["accuracy: links"] == []


def test_external_links_and_anchors_are_not_checked(tmp_path: Path):
    root = site(tmp_path, page="[a](https://x.test) [b](#section) [c](mailto:a@b.test)\n")
    assert audit(root)["accuracy: links"] == []


def test_an_anchor_on_a_real_page_still_resolves(tmp_path: Path):
    root = site(tmp_path, page="See [other](other.md#part).\n")
    write(root / "docs" / "other.md", "# Other\n")
    assert audit(root)["accuracy: links"] == []


# --- accuracy: citations ---------------------------------------------------


def test_a_named_repo_path_that_does_not_exist_is_reported(tmp_path: Path):
    site(tmp_path, page="Run `ci/nonexistent.py`.\n")
    assert audit(tmp_path)["accuracy: citations"]


def test_a_named_repo_path_that_exists_is_clean(tmp_path: Path):
    root = site(tmp_path, page="Read `AGENTS.md`.\n")
    write(root / "AGENTS.md", "# Agents\n")
    assert audit(root)["accuracy: citations"] == []


# --- accuracy: duplicates --------------------------------------------------


def test_a_docs_page_shadowing_a_corpus_document_is_reported(tmp_path: Path):
    """The real instance: docs/ref/glossary.md against handbook/glossary.md."""
    root = site(tmp_path)
    write(root / "handbook" / "glossary.md", "# Glossary\n")
    write(root / "docs" / "ref" / "glossary.md", "# Glossary\n")
    assert audit(root)["accuracy: duplicates"]


def test_citing_the_corpus_twin_clears_it(tmp_path: Path):
    """Citing it makes the page a view of something rather than a rival."""
    root = site(tmp_path)
    write(root / "handbook" / "glossary.md", "# Glossary\n")
    write(root / "docs" / "ref" / "glossary.md",
          "# Glossary\n\nRendered from `handbook/glossary.md`.\n")
    assert audit(root)["accuracy: duplicates"] == []


def test_index_pages_are_not_duplicates(tmp_path: Path):
    """Every directory has one; a shared name there means nothing."""
    root = site(tmp_path)
    write(root / "handbook" / "index.md", "# H\n")
    write(root / "docs" / "ref" / "index.md", "# R\n")
    assert audit(root)["accuracy: duplicates"] == []


# --- how it exits ----------------------------------------------------------


def test_accuracy_alone_does_not_fail_the_run(tmp_path: Path):
    """A link typo must not block a merge; a broken build must."""
    site(tmp_path, page="See [gone](missing.md).\n")
    result = run(tmp_path)
    assert result.returncode == 0
    assert "accuracy: links: 1 finding" in result.stdout


def test_strict_fails_on_accuracy_too(tmp_path: Path):
    site(tmp_path, page="See [gone](missing.md).\n")
    assert run(tmp_path, "--strict").returncode == 1


def test_it_says_the_generator_was_not_run(tmp_path: Path):
    """A green audit must not read as a green build."""
    site(tmp_path)
    assert "generator is not run here" in run(tmp_path).stdout
