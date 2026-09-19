#!/usr/bin/env python3
"""Two views of one address disagree. That is a delta, not an error.

    uv run qm divergence --left <a.json> --right <b.json>
    uv run qm divergence --left <a.json> --right <b.json> --deltas

`records/DRAFT-a-disagreement-is-a-delta.md` is the decision. This is the
mechanism, and the four properties it has to hold are that record's, restated
here only as the reason each line of code is the way it is.

NEITHER VALUE IS DISCARDED. A comparison that returned a winner would throw away
the losing value at exactly the moment somebody wants to see it. Every
divergence carries both, and which view said which.

IDENTITY IS THE ADDRESS PLUS THE FIELD, NEVER THE TIME. `delta_name` is derived
from those two and nothing else, so re-running detection over an unresolved
disagreement produces the same name. A detector that keyed on the run would open
one row per sync, and a queue that grows on a timer is a queue nobody reads.

DETECTION NEVER SETS A PHASE PAST `brainstorm`. Noticing that two values differ
is not deciding anything about them.

CONVERGENCE IS REPORTED, NOT CONCLUDED. When two values agree again this says so
and closes nothing. It cannot tell whether a person acted or whether one side
re-synced, and `complete` is a claim that work was done.

WHICH FIELDS ARE COMPARED IS A DECLARATION. Passing two whole documents and
diffing everything would open a delta on every field the two systems
legitimately hold differently -- each one's own "when I last looked" timestamp
first. `fields` is given by the caller, and getting that list wrong is the
failure mode the record names.

WHAT THIS CANNOT SEE. Which value is right. It has no opinion, by design, and
adding one would be the rejected alternative arriving as an implementation
detail. It also cannot see a disagreement about something only one side holds:
a field absent from a view is reported as missing rather than as a difference,
because "we disagree" and "one of us has never heard of this" are different
facts and a queue that conflates them is one nobody can triage.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ci"))

from addresses import parse  # noqa: E402

SCHEMA = 1

# The phase a newly detected disagreement opens at. Named rather than inlined,
# because the record's third property is exactly that this value is not a
# knob: anything further along asserts somebody looked.
OPENING_PHASE = "brainstorm"
DELTA_TYPE = "reconcile"

MISSING = object()

_UNSAFE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class Divergence:
    """One field, one address, two views that do not agree."""

    address: str
    field: str
    left_view: str
    right_view: str
    left: Any
    right: Any

    @property
    def missing(self) -> str | None:
        """Which side has never heard of this field, if either.

        A different fact from a disagreement, and kept separate so a triage
        queue can tell "we differ" from "one of us has no such column".
        """
        if self.left is MISSING and self.right is MISSING:
            return "both"
        if self.left is MISSING:
            return self.left_view
        if self.right is MISSING:
            return self.right_view
        return None

    def delta_name(self) -> str:
        """Deterministic in the address and the field, and in nothing else.

        Slugged, because a delta name is a short human identifier. The address
        itself is carried whole in the links, where it stays reversible -- the
        name being lossy is fine precisely because it is not the identity.
        """
        slug = _UNSAFE.sub("-", f"{self.address}/{self.field}".lower()).strip("-")
        return f"reconcile-{slug}"


def value_of(view: dict, field: str) -> Any:
    return view.get(field, MISSING)


def compare(address: str, left: dict, right: dict, fields: list[str],
            left_view: str = "left", right_view: str = "right") -> list[Divergence]:
    """Every declared field on which these two views disagree, in field order.

    Equal values produce nothing: this returns disagreements, and a caller
    wanting to know that two views agree reads the empty list.
    """
    found: list[Divergence] = []
    for field in fields:
        ours, theirs = value_of(left, field), value_of(right, field)
        if ours is MISSING and theirs is MISSING:
            continue
        if ours is not MISSING and theirs is not MISSING and ours == theirs:
            continue
        found.append(Divergence(address, field, left_view, right_view, ours, theirs))
    return found


def describe(divergence: Divergence) -> str:
    def shown(value: Any) -> str:
        return "(absent)" if value is MISSING else json.dumps(value)

    return (
        f"{divergence.left_view} says {divergence.field}={shown(divergence.left)}; "
        f"{divergence.right_view} says {shown(divergence.right)}. "
        f"Neither is treated as correct."
    )


def to_delta(divergence: Divergence, *, priority: str = "medium") -> dict:
    """The delta this disagreement is.

    The same payload shape `qmcp/cookbook/delta.py` emits, so a consumer
    ingests a reconcile delta by the path it already has: the `delta` key holds
    `ProjectDelta` columns and `project_id` remains the consumer's to resolve.
    """
    found = parse(divergence.address)
    project = found.project if found else None
    links = [{"link_type": "address", "target_id": None,
              "target_name": divergence.address}]
    return {
        "schema": SCHEMA,
        "project": project,
        "delta": {
            "name": divergence.delta_name(),
            "title": f"Reconcile {divergence.field} on {divergence.address}",
            "description": describe(divergence),
            "phase": OPENING_PHASE,
            "delta_type": DELTA_TYPE,
            "priority": priority,
        },
        "links": links,
        "divergence": {
            "address": divergence.address,
            "field": divergence.field,
            "views": {
                divergence.left_view: None if divergence.left is MISSING else divergence.left,
                divergence.right_view: None if divergence.right is MISSING else divergence.right,
            },
            "missing": divergence.missing,
        },
    }


def converged(previous: list[str], current: list[Divergence]) -> list[str]:
    """Delta names that were diverging and no longer are.

    Reported and never closed. Whether a person resolved this or one side
    re-synced is not visible from here, and `complete` is a claim about work.
    """
    still = {d.delta_name() for d in current}
    return [name for name in previous if name not in still]


def render(divergences: list[Divergence], gone: list[str]) -> str:
    out = [
        f"{len(divergences)} divergence(s). Each is a delta, and neither view "
        f"is treated as correct.",
        "",
    ]
    for divergence in divergences:
        out.append(f"  [!] {divergence.delta_name()}")
        out.append(f"      {describe(divergence)}")
        if divergence.missing:
            out.append(f"      absent from: {divergence.missing} -- not a "
                       f"disagreement about a value")
    if gone:
        out += ["", f"{len(gone)} no longer diverging:"]
        out += [f"  [=] {name}" for name in gone]
        out.append("      Reported, not closed. Whether anyone acted is not "
                   "visible from here.")
    out += [
        "",
        f"New deltas open at phase `{OPENING_PHASE}`: noticing a difference is "
        f"not deciding anything about it.",
        "This does NOT say which value is right. It has no opinion, by design.",
    ]
    return "\n".join(out)


def load(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"{path}: no view there.")
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--left", required=True, help="one view, as JSON")
    parser.add_argument("--right", required=True, help="the other view, as JSON")
    parser.add_argument("--deltas", action="store_true",
                        help="emit the delta payloads instead of the report")
    args = parser.parse_args(argv)

    left, right = load(Path(args.left)), load(Path(args.right))
    address = left.get("address") or right.get("address")
    if not address:
        raise SystemExit("neither view names an address; there is nothing to "
                         "compare them about.")
    fields = left.get("fields") or right.get("fields")
    if not fields:
        raise SystemExit(
            "neither view declares `fields`. Comparing everything opens a delta "
            "on each side's own observation timestamp, which is the failure mode "
            "records/DRAFT-a-disagreement-is-a-delta.md names."
        )

    found = compare(
        address, left.get("values") or {}, right.get("values") or {}, fields,
        left.get("view", "left"), right.get("view", "right"),
    )

    if args.deltas:
        print(json.dumps([to_delta(d) for d in found], indent=2))
        return 0

    print(render(found, converged(left.get("previous") or [], found)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
