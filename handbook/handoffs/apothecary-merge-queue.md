# Handoff — apothecary: its stack landed on main; a pull request's CI is the governance checks, lint and the walkthrough, the suite on the machine

**Goal.** Keep apothecary's `main` landing as pull requests arrive: a pull request's
CI kept to the governance checks, lint and the walkthrough's hermetic pages, each push
priced and authorised, and the whole suite run on the contributor's machine on the
tree that lands, every test inside its time bound.

**Stamped 2026-10-26.** apothecary `main` at `a067786`, tree `88a14d7`: the stack of
2026-09-19 to 2026-10-24 landed, #21 to #98 with #99 and #100, then #101 to #103, #104
and #105, and #106. Nothing is open in apothecary. apothecary pins `qm` at `baec440`,
#211's head. `qm` `main` at `a3fe2be`. Every figure
here was true at those commits. Re-derive each with `gh` and the tree before acting on
it.

## 1. Decisions in force

1. **A pull request's push runs the governance checks, lint and the walkthrough's
   hermetic pages, and nothing else.** The rest of the tests -- unit, browser, the
   Rust check, doc capture, the step-through tests -- run on the contributor's machine
   and in CI at a `v*` tag or on demand. apothecary's `tests/test_ci_workflows.py`
   holds which workflow runs when. (2026-10-24; the walkthrough 2026-10-25, #103)
2. **A merge skips no CI.** Its push to `main` runs the same checks again: the default
   branch's run the walkthrough record counts (`records/DRAFT-one-executable-walkthrough.md`,
   decision 7) for a hermetic page. A runtime-bound page's evidence is the run its
   version tag makes; between tags it has the merge's claim. (2026-10-25; the tag
   2026-10-26, qm #252)
3. **The whole suite runs on the machine before a merge, on the tree that lands.**
   `apothecary test all` -- the unit tests, the walkthrough and every browser test --
   on the pull request's head merged onto `main`'s tip: before it is marked ready,
   and again before it merges if that tree has changed. The merge commit's body names
   the tree, the command and its counts. `apothecary test changed` is for while
   working and is never the gate. (2026-10-24)
4. **A stack that lands as one run is tested once, on the tree `main` ends at.** Each
   level is merged onto `main`'s tip in order in a simulation (`git merge-tree`,
   `git commit-tree`), the suite runs on the final tree, and the levels land in order:
   each retargeted onto `main` and marked ready only once the one beneath it has
   merged, a red governance check stopping the run, each merge commit naming the run,
   each landed tree checked against the simulated one. The trees in between are not
   tested alone: the version tag is the claim, and a red run is found by testing the
   middle level. (2026-10-25)
5. **Coverage informs a pull request; nothing fails on a number.** `apothecary test all
   --coverage` measures the whole suite, the server the browser tests drive included,
   and says the package's share of statements run and, of the statements the pull
   request adds or changes, how many ran and which did not; the body carries it
   (`apothecary test coverage --markdown`). (2026-10-25)
6. **No limit is chosen by hand, and every test has one, on the machine and in CI.**
   Each phase of every test -- setup, call, teardown -- ends at twice the longest test
   `tests/e2e/durations.json` records, the process with it and every thread's stack
   written; a crashed browser worker ends a parallel run (`--max-worker-restart 0`).
   In CI a browser test's cap is also twice the time that file records for it, and a
   job's is twice its median over the runs GitHub records for it; a job with no record
   has GitHub's own. A bound that fires fails its test and names it. (2026-10-24; on
   the machine 2026-10-26, #104)
