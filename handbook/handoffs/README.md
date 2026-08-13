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

**Ordered by expected delta**, highest first, against the current milestone:
*managing qmcp's flows with dossier by planning deltas*. The first three are one
chain — each is the next page's blocker — so taking them out of order buys
nothing.

| Handoff | Blocks on | Repo |
|---|---|---|
| [`for-a-stronger-model.md`](for-a-stronger-model.md) | nothing — **read this first**: what to distrust in the other pages, and why | every repo |
| [`qmcp-flows-as-deltas.md`](qmcp-flows-as-deltas.md) | the milestone, and the four-step path to it. Step 1 is **done** — the work is on a ref and its parent's 19 test failures are fixed. Step 2 next | qmcp + dossier |
| [`dossier-delta-review.md`](dossier-delta-review.md) | step 3 of that path. Two alembic heads to fix, and dossier's slot is held by #12 | dossier |
| [`disk-tooling.md`](disk-tooling.md) | **built**; its item 3 is now answered by the delta review — the orphan tables are in progress. Items 1, 2 and 4 want a decision | qm + dossier |
| [`harness-next-test.md`](harness-next-test.md) | nothing — the harness is in place and untried by anyone who did not build it | qm + one project |
| [`governance-status-generator.md`](governance-status-generator.md) | **built** — now the seam contract, and eleven questions for a human | qm |
| [`session-2026-08-12.md`](session-2026-08-12.md) | nothing — where the 2026-08-11/12 session left things, and the decisions waiting | every repo |

**Three pages are gone rather than marked done**, per the routing rule above.
`workspace-unlanded.md` first: both decisions it opened with are settled —
apothecary's adoption commit is on its `origin/main` (`git branch -r --contains
2409244`), and qmetronome's two `120000` pointer files are present on disk with
a clean tree. Its survey was a moment, and the moment has passed.

Then `dossier-adoption.md` and `dossier-governance-view.md`. dossier has
adopted —
`AGENTS.md`, `.gitmodules` and the disk tooling are on its `main`, and
dossier#10 and #11 are merged. A page describing delivered work as pending is
worse than no page, because a session picks it up and re-derives a state that no
longer exists.

**The harness is on `main`.** `ci/` (17 files) and
the session scripts in `project-seed/ci/` both landed with #36 on 2026-08-11, so a
project pinned to `main` now gets `/cowork`, the slot check and the two status
documents at its next pin bump rather than waiting on anything. Every page here
older than that date describes the harness in the present tense as unmerged;
that is a *stamp* doing its job, not a claim to act on. Re-derive before quoting
one.

`project/datum`'s propagation landed as **#39**, after #34
was closed unmerged on 2026-08-09. It is not level with `main` now, and no
project branch is: all twelve fell behind again when #38 and #41 landed. Read
`governance-status.yaml`'s `behind_corpus` rather than a number on this page.

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

*Stamped 2026-08-12. `qm` `main` at `104361a`, `dossier` `main` at `604efb8`,
`qmcp` `main` at `85013c5`.*
