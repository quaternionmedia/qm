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
        "reading": {
            "refresh": "python ci/harness_status.py --no-local --write harness-status.json",
            "staleness_budget_hours": 24,
            "unknown_convention": "it is not zero, not empty, and not compliant",
            "do_not": [
                "quote a figure from this document without its generated_at",
                "treat a phase as evidence: phase is what a human claimed",
            ],
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


# --- the agent view, and the committed document ---------------------------


def test_the_markdown_view_states_unknown_in_words() -> None:
    """An agent parsing HTML loses the distinction the page spends colour on."""
    text = hd.render_markdown(DOC)
    assert "unknown (gh api repos/example/private-repo: HTTP 404)" in text
    assert "unknown (no project/<name> branch in the corpus)" in text


def test_the_markdown_view_never_leaves_a_state_implied_by_an_empty_cell() -> None:
    """A blank cell reads as fine, in any format."""
    for line in hd.render_markdown(DOC).splitlines():
        if line.startswith("| ") and "---" not in line and "Repository" not in line:
            assert "|  |" not in line, line
            assert not line.endswith("| |"), line


def test_the_markdown_view_names_the_violating_pull_requests() -> None:
    text = hd.render_markdown(DOC)
    assert "OVER" in text
    assert "#8" in text and "#9" in text


def test_the_markdown_view_carries_the_staleness_budget_and_refresh() -> None:
    """The next agent has the file, not the handbook page that explains it."""
    text = hd.render_markdown(DOC)
    assert "older than 24h" in text
    assert "harness_status.py --no-local --write" in text


def test_the_markdown_view_carries_the_do_not_list() -> None:
    text = hd.render_markdown(DOC)
    assert "Do not quote a figure from this document without its generated_at" in text
    assert "Do not treat a phase as evidence" in text


def test_the_markdown_view_collects_what_needs_a_human() -> None:
    text = hd.render_markdown(DOC)
    section = text.split("## What needs a human")[1].split("## ")[0]
    assert "busy-repo" in section
    assert "Close the pull request FIRST" in section
    assert "clean-repo" in section  # scaffolded phase


def test_the_markdown_view_lists_every_gap_with_its_reason() -> None:
    section = hd.render_markdown(DOC).split("could not establish")[1]
    assert "HTTP 404" in section
    assert "not found on this machine" in section


def test_a_document_with_no_gaps_says_so_rather_than_showing_nothing() -> None:
    doc = document()
    doc["repositories"] = [doc["repositories"][0]]
    section = hd.render_markdown(doc).split("could not establish")[1]
    assert "every layer was read" in section


def test_both_views_render_the_same_document() -> None:
    """One document, two formats — never two pipelines that can disagree."""
    for name in ("clean-repo", "busy-repo", "private-repo"):
        assert name in hd.render(DOC)
        assert name in hd.render_markdown(DOC)


def test_the_markdown_view_runs_nothing() -> None:
    text = hd.render_markdown(DOC)
    assert "reads no network" in text


def test_the_committed_document_exists_and_parses() -> None:
    """The path AGENTS.md sends the next agent to. If it is absent, they get nothing."""
    committed = CI_DIR.parent / "harness-status.json"
    assert committed.exists(), "harness-status.json is not committed"
    doc = json.loads(committed.read_text(encoding="utf-8"))
    assert doc["schema"] == 1
    assert doc["repositories"]


def test_the_committed_document_carries_its_own_reading_instructions() -> None:
    """A convention that lives only in a handbook page is one the reader lacks."""
    doc = json.loads((CI_DIR.parent / "harness-status.json").read_text(encoding="utf-8"))
    reading = doc["reading"]
    assert reading["refresh"]
    assert reading["staleness_budget_hours"] == hs.STALENESS_BUDGET_HOURS
    assert "not compliant" in reading["unknown_convention"]
    assert reading["do_not"]


def test_the_committed_document_omits_the_machine_layer() -> None:
    """One machine's branch names must not become an organisation fact."""
    doc = json.loads((CI_DIR.parent / "harness-status.json").read_text(encoding="utf-8"))
    assert "local" not in doc["generator"]["layers"]
    for repo in doc["repositories"]:
        assert "local" not in repo, repo["name"]


def test_the_committed_document_renders_in_both_formats() -> None:
    """A document nobody can render is a document nobody will read."""
    doc = json.loads((CI_DIR.parent / "harness-status.json").read_text(encoding="utf-8"))
    assert "<table>" in hd.render(doc)
    assert "| Repository |" in hd.render_markdown(doc)


def test_inside_corpus_recognises_a_path_that_would_be_committed(tmp_path: Path) -> None:
    assert hs.inside_corpus(CI_DIR.parent / "harness-status.json")
    assert hs.inside_corpus(CI_DIR / "nested" / "thing.json")
    assert not hs.inside_corpus(tmp_path / "harness-status.json")


def test_writing_the_machine_layer_into_the_repository_is_refused() -> None:
    """Rather than trusting anybody to remember --no-local.

    Run against the real path, because the real path is the whole subject: a
    guard tested against a temporary directory is a guard tested where it never
    fires. That makes this a test that can damage what it tests — a mutation
    run with the guard disabled wrote one machine's branch names into the
    committed document — so the file is restored before anything is asserted.
    """
    committed = CI_DIR.parent / "harness-status.json"
    before = committed.read_bytes()
    try:
        result = subprocess.run(
            [sys.executable, str(CI_DIR / "harness_status.py"),
             "--write", "harness-status.json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(CI_DIR.parent),
        )
    finally:
        if committed.read_bytes() != before:
            committed.write_bytes(before)

    assert result.returncode == 1
    assert "refusing to write the machine layer" in result.stderr
    assert "--no-local" in result.stderr


# --- threads: work in flight, as states rather than a percentage -----------


def threaded(**kw) -> dict:
    """A document with one repository and the threads given."""
    doc = document()
    doc["repositories"] = [doc["repositories"][0]]
    doc["repositories"][0].update(kw)
    doc["generator"]["stalled_after_hours"] = 48
    doc["generator"]["thread_stages_are_states_not_progress"] = "observable states"
    doc["totals"]["threads_by_stage"] = {"local": 1, "pushed": 1, "draft": 1, "ready": 1}
    doc["totals"]["threads_stalled"] = 1
    return doc


ORG_THREAD = {
    "name": "evolve/thing", "stage": "draft", "pr": 36, "base": "main",
    "delta": {"commits": 17, "additions": 10490, "deletions": 60, "changed_files": 60},
    "idle_hours": 0.7, "stalled": False,
}
PUSHED_THREAD = {
    "name": "feature/delta", "stage": "pushed", "pr": None, "base": "main",
    "delta": {"commits": 16, "shortstat": "18 files changed, 2392 insertions(+)"},
    "idle_hours": 4711.0, "stalled": True,
}


def test_a_thread_is_rendered_in_both_views() -> None:
    doc = threaded(threads=[ORG_THREAD])
    assert "evolve/thing" in hd.render(doc)
    assert "evolve/thing" in hd.render_markdown(doc)


def test_the_two_delta_shapes_are_rendered_as_measured() -> None:
    """A pull request's counts come from the host; a branch's from git.

    Rendering one as the other would print a number the reader cannot check.
    """
    assert "17 commits, 60 files, +10490/-60" == hd.delta_text(ORG_THREAD["delta"])
    assert hd.delta_text(PUSHED_THREAD["delta"]).startswith("16 commits, 18 files changed")


def test_an_unmeasured_delta_says_unknown_with_its_reason() -> None:
    assert "unknown (pulls/9: HTTP 404)" == hd.delta_text({"unknown": "pulls/9: HTTP 404"})


def test_a_pushed_thread_is_warned_on_not_treated_as_progress() -> None:
    """It exists on a remote and no reviewer has been told.

    Asserted on the stage pill itself, not on the page: the repository table
    above carries p-warn cells of its own, so a page-wide assertion passes
    against a renderer that marks every stage as fine.
    """
    page = hd.render(threaded(local={"threads": [PUSHED_THREAD]}))
    assert '<span class="pill p-warn">pushed</span>' in page
    assert "no pull request" in page


def test_a_pushed_thread_becomes_an_action_for_a_human() -> None:
    text = hd.render_markdown(threaded(local={"threads": [PUSHED_THREAD]}))
    section = text.split("## What needs a human")[1].split("## ")[0]
    assert "feature/delta" in section
    assert "no reviewer has been told" in section


def test_a_draft_thread_is_not_an_action() -> None:
    """Draft is the normal state here; flagging it would flag everything."""
    text = hd.render_markdown(threaded(threads=[ORG_THREAD]))
    section = text.split("## What needs a human")[1].split("## ")[0]
    assert "evolve/thing" not in section


def test_stalled_threads_sort_above_active_ones() -> None:
    """The stalled one must win even when its stage would sort it last.

    A stalled `pushed` thread against a fresh `draft` one proves nothing: the
    stage order already puts pushed first, so the test passes with the stalled
    key ignored entirely. `ready` sorts last, so a stalled `ready` thread only
    reaches the top if being stalled is what lifted it.
    """
    stalled_ready = {**ORG_THREAD, "name": "old/ready", "stage": "ready",
                     "stalled": True, "idle_hours": 900.0}
    fresh_draft = {**ORG_THREAD, "name": "new/draft", "stage": "draft",
                   "stalled": False, "idle_hours": 1.0}
    doc = threaded(threads=[fresh_draft, stalled_ready])
    ordered = [t["name"] for t in hd.thread_rows(doc)]
    assert ordered.index("old/ready") < ordered.index("new/draft")


def test_pushed_sorts_above_draft_when_neither_is_stalled() -> None:
    """A branch nobody can see outranks one already in front of a reviewer."""
    fresh = {**PUSHED_THREAD, "stalled": False, "idle_hours": 1.0}
    doc = threaded(threads=[ORG_THREAD], local={"threads": [fresh]})
    ordered = [t["name"] for t in hd.thread_rows(doc)]
    assert ordered.index("feature/delta") < ordered.index("evolve/thing")


def test_each_thread_is_tagged_with_its_scope() -> None:
    """Org-wide and one-machine facts side by side must stay distinguishable."""
    doc = threaded(threads=[ORG_THREAD], local={"threads": [PUSHED_THREAD]})
    by_name = {t["name"]: t["scope"] for t in hd.thread_rows(doc)}
    assert by_name == {"evolve/thing": "org", "feature/delta": "machine"}


def test_idle_is_shown_in_days_once_it_stops_being_a_working_day() -> None:
    assert hd.idle_text(0.7) == "1h"
    assert hd.idle_text(30.0) == "30h"
    assert hd.idle_text(4711.0) == "196d"
    assert hd.idle_text(None) == "unknown"


def test_unreadable_threads_are_named_rather_than_shown_as_none() -> None:
    doc = threaded(threads={"unknown": "open pull requests could not be read"})
    page = hd.render(doc)
    assert "could not be read" in page
    assert hd.thread_rows(doc) == []


def test_no_view_claims_a_completion_percentage() -> None:
    """The corpus has no definition of done, so nothing may imply one.

    The stylesheet is excluded before matching: `width: 100%` is a percentage
    and is not a claim about anybody's progress. An assertion over the whole
    page matches it and fails for a reason unrelated to what it tests.
    """
    doc = threaded(threads=[ORG_THREAD], local={"threads": [PUSHED_THREAD]})
    html_body = hd.render(doc).split("</style>", 1)[1]
    for view in (html_body, hd.render_markdown(doc)):
        assert not re.search(r"[0-9]+\s*%", view), view[:400]


def test_the_markdown_view_states_that_stages_are_not_progress() -> None:
    text = hd.render_markdown(threaded(threads=[ORG_THREAD]))
    assert "not progress" in text


def test_no_threads_says_so_rather_than_rendering_an_empty_table() -> None:
    page = hd.render(threaded(threads=[]))
    assert "No threads in flight" in page


# --- the collector's thread rules ------------------------------------------


def test_threads_are_unknown_when_the_pull_requests_could_not_be_read() -> None:
    """Not an empty list, which would say this repository has no work in flight."""
    result = hs.org_threads("example/thing", {"unknown": "HTTP 404"}, False)
    assert "unknown" in result


def test_bot_pull_requests_are_not_threads() -> None:
    """They are excluded from every other count, so their size is unread."""
    slots = {"open_prs": [
        {"number": 1, "author": "dependabot[bot]", "bot": True, "base": "main",
         "head": "dependabot/x", "draft": False, "title": "bump"},
    ]}
    assert hs.org_threads("example/thing", slots, False) == []


def test_a_draft_and_a_ready_pull_request_get_their_stages() -> None:
    slots = {"open_prs": [
        {"number": 1, "author": "ada", "bot": False, "base": "main",
         "head": "a", "draft": True, "title": "t"},
        {"number": 2, "author": "ada", "bot": False, "base": "main",
         "head": "b", "draft": False, "title": "t"},
    ]}
    stages = {t["name"]: t["stage"] for t in hs.org_threads("example/t", slots, False)}
    assert stages == {"a": "draft", "b": "ready"}


def test_hours_since_reads_both_instant_spellings() -> None:
    assert hs.hours_since("2026-01-01T00:00:00Z") > 0
    assert hs.hours_since("2026-01-01T00:00:00+00:00") > 0
    assert hs.hours_since(None) is None
    assert hs.hours_since("not a date") is None
