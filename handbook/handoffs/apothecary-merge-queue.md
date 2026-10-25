# Handoff — apothecary: its stack landed on main; CI kept to governance and lint, the suite on the machine

**Goal.** Keep apothecary's `main` landing as pull requests arrive, every pull
request's CI kept to the governance checks and lint, and the whole suite run on the
contributor's machine on the tree that lands.

**Stamped 2026-10-25.** apothecary `main` at `acf1cc9`, tree `eec462f`: the stack of
2026-09-19 to 2026-10-24 landed, #21 to #98 with #99 and #100. Open: #101, ready on
`main`, and #102, a draft stacked on it; Dependabot's. `qm` `main` at `e225109`.
Every figure here was true at those commits. Re-derive each with `gh` and the tree
before acting on it.

## 1. Decisions in force

1. **A pull request's push runs the governance checks and lint, and nothing else.**
   The tests -- unit, walkthrough, browser, the Rust check, doc capture, the
   step-through tests -- run on the contributor's machine and in CI at a `v*` tag or
   on demand. apothecary's `tests/test_ci_workflows.py` fails if a test workflow
   goes back on pull requests. (2026-10-24)
2. **The whole suite runs on the machine before a merge, on the tree that lands.**
   `apothecary test all` -- the unit tests, the walkthrough and every browser test --
   on the pull request's head merged onto `main`'s tip: before it is marked ready,
   and again before it merges if that tree has changed. The merge commit's body names
   the tree, the command and its counts. `apothecary test changed` is for while
   working and is never the gate. (2026-10-24)
3. **A stack that lands as one run is tested once, on the tree `main` ends at.** Each
   level is merged onto `main`'s tip in order in a simulation (`git merge-tree`,
   `git commit-tree`), the suite runs on the final tree, and the levels land in order:
   each retargeted onto `main` and marked ready only once the one beneath it has
   merged, a red governance check stopping the run, each merge commit naming the run,
   each landed tree checked against the simulated one. The trees in between are not
   tested alone: the version tag is the claim, and a red run is found by testing the
   middle level. (2026-10-25)
4. **Coverage informs a pull request; nothing fails on a number.** `apothecary test all
   --coverage` measures the whole suite, the server the browser tests drive included,
   and says the package's share of statements run and, of the statements the pull
   request adds or changes, how many ran and which did not; the body carries it
   (`apothecary test coverage --markdown`). #102. (2026-10-25)
5. **No limit is chosen by hand.** A CI job's cap is twice its median over the runs
   GitHub records for it; a job with no record has GitHub's own. In CI each browser
   test's cap is twice the time `tests/e2e/durations.json` records for it; run on a
   machine, nothing is capped. (2026-10-24)
6. **A push is priced before it is made.** A pushed level costs about two
   runner-minutes under decision 1; a push to a pull request whose merge still runs
   the test workflow costs some twenty-five. Read the price again from the run's
   jobs. (2026-10-24)

## 2. How the stack landed

- #21 to #40 one level at a time, each tested on its own landing tree; the rest, #42
  to #98, as one run on the final tree (decision 3), which `main`'s tree is.
- #100 put the lock's fixed `pillow` and `certifi` on `main` first: `pip-audit` found
  advisories against the lock every level below #66 carried.
- #50's branch marks each line of the timeless sweep's plan that quotes a flagged
  phrase `timeless: allow`, with its reason.
- Five levels took their merged-up heads first (#79, #80, #81, #91, #97): their heads
  on origin did not carry #99's CI change and conflicted once it had landed.
- Three levels' branches took `main` before merging (#53, #91, #97): their heads and
  `main` met at several merge bases, on each of which alone the merge conflicts. Git
  merges them through a virtual base; GitHub refuses them. The branch's merge commit
  has the simulated tree, so GitHub's merge has one base.

## 3. Open, and paused until a person says

- **#101 and #102.** `apothecary test changed`, and the coverage measure; their run
  and their coverage are in their bodies.
- **Dependabot's pull requests**: ungrouped, and apothecary has no `dependabot.yml`;
  `qm-queue.md` decision 5 says one with `groups:`. #61's `pillow` 13.0.0 is the
  version `main`'s lock carries.
- **The review cycle at ten times the requests**: drafted, not on origin. Its
  proposals each change a record or a setting and are asked first: an amendment of
  apothecary's *review the integrated whole* (Proposed), and protection and a merge
  queue for `main`.
- **The retrospective**, qm #237, into `project/apothecary`.
- **The 2026-10-24 review's code items**, none started.
- **CI's setup still installs from apt**, a quarter of an hour on a busy runner; a
  priced change.

## 4. What to distrust

- **A machine's suite is bound by its processor.** On four cores headless Chromium's
  software WebGL takes most of it: three workers bring the browser part from some
  seventeen minutes to eleven, and more do not help. The order that helps is the
  longest files first by recorded time, with the unit part beside it.
- **Coverage's older tracer doubles the server's time**, and a browser test waiting
  for a window misses its wait. From Python 3.12 a measured run uses
  `sys.monitoring`, which costs next to nothing.
- **A governance job cancelled before a step ran** -- no runner came before its limit
  -- reads as a failure in `gh pr checks`. It says nothing of the pull request: run it
  again.
- **A pushed head reaches its pull request a moment later**, and a fetch that moves
  `origin/main` races any other process fetching the same checkout.
- **Four unit tests fail once on four workers and pass alone** (two firmware CLI
  tests, one listing every part's SCAD, one rendering an overlay with a real
  OpenSCAD). Unexplained.

## 5. Limits

The final tree's run passed on the machine that landed it: the unit and walkthrough
tests, and every browser test but the doc-capture ones. CI has not run the browser
suite on `main`'s tree; a version tag is where it does.
