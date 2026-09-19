#!/usr/bin/env python3
"""Every restatement of a record is declared, in both directions.

Org-level tooling, copied nowhere -- it reads this corpus's own layout.

WHAT THIS IS FOR. `records/DRAFT-the-read-document-governs.md` §3: an entry
point may summarize a decision a record owns, and the cost is a declaration.
The record carries a `Restated in` row naming every document that summarizes
it, and each of those documents names the record's path. A summary that exists
in only one direction is a defect.

The failure this exists for is silent by construction. `AGENTS.md` item 3 said
a pull request was opened "for human review" and that an agent must never merge,
while `records/DRAFT-version-tags-are-claims.md` §4 said `main` asserts nothing
and the human gate is the tag. Both were in the tree at the same commit, neither
looked wrong alone, no gate went red, and a session read the entry point and
built a model of the whole organisation that the record contradicted.

WHAT THIS CANNOT DO. Two limits, and they are larger than the check:

  1. **It cannot tell that a restatement and its record say different things.**
     It checks that the pair is *declared*, so the corpus knows where its copies
     are and a reader comparing them knows to look.

  2. **It cannot find an undeclared restatement.** Distinguishing a restatement
     from a citation is reading, not matching -- `README.md`'s record index
     names every record and restates none of them, and §2 asks entry points to
     cite. A check that failed on any mention would penalise exactly the
     behaviour the record wants. So the declaration is the author's act, and
     this verifies the declarations that exist rather than discovering the ones
     that do not.

Undeclared citations are therefore *listed* and never failed. A green result
asserts that every declared pair names the other, and asserts nothing about
whether the two texts agree or whether some third document restates a record in
silence. Overstating either would be the failure this corpus keeps finding in
its own tooling: a green tick standing where a reader believes something is
enforced.

Usage:
    python ci/check_restatements.py
    python ci/check_restatements.py --root . --records-dir records
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# The documents a session reads before it reads a record. The record's §2 names
# this set: a summary anywhere in here needs a declaration, because these are
# what get read first, fully, and by everyone.
ENTRY_POINTS = (
    "AGENTS.md",
    "README.md",
    "PRINCIPLES.md",
    "project-seed/ide/AGENTS.md",
)
ENTRY_POINT_GLOBS = ("handbook/**/*.md",)

# The set is a whitelist, and the two directories a reader would expect to see
# here are absent from it rather than filtered out of it:
#
#   `perspectives/` is dated, attributed and non-binding, and its own README
#   requires a Tools row. A perspective quoting a record is a citation, not a
#   restatement, and forcing declarations there would make every retrospective a
#   standing maintenance obligation on the records it discusses.
#
#   `records/` is out for a different reason: a record citing another record is
#   precedence, which README.md's "Namespaces and precedence" already governs.
#
# An exclusion list alongside a whitelist would be dead code that reads as a
# guard, which is the shape this corpus keeps finding in its own tooling. There
# is no such list here on purpose; adding one means a directory reached the
# whitelist that should not have.

# `| **Restated in** | `AGENTS.md` item 3; `project-seed/ide/AGENTS.md` item 3 |`
RESTATED_ROW = re.compile(
    r"^\|\s*\*\*Restated in\*\*\s*\|(?P<value>.*?)\|\s*$", re.MULTILINE
)
ITEM_POINTER = re.compile(r"`([^`]+)`\s+item\s+(\d+)")
BACKTICKED = re.compile(r"`(?P<path>[^`]+?\.md)`")

# A record path as it appears in prose. Deliberately unanchored, which is also
# what makes the submodule spelling work: `governance/qm/records/DRAFT-x.md`
# contains `records/DRAFT-x.md`, so the seed copies need no special case here.
# An optional `(?:governance/qm/)?` group would read as the mechanism and be
# dead -- the match happens with or without it.
RECORD_MENTION = re.compile(r"(?P<path>records/DRAFT-[A-Za-z0-9._-]+\.md)")


def normalise(path: str) -> str:
    """One spelling per file, so the two directions can be compared.

    >>> normalise("governance/qm/records/DRAFT-x.md")
    'records/DRAFT-x.md'
    >>> normalise("./AGENTS.md")
    'AGENTS.md'
    """
    text = path.strip().replace("\\", "/")
    for prefix in ("./", "governance/qm/"):
        if text.startswith(prefix):
            text = text[len(prefix):]
    return text


def declared_restatements(record_text: str) -> set[str]:
    """The documents a record says restate it.

    >>> sorted(declared_restatements("| **Restated in** | `AGENTS.md` item 3 |"))
    ['AGENTS.md']
    >>> declared_restatements("| **Status** | Proposed |")
    set()
    """
    match = RESTATED_ROW.search(record_text)
    if match is None:
        return set()
    value = match.group("value")
    if value.strip().lower() in ("", "none", "nothing", "-", "*none.*"):
        return set()
    return {normalise(m.group("path")) for m in BACKTICKED.finditer(value)}


def declared_items(record_text: str) -> set[tuple[str, int]]:
    """Every `<path> item N` a record's `Restated in` row names.

    The row often points at a numbered item rather than a whole document, and
    that number was decoration: `declared_restatements` keeps the path and
    drops it. Inserting an item into `AGENTS.md` renumbered everything below,
    and a record went on naming the item that used to carry its summary while
    this check stayed green -- it was verifying that the document cited the
    record somewhere, which was still true.

    >>> sorted(declared_items("| **Restated in** | `AGENTS.md` item 3 |"))
    [('AGENTS.md', 3)]
    """
    match = RESTATED_ROW.search(record_text)
    if match is None:
        return set()
    return {(normalise(m.group(1)), int(m.group(2)))
            for m in ITEM_POINTER.finditer(match.group("value"))}


def numbered_items(document_text: str, number: int) -> list[str]:
    """Every top-level item carrying this number, in document order.

    Plural because a page may hold more than one numbered list, and taking the
    first match is wrong: `AGENTS.md` opens with a short list of facts to
    establish and then runs a long list of rules, so "item 3" matched the
    wrong list entirely and this check reported a restatement as missing that
    was present a hundred lines further down.
    """
    lines = document_text.splitlines()
    found: list[str] = []
    for index, line in enumerate(lines):
        if not re.match(rf"^{number}\.\s", line):
            continue
        body = [line]
        for following in lines[index + 1:]:
            if re.match(r"^\d+\.\s", following):
                break
            body.append(following)
        found.append(chr(10).join(body))
    return found


def cited_records(document_text: str) -> set[str]:
    """The records a document names by path.

    >>> sorted(cited_records("see records/DRAFT-a.md and governance/qm/records/DRAFT-a.md"))
    ['records/DRAFT-a.md']
    """
    return {normalise(m.group("path")) for m in RECORD_MENTION.finditer(document_text)}


def entry_point_paths(root: Path) -> list[Path]:
    """Every entry point present on disk, deduplicated and ordered."""
    found: list[Path] = []
    seen: set[Path] = set()
    for name in ENTRY_POINTS:
        path = root / name
        if path.is_file() and path not in seen:
            seen.add(path)
            found.append(path)
    for pattern in ENTRY_POINT_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file() and path not in seen:
                seen.add(path)
                found.append(path)
    return found


def read(path: Path) -> str:
    """Read as text, tolerating whatever encoding reached the tree."""
    return path.read_text(encoding="utf-8", errors="replace")


def check(root: Path, records_dir: Path) -> tuple[list[str], list[str]]:
    """Return (problems, notes).

    `problems` fail the check. `notes` are citations nobody declared, which are
    almost always citations rather than restatements and are reported so a
    reader can see the surface, never so a run goes red for them.
    """
    problems: list[str] = []
    notes: list[str] = []

    records = sorted(records_dir.glob("DRAFT-*.md"))
    if not records:
        # An empty record set would make every check below vacuously pass, and
        # a vacuous pass is how this corpus's lint globs have failed before.
        return ([f"no DRAFT-*.md records under {records_dir} -- nothing was checked"], [])

    declared: dict[str, set[str]] = {}
    for record in records:
        rel = record.relative_to(root).as_posix()
        declared[rel] = declared_restatements(read(record))

    entry_points = entry_point_paths(root)
    if not entry_points:
        return ([f"no entry-point documents found under {root} -- nothing was checked"], [])

    cites: dict[str, set[str]] = {}
    for doc in entry_points:
        rel = doc.relative_to(root).as_posix()
        cites[rel] = cited_records(read(doc))

    # A declaration that names an item number has to point at the item that
    # actually carries the summary, not merely at a document that mentions the
    # record somewhere on the page.
    for record in records:
        rel = record.relative_to(root).as_posix()
        for document, number in declared_items(read(record)):
            path = root / document
            if not path.is_file():
                continue
            items = numbered_items(read(path), number)
            if not items:
                problems.append(
                    f"{rel} says it is restated in {document} item {number}, "
                    f"which does not exist")
            elif not any(normalise(rel) in cited_records(item) for item in items):
                problems.append(
                    f"{rel} says it is restated in {document} item {number}, "
                    f"but that item does not name it. Items renumber when one "
                    f"is inserted above them")

    # Direction one: a record names a document, and the document must name it.
    for record_rel, documents in declared.items():
        for doc_rel in documents:
            if not (root / doc_rel).is_file():
                problems.append(
                    f"{record_rel}: `Restated in` names {doc_rel}, which is not a file"
                )
                continue
            if doc_rel not in cites:
                problems.append(
                    f"{record_rel}: `Restated in` names {doc_rel}, which is not an "
                    f"entry point -- only entry points carry restatements"
                )
                continue
            if record_rel not in cites[doc_rel]:
                problems.append(
                    f"{doc_rel}: restates {record_rel} by declaration, but never "
                    f"names its path, so a reader who stops there is not told it exists"
                )

    # Direction two is informational. A citation is what §2 asks for; only the
    # author knows whether a given passage also restates. Failing here would
    # make `README.md`'s record index -- which names every record and restates
    # none -- the largest violation in the corpus.
    for doc_rel, record_paths in sorted(cites.items()):
        for record_rel in sorted(record_paths):
            if record_rel not in declared:
                problems.append(
                    f"{doc_rel}: cites {record_rel}, which is not a record here"
                )
                continue
            if doc_rel not in declared[record_rel]:
                notes.append(f"{doc_rel} cites {record_rel} (cited, not declared as restated)")

    return problems, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Every restatement of a record is declared, in both directions.",
        epilog=(
            "This checks that the pairs are declared. It cannot check that a "
            "restatement and its record agree -- see the module docstring."
        ),
    )
    parser.add_argument("--root", default=".", help="corpus root (default: cwd)")
    parser.add_argument("--records-dir", default=None, help="default: <root>/records")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    records_dir = Path(args.records_dir).resolve() if args.records_dir else root / "records"

    problems, notes = check(root, records_dir)

    if notes:
        print(f"{len(notes)} citation(s), declared as restatements by nobody:")
        for note in notes:
            print(f"  . {note}")
        print()

    if problems:
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print(
            f"\n{len(problems)} unpaired restatement(s). "
            f"See records/DRAFT-the-read-document-governs.md §3.",
            file=sys.stderr,
        )
        return 1

    print(
        "restatement check: every declared pair names the other.\n"
        "This does NOT mean they agree -- nothing here compares their text -- "
        "and it does NOT mean no document restates a record in silence."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
