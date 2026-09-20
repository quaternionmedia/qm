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


def declared(record: Path = RECORD) -> dict[str, str]:
    """`{name: what it drives}` for every family §3's table declares.

    **§3'S TABLE, NOT THE WHOLE DOCUMENT.** The row pattern is a proxy — a
    backticked first cell — and scanned over the full record it matched any
    table anywhere: an adversarial pass appended an appendix table with a
    backticked cell and this function declared a seventh family, silently,
    which the roster check would then have *accepted* claims against. The
    declaring section is named in this module's own docstring, so the scan is
    bounded to it, and a family added anywhere else does not exist.
    """
    if not record.is_file():
        return {}
    text = record.read_text(encoding="utf-8")
    start = text.find("### §3")
    if start < 0:
        return {}
    end = text.find("\n### ", start + 1)
    section = text[start:end] if end > 0 else text[start:]
    return {m.group("name"): m.group("drives").strip()
            for m in FAMILY_ROW.finditer(section)}


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


def publishable(entry: dict) -> str:
    """What a repository may be called in a committed file.

    **NOT `roster.label`.** That prefers `name`, and `roster.load` merges the
    uncommitted private companion -- so on a machine that has the companion a
    private repository arrives carrying its real name, and a writer using
    `label` serialises it. This one prefers the `ref`, which is the redacted
    form and the only one a committed artifact may hold.

    `uv run qm private-names` caught exactly this: three private names reached
    `families.json` on the first write, from a helper that looked correct and
    was correct for printing to a terminal.
    """
    return entry.get("ref") or entry.get("name") or "<unnamed>"


def document(entries: list[dict], families: dict[str, str]) -> dict:
    """The families as data, for a consumer that is not this CLI.

    A SEAM, NOT AN IMPORT. `dossier` and `codecartographer` both need to reach
    the families, and neither may import this corpus to do it --
    `records/DRAFT-seams-on-standard-protocols.md` governs, and a Python import
    would make one of them depend on a governance tool to draw a picture. So
    the families are written as a file at a stable path and read as JSON.

    `unstated` is a member of the shape rather than an absence, for the reason
    the roster gives everywhere else: a consumer that had to infer it would
    infer `none`.
    """
    members: dict[str, list[str]] = {name: [] for name in families}
    unstated: list[str] = []
    for entry in entries:
        name = publishable(entry)
        family = entry.get("family")
        (members[family] if family in members else unstated).append(name)
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": str(RECORD).replace("\\", "/"),
        "reading": {
            "families_come_from": "the record, not this file -- renaming one there "
                                  "makes a roster claim stop resolving",
            "membership_is_a_claim": "stated in ci/workspace.yaml by a person, never "
                                     "inferred from a dependency graph or a commit date",
            "unstated_is_not_none": "a repository with no family has not been placed; "
                                    "nobody answered the question",
            "do_not": "read a family as a statement that anybody is working on it -- "
                      "that is `attention`, and it is a different claim",
        },
        "families": [
            {"name": name, "drives": families[name].replace("**", "").strip(),
             "members": members[name]}
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
    entries = roster.load()
    found = problems(entries, families)

    for problem in found:
        print(f"  {problem}", file=sys.stderr)
    if found:
        print(f"\nfamilies: {len(found)} problem(s).", file=sys.stderr)
        return 1

    if args.check:
        # THE SEAM FILE IS CHECKED FOR STALENESS HERE, because this is the one
        # entry registries.yml already runs and the file two repositories pin
        # was otherwise regenerated and verified by nothing a runner executes
        # -- the adversarial review's completeness finding 7. Tree-only by
        # construction: the roster, the record, and the committed file.
        committed_path = Path("families.json")
        if committed_path.is_file():
            fresh = document(entries, families)
            committed = json.loads(committed_path.read_text(encoding="utf-8"))
            fresh.pop("generated_at", None); committed.pop("generated_at", None)
            if fresh != committed:
                print("families.json no longer matches the roster and the "
                      "record. Regenerate: uv run qm families --write "
                      "families.json", file=sys.stderr)
                return 1

    if args.write:
        rendered = json.dumps(document(entries, families), indent=2)
        Path(args.write).parent.mkdir(parents=True, exist_ok=True)
        # newline="\n": a text write on Windows turns every newline into CRLF,
        # and the committed file is then a CRLF-to-LF diff on every line.
        Path(args.write).write_text(rendered + chr(10), encoding="utf-8", newline="\n")
        print(f"wrote {args.write}")
        return 0

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
