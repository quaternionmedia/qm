# QM-XXXX — Whether Something Is a Delta Is a Perspective, Not a Property

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-20 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P6 — decisions are documented or they didn't happen; P3 — seams on standard protocols |
| **Restated in** | Nothing. The qmPM standardisations page cites it, which is a citation rather than a restatement: that page decides nothing and says so |

## Context

The delta is this organisation's unit of work, and the obvious next question is
what counts as one. A branch, plainly. A pull request, plainly. A step in a
pipeline — less plainly. A single turn in a conversation — surely not.

That framing is wrong, and it is wrong in a way that only shows up once work
starts arriving from more than one kind of place.

`qmcp/cookbook/delta.py` already half-knows it. Its docstring says a workflow
step and a delta are *one unit of work seen from two ends*, and it maps between
them without deciding which is the real one. That module was written for one
correspondence and the property it noticed is general: **the same thing is a
unit of work from one vantage and an internal detail from another, and both
readings are correct.**

A test suite is one delta to the person deciding whether to cut a tag. It is
four hundred deltas to whoever is fixing them. Neither is confused.

The failure that follows from getting this wrong is not abstract. A standard
that fixes granularity globally has to pick a level, and every system whose
natural level is different then either inflates its work to fit — filling the
board with rows nobody reads — or hides it, so the board is quiet about work
that is happening. Both are worse than saying nothing, because both look like
answers.

There is a second cost, and it is the one that would have bitten soonest.
Threads. A conversation is mostly steps: a hundred turns producing three
decisions. Mirroring every turn as a delta buries the three. Mirroring none
loses them. The question "is a turn a delta" has no answer, and the reason is
that the question is missing its subject.

## Decision

**Granularity is a property of the perspective, not of the thing. A payload
says whose perspective it was emitted from, and no perspective is
authoritative over another.**

1. **A delta is a unit of work *to somebody*.** The same underlying thing may
   be a delta in one perspective and a step inside a delta in another. Neither
   is a mistake and neither is corrected.

2. **Every emitted delta names its perspective.** A payload without one cannot
   be placed: the receiving system does not know at what level it was told
   this, and will either flatten it into its own or guess. The perspective is
   part of the claim, in the same way `phase_source` is part of a phase claim.

3. **A perspective is named, not ranked.** There is no root perspective and no
   ordering. Asking which of two is more correct is the question this record
   says is malformed.

4. **The two readings are related by `part-of`, and that relation is stated
   rather than derived.** When one perspective's delta is another's step, the
   composition vocabulary already says so — `records/DRAFT-deltas-compose.md`.
   What must never happen is a system inferring the relation from the fact that
   two rows have similar names.

5. **A receiver may filter by perspective and may not rewrite one.** A board
   showing only its own perspective is ordinary and correct. A board that
   promotes another perspective's steps into its own deltas is asserting
   something nobody claimed.

6. **What is not work is still not a delta, in any perspective.** A green check
   is not a unit of work — that rule stands and this does not soften it. This
   record is about *level*, not about whether something is work at all.

**Enforcement.** The delta payload carries `perspective`; a payload without one
is refused rather than defaulted, because a default here is a silent claim about
level. `dossier deltas ingest` is the mechanism.

## Consequences

**Threads become tractable.** A session can emit its decisions as deltas from
its own perspective, and the turns underneath them stay steps. Nothing has to
decide globally whether a conversation turn is a unit of work, because the
question was never global.

**Two boards can show different numbers of rows for the same work and both be
right.** That will look like a bug the first time somebody sees it, and the
perspective field is what makes the answer available instead of a debate.

**A payload gains a required field**, and existing emitters have to say what
they are. That is a cost and it is the point: an emitter that cannot say whose
perspective it speaks from does not know, and a receiver placing that row is
guessing.

**Rollup between perspectives is not free.** Counting one perspective's deltas
and another's together produces a number that means nothing. Any view that
spans perspectives has to say it is doing so.

## Alternatives considered

**Pick a level and standardise on it.** Rejected: whichever is picked, every
system with a different natural level inflates or hides. This is the state the
record prevents rather than one it improves on.

**Let each system use its own level and say nothing.** Rejected as the current
state. It works while there is one emitter and stops the moment two disagree,
with no vocabulary to describe what happened.

**Rank perspectives, with a root.** Rejected. It reintroduces the global answer
through the back door, and the ranking would have to be maintained by somebody
who understands every system at once.

**Derive `part-of` from name similarity or shared branches.** Rejected, and it
is the tempting shortcut. Composition is a claim somebody makes — the
composition record's clause 5 — and a derived hierarchy is a hierarchy nobody
agreed to.

## Revision triggers

- A perspective that has to be split to be useful, which would mean the unit is
  wrong rather than the level.
- Two perspectives that are always in one-to-one correspondence, which would
  mean they are one perspective with two names and `same-as` is the better
  tool.
- A view spanning perspectives that people read as a single total anyway, which
  would mean the field is not visible enough at the place it matters.

## Amendments

*(none)*
