# Handoff — the consolidation landed; what remains

**Date:** 2026-09-20. **Repos:** dossier, codecartographer, datum, apothecary, alfred, qm. **Author:** Peter Kagstrom.

The body of unpushed work that `the-estate-has-one-copy.md` (retired)
and `the-menu-contract-nobody-could-fetch.md` (retired)
described as having one copy on one disk has been pushed, reviewed stage by
stage, and **merged to `main` in seven repositories** with merge commits
(never squash or rebase): dossier #56, qmcp #35, looksatwords #22, rad #5,
codecartographer #98, datafactorio #10, and **qm #110** (the constitution's
consolidation — the status documents under `status/`, the families, ~15 DRAFT
records, the loose-ends join). Every merge ratified nothing: the records are
DRAFT for a person, and `main` asserts nothing until a tag. Those two pages'
findings are settled and both pages are retired: the estate's *preserve* half
landed and its *delete* half is queued below; the menu-contract's nine-cells
cell↔angle finding was resolved by rad's "let the seam take a cell" change,
now on rad's `main`.

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

- **Prune the merged branches across the estate** — the second half of
  `the-estate-has-one-copy.md` (retired with this page), which sequenced
  *preserve, then delete*. Preserve is done: every at-risk line now has a
  second copy on origin. `uv run qm branches --repo <path>` per repository
  names what is fully merged and safe to delete; it takes no `--delete` flag
  by design, so the deletion is a person's act, repo by repo.

Each is its own PR, one at a time per repo. **None rebases clean onto the
moved `main`** — established by a real trial merge in a scratch worktree, not
by `git merge-tree`, which on this machine's git 2.37 misreports every branch
as clean (the tool errors on `--write-tree` and a grep for `CONFLICT` in the
error finds nothing; item 10 in `AGENTS.md`). Expect the reconciliation pattern
#110 needed: a branch that predates what `main` added conflicts first in
generated artifacts and index files, which are resolved by regenerating, and
only sometimes in source.

- **dossier** — `evolve/rad-conformance-replay` (+8; conflicts only in the
  regenerated `docs/screenshots/first-run.gif` — regenerate, trivial);
  `feat/the-terminal-replays-the-governed-vectors` (+2; only the generated
  `docs/commands.md` — regenerate); `wip/delta-entity-type-local` (+1; **real
  source conflicts** in `alembic/env.py`, `src/dossier/api/main.py`,
  `src/dossier/cli.py` — a `wip` line, possibly stale; read before rebasing).
  All signed and trailer-clean.
- **codecartographer** — `feat/the-monitor-derives-the-system` (+1;
  `.gitignore` and `web/package.json` trivial, `web/src/.../graph_renderer.ts`
  real); `test` (+4, coordinate/vectors consumer work; only `web/package.json`;
  rename off `test` before pushing); `cleanup/2026-07-21-full-review` (+3, the
  July governance-adoption line; conflicts in the three seed workflow files and
  the `governance/qm` pin — **likely superseded** by the adoption `main` already
  carries; confirm its content is absent from `main` before spending an
  afternoon on it).
- **qm** — `perspective/2026-08-30-a-guard-that-reads-prose` (+1; only the
  `perspectives/README.md` index row — re-add it). The other session's
  `evolve/games-family` (worktree `repos/qm/qm-games-family`) was cut from the
  local stage `test` and must rebase onto `main`.
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
