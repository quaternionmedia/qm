# Perspective — The Suite That Outgrew Its Loop: A Retrospective on Making Verification Too Slow To Use

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5, the assistant that wrote the tests this retrospective is about and then waited at them |
| **Task** | A process retrospective on one long session in `dossier`: nine slices landed as nine pull requests, and across them the assistant roughly doubled the test suite's runtime and then repeatedly blocked on it — including one instance of tying up the maintainer's machine for a fifty-minute foreground call. The maintainer named the shape directly: *"that was me idling instead of planning around it"* was the assistant's own sentence, quoted back. This document is about the reasoning failure, not the split of `tui/app.py` that follows it. |

## 0. Standing, scope, and evidence base

Single-session retrospective. Every figure below was measured during the session
it describes, on one machine and one repository, and each is one run at one
commit.

Evidence classes, per this corpus's convention:

- **E1** — directly measured this session: `pytest` durations, GitHub Actions
  job times read from `gh pr checks`, file and test counts from `git`.
- **E2** — read from the session's own transcript: which commands were run,
  in what order, and what was said while waiting.
- **E3** — inference. Marked where it appears.

## 1. What happened

Nine slices, nine pull requests, all green. That is the part that looks fine.

The part that does not:

| | at the session's start | at its end |
|---|---|---|
| CI's `tests` job (**E1**) | 5m 2s | 9m 32s |
| the local governed loop (**E1**) | 412s | 836s |
| tests collected (**E1**) | ~1,050 | 1,259 |
| test files (**E1**) | 66 | 75 |

**The suite's runtime doubled in one session, and I doubled it.** Then, at the
end of every slice, I ran it — and waited.

### 1.1 It was not the accumulation, and I nearly published that it was

The first draft of this document said the suite had grown steadily heavier and
blamed the two hundred tests I added. Writing that sentence is what made me
check it, and the curve says otherwise (**E1**):

| pull request | CI `tests` |
|---|---|
| #35 | 5m 2s |
| #39 | 4m 37s |
| #43 | 5m 9s |
| #45 | 4m 53s |
| **#46** | **9m 5s** |
| #47 | 9m 32s |

Flat for six pull requests, then a step. Two hundred tests spread evenly do not
draw that shape; one change does. #46 is mine, and §4.1 is what it did.

The retrospective almost carried a plausible cause instead of the real one,
which is the same failure it is about.

The worst instance was a single foreground call with a fifty-minute timeout on
it. The maintainer stopped that one: *"No more timeouts longer than a few
minutes. 50 minutes is absolutely unacceptable."* That was correct, and the
number is mine.

## 2. The shape of the error, which is not "the tests are slow"

Slow tests are a cost. Costs get paid. The error is narrower and worse.

**I treated "run the gates locally before calling a pull request ready" as "run
everything, every time, and stand still while it runs."** The constitution's
item 5 says to run the CI locally before calling a PR ready. It does not say
that verification is the only thing that may happen in a working hour, and it
does not say the whole suite is the only unit of verification.

What I actually did, per slice (**E2**):

1. write the change,
2. run the targeted tests (seconds — this part was fine),
3. run the mutations (a minute or two — also fine),
4. **run the entire suite and wait**,
5. commit, push, open the PR,
6. **wait for CI to run the same suite again**.

Steps 4 and 6 are the same measurement taken twice, and I blocked on both. By
the end of the session step 4 alone was fourteen minutes, and I ran it — with
restarts after edits invalidated a run — on the order of a dozen times.

### 2.1 The specific waste: measuring a tree I was still changing

Three times I started the full loop, then edited source before it finished, then
stopped it and started it again (**E2**). Each restart threw away several
minutes for a reason I had already written down elsewhere in this same corpus:
the scaffolding is part of the measurement, and a suite reading a tree that
changes underneath it measures nothing.

Knowing the rule did not stop me spending the minutes. What would have stopped
me is a habit of *finishing the edits before starting the long thing*, which is
a scheduling decision and not a knowledge one.

