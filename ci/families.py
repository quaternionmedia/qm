#!/usr/bin/env python3
"""Which repositories the org has claimed are one working system, and whether
every claim names a family the corpus actually declares.

The set of families is read from
`records/DRAFT-a-family-is-bordered-by-what-it-drives.md` §3, not kept here, so
a family renamed there is a roster claim that stops resolving here. So is the
nesting: §3's `within` column says which family sits inside which, and a member
of the inner family is a member of the outer one.

A family is a claim (`records/DRAFT-nothing-is-both-a-claim-and-its-own-evidence.md`):
it is stated by a person in `ci/workspace.yaml`, never inferred from a
dependency graph, a shared word or a commit date. A claim is one family's name
or a list of them, because a repository that drives two things is in both. An
absent `family` is *unstated*, which is not "belongs to none", so a repository
with no family is reported and never refused.

What this cannot do: tell whether a repository really belongs to the families
somebody put it in. That is the border test in §2 of the record (what the thing
drives), and reading it needs a person who knows what the code does. It also
cannot see a family member that is not in the roster at all: an estate with a
missing member and a complete one are the same shape to this tool.
`docs/ref/ci/registries.md` describes families and the seam file.

Usage:
    families.py            # what is claimed, and what is unstated
    families.py --check    # refuse a claim naming a family the record does not
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import roster  # noqa: E402

RECORD = Path("records/DRAFT-a-family-is-bordered-by-what-it-drives.md")

# A row of §3's table: the first cell is the family's name, in backticks, in
# the same shape a principle heading carries one. The `drives` column is the
# border and is prose on purpose -- it is the half no check can read.
FAMILY_ROW = re.compile(r"^\|\s*`(?P<name>[a-z][a-z0-9-]*)`\s*\|(?P<drives>[^|]*)\|", re.MULTILINE)
NAME = re.compile(r"`(?P<name>[a-z][a-z0-9-]*)`")


def _section(record: Path) -> str:
    """§3 of the record and nothing else, or "" when there is none.

    Bounded to the declaring section: the row pattern is a proxy (a backticked
    first cell) that would match any table anywhere in the record, so a family
    added anywhere else does not exist.
    """
    if not record.is_file():
        return ""
    text = record.read_text(encoding="utf-8")
    start = text.find("### §3")
    if start < 0:
        return ""
    end = text.find("\n### ", start + 1)
    return text[start:end] if end > 0 else text[start:]


def declared(record: Path = RECORD) -> dict[str, str]:
    """`{name: what it drives}` for every family §3's table declares."""
    return {m.group("name"): m.group("drives").strip()
            for m in FAMILY_ROW.finditer(_section(record))}


def within(record: Path = RECORD) -> dict[str, str | None]:
    """`{name: the family it sits within, or None}` for every declared family.

    Read from the column §3's header names `within`; a table with no such
    column declares every family at the top. A cell holding no backticked name
    is the top as well, so a dash and a blank mean the same thing.
    """
    column = None
    found: dict[str, str | None] = {}
    for line in _section(record).splitlines():
        cells = line.strip().strip("|").split("|")
        if column is None and cells[0].strip().lower() == "family":
            heads = [c.strip().lower() for c in cells]
            column = heads.index("within") if "within" in heads else -1
            continue
        row = FAMILY_ROW.match(line)
        if row is None:
            continue
        named = NAME.search(cells[column]) if column and 0 < column < len(cells) else None
        found[row.group("name")] = named.group("name") if named else None
    return found


def ancestors(name: str, parents: dict[str, str | None]) -> list[str]:
    """Every family `name` sits within, nearest first. Stops at a cycle."""
    chain: list[str] = []
    current = parents.get(name)
    while current is not None and current not in chain and current != name:
        chain.append(current)
        current = parents.get(current)
    return chain


def children(name: str, parents: dict[str, str | None]) -> list[str]:
    """The families that sit directly within `name`, in name order."""
    return sorted(child for child, parent in parents.items() if parent == name)


def nesting_problems(families: dict[str, str], parents: dict[str, str | None]) -> list[str]:
    """A `within` naming no declared family, or a family inside itself."""
    found = []
    for name, parent in sorted(parents.items()):
        if parent is None:
            continue
        if parent not in families:
            found.append(f"{RECORD}: `{name}` sits within {parent!r}, which §3 does "
                         f"not declare")
            continue
        seen = [name]
        current: str | None = parent
        while current is not None:
            if current in seen:
                found.append(f"{RECORD}: `{name}` sits within itself "
                             f"({' within '.join(seen + [current])})")
                break
            seen.append(current)
            current = parents.get(current)
    return found


def claims(entries: list[dict]) -> list[tuple[str, list[str]]]:
    """`(repository, [families])` for every roster entry, in roster order."""
    return [(roster.label(e), roster.families_of(e)) for e in entries]


def problems(entries: list[dict], families: dict[str, str],
             parents: dict[str, str | None] | None = None) -> list[str]:
    """Every claim that does not resolve, and every nesting that does not.

    Three refusals per claim: a family the record does not declare, the same
    family named twice, and a family named beside one it sits within -- the
    inner claim already places the repository in the outer family, so the
    second name says nothing and reads as if it did.
    """
    parents = parents or {}
    found = []
    if not families:
        return [f"{RECORD}: declares no families -- nothing was checked. "
                f"An empty set would let every roster claim pass."]
    found.extend(nesting_problems(families, parents))
    for name, claimed in claims(entries):
        for family in claimed:
            if family not in families:
                known = ", ".join(sorted(families))
                found.append(
                    f"{name}: claims family {family!r}, which "
                    f"{RECORD} does not declare. Declared: {known}"
                )
        repeated = sorted({f for f in claimed if claimed.count(f) > 1})
        if repeated:
            found.append(f"{name}: claims {', '.join(repeated)} more than once")
        for family in claimed:
            outer = [a for a in ancestors(family, parents) if a in claimed]
            if outer:
                found.append(
                    f"{name}: claims {family} and {', '.join(outer)}; {family} sits "
                    f"within {outer[0]}, so claiming it already places {name} there")
    return found


