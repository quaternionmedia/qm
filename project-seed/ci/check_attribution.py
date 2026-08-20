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

THREE CHECKS, all independent:

    --records-dir DIR   no vendor or model name in the prose of any record there
    --base-ref REF      no vendor or model name in any commit subject REF..HEAD,
                        and no commit trailer or author field in that range
                        standing on an unmonitored address or a tool's name

THE TRAILER CHECK IS THE ONE THAT WAS MISSING. `DRAFT-human-only-contributorship.md`
section 3 bans a trailer or author field naming "an address that is not a
monitored inbox reachable to a human accountable for the content", and names
vendor `noreply@` addresses as the case. Every surface in this corpus describes
that rule as enforced -- the adr-lint workflow's own comment says "the co-author
trailer was already forbidden" -- and until this function existed, nothing
anywhere read a trailer. Default tooling appends these, so a rule enforced by
remembering to suppress it is a rule that holds until somebody is busy.

TWO INDEPENDENT WAYS ATTRIBUTION FAILS, because the record and the seed
AGENTS.md draw slightly different lines and both are worth holding:

  - **The address is unmonitored.** The record's own test. `noreply@vendor`
    names nobody who can be asked why.
  - **The name is a tool's.** The seed AGENTS.md adds "do not add yourself, your
    model name". A trailer reading `<Model> <a@real.address>` routes somewhere
    real and still credits software for the work.

WHERE AN ADDRESS THAT LOOKS UNMONITORED IS FINE, and the check would be useless
without the distinction:

  - **A forge's per-user alias** -- `someone@users.noreply.github.com`. That is
    not an unreachable address standing in for accountability; it *is* an
    account, and it names one person reachable through the forge. Refusing it
    would refuse every contributor who keeps their email private.
  - **The committer field, which is not read at all.** Every squash merge on a
    GitHub repository is committed by `GitHub <noreply@github.com>` -- measured
    on this corpus before the rule was written. Checking the committer would
    fail every merge this org makes, on the forge's own identity. Section 3 says
    "author field", and the author is the accountable human.

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

# --- attribution metadata ---------------------------------------------------

# A local part that says up front that nobody reads it. The record's test is
# whether a human accountable for the content can be reached at the address, and
# these announce that they cannot.
UNMONITORED = re.compile(
    r"^(?:no[._+-]?reply|do[._+-]?not[._+-]?reply)(?:[+._-][^@]*)?$",
    re.IGNORECASE,
)

# ...except a forge's per-user alias, which is the opposite of an unreachable
# address standing in for accountability: it identifies one account, and the
# person behind it is reachable through the forge. Matched on the host label
# rather than on a list of forges, so a self-hosted instance is not a hole.
PER_USER_ALIAS = re.compile(r"@users\.no[._-]?reply\.", re.IGNORECASE)

# An address inside a trailer or an identity. Deliberately permissive about what
# sits between the brackets: a pattern that only recognised well-formed
# addresses would wave through anything malformed, and malformed is the cheapest
# way past a guard.
ADDRESS = re.compile(r"<([^<>]*)>")

# And an address standing on its own, with no display name around it. Found by
# attacking the check: `Co-authored-by: noreply@vendor` has no brackets, so the
# bracketed pattern saw no address at all and the *name* test flagged it -- for
# the domain, which meant a real contributor's bare `person@vendor` address
# would have been refused with the words "names a tool". Right verdict, wrong
# reason, and the wrong reason is what teaches somebody the check is stupid.
BARE_ADDRESS = re.compile(r"(?<![<\w.+-])([^\s<>@,()]+@[^\s<>@,()]+)(?![>\w])")

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


# Commit subjects allowed to name a tool, by full SHA, each with the reason.
#
# THE OBJECTION TO A LIST LIKE THIS IS REAL, and it is the one
# `check_signatures.py` states when it chooses a date instead: a list of blessed
# SHAs grows quietly and nobody can tell later which entries were deliberate.
# Two things answer it here. Every entry carries its reason, printed on every
# run, so an exemption nobody can justify is an exemption a reader can see. And
# a commit subject is immutable -- the alternative to exempting is rewriting
# somebody else's history, which this org does not do, so the population is
# bounded by acts that already happened rather than by future convenience.
#
# An entry is added by editing this file, in a pull request, with the reason
# written down. That is the whole control.
EXEMPT_SUBJECTS = {
    "35ebca6ac214bafca34985cb68c48b7d6b99b040": (
        "Kept deliberately as the worked example this rule is taught from. It is "
        "a real commit, by a real contributor, that named a model in its subject "
        "before the check existed -- and it is now permanently in the history of "
        "the corpus that forbids it. A rule illustrated by a live instance in its "
        "own tree is harder to dismiss than one illustrated by a hypothetical, "
        "and the cost of the illustration is that this exemption exists."
    ),
}


def verify_ref(base_ref: str) -> str | None:
    """The one message about a ref that is not there.

    Spelled once because two checks read the same range: each still probes, so
    either works alone, and `main` probes first so a bad ref is one finding
    rather than the same sentence twice under a count of two.
    """
    probe = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{base_ref}^{{commit}}"],
        capture_output=True,
        text=True,
    )
    if probe.returncode:
        return (
            f"check_attribution: {base_ref} does not exist. Pass a ref that does, "
            f"or drop --base-ref."
        )
    return None


