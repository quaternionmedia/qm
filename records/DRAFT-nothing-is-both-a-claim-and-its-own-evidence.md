# QM-XXXX — Nothing Is Both a Claim and Its Own Evidence

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-29 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `decisions-are-documented` — decisions are documented or they didn't happen; `systems-over-heroics` — systems over heroics |
| **Restated in** | Nothing. |
| **Unifies** | `records/DRAFT-attention-is-a-claim-activity-is-measured.md`; `records/DRAFT-version-tags-are-claims.md`; `records/DRAFT-project-phase-ladder.md`; `records/DRAFT-few-integers-in-durable-text.md`; `records/DRAFT-a-capability-has-four-phases.md`; `records/DRAFT-a-family-is-bordered-by-what-it-drives.md` |

## Context

Five records in this corpus decide the same thing about five different
subjects, and none of them names the other four.

`attention` is stated by a person and never inferred from a commit date.
A version tag is a claim and an untagged repository asserts nothing. A
project's `phase` carries a `phase_source` saying whether a human stated it or
the ladder's floor applied. A capability's rung is claimed, with the evidence
named separately per phase. An integer in durable prose is a claim with an
expiry date that the prose does not carry.

Each was written for its own subject, and each re-derives the same Context
before it can decide anything: that somebody asserting a thing and a tool
deriving it are different kinds of fact, that collapsing them lets the first
wear the authority of the second, and that a reader who cannot tell which they
are holding will act on the wrong one.

The cost of five derivations is not the words. It is that the rule is learned
five times and generalised zero times — so the sixth subject arrives, nothing
in the corpus says the rule applies to it, and it gets decided again from
scratch. That has already happened five times. `ci/workspace.yaml`'s header
carries the clearest statement of the rule anywhere in this repository —
*NOTHING HERE IS EVIDENCE* — and it is in a comment in a data file, reachable
only by someone already editing the roster.

There is a second cost, and it is the one that bites hardest. When the rule
lives only inside its instances, a *generator* can quietly violate it and no
record is being contradicted. `status/documents.yaml` reported mandatory reading
inside its budget while the charter every reader is told to read in full was
not in the measured set; the figure was a claim about the scaffolding wearing
the authority of a measurement, and it read as green on an alpha requirement.

## Decision

**Nothing is both a claim and its own evidence. A claim is asserted by a
person and carries who asserted it. A measurement is derived and carries how.
They are shown together, and neither is rewritten to match the other.**

### §1 — A claim carries its claimant

A stated fact records that it was stated, and by what. `phase_source` is the
worked instance: `stated` and `scaffolded` are the same value with different
provenance, and a reader who cannot see which is holding an opinion.

Absence is not a value. Where nothing has been asserted the field is
*unstated*, never the reassuring default — a generator that filled it in would
grow the corpus assertions nobody made.

### §2 — A measurement carries its method and its moment

A derived fact records what produced it and when. A figure without both is not
a measurement; it is a number, and a number in durable text is a claim.

### §3 — A measurement declares its scope, and the scope is checked

This is the clause the other four instances did not have, and its absence is
what let a measurement describe its own scaffolding rather than its subject.

A tool that measures a set says which set, in its output. Where the set is a
list in the tool rather than a property of the thing measured, something
compares the two and refuses when they diverge. A scope nobody checks turns
every figure downstream of it into a claim about the tool.

### §4 — The two are never reconciled into one number

Where a claim and a measurement of the same subject disagree, both are shown
and neither is corrected — `records/DRAFT-a-disagreement-is-a-delta.md`
governs what happens next. A view that resolves the disagreement silently
teaches its readers that the two agree.

## What this unifies

The five records stay where they are. Each holds the worked instance for its
own subject, and the instances are the value — the same reason
`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md` gave for
leaving three sections of the discipline record in place. What changes is that
they stop being five conventions and become one rule with five faces.

| Record | Reads as | Is really |
|---|---|---|
| attention is a claim | who is working on what | a claim, with the measured activity beside it |
| version tags are claims | how releases are numbered | the tag is the assertion; the branch it points at makes none |
| the project phase ladder | a roadmap | a claim with `phase_source` naming who made it |
| a capability has four phases | a maturity model | a rung claimed, with evidence named per phase |
| few integers in durable text | a style rule | a number in prose is a claim whose expiry the prose omits |
| a family is bordered by what it drives | a grouping of repositories | a claim about which repositories are one system, stated in the roster |

The sixth arrived while this record was being drafted: a repository family is a claim about which repositories are one working system, and it was written against this rule rather than deriving it again.

## Consequences

**A new field carrying a stated fact needs a provenance companion**, and that
is a real cost paid at design time rather than a free property. The corpus
already pays it in three places and has not regretted it.

**A generator gains an obligation it did not have.** §3 asks a measuring tool
to declare its scope and something to check that declaration. That is work,
and it is the clause with the least mileage here: one instance, added the day
this record was drafted.

**Nothing in the five records changes.** A reader who consults only an
instance is not misled by it — this record generalises them and contradicts
none, which is the property that makes unification safe and merging not.

**The rule is now falsifiable at the level it is stated.** A future decision
that treats an asserted value as evidence contradicts a record rather than
departing from a habit nobody wrote down.

## Alternatives considered

**Merge the five into one record and delete them.** Rejected, and it was the
first plan. Three of the five are restated in entry points or in a data file's
header, so merging rewrites those declarations; one carries a live `Pends on`
that the merged record would have to inherit and thereby weaken; and the
worked instances are what make the rule legible. Unification keeps every
instance readable on its own and adds the general statement once. The corpus
has done this before and it held.

**Leave the rule implicit and let the instances teach it.** This is the state
this record ends. It survived four instances and failed on the fifth, and it
failed silently: a generator measured its own scope and reported green against
a milestone requirement, contradicting nothing because nothing had been
written down to contradict.

**State it in `PRINCIPLES.md` as a new principle.** Rejected. The charter is
the corpus's longest single document and the one every reader is told to read
in full, so a clause added there is paid for by every session forever. A
record is reached by the reader who needs it. `decisions-are-documented` and `systems-over-heroics` already carry this
rule's weight at charter altitude.

**State it in `AGENTS.md`.** Rejected for the reason
`records/DRAFT-governance-arrives-as-a-mechanism.md` §4 gives about itself:
adding lines to the entry point to announce a rule about disciplined
measurement would be paid for by every reader, and this record is reachable
from the index by the one who needs it.

## Revision triggers

- A sixth subject that needs its own record anyway, because this one does not
  reach it. That would mean the rule stated here is narrower than it reads.
- A `Unifies` declaration that names a record which does not exist, or a
  unified record that grows a decision contradicting §1 to §4. Either means
  the unification is stale rather than the instances wrong.
- §3 acquiring a second and third instance, or acquiring none. One instance is
  a clause that has been executed once, and that is worth saying plainly.
- A measured scope and its declared scope diverging with nothing reporting it,
  which is the failure §3 exists to prevent and the one that produced this
  record.

## Amendments

*(none)*
