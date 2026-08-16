#!/usr/bin/env python3
"""The lanes this work is separated into, so one interaction is about one thing.

    uv run qm lanes                 # every lane, what it owns, what is open
    uv run qm lanes --id usage      # one lane
    uv run qm lanes --check         # refuse a lane that is not separable
    uv run qm lanes --where <path>  # which lane owns this file

WHAT A LANE IS FOR. Not a folder and not a label: the unit an interaction can
be scoped to. A session that set out to build a policy registry also redacted a
roster, fixed a workflow runner and rewrote a retrospective. Each step followed
from the last and none of them belonged in the same conversation.

WHAT MAKES TWO LANES SEPARABLE. A distinct gate. Two lanes settled by the same
gate are one lane with two names, and `--check` refuses that -- except where a
lane explicitly has no gate of its own, which is a real answer and stated as
one.

WHAT THIS CANNOT DO. It cannot tell that a change is in the lane its author
said. `--where` reads path ownership, and paths overlap: a record about the
development loop lives in `records/`, which meta-governance owns. The lane is a
scoping decision, and declaring it is the author's job.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "ci" / "lane-registry.yaml"

REQUIRED = ("id", "name", "question", "owns", "does_not_own", "gate")


def load(path: Path = REGISTRY) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"{path}: no lane registry. The work is undifferentiated.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    lanes = data.get("lanes") or []
    if not lanes:
        raise SystemExit(f"{path}: no lanes listed. That is a claim, not an absence.")
    return lanes


def has_own_gate(lane: dict) -> bool:
    """A lane whose gate is `None...` produces evidence rather than decisions."""
    return not str(lane.get("gate", "")).strip().lower().startswith("none")


def problems(lanes: list[dict]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    gates: dict[str, str] = {}

    for lane in lanes:
        lid = lane.get("id", "<no id>")
        if lid in seen:
            found.append(f"{lid}: duplicate id")
        seen.add(lid)
        for field in REQUIRED:
            if not lane.get(field):
                found.append(f"{lid}: missing `{field}`")

        # The separability rule. Two lanes settled the same way are one lane.
        if has_own_gate(lane):
            gate = " ".join(str(lane.get("gate", "")).split())
            if gate in gates:
                found.append(
                    f"{lid}: shares a gate with {gates[gate]} -- two lanes "
                    f"settled the same way are one lane with two names"
                )
            gates[gate] = lid

    for lane in lanes:
        for path in lane.get("owns") or []:
            # A path with a placeholder names a shape rather than a file.
            if "<" in str(path) or str(path).endswith("/"):
                continue
            if not (ROOT / str(path)).exists():
                found.append(f"{lane.get('id')}: owns {path}, which is not there")
    return found


def owner_of(lanes: list[dict], target: str) -> list[str]:
    """Every lane claiming this path. More than one is a finding, not an error."""
    owners = []
    for lane in lanes:
        for path in lane.get("owns") or []:
            path = str(path).split("#")[0].strip()
            if not path or "<" in path:
                continue
            if target == path or target.startswith(path.rstrip("/") + "/"):
                owners.append(lane["id"])
                break
    return owners


def render(lanes: list[dict], only: str | None) -> str:
    rows = [x for x in lanes if not only or x["id"] == only]
    if only and not rows:
        raise SystemExit(f"{only}: no such lane. Known: "
                         f"{', '.join(x['id'] for x in lanes)}")

    out = [f"{len(lanes)} lanes. One interaction is about one of them.", ""]
    for lane in rows:
        gate = " ".join(str(lane["gate"]).split())
        out += [
            f"## {lane['name']}  ({lane['id']})",
            f"   {' '.join(str(lane['question']).split())}",
            "",
            f"   owns      {', '.join(str(p).split('#')[0].strip() for p in lane['owns'])}",
            f"   not this  {' '.join(str(lane['does_not_own']).split())}",
            f"   gate      {gate}",
        ]
        for measure in lane.get("measures") or []:
            out.append(f"   measure   {measure}")
        for item in lane.get("open") or []:
            out.append(f"   open      {' '.join(str(item).split())}")
        out.append("")

    out += [
        "A lane is separable because its gate is its own. The development loop "
        "and usage lanes",
        "have no gate: they produce evidence and surfaces for the others, and "
        "settle nothing.",
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", default=str(REGISTRY))
    parser.add_argument("--id", help="one lane")
    parser.add_argument("--where", help="which lane owns this repo-relative path")
    parser.add_argument("--check", action="store_true",
                        help="refuse a lane that is not separable from another")
    args = parser.parse_args(argv)

    lanes = load(Path(args.registry))

    if args.where:
        target = args.where.replace("\\", "/").lstrip("./")
        owners = owner_of(lanes, target)
        if not owners:
            print(f"{target}: no lane claims this path.")
            print("That is a gap in the registry, not a file that does not matter.")
            return 0
        print(f"{target}: {', '.join(owners)}")
        if len(owners) > 1:
            print("More than one lane claims it. Say which lane the change is in.")
        return 0

    if args.check:
        found = problems(lanes)
        for problem in found:
            print(f"  - {problem}", file=sys.stderr)
        if found:
            print(f"\n{len(found)} problem(s) in ci/lane-registry.yaml.", file=sys.stderr)
            return 1
        gated = sum(1 for x in lanes if has_own_gate(x))
        print(f"lanes: {len(lanes)}, {gated} with a gate of their own and "
              f"{len(lanes) - gated} producing evidence for the rest.")
        print("This does NOT mean a change is in the lane its author said -- "
              "nothing here reads that.")
        return 0

    print(render(lanes, args.id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
