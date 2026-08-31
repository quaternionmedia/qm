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

# Narration a pre-ratification draft must not carry: the document describing
# its own revision history rather than being rewritten.
#
# THESE ARE PROXIES FOR A MEANING, AND A PROXY MATCHES THINGS IT DID NOT MEAN.
# `corrected` was a bare word here, and it fired on "neither is corrected" in a
# sentence about two perspectives -- prose that was true, that narrated nothing,
# and that got reworded to satisfy the check. Editing a correct record to keep a
# tool quiet is the failure `records/DRAFT-deltas-compose.md` 7 names in another
# register: the tool ends consistent and the record ends worse.
#
# So the words that have innocent uses are matched only in a narrating
# construction, and every rule here is escapable with a stated reason. The ones
# with no innocent use in a draft stay bare.
BANNED = re.compile(
    # No innocent use inside a pre-ratification draft.
    r"earlier draft|re-review|renumber|retroactive"
    r"|supersedes the .* (?:stance|finding)"
    # Narrating constructions only. "previously X" narrates; "previously
    # unknown" is a description of the world.
    r"|\bpreviously\s+(?:said|stated|read|held|named|claimed|was|were)\b"
    r"|\boriginally\s+(?:said|stated|read|held|named|claimed|was|were)\b"
    r"|\b(?:this|that|these|those|it|which|the|a|an)\s+(?:\w+\s+){0,2}"
    r"(?:was|were|has been|have been|has since been|is now|are now)"
    r"\s+corrected\b"
    r"|\bnow\s+corrected\b|\bcorrected\s+(?:from|to|in a later|in this)\b",
    re.IGNORECASE,
)

# An escape hatch with a price: the reason is required, and the count of
# exemptions used is printed on every run, so silencing the check stays visible
# rather than becoming the way it is used.
EXEMPTION = re.compile(
    r"<!--\s*adr-lint:\s*allow\s+(?P<quoted>\S.*?)\s*-->", re.IGNORECASE
)

NUMBERED_FILENAME = re.compile(r"^(?:ADR|QM)-(\d{4})-.+\.md$")
# A markdown link target inside an index row. Matched on the row rather than on
# the whole file so prose elsewhere in an index page cannot register a record
# as listed -- the table is the index, and a mention in a paragraph is not one.
INDEX_LINK = re.compile(r"\]\(([^)]+\.md)\)")
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


def exemption_on(lines: list[str], index: int) -> str | None:
    """The reason stated for allowing a hit, from this line or the one above.

    Two places because a long line is wrapped in this corpus and an annotation
    at the end of it would push past the margin every other rule respects.
    """
    for candidate in (lines[index], lines[index - 1] if index else ""):
        found = EXEMPTION.search(candidate)
        if found:
            return found.group("quoted").strip()
    return None


def check_banned_vocabulary(records: Path) -> list[str]:
    failures = []
    allowed = 0
    for path in sorted(records.glob("DRAFT-*.md")):
        raw = path.read_text(encoding="utf-8")
        # Scanned against prose, but the exemption is read from the raw file:
        # `prose_only` blanks HTML comments, which is right for the scan and
        # would make the annotation invisible to the thing it annotates.
        # `prose_only` preserves line numbering, so the two line up.
        lines = prose_only(raw).splitlines()
        raw_lines = raw.splitlines()
        for index, line in enumerate(lines):
            for hit in BANNED.finditer(line):
                reason = exemption_on(raw_lines, index)
                if reason is None:
                    failures.append(
                        f"{path}:{index + 1}: pre-ratification drafts are "
                        f"squashed, not narrated -- found {hit.group(0)!r}. If "
                        f"this narrates nothing, annotate the line: "
                        f"<!-- adr-lint: allow \"why this is not narration\" -->"
                    )
                elif not reason.strip('"\''):
                    failures.append(
                        f"{path}:{index + 1}: an adr-lint exemption states a "
                        f"reason. An empty one is the check turned off."
                    )
                else:
                    allowed += 1
    if allowed:
        print(f"ADR lint: {allowed} banned-vocabulary hit(s) allowed by a "
              f"stated reason. Each is a place the proxy matched prose that "
              f"narrates nothing.")
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


