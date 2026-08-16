"""Tests for the exception registry.

The registry's job is to be complete and to notice when it stops describing the
source. So the tests are mostly about refusing silence: an empty registry, a
missing reason, a constant that has been renamed out from under an entry.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from exceptions import REQUIRED, drift, incomplete, load, render  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def entry(**kw) -> dict:
    base = {
        "id": "an-exemption",
        "rule": "some rule",
        "enforced_by": "ci/thing.py",
        "constant": "SOME_CONSTANT",
        "scope": "a named case",
        "reason": "because of a thing",
        "removal_condition": "when the thing stops",
    }
    base.update(kw)
    return base


def registry(tmp_path: Path, entries: list[dict]) -> Path:
    import yaml
    path = tmp_path / "exception-registry.yaml"
    write(path, yaml.safe_dump({"schema": 1, "exceptions": entries}))
    return path


# --- refusing silence -------------------------------------------------------


def test_an_empty_registry_is_refused(tmp_path: Path):
    """"This corpus enforces everything" is the most flattering wrong answer."""
    path = registry(tmp_path, [])
    with pytest.raises(SystemExit):
        load(path)


def test_a_missing_registry_is_refused(tmp_path: Path):
    with pytest.raises(SystemExit):
        load(tmp_path / "nope.yaml")


@pytest.mark.parametrize("field", REQUIRED)
def test_every_required_field_is_required(field: str):
    e = entry()
    del e[field]
    assert any(field in p for p in incomplete([e]))


def test_a_removal_condition_is_required():
    """An exemption with no way out is permanent by default, and
    permanent-by-default is how a corpus stops enforcing things nobody chose."""
    e = entry()
    del e["removal_condition"]
    assert any("removal_condition" in p for p in incomplete([e]))


def test_a_duplicate_id_is_refused():
    assert any("duplicate" in p for p in incomplete([entry(), entry()]))


def test_a_complete_entry_passes():
    assert incomplete([entry()]) == []


# --- drift against the source ----------------------------------------------


def test_a_constant_that_no_longer_exists_is_reported(tmp_path: Path):
    """Caught two real errors on its first run against this corpus."""
    write(tmp_path / "ci" / "thing.py", "SOMETHING_ELSE = 1\n")
    found = drift([entry()], tmp_path)
    assert any("no longer contains" in f for f in found)


def test_a_constant_that_exists_is_clean(tmp_path: Path):
    write(tmp_path / "ci" / "thing.py", "SOME_CONSTANT = 1\n")
    assert drift([entry()], tmp_path) == []


def test_a_missing_enforcing_file_is_reported(tmp_path: Path):
    assert any("does not exist" in f for f in drift([entry()], tmp_path))


def test_an_entry_with_no_constant_is_not_drift_checked(tmp_path: Path):
    """Some exemptions are a flag rather than a constant."""
    e = entry()
    del e["constant"]
    write(tmp_path / "ci" / "thing.py", "")
    assert drift([e], tmp_path) == []


# --- what a reader is told --------------------------------------------------


def test_the_brief_form_drops_the_reasoning_and_keeps_the_scope():
    full = render([entry()], brief=False)
    brief = render([entry()], brief=True)
    assert "a named case" in brief
    assert "because of a thing" in full
    assert "because of a thing" not in brief


def test_the_output_refuses_to_read_as_permission():
    """A list of holes is an argument record, not a licence to add another."""
    assert "without the same argument" in render([entry()], brief=False)
