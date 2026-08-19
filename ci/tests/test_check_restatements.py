"""Tests for the restatement declaration check.

Exit status is the contract. Each test builds a small corpus on disk rather
than pointing at the real one, so a test never passes because the real corpus
happens to be in the state it asserts -- the scaffolding-measures-itself failure
this corpus has recorded four times.

The check's two blind spots are tested as blind spots. A test that asserted it
catches an undeclared restatement would be asserting a capability the module
docstring says it does not have, and would pass only until somebody read it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "check_restatements.py"

RECORD = """# QM-XXXX — A Record

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-01-01 |
{restated}

## Context

Body.

## Amendments

*None.*
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def corpus(root: Path, *, restated: str = "", agents: str = "Nothing here.") -> Path:
    """A minimal corpus: one record, one entry point."""
    row = f"| **Restated in** | {restated} |" if restated else ""
    write(root / "records" / "DRAFT-a-record.md", RECORD.format(restated=row))
    write(root / "AGENTS.md", agents + "\n")
    return root


def run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_declared_and_cited_passes(tmp_path: Path):
    corpus(
        tmp_path,
        restated="`AGENTS.md` item 3",
        agents="Item 3 summarizes records/DRAFT-a-record.md and says so.",
    )
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_declared_but_not_cited_fails(tmp_path: Path):
    """The half that actually bites: a record claims a copy that never links back."""
    corpus(tmp_path, restated="`AGENTS.md` item 3", agents="Item 3 says a thing.")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "never names its path" in result.stderr


def test_declared_file_that_does_not_exist_fails(tmp_path: Path):
    corpus(tmp_path, restated="`HANDBOOK.md` item 1")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "not a file" in result.stderr


def test_declared_file_that_is_not_an_entry_point_fails(tmp_path: Path):
    corpus(tmp_path, restated="`notes.md` somewhere")
    write(tmp_path / "notes.md", "records/DRAFT-a-record.md\n")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "not an entry point" in result.stderr


def test_citation_without_declaration_is_reported_not_failed(tmp_path: Path):
    """§2 asks entry points to cite. Failing on a citation would invert that.

    README.md's record index is the case: it names every record and restates
    none of them.
    """
    corpus(tmp_path, agents="See records/DRAFT-a-record.md for the detail.")
    result = run(tmp_path)
    assert result.returncode == 0
    assert "cited, not declared as restated" in result.stdout


def test_citation_of_a_record_that_does_not_exist_fails(tmp_path: Path):
    corpus(tmp_path, agents="See records/DRAFT-imaginary.md for the detail.")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "not a record here" in result.stderr


def test_submodule_spelling_of_a_record_path_counts(tmp_path: Path):
    """A seed copy reaches the corpus through the mount; it is the same file.

    No single mutation makes this go red, and that is a property of the tool
    rather than a weakness here: `RECORD_MENTION` is unanchored, so
    `governance/qm/records/DRAFT-x.md` matches by containing the shorter path.
    The behaviour is asserted; there is no separate guard to break.
    """
    write(tmp_path / "records" / "DRAFT-a-record.md", RECORD.format(
        restated="| **Restated in** | `project-seed/ide/AGENTS.md` item 3 |"
    ))
    write(tmp_path / "AGENTS.md", "Nothing here.\n")
    write(
        tmp_path / "project-seed" / "ide" / "AGENTS.md",
        "Item 3 summarizes governance/qm/records/DRAFT-a-record.md.\n",
    )
    assert run(tmp_path).returncode == 0


def test_no_records_is_a_failure_not_a_vacuous_pass(tmp_path: Path):
    """An empty glob passing green is how this corpus's lints have failed before."""
    write(tmp_path / "AGENTS.md", "Nothing here.\n")
    (tmp_path / "records").mkdir()
    result = run(tmp_path)
    assert result.returncode == 1
    assert "nothing was checked" in result.stderr


def test_no_entry_points_is_a_failure_not_a_vacuous_pass(tmp_path: Path):
    write(tmp_path / "records" / "DRAFT-a-record.md", RECORD.format(restated=""))
    result = run(tmp_path)
    assert result.returncode == 1
    assert "nothing was checked" in result.stderr


@pytest.mark.parametrize("value", ["Nothing", "None", "-"])
def test_an_explicit_empty_declaration_is_not_a_path(tmp_path: Path, value: str):
    corpus(tmp_path, restated=value)
    assert run(tmp_path).returncode == 0


def test_perspectives_are_not_entry_points(tmp_path: Path):
    """A retrospective quoting a record is a citation, and dated besides."""
    corpus(tmp_path)
    write(tmp_path / "perspectives" / "2026-01-01-a.md", "records/DRAFT-a-record.md\n")
    result = run(tmp_path)
    assert result.returncode == 0
    assert "perspectives/" not in result.stdout


def test_handbook_pages_are_entry_points(tmp_path: Path):
    """A handbook page must reach the *uncited* failure, not the *not-an-entry-point* one.

    Both messages name the file, so asserting the filename alone passes whether
    handbook pages are collected or not — the test would survive the glob being
    deleted, which is the case it exists to catch.
    """
    corpus(tmp_path, restated="`handbook/a-page.md` §2")
    write(tmp_path / "handbook" / "a-page.md", "no citation here\n")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "never names its path" in result.stderr
    assert "not an entry point" not in result.stderr
