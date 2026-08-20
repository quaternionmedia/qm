# qmPM — standardisations to pick from

**Status: a stub, and deliberately a list.** Nothing here is decided. It exists
so downstream work has something to argue with instead of inventing a
vocabulary per repository, which is what happens otherwise and what
`ci/workspace.yaml`'s four comment headers already cost this organisation once.

**What qmPM is meant to be.** One way to say what work exists, what it is made
of, and what is waiting on whom — across repositories, threads, branches and
whatever else turns out to carry work. The delta is the unit; this page is the
list of things a standard around it would have to settle.

**How to use it.** Take one item, decide it, and write a record. An item that
gets decided leaves this page. An item nobody can decide yet stays, with the
reason. **A tick against an item on this page means nothing** — the decisions
live in `records/`.

---

## Already decided, and load-bearing for everything below

Not candidates. Listed so nobody re-opens them by accident.

| | |
|---|---|
| A unit of work is a **delta** | `records/DRAFT-a-disagreement-is-a-delta.md` |
| Every row has an **address**, `<owner>/<repo>/<kind>/<id>` | `docs/ref/addresses.md` |
| Two views disagreeing is **a delta, not an error** | same record; neither side wins |
| A **claim** and a **measurement** are separate documents | `records/DRAFT-project-phase-ladder.md` §4 |
| A count nobody took is **`unknown`**, never zero | `harness-status.json`'s reading block |
| A person is interrupted **only by a decision** | `PRINCIPLES.md` P13 |

## 1. Identity and composition

- ~~**Composition vocabulary.**~~ Decided:
  `records/DRAFT-deltas-compose.md` — five relations, closed, by address, and a
  cycle is reported rather than refused. This page restates it and the record
  is what the organisation decided.
- **Identity across a split.** One delta becomes two. Are they new, or is the
  original a container? Whichever, the old address must still resolve.
- **Identity across a merge.** Two strands turn out to be one thing. `same-as`
  keeps both addresses alive; a rename kills one. The corpus already refuses
  lossy resolution elsewhere.
- **Whether a delta may span owners.** `<owner>/<repo>/delta/<id>` is
  repo-scoped by construction. Work that genuinely belongs to no single
  repository needs either a global prefix (there are three already) or a home
  repository by convention.

## 2. Lifecycle

- **Is one lifecycle enough?** `brainstorm → planning → implementation → review
  → documentation → complete` fits code. It fits a conversation badly and a
  decision worse. Either the phases generalise or `delta_type` selects a
  lifecycle. **Narrowed** by
  `records/DRAFT-granularity-is-a-perspective.md`: a conversation's *turns* are
  not the subject, because they are steps in that perspective. What needs a
  lifecycle is what the conversation produced.
- **Who may advance a phase.** Today anything can. Detection opening at
  `brainstorm` is already a rule; the rest are not.
- **What `complete` asserts**, and whether a container is complete when its
  parts are. Automatic rollup is convenient and would be the first place this
  standard lies.
- **Reopening.** A delta that was complete and is not any more: a new delta, or
  the same one moved back? Rows exist either way, so this is about what history
  a reader can see.

## 3. Provenance

- **Where a delta came from**, as a field rather than prose: a person, a
  detector, a sync, a conversation. Related and decided:
  `records/DRAFT-no-unattended-spending.md` — anything that cost money to
  produce had a person behind it by construction, so provenance for that class
  is never "a schedule".
- **What produced a claim inside it.** The harness already links an invocation;
  the general form is unsettled.
- **Confidence, or its refusal.** A delta a detector guessed at and one a person
  wrote are not the same claim. Either that is a field or detectors do not
  create deltas past `brainstorm` — the second is cheaper and already the rule
  in one place.

## 4. What is waiting on whom

- **One queue or many.** The harness has `ask`; a review request and a
  ratification are the same shape. One vocabulary or three is undecided.
- **Answerability.** P13 says a notification owes a way to act. Standardising
  *what an answer looks like* is the mechanical half: an option from a declared
  set, free text, or a delta reference.
- **Expiry.** Every queue grows. What an unanswered question becomes after long
  enough is a policy nobody has written.

## 5. Time

- **Observation time versus event time.** The disagreement record names
  comparing each side's own observation timestamp as its failure mode. The
  standard should make that hard to do by accident.
- **Staleness budgets per kind.** The generated documents each carry one;
  deltas do not.
- **Ordering across systems** with no shared clock. Addresses are stable;
  timestamps are not comparable, and pretending otherwise is the usual bug.

## 6. Sizing, and what to refuse

- **No estimates, or estimates as claims.** If they exist they are claims and
  belong beside their evidence, like `phase`.
- **Priority as a declaration.** `high` today means whatever the emitter meant.
- ~~**What is not a delta.**~~ Decided:
  `records/DRAFT-granularity-is-a-perspective.md` — granularity is a property
  of the perspective, not of the thing, and every payload names the perspective
  it speaks from. A green check is still not work in any perspective; that is
  about whether it is work, not at what level.

## 7. Interop

- **Import without adoption.** Reading an issue tracker without becoming one.
  `dossier deltas from-prs` is the worked example.
- **Round-tripping.** If a delta leaves and comes back, what must survive.
- **Schema versioning at the seam.** The harness payload is at 2 and the delta
  payload at 1, and the rule for bumping either is convention rather than
  record.
- **Refusal over guessing**, as the standing default: an ingest that cannot
  place a row says so. Already how `deltas ingest` behaves; not yet stated as a
  standard.

## 8. Where this standard lives

- **In `qm`, adopted by reference**, like everything else here — or as its own
  repository with its own tag line.
- **Conformance vectors**, the way addresses and the harness payload have them.
  A standard without cases is prose, and this corpus has measured what prose
  achieves on its own.
- **Which project implements it first.** dossier owns the delta tables today,
  which makes it the reference implementation whether or not anybody says so.

## What this page is not

A roadmap, a backlog, or a claim that any of it is needed. Several items will
turn out to be decisions nobody has to make, and finding that out is cheaper
than building for them.
