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
| [`dossier-adoption.md`](dossier-adoption.md) | **delivered** — dossier#10 (draft, assigned); `project/dossier` pushed | dossier + qm |
| [`governance-status-generator.md`](governance-status-generator.md) | **built** — now the seam contract, and eleven questions for a human | qm |
| [`dossier-governance-view.md`](dossier-governance-view.md) | **first cut delivered in dossier#10**; the delta-review page still open | dossier |
| [`harness-next-test.md`](harness-next-test.md) | nothing — the harness is in place and untried by anyone who did not build it | qm + one project |
| [`workspace-unlanded.md`](workspace-unlanded.md) | nothing — a survey, and two items wanting a decision | every repo |

The two dossier pages are genuinely independent of each other. The status
document now exists, so the fourth page needs only a reviewed schema to build
against and a repo that has adopted the corpus it reports on.

Adoption is delivered: `project/dossier` at `a9a6e33` here, pushed as a
long-lived project branch, and dossier `governance/status-view` at `651ea01` as
**dossier#10**, draft and assigned. All eight of dossier's gates pass. Its page
carries the one thing worth a reviewer's attention: `project/dossier` is pushed
without a pull request, because the fork procedure says to push it and a pull
request from it into `main` would merge one project's records into the corpus.

**The harness does not reach dossier at adoption.** Nothing in
`project-seed/ide/.claude/commands/` and no `ci/` directory exists on `main` —
both live on `evolve/ci-tooling-fixes` (#36). A project pinned to `main` gets
governance discovery and the three seed gates, and gets `/cowork`, the slot
check and the two status documents at its first pin bump after #36 lands. That
is the propagation path working as designed, and it is also the single thing
standing between here and a governance view with anything to render.

### Not a handoff yet, but don't lose it

`propagate/datum-2026-08-08` is pushed, contains all of `main`, and has **no
open pull request** — #34 was closed unmerged on 2026-08-09. `project/datum` is
62 behind as a result, while its six sibling project branches each have an open
propagation PR. Someone closed that PR on purpose, so re-opening it is a human's
call and not an agent's; the fact is recorded here so it stops being invisible.

## Rules that apply to every one of these

**One open pull request per repository, per contributor.** Not one per task.
If your slot already holds an open PR, add to it or wait — do not open a
second. This is a review-bandwidth constraint, not a style preference. In this
repo each `project/*` branch holds its own slot, because each is pinned by a
different downstream submodule; in a project repo it means one, full stop.

`handbook/async-contract.md` §1 is the rule and the reasoning;
`project-seed/ci/check_one_pr.py` is the check, and `one-pr-check.yml` runs it
on every pull request. Run it before you open anything.

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

*Stamped 2026-08-10. `qm` `main` at `b94d910`, `project/dossier` at `a9a6e33`, `dossier` `main` at `f055376`.*
