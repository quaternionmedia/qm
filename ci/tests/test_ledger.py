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


# --- closing an entry -------------------------------------------------------
#
# `--close` edits the file's text rather than round-tripping it through YAML.
# A first attempt here used yaml.safe_dump and turned a four-field change into
# a 989-line diff that deleted the file's header comments, so these tests are
# mostly about what the edit must NOT touch.

import textwrap  # noqa: E402

import pytest  # noqa: E402
import yaml  # noqa: E402

from ledger import block, close  # noqa: E402

RAW = textwrap.dedent(
    """\
    # A header comment that must survive.
    #
    # A second line of it.
    schema: 1
    entries:
      - id: 2026-01-01-001
        tool: assistant-2026-08
        kind: build
        action: the first thing
        projected_impact: it will work
        outcome: it did
        failure_cost: none
        outcome_matched_projection: true
        status: closed
      - id: 2026-01-01-002
        tool: assistant-2026-08
        kind: build
        action: the second thing
        projected_impact: it will be defective
        outcome: null
        failure_cost: null
        outcome_matched_projection: null
        status: open
    """
)


def closed(raw=RAW, entry_id="2026-01-01-002", outcome="what happened",
           cost="a cycle", matched=True):
    return close(raw, entry_id, outcome, cost, matched)


def test_closing_settles_all_four_fields():
    data = yaml.safe_load(closed())
    settled = data["entries"][1]
    assert settled["status"] == "closed"
    assert settled["outcome"] == "what happened"
    assert settled["failure_cost"] == "a cycle"
    assert settled["outcome_matched_projection"] is True


def test_closing_preserves_the_header_comments():
    """safe_dump dropped these, taking the note on reconstructed entries."""
    out = closed()
    assert "# A header comment that must survive." in out
    assert "# A second line of it." in out


def test_closing_leaves_every_other_entry_byte_identical():
    before = RAW.split("\n")
    after = closed().split("\n")
    assert before[:14] == after[:14]


def test_closing_does_not_touch_another_entrys_open_fields():
    """The scan is bounded to one entry; `outcome:` appears in both."""
    raw = RAW.replace("    outcome: it did", "    outcome: null")
    data = yaml.safe_load(closed(raw=raw))
    assert data["entries"][0]["outcome"] is None


def test_a_multi_paragraph_outcome_keeps_its_paragraphs():
    """A folded scalar would rewrap a four-clause score into one line."""
    text = "(1) MATCHED.\n\n(2) MATCHED, in the predicted mode.\n\n(3) refused."
    data = yaml.safe_load(closed(outcome=text))
    assert data["entries"][1]["outcome"].strip() == text


def test_an_unknown_id_is_refused():
    with pytest.raises(SystemExit):
        closed(entry_id="2026-01-01-099")


def test_a_duplicated_id_is_refused_rather_than_guessed():
    raw = RAW + RAW.split("entries:\n")[1]
    with pytest.raises(SystemExit):
        closed(raw=raw)


def test_an_entry_missing_the_fields_is_refused():
    raw = RAW.replace("    outcome: null\n", "", 1)
    with pytest.raises(SystemExit) as exc:
        closed(raw=raw)
    assert "outcome" in str(exc.value)


def test_unknown_is_carried_through_as_a_value_not_a_boolean():
    data = yaml.safe_load(closed(matched="unknown"))
    assert data["entries"][1]["outcome_matched_projection"] == "unknown"


def test_the_block_indent_is_deeper_than_its_key():
    """A hardcoded indent produced a parse error against 4-space fields."""
    assert block("a line", "      ").splitlines()[1].startswith("      a line")


def test_an_already_closed_entry_is_refused():
    """Its outcome is a literal block; replacing the key line would leave the
    block's body behind as orphaned lines the YAML would still parse."""
    with pytest.raises(SystemExit) as exc:
        closed(entry_id="2026-01-01-001")
    assert "already closed" in str(exc.value)


def test_a_long_entry_is_still_seen_as_closed():
    """The first version of that guard scanned a fixed forty-line window. It
    passed against the short entry above and walked straight past the real one,
    whose projection block alone is longer than the window -- so the real file
    was closed twice and its outcome silently acquired an orphaned prefix."""
    padding = "\n".join(f"      line {i} of a long projection" for i in range(80))
    raw = RAW.replace("    projected_impact: it will work",
                      f"    projected_impact: |-\n{padding}")
    with pytest.raises(SystemExit) as exc:
        closed(raw=raw, entry_id="2026-01-01-001")
    assert "already closed" in str(exc.value)


def test_closing_twice_never_produces_a_prefixed_outcome():
    """The corruption itself, asserted on the value rather than on the guard."""
    once = closed()
    with pytest.raises(SystemExit):
        close(once, "2026-01-01-002", "second", "second", True)
    assert yaml.safe_load(once)["entries"][1]["outcome"] == "what happened"


def test_the_outcome_carries_no_trailing_newline():
    """`|-` rather than `|`, so the stored value is exactly what was passed."""
    data = yaml.safe_load(closed(outcome="what happened"))
    assert data["entries"][1]["outcome"] == "what happened"
