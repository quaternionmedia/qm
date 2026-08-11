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

    def qualify(ref: str) -> str:
        """Prefix a bare branch name with the remote; leave a qualified ref alone.

        "Does it contain a slash" cannot answer this, because the branch names
        here nearly all contain one -- project/datum, evolve/foo, perspective/
        bar. Asking whether it already names this remote can.
        """
        return ref if ref.startswith(f"{args.remote}/") else f"{args.remote}/{ref}"

    # An empty --base or --head qualifies to a bare "origin/", and git's error
    # for that names the mangled ref rather than the missing argument. In CI the
    # cause is always the same: $GITHUB_BASE_REF and $GITHUB_HEAD_REF are set on
    # a pull_request event and empty on every other one, so the step is running
    # on a trigger it was not written for.
    for name, value in (("--base", args.base), ("--head", args.head)):
        if not value.strip():
            sys.exit(
                f"check_pr_base: {name} is empty.\n"
                "In a workflow this comes from $GITHUB_BASE_REF / $GITHUB_HEAD_REF,\n"
                "which are set only on a pull_request event."
            )

    base = qualify(args.base)
    head = qualify(args.head)
    for ref in (base, head):
        git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")

    # A `project/<name>` branch is permanent and takes changes in, never out. It
    # holds one project's deviation from the corpus, and merging it into the
    # default branch moves that project's `adr/` into the org namespace -- where
    # a local decision reads as an org record binding every other project, and
    # the precedence rule runs backwards.
    #
    # Refused here rather than warned about, because nothing in the resulting
    # tree looks wrong. The records are all present and all well-formed; they are
    # merely in the wrong namespace, and the next project to adopt inherits them.
    # There is no later signal, so this is the only place it can be caught.
    #
    # Bare names are compared, not the remote-qualified ones: `origin/project/x`
    # and a `--remote upstream` spelling of the same branch must both match.
    bare_head = args.head.removeprefix(f"{args.remote}/")
    bare_base = args.base.removeprefix(f"{args.remote}/")
    if bare_head.startswith("project/") and bare_base == args.default:
        print(f"base            {base}")
        print(f"head            {head}")
        print(
            f"\nREFUSED: {bare_head} may not target {bare_base}.\n"
            f"\nA project/<name> branch is permanent and never merges into "
            f"{args.default}. Merging\nit would put one project's adr/ into the "
            f"org namespace, where a local decision\nreads as an org record "
            f"binding every project -- and nothing in the tree would\nlook wrong "
            f"afterwards.\n"
            f"\nWhat you probably meant:\n"
            f"  - adding records to that project: open the PR with --base "
            f"{bare_head}\n"
            f"  - bringing {args.default} to that project: a propagate/<name>-"
            f"<date> branch,\n    --base {bare_head}\n"
            f"See the corpus README's \"Branch namespaces\"."
        )
        return 1

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
