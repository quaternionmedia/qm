# QM-XXXX — Shrink the Black Box: Undecidable Judgement, Decidable Guards

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-25 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P17 — shrink the black box; P15 — the layer's mathematics is sought on purpose; P16 — a check is evidence only after it has failed |
| **Restated in** | `PRINCIPLES.md` P17 |

## Context

This organisation already routes work through two rules that look like ergonomics
and are not:

- **Everything runs through `uv run qm <command>`.** Stated in `AGENTS.md` as
  "use the declared entry point"; `records/DRAFT-clis-are-for-machines-and-debugging.md`
  gives the interface reason.
- **Every paid model call passes through one gate.** `records/DRAFT-no-unattended-spending.md`;
  the mechanism is `qmcp/spend.py`, which does not call a paid service and is
  what a module that does must pass through.

Both were argued from cost and from interruption. Neither said what they have in
common, and they have the same shape: **each takes a decision away from something
that cannot be decided and gives it to something that can.**

That is a statement about computability, and this corpus has a principle (P15)
that says a layer's mathematics is looked for on purpose. This record does that
for the layer nobody had named — the boundary between an agent's judgement and
the code it produces.

## Decision

**A model is a black box with no halting guarantee, so it is never the check.
It drafts the check; a person authors it.**

Both halves are load-bearing and the second is the one that decays first. A
model that is not the decision procedure but *is* credited with the guard has
been let back in through the door this record closes: the guard's authority
would then rest on the thing with no halting guarantee. It rests on the person
who read it, broke it, watched it go red, and is accountable for it —
`records/DRAFT-human-only-contributorship.md`.

Three obligations follow, and they are the whole of the decision:

1. **Every guard is a total function.** It terminates on all inputs and returns
   a value. A check that might not return is not a check, and a check with no
   bound is a check that might not return.

2. **A bound that fires is reported, never absorbed.** Converting an undecidable
   question into a decidable one costs an answer: you learn "did not finish in
   N", not "will not finish". That is a fine trade and it is only fine if the
   bound firing is visible. **A bound that is caught and discarded is worse than
   no bound**, because it turns a halting failure into a plausible answer.

3. **The black box's surface is minimised, and what remains is metered at one
   seam.** Every act moved from an agent's judgement into a command shrinks the
   region where nothing can be decided. What cannot be moved goes through
   `qmcp`, so the non-determinism this organisation admits has exactly one door
   and that door counts what passes.

### The productive inversion

The obligations above sound like a restriction on the model. They are the
opposite: **the deterministic, time-bounded guards are drafted _with_ the
non-deterministic tool.** An agent is bad at being a decision procedure and good
at producing the syntax of one. So the work is to draft the check, run it, break
it, watch it go red (P16), and hand a person something they can author — and
then never be the check again.

**Which is why P16 is the transfer of authorship and not a testing habit.** A
guard nobody has seen fail is a draft. Breaking it, watching it go red, and
writing the mutation down is what a person does to take responsibility for it,
and after that the guard is theirs. The tool typed it; the mutation note is the
signature.

Said plainly, and this wording is the one to keep:

> **Work yourself out of the jobs you are not good at, playing to your
> strengths.**

The concrete instance this record was written from: an agent that waits for a
fourteen-minute test suite is doing a scheduler's job badly. Threading the run
and spending the interval drafting checks is the same time spent on the half it
is good at — and the drift between "what I expected while it ran" and "what it
reported" is itself material for the next guard.

## Why this is mathematics and not metaphor

The mapping is added to `ci/mathematics-registry.yaml` with its state named, as
P15 requires. The short form:

**The halting problem is not an obstacle here; it is the boundary condition that
tells you where to put the wall.** No general procedure decides whether an
arbitrary computation terminates. Adding a bound makes the question decidable —
trivially, and at a stated cost. So the design question is never "can this be
decided" but **"where is the wall, and does anyone see it when it is hit".**

That is why obligation 2 exists, and this session produced its worked example:
`waiting_org` asked `overview.build` for its attention rows, and
`overview.build` builds every facet including that one. The recursion ran
**109 levels** and was stopped by Python's recursion limit — a real bound, doing
its job. The `RecursionError` was then caught by a per-source guard written to
keep an unreachable harness from emptying a queue, and every frame above it
returned a plausible answer.

Nothing raised. The reading was correct. It was computed a hundred times, a
function deliberately optimised from 8.15s to 0.07s went back to 1.478s, and no
test noticed for four pull requests. **The bound fired and the report was
swallowed**, which is precisely the failure obligation 2 names.

## Alternatives

**Trust the agent and check the output.** This is the default elsewhere and it
is not wrong so much as unbounded: the set of things that could be wrong is the
set of things the agent might do, which is the black box again. Checking output
is necessary and is not a substitute for shrinking the region that produces it.

**Forbid the non-deterministic tool.** Refuses the leverage rather than
bounding it, and this corpus has an explicit position against that shape —
`records/DRAFT-build-the-seam-buy-the-engines.md`. The engines are bought; the
seam is built. A model is an engine.

**Bound everything with timeouts and stop there.** This is where the
organisation already was.
`perspectives/claude-sonnet-5-2026-07-18-test-timeout-halting-problem-retrospective.md`
produced a project-default test timeout, which is obligation 1 for one kind of
computation. Five weeks later the same practitioner class recurred in a form no
timeout addresses — a person standing still, and a bound whose firing was
discarded. A timeout answers *when do I stop waiting*. It does not answer *what
do I do meanwhile*, and it does not answer *who sees that it fired*.

## Consequences

- **`uv run qm <command>` stops being a convention and becomes the mechanism.**
  Each command is a total function with an exit status: a decision procedure a
  person or a machine can run without reading a transcript. Adding a route is
  how the undecidable region gets smaller, which is why `AGENTS.md` says that if
  there is no route, add one.
- **All model interaction moves behind `qmcp`.** Not for tidiness: one door is
  what makes the admitted non-determinism countable, and `spend.py`'s zero-budget
  first pass is the same idea in the cost dimension — establish the number
  without spending to find it out.
- **A caught bound must be reported.** `gather`-style per-source guards keep
  their reason for existing and gain an obligation: what they swallowed is
  surfaced, not merely survived.
- **Waiting becomes a choice that has to be justified**, which is a change to
  `handbook/async-contract.md` rather than to any tool.

## Verification

The recursion above: measured at 109 levels of nested `overview.build`, 1.478s
against 0.061s once the source asked `_attention` directly, and the reading
identical either way. Guarded by a call-count assertion rather than a duration —
a timing assertion on a fast machine passes with the recursion restored. Seen to
fail: restoring the `build` call turns the guard red.

The registry entry this record adds names what it has **not** earned: no bound
is stated for a `qm` command's own runtime, so obligation 1 is asserted of
guards and unmeasured for commands.
