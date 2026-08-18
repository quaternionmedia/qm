# Precedence Lost to Readership

| | |
|---|---|
| **Date** | 2026-08-14 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | An assistant, which built the wrong model described here and then wrote the record against it |

---

## What happened

A session was asked to review the workspace and line up parallel work. It read
`AGENTS.md`, read the handbook, ran the gates, and reported that three pull
requests — `qm` #56, `dossier` #12, `qmcp` #21 — were green, mergeable, and
blocked on a human leaving draft. It framed the whole organisation around that:
a producer/consumer rate mismatch, the one-PR rule as the only backpressure,
the queue as the thing to manage.

The reviewer's correction was one line. Pull requests are review and audit into
`main`. Human review happens at tagged releases. Agents get `main` clean and
working; human-reviewed pull requests that assign tags drive releases.

`records/DRAFT-version-tags-are-claims.md` had said so since 2026-08-08. §4:
*"Everything untagged carries no release claim. `main`, a pull request, a
working branch, and a local build are drafts."* §2 puts human review and manual
testing at the tag. The record and the reviewer agreed. The session's reading
disagreed with both.

## Why the reading happened

`AGENTS.md` item 3 said a pull request is opened "for human review", that an
agent must never merge into `main`, and that "leaving draft is their decision
and follows their own testing." That last clause is the tag record's
manual-testing claim, relocated to a gate the tag record says asserts nothing.

Both documents were in the tree at the same commit. Neither was ambiguous on
its own. No gate went red, because no gate compares two documents.

The session had also read the tag record earlier in the same thread, and had a
note about the tag gate in its own memory. Neither helped. It is worth being
precise about that, because the comfortable reading is that the session was
careless, and the useful reading is that **being careful about the document in
front of you is exactly what produces this failure.** The entry point was read
first, read fully, and read completely correctly.

## The asymmetry

An entry point is read first, read fully, and read by everyone. A record is read
when something points at it.

So a restatement in an entry point is not a copy of a decision. In practice it
*is* the decision, and the record becomes a description of what the organisation
would have decided if anyone had reached it. Precedence — which document wins —
had the right answer throughout and never got asked the question.

This is what P11 names, arriving from inside. Governance found the reader. What
it handed them was a second copy.

## What was done

`records/DRAFT-the-read-document-governs.md`, and the reconciliation the
correction implied:

- `AGENTS.md` item 3 and its seed twin now say the pull request is an audit
  record, that the author merges it once the gates are green, that `main`
  asserts nothing, and that there are exactly two human gates — ratification and
  the tag. Both cite the tag record's path.
- `handbook/async-contract.md` §1 keeps its mechanism and loses its stated
  reason: it is a sequencing constraint, not a review-bandwidth one. §2 stops
  making draft the default, because draft was a holding pen for a queue that
  does not exist.
- Draft now means unfinished, which is what it means everywhere else.
- `ci/check_restatements.py` pairs a record's `Restated in` row against the
  documents that cite it, in both directions.

## What the check does not do, which is most of it

It cannot tell that a restatement and its record say different things. That is
reading, not matching. And it cannot find a restatement nobody declared —
`README.md`'s record index names every record and restates none of them, so a
check that failed on any mention would penalise the exact behaviour the record
asks for.

So the declaration is an author's act, and the check verifies the declarations
that exist rather than discovering the ones that do not. Building it surfaced
that limit late: the first version failed on every citation and reported 27
violations, most of which were the index doing its job. A tool that had shipped
in that state would have taught every future session that citing a record is
expensive.

## The part worth arguing with

Two clauses were added to entry points to fix a problem caused by entry points
carrying too much. That is not obviously the right direction, and the corpus has
evidence against it: two perspectives in the preceding week established that
clauses without a mechanism do not change session behaviour, and that every
clause broken in one measured session had been read in full by the session that
broke it.

The defence is that the new clause carries a check and the check is small. The
honest counter is that the check verifies bookkeeping, not agreement, and
bookkeeping is the part nobody was getting wrong.

The reviewer's own framing during the thread is the better lever, and it is not
in the record: *write down what a competent reader cannot derive.* The sentence
this corpus lost most to — *an agent finishes in minutes, a human reviews at
human speed* — was self-evident where it was true, wrong where it was specific
(agents burn tokens in minutes; they do not finish tasks in them), and wrong
about the human (inaction on a pull request is a judgment about the work, not a
service rate). It is deleted. Mandatory reading before a first edit stood at 568
lines across three documents. That number is the one to move, and no clause
moves it.