7. **Cloud CI's runner time is spend; a run on the machine is bounded in time, not
   spent.** A push is priced before it is made -- its jobs and their recorded minutes
   -- and made once a person has authorised that number, for that push. A pushed
   level costs about a minute and a half of runner time, seven to eleven minutes
   under GitHub's per-job rounding; a push that ran the test workflow cost some
   twenty-five. A bot's push or pull request starts no job until a person re-runs
   it: every job a pull request or a push to a branch other than `main` can start
   runs only when the run's triggering actor is not a bot (#106). Dependabot opens
   grouped security updates alone (#105). The spending record says this (qm #273).
   (2026-10-25; the bot 2026-10-26)

## 2. How the stack landed

- #21 to #40 one level at a time, each tested on its own landing tree; #42 to #98 as
  one run on the final tree (decision 4); #101 to #103 the same way, their merges the
  first since 2026-08-12 to run CI on `main`, each push run passing; #104 and #105 the
  same way, then #106, each landed tree the one the suite passed on.
- #100 put the lock's fixed `pillow` and `certifi` on `main` first: `pip-audit` found
  advisories against the lock every level below #66 carried.
- #50's branch marks each line of the timeless sweep's plan that quotes a flagged
  phrase `timeless: allow`, with its reason.
- Five levels took their merged-up heads first (#79, #80, #81, #91, #97): their heads
  on origin did not carry #99's CI change and conflicted once it had landed.
- Three levels' branches took `main` before merging (#53, #91, #97): their heads and
  `main` met at several merge bases (three for #53, two for the others), on each of
  which alone the merge conflicts. Git merges them through a virtual base; GitHub
  refused #53's with a 405. The branch's merge commit has the simulated tree, so
  GitHub's merge has one base.
- Dependabot's six pull requests were closed: `main`'s lock carries each package at or
  above the version each moved to.

## 3. Open, and paused until a person says

- **apothecary's records chain in `qm`**: #171, then #172, #197 and #211 stacked on it,
  into `project/apothecary`. Kept, and landed by other sessions; this page takes it as
  landing. apothecary pins `baec440`, #211's head, which no other ref carries: #211's
  branch stays until the pin moves to `project/apothecary`'s tip, after the chain lands.
- **The review cycle at ten times the requests**: drafted, not on origin. Its merge
  queue is unattended spend under decision 7: a batch bisected on what it finds is a
  count nobody stated before it ran.
- **The 2026-10-24 review's code items**, none started.
- **CI's setup still installs from apt**, a quarter of an hour on a busy runner at the
  worst; a priced change.
- **The bench checklist** on the printer and the board: a person's act.

## 4. What to distrust

- **The browser part is bound by the processor it runs on.** Three workers took it
  from some seventeen minutes to eleven where the stack was landed; more were not
  measured. The order that helps is the longest files first by recorded time, with
  the unit part beside it.
- **Coverage's older tracer doubles the server's time**, and a browser test waiting
  for a window misses its wait. From Python 3.12 a measured run uses
  `sys.monitoring`, which costs next to nothing.
- **A `slot` or `integrates` run cancelled before a step ran** reads as a failure in
  `gh pr checks`. Each was superseded by a newer run of the same workflow on the same
  pull request, which passed; none needs running again.
- **A browser test's cap fired by signal leaves Playwright's sync API unusable** in
  that process: the teardown after it spins on stopping the trace until the phase's
  bound ends the process. On the machine, under three workers and coverage, a short
  test's cap -- twice a record of a second or two -- is within the noise, which is why
  the recorded caps are CI's alone.
- **xdist's loadfile scheduler waits forever on a crashed worker's file** when a
  worker is started in its place; `--max-worker-restart 0` ends the run instead.
- **`apothecary preflight` fails `signature-check.yml` before a push**: the workflow
  asks the host (`--source host`) about commits it has not received.
  `check_signatures.py --source git` is the check on the machine.
- **A commit message carrying the skip marker**, even quoted inside its body, starts
  no workflow on that head. #103's first head ran none.
- **A pushed head reaches its pull request a moment later**, and a fetch that moves
  `origin/main` races any other process fetching the same checkout.
- **Four unit tests failed once on four workers and passed alone** (two firmware CLI
  tests, one listing every part's SCAD, one rendering an overlay with a real
  OpenSCAD), and one browser test (`test_printer_ui.py::test_editing_survives_polling`,
  a five-second wait for a two-second poll) failed once under a full run and passed
  alone three times. Unexplained.

## 5. Limits

The final trees' runs passed on the machine that landed them: the unit and walkthrough
tests, and every browser test but the doc-capture ones. In CI, `main`'s tree has run
the governance checks, lint and the walkthrough's hermetic pages (each merge's push
since #103). Its runtime-bound pages have not run in CI: a version tag is where they
do and is their evidence (qm #252), and none has been cut since.
