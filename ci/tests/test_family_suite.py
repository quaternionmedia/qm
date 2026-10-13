"""A batch says what it established, and what it was too small to reach.

The failure this exists against is the one `qm demo` already refuses: one
window agreeing with itself, reported as agreement. Here the same shape is a
cross-family assertion evaluated over one family and printed as green.

So every tier carries its own denominator, and a tier the batch could not
evaluate is `not reached` — never passing, and never silently absent.
"""

from __future__ import annotations

import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import family_suite  # noqa: E402


def document(*families):
    return {"families": [{"name": n, "drives": "x", "members": list(m)}
                         for n, m in families]}


def ok(member="a"):
    return {"member": member, "ran": True, "passed": True, "why": ""}


def by_tier(found):
    return {t["tier"]: t for t in found}


def test_nothing_reported_reaches_nothing():
    """**THE EMPTY BATCH, WHICH IS WHERE A CHECK STOPS CHECKING.**

    Zero members ran. Every tier must say so; a `shape` tier that passed on an
    empty batch would make "all green" mean "nothing was tried".

    Mutation: make the shape tier `reached: True` unconditionally and this
    fails.
    """
    found = by_tier(family_suite.tiers(document(("core", ["a"])), {"core": []}))
    assert not found["shape"]["reached"]
    assert not found["disjoint"]["reached"]
    assert not found["cover"]["reached"]
    assert not found["contract"]["reached"]


def test_one_family_reaches_shape_and_no_further():
    """A cross-family assertion cannot be evaluated within one family."""
    found = by_tier(family_suite.tiers(
        document(("core", ["a"]), ("other", ["b"])), {"core": [ok()]}))
    assert found["shape"]["reached"]
    assert not found["disjoint"]["reached"]
    assert "1 family" in found["disjoint"]["verdict"]


def test_two_families_reach_disjointness():
    found = by_tier(family_suite.tiers(
        document(("core", ["a"]), ("other", ["b"])),
        {"core": [ok("a")], "other": [ok("b")]}))
    assert found["disjoint"]["reached"]
    assert not found["disjoint"].get("failed")


def test_a_repository_in_two_families_fails_disjointness():
    """The assertion the tier exists for, rather than the tier merely running."""
    found = by_tier(family_suite.tiers(
        document(("core", ["a", "shared"]), ("other", ["shared"])),
        {"core": [ok()], "other": [ok()]}))
    assert found["disjoint"]["reached"]
    assert found["disjoint"]["failed"]
    assert "shared" in found["disjoint"]["verdict"]


def test_cover_needs_every_declared_family_not_merely_many():
    """Three of four reporting is not cover, however many members ran."""
    found = by_tier(family_suite.tiers(
        document(("a", ["1"]), ("b", ["2"]), ("c", ["3"])),
        {"a": [ok()], "b": [ok()]}))
    assert not found["cover"]["reached"]
    assert "c" in found["cover"]["verdict"]


def test_cover_is_reached_when_every_family_reported():
    found = by_tier(family_suite.tiers(
        document(("a", ["1"]), ("b", ["2"])),
        {"a": [ok()], "b": [ok()]}))
    assert found["cover"]["reached"]


def test_contract_cannot_be_reached_without_cover():
    """It is the one tier that depends on another, and it says so rather than
    running the seam check over a partial estate."""
    found = by_tier(family_suite.tiers(
        document(("a", ["1"]), ("b", ["2"])), {"a": [ok()]}))
    assert not found["contract"]["reached"]
    assert "cover tier was not reached" in found["contract"]["verdict"]


def test_a_family_that_reported_nothing_does_not_count_toward_a_tier():
    """An entry with an empty result list is a family that was asked and had
    nothing to say. Counting it would let adding an unadopted family raise the
    tier."""
    found = by_tier(family_suite.tiers(
        document(("a", ["1"]), ("b", ["2"])),
        {"a": [ok()], "b": []}))
    assert not found["disjoint"]["reached"]
    assert not found["cover"]["reached"]


def test_a_member_with_no_suite_is_a_fact_about_the_estate():
    """Most of the performing families have never been adopted. Inventing a
    command for them would manufacture a result."""
    result = family_suite.run_member("definitely-not-a-member")
    assert result["ran"] is False
    assert "no suite" in result["why"]
