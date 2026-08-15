# Handoff — The exploration namespace, and three unmerged branches

| | |
|---|---|
| **Stamp** | `main` at `288bbc4`, 2026-08-15 16:10 UTC. **Every number on this page was true at that commit and nowhere else** — re-derive rather than quote, and delete this page when the work lands. |
| **Repo** | qm only. Nothing in any project repository was touched. |
| **Retrospective** | `perspectives/2026-08-15-stating-a-constraint-is-not-enforcing-it.md` — why, including the hole this work shipped and closed. |

## State

Three branches, all pushed, **none with a pull request**.

| Branch | Head | Carries | Base it wants |
|---|---|---|---|
| `evolve/exploration-branch-namespace` | `8045c33` | 2 commits, 7 files. The standard: `handbook/research-workspaces.md`, the `math/<slug>` namespace, `--per-head` on `check_one_pr.py`, the matching refusal in `check_pr_base.py`, README and `AGENTS.md` namespace lists, the corpus's own `one-pr-check.yml` | `main` |
| `math/hierarchical-complexity` | `0e6181a` | 1 commit, 4 files. `math/07-hierarchical-complexity/` (topic README + a reference document on the Model of Hierarchical Complexity) and `math/GLOSSARY.md` | `workspace/math-experiments` |
| `perspective/2026-08-15-a-namespace-with-one-direction` | `2308086` | 1 commit, 2 files. The finding about the namespace table | `main` |

`workspace/math-experiments` is **74 commits behind `main`** and has no
`.github/` directory, so none of the gates exist on it to run.
`project/codecartographer` is **15 behind**.

A fourth branch carries the retrospective:
`perspective/2026-08-15-stating-a-constraint-is-not-enforcing-it` at `e2ae50d`,
1 commit, 2 files, base `main`.

**The two perspective branches conflict with each other**, in
`perspectives/README.md` only — both add an index row at the same anchor, having
been cut from the same tip. Verified by dry-run merge. Resolve by taking both
rows in date order; nothing else in either branch overlaps.

## What is blocked, and on whom

**Two of the three cannot open a pull request.** `subcontrabass` holds one
non-`project/*` slot and **#58** (`evolve/governance-loop-poc -> main`, READY)
has it. The standard and the perspective both target `main`. Only
`math/hierarchical-complexity` is exempt, because the namespace it is in is the
one this work adds.

That is a human decision with an order to it: **close a pull request before
pushing its commits onto another branch**, or the push merges it. Do not fold
anything to make room without being asked.

**Verified, not inferred:** `check_one_pr.py --per-base 'project/*' --per-head
'math/*'` against the live PR list plus two simulated explorations exits 0; the
same list plus the two `main`-targeting branches above exits 1 and names #58,
#92, #93. The exemption does not loosen `main`.

## Decisions taken, 2026-08-15 — build these, in this order

Approved by the maintainer in session. They are design commitments, not
ratified records; each becomes an `evolve/*` branch when a slot is free.

1. **A namespace registry is the single declaration.** `ci/namespace-registry.yaml`
   holds each namespace's pattern, what it holds, its lifetime, its legal bases,
   whether it may be a head, and its slot rule. README's table and `AGENTS.md`'s
   list are **generated** from it; `check_pr_base.py` and `check_one_pr.py`
   **read** it rather than carrying their own globs. A namespace cannot then be
   documented without being enforced, or enforced without being documented —
   which is every defect this branch's own history records.
2. **The guard layers are a parallel redundancy checker, and their drift is
   calculated.** Three independent detectors of the same property: negative
   tests generated from the registry's bounds, the guard registry's
   route-around coverage, and the scheduled adversarial sweep. They must
   **agree**; disagreement is the signal, and the divergence is measured over
   time rather than resolved silently. This is the corpus's own
   correlated-defenses problem — `n_eff = n/(1+(n−1)ρ̄)` from the
   mathematical-limits perspective §4 is the metric for what three
   non-independent detectors are actually worth, and
   `math/03-effective-reviewer-count/` is where estimating ρ̄ is designed.
3. **Propagation triggers on the event, not the commit count.** A ratification,
   a `project-seed/**` change, or a new gate fires it. The trigger list lives in
   the registry with everything else, so it cannot drift the way the namespace
   list did. Its known weakness is recorded rather than designed around: this
   workspace went 74 commits with no qualifying event, so the redundancy checker
   in (2) is what surfaces a branch that fell behind without one.
