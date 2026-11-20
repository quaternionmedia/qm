"""Tests for the config standard check and its migration mode.

Migration is tested on a fabricated tree, never on the real one: a test that
moved this repository's own files would pass once and then describe a corpus
that no longer exists.

The idempotence test is the important one. `--migrate` is a mode of a check
rather than a one-off script precisely so it can be run again, and a migration
that corrupts on a second run is a script wearing a check's name.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from config_standard import (  # noqa: E402
    MIGRATIONS, migrate, stale_references, violations,
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def tree(tmp_path: Path, **files) -> Path:
    for name, text in files.items():
        write(tmp_path / name.replace("__", "/"), text)
    return tmp_path


# --- what counts as a violation --------------------------------------------


def test_a_data_file_at_the_root_is_a_violation(tmp_path: Path):
    write(tmp_path / "gate-status.json", "{}")
    found = violations(tmp_path)
    assert any("repository root" in v for v in found)
    assert any("status/gates.yaml" in v for v in found), "it should say where it belongs"


def test_packaging_files_at_the_root_are_allowed(tmp_path: Path):
    """pyproject.toml belongs at the root by its own tool's convention."""
    write(tmp_path / "pyproject.toml", "[project]\n")
    write(tmp_path / "uv.lock", "")
    assert violations(tmp_path) == []


def test_the_machine_scoped_files_are_exempt(tmp_path: Path):
    """They are gitignored and belong in neither folder, on purpose."""
    write(tmp_path / "inventory-private.json", "{}")
    write(tmp_path / "inventory-local.json", "{}")
    assert violations(tmp_path) == []


def test_json_under_status_is_a_violation(tmp_path: Path):
    write(tmp_path / "status" / "gates.json", "{}")
    assert any("not YAML" in v for v in violations(tmp_path))


def test_json_under_ci_is_a_violation(tmp_path: Path):
    write(tmp_path / "ci" / "thing.json", "{}")
    assert any("not YAML" in v for v in violations(tmp_path))


def test_a_redundant_suffix_under_status_is_a_violation(tmp_path: Path):
    """`status/gate-status.yaml` says status twice."""
    write(tmp_path / "status" / "gate-status.yaml", "a: 1\n")
    assert any("folder already says status" in v for v in violations(tmp_path))


def test_a_conforming_tree_is_clean(tmp_path: Path):
    write(tmp_path / "status" / "gates.yaml", "a: 1\n")
    write(tmp_path / "ci" / "gate-registry.yaml", "b: 2\n")
    assert violations(tmp_path) == []


# --- stale references -------------------------------------------------------


def test_a_stale_reference_is_found(tmp_path: Path):
    write(tmp_path / "handbook" / "x.md", "read `gate-status.json` for that\n")
    assert "gate-status.json" in stale_references(tmp_path)


def test_an_already_migrated_path_is_not_reported_as_stale(tmp_path: Path):
    """`status/gates.yaml` contains `gates.yaml`; a naive search matches it."""
    write(tmp_path / "handbook" / "x.md", "read `status/gates.yaml`\n")
    assert stale_references(tmp_path) == {}


def test_the_checker_does_not_report_itself(tmp_path: Path):
    """It names both sides of every move by design."""
    write(tmp_path / "ci" / "config_standard.py", "x = 'gate-status.json'\n")
    assert stale_references(tmp_path) == {}


# --- migration --------------------------------------------------------------


def test_json_becomes_yaml_with_its_content_intact(tmp_path: Path):
    write(tmp_path / "gate-status.json", json.dumps({"schema": 1, "totals": {"built": 10}}))
    migrate(tmp_path)
    moved = tmp_path / "status" / "gates.yaml"
    assert moved.is_file()
    assert not (tmp_path / "gate-status.json").exists()
    assert yaml.safe_load(moved.read_text(encoding="utf-8")) == {
        "schema": 1, "totals": {"built": 10}}


def test_yaml_moves_without_being_reserialised(tmp_path: Path):
    """Reserialising would strip every comment, and these files are commented."""
    body = "# a comment that must survive\nschema: 1\n"
    write(tmp_path / "ledger.yaml", body)
    migrate(tmp_path)
    assert (tmp_path / "status" / "ledger.yaml").read_text(encoding="utf-8") == body


def test_references_are_rewritten(tmp_path: Path):
    write(tmp_path / "gate-status.json", "{}")
    write(tmp_path / "handbook" / "x.md", "see `gate-status.json`\n")
    migrate(tmp_path)
    assert "status/gates.yaml" in (tmp_path / "handbook" / "x.md").read_text(encoding="utf-8")


def test_migration_is_idempotent(tmp_path: Path):
    """A second run must not double-prefix a path it already rewrote."""
    write(tmp_path / "gate-status.json", json.dumps({"a": 1}))
    write(tmp_path / "handbook" / "x.md", "see `gate-status.json`\n")
    migrate(tmp_path)
    first = (tmp_path / "handbook" / "x.md").read_text(encoding="utf-8")
    migrate(tmp_path)
    assert (tmp_path / "handbook" / "x.md").read_text(encoding="utf-8") == first
    assert "status/status/" not in first


def test_migrating_a_conforming_tree_does_nothing(tmp_path: Path):
    write(tmp_path / "status" / "gates.yaml", "a: 1\n")
    assert migrate(tmp_path) == []


def test_every_migration_target_lands_under_status():
    for old, new in MIGRATIONS.items():
        assert new.startswith("status/"), old
        assert new.endswith(".yaml"), old
        assert not Path(new).stem.endswith("-status"), new
