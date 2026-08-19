# QM-XXXX — Few Integers In Durable Text

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-18 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P6 — decisions are documented or they didn't happen; P8 — systems over heroics |
| **Restated in** | `AGENTS.md` |

## Context

A number written into prose is a claim with an expiry date, and prose does not
carry the date. A record, a pull request body, a handbook page and a module
docstring are all read long after they are written, by someone who has no way
to tell which of their figures still hold.

The counts go stale on their own. A test total changes when a test is added.
A repository count changes when one is synced. A star total changes because
somebody else did something. None of these edits is about the document, so
nobody thinks to revisit it, and the document keeps asserting the old figure
in a confident voice.

What follows is worse than the staleness. A reader who spots one wrong number
must now check every number, because the document has given no way to tell
which were load-bearing and which were incidental. So a page whose argument is
entirely sound gets audited line by line, and the author spends the session
correcting arithmetic rather than advancing the work. This has happened here
repeatedly, in a single afternoon: a pull request body opened with two counts
that were both wrong before it was merged, and neither mattered to anything
the change did.

The figures are not the problem. **Undated figures embedded in text that
outlives them** are the problem, and the fix is not to check them more often.

## Decision

**Durable text carries as few integers as it can while remaining true.**

Durable text is anything meant to be read later: records, handbook pages,
`AGENTS.md`, module and function docstrings, pull request bodies, and the
notes a generated view prints beside its own tables.

Three rules, in order of how often they apply.

1. **Prefer the relation to the count.** "Every synced repository" survives a
   sync; "113 repositories" does not. "The suite passes" survives a new test;
   "466 passed" does not. Where the sentence is about a property, say the
   property.

2. **Where a figure is the point, name where it came from and when.** A
   measured result — a benchmark, a survey of a corpus, a defect count in a
   retrospective — is worth stating precisely, and it stays true if the reader
   can see what produced it. Give the command and the commit, or the date. A
   figure with its provenance is evidence; the same figure alone is folklore.

3. **Never restate a figure a generated artifact already holds.** The status
   documents at the root, and the views built from them, carry their own
   numbers and their own age. A page that copies one has created a second copy
   that nothing updates, and readership will find the copy first.

**A verification section is the one place a bare count belongs**, because its
whole subject is one run at one commit: the commit is named, and the reader
knows the figure describes that run and not the present.

## Consequences

Pull request bodies get shorter and stop needing amendment. A reviewer reading
a record a year later can trust its sentences without auditing its arithmetic.
Retrospectives keep their counts, which is correct — a retrospective is about a
period that has ended, and its numbers are findings rather than status.

The cost is real: some sentences are less vivid. "Most of the dashboard is
still drawn behind the ring" is weaker than a percentage, and a reader who
wants the percentage must run the test that measures it. That is the trade,
and it is worth taking, because the vivid version is the one that will be
wrong.

This applies to text, not to code. An assertion, a constant and a fixture are
executable: when they go stale the suite says so, which is exactly the property
prose lacks.

## Alternatives

**Check every number before every commit.** This is the current practice and it
is what produced the problem. It scales with the number of figures written,
which is the quantity this record reduces instead.

**Date every figure inline.** Honest, and unreadable at density. Rule 2 keeps
it for the cases where the figure is the subject and drops it elsewhere.

**Generate the prose.** Correct for status documents, which is why they exist
and why rule 3 points at them. It is not available for a record's argument or a
pull request's reasoning, which is where most stale figures live.
