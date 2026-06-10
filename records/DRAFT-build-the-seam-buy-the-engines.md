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

## Consequences

- Custom-code surface stays small enough that one person can hold a whole
  system, and patterns transfer across projects (the seam looks the same in
  fleet management, streaming, and media tooling).
- Engine selection becomes the high-stakes activity, governed by the
  open-license and seams records — which is where the governance weight
  already is.
- Cost accepted: some capabilities will live upstream-shaped rather than
  exactly-as-we'd-build-them. That is the commons working as intended.

## Alternatives considered

1. **Build the engines** — rejected: duplicates the commons, concentrates
   bus-factor in the worst place, and starves the seam of attention.
2. **Buy the seam too** (low-code/iPaaS orchestrators) — rejected: the seam
   is exactly where policy and sovereignty live; outsourcing it inverts the
   doctrine.

## Revision triggers

- A project's seam record trips its size smell (forces the split-or-upstream
  decision).
- An engine category QM depends on loses all compliant options (the seam may
  need to absorb a capability — a doctrine-level event, decided here).

## Amendments

*None.*
