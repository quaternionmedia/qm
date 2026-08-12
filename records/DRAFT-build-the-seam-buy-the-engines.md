# QM-XXXX — Build the Seam, Buy the Engines

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-09 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P4 — custom code concentrates where sovereignty matters |

## Context

Engineering effort is the scarcest resource; sovereignty is the product.
These reconcile only if custom code concentrates at the point of maximum
leverage: the control plane that holds state, policy, and orchestration — the
seam — while engines (muxers, databases, transcoders, detectors, CMSes) are
selected from the commons. The seam is also the only place where bus-factor
is *ours*, which is the only acceptable place for it.

Stated as select-or-absorb, that framing has a hole, and a QM project already
occupies it. Alfred's render engine is neither selected from the commons nor
part of alfred's seam: QM wrote it, published it as a standalone package with
its own repository, tests, documentation, and release line, and alfred
consumes it at a version across its public API. The open-license record
reaches something adjacent — its §2 relicense protocol, which requires a
migration-or-fork record within 90 days when an upstream changes terms. That is
a tourniquet for a licence event, and it decides nothing about whether QM
maintains an engine of its own by choice. What alfred did is a
deliberate first choice, and it serves commons-first economics directly:
the artifact is a public package anyone can use, not a private module that
happens to live in a second directory. §5 names it, and bounds it, because a
doctrine that says "buy the engines" while the org writes engines is either
being ignored or is incomplete, and it is the latter.

## Decision

1. Each QM system is structured as **one small control plane** (house stack)
   orchestrating **selected engines** behind standard-protocol seams.
2. The seam owns: identity/auth decisions, lifecycle state, policy,
   orchestration triggers, and integration glue. The seam must never grow
   into an engine — no media handling, no storage engine, no CMS — and a seam
   service approaching the complexity of an engine it orchestrates is a
   design failure, not an achievement.
3. **Ordering rule** (reconciling with commons-first economics): every new
   capability first asks *which engine should own this upstream* — answered
   per the open-license record's remediation path — before defaulting to the
   seam. Seam logic is whatever no engine should reasonably own.
4. Each project ratifies a control-plane instance record naming what its seam
   owns, what it refuses to own, and concrete size-smell thresholds as
   revision triggers.
5. **A QM-authored engine is a legitimate third answer to §3, and is
   published or it is not an engine.** When the ordering rule finds that no
   existing engine should own a capability upstream, and the capability is
   engine-shaped rather than seam-shaped, QM may write the engine. It is
   classified as an engine by what it does, never by who wrote it, and it
   qualifies only under all of the following:
   - **Separate repository, independent release line.** It is consumed as a
     released package at a version, across its published API. A directory in
     the consuming project, or a dependency on an unreleased branch, is seam
     code in a costume.
   - **Public, under a license satisfying the open-license record.** This is
     a contribution to the commons, which is the entire justification for
     writing it rather than selecting one. A private engine is the outcome
     Alternatives §1 rejects.
   - **Its own tests, documentation, and decision memory.** It is governed as
     a project, not as an appendix to its first consumer.
   - **The consuming seam depends on the published API only.** A development
     convenience such as a submodule checkout does not license coupling to
     unreleased or private surfaces.

   Failing any of these, the code is seam logic and is governed by §2's size
   smells rather than escaping them by being kept in another repository.
   The honest failure mode of this clause is that it makes "write it
   ourselves" available, and §3's ordering rule is what keeps that from
   becoming the default: the question of which engine should own a capability
   upstream is asked and answered *before* this clause is reached, never
   after.

## Consequences

- Custom-code surface stays small enough that one person can hold a whole
  system, and patterns transfer across projects (the seam looks the same in
  fleet management, streaming, and media tooling).
- Engine selection becomes the high-stakes activity, governed by the
  open-license and seams records — which is where the governance weight
  already is.
- Cost accepted: some capabilities will live upstream-shaped rather than
  exactly-as-we'd-build-them. That is the commons working as intended.
- §5's publication requirement is what makes the boundary testable rather
  than asserted. A boundary only one consumer ever crosses, in one
  repository, is an untested claim about modularity; a released package with
  a versioned API is a claim something else can falsify.
- Cost accepted: a QM-authored engine is maintenance the org owns
  indefinitely, including for consumers outside the project that motivated
  it. That obligation is the price of the clause, and a project unwilling to
  carry it should select an engine or route the capability upstream.
- Cost accepted: two repositories and a release step for changes spanning
  seam and engine, against the alternative of one repository where the
  boundary erodes quietly because nothing forces it to hold.

## Alternatives considered

1. **Build the engines privately** — rejected: duplicates the commons,
   concentrates bus-factor in the worst place, and starves the seam of
   attention. §5 is not this: it permits authoring an engine only as a
   published commons artifact, under the conditions listed there, and only
   after §3's ordering rule has found no upstream that should own the
   capability.
2. **Buy the seam too** (low-code/iPaaS orchestrators) — rejected: the seam
   is exactly where policy and sovereignty live; outsourcing it inverts the
   doctrine.
3. **Treat a QM-authored engine as part of the seam, because QM wrote it** —
   rejected: authorship is the wrong test and adopting it would make §2's
   size smell meaningless, since any engine could be absorbed into the seam's
   accounting by the accident of who wrote it. Classification follows
   function throughout this record.
4. **Leave QM-authored engines to the open-license record's fork-promotion
   clause** — rejected: that clause describes a remediation after an upstream
   rejects a patch or dies. Reaching it requires a failure to have happened
   first, so it cannot describe a capability QM deliberately chose to build
   and publish, and stretching it to cover that case would misfile a first
   choice as a fallback.

## Revision triggers

- A project's seam record trips its size smell (forces the split-or-upstream
  decision).
- An engine category QM depends on loses all compliant options (the seam may
  need to absorb a capability — a doctrine-level event, decided here).
- A QM-authored engine gains no consumer and no release cadence beyond its
  first project — §5's conditions are being met formally and not in
  substance, and the code should be reclassified as seam logic.
- §5 is invoked twice in short succession — the ordering rule in §3 is not
  doing its work, and "write it ourselves" is becoming the default the clause
  was bounded to prevent.

## Amendments

*None.*
