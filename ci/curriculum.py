#!/usr/bin/env python3
"""An ordered path through this corpus, and how two of them reconcile.

    uv run qm curriculum                          # the org curriculum, in order
    uv run qm curriculum --check                  # refuse a unit that misteaches
    uv run qm curriculum --merge <other.yaml>     # report what integrating costs
    uv run qm curriculum --merge <other.yaml> --write <out.yaml>

WHAT A CURRICULUM IS. An ordered list of units. Each names one document, what a
reader can do after reading it, and what must come first. It is not a summary
of the corpus and must never become one -- a unit that restates its document is
a second copy of a decision, which is the failure
`records/DRAFT-the-read-document-governs.md` is about.

WHY THE MERGE IS THE INTERESTING HALF. A project fork will teach its own
`adr/` and will want the org's path underneath it. Two curriculums therefore
have to combine, and the combination has to be:

  OPTIMISTIC   An incoming unit is accepted by default. Integration is the
               normal outcome and needs no approval per unit -- a reconciler
               that asked about every one would not be used, and an unused
               reconciler means two divergent paths and nobody reading either.

  OPTIONAL     Nothing adopts anything. Without `--write` this prints and
               writes no file, no gate requires a curriculum, and the org
               curriculum binds no project. `optional: true` in
               `ci/protocol-registry.yaml` is that, declared.

  GOVERNANCE   Optimism stops at three things, and only these three. They are
   -AWARE      refusals rather than warnings because each one produces a
               curriculum that teaches something false:

                 1. a unit citing a document that does not exist;
                 2. a unit claiming a Status its document does not carry --
                    teaching a `Draft` as settled is the corpus asserting
                    something no human ratified;
                 3. a unit teaching an org document as though a project decided
                    it. Precedence runs one way (`docs/ref/precedence.md`), and
                    a project curriculum that owns an org record inverts it.

               A CONFLICT IS NOT A REFUSAL. Two units sharing an id and
               disagreeing are reported and the base is kept, never merged
               field-by-field and never silently dropped. Someone decides.

WHAT THIS CANNOT SEE. Whether anyone learned anything. Whether the order is a
good order. Whether a unit's prose is true of the document it cites -- it reads
the document's Status and its existence, not its meaning. And a document that
should be taught and is in no unit: an incomplete curriculum and a complete one
are the same shape here.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "curriculum" / "org.yaml"

REQUIRED = ("id", "teaches", "after_this_you_can")

# `| **Status** | Proposed |` in a record's header table. Records are the only
# documents carrying one, and a unit that claims a Status for anything else is
# claiming something the document cannot support.
STATUS_ROW = re.compile(r"^\|\s*\*\*Status\*\*\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)

# Paths a project's own curriculum may claim as its own decisions. Everything
# else in a project fork is the org's, arriving by propagation.
PROJECT_OWNED = ("adr/",)

ACCEPTED, CONFLICT, REFUSED, PRESENT = "accept", "conflict", "refuse", "present"


def load(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"{path}: no curriculum there.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not data.get("units"):
        raise SystemExit(f"{path}: no units. An empty curriculum teaches nothing "
                         f"and would reconcile clean against anything.")
    return data


def declared_status(document: Path) -> str | None:
    """The Status a document carries, or None when it carries none.

    None is not `Unknown`: most documents here are not records and have no
    Status at all, which is a different fact from a record whose Status could
    not be read.
    """
    if not document.is_file():
        return None
    match = STATUS_ROW.search(document.read_text(encoding="utf-8"))
    return match.group(1).strip() if match else None


def unit_problems(unit: dict, scope: str, root: Path = ROOT) -> list[str]:
    """The three refusals. Everything else about a unit is somebody's judgement."""
    found: list[str] = []
    uid = unit.get("id", "<no id>")

    for field in REQUIRED:
        if not unit.get(field):
            found.append(f"{uid}: missing `{field}`")

    teaches = str(unit.get("teaches") or "")
    if not teaches:
        return found

    document = root / teaches
    if not document.is_file():
        found.append(f"{uid}: teaches {teaches}, which is not there")
        return found

    actual = declared_status(document)
    claimed = unit.get("status_claimed")
    if claimed is not None:
        if actual is None:
            found.append(
                f"{uid}: claims status `{claimed}` for {teaches}, which carries "
                f"no Status row. Only a record does"
            )
        elif str(claimed).strip().lower() != actual.lower():
            found.append(
                f"{uid}: claims `{claimed}` for {teaches}, which says `{actual}`. "
                f"Teaching an unratified record as settled asserts what no human did"
            )

    if scope == "project" and not teaches.startswith(PROJECT_OWNED):
        found.append(
            f"{uid}: a project curriculum teaches {teaches}, which is the org's. "
            f"Cite it, do not own it -- precedence runs one way"
        )

    prerequisites = unit.get("prerequisites") or []
    if uid in prerequisites:
        found.append(f"{uid}: is its own prerequisite")
    return found


