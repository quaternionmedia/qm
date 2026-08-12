# Record precedence

!!! info "Source of truth"
    This page defines how records in different namespaces relate to each other. Cited as: [quaternionmedia/qm](https://github.com/quaternionmedia/qm) `docs/ref/precedence.md`.

## Org vs. project records

- **Org records:** `QM-NNNN`, numbered at ratification by the [index](../README.md#index--org-records) in the `README.md`.
- **Project records:** `ADR-NNNN`, numbered locally per project, starting at 0001.

## The precedence rule

QM records bind all projects. A project record may add constraints on top of a QM record; it may not waive one. A genuine exception is an *amendment to the QM record*, ratified at org level — never a project-level workaround.

Each project's `adr/` directory lives on its own branch of [this repo](https://github.com/quaternionmedia/qm) (`project/<name>`), created from `main`. That branch's ancestry is the pin — no separate hash to hand-maintain. Org ratifications and amendments propagate by merging `main` into the project's branch — a reviewed commit, not an ambient change. This is "adoption by reference."

See [Branch namespaces](namespaces.md) for how project branches are structured.

## What binds, and what does not

Only `records/` binds. The rest of the corpus carries force by pointing at a record, never on its own authority:

| Directory | Force | If it conflicts with a record |
|---|---|---|
| `records/` | binding on every project | it *is* the rule |
| `registers/` | binding, as the record that creates it says | the record wins; the register is its data, not a second rule |
| `handbook/` | policy and status, binding on QM's own conduct | the record wins, and the conflict means the page needs promoting or correcting |
| `perspectives/` | none, by construction | no conflict is possible; a perspective is an opinion |
| `project-seed/` | none in itself | it is a template; the copy is governed where it lands |

A project record may tighten a `handbook/` page the same way it may tighten a record. It may not relax either. If a handbook page ever needs to settle a dispute rather than describe a practice, that is the signal to promote it to a record — each page states its own promotion path.

The drafting discipline (squash before ratification, append-only after, numbering at ratification, one decision per record, banned-vocabulary lint) is identical at both levels and is itself an org record: see [*Decision-record discipline*](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-decision-record-discipline.md) in `records/`.

## Related

- [Ratification](ratification.md) — how records move from `Proposed` to `Accepted`
- [Branch namespaces](namespaces.md) — how project branches hold their records
- [Handbook: Governance rollout](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) — what is enforced vs. written-only
