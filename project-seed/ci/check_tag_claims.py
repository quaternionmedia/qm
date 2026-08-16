#!/usr/bin/env python3
"""Refuse a version tag that does not carry the claims a version tag makes.

SEED FILE, run in place: a forking project runs it out of the governance
submodule. Nothing copies it.

WHAT THIS IS FOR. `records/DRAFT-version-tags-are-claims.md` §2 says a `v*` tag
asserts three things at the tagged commit -- a human reviewed the change set, a
human manually tested it against its real runtime, and deterministic automated
validation passed. §6 says the tag is annotated and the annotation names who
reviewed, what was manually tested, and what the automated gate covered
*including what it did not*. §7 says that is mechanical rather than customary.

Until this file existed it was customary. Two lightweight tags in this org --
`alfred@v0.2.0` and `datum@v0.0.1` -- assert what §6 says a lightweight tag
cannot, because nothing was reading them.

THREE MODES, independent and usable alone:

    --tag NAME          one tag: object type, name form, annotation fields
    --all               every `v*` tag reachable here, as a table plus exit code
    --test-output FILE  a captured test run: refuse skips, reruns, retries

WHAT THIS CANNOT DO, and the list matters more than the checks:

  - It cannot tell whether the human review happened. It reads an annotation
    somebody wrote. A tag whose annotation names a reviewer who never looked
    passes here and is a lie told in git rather than a lie told in a meeting,
    which is the entire improvement on offer.
  - It cannot tell whether the manual test was performed, only that the
    annotation states one. §2's second clause is not mechanisable and this
    file does not pretend otherwise.
  - It cannot establish determinism. `--test-output` refuses a run that
    *announces* nondeterminism -- a skip, a rerun, a retry. A suite that is
    nondeterministic and silent about it passes.
  - It cannot stop a tag being created. That is a host-side tag-protection
    ruleset, named in §7 and applied outside this repository.

So a green result here means: the tag is shaped like a claim. Whether the claim
is true is a human's word, recorded where a reader can find it and hold them to
it. That is what §6 asks for and it is all it asks for.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field

# A tag name this record governs. `v` then semver, with an optional
# pre-release identifier -- §4's `v0.2.0-rc.1`, which is "a tag that says so".
TAG_NAME = re.compile(
    r"^v(?P<major>0|[1-9]\d*)"
    r"\.(?P<minor>0|[1-9]\d*)"
    r"\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?$"
)

# The annotation fields §6 requires. The trailing pair is the "including what
# it did not" clause, which is the one a release note always drops.
REQUIRED_FIELDS = {
    "Reviewed-by": "who reviewed the change set (§2, first claim)",
    "Manually-tested": "what was tested against the real runtime (§2, second claim)",
    "Automated-gate": "what the automated validation covered (§2, third claim)",
    "Not-covered": "what the automated gate did not cover (§6)",
}

FIELD_LINE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z-]*):\s*(?P<value>.*)$")

# A pytest summary line: "278 passed, 11 skipped in 8.33s". Each count is read
# on its own so a suite reporting only skips is still read.
SUMMARY_COUNT = re.compile(r"(?P<count>\d+)\s+(?P<outcome>[a-z]+)")

# Outcomes that void §3. `skipped` and `xfailed` are tests that did not run;
# `rerun` and `flaky` are tests that did not run deterministically.
NONDETERMINISTIC_OUTCOMES = ("skipped", "xfailed", "xpassed", "rerun", "flaky", "error")

# The subject name used for a captured test run, which is not a tag and must
# not be described with a tag's properties.
TEST_RUN = "<test run>"


@dataclass
class Verdict:
    """One tag's result. `ok` is the whole point; `problems` is why not."""

    tag: str
    ok: bool = True
    annotated: bool = False
    problems: list[str] = field(default_factory=list)

    def fail(self, why: str) -> None:
        self.ok = False
        self.problems.append(why)


