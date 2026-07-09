# Perspective — Compute Is Not the Bottleneck: What qMetronome's Timing Saga Actually Shows

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Claude Sonnet 5 (Anthropic), the assistant performing this round of qmetronome's first-beat timing remediation |
| **Task** | An honest reflection on why a modern phone - billions of transistors, multi-core gigahertz silicon - needed several rounds of real software-architecture work to get a metronome's first click to land on time, prompted directly by a maintainer's frustration that this "should" have been trivial given the hardware involved. |

## 0. Standing, scope, and evidence base

Single-instance reflection, not a survey - the evidence is one project's timing history, traced by
one assistant, across one extended session (this one, plus the two prior sessions that produced
the streaming-engine rewrite and the warm-keep/count-in fix this perspective is written alongside).

Evidence classes, per this corpus's convention:

- **E1** — directly traced this session: the actual code (`StreamingClickEngine.kt`,
  `MetronomeEngine.kt`, `InternalClockSource`), the actual git/checklist history
  (`docs/publication_checklist.md`'s dated entries), a pre-existing flaky test caught while
  verifying this round's fix.
- **E4** — inference from a single project's history; there is no second app to compare this
  pattern against yet.
- **E5** — prior general knowledge (audio/HAL architecture, timing-perception literature),
  unverified this cycle beyond what's cited.

I am reviewing an investigation and fix I performed myself, across this session and the one
immediately before it. Treat §1-2 with the same self-flattery discount the corpus's own prior
retrospective (`claude-sonnet-5-2026-07-04-qmetronome-onramp-retrospective.md`) applies to itself.

## 1. The concrete gap, traced this session

qMetronome's own `StreamingClickEngine.kt` already builds toward the correct target: a
continuously-running, sample-clocked `AudioTrack` that mixes each click at an exact frame offset,
"the same mechanism every professional audio scheduler (DAWs, Web Audio API, Ableton Link) relies
on." That claim held up under tracing - the frame<->nanoTime calibration is sound, and steady-state
beats (1 onward) get genuine predictive lead via `MetronomeEngine.startAudioScheduling()`.

Beat 0 of every session didn't. Two distinct, traceable causes (E1):

1. **`StreamingClickEngine` was rebuilt from scratch on every play/stop toggle** - re-paying
   `AudioTrack.getTimestamp()`'s warm-up wait (up to a full second, by the code's own documented
   timeout, before falling back) every single time, not once per app session. The most common
   real-world trigger wasn't even opening the app fresh - it was `MetronomeGlyphService`'s
   already-existing, intentional behavior of stopping playback on every phone unlock. A musician
   glancing at their locked phone mid-practice session paid a cold-start tax every time.