### 2.2 The idling, which is the part the maintainer named

While the loop ran I said, in as many words, that I was holding off on edits so
the run would stay valid. The maintainer's reply: *"no. keep track and properly
plan and async the work."*

That was right, and my framing had been wrong in an interesting way. I had
correctly identified that editing during a run invalidates it, and then drawn
the conclusion that the only safe thing was to do nothing. The actual
conclusion available was: **do work that does not touch the tree** — read code,
scope the next slice, review the diff I had just written, check another
repository. I did some of that later in the session, after being told twice.

## 3. This is a recurrence, and that is the evidence

`perspectives/claude-sonnet-5-2026-07-18-test-timeout-halting-problem-retrospective.md`
is a retrospective on watching a maybe-hung test rather than bounding it. Same
practitioner class, five weeks earlier, and its concrete response was a
project-default test timeout in qmetronome.

`records/DRAFT-decision-record-discipline.md` §8 is explicit that recurrence by
one practitioner is evidence, not its absence. So the honest reading is not
"this happened again"; it is that **the July response bounded how long a single
test may run and left untouched how long a person may stand still**, and the
second is what recurred.

A timeout answers "when do I stop waiting". It does not answer "what do I do
while waiting", and it does not answer "should this take fourteen minutes at
all".

## 4. Where the fourteen minutes actually goes

### 4.1 A reading that rebuilt the page it sits on

`waiting_org` gathers three sources, and one of them asked
`overview.build(...)` for the attention rows. `overview.build` builds every
facet — including `waiting`.

Measured after the curve above pointed at #46 (**E1**):

```
overview.build entered, deepest nesting: 109
overview.build      1.478s     (it was 0.061s)
the waiting facet   1.461s     (it is 0.001s)
```

**109 levels of nested `build`**, stopped by Python's recursion limit, with the
`RecursionError` caught by `gather`'s own per-source guard — the guard that
exists so an unreachable harness does not empty the queue. Every level above
the innermost one succeeded, so the answer came back *correct*, computed a
hundred times, and `unreachable` was empty because nothing above that frame had
failed.

Nothing raised. Nothing was wrong on screen. `overview.build` had been taken
from 8.15s to 0.07s by deliberate work in #33, and this put it back to 1.478s
without a single test noticing.

The only signal was CI's clock, and I read it four pull requests later, while
writing a document about not reading clocks.

The fix is one line: ask `_attention` for the attention rows rather than asking
`build` for the whole page. `build` is the page that happens to contain the
answer; `_attention` is the function that has it.

Measured this session (**E1**):

| | tests | wall clock |
|---|---|---|
| `tests/core` | 793 | 99s |
| everything else | ~470 | ~737s, derived |

The second figure is derived rather than measured, and the way it came to be
derived belongs in this document. I started a `tests/ui --durations` run to get
it directly, left it going, and stopped it after fifteen minutes — because the
whole suite is 836s and `tests/core` is 99s, so the remainder was already known
to within the rounding. Fifteen minutes of somebody's machine for a number
arithmetic already had.

I also piped that run through `tail`, which meant no interim output existed to
check, so "is it still working" was unanswerable for the whole fifteen minutes.
That is the same mistake in a smaller frame: I arranged not to be able to see.

I did it three times in this one investigation (**E2**) — twice on a test run
and once on the corpus's own `preflight`, where it discarded the failing step's
explanation and left me with only the step's name. Piping a long command
through `tail` trades everything that happens for the last few lines of it, and
the thing worth reading is almost never in the last few lines.

`tests/ui` constructs a Textual application **127 times** (**E1**) across 22
files. Every one of those boots a widget tree, a database session and an event
loop to assert one fact.

