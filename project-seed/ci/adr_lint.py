#!/usr/bin/env python3
"""ADR lint — enforces the decision-record-discipline record's four checks.

SEED FILE, run in place: a forking project copies adr-lint.yml into its own
.github/workflows/ and leaves this script where it is. The workflow invokes it
out of the governance submodule the project already vendors, so the logic is
always the version that project's governance pin points at. Copying this file
into a project would create a second copy to keep in sync across N
repositories, which is the drift the arrangement avoids. See adr/README.md's
"CI enforcement" section.

The discipline record's Consequences name four things CI rejects. This
implements all four:

  1. Banned vocabulary in a pre-ratification draft.
  2. A numbered record filename whose Status is not Accepted or later.
  3. An edit to an Accepted record's body outside its Amendments section.
  4. A mismatch between the index and the record directory.

Check 1 scans prose only. Fenced code blocks, inline code spans (including
ones wrapping across lines), and HTML comments are stripped before matching,
because a document that *quotes* the banned list -- the discipline record
itself does, and the template's own drafting-rules comment does -- is
describing the rule rather than breaking it. Matching those was the single
false positive this lint produced against the corpus that defines it.

Usage:
    adr_lint.py --records-dir adr [--index adr/README.md] [--base-ref origin/main]

--base-ref enables check 3, which needs something to diff against. Without
it, check 3 is skipped and says so rather than passing silently.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

BANNED = re.compile(
    r"previously|originally|earlier draft|re-review|renumber|retroactive"
    r"|supersedes the .* (?:stance|finding)|\bcorrected\b",
    re.IGNORECASE,
)

NUMBERED_FILENAME = re.compile(r"^(?:ADR|QM)-(\d{4})-.+\.md$")
STATUS_ROW = re.compile(r"^\|\s*\*\*Status\*\*\s*\|\s*(.+?)\s*\|", re.MULTILINE)
RATIFIED = ("accepted", "deprecated", "superseded")

FENCE = re.compile(r"^\s*```.*?^\s*```", re.MULTILINE | re.DOTALL)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`", re.DOTALL)


def prose_only(text: str) -> str:
    """Strip code fences, HTML comments, and inline code spans.

    Replaces each with blank lines rather than deleting them, so reported
    line numbers still line up with the file on disk.
    """

    def blank(match: re.Match) -> str:
        return "\n" * match.group(0).count("\n")

    text = HTML_COMMENT.sub(blank, text)
    text = FENCE.sub(blank, text)
    text = INLINE_CODE.sub(blank, text)
    return text


def status_of(text: str) -> str | None:
    match = STATUS_ROW.search(text)
    return match.group(1).strip().lower() if match else None


def is_ratified(status: str | None) -> bool:
    return bool(status) and status.startswith(RATIFIED)


def check_banned_vocabulary(records: Path) -> list[str]:
    failures = []
    for path in sorted(records.glob("DRAFT-*.md")):
        text = prose_only(path.read_text(encoding="utf-8"))
        for lineno, line in enumerate(text.splitlines(), start=1):
            for hit in BANNED.finditer(line):
                failures.append(
                    f"{path}:{lineno}: pre-ratification drafts are squashed, not "
                    f"narrated -- found {hit.group(0)!r}"
                )
    return failures


def check_numbered_are_ratified(records: Path) -> list[str]:
    failures = []
    for path in sorted(records.glob("*.md")):
        if not NUMBERED_FILENAME.match(path.name):
            continue
        status = status_of(path.read_text(encoding="utf-8"))
        if not is_ratified(status):
            failures.append(
                f"{path}: numbered filename with Status {status or 'missing'!r}. "
                "Numbers are assigned at ratification; a draft stays numberless."
            )
    return failures


def check_accepted_bodies_untouched(records: Path, base_ref: str) -> list[str]:
    """Fail if a ratified record changed anywhere above its Amendments heading."""
    failures = []
    try:
        changed = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", str(records)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
    except subprocess.CalledProcessError as exc:
        return [f"could not diff against {base_ref}: {exc.stderr.strip()}"]

    for name in changed:
        path = Path(name)
        if not path.exists() or not path.suffix == ".md":
            continue
        text = path.read_text(encoding="utf-8")
        if not is_ratified(status_of(text)):
            continue

        amendments_line = None
        for lineno, line in enumerate(text.splitlines(), start=1):
            if re.match(r"^##\s+Amendments\s*$", line):
                amendments_line = lineno
                break
        if amendments_line is None:
            failures.append(f"{path}: ratified record has no Amendments section.")
            continue

        hunks = subprocess.run(
            ["git", "diff", "-U0", f"{base_ref}...HEAD", "--", str(path)],
            capture_output=True,
            text=True,
        ).stdout
        for header in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", hunks, re.MULTILINE):
            start = int(header.group(1))
            count = int(header.group(2) or 1)
            if count and start < amendments_line:
                failures.append(
                    f"{path}:{start}: ratified records are append-only. Changes go "
                    "in dated entries under Amendments; the body is never edited."
                )
    return failures


def check_index_matches_directory(records: Path, index: Path) -> list[str]:
    if not index.exists():
        return [f"{index}: index file not found."]

    on_disk = {
        int(m.group(1))
        for p in records.glob("*.md")
        if (m := NUMBERED_FILENAME.match(p.name))
    }

    in_index = set()
    for line in index.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        first = re.sub(r"^(?:ADR|QM)-", "", cells[0]).strip()
        if first.isdigit():
            in_index.add(int(first))

    failures = []
    for number in sorted(on_disk - in_index):
        failures.append(
            f"{index}: record {number:04d} exists on disk but is absent from the index."
        )
    for number in sorted(in_index - on_disk):
        failures.append(
            f"{index}: index lists record {number:04d} with no matching file."
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-dir", required=True, type=Path)
    parser.add_argument("--index", type=Path)
    parser.add_argument("--base-ref")
    args = parser.parse_args()

    records = args.records_dir
    if not records.is_dir():
        print(f"ADR lint: no such directory: {records}", file=sys.stderr)
        return 2

    index = args.index or (records / "README.md")

    failures: list[str] = []
    failures += check_banned_vocabulary(records)
    failures += check_numbered_are_ratified(records)
    failures += check_index_matches_directory(records, index)

    if args.base_ref:
        failures += check_accepted_bodies_untouched(records, args.base_ref)
    else:
        print("ADR lint: no --base-ref given; skipping the append-only check.")

    if failures:
        print(f"\nADR lint: {len(failures)} problem(s) in {records}/\n")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print(f"ADR lint: clean ({records}/)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
