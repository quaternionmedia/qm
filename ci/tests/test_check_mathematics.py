"""The mathematics registry checker, against registries that should fail.

**THE CHECKER WAS ROUTED INTO THE CLI AND NEVER TESTED.** It was written and
wired in one session, `uv run qm mathematics` exits zero against the real
registry, and nothing had ever seen it exit non-zero for a reason. Charter P16:
that is scaffolding, not evidence. `uv run qm posture` found it by trying to
mutate a module whose tests it could not locate.

THE TESTS WORTH READING ARE THE LAST TWO. The checker's whole purpose is to stop
the practice becoming a habit of naming things after theorems, and the two rules
that do that work are `earned` needing a measurement and `unearned` never being
empty. Everything else is shape.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

CI = Path(__file__).resolve().parent.parent


def _module():
    spec = importlib.util.spec_from_file_location(
        "check_mathematics", CI / "check_mathematics.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


check_mathematics = _module()


def entry(**over) -> dict:
    """One mapping that passes, so a test changes exactly one thing."""
    found = {
        "layer": "relations",
        "structure": "a directed graph with symmetric edges",
        "state": "earned",
        "decides": "which cycles are reported as knots and which as loops",
        "measured": "42 loops and 0 knots across 169 relations",
        "unearned": "no invariant yet forbids a knot being introduced",
        "next": "measure again after the next archive import",
    }
    found.update(over)
    return found


def registry(tmp_path: Path, *entries: dict) -> Path:
    path = tmp_path / "mathematics-registry.yaml"
    path.write_text(yaml.safe_dump({"mappings": list(entries)}),
                    encoding="utf-8")
    return path


# --- the registry has to say something ----------------------------------------


def test_a_registry_with_no_mappings_is_refused(tmp_path: Path):
    """An empty registry passes every rule below and asserts nothing, which is
    the failure this whole file exists against.

    Mutation: return no problems for an empty registry and this fails.
    """
    path = tmp_path / "mathematics-registry.yaml"
    path.write_text(yaml.safe_dump({"mappings": []}), encoding="utf-8")
    problems = check_mathematics.check(path)
    assert problems and "asserts nothing" in problems[0]


def test_a_missing_registry_is_named_rather_than_treated_as_empty(tmp_path: Path):
    problems = check_mathematics.check(tmp_path / "nothing.yaml")
    assert problems and "not there" in problems[0]


def test_a_complete_entry_passes(tmp_path: Path):
    assert check_mathematics.check(registry(tmp_path, entry())) == []


# --- every field is required, and a placeholder is not a field ----------------


@pytest.mark.parametrize("field", check_mathematics.REQUIRED)
def test_a_missing_field_is_caught(tmp_path: Path, field: str):
    """One case per field, so a gap names the field.

    Mutation: drop a name from REQUIRED and this fails for that field.
    """
    problems = check_mathematics.check(
        registry(tmp_path, entry(**{field: ""})))
    assert any(field in p for p in problems), problems


@pytest.mark.parametrize("field", ("decides", "measured", "unearned", "next"))
def test_a_one_word_answer_is_not_an_answer(tmp_path: Path, field: str):
    """A field filled in to get past the check is worse than an empty one,
    because an empty one is visible.

    Mutation: remove the length rule and this fails.
    """
    problems = check_mathematics.check(
        registry(tmp_path, entry(**{field: "yes"})))
    assert any("too short" in p for p in problems), problems


def test_two_entries_claiming_one_layer_are_caught(tmp_path: Path):
    problems = check_mathematics.check(
        registry(tmp_path, entry(), entry(structure="something else")))
    assert any("two entries claim" in p for p in problems), problems


def test_a_state_outside_the_vocabulary_is_caught(tmp_path: Path):
    problems = check_mathematics.check(
        registry(tmp_path, entry(state="promising")))
    assert any("not one of" in p for p in problems), problems


# --- a field stated twice, which YAML resolves silently -----------------------


def test_a_field_stated_twice_is_caught(tmp_path: Path):
    """**YAML KEEPS THE LAST AND SAYS NOTHING**, so a second `measured:`
    replaces the first and the checker reads a value nobody meant.

    Written as text because by the time the document is parsed the duplicate is
    gone, which is exactly the problem.

    Mutation: drop the duplicate-key scan from `check` and this fails.
    """
    path = tmp_path / "mathematics-registry.yaml"
    path.write_text(
        "mappings:\n"
        "  - layer: relations\n"
        "    structure: a directed graph\n"
        "    state: earned\n"
        "    decides: which cycles are reported as knots\n"
        "    measured: 42 loops and 0 knots across 169 relations\n"
        "    measured: nothing was measured at all\n"
        "    unearned: no invariant forbids a knot being introduced\n"
        "    next: measure again after the next import\n",
        encoding="utf-8")
    problems = check_mathematics.check(path)
    assert any("stated twice" in p for p in problems), problems


# --- the two that keep the practice honest ------------------------------------


def test_earned_without_a_measurement_is_caught(tmp_path: Path):
    """THE ONE THAT MATTERS.

    `earned` is the word that makes a mapping load-bearing. Claiming it without
    naming what measured it is how a corpus ends up naming things after
    theorems, which is the practice charter P15 exists to prevent, and this
    rule is its whole enforcement.

    Mutation: remove the earned/measured rule and this fails.
    """
    problems = check_mathematics.check(
        registry(tmp_path, entry(state="earned", measured="none")))
    assert any("names no measurement" in p for p in problems), problems


def test_earned_that_decides_nothing_is_caught(tmp_path: Path):
    problems = check_mathematics.check(
        registry(tmp_path, entry(state="earned", decides="nothing")))
    assert any("decides nothing" in p for p in problems), problems


def test_decorative_that_claims_to_decide_is_caught(tmp_path: Path):
    """Naming a port after a constant is a mnemonic. Calling it structure would
    leave the practice indistinguishable from ornament."""
    problems = check_mathematics.check(
        registry(tmp_path, entry(state="decorative",
                                 decides="which cycles are knots")))
    assert any("is decorative and claims" in p for p in problems), problems


def test_aspirational_that_names_a_measurement_is_caught(tmp_path: Path):
    """A measured mapping is earned or it failed; either way it is not still
    aspirational."""
    problems = check_mathematics.check(
        registry(tmp_path, entry(state="aspirational",
                                 measured="42 loops across 169 relations")))
    assert any("still aspirational" in p for p in problems), problems


def test_nothing_unearned_is_caught(tmp_path: Path):
    """THE OTHER ONE THAT MATTERS.

    An entry with nothing unearned is either a finished mapping, rare enough to
    be worth arguing about in a record, or somebody who stopped looking.
    Requiring it keeps the practice evolving rather than congratulating itself,
    which is why it applies even to decorative entries.

    Mutation: remove the `unearned` rule and this fails.
    """
    for empty in ("nothing", "none", "n/a"):
        problems = check_mathematics.check(
            registry(tmp_path, entry(unearned=empty)))
        assert any("stopped looking" in p for p in problems), (empty, problems)


def test_the_real_registry_passes():
    """The committed registry, through the same function CI runs.

    Not a duplicate of `uv run qm mathematics`: that asserts the exit status,
    this asserts there is nothing to report, and a checker that returned
    problems and exited zero would pass one and fail the other.
    """
    assert check_mathematics.check(CI / "mathematics-registry.yaml") == []