def run_git(args: list[str], cwd: str | None = None) -> tuple[int, str]:
    """Run git and return (exit code, stripped stdout). stderr is discarded.

    Every caller here treats a non-zero exit as "the ref is not there", which
    is the only failure git reports for these commands.
    """
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout.strip()


def parse_annotation(body: str) -> dict[str, str]:
    """Read `Key: value` lines out of a tag annotation.

    Only lines that are entirely a field count. A sentence containing a colon
    is prose, not a field -- otherwise "Tested: see below" buried mid-paragraph
    would satisfy a clause it never states.

    A field whose value is empty or whitespace is absent, not present:

    >>> parse_annotation("Reviewed-by: Ada\\nManually-tested:   \\nnotes here")
    {'Reviewed-by': 'Ada'}
    >>> parse_annotation("no fields at all")
    {}
    """
    fields: dict[str, str] = {}
    for line in body.splitlines():
        match = FIELD_LINE.match(line.strip())
        if match is None:
            continue
        value = match.group("value").strip()
        if value:
            fields[match.group("key")] = value
    return fields


def check_annotation(tag: str, object_type: str, body: str) -> Verdict:
    """Judge one tag from facts already read out of git.

    Split from the git calls so the whole rule is testable without a
    repository -- the tag record's own §3 complaint about tests that need a
    fixture to be present.

    >>> check_annotation("v1.0.0", "commit", "").ok
    False
    >>> good = ("Reviewed-by: Ada\\nManually-tested: on the rig\\n"
    ...         "Automated-gate: 278 unit tests\\nNot-covered: the flow layer")
    >>> check_annotation("v1.0.0", "tag", good).ok
    True
    >>> check_annotation("1.0.0", "tag", good).ok
    False
    """
    verdict = Verdict(tag=tag)

    if TAG_NAME.match(tag) is None:
        verdict.fail(f"name is not vMAJOR.MINOR.PATCH[-prerelease]: {tag!r}")

    if object_type != "tag":
        verdict.fail(
            "lightweight tag; §6 requires an annotated tag, and a lightweight "
            "one cannot carry the annotation the other clauses are read from"
        )
        # Every field check below would restate this one failure. Stop here so
        # the output names the cause once.
        return verdict

    verdict.annotated = True
    fields = parse_annotation(body)
    for key, why in REQUIRED_FIELDS.items():
        if key not in fields:
            verdict.fail(f"annotation has no `{key}:` line -- {why}")

    return verdict


def read_tag(tag: str, cwd: str | None = None) -> Verdict:
    """Read one tag out of git and judge it."""
    code, object_type = run_git(["cat-file", "-t", tag], cwd=cwd)
    if code != 0:
        verdict = Verdict(tag=tag)
        verdict.fail(f"no such tag in this repository: {tag!r}")
        return verdict

    # A lightweight tag's `contents` is the *commit* message, which is why the
    # object type is established first and the body is only trusted after.
    _, body = run_git(["tag", "-l", "--format=%(contents)", tag], cwd=cwd)
    return check_annotation(tag, object_type, body)


def list_tags(cwd: str | None = None) -> list[str]:
    """Every `v*` tag in this repository, newest first by creation."""
    code, out = run_git(
        ["for-each-ref", "--sort=-creatordate", "--format=%(refname:short)", "refs/tags/v*"],
        cwd=cwd,
    )
    if code != 0 or not out:
        return []
    return out.splitlines()


def parse_test_summary(text: str) -> dict[str, int]:
    """Counts from a pytest summary line, or {} if there is no summary.

    The last summary-looking line wins: a run that prints per-file progress
    still ends with the totals.

    >>> parse_test_summary("278 passed, 11 skipped in 8.33s")
    {'passed': 278, 'skipped': 11}
    >>> parse_test_summary("nothing here")
    {}
    """
    counts: dict[str, int] = {}
    for line in text.splitlines():
        stripped = line.strip().strip("=").strip()
        if " in " not in stripped and "passed" not in stripped and "failed" not in stripped:
            continue
        found = {
            match.group("outcome"): int(match.group("count"))
            for match in SUMMARY_COUNT.finditer(stripped)
        }
        # `in 8.33s` has no outcome word attached, so a stray number cannot
        # invent an outcome. Only recognised words are kept.
        found = {k: v for k, v in found.items() if k.isalpha() and k != "in"}
        if found:
            counts = found
    return counts


