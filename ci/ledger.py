#!/usr/bin/env python3
"""The ledger: every action, what it was predicted to do, and what it cost.

    uv run qm ledger              # the running list
    uv run qm ledger --check      # every closed entry is complete and scored
    uv run qm ledger --open       # what is predicted and not yet settled

WHY. A session states an intention, acts, and reports. Nothing compares the
first to the third, so an overclaim is only caught if a human happens to
remember what was promised. This file makes the prediction durable and the
comparison mechanical.

The scoring field is the point. `outcome_matched_projection` is `true`, `false`,
or `unknown`, and a `false` is not a defect -- an honest wrong prediction is
worth more than a vague right one. What is a defect is a closed entry with no
outcome, which is a prediction quietly dropped.

WHAT IT CANNOT DO. It cannot tell that a projection was vague enough to be
unfalsifiable, or that an outcome was written to match. Both are readings. It
checks that the fields exist, that closed entries are scored, and that nothing
open has been abandoned.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ledger.yaml"
TOOL_REGISTRY = ROOT / "ci" / "tool-registry.yaml"

REQUIRED = ("id", "action", "kind", "projected_impact", "status", "tool")
REQUIRED_WHEN_CLOSED = ("outcome", "failure_cost", "outcome_matched_projection")
KINDS = {"build", "fix", "document", "decide", "verify", "revert"}
STATUSES = {"open", "closed"}
SCORES = {True, False, "unknown"}


def load(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"{path}: no ledger. Nothing was recorded.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("entries") or []
    if not entries:
        raise SystemExit(f"{path}: the ledger is empty -- nothing was checked.")
    return entries


def known_tools(path: Path) -> set[str]:
    """Ids in the tool registry. Empty if it is missing, which is itself a problem."""
    if not path.is_file():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {t["id"] for t in (data.get("tools") or []) if t.get("id")}


def problems(entries: list[dict], tools: set[str] | None = None) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    if tools is not None and not tools:
        found.append(
            "ci/tool-registry.yaml names no tools -- every attribution below is "
            "unresolvable, which is the state this field exists to prevent"
        )
    for entry in entries:
        eid = entry.get("id", "<no id>")
        if eid in seen:
            found.append(f"{eid}: duplicate id")
        seen.add(eid)
        for field in REQUIRED:
            if not entry.get(field):
                found.append(f"{eid}: missing `{field}`")
        if entry.get("kind") not in KINDS:
            found.append(f"{eid}: kind {entry.get('kind')!r} is not one of {sorted(KINDS)}")
        if entry.get("status") not in STATUSES:
            found.append(f"{eid}: status {entry.get('status')!r} is not open or closed")
        # Required on every entry, not only failures. Tool authorship is
        # audited on the same terms as tool fault.
        if tools and entry.get("tool") and entry["tool"] not in tools:
            found.append(
                f"{eid}: tool {entry['tool']!r} is not in ci/tool-registry.yaml -- "
                f"an attribution that resolves to nothing cannot be audited"
            )
        if entry.get("status") == "closed":
            for field in REQUIRED_WHEN_CLOSED:
                if field not in entry or entry[field] in (None, ""):
                    found.append(f"{eid}: closed with no `{field}` -- a prediction dropped")
            score = entry.get("outcome_matched_projection")
            if field_present(entry, "outcome_matched_projection") and score not in SCORES:
                found.append(f"{eid}: score {score!r} is not true, false or unknown")
    return found


def field_present(entry: dict, name: str) -> bool:
    return name in entry and entry[name] not in (None, "")


def render(entries: list[dict], only_open: bool) -> str:
    rows = [e for e in entries if not only_open or e.get("status") == "open"]
    closed = [e for e in entries if e.get("status") == "closed"]
    missed = [e for e in closed if e.get("outcome_matched_projection") is False]

    out = [f"{len(entries)} entr(ies): {len(closed)} closed, "
           f"{len(entries) - len(closed)} open.",
           f"{len(missed)} closed entr(ies) did not match their projection.\n"]
    for entry in rows:
        mark = {"open": "[ ]", "closed": "[x]"}.get(entry.get("status"), "[?]")
        score = entry.get("outcome_matched_projection")
        tag = {True: "as predicted", False: "MISSED", "unknown": "unscored"}.get(score, "")
        out.append(f"{mark} {entry.get('id')}  {entry.get('kind')}  {tag}")
        out.append(f"      {entry.get('action')}")
        out.append(f"      projected: {entry.get('projected_impact')}")
        if entry.get("outcome"):
            out.append(f"      outcome:   {entry['outcome']}")
        if entry.get("failure_cost") and entry["failure_cost"] != "none":
            out.append(f"      cost:      {entry['failure_cost']}")
        for lesson in entry.get("lessons") or []:
            out.append(f"      lesson:    {lesson}")
        for test in entry.get("tests_generated") or []:
            out.append(f"      test:      {test}")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--path", default=str(LEDGER))
    parser.add_argument("--check", action="store_true",
                        help="fail if any entry is incomplete or a closed one is unscored")
    parser.add_argument("--open", dest="only_open", action="store_true",
                        help="only entries still predicted and unsettled")
    args = parser.parse_args(argv)

    entries = load(Path(args.path))

    if args.check:
        found = problems(entries, known_tools(TOOL_REGISTRY))
        for problem in found:
            print(f"  - {problem}", file=sys.stderr)
        if found:
            print(f"\n{len(found)} ledger problem(s). A closed entry with no outcome "
                  f"is a prediction nobody scored.", file=sys.stderr)
            return 1
        closed = sum(1 for e in entries if e.get("status") == "closed")
        print(f"ledger: {len(entries)} entries, {closed} closed and all scored.")
        print("This does NOT mean the projections were good -- nothing here reads "
              "them for vagueness, and nothing verifies that the tool named is the "
              "tool that ran.")
        return 0

    print(render(entries, args.only_open))
    return 0


if __name__ == "__main__":
    sys.exit(main())
