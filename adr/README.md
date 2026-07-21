# Architecture Decision Records — Process & Handoff

This directory is the project's decision memory. This file is the contract
for producing and maintaining it. The discipline exists because decision
documents drift in a specific, predictable way — drafts accumulate references
to their own revision history, numbers get assigned before ratification and
then need "renumbering," and supersession language leaks into documents that
were never published. The rules below make the discipline mechanical instead
of dependent on any one contributor's (or assistant's) memory.

## Adopted org records

This project adopts the QM constitution by reference. Org records bind this
project; project records may tighten them, never relax them. A genuine
exception is an amendment ratified at org level.

This directory lives inside the `docs/qm` submodule, on this project's own
dedicated branch (`project/codecartographer`, created from `main`) — not
copied into codecartographer's own git history. The branch's ancestry *is*
the pin: there is no separate commit hash to hand-maintain here. `git log
--first-parent` on this branch shows exactly which org state was adopted
and when it was last refreshed.

Bumping the pin is merging `main` into this branch - a normal git
operation, reviewed the same way any other commit to this branch is.

## The one rule that prevents most drift

> **Before ratification, documents have no memory. After ratification, they
> have nothing but memory.**

- A **draft** is rewritten in place as understanding improves — squashed, as
  if the final position had been held from the beginning. Git is the
  archaeology; prose is not. A draft never says "previously," "supersedes the
  earlier stance," or "corrected in review."
- An **Accepted** ADR is append-only. Its body is never silently edited.
  Changes are dated entries under **Amendments**; reversals are a new ADR
  that **supersedes** it. Supersession is a relation between *ratified*
  documents only.

## Lifecycle

```
Draft ──▶ Proposed ──▶ Accepted ──▶ (Amended*) ──▶ Deprecated | Superseded by ADR-NNNN
  ▲           │
  └── squash ─┘   (any change before Accepted = rewrite in place)
```

| Status | Meaning |
|---|---|
| **Draft** | Being written. Numberless (`ADR-XXXX`). Rewritten freely. |
| **Proposed** | Complete; pending a named input (`Pends on`) or ratification. Numberless. |
| **Accepted** | Ratified. Number assigned. Append-only from here. |
| **Deprecated** | No longer applies; nothing replaced it. Body intact. |
| **Superseded** | Replaced by a named ADR. Body intact, header points forward. |

## Numbering

Numbers are assigned **at ratification, by the index below, in order of
acceptance** — never during drafting. Drafts reference each other by *title*.
Once assigned, a number is permanent; gaps are fine; numbers are never
reused. Project numbering is local (`ADR-NNNN`); org records are `QM-NNNN`.

## Authoring rules

1. **One decision per ADR.**
2. **Org records are constitutional** — component selections must pass the
   open-license record; gaps route through its upstream-contribution
   remediation; seams pass the replaceability test.
3. **Alternatives are written honestly** — each with the real reason it lost.
4. **Every ADR has revision triggers** — observable events, not vibes.
5. **Open questions are not decided by stealth** — undecided input → status
   Proposed with an explicit `Pends on`.
6. **External history is context; internal history is noise.**
7. **Build-time patches are registered** in the org carried-patch register
   before the patch ships.

## Drafting-session handoff (humans and AI assistants alike)

**Inputs to provide the session:** this file; the pinned org records
(minimally the open-license record); the current index; the project design
plan and any ADRs being touched.

**Session obligations:** plan first, with a contradiction check against the
org records and the index; squash continuously (the chat may discuss a
position change; the document may not); never assign numbers, never
renumber, never write supersession language into a draft; mark pending human
decisions as Proposed with `Pends on`; end by outputting drafts, the proposed
index diff, and the open-question list. Ratification — status flip, number
assignment, index update — is a **human commit** naming the record.

**Session prohibitions (verbatim-banned):** "takes the ADR-NNNN slot,"
"the set renumbers," "supersedes the stance from the earlier review/draft,"
"retroactive" framing for adoption-time rules, edits to an Accepted body
outside Amendments.

## CI enforcement

The ADR lint (banned vocabulary in drafts; numbered filenames not
Accepted+; Accepted bodies modified outside Amendments; index/directory
mismatch) runs from codecartographer's own `.github/workflows/adr-lint.yml`
(ported from `project-seed/ci/adr-lint.yml`, path adjusted for this
project's `docs/qm` submodule mount point instead of `governance/qm`). The
license gate required by the org open-license record is doctrine, not one
fixed script: wire an SBOM-per-image gate for container and server
runtimes, or a dependency-manifest-plus-allowlist gate per package
ecosystem otherwise (see that record's Enforcement clause). Both run in the
same pipeline as the ADR lint — the constitution and its enforcement ship
together.

## Index

| # | Title | Status | Date |
|---|---|---|---|
| | | | |

Drafts in flight (numberless, by title):
- *Unify parser/cache architecture around `ParserRegistry` + `batch_whole_tree`* — `DRAFT-parser-cache-unification.md`
- *Golden Layout as the primary application shell* — `DRAFT-golden-layout-primary-shell.md`
- *Compound hierarchical layout (dirs → files → symbols)* — `DRAFT-compound-hierarchical-layout.md`
- *`CacheService` and `graphbase` stay separate stores* — `DRAFT-cache-service-vs-graphbase.md`
- *Generalize dock panels into a registry; add a window-add menu* — `DRAFT-panel-registry-and-add-window-menu.md`
- *Hierarchical drag propagation, per-depth labels, and compound layout spread improvements* — `DRAFT-d3-hierarchy-layout-improvements.md`
- *Wire graphbase as a named bookmark store via /db/bookmarks* — `DRAFT-graphbase-bookmark-integration.md`
- *Formalize the graphbase submodule interface; keep it a submodule* — `DRAFT-graphbase-submodule-interface-contract.md`
- *Code-map navigation: source-ordered layout, depth-4 hierarchy, view-source* — `DRAFT-code-map-navigation.md`
- *GitHub token resolution order: gh CLI keyring primary, env vars secondary* — `DRAFT-github-token-resolution.md`
