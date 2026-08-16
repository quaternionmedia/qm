#!/usr/bin/env python3
"""Write the document state document: what state every governed page is in.

Org-level tooling, copied nowhere. The document half of the shape
`handbook/generated-documents.md` describes; `ci/doc_dashboard.py` renders it.

WHAT THIS IS FOR. This corpus has four state vocabularies and they do not
overlap. A record is `Proposed` or `Accepted`, and its filename separately says
`DRAFT-` or `QM-NNNN-`. A perspective is `Unreviewed`, `Acknowledged`,
`Responded` or `Declined`. A generated page has no lifecycle at all, only an
age. A handbook page has no state vocabulary whatsoever. So a reader opening a
page in this repository cannot tell, from the page, which of those systems it
belongs to or where in one it sits -- and every one of those states means
something different about whether the page binds them.

TWO SIGNALS PER DOCUMENT, AND THEY CAN DISAGREE

  declared   the document's own `| **Status** | ... |` row. What it says of
             itself.
  filename   what the name asserts: `DRAFT-` is pre-ratification,
             `QM-NNNN-` is ratified.

A file named `DRAFT-` whose Status reads `Accepted` is a ratification somebody
started and did not finish -- step 3 of five, per the ratification path, is the
rename. Nothing else in this repository notices that, so the disagreement is a
first-class output here rather than a footnote.

WHAT THIS CANNOT DO

  - It cannot tell whether a state is *correct*. `Proposed` on a record nobody
    has read and `Proposed` on a record awaiting one signature are the same
    string. Status tracks whether a human has acted, never whether the content
    is right, and this tool reads the string.
  - It cannot give a handbook page a state, because the corpus has not defined
    one for that class. Those are reported `standing` with the reason, not
    given a state this tool invented.

Usage:
    python ci/doc_status.py --write doc-status.json
    python ci/doc_status.py --check doc-status.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

SCHEMA = 1
ROOT = Path(__file__).resolve().parent.parent

# `| **Status** | Proposed |` in a document's own header table.
STATUS_ROW = re.compile(r"^\|\s*\*\*Status\*\*\s*\|\s*(?P<value>[^|]+?)\s*\|", re.M)

# A row of the perspectives index:
#   | 2026-08-13 | `file.md` | Author | Perspective | Unreviewed | Notes |
# That index is the authority for a perspective's status -- `perspectives/README.md`
# says so in as many words: "This index is the whole mechanism." Reading the
# file's own header instead reported 21 of 26 perspectives as `unknown`, which
# was a fact about where this tool looked and not about the corpus.
INDEX_ROW = re.compile(
    r"^\|\s*[\d-]+\s*\|\s*`(?P<file>[^`]+\.md)`\s*\|[^|]*\|[^|]*\|\s*(?P<status>[^|]+?)\s*\|",
    re.M,
)

# The generated documents, and the state they are always in. Listed rather than
# detected: a page is generated because a generator writes it, which is a fact
# about the tooling and not about the file's contents.
GENERATED = {
    "governance-status.yaml": "python ci/governance_status.py --write governance-status.yaml",
    "harness-status.json": "python ci/harness_status.py --no-local --write harness-status.json",
    "gate-status.json": "python ci/gate_status.py --write gate-status.json",
    "doc-status.json": "python ci/doc_status.py --write doc-status.json",
    "handbook/gates.md": "python ci/gate_dashboard.py gate-status.json --format md --out handbook/gates.md",
    "handbook/document-states.md": "python ci/doc_dashboard.py doc-status.json --out handbook/document-states.md",
}

# What a session must read before its first edit, per AGENTS.md's opening.
# Measured because it is a cost paid by every reader, and because it rose 58
# lines in a session whose stated aim included cutting it -- an unmeasured
# figure moves in whichever direction nobody is watching.
# records/DRAFT-governance-arrives-as-a-mechanism.md 4 sets the budget.
MANDATORY_READING = ("AGENTS.md", "handbook/async-contract.md",
                     "handbook/handoffs/README.md")
READING_BUDGET_LINES = 700


def reading_load(root: Path) -> dict:
    """Lines a session must read before writing anything, against the budget."""
    documents = []
    total = 0
    for rel in MANDATORY_READING:
        path = root / rel
        if not path.is_file():
            documents.append({"path": rel, "lines": unknown("not present")})
            continue
        lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        total += lines
        documents.append({"path": rel, "lines": lines})
    return {
        "documents": documents,
        "total_lines": total,
        "budget_lines": READING_BUDGET_LINES,
        "within_budget": total <= READING_BUDGET_LINES,
        "headroom_lines": READING_BUDGET_LINES - total,
        "budget_source": "records/DRAFT-governance-arrives-as-a-mechanism.md 4",
        "the_budget_is_a_ratchet": (
            "It is lowered as prose is deleted, never raised on contact. Raising "
            "it is an amendment to that record, argued in the open."
        ),
    }


# Every state this tool will ever write, and what each one tells a reader about
# whether the page binds them. A state not in this list is a bug, not a new
# category -- the vocabulary is closed for the same reason the pattern registry's
# is.
STATES = {
    "draft": "pre-ratification. Rewritten in place, binds nobody, and may change entirely.",
    "proposed": "drafted and awaiting a human's ratification. Binds nobody yet.",
    "ratified": "a human ratified it. This binds every QM project.",
    "unreviewed": "written, and no maintainer has looked at it. Opinion, never binding.",
    "acknowledged": "a maintainer has read it. Logged, no further commitment.",
    "responded": "concrete work exists because of it.",
    "declined": "a maintainer read it and decided not to act, for a stated reason.",
    "generated": "written by a tool. Do not edit by hand; check its age before quoting.",
    "standing": "policy or charter with no lifecycle defined for its class.",
    "transient": "working instructions, deleted when the work lands.",
    "unknown": "the state could not be established, which is not the same as fine.",
}


def unknown(reason: str) -> dict:
    return {"unknown": reason}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def declared_status(text: str) -> str | None:
    """The document's own Status row, or None if it has no header table."""
    match = STATUS_ROW.search(text)
    return match.group("value").strip() if match else None


