# Handoff — Run the next harness test

**Repo:** qm, plus one project repository of your choice.
**Blocks on:** nothing. The harness is in place; this is its first real trial.

*Stamped 2026-08-09. `qm` at `3496ad0` plus the harness commit on
`evolve/ci-tooling-fixes` (#36). Every number on this page was true then.
Re-derive before acting; do not quote these figures as current.*

---

## What exists now

| Piece | Path | What it does |
|---|---|---|
| The contract | `handbook/async-contract.md` | Ten clauses, each naming the event that produced it |
| session open | `adapters/claude-code/commands/cowork.md` (optional adapter) | Establishes the four facts `AGENTS.md` requires before writing |
| `/preflight` | same directory | Runs every gate and reports what could not be reproduced |
| `/handoff` | same directory | Closes a session: handoff page plus retrospective |
| The brief builder | `project-seed/ci/cowork_context.py` | The facts behind `/cowork`, with `unknown` as a real value |
| The slot check | `project-seed/ci/check_one_pr.py` | One open PR per repository, per contributor |
| Its workflow | `project-seed/ci/one-pr-check.yml` | Copy into `.github/workflows/` per project |
| The status document | `ci/harness_status.py` → `harness-status.json` | Headless: two layers, org and machine |
| The dashboard | `ci/harness_dashboard.py` | Reads only that document; runs nothing |
| The workspace | `ci/workspace.yaml` + `ci/make_workspace.py` | The repository roster, and a multi-root workspace built from it |

This repository's `.claude/commands/` and `.vscode/` are symlinks into
`project-seed/ide/`. Edit the seed; never the pointer.

## The test

The harness has been exercised by its author, which is the weakest possible
evidence. What it has not survived is a session that did not build it.

**Run one ordinary piece of work, in one repository, entirely through the
harness**, and record where the harness got in the way rather than helping.

1. Open with `/cowork`. Do not read anything else first — the point is whether
   the brief is sufficient on its own.
2. Do the work.
3. `/preflight`, then the pull request if it passes.
4. Close with `/handoff`.

**What to record, as you go rather than afterwards:**

- Every question you had to ask that the brief should have answered.
- Every fact in the brief you did not trust, and what you checked instead.
- Every time a clause sent you the wrong way, or was silent when you needed it.
- How long `/cowork` took, and whether you would run it again unprompted.

That record is the deliverable. It goes in a retrospective, per
`handbook/style-guide.md`, and the fixes it implies go into `project-seed/` —
not into the local copy.

## Adoption is not done

`one-pr-check.yml` runs in this repository only. No project has copied it, and
copying it is part of propagation — `handbook/propagation-runbook.md`, Part B,
where the seed files are re-copied. **A merge does not fix a copy**: a project
whose pin is current still has no slot check until that file lands in its
`.github/workflows/`.

The same is true of `.claude/commands/`. A project that bumped its pin before
today has the contract available through the submodule and no commands.

## Known state, and one thing that needs a human

At the stamp, one repository was over the limit: **apothecary**, where
`subcontrabass` held **#8**, **#12** and **#13** — and #13 is based on #12's
head, so folding them has an order. Closing or folding is a human's call and
not an agent's, exactly as `propagate/datum-2026-08-08`'s closed pull request
was. It is recorded here so it stops being invisible.

Seven repositories carry `phase: unknown` in `ci/workspace.yaml`: alfred,
datum, `private-32`, `private-33`, factorio-sysops, dossier, qmcp. The ladder
is defined at the top of that file. `unknown` is the honest value and not a
synonym for dormant; answering is a human's call, and the answer is an edit to
that file.

## What this handoff does not authorise

Ratifying anything. Merging to `main` or to a `project/*` branch. Closing
somebody's pull request. Deleting or force-pushing a branch. Bumping a
project's pin.

## The failure this is written against

The harness's own tests found four checks that passed against a broken tool,
in one afternoon — including one that matched a phrase produced by a different
section of the same page. **Every signal needs a fixture in which it reports
bad**, and after writing that fixture, break the tool in the way it names and
confirm the test fails. A signal only ever observed green has not been tested;
it has been watched.
