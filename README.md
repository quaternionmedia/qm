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
├── perspectives/        ← attributed, dated, non-binding opinions; index + response status in perspectives/README.md
├── math/                ← experiments workspace: demonstrations against open questions named in perspectives
└── project-seed/        ← the forkable template a new project's own branch copies verbatim
    ├── adr/              ← README + TEMPLATE, copied onto that project's own project/<name> branch as adr/
    └── ci/                ← adr-lint.yml, copied into the project's own .github/workflows/
```

Each adopting project's own `adr/` directory — its decision records, as
opposed to the org's — lives on a dedicated branch of *this* repo
(`project/<name>`), not copied into the project's own git history. The
project vendors this repo as a submodule and checks out its own branch; see
"Forking a new project" below.

## Namespaces and precedence

- **Org records:** `QM-NNNN`, numbered at ratification by this README's index.
- **Project records:** `ADR-NNNN`, numbered locally per project, starting at 0001.
- **Precedence:** QM records bind all projects. A project record may add
  constraints on top of a QM record; it may not waive one. A genuine
  exception is an *amendment to the QM record*, ratified at org level — never
  a project-level workaround.
- **Adoption by reference:** each project's `adr/` directory lives on its own
  branch of this repo, created from `main`. That branch's ancestry is the
  pin — no separate hash to hand-maintain. Org ratifications and amendments
  propagate by merging `main` into the project's branch — a reviewed commit,
  not an ambient change.

The drafting discipline (squash before ratification, append-only after,
numbering at ratification, one decision per record, banned-vocabulary lint)
is identical at both levels and is itself an org record: see
*Decision-record discipline* in `records/`.

## Forking a new project

The seed is proven — its first instance is the streaming-infrastructure
project, which serves as the reference implementation for a server/container
runtime; `project/qmetronome` (a branch of this repo, not a separate fork)
is the reference implementation of the branch-per-project ADR model below
for a non-server runtime.

1. **Add this repo as a submodule** at `governance/qm` in the new project.
2. **Create branch `project/<name>`** off `main` in this repo. On that
   branch, copy `project-seed/adr/` into a new top-level `adr/` directory
   (README + TEMPLATE, verbatim) — the same copy-verbatim discipline as
   before, now landing on a branch of this repo instead of the new
   project's own repository. Push the branch.
3. **Point the submodule at that branch's tip** (checkout the branch inside
   the submodule, commit the updated pointer in the new project); add
   `branch = project/<name>` to the new project's `.gitmodules` so
   `git submodule update --remote` tracks it going forward — the parent
   repo still records an exact commit each time, so builds stay
   reproducible.
4. **Wire CI:** copy `project-seed/ci/adr-lint.yml` into
   `.github/workflows/` verbatim — the ADR lint runs as shipped, no
   project-specific edits needed. Wire the license gate required by the
   open-license record along the path matching the project's runtime shape
   (SBOM-per-image, or a dependency-manifest-plus-allowlist per package
   ecosystem; see that record's Enforcement clause); a project without both
   is not instantiated, it is improvised.
5. **Seed the first project records** on that branch as numberless drafts
   by title; ratify per process. Project ADR-0001 is conventionally the
   project's adoption + scope record, but nothing enforces a particular
   first decision.
6. **Register** any carried patches in `registers/carried-patches.md` here —
   the register is org-level by design: a patch carried by one project is a
   commitment made by the org.

A fork onto a materially different project shape than the reference
instance — non-server, non-container, a different language ecosystem —
should expect step 5 to cost real translation effort, not just decision
effort: naming what a "deployment," an "image," or a "control plane" even
means for that shape, before a first record can be written. That cost is
expected overhead, not a signal of poor fit. The org corpus's own origin is
proof this runs both directions: this constitution was itself extracted and
generalized from a single project's experience (the streaming project's,
per `perspectives/session-transcript-2026-06-09.md`) — a first project of a
new class discovering the constitution needs to generalize is exactly how
this corpus is supposed to evolve.

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
| — | Human-only contributorship | Proposed | 2026-07-05 |

Handbook (policy, not records): public-by-default (with a defined promotion
path to record form), style guide (minimal, legible deliverables).

**Post-ratification step for the reference project:** once the org
open-license record is Accepted, the streaming project's ADR-0001 receives a
dated amendment recording adoption-by-reference of the org record. Its body
is untouched; the amendment aligns the instance to the doctrine.

**Post-ratification step for Human-only contributorship:** once Accepted,
`perspectives/README.md`'s Index table is migrated — its Author column stops
naming models; each existing entry's model name moves to a Notes/Tools
annotation, and the human who sponsored or submitted that perspective becomes
the Author of record.
