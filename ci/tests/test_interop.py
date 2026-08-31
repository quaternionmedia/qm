"""One contract surface, one coordinate — or the surface says it disagrees.

`records/DRAFT-a-shared-tag-asserts-interoperability.md`: equal numbers assert
that these artifacts were proven to work together, and unequal ones assert
nothing about the pair. This is the check for the first half of that; the
second half — whether a repository that *claims* a version actually replayed
it — is not mechanised anywhere and the tool says so on every run.

The defect this exists against is measured rather than imagined: a publisher
governed `0.6.0` while a consumer replayed `0.4.0`, both were green, and no
artifact in the estate compared them.
"""

from __future__ import annotations

import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import interop  # noqa: E402


def surface(*versions: str) -> dict:
    """A read surface with one publisher and N implementations."""
    roles = ["publisher"] + ["implementation"] * (len(versions) - 1)
    return {
        "id": "a-surface",
        "claims": [
            {"repo": f"r{i}", "role": role, "version": v,
             "where": "f", "covers": "", "absent": False}
            for i, (role, v) in enumerate(zip(roles, versions))
        ],
    }


def test_one_coordinate_across_the_surface_is_clean():
    assert interop.problems(surface("0.6.0", "0.6.0", "0.6.0")) == []


def test_a_surface_that_disagrees_is_refused():
    """**THE DEFECT, AT THE SMALLEST SCALE THAT SHOWS IT.**

    Mutation: make `problems` return `[]` when the known versions differ and
    this fails.
    """
    found = interop.problems(surface("0.6.0", "0.4.0", "0.6.0"))
    assert found, "a surface with two versions reported clean"
    assert "disagrees" in found[0]
    assert "0.4.0" in found[0] and "0.6.0" in found[0]


def test_an_unreadable_claim_is_unknown_and_never_agreement():
    """`unknown` must not compare equal to anything. A default that read as
    agreement would make an unreadable file the quietest way to pass."""
    found = interop.problems(surface("0.6.0", interop.UNKNOWN))
    assert found, "an unknown version reported clean"
    assert "claims no version" in found[0]


def test_two_unknowns_do_not_agree_with_each_other():
    """The case a set-equality check gets wrong: `{unknown}` has one element."""
    found = interop.problems(surface(interop.UNKNOWN, interop.UNKNOWN))
    assert found, "two unknowns reported as agreement"


def test_a_missing_clone_says_so_rather_than_reporting_a_version():
    read = surface("0.6.0", interop.UNKNOWN)
    read["claims"][1]["absent"] = True
    found = interop.problems(read)
    assert any("no clone on this disk" in p for p in found)


def test_the_registry_registers_the_surface_this_estate_has():
    """A registry nobody added to is the state every registry check reports as
    clean, so the committed file is asserted rather than only its schema."""
    import yaml
    document = yaml.safe_load(interop.REGISTRY.read_text(encoding="utf-8"))
    surfaces = document["surfaces"]
    assert surfaces, "no surface registered"
    for entry in surfaces:
        assert entry.get("publisher"), f"{entry['id']} has no publisher"
        assert entry.get("implementations"), f"{entry['id']} has no implementation"
        assert entry.get("cannot_see"), f"{entry['id']} states no blind spot"
