# Handbook — Handoffs

**Routing.** Working instructions for asynchronous agents, not decision
records. Each page is a task somebody can pick up cold. Delete a page when its
work lands; the method that outlives it belongs in the runbook or the audit
queue, not here.

**Read this page first, then exactly one of the others.** They are written to
be worked in parallel by different sessions, and the ordering constraints
between them are recorded here rather than inside each one.

---

## The queue

| Handoff | Blocks on | Repo |
|---|---|---|
| [`dossier-delta-review.md`](dossier-delta-review.md) | nothing | dossier |
| [`dossier-adoption.md`](dossier-adoption.md) | nothing | dossier + qm |
| [`governance-status-generator.md`](governance-status-generator.md) | **built** — now the seam contract, and eleven questions for a human | qm |
| [`dossier-governance-view.md`](dossier-governance-view.md) | the two dossier pages above | dossier |

The two dossier pages are genuinely independent of each other. The status
document now exists, so the fourth page needs only a reviewed schema to build
against and a repo that has adopted the corpus it reports on.

### Not a handoff yet, but don't lose it

`propagate/datum-2026-08-08` is pushed, contains all of `main`, and has **no
open pull request** — #34 was closed unmerged on 2026-08-09. `project/datum` is
62 behind as a result, while its six sibling project branches each have an open
propagation PR. Someone closed that PR on purpose, so re-opening it is a human's
call and not an agent's; the fact is recorded here so it stops being invisible.

## Rules that apply to every one of these

**One pull request per base branch, and only ever one to `main`.** Not one per
task. If a base already has an open PR from an agent, add to it or wait — do
not open a second. This is a review-bandwidth constraint, not a style
preference. In this repo that currently means one PR to `main` plus one per
`project/*` branch; in a project repo it means one, full stop.

**Open it as a draft, and never request a review.** Add the person who asked
for the work as assignee. Leaving draft is their decision.

**Close a PR before pushing its commits onto its base branch.** Pushing a
head's commits onto its base *merges* the PR, with no review and no way to
undo the record. This has already happened once here.

**State which commit you are working against, at the start and in the PR.**
Every number on these pages was true when written and may not be now. The
tables carry a stamp for that reason; re-derive before acting, and never quote
a figure from these pages as current.

**Run the gates and report what they said**, including what the local runner
cannot reproduce. `project-seed/ci/run_workflows_locally.py` does not
reproduce `uses:` steps, the runner image, or secrets.

**Check what your branch carries before opening the PR.**
`project-seed/ci/check_pr_base.py --base <base> --head <branch>`, output pasted
into the description. A branch cut from the wrong parent passes every other
check.

## What none of these authorise

Ratifying anything. Merging to `main` or to a `project/*` branch. Deleting a
branch. Force-pushing. Rewriting a branch a submodule pins — and if you find
one that was rewritten, `handbook/propagation-runbook.md` has the recovery.

## The failure mode these are written against

Every defect this corpus has found in its own tooling was a check that
reported success while enforcing nothing: a lint whose glob matched no files,
a runner that used the wrong shell mode, an append-only check that asked a
superproject for a diff of a path inside a submodule. Six of them, in tooling
that had no tests.

The work in these handoffs is the same class of artifact. A governance
dashboard that is green because its query returned empty is worse than no
dashboard, because it discourages the manual check that would have caught the
problem. **Every signal needs a fixture in which it reports bad.** A signal
only ever observed green has not been tested; it has been watched.

Building the status generator produced four more of them, in one afternoon and
none of them a crash: `ls-tree` without `-r` reported a directory of ten
records as empty; walking every reachable merge counted the corpus's own
thirteen merges as thirteen propagations; `gh api` without `--paginate`
returned a hundred of a hundred and nine repositories and declared three
existing projects nonexistent; and a `--jq` path naming a key the endpoint does
not have reported every repository in the org as unlicensed. Each produced a
tidy, confident, wrong table.

**A test that passes against the broken tool is inert**, and this corpus has
shipped two of those. After writing a signal's test, break the tool in the way
the test names and confirm the test fails. Ten such mutations were run against
`ci/governance_status.py`; two tests were inert on the first pass and both were
rewritten.

*Stamped 2026-08-09. `qm` at `b94d910`, `dossier` at `f055376`.*
