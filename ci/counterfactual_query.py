#!/usr/bin/env python3
"""Query shape-index.json for historical instances of a given decision shape.

This is the prospective half of the loop. Before entering a situation, read
what happened last time someone was in it. The output names the path that was
taken, the path that was available, and what each cost.

Usage:
    python ci/counterfactual_query.py --type proxy-for-the-thing
    python ci/counterfactual_query.py --type proxy-for-the-thing \\
        --context verifying-a-result
    python ci/counterfactual_query.py --list
    python ci/counterfactual_query.py --from ARTIFACT  # query shapes in one artifact
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

DEFAULT_INDEX = Path("perspectives/artifacts/shape-index.json")


def is_unknown(value: object) -> bool:
    return isinstance(value, dict) and "unknown" in value


def cost_label(cost: object) -> str:
    if not isinstance(cost, dict):
        return "cost unknown"
    parts = []
    commits = cost.get("commits", 0)
    if isinstance(commits, int) and commits:
        parts.append(f"{commits} corrective commit(s)")
    attention = str(cost.get("attention", ""))
    if attention and attention not in ("low", ""):
        parts.append(f"{attention} attention")
    agency = str(cost.get("agency", ""))
    if agency and agency.lower() not in ("", "none"):
        parts.append(f"agency taken: {agency}")
    return "; ".join(parts) if parts else "low cost"


def print_instance(instance: dict, worst_date: str | None, best_date: str | None) -> None:
    label = ""
    if instance.get("date") == worst_date:
        label = "  ← worst cost"
    elif instance.get("date") == best_date:
        label = "  ← best catch"

    print(f"  {instance.get('date', '?')}  [{instance.get('caught_by', '?')}]{label}")
    print(f"  pattern:    {instance.get('pattern_id', '?')}")

    taken = instance.get("path_taken") or {}
    avoided = instance.get("path_avoided") or {}

    taken_action = taken.get("action", "?") if not is_unknown(taken) else "unknown"
    taken_outcome = taken.get("outcome", "") if not is_unknown(taken) else "unknown"
    avoided_action = avoided.get("action", "?") if not is_unknown(avoided) else "unknown"
    avoided_outcome = avoided.get("outcome", "") if not is_unknown(avoided) else "unknown"

    print(f"  took:       {taken_action}")
    if taken_outcome and not is_unknown(taken_outcome):
        print(f"  result:     {taken_outcome}")
    print(f"  could have: {avoided_action}")
    if avoided_outcome and not is_unknown(avoided_outcome):
        print(f"  would get:  {avoided_outcome}")
    print(f"  cost:       {cost_label(instance.get('cost'))}")


def load_index(index_path: Path) -> dict:
    if not index_path.exists():
        print(f"shape index not found: {index_path}", file=sys.stderr)
        print("run: python ci/shape_index.py --write <path>", file=sys.stderr)
        sys.exit(1)
    return json.loads(index_path.read_text(encoding="utf-8"))


def query_shapes(
    shapes: dict,
    stype: str,
    context: str | None,
) -> dict:
    """Return matching shape entries keyed by their index key."""
    return {
        key: entry
        for key, entry in shapes.items()
        if entry.get("type") == stype
        and (context is None or entry.get("context") == context)
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--type", "-t", metavar="TYPE")
    parser.add_argument("--context", "-c", metavar="CONTEXT")
    parser.add_argument("--list", action="store_true",
                        help="list all shapes in the index")
    parser.add_argument("--from", dest="from_artifact", metavar="ARTIFACT",
                        help="query all shapes recorded in one artifact file")
    parser.add_argument("--index", metavar="FILE", default=str(DEFAULT_INDEX))
    args = parser.parse_args(argv)

    doc = load_index(Path(args.index))
    shapes = doc.get("shapes") or {}

    if args.list:
        if not shapes:
            print("(no shapes indexed yet)")
            return 0
        # Sort by worst cost then count
        print(f"  {'Shape':<52} {'N':>3}  Worst date")
        print("  " + "-" * 66)
        for key, entry in sorted(shapes.items(), key=lambda x: -x[1]["count"]):
            worst = entry.get("worst_cost_instance", "-") or "-"
            print(f"  {key:<52} {entry['count']:>3}  {worst}")
        return 0

    if args.from_artifact:
        artifact = yaml.safe_load(
            Path(args.from_artifact).read_text(encoding="utf-8")
        )
        types_seen: set[tuple[str, str]] = set()
        for b in (artifact.get("breaks") or []):
            shape = b.get("shape") or {}
            stype = shape.get("type", "")
            ctx = shape.get("context", "")
            if stype and not is_unknown(stype):
                types_seen.add((stype, ctx))

        if not types_seen:
            print("no indexable shapes found in this artifact")
            return 0

        for stype, ctx in sorted(types_seen):
            matched = query_shapes(shapes, stype, ctx or None)
            _print_matches(matched, stype, ctx)
        return 0

    if not args.type:
        parser.print_help()
        return 1

    matched = query_shapes(shapes, args.type, args.context)
    return _print_matches(matched, args.type, args.context)


def _print_matches(matched: dict, stype: str, context: str | None) -> int:
    suffix = f" / {context}" if context else ""
    if not matched:
        print(f"no instances found for shape: {stype}{suffix}")
        return 0

    for key, entry in sorted(matched.items()):
        instances = entry.get("instances") or []
        worst_date = entry.get("worst_cost_instance")
        best_date = entry.get("best_catch_instance")
        ctx = entry.get("context", "")
        key_suffix = f" / {ctx}" if ctx else ""

        print(f"Shape: {entry.get('type', '?')}{key_suffix}  ({len(instances)} instance(s))")
        if not instances:
            print("  (no instances recorded)")
            print()
            continue

        # Sort: worst-cost first, then by date
        def _sort(i: dict) -> tuple:
            return (0 if i.get("date") == worst_date else 1, i.get("date", ""))

        for instance in sorted(instances, key=_sort):
            print()
            print_instance(instance, worst_date, best_date)
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
