#!/usr/bin/env python3
"""What this corpus deliberately does not enforce, and why.

    uv run qm exceptions            # every exemption, with its reason
    uv run qm exceptions --brief    # the short form, for a session brief
    uv run qm exceptions --drift    # constants named here that no longer exist

WHY A SESSION NEEDS THIS. A session that arrives with no history reads
`AGENTS.md` and learns the rules. Nothing tells it which rules have holes,
where, or why — that knowledge lived in six constants inside five checks, and
in one operator's memory. So a blind session either rediscovers an exemption by
tripping over it, or reimplements a rule that was deliberately suspended.

`ci/exception-registry.yaml` is the claim. This reads it, and `--drift` compares
it against the source: a constant the registry names that no longer exists in
the file it names is an exemption that has moved, been renamed, or been quietly
dropped.

WHAT IT CANNOT DO. It cannot tell that an exemption is still justified, that its
reason is honest, or that a check honours the constant the registry attributes
to it. `--drift` finds a missing name, not a changed meaning. An exemption
widened inside a constant this still finds passes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "ci" / "exception-registry.yaml"

REQUIRED = ("id", "rule", "enforced_by", "scope", "reason", "removal_condition")


def load(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"{path}: no exception registry. Nothing is recorded.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("exceptions") or []
    if not entries:
        # An empty registry would read as "this corpus enforces everything",
        # which is the most flattering possible wrong answer.
        raise SystemExit(f"{path}: no exceptions listed. That is a claim, not an absence.")
    return entries


def incomplete(entries: list[dict]) -> list[str]:
    found = []
    seen: set[str] = set()
    for entry in entries:
        eid = entry.get("id", "<no id>")
        if eid in seen:
            found.append(f"{eid}: duplicate id")
        seen.add(eid)
        for field in REQUIRED:
            if not entry.get(field):
                found.append(f"{eid}: missing `{field}`")
    return found


def suppressed(entry: dict) -> bool:
    """Does this exemption silence a check, or only declare a known gap?

    Two different things wear the word exemption. One is code: a constant that
    makes a check skip something, and if it is renamed the exemption silently
    widens -- that is what `drift` exists to catch. The other is a gap that is
    *declared and still reported*: the check goes on failing, and the registry
    records why nobody has fixed it yet. The second has no constant to drift
    against, and giving it a fake one to satisfy the schema would be the worse
    outcome, because the only way to make the name real is to suppress the
    finding.
    """
    constant = str(entry.get("constant") or "").strip()
    return bool(constant) and not constant.lower().startswith("none")


def drift(entries: list[dict], root: Path) -> list[str]:
    """Where the registry and the source disagree about a constant."""
    found = []
    for entry in entries:
        constant, owner = entry.get("constant"), entry.get("enforced_by")
        if not constant or not owner or not suppressed(entry):
            continue
        path = root / owner
        if not path.is_file():
            found.append(f"{entry['id']}: {owner} does not exist")
            continue
        if constant not in path.read_text(encoding="utf-8", errors="replace"):
            found.append(
                f"{entry['id']}: {owner} no longer contains `{constant}` -- the "
                f"exemption has been renamed, moved, or dropped without the "
                f"registry noticing"
            )
    return found


def render(entries: list[dict], brief: bool) -> str:
    out = [f"{len(entries)} place(s) where a rule in this corpus does not apply.", ""]
    for entry in entries:
        out.append(f"  {entry['id']}")
        out.append(f"    rule       {' '.join(entry['rule'].split())}")
        out.append(f"    scope      {' '.join(entry['scope'].split())}")
        if not brief:
            out.append(f"    enforced   {entry.get('enforced_by')}"
                       + (f"  ({entry['constant']})" if entry.get("constant") else ""))
            out.append(f"    why        {' '.join(entry['reason'].split())}")
            out.append(f"    removed    {' '.join(entry['removal_condition'].split())}")
            if entry.get("announced"):
                out.append(f"    announced  {' '.join(entry['announced'].split())}")
        out.append("")
    silencing = sum(1 for e in entries if suppressed(e))
    out.append(f"{silencing} of {len(entries)} silence a check; the rest are gaps "
               f"that are declared and still reported.")
    out.append("Each is deliberate and each was argued for. None is a bug, and")
    out.append("none is permission to add another without the same argument.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", default=str(REGISTRY))
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--brief", action="store_true",
                        help="rule and scope only, for a session brief")
    parser.add_argument("--drift", action="store_true",
                        help="report constants the registry names that no longer exist")
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero on an incomplete entry or on drift")
    args = parser.parse_args(argv)

    entries = load(Path(args.registry))
    root = Path(args.root).resolve()

    if args.drift or args.check:
        problems = incomplete(entries) + drift(entries, root)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        if problems:
            print(f"\n{len(problems)} problem(s) in ci/exception-registry.yaml.",
                  file=sys.stderr)
            return 1 if args.check else 0
        print(f"exception registry: {len(entries)} entries, all complete, every "
              f"named constant still present.")
        print("This does NOT mean an exemption is still justified -- nothing here "
              "reads a reason.")
        return 0

    print(render(entries, args.brief))
    return 0


if __name__ == "__main__":
    sys.exit(main())
