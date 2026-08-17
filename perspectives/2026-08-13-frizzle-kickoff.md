# Perspective — planning the bus by reading what already refused to build it

**Date.** 2026-08-13. **Attribution.** Peter's Cowork session.
**Tools:** Claude (Cowork cloud session), fresh depth-1 clones of seven repos.
**Binds.** Nothing. Destination: `qm:perspectives/`.

The session's job was a long-term plan for a minimal message queue and
dispatcher. The findings worth keeping are the assumptions that fell.

**False assumption one: the dispatcher would be a green-field design.** It
isn't. qmcp already contains the complete data model — a persisted `messages`
table, `PUBSUB`/`BROADCAST`/`HEARTBEAT` enums, five priorities, `QUEUED`
status, a `RunnerRegistry` with an `AsyncRunner` slot — and every executor
raises `NotImplementedError` on purpose, because the architecture doc forbids
orchestration in the server plane. The design work had been done and then
deliberately parked at a boundary. The plan's envelope contract reuses that
vocabulary instead of inventing a rival one; the reusable lesson is to search
for the parked design before drafting, because the org's own invariants are
why it looks unbuilt.

**False assumption two: governance would be the slow, trailing part.** The
opposite. qm had already written the two rules that decided the architecture —
MQTT is pre-blessed in the seams record, and the monitoring-seam record
mandates the collector pattern and had already audited qmcp's live defects
(mutate-on-read expiry, indistinguishable instances, no `generated_at`). The
policy layer was ahead of the code. The check that would have caught a
non-conforming design existed before the design did; the plan simply obeyed
it.

**False assumption three: the org's repos are roughly uniformly governed.**
They span the full spectrum, from qm/rad rigor to repos invisible to the org's
own status tooling, with codecartographer's *partial* adoption the most
instructive failure — wrong mount path, unpinned branch, missing workflows.
Partial adoption misconfigured is arguably worse than absence, because it
reads as compliance at a glance. That observation shaped decision 6 (moat
adopted now, checklist built from codecartographer's specific mistakes) and
the staged-codification decision (PoCs first, records from evidence).

**A check that does not yet exist:** nothing verifies that a repo can actually
be born from project-seed — every adopter was retrofitted. frizzle's spawn is
that check, run for the first time; ledger N1 collects what it finds. If the
spawn is painful, the pain is the deliverable.

**One admission.** The Mosquitto chart in the kickoff bundle imitates moat's
wrapper idiom from reading three examples; it has never been templated against
the cluster. It is in the bundle because a concrete wrong draft beats an
abstract right intention, but the handoff marks it unverified, and it should
be treated as a starting point, not a claim.
