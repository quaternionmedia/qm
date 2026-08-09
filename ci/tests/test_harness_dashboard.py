"""The harness dashboard's red paths, and the collector's unknown handling.

A dashboard fails differently from a check: it does not report the wrong
answer, it draws a reassuring picture of one. So every test below is a state
that must NOT render like a clean organisation — an absent document, a
repository nobody could read, a violation, a phase nobody answered.

The collector is tested for the same property from the other side: when it
cannot establish a fact it must write `unknown` with a reason, because the
renderer can only be honest about what the document admits.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))
import harness_dashboard as hd  # noqa: E402
import harness_status as hs  # noqa: E402


def document(**overrides) -> dict:
    base = {
        "schema": 1,
        "generated_at": "2026-08-09T21:00:00Z",
        "generator": {
            "tool": "ci/harness_status.py",
            "org": "example",
            "rule": "one open pull request per repository, per contributor",
            "rule_source": "handbook/async-contract.md",
            "corpus_exemption": ["project/*"],
            "layers": ["slots", "local"],
            "local_layer_scope": "one machine, one set of clones",
        },
        "totals": {
            "repositories": 3,
            "slots_measured": 2,
            "slots_unknown": 1,
            "compliant": 1,
            "over_limit": 1,
        },
        "repositories": [
            {
                "name": "clean-repo",
                "slug": "example/clean-repo",
                "role": "project",
                "phase": "v0.0.1",
                "slots": {"open_prs": [], "violations": [], "compliant": True},
                "local": {"branch": "main", "dirty": 0, "upstream": "origin/main", "ahead": 0},
            },
            {
                "name": "busy-repo",
                "slug": "example/busy-repo",
                "role": "project",
                "phase": "unknown",
                "note": "nobody has placed this on the ladder",
                "slots": {
                    "open_prs": [
                        {"number": 8, "author": "ada", "bot": False, "base": "main",
                         "draft": False, "title": "One"},
                        {"number": 9, "author": "ada", "bot": False, "base": "main",
                         "draft": True, "title": "Two"},
                    ],
                    "violations": [{"author": "ada", "base": "", "numbers": [8, 9]}],
                    "compliant": False,
                },
                "local": {"branch": "wip", "dirty": 3, "upstream": None, "ahead": None},
            },
            {
                "name": "private-repo",
                "slug": "example/private-repo",
                "role": "project",
                "phase": "unknown",
                "slots": {"unknown": "gh api repos/example/private-repo: HTTP 404"},
                "local": {"unknown": "not found on this machine"},
            },
        ],
    }
    base.update(overrides)
    return base


DOC = document()


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CI_DIR / "harness_dashboard.py"), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def row_for(page: str, name: str) -> str:
    match = re.search(rf'<tr[^>]*>\s*<th scope="row">{name}.*?</tr>', page, re.S)
    assert match, f"no row for {name}"
    return match.group(0)


# --- the renderer refuses to invent a clean page ---------------------------


def test_an_absent_document_is_a_failure_not_an_empty_page(tmp_path: Path) -> None:
    result = run(str(tmp_path / "nothing.json"))
    assert result.returncode != 0
    assert "no document" in result.stderr


def test_a_file_that_is_not_a_status_document_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "other.json"
    path.write_text(json.dumps({"hello": "world"}), encoding="utf-8")
    result = run(str(path))
    assert result.returncode != 0
    assert "not a harness status document" in result.stderr


def test_an_unreadable_repository_renders_as_unknown_not_as_ok() -> None:
    """The single failure mode a governance dashboard has."""
    row = row_for(hd.render(DOC), "private-repo")
    assert "s-unknown" in row
    assert "unknown" in row
    assert "p-ok" not in row


def test_the_reason_a_repository_is_unknown_survives_into_the_page() -> None:
    """Both places, and the row is the one that matters.

    Asserting only that the reason is somewhere on the page passes against a
    renderer that dropped it from the cell, because the section below repeats
    it — and the cell is where a reader hovering the word `unknown` looks.
    """
    page = hd.render(DOC)
    assert 'title="gh api repos/example/private-repo: HTTP 404"' in row_for(
        page, "private-repo"
    )
    section = page.split("What this page could not read")[1]
    assert "HTTP 404" in section


def test_a_violation_is_distinguished_in_form_and_not_only_in_words() -> None:
    """Colour alone is not a signal; the row carries a class either way."""
    page = hd.render(DOC)
    assert 'class="over"' in row_for(page, "busy-repo")
    assert 'class="over"' not in row_for(page, "clean-repo")


def test_the_pull_requests_that_hold_the_slots_are_named() -> None:
    """A count without numbers cannot be acted on."""
    page = hd.render(DOC)
    assert "#8" in page and "#9" in page
    assert "ada" in page


def test_a_compliant_repository_is_not_described_as_over() -> None:
    row = row_for(hd.render(DOC), "clean-repo")
    assert "p-ok" in row
    assert "over limit" not in row


def test_an_unanswered_phase_is_carried_into_the_question_list() -> None:
    page = hd.render(DOC)
    assert "Phases nobody has answered" in page
    assert "busy-repo" in page.split("Phases nobody has answered")[1]


def test_a_repository_absent_from_this_machine_is_not_asked_about_its_phase() -> None:
    """Its phase is unknown, but nobody can answer it from a clone they lack."""
    section = hd.render(DOC).split("Phases nobody has answered")[1].split("<h2>")[0]
    assert "private-repo" not in section


def test_unpushed_and_dirty_local_state_is_shown_as_needing_attention() -> None:
    row = row_for(hd.render(DOC), "busy-repo")
    assert "3 uncommitted" in row
    assert "no upstream" in row
    assert "p-warn" in row


def test_the_machine_layer_is_labelled_as_one_machine() -> None:
    """Rendering it as an org fact would be lying about the scope."""
    page = hd.render(DOC)
    assert "one machine, one set of clones" in page
    assert "Nothing in it is an organisation-level fact" in page


def test_the_generation_time_is_shown_not_buried() -> None:
    page = hd.render(DOC)
    header = page.split("<h2>")[0]
    assert DOC["generated_at"] in header


def test_a_note_containing_markup_is_escaped() -> None:
    doc = document()
    doc["repositories"][1]["note"] = "<script>alert(1)</script>"
    page = hd.render(doc)
    assert "<script>" not in page
    assert "&lt;script&gt;" in page


def test_zero_violations_says_so_rather_than_showing_an_empty_section() -> None:
    doc = document()
    doc["repositories"] = [doc["repositories"][0]]
    page = hd.render(doc)
    assert "Every contributor holds at most one slot" in page


@pytest.mark.parametrize(
    "theme_block", [":root {", "prefers-color-scheme: dark", '[data-theme="dark"]']
)
def test_the_page_defines_all_three_theme_states(theme_block: str) -> None:
    assert theme_block in hd.render(DOC)


def test_every_colour_token_is_defined_on_bare_root() -> None:
    """A token defined only inside a media query never applies to the default."""
    page = hd.render(DOC)
    bare = re.search(r":root \{(.*?)\}", page, re.S).group(1)
    defined = set(re.findall(r"(--[a-z-]+)\s*:", bare))
    used = set(re.findall(r"var\((--[a-z-]+)\)", page))
    assert not used - defined


def test_the_page_closes_every_tag_it_opens() -> None:
    import html.parser

    void = {"meta", "br", "img", "hr", "input", "link"}

    class P(html.parser.HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.stack: list[str] = []
            self.bad: list[str] = []

        def handle_starttag(self, tag, attrs):
            if tag not in void:
                self.stack.append(tag)

        def handle_endtag(self, tag):
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            else:
                self.bad.append(tag)

    parser = P()
    parser.feed(hd.render(DOC))
    assert not parser.bad and not parser.stack


def test_the_renderer_never_shells_out() -> None:
    """It reads a document. Anything else would be a second definition."""
    source = Path(hd.__file__).read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "import os" not in source


def test_a_fragment_carries_no_document_shell() -> None:
    """A host that supplies its own <head> must not receive a second one."""
    fragment = hd.render(DOC, fragment=True)
    for tag in ("<!doctype", "<html", "<head>", "<body>"):
        assert tag not in fragment.lower()


def test_a_fragment_still_carries_the_stylesheet() -> None:
    """Inheriting an unknown palette renders three states in one colour."""
    fragment = hd.render(DOC, fragment=True)
    assert "<style>" in fragment
    assert "--unknown:" in fragment
    assert ":root {" in fragment


def test_a_fragment_is_the_same_page_as_the_document() -> None:
    """One body, two wrappers — otherwise the two drift and only one is checked."""
    fragment = hd.render(DOC, fragment=True)
    full = hd.render(DOC)
    body = fragment.split("</style>", 1)[1]
    assert body in full


def test_both_views_share_one_stylesheet() -> None:
    """Two governance pages in one window must not be two colour systems."""
    import governance_render as gr

    assert gr.STYLE is hd.STYLE


# --- the collector writes unknown rather than a comfortable default --------


def test_the_collector_reports_an_unparseable_check_as_unknown(monkeypatch) -> None:
    monkeypatch.setattr(hs, "run", lambda *a, **k: (0, "not json at all", ""))
    result = hs.slot_layer("example/thing", [])
    assert "unknown" in result
    assert "not JSON" in result["unknown"]


def test_the_collector_reports_a_silent_check_as_unknown(monkeypatch) -> None:
    """Empty output must never become an empty, therefore clean, PR list."""
    monkeypatch.setattr(hs, "run", lambda *a, **k: (1, "", "gh: Not Found (HTTP 404)"))
    result = hs.slot_layer("example/thing", [])
    assert "unknown" in result
    assert "404" in result["unknown"]


def test_the_collector_records_the_checks_exit_status(monkeypatch) -> None:
    payload = json.dumps(
        {"repository": "example/thing", "open_prs": [],
         "violations": [{"author": "ada", "base": "", "numbers": [1, 2]}]}
    )
    monkeypatch.setattr(hs, "run", lambda *a, **k: (1, payload, ""))
    result = hs.slot_layer("example/thing", [])
    assert result["exit_status"] == 1
    assert result["compliant"] is False


def test_the_collector_marks_a_missing_clone_unknown(tmp_path: Path) -> None:
    result = hs.local_layer(tmp_path / "nothing")
    assert "unknown" in result
    assert "no clone" in result["unknown"]


def test_the_totals_never_count_an_unknown_as_compliant(monkeypatch) -> None:
    """The arithmetic behind the summary cards, which is where a lie compounds."""
    monkeypatch.setattr(
        hs, "slot_layer", lambda slug, per_base: {"unknown": "could not read"}
    )
    built = hs.build([{"name": "a", "paths": []}], "example", [], False)
    assert built["totals"] == {
        "repositories": 1,
        "slots_measured": 0,
        "slots_unknown": 1,
        "compliant": 0,
        "over_limit": 0,
    }
