# ADR-XXXX — Appointing one instance to direct another, without a v0 contract change

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-17 |
| **Pends on** | **Human review.** This builds on a rule v0 excluded deliberately; nothing here is ratified, and §5's drift is live in the code today |

## Context

rad is the bus's first consumer, and it runs as two instances — a stage-left
and a stage-right — that must stay in step. The question this record answers
is narrower: **can one instance be appointed, under stated circumstances, to
direct the other, and what does that cost?**

The topic contract makes it deliberately hard:

> Commands are present tense and are requests *to frizzle's queue*, not to a
> peer: the producer publishes, frizzle journals/assigns/acks, a worker claims.
> **Project-to-project direct commands are deliberately absent from v0.**

And facts are the other half of that design:

> Facts are past tense and describe something that happened; publishing one
> **asserts nothing about what any consumer will do**.

So the bus has no way for one peer to instruct another, on purpose. The
temptation is to add one. This record is the argument for not doing that yet,
and for what to build instead.

The demonstration is `frizzle poc rad`, which runs green against a real
broker. It models rad; it does not run rad.

## Decision

**§1. Authority and instruction are separated.** They are different problems
with different lifetimes, and conflating them is where this design goes wrong.
*Authority* — who may direct, under what circumstances — is slow-moving, must
survive a restart, and must be revocable. *Instruction* — the individual
direction — is fast-moving and needs delivery, an acknowledgement, and an
audit trail.

**§2. Authority is retained config, carrying an epoch, a scope and an expiry.**
A retained `qm/rad/cfg/director` names the appointee. Retention is what makes
a restarting instance know who is in charge *before its first frame*, which is
the same property the config recipe already proves for ordinary state.

Three fields are load-bearing:

- **`epoch`**, monotonic. Without it a director whose appointment was withdrawn
  keeps issuing, and no follower can tell a stale direction from a current one.
  This is a fencing token, and frizzle already has the same gap for job claims.
- **`scope`** — which verbs, which acts. The circumstances belong in the
  appointment, not in the follower's code, or "under some circumstances" is
  invisible to the journal and unauditable after the show.
- **`expires_after`** — an appointment with no expiry becomes permanent the
  first time somebody forgets to revoke it.

**§3. Instruction goes through frizzle's queue, addressed by payload.** The
director publishes to `qm/rad/cmd/<verb>` with `assignee` naming the intended
executor. frizzle queues it as it queues anything; the named instance claims
it and the others do not.

This is inside the letter of the v0 rule — the command is still a request to
frizzle's queue, not to a peer — and it buys what a stage needs anyway: a
direction that is not followed **dead-letters instead of vanishing**, "did
stage-left obey?" becomes a journal query, and retry and acknowledgement come
free.

**§4. A follower may refuse, and must be able to say why.** A follower that
cannot refuse is not a peer. A stage instance with a safety interlock engaged
has to be able to decline, and the refusal has to carry a reason. The POC
publishes a correlated `stage.direction-refused` fact alongside the queue
event.

**§5. The drift this creates, named rather than discovered later.**

Every mechanism above is a **convention that nothing enforces**. The POC
records them as a measurement (`unenforced_conventions`) so they appear in
every run rather than only in this document:

| Convention | What enforces it today | How it drifts |
|---|---|---|
| `payload.assignee` selects the executor | Nothing. Any instance may claim any job | A second consumer invents `payload.target`, or an instance claims work addressed to a peer, and both are legal |
| `payload.epoch` supersedes an appointment | Nothing. No component compares epochs | A withdrawn director keeps directing and the bus carries it faithfully |
| Refusal is expressed as `job.failed` | The queue vocabulary is `queued \| claimed \| done \| failed \| dead` — there is **no terminal-refusal state** | A final "no" is retried. Measured: the POC's refusal was re-asked **3 times** before dead-lettering |
| A direction is `priority: critical` | Nothing. `priority` is carried and never read | A direction is dispatched exactly like a background job |

The largest drift is not in the table. It is that **a POC can become the
contract by habit**: if rad ships on these conventions, they are the bus's
real interface whether or not the contract document ever mentions them, and
the next consumer will copy them from the code. The contract document is the
source of truth precisely so that cannot happen quietly.

**§6. What is deliberately not proposed.** No new `dir/` domain, no addressing
field on the envelope, no project-to-project command. Those are the v0
exclusion, and reopening it is an amendment to the contract, not a commit —
document, code and recipe moving together, with a record behind it.

The honest trigger for reopening is **latency**, not convenience: the queue
round-trip may not fit rad's above-the-clock tolerance. That is Phase 1's
question, and it is answered with numbers or not at all.

## Consequences

- Two rad instances can be appointed and can direct each other today, with no
  contract change, and the POC demonstrates it end to end.
- Four unenforced conventions are now load-bearing. They are printed by every
  POC run, which is the cheapest way to keep them from becoming invisible.
- A principled refusal costs `max_attempts` round trips before it is terminal.
  For a stage cue that is a real latency cost and a misleading audit trail: the
  journal shows a direction asked three times, which reads as an unreliable
  follower rather than a firm no.
- If the conventions are adopted, they belong in the contract document — at
  which point they are no longer conventions and the enforcement gaps become
  frizzle's work: assignee-aware claiming, epoch rejection, a terminal-refusal
  state, and a priority the dispatcher actually reads.
- Until a human reviews this, nothing here is settled. The POC is evidence,
  not a decision.

## Alternatives considered

1. **Facts plus follower policy, with no queue involvement.** The director
   publishes a fact and the follower's own policy decides to obey. It needs
   nothing new at all and keeps the contract's semantics exactly. It loses
   because authority stays advisory: nothing records whether the direction was
   followed, and for stage work "did it happen?" is the whole question.

2. **A new `qm/<project>/dir/<instance>/<verb>` domain.** Explicit, direct, and
   the lowest latency. It loses *for now* because it is precisely the v0
   exclusion, it reintroduces point-to-point coupling between instances, and
   the contract's own open question — whether `msg/` needs per-recipient
   subtopics — is the thin end of the same wedge. Reopen it with latency
   numbers, not with a preference.

3. **An addressing field on the envelope (`to`, `audience`).** Cleaner than a
   topic-level answer and it would serve `msg/` too. It loses because it is an
   envelope contract change, which every consumer must then handle, to solve a
   problem one consumer has not yet measured.

4. **Election rather than appointment.** Removes the human from the loop. It
   loses because MQTT is a poor consensus substrate, and because for a stage
   the question "who is calling the show" has an operator answer already —
   automating it adds a distributed-systems problem to buy nothing.

## Revision triggers

- Phase 1 measures MQTT round-trip latency against rad's tolerances. If the
  queue path does not fit, §3 is wrong and alternative 2 gets its hearing.
- rad ships anything built on §2 or §3, at which point the conventions in §5
  stop being a POC's business and belong in the contract document.
- A second consumer needs directed work, making a per-project convention an
  org-level interface.
- frizzle gains claim exclusivity or a fencing token, which closes two rows of
  §5 and changes what this record has to say about them.
- The `job/<state>` vocabulary gains a terminal-refusal state.

## Amendments

*None.*
