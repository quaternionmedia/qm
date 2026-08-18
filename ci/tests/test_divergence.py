"""A disagreement is a delta, and the four properties that makes it one.

`records/DRAFT-a-disagreement-is-a-delta.md` states them; this file is what
stops them being customary. Each has its own section below, because each fails
in a different and quiet way:

  * discarding a value  -- the dashboard reads as though the views agreed;
  * keying on the run   -- the queue grows by one row per sync;
  * opening past brainstorm -- the row asserts somebody looked at it;
  * closing on convergence  -- `complete` claims work that may never have happened.

The last is the one worth writing a test for even though it feels like testing
an absence. Auto-closing is the natural thing to write, it looks tidy, and it
silently turns a re-sync into a completed piece of work.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from divergence import (  # noqa: E402
    DELTA_TYPE,
    MISSING,
    OPENING_PHASE,
    SCHEMA,
    Divergence,
    compare,
    converged,
    describe,
    main,
    render,
    to_delta,
)

ADDRESS = "quaternionmedia/qm/branch/evolve/protect-main"
FIELDS = ["phase", "head"]


def views(left: dict, right: dict, fields: list[str] | None = None):
    return compare(ADDRESS, left, right, fields or FIELDS, "dossier", "qmcp")


# --- neither value is discarded ----------------------------------------------


def test_both_values_are_carried():
    found = views({"phase": "review"}, {"phase": "implementation"})
    assert found[0].left == "review"
    assert found[0].right == "implementation"


def test_the_delta_records_which_view_said_which():
    """A reader who disagrees with a resolution has to see what was resolved
    away, and by whom."""
    payload = to_delta(views({"phase": "review"}, {"phase": "implementation"})[0])
    assert payload["divergence"]["views"] == {"dossier": "review", "qmcp": "implementation"}


def test_the_description_names_both_and_declares_no_winner():
    text = describe(views({"phase": "review"}, {"phase": "implementation"})[0])
    assert "dossier says" in text and "qmcp says" in text
    assert "Neither is treated as correct" in text


def test_agreement_produces_nothing():
    assert views({"phase": "review"}, {"phase": "review"}) == []


def test_only_declared_fields_are_compared():
    """Comparing everything opens a delta on each side's own observation
    timestamp -- the failure mode the record names."""
    found = views({"phase": "a", "seen_at": "1"}, {"phase": "a", "seen_at": "2"})
    assert found == []


# --- identity is the address and the field, never the time -------------------


def test_the_same_disagreement_produces_the_same_name():
    """Re-running detection must find the same delta, not open a second one."""
    first = views({"phase": "review"}, {"phase": "implementation"})[0]
    second = views({"phase": "review"}, {"phase": "implementation"})[0]
    assert first.delta_name() == second.delta_name()


def test_the_name_changes_with_the_field():
    found = views({"phase": "a", "head": "x"}, {"phase": "b", "head": "y"})
    assert len({d.delta_name() for d in found}) == 2


def test_the_name_changes_with_the_address():
    one = compare("o/r/branch/a", {"phase": "x"}, {"phase": "y"}, ["phase"])[0]
    two = compare("o/r/branch/b", {"phase": "x"}, {"phase": "y"}, ["phase"])[0]
    assert one.delta_name() != two.delta_name()


def test_the_name_does_not_depend_on_the_values():
    """Identity is what disagrees, not what it disagrees about. A name that
    moved with the values would open a new row each time either side changed."""
    one = views({"phase": "a"}, {"phase": "b"})[0]
    two = views({"phase": "c"}, {"phase": "d"})[0]
    assert one.delta_name() == two.delta_name()


def test_the_name_is_a_usable_identifier():
    name = views({"phase": "a"}, {"phase": "b"})[0].delta_name()
    assert name.startswith("reconcile-")
    assert " " not in name and "/" not in name


def test_the_address_survives_whole_in_the_links():
    """The name is slugged and lossy; the address is not, and it is the one
    that has to round-trip back to a ref."""
    payload = to_delta(views({"phase": "a"}, {"phase": "b"})[0])
    assert payload["links"] == [
        {"link_type": "address", "target_id": None, "target_name": ADDRESS}
    ]


# --- detection never sets a phase past brainstorm ----------------------------


def test_a_new_divergence_opens_at_brainstorm():
    """Noticing that two values differ is not deciding anything about them."""
    assert to_delta(views({"phase": "a"}, {"phase": "b"})[0])["delta"]["phase"] == "brainstorm"
    assert OPENING_PHASE == "brainstorm"


def test_the_delta_type_marks_it_as_reconciliation():
    assert to_delta(views({"phase": "a"}, {"phase": "b"})[0])["delta"]["delta_type"] == DELTA_TYPE


# --- convergence is reported, not concluded ----------------------------------


def test_a_resolved_divergence_is_reported():
    previous = [views({"phase": "a"}, {"phase": "b"})[0].delta_name()]
    assert converged(previous, []) == previous


def test_a_still_diverging_one_is_not_reported_as_resolved():
    current = views({"phase": "a"}, {"phase": "b"})
    assert converged([current[0].delta_name()], current) == []


def test_convergence_closes_nothing():
    """The test for an absence, and the one that matters. Auto-closing is the
    tidy thing to write and turns a re-sync into completed work."""
    previous = [views({"phase": "a"}, {"phase": "b"})[0].delta_name()]
    text = render([], converged(previous, []))
    assert "no longer diverging" in text
    assert "Reported, not closed" in text
    assert "complete" not in text


# --- absent is not the same fact as different --------------------------------


def test_a_field_only_one_view_holds_is_reported_as_missing():
    found = views({"phase": "a"}, {})
    assert found[0].missing == "qmcp"
    assert found[0].right is MISSING


def test_a_field_neither_view_holds_is_not_a_divergence():
    """Two systems that have both never heard of a field do not disagree."""
    assert views({}, {}) == []


def test_missing_is_distinguishable_from_a_null_value():
    """`None` is a value a system holds. Absent is a column it does not have,
    and a triage queue that conflates them cannot be triaged."""
    absent = views({"phase": "a"}, {})[0]
    held = views({"phase": "a"}, {"phase": None})[0]
    assert absent.missing == "qmcp"
    assert held.missing is None


def test_a_missing_side_renders_as_absent_rather_than_as_a_value():
    assert "(absent)" in describe(views({"phase": "a"}, {})[0])


# --- the payload a consumer ingests ------------------------------------------


def test_the_delta_row_holds_only_project_delta_columns():
    """Same contract as qmcp's delta seam, so a consumer needs no second path.
    `project_id` stays outside the row and is the consumer's to resolve."""
    payload = to_delta(views({"phase": "a"}, {"phase": "b"})[0])
    assert set(payload["delta"]) == {
        "name", "title", "description", "phase", "delta_type", "priority"}
    assert "project_id" not in payload["delta"]


