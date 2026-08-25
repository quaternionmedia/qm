#!/usr/bin/env python3
"""What each capability has reached, and what nobody has established about it.

    uv run qm capabilities                  # every capability and its rungs
    uv run qm capabilities --id qmcp/governed
    uv run qm capabilities --check          # refuse a declaration nobody could act on

A CAPABILITY IS NOT A DELTA AND NOT A PROJECT. A delta ends; a project has a
release phase. A capability is one named thing this estate can do, and it
persists after the change that introduced it closed --
`records/DRAFT-a-capability-has-four-phases.md` is the decision, and the four
rungs are stated there rather than restated here.

**THE PHASE IS A CLAIM AND THIS COMPUTES NOTHING FROM THE EVIDENCE.** That is
clause 3, inherited from the project phase ladder. A generator that read the
evidence and set the phase would delete the only signal worth having, which is
the gap between what somebody asserted and what can be checked. So this prints
both columns and never reconciles them.

WHAT `--check` REFUSES:

  * a capability whose `phase` is not one of the four rungs, or whose rungs
    below the claimed one carry no evidence pointer at all -- claiming
    `execution` while naming nothing for `design` is a ladder with a missing
    rung, and the record's ordering makes that unreadable rather than merely
    untidy;
  * a `design` pointer naming a file that is not in this corpus. The other
    three point outward -- a command in another repository, an address, a
    workflow -- and this one does not, so it is the one that can be checked
    here;
  * a capability with no `cannot_see`, which is undescribed rather than
    thorough. The same rule the gate and protocol registries carry.

WHAT IT DOES NOT REFUSE. A capability that has reached only `design`, or one
whose `monitoring` is `null`. Most of this list should never reach the top rung
-- watching everything costs attention, which is the scarcest thing here, and
clause 7 says a capability may sit at a rung indefinitely. A check that failed
on that would be a check somebody deletes.

**WHAT THIS CANNOT SEE, AND IT IS MOST OF THE POINT.** Whether any of the
evidence is true. It reads that a pointer was written down; it does not run the
command, resolve the address, or open the workflow. A capability claiming
`deployment` and naming a command that does not exist passes this file
completely -- which is precisely the defect the record was written about, so
the limit is stated here rather than discovered later. Establishing the
deployment rung is each project's own gate, published in a document a window
reads; `qmcp`'s `tests/test_declared_commands.py` is the one implementation
that exists.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "ci" / "capability-registry.yaml"

# The rungs, in order. Ordered because clause 1 says they are, and because
# `--check` reads "every rung below the claimed one" off this list.
RUNGS = ("design", "deployment", "execution", "monitoring")

REQUIRED = ("id", "title", "repo", "phase", "stated_by", "stated_on", "what",
            "evidence", "cannot_see")

UNKNOWN = "unknown"
"""What a rung with no pointer reports. **Never `false`** -- clause 5: a thing
nobody could measure must not render like a thing measured and found wanting."""


def load(path: Path = REGISTRY) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"{path}: no capability registry. Nothing is declared.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    found = data.get("capabilities") or []
    if not isinstance(found, list):
        raise SystemExit(f"{path}: `capabilities` is a list of entries.")
    return found


def reached(entry: dict) -> list[str]:
    """The rungs at or below the claimed phase. Empty for an unknown phase."""
    phase = entry.get("phase")
    if phase not in RUNGS:
        return []
    return list(RUNGS[: RUNGS.index(phase) + 1])


def evidence_for(entry: dict, rung: str) -> str:
    """The pointer written down for one rung, or `unknown`.

    `unknown` for a missing key and for an explicit `null` alike: neither says
    the rung was checked and found wanting, and the registry's comment is
    explicit that `null` is not `false`.
    """
    pointers = entry.get("evidence") or {}
    value = pointers.get(rung)
    return str(value) if value else UNKNOWN


def problems(entries: list[dict]) -> list[str]:
    """Every declaration nobody could act on, each said plainly."""
    found: list[str] = []
    seen: set[str] = set()

    for entry in entries:
        name = entry.get("id") or "<no id>"

        missing = [key for key in REQUIRED if not entry.get(key)]
        if missing:
            found.append(f"{name}: missing {', '.join(missing)}")
            continue

        if name in seen:
            found.append(f"{name}: declared twice. One capability, one entry.")
        seen.add(name)

        if entry["phase"] not in RUNGS:
            found.append(
                f"{name}: phase {entry['phase']!r} is not one of "
                f"{', '.join(RUNGS)}. A word is not a rung.")
            continue

        for rung in reached(entry):
            if evidence_for(entry, rung) == UNKNOWN:
                found.append(
                    f"{name}: claims {entry['phase']!r} and names no evidence "
                    f"for {rung!r}. The rungs are ordered, so a claim above an "
                    f"empty one cannot be read.")

        design = entry.get("evidence", {}).get("design")
        if design and not (ROOT / str(design)).exists():
            found.append(
                f"{name}: design evidence {design!r} is not a file in this "
                f"corpus. The other three rungs point outward and this one "
                f"does not, so it is the one that can be checked here.")

    return found


def render(entries: list[dict], only: str | None = None) -> str:
    lines: list[str] = []
    for entry in entries:
        if only and entry.get("id") != only:
            continue
        claimed = entry.get("phase", UNKNOWN)
        lines.append(f"{entry.get('id', '<no id>')}   [{entry.get('repo', '?')}]")
        lines.append(f"  {entry.get('title', '')}")
        lines.append(f"  claims {claimed}, stated by {entry.get('stated_by')} "
                     f"on {entry.get('stated_on')}")
        below = reached(entry)
        for rung in RUNGS:
            pointer = evidence_for(entry, rung)
            # Labelled rather than marked with a glyph. A tick would read as
            # "checked", and nothing here checks anything -- and a non-ASCII
            # mark mangles on a cp1252 console, which is how this printed the
            # first time it ran.
            mark = "claimed" if rung in below else "--"
            lines.append(f"    {rung:<11} {mark:<8} {pointer}")
        lines.append(f"  cannot see: {entry.get('cannot_see', '').strip()}")
        lines.append("")

    if not lines:
        return f"No capability with id {only!r}." if only else "Nothing declared."
    lines.append("A pointer is where to look, never what was found. Nothing "
                 "here runs a command or")
    lines.append("resolves an address, so a capability naming a command that "
                 "does not exist passes.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="refuse a declaration nobody could act on")
    parser.add_argument("--id", default=None, help="one capability")
    args = parser.parse_args(argv)

    entries = load()

    if args.check:
        found = problems(entries)
        if found:
            for line in found:
                print(f"  {line}")
            print(f"\ncapability registry: {len(found)} problem(s) in "
                  f"{len(entries)} declaration(s).")
            return 1
        print(f"capability registry: {len(entries)} declaration(s), clean.")
        return 0

    print(render(entries, only=args.id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
