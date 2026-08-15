"""Tests for the whole-corpus record review.

Every case builds a small corpus in a temp directory. The review's value is that
it fires on the two defects this corpus actually shipped -- an enforcement clause
naming a mechanism that does not exist, and a record nothing points at -- and
that it does *not* fire on the prose that legitimately describes the world.

The false-positive tests matter as much as the others. The first version of this
tool reported 35 findings, of which most were Context sections doing their job,
and a check that fires on everything trains a reader to skip it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from record_review import decision_section, review_record  # noqa: E402

TOOL = CI_DIR / "record_review.py"

RECORD = """# QM-XXXX — A Record

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-01-01 |

## Context

{context}

## Decision

{decision}

## Amendments

*None.*
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def corpus(tmp_path: Path, context: str = "Background.", decision: str = "1. A rule.",
           reachable: bool = True) -> Path:
    write(tmp_path / "records" / "DRAFT-a.md",
          RECORD.format(context=context, decision=decision))
    link = "See records/DRAFT-a.md." if reachable else "Nothing."
    write(tmp_path / "AGENTS.md", link + "\n")
    write(tmp_path / "README.md", "# R\n")
    write(tmp_path / "PRINCIPLES.md", "# P\n")
    return tmp_path


def kinds(tmp_path: Path, gates: list[dict] | None = None) -> list[str]:
    from record_review import entry_point_text
    record = tmp_path / "records" / "DRAFT-a.md"
    result = review_record(record, tmp_path, gates or [], entry_point_text(tmp_path))
    return [f["kind"] for f in result["findings"]]


# --- the defects this exists for -------------------------------------------


def test_an_enforcement_clause_naming_a_missing_mechanism_is_reported(tmp_path: Path):
    """The version-tags failure: 7 claimed mechanical, nothing read a tag."""
    corpus(tmp_path, decision="6. **Enforcement.** `ci/nonexistent.py` does it.")
    assert "enforcement-names-a-missing-mechanism" in kinds(tmp_path)


def test_an_enforcement_clause_naming_a_real_mechanism_is_clean(tmp_path: Path):
    corpus(tmp_path, decision="6. **Enforcement.** `AGENTS.md` does it.")
    assert "enforcement-names-a-missing-mechanism" not in kinds(tmp_path)


def test_an_enforcement_clause_naming_nothing_at_all_is_reported(tmp_path: Path):
    corpus(tmp_path, decision="6. **Enforcement.** Somebody remembers.")
    assert "enforcement-clause-names-no-mechanism" in kinds(tmp_path)


def test_a_gate_enforcing_a_record_that_never_says_so_is_reported(tmp_path: Path):
    corpus(tmp_path)
    gates = [{"id": "some-gate", "enforces": ["records/DRAFT-a.md"]}]
    assert "enforced-but-does-not-say-so" in kinds(tmp_path, gates)


def test_a_record_nothing_points_at_is_reported(tmp_path: Path):
    corpus(tmp_path, reachable=False)
    assert "unreachable" in kinds(tmp_path)


def test_a_record_an_entry_point_names_is_reachable(tmp_path: Path):
    corpus(tmp_path, reachable=True)
    assert "unreachable" not in kinds(tmp_path)


def test_a_gate_makes_a_record_reachable_even_with_no_entry_point(tmp_path: Path):
    """A record nothing links to but a gate enforces is findable through the gate."""
    corpus(tmp_path, reachable=False)
    gates = [{"id": "g", "enforces": ["records/DRAFT-a.md"]}]
    assert "unreachable" not in kinds(tmp_path, gates)


def test_a_dangling_citation_is_reported(tmp_path: Path):
    corpus(tmp_path, decision="1. See `handbook/gone.md` for the rest.")
    assert "dangling-citation" in kinds(tmp_path)


# --- what it must NOT fire on ----------------------------------------------


def test_a_universal_in_context_is_not_reported(tmp_path: Path):
    """Context describes the world in order to argue about it. That is its job."""
    corpus(tmp_path, context="Every QM project acquires a version number.")
    assert "universal-to-read-by-hand" not in kinds(tmp_path)


def test_a_universal_in_a_decision_clause_is_surfaced(tmp_path: Path):
    corpus(tmp_path, decision="1. Every QM repository is REUSE-compliant.")
    assert "universal-to-read-by-hand" in kinds(tmp_path)


def test_a_universal_with_a_modal_is_a_requirement_and_is_not_surfaced(tmp_path: Path):
    corpus(tmp_path, decision="1. Every QM repository must be REUSE-compliant.")
    assert "universal-to-read-by-hand" not in kinds(tmp_path)


def test_a_project_branch_path_is_not_a_dangling_citation(tmp_path: Path):
    """`adr/` exists on every project branch and on no default branch."""
    corpus(tmp_path, decision="1. See `adr/README.md`.")
    assert "dangling-citation" not in kinds(tmp_path)


def test_a_bare_filename_that_exists_somewhere_is_not_dangling(tmp_path: Path):
    write(tmp_path / ".vscode" / "settings.json", "{}")
    corpus(tmp_path, decision="1. See `settings.json`.")
    assert "dangling-citation" not in kinds(tmp_path)


def test_a_record_with_no_decision_section_surfaces_no_universals(tmp_path: Path):
    write(tmp_path / "records" / "DRAFT-a.md",
          "# T\n\n## Context\n\nEvery QM repository is fine.\n")
    write(tmp_path / "AGENTS.md", "records/DRAFT-a.md\n")
    assert "universal-to-read-by-hand" not in kinds(tmp_path)


def test_decision_section_is_bounded_by_the_next_heading():
    text = "## Decision\n\nrule\n\n## Consequences\n\nEvery project is fine.\n"
    assert "Every project" not in decision_section(text)


# --- the entry point --------------------------------------------------------


def test_no_records_is_a_failure_not_a_clean_review(tmp_path: Path):
    write(tmp_path / "AGENTS.md", "x\n")
    (tmp_path / "records").mkdir()
    result = subprocess.run(
        [sys.executable, str(TOOL), "--root", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 1
    assert "nothing was reviewed" in result.stderr


def test_strict_exits_non_zero_on_a_finding(tmp_path: Path):
    corpus(tmp_path, decision="6. **Enforcement.** `ci/nonexistent.py` does it.")
    result = subprocess.run(
        [sys.executable, str(TOOL), "--root", str(tmp_path), "--strict"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 1


def test_without_strict_a_finding_is_reported_and_exits_zero(tmp_path: Path):
    """A review is a report. Failing a pull request on 12 candidates-for-reading
    would make the review something people route around."""
    corpus(tmp_path, decision="6. **Enforcement.** `ci/nonexistent.py` does it.")
    result = subprocess.run(
        [sys.executable, str(TOOL), "--root", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0
    assert "structural finding" in result.stdout


def test_the_output_says_it_is_not_a_semantic_review(tmp_path: Path):
    corpus(tmp_path)
    result = subprocess.run(
        [sys.executable, str(TOOL), "--root", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert "is a semantic review" in result.stdout  # "None of this is a semantic review"