**Most of those boots are justified**, and I want to be careful not to overclaim
here, because overclaiming is the other failure this session recorded. A test
that posts `Tree.NodeSelected` and checks what the handler did has to have a
running application; I wrote several of those deliberately, after a mutation run
proved that calling the handler's helper directly passed while the feature was
broken. Those are the tests earning their seconds.

What I have **not** established is how many of the 127 are of that kind and how
many assert something a registry lookup or a source scan would answer in
milliseconds (**E3** — this is inference, and the measurement to settle it is
one `--durations` run per file, which is cheap). Of the five UI files I added
this session, one boots no application at all and the other four boot seventeen
between them.

## 5. What I would do differently, concretely

1. **Two loops, named, with different jobs.** A fast one for the inner cycle —
   the targeted tests plus the mutations, seconds — and the full governed loop
   once, at the end, before the pull request. I ran both all session; I just
   ran the slow one far more often than it earned.

2. **Start the long thing last, and never before an edit.** The three restarts
   were entirely avoidable and cost more than they saved.

3. **Background it, and have the next thing ready.** Not "find something to do
   while waiting" — decide *before* starting the run what the parallel work is.
   Reading the next slice's code is almost always available and almost always
   useful.

4. **Treat CI as the second measurement, not the first.** Local verification
   before the PR is the constitution's requirement and I will keep it. Watching
   CI re-run the identical suite while doing nothing else is the part with no
   justification.

5. **Budget the suite the way this corpus budgets a menu.** rad refuses a verb
   over its keyboard budget and calls it a resolver design error rather than a
   number to relax. A suite has the same property: every test is paid for on
   every run by every contributor, and "it is only three more seconds" is the
   sentence that produced fourteen minutes.

## 6. What this does not claim

It does not claim the tests are bad, or that there are too many. The suite
caught real defects in my own work repeatedly this session — a component pane
that would have become unreachable, a guard that silently tested nothing, an
overclaimed bug that no mutation could kill. Those tests are why nine slices
landed without a regression, and the count is not the problem.

It does not claim the recursion in §4.1 is the whole of the difference. It is
worth about four minutes of CI on the measurement above; whether the remaining
growth is the tests I added or something else is unmeasured, and one
`--durations` run per file would settle it.

It does not claim a number the suite *should* run in. I have not measured what a
reasonable target would be, and inventing one here would be a figure in durable
text with nothing behind it.

It does not claim the split of `tui/app.py` — nine thousand lines, and the
direct cause of three separate anchoring mistakes this session — is a response
to any of this. That work was queued before this retrospective and stands on its
own.

## 7. Proposals

Offered, not decided. Each names the smallest thing that would have changed the
session.

1. **A named fast loop in the seed.** `run_workflows_locally.py` is the full
   gate and should stay so. A sibling entry point that runs a repository's
   quick checks — whatever that repository defines as quick — would give the
   inner cycle something to be, rather than leaving the full loop as the only
   verb.

2. **Per-file duration reporting in the ordinary command.** `--durations` costs
   nothing and would make the cost of a new test visible at the moment it is
   added, which is the only moment anybody is deciding.

3. **Read the clock that is already running.** CI reported this defect on
   every pull request from #46 onward and I did not look, because the check
   was green and green is what I was checking for. A step change in a job's
   duration is a signal even when nothing fails, and it is free — the number is
   already printed next to the tick.

4. **An extension of the July timeout decision to cover waiting, not only
   running.** The mechanism there bounds a test. What recurred here is a person
   bounded by nothing, and the fix is a habit rather than a flag: name the
   parallel work before starting anything long.

5. **A line in `handbook/async-contract.md` about backgrounding.** That page
   exists because other sessions are running concurrently. A long verification
   run is the same class of fact: it is a thing in flight, and standing still
   next to it is a choice that should have to be justified.

## 8. The sentence worth keeping

The maintainer's framing was better than mine: *plan to be effective instead of
idling and skirting around the task at hand.*

I had been treating waiting as a neutral state — neither progress nor error. It
is neither only when nothing else could have been done, and this session that
was almost never true.
