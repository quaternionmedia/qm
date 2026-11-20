#!/usr/bin/env python3
"""Aggregate session artifacts by shape into shape-index.json.

The shape is the cross-temporal key: two breaks from different sessions with
nothing else in common are connected by sharing the same shape.type and
shape.context. The index carries the full path_taken and path_avoided for
every instance so that counterfactual_query.py can surface them later.

Usage:
    python ci/shape_index.py --artifacts DIR --write FILE
    python ci/shape_index.py               # emit to stdout
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

STALENESS_BUDGET_HOURS = 168


def load_artifacts(artifacts_dir: Path) -> list[dict]:
    if not artifacts_dir.is_dir():
        return []
    result = []
    for p in sorted(artifacts_dir.glob("*.yaml")):
        try:
            doc = yaml.safe_load(p.read_text(encoding="utf-8"))
            if isinstance(doc, dict):
                doc["_source"] = str(p.name)
                result.append(doc)
        except Exception:
            pass
    return result


def is_unknown(value: object) -> bool:
    return isinstance(value, dict) and "unknown" in value


def cost_score(cost: object) -> int:
    """Numeric severity score — higher is worse. Used to find worst_cost_instance."""
    if not isinstance(cost, dict):
        return 0
    score = cost.get("commits", 0) if isinstance(cost.get("commits"), int) else 0
    score += {"low": 1, "medium": 3, "high": 9}.get(str(cost.get("attention", "")), 0)
    agency = str(cost.get("agency", ""))
    if agency and agency.lower() not in ("", "none"):
        score += 5
    return score


def aggregate(artifacts: list[dict]) -> dict:
    """Build the shapes dict from artifact files."""
    shapes: dict[str, dict] = {}

    for artifact in artifacts:
        adate = str(artifact.get("date", ""))
        for b in (artifact.get("breaks") or []):
            shape = b.get("shape") or {}
            if is_unknown(shape) or not isinstance(shape, dict):
                continue
            stype = shape.get("type", "")
            ctx = shape.get("context", "")
            if is_unknown(stype) or is_unknown(ctx) or not stype:
                continue

            key = f"{stype}/{ctx}" if ctx else stype
            if key not in shapes:
                shapes[key] = {
                    "type": stype,
                    "context": ctx,
                    "count": 0,
                    "instances": [],
                    "worst_cost_instance": None,
                    "best_catch_instance": None,
                }

            entry = shapes[key]
            entry["count"] += 1
            entry["instances"].append({
                "date": adate,
                "branch": str(artifact.get("branch", "")),
                "pattern_id": b.get("pattern_id", ""),
                "caught_by": b.get("caught_by", ""),
                "path_taken": b.get("path_taken", {}),
                "path_avoided": b.get("path_avoided", {}),
                "cost": b.get("cost", {}),
                "source": artifact.get("_source", ""),
            })

    # Compute worst_cost and best_catch pointers for each shape
    for entry in shapes.values():
        instances = entry["instances"]
        if not instances:
            continue
        worst = max(instances, key=lambda i: cost_score(i.get("cost")))
        entry["worst_cost_instance"] = worst["date"]
        mechanical = [i for i in instances if i.get("caught_by") == "mechanical-check"]
        entry["best_catch_instance"] = mechanical[-1]["date"] if mechanical else None

    return shapes


def emit_document(shapes: dict) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "staleness_budget_hours": STALENESS_BUDGET_HOURS,
        "shapes": shapes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--artifacts", metavar="DIR", default="perspectives/artifacts")
    parser.add_argument("--write", metavar="FILE")
    args = parser.parse_args(argv)

    artifacts = load_artifacts(Path(args.artifacts))
    shapes = aggregate(artifacts)
    doc = emit_document(shapes)

    if args.write:
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"written: {out}  ({len(shapes)} shape(s))", file=sys.stderr)
        return 0

    print(json.dumps(doc, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
