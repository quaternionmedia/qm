# QM-XXXX — Contribution and Sponsorship Policy

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-09 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P2 — commons-first economics |

## Context

The open-license record establishes *that* gaps are closed upstream; this
record establishes the economics and mechanics around it — budget, registers,
and how client engagements interact with contributions. The causal claim
underneath: QM's consulting is credible because its maintenance is real, so
the contribution pipeline is revenue infrastructure, not charity overhead.

## Decision

1. **Sponsorship is a budget line.** Maintainers of engines QM depends on are
   sponsorship candidates by default; sponsorship may be paired with QM's own
   PRs, explicitly including paying for review bandwidth.
2. **The carried-patch register is org-level** (`registers/carried-patches.md`
   in this corpus): every patch any QM project applies at build time is
   registered with upstream PR link, owning project, and carry start date. A
   carried patch is a commitment made by the org, whichever project carries
   it. A build-time patch absent from the register is a lint failure.
3. **Quarterly register review** enforces the promote-or-drop trigger: any
   patch carried two quarters without upstream movement is promoted to a
   maintained public QM fork or dropped — silent indefinite carrying is the
   banned middle state.
4. **Client work touching upstream:** contributions produced inside an
   engagement are contributed to the commons under the upstream's license;
   the client is credited where they consent. Engagement contracts state this
   up front — including the AGPL source-availability obligations of copyleft
   components in client deployments — as scoped terms, never discovered
   terms.

## Consequences

- The register makes the org's total upstream exposure visible in one file —
  an honest dashboard of how much commons debt is in flight.
- Contracts gain a standard contribution clause; sales conversations gain a
  differentiator that is also simply true.
- Cost accepted: some clients will decline the contribution clause; that is a
  scoping outcome, not a policy failure.

## Alternatives considered

1. **Per-project patch tracking** — rejected: fragments the org's commitment
   picture and hides aggregate carry load.
2. **Contribute-only-when-convenient** — rejected: converts the causal claim
   back into a slogan.

## Revision triggers

- Register exceeds a sustainable carry count (forces prioritization rules).
- A client engagement pattern emerges that the standard contribution clause
  cannot scope (the clause needs a decision, not ad-hoc waivers).

## Amendments

*None.*