def ordering_problems(units: list[dict]) -> list[str]:
    """A prerequisite must exist and must come first. Order is the whole artifact."""
    found: list[str] = []
    position = {u.get("id"): i for i, u in enumerate(units)}
    for index, unit in enumerate(units):
        for need in unit.get("prerequisites") or []:
            if need not in position:
                found.append(f"{unit.get('id')}: needs `{need}`, which is not a unit")
            elif position[need] > index:
                found.append(
                    f"{unit.get('id')}: needs `{need}`, which comes after it"
                )
    return found


def problems(curriculum: dict, root: Path = ROOT) -> list[str]:
    units = curriculum.get("units") or []
    scope = str(curriculum.get("scope") or "org")
    found: list[str] = []
    seen: set[str] = set()
    for unit in units:
        uid = unit.get("id")
        if uid in seen:
            found.append(f"{uid}: duplicate unit id")
        seen.add(uid)
        found += unit_problems(unit, scope, root)
    return found + ordering_problems(units)


def reconcile(base: dict, other: dict, root: Path = ROOT,
              other_root: Path | None = None) -> list[dict]:
    """One verdict per incoming unit. Optimistic, and refusing only three things.

    The base is never modified here and no file is written: this returns what
    integrating *would* cost, which is what makes the operation safe to run
    before deciding to do it.

    `other_root` IS SEPARATE FROM `root` AND USUALLY HAS TO BE SET. A project
    curriculum's `teaches: adr/DRAFT-x.md` names a file in *that* project's
    checkout. Resolved against this repository it is not there, and every
    incoming unit is refused -- for the wrong reason, in a report that looks
    like a governance verdict. It defaults to `root` because a curriculum being
    merged from a sibling file in the same tree is the simpler case, not the
    common one.
    """
    other_root = other_root or root
    by_id = {u.get("id"): u for u in base.get("units") or []}
    scope = str(other.get("scope") or "org")
    verdicts: list[dict] = []

    for unit in other.get("units") or []:
        uid = unit.get("id")
        issues = unit_problems(unit, scope, other_root)
        if issues:
            verdicts.append({"id": uid, "verdict": REFUSED, "why": issues, "unit": unit})
            continue
        existing = by_id.get(uid)
        if existing is None:
            verdicts.append({"id": uid, "verdict": ACCEPTED, "why": [], "unit": unit})
        elif existing == unit:
            verdicts.append({"id": uid, "verdict": PRESENT, "why": [], "unit": unit})
        else:
            differing = sorted(
                key for key in set(existing) | set(unit)
                if existing.get(key) != unit.get(key)
            )
            verdicts.append({
                "id": uid, "verdict": CONFLICT, "unit": unit,
                "why": [f"differs on: {', '.join(differing)}; the base is kept"],
            })
    return verdicts


def merged(base: dict, verdicts: list[dict]) -> dict:
    """Base, plus every accepted unit, in order. Conflicts keep the base.

    Appended rather than interleaved: a reconciler that guessed where an
    incoming unit belongs in a reading order would be deciding the one thing a
    curriculum is for.
    """
    out = dict(base)
    out["units"] = list(base.get("units") or []) + [
        v["unit"] for v in verdicts if v["verdict"] == ACCEPTED
    ]
    return out


