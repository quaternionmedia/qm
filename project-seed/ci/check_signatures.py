#!/usr/bin/env python3
"""Refuse a branch whose own commits carry no verifiable signature.

SEED FILE, run in place: a forking project runs it out of the governance
submodule. Nothing copies it.

WHAT THIS IS FOR. A signature is what makes the author field a claim somebody
made rather than a string anybody can type. `records/DRAFT-human-only-contributorship.md`
turns on attribution being real, and nothing in this org has ever checked it.

The history says what happens without a check. Signing stopped in this corpus at
2026-08-12T23:29, mid-branch, immediately after a signed commit -- a session
added a flag disabling it and nothing noticed. `origin/main`'s recent history
carries no signature at all, and across every ref the repository holds a mix of
signed, unsigned and uncheckable.

**ONLY THE COMMITS THE BRANCH ADDS.** `--base-ref` is required and the range is
`base..head`. Checking whole history would fail every pull request in this
repository forever, for commits their author did not write and cannot re-sign --
a gate that can only be satisfied by rewriting somebody else's history is a gate
that gets switched off.

WHAT THIS CANNOT DO, and the list is most of it:

  - It cannot tell that the signer is the person in the author field beyond what
    the key attests, and it does not check who the key belongs to. A valid
    signature by an unknown key passes `--allow-untrusted`, which is the default,
    because a trust store nobody maintains would fail honest work.
  - It cannot make an unsigned commit signed. The remedy is the author
    re-signing their own commits, which is history rewriting and is the author's
    call, so this reports and does not offer to fix.
  - It says nothing about content. A signed commit is an attested commit, not a
    correct one.

Exit status is the contract: 0 when every commit in range carries a signature
this git could read, 1 otherwise.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

# `git log --format=%G?` per commit. The values that mean "a signature is
# present and this git could verify it".
#
#   G  good              U  good, untrusted key
#   X  good, expired     Y  good, key expired     R  good, revoked key
#   B  bad               E  cannot be checked     N  no signature
#
# `U` is the ordinary state anywhere the signer's key is not in the local
# keyring, which is every CI runner. Treating it as failure would fail every
# correctly-signed commit on the one machine that matters.
GOOD = {"G", "U"}
GOOD_WITH_WARNING = {"X", "Y", "R"}
NO_SIGNATURE = "N"
UNVERIFIABLE = "E"
BAD = "B"

# Commits committed before this date are reported and not failed.
#
# WHY A CUTOFF EXISTS AT ALL. This check was written on 2026-08-15, and the
# branch that introduced it carries nine unsigned commits made before it. They
# cannot be signed without rewriting history, which this org's governance does
# not permit. A gate whose only remedy is a forbidden act is a gate that gets
# switched off within a week, and the corpus would then have neither the history
# nor the check.
#
# WHY IT IS A DATE AND NOT A LIST. A list of blessed SHAs grows silently and
# nobody can tell later which were exempted deliberately. A date is one number,
# it is in the diff that introduced it, and moving it is a reviewable edit.
#
# THIS IS A DEBT, AND IT DOES EXIT GREEN. Be exact about that, because the
# comment here first claimed grandfathered commits "never turn the exit status
# green on their own" and that was false: a range containing only old unsigned
# commits exits 0. It has to -- the alternative is a gate nobody can satisfy.
# What the check does instead is refuse to *describe* them as signed: the debt
# is marked per commit, counted on stderr, and the summary reads "0 of 1
# commit(s) carry a signature" rather than a cheerful total.
#
# THE HOLE, NAMED: commit dates are author-controlled. Someone can backdate a
# commit past this cutoff and be exempted. That is not defended against here
# because the defence -- refusing commits whose date precedes their parent's --
# breaks legitimate rebases and cherry-picks, and this check is not the right
# place to police clock skew.
ENFORCED_FROM = "2026-08-15"

MEANING = {
    "G": "good signature",
    "U": "good signature, key not in this keyring",
    "X": "good signature, expired",
    "Y": "good signature, key expired",
    "R": "good signature, revoked key",
    "B": "BAD signature",
    "E": "signature could not be checked",
    "N": "no signature",
}


def host_verification(repo: str, sha: str) -> str:
    """The host's own verdict for one commit, mapped onto a `%G?` letter.

    WHY THIS EXISTS. Verifying a signature needs the signer's public key. A CI
    runner has none, so `git log --format=%G?` there reports on the runner's
    empty keyring rather than on the commit -- the measurement describes the
    scaffolding. The host has already verified every commit server-side against
    the keys it holds for the author, and exposes the verdict. That is the
    authoritative source and it needs no key material on the machine asking.

    So: `--source git` locally, where a developer has their own key, and
    `--source host` in CI. Same rule, read from the place that can answer.
    """
    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/commits/{sha}",
         "--jq", ".commit.verification.verified,.commit.verification.reason"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        return UNVERIFIABLE
    lines = proc.stdout.strip().splitlines()
    if len(lines) < 2:
        return UNVERIFIABLE
    verified, reason = lines[0].strip().lower(), lines[1].strip()
    if verified == "true":
        return "G"
    # `unsigned` is a different fact from `could not be checked`, and the two
    # must not collapse: one is a commit with no signature, the other is a
    # commit whose signature nobody could evaluate.
    return NO_SIGNATURE if reason == "unsigned" else UNVERIFIABLE


def run_git(args: list[str], cwd: str | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    return proc.returncode, proc.stdout.strip()


def commits_in_range(
    base: str, head: str, cwd: str | None = None
) -> tuple[list[tuple[str, str, str, str]], str | None]:
    """[(sha, %G?, committed_at, subject)] for base..head, or ([], reason).

    `cwd` names the repository, the way every other seed check takes one. Left
    to the process's working directory this could only ever inspect whatever
    happens to be checked out, which is the proxy-for-the-thing error this
    corpus keeps recording.

    The commit date is carried because the cutoff needs it. It is committer
    date, not author date: a rebase resets the first and preserves the second,
    and the question here is when the object entered this history.
    """
    code, out = run_git(
        ["log", "--format=%h\t%G?\t%cI\t%s", "--no-merges", f"{base}..{head}"], cwd=cwd
    )
    if code != 0:
        return [], f"git could not read {base}..{head}"
    rows = []
    for line in out.splitlines():
        parts = line.split("\t", 3)
        if len(parts) == 4:
            rows.append((parts[0], parts[1], parts[2], parts[3]))
    return rows, None


def judge(
    rows: list[tuple[str, str, str, str]],
    allow_untrusted: bool,
    enforced_from: str = ENFORCED_FROM,
) -> tuple[list, list]:
    """(failing, grandfathered). Merges are excluded before this by --no-merges.

    A commit older than `enforced_from` and unsigned is grandfathered: reported,
    counted, and not failed. A commit older than the cutoff that IS signed is
    simply fine and appears in neither list.
    """
    failing, grandfathered = [], []
    for row in rows:
        _, status, committed_at, _ = row
        signed = status in GOOD or status in GOOD_WITH_WARNING
        if signed and not (status == "U" and not allow_untrusted):
            continue
        if committed_at[:10] < enforced_from:
            grandfathered.append(row)
            continue
        failing.append(row)
    return failing, grandfathered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Refuse a branch whose own commits carry no signature.",
        epilog=(
            "A signature attests who made the commit. It says nothing about "
            "whether the commit is correct."
        ),
    )
    parser.add_argument("--base-ref", required=True,
                        help="the branch's base; only base..head is checked")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--repo-dir", default=None, help="repository to read (default: cwd)")
    parser.add_argument("--source", choices=("git", "host"), default="git",
                        help="git reads the local keyring; host asks the forge, "
                             "which is the only answer available on a runner")
    parser.add_argument("--repo", default=None, help="owner/name, required by --source host")
    parser.add_argument("--enforced-from", default=ENFORCED_FROM,
                        help=f"unsigned commits committed before this date are a "
                             f"recorded debt, not a failure (default: {ENFORCED_FROM})")
    parser.add_argument("--allow-untrusted", action="store_true", default=True,
                        help="accept a good signature by a key this keyring lacks (default)")
    parser.add_argument("--require-trusted", dest="allow_untrusted", action="store_false",
                        help="refuse a signature whose key is not in this keyring")
    args = parser.parse_args(argv)

    rows, problem = commits_in_range(args.base_ref, args.head_ref, cwd=args.repo_dir)
    if problem:
        print(f"signature check: {problem}", file=sys.stderr)
        return 1

    if args.source == "host":
        if not args.repo:
            print("signature check: --source host needs --repo owner/name",
                  file=sys.stderr)
            return 1
        rows = [(sha, host_verification(args.repo, sha), when, subject)
                for sha, _, when, subject in rows]

    if not rows:
        # A real answer: a branch that adds no non-merge commit has nothing to
        # attest. Reported rather than silently passing.
        print(f"signature check: {args.base_ref}..{args.head_ref} adds no non-merge "
              f"commit; nothing to check.")
        return 0

    failing, grandfathered = judge(rows, args.allow_untrusted, args.enforced_from)

    print(f"signature check: {len(rows)} commit(s) in {args.base_ref}..{args.head_ref}")
    print(f"enforced from {args.enforced_from}; anything unsigned before that is a "
          f"recorded debt, not a pass\n")
    for row in rows:
        sha, status, committed_at, subject = row
        mark = "FAIL" if row in failing else ("debt" if row in grandfathered else "ok  ")
        print(f"  {mark} {sha}  {status}  {committed_at[:10]}  "
              f"{MEANING.get(status, 'unknown status')}  {subject[:48]}")

    if grandfathered:
        print(
            f"\n{len(grandfathered)} unsigned commit(s) predate "
            f"{args.enforced_from} and are not failed.\nThey are permanent: "
            f"signing them means rewriting history, which this org does not do. "
            f"This count is the cost of the session that made them, and it does "
            f"not go down.",
            file=sys.stderr,
        )

    if failing:
        print(
            f"\n{len(failing)} of {len(rows)} commit(s) carry no signature this git "
            f"could read.\nRe-sign your own commits, or say in the pull request why "
            f"they are unsigned. Do not disable signing to make this pass -- that is "
            f"the act this check exists for.",
            file=sys.stderr,
        )
        return 1

    # Never "all N carry a signature" when some do not. The grandfathered ones
    # are exempt from failing, not signed, and a summary line that rounded them
    # into the good number would be this check reporting success while
    # attesting nothing -- the defect it was built against.
    signed = len(rows) - len(grandfathered)
    if grandfathered:
        print(f"\n{signed} of {len(rows)} commit(s) carry a signature. "
              f"{len(grandfathered)} do not and are exempt by date.")
    else:
        print(f"\nAll {len(rows)} commit(s) carry a signature.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
