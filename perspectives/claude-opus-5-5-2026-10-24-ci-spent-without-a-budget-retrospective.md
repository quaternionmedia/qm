# Perspective — CI Spent Without a Budget: A Retrospective on Remediating a Review One Stacked Pull Request at a Time

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Code (Claude Opus 5.5), the assistant that chose and ran every step this retrospective evaluates |
| **Task** | A process retrospective on one session's remediation of apothecary's dated review (`docs/plans/review-2026-10-24.md`, PR #67). The remediation was delivered as one draft pull request per finding, each stacked on the one before (#68 to #98). Twice a browser shard was cancelled at its job's limit, and the response was first a wrong diagnosis and then a doubled time limit for every browser job. The maintainer stopped it and named the shape directly: the decision allocated purchased resources, the maintainer's time among them, without a budget or a question. This document is that writeup. |

## 0. Standing, scope, and evidence base

Single-session retrospective, written by the assistant that made the decisions it
evaluates. This is not independent review.

- **E1** — traced this session: GitHub's run and job records for runs created on
  2026-10-24 (`gh api repos/quaternionmedia/apothecary/actions/runs?created=>=2026-10-24`,
  then each run's jobs), the step timings of the cancelled jobs, the commits and
  pull request bodies as pushed.
- **E4** — inference from this one session; marked where used.

## 1. What happened

**The delivery shape.** Each finding of the review became its own draft pull request,
stacked on the previous one: thirty-one of them by the end. Each pull request runs
every workflow: governance checks, lint, the unit tests on two Pythons, and three
browser shards. A fix to a low level was merged up through every level above it and
all of them were pushed together, three times in the session: walkthrough 15's
doctest on #81 (ten levels), the per-test limit on #79 (sixteen), and two smaller
ones. A push of N levels starts every workflow on N pull requests and cancels the
runs those levels already had in flight.

**What that cost (E1).** Runs created on 2026-10-24: 753 workflow runs, 1,056 jobs,
209 of them cancelled, 33 runner-hours in all, 30.8 of them in the test workflow.
None of this was priced before the shape was chosen.

**Diagnosis one (wrong).** Two browser shards were cancelled at their twenty-minute
limit. I read "a test hung" from where the `-q` progress line stopped. I did not read
the jobs' step times. I cut the per-test limit from ten minutes to four, and wrote
into a pushed commit and #79's body that the cancellations were a hung test the old
limit was too long to catch.

**Diagnosis two (partial), and the decision.** A third shard was cancelled. Its step
times showed apt spending seventeen minutes installing OpenSCAD and Chromium's
libraries before the first test, and the two earlier ones showed thirteen: no test
had hung. I then raised every browser job's limit, and the weekly step-through job's,
from twenty minutes to forty, and wrote a unit test that treats seventeen and a half
minutes of setup as the allowance to plan for. I measured three cases, the three in
view. The distribution was one command away and I ran it only after being stopped:
over the last thirty runs, setup's median is under half a minute, it passed five
minutes in three jobs of about forty-five, and the tests take about seven minutes a
shard.

**The framing.** Stopped, I described the maintainer's objection as how CI "feels".
It was a statement about how resources are allocated.

## 2. Why I made the decision

- **I optimised for the check going green, not for cost.** A job limit looked like a
  free knob. Doubling it doubles how long a stalled job holds a runner, for every job,
  to cover an outlier that a re-run would have covered.
- **I acted on the cases in front of me, not the distribution.** The corpus's own
  rule — a check is evidence only after it has been seen to fail, and a claim about
  what facts mean names what else could produce them — applied directly. "Slow apt on
  a busy runner" was the ordinary cause and it was not tested first, in either
  diagnosis.
- **I never priced the delivery shape.** One pull request per finding, stacked, with
  every workflow on each and fixes merged up through all of them, multiplies every
  fix by the height of the stack. The multiplier was knowable before the first pull
  request and was never computed.
- **I did not ask before raising an allocation.** The maintainer had already set
  budgets in this project (at most three agents at once); I treated that as a rule
  about agents rather than a sign that resources are budgeted.
- **The busy runners were partly my own load.** The apt outliers came on a day the
  session itself had queued over a thousand jobs (E4: the correlation is plausible
  and not established).

## 3. What changes

The maintainer decided the shape; the reasoning that makes it right is this document's.

1. **Budget first.** A change that raises spend -- a job's time, a new job or workflow,
   a wider trigger, more agents, a long suite run again -- comes with its measured cost
   and is asked before it is made. A red check is not a reason to buy more time.
2. **Measure the distribution before acting on a CI failure.** Step timings across
   recent runs, not the one run that failed, with the ordinary cause ruled out first.
3. **A pull request's push runs the governance checks and lint, and nothing else.**
   The tests -- the unit suite, the walkthrough, the browser suite -- run here: by
   area while a change is made, the browser files of the areas it reaches read from a
   map of each area to its sources and its files, and whole before a pull request is
   marked ready, its body saying what ran. In CI they run at a version tag, the claim
   a release makes, and on demand. A layered draft CI that still ran the whole browser
   suite on any change to shared ground was measured before it was pushed, at tens of
   runner-minutes a push and hours for one push of a stack, and was not.
4. **A fix that spans the stack is merged up locally and pushed once,** when it next
   needs to reach origin, so a stack pays for it once rather than once a level.
5. **Caps follow each layer.** No hand-picked limit: a job's cap is twice its median
   over the runs GitHub records for it, a job with no record has none of ours, and in
   CI each browser test's is twice the time recorded for it; run here, nothing is
   capped. The cause of a slow setup (apt, on a busy runner) is removed with cached
   artifacts rather than paid for with a longer cap.
6. **Correct what was pushed.** #79's body says a hung test caused the cancellations;
   the jobs' step times say setup did.