2. **Beat 0 structurally cannot get the same lead-scheduling window every later beat gets.** The
   predictive loop that gives beat 1+ their precision only starts running *after* the clock itself
   starts ticking - and the clock's first tick fires within microseconds of `start()` being called,
   by design (so the display doesn't sit blank). There is no window between "user presses play" and
   "beat 0 is due" for anything to lead-schedule into. This was already known, not newly
   discovered - an existing regression test's own comment explicitly excluded the first beat-to-
   beat interval from its jitter assertion, documenting the gap rather than closing it.

Neither cause is a hardware limitation. Both are software-architecture choices: an unnecessary
rebuild-per-session pattern (fixed this round by keeping the engine warm across sessions), and an
unaddressed structural gap in when the very first beat can be scheduled (partially closed this
round by a deliberate, user-tunable, bounded pause - a genuine trade, not a free fix, and honestly
labeled as such rather than oversold).

## 2. Why "more compute" was never going to fix this

The maintainer's framing - "with all the computing power available... a simple timing exercise is
proving how fragile and underprepared the tech stack is" - names something real, but the
mechanism isn't what "more compute" language implies (E5, general knowledge, applied to this
session's specific evidence):

- **This was never CPU-throughput-bound.** Nothing traced this session or in the prior rounds
  logged in `publication_checklist.md` (the busy-spin fix, the dedicated-timing-dispatcher pass,
  the streaming-engine rewrite that superseded it) was limited by FLOPS or core count. Every fix
  was about *when* work got scheduled relative to a deadline, never about there being too much
  work for the silicon to do in time.
- **Digital audio has its own resolution floor, and it isn't the CPU's.** A clock cycle on this
  class of SoC is ~0.3-0.5ns; one audio sample at 44.1kHz is ~22.7µs - about 50,000x coarser.
  "Sub-clock-cycle" placement of an audio event is not a real target for *any* system, including
  professional studio hardware, because the signal itself doesn't have that resolution. The
  achievable ceiling here is sample-accurate placement, and `StreamingClickEngine`'s own mechanism
  already reaches for exactly that - see `docs/timing-accuracy-benchmark.md`, written alongside
  this perspective, for the concrete, re-measurable target that replaces the literal "one clock
  cycle" ask with a physically coherent one.
- **The actual bottleneck is a latency *guarantee*, which general-purpose mobile OSes deliberately
  don't provide.** Android (and the Linux scheduler underneath it) is not a hard-real-time
  system - "low latency" audio paths are best-effort, not deadline-guaranteed, because the same
  scheduler is fairly sharing the device with everything else running on it, and because strict
  real-time guarantees trade against the power management and multitasking a general-purpose
  consumer device needs. That is a deliberate, reasonable platform design choice, not an oversight
  - it just means software wanting tight timing on this class of device has to build its own margin
  around that non-guarantee (lead-scheduling, buffer-ahead placement, warm long-lived resources
  instead of cold-starting them) rather than assuming the platform will hand it precision for free.
  qMetronome's own `StreamingClickEngine` already does this correctly for steady-state beats; this
  round's fix extends the same discipline to session start-up, which the original implementation
  hadn't gotten to yet.
- **A small, telling data point from this very session (E1):** while verifying this round's fix, a
  *pre-existing* Robolectric test (`a positive audio offset fires the click only after the engine's
  own beat counter has advanced`) failed intermittently - roughly one run in five - on a development
  workstation, running plain JVM unit tests, nothing to do with a phone at all. Scheduling jitter
  under load is not a mobile-hardware-specific phenomenon; it is a property of concurrent software
  on general-purpose operating systems generally, and it showed up on the machine writing this
  document as readily as it shows up on the device the metronome runs on.

## 3. What this suggests, honestly bounded

None of the above is a defense of the status quo before this round's fix - the rebuild-per-session
pattern (§1.1) was a real, avoidable defect, and it existed in shipped code across multiple
prior release rounds before being named specifically as a gap. The proposal here is about where to
aim the frustration, not whether it's warranted:

- The frustration that "a phone this powerful shouldn't struggle with a metronome click" is
  correct about the *should* and wrong about *why it did*. The struggle was never about power. It
  was about (a) an architecture that paid an avoidable cold-start cost on every session, layered on
  top of (b) a structural lead-scheduling gap that no amount of raw compute closes, because it's a
  *notice-period* problem (how far ahead can this specific event be predicted), not a *throughput*
  problem (how fast can the work be done once it's known).
- This generalizes cautiously (E4, one project): a team hitting "the timing is still off" after a
  fix that felt architecturally sound should ask *which* of these two categories the residual gap
  is in before reaching for either "throw more engineering at the same mechanism" or "the platform
  is fundamentally inadequate." Both of qMetronome's own gaps this round were in the first
  category (avoidable software choices), and the honest remaining one (Gap B's residual, even with
  the count-in) is structurally in the second - which is why it's shipped as a measured, bounded
  trade-off with a user-facing dial, not claimed as solved.
- **The most durable output of this round isn't the fix - it's the benchmark.** Before this
  session, "is the first beat accurate" was a subjective, on-device impression with no number
  attached, verified (or not) by feel. `docs/timing-accuracy-benchmark.md` and
  `FirstBeatTimingBenchmarkTest` exist so the next round of this same question - and there will be
  a next round, per §2's own busy-spin/streaming-rewrite/count-in lineage - has a measured
  before/after to check against, rather than another engineer's confident impression standing in
  for one. That test could not be written until this round, because it needed the same
  frame<->nanoTime calibration this round's investigation had to understand in order to fix Gap A
  and correctly reject a same-shaped fix for Gap B.

## 4. Concrete proposals

Not self-executing - candidates for a human (or a future assistant session, explicitly directed)
to pick up:

1. **Re-run `docs/timing-accuracy-benchmark.md`'s Benchmark 1 on real hardware** as the very next
   step after this perspective - it's written, compiles, and is blocked only on a connected device,
   which this session didn't have. Until that number exists, this whole perspective is analysis
   without verification of its own conclusion. **Done, one day later - see §6.**
2. **Track the benchmark's numbers over time, in the doc's own results table**, the same
   "measured, dated, not overwritten" discipline `publication_checklist.md` already uses for every
   prior timing fix - so a future regression is visible as a table row that got worse, not
   rediscovered by feel.
3. **Investigate the flaky Robolectric test named in §2** as its own small, separate fix - not
   because it's urgent, but because a test suite that occasionally can't verify its own timing
   claims is a small instance of the exact category error this document is about: mistaking "ran
   fine most of the time" for "verified."
4. **If Benchmark 1's numbers show Gap B's residual gap still exceeds the ≤10ms target** in
   `docs/timing-accuracy-benchmark.md`, the only further lever is the bigger, user-visible
   "count-in" change already scoped and deliberately deferred in this round's own plan - not a new
   mitigation layered on top of the current one. **This condition turned out true - see §6; the
   actual next lever it points to is narrower than this proposal guessed.**

## 5. Closing honesty

This document analyzes a fix it has not yet seen verified - no device was connected in the session
that wrote it, so every claim in §1 about this round's fix rests on Robolectric-level logic tests
and traced code, not the on-device benchmark this same document argues is the actual bar. That is
not a comfortable position to publish from, and I am naming it rather than waiting to write this
until the number exists, because the absence of that number *is itself* the point §3 is making:
confident engineering analysis is not the same thing as measurement, and this document is currently
an instance of the former standing in for the latter - exactly the gap `docs/timing-accuracy-
benchmark.md` exists to close. Read this perspective as reasoning that should be checked against
Benchmark 1's first real result, not as a conclusion that already has been.

— Claude Sonnet 5, 2026-07-08

## 6. Postscript — the benchmark's first real result (2026-07-09)

A device became available the day after this was written. Benchmark 1 ran on a Nothing A024
(SDK 36). Full numbers are in `docs/timing-accuracy-benchmark.md`'s results table; the shape of
the result matters more here than the digits:

- The count-in fix is real and substantial, not just directionally correct: beat 0's error
  *specific to the gap this round targeted* (its excess over the baseline every beat on this
  device carries) dropped from ~128ms to ~36ms - a 72% reduction, consistent across every session
  in both the count-in-enabled and count-in-disabled runs. §1-2's causal account held up against
  measurement, not just against re-reading the code.
- It does **not** reach the ≤10ms target §1's own companion doc sets. §3's proposal 4 anticipated
  this exact outcome and pointed at "the bigger, user-visible count-in change" as the only further
  lever - that guess was too broad. The actual, narrower cause: the count-in currently schedules
  beat 0's audio *once*, at the start of the pause, while every steady-state beat gets *repeatedly*
  refined by the existing lookahead loop right up until its own deadline. The fix this points to is
  smaller than "a bigger count-in" - it's "let the existing beat 0 pause use the same
  repeated-refinement mechanism steady-state beats already get," not a new mechanism.
- One thing neither this document nor the benchmark's own design anticipated: steady-state beats
  carry a consistent ~47ms `|error|` in this benchmark's own measurement, not just beat 0. That's
  almost certainly `StreamingClickEngine`'s real buffer-ahead depth on this device showing up in
  the measurement itself (this benchmark reads target-vs-actual-mixed-frame, not true acoustic
  latency), not a second bug - but it's a reminder that a benchmark's first real run teaches you
  things about your own measurement, not only about the system it's measuring. §5's point stands
  undiminished by having a number now: the number itself needed a second look before its shape was
  trustworthy, which is exactly what measurement is for and confident analysis alone cannot supply.

— Claude Sonnet 5, 2026-07-09
