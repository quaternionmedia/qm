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

--base-ref names a commit in whichever repository the command is run from. In
the branch-per-project model the records sit in a submodule, so it names a
commit in the superproject and check 3 reads the submodule pin out of it,
then diffs that pin against the checked-out one inside the submodule. That
indirection is the whole reason check 3 needs its own code path: a
superproject cannot see inside a gitlink, and a diff filtered to a path
within one matches nothing rather than failing.
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


def _git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )


def _toplevel(path: Path) -> Path | None:
    proc = _git(["-C", str(path), "rev-parse", "--show-toplevel"])
    return Path(proc.stdout.strip()) if proc.returncode == 0 else None


def diff_plan(records: Path, base_ref: str) -> tuple[Path, list[str], str] | str | None:
    """Where to run the diff, over what range, filtered to which path.

    Returns (repo_root, range_args, path) to diff, a string to report as a
    failure, or None when there is nothing comparable and check 3 must skip.

    The records directory is usually inside a *submodule* -- that is the
    branch-per-project model this seed advertises, where a project's records
    live on their own branch of the governance repo and the project vendors
    it. A superproject tracks that submodule as a gitlink, so asking it to
    diff a path *inside* the submodule matches nothing at all: not some
    edits, none of them. Check 3 then runs over an empty change list and
    reports clean no matter what was edited, which is the one outcome this
    script exists to prevent. The diff has to run in the repository that
    actually tracks the files.
    """
    records = records.resolve()
    inner = _toplevel(records)
    if inner is None:
        return f"{records}: not inside a git repository."
    rel = records.relative_to(inner).as_posix() or "."

    outer = _toplevel(Path.cwd())
    if outer is None or inner == outer:
        return inner, [f"{base_ref}...HEAD"], rel

    # Records live in a nested repository. base_ref names a commit in the
    # OUTER one, where the only thing it says about the records is which
    # commit the submodule was pinned to. Compare that pin against the one
    # checked out now -- two commits, so compare their trees directly rather
    # than through a merge base they may not share.
    sub = inner.relative_to(outer).as_posix()
    old = _git(["rev-parse", f"{base_ref}:{sub}"], cwd=outer)
    if old.returncode != 0:
        # The submodule is not a gitlink at base_ref -- it is being added in
        # this change. Nothing was pinned before, so no ratified body can
        # have been edited.
        print(
            f"ADR lint: {sub} is not a submodule at {base_ref}; "
            "skipping the append-only check."
        )
        return None
    new = _git(["rev-parse", "HEAD"], cwd=inner)
    if new.returncode != 0:
        return f"could not resolve HEAD in {inner}: {new.stderr.strip()}"
    return inner, [old.stdout.strip(), new.stdout.strip()], rel


def check_accepted_bodies_untouched(records: Path, base_ref: str) -> list[str]:
    """Fail if a ratified record changed anywhere above its Amendments heading."""
    failures = []
    plan = diff_plan(records, base_ref)
    if plan is None:
        return []
    if isinstance(plan, str):
        return [plan]
    root, rng, rel = plan

    proc = _git(["diff", "--name-only", *rng, "--", rel], cwd=root)
    if proc.returncode != 0:
        return [f"could not diff against {base_ref}: {proc.stderr.strip()}"]
    changed = proc.stdout.split()

    for name in changed:
        path = root / name
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
            failures.append(f"{name}: ratified record has no Amendments section.")
            continue

        hunks = _git(["diff", "-U0", *rng, "--", name], cwd=root).stdout
        for header in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", hunks, re.MULTILINE):
            start = int(header.group(1))
            count = int(header.group(2) or 1)
            # A deletion-only hunk carries a new-file count of 0 and reads
            # `@@ -10 +9,0 @@`: nothing was added, so `start` is the line the
            # removal sits after rather than a line that exists. Skipping those
            # would let a ratified body be edited by deletion alone, which is
            # the append-only rule's most obvious violation.
            where = start if count else start + 1
            if where <= amendments_line - 1 or (count and start < amendments_line):
                verb = "removed from" if not count else "edited in"
                failures.append(
                    f"{name}:{start}: ratified records are append-only; content was "
                    f"{verb} the body. Changes go in dated entries under Amendments."
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
