# Perspective — First-Beat Timing: A Retrospective on How the Investigation Itself Was Run

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Claude Sonnet 5 (Anthropic), the assistant that performed every round of qmetronome's first-beat timing investigation |
| **Task** | A process retrospective on the multi-session investigation itself - what working discipline found the real fix, what friction slowed it down, and concrete proposals for the next time a similarly stubborn, hard-to-measure bug shows up. The technical content (what the bugs actually were, what fixed them) lives in `claude-sonnet-5-2026-07-08-mobile-timing-precision-perspective.md` and `docs/timing-accuracy-benchmark.md` - this document is deliberately about *how the work was conducted*, not what it found. |

## 0. Standing, scope, and evidence base

Single-instance retrospective, not a survey - the evidence is one investigation, spanning several
sessions with the same maintainer, traced by one assistant. Where a claim generalizes beyond this
one investigation it's marked as inference, not observation.

Evidence classes, per this corpus's convention:

- **E1** - directly traced across this investigation: the actual commits on `timing/first-beat-
  precision`, the benchmark's own results table (every row, including the ones that didn't help),
  the maintainer's own messages requesting research and an estimate.
- **E4** - inference from a single investigation; there's no second comparably-hard timing bug in
  this project's history to check these proposals against yet.
- **E5** - prior general knowledge (audio architecture, debugging methodology), unverified this
  cycle beyond what's cited in the companion perspective/benchmark doc.

I performed every round this retrospective evaluates. Apply the same self-flattery discount the
onramp retrospective (`claude-sonnet-5-2026-07-04-...`) applies to itself - this is not independent
review.

## 1. What worked

### 1.1 Building the wrong fix on purpose, instrumented, beat building the right one blind (E1)

The self-calibrating lead margin (`LeadMarginCalibrator`) had zero measured effect. That was not
wasted work - a temporary diagnostic added specifically to understand *why* it had no effect (not
left in the shipped code) surfaced the actual bug: the streaming engine's buffer was sized at
~120ms, two orders of magnitude larger than a real low-latency burst. The fix that closed the gap
(~2ms excess, from ~31-36ms) came directly from that diagnostic's output, not from reasoning to it
in advance. A plausible, well-justified hypothesis that turns out wrong, *measured and instrumented
rather than just discarded*, was a faster path to the real answer than continuing to reason from
the armchair would have been.

### 1.2 Real on-device measurement at every step, not trust in the code reading (E1)

Every hypothesis this investigation tried was verified against real hardware before being kept,
including ones that looked correct on paper. Two of the four hypotheses tried (routing beat 0
through the existing predictive loop; keeping the scheduling coroutine warm) would have shipped as
"probably fine" without that discipline - one was a measured no-op, the other a measured
*regression*, caught and reverted the same session specifically because the benchmark was re-run
after each change rather than trusted from the reasoning alone.

### 1.3 Research, once actually done, was worth more than another round of guessing (E1)

Two hypotheses were tried and measured before the maintainer explicitly asked for research into
prior art. That research (Web Audio's lookahead scheduler, Android's own AAudio/Oboe guidance,
`AudioTrack.getMinBufferSize()`'s documented-estimate status, commercial metronome apps' reliance on
native engines) supplied, within one research pass, several concrete, checkable facts that hadn't
surfaced across those two earlier rounds of pure code-tracing and reasoning. See §2.1 for the
honest flip side of this.

### 1.4 Never overwriting a prior measurement, even a wrong one (E1)

`docs/timing-accuracy-benchmark.md`'s results table has grown to seven dated rows across this
investigation, including the regression and the null result, none of them deleted or replaced. That
discipline (already established in this project's `publication_checklist.md` before this
investigation started) is what made the eventual finding *traceable* - a reader can see the exact
shape of "tried, measured, didn't help, here's why" rather than a single triumphant final number
with no visible history behind it.

## 2. Friction worth naming

### 2.1 Research should have come earlier in the sequence, not fourth (E1)

