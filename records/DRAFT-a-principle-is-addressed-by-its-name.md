# QM-XXXX — A Principle Is Addressed by Its Name

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-29 |
| **Pends on** | §5 — whether an adopting project's own records are swept during propagation or left to each project. Every project that cites the charter addresses it the old way today, and which of the two happens is an organisation decision rather than a drafting one. |
| **Principle** | `decisions-are-documented` — decisions are documented or they didn't happen; `a-check-is-evidence-after-it-fails` — a check is evidence only after it has failed |
| **Restated in** | Nothing. |

## Context

The charter addressed its principles by position. A heading carried a letter
and a number, edges between principles named that number, and the rest of the
corpus followed: records, handbook pages, generated documents, docstrings and
test fixtures all pointed at a position in one file.

A position is a claim about where a thing sits, and it is a claim that
something other than the reference can change. Insert a principle anywhere but
the end and every reference below it addresses a different principle than it
did before. Reorder two and both sets of references swap silently.

**The failure mode is the one nothing downstream can detect.** A stale
reference to a position is still well-formed. It resolves — to the wrong
principle. There is no dangling link to find, no broken anchor, no missing
target: the corpus stays internally consistent and says something else. Every
other addressing failure in this repository announces itself by failing to
resolve, and this one announces nothing.

This is the same family as two rules the corpus already holds.
`records/DRAFT-few-integers-in-durable-text.md` says a number in durable prose
is a claim with an expiry date the prose does not carry, and a principle's
number is exactly that. `ci/check_restatements.py` already warns about the
neighbouring case in its own message — that a pointer at a numbered item goes
wrong when an item is inserted above it — so the hazard was known one layer
down and unaddressed one layer up.

Nothing had gone wrong yet. Principles had only ever been appended, so no
reference had been reaimed. That is a property of the edit history rather than
of the design, and it is not a property anybody had decided to preserve.

## Decision

**A principle is addressed by its name. Nothing in a binding document
addresses one by its position.**

### §1 — The name is declared in the heading, and the title follows it

A heading carries the name, then the human-readable title. The name is a
stable identifier; the title is a gloss on it and may be improved without
moving anything, which is the property a name derived from the title would not
have.

### §2 — Machine-read lines carry the name

The charter's edge declarations name the principle at the other end. They read
as sentences now — `rests-on show-it-by-running-it` says what it means, where
the positional form needed a lookup to say anything at all. That readability is
a side effect and not the argument.

### §3 — Prose carries the name too, in backticks

The same identifier, spelled the same way, in a record, a handbook page, a
docstring or a comment. One address per principle, per
`records/DRAFT-a-route-is-an-address.md`.

### §4 — Two directories keep what their authors wrote

`perspectives/` is dated, attributed, non-binding opinion. A retrospective
records what somebody wrote on a day, and rewriting one to match a later
renaming would falsify the thing its value rests on.
`handbook/handoffs/` is transient by its own definition and is deleted when
the work lands.

Both are excluded from the guard in §5, and the guard says so on every run.
That means positional references survive in this repository, and a green result
is not a claim that none exist anywhere.

### §5 — The guard, and what it costs to step around

`ci/check_principle_edges.py` refuses a positional reference in a binding
document. A line that names the old form in order to forbid it annotates
itself with a stated reason, and the count of exemptions is printed on every
run — the same shape and the same price as the drafting lint's.

The check was watched failing on the case it exists for, on a fixture and on
this repository, before it was trusted.

## Consequences

**A rename now breaks references visibly instead of reaiming them quietly.**
That is the whole trade: the positional form never dangled and was never right
either. A name that changes leaves a reference that resolves to nothing, and
nothing is a state a reader and a check can both see.

**Adopting projects address the charter the old way until they are swept.**
Their references are prose pointing into a document they vendor, so they do not
break; they go stale in the way this record describes. Which repository fixes
them, and when, is the `Pends on` above.

**The charter's own text got shorter to read and longer on the page.** A name
is more characters than a number and fewer lookups. Anyone measuring the
mandatory reading budget in lines should expect it to move the wrong way and be
worth it.

**One more identifier vocabulary to keep unique.** Two principles cannot share
a name, where two could not share a number either — the constraint moved rather
than appeared, and the guard reads both ends of every edge.

## Alternatives considered

**Keep the position and add the name as an alias.** Rejected: two addresses for
one thing, and the shorter one stays the one people type. It would leave the
silent-reaiming failure exactly where it was while adding the appearance of
having fixed it.

**Derive the name from the title automatically.** Rejected. It removes a thing
to keep in sync and replaces it with a worse coupling: improving the wording of
a title would then move every reference to that principle. A declared name is
edited deliberately, which is the point.

**Sweep `perspectives/` as well, for consistency.** Rejected under §4. A dated
opinion that has been edited to agree with a later decision is no longer
evidence of what anybody thought, and the corpus keeps retrospectives for
exactly that evidence.

**Leave it, since nothing has gone wrong.** This is the argument the record
answers. Nothing had gone wrong because principles had only been appended, and
the first insertion in the middle would have produced a corpus that was
confidently and undetectably wrong about what it stands on.

## Revision triggers

- A principle renamed, and the number of references left dangling. That is the
  cost of this design landing where it should, and it is worth counting once.
- The guard's exemption list growing past the documents that name the old form
  in order to refuse it. Exemptions used as the ordinary path mean the rule is
  wrong or the annotation is too cheap.
- An adopting project's records being swept, which closes the `Pends on` and
  makes §4's exclusion list the only place positional references remain.
- Two principles proposed with names close enough to be confused. A name
  collision is caught; a near-collision is not, and that is a reading.

## Amendments

*(none)*
