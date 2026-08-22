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


# --- citing another repository in the org ----------------------------------
#
# This corpus governs every QM repository, so its records are written *about*
# them and cite their files. Before this existed those citations were reported
# as `dangling-citation` -- "which is not in the corpus" -- and three of them
# were, all resolving perfectly well one directory over. The two facts are
# different and a check that renders them identically is the unknown-as-zero
# conflation this corpus names everywhere else.


def with_roster(tmp_path: Path, names: list[str]) -> None:
    """Give the temp corpus a roster, which is where sibling names come from.

    Written in YAML flow style so the fixture is one line: the loader walks the
    parsed structure, not the text, so the two spellings are the same input.
    """
    rows = ", ".join("{name: " + name + "}" for name in names)
    write(tmp_path / "ci" / "workspace.yaml", "repositories: [" + rows + "]")


def test_a_citation_into_a_sibling_repository_is_not_called_dangling(tmp_path: Path):
    """THE ONE THAT MATTERS.

    Mutation: drop the sibling branch and this fails -- the finding reverts to
    `dangling-citation`, which tells a reader the file does not exist.
    """
    with_roster(tmp_path, ["dossier", "qmcp"])
    corpus(tmp_path, decision="1. See `dossier/tests/core/test_composition.py`.")
    found = kinds(tmp_path)
    assert "cross-repository-citation" in found
    assert "dangling-citation" not in found


def test_a_sibling_citation_is_still_reported(tmp_path: Path):
    """**REPORTED, NOT SILENCED.** A carve-out that emits nothing is
    indistinguishable from a rule nobody wrote, and the reader still has to go
    to the other repository and look.

    Mutation: `continue` without appending and this fails.
    """
    with_roster(tmp_path, ["dossier"])
    corpus(tmp_path, decision="1. See `dossier/docs/rad-commands.md`.")
    assert kinds(tmp_path).count("cross-repository-citation") == 1


def test_a_repository_not_in_the_roster_is_still_dangling(tmp_path: Path):
    """**THE ROUTE AROUND THE GUARD.** The carve-out keys on the first path
    segment, so any invented directory name would walk through it if the roster
    were not what decides. `notarepo/` is exactly the typo this check exists to
    catch, and it must not be excused for looking like a repository.

    Mutation: match any first segment rather than a roster name and this fails.
    """
    with_roster(tmp_path, ["dossier"])
    corpus(tmp_path, decision="1. See `notarepo/handbook/gone.md`.")
    found = kinds(tmp_path)
    assert "dangling-citation" in found
    assert "cross-repository-citation" not in found


def test_this_corpus_is_not_its_own_sibling(tmp_path: Path):
    """`qm` is in the roster and is the corpus being checked. Treating it as a
    sibling would excuse every broken path written as `qm/...`, which is the
    most likely way to write one.

    Mutation: keep `qm` in the sibling set and this fails.
    """
    with_roster(tmp_path, ["qm", "dossier"])
    corpus(tmp_path, decision="1. See `qm/handbook/gone.md`.")
    assert "dangling-citation" in kinds(tmp_path)


def test_no_roster_leaves_the_check_exactly_as_strict(tmp_path: Path):
    """A corpus with no readable roster must not become permissive -- a check
    that quietly relaxes when its input is missing is the failure mode this
    corpus keeps finding in its own tooling.

    Mutation: return every first segment when the roster is unreadable and this
    fails.
    """
    corpus(tmp_path, decision="1. See `dossier/tests/core/test_composition.py`.")
    assert "dangling-citation" in kinds(tmp_path)


def test_an_unparseable_roster_is_not_a_crash(tmp_path: Path):
    """The review must survive a roster somebody is midway through editing."""
    write(tmp_path / "ci" / "workspace.yaml", "repositories: [unclosed")
    corpus(tmp_path, decision="1. See `dossier/x.md`.")
    assert "dangling-citation" in kinds(tmp_path)


def test_a_roster_entry_whose_name_is_not_a_string_is_ignored(tmp_path: Path):
    """A `name:` holding a list or a mapping is a roster somebody is midway
    through editing. The walker must skip it rather than call a string method on
    it -- a review that crashes on a half-written roster is a gate that fails for
    a reason having nothing to do with the records.

    Mutation: `and` to `or` on the isinstance guard and this raises
    AttributeError instead of reporting. Found by `uv run qm mutate`, not by
    reading the function.
    """
    write(tmp_path / "ci" / "workspace.yaml",
          "repositories: [{name: [a, b]}, {name: dossier}]")
    corpus(tmp_path, decision="1. See `dossier/x.md`.")
    assert "cross-repository-citation" in kinds(tmp_path)
