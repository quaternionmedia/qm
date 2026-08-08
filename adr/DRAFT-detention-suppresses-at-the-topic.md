# ADR-XXXX — Detention Suppresses at the Topic, Never in the Payload

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-08 |
| **Pends on** | Nothing — ready to be argued |

## Context

A physical control needs a way to be temporarily deaf. The cases are ordinary
and they are the ones that decide whether someone keeps the thing on the wall:
a cat that has learned the button does something, a toddler at exactly the
right height, a sleeve that catches a plate, a rehearsal where the light must
not change no matter what anyone leans on.

A detent is the position a mechanism rests in, which is the right vocabulary
for a module with two: **armed**, accepting input, and **detained**, ignoring
it.

The design question is not whether to have the state. It is where the
suppression is expressed, and there are only two candidates: in the payload, as
a field on the event, or in the routing, by sending the press somewhere the
actuating consumer is not listening.

The payload option is the obvious one and it is unavailable, for a reason
internal to this project rather than a matter of taste. The event envelope
record makes unknown fields ignorable by consumers — absolutely, as the
mechanism that lets a consumer written today survive a module built years from
now. A `"detained": true` field would therefore be discarded by exactly the
consumers that most need to honour it: every one written before the field
existed. They would read the `action` they understand, ignore the field they do
not, and switch the light. The cat wins, and the compatibility guarantee is
what handed it the victory.

This is the general shape of the problem: **a must-understand semantic cannot
be carried additively in a payload whose readers are contractually required to
discard what they do not recognise.** Protocols that need both usually grow a
must-understand flag or a version gate. This project has deliberately refused
both, because they are the mechanisms by which a consumer written today starts
rejecting tomorrow's modules.

## Decision

1. **A module has a detent position**, one of `armed` or `detained`, published
   **retained** on `<src>/detent`. Retained for the same reason availability
   is: a consumer arriving late must be able to tell a deliberately deaf button
   from a broken one, or it will report a fault that is a setting.
2. **While detained, a press is published to `<src>/detained` instead of
   `<src>/event`.** Not retained, on the same reasoning as events: a press is a
   moment, even a press nobody acted on.
3. **Suppression is never expressed as a field on the event.** No
   must-understand flag, no version gate, no field whose absence changes how an
   event should be treated. Any consumer subscribed to the event topic is
   correct during detention by construction, because it receives nothing.
4. **Detention suppresses actuation, not observation.** The press is still
   published, still carries a valid envelope, and is still visible to anything
   that chooses to subscribe. A module that silently discarded input would make
   "why did nothing happen" unanswerable, and would remove the evidence that a
   detained button is being pressed constantly — which is the signal that it is
   mounted in the wrong place.
5. **`seq` advances through detention.** A detained module that skipped
   sequence numbers would be indistinguishable from one dropping packets, and
   loss detection is what `seq` exists for.
6. **Detention is a local state in this milestone.** The module holds it; the
   contract publishes it. Whether a controller can *set* it remotely is a
   separate decision, because it introduces the first inbound path in a
   contract that is otherwise entirely outbound, and that direction deserves
   its own record rather than arriving as an implementation detail of this one.

## Consequences

- The feature works against every consumer that already exists, including ones
  written before detention was conceived, with no coordination and no version
  negotiation. That property is a direct consequence of clause 3 and is the
  reason this record is worth ratifying rather than being a naming exercise.
- A deployment gains a record of detained presses, which is diagnostically
  useful in a way the suppressed alternative is not: a detained topic with
  heavy traffic is a mounting problem stating itself.
- **Accepted cost: two topics now carry the same payload shape**, and a
  consumer that wants "every press regardless of detent" must subscribe to
  both. That is real friction, and it is the price of clause 3. A single topic
  with a flag would be tidier and would not work.
- **Accepted cost: the detent state is one more retained topic to reason
  about**, and a stale retained `detained` after a firmware wipe would leave a
  button mysteriously deaf. Availability has the same hazard and the same
  answer — publish the current position on connect — but it is a hazard, not a
  theoretical one.
- Obligation created: the projections table gains a question for every future
  transport. A projection that cannot express two distinct destinations cannot
  express detention, and must say so rather than silently collapsing them into
  one — which would reintroduce exactly the failure clause 3 avoids.
- Clause 6 leaves a visible gap. A user who wants to detain a button from a
  phone cannot, and the honest position is that the inbound path is undecided
  rather than unnecessary.

## Alternatives considered

1. **A `detained: true` field on the event.** The design everyone reaches for
   first. It lost outright, not on preference: the envelope's ignore-unknown
   rule guarantees that every consumer predating the field ignores it, so the
   flag would be honoured only by consumers that did not need it. A safety
   affordance that works exclusively on up-to-date software is not a safety
   affordance.
2. **A must-understand flag, or a schema version gate that makes old consumers
   reject events they cannot fully interpret.** The standard protocol answer,
   and it lost because it inverts this project's central claim. Both work by
   making a consumer refuse what it does not understand, and the entire premise
   is that a consumer written today keeps working against a module built later.
   Adopting either would trade the generational guarantee for one feature.
3. **Publish nothing while detained.** Simple, and it loses the diagnostic
   value in clause 4 along with any way to distinguish a detained button from a
   dead one, from a broken contact, from a radio that stopped associating. The
   silence is indistinguishable from every failure mode it resembles.
4. **Let the consumer decide, by publishing the detent state and expecting
   subscribers to check it before acting.** It lost because it relocates a
   safety property into every consumer's automation logic, where it is
   invisible, untested, and absent from the ones written before detention
   existed. It is the same failure as alternative 1 with an extra step.
5. **A separate "disabled" device that shadows the real one**, so a controller
   binds to one or the other. It lost on identity: the button did not move, and
   anything binding to it should not have to re-bind because it was
   temporarily muted.

## Revision triggers

- A transport is adopted whose projection cannot express two distinct
  destinations, forcing either detention's absence on that transport or a
  reconsideration of clause 3.
- Remote setting of the detent becomes a committed deliverable, which resolves
  clause 6 and adds an inbound path the contract does not currently have.
- A deployment is found subscribing to both topics and merging them, which
  means the two-topic split is being worked around rather than used, and the
  friction named in Consequences has become a cost rather than a price.
- A second must-understand semantic appears — anything else meaning "do not act
  on this" — which would make the routing answer a general pattern worth
  stating once rather than a solution to detention specifically.
- A stale retained detent position is observed causing a mysteriously deaf
  module in the field, which makes the hazard in Consequences a defect needing
  a mechanism rather than a note.

## Amendments

*None.*
