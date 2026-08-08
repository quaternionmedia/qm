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

Descriptive-before-prescriptive cuts both ways, and the packaging entry is
where it has been tested. Two projects — alfred and the otto engine it
consumes — migrated to PDM deliberately, for PEP 621 conformance. That is
this record's own revision trigger firing exactly as designed: the same
out-of-set choice made by two projects is a signal the set needs a decision
rather than repeated exceptions. The set records PDM because that is what QM
builds with; a project standing on uv would be the same trigger firing in the
other direction, and would be answered the same way.

The frontend entry is a second correction of the same kind. The set
contemplated browser code only as single-file visualization deliverables,
which described the visualization work and not the interfaces QM actually
ships alongside its services. A project running a real frontend had no entry
to point at and no honest way to comply, which produces silent drift rather
than a record.

## Decision

1. **The blessed set** for code QM builds:
   - **Python** — FastAPI (services), SQLModel/Pydantic (models/validation),
     Metaflow (DAGs and scheduled flows), Click (CLIs), Jinja2 (templating),
     httpx (clients), Alembic (migrations), pytest (tests), PDM (packaging,
     with a committed lockfile).
   - **PostgreSQL** as the default store; SQLite acceptable for single-node
     tools.
   - **Single-file HTML + modular JS** (vendored libraries; anime.js for
     motion) for visualization deliverables.
   - **Frontend applications** — a distinct category from the line above.
     A visualization deliverable is an artifact handed to a reader; a frontend
     application is a long-lived interface with routing, state, a build step,
     and a dependency tree, and pretending the two are the same shape serves
     neither. The current instance is mithril with a parcel build, and a
     different framework needs a record under §2 the same as any other
     addition. Its dependencies are vendored, never CDN-loaded, per the
     open-license record, and its lockfile is committed.
   - Containers + Compose/k3s + GitOps for deployment.
2. **Additions require a record**, org-level, with the alternatives the
   blessed set already covers honestly weighed. A dependency outside the set
   appearing in review without a linked record fails review.
3. **Carve-outs, explicit:**
   - *Contributions* — written in the target community's language and idiom,
     per the open-license record. The house stack governs our repos, not our
     PRs.
   - *Client- or platform-mandated stacks* — scope fixed by the client's
     contract or the target platform's toolchain, recorded in the
     engagement, never imported as house drift.
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
- The set is revisable by evidence, and has been revised by it. A project
  that finds the set wrong writes that up rather than quietly diverging; two
  projects finding the same thing is sufficient to move the set.
- Cost accepted: naming a frontend framework in the set commits the org to
  depth in one, which is the same bet the Python entry makes and carries the
  same risk of being wrong about a fast-moving ecosystem.

## Alternatives considered

1. **Best tool per job** — rejected: locally optimal, organizationally
   corrosive; five half-known stacks are worse than one deep one.
2. **Stricter monoculture (no carve-outs)** — rejected: it would contradict
   the contribution doctrine and make client- or platform-mandated work
   impossible to scope.
3. **Bless both packaging tools and let each project choose** — rejected: two
   blessed answers to one question is how a set stops being a set, and the
   depth argument this record rests on does not survive being applied
   optionally.
4. **Hold the set and require the two diverging projects to conform** —
   rejected: the divergence was deliberate and well-reasoned, the set's own
   trigger names this exact situation as calling for a decision, and
   discarding a considered migration in two repositories to preserve a line
   nothing in the org was standing on would be consistency for its own sake.
5. **Leave frontend applications outside the set entirely**, treating each as
   a per-project decision — rejected: that is the status quo that produced
   unrecorded drift, and it makes the visualization-deliverable entry read as
   a prohibition on frontends the org demonstrably ships.

## Revision triggers

- A blessed component's upstream relicenses or is abandoned (handled jointly
  with the open-license record).
- The same out-of-set dependency is requested by two projects — the set
  needs a decision, not repeated exceptions.
- A QM project is found standing on a packaging tool other than the blessed
  one — the same trigger that set this entry, firing in the other direction,
  and answered the same way rather than by defending the current text.
- A second frontend framework is proposed — the category entry needs either
  a decision between them or an honest statement that the category is
  per-project after all.

## Amendments

*None.*
