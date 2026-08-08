# QM-XXXX — Contribution and Sponsorship Policy

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-09 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P2 — commons-first economics |

## Context

The open-license record decides *that* a capability gap is closed upstream
rather than by a closed product or a private workaround. It stops there. This
record owns everything that follows from it — the budget, the carry mechanics,
the register, the stall trigger, and how client engagements interact with
contributions — so the two records can be amended independently without one
silently contradicting the other. The causal claim
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
   it. A build-time patch absent from the register fails review. It is not a
   gate: nothing can discover a build-applied patch from a repository, which
   is exactly why registering it is an obligation on the person who adds it
   rather than a check on the artifact.
3. **Carrying, and how it ends.** A pending patch is carried on a public
   branch of a public QM fork, applied at build time, registered before it
   ships, and archived on merge. **Quarterly register review** enforces the
   stall trigger: any patch carried two quarters without upstream movement
   ends one of three ways — promoted to a maintained public QM fork,
   implemented in the carrying project's control plane if it is genuinely
   seam logic, or dropped. Silent indefinite carrying is the banned middle
   state. "Upstream movement" means a maintainer response, a review, or a
   merge on the linked PR; a patch nobody upstream has acknowledged has not
   moved, however active the fork is.
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