def check_ratified_are_numbered(records: Path) -> list[str]:
    """A ratified record carries a number in its filename.

    **THE CONVERSE OF `check_numbered_are_ratified`, AND IT WAS MISSING.** Both
    of the other checks key on the *filename*: one asks whether a numbered file
    is ratified, and the index check compares numbers taken from filenames
    against numbers in the index. So a record whose Status was flipped to
    `Accepted` and whose file was never renamed matched neither, and the lint
    reported clean.

    That state reads as ratified to a person and as nonexistent to every check
    — the worst of the two. `docs/ref/ratification.md` documents the *other*
    failure, where the index was updated too, and that one does fire. This is
    the case where the ratifier stopped one step earlier.

    Found by performing the ratification steps wrongly on purpose rather than by
    reading the lint, which is the practice charter `a-check-is-evidence-after-it-fails` states.
    """
    failures = []
    for path in sorted(records.glob("*.md")):
        if NUMBERED_FILENAME.match(path.name):
            continue
        status = status_of(path.read_text(encoding="utf-8"))
        if is_ratified(status):
            failures.append(
                f"{path}: Status {status!r} but the filename carries no number. "
                "Ratification renames the file; see docs/ref/ratification.md. "
                "Left unrenamed the record is invisible to the index check too."
            )
    return failures


# The three H1 forms this estate writes, all meaning "unratified record":
#   `# QM-XXXX --- Title`     the org corpus
#   `# ADR-XXXX --- Title`    a project following the seed template
#   `# DRAFT --- Title`       a project that marks the state instead of the slot
# Only the title travels into an index, so all three prefixes come off. Handling
# two of the three silently dropped a word from every title in the third, and
# every one of that project's eleven records then read as unlisted while its
# index listed all eleven correctly.
TITLE_PREFIX = re.compile(r"^(?:DRAFT|(?:ADR|QM)-[0-9X]{4})\s*[-–—]\s*")


def _title_of(path: Path) -> str:
    """A record's H1, minus whichever prefix marks it. Empty when it has no H1."""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("# "):
            return TITLE_PREFIX.sub("", line[2:]).strip()
        if line.strip():
            break
    return ""


