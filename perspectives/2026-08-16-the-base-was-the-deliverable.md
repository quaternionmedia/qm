# The Base Was the Deliverable

| | |
|---|---|
| **Date** | 2026-08-16 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | assistant-2026-08. See `ci/tool-registry.yaml` |

---

## What was actually being built

Three days of work in this repository read, entry by entry, as reacting to
things that broke. A pull-request model corrected. A tag record given teeth. A
CLI. Four gates. A ledger. Four registries. A config standard. An inventory. A
privacy split.

None of it was the governance loop. All of it was the **base the loop stands
on**, and nobody said so — including in the plans written to say what was being
done.

The operator named it on 2026-08-16: *a stable governance base, which is the
deliverable after a realistic loop can begin.* Everything above had been chasing
that, "although maybe not that explicitly stated."

## Why it went unstated

Every mechanism arrived from a break. Of twenty ledger entries, **six originate
in something going wrong** — five recorded as `kind: fix`, and one build that
exists only because a tool corrupted the file it was settling. A wrong model, a
leaked name, an improvised invocation, a lying success line. Reactive work does
not announce its own shape. Each fix looked local, so each was recorded as a
fix, and the pattern they formed was only visible after there were enough of
them to form one.

That is not a criticism of reacting. The breaks were real and the fixes were
right. But work that is only ever named locally cannot be finished, because
nobody can say what "done" would be.

## What the base turned out to consist of

Measured on the working tree at `3bb45f4`, by the commands named beside each
figure:

| | | |
|---|---|---|
| Entry points | 1 — `uv run qm`, 18 routes | `ci/cli.py` dispatch table |
| Registries of claims | 6 in `ci/` | `ci/*registry*.yaml` |
| Gates built | 10, 0 declared-and-unbuilt | `ci/gate-registry.yaml` |
| Declared gaps | 5 of 7 patterns | `check_exists: false` |
| Exemptions, each with a reason | 6 | `ci/exception-registry.yaml` |
| Policies, detected or explained | 9 — 6 detected, 2 cannot be, 1 planned | `qm policies` |
| Ledger entries, all attributed | 20 | `qm ledger --check` |
| Lessons recorded | 36 | `ledger.yaml` |

Read as a list of features that is unremarkable. Read as an answer to *what must
be true before a loop can run*, it is close to complete, and the shape is:

- **One surface**, so an operation is repeatable rather than improvised.
- **Claims separated from evidence**, so a measurement cannot be mistaken for
  an intention.
- **Detectors that read artifacts**, so a check survives the tool that ran it.
- **Attribution on every action**, so credit and fault are audited on the same
  terms.
- **Declared gaps and exemptions**, so the floor's holes are countable rather
  than discovered.
- **Predictions recorded before acting**, so an overclaim is comparable rather
  than remembered.

## The stability test already exists

The operator set it earlier, for a sweep: *we're stuck here until the loop runs
multiple times without new entries.* That is not only a test for a sweep. It is
the definition of a stable base.

A base is stable when running everything over it produces nothing new. Applied
to governance rather than to a directory, the same test says: **the base is
stable when a full pass adds no ledger entry.** Six of twenty entries missed
their projection and one is unscored, which is a measure of how much the ground
still moves.

By that test the base is **not yet stable, and the writing of this page proved
it.** The pass that produced this retrospective added an entry: a tool built to
settle a ledger entry destroyed the ledger's readable diff on its first attempt
and corrupted a live entry on its second. Entries `-004`, `-005` and `-006` are
three consecutive builds, each of which added one. The test is not close to
passing, and a retrospective claiming otherwise would be the failure it
describes.

That reframes the loop condition from a chore into the acceptance criterion for
the deliverable. It also explains why the loop kept not starting — each pass
found something, so each pass changed the base, so the next pass was over
different ground.

## What is still missing, honestly

**Most policies have no durable detector, and most never can.** Of thirty-two
lessons recorded here, six to eight are readable from an artifact. The rest are
judgement: *read stderr before calling a tool silent*, *prefer the artefact you
did not create*, *a correction names a class rather than the instance it arrived
on*. A base that only holds what a script can check is not the base this corpus
needs, and pretending otherwise would fill a column with weak detectors that read
as coverage.

**The proprietary layer is not the base.** Anything enforced only by one
vendor's hook vanishes with that vendor and vanishes silently. The rule that
keeps the base durable is that a policy may not have a preventer as its only
enforcement — prevention is disposable, detection is not.

**Nothing is ratified.** Sixteen records, none read as one body, none ratified.
A base whose own decisions are all `Proposed` is a base held up by one person's
consistency.

## The thing this retrospective is for

Naming the deliverable changes what counts as finished. Before: an open-ended
sequence of fixes, each justified, with no end. After: a base with a definition,
a stability test, and a known list of what it cannot hold.

The next honest question is not *what else should we build* but **what is the
smallest base that lets a real loop start** — and whether the answer is already
behind us.
