#!/usr/bin/env python3
"""Write a structured session break observation.

Reads a YAML document containing a session's breaks (from stdin or --input),
validates all slugs against the registries, and writes the validated artifact.

The artifact is machine-scoped: it describes one session on one machine.
It is never committed to the corpus. The .gitignore entry for
perspectives/artifacts/ is load-bearing.

Unknown is a value. A pattern_id not in the registry, a vague avoided-path
outcome, or an invalid shape type are each written as {"unknown": reason}
rather than rejected. The artifact is written regardless; the caller sees how
many unknowns were produced.

Usage:
    python ci/session_record.py --input breaks.yaml \\
        --out perspectives/artifacts/2026-08-13-branch.yaml
    cat breaks.yaml | python ci/session_record.py \\
        --out perspectives/artifacts/2026-08-13-branch.yaml
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

CI_DIR = Path(__file__).resolve().parent

VALID_CAUGHT_BY = {"mechanical-check", "manual", "reviewer"}
VALID_REVERSIBILITY = {"low", "medium", "high"}
VALID_DECISION_PRESSURE = {"implicit", "explicit", "asked"}
# Outcomes this vague are rejected — the deflation principle applies to
# path_avoided as much as to path_taken.
VAGUE_OUTCOMES = {"no problems", "fine", "ok", "nothing", "good", ""}


def load_registry(path: Path) -> dict:
    """Load a YAML registry, returning empty dict if absent."""
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def unknown(reason: str) -> dict:
    return {"unknown": reason}


def is_unknown(value: object) -> bool:
    return isinstance(value, dict) and "unknown" in value


def _validate_path_field(path: object, field_name: str) -> dict:
    """Validate a path_taken or path_avoided mapping."""
    if not isinstance(path, dict):
        return unknown(f"{field_name} must be a mapping with action and outcome")
    result = {}
    action = (path.get("action") or "").strip()
    result["action"] = action if action else unknown("action is missing or empty")
    outcome = (path.get("outcome") or "").strip().lower()
    if not outcome or outcome in VAGUE_OUTCOMES:
        result["outcome"] = unknown(
            "outcome is missing or too vague — state specifically what happened "
            "(the deflation principle: a vague avoided-path is a second unverified claim)"
        )
    else:
        result["outcome"] = path["outcome"]
    return result


def validate_break(b: dict, pattern_reg: dict, shape_reg: dict) -> dict:
    """Validate one break mapping. Returns a dict; unknown fields flagged."""
    result: dict = {}

    # pattern_id
    pid = (b.get("pattern_id") or "").strip()
    known_patterns = (pattern_reg.get("patterns") or {})
    if not pid:
        result["pattern_id"] = unknown("missing")
    elif pid not in known_patterns:
        result["pattern_id"] = unknown(
            f"slug '{pid}' not in pattern-registry.yaml — "
            f"add it there before recording this break"
        )
    else:
        result["pattern_id"] = pid

    # clause
    result["clause"] = (b.get("clause") or "").strip() or unknown("missing")

    # caught_by
    caught = (b.get("caught_by") or "").strip()
    result["caught_by"] = caught if caught in VALID_CAUGHT_BY else unknown(
        f"'{caught}' not in {sorted(VALID_CAUGHT_BY)}"
    )

    # path_taken / path_avoided
    result["path_taken"] = _validate_path_field(b.get("path_taken"), "path_taken")
    result["path_avoided"] = _validate_path_field(b.get("path_avoided"), "path_avoided")

    # shape
    shape = b.get("shape") or {}
    if not isinstance(shape, dict):
        result["shape"] = unknown("must be a mapping with type, context, reversibility, decision_pressure")
    else:
        vsshape: dict = {}
        stype = (shape.get("type") or "").strip()
        ctx = (shape.get("context") or "").strip()
        known_shapes = (shape_reg.get("shapes") or {})

        if stype not in known_shapes:
            vsshape["type"] = unknown(
                f"'{stype}' not in shape-registry.yaml — "
                f"known: {sorted(known_shapes.keys())}"
            )
            vsshape["context"] = ctx or unknown("missing")
        else:
            vsshape["type"] = stype
            valid_contexts = known_shapes[stype].get("contexts", [])
            if not ctx:
                vsshape["context"] = unknown("missing")
            elif ctx not in valid_contexts:
                vsshape["context"] = unknown(
                    f"'{ctx}' not a known context for '{stype}'; "
                    f"valid: {valid_contexts}"
                )
            else:
                vsshape["context"] = ctx

        rev = (shape.get("reversibility") or "").strip()
        vsshape["reversibility"] = rev if rev in VALID_REVERSIBILITY else unknown(
            f"'{rev}' not in {sorted(VALID_REVERSIBILITY)}"
        )
        dp = (shape.get("decision_pressure") or "").strip()
        vsshape["decision_pressure"] = dp if dp in VALID_DECISION_PRESSURE else unknown(
            f"'{dp}' not in {sorted(VALID_DECISION_PRESSURE)}"
        )
        result["shape"] = vsshape

    # cost
    cost = b.get("cost") or {}
    commits = cost.get("commits", 0)
    result["cost"] = {
        "commits": commits if isinstance(commits, int) else unknown("must be an integer"),
        "attention": (cost.get("attention") or "").strip() or unknown("missing"),
        "time": (cost.get("time") or "").strip(),
        "agency": (cost.get("agency") or "").strip() or unknown("missing"),
    }

    return result


def build_artifact(doc: dict, pattern_reg: dict, shape_reg: dict) -> dict:
    """Validate and build the full artifact document."""
    today = date.today().isoformat()
    artifact = {
        "date": str(doc.get("date") or today),
        "branch": (doc.get("branch") or "").strip() or unknown("not provided"),
        "repo": (doc.get("repo") or "").strip() or unknown("not provided"),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "breaks": [],
        "artifacts_produced": list(doc.get("artifacts_produced") or []),
    }
    for b in (doc.get("breaks") or []):
        if isinstance(b, dict):
            artifact["breaks"].append(validate_break(b, pattern_reg, shape_reg))
    return artifact


def count_unknowns(obj: object) -> int:
    """Recursively count {"unknown": ...} values in a structure."""
    if is_unknown(obj):
        return 1
    if isinstance(obj, dict):
        return sum(count_unknowns(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_unknowns(v) for v in obj)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", "-i", metavar="FILE",
                        help="input YAML file (default: stdin)")
    parser.add_argument("--out", "-o", metavar="FILE", required=True,
                        help="output YAML artifact file")
    parser.add_argument("--registry-dir", metavar="DIR", default=str(CI_DIR),
                        help="directory containing the registry YAML files")
    args = parser.parse_args(argv)

    reg_dir = Path(args.registry_dir)
    pattern_reg = load_registry(reg_dir / "pattern-registry.yaml")
    shape_reg = load_registry(reg_dir / "shape-registry.yaml")

    if not pattern_reg:
        print(f"warning: pattern-registry.yaml not found in {reg_dir}", file=sys.stderr)
    if not shape_reg:
        print(f"warning: shape-registry.yaml not found in {reg_dir}", file=sys.stderr)

    text = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as e:
        print(f"error: invalid YAML: {e}", file=sys.stderr)
        return 1
    if not isinstance(doc, dict):
        print("error: input must be a YAML mapping", file=sys.stderr)
        return 1

    artifact = build_artifact(doc, pattern_reg, shape_reg)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.dump(artifact, allow_unicode=True, sort_keys=False), encoding="utf-8")

    n = count_unknowns(artifact)
    n_breaks = len(artifact["breaks"])
    msg = f"written: {out}  ({n_breaks} break(s)"
    if n:
        msg += f", {n} unknown field(s) — review before using"
    msg += ")"
    print(msg, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
