# QM-XXXX — The Read Document Governs

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-14 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `governance-finds-the-reader` — governance finds the reader, not the reverse; `decisions-are-documented` — decisions are documented or they didn't happen |
| **Restated in** | `AGENTS.md` item 16 |

## Context

This corpus answers *which document wins when two disagree*. `README.md`'s
"Namespaces and precedence" says org records bind every project and a project
record may tighten one, never relax it. That rule is sound and not enough,
because it answers a question a reader only asks once they have noticed the
disagreement.

The question it does not answer is *which document a reader reads*. Those have
different answers, and the gap between them is where a corpus can be entirely
correct and still govern wrongly.

An entry point and a record can disagree at the same commit with neither wrong
in isolation. A record can state that `main` and a pull request assert nothing
and that the human gate is the version tag, while the entry point describes the
pull request as opened "for human review" and places the manual-testing clause
the record owns at a gate the record says asserts nothing. A reader who builds
a model of the organisation from the entry point then reasons from the summary,
with the record in the same tree, read, and quotable on request. Nothing is
hidden and nothing is ambiguous in isolation.

The asymmetry that makes this the default rather than an accident: an entry
point is read first, read fully, and read by every session, while a record is
read when something points at it. A restatement in an entry point is therefore
not a copy of the decision. In practice it *is* the decision, and the record
becomes a description of what the organisation would have decided if anyone had
reached it.

This is the failure mode `governance-finds-the-reader` names, arriving from inside. Governance found the
reader; what it handed them was a second copy.

## Decision

1. **Precedence and readership are separate properties, and a rule needs
   both.** A decision that wins on precedence and loses on readership does not
   govern. Where the two are in tension, the fix is to the document that is
   read, never to the reader.

2. **An entry point cites a decision; it does not silently restate one.** The
   entry points are `AGENTS.md` and its seed copy, `README.md`, `PRINCIPLES.md`,
   and every page under `handbook/`. Where one states a rule that a record owns,
   it names the record's path in the same passage, so a reader who stops at the
   entry point has at least been told that a fuller statement exists and where.

3. **Restating is permitted, and it costs a declaration.** An entry point must
   brief a session that has no other context, and a page of bare citations does
   not do that. So a record carries a **`Restated in`** row naming every
   document that summarizes it, and each of those documents names the record.
   A summary that exists in only one direction is a defect in the corpus.

4. **Where a restatement and its record disagree, the record is what the
   organisation decided.** The restatement is repaired. Drift in an entry point
   is not evidence that a record has gone stale; a record changes by amendment
   and by nothing else.

5. **A wrong model built from correct documents is a finding about the corpus.**
   When a reader — human or session — reports a belief that contradicts a
   record, the routing that produced the belief is examined before the reader
   is. The report is recorded as a defect in the corpus's own reachability,
   because that is what it is evidence of.

6. **Enforcement.** `ci/check_restatements.py` reads each record's
   `Restated in` row and verifies that every named document cites that record's
   path, then reads the entry points for citations of a record path and verifies
   that the record names the document back. It fails on either half missing.
   **What it cannot do, and the limit is the point:** it cannot detect that a
   restatement and its record say different things. It makes the pair findable
   and forces the corpus to know where its copies are. A green result asserts
   that the pairs are declared, and asserts nothing about whether they agree.

## Consequences

- Entry points get shorter. A restatement nobody will declare is a restatement
  nobody needed, and the declaration is cheap enough that the ones which survive
  are the ones somebody wanted.
- The reader is told where the fuller statement is, at the point where they
  would otherwise stop. That is the whole mechanism: it does not make anyone
  read the record, it removes the state of not knowing one exists.
- Cost accepted: a record acquires a maintenance obligation — it has to know who
  quotes it. That obligation is the deliverable. A decision whose copies are
  untracked has an unknown number of versions in circulation, which is the
  condition this record addresses.
- Cost accepted: the check is link integrity and will read as stronger than it
  is. Two declared documents can contradict each other and pass. The tool's
  output says so on every run, because a check that overstates its coverage
  misleads the reader who trusts it.
- The failure this addresses is silent by construction. Neither document looks
  wrong on its own, no gate goes red, and the reader who acts on the entry point
  has behaved correctly by everything visible to them. Nothing but the pairing
  makes it detectable.

## Alternatives considered

1. **Ban restatement outright** — rejected. `AGENTS.md` has to brief a session
   with no other briefing, which is its stated purpose, and a file of bare
   citations fails that reader on their first minute.
2. **Rely on the precedence rule already in `README.md`** — rejected. It is
   clearly written and does not prevent this. Precedence resolves
   a conflict a reader has already noticed; this failure consists of not
   noticing.
3. **Generate entry points from records** — rejected. It inverts the audience:
   entry points are ordered by what a session needs first, records by decision,
   and a generated ordering serves neither. It would also make the entry point
   unable to say anything a record does not.
4. **Write it as a session-discipline clause** — rejected. Clauses without a
   mechanism do not change session behaviour, and a clause read in full is
   still broken; `perspectives/2026-08-12-nineteen-reversals-and-what-a-clause-cannot-fix.md`
   and `perspectives/2026-08-13-thirteen-breaks-and-the-five-that-became-yours.md`
   hold the evidence. This failure is also not one a careful reader catches,
   since being careful about the document in front of you is exactly what
   produces it.

## Revision triggers

- A restatement and its record are found to disagree while the declaration was
  present — the known blind spot in §6 has cost something, and semantic
  comparison becomes worth building.
- `Restated in` rows go stale across two propagations, which would mean the
  obligation is not being met and needs a mechanism rather than a rule.
- Entry points stop being read first — by a change in tooling, or by sessions
  arriving through a different door — since the routing assumption in the
  Context is what this record rests on.
- The declaration count grows past the point where a reader can hold it, which
  would indicate the entry points are carrying decisions that belong in records.

## Amendments

*None.*