Two hypotheses were tried and measured (one a no-op, one a real regression) before research into
prior art was explicitly requested. In hindsight, the pattern that eventually worked - "this residual
survived two good-faith code-level fixes; what does the platform's own documentation say about this
class of problem" - was available after the *first* hypothesis failed, not just after the second.
The maintainer's own prompt was the actual unlock here, not something initiated proactively early
enough. A team (or an assistant) hitting a second failed hypothesis on a persistent, well-measured,
unexplained gap should treat that as the trigger for research, not wait for it to be asked for.

### 2.2 The diagnostic that cracked the case was reactive, not standard practice (E1)

The temporary logging that revealed the 120ms buffer size was added only after the calibrator's
null result was surprising enough to demand an explanation. A more disciplined default would build
a cheap, removable diagnostic *alongside* any timing hypothesis as a matter of course - not reach
for one only after being surprised. Instrumentation is cheap; guessing why a null result happened
without it is not.

### 2.3 A subjective complaint ("still fairly noticeable") arrived after a very good measured number, and the investigation had no ready way to triage it (E1, ongoing as of this writing)

The buffer-sizing fix measured ~2ms excess - inside target, a huge improvement. The very next
message reported the fix still feels noticeable. `docs/timing-accuracy-benchmark.md`'s own
"Deferred: true acoustic ground truth" section had already named, in advance, that the benchmark
measures internal scheduling/mixing precision, not real speaker-to-ear latency, and not whether a
perceived delay is the count-in's own deliberate pause rather than an error - but that gap sat
written down and unrevisited rather than being closed or even cheaply triaged the moment a real
complaint arrived that the measured number couldn't fully explain. Asking "which of these three
does the complaint actually describe" is a five-minute check (toggle the count-in cap, listen
again); it should happen before estimating a 1.5-2.5 week native migration, not after.

### 2.4 Several risky changes landed within one session under real time pressure, safe only because verification was consistent (E4)

The "try, measure, revert if wrong" cycle happened multiple times within single sessions. It worked
every time *because* verification (Robolectric suite + on-device benchmark) ran after every change,
without exception. That consistency is a discipline, not a guarantee - the one round that produced a
real regression (the warm-keep coroutine fix) would have shipped silently broken if verification had
been skipped "just this once" as an efficiency shortcut under the same time pressure that produced
it. Worth naming as a real risk the process carries, not just a risk that happened to not materialize
badly.

## 3. Concrete proposals

Not self-executing - candidates for a human (or a future assistant session) to pick up:

1. **Treat two consecutive failed hypotheses on the same persistent, measured gap as an explicit
   trigger for a research pass**, not something to wait for an explicit request for (§2.1). Cheap to
   adopt: it's a one-line addition to whatever internal checklist governs "what to try next" on a
   stubborn timing/performance bug.
2. **Default to adding a cheap, removable diagnostic alongside any new timing hypothesis**, before
   running it, not after a surprising result demands one (§2.2). The self-calibrating margin's
   diagnostic should have been standard practice, not an emergency measure.
3. **When a benchmark's own documentation names a measurement gap ("this doesn't cover X"), treat a
   later real-world complaint that contradicts an otherwise-good measured number as the trigger to
   close or at least cheaply triage that gap** (§2.3) - not as a prompt to reach for the next
   available code change (in this case, jumping straight to estimating a native rewrite) before
   ruling out the cheaper explanations the documentation already flagged as possible.
4. **Name "verification runs every time, no exceptions, even under time pressure" as an explicit
   rule for this class of work**, not an implicit habit (§2.4) - the cost of writing it down is
   zero, and the one round that needed it most (the regression) is proof it doesn't enforce itself.

## 4. Closing honesty

This is not independent review - I performed every round of the work it evaluates. It is not a
survey - every claim above rests on one investigation's history and should be weighted accordingly
until a second, comparably hard timing/performance investigation either confirms or contradicts these
proposals. And §2.3 is being written *before* it is resolved: the subjective complaint that prompted
this very retrospective is still open at the time of writing, addressed here only by naming the
triage step that hasn't yet happened, not by having done it. That is the honest state of things, not
a gap to paper over before publishing.

— Claude Sonnet 5, 2026-07-09
