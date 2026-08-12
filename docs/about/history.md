# History

!!! info "Rationale lives in perspectives"
    This page names what happened. **Why** it happened, what was learned, and what the alternatives were live in [perspectives/](https://github.com/quaternionmedia/qm/blob/main/perspectives/) — the corpus's record of dated, attributed opinion and incident reports.

## How the corpus started

The QM constitution began as a single decision-recording template and a set of charter beliefs about how governance should work. It was drafted and is continually refined.

All twelve current records are marked `Proposed` deliberately: ratification waits on a second active code owner. This is not a backlog — it is a gate. See [Ratification](../ref/ratification.md) and [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) for why.

## Reference implementations

The corpus has adopted projects:

- **`project/qmetronome`** — a non-server runtime, the reference instance for that class
- **`project/codecartographer`** — an existing project brought under governance after the fact (brownfield adoption)
- **`project/datum`** — a hardware project
- **`project/dossier`** — a dashboard and audit tool for the corpus itself
- **Others** — in various stages of adoption and phase progression

There is **no reference instance for a server/container runtime.** `project/streaming-infrastructure` is a design branch that once held that role; the public repository no longer exists.

## Where rationale lives

The corpus records how decisions are *made*; the [perspectives/](https://github.com/quaternionmedia/qm/blob/main/perspectives/) directory holds the *why* — incident reports, process retrospectives, what was learned, what failed. These are dated and attributed.

The style guide rule is: rationale belongs in perspectives, not inline with code or embedded in prose elsewhere. Rationale in comments goes stale silently; rationale in a dated perspective is allowed to age, and it says what was true on a day.

Some key perspectives:

- **2026-07-04** — [qmetronome onramp retrospective](https://github.com/quaternionmedia/qm/blob/main/perspectives/claude-sonnet-5-2026-07-04-qmetronome-onramp-retrospective.md) — proposals that became draft records and committed procedures
- **2026-08-07** — [alfred brownfield adoption](https://github.com/quaternionmedia/qm/blob/main/perspectives/2026-08-07-alfred-brownfield-adoption.md) — first adoption of a project predating the corpus
- **2026-08-09** — [explanation in the wrong place](https://github.com/quaternionmedia/qm/blob/main/perspectives/2026-08-09-explanation-in-the-wrong-place.md) — the style guide delivered as a perspective
- **2026-08-11** — [inflation, deflation, and what discovery looks like](https://github.com/quaternionmedia/qm/blob/main/perspectives/2026-08-11-inflation-deflation-and-what-discovery-looks-like.md) — a finding about the corpus's own generated-documents convention

See [perspectives/README.md](https://github.com/quaternionmedia/qm/blob/main/perspectives/README.md) for the full index.

## Related

- [Overview](overview.md) — what the corpus is
- [Architecture](architecture.md) — how it works
- [perspectives/README.md](https://github.com/quaternionmedia/qm/blob/main/perspectives/README.md) — the full index of dated opinion
- [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) — where the corpus stands in governing itself
