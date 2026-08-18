"""The lane registry, whose one structural rule is that lanes are separable.

A lane is the unit an interaction can be scoped to. What makes two of them
separable is a distinct gate: two lanes settled the same way are one lane with
two names, and the registry would then be a labelling exercise.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from lanes import has_own_gate, load, owner_of, problems, render  # noqa: E402


def lane(**kw) -> dict:
    base = {
        "id": "a-lane", "name": "A Lane", "question": "what?",
        "owns": ["ci/lanes.py"], "does_not_own": "other things",
        "gate": "a human ratifies it",
    }
    base.update(kw)
    return base


# --- separability -----------------------------------------------------------


def test_two_lanes_sharing_a_gate_are_refused():
    found = problems([lane(), lane(id="b")])
    assert any("shares a gate" in p for p in found)


def test_two_lanes_with_distinct_gates_are_fine():
    assert problems([lane(), lane(id="b", gate="a version tag")]) == []


def test_two_gateless_lanes_do_not_collide():
    """`None` is a real answer: the lane produces evidence and settles nothing.
    Two such lanes are not the same lane, so this must not fire."""
    a = lane(gate="None. It produces evidence for the others.")
    b = lane(id="b", gate="None of its own. A missing route is a defect here.")
    assert problems([a, b]) == []


@pytest.mark.parametrize(
    "gate, owns_it",
    [
        ("a human ratifies it", True),
        ("None. Produces evidence only.", False),
        ("none of its own", False),
    ],
    ids=["real-gate", "none-with-detail", "lowercase-none"],
)
def test_a_gate_of_none_is_read_as_gateless(gate, owns_it):
    assert has_own_gate(lane(gate=gate)) is owns_it


# --- completeness -----------------------------------------------------------


@pytest.mark.parametrize("field", ["id", "name", "question", "owns",
                                   "does_not_own", "gate"])
def test_a_lane_missing_a_required_field_is_refused(field):
    entry = lane()
    del entry[field]
    assert any(field in p for p in problems([entry]))


def test_a_duplicate_id_is_refused():
    assert any("duplicate" in p for p in problems([lane(), lane()]))


def test_a_lane_owning_a_path_that_is_not_there_is_refused():
    found = problems([lane(owns=["ci/not-a-real-file.py"])])
    assert any("which is not there" in p for p in found)


@pytest.mark.parametrize("path", ["project/<name> branches", "docs/", "handbook/"])
def test_a_shape_rather_than_a_file_is_not_checked(path):
    """A branch pattern and a directory are not paths to probe for."""
    assert problems([lane(owns=[path])]) == []


def test_an_empty_registry_is_refused(tmp_path: Path):
    path = tmp_path / "r.yaml"
    path.write_text(yaml.safe_dump({"schema": 1, "lanes": []}), encoding="utf-8")
    with pytest.raises(SystemExit):
        load(path)


# --- ownership --------------------------------------------------------------


def test_a_file_under_an_owned_directory_belongs_to_that_lane():
    lanes = [lane(id="docs", owns=["handbook/"])]
    assert owner_of(lanes, "handbook/gates.md") == ["docs"]


def test_a_prefix_that_is_not_a_directory_boundary_does_not_match():
    """`handbook/` must not claim `handbook-drafts/notes.md`."""
    lanes = [lane(id="docs", owns=["handbook/"])]
    assert owner_of(lanes, "handbook-drafts/notes.md") == []


def test_a_trailing_comment_in_the_path_is_stripped():
    lanes = [lane(id="meta", owns=["ledger.yaml       # what was predicted"])]
    assert owner_of(lanes, "ledger.yaml") == ["meta"]


def test_a_path_no_lane_claims_is_reported_rather_than_assigned():
    assert owner_of([lane(owns=["ci/lanes.py"])], "some/other/file.py") == []


def test_more_than_one_owner_is_returned_rather_than_picked():
    lanes = [lane(id="a", owns=["ci/"]), lane(id="b", owns=["ci/lanes.py"])]
    assert set(owner_of(lanes, "ci/lanes.py")) == {"a", "b"}


# --- the committed registry -------------------------------------------------


def test_the_real_registry_is_separable():
    assert problems(load()) == []


def test_the_real_registry_covers_the_six_lanes_that_were_asked_for():
    ids = {x["id"] for x in load()}
    assert ids == {
        "meta-governance", "governing-projects", "project-governance",
        "development-loop", "usage", "documentation",
    }


def test_the_output_says_why_a_lane_is_separable():
    """An `or` across two candidate phrases would pass on either, which is a
    test that cannot distinguish the output from half of it."""
    out = render(load(), None)
    assert "A lane is separable because its gate is its own." in out
    assert "have no gate" in out


def test_asking_for_an_unknown_lane_is_refused():
    with pytest.raises(SystemExit):
        render(load(), "no-such-lane")