def perspective_index(root: Path) -> dict[str, str]:
    """Filename -> Status, from the perspectives index.

    >>> import tempfile, pathlib
    >>> d = pathlib.Path(tempfile.mkdtemp()); (d / "perspectives").mkdir()
    >>> _ = (d / "perspectives" / "README.md").write_text(
    ...     "| 2026-01-01 | `a.md` | Someone | Perspective | Responded | note |\\n")
    >>> perspective_index(d)
    {'a.md': 'Responded'}
    """
    index = root / "perspectives" / "README.md"
    if not index.is_file():
        return {}
    text = index.read_text(encoding="utf-8", errors="replace")
    return {m.group("file"): m.group("status").strip() for m in INDEX_ROW.finditer(text)}


def filename_state(name: str) -> str | None:
    """What the filename asserts about a record. None for anything else."""
    if name.startswith("DRAFT-"):
        return "draft"
    if re.match(r"^QM-\d{4}-", name):
        return "ratified"
    return None


def normalise(declared: str | None) -> str | None:
    """Map a declared Status string onto the closed vocabulary."""
    if not declared:
        return None
    key = declared.strip().lower()
    if key in ("accepted", "ratified"):
        return "ratified"
    if key in STATES:
        return key
    return None


def classify(path: Path, root: Path) -> tuple[str, str]:
    """(class, why) for one path. Class decides which vocabulary applies."""
    rel = path.relative_to(root).as_posix()
    if rel in GENERATED:
        return "generated", "a tool writes it"
    # An index is not a member of the thing it indexes. Classifying
    # perspectives/README.md as a perspective asked it for a status it does not
    # have and reported the index itself as unknown.
    if path.name == "README.md" and rel != "README.md":
        return "index", "the index for its directory, not a member of it"
    if rel.startswith("records/"):
        return "record", "an org decision record"
    if rel.startswith("perspectives/"):
        return "perspective", "dated, attributed, non-binding opinion"
    if rel.startswith("handbook/handoffs/"):
        return "handoff", "working instructions, deleted when the work lands"
    if rel.startswith("handbook/"):
        return "handbook", "policy binding on QM's own conduct"
    if rel in ("PRINCIPLES.md", "AGENTS.md", "README.md"):
        return "entry", "read first, by everyone"
    return "other", "not in a governed directory"


