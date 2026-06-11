# Quaternion Media Constitution

The org-level decision corpus: the philosophies that govern every QM project,
the process that keeps them coherent, and the proven template each new
project forks from. Projects adopt this corpus **by reference** and may
tighten its rules — never relax them.

## Layout

```
qm/
├── README.md            ← this file: namespaces, precedence, fork procedure
├── PRINCIPLES.md        ← the charter: interpretation the records are cut from
├── TEMPLATE.md          ← record template for THIS corpus (QM-XXXX)
├── records/             ← org records (philosophies); DRAFT-* until ratified
├── registers/           ← org-level live registers (carried patches, …)
├── handbook/            ← business policy routed out of ADR form
├── perspectives/        ← attributed, dated, non-binding opinions (incl. AI drafting sessions)
├── math/                ← experiments workspace: demonstrations against open questions named in perspectives
└── project-seed/adr/    ← the forkable template a new project copies verbatim
```

## Namespaces and precedence

- **Org records:** `QM-NNNN`, numbered at ratification by this README's index.
- **Project records:** `ADR-NNNN`, numbered locally per project, starting at 0001.
- **Precedence:** QM records bind all projects. A project record may add
  constraints on top of a QM record; it may not waive one. A genuine
  exception is an *amendment to the QM record*, ratified at org level — never
  a project-level workaround.
- **Adoption by reference:** each project's `adr/README.md` index opens with
  an "Adopted org records" table pinning this corpus at a tag/commit. Org
  ratifications and amendments propagate by bumping that pin — a reviewed
  commit in the project, not an ambient change.

The drafting discipline (squash before ratification, append-only after,
numbering at ratification, one decision per record, banned-vocabulary lint)
is identical at both levels and is itself an org record: see
*Decision-record discipline* in `records/`.

## Forking a new project

The seed is proven — its first instance is the streaming-infrastructure
project, which serves as the reference implementation.

1. **Copy** `project-seed/adr/` into the new repo as `adr/` (README +
   TEMPLATE, verbatim).
2. **Pin** this corpus: fill the "Adopted org records" table in the project
   README with the current QM index at a tag.
3. **Wire CI:** the ADR lint job and the SBOM license gate (required by the
   open-license record) ship in the standard CI scaffold; a project without
   them is not instantiated, it is improvised.
4. **Seed the first project records** as numberless drafts by title; ratify
   per process. Project ADR-0001 is conventionally the project's adoption +
   scope record, but nothing enforces a particular first decision.
5. **Register** any carried patches in `registers/carried-patches.md` here —
   the register is org-level by design: a patch carried by one project is a
   commitment made by the org.

## Ratification

Ratification is a human action at both levels: a commit that flips Status to
Accepted, assigns the number from the index, updates the index, and names the
record in the commit message. Assistants draft; humans ratify.

## Index — org records

| # | Title | Status | Date |
|---|---|---|---|
| — | Decision-record discipline | Proposed | 2026-06-09 |
| — | Open-license exclusion and upstream-contribution remediation | Proposed | 2026-06-09 |
| — | Seams on standard protocols | Proposed | 2026-06-09 |
| — | Build the seam, buy the engines | Proposed | 2026-06-09 |
| — | House stack | Proposed | 2026-06-09 |
| — | Contribution and sponsorship policy | Proposed | 2026-06-09 |

Handbook (policy, not records): public-by-default (with a defined promotion
path to record form), style guide (minimal, legible deliverables).

**Post-ratification step for the reference project:** once the org
open-license record is Accepted, the streaming project's ADR-0001 receives a
dated amendment recording adoption-by-reference of the org record. Its body
is untouched; the amendment aligns the instance to the doctrine.
