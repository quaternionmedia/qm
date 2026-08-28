# ADR-XXXX — What Apothecary's `v0.0.2` Asserts

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-28 |
| **Pends on** | rad's core-extraction decision. §3 requires replaying rad's conformance vectors against a platform-free core; `rad/adr/DRAFT-rad-adoption-and-scope.md` records that conflict as open — the core is a comment header inside a file that also calls `document`, so the import-boundary lint the contract requires cannot exist on either side — and `rad/adr/DRAFT-rad-core-extraction.md` is itself `Proposed`, pending a human decision on whether the single-file deliverable becomes a build output. Until that lands, §3 names a target this project cannot begin. |

## Context

The org's phase ladder settles the shape of this question and declines to answer
it. Its §1 makes `v0.0.1` one claim with one meaning in every project. Its §2
puts every rung above that in the project's own records, and says in terms that a
project which has not written the definition "has not got a `v0.0.2`; it has a
word". Its Consequences name this project as carrying exactly that gap. The
record is present at this project's governance pin and is byte-identical to the
copy on the org's `main`, so citing it here cites the same document a reader
upstream would open.

Where the word came from matters. The org roster carries `phase: v0.0.2` with
`phase_source: stated` and the note *named as a `v0.0.2` integration consumer* —
named, that is, by a neighbour. rad's release-milestones record names apothecary
and benchmark as the proving consumers of its integration standard and calls that
standard "the real deliverable of this milestone". That is rad's claim, about
rad's contract, and it binds rad. Under the ladder's §2 it is a statement of
intent about this project made by somebody else, which is the one thing §2 says a
rung may not be.

There is a second separation the record has to hold. The work in flight in this
repository is the picture path — a photograph read into flat shapes, each named
from a small vocabulary and placed in an ordinary arrangement. It is the larger
body of code here and it is not what the word `v0.0.2` was used for. Folding it
in because it is what is being built would make the rung mean *whatever this
project did next*, and a rung that means that cannot be compared with anything,
which is the failure the ladder exists to prevent.

## Decision

Apothecary's `v0.0.2` asserts that **this project is a host of rad's integration
standard, and that its own command surface is that standard's surface**. Four
clauses, each refutable on this project's default branch by somebody who did not
write it.

1. **One mutation path.** Every mutation of a scene routes through this project's
   intent endpoint. A control that changes the scene by any other route is a
   defect against this rung rather than a variation of it. This clause is what
   makes the others checkable: with one path, what the ring can express and what
   the program can do are the same set by construction rather than by inspection.

2. **The viewer has no controls of its own.** The meter is `apothecary census`,
   which reads the viewer's markup and refuses to give a number when it meets
   something it cannot classify. The claim is *nothing*, not *fewer* — a ring
   that leaves a handful of buttons behind has not replaced them. Run the census
   rather than quoting a figure from this page; it does not print nothing today.

3. **This project replays rad's conformance vectors in its own runner**, pinning
   the vector version it claims, and contributes at least one divergence back as
   a new vector before changing code to accommodate it. The runner is this
   project's. The standard is not, which is why this clause asserts something
   about apothecary and nothing about rad.

4. **`v0.0.2` asserts nothing about the picture path, nothing about storage, and
   nothing about any other project.** How well shapes are found, what "your own
   machine" means for anything derived from a photograph, and whether rad's
   standard also fits its other named consumer are three real questions with
   their own homes. None of them is evidence for or against this rung.

Ratifying this record does not confer the rung. Per the ladder's §4 and the
version-tags record, the claim and its evidence stay separate documents: this
record fixes what the claim would mean, and a human cutting the tag is what makes
it.

## Consequences

- The gap the ladder names for this project closes as a definition and reopens as
  a measured distance. None of §1–§3 is satisfied today, and §2 is the one that
  can say by how much.
- Every clause is refutable by a reader who did not write it, which is the
  property a roster marker reading `stated` cannot have however honest it is.
- §3 makes this project's rung depend on a deliverable another project owns. The
  cost is accepted and named rather than designed around. The alternative is a
  rung whose evidence this project can produce alone, which would not be the
  thing the word was used for.
- The interface work stops being optional. All but one of this project's named
  jobs is reached by nothing but typing, and neither §1 nor §2 can be satisfied
  while that holds.
- Nothing in the picture path counts toward this rung, including what is already
  built. That is a cost, it is accepted, and it is the whole point of §4.

## Alternatives considered

1. **Define `v0.0.2` as the picture path** — photographs into named pieces, at
   some stated accuracy. Rejected because the rung would then be defined by
   whatever this project happened to build next, and because accuracy measured on
   pictures this project drew itself is not evidence a reader can weigh. The
   picture path is worth a record; it is not worth this one.

2. **Define it as the picture path and the host integration together.** Rejected:
   two decisions in one rung, so neither half can be refused without refusing the
   other, and a rung nobody can fail half of is not a claim.

3. **Adopt rad's milestone definition by reference** — this project's `v0.0.2` is
   whatever rad's says it is. Rejected as the tidiest wrong answer. It puts this
   project's rung inside another project's document, where a change to that
   project's milestone silently changes what this one claims, and it inverts the
   ladder's §2 — the project defines its own rung, and a neighbour naming it is
   precisely what §2 says is not enough.

4. **Leave the rung undefined and let the roster's marker carry it.** Rejected
   because it is the state that produced this record. The marker is honest that a
   claim is a claim; it cannot say what the claim means.

## Revision triggers

- rad's core-extraction decision lands either way, which either unblocks §3 or
  establishes that this project cannot replay the vectors at all.
- rad's milestone record changes what its standard requires of a host, which
  changes what §3 can be conformed to.
- The census reaches nothing while §1 or §3 is unsatisfied, which would mean the
  surface was unified without the standard and this rung is metering the wrong
  thing.
- benchmark writes its own `v0.0.2` definition and it needs these same clauses,
  which is evidence under the ladder's own revision trigger that the rung is
  org-level after all.
- A human cuts a `v0.0.2` tag on this project, at which point this record's
  subject stops being a target and the version-tags record governs what the tag
  asserts.

## Amendments

*None.*
