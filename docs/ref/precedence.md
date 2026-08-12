# Record precedence

!!! info "Canonical"
    This page states how records at the two levels relate. Cited as `docs/ref/precedence.md`.

## Two kinds of record

- **Org records:** `QM-NNNN`. Numbered at ratification, by the index in the repository's [README](https://github.com/quaternionmedia/qm/blob/main/README.md#index--org-records).
- **Project records:** `ADR-NNNN`. Numbered locally by each project, starting at 0001.

## The precedence rule

**QM records bind all projects.** A project record may add constraints on top of a QM record. It may not waive one.

If a project genuinely needs an exception, the path is an amendment to the QM record, ratified at the org level — never a project-level workaround.

## Adoption by reference

Each project's `adr/` directory lives on that project's own branch of this repository, created from `main`. The branch's ancestry is the pin: there is no separate version hash to maintain. Org ratifications reach the project when `main` is merged into its branch — a reviewed commit, not an ambient change.

## What binds, and what does not

Only `records/` binds. Everything else carries force by pointing at a record:

| Directory | Force | If it conflicts with a record |
|---|---|---|
| `records/` | binding on every project | it **is** the rule |
| `registers/` | binding, as the record that creates it says | the record wins; a register is data, not a second rule |
| `handbook/` | policy, binding on QM's own conduct | the record wins; the page needs correcting or promoting |
| `perspectives/` | none | no conflict is possible; a perspective is opinion |
| `project-seed/` | none in itself | it is a template; the copy is governed where it lands |

A project record may tighten a handbook page the same way it may tighten a record — and may not relax either. If a handbook page ever needs to settle a dispute rather than describe a practice, that is the signal to promote it to a record. Each page states its own promotion path.

## The drafting discipline

The same discipline applies at both levels: one decision per record, squash before ratification, append-only after, numbering at ratification, and a lint for banned drafting vocabulary. The discipline is itself an org record: [Decision-record discipline](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-decision-record-discipline.md).

## Related

- [Ratification](ratification.md) — how a record becomes binding
- [Branch namespaces](namespaces.md) — where each kind of record lives
- [Draft a record](../cookbook/draft-a-record.md) — the recipe