def publishable(entry: dict) -> str:
    """What a repository may be called in a committed file.

    Not `roster.label`: that prefers `name`, and `roster.load` merges the
    uncommitted private companion, so on a machine that has the companion a
    private repository arrives carrying its real name. This prefers the `ref`,
    the redacted form, which is the only one a committed artifact may hold.
    """
    return entry.get("ref") or entry.get("name") or "<unnamed>"


def everyone(name: str, members: dict[str, list[str]],
             parents: dict[str, str | None]) -> list[str]:
    """A family's own members, then each family within it, without repeats."""
    out: list[str] = []
    pending = [name]
    visited: set[str] = set()
    while pending:
        current = pending.pop(0)
        if current in visited:
            continue
        visited.add(current)
        out.extend(m for m in members.get(current, []) if m not in out)
        pending.extend(children(current, parents))
    return out


def document(entries: list[dict], families: dict[str, str],
             parents: dict[str, str | None] | None = None) -> dict:
    """The families as data, for a consumer that is not this CLI.

    A seam, not an import: `dossier` and `codecartographer` both read the
    families, and neither may import this corpus to do it
    (`records/DRAFT-seams-on-standard-protocols.md`). The families are written
    as a file at a stable path and read as JSON.

    `members` is who claims the family itself; `all_members` adds everyone in
    a family within it, which is the set a reader asking "who is in this
    family" means. A repository in two families is listed in both.

    `unstated` is a member of the shape rather than an absence, for the reason
    the roster gives everywhere else: a consumer that had to infer it would
    infer `none`.
    """
    parents = {name: (parents or {}).get(name) for name in families}
    members: dict[str, list[str]] = {name: [] for name in families}
    unstated: list[str] = []
    for entry in entries:
        name = publishable(entry)
        claimed = [f for f in roster.families_of(entry) if f in members]
        if not claimed:
            unstated.append(name)
        for family in claimed:
            if name not in members[family]:
                members[family].append(name)
    return {
        "schema": 2,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": str(RECORD).replace("\\", "/"),
        "reading": {
            "families_come_from": "the record, not this file -- renaming one there "
                                  "makes a roster claim stop resolving",
            "membership_is_a_claim": "stated in ci/workspace.yaml by a person, never "
                                     "inferred from a dependency graph or a commit date",
            "a_repository_may_be_in_several": "a repository that drives two things "
                                              "claims both families and is listed in each",
            "within": "a family may sit within another; `all_members` of the outer "
                      "family includes everyone in the inner one",
            "unstated_is_not_none": "a repository with no family has not been placed; "
                                    "nobody answered the question",
            "do_not": "read a family as a statement that anybody is working on it -- "
                      "that is `attention`, and it is a different claim",
        },
        "families": [
            {"name": name, "drives": families[name].replace("**", "").strip(),
             "within": parents[name],
             "subfamilies": children(name, parents),
             "members": members[name],
             "all_members": everyone(name, members, parents)}
            for name in sorted(families)
        ],
        "unstated": sorted(unstated),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero on a claim naming an undeclared family")
    parser.add_argument("--write", metavar="PATH",
                        help="write the families as JSON for a consumer to read")
    args = parser.parse_args(argv)

    families = declared()
    parents = within()
    entries = roster.load()
    found = problems(entries, families, parents)

    for problem in found:
        print(f"  {problem}", file=sys.stderr)
    if found:
        print(f"\nfamilies: {len(found)} problem(s).", file=sys.stderr)
        return 1

    if args.check:
        # The seam file is checked for staleness here, because this is the
        # entry registries.yml runs. Tree-only by construction: the roster,
        # the record, and the committed file.
        committed_path = Path("families.json")
        if committed_path.is_file():
            fresh = document(entries, families, parents)
            committed = json.loads(committed_path.read_text(encoding="utf-8"))
            fresh.pop("generated_at", None); committed.pop("generated_at", None)
            if fresh != committed:
                print("families.json no longer matches the roster and the "
                      "record. Regenerate: uv run qm families --write "
                      "families.json", file=sys.stderr)
                return 1

    if args.write:
        rendered = json.dumps(document(entries, families, parents), indent=2)
        Path(args.write).parent.mkdir(parents=True, exist_ok=True)
        # newline="\n": a text write on Windows turns every newline into CRLF,
        # and the committed file is then a CRLF-to-LF diff on every line.
        Path(args.write).write_text(rendered + chr(10), encoding="utf-8", newline="\n")
        print(f"wrote {args.write}")
        return 0

    by_family: dict[str, list[str]] = {name: [] for name in families}
    unstated: list[str] = []
    for name, claimed in claims(entries):
        for family in claimed:
            by_family[family].append(name)
        if not claimed:
            unstated.append(name)

    print(f"{len(families)} family(ies), declared in {RECORD}.")

    def show(name: str, depth: int) -> None:
        indent = "   " * depth
        drives = families[name].replace("**", "")
        print(f"\n{indent}## {name}  — drives {drives}")
        members = by_family[name]
        print(f"{indent}   in the roster: " + (", ".join(members) if members else
              "none of its own -- the family is declared and the roster claims "
              "no member directly"))
        for child in children(name, parents):
            show(child, depth + 1)

    for name in sorted(n for n in families if parents.get(n) is None):
        show(name, 0)
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
