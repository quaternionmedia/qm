# Overview

!!! info "Source of truth"
    This is a summary of [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) and the records in `records/`. See those sources for the complete text.

## What QM is

The Quaternion Media constitution is the org-level decision corpus: the philosophies that govern every QM project, the process that keeps them coherent, and the proven template each new project forks from.

Projects adopt this corpus **by reference** and may tighten its rules — never relax them. This means:

1. A project can impose stronger constraints than the corpus demands
2. A project cannot waive a corpus constraint — exceptions require an amendment to the corpus itself, ratified at the org level
3. The corpus is a shared set of rules, not a template copied and diverged

## The four artifact classes

| Artifact | Binding | What it holds | Lives in |
|---|---|---|---|
| **Record** | Yes (if `Accepted`) | A decision made with full context, alternatives considered, and rationale | `records/` (org) or `adr/` (project) |
| **Register** | Yes (by the record that creates it) | Living data: what's currently true about a set of things | `registers/` or project-local |
| **Handbook** | On QM's own conduct only | Policy and procedure, non-binding unless ratified | `handbook/` |
| **Perspective** | No | Attributed, dated opinion; incidents and lessons learned | `perspectives/` |

## The charter

QM believes in:

1. **Autonomy in tactics, alignment in values** — projects choose their own tools and methods; they share principles
2. **Decisions recorded before they're made** — the form disciplines the thought
3. **Ratification by two** — a gate one person can satisfy alone is no gate
4. **Every change through review** — nothing reaches `main` by direct push
5. **No rationale in code** — explanations live in decision records, not comments
6. **Single-source-of-truth** — one place to update rather than two that drift
7. **Git as the state machine** — branches are states; commits are transitions
8. **Adoption by reference** — projects don't copy the corpus; they pin and merge it
9. **Precedence without bureaucracy** — QM records bind all projects; project records bind only their own
10. **Open by default** — work is public unless there's a reason (named in policy)
11. **Taste is personal; constitution is shared** — what counts is what's ratified, not what someone believes

See [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) for the full charter.

## The records (draft)

Twelve decisions are currently drafted and awaiting ratification:

- **Build the seam, buy the engines** — What the corpus builds vs. what it buys
- **Contribution and sponsorship policy** — Who can contribute
- **Decision-record discipline** — How records are drafted, numbered, and amended
- **House stack** — The standard seams and protocols
- **Human-only contributorship** — No agent bylines, no tool-as-author trailers
- **IDE-integrated governance discovery** — Reading and discovering governance in your editor
- **Monitoring seam and instance identity** — How projects report what's running
- **Open-license exclusion and upstream-contribution remediation** — License gate patterns
- **Outbound licensing of QM work** — How derivative work is licensed
- **Project phase ladder** — Governance maturity levels
- **Seams on standard protocols** — Standardized integration points
- **Version tags are claims** — What a tag asserts about a build

All records are marked `Proposed` deliberately — ratification waits on a second active code owner. See the [org records index](../README.md#index--org-records) for links.

## Related

- [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) — the full charter
- [Architecture](architecture.md) — how these principles are implemented in the structure
- [Record precedence](../ref/precedence.md) — how records bind projects
