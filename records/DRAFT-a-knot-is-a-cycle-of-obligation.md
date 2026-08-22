# QM-XXXX — A Knot Is a Cycle of Obligation, Not a Cycle in the Graph

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-21 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P15 — a loop is not a knot; P6 — decisions are documented or they didn't happen |
| **Restated in** | `PRINCIPLES.md` P15 |

## Context

`records/DRAFT-deltas-compose.md` settled that a cycle is reported and never
broken: refusing to store `a blocks b blocks a` makes the tool consistent and
the record false, and the deletion gets made by whoever was least equipped to
judge it.

That left a question nobody had needed to answer: **which cycles are worth
reporting?** The answer looked like "all of them" until it was measured.

The organisation's relation set was computed from real work — a dependency
sweep across twenty-four repositories, and two hundred and thirty-seven
archived conversations placed against the projects they discuss. 169 relations:
49 `part-of`, 120 `crosses`.

Searching the directed relations found **zero** cycles. The obvious refinement
was to walk the symmetric ones too — `crosses` is symmetric, and `a crosses b
crosses c crosses a` looks like a finding. Doing that found **42 cycles, and
every one had the same shape**:

    thread -> project -> thread -> project -> ...

Two conversations that touched the same repository. Forty-two of those, and not
one of them is anything a person would act on. The refinement produced noise at
length four exactly as the original decision predicted it would at length two.

## The mathematics, and how far it actually carries

Knot theory studies embeddings of a circle in three-space, considered up to
**ambient isotopy**: continuous deformation that does not cut the strand. Its
central fact is the one that matters here — *every* embedding is a closed loop,
and closure is therefore not what distinguishes a knot from a piece of string
lying in a circle. The **unknot** is a genuine loop that can be deformed to a
plain circle. A knot is a loop that cannot, and no amount of rearranging will do
it; the only way out is to cut.

The mapping to a relation graph is exact in the part that matters and should not
be pushed past it:

| knot theory | here |
|---|---|
| a closed curve | a cycle in the relation graph |
| ambient isotopy — deform, never cut | reorder the work, never delete a relation |
| the unknot | a cycle that still admits a working order |
| a knot | a cycle with no valid order; something must be cut or decided |
| cutting the strand | deleting a relation somebody stated |

**This mapping is deliberate, and it is organisational practice rather than
decoration.** Finding the mathematical structure that a layer of the stack
actually has — and then building that layer to match it — is a stated goal here,
measured rather than asserted. A layer whose structure is named can be reasoned
about with everything already known about that structure; a layer described only
in its own vocabulary can be reasoned about only by the people who wrote it.

So the question is never "is this a nice metaphor". It is **what has this
mapping earned, and what has it not yet**.

*What is earned here.* Closure is cheap and unknottedness is the test. That is
not an illustration of the decision below — it is the decision, and it was
arrived at by measurement: forty-two closed loops, none of them knots.

*What is not yet earned.* There is no invariant. Nothing here tells two knots
apart — no crossing number, no polynomial — because a relation graph is not
embedded in three-space and its cycles carry no over- and under-crossings to
count. **That is a gap in the mapping rather than a limit on it**, and it names
real work: a knot invariant for obligation graphs would let two tangles be
compared, which is the question that arrives the moment there is more than one.

*Where the mapping is looked for next.* Ordering is the obvious one — a knot
that admits no total order is a cycle in a dependency relation, and the theory
of partial orders is better developed for scheduling than knot theory is. It may
turn out that obligation graphs are a poset question wearing a knot's clothes.
Establishing that would be a better outcome than defending the analogy.

## Decision

**A cycle is a knot when it carries obligation all the way round.** Report those.
A cycle whose edges impose no order is a loop, and reporting it buries the knots
in noise.

**Obligation is a property of the relation, not of the shape.** `blocks` says
one thing must close before another starts. `part-of` says closing the whole
requires closing the share. Both order the work, and a ring of them has no first
step — that is a knot, and untying it means somebody chooses.

`crosses` and `same-as` order nothing. `crosses` says two pieces of work
interact and neither contains the other; `same-as` says two addresses are one
strand. A ring of either can be scheduled in any order at all, which is exactly
what it means to be the unknot: it looks like a loop and it constrains nothing.

