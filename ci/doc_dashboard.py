#!/usr/bin/env python3
"""Render the document state document, filtered to one state or all of them.

Org-level tooling, copied nowhere. Reads a document; writes a page. It may not
run git, gh, or anything else -- if a fact is not in the document, this renderer
does not have it, and the fix belongs in ci/doc_status.py where the rule is
defined once. `ci/tests/test_doc_tooling.py` asserts no process-spawning import
appears anywhere in this file, this sentence included.

THE TOGGLE. `--state <name>` narrows the page to one state. The count of what
was hidden is always printed, because a filtered page that does not say it is
filtered reads as the whole corpus -- and this is a governance view, where a
short clean list is the most dangerous thing on offer.

Usage:
    python ci/doc_dashboard.py doc-status.json
    python ci/doc_dashboard.py doc-status.json --state draft
    python ci/doc_dashboard.py doc-status.json --out handbook/document-states.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# The mark is the whole signal in markdown, which has no colour. It survives
# printing, monochrome, and being parsed back out of the page.
MARK = {
    "ratified": "[R]",
    "proposed": "[P]",
    "draft": "[D]",
    "responded": "[+]",
    "acknowledged": "[a]",
    "declined": "[x]",
    "unreviewed": "[-]",
    "generated": "[G]",
    "standing": "[S]",
    "transient": "[T]",
    "unknown": "[??]",
}

# Ordered so a reader meets the binding states first.
ORDER = ["ratified", "proposed", "draft", "unknown", "responded", "acknowledged",
         "declined", "unreviewed", "generated", "standing", "transient"]


def reason(value: object) -> str | None:
    """The reason, if this value is the document's unknown form.

    Duplicated from `gate_dashboard.py` rather than imported: these are two
    renderers of two documents, and a shared helper module between them is a
    coupling that makes a change to one silently change the other. Four lines
    is the right price for that independence.

    >>> reason({"unknown": "why"})
    'why'
    >>> reason({"unknown": "why", "and": "more"}) is None
    True
    """
    if isinstance(value, dict) and "unknown" in value and len(value) == 1:
        return str(value["unknown"])
    return None


def readiness_lines(doc: dict) -> list[str]:
    """The milestone claim and the measurements, side by side and unreconciled.

    Deliberately not a score. One of the five requirements cannot be measured at
    all, and a percentage that quietly dropped it would be the most confidently
    wrong thing this page could print.
    """
    block = doc.get("readiness") or {}
    claim, measured = block.get("claim"), block.get("measured") or {}
    why = reason(claim)
    if why:
        return ["## Where this corpus stands\n",
                f"**unknown** — {why}. Not established is not the same as ready.\n"]

    records = measured.get("records") or {}
    version = claim.get("version")
    lines = [
        "## Where this corpus stands\n",
        f"Working toward **{claim.get('name')}** (`{claim.get('target_version')}`) — "
        f"{' '.join((claim.get('audience') or '').split())}\n",
        "| | Claimed | Measured |",
        "|---|---|---|",
        f"| Corpus version | `{claim.get('target_version')}` is the target | "
        + (f"`{version}`" if version else
           f"**none.** No `v*` tag, so no release claim — {claim.get('version_source')}")
        + " |",
        f"| Records ratified | every requirement below | "
        f"**{records.get('ratified')} of {records.get('total')}**; "
        f"{records.get('proposed')} proposed |",
        f"| Mandatory reading | under budget | "
        f"{measured.get('reading_total_lines')} of {measured.get('reading_budget_lines')} lines"
        + ("" if measured.get("reading_within_budget") else " — **over**") + " |",
        f"| Documents whose state is unknown | none | "
        f"{measured.get('documents_in_unknown_state')} |",
        "",
        "**What the milestone requires**, and where each is measured:\n",
    ]
    for req in claim.get("requires") or []:
        lines.append(f"- **`{req.get('id')}`** — {' '.join((req.get('what') or '').split())}  ")
        lines.append(f"  *measured by:* `{req.get('measured_by')}`")
    lines += [
        "",
        f"*{block.get('no_score_is_computed')}* "
        f"{block.get('claim_is_not_evidence')}\n",
    ]
    return lines


def render(doc: dict, only: str | None) -> str:
    out: list[str] = []
    add = out.append
    documents = doc.get("documents") or []
    totals = doc.get("totals") or {}
    reading = doc.get("reading") or {}
    states = doc.get("states") or {}

    shown = [d for d in documents if only is None or d.get("state") == only]
    hidden = len(documents) - len(shown)

    add("# Handbook — Document States\n")
    add(f"**Generated `{doc.get('generated_at')}`.** Quotable for "
        f"{reading.get('staleness_budget_hours')}h. **Do not edit by hand.**\n")

    out.extend(readiness_lines(doc))

    if only:
        add(f"> **Filtered to `{only}`.** {len(shown)} shown, **{hidden} hidden**. "
            f"Run without `--state` for all {len(documents)}.\n")
    else:
        add(f"Every governed document in this corpus: **{len(documents)}**, "
            f"unfiltered.\n")

    add(f"| | |\n|---|---|")
    add(f"| **Refresh** | `{reading.get('refresh')}` |")
    add(f"| **Toggle one state** | `{reading.get('toggle')}` |")
    add(f"| **Regenerate every document** | `{reading.get('regenerate_everything')}` |\n")

    add("## What each state tells you\n")
    add("A state says whether a page binds you. It never says the content is "
        "right — Status tracks whether a human has acted.\n")
    add("| | State | Means |\n|---|---|---|")
    for name in ORDER:
        if name in states:
            add(f"| {MARK.get(name, '[??]')} | `{name}` | {states[name]} |")
    add("")

    add("## Counts\n")
    add("| State | Documents |\n|---|---|")
    for name, count in sorted((totals.get("by_state") or {}).items(),
                              key=lambda kv: (ORDER.index(kv[0]) if kv[0] in ORDER else 99)):
        add(f"| {MARK.get(name, '[??]')} `{name}` | {count} |")
    add("")

    if totals.get("disagreements"):
        add("## The filename and the Status row disagree\n")
        add("Ratification renames the file. A disagreement means one of its five "
            "steps has not been done, and nothing else in this repository "
            "notices.\n")
        for entry in documents:
            if entry.get("disagreement"):
                add(f"- **`{entry['path']}`** — {entry['disagreement']}")
        add("")

    add("## Documents\n")
    if not shown:
        add(f"*No document is in state `{only}`.* That is a real answer: "
            f"{len(documents)} documents were read and none matched.\n")
    else:
        add("| | State | Document | Class | Declared |")
        add("|---|---|---|---|---|")
        for entry in sorted(shown, key=lambda d: (
                ORDER.index(d["state"]) if d["state"] in ORDER else 99, d["path"])):
            declared = entry.get("declared_status") or "—"
            add(f"| {MARK.get(entry['state'], '[??]')} | `{entry['state']}` | "
                f"`{entry['path']}` | {entry['class']} | {declared} |")
        add("")

    unknowns = [d for d in shown if d.get("state") == "unknown"]
    if unknowns:
        add("## Could not be established\n")
        add("Not the same as fine. Each of these is a document whose own state "
            "nobody can read.\n")
        for entry in unknowns:
            add(f"- **`{entry['path']}`** — {entry.get('why_unknown', 'no reason recorded')}")
        add("")

    add("## Reading this document\n")
    for line in reading.get("do_not") or []:
        add(f"- **Do not** {line}.")
    add("")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("document")
    parser.add_argument("--state", help="show only this state")
    parser.add_argument("--out")
    parser.add_argument("--check")
    args = parser.parse_args(argv)

    path = Path(args.document)
    if not path.is_file():
        print(f"{args.document}: not present.", file=sys.stderr)
        return 1
    doc = json.loads(path.read_text(encoding="utf-8"))

    if args.state and args.state not in (doc.get("states") or {}):
        print(f"unknown state {args.state!r}. The vocabulary is closed: "
              f"{', '.join(sorted(doc.get('states') or {}))}", file=sys.stderr)
        return 2

    page = render(doc, args.state)

    if args.check:
        target = Path(args.check)
        if not target.is_file():
            print(f"{args.check}: not present.", file=sys.stderr)
            return 1
        if target.read_text(encoding="utf-8").replace("\r\n", "\n") != page.replace("\r\n", "\n"):
            print(f"{args.check} has drifted from {args.document}.", file=sys.stderr)
            return 1
        print(f"{args.check} matches {args.document}.")
        return 0

    if args.out:
        Path(args.out).write_text(page, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
        return 0

    sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    sys.exit(main())
