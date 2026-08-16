"""Tests for the ledger, and for the attribution it now requires.

The attribution tests are the point. A ledger that named a tool only when
something went wrong would let an instrument accumulate credit while shedding
responsibility -- so `tool` is required on every entry, and it has to resolve.
"""

from __future__ import annotations

import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from ledger import known_tools, problems  # noqa: E402

TOOLS = {"assistant-2026-08", "human"}


def entry(**kw):
    base = {
        "id": "2026-01-01-001", "kind": "build", "action": "a thing",
        "projected_impact": "something", "status": "closed",
        "tool": "assistant-2026-08", "outcome": "it happened",
        "failure_cost": "none", "outcome_matched_projection": True,
    }
    base.update(kw)
    return base


def test_a_complete_entry_passes():
    assert problems([entry()], TOOLS) == []


# --- attribution ------------------------------------------------------------


def test_an_entry_with_no_tool_is_refused():
    e = entry(); del e["tool"]
    assert any("tool" in p for p in problems([e], TOOLS))


def test_a_successful_entry_needs_attribution_too():
    """Equal fervor: credit is audited on the same terms as fault."""
    e = entry(failure_cost="none", outcome_matched_projection=True)
    del e["tool"]
    assert any("tool" in p for p in problems([e], TOOLS))


def test_a_tool_that_is_not_registered_is_refused():
    found = problems([entry(tool="some-unregistered-thing")], TOOLS)
    assert any("not in ci/tool-registry.yaml" in p for p in found)


def test_an_empty_registry_is_reported_rather_than_ignored():
    """Every attribution is unresolvable, which is worse than none of them."""
    found = problems([entry()], set())
    assert any("names no tools" in p for p in found)


def test_a_person_can_be_the_named_actor():
    """An entry produced without a tool must have something true to name."""
    assert problems([entry(tool="human")], TOOLS) == []


def test_the_registry_loads_and_names_the_tools_in_use():
    tools = known_tools(CI_DIR / "tool-registry.yaml")
    assert "assistant-2026-08" in tools
    assert "human" in tools


# --- the pre-existing contract ---------------------------------------------


def test_a_closed_entry_with_no_outcome_is_refused():
    e = entry(); del e["outcome"]
    assert any("outcome" in p for p in problems([e], TOOLS))


def test_a_closed_entry_with_no_failure_cost_is_refused():
    e = entry(); del e["failure_cost"]
    assert any("failure_cost" in p for p in problems([e], TOOLS))


def test_an_open_entry_needs_no_outcome():
    e = entry(status="open")
    for field in ("outcome", "failure_cost", "outcome_matched_projection"):
        e.pop(field, None)
    assert problems([e], TOOLS) == []


def test_a_duplicate_id_is_refused():
    assert any("duplicate" in p for p in problems([entry(), entry()], TOOLS))


def test_an_unknown_kind_is_refused():
    assert any("kind" in p for p in problems([entry(kind="vibes")], TOOLS))


def test_a_false_score_is_not_a_defect():
    """An honest miss is worth more than a vague hit."""
    assert problems([entry(outcome_matched_projection=False)], TOOLS) == []
