"""Tests for the draft banner.

The banner's only job is that a reader cannot mistake a draft build for the
published site. So the tests are about coverage and visibility: every page gets
one, an empty build fails rather than uploading clean, and re-running does not
stack banners.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from docs_draft_banner import MARKER, inject  # noqa: E402

TOOL = CI_DIR / "docs_draft_banner.py"
PAGE = "<!doctype html><html><head><title>t</title></head><body><h1>Hi</h1></body></html>"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run(site: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), str(site), "--label", "PR #1", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


# --- placement --------------------------------------------------------------


def test_the_banner_lands_inside_body():
    out = inject(PAGE, "PR #1", "u")
    assert out.index(MARKER) > out.lower().index("<body")
    assert out.index(MARKER) < out.index("<h1>")


def test_a_page_with_no_body_still_gets_one():
    """A fragment or an odd template must not publish unmarked."""
    assert MARKER in inject("<h1>Hi</h1>", "PR #1", "u")


def test_a_body_tag_with_attributes_is_handled():
    out = inject('<html><body class="md" data-x="1"><p>x</p></body></html>', "PR #1", "u")
    assert MARKER in out
    assert out.index(MARKER) < out.index("<p>")


def test_running_twice_does_not_stack_banners():
    once = inject(PAGE, "PR #1", "u")
    assert inject(once, "PR #1", "u").count(MARKER) == 1


def test_the_label_and_url_reach_the_page():
    out = inject(PAGE, "PR #55 docs", "https://example.test/pr")
    assert "PR #55 docs" in out
    assert "https://example.test/pr" in out


def test_it_says_the_draft_asserts_nothing():
    """The banner's whole point: a reader must not take it for the real site."""
    out = inject(PAGE, "PR #1", "u").upper()
    assert "DRAFT" in out
    assert "ASSERTS NOTHING" in out


# --- coverage ---------------------------------------------------------------


def test_every_page_in_the_build_is_marked(tmp_path: Path):
    for name in ("index.html", "a/b.html", "deep/deeper/c.html"):
        write(tmp_path / name, PAGE)
    assert run(tmp_path).returncode == 0
    for page in tmp_path.rglob("*.html"):
        assert MARKER in page.read_text(encoding="utf-8")


def test_an_empty_build_fails_rather_than_uploading_clean(tmp_path: Path):
    """A site with no pages uploads green and says nothing."""
    result = run(tmp_path)
    assert result.returncode == 1
    assert "nothing was built" in result.stderr


def test_a_missing_directory_fails(tmp_path: Path):
    result = run(tmp_path / "nope")
    assert result.returncode == 1
    assert "not a directory" in result.stderr


def test_non_html_files_are_left_alone(tmp_path: Path):
    write(tmp_path / "index.html", PAGE)
    write(tmp_path / "style.css", "body{}")
    run(tmp_path)
    assert (tmp_path / "style.css").read_text(encoding="utf-8") == "body{}"
