#!/usr/bin/env python3
"""Refuse vendor and model names where they do not belong.

SEED FILE, run in place: a forking project runs it out of the governance
submodule. Nothing copies it.

WHAT THIS IS FOR. Tool involvement is disclosed in one place -- a `Tools:` note
on the artifact that calls for one -- and nowhere else. It is not a byline, not a
commit subject, and not a sentence in a binding record. The existing rule covers
only the co-author trailer, so a commit titled "Re-refactor docs with <model>"
passes every check this org has, and that name is then in the permanent history
of a corpus meant to outlive the product.

The deeper reason is the seams doctrine: a record naming a vendor's mechanism in
prose reads, to the next person, as that mechanism being sanctioned. A record
states the invariant; a clearly-labelled adapter names the product.

TWO CHECKS, both independent and both usable alone:

    --records-dir DIR   no vendor or model name in the prose of any record there
    --base-ref REF      no vendor or model name in any commit subject REF..HEAD

WHERE A NAME IS FINE, and these are the point rather than loopholes:

  - **Inside a code span or fence.** A record forbidding a trailer has to quote
    the trailer, exactly as the banned-vocabulary check lets the discipline
    record quote its own list. Also house style for a path, so `CLAUDE.md` and
    `.github/copilot-instructions.md` are covered by the same exemption.
  - **In `perspectives/`.** Dated, attributed, non-binding, and their own README
    *requires* a `Tools:` row. This script never reads them.
  - **In an enumeration of competing vendors.** Nobody attributes one piece of
    work to four rivals, so a paragraph naming three or more vendor families is
    making an interoperability claim, not a byline. This corpus needs to be able
    to make one: the record establishing that a plain `AGENTS.md` is read by
    every mainstream agent names nine of them, and that passage is the evidence
    the format is vendor-neutral -- which is what the seams doctrine asks for.
    Refusing it would invert the rule.

The window for that count is the **paragraph**, not the line. Prose wraps, and
the nine-agent enumeration above spans three lines: the first names two families,
the second three, the third one. Counting per line would refuse two thirds of a
sentence whose whole point is breadth.

Exit status is 1 if anything is found, 0 otherwise. There is no advisory tier --
unlike check_pr_base.py, every finding here is a refusal, because the fix is
always the same: move the name into a `Tools:` note or a code span.

Usage:
    python check_attribution.py --records-dir records
    python check_attribution.py --base-ref origin/main
    python check_attribution.py --records-dir records --base-ref origin/main
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

# Grouped by vendor family, because the number of *families* in a paragraph is
# what separates attribution from interoperability.
FAMILIES: dict[str, re.Pattern] = {
    "anthropic": re.compile(
        r"\banthropic\b|\bclaude\b|\b(?:sonnet|opus|haiku|fable)[\s-]*\d",
        re.IGNORECASE,
    ),
    "openai": re.compile(
        r"\bopenai\b|\bchatgpt\b|\bcodex\b|\bgpt-?\d", re.IGNORECASE
    ),
    "microsoft": re.compile(r"\bcopilot\b", re.IGNORECASE),
    "google": re.compile(r"\bgemini\b|\bdeepmind\b", re.IGNORECASE),
    "meta": re.compile(r"\bllama[\s-]*\d", re.IGNORECASE),
}

# Three competing vendors in one paragraph is an enumeration. The threshold is
# crude on purpose, and explained rather than tunable: the alternative was an
# inline exemption marker, which is a comment people learn to add without
# reading.
ENUMERATION_THRESHOLD = 3

# `opus` and `haiku` are ordinary words -- a corpus about music or poetry tooling
# would use both -- so they are only matched when followed by a version number.
# The accepted cost is that a bare "Opus" goes unflagged, which is right: it is
# not a byline.

FENCE = re.compile(r"^\s*```.*?^\s*```", re.MULTILINE | re.DOTALL)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`", re.DOTALL)


def prose_only(text: str) -> str:
    """Strip fences, HTML comments and code spans, preserving line numbers.

    Each is replaced by as many blank lines as it spanned, so a reported line
    number still matches the file on disk. Same approach as adr_lint.py, and
    deliberately duplicated rather than imported: this runs standalone out of a
    submodule, and a shared helper would make it need a package.
    """

    def blank(match: re.Match) -> str:
        return "\n" * match.group(0).count("\n")

    text = HTML_COMMENT.sub(blank, text)
    text = FENCE.sub(blank, text)
    text = INLINE_CODE.sub(blank, text)
    return text


def families_in(text: str) -> dict[str, str]:
    """Which vendor families a span of text names, and the first hit for each."""
    found: dict[str, str] = {}
    for family, pattern in FAMILIES.items():
        match = pattern.search(text)
        if match:
            found[family] = match.group(0)
    return found


def paragraphs(text: str) -> list[tuple[int, str]]:
    """Split into (first line number, paragraph text) on blank lines."""
    out: list[tuple[int, str]] = []
    start, buf = 1, []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.strip():
            if not buf:
                start = lineno
            buf.append(line)
        elif buf:
            out.append((start, "\n".join(buf)))
            buf = []
    if buf:
        out.append((start, "\n".join(buf)))
    return out


def check_records(records: Path) -> list[str]:
    """No vendor or model name in the prose of any record."""
    if not records.is_dir():
        return [f"{records}: not a directory"]
    failures: list[str] = []
    for path in sorted(records.glob("*.md")):
        text = prose_only(path.read_text(encoding="utf-8"))
        for start, para in paragraphs(text):
            found = families_in(para)
            if not found or len(found) >= ENUMERATION_THRESHOLD:
                continue
            named = ", ".join(repr(v) for v in found.values())
            failures.append(
                f"{path}:{start}: a record states the invariant and does not name "
                f"the tool -- found {named}. Move it to a `Tools:` note, or put it "
                f"in a code span if you are quoting it."
            )
    return failures


def check_commit_subjects(base_ref: str) -> list[str]:
    """No vendor or model name in any commit subject in base_ref..HEAD."""
    probe = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{base_ref}^{{commit}}"],
        capture_output=True,
        text=True,
    )
    if probe.returncode:
        return [
            f"check_attribution: {base_ref} does not exist. Pass a ref that does, "
            f"or drop --base-ref."
        ]
    result = subprocess.run(
        ["git", "log", "--format=%H%x1f%s", f"{base_ref}..HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return [f"check_attribution: git log failed:\n{result.stderr.strip()}"]

    failures: list[str] = []
    for entry in result.stdout.splitlines():
        if not entry.strip():
            continue
        sha, _, subject = entry.partition("\x1f")
        # No enumeration exemption here. A commit subject has no room for an
        # interoperability claim, and every real instance is attribution.
        found = families_in(subject)
        if not found:
            continue
        named = ", ".join(repr(v) for v in found.values())
        failures.append(
            f"{sha[:8]}: commit subject names a tool -- found {named} in "
            f"{subject!r}. The subject says what changed; tool involvement goes "
            f"in a `Tools:` note on the artifact."
        )
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--records-dir", help="Directory of records to read as prose")
    ap.add_argument("--base-ref", help="Check commit subjects in <ref>..HEAD")
    args = ap.parse_args()

    if not args.records_dir and not args.base_ref:
        ap.error("pass --records-dir, --base-ref, or both")

    failures: list[str] = []
    if args.records_dir:
        failures += check_records(Path(args.records_dir))
    if args.base_ref:
        failures += check_commit_subjects(args.base_ref)

    if failures:
        for line in failures:
            print(line)
        print(f"\ncheck_attribution: {len(failures)} finding(s).")
        return 1

    checked = []
    if args.records_dir:
        checked.append(f"records in {args.records_dir}")
    if args.base_ref:
        checked.append(f"commit subjects in {args.base_ref}..HEAD")
    print(f"check_attribution: clean ({', '.join(checked)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
