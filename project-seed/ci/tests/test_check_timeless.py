"""Tests for the timeless-text check.

Each case commits into a small repository, because the check reads tracked
files and, with `--base`, the lines a branch adds.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from check_timeless import findings, main, scan  # noqa: E402


def git(*args: str, cwd: Path) -> None:
    done = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 0, f"git {' '.join(args)}\n{done.stdout}{done.stderr}"


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    where = tmp_path / "repo"
    where.mkdir()
    git("init", "-q", "-b", "main", cwd=where)
    git("config", "user.email", "t@example.com", cwd=where)
    git("config", "user.name", "T", cwd=where)
    return where


def commit(repo: Path, name: str, body: str) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    git("add", "-A", cwd=repo)
    git("-c", "commit.gpgsign=false", "commit", "-q", "-m", name, cwd=repo)


def kinds(path: str, text: str) -> list[str]:
    found, _ = scan(path, text)
    return [item.kind for item in found]


# --- what is refused -------------------------------------------------------------


def test_a_phrase_in_capitals_in_a_docstring_is_a_shout():
    """Mutation: return no matches from `SHOUT` and this fails."""
    text = '"""Saved designs.\n\n**THE TABLE EXISTED AND NOTHING SERVED IT.**\n"""\n'
    assert "shout" in kinds("designs.py", text)


def test_a_section_label_in_capitals_is_a_shout():
    assert kinds("tool.py", '"""What it does.\n\nWHAT THIS CANNOT DO. Delete.\n"""\n') == ["shout"]


def test_a_narrating_phrase_in_a_comment_is_narrative():
    """Mutation: empty `NARRATIVE` and this fails."""
    assert kinds("tool.py", "x = 1  # the check that caught it\n") == ["narrative"]


def test_narrative_in_markdown_prose_is_found():
    assert kinds("guide.md", "This page used to be longer.\n") == ["narrative"]


def test_a_comment_in_configuration_is_prose():
    assert kinds("ci.yml", "# Until now nothing ran this.\nrun: echo\n") == ["narrative"]


# --- what is left alone ---------------------------------------------------------


def test_capitals_in_code_are_not_prose():
    """A SQL string is code. Mutation: read every line of a Python file and
    this fails."""
    text = 'QUERY = "CREATE TABLE IF NOT EXISTS rows"\n'
    assert kinds("store.py", text) == []


def test_fenced_blocks_and_code_spans_are_not_prose():
    text = "Quote `WHAT THIS CANNOT DO` as an example.\n\n```\nUSED TO BE LOUD\n```\n"
    assert kinds("guide.md", text) == []


def test_a_code_span_in_a_docstring_is_not_prose():
    """Quoting a phrase is not using it. Mutation: drop the code-span strip in
    `scan` and this fails."""
    assert kinds("tool.py", '"""Refuses phrases such as `used to be`."""\n') == []


def test_a_hyphenated_name_is_one_word():
    assert kinds("licence.md", "Published under CC-BY-SA as YYYY-MM-DD dated.\n") == []


def test_an_acronym_pair_is_not_a_run():
    assert kinds("api.md", "Send a GET to the API.\n") == []


def test_an_allowance_on_the_line_or_above_is_counted_not_found():
    """Mutation: ignore `ALLOW` and both lines are found."""
    text = ("Send HTTP GET API calls.  <!-- timeless: allow three acronyms -->\n"
            "<!-- timeless: allow the protocol's own words -->\n"
            "Answer with HTTP GET API.\n")
    found, allowed = scan("api.md", text)
    assert found == [] and allowed == 2


def test_an_allowance_without_a_reason_counts_for_nothing():
    """Mutation: accept a bare `timeless: allow` and both lines pass."""
    found, allowed = scan("api.md", "THE ONE THAT MATTERS <!-- timeless: allow -->\n"
                                    "WHAT THIS CANNOT DO  # timeless: allow\n")
    assert len(found) == 2 and allowed == 0


def test_exempt_paths_are_not_read(repo: Path):
    commit(repo, "perspectives/2026-01-01-a-day.md", "It turned out the gate used to be off.\n")
    commit(repo, "protocols/runs/2026-01-01-run.md", "That afternoon it was found to work.\n")
    found, _ = findings(repo)
    assert found == []


# --- the gate reads only what a branch adds -------------------------------------


def test_a_branch_is_checked_on_the_lines_it_adds(repo: Path):
    """Text already on the base is the sweep's to fix; the branch is held to
    its own lines. Mutation: scan whole files under `--base` and the old line
    is found."""
    commit(repo, "tool.py", '"""Old.\n\nWHAT THIS CANNOT DO.\n"""\n')
    git("switch", "-q", "-c", "work", cwd=repo)
    commit(repo, "tool.py", '"""Old.\n\nWHAT THIS CANNOT DO.\n"""\n\n\ndef f():\n    """Plain."""\n')
    found, _ = findings(repo, base="main")
    assert found == []

    commit(repo, "other.py", "# nobody had noticed this\n")
    found, _ = findings(repo, base="main")
    assert [(item.path, item.kind) for item in found] == [("other.py", "narrative")]


def test_uncommitted_and_untracked_lines_count_as_added(repo: Path):
    """A local run before the commit reads what the commit will hold.
    Mutation: diff against `HEAD` instead of the working tree, or skip
    untracked files, and a branch with nothing committed reads as clean."""
    commit(repo, "tool.py", '"""Plain."""\n')
    git("switch", "-q", "-c", "work", cwd=repo)
    (repo / "tool.py").write_text('"""Plain."""\n# it turned out fine\n', encoding="utf-8")
    (repo / "new.md").write_text("WHAT THIS CANNOT DO is listed.\n", encoding="utf-8")
    found, _ = findings(repo, base="main")
    assert sorted((item.path, item.kind) for item in found) == [
        ("new.md", "shout"), ("tool.py", "narrative")]


def test_exit_status_says_found_clean_or_unreadable(repo: Path, capsys):
    commit(repo, "clean.md", "Saved designs are listed by project.\n")
    assert main(["--all", "--root", str(repo)]) == 0
    commit(repo, "loud.md", "THE ONE THAT MATTERS is this.\n")
    assert main(["--all", "--root", str(repo)]) == 1
    assert main(["--base", "no-such-ref", "--root", str(repo)]) == 2
    out = capsys.readouterr().out
    assert "loud.md:1: shout: THE ONE THAT MATTERS" in out
