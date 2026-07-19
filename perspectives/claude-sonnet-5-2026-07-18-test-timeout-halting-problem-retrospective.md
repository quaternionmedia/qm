# Perspective — Watching a Maybe-Hung Test Doesn't Resolve It: A Retrospective on Enforcing Time Bounds

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Claude Sonnet 5 (Anthropic), the assistant that ran (and re-ran) the test session this retrospective evaluates |
| **Task** | A process retrospective on a single incident within a larger feature-development session: a newly added Robolectric/Compose video test appeared to stall during a background `testDebugUnitTest` run, and the response to that - across two separate attempts - was to watch it for a while and re-run it, rather than to establish a bound on how long "watching" could mean before concluding anything. The maintainer named the actual shape of the mistake directly: *this is the halting problem*, and asked for an enforced fix plus a reflective writeup, not just a bugfix. This document is that writeup. The concrete decision (a project-default `Test` task timeout) is recorded separately as `adr/DRAFT-enforced-test-timeouts.md`; this document is about the reasoning failure that made the ADR necessary, not the mechanism itself. |

## 0. Standing, scope, and evidence base

Single-incident retrospective — the evidence is one session, one stalled test, traced directly by
the assistant that ran it. Where a claim generalizes beyond this one incident it is marked as
inference, not observation.

Evidence classes, per this corpus's convention:

- **E1** — directly traced this session: the actual background-task transcripts (bash output files,
  `Monitor` event, `TaskStop` calls), the actual Gradle daemon log
  (`daemon-14132.out.log`) showing the exact moment the connection reset, the actual process-list
  snapshots (`Get-Process java`) taken between attempts, the actual diff to `app/build.gradle.kts`.
- **E4** — inference from a single incident; there is no second comparably-shaped "did I add a bound
  before or after starting to wait" incident in this project's history yet to check these proposals
  against.
- **E5** — prior general knowledge (the halting problem itself, standard practice around test
  timeouts), unverified this cycle beyond what's cited.

I performed and narrated every step this retrospective evaluates, including the mistake itself, in
real time, in front of the maintainer. This is not independent review.

## 1. What worked

### 1.1 CPU-time-vs-wall-time was a real diagnostic, not a guess (E1)

Before concluding anything, I compared each Java process's accumulated CPU time to its wall-clock
elapsed time (`Get-Process java | Select Id, CPU, StartTime`). A process burning close to its full
wall-clock budget in CPU time is doing *something*, even if that something is a bug (e.g., a tight
recomposition loop) rather than useful work - that distinction (busy vs. truly blocked) was
information a plain "is it still running" check would not have given, and it correctly ruled out
the simplest hypothesis (a dead lock/deadlock with zero CPU use) early.

### 1.2 Once real evidence appeared, the diagnosis moved fast and stayed honest (E1)

