# QM-XXXX — A Route Is an Address, and an Unavailable One Is Still Shown

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-20 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P13 — a person is interrupted only by a decision; P11 — governance finds the reader; P9 — minimal, legible deliverables |
| **Restated in** | `PRINCIPLES.md` P14 restates §5 only. §1–§4 are stated here and nowhere else |

## Context

`records/DRAFT-clis-are-for-machines-and-debugging.md` settled that a loop only
walkable by typing has not been built. It did not say what the built thing owes
a person, and the first serious attempt to document one produced the question
this record answers.

A control panel here carries a keyboard menu — nine cells laid out like a numpad,
opened with one key, every item one keystroke from the centre. Somebody asked for
an instruction sheet *indexed on the command numbers*, and named an example:
sync is `6.2`.

That request contains a design constraint most menus fail. `6.2` is only worth
writing down if it is stable, and only worth reading if it can be derived. Both
of those are properties of the *addressing scheme*, not of the documentation —
and the documentation is where their absence is discovered, always too late,
because by then the numbers are in somebody's notes.

The four sections below are what that turned out to require. The fifth is the
part that generalises past menus.

## Decision

### 1. A route is derived, not assigned

**The number of a command is the sequence of inputs that reaches it.** `6.2` is
not an identifier somebody allocated to sync; it is `6` for the second verb and
`2` for the third thing under it. A reader holding the number holds the
keystrokes, and a reader who pressed the keystrokes can state the number without
consulting anything.

The alternative — a stable identifier assigned per command — is what most
software does, and it costs a lookup on every use in both directions. The
lookup is the thing being removed. An addressing scheme that still needs a table
has not addressed anything; it has named things.

This is the same shape as the address grammar in
`plans/qmpm-standardisations.md`: `<owner>/<repo>/<kind>/<id>` is derived from
where a thing lives rather than allocated by a registry, for the same reason.

### 2. A generated index, or none

**A menu's documentation is computed from the menu.** Not checked against it,
not reviewed alongside it — computed, so the two cannot disagree.

A hand-written table of routes is a second copy of the menu, and the failure
mode of a second copy of a menu is specific and bad: a documented number that
opens something else. It is worse than a missing document, because a reader who
finds nothing looks; a reader who finds `6.2` presses it.

This is `P12 — show it by running it` applied to an interface rather than a
behaviour, and the mechanism is the one that record already names: the artifact
rides the ordinary test command, and is recorded rather than compared.

### 3. What a host cannot do is greyed, never removed

**An unavailable command keeps its cell, its number and its place.**

Removing it is the obvious implementation and it is wrong, for a reason that
<!-- adr-lint: allow "renumber is the literal subject here -- what happens to a menu's addresses when an item is dropped -- not this draft narrating its own history" -->
only shows up once §1 and §2 are in place: dropping an item renumbers every item
after it. The route is the address, so removing one command silently
*readdresses* the rest — and the same menu then has different numbers depending
on which host is running it and which features that host has finished. A menu
<!-- adr-lint: allow "renumber is the literal subject here -- what happens to a menu's addresses when an item is dropped -- not this draft narrating its own history" -->
that renumbers itself cannot be documented at all, which returns the
organisation to a page of ordered commands and the record that forbade them.

So the cell stays, and it is shown as unavailable. This also happens to be the
more honest interface: a person can see that the thing exists, that somebody
intends it, and that it is not ready — three facts that a missing cell replaces
with nothing.

**Unavailable means unavailable by every route.** A cell that refuses a digit
press and accepts an arrow key is not guarded; it is guarded against the route
whoever wrote it happened to think of. `records/DRAFT-decision-record-discipline.md`
§10 says a guard is not finished until somebody has tried to route around it,
and a menu is the case where the routes can be *enumerated* — so enumerate them
and close all of them. In the implementation that prompted this record there
were five, and the first pass closed three.

**A container is unavailable when everything it holds is.** Otherwise a person
spends inputs opening a level where nothing can be chosen, which is worse than
finding it closed: they have paid to be told nothing is there.

### 4. State survives losing colour

**Anything an interface says with colour it also says in characters.**

