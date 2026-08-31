#!/usr/bin/env python3
"""Which repositories the org has claimed are one working system, and whether
every claim names a family the corpus actually declares.

**THE SET OF FAMILIES IS READ FROM THE RECORD, NOT KEPT HERE.** A second list
in this file would be a scope nobody checks, and this repository has now found
four of those in its own generators in a single week -- a reading budget that
omitted the charter, an index comparison whose two sets were both empty, a
document scan that skipped the reference tier, and a seed-workflow list one
short of the procedure it measured. Each was green and each described its own
scaffolding. So the families come from
`records/DRAFT-a-family-is-bordered-by-what-it-drives.md` §3, and a family
renamed there is a roster claim that stops resolving here.

A FAMILY IS A CLAIM. `records/DRAFT-nothing-is-both-a-claim-and-its-own-evidence.md`
governs: it is stated by a person in `ci/workspace.yaml`, never inferred from a
dependency graph, a shared word or a commit date. An absent `family` is
*unstated*, which is not the same as "belongs to none" -- so a repository with
no family is reported and never refused.

WHAT THIS CANNOT DO. Tell whether a repository really belongs to the family
somebody put it in. That is the border test in §2 of the record -- what the
thing drives -- and reading it needs a person who knows what the code does. It
also cannot see a family member that is not in the roster at all: an estate
with a missing member and a complete one are the same shape to this tool.

Usage:
    families.py            # what is claimed, and what is unstated
    families.py --check    # refuse a claim naming a family the record does not
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import roster  # noqa: E402

RECORD = Path("records/DRAFT-a-family-is-bordered-by-what-it-drives.md")

# A row of §3's table: the first cell is the family's name, in backticks, in
# the same shape a principle heading carries one. The `drives` column is the
# border and is prose on purpose -- it is the half no check can read.
FAMILY_ROW = re.compile(r"^\|\s*`(?P<name>[a-z][a-z0-9-]*)`\s*\|(?P<drives>[^|]*)\|", re.MULTILINE)


def declared(record: Path = RECORD) -> dict[str, str]:
    """`{name: what it drives}` for every family the record declares."""
    if not record.is_file():
        return {}
    text = record.read_text(encoding="utf-8")
    return {m.group("name"): m.group("drives").strip() for m in FAMILY_ROW.finditer(text)}


def claims(entries: list[dict]) -> list[tuple[str, str | None]]:
    """`(repository, family or None)` for every roster entry, in roster order."""
    return [(roster.label(e), e.get("family")) for e in entries]


def problems(entries: list[dict], families: dict[str, str]) -> list[str]:
    found = []
    if not families:
        return [f"{RECORD}: declares no families -- nothing was checked. "
                f"An empty set would let every roster claim pass."]
    for name, family in claims(entries):
        if family is None:
            continue
        if family not in families:
            known = ", ".join(sorted(families))
            found.append(
                f"{name}: claims family {family!r}, which "
                f"{RECORD} does not declare. Declared: {known}"
            )
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero on a claim naming an undeclared family")
    args = parser.parse_args(argv)

    families = declared()
    entries = roster.load()
    found = problems(entries, families)

    for problem in found:
        print(f"  {problem}", file=sys.stderr)
    if found:
        print(f"\nfamilies: {len(found)} problem(s).", file=sys.stderr)
        return 1

    by_family: dict[str, list[str]] = {name: [] for name in families}
    unstated: list[str] = []
    for name, family in claims(entries):
        (by_family[family] if family else unstated).append(name)

    print(f"{len(families)} family(ies), declared in {RECORD}.")
    for name in sorted(families):
        members = by_family[name]
        drives = families[name].replace("**", "")
        print(f"\n## {name}  — drives {drives}")
        print("   in the roster: " + (", ".join(members) if members else
                                      "none -- the family is declared and the roster claims no member"))
    if unstated:
        print(f"\n{len(unstated)} rostered repository(ies) claim no family. That is "
              f"*unstated*, not *none*: nobody has answered the question.")
    if not args.check:
        print("\nA family is a claim. Nothing here read a repository to see whether it "
              "belongs where somebody put it -- the border is what a thing drives, and "
              "that is a person's reading.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
