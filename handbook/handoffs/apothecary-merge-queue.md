# Handoff — apothecary: its stack's merge queue, and CI kept to governance and lint

**Goal.** Land apothecary's open stack on `main` bottom first, keeping every pull
request's CI to the governance checks and lint, and the tests on the contributor's
machine and at a version tag.

**Stamped 2026-10-24.** apothecary `main` at `f1c1543`; the stack's bottom, #21, at
`1835b47`; the remediation stack's top on origin, #98, at `0ef44b2`, and its CI
change, #99, at `3698ec6`; `qm` `main` at `ba3e6ab`. Every figure here was true at
those commits. Re-derive each with `gh` and the tree before acting on it.

## 1. Decisions in force

1. **A pull request's push runs the governance checks and lint, and nothing else.**
   The tests -- unit, walkthrough, browser, the Rust check, doc capture, the
   step-through tests -- run on the contributor's machine and in CI at a `v*` tag or
   on demand. apothecary #99 makes it so; its `tests/test_ci_workflows.py` fails if a
   test workflow goes back on pull requests. (2026-10-24)
2. **The whole suite runs on the machine before every merge.** `apothecary test all`
   -- the unit tests, the walkthrough and every browser test -- runs on the tree `main`
   will have after the merge (the pull request's head merged onto `main`'s tip): before
   the pull request is marked ready, and again before it merges if that tree has
   changed since. The merge commit's body names the commit it ran on, the command and
   its counts; a red run is fixed in the pull request's own branch before it merges.
   `apothecary test changed` is for while working and is never the gate. (2026-10-24)
3. **No limit is chosen by hand.** A CI job's cap is twice its median over the runs
   GitHub records for it; a job with no record has GitHub's own. In CI each browser
   test's cap is twice the time `tests/e2e/durations.json` records for it; run on a
   machine, nothing is capped. #99 and #79. (2026-10-24)
4. **A push is priced before it is made.** A stack-wide fix is merged up on the
   machine and pushed once, when it next needs to reach origin. Under decision 1 a
   pushed level costs about two runner-minutes (eight governance jobs and lint);
   read it again from the run's jobs. (2026-10-24)
5. **The stack lands as the async contract's §1 says**: the bottom merged with a
   merge commit; the next pull request retargeted onto `main` before any branch is
   deleted; marked ready; its gates read, the suite run as decision 2 says among
   them; merged. (async contract §1)

## 2. The queue, and what clears each step

`gh api repos/quaternionmedia/apothecary/pulls?state=open` gives the open set; the
order is depth first from `main`, oldest first on each base, as
`.github/ci/check_integrates.py` merges them. At the stamp it is 74 of the
maintainer's pull requests, #21 at the bottom.

| Step | State at the stamp | Clears it |
|---|---|---|
| #21, `consolidate/2026-09-19`, the bottom | ready, clean, every check green; `main` is an ancestor of its head, so the merged tree is the tree its own checks ran on | `apothecary test all` on its head, the tree `main` will have (decision 2), then **a person**: `qm-queue.md` §3 holds it -- merge or close. Its merge commit may carry `[skip ci]`, since the push would only re-run the checks the pull request ran on the same tree |
| #24 to #59, the levels above it, with the timeless side chains off `build/timeless-docs` (#40 to #53, each already merged into #55's line) | green at their last push | each in turn as §1.5 says, its suite run on its head merged onto `main`'s tip -- the head's own tree for a level of the line, a true merge for a side chain. The leak and timeless checks run on the machine on that tree too (`project-seed/ci/check_leaks.py`, `check_timeless.py --base <main's tip>`): a finding of either stops a level that carries its workflow (`leak-check.yml`, `timeless-check.yml`); below that level a finding lands only when the stack's top no longer has the line -- a later level rewrote it -- and the merge commit names its file and line. A leak finding `main` already carries is no new finding |
| #62 to #65, `theatre` to `build/airgap` | `license-check` red: `pip-audit` finds advisories against the lock's `pillow` 12.3.0 and `certifi` 2025.10.5 | the lock the levels above them carry, merged down into #62's branch and up through #65 |
| #92 | one browser shard red: cancelled at its job's twenty minutes while apt installed OpenSCAD and Chromium's libraries; no test failed | nothing in CI under decision 1: its next push runs governance and lint, and its suite runs on the machine before it merges (decision 2) |
| #80 to #98 | do not yet carry #99 and #79's change; their checks are the old full suite's | #99 and #79 merged up through each level -- conflicts in `CONTRIBUTING.md`'s CI table and its paragraph on the loop, `tests/e2e/conftest.py`'s collection hook and `tests/test_e2e_shards.py`, each resolved by keeping both sides -- and pushed once (decision 4) |
| apothecary's Dependabot pull requests | seven on `main`, ungrouped; apothecary has no `dependabot.yml` | a person, as `qm-queue.md` decision 5 says for every repository: one `dependabot.yml` with `groups:`, then the ungrouped ones closed |

## 3. Open, and paused until a person says

- **The review cycle at ten times the requests.** The measured assessment is drafted
  for apothecary's `docs/plans/` and not yet on origin. Its proposals: requests gated
  by machines and merged by their authors; a merge queue that runs the suite once per
  batch; people reviewing releases, split by the README map's areas, in parallel;
  stacks a few deep that land continuously; the files a third or more of requests
  touch -- the page's template, `api.py`, the changelog, the docs index -- split
  until requests stop meeting. Each changes a record or a setting and is asked
  first: an amendment of apothecary's *review the integrated whole* (Proposed), and
  protection and a merge queue for `main`, a repository setting.
- **The retrospective**, qm #237, into `project/apothecary`: a perspective on
  spending CI and the maintainer's time without a budget.
- **The 2026-10-24 review's code items**, none started: dependencies, logging, one
  import helper, the retired stubs' removal date, examples as a package, one
  installer download, the template and `api.py` split, the wheel's template check,
  installer signatures, the governance items in `todo.md`, an architecture page.
- **CI's setup still installs from apt**, which on a busy runner has spent a quarter
  of an hour before the first test. Cached artifacts remove it; a priced change.

## 4. What to distrust

- **A green check on #80 to #98 is the old full suite at its last push**, not the
  CI decision 1 describes.
- **A browser shard cancelled at its job's limit** was, every time it was read on
  2026-10-24, a slow setup and not a hung test. Read the job's step times before
  saying otherwise.
- **Four unit tests fail once on four workers and pass alone** (two firmware CLI
  tests, one listing every part's SCAD, one rendering an overlay with a real
  OpenSCAD); CI's unit job runs them serially. Unexplained.
- **The integration check judges the open pull requests as they stood** when it
  last ran.

## 5. Limits

The local suite passed on the whole stack merged together, with #99 and #79 merged
up, on the machine that made them (unit and walkthrough tests, and every browser
test but the doc-capture ones). Nothing on origin has run the browser suite on that
tree; a tag is where CI does.