Greying out is a colour, and colour is the least reliable channel an interface
has: a high-contrast theme deliberately has no dimmer ink to grey with, a
sixteen-colour terminal approximates, and a reader may not see colour at all. A
state carried by colour alone becomes an item that looks ordinary and refuses to
be chosen — the interface lying, quietly, to exactly the readers with least
recourse.

This is not a new rule so much as the existing one held to. The menu already
drew its selection with a doubled border rather than a highlight, for this
reason, and then greyed items out with a colour anyway. The general form: when
an interface acquires a new state, the question is not *what colour* but *what
does this look like with no colour at all*.

### 5. A change that can only be typed schedules interface work

**When a person has to leave the interface to make a needed change, that is
recorded as work against the interface — not as the change being done.**

This is the trigger, and it is deliberately not a prohibition. Dropping to a
command line to make a change is fine and often correct: it is how something
gets fixed today. What is not fine is that the loop closes there. The typed
change is the *diagnosis*; the interface route is the fix, and nothing currently
converts one into the other.

So: **the act of doing something by typing that a person would reasonably expect
to do in the interface creates an item against that interface.** Named, in the
same place the organisation keeps its other open work, saying which workflow
needed it. `PRINCIPLES.md` P14 restates this and it is the section with teeth.

The measure is already defined — `records/DRAFT-clis-are-for-machines-and-debugging.md`
counts the steps a person must type to complete a named workflow. This says what
happens when that count goes up: it is not merely observed, it schedules the
work that brings it down.

**What this does not say.** That every CLI command needs a menu route. Most do
not: automation needs a command line, so does diagnosis, and a menu that grew a
cell for every flag would fail its own budget. The trigger is a *person* doing a
*needed change* they would reasonably expect the interface to carry. The
judgement of "reasonably" is a person's, and the item it creates is a proposal
rather than a commitment.

## Consequences

- An interface with a documented addressing scheme cannot drop items to tidy
  itself. It marks them, which is more work and is the cost of §1.
- The index cannot be written by hand. Any host adopting this owes a generator,
  and a host that cannot generate one does not get to publish numbers.
- Unfinished features become visible rather than invisible. This is intended and
  it is uncomfortable: the menu now shows how much is not done. The alternative
  is an interface that looks complete and is not, which is the thing a reader
  cannot check.
- §5 will generate items faster than they are closed, at first. That backlog is
  the measurement, not a failure of it.

## Alternatives considered

<!-- adr-lint: allow "renumber is the literal subject here -- what happens to a menu's addresses when an item is dropped -- not this draft narrating its own history" -->
**Assign stable identifiers, and let placement vary.** Solves renumbering
outright. Rejected because it reintroduces the lookup in both directions, which
is the entire cost §1 exists to remove — and because a stable id that does not
match the keys pressed is a third thing to keep in sync.

**Remove unavailable items and regenerate the index per host.** Internally
consistent, and it produces a document that is correct for exactly one
installation. Rejected: the numbers are shared between people running different
builds, which is the case the document exists for.

**Grey out with colour only, and treat the accessible rendering as a later
pass.** Rejected on evidence rather than principle: the theme that would have
broken first is the one already in the codebase for readers who need contrast,
so "later" would have shipped a menu that was wrong for precisely them.

**Make §5 a prohibition — no typed changes to things with interfaces.**
Rejected. It would make the honest diagnostic path a violation, and the
predictable result is people doing it and not saying so, which removes the
signal the section exists to collect.

## Verification

At the commit that proposed this record, in `quaternionmedia/dossier` on
`fix/refuse-a-count-nobody-took`:

- `uv run pytest tests/core/test_rad_index.py tests/core/test_rad_availability.py`
  — 33 passed. The first file asserts §1 and §2, the second §3.
- Five routes to a cell were enumerated and each closed: a digit press, an
  arrow step, a diagonal chord, a rotate, and a highlight left in place. Each
  guard was then mutated and observed to fail — the chord and the rotate had
  been missed by the first implementation and were found by writing the
  enumeration down.
- `dossier/docs/rad-commands.md` is generated and carries no figure that was typed: both
  thresholds in it are read from the constants that decide the behaviour.