def _flatten(text: str) -> str:
    """Case- and punctuation-insensitive, so a title quoted in a sentence still
    matches the heading it came from. Backticks, dashes and stray spacing are
    exactly what differs between the two, and none of them carries meaning."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def check_index_matches_directory(records: Path, index: Path) -> list[str]:
    """The index lists every record, and every row names a file that exists.

    TWO COMPARISONS, AND ONLY ONE OF THEM CAN FIRE BEFORE A RATIFICATION. The
    numbered comparison below is the older half: it reads the number out of a
    filename and out of a row's first cell. Numbers are assigned at
    ratification, so in a corpus where nothing has been ratified yet *both*
    sets are empty, and it compares nothing to nothing and reports clean --
    every run, for the whole life of the check, while the index it guards can
    be missing records. That is not a hypothetical: it was the state of this
    corpus's own index when the filename comparison was added, and four records
    were absent, two of them the records behind charter principles.

    So the filename comparison is the half that works from day one. It matches
    each record file against the link targets in the index's table rows, by
    basename, so it is indifferent to whether an index links `DRAFT-x.md` from
    inside the directory or `records/DRAFT-x.md` from the repository root.

    A check that cannot fail is not evidence -- charter `a-check-is-evidence-after-it-fails`.

    WHAT IT STILL CANNOT SEE, found by trying to walk past it rather than by
    reading it: a record in a subdirectory of the records directory is invisible
    to both halves, because the scan is `*.md` and a link pointing there lands
    under a different parent, so neither set holds it and it passes.

    **TWO CONVENTIONS ARE LISTED, BECAUSE THIS CORPUS HAS TWO.** A record counts
    as listed if a table row links its file, *or* if its title appears in the
    index prose -- which is the `Drafts in flight (numberless, by title): ...`
    line this seed's own `adr/README.md` template ships. The org corpus lists
    unratified drafts as linked table rows; the seed tells a project to list
    them by title in that line, and numbers arrive in the table only at
    ratification.

    Reading only the table was wrong and would have failed every project that
    followed the template it was given. It was caught on a project branch whose
    author had listed all three records exactly as the seed prescribes, in a
    commit whose message says "and put it in the index" -- because they had.
    """
    if not index.exists():
        return [f"{index}: index file not found."]

    index_text = index.read_text(encoding="utf-8")

    on_disk = {
        int(m.group(1))
        for p in records.glob("*.md")
        if (m := NUMBERED_FILENAME.match(p.name))
    }

    # The directory's own furniture is not a record. An index and a template
    # are never listed in the index, and reading them as missing rows would
    # make the check fire on every correctly-set-up project.
    on_disk_files = {
        p.name for p in records.glob("*.md")
        if p.name not in ("README.md", "TEMPLATE.md") and p.resolve() != index.resolve()
    }

    in_index = set()
    in_index_files = set()
    for line in index_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        first = re.sub(r"^(?:ADR|QM)-", "", cells[0]).strip()
        if first.isdigit():
            in_index.add(int(first))
        for target in INDEX_LINK.findall(line):
            # Only links that land *in the records directory* are index rows.
            # An index page carries other tables -- this corpus's own README
            # links the handbook and the docs site from the same file -- and
            # reading those as record rows reported fourteen handbook pages as
            # missing records the first time this ran. Resolve the target
            # against the index's own directory, because an index inside the
            # records directory links `DRAFT-x.md` and one at the repository
            # root links `records/DRAFT-x.md`, and both are correct.
            landed = (index.parent / target).resolve()
            if landed.parent == records.resolve():
                in_index_files.add(landed.name)

    # The second convention: a record listed by title in the index prose. The
    # title is the H1 minus its `ADR-XXXX — ` / `QM-XXXX — ` prefix, compared
    # with punctuation and case flattened, because the drafts line is written
    # by a person and a title is quoted the way a sentence quotes it.
    # A title counts as listed when a whole *segment* of the index equals it --
    # a bullet item, or one semicolon-separated part of the drafts line. Bare
    # substring containment was the first implementation, and an adversarial
    # pass walked straight through it: a record titled "The" passed against an
    # index whose prose merely contained the word. Equality over segments keeps
    # both listing conventions working and closes the accidental third one,
    # "mentioned somewhere".
    segments = set()
    for line in index_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            segments.add(_flatten(stripped[2:]))
        elif "by title)" in stripped:
            after = stripped.split(":", 1)[-1]
            for part in after.replace(";", "\n").splitlines():
                segments.add(_flatten(part.rstrip(".")))
        elif ";" in stripped and not stripped.startswith("|"):
            for part in stripped.replace(";", "\n").splitlines():
                segments.add(_flatten(part.rstrip(".")))
    segments.discard("")
    listed_by_title = set()
    for path in records.glob("*.md"):
        if path.name in in_index_files or path.name in ("README.md", "TEMPLATE.md"):
            continue
        title = _flatten(_title_of(path))
        if title and title in segments:
            listed_by_title.add(path.name)

    failures = []
    for name in sorted(on_disk_files - in_index_files - listed_by_title):
        failures.append(
            f"{index}: {name} exists in {records}/ and the index neither links it "
            f"nor names its title. List it as a table row, or in the "
            f"`Drafts in flight (numberless, by title)` line."
        )
    for name in sorted(in_index_files - on_disk_files):
        failures.append(
            f"{index}: a row links {name}, which is not a file in {records}/."
        )
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
    failures += check_ratified_are_numbered(records)
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