def row(path: Path, root: Path, index: dict[str, str] | None = None) -> dict:
    rel = path.relative_to(root).as_posix()
    kind, why = classify(path, root)
    present = path.is_file()
    text = (
        path.read_text(encoding="utf-8", errors="replace")
        if present and path.suffix == ".md" else ""
    )

    declared_raw = declared_status(text) if text else None
    declared = normalise(declared_raw)
    from_name = filename_state(path.name)

    entry = {
        "path": rel,
        "class": kind,
        "class_reason": why,
        "declared_status": declared_raw,
        "state_from_status_row": declared,
        "state_from_filename": from_name,
    }

    if kind == "generated":
        entry["state"] = "generated"
        entry["refresh"] = GENERATED[rel]
        entry["present"] = present
        if not present:
            # Reported, never omitted. A declared document that has never been
            # generated is a fact; dropping it would make the set depend on the
            # order the generators ran in, and this document would then never
            # be self-consistent -- it lists a view that is written after it.
            entry["why_absent"] = "declared generated, and not on disk. Run its refresh command."
        return entry

    if kind == "record":
        if declared is None:
            entry["state"] = "unknown"
            entry["why_unknown"] = (
                "no readable Status row, and a record without one states nothing "
                "about whether it binds"
            )
        else:
            entry["state"] = declared
        # The half-finished ratification nothing else in this repository notices.
        if from_name and declared and from_name != declared:
            if not (from_name == "draft" and declared == "proposed"):
                entry["disagreement"] = (
                    f"the filename says {from_name} and the Status row says "
                    f"{declared}; ratification renames the file, so one of the "
                    f"five steps has not been done"
                )
        return entry

    if kind == "perspective" and not present:
        # Indexed and absent. Not `unknown` -- the state is perfectly readable,
        # the document is missing, and those are different facts.
        entry["state"] = "unknown"
        entry["present"] = False
        entry["why_unknown"] = (
            "the perspectives index names this file and it is not on disk. An "
            "index row is a claim that something exists"
        )
        return entry

    if kind == "perspective":
        # The index is the authority here, not the file. Most perspectives carry
        # no Status row of their own, and perspectives/README.md states that the
        # index is the mechanism.
        indexed_raw = (index or {}).get(path.name)
        indexed = normalise(indexed_raw)
        entry["indexed_status"] = indexed_raw
        entry["state"] = indexed or declared or "unknown"
        if entry["state"] == "unknown":
            entry["why_unknown"] = (
                "no row in perspectives/README.md and no Status row in the file, "
                "so nothing states whether anyone has read it"
            )
        elif indexed and declared and indexed != declared:
            entry["disagreement"] = (
                f"the perspectives index says {indexed} and the file's own header "
                f"says {declared}; the index is the authority and the file is stale"
            )
        return entry

    if kind == "handoff":
        entry["state"] = "transient"
        return entry

    entry["state"] = "standing"
    entry["note"] = (
        "the corpus defines no lifecycle for this class, so this is the absence "
        "of a state rather than a state"
    )
    return entry


def readiness(root: Path, rows: list[dict], by_state: dict[str, int], load: dict) -> dict:
    """The milestone claim from ci/workspace.yaml, beside what is measured.

    The two are never reconciled here. A requirement whose `measured_by` names a
    figure this document holds gets that figure attached; one that names another
    document, or names nothing mechanisable, says so. A readiness layer that
    quietly computed a percentage would be the single most confidently wrong
    thing a governance dashboard can print.
    """
    workspace = root / "ci" / "workspace.yaml"
    if not workspace.is_file():
        return {"claim": unknown(f"{workspace} is not present"), "measured": {}}
    claim = (yaml.safe_load(workspace.read_text(encoding="utf-8")) or {}).get("milestone")
    if not claim:
        return {"claim": unknown("ci/workspace.yaml declares no milestone block"), "measured": {}}

    records = [r for r in rows if r["class"] == "record"]
    measured = {
        "records": {
            "total": len(records),
            "ratified": sum(1 for r in records if r["state"] == "ratified"),
            "proposed": sum(1 for r in records if r["state"] == "proposed"),
        },
        "documents_in_unknown_state": by_state.get("unknown", 0),
        "reading_within_budget": load["within_budget"],
        "reading_total_lines": load["total_lines"],
        "reading_budget_lines": load["budget_lines"],
        "gates": unknown(
            "held in gate-status.json, which this generator does not read -- one "
            "document does not restate another's figures"
        ),
        "semantic_review": unknown(
            "not mechanisable. A human reads every record in one sitting and says "
            "so; no count here can stand in for that"
        ),
    }
    return {
        "claim": claim,
        "claim_is_not_evidence": (
            "milestone, target_version and requires are what a human stated in "
            "ci/workspace.yaml. Nothing here is derived from the repository."
        ),
        "measured": measured,
        "no_score_is_computed": (
            "This layer does not say whether the milestone is met. It puts the "
            "claim and the measurements side by side; the judgement is a human's, "
            "and one of the five requirements cannot be measured at all."
        ),
    }


