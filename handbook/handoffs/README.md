# Handbook — Handoffs

**Routing.** Working instructions for asynchronous agents, not decision
records. Each page is a task somebody can pick up cold. Delete a page when its
work lands; the method that outlives it belongs in the runbook or the audit
queue, not here.

**Read this page first, then [`qm-queue.md`](qm-queue.md), then at most one
other.** The queue page is the standing one, kept current by every session by
its own first section; `uv run qm queue` says what has moved since its stamp.
The others are written to be worked in parallel by different sessions, and the
ordering constraints between them are recorded here rather than inside each
one.

---

## The queue

**Ordered by expected delta**, highest first, against the current milestone:
*managing qmcp's flows with dossier by planning deltas*, except the first row,
which decides which of the others survive. The two after it are one chain —
each is the next page's blocker — so taking them out of order buys nothing.

**Re-read on 2026-10-25** against `qm` `main` at `685d086`, by
`handbook/consolidation-runbook.md` Step 7. No page's work has wholly landed,
so none is deleted. Every page in this directory has a row, and every row's
page exists.

| Handoff | Blocks on | Repo |
|---|---|---|
| [`performing-family-consolidation.md`](performing-family-consolidation.md) | **Peter, for every merge** — the core performing family's stacks, every branch on origin with its pull requests; ShowRunner #39 reviewed, fixed on its branch and checked against the stack; the family demo's manual integration loop and its gate; what is blocked on Peter and on mrharpo, and what done looks like for each remaining piece | qm + ShowRunner + ShowStopper + carlos + joe + leo |
| [`apothecary-merge-queue.md`](apothecary-merge-queue.md) | apothecary's stack, landed on `main`: a pull request's CI kept to the governance checks, lint and the walkthrough, each push priced and authorised as spend, the whole suite on the contributor's machine on the tree that lands and inside its time bounds, a stack tested once on the tree `main` ends at, coverage informing a pull request; what is open, paused for a person, and what to distrust | apothecary |
| [`qm-queue.md`](qm-queue.md) | **nothing; every session keeps it** — the standing queue: what is open into `qm`'s project branches, grouped by what clears each: eight branches waiting on a propagation of `main`, apothecary's set, codecartographer's record chain, and `qmcp`'s adoption restatement. Carries the decisions in force, Dependabot's grouping across the estate, two gaps in the gates, and what still waits on a person | qm |
| [`joe-manual-validation.md`](joe-manual-validation.md) | **a human, and nothing else** — joe's open set validated by hand: the three lane pages step by step with the spec or test behind each, every docs page against what the lanes showed, and the tests, with a findings log; steps no spec or test drives are marked. Walked against joe's `main`; delete it when the walk is done | joe |
| [`the-voice-loop.md`](the-voice-loop.md) | **nothing — read this for the loop**: what landed across `joe`, `vox`, `dossier`, `qmcp` and this corpus, the voice set included — Phase 10 of `qmcp`'s roadmap built on the local model, continuity from `qmcp`'s record — what remains, and the baseline Phase 0 of `qmcp`'s next phases established on `qmcp`'s `main`. Carries the three-process development environment, audio capture on the engine's machine, what no check covers, and the standing constraints | vox + joe + qmcp + dossier |
| [`hil-review-2026-10-31.md`](hil-review-2026-10-31.md) | **a human, and nothing else** — what to start to review the estate by hand: the docs site as `main` renders it, the trio on its reserved ports, and joe's checklist; what landed on 2026-10-31 and what to look at in each; the decisions only a person takes; the findings log. Delete it when its findings are closed | qm + joe |
| [`design-review-of-the-estate.md`](design-review-of-the-estate.md) | **the next session, for phases 4 to 7** — the first of the estate's design reviews, by `handbook/design-review-runbook.md`. Part 1 ran phases 0, 1 and 3 against `main` at `debf210`, read-only and scoped to a stranger's first hour, and carries the leads as hypotheses with the command behind each, the skeptic verdicts, and what remains; the semantic review stays downstream rather than redone. Then the order for the rest of the estate, tiered by adoption and activity and re-derived from the host, because `qm estate` needs sibling clones | qm, then every repo
| [`the-web-window.md`](the-web-window.md) | **nothing — read this for the window**: Phases 0 and 1 of `plans/the-web-window.md` landed on 2026-09-20 in five repositories, and this page is where Phases 2 to 6 are picked up — the live flow on a topology's shape, the designer on the routes the harness now serves, manipulation through the governed seam, cartography with chrestomathy and the prose reader's bridge, the triangle walkthrough — each with what to read first, where it goes, and what done looks like. Also the slice's residue: an address kind, a `dossier.sources` row, a record branch that exists only in a local clone, and a dossier test that names a private repository | qm + codecartographer + qmcp + looksatwords + rad + dossier |
| [`the-triplet.md`](the-triplet.md) | **nothing — read this for the graph leg**: the triplet's graphs from the pages on. codecartographer's show seam, its Show panel and `codecarto show export` are on its `main`, and every family's and project's showgraph is on its page in `main` here, with how to draw them again. Then the show document's schema, `qm cookbook --check` reading the documents, a refresh protocol, the seed's last three workflows, measured edges from the host, and the viewer, the READMEs and dossier's leg, each with what done looks like | qm + codecartographer |
| [`enact-the-stages.md`](enact-the-stages.md) | **a human, for two acts in order** — clear every slot, then push `test`, which the stage record says is the enactment. Carries the re-keying inventory (every line that decides on `main`, read at `test`), the two `AGENTS.md` sentences that become the trap on that day, and the cross-tool findings: every named tool now reads `AGENTS.md` natively, the `CLAUDE.md` symlink is nine bytes on a Windows clone without `core.symlinks`, and one policy page names an adapter's slash commands. The push-through is phased family by family in `ci/rollout.yaml` and tracked by `uv run qm rollout` | every repo |
| [`views-declare-what-they-need.md`](views-declare-what-they-need.md) | nothing — where 2026-08-27 left four repositories, with a readiness model built in two of them. Its §2 is five independent things to review asynchronously and its §3 is triage, ordered. Its §3.1 is closed and left standing on purpose — a pull request read as having lost its checks, six minutes before they arrived, and written up as the session's headline. Also names what is blocked on a person and what could not be verified, including a local workflow runner that fails ten steps of ten on this machine for one environment reason. Its pull requests have landed. It stays while the share link it carries waits on a person, and while `plans/the-web-window.md` cites its §2.1 | every repo |
| [`semantic-review-of-the-records.md`](semantic-review-of-the-records.md) | nothing — the one milestone requirement no check can measure: every record read as one body, in dependency order, with the same questions for each, before strangers read them. Unblocks the ratification rehearsal | qm |
| [`simultaneous-performing-family-plan-2026-09-21.md`](simultaneous-performing-family-plan-2026-09-21.md) | **Wave 0 readiness and private-34's clone** — ten participant handoffs define the probes; the plan defines baseline, pairwise and full-run measurements, with unknown kept distinct from failure | instruments + performer-display + show-control |
| [`carlos`](carlos-simultaneous-run.md), [`holophonor`](holophonor-simultaneous-run.md), [`joe`](joe-simultaneous-run.md), [`leo`](leo-simultaneous-run.md), [`ludwig`](ludwig-simultaneous-run.md), [`midiphonor`](midiphonor-simultaneous-run.md), [`private-34`](private-34-simultaneous-run.md), [`ShowRunner`](showrunner-simultaneous-run.md), [`ShowStopper`](showstopper-simultaneous-run.md), [`wolf`](wolf-simultaneous-run.md) | **nothing — read with the plan above**: one participant's probe each, its stamp and the evidence it starts from | each member |

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
`status/governance.yaml`'s `behind_corpus` rather than a number on this page.