def render(curriculum: dict, path: Path) -> str:
    units = curriculum.get("units") or []
    out = [
        f"{path.name}: {len(units)} unit(s), scope {curriculum.get('scope', 'org')}.",
        f"audience: {' '.join(str(curriculum.get('audience', '')).split())}",
        "",
    ]
    for index, unit in enumerate(units, start=1):
        needs = ", ".join(unit.get("prerequisites") or []) or "nothing"
        out += [
            f"  {index:>2}. {unit.get('id')}  -> {unit.get('teaches')}",
            f"      after this you can  {' '.join(str(unit.get('after_this_you_can', '')).split())}",
            f"      after               {needs}",
        ]
        if unit.get("status_claimed"):
            out.append(f"      status claimed      {unit['status_claimed']}")
        out.append("")
    out.append("Reading order is a judgement. Nothing here measures whether it "
               "is a good one.")
    return "\n".join(out)


def render_reconcile(verdicts: list[dict], base_path: Path, other_path: Path) -> str:
    counts = {k: sum(1 for v in verdicts if v["verdict"] == k)
              for k in (ACCEPTED, PRESENT, CONFLICT, REFUSED)}
    out = [
        f"reconciling {other_path.name} into {base_path.name}: "
        f"{len(verdicts)} incoming unit(s).",
        f"  {counts[ACCEPTED]} accepted   {counts[PRESENT]} already present   "
        f"{counts[CONFLICT]} conflicting   {counts[REFUSED]} refused",
        "",
        "Accepted by default. Nothing is written without --write.",
        "",
    ]
    mark = {ACCEPTED: "[+]", PRESENT: "[=]", CONFLICT: "[!]", REFUSED: "[x]"}
    for verdict in verdicts:
        out.append(f"  {mark[verdict['verdict']]} {verdict['id']}")
        for why in verdict["why"]:
            out.append(f"        {why}")
    out += [
        "",
        "[+] accepted   [=] already present   [!] conflict, base kept   "
        "[x] refused",
        "",
        "A conflict is not resolved here and is not dropped. Someone decides.",
        "A refusal is one of three things: a document that is not there, a "
        "Status the",
        "document does not carry, or a project claiming an org document as its "
        "own.",
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", default=str(DEFAULT), help="the base curriculum")
    parser.add_argument("--root", default=str(ROOT),
                        help="the checkout the base curriculum's documents live in")
    parser.add_argument("--merge", help="another curriculum to reconcile into it")
    parser.add_argument("--other-root",
                        help="the checkout the merged curriculum's documents live in; "
                             "without it a project curriculum refuses for the wrong reason")
    parser.add_argument("--write", help="write the merged result here (otherwise report only)")
    parser.add_argument("--check", action="store_true",
                        help="refuse a unit that teaches something false")
    args = parser.parse_args(argv)

    base_path = Path(args.file)
    root = Path(args.root)
    base = load(base_path)

    if args.merge:
        other_path = Path(args.merge)
        other_root = Path(args.other_root) if args.other_root else root
        verdicts = reconcile(base, load(other_path), root, other_root)
        print(render_reconcile(verdicts, base_path, other_path))
        if args.write:
            out = Path(args.write)
            out.write_text(
                yaml.safe_dump(merged(base, verdicts), sort_keys=False,
                               allow_unicode=True),
                encoding="utf-8",
            )
            print(f"\nwrote {out}")
        else:
            print("\nNothing was written. Pass --write <path> to keep this.")
        # Reporting is not judging. A refusal reds the run only under --check,
        # so the reconcile can be read before anyone decides to act on it.
        if args.check and any(v["verdict"] == REFUSED for v in verdicts):
            return 1
        return 0

    if args.check:
        found = problems(base, root)
        for problem in found:
            print(f"  - {problem}", file=sys.stderr)
        if found:
            print(f"\n{len(found)} problem(s) in {base_path}.", file=sys.stderr)
            return 1
        print(f"curriculum: {len(base.get('units') or [])} unit(s), every one "
              f"citing a document that exists and stating its Status correctly.")
        print("This does NOT mean the order is right, that the prose is true of "
              "the document, or that anything omitted should have been.")
        return 0

    print(render(base, base_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
