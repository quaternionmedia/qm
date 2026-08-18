"""Tests for the policy registry.

The registry exists to enforce one rule: a policy may not be held up only by a
disposable preventer. So most of these are about refusing the shapes that let
that happen quietly -- a blank detector column, an unexplained gap, a detector
naming a file that is not there.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from policies import fragile, load, problems, render  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def policy(**kw) -> dict:
    base = {
        "id": "a-policy",
        "invariant": "something must hold",
        "source": "records/DRAFT-x.md",
        "detectable": True,
        "detector": "ci/detector.py",
        "preventers": [],
    }
    base.update(kw)
    return base


def root_with(tmp_path: Path, *, detector: bool = True) -> Path:
    write(tmp_path / "records" / "DRAFT-x.md", "# a record\n")
    if detector:
        write(tmp_path / "ci" / "detector.py", "# a detector\n")
    return tmp_path


# --- the rule the registry exists for ---------------------------------------


def test_a_policy_with_only_a_preventer_is_refused(tmp_path: Path):
    """A vendor hook with nothing behind it dies with the vendor, silently."""
    root = root_with(tmp_path)
    p = policy(detector=None, preventers=["a harness hook"])
    found = problems([p], root)
    assert any("nothing durable behind them" in f for f in found)


def test_a_preventer_is_fine_when_a_detector_backs_it(tmp_path: Path):
    root = root_with(tmp_path)
    assert problems([policy(preventers=["a git hook"])], root) == []


def test_a_preventer_is_fine_when_the_gap_is_explained(tmp_path: Path):
    """`detectable: false` with a reason is an answer, not an omission."""
    root = root_with(tmp_path, detector=False)
    p = policy(detectable=False, detector=None,
               undetectable_because="the artifact is identical either way",
               preventers=["a harness hook"])
    assert problems([p], root) == []


def test_an_unexplained_undetectable_policy_is_refused(tmp_path: Path):
    """A blank reads as an oversight; the pressure is then to fill it badly."""
    root = root_with(tmp_path, detector=False)
    p = policy(detectable=False, detector=None)
    assert any("no `undetectable_because`" in f for f in problems([p], root))


def test_a_detectable_policy_with_no_detector_is_refused(tmp_path: Path):
    root = root_with(tmp_path, detector=False)
    assert any("no detector" in f for f in problems([policy(detector=None)], root))


def test_a_planned_detector_is_accepted_as_an_honest_interim(tmp_path: Path):
    root = root_with(tmp_path, detector=False)
    p = policy(detector=None, detector_planned="twenty lines, not written")
    assert problems([p], root) == []


def test_a_detector_that_does_not_exist_is_refused(tmp_path: Path):
    """The exception registry's --drift caught two of these on its first run."""
    root = root_with(tmp_path, detector=False)
    assert any("detector" in f and "does not exist" in f
               for f in problems([policy()], root))


def test_a_source_that_does_not_exist_is_refused(tmp_path: Path):
    """Three entries named a path a pending migration would create, not one the
    tree had, and --check passed because it read only the detector column."""
    root = root_with(tmp_path)
    p = policy(source="status/ledger.yaml")
    assert any("source status/ledger.yaml does not exist" in f
               for f in problems([p], root))


def test_a_source_may_carry_an_anchor_after_the_path(tmp_path: Path):
    """`ledger.yaml 2026-08-15-001` names a file and an entry within it."""
    root = root_with(tmp_path)
    write(tmp_path / "ledger.yaml", "entries: []\n")
    assert problems([policy(source="ledger.yaml 2026-08-15-001")], root) == []


def test_a_source_that_is_not_a_path_is_left_alone(tmp_path: Path):
    """A record cited by title, or a policy sourced from a conversation."""
    root = root_with(tmp_path)
    assert problems([policy(source="the charter, P12")], root) == []


# --- refusing silence -------------------------------------------------------


def test_an_empty_registry_is_refused(tmp_path: Path):
    write(tmp_path / "r.yaml", yaml.safe_dump({"schema": 1, "policies": []}))
    with pytest.raises(SystemExit):
        load(tmp_path / "r.yaml")


def test_a_missing_registry_is_refused(tmp_path: Path):
    with pytest.raises(SystemExit):
        load(tmp_path / "nope.yaml")


def test_a_duplicate_id_is_refused(tmp_path: Path):
    root = root_with(tmp_path)
    assert any("duplicate" in f for f in problems([policy(), policy()], root))


# --- what a reader is told --------------------------------------------------


def test_fragile_lists_every_policy_without_a_detector():
    entries = [policy(), policy(id="b", detector=None, detectable=False,
                                undetectable_because="no artifact")]
    assert [e["id"] for e in fragile(entries)] == ["b"]


def test_the_summary_separates_cannot_from_not_yet():
    """Grouping them would make an honest limit look like a backlog."""
    entries = [
        policy(),
        policy(id="b", detector=None, detectable=False, undetectable_because="x"),
        policy(id="c", detector=None, detector_planned="soon"),
    ]
    out = render(entries, only_fragile=False)
    assert "1 with a durable detector" in out
    assert "1 that cannot have one" in out
    assert "1 with one planned" in out


def test_the_output_says_a_preventer_is_not_durable():
    out = render([policy(preventers=["a hook"])], only_fragile=False)
    assert "disposable" in out


def test_the_check_disclaims_what_it_cannot_verify():
    """It reads whether a detector exists, never whether it detects."""
    from policies import main
    assert callable(main)
    source = (CI_DIR / "policies.py").read_text(encoding="utf-8")
    assert "nothing here reads that" in source
