# Handoff — the consolidation landed; what remains

**Transient.** Delete this page when its work lands; the method is in
`handbook/consolidation-runbook.md`.

## Stamp

Every figure on this page is true at these commits and nowhere else.
Re-derive before quoting — `uv run qm estate` is the reading, and the estate
moved twice under this session while it worked.

| repository | `origin/main` | date |
|---|---|---|
| qm | `5cc7a555e6a4` (#111); the open #112 head is `8ebd0f8ec2bb` | 2026-09-20 |
| dossier | `bd322d38d496` (#56 merged) | 2026-09-20 |
| qmcp | `3e2571186a1b` (#35 merged) | 2026-09-20 |
| looksatwords | `32d337191f58` (#22 merged) | 2026-09-20 |
| rad | `a39d3bfd163a` (#5 merged) | 2026-09-20 |
| codecartographer | `4e30271e6b70` (#98 merged) | 2026-09-20 |
| a private roster entry (it is in `ci/workspace-private.yaml`, not here) | `7c47d2809bd3` (its #10 merged) | 2026-09-20 |
| apothecary | `f1c1543156f7` (#21 open) | 2026-09-20 |
| datum | `72b04348b3f9` (#2 open) | 2026-09-20 |
| alfred | `7fff7ae01bce` (untouched) | 2026-09-20 |

**Standing constraints in force.** *Keep everything local* is **not** in
force — this session delivered, and every merge was a person's approval, stage
by stage. One exception is deliberate and looks like an oversight: qm's local
branch `test` is the ephemeral stage named by
`records/DRAFT-a-stage-is-recorded-and-main-receives-releases.md`; it was
fast-forwarded to `main` and is **not pushed on purpose**. Advancing it after
#112 merges is that record's own decision, not a reset. Merging to `main`
ratified nothing: every record is DRAFT for a person, and `main` asserts
nothing until a tag.

## State

Seven repositories were merged to `main` with merge commits (never squash or
rebase), each stage approved by a person: dossier #56, qmcp #35, looksatwords
#22, rad #5, codecartographer #98, a private repository's #10, and qm #110 — the
constitution's consolidation, which joined the `test` line with the loose-ends
tracker (four reconciliations, all because #110 predated rules the line
added). The two prior handoffs on this work are retired: the estate page's
*preserve* half landed and its *delete* half is queued below; the
menu-contract's nine-cells finding was resolved by rad's "let the seam take a
cell". The why is `perspectives/2026-09-20-the-consolidation-cycle.md`.

**Open, pushed, with a pull request:**
- **qm #112** `evolve/smooth-the-consolidation-cycle` — not a draft; green on
  every gate; level with `main`. Carries `uv run qm estate`, `uv run qm merge`,
  `handbook/consolidation-runbook.md`, the instruction-set refinements, this
  page, and the retrospective. **Held by the person for a closer read.** It
  holds qm's one non-project slot.
- **apothecary #21** `consolidate/2026-09-19` — green, `MERGEABLE`; the
  maker-family consolidation; folds in every apothecary leftover. Held by
  decision at the review.
- **datum #2** `wp3-firmware` — green, `MERGEABLE`; its cross-repository gate
  `pinned-apothecary-renders-our-parts` passes. Held by decision at the review.

**Local only, no pull request** — the leftover queue, one PR per repository at
a time. **None rebases clean onto the moved `main`** (E1, by a real trial
merge in a detached worktree; `git merge-tree --write-tree` on this machine's
git 2.37 misreports every one as clean). Expect the reconciliation pattern
#110 needed: conflicts first in regenerated artifacts and index files,
resolved by regenerating, and only sometimes in source.

- dossier — `evolve/rad-conformance-replay` (+8; conflict only in the
  regenerated `docs/screenshots/first-run.gif`); `feat/the-terminal-replays-the-governed-vectors`
  (+2; only the generated `docs/commands.md`); `wip/delta-entity-type-local`
  (+1; **source** conflicts in `alembic/env.py`, `src/dossier/api/main.py`,
  `src/dossier/cli.py` — a `wip` line, possibly stale). All signed and
  trailer-clean.
- codecartographer — `feat/the-monitor-derives-the-system` (+1; `.gitignore`
  and `web/package.json` trivial, `graph_renderer.ts` real); `test` (+4; only
  `web/package.json`; rename off `test` before pushing);
  `cleanup/2026-07-21-full-review` (+3; the seed workflow files and the
  `governance/qm` pin — E3: likely superseded by the adoption `main` carries;
  confirm before spending time on it).
- qm — `perspective/2026-08-30-a-guard-that-reads-prose` (+1; only the
  `perspectives/README.md` index row). The `adr/*-charter-by-name`,
  `fix/*-seed-refresh` and `rescued/rad-integration` branches are project
  namespace records whose `project/<name>` branch is their git ancestor: route
  each to that branch (records go in; `main` reaches it via
  `propagate/<name>-<date>`), **never a PR into `main`**.
  `workspace/math-experiments` deletes chunks of `records/` — not a candidate.

## Unfinished, and what done looks like

- **The leftover queue above.** Done: each branch rebased onto current
  `main`, its gates green, one pull request per repository, merged by the
  person; `uv run qm estate` then reports no one-copy branch in that
  repository. Start with the trivial ones (a regenerated artifact or an index
  row) and rename off `test` before pushing.
- **Prune the merged branches across the estate** — the second half of the
  retired estate page, unblocked now that every at-risk line has a second
  copy. Done: `uv run qm branches --repo <path>` per repository reports
  nothing merged-and-deletable; it takes no `--delete` flag by design, so the
  deletion is the person's act.
- **Merge #112, then advance the stage.** Done: #112 merged with a merge
  commit; qm's local `test` fast-forwarded to that `main`; the `qm-cycle`
  worktree removed.
- **`qm estate --trial-merge`** (named by the retrospective §2). Done: the
  survey performs the worktree trial merge for each one-copy branch and
  reports conflicts per file, so no session reaches for `merge-tree` again.
- **A guard for seam-crossing UI workers** (retrospective §3, dossier). Done:
  a test that enumerates every threaded worker that can reach the network and
  fails when one is missing from `tests/ui/conftest.py`'s stub list.
- **Preflight counts `E` apart from `N`** (retrospective §4). Done: the
  signature summary reports "could not be checked" as its own figure.

## Blocked on a person

- **alfred — DO NOT PUSH THE SUBMODULE PIN.** The working tree moves the
  `governance/qm` gitlink from `e76827d` to `3c88df7`, a local-only commit on
  no origin ref (E1, `git ls-remote`). Pushing it records a pin no consumer can
  fetch. Choose: reset to `e76827d`, or forward to `origin/project/alfred`
  (`314ca5c`). The rest of the dirt is benign: `dossier.db`/`__pycache__` junk,
  an accidental lossless `data/.gitignore` deletion, a coherent `al`+`thin.yml`
  feature, an undeclared `uv.lock` (pdm→uv migration question).
  `release/0.3.0` (+40, == `test/validate-onboarding-claims`, checked out in
  another live worktree) is the consolidation candidate. #113 is `mrharpo`'s;
  by one-PR-per-*contributor* it may not block this slot.
- **qmcp's outbound licensing class.** #35 recorded MIT as *current state*,
  not a ratified class; qmcp is a candidate AGPL service per the
  outbound-licensing record — declare it in the adoption record.
- **rad's `deploy` job is red on `main`** — GitHub Pages is not enabled for
  the repository. A setting, not code; E3 that nothing else is red there.
- **A live share link** committed in
  `handbook/handoffs/views-declare-what-they-need.md` since 2026-08-26 —
  `uv run qm leaks` names it; no workflow gates it on pull requests. Redact,
  or add the account to the placeholders if it is nobody's.
- **Two held pull requests** — datum #2 and apothecary #21 — merge or close is
  the person's.
- **`main`'s working tree names private repositories.** `uv run qm
  private-names --strict` (local-only by design — `registries.yml` says why)
  finds a private repository's name used as a repository in the committed
  roster `ci/workspace.yaml`, in `families.json`, `status/harness.yaml`, and
  in the games-family pages #111 added. Private roster entries belong in the
  gitignored `ci/workspace-private.yaml`; the rest is a redaction or a
  placeholder. This page carried two such names until its closing pass ran
  the check; the runbook's Step 3 now runs it before any push. One doc nit
  beside it: `ci/check_private_names.py`'s docstring says CI runs it with
  `--strict`, and no workflow does.

## Could not be verified (inference)

- Whether another qm session is live now. #111 merged under this session and
  the memory says its worktree and branch are gone; `git worktree list` is
  the reading.
- Whether the leftover branches' source conflicts are shallow. The trial merge
  named the files, not the depth.
- That `cleanup/2026-07-21-full-review` is superseded — the adoption `main`
  carries looks like the same work, and nobody diffed them.

## Standing residuals (systemic, not per-PR)

Submodule pins are branch-tip SHAs on `project/<name>`; a session that
force-pushes or GC-prunes one strands every consumer's `check-submodule-refs`.
Recorded-not-compared artifacts (gifs, screenshots, doc indexes) are ungated —
drift ships silently but fails nothing. codecartographer's private submodule pin sits
on a non-default branch; qmcp's `REUSE.toml` `**`=MIT catch-all neuters the
missing-license arm; `web/` in codecartographer is ungated on `pull_request`.
