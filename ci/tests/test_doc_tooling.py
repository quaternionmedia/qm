"""Tests for the document state document and its view.

Same contract as the gate tooling: the renderer may not run a command, `unknown`
may not render as fine, and a filtered page must say it is filtered. Every case
builds a small corpus in a temp directory, so no test passes because this
repository happens to be in the state it asserts.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from doc_status import build, classify, normalise, perspective_index  # noqa: E402

STATUS = CI_DIR / "doc_status.py"
DASHBOARD = CI_DIR / "doc_dashboard.py"

HEADER = "# T\n\n| | |\n|---|---|\n| **Status** | {status} |\n\n## Body\n\ntext\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def corpus(tmp_path: Path) -> Path:
    write(tmp_path / "AGENTS.md", "# Agents\n")
    write(tmp_path / "README.md", "# Readme\n")
    write(tmp_path / "PRINCIPLES.md", "# Charter\n")
    return tmp_path


def states(doc: dict) -> dict[str, str]:
    return {d["path"]: d["state"] for d in doc["documents"]}


def find(doc: dict, path: str) -> dict:
    """Rows are sorted by path, so `documents[0]` is AGENTS.md, not the subject."""
    return next(d for d in doc["documents"] if d["path"] == path)


def run(tool: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(tool), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


# --- the separation ---------------------------------------------------------


def test_the_renderer_cannot_run_a_command():
    source = DASHBOARD.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "import os" not in source


# --- the two signals on a record -------------------------------------------


def test_a_proposed_draft_record_is_proposed(tmp_path: Path):
    corpus(tmp_path)
    write(tmp_path / "records" / "DRAFT-a.md", HEADER.format(status="Proposed"))
    assert states(build(tmp_path))["records/DRAFT-a.md"] == "proposed"


def test_a_ratified_numbered_record_is_ratified(tmp_path: Path):
    corpus(tmp_path)
    write(tmp_path / "records" / "QM-0001-a.md", HEADER.format(status="Accepted"))
    assert states(build(tmp_path))["records/QM-0001-a.md"] == "ratified"


def test_a_draft_filename_holding_an_accepted_status_is_a_disagreement(tmp_path: Path):
    """Ratification renames the file. Nothing else in the corpus notices this."""
    corpus(tmp_path)
    write(tmp_path / "records" / "DRAFT-a.md", HEADER.format(status="Accepted"))
    doc = build(tmp_path)
    assert doc["totals"]["disagreements"] == 1
    assert "one of the five steps" in find(doc, "records/DRAFT-a.md")["disagreement"]


def test_draft_filename_with_proposed_status_is_not_a_disagreement(tmp_path: Path):
    """The ordinary state of every record here. Flagging it would flag everything."""
    corpus(tmp_path)
    write(tmp_path / "records" / "DRAFT-a.md", HEADER.format(status="Proposed"))
    assert build(tmp_path)["totals"]["disagreements"] == 0


def test_a_record_with_no_status_row_is_unknown_not_draft(tmp_path: Path):
    corpus(tmp_path)
    write(tmp_path / "records" / "DRAFT-a.md", "# T\n\nno table\n")
    assert states(build(tmp_path))["records/DRAFT-a.md"] == "unknown"


# --- the perspective index is the authority --------------------------------


def test_a_perspective_takes_its_state_from_the_index(tmp_path: Path):
    """Most perspectives carry no Status row; the index is the mechanism."""
    corpus(tmp_path)
    write(tmp_path / "perspectives" / "a.md", "# T\n\n*byline*\n")
    write(tmp_path / "perspectives" / "README.md",
          "| 2026-01-01 | `a.md` | Someone | Perspective | Responded | note |\n")
    assert states(build(tmp_path))["perspectives/a.md"] == "responded"


def test_a_perspective_missing_from_the_index_is_unknown(tmp_path: Path):
    """A real finding on this tool's first run: one perspective had no row."""
    corpus(tmp_path)
    write(tmp_path / "perspectives" / "a.md", "# T\n\n*byline*\n")
    write(tmp_path / "perspectives" / "README.md", "| Date | File |\n")
    doc = build(tmp_path)
    assert states(doc)["perspectives/a.md"] == "unknown"


def test_the_index_disagreeing_with_the_file_is_reported(tmp_path: Path):
    corpus(tmp_path)
    write(tmp_path / "perspectives" / "a.md", HEADER.format(status="Unreviewed"))
    write(tmp_path / "perspectives" / "README.md",
          "| 2026-01-01 | `a.md` | Someone | Perspective | Responded | note |\n")
    doc = build(tmp_path)
    assert doc["totals"]["disagreements"] == 1
    assert "the index is the authority" in find(doc, "perspectives/a.md")["disagreement"]