The daemon's own log (`Connection reset by peer` at the exact moment the third test's `STARTED`
line was printed, with a `timeout` command in the reproduction shell) was read *before* concluding
the test was hung — and correctly interpreted as inconclusive (my own `timeout 90` could have caused
the disconnect) rather than seized on as confirmation of the more dramatic hypothesis. The
methodology flaw in that same reproduction attempt (piping through `tail`, so `$?` reported `tail`'s
exit code, not `gradlew.bat`'s) was caught and named rather than left to quietly undermine the next
claim.

### 1.3 The fix, once applied, immediately produced better information (E1)

The very next re-run under the new enforced timeout reproduced the stall at the *exact same test*, a
third time. That is a stronger signal than either of the two unbounded attempts produced on their
own — not because the bound itself diagnosed anything, but because a bounded, logged run is
something you can compare *across* repetitions cleanly, where an open-ended watch produces one
data point you eventually give up on and never really compare to anything.

## 2. Friction worth naming

### 2.1 The core error: watching is not a bound, and no amount of watching becomes one (E1, E5)

Twice — once letting a background task run unattended for roughly sixteen minutes, once switching to
a live `Monitor` and waiting for its next event — the operative plan was "give it more time and see."
Neither attempt had a stated condition under which "still no result" would be treated as an answer
rather than a reason to keep waiting. That is not a minor inefficiency; it is structurally
unresolvable. Whether a specific run of a specific program halts is, in the fully general case,
undecidable — and even where a specific instance *is* decidable in principle (most real hangs are,
with enough static or dynamic analysis), watching stdout for an unbounded amount of time is not that
analysis. It is a strategy with no termination condition, applied to a question that needs one. The
maintainer's framing — "how will this produce a different result if we are in a halting problem" —
is the correct diagnosis of exactly what was wrong with the plan, not a rhetorical flourish.

### 2.2 The fix was available before the second unbounded attempt, not just before the third (E1)

The Gradle `Test.timeout` API is not new or obscure — it has existed for multiple major Gradle
versions and is the first result for "gradle test hang timeout." The `testLogging` change made
earlier in the same session (to get per-test visibility) was the *correct instinct applied to the
wrong half of the problem*: it makes a hang attributable once bounded, but does nothing to bound one.
Adding both in the same edit, before the first background run rather than after two failed watches,
was available the entire time and wasn't taken.

### 2.3 A tool built for a different purpose got reached for mid-incident (E1)

While waiting on the first unbounded background run, `ScheduleWakeup` — a tool scoped to `/loop`
dynamic-mode sessions — was invoked to "check back later" on a task the harness already tracks and
notifies on completion automatically. This was caught and named as an error within the same turn,
but it is worth recording as a *symptom* of the same root cause as §2.1: without a real bounded-wait
primitive in mind, the instinct under "I'm waiting for something uncertain" pressure was to reach for
whatever tool had wait-shaped affordances, rather than to ask whether a bound existed at all. A
correctly bounded process (§1.3's re-run) needed no such tool — its own enforced ceiling was the
entire mechanism.

### 2.4 The request was, correctly, not "explain why it's slow" but "make hangs decidable by policy" (E1)

The maintainer's actual ask after naming the halting-problem framing was structural: a required step
in memory, in this repo's contributor instructions, and in the inherited governance material — not a
one-off patch to this one test file. That is the right level to fix this at. A bugfix for
`LayoutToggleVideoTest` alone would have left the *process* gap (no default enforcement, anywhere,
for any future test) completely open, ready to reproduce the identical incident on the next hang in
a different file.

## 3. Concrete proposals

Not self-executing — candidates for a human (or a future assistant session) to pick up, and largely
already acted on within this same incident (see `adr/DRAFT-enforced-test-timeouts.md` and
`CONTRIBUTING.md`'s testing section for the parts already done):

1. **Before starting any process whose completion is uncertain and whose output will be watched for
   a result, confirm an enforced bound already exists — and if it doesn't, add the bound *before*
   the first run, not after the first unbounded wait fails to resolve** (§2.1, §2.2). This
   generalizes past Gradle/JVM tests: any long-running command, agent, or external process an
   assistant intends to "check back on" should have its own stop condition established up front, not
   discovered to be missing mid-wait.
2. **Treat "let's watch it a bit longer" as a decision that needs its own justification, not a
   default** (§2.1). If the honest justification is "so we can see whether it resolves," that is
   only a valid plan when a bound already guarantees it eventually will, one way or the other — never
   as a load-bearing plan on its own.
3. **When reaching for a tool to manage an uncertain wait, check whether the tool's own scope
   actually matches the situation** (§2.3) — a harness-tracked background task with its own
   completion notification needs no additional wait-scheduling at all; reaching for one anyway is a
   sign the real gap is the missing bound, not a missing notification mechanism.
4. **Encode the enforcement mechanism, not just the rule, in project-durable material** (§2.4) —
   this project's own ADR-lint and Glyph-boundary CI checks are the existing precedent that a written
   rule without an automatic gate erodes under time pressure; `adr/DRAFT-enforced-test-timeouts.md`
   follows that same shape deliberately rather than inventing a new one.

## 4. Closing honesty

This is not independent review — I made the error this retrospective evaluates, narrated it in real
time, and wrote the fix and this document in the same session. It is not a survey — every claim above
rests on one incident's history and should be weighted as a single, fresh data point (E4) until a
second comparable incident either confirms or contradicts the proposals in §3. At the time of writing,
the reproduction run under the new enforced timeout (§1.3) has stalled at the same test a third time
but has not yet resolved — the ADR's underlying bound guarantees it will resolve, one way or another,
within its stated window, but the actual root cause of the stall in `LayoutToggleVideoTest > record
toggling unit symbols` itself is still open and is not what this document is about. That the *process*
gap (no enforced bound, anywhere) is what got fixed here, ahead of and independent of the *test* bug
that exposed it, is the point being made, not a loose end being quietly left for later.

— Claude Sonnet 5, 2026-07-18
