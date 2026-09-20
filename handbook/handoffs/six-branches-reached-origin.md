# Handoff — the consolidation landed; what remains

**Date:** 2026-09-20. **Repos:** dossier, codecartographer, datum, apothecary, alfred, qm. **Author:** Peter Kagstrom.

The body of unpushed work that [`the-estate-has-one-copy.md`](the-estate-has-one-copy.md)
and [`the-menu-contract-nobody-could-fetch.md`](the-menu-contract-nobody-could-fetch.md)
described as having one copy on one disk has been pushed, reviewed stage by
stage, and **merged to `main` in seven repositories** with merge commits
(never squash or rebase): dossier #56, qmcp #35, looksatwords #22, rad #5,
codecartographer #98, datafactorio #10, and **qm #110** (the constitution's
consolidation — the status documents under `status/`, the families, ~15 DRAFT
records, the loose-ends join). Every merge ratified nothing: the records are
DRAFT for a person, and `main` asserts nothing until a tag. Those two pages'
findings are settled; retire them when you next touch the queue.

This page is only what is left.

## Open by decision (a person chose to hold them)

- **datum #2** — WP-3 firmware, the pre-HIL run, a pinned enclosure. Green,
  `MERGEABLE`, its `pinned-apothecary-renders-our-parts` gate passes. Skipped
  at the review; merge when the person is ready.
- **apothecary #21** — the maker-family consolidation (enclosure, photos into
  pieces, firmware toolchain, viewer range). Green, `MERGEABLE`; folds in every
  apothecary leftover. Skipped at the review. Residual: its E2E/firmware tests
  use real sockets and bounded sleeps, so a post-merge re-run could flake.

## Now unblocked — the leftover queue (slots are free)

Each is its own PR, one at a time per repo, cut from the **new** `main`
(rebase first; the old base moved). Redundant leftovers already in `main` are
omitted.

- **dossier**: `evolve/rad-conformance-replay` (+8, replay rad's governed
  vectors and prove this host's conformance), `feat/the-terminal-replays-the-governed-vectors`
  (+2), `wip/delta-entity-type-local` (+1). All signed and trailer-clean.
- **codecartographer**: `feat/the-monitor-derives-the-system` (+1),
  `cleanup/2026-07-21-full-review` (+3, governance adoption),
  `test` (+4, coordinate/vectors consumer work — rename off `test` before
  pushing).
- **qm**: `perspective/2026-08-30-a-guard-that-reads-prose` (+1) — the only
  org content that was not in #110; trivially rebases onto `main`. The other
  session's `evolve/games-family` (worktree `repos/qm/qm-games-family`) was cut
  from the local stage `test` and must rebase onto `main`.
- **qm project namespaces**: every `adr/*-charter-by-name`,
  `fix/*-seed-refresh` and `rescued/rad-integration` branch has its
  `project/<name>` branch as git ancestor — route each to that branch
  (records go in; `main` reaches it via `propagate/<name>-<date>`), **never a
  PR into `main`**. `workspace/math-experiments` deletes chunks of `records/`
  — not a PR candidate.

## Deferred — needs a person

- **alfred — DO NOT PUSH THE SUBMODULE PIN.** Its working tree moves the
  `governance/qm` gitlink from `e76827d` to `3c88df7`, a **local-only**
  perspective commit on no origin ref (verified with `git ls-remote`).
  Pushing it records a pin no consumer can fetch and breaks
  `git submodule update`. Choose: reset to `e76827d`, or forward to
  `origin/project/alfred` (`314ca5c`). The rest of the dirt is benign:
  `dossier.db`/`__pycache__` junk, an accidental lossless `data/.gitignore`
  deletion, a coherent `al`+`thin.yml` "thin dev stack" feature, an undeclared
  `uv.lock` (pdm→uv migration question). `release/0.3.0` (+40, ==
  `test/validate-onboarding-claims`, checked out in another live worktree) is
  the consolidation candidate. #113 is `mrharpo`'s, so by
  one-PR-per-*contributor* it may not block this slot.
- **qmcp's outbound licensing class.** #35 recorded the tree as MIT = *current
  state*, not a ratified class; qmcp is a candidate AGPL service per the
  outbound-licensing record — declare it in the adoption record.
- **rad's `deploy` job is red on `main`** — GitHub Pages is not enabled for the
  repo. A repo setting, not code; pre-existing.
- **qm's local stage `test`** is 9 behind `main` (main has all of it).
  Advancing it for the next cycle is the stage record's own decision, not an
  automatic reset.

## Standing residuals the bolster pass surfaced (systemic, not per-PR)

- Submodule pins are branch-tip SHAs on `project/<name>`; a session that
  force-pushes or GC-prunes one strands every consumer's `check-submodule-refs`.
- Recorded-not-compared artifacts (gifs, screenshots, doc indexes) are
  ungated — drift ships silently but fails nothing.
- codecartographer's `graphbase` pin sits on a non-default branch; qmcp's
  `REUSE.toml` `**`=MIT catch-all neuters the missing-license arm; `web/` in
  codecartographer is ungated on `pull_request`.

## What to distrust in this page

Counts and states are one run at one commit (2026-09-20, qm `main` at
`1157fa2a`); re-derive before quoting. The two "open by decision" PRs may
have moved.