**So the tangle finder searches the directed relations**, and every cycle it
reports is one a person has to decide about.

**And a loop is still a fact.** Not reporting it as a knot is not the same as
refusing to store it. The two conversations that both touched one repository are
genuinely related, the relation stays recorded, and something else may want it —
the finding is that it is not a scheduling problem, not that it is noise in the
record.

## The practice this is an instance of

Mathematical structure is sought per layer, and the discipline is that a claimed
mapping is measured before it is relied on. Two other instances stand today, and
they are worth naming because they are unequal in how much they have earned:

- **The relation vocabulary as a closed algebra.** Five relations, each with a
  declared inverse, two of them symmetric, and `derived-from` deliberately
  without an inverse. That is a structure with rules, and the rules are checked:
  `check_relation` refuses a sixth, and the inverse table is read rather than
  restated. This one is earned.

- **The service ports as constants — π, φ, e.** These were chosen to be
  memorable, and one of the three has a reason beyond memorability: `e` is the
  base of natural growth and it went to the layer whose stated problem is
  complexity growing faster than anybody can hold. The other two are mnemonics.
  Saying so is the point: a mapping that is decorative should be recorded as
  decorative, or the practice degrades into naming things after mathematics and
  calling it structure.

## The mechanism

`ci/mathematics-registry.yaml` is the list, and `ci/check_mathematics.py` is
what keeps it honest. Five mappings today: two earned, one decorative and
labelled so, two aspirational.

Every entry states what it **decides** — what the mapping settles that taste
would otherwise settle — what **measured** it, and what it has **not earned**.
That last field is the one that matters. An entry with nothing unearned is
either a finished mapping, which is rare enough to deserve its own record, or
somebody who stopped looking. Requiring it is what makes this a practice that
evolves rather than one that congratulates itself.

The checker knows no mathematics and is not meant to. It asks whether a claim is
*shaped* so a person can check it: an `earned` mapping that names no measurement
is refused, a `decorative` one claiming to decide something is refused, and an
`aspirational` one that names a measurement is refused because a measured
mapping has either been earned or has failed.

**A state moves in both directions.** An earned mapping whose measurement stops
holding is not still earned because it once was. Re-integration is the point:
what a layer is found to be should change how the layer is built, and a
structure that stops fitting is demoted rather than defended.

## Consequences

- The tangle finder is quiet on this organisation's current relations, and the
  quiet is meaningful rather than a gap. Zero knots in 169 relations says the
  work has no circular obligations today.
- A relation added to the closed vocabulary must declare whether it orders. That
  is a new question for the next relation somebody proposes, and it is a better
  question than "is it symmetric" — symmetry is a hint and obligation is the
  test.
- The 42 loops are computable and are not reported by default. If somebody
  later wants "which conversations share a repository", that is a different
  query with a different name, and it should not arrive dressed as a tangle.

## Alternatives considered

**Report every cycle and let a reader filter.** Rejected on the measurement:
forty-two to zero is not a ratio a reader filters, it is a ratio that trains
them to stop looking. `PRINCIPLES.md` P13 is the same failure in a different
place — a system that interrupts constantly gets its interruptions ignored.

**Report symmetric cycles above some length.** This was the proposal that got
tested. Length is not the distinction: the four-node alternating ring is as
uninformative as the two-node one, and a six-node one would be too.

**Drop symmetric relations from the vocabulary.** Rejected outright. `crosses`
is how the pair's seam is described and `same-as` is how two names for one
strand are reconciled. They carry real meaning; they just do not carry order.

## Verification

At the commit that proposed this record, against the organisation's real
relations:

- 169 relations computed from live data — 49 `part-of`, 120 `crosses` — from
  `dossier.sweep` and `qmcp.threads.consolidate`.
- `dossier.composition.tangles` reports **0**.
- Walking symmetric relations both ways and ignoring two-node cycles reports
  **42**, all of the form `thread -> project -> thread -> project`. That run is
  what this record is written from.
- `dossier/tests/core/test_composition.py` pins both directions: a ring of `crosses` is
  not a tangle, a ring of `blocks` is.
