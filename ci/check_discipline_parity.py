"""The verification discipline reaches a fork, or it does not exist for one.

This corpus's own `AGENTS.md` and the `project-seed/ide/AGENTS.md` a project
forks are two hand-maintained files carrying the same discipline in adapted
wording. Neither is generated from the other and neither is a symlink, so a rule
added to one reaches nobody through the other. That is the exact shape item 17
names -- a summary of a canonical list is a copy, and copies drift -- applied to
the discipline that exists to prevent drift.

WHAT THIS CHECKS, AND WHAT IT CANNOT

It checks that each shared rule is *present* in both files, by a short anchor
phrase. It cannot check that the two statements of a rule still mean the same
thing: the seed's wording is deliberately adapted (a fork reads
`governance/qm/records/...`, this repo reads `records/...`), so a diff would be
noise and an equality assertion would be wrong. Presence is the property that
was actually violated -- a rule in one file and absent from the other -- and it
is the one worth mechanising.

WHY AN ANCHOR RATHER THAN A HEADING

Numbering differs between the files and has moved twice. A check keyed on "item
12" would pass while pointing at a different rule, which is worse than no check.
An anchor is a distinctive phrase from the rule's own statement: if someone
rewords a rule past recognition in one file, this fails and asks them to update
both -- which is the intended outcome, not a false positive.

ADDING A RULE

Add its anchor below in the same commit that adds the rule to both files. An
anchor that never fails is one nobody had to think about; that is fine. An
anchor you are tempted to delete to make this pass is a rule you are removing
from every fork, and it should be removed deliberately, in prose, not here.

Usage:
    python ci/check_discipline_parity.py
    python ci/check_discipline_parity.py --root /path/to/corpus
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CORPUS_AGENTS = "AGENTS.md"
SEED_AGENTS = "project-seed/ide/AGENTS.md"

# Matched case-insensitively, so a rule opening a sentence in one file and
# mid-sentence in the other still counts. Keep each anchor to the distinctive
# core of its rule -- long enough to be unique, short enough to survive an edit
# that does not change the rule.
SHARED_ANCHORS: list[str] = [
    # Established before this session; listed so a future edit cannot quietly
    # drop one from the seed while leaving it here.
    "a signal before reading it",
    "names what else could produce them",
    "scaffolding you measure with is part of the measurement",
    "tried to route around it",
    # Added 2026-08-15, from a session that broke each of them in turn.
    "never through a pipe",
    "stated in prose is not a bound",
    "a copy, and copies drift",
]


def _normalise(text: str) -> str:
    """Collapse whitespace so an anchor matches prose, not line wrapping.

    Both files wrap at about 79 columns, and they wrap in different places
    because their wording differs. Without this, an anchor fails whenever a
    line break happens to fall inside it -- which is a report about column
    widths dressed as a report about a missing rule, and the first run of this
    check produced exactly that.
    """
    return " ".join(text.split()).lower()


def missing_anchors(text: str, anchors: list[str]) -> list[str]:
    haystack = _normalise(text)
    return [a for a in anchors if _normalise(a) not in haystack]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root holding both AGENTS.md files. Defaults to cwd.",
    )
    args = parser.parse_args(argv)
    root = Path(args.root)

    findings: list[str] = []
    for relative in (CORPUS_AGENTS, SEED_AGENTS):
        path = root / relative
        if not path.is_file():
            findings.append(f"{relative}: not found under {root}")
            continue
        for anchor in missing_anchors(path.read_text(encoding="utf-8"), SHARED_ANCHORS):
            findings.append(f"{relative}: missing the rule anchored on {anchor!r}")

    print(f"shared rules   {len(SHARED_ANCHORS)}")
    print(f"files          {CORPUS_AGENTS}, {SEED_AGENTS}")

    if not findings:
        print("\nBoth files carry every shared rule.")
        return 0

    print()
    for finding in findings:
        print(f"  {finding}")
    print(
        "\nA rule present in one file and absent from the other reaches nobody "
        "through\nthe missing one. Add it to both, or remove its anchor above "
        "deliberately."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
