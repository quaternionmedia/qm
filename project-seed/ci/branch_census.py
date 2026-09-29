#!/usr/bin/env python3
"""Every branch in this repository, and what would be lost by deleting it.

**A BRANCH CLEANUP NEEDS TO KNOW WHAT IS ON ONE DISK.** `git branch -r
--merged` answers the easy half: a branch whose commits are all on the default
branch can go, and nothing is lost. It cannot see the dangerous half, which is
a *local* branch holding commits its own remote does not have. Deleting the
remote is harmless there; deleting the clone is not, and the two look identical
in a list of branch names.

That is not hypothetical here. `rad`'s `evolve/rad-v1` carried seven commits
that existed on exactly one disk for seventeen days, while two other
repositories cited a document and pinned a contract version that only those
commits held. This module exists because the handoff that found it had to
reconstruct that by hand.

WHAT IT READS AND WHAT IT REFUSES TO DO. Refs, never the working tree -- the
checked-out branch is an accident of who ran this last. It **never deletes
anything and takes no `--delete` flag**, because a census that can also destroy
is one somebody runs in a hurry. It prints what it found and what each finding
would cost; the deletion is a separate, deliberate act by a person.

THE CLASSES, AND WHY THEY ARE NOT ORDERED BY SAFETY. A reader scanning for
"which can I delete" wants `merged` first; a reader asking "what am I about to
lose" wants `stranded` first. The second question is the one that has actually
gone wrong here, so it sorts first and the safe rows sort last.

  stranded   the local ref is ahead of its own remote -- commits on one disk
  local      a local branch with no remote at all
  gone       a remote branch whose local ref is gone (nothing to lose here)
  ahead      unmerged work that is pushed and reachable
  merged     every commit is on the default branch; deleting loses nothing

WHAT THIS CANNOT TELL YOU. Whether an `ahead` branch is abandoned or paused.
It reports the age of the tip and stops: a branch untouched for a month is a
question for a person, and a script that answered it would be guessing with a
threshold nobody agreed.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field

STRANDED = "stranded"
LOCAL = "local"
GONE = "gone"
AHEAD = "ahead"
MERGED = "merged"

# Sorted by what it costs to be wrong about, not by tidiness. See the header.
ORDER = (STRANDED, LOCAL, AHEAD, GONE, MERGED)

WHAT_IT_COSTS = {
    STRANDED: "commits exist on this disk and nowhere else",
    LOCAL: "never pushed; deleting the clone deletes the work",
    AHEAD: "unmerged, and reachable from the remote",
    GONE: "on the remote only; this clone has no copy",
    MERGED: "nothing -- every commit is on the default branch",
}


def git(*args: str, repo: str = ".") -> str:
    done = subprocess.run(("git", "-C", repo, *args), capture_output=True,
                          text=True)
    if done.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout.strip()


def lines(*args: str, repo: str = ".") -> list[str]:
    out = git(*args, repo=repo)
    return [line for line in out.splitlines() if line.strip()]


@dataclass
class Branch:
    """One branch, by name, wherever it exists."""

    name: str
    kind: str = ""
    ahead: int = 0          # commits not on the default branch
    behind: int = 0         # commits the default branch has and this does not
    unpushed: int = 0       # local commits the remote ref does not have
    unique: int = 0         # of those, the ones whose patch is not upstream
    tip: str = ""
    when: str = ""
    who: str = ""
    notes: list[str] = field(default_factory=list)

    @property
    def automation(self) -> bool:
        """Dependabot's branches are its own to open and close.

        Named by prefix rather than by author: the author of a dependabot
        commit is a bot account whose name is a host detail, and this has to
        work in a clone that never spoke to the host.
        """
        return self.name.startswith("dependabot/")


def describe_unique(unique: int) -> str:
    """The sentence a reader needs beside a count of commits."""
    if unique < 0:
        return "patch comparison unavailable"
    if unique == 0:
        return "nothing unique -- every patch is already upstream"
    return f"{unique} carrying work not upstream by patch"


def unique_commits(base: str, ref: str, repo: str) -> int:
    """How many of `ref`'s commits are not upstream **by content**.

    **A COUNT OF COMMITS IS NOT A MEASURE OF LOSS.** `rev-list` counts by sha,
    so a branch whose work landed on the default branch under a different sha
    -- squashed through a pull request, cherry-picked, rebased -- still reports
    commits ahead, and a census built on that alone shouts about branches that
    hold nothing.

    dossier is the worked example. `governance/adopt-corpus` and
    `wip/delta-entity-type-local` both carried one commit this clone had not
    pushed, seventeen days old, and looked identical in every count. By patch,
    the first is already upstream and the second is 556 lines of real work on
    one disk. Only this call tells them apart.

    `git cherry` compares patch ids: `-` means the patch is upstream already,
    `+` means it is not.

    **It errs toward reporting loss.** A commit whose content landed in a
    different shape -- reformatted, split, merged with another -- reads as `+`.
    So this can say work is at risk when it is not, and never the reverse,
    which is the safe direction for a tool a person reads before deleting.
    """
    try:
        out = lines("cherry", base, ref, repo=repo)
    except RuntimeError:
        # An unrelated history has no merge base to compare against. Fall back
        # to saying nothing rather than to saying zero.
        return -1
    return sum(1 for line in out if line.startswith("+"))


def default_branch(remote: str, repo: str) -> str:
    """The default branch, asked of the remote ref rather than assumed.

    `main` is this org's answer everywhere, and hard-coding it would make this
    silently wrong in the first repository that says otherwise.
    """
    try:
        head = git("symbolic-ref", f"refs/remotes/{remote}/HEAD", repo=repo)
        return head.rsplit("/", 1)[-1]
    except RuntimeError:
        return "main"


def census(repo: str = ".", remote: str = "origin") -> list[Branch]:
    """Every branch this clone or its remote knows about."""
    base = f"{remote}/{default_branch(remote, repo)}"

    head = default_branch(remote, repo)
    prefix = f"{remote}/"

    remote_refs = set()
    for ref in lines("for-each-ref", "--format=%(refname:short)",
                     f"refs/remotes/{remote}", repo=repo):
        # `origin/HEAD` is a symbolic ref, not a branch. Counting it reports a
        # duplicate of the default branch under a name nobody pushed.
        if ref.endswith("/HEAD") or not ref.startswith(prefix):
            continue
        remote_refs.add(ref[len(prefix):])
    remote_refs.discard(head)

    local_refs = set(lines("for-each-ref", "--format=%(refname:short)",
                           "refs/heads", repo=repo))
    local_refs.discard(head)

    found = []
    for name in sorted(remote_refs | local_refs):
        here = name in local_refs
        there = name in remote_refs
        # The remote ref is the shared truth; fall back to the local one only
        # when there is no remote, so `ahead`/`behind` always describe what
        # somebody else can see.
        tip_ref = f"{remote}/{name}" if there else name
        branch = Branch(name=name)
        branch.tip = git("rev-parse", "--short", tip_ref, repo=repo)
        branch.when = git("log", "-1", "--format=%ad", "--date=short", tip_ref,
                          repo=repo)
        branch.who = git("log", "-1", "--format=%an", tip_ref, repo=repo)
        branch.ahead = int(git("rev-list", "--count", f"{base}..{tip_ref}",
                               repo=repo))
        branch.behind = int(git("rev-list", "--count", f"{tip_ref}..{base}",
                                repo=repo))

        if here and there:
            branch.unpushed = int(git("rev-list", "--count",
                                      f"{remote}/{name}..{name}", repo=repo))

        if here and (branch.unpushed or not there):
            # Only work this clone alone holds is worth the patch comparison.
            branch.unique = unique_commits(base, name, repo=repo)

        if branch.unpushed:
            branch.kind = STRANDED
            # The count is the headline, so it is also the note: a reader who
            # sees only one line per branch still learns the size of the loss.
            branch.notes.append(
                f"{branch.unpushed} commit(s) not on {remote}")
            branch.notes.append(describe_unique(branch.unique))
        elif here and not there:
            branch.kind = LOCAL
            branch.notes.append(describe_unique(branch.unique))
        elif there and not here:
            branch.kind = GONE if branch.ahead else MERGED
        elif branch.ahead == 0:
            branch.kind = MERGED
        else:
            branch.kind = AHEAD
        found.append(branch)
    return found


def at_risk_in(found: list[Branch]) -> list[Branch]:
    """The branches whose loss would actually cost something.

    One definition, used by the summary line and by the exit status, because
    a report and the code beside it disagreeing is worse than either being
    wrong alone. Automation is excluded: a dependabot branch this clone
    happens to hold is not work anybody is about to lose.
    """
    return [b for b in found
            if not b.automation and b.kind in (STRANDED, LOCAL) and b.unique != 0]


def render(found: list[Branch], remote: str = "origin") -> str:
    """What a person reads before deciding what to delete."""
    if not found:
        return "  No branches besides the default.\n"

    out = []
    people = [b for b in found if not b.automation]
    bots = [b for b in found if b.automation]

    for kind in ORDER:
        rows = [b for b in people if b.kind == kind]
        if not rows:
            continue
        out.append(f"  {kind.upper()} -- {WHAT_IT_COSTS[kind]}")
        for b in sorted(rows, key=lambda b: b.when, reverse=True):
            note = f"  ({'; '.join(b.notes)})" if b.notes else ""
            out.append(f"    {b.when}  {b.tip}  +{b.ahead}/-{b.behind}  "
                       f"{b.name}{note}")
        out.append("")

    if bots:
        # One line, not one per branch. Fourteen dependabot rows push the
        # rows a person has to decide about off the top of a terminal, and
        # nobody triages them here anyway.
        out.append(f"  {len(bots)} automation branch(es), not listed: "
                   f"dependabot opens and closes its own.")
        out.append("")

    # **COUNTED BY LOSS, NOT BY BRANCH NAME.** A branch whose every patch is
    # already upstream is not at risk however it is classified, and counting it
    # as if it were is how a census becomes an alarm somebody learns to ignore.
    at_risk = at_risk_in(found)
    safe = [b for b in people if b.kind in (STRANDED, LOCAL) and b.unique == 0]

    if at_risk:
        out.append(f"  {len(at_risk)} branch(es) hold work this clone alone "
                   f"has: " + ", ".join(b.name for b in at_risk))
    else:
        out.append("  Nothing unique is held only in this clone.")
    if safe:
        out.append(f"  {len(safe)} unpushed branch(es) carry nothing upstream "
                   f"does not already have: " + ", ".join(b.name for b in safe))
    out.append("  This tool deletes nothing. Deleting is a person's act.")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Every branch, and what deleting it would cost.")
    parser.add_argument("--repo", default=".", help="path to the repository")
    parser.add_argument("--remote", default="origin")
    parser.add_argument(
        "--fail-on-stranded", action="store_true",
        help="exit non-zero when work exists only in this clone")
    args = parser.parse_args(argv)

    found = census(args.repo, args.remote)
    sys.stdout.write(render(found, args.remote))

    if args.fail_on_stranded:
        # The same rule the summary line applies, and deliberately the same
        # expression: an exit code that disagrees with the text above it is
        # worse than either being wrong alone.
        at_risk = at_risk_in(found)
        if at_risk:
            sys.stderr.write(
                "branch census: work exists only in this clone: "
                + ", ".join(b.name for b in at_risk) + "\n")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
