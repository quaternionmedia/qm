# Handbook — Merge Review

`AGENTS.md` item 3 says the author merges once every gate is green, and
`handbook/propagation-runbook.md` says how: a merge commit, never squash, never
rebase. `uv run qm merge` is those two sentences as a route. It has a reading
half and an act, and the act is one flag away from the reading.

## The reading

```sh
uv run qm merge                       # every roster repository
uv run qm merge --repo owner/name     # one
```

For every open pull request of yours it prints the host's live state — draft
or not, mergeable or not, the host's own merge verdict, and every check that
is failing or still pending, by name — and marks a pull request **READY** only
when all of those are clean at once. Beside each repository it says whether
you hold more than the one open pull request the slot rule allows
(`handbook/async-contract.md` §1), because the second one is the one that
should not have been opened yet, whatever its checks say.

This mode mutates nothing. A repository it could not read is listed as
unknown rather than as empty, and a private entry the clone cannot name is
listed as not asked.

## The act

```sh
uv run qm merge --repo owner/name --pr <n>        # re-verify, and stop
uv run qm merge --repo owner/name --pr <n> --yes  # merge
```

The act reads the pull request again at the moment of the call and refuses,
naming the reason, if it is not READY *now* — the listing and the act are two
moments, and a pull request that was green an hour ago is exactly that. It
also refuses a pull request somebody else opened: the author merges their own.

`--yes` is the signature. Without it the act reports and exits non-zero, so a
script that dropped the flag cannot read the pause as a merge. `--squash` and
`--rebase` are refused before the host is asked, with the runbook's reason. On
success it prints the merge commit and the time the host recorded.

READY is one definition in the module (`blockers`) and both halves use it, so
the listing cannot say READY where the act would refuse.

## What it never does

It never pushes to `main`, never closes a pull request, and never merges by
any route but the host's own merge commit with the branch deleted. Closing is
a git operation with an ordering trap of its own (`AGENTS.md` item 3) and
stays a person's deliberate act.

## What it cannot see

Whether the pull request *should* merge — only whether the host says it can. A
green pull request carrying a stack of unrelated commits is READY here and
wrong; `uv run qm branch` reads that. A red check is a reason to stop, by name;
whether it is a defect or an environment difference is what
`uv run --extra preflight qm preflight` and a person establish.

Exit status: 0 for a completed listing or merge, 1 for a refused merge with
its reason, 2 when `gh` cannot be run or the roster cannot be read.
