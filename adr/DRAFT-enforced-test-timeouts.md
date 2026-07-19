# ADR-XXXX — Enforced upper time bound on all automated test runs

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-07-18 |

## Context

A newly added Robolectric/Compose video test (`LayoutToggleVideoTest > record toggling unit
symbols`) stalled during a background `testDebugUnitTest` run, with no prior indication of why.
Without any enforced bound on test execution, the only tool available was watching the live
`testLogging` output and re-running the suite, hoping the next observation would resolve the
question. It never could: "is this test hung or just slow" is not decidable by watching a running
process for an arbitrary-but-finite amount of time and then giving up — that's the halting problem
in miniature, and every additional minute spent watching produces the same non-answer a minute
sooner spent watching would have. The session repeated this pattern twice (once across a ~16-minute
unattended background run, once via a live `Monitor`) before the actual fix — a hard, enforced
ceiling — was applied. Only after that ceiling existed did the same stall reproduce a third time
deterministically, at the exact same test, confirming a real bug rather than transient flakiness -
information the ceiling made available immediately where the two prior attempts had not. With the
bound in place, the same investigation that had produced two inconclusive multi-minute waits took
one bounded 8-minute run with temporary diagnostic logging to pinpoint the exact line
(`performScrollTo()` targeting `unit_symbols_switch` directly never converged in Robolectric's scroll
simulation) and one more bounded run (21 seconds) to confirm the fix (scroll to an adjacent,
already-working node instead of using the actual interaction target as the scroll target itself -
see `LayoutToggleVideoTest.kt`). The bound did not just cap the damage of a hang; it was the
precondition for diagnosing it at all in a tractable number of steps.

This project already accepts the underlying principle elsewhere: `adr/README.md`'s CI enforcement
section runs an ADR-draft-vocabulary lint and a Glyph SDK import-boundary check specifically
*because* a written rule with no enforcement mechanism doesn't hold under real pressure. `governance/
qm/PRINCIPLES.md`'s charter states the same thing at the org level: "A principle earns a record only
if it produces decisions with teeth: enforceable consequences... Every record names its enforcement
mechanism." A testing-discipline rule that says "tests shouldn't hang" without an enforcement
mechanism is exactly the kind of motherhood statement that charter is written to route around.

`app/build.gradle.kts` already gained per-test `testLogging` (`started`/`passed`/`skipped`/`failed`
events) in the same investigation that produced this ADR — necessary for *diagnosing* a stall once
one is bounded, but insufficient by itself, since a live stream of events that never stops streaming
new ones is exactly as unresolvable to watch as silence is.

## Decision

Every Gradle `Test` task in this project carries an enforced, project-default wall-clock `timeout`,
applied automatically via a single `tasks.withType<Test>().configureEach { ... }` block in
`app/build.gradle.kts` — zero per-file or per-author action required for it to apply to a new test
class. Currently `Duration.ofMinutes(8)`, roughly 3x the suite's healthy full run (~2.5 minutes as of
2026-07). A run that exceeds the bound is killed by Gradle and fails loudly and immediately, rather
than continuing silently or indefinitely.

§1. This is a *task-level* bound (the whole `Test` task's JVM is killed), not a per-test-method one.
Combined with the `testLogging` events already in place, the last `STARTED` line with no matching
`PASSED`/`FAILED`/`SKIPPED` in the log at the moment of the kill identifies the specific test to
investigate — the task-level bound supplies the stop condition; the per-test log supplies the
attribution.

§2. This rule generalizes beyond Gradle/JVM specifics: any automated process an assistant or
contributor starts and intends to wait on for a result — not just test suites — needs an enforced
stop condition decided *before* the process starts, not applied reactively after an unbounded wait
has already begun. §1's mechanism is the concrete instance for this project's test suite; the general
form is a candidate for an org-level record (see Consequences).

## Consequences

- A hang is now bounded and diagnosable in a fixed, known amount of time, replacing an open-ended
  "watch and hope" loop with a guaranteed resolution (pass, or a clear timeout failure) within 8
  minutes of any single `Test` task invocation.
- Cost, accepted: task-level (not per-method) granularity means one hung test kills the whole task
  run, losing results for every test that would have executed after it in that invocation. Finer
  granularity (Alternative 1 below) would avoid this but at a real authoring cost across the existing
  suite; deferred rather than paid for now.
- Obligation: `CONTRIBUTING.md`'s testing section documents this rule and points back to this ADR.
  Changing the bound requires updating both together — the code (`app/build.gradle.kts`), the
  contributor-facing doc, and (once ratified) this ADR's Amendments, not just one of the three.
- The bound is a project default, not a tuned-per-test value — a test with a legitimately long but
  bounded runtime (e.g. a deliberate multi-second `Thread.sleep`-based timing test) still has to fit
  inside the whole-suite ceiling; there is currently no per-test override mechanism, so a future
  test with unusually long legitimate runtime is a revision trigger (below), not silently exempted.

## Alternatives considered

1. **Per-test JUnit 4 `@Rule val timeout = Timeout(...)` in every test class.** Finer-grained — kills
   only the offending method, lets the rest of the suite continue and report normally. Rejected for
   now: this project's ~30+ existing test classes each declare their own `@Rule`s independently (no
   shared base class), so adopting this uniformly means either a base-class refactor touching every
   file or trusting every future test author to remember to add the rule by hand. A mechanism whose
   enforcement depends on a human remembering to opt in, per file, is the exact failure mode this ADR
   exists to close — identical in shape to why the ADR-lint and Glyph-boundary CI checks exist as
   automatic gates rather than contributor guidelines. Worth adopting *in addition* later if
   per-method granularity turns out to matter in practice (see Revision triggers).
2. **Do nothing; rely on watching live output and manually killing a run that looks stuck.** The
   status quo this ADR replaces. Rejected: "does this look stuck yet" has no terminating condition —
   it is the halting problem stated informally, and it cost real session time this incident (two
   unbounded watch/re-run cycles) before converging on nothing more useful than "it's slow, or it's
   hung, unknown which."
3. **CI-only timeout (e.g., a GitHub Actions job-level `timeout-minutes`).** Insufficient alone: it
   only fires in CI, not during local or on-device-adjacent development loops, which is exactly where
   this incident happened. Kept as a complementary, not substitute, safeguard — CI should still carry
   its own outer bound independent of this one.

## Revision triggers

- The suite's healthy full-run time approaches roughly two-thirds of the bound (~5.3 minutes at the
  current 8-minute setting) as more tests are added — raise the bound rather than let routine growth
  start producing false-positive timeout failures.
- A genuine (non-hanging) individual test needs longer than the whole-task bound to legitimately
  complete — adopt Alternative 1 (per-test override) at that point rather than raising the project
  default to accommodate one outlier.
- A real hang recurs and the task-level kill's "last STARTED line" attribution proves ambiguous or
  insufficient in practice (e.g. two tests genuinely running concurrently) — same trigger as above.
- This pattern (enforce a bound before waiting, not after) is validated by a second incident outside
  this project — candidate to propose as an org-level `governance/qm` record rather than a
  project-local one.

## Amendments

*None.*