def test_an_index_is_not_a_member_of_what_it_indexes(tmp_path: Path):
    """Asking perspectives/README.md for a status reported the index as unknown."""
    corpus(tmp_path)
    write(tmp_path / "perspectives" / "README.md", "| Date | File |\n")
    assert states(build(tmp_path))["perspectives/README.md"] == "standing"
    assert classify(tmp_path / "perspectives" / "README.md", tmp_path)[0] == "index"


# --- generated documents ----------------------------------------------------


def test_a_declared_generated_document_absent_from_disk_is_still_listed(tmp_path: Path):
    """Omitting it would make the set depend on which generator ran first, and
    this document lists a view written after itself."""
    corpus(tmp_path)
    doc = build(tmp_path)
    row = [d for d in doc["documents"] if d["path"] == "gate-status.json"][0]
    assert row["state"] == "generated"
    assert row["present"] is False
    assert "not on disk" in row["why_absent"]


def test_the_document_is_order_independent(tmp_path: Path):
    """Built twice with a file appearing in between, the earlier run must have
    already listed it -- otherwise --check can never pass."""
    corpus(tmp_path)
    first = build(tmp_path)
    write(tmp_path / "handbook" / "gates.md", "# generated\n")
    second = build(tmp_path)
    assert [d["path"] for d in first["documents"]] == [d["path"] for d in second["documents"]]


def test_an_empty_corpus_is_refused(tmp_path: Path):
    with pytest.raises(SystemExit):
        build(tmp_path / "nothing")


# --- the vocabulary is closed ----------------------------------------------


@pytest.mark.parametrize("raw,expected", [
    ("Proposed", "proposed"), ("Accepted", "ratified"), ("Ratified", "ratified"),
    ("Unreviewed", "unreviewed"), ("Declined", "declined"), ("Nonsense", None),
])
def test_status_strings_map_onto_the_closed_vocabulary(raw: str, expected):
    assert normalise(raw) == expected


def test_an_unrecognised_status_is_unknown_not_a_new_category(tmp_path: Path):
    corpus(tmp_path)
    write(tmp_path / "records" / "DRAFT-a.md", HEADER.format(status="Nearly Done"))
    doc = build(tmp_path)
    assert states(doc)["records/DRAFT-a.md"] == "unknown"
    assert find(doc, "records/DRAFT-a.md")["declared_status"] == "Nearly Done"


def test_perspective_index_of_a_missing_file_is_empty_not_an_exception(tmp_path: Path):
    assert perspective_index(tmp_path) == {}


# --- the view and its toggle ------------------------------------------------


def render(tmp_path: Path, doc: dict, *args: str) -> str:
    path = tmp_path / "doc.json"
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
    result = run(DASHBOARD, str(path), *args)
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_a_filtered_page_says_how_many_it_hid(tmp_path: Path):
    """A filtered page that does not say so reads as the whole corpus."""
    corpus(tmp_path)
    write(tmp_path / "records" / "DRAFT-a.md", HEADER.format(status="Proposed"))
    text = render(tmp_path, build(tmp_path), "--state", "proposed")
    assert "Filtered to `proposed`" in text
    assert "hidden" in text


def test_an_unfiltered_page_says_it_is_unfiltered(tmp_path: Path):
    corpus(tmp_path)
    text = render(tmp_path, build(tmp_path))
    assert "unfiltered" in text


def test_an_empty_filter_result_is_a_real_answer_not_a_blank(tmp_path: Path):
    corpus(tmp_path)
    text = render(tmp_path, build(tmp_path), "--state", "ratified")
    assert "No document is in state `ratified`" in text
    assert "documents were read and none matched" in text


def test_an_unknown_state_name_is_refused(tmp_path: Path):
    corpus(tmp_path)
    path = tmp_path / "doc.json"
    path.write_text(json.dumps(build(tmp_path)), encoding="utf-8", newline="\n")
    result = run(DASHBOARD, str(path), "--state", "nearly")
    assert result.returncode == 2
    assert "vocabulary is closed" in result.stderr


def test_the_generation_time_is_at_the_top(tmp_path: Path):
    corpus(tmp_path)
    doc = build(tmp_path)
    assert any(doc["generated_at"] in line for line in render(tmp_path, doc).splitlines()[:4])


def test_state_is_carried_in_form_not_only_colour(tmp_path: Path):
    corpus(tmp_path)
    write(tmp_path / "records" / "DRAFT-a.md", "# T\n\nno table\n")
    assert "[??]" in render(tmp_path, build(tmp_path))
