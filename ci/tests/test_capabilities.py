"""What the capability registry refuses, and what it deliberately does not.

**THE CHECK IS NARROW ON PURPOSE AND THE TESTS SAY SO.** `ci/capabilities.py`
verifies that a declaration is *readable* -- ordered rungs, a design pointer
that resolves in this corpus, a stated limit. It verifies nothing about whether
the evidence is true, and `test_a_command_that_does_not_exist_is_not_caught`
exists to pin that rather than leave a reader to assume otherwise. A test suite
that only demonstrated the strengths would leave the gap for somebody to find at
the worst moment, which is the shape
`records/DRAFT-a-capability-has-four-phases.md` was written about.

THE MUTATIONS, per P16, quoted as they printed:

The ordered-rungs check removed, so a claim can stand above an empty rung:

    AssertionError: a claim above an unevidenced rung was accepted
    assert [] != []

`evidence_for` returning "" rather than UNKNOWN for a null pointer:

    AssertionError: a null pointer did not read as unknown
    assert '' == 'unknown'

The design-file existence check removed:

    AssertionError: a design pointer to nothing was accepted
    assert 0 == 1
     +  where 0 = len([])
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import capabilities as mod  # noqa: E402


def entry(**over) -> dict:
    """One declaration that passes, so a case can break exactly one thing."""
    base = {
        "id": "x/y", "title": "A thing", "repo": "owner/repo",
        "phase": "design", "stated_by": "Somebody", "stated_on": "2026-08-25",
        "what": "It does a thing.",
        "evidence": {"design": "README.md", "deployment": None,
                     "execution": None, "monitoring": None},
        "cannot_see": "Whether it is any good.",
    }
    base.update(over)
    return base


# --- the registry this corpus actually ships -----------------------------------


def test_the_committed_registry_is_clean():
    """The file in this repository passes its own check.

    First, because a checker green only against fixtures is a checker that has
    never met the thing it guards.
    """
    assert mod.problems(mod.load()) == []


def test_every_committed_capability_states_what_it_cannot_see():
    """The rule the gate and protocol registries carry, applied here.

    An empty one is undescribed rather than thorough.
    """
    for declared in mod.load():
        assert declared["cannot_see"].strip(), f"{declared['id']} sees everything"


# --- what it refuses ------------------------------------------------------------


def test_a_phase_that_is_not_a_rung_is_refused():
    found = mod.problems([entry(phase="shipped")])

    assert found and "is not one of" in found[0]


def test_a_claim_standing_above_an_unevidenced_rung_is_refused():
    """THE ONE THAT MATTERS.

    The rungs are ordered, so claiming `execution` while naming nothing for
    `deployment` is a ladder with a missing rung. It is not untidiness: the
    record's whole argument is that deployment is the rung that fails silently,
    and a registry that let a claim skip it would reproduce the defect it was
    written about.
    """
    found = mod.problems([entry(
        phase="execution",
        evidence={"design": "README.md", "deployment": None,
                  "execution": "owner/repo/delta/x", "monitoring": None})])

    assert found != [], "a claim above an unevidenced rung was accepted"
    assert "'deployment'" in found[0]


def test_a_design_pointer_to_nothing_is_refused():
    """The one rung that points inward, so the one that can be checked here."""
    found = mod.problems([entry(
        evidence={"design": "records/DRAFT-not-a-real-record.md"})])

    assert len(found) == 1, "a design pointer to nothing was accepted"
    assert "not a file in this corpus" in found[0]


def test_a_capability_declared_twice_is_refused():
    found = mod.problems([entry(), entry()])

    assert any("declared twice" in problem for problem in found)


@pytest.mark.parametrize("field", mod.REQUIRED)
def test_every_required_field_is_required(field: str):
    incomplete = entry()
    incomplete.pop(field)

    found = mod.problems([incomplete])

    assert found and field in found[0]


# --- what it deliberately does not refuse ---------------------------------------


def test_a_capability_that_only_reached_design_is_fine():
    """Most of this list should never climb. Clause 7: a capability may sit at
    a rung indefinitely, and that is a report rather than a fault."""
    assert mod.problems([entry(phase="design")]) == []


def test_a_null_monitoring_rung_is_fine():
    """Watching everything costs attention, which is the scarcest thing here."""
    assert mod.problems([entry(phase="execution", evidence={
        "design": "README.md", "deployment": "uv run qm capabilities",
        "execution": "owner/repo/delta/x", "monitoring": None})]) == []


def test_a_command_that_does_not_exist_is_not_caught():
    """**THE LIMIT, PINNED RATHER THAN LEFT TO BE DISCOVERED.**

    A capability claiming `deployment` and naming a command nobody can run
    passes this file completely. That is precisely the defect the record is
    about, so the gap is asserted here: if somebody later makes this file run
    the command, this test fails and they are told to delete it.
    """
    assert mod.problems([entry(phase="deployment", evidence={
        "design": "README.md",
        "deployment": "uv run qm this-command-does-not-exist"})]) == []


# --- how a rung with no pointer reads -------------------------------------------


def test_a_null_pointer_reads_as_unknown_and_never_as_false():
    """Clause 5. A thing nobody could measure must not render like a thing
    measured and found wanting."""
    declared = entry()

    assert mod.evidence_for(declared, "monitoring") == mod.UNKNOWN, (
        "a null pointer did not read as unknown")
    assert mod.evidence_for(declared, "design") == "README.md"


def test_a_missing_key_and_an_explicit_null_read_the_same():
    """Neither says the rung was checked and found wanting."""
    absent = entry(evidence={"design": "README.md"})
    explicit = entry(evidence={"design": "README.md", "monitoring": None})

    assert (mod.evidence_for(absent, "monitoring")
            == mod.evidence_for(explicit, "monitoring") == mod.UNKNOWN)


def test_the_rungs_below_a_claim_are_the_claim_and_everything_under_it():
    assert mod.reached(entry(phase="design")) == ["design"]
    assert mod.reached(entry(phase="execution")) == [
        "design", "deployment", "execution"]
    assert mod.reached(entry(phase="monitoring")) == list(mod.RUNGS)


def test_an_unreadable_phase_reaches_nothing():
    """Not everything, which is what a permissive default would give."""
    assert mod.reached(entry(phase="shipped")) == []


# --- what a person reads ---------------------------------------------------------


def test_the_rendering_says_a_pointer_is_not_a_finding():
    """The sentence that stops the table being read as a set of green ticks."""
    text = mod.render(mod.load())

    assert "where to look, never what was found" in text
    assert "does not exist passes" in text


def test_the_rendering_marks_a_rung_without_a_tick():
    """A tick would read as checked, and nothing here checks anything."""
    text = mod.render([entry(phase="design")])

    assert "design      claimed" in text
    assert "monitoring  --" in text


def test_the_rendering_is_ascii_so_a_cp1252_console_can_print_it():
    """It printed a replacement character the first time it ran.

    The same failure `dossier.cli._make_output_encodable` documents, caught
    here instead of in somebody's terminal.
    """
    mod.render(mod.load()).encode("cp1252")


def test_asking_for_one_capability_that_is_not_there_says_so():
    assert "No capability with id" in mod.render(mod.load(), only="nope/nope")
