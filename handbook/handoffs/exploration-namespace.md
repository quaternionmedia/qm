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

## What is unfinished

| Item | Done looks like |
|---|---|
| The standard is unreviewed | #58 lands, then a draft PR `evolve/exploration-branch-namespace -> main` with `check_pr_base.py` output in the body |
| `workspace/math-experiments` is 74 behind and ungated | A `propagate/math-experiments-<date>` PR based on the workspace branch, merged not rebased. **This is the first use of the rule this work adds** — nothing has exercised it |
| The seed's `one-pr-check.yml` does not pass `--per-head` | Correct as it stands: `math/*` is corpus-specific, as `project/*` is. Revisit only if a project grows a research workspace |
| Nothing detects a namespace spelled with two placeholders | `propagate/<name>` / `<target>` / `<slug>` all named one namespace mid-session. Fixed by hand; no check exists |
| `perspectives/README.md` Status for the mathematical-limits row | Setting it to `Responded` is a maintainer action. The linked-work fact is already recorded there; the Status is not mine to set |

## What I could not verify

- **That `math/*` is the right name (E4).** It matches `perspectives/README.md`,
  which already cites "a `math/` workspace" as the shape of a Responded
  perspective. A second research workspace needs its own namespace by the same
  pattern and there is no second workspace to test that against.
- **That a `workspace/*` head is a legal shape.** `check_pr_base.py` does not
  refuse one. Nothing has needed it and I did not test it.
- **Remote CI.** Everything below is `run_workflows_locally.py`, 18/18 on
  `evolve/exploration-branch-namespace` at `8045c33`, exit code read directly.
  The runner does not execute `uses:` steps or reproduce the runner image, and
  no workflow has run on GitHub for any of these branches.

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
