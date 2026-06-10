# QM-XXXX — House Stack

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-09 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P5 — one stack, deeply known |

## Context

Depth in one stack beats breadth across five: every project compounds skill,
patterns transfer wholesale, and anyone at QM can enter any QM codebase. The
stack below is descriptive before it is prescriptive — it is what QM's
existing systems are built from — and this record's job is to make additions
deliberate rather than enthusiasm-driven.

## Decision

1. **The blessed set** for code QM builds:
   - **Python** — FastAPI (services), SQLModel/Pydantic (models/validation),
     Metaflow (DAGs and scheduled flows), Click (CLIs), Jinja2 (templating),
     httpx (clients), Alembic (migrations), pytest (tests), uv (packaging).
   - **PostgreSQL** as the default store; SQLite acceptable for single-node
     tools.
   - **Single-file HTML + modular JS** (vendored libraries; anime.js for
     motion) for visualization deliverables.
   - Containers + Compose/k3s + GitOps for deployment.
2. **Additions require a record**, org-level, with the alternatives the
   blessed set already covers honestly weighed. A dependency outside the set
   appearing in review without a linked record fails review.
3. **Carve-outs, explicit:**
   - *Contributions* — written in the target community's language and idiom,
     per the open-license record. The house stack governs our repos, not our
     PRs.
   - *Client-mandated stacks* — contract scope, recorded in the engagement,
     never imported as house drift.
   - *Engines* — selected components are whatever language their community
     builds in; the house stack governs the seam, not the engines.

## Consequences

- Hiring, onboarding, and cross-project maintenance all amortize over one
  stack.
- The dependency-review gate creates light friction on every new library —
  accepted: that friction is the mechanism.
- Cost accepted: occasionally a genuinely better tool waits outside the set
  until its record is written. Writing the record is cheap; unwritten drift
  is not.

## Alternatives considered

1. **Best tool per job** — rejected: locally optimal, organizationally
   corrosive; five half-known stacks are worse than one deep one.
2. **Stricter monoculture (no carve-outs)** — rejected: it would contradict
   the contribution doctrine and make client work impossible to scope.

## Revision triggers

- A blessed component's upstream relicenses or is abandoned (handled jointly
  with the open-license record).
- The same out-of-set dependency is requested by two projects — the set
  needs a decision, not repeated exceptions.

## Amendments

*None.*