def check_commit_subjects(base_ref: str) -> list[str]:
    """No vendor or model name in any commit subject in base_ref..HEAD."""
    problem = verify_ref(base_ref)
    if problem:
        return [problem]
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
        if sha in EXEMPT_SUBJECTS:
            # Announced, never silent. An exemption a run does not print is a
            # hole in a check that still reports green.
            print(
                f"check_attribution: {sha[:8]} names a tool in its subject and is "
                f"exempt.\n  {subject!r}\n  {EXEMPT_SUBJECTS[sha]}"
            )
            continue
        named = ", ".join(repr(v) for v in found.values())
        failures.append(
            f"{sha[:8]}: commit subject names a tool -- found {named} in "
            f"{subject!r}. The subject says what changed; tool involvement goes "
            f"in a `Tools:` note on the artifact."
        )
    return failures


# THERE IS NO EXEMPTION LIST FOR THIS CHECK, and that is a decision rather than
# an omission. EXEMPT_SUBJECTS above exists because a commit subject is
# immutable and the alternative was rewriting somebody's history. Attribution
# does not need the same hatch: this runs over a pull request's own range, so
# the commits it reads are the ones their author can still amend, and section 4
# leaves merged history alone by never being asked about it. An empty list would
# be an invitation to add the first red rather than fix it.


def addresses_in(value: str) -> list[str]:
    """Every address in a trailer value or an identity, bracketed or bare."""
    found = [a.strip() for a in ADDRESS.findall(value)]
    remainder = ADDRESS.sub(" ", value)
    found += [a.strip() for a in BARE_ADDRESS.findall(remainder)]
    return [a for a in found if a]


def attribution_problems(value: str) -> list[str]:
    """Why a trailer value or an identity cannot stand as attribution.

    Two independent tests, either of which is enough: the name is a tool's, or
    the address is one nobody reads. Reported separately because the fixes
    differ -- one is deleting a byline, the other is naming somebody who can be
    asked why.
    """
    problems: list[str] = []

    # The name is what is left once the addresses are removed. Matched there
    # rather than over the whole value on purpose: `someone@anthropic.com` is a
    # human who works at a vendor, and section 3 says naming them is always
    # fine. The ban is on software standing where a person should be.
    named_by = BARE_ADDRESS.sub("", ADDRESS.sub("", value)).strip().strip(",")
    found = families_in(named_by)
    if found:
        tools = ", ".join(repr(v) for v in found.values())
        problems.append(f"names a tool where a person should be -- found {tools}")

    for address in addresses_in(value):
        local, _, domain = address.partition("@")
        # A per-user alias names an account, so it is exempt -- but only when
        # the local part names one. `noreply@users.noreply.anything` is a
        # no-reply wearing the exemption, and the adversarial pass walked
        # straight through the earlier version with exactly that.
        if PER_USER_ALIAS.search("@" + domain) and not UNMONITORED.match(local):
            continue
        if UNMONITORED.match(local):
            problems.append(f"stands on <{address}>, which nobody reads")

    return problems


def check_commit_attribution(base_ref: str) -> list[str]:
    """No trailer or author field in base_ref..HEAD naming a tool or a void.

    Git parses the trailers rather than a regex here. Git owns the definition --
    which paragraph they must sit in, folded continuations, which colons count --
    and a second definition written beside it would disagree with the forge,
    which uses the same one.
    """
    problem = verify_ref(base_ref)
    if problem:
        return [problem]

    # Unit-separated fields, record-separated commits. A trailer block is
    # multi-line, so a line-oriented format would split one commit across
    # several records and hang a trailer on the wrong SHA.
    fmt = "%H%x1f%an <%ae>%x1f%(trailers:only=true,unfold=true)%x1e"
    result = subprocess.run(
        ["git", "log", "--format=" + fmt, f"{base_ref}..HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return ["check_attribution: git log failed:\n" + result.stderr.strip()]

    failures: list[str] = []
    for entry in result.stdout.split("\x1e"):
        if not entry.strip():
            continue
        sha, _, rest = entry.strip().partition("\x1f")
        author, _, trailers = rest.partition("\x1f")

        findings: list[str] = []
        for problem in attribution_problems(author):
            findings.append(f"author {author!r} {problem}")
        for line in trailers.splitlines():
            key, sep, value = line.partition(":")
            if not sep or not value.strip():
                continue
            for problem in attribution_problems(value):
                findings.append(f"trailer {key.strip()!r} {problem}")

        for finding in findings:
            failures.append(
                f"{sha[:8]}: {finding}. A contributor is someone who can be "
                f"asked why, and reached to answer; tool involvement goes in a "
                f"`Tools:` note on the artifact, never in a byline."
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
        unreachable = verify_ref(args.base_ref)
        if unreachable:
            failures.append(unreachable)
        else:
            failures += check_commit_subjects(args.base_ref)
            failures += check_commit_attribution(args.base_ref)

    if failures:
        for line in failures:
            print(line)
        print(f"\ncheck_attribution: {len(failures)} finding(s).")
        return 1

    checked = []
    if args.records_dir:
        checked.append(f"records in {args.records_dir}")
    if args.base_ref:
        checked.append(
            f"commit subjects, trailers and authors in {args.base_ref}..HEAD"
        )
    print(f"check_attribution: clean ({', '.join(checked)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
