#!/usr/bin/env python3
"""Aggregate session artifacts by pattern_id into pattern-index.json.

Two-layer output — same split as governance_status.py:
  git layer   counts and caught_by: pure function of the artifact files.
              Given the same artifacts, yields the same answer forever.
              Verifiable offline; --check re-derives this layer.
  registry layer  check_exists: pure function of pattern-registry.yaml.
              Also offline and deterministic.

Unknown is a value. A pattern not in the registry writes
{"unknown": "slug not in pattern-registry.yaml"}, never false and never
omitted. A pattern with check_exists: {"unknown": ...} is treated the same as
check_exists: false by the coverage gate — both are gaps.

Usage:
    python ci/pattern_index.py --artifacts DIR --write FILE
    python ci/pattern_index.py --check FILE   # re-derive and diff the git layer
    python ci/pattern_index.py                # emit to stdout
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

CI_DIR = Path(__file__).resolve().parent
STALENESS_BUDGET_HOURS = 168


def load_artifacts(artifacts_dir: Path) -> list[dict]:
    """Load all YAML artifact files from the directory, newest first."""
    if not artifacts_dir.is_dir():
        return []
    result = []
    for p in sorted(artifacts_dir.glob("*.yaml"), reverse=True):
        try:
            doc = yaml.safe_load(p.read_text(encoding="utf-8"))
            if isinstance(doc, dict):
                doc["_source"] = str(p.name)
                result.append(doc)
        except Exception:
            pass  # malformed artifact; skip
    return result


def load_registry(ci_dir: Path) -> dict:
    path = ci_dir / "pattern-registry.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def is_unknown(value: object) -> bool:
    return isinstance(value, dict) and "unknown" in value


def aggregate(artifacts: list[dict], registry: dict) -> dict:
    """Build the patterns dict from artifacts, cross-referenced against registry."""
    registered = registry.get("patterns") or {}
    data: dict[str, dict] = {}

    for artifact in artifacts:
        adate = str(artifact.get("date", ""))
        for b in (artifact.get("breaks") or []):
            pid = b.get("pattern_id")
            if is_unknown(pid) or not isinstance(pid, str):
                continue

            if pid not in data:
                data[pid] = {
                    "count": 0,
                    "first_seen": adate,
                    "last_seen": adate,
                    "caught_by": {"mechanical-check": 0, "manual": 0, "reviewer": 0},
                    "perspectives": [],
                    # Will be set by registry cross-reference below
                    "check_exists": {"unknown": f"'{pid}' not in pattern-registry.yaml"},
                    "threshold": 3,
                }
            entry = data[pid]
            entry["count"] += 1
            if adate and (not entry["first_seen"] or adate < entry["first_seen"]):
                entry["first_seen"] = adate
            if adate and adate > entry["last_seen"]:
                entry["last_seen"] = adate

            caught = b.get("caught_by", "")
            if isinstance(caught, str) and caught in entry["caught_by"]:
                entry["caught_by"][caught] += 1

            src = artifact.get("_source", "")
            if src and src not in entry["perspectives"]:
                entry["perspectives"].append(src)

    # Registry cross-reference: set check_exists and threshold from registry
    for pid in list(data.keys()):
        if pid not in registered:
            continue
        reg = registered[pid]
        check = reg.get("check_exists")
        if check is True:
            cf = reg.get("check_file")
            data[pid]["check_exists"] = {"file": cf} if cf else True
        elif isinstance(check, str) and check.startswith("deferred-"):
            data[pid]["check_exists"] = {"deferred": check}
        else:
            data[pid]["check_exists"] = False
        data[pid]["threshold"] = reg.get("threshold", 3)

    return data


def emit_document(patterns: dict) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "staleness_budget_hours": STALENESS_BUDGET_HOURS,
        "patterns": patterns,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--artifacts", metavar="DIR",
                        default="perspectives/artifacts",
                        help="directory of session artifact YAML files")
    parser.add_argument("--write", metavar="FILE",
                        help="write the index JSON to this path")
    parser.add_argument("--check", metavar="FILE",
                        help="re-derive the git layer and diff against FILE")
    parser.add_argument("--registry-dir", metavar="DIR", default=str(CI_DIR))
    args = parser.parse_args(argv)

    reg_dir = Path(args.registry_dir)
    artifacts_dir = Path(args.artifacts)
    registry = load_registry(reg_dir)
    artifacts = load_artifacts(artifacts_dir)
    patterns = aggregate(artifacts, registry)
    doc = emit_document(patterns)

    if args.write:
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(
            f"written: {out}  ({len(patterns)} pattern(s), "
            f"{sum(1 for e in patterns.values() if e.get('check_exists') is False)} uncovered)",
            file=sys.stderr,
        )
        return 0

    if args.check:
        existing = json.loads(Path(args.check).read_text(encoding="utf-8"))
        # Compare only the git layer (counts, caught_by) — the timestamps differ
        for pid, entry in patterns.items():
            existing_entry = existing.get("patterns", {}).get(pid, {})
            if entry["count"] != existing_entry.get("count"):
                print(
                    f"check: drift on '{pid}': "
                    f"derived count={entry['count']}, "
                    f"document count={existing_entry.get('count')}",
                    file=sys.stderr,
                )
                return 1
        print("check: git layer up to date", file=sys.stderr)
        return 0

    print(json.dumps(doc, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
