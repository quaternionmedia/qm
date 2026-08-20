# QM-XXXX — Deltas Compose, and a Tangle Is a Fact

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-20 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P6 — decisions are documented or they didn't happen; P8 — systems over heroics |
| **Restated in** | `plans/qmpm-standardisations.md` §1 |

## Context

A delta is a unit of work with a name, a lifecycle and an audit trail. That was
enough while a delta meant one branch or one pull request. It stopped being
enough as soon as work started arriving from places that are not repositories:
a conversation that produced three decisions and one of them spans two
projects; a branch whose reason lives in a thread; a question waiting on a
person that blocks two unrelated strands at once.

The shapes that turn up are not a hierarchy. A tree would be convenient and it
is the wrong model: work in this organisation crosses. Two efforts touch at one
point, one has to go first there, and neither contains the other — that is a
crossing, and a tree cannot say it. The same strand shows up under two
addresses because two systems each named it. A strand splits and both halves
keep the history.

**The vocabulary for that already exists in mathematics**, and using it is not
decoration. Strands, crossings and the fact that a tangle is a property of the
arrangement rather than a mistake in it — those are the three ideas this record
needs, and each has a consequence a project-management tool usually gets wrong.

The one that matters most: **most tools refuse a cycle.** `a` blocks `b` blocks
`a` is rejected as invalid input. Real work produces those constantly, and what
actually happens is that somebody deletes whichever relation the tool complained
about — so the tool is now consistent and the record is now false. The
organisation has lost the fact that the work is genuinely knotted, which was
the most useful thing anybody knew about it.

This corpus has already taken the same position once, in a different register:
`records/DRAFT-a-disagreement-is-a-delta.md` refuses to resolve two views by
fiat, because the losing value is discarded exactly when somebody would want to
see it. A refused cycle is that failure again.

## Decision

**Deltas compose, by address, through a closed set of relations. A cycle is
reported and never broken.**

1. **A relation joins two addresses, not two rows.** Both sides are
   `<owner>/<repo>/delta/<id>`, so a relation crosses repositories, threads and
   systems by construction. A relation naming something this side has never
   seen is kept: an address denotes without existing, which the grammar is
   explicit about, and the row it names may arrive later.

2. **The vocabulary is closed.** Five relations, each with a test somebody can
   apply:

   | relation | holds when | inverse |
   |---|---|---|
   | `part-of` | closing the whole requires closing this | `contains` |
   | `same-as` | two addresses denote one strand | itself |
   | `blocks` | this must close before that can start | `blocked-by` |
   | `crosses` | both must happen, they interact at one point, and neither contains the other | itself |
   | `derived-from` | this strand came out of that one and both continue | — |

   A sixth relation is a change to this record. A free string would let a typo
   become a category, which is the substitution
   `records/DRAFT-attention-is-a-claim-activity-is-measured.md` §1 already
   refuses for `attention`.

3. **`crosses` is not weak `blocks`, and the difference is the point.** `blocks`
   is an ordering over whole strands. `crosses` is an ordering *at one place*,
   with the rest of both strands independent. Recording a crossing as a block
   over-constrains the schedule and is how a board comes to say that nothing can
   start.

4. **`same-as` keeps both addresses.** Neither is retired, neither is rewritten
   to point at the other. Two systems each named one strand and both names are
   in documents that already exist; picking a winner breaks whichever links did
   not win. Resolution is a reader's operation, not a write.

5. **A relation is a claim, and it says who made it.** Composition is never
   inferred from a shared branch, a shared word, or a shared file. A detector
   may propose one; proposing is not asserting, and a proposed relation is
   visible as proposed.

6. **Nothing rolls up.** A container is not complete because its parts are, and
   its phase is not computed from theirs. Closing the whole is somebody
   deciding the whole is closed — the same act that closes any other delta, and
   for the same reason `complete` is a human's everywhere else in this corpus.

7. **A cycle is a finding, not an error.** Relations may form one. The system
   reports every cycle it can see, names the relations in it, and changes
   nothing. **A tangle is a fact about the work.** Refusing to store it does not
   untangle the work; it deletes the only record that the work is tangled, and
   the deletion is done by whoever was least equipped to judge — the person
   staring at a validation error.

8. **Reachability is bounded and says so.** "What is this made of" walks
   `part-of` and stops at a stated depth, reporting that it stopped. An
   unbounded walk over a graph that is allowed to contain cycles is a hang, and
   a hang in a dashboard reads as a broken tool rather than as deep work.

## Consequences

**A board can show work that is not a tree**, which is most of it. It can also
show a knot nobody had noticed, and that is the payoff — a cycle between three
strands across two repositories is a real finding and nothing before this could
express it.

**Cycles will appear, and some will be mistakes.** Distinguishing a mistake from
a genuine tangle is a person's job, and it is a better job than the one the
validation error was giving them.

**Cross-repository relations will dangle.** An address whose delta this side has
never ingested is normal and stays. It also means a relation count is not a
measure of anything — the corpus is used to that from `governance-status.yaml`.

**`same-as` makes duplicate detection possible and does not do it.** Two
detectors proposing the same strand under two addresses is the ordinary case,
and this makes it *sayable*. Somebody still has to say it.

**Six clauses are cheap and clause 7 is not.** Storing tangles means every
reader has to be written for a graph with cycles. That cost is real and it is
paid once, in the traversal, rather than continuously by people editing their
records to satisfy a checker.

## Alternatives considered

**A tree: every delta has at most one parent.** Rejected. It is the model that
fits a plan and not the work, and the failure is silent — a crossing gets
recorded as containment, and the board asserts a hierarchy nobody agreed to.

**A free-form tag between deltas.** Rejected for the reason clause 2 gives.
It is also the state today: `DeltaLink.link_type` is a free string, which is
right for pointing at an issue or a document and wrong for a relation whose
meaning has to be the same in two repositories.

**Refuse cycles, as every tracker does.** Rejected, and it is the load-bearing
rejection. It trades a true record for a consistent one, and it does the trade
at the moment somebody is least able to weigh it.

**Resolve `same-as` by merging into one row.** Rejected as lossy in the way this
corpus keeps refusing: every document already citing the losing address now
cites nothing.

**Compute the container's phase from its parts.** Rejected. It is the single
most requested convenience in a tool like this and the first place it will lie:
a container whose parts are all `complete` is not finished until somebody says
the thing it was for is done.

## Revision triggers

- A relation people keep expressing as a `crosses` with a note, which would mean
  the vocabulary is one short.
- Cycles that are always mistakes in practice, which would mean clause 7 is
  costing more than the record it preserves.
- A traversal depth that is routinely hit, which would mean the bound in clause
  8 is wrong or that `part-of` is being used where `crosses` belongs.
- Anybody needing a delta that belongs to no repository, which the address
  grammar cannot currently express and which `plans/qmpm-standardisations.md`
  §1 already lists as open.

## Amendments

*(none)*
