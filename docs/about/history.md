# History

!!! info "Where the reasons live"
    This page names what happened. The reasons — incidents, lessons, and arguments — live in [perspectives/](https://github.com/quaternionmedia/qm/tree/main/perspectives), the corpus's collection of dated, attributed opinion.

## How the corpus started

The corpus began as a charter ([PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md)) and a set of draft decision records cut from it. The records, the seed template, and the CI tooling grew from there, shaped by each project adoption.

All twelve org records are still `Proposed`. This is deliberate: ratification requires a second active code owner. See [Ratification](../ref/ratification.md) and [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md).

## Adopting projects

Several projects have adopted the corpus, each on its own `project/<name>` branch:

- **qmetronome** — the reference instance for a non-server runtime.
- **alfred** — the first adoption by a project that existed before the corpus (a "brownfield" adoption).
- **datum** — the first hardware project.
- **dossier** — a dashboard and audit tool for the corpus itself.
- Others, in various stages of adoption.

There is **no reference instance for a server or container runtime**. The `project/streaming-infrastructure` branch is a design branch, not an adopted project; no repository exists behind it.

The current state of every project is in [governance-status.yaml](https://github.com/quaternionmedia/qm/blob/main/governance-status.yaml). Read that file rather than trusting counts written into prose — a number in a sentence goes stale silently.

## Where the reasons live

The corpus separates *what was decided* from *why things went the way they did*:

- Records hold decisions, with their context and alternatives.
- Perspectives hold experience: incidents, retrospectives, and lessons. They are dated and attributed, so they are allowed to age — each one says what was true on a day.

Some notable perspectives:

- [qmetronome onramp retrospective](https://github.com/quaternionmedia/qm/blob/main/perspectives/claude-sonnet-5-2026-07-04-qmetronome-onramp-retrospective.md) (2026-07-04) — proposals that later became draft records and committed procedures
- [alfred brownfield adoption](https://github.com/quaternionmedia/qm/blob/main/perspectives/2026-08-07-alfred-brownfield-adoption.md) (2026-08-07) — the first adoption of a pre-existing project
- [Explanation in the wrong place](https://github.com/quaternionmedia/qm/blob/main/perspectives/2026-08-09-explanation-in-the-wrong-place.md) (2026-08-09) — the incident behind the style guide
- [Inflation, deflation, and what discovery looks like](https://github.com/quaternionmedia/qm/blob/main/perspectives/2026-08-11-inflation-deflation-and-what-discovery-looks-like.md) (2026-08-11) — a finding about the corpus's own generated documents

The full index, with review status for each file, is [perspectives/README.md](https://github.com/quaternionmedia/qm/blob/main/perspectives/README.md).

## Related

- [Overview](overview.md) — what the corpus is
- [Architecture](architecture.md) — how it works
- [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) — where the corpus stands in governing itself