4. **Work stays on branches without pull requests for now.** Not a queue, not a
   re-scoped slot. Branches are the durable artifact; this page is how they are
   found.

Two principles the maintainer set, which the above is shaped by: **avoid the
shape by design rather than resolving its symptom**, and **git should be
disappearing as a layer that interacts with humans** — link to hashes where a
reference is needed.

Applying the first to this page's own index row: hand-maintained index tables
conflict whenever two branches add an entry, and the fix is to stop having one,
not to document a merge ritual. That applies to `perspectives/README.md` and
`handbook/handoffs/README.md` alike, and folds into (1) — both are derived
documents whose only hand-set field is a human judgement.

## What is unfinished

| Item | Done looks like |
|---|---|
| The standard is unreviewed | #58 lands, then a draft PR `evolve/exploration-branch-namespace -> main` with `check_pr_base.py` output in the body |
| `workspace/math-experiments` is 74 behind and ungated | A `propagate/math-experiments-<date>` PR based on the workspace branch, merged not rebased. **This is the first use of the rule this work adds** — nothing has exercised it |
| The seed's `one-pr-check.yml` does not pass `--per-head` | Correct as it stands: `math/*` is corpus-specific, as `project/*` is. Revisit only if a project grows a research workspace |
| Nothing detects a namespace spelled with two placeholders | `propagate/<name>` / `<target>` / `<slug>` all named one namespace mid-session. Fixed by hand; no check exists |
| **#58 states two command surfaces** | Its `AGENTS.md` line 27 calls `uv run qm --help` "the whole surface"; lines 130 and 138 still instruct `python project-seed/ci/check_pr_base.py` and `run_workflows_locally.py`. Both work — `qm` wraps those scripts with flag passthrough, and cli.py's own docstring says forks execute them directly. Done: one is the source and the other is generated from it, under the registry decision above, so a reader is never choosing between two spellings of one rule |
| `perspectives/README.md` Status for the mathematical-limits row | Setting it to `Responded` is a maintainer action. The linked-work fact is already recorded there; the Status is not mine to set |

## What I could not verify

- **That `math/*` is the right name (E4).** It matches `perspectives/README.md`,
  which already cites "a `math/` workspace" as the shape of a Responded
  perspective. A second research workspace needs its own namespace by the same
  pattern and there is no second workspace to test that against.
- **That a `workspace/*` head is a legal shape.** `check_pr_base.py` does not
  refuse one. Nothing has needed it and I did not test it.
- **Remote CI.** Everything here is the local runner (`uv run qm preflight`
  once #58 lands; `python project-seed/ci/run_workflows_locally.py` is the same
  thing on today's `main`, which has no CLI). 18/18 on
  `evolve/exploration-branch-namespace` at `8045c33`, exit code read directly.
  The runner does not execute `uses:` steps or reproduce the runner image, and
  no workflow has run on GitHub for any of these branches.
- **The command spellings on this page assume #58.** `qm slot`, `qm branch`
  and `qm preflight` do not exist on `main` — there is no `pyproject.toml`,
  no `ci/cli.py` and no entry point there. They arrive with
  `evolve/governance-loop-poc`, which is planned to land first. Until it does,
  the seed scripts under `project-seed/ci/` are the runnable form, and remain
  so for any fork that never gets the CLI.

## Standing constraints in force

- **Other sessions are completing the `governance/qm` submodule migration in
  codecartographer.** I touched none of it: not `governance/qm`, not
  `project/codecartographer`, not `.gitmodules`, not any propagation. There is
  an untracked `governance/qm` directory in that clone alongside the tracked
  `docs/qm` — two checkouts of this repo at different commits — and reconciling
  it belongs to that work, not this.
- **`AGENTS.md` and `README.md` are also edited by #58.** My edits to both are
  additive — a table row, a list item, and one paragraph — so the merge is
  cheap, but they will conflict. #58's copy of `AGENTS.md` still lists three of
  the six namespaces; whoever resolves should take both changes rather than
  either side.
- **Nothing here is ratified or ratifiable.** A workspace binds nothing and a
  perspective binds nothing. The only binding artifact this work touches is the
  handbook, which carries force by pointing at records and never on its own.

## The single next action

Land or fold #58. Everything else on this page is waiting on that one slot.
