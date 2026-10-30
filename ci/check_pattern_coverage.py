#!/usr/bin/env python3
"""Gate: exit non-zero if any high-frequency pattern has no mechanical check.

Reads pattern-index.json. Does NOT re-derive frequency — the document holds
the counts. If the document is stale (past its staleness_budget_hours), prints
a warning and exits 0: a stale document is an absent signal, not a green one.

Exit codes:
  0  all patterns above threshold have check_exists: true
     (or the document is absent/stale — missing is not passing)
  1  one or more patterns above threshold have check_exists false or unknown
  2  the index file is missing or unreadable

Usage:
    python ci/check_pattern_coverage.py
    python ci/check_pattern_coverage.py --index PATH/pattern-index.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent
DEFAULT_INDEX = Path("perspectives/artifacts/pattern-index.json")


def is_unknown(value: object) -> bool:
    return isinstance(value, dict) and "unknown" in value


def is_covered(check_exists: object) -> bool:
    """True only when we have positive evidence a check exists."""
    if check_exists is True:
        return True
    if isinstance(check_exists, dict) and "file" in check_exists:
        return True
    return False


def document_age_hours(generated_at: str) -> float | None:
    try:
        stamped = datetime.strptime(generated_at[:19], "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        return (datetime.now(timezone.utc) - stamped).total_seconds() / 3600
    except (ValueError, TypeError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--index", metavar="FILE", default=str(DEFAULT_INDEX),
        help="path to pattern-index.json (default: perspectives/artifacts/pattern-index.json)"
    )
    args = parser.parse_args(argv)

    index_path = Path(args.index)
    if not index_path.exists():
        print(f"pattern-index.json not found: {index_path}", file=sys.stderr)
        print("run: python ci/pattern_index.py --write <path>", file=sys.stderr)
        return 2

    try:
        doc = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"error reading {index_path}: {e}", file=sys.stderr)
        return 2

    budget = doc.get("staleness_budget_hours", 168)
    age = document_age_hours(doc.get("generated_at", ""))
    if age is not None and age > budget:
        print(
            f"warning: pattern-index.json is {age:.0f}h old "
            f"(budget {budget}h) — re-derive before acting on this result.",
            file=sys.stderr,
        )
        print(
            "exiting 0: a stale document is not a passing gate; "
            "it is a gap in visibility.",
            file=sys.stderr,
        )
        return 0

    patterns = doc.get("patterns") or {}
    gaps: list[tuple] = []

    for pid, entry in patterns.items():
        threshold = entry.get("threshold", 3)
        count = entry.get("count", 0)
        check_exists = entry.get("check_exists")
        if count >= threshold and not is_covered(check_exists):
            gaps.append((pid, count, threshold, check_exists, entry))

    if not gaps:
        n = len(patterns)
        above = sum(
            1 for e in patterns.values()
            if e.get("count", 0) >= e.get("threshold", 3)
        )
        print(
            f"coverage: ok — {n} pattern(s) tracked, "
            f"{above} above threshold, all covered"
        )
        return 0

    print(
        f"coverage: FAIL — {len(gaps)} pattern(s) above threshold "
        f"with no mechanical check\n"
    )
    for pid, count, threshold, check_exists, entry in sorted(gaps, key=lambda x: -x[1]):
        caught = entry.get("caught_by", {})
        reviewer_hits = caught.get("reviewer", 0)
        print(f"  {pid}")
        print(f"    count: {count}  (threshold: {threshold})")
        if is_unknown(check_exists):
            print(f"    check: unknown — {check_exists['unknown']}")
        else:
            print(f"    check: none")
        if reviewer_hits:
            print(
                f"    *** reached the reviewer {reviewer_hits} time(s) "
                f"— this pattern has direct toil cost ***"
            )
        if entry.get("perspectives"):
            print(f"    seen in: {', '.join(entry['perspectives'][:2])}")
        print()

    print(
        "To fix: draft a check, then in ci/pattern-registry.yaml set\n"
        "  check_exists: true\n"
        "  check_file: ci/checks/<name>.py"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