def test_the_project_is_derived_from_the_address():
    payload = to_delta(views({"phase": "a"}, {"phase": "b"})[0])
    assert payload["project"] == "quaternionmedia/qm"


def test_an_unparseable_address_leaves_the_project_unset_rather_than_guessed():
    found = compare("not an address", {"phase": "a"}, {"phase": "b"}, ["phase"])[0]
    assert to_delta(found)["project"] is None


def test_the_payload_declares_its_schema():
    assert to_delta(views({"phase": "a"}, {"phase": "b"})[0])["schema"] == SCHEMA


# --- the route ---------------------------------------------------------------


def write(path: Path, body: dict) -> Path:
    path.write_text(json.dumps(body), encoding="utf-8")
    return path


def test_the_route_reports_a_divergence(tmp_path, capsys):
    left = write(tmp_path / "l.json", {"address": ADDRESS, "view": "dossier",
                                       "fields": ["phase"], "values": {"phase": "review"}})
    right = write(tmp_path / "r.json", {"view": "qmcp", "values": {"phase": "implementation"}})
    assert main(["--left", str(left), "--right", str(right)]) == 0
    out = capsys.readouterr().out
    assert "1 divergence(s)" in out
    assert "no opinion" in out


def test_the_route_refuses_when_no_fields_are_declared(tmp_path):
    left = write(tmp_path / "l.json", {"address": ADDRESS, "values": {"a": 1}})
    right = write(tmp_path / "r.json", {"values": {"a": 2}})
    with pytest.raises(SystemExit, match="fields"):
        main(["--left", str(left), "--right", str(right)])


def test_the_route_refuses_when_neither_view_names_an_address(tmp_path):
    left = write(tmp_path / "l.json", {"fields": ["a"], "values": {"a": 1}})
    right = write(tmp_path / "r.json", {"values": {"a": 2}})
    with pytest.raises(SystemExit, match="address"):
        main(["--left", str(left), "--right", str(right)])


def test_the_route_emits_ingestable_deltas(tmp_path, capsys):
    left = write(tmp_path / "l.json", {"address": ADDRESS, "fields": ["phase"],
                                       "values": {"phase": "review"}})
    right = write(tmp_path / "r.json", {"values": {"phase": "implementation"}})
    assert main(["--left", str(left), "--right", str(right), "--deltas"]) == 0
    payloads = json.loads(capsys.readouterr().out)
    assert payloads[0]["delta"]["phase"] == "brainstorm"


def test_a_missing_view_file_is_refused(tmp_path):
    left = write(tmp_path / "l.json", {"address": ADDRESS, "fields": ["a"], "values": {}})
    with pytest.raises(SystemExit):
        main(["--left", str(left), "--right", str(tmp_path / "absent.json")])


def test_a_divergence_cannot_be_edited_after_it_is_detected():
    """It is passed around as the identity of a work item. One that can be
    rewritten in flight is not an identity."""
    found = views({"phase": "a"}, {"phase": "b"})[0]
    with pytest.raises(Exception):
        found.field = "head"


def test_both_views_are_required(tmp_path):
    """One view alone cannot disagree with anything, and defaulting the other
    to empty would report every field as absent from a view nobody supplied."""
    left = write(tmp_path / "l.json", {"address": ADDRESS, "fields": ["a"], "values": {}})
    with pytest.raises(SystemExit):
        main(["--left", str(left)])
    with pytest.raises(SystemExit):
        main(["--right", str(left)])


def test_the_route_reads_the_values_rather_than_treating_them_as_empty(tmp_path, capsys):
    """Both values must reach the report. Dropping one side's values still
    yields a divergence -- of the wrong kind, reported as absent."""
    left = write(tmp_path / "l.json", {"address": ADDRESS, "view": "dossier",
                                       "fields": ["phase"], "values": {"phase": "review"}})
    right = write(tmp_path / "r.json", {"view": "qmcp",
                                        "values": {"phase": "implementation"}})
    assert main(["--left", str(left), "--right", str(right)]) == 0
    out = capsys.readouterr().out
    assert '"review"' in out and '"implementation"' in out
    assert "(absent)" not in out
