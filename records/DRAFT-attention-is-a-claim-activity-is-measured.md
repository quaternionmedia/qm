# QM-XXXX — Attention Is a Claim, Activity Is Measured

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-19 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P6 — decisions are documented or they didn't happen; P8 — systems over heroics |
| **Restated in** | `ci/workspace.yaml`'s header, which names this record back |

## Context

The org has many times more repositories than any plan has ever considered, and
the question a session asks first is which of them anybody is working on.

`ci/workspace.yaml` answered it in four comment headers — *Active: the working
set*, *Worked on 2026-08-09, not since*, and two more. Nothing could read them,
nothing could check them, and only one of the four was a claim about attention
at all. The other three were dated observations written as prose, which is a
measurement with no mechanism behind it and no date attached to the reader's
copy. They went stale silently, which is what a measurement in a comment does.

`records/DRAFT-project-phase-ladder.md` §4 already settles the shape for the
adjacent question: the claim and the evidence are separate documents and
neither may be derived from the other. `phase` says what a project is working
toward; nothing said whether anybody was working on it.

The tempting fix is to compute the answer from the host, and it is wrong in a
way that would have shipped. The host offers three plausible fields and none of
them answers the question. `updatedAt` moves when somebody edits a description.
`pushedAt` moves on a push to any ref — a tag, a bot branch, a Pages deploy, a
sweep — so repositories whose default branches had not moved in years reported
it on the same afternoon. The nearest field, the default branch's own last
commit, still cannot see work on another branch and cannot see work that never
left a disk. The measurements are in
`perspectives/2026-08-19-three-fields-and-none-of-them-is-activity.md`.

That last blindness is not academic. Measuring the clones instead found a
governance standard that one repository's committed handoff defers to and that
exists on no remote; a version tag on no remote, in a corpus where the tag is a
human gate; and a repository every host field reports as dead while it holds the
largest body of unpushed work in the workspace.

## Decision

**Attention is a claim a human makes. Activity is measured, on more than one
axis, and no axis is allowed to stand for another.**

1. **`attention` is a roster field and never inferred.** Its values are
   `active`, `queued`, `dormant`, `retired` and `external`. It records what a
   human said, in `ci/workspace.yaml`, beside `phase` and for the same reason.

2. **An absent `attention` is `unstated`.** It is not `dormant`. `dormant` says
   nobody is working on a repository; `unstated` says nobody has answered the
   question. A generator that read silence as `dormant` would grow the roster
   claims no human made — the substitution `phase_source` already refuses, and
   the one the phase ladder's §7 keeps `unknown` available for.

3. **`recency` is measured from the default branch's last commit**, and never
   from a host's `updatedAt` or `pushedAt`. Its values are `archived`, `live`,
   `quiet`, `cold` and `unknown`. `archived` is a host statement and outranks
   every date: a commit on a branch somebody forgot to stop pushing to does not
   reopen a closed repository.

4. **`risk` is measured from a clone, is machine-scoped, and never reaches a
   committable document.** Its values are `unpushed:<n>`, `dirty:<n>`,
   `pin-drift`, `clean`, and `unreadable:<reason>`. Unpushed counts describe one
   operator's disk. The split is a file boundary rather than a filter, for the
   reason `ci/inventory.py` already records: a filter with a bug publishes what
   it was meant to withhold, and a file that never receives the value cannot.

5. **`unreadable` is not `clean`.** A repository nobody could inspect has an
   unknown amount of work at stake. Reporting that as nothing at stake is how a
   dashboard goes green because its query returned empty.

6. **A count of unpushed commits is reported with what produced it.** A branch
   whose upstream is gone, a branch that was never pushed, a local copy ahead of
   a live remote branch, and a tag on no remote are four different situations
   that produce one number, and only the last two have no benign reading. The
   count without the refs behind it is not actionable, and a tool that offers
   only the count invites the reader to act on the wrong one.

7. **Where the claim and the measurement disagree, the pair is named and
   neither side is overwritten.** By
   `records/DRAFT-a-disagreement-is-a-delta.md` that disagreement is a unit of
   work: identified by what disagrees, opened at
   `brainstorm`, closed by somebody deciding. A repository claimed `active`
   whose branch is cold, one claimed `retired` that is moving, and one moving
   that the roster does not list are all deltas rather than fields to fix.

**Mechanism:** `ci/inventory.py`, run as `uv run qm inventory`, writing
`inventory-public.json` and the two gitignored companions. Per
`records/DRAFT-governance-arrives-as-a-mechanism.md` §1 this record arrives with
that mechanism rather than as prose.

## Consequences

**The roster gains a field every entry can be asked about**, and loses four
comment headers that no check could read. Repositories nobody has stated an
attention for acquire `unstated` rather than a category invented for them.

**The corpus can see work that has not left a machine**, which no document here
could before. That is the axis that found the standard, the tag and the dormant
host copy, and it is the axis that costs the most: it needs a clone, and it
reports `unreadable` for every repository nobody has cloned.

**`unreadable` will be the common answer for most of the org.** That is the
honest reading and it looks like a gap, because it is one.

**A reconcile queue can grow.** The disagreement rule creates work items and
does not create anybody to do them. A growing queue is a real signal about the
roster and should be read as one.

## Alternatives considered

**One label per repository, measured only.** Simpler to read, and it collapses
*nobody has decided to stop* with *we decided to stop*. There would be nowhere
to record intent, and the roster's whole purpose is to hold what humans have
said.

**Infer `attention` from the commit dates.** Rejected for the same reason the
phase ladder rejects computing a phase from artifacts: it makes the table
self-maintaining and quietly redefines a human's claim as a machine's
observation. It is also the failure this record exists because of — the roster's
comment headers were exactly that inference, written by hand.

**Classify on `pushedAt`.** Rejected on measurement, not on principle. It is the
field a reasonable person picks, it is right about most repositories, and it is
wrong about the ones worth looking at.

**Put `risk` in the public document.** Rejected. It would publish one operator's
working state in a committable file, and the reason the inventory splits by file
rather than by filter is that a filter's bug is irreversible.

**Keep the categories as comments and refresh them.** This is the state that
produced the record. It scales with how often anybody remembers.

## Revision triggers

- A repository whose default branch is not where its work happens, making
  `recency` wrong in the ordinary case rather than the edge case.
- An attention value that has to be inferred to be useful, which would mean the
  vocabulary is wrong rather than the inference.
- A second machine reporting `risk`, which this record does not describe: it is
  written for one clone per repository and says nothing about how two disagree.
- A disagreement between claim and measurement that is never work — where the
  right response is always automatic — which would mean §7 is too broad.

## Amendments

*(none)*
