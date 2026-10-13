#!/usr/bin/env python3
"""What enforces each policy, and what survives the tool that enforces it.

    uv run qm policies            # every policy, its detector, its preventers
    uv run qm policies --check    # refuse a policy nothing durable enforces
    uv run qm policies --fragile  # only the ones a tool change would silence

THE RULE. Prevention is disposable; detection is not. A policy enforced only by
a vendor's hook dies when that vendor changes, and dies silently -- nothing
reports the absence of a hook that used to run. So a policy needs a detector
that reads an artifact, or a stated reason it cannot have one.

`detectable: false` IS AN ANSWER, NOT A GAP. Most policies here are judgement
and leave no artifact. A registry that left those blank would invite a weak
detector to fill the column, and a weak detector is worse than an honest none
because the column then reads as coverage.

WHAT THIS CANNOT DO. It cannot tell that a detector detects the thing its policy
describes. It reads whether a file exists and whether the fields are consistent.
A detector that checks the wrong property passes here -- which is exactly the
error `--drift` caught twice in the exception registry, and this check has no
equivalent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "ci" / "policy-registry.yaml"

REQUIRED = ("id", "invariant", "source", "detectable")


def load(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"{path}: no policy registry. Nothing is recorded.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("policies") or []
    if not entries:
        raise SystemExit(f"{path}: no policies listed. That is a claim, not an absence.")
    return entries


def problems(entries: list[dict], root: Path) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        pid = entry.get("id", "<no id>")
        if pid in seen:
            found.append(f"{pid}: duplicate id")
        seen.add(pid)
        for field in REQUIRED:
            if entry.get(field) is None:
                found.append(f"{pid}: missing `{field}`")

        detectable = entry.get("detectable")
        detector = entry.get("detector")
        preventers = entry.get("preventers") or []

        if detectable is False and not entry.get("undetectable_because"):
            found.append(
                f"{pid}: detectable is false with no `undetectable_because` -- "
                f"an unexplained gap reads as an oversight"
            )
        if detectable is True and not detector and not entry.get("detector_planned"):
            found.append(
                f"{pid}: detectable but no detector and no `detector_planned`"
            )
        # The rule the registry exists for.
        if preventers and not detector and detectable is not False \
                and not entry.get("detector_planned"):
            found.append(
                f"{pid}: has preventers and nothing durable behind them -- "
                f"a policy enforced only by a disposable layer dies silently"
            )
        if detector and not (root / detector).exists():
            found.append(f"{pid}: detector {detector} does not exist")

        # `source` is checked for the same reason `detector` is, and was added
        # after three entries here named a path the config migration would
        # create rather than one the tree had. The check passed, because it
        # read only the detector column -- the blind spot was the error.
        source = entry.get("source")
        if source:
            path = str(source).split()[0]
            if "/" in path and not (root / path).exists():
                found.append(f"{pid}: source {path} does not exist")
    return found


def fragile(entries: list[dict]) -> list[dict]:
    """Policies a tool change would silence: no detector, whatever the reason."""
    return [e for e in entries if not e.get("detector")]


def render(entries: list[dict], only_fragile: bool) -> str:
    rows = fragile(entries) if only_fragile else entries
    detected = sum(1 for e in entries if e.get("detector"))
    undetectable = sum(1 for e in entries if e.get("detectable") is False)
    planned = sum(1 for e in entries if not e.get("detector") and e.get("detector_planned"))

    out = [
        f"{len(entries)} policies: {detected} with a durable detector, "
        f"{undetectable} that cannot have one, {planned} with one planned.",
        "",
    ]
    for entry in rows:
        mark = "[d]" if entry.get("detector") else ("[--]" if entry.get("detectable") is False else "[ ]")
        out.append(f"  {mark} {entry['id']}")
        out.append(f"      {' '.join(entry['invariant'].split())}")
        if entry.get("detector"):
            out.append(f"      detector   {entry['detector']}")
        elif entry.get("detector_planned"):
            out.append(f"      planned    {' '.join(entry['detector_planned'].split())}")
        else:
            out.append(f"      no detector: {' '.join(entry.get('undetectable_because', '').split())}")
        for preventer in entry.get("preventers") or []:
            out.append(f"      preventer  {preventer}  (disposable)")
        out.append("")

    out += [
        "[d] a detector reads the artifact and survives a tool change",
        "[--] cannot have one, and says why",
        "[ ] neither yet",
        "",
        "A preventer is not enforcement that survives. It stops one tool doing "
        "one thing,",
        "and it goes away with that tool without announcing that it has.",
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", default=str(REGISTRY))
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--fragile", action="store_true",
                        help="only policies a tool change would silence")
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero on a policy nothing durable enforces")
    args = parser.parse_args(argv)

    entries = load(Path(args.registry))
    root = Path(args.root).resolve()

    if args.check:
        found = problems(entries, root)
        for problem in found:
            print(f"  - {problem}", file=sys.stderr)
        if found:
            print(f"\n{len(found)} problem(s) in ci/policy-registry.yaml.", file=sys.stderr)
            return 1
        print(f"policy registry: {len(entries)} policies, every one either detected "
              f"or explained.")
        print("This does NOT mean a detector detects what its policy describes -- "
              "nothing here reads that.")
        return 0

    print(render(entries, args.fragile))
    return 0


if __name__ == "__main__":
    sys.exit(main())
