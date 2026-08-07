# ADR-XXXX — Datastore and Task Queue

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-07 |
| **Pends on** | The choice of compliant replacements for the datastore and the broker. Nobody has scoped that migration, and this record declines to pick one by implication. |
| **Principle** | P1 — ownership is the deliverable |

## Context

MongoDB fills three roles in Alfred simultaneously: the primary document
store behind Beanie and Motor, the Celery broker, and the Celery result
backend. The deployed stack runs it as `mongo:bionic`.

MongoDB moved to the Server Side Public License in 2018. SSPL is named
explicitly in the exclusion rule's list of excluded source-available regimes,
and that rule admits no waivers. The Python drivers are not the problem —
Motor and PyMongo are Apache-2.0 and fully compliant. The server is.

The exclusion rule's relicense protocol does not reach this. That protocol
handles a component relicensing *after* QM adopts it: freeze at the last
compliant version, ratify a migration-or-fork record within ninety days. Here
the relicense long predates this project's adoption of the constitution, so
the trigger never fires and the ninety-day clock has nothing to start from.
The org record covers future breakage and greenfield selection; it has no
path for a component that was already non-compliant on the day the
constitution arrived.

Two further facts bear on the eventual replacement without settling it.
Celery's MongoDB broker support has never been a first-class transport, so
this coupling is fragile independently of licensing. And the three roles are
separable: the document store and the broker are one component today by
convenience, not by necessity.

## Decision

1. **The MongoDB dependency is recorded as non-compliant with the exclusion
   rule, and this record does not waive it.** Adoption acknowledges the
   conflict; it does not authorize it. No reading of the org record makes the
   current stack compliant, and none is attempted here.

2. **Scope is frozen.** No new MongoDB-specific coupling is added while the
   conflict is open: no new dependency on MongoDB-only query features,
   aggregation pipelines, or server-side behavior beyond what the application
   already uses, and no additional role assigned to the MongoDB instance.
   Freezing scope is not remediation. It keeps the eventual migration from
   growing while it is unscheduled.

3. **The replacement is not chosen here, and the choice is not made by
   implication.** The option space is real and the tradeoffs are material —
   whether to keep a document model or move to the house-stack default
   relational store, and whether the broker moves with the store or
   separately. Choosing well requires scoping work nobody has done. A record
   that picked under those conditions would be guessing with the authority of
   a decision.

4. **The conflict carries no deadline, and that is deliberate.** No date here
   would be derived from an estimate, and an invented one either slips —
   teaching contributors that recorded dates are decorative — or forces the
   migration to be closed badly to meet it. The revision triggers below are
   observable events, which is what the template asks for and what actually
   binds.

5. **The brownfield gap is raised to the org.** That the exclusion rule has no
   path for a component non-compliant at adoption time is a hole in the org
   record, not a peculiarity of this project. It is proposed as an amendment
   there rather than patched by local interpretation here.

## Consequences

- This project cannot claim compliance with the exclusion rule, and does not.
  It claims that the conflict is known, bounded by §2, and recorded.
- Cost accepted: the primary sovereignty exposure in this stack stays open
  for an undetermined period. That is the honest consequence of declining to
  invent a schedule, and it is preferable to a schedule nobody believes.
- Cost accepted: `mongo:bionic` also runs on an out-of-support base, so the
  operational risk of leaving this open grows over time even though the
  licensing risk is static.
- §2 makes the migration cheaper the longer it waits rather than more
  expensive, which is the one lever available without a schedule.
- The license report cannot see any of this: a database image is not an entry
  in a dependency manifest. This record is the only place the conflict is
  visible, which is why enumerating it matters more than gating on it.

## Alternatives considered

1. **Choose the replacement now.** Rejected: the datastore decision drives
   the data model, the driver, the migration path, and the broker question
   with it, and none of that has been scoped. Deciding now would produce a
   record that reads as settled while resting on nothing, which is worse than
   a recorded open question.
2. **Apply the relicense protocol's ninety-day clock by analogy.** Rejected:
   the analogy does not hold. That protocol responds to a change in a
   component QM already vetted, where freezing at the last compliant version
   is meaningful. There is no last compliant version to freeze at here — the
   supported line has been SSPL throughout this project's life.
3. **Pin to the last Apache-2.0 MongoDB release.** Rejected: that line is
   years out of support and carries unpatched vulnerabilities. Trading a
   licensing conflict for an unpatched database is not remediation, and the
   exclusion rule exists to protect sovereignty, not to be satisfied
   technically at the cost of the thing it protects.
4. **Treat the driver's Apache-2.0 license as satisfying the rule.**
   Rejected: the rule covers every component in the deployed runtime path,
   and the server is in that path. This reading would be compliance theater
   in the record's own words.

## Revision triggers

- A replacement datastore or broker is scoped — this record's `Pends on`
  resolves and the decision moves into a successor record.
- The org ratifies an amendment covering components non-compliant at adoption
  time — §5's referral is answered, and this record aligns to whatever
  mechanism that establishes.
- MongoDB relicenses to an OSI-approved or FSF-free license — the conflict
  disappears without any migration.
- A MongoDB-only feature is proposed for the application — §2's freeze is
  under pressure, which is the signal that deferral has begun to cost.
- The `mongo:bionic` base reaches a point where operational risk, not
  licensing, forces the move — the decision gets made for different reasons
  than this record anticipates, and should be recorded as such.

## Amendments

*None.*