def check_test_output(text: str) -> Verdict:
    """§3 and §7: a release test run that announces nondeterminism is not a gate.

    >>> check_test_output("278 passed, 11 skipped in 8.33s").ok
    False
    >>> check_test_output("278 passed in 8.33s").ok
    True
    >>> check_test_output("no summary line at all").ok
    False
    """
    verdict = Verdict(tag=TEST_RUN)
    counts = parse_test_summary(text)

    if not counts:
        verdict.fail(
            "no test summary found. An absent result is not a passing result -- "
            "§2's third claim needs a run that reported something"
        )
        return verdict

    if counts.get("failed") or counts.get("errors"):
        verdict.fail(f"the suite did not pass: {counts}")

    for outcome in NONDETERMINISTIC_OUTCOMES:
        if counts.get(outcome):
            verdict.fail(
                f"{counts[outcome]} {outcome} -- §3: a test that skips, reruns or "
                f"retries contributes nothing to the automated-validation claim"
            )

    if not counts.get("passed"):
        verdict.fail("no test passed, so the automated gate covered nothing")

    return verdict


def report(verdicts: list[Verdict], stream=sys.stdout) -> None:
    """Print one line per verdict, then the problems under each failure."""
    for verdict in verdicts:
        mark = "ok  " if verdict.ok else "FAIL"
        # `annotated`/`lightweight` is a property of a tag object. A captured
        # test run has neither, and printing "(lightweight)" beside one labels
        # it with a fact from a different subject -- which is the kind of
        # confidently-wrong output this file exists to refuse.
        if verdict.tag == TEST_RUN:
            print(f"{mark} {verdict.tag}", file=stream)
        else:
            kind = "annotated" if verdict.annotated else "lightweight"
            print(f"{mark} {verdict.tag}  ({kind})", file=stream)
        for problem in verdict.problems:
            print(f"       - {problem}", file=stream)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Refuse a version tag that does not carry its claims.",
        epilog=(
            "Green means the tag is shaped like a claim. Whether the claim is "
            "true is the tagger's word, which is what records/"
            "DRAFT-version-tags-are-claims.md §6 asks to be written down."
        ),
    )
    parser.add_argument("--tag", help="one tag to check")
    parser.add_argument("--all", action="store_true", help="every v* tag here")
    parser.add_argument("--test-output", help="file holding a captured test run")
    parser.add_argument("--repo-dir", default=None, help="repository to read (default: cwd)")
    args = parser.parse_args(argv)

    if not (args.tag or args.all or args.test_output):
        parser.error("give one of --tag, --all, or --test-output")

    verdicts: list[Verdict] = []

    if args.tag:
        verdicts.append(read_tag(args.tag, cwd=args.repo_dir))

    if args.all:
        tags = list_tags(cwd=args.repo_dir)
        if not tags:
            # Not a failure. A project that has never tagged has made no claim,
            # which §4 says is a legitimate state rather than a deficiency.
            print("no v* tags in this repository; nothing claimed, nothing to check")
        verdicts.extend(read_tag(tag, cwd=args.repo_dir) for tag in tags)

    if args.test_output:
        try:
            text = open(args.test_output, encoding="utf-8", errors="replace").read()
        except OSError as exc:
            print(f"FAIL <test run>  ({exc})", file=sys.stderr)
            return 1
        verdicts.append(check_test_output(text))

    report(verdicts)

    failed = [v for v in verdicts if not v.ok]
    if failed:
        print(
            f"\n{len(failed)} of {len(verdicts)} checked item(s) do not carry "
            f"their claims. See records/DRAFT-version-tags-are-claims.md.",
            file=sys.stderr,
        )
        return 1

    if verdicts:
        print(f"\n{len(verdicts)} checked item(s) carry their claims.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
