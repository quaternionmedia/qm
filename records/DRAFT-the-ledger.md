# QM-XXXX — The Ledger

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-15 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P6 — decisions are documented or they didn't happen; P8 — systems over heroics |
| **Restated in** | Nothing |

## Context

A session states an intention, acts, and reports. Nothing in this corpus
compares the first to the third. An overclaim is caught only if a reader happens
to remember what was promised, which is a property of the reader's attention
rather than of the process.

Two days of work here made that concrete. A session predicted that reviewing a
workspace would surface parallel lanes and instead delivered an analysis
contradicting a record it had already read. A gate index was predicted to take
one file and took two, because the handbook already specified the shape and was
not consulted. A CLI was predicted to unify thirteen script paths, did, and was
simultaneously broken in a way no local run could reveal. Every one of those was
established afterwards, by reconstruction, when somebody asked.

The cost of reconstruction is not the reconstruction. It is that the record
comes from the party with the strongest interest in it reading well, at the
moment they are least able to remember accurately.

There is a second failure the same instrument addresses. Corrections in this
corpus have twice been applied to the instance they arrived on and not to the
class — a shell-loop audit fixed without the twenty other improvised invocations
being fixed, a signing flag reversed in direction rather than removed. A running
list of what has been attempted is the artifact a session can re-scan when a new
rule arrives.

## Decision

1. **Every substantive action is recorded in `ledger.yaml` before it is taken**,
   with what it is projected to do. An action too small to project is too small
   to record; the boundary is judgement and is meant to be.

2. **The projection is written before acting.** A prediction made after the
   outcome is known is not a prediction, and an instrument that permitted it
   would measure nothing. This is the clause the whole record rests on and the
   one no check can enforce.

3. **An entry is closed with an outcome, a failure cost, and a score.**
   `outcome_matched_projection` is `true`, `false` or `unknown`. **A `false` is
   not a defect.** An honest miss is more useful than a vague hit, and a ledger
   with no misses in it is evidence that the projections were unfalsifiable.

4. **`failure_cost` records what being wrong cost, including when nothing was
   wrong** (`none`). It is written even when — especially when — the cost is
   permanent and cannot be paid down.

5. **A reconstructed entry says so.** `reconstructed: true` marks an account
   written after the fact. It carries the reliability of a memory, and the
   distinction is kept because the first entries in this ledger are exactly
   that.

6. **The ledger is re-read when a correction arrives**, to find every other
   entry the correction applies to. This is the class-not-instance step, and it
   is the reason the list is running rather than per-task.

7. **Enforcement.** `ci/ledger.py --check` refuses a closed entry with no
   outcome, no failure cost, or no score; refuses an unknown `kind` or `status`;
   and refuses duplicate ids. `uv run qm ledger --open` lists what is predicted
   and unsettled.
   **What it cannot do, and this is most of it:** it cannot tell that a
   projection was vague enough to be unfalsifiable, that an outcome was written
   to match, or that §2 was honoured at all — a projection typed after the fact
   is indistinguishable from one typed before. The instrument makes the
   comparison possible and cheap. It does not make it honest.

## Consequences

- An overclaim becomes mechanical to spot: the projection is durable and sits
  next to the outcome.
- A session's cost accounting exists at the end of the session rather than being
  reconstructed when somebody asks, by the party with the most interest in it
  reading well.
- Cost accepted: a per-action overhead on work that is going fine. The bet is
  that it is small and that the sessions where it feels wasteful are exactly the
  ones whose predictions later turn out to have been wrong.
- Cost accepted: the ledger grows and nothing prunes it. When that becomes a
  burden the answer is a per-milestone file, not a shorter memory.
- The instrument is most easily defeated by the party operating it, and §2 is
  unenforceable by construction. This record states that rather than implying a
  guarantee it cannot give.

## Alternatives considered

1. **Rely on the handoff at session end** — rejected. That is reconstruction,
   which is the failure. A handoff is written by whoever wants the session to
   read well, at the point of least accurate recall.
2. **Record only failures** — rejected. `ci/pattern-registry.yaml` already does
   that and it cannot show a prediction that was met, so it cannot show a
   *rate*. A register of only-bad-things also invites the operator to classify
   marginal outcomes as fine.
3. **Score the projections for quality** — rejected for now. Judging whether a
   projection was falsifiable is a reading, and a rubric would be gamed by the
   same party that writes the projections. It is named as a revision trigger.
4. **Automate capture from the transcript** — rejected. The transcript is not in
   the repository, and a projection extracted from prose after the fact violates
   §2 while looking like compliance.

## Revision triggers

- The ledger accumulates entries with no `false` scores over a milestone, which
  would mean the projections are unfalsifiable rather than that the work is
  faultless.
- Open entries accumulate and are never closed, making the instrument a place
  intentions go to be forgotten.
- The overhead is cited as a reason to skip it on a real task. That is the
  moment to make it smaller, not optional.
- Someone other than the author of an entry finds the outcome field materially
  wrong. §2 would then be failing silently and the instrument would be worse
  than nothing.

## Amendments

*None.*
