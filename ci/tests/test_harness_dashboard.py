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
            "governance_readable": 2,
            "governance_precondition_met": 1,
            "phase_scaffolded": 1,
            "phase_stated_above_governance": 1,
        },
        "repositories": [
            {
                "name": "clean-repo",
                "slug": "example/clean-repo",
                "role": "project",
                "phase": "v0.0.1",
                "phase_source": "scaffolded",
                "governance": {"precondition": "met", "missing": [],
                               "behind_corpus": 0},
                "slots": {"open_prs": [], "violations": [], "compliant": True},
                "local": {"branch": "main", "dirty": 0, "upstream": "origin/main", "ahead": 0},
            },
            {
                "name": "busy-repo",
                "slug": "example/busy-repo",
                "role": "project",
                "phase": "v0.0.2",
                "phase_source": "stated",
                "note": "nobody has placed this on the ladder",
                "governance": {"precondition": "incomplete",
                               "missing": ["ide", "workflows"],
                               "behind_corpus": 62},
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
                "phase_source": "unknown",
                "governance": {"unknown": "no project/<name> branch in the corpus"},
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
    doc = document()
    doc["repositories"][0]["phase"] = "unknown"
    page = hd.render(doc)
    assert "Phases nobody has answered" in page
    assert "clean-repo" in page.split("Phases nobody has answered")[1]


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


def test_text_from_the_document_containing_markup_is_escaped() -> None:
    """Every field that reaches the page, not just the one that is convenient.

    The reason string in particular is assembled from a command's stderr, which
    is the least trusted text in the document.
    """
    doc = document()
    doc["repositories"][0]["phase"] = "unknown"
    doc["repositories"][0]["note"] = "<script>alert('note')</script>"
    doc["repositories"][1]["governance"]["missing"] = ["<script>alert('missing')</script>"]
    doc["repositories"][2]["governance"] = {"unknown": "<script>alert('why')</script>"}
    page = hd.render(doc)
    assert "<script>" not in page
    assert page.count("&lt;script&gt;") >= 3


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
    totals = built["totals"]
    assert totals["repositories"] == 1
    assert totals["slots_measured"] == 0
    assert totals["slots_unknown"] == 1
    assert totals["compliant"] == 0
    assert totals["over_limit"] == 0


# --- the phase ladder: a claim and its evidence, kept apart ----------------


def test_a_scaffolded_phase_is_marked_as_nobody_having_decided() -> None:
    """A default rendered like a choice has become a finding nobody made."""
    row = row_for(hd.render(DOC), "clean-repo")
    assert "v0.0.1" in row
    assert "nobody decided this" in row


def test_a_stated_phase_is_not_marked_as_scaffolded() -> None:
    row = row_for(hd.render(DOC), "busy-repo")
    assert "stated" in row
    assert "nobody decided this" not in row


def test_a_met_precondition_never_says_the_claim_has_been_made() -> None:
    """A complete artifact set means a human MAY assert v0.0.1, not that they did."""
    page = hd.render(DOC)
    row = row_for(page, "clean-repo")
    assert "precondition met" in row
    assert not re.search(r"\badopted\b", page, re.I)


def test_incomplete_governance_names_what_is_missing() -> None:
    """'Incomplete' without the list cannot be acted on."""
    row = row_for(hd.render(DOC), "busy-repo")
    assert "incomplete" in row
    assert "ide" in row and "workflows" in row


def test_governance_that_could_not_be_read_is_unknown_not_incomplete() -> None:
    """A project nobody measured must not look like one measured and found short."""
    row = row_for(hd.render(DOC), "private-repo")
    assert "s-unknown" in row
    assert "incomplete" not in row


def test_a_rung_stated_above_unevidenced_governance_is_surfaced() -> None:
    page = hd.render(DOC)
    section = page.split("Claimed above the evidence")[1].split("<h2>")[0]
    assert "busy-repo" in section
    assert "v0.0.2" in section
    assert "ide" in section


def test_a_scaffolded_v001_is_not_surfaced_as_claimed_above_the_evidence() -> None:
    """The floor is not a claim above anything; listing it would bury the real ones."""
    section = hd.render(DOC).split("Claimed above the evidence")[1].split("<h2>")[0]
    assert "clean-repo" not in section


def test_a_stated_rung_with_met_governance_is_not_surfaced() -> None:
    doc = document()
    doc["repositories"][1]["governance"] = {"precondition": "met", "missing": []}
    section = hd.render(doc).split("Claimed above the evidence")[1].split("<h2>")[0]
    assert "busy-repo" not in section
    assert "No project claims a rung above governance" in section


def test_the_page_says_the_phase_column_is_a_claim() -> None:
    """Two columns side by side are read as one fact unless the page says otherwise."""
    page = hd.render(DOC)
    assert "Phase <span class=\"s-muted\">(claimed)</span>" in page
    assert "(evidence)" in page
    assert "work sitting in an open pull request is work, and it is" in page


# --- the collector reads evidence from the document, never from the roster --


def test_evidence_cannot_read_the_claim_it_is_evidence_for() -> None:
    """A check that reads a claim to decide whether the claim is true is not a check.

    Asserted on the signature rather than the source text: a scan for the word
    `phase` matches the paragraph explaining that this function does not use
    one. Taking a single argument, which is the status document's project entry,
    is the structural guarantee — there is no roster in scope to consult.
    """
    import inspect

    assert list(inspect.signature(hs.governance_evidence).parameters) == ["project"]


def test_a_project_with_no_branch_is_unknown_rather_than_incomplete() -> None:
    result = hs.governance_evidence(None)
    assert "unknown" in result
    assert "no project/<name> branch" in result["unknown"]


def test_an_unreadable_adoption_block_carries_its_reason() -> None:
    result = hs.governance_evidence({"adoption": {"unknown": "HTTP 404"}})
    assert result == {"unknown": "HTTP 404"}


def test_the_full_artifact_set_meets_the_precondition() -> None:
    result = hs.governance_evidence(
        {
            "adoption": {
                "submodule": {"corpus_mounted_at": "governance/qm", "branch": "project/x"},
                "ide": ["AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"],
                "ide_missing": [],
                "seed_workflow_filenames_present": ["adr-lint.yml"],
                "seed_workflow_filenames_absent": [],
                "licensing": ["LICENSE", "REUSE.toml"],
            },
            "branch": {"behind_corpus": 0},
        }
    )
    assert result["precondition"] == "met"
    assert result["missing"] == []


def test_a_submodule_mounted_without_its_own_branch_is_incomplete() -> None:
    """Being pinned is not being adopted, and the branch IS the pin."""
    result = hs.governance_evidence(
        {
            "adoption": {
                "submodule": {"corpus_mounted_at": "docs/qm", "branch": None},
                "ide": ["AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"],
                "ide_missing": [],
                "seed_workflow_filenames_present": ["adr-lint.yml"],
                "seed_workflow_filenames_absent": [],
                "licensing": ["LICENSE", "REUSE.toml"],
            },
            "branch": {},
        }
    )
    assert result["precondition"] == "incomplete"
    assert "submodule branch" in result["missing"]


def test_each_absent_artifact_class_is_named_individually() -> None:
    result = hs.governance_evidence(
        {
            "adoption": {
                "submodule": {"corpus_mounted_at": None, "branch": None},
                "ide": [],
                "ide_missing": ["AGENTS.md"],
                "seed_workflow_filenames_present": [],
                "seed_workflow_filenames_absent": ["adr-lint.yml"],
                "licensing": [],
            },
            "branch": {},
        }
    )
    assert result["missing"] == ["submodule", "ide", "workflows", "licensing"]


def test_a_missing_status_document_makes_evidence_unknown_not_absent(tmp_path: Path) -> None:
    """A vanished column reads as a column with nothing in it."""
    loaded, gap = hs.load_governance(tmp_path / "nothing.yaml")
    assert loaded == {}
    assert "no governance status document" in gap

    built = hs.build(
        [{"name": "a", "paths": []}], "example", [], False, {}, gap
    )
    assert "unknown" in built["repositories"][0]["governance"]


def test_the_totals_count_governance_over_what_was_readable(monkeypatch) -> None:
    """A project with no evidence sits in neither numerator nor denominator."""
    monkeypatch.setattr(hs, "slot_layer", lambda slug, per_base: {"open_prs": [], "violations": [], "compliant": True})
    built = hs.build(
        [
            {"name": "met", "paths": [], "phase": "v0.0.1", "phase_source": "scaffolded"},
            {"name": "short", "paths": [], "phase": "v0.0.2", "phase_source": "stated"},
            {"name": "absent", "paths": [], "phase": "v0.0.1", "phase_source": "scaffolded"},
        ],
        "example",
        [],
        False,
        {
            "met": {
                "adoption": {
                    "submodule": {"corpus_mounted_at": "governance/qm", "branch": "project/met"},
                    "ide": ["a"], "ide_missing": [],
                    "seed_workflow_filenames_present": ["a"],
                    "seed_workflow_filenames_absent": [],
                    "licensing": ["LICENSE", "REUSE.toml"],
                },
                "branch": {"behind_corpus": 0},
            },
            "short": {
                "adoption": {
                    "submodule": {"corpus_mounted_at": None, "branch": None},
                    "ide": [], "ide_missing": ["AGENTS.md"],
                    "seed_workflow_filenames_present": [],
                    "seed_workflow_filenames_absent": ["adr-lint.yml"],
                    "licensing": [],
                },
                "branch": {},
            },
        },
        None,
    )
    totals = built["totals"]
    assert totals["governance_readable"] == 2
    assert totals["governance_precondition_met"] == 1
    assert totals["phase_scaffolded"] == 2
    assert totals["phase_stated_above_governance"] == 1


def test_a_stated_v001_is_not_surfaced_as_claimed_above_the_evidence() -> None:
    """The floor is not a claim above anything, even when a human stated it.

    This is a real shape: `rad` states v0.0.1 and has no project branch, so its
    governance is unknown. Listing it beside a project claiming v0.0.3 would
    bury the distinction the section exists to draw. The scaffolded case does
    not test this — it is already excluded for having no stated claim at all.
    """
    doc = document()
    doc["repositories"][1]["phase"] = "v0.0.1"
    doc["repositories"][1]["phase_source"] = "stated"
    section = hd.render(doc).split("Claimed above the evidence")[1].split("<h2>")[0]
    assert "busy-repo" not in section
