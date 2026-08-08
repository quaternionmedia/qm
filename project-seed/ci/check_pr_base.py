#!/usr/bin/env python3
"""Assert a branch is based on what its pull request targets, and say what it carries.

SEED FILE, run in place. Run it *before* opening a PR, and paste its output into
the description.

The failure it exists for: a branch cut from the wrong parent is internally
consistent. Its tests pass, its lint is clean, and a local CI run reports it
green -- because every one of those measures the branch, and none of them
measures where the branch came from. One such PR in this org sat open carrying
eighteen commits of unrelated feature work under a title describing a single CI
check. Nothing flagged it; a consolidation happened to compare the numbers.

One correction, established by running this against that very PR: the
merge-base test does NOT catch it. The feature branch was itself cut from main,
so the misbranched PR is transitively based on main and the merge-base check
passes. What catches it is the last test below -- the commits are shared with
another branch that has its own open pull request.

So this reports five things a PR description asserts implicitly and usually
without evidence:

  - whether merge-base(base, head) is the base tip: catches a branch that has
    diverged, not a branch cut from the wrong parent;
  - how many commits and files the PR actually carries;
  - who authored each commit, so foreign work is visible rather than counted;
  - the top-level paths touched, to compare against what the description claims;
  - whether any carried commit already belongs to another branch. THIS is the
    one that catches a branch stacked on someone else's work.

Exit status is 1 when the merge-base is not the base tip, or when commits are
shared with another branch. **Neither means broken; both mean "explain this".**
A long-running branch legitimately falls behind, and merging one of your own
branches into another is normal. Read the ratio: "1 of 61" is a branch you
folded in deliberately, "18 of 20" is a branch you did not mean to be on. The
number is the finding; the exit code only makes you look at it.

Usage:
    python check_pr_base.py --base main --head my-branch
    python check_pr_base.py --base project/foo --head propagate/foo --remote origin
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"check_pr_base: git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def is_ancestor(commit: str, ref: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, ref], capture_output=True
        ).returncode
        == 0
    )


def shared_with_other_branches(
    merge_base: str, head: str, base: str, remote: str, default: str
) -> dict[str, int]:
    """Which other remote branches already contain the commits this PR carries.

    Commits already on the default branch are excluded. A propagation PR --
    merging the default branch into a long-lived branch -- carries them by
    definition, and flagging that would fire on every propagation while saying
    nothing. What remains is work that came from somewhere that is *not* the
    default branch, which is the misbranching this check exists for.
    """
    counts: dict[str, int] = {}
    commits = [
        c
        for c in git("log", "--format=%H", f"{merge_base}..{head}").splitlines()
        if c and not is_ancestor(c, f"{remote}/{default}")
    ]
    for commit in commits:
        containing = git(
            "branch", "-r", "--contains", commit, "--format=%(refname:short)"
        ).splitlines()
        for branch in containing:
            branch = branch.strip()
            if not branch or branch in (head, base) or branch.endswith("/HEAD"):
                continue
            if not branch.startswith(f"{remote}/"):
                continue
            counts[branch] = counts.get(branch, 0) + 1
    return counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--remote", default="origin")
    ap.add_argument(
        "--default",
        default="main",
        help="Default branch. Commits already on it are not counted as shared, "
        "since a propagation PR carries them by design.",
    )
    ap.add_argument(
        "--expect-author",
        action="append",
        default=[],
        help="Author expected to have written every commit. Repeatable. Any commit by "
        "someone else is listed rather than failed -- carrying another person's commit "
        "is legitimate, and describing it as your own is not.",
    )
    args = ap.parse_args()

    base = f"{args.remote}/{args.base}" if "/" not in args.base.split("/")[0] else args.base
    head = f"{args.remote}/{args.head}"
    for ref in (base, head):
        git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")

    base_tip = git("rev-parse", base)
    merge_base = git("merge-base", base, head)
    aligned = base_tip == merge_base

    commits = [c for c in git("log", "--format=%H", f"{merge_base}..{head}").splitlines() if c]
    files = [f for f in git("diff", "--name-only", merge_base, head).splitlines() if f]
    authors = Counter(
        git("log", "--format=%an", f"{merge_base}..{head}").splitlines()
    )
    tops = sorted({f.split("/")[0] for f in files})

    print(f"base            {base} @ {base_tip[:8]}")
    print(f"head            {head} @ {git('rev-parse', head)[:8]}")
    print(f"merge-base      {merge_base[:8]}  {'== base tip' if aligned else '!= BASE TIP'}")
    print(f"carries         {len(commits)} commit(s), {len(files)} file(s)")
    print("authors         " + ", ".join(f"{a} ({n})" for a, n in authors.most_common()))
    print("top-level       " + (", ".join(tops) if tops else "(none)"))

    if args.expect_author:
        foreign = {a: n for a, n in authors.items() if a not in args.expect_author}
        if foreign:
            print(
                "\nnot by the expected author(s) -- name these in the description:\n  "
                + "\n  ".join(f"{a}: {n} commit(s)" for a, n in foreign.items())
            )

    others = shared_with_other_branches(
        merge_base, head, base, args.remote, args.default
    )
    if others:
        print("\ncommits here also live on another branch:")
        for branch, n in sorted(others.items(), key=lambda kv: -kv[1]):
            print(f"  {branch}: {n} of {len(commits)}")
        print(
            "\nA branch cut from another branch carries that branch's work. Say so in\n"
            "the description, or rebuild on the base. This is the check that catches a\n"
            "misbranched PR; the merge-base test above does not, because a feature\n"
            "branch cut from the base is still transitively based on it."
        )

    if not aligned:
        behind = len(git("log", "--format=%H", f"{head}..{base}").splitlines())
        print(
            f"\nThe merge-base is not {base}'s tip: this branch is {behind} commit(s) "
            f"behind it.\nThat is fine for a long-running branch and wrong for a branch "
            f"you meant to cut\nfrom {base} just now. Say which in the description."
        )
        return 1
    return 1 if others else 0


if __name__ == "__main__":
    raise SystemExit(main())
