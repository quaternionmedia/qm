# ADR-XXXX — What Apothecary's `v0.0.2` Asserts

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-28 |
| **Pends on** | rad's core-extraction decision. §5 requires replaying rad's conformance vectors against a platform-free core; `rad/adr/DRAFT-rad-adoption-and-scope.md` records that conflict as open — the core is a comment header inside a file that also calls `document`, so the import-boundary lint the contract requires cannot exist on either side — and `rad/adr/DRAFT-rad-core-extraction.md` is itself `Proposed`, pending a human decision on whether the single-file deliverable becomes a build output. Until that lands, §5 names a target this project cannot begin. |

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

What this project is building is one path: a photograph becomes flat shapes, the
shapes get names from a small vocabulary, the named pieces become an ordinary
arrangement, and a person walks that arrangement. The last step is the one the
neighbour named. Treating it as a rung of its own would put the rung's boundary
in the middle of a path a person experiences as continuous, and the boundary
would then have to be described — which is how one path acquires two accounts of
itself. This project has already paid that: the model half and the viewer half
had a page each, one of them produced by a command somebody had to remember, and
the remembered one was stale while every check stayed green.

So the rung is the path, and the evidence is the run.

## Decision

Apothecary's `v0.0.2` asserts that **one path runs end to end on one machine — a
photograph becomes named pieces, and those pieces are reached through rad's ring
rather than through controls of the viewer's own — and that a single
demonstration shows the whole of it.** Five clauses, each refutable on this
project's default branch by somebody who did not write it.

1. **One demonstration, and it is the evidence.** There is one walkthrough. It is
   written by the run that asserts it, the ordinary test command runs that run,
   and no part of the path is shown by a second page or reached by a command
   somebody has to remember. A behaviour that stops being true fails the run; a
   sentence that stops being true is rewritten by it. This clause is first
   because the other four are claims about a path, and this is what makes the
   path one thing rather than four.

2. **The demonstration is local, and says what it needs.** It draws its own
   photographs, reads them back, and drives a real browser against a real server
   on the machine it runs on. No network, no hosted service, no fetched model.
   The cost is that the demonstration needs a browser everywhere, and the page
   states that rather than degrading quietly on a machine without one.

3. **One mutation path.** Every mutation of a scene routes through this project's
   intent endpoint. A control that changes the scene by any other route is a
   defect against this rung rather than a variation of it. With one path, what
   the ring can express and what the program can do are the same set by
   construction rather than by inspection.

4. **The viewer has no controls of its own.** The meter is `apothecary census`,
   which reads the viewer's markup and refuses to give a number when it meets
   something it cannot classify. The claim is *nothing*, not *fewer* — a ring
   that leaves a handful of buttons behind has not replaced them. The
   demonstration prints what the census reports, so the distance to this clause
   is on the page rather than in anybody's memory of it.

5. **This project replays rad's conformance vectors in its own runner**, pinning
   the vector version it claims, and contributes at least one divergence back as
   a new vector before changing code to accommodate it. The runner is this
   project's. The standard is not, which is why this clause asserts something
   about apothecary and nothing about rad.

`v0.0.2` asserts nothing about how well shapes are found in photographs this
project did not draw, nothing about where anything is stored, and nothing about
any other project. Those are three real questions with their own homes, and none
of them is evidence for or against this rung.

Ratifying this record does not confer the rung. Per the ladder's §4 and the
version-tags record, the claim and its evidence stay separate documents: this
record fixes what the claim would mean, and a human cutting the tag is what makes
it.

## Consequences

- The gap the ladder names for this project closes as a definition and reopens as
  a measured distance. §1 and §2 hold today. §3, §4 and §5 do not, and §4 is the
  one that can say by how much.
- The demonstration becomes load-bearing rather than illustrative. Its run is
  what this rung is evidenced by, so a machine that cannot run it cannot check
  the claim — and the ordinary test command now needs a browser and starts its
  own server. That cost is accepted, and it is the price of the path having one
  account of itself.
- Every clause is refutable by a reader who did not write it, which is the
  property a roster marker reading `stated` cannot have however honest it is.
- §5 makes this project's rung depend on a deliverable another project owns. That
  cost is accepted and named rather than designed around. The alternative is a
  rung whose evidence this project can produce alone, which would not be the
  thing the word was used for.
- The interface work stops being optional. All but one of this project's named
  jobs is reached by nothing but typing, and neither §3 nor §4 can be satisfied
  while that holds.

## Alternatives considered

1. **Two rungs: the picture path, then the host integration.** Rejected, and it
   is the tempting one, because the two halves have different owners and
   different evidence. It loses on what it does to the demonstration: a rung
   boundary in the middle of one path is a boundary the pages have to describe,
   and this project has already had two pages describing one path with the
   remembered one going stale. The neighbour's dependency is real and is held in
   §5 as one clause rather than as a wall through the middle.

2. **Define `v0.0.2` as the picture path alone** — photographs into named pieces,
   at some stated accuracy. Rejected because accuracy measured on pictures this
   project drew itself is not evidence a reader can weigh, and because it would
   leave the word the roster carries meaning something nobody said it meant.

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

- rad's core-extraction decision lands either way, which either unblocks §5 or
  establishes that this project cannot replay the vectors at all.
- rad's milestone record changes what its standard requires of a host, which
  changes what §5 can be conformed to.
- The demonstration is split, or a second page describing any part of the path
  appears, which breaks §1 and means the rung has lost the thing it is evidenced
  by.
- The census reaches nothing while §3 or §5 is unsatisfied, which would mean the
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
