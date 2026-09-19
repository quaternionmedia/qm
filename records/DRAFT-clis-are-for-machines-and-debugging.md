# QM-XXXX — CLIs Are for Machines and for Debugging

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-20 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P13 — a person is interrupted only by a decision; P8 — systems over heroics |
| **Restated in** | `PRINCIPLES.md` P13 |

## Context

This organisation built a human-in-the-loop pair — a harness that runs things
and a control panel that shows them — and then wrote the onramp for testing it
with a person. The loop it described was **eight commands, across two
repositories, in two shells**, with two files copied by hand between them.

Every one of those commands worked. The suites were green, the payloads were
contract-verified, and the whole path had been exercised end to end. What had
not been noticed is that none of it was a workflow. It was a set of levers, and
the page describing the order to pull them was doing the work an interface
should have done.

The evidence arrived immediately and in the worst way: the first person to
follow the page could not complete it. Two of the eight commands had no step
number, so the file the seventh command needed was never written. The same
literal path meant two different directories in the two shells the page moved
between. Neither failure was in the code. Both were in the space the design had
left for a person to get right by reading carefully.

**A page of ordered commands is a workflow specification that nobody
implemented.** The moment it exists, its correctness depends on the reader, and
readers do not run in CI.

There is a second half, and it is the one that cost more. The queue of questions
the harness put to a person crossed to the control panel **as a count**. The
panel could say one thing was waiting and never which thing, so answering
anything meant going back to the other application. A count is not something
anybody can answer, and a notification that cannot be acted on where it is read
is not a notification — it is a reminder to go and find the real one.

## Decision

**A command line is for machines and for debugging. A person is interrupted
only when a decision is needed, and the interruption carries what a decision
requires.**

1. **A workflow a person walks is implemented, not documented.** Where a
   sequence of steps exists, the system runs the sequence; the person supplies
   what only they can. A page that orders commands is a design note about an
   interface that has not been built, and it is honest to call it that.

2. **Every interface has a command line, and no interface is only one.** The
   CLI is required — automation needs it, and so does whoever is diagnosing why
   the interface is wrong. What is refused is the CLI standing in for the
   design.

3. **A person is reached for a decision, not for a step.** Sequencing, copying,
   re-running and remembering are the system's work. If a person is asked to do
   one of them, the reason is that the system cannot yet, and that is a gap
   with a name rather than a way of working.

4. **An interruption states the question, the options, and what turns on it.**
   Not that something failed. What happened, what may be said in reply, and
   what each reply commits the answerer to. A prompt without options is a
   report; a report is not an interruption and must not be delivered as one.

5. **What is waiting on a person is visible where they are, and answerable
   there.** A queue that crosses as a count has not crossed. This is the
   clause with the sharpest edge: it means a notification surface owes a way to
   act, or it owes an explanation of why acting happens elsewhere.

6. **Interrupting has a cost that is paid later.** A system that asks
   constantly trains its people to stop reading, and the question that mattered
   then arrives looking like the ones that did not. The budget for
   interruptions is small because attention does not scale, not because
   attention is expensive.

**Enforcement, and it is a count rather than a rule.** Each named workflow
records the number of commands a person must type to complete it. The number is
kept beside the workflow and a rise without a stated reason is a regression.
The paired measure is the proportion of interruptions in a session that were
decisions rather than steps. Neither number is a threshold anybody passes or
fails; both are trends that make a drift visible while it is still cheap.

## Consequences

**Some work gets harder before it gets easier.** Building the loop into the
applications is more expensive than writing the page that lists the commands,
and the page is available today. This record says to build it anyway, and the
cost is real.

**"It has a CLI" stops counting as done.** That will be unwelcome in exactly
the cases where the CLI was the fast path, which is most of them.

**A queue gains an obligation.** Anything that can be waiting on a person now
owes a surface where that person can see it and act. Half of that is cheap and
half is the seam between two systems, which is where the expensive part lives.

**Debugging keeps every affordance it has.** Nothing here removes a flag, a
`--json`, or a way to drive a component in isolation. The refusal is narrow: a
command line may not be the only way a person completes ordinary work.

## Alternatives considered

**Say "prefer a UI" and leave it there.** Rejected as a motherhood statement —
the failure mode this charter names. It states a preference with no way to tell
whether anybody followed it, and this organisation's own measured finding is
that a clause without a mechanism does not change behaviour.

**Ban command lines for user-facing work.** Rejected as false. The CLI is how
automation drives anything, how a walkthrough executes, and how somebody
establishes what a broken interface is actually doing. Removing it would cost
more than the problem.

**Count clicks instead of commands.** Rejected: it optimises the wrong thing. A
single well-formed question that takes three clicks to answer is better than
one keypress that answers the wrong question. The count that matters is *steps
a person must sequence themselves*, not effort per step.

**Treat this as a style-guide matter.** Rejected. Taste belongs in the style
guide, and this has architectural consequence: it decides whether a seam owes a
surface, and it is the reason a queue crossing as a count is a defect rather
than a limitation.

## Revision triggers

- A workflow whose command count is high and correctly so — where sequencing
  genuinely is the person's judgement — which would mean clause 1 is too broad.
- An interruption surface that carries options and is still ignored, which
  would mean clause 4 names the wrong property.
- The counts staying flat while people still describe the work as painful,
  which would mean the measure is not measuring the thing.
- A second organisation adopting this and finding the CLI carve-out in clause 2
  used to justify what clause 1 refuses.

## Amendments

*(none)*