## Rules that apply to every one of these

**One pull request carries one change: parallel when independent, stacked
when dependent.** Nothing limits how many a contributor holds open, and one
active stack at a time is a habit, never a rule. A pull request above the
bottom of a stack stays a draft. `handbook/async-contract.md` §1 is the rule
and the reasoning; `uv run qm stacks` lists your open pull requests and refuses
one marked ready while stacked, and `one-pr-check.yml` runs it on every pull
request.

**Never request a review, and merge it yourself once the gates are green.**
Add the person who asked for the work as assignee. The pull request is the
audit record; the human gates are ratification and the version tag. Draft
means unfinished.

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

Ratifying anything. Merging a pull request before every gate is green.
Deleting a branch another pull request is based on. Force-pushing. Rewriting a
branch a submodule pins — and if you find one that was rewritten,
`handbook/propagation-runbook.md` has the recovery.

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

**Pages written before 2026-08-14 describe a draft pull request as work waiting
for a person.** That model is corrected in `AGENTS.md` item 3 rather than in
each page. Where one of them
tells you to open a draft and wait, read it as: open it, run the gates, merge it.
The rest of what those pages say about their own subject stands.

*Stamped 2026-08-14. `qm` `main` at `104361a`, `dossier` `main` at `604efb8`,
`qmcp` `main` at `85013c5`.*