def build(root: Path) -> dict:
    # Collected as a set and sorted, so the output does not depend on which
    # generator ran first. An order-dependent document cannot be checked, and
    # this one lists a view that is written after it.
    found: set[str] = set()
    for pattern in ("records/*.md", "perspectives/*.md", "handbook/**/*.md",
                    "plans/*.md",
                    "PRINCIPLES.md", "AGENTS.md", "README.md"):
        for path in root.glob(pattern):
            found.add(path.relative_to(root).as_posix())

    # Guarded on what was *found*, not on the row count. `GENERATED` seeds the
    # set unconditionally, so a count-based guard could never fire -- it would
    # be dead code sitting where a reader believes something is checked.
    if not found:
        raise SystemExit(f"{root}: no governed documents found -- nothing was measured")

    index = perspective_index(root)

    # An index row naming a file that does not exist. The reverse -- a file with
    # no row -- was already caught, and checking one direction only is how a
    # perspective got indexed here before it was written. `check_restatements.py`
    # got this right in the same session that got it wrong here.
    for name in index:
        rel = f"perspectives/{name}"
        if rel not in found:
            found.add(rel)

    rows = [row(root / rel, root, index) for rel in sorted(found | set(GENERATED))]

    by_state: dict[str, int] = {}
    for r in rows:
        by_state[r["state"]] = by_state.get(r["state"], 0) + 1

    load = reading_load(root)

    return {
        "schema": SCHEMA,
        "generated_at": now(),
        "generator": {
            "tool": "ci/doc_status.py",
            "signals": ["declared_status", "state_from_filename"],
            "vocabulary_is_closed": (
                "every state written here is a key of `states` below. A document "
                "whose Status string is not in that vocabulary is `unknown`, "
                "never a new category."
            ),
            "status_is_not_correctness": (
                "Status tracks whether a human has acted, never whether the "
                "content is right. This tool reads the string."
            ),
        },
        "reading": {
            "refresh": "uv run qm docs generate",
            "refresh_without_the_cli": "python ci/doc_status.py --write doc-status.json",
            "staleness_budget_hours": 168,
            "agent_view": "uv run qm docs states",
            "toggle": "uv run qm docs states --state draft",
            "regenerate_everything": "uv run qm docs generate",
            "unknown_convention": (
                '{"unknown": "<reason>"} is a value, and `state: unknown` means '
                "the state could not be established. It is not `standing`, not "
                "`draft`, and not fine."
            ),
            "do_not": [
                "read `ratified` off a filename alone -- the Status row is the claim",
                "read `proposed` as reviewed: nothing in this corpus has been ratified",
                "treat `standing` as a state; it is the absence of one for that class",
                "quote a count without this document's generated_at",
            ],
        },
        "states": STATES,
        "reading_load": load,
        "readiness": readiness(root, rows, by_state, load),
        "totals": {
            "documents": len(rows),
            "by_state": dict(sorted(by_state.items())),
            "disagreements": sum(1 for r in rows if r.get("disagreement")),
            "unknown": sum(1 for r in rows if r["state"] == "unknown"),
        },
        "documents": rows,
    }


def comparable(doc: dict) -> dict:
    """Everything a check verifies -- `generated_at` moves on its own."""
    return {k: v for k, v in doc.items() if k != "generated_at"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--write")
    parser.add_argument("--check")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()

    if args.check:
        target = Path(args.check)
        if not target.is_file():
            print(f"{args.check}: not present.", file=sys.stderr)
            return 1
        committed = json.loads(target.read_text(encoding="utf-8"))
        if comparable(committed) != comparable(build(root)):
            print(f"{args.check} no longer describes the documents on disk.\n"
                  f"Run: python ci/doc_status.py --write {args.check}", file=sys.stderr)
            return 1
        print(f"{args.check}: matches the documents on disk.")
        return 0

    document = build(root)
    if args.write:
        Path(args.write).write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        print(f"wrote {args.write}")
        return 0

    json.dump(document, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
