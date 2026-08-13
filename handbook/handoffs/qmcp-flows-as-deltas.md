# Handoff — Managing qmcp's Flows as dossier Deltas

**Goal.** Plan and track qmcp's flow work as `Delta` rows in dossier, so the
change management for one project's workflows lives in the tool built for it
rather than in a roadmap file nobody can query.

**State: blocked, three steps deep.** The vehicle is not on dossier's `main`,
dossier's slot is spent, and a third of the thing to be planned exists on one
disk with no ref. Each step below is small; the order is the whole content of
this page.

*Stamped 2026-08-12. `qm` `main` at `104361a`, this page written on
`evolve/git-hygiene-and-handoff` at `6b621b6`. `dossier` `main` at `604efb8`,
`feature/delta-entity-type` at `393450f`, `wip/delta-entity-type-local` at
`3dc8192`. `qmcp` `main` at `85013c5`, `feat/pydantic-ai-integration-docs` at
`a3f827d`. Every figure was true at those commits — re-derive before acting.*

---

## The critical path

| # | Step | Repo | Blocked by |
|---|---|---|---|
| 1 | Get the uncommitted flow work onto a ref | qmcp | nothing — it is the first thing |
| 2 | Land #12 to free the slot | dossier | a human un-drafting it |
| 3 | Re-parent the delta migration, open the delta PR | dossier | step 2 |
| 4 | Create one delta per qmcp work item | dossier + qmcp | step 3 |

Steps 1 and 2 are independent and can run in either order. Nothing in 3 or 4
can start before both.

## Step 1 — qmcp has 3,646 lines of Python on no ref

This is the highest-risk item on this page and it is not a governance
observation. Measured in `c:\Users\peter\repos\qm\qmcp` with
`feat/pydantic-ai-integration-docs` (`a3f827d`) checked out:

| | |
|---|---|
| Untracked Python, on **no ref** | 3,646 lines across 14 files |
| Tracked but uncommitted | 20 files, +715 / −976 |

`git log --all -- qmcp/cookbook/` returns nothing, and no ref under
`refs/heads` or `refs/remotes/origin` carries `tests/test_cookbook.py` —
checked by `git cat-file -e` per ref rather than by reading the working tree.

The largest untracked files are `qmcp_mcp.py` (544), `tests/test_qmcp_mcp.py`
(535), `tests/test_cookbook.py` (330) and `qmcp/cookbook/persistence.py` (329).
Three flows — `plan_council.py`, `qc_release.py`, `change_impact.py` — are
untracked, and two others (`local_dev_db.py`, `local_mcp.py`) are deleted in
the working tree only.

**`docs/ROADMAP.md` is one of the 20 modified files**, and the modification is
the part that matters. The committed roadmap ends at **Phase 7** and declares
all phases complete. The working tree adds a **Phase 8 — Composable Cookbook &
MetaflowRunner**, ticked complete, describing exactly the untracked files
above. So a reader of the repository sees seven phases; a reader of the disk
sees eight. Read `origin/<ref>:docs/ROADMAP.md`, not the file, until this
lands.

*Done* is those files on a branch with a pull request. qmcp's slot is spent by
**#21** (adopt the constitution, draft, additions-only), so this needs #21 to
land first or it needs to go on #21 — which would change #21 from an
additions-only governance change into a feature branch, and that is a decision
rather than a keystroke.

## Step 2 — dossier's slot is held by a pull request that is ready

**#12** (`governance/refresh-seed-copies` → `main`, `ae183d1`): draft,
`MERGEABLE`, and all six checks green — `adr-lint`, `licenses`, `reuse`,
`check-submodule-refs` ×2, GitGuardian. It is waiting on nothing but a human
leaving draft, which is the assignee's call and not a session's.

Until it lands or closes, dossier holds no free slot and the delta pull request
cannot open. That is `handbook/async-contract.md` §1, and folding the two is not
the answer: a seed-workflow refresh and a new entity type are unrelated changes.

## Step 3 — the delta branch needs one migration edit before it can land

See [`dossier-delta-review.md`](dossier-delta-review.md) for the full review
brief. The one fact that belongs here, because it blocks this milestone: the
delta migration and `main`'s migration chain **both descend from
`004_full_name`**, so merging produces two alembic heads.

```
004_full_name ─┬─ 005_governance ─ 006_disk ─ 007_reclaim ─ 008_release   (main)
               └─ 005_delta_tables                                        (delta branch)
```

The revision identifiers do not collide — they are `005_governance` and
`005_delta_tables`, distinct strings — so nothing errors on import. `alembic
upgrade head` is what fails, with multiple heads present. The fix is
re-parenting `005_delta_tables` onto `008_release`, one line, plus renaming the
file so the number stops lying.

## Step 4 — what becomes a delta

The `Delta` model carries `name`, `title`, `phase`, `priority`, `delta_type`,
and optional `issue_number` / `pr_number` / `branch_name`, with `DeltaLink`
joining to issues, pull requests, branches, docs and other deltas. qmcp's work
maps onto it directly.

From the **committed** roadmap's Next Steps, one delta each:

| Delta | `delta_type` | Note |
|---|---|---|
| topology-runtime-execution | feature | Pipeline, Council and the rest, executing rather than registered |
| cicd-pipeline | chore | qmcp has no workflows; the org's slot check is one of them |
| hitl-api-integration | feature | `HumanInLoopMixin` against the HITL endpoints |
| async-runner | feature | |
| authn-authz | feature | |
| hitl-webhooks | feature | |
| backend-options | feature | Redis / PostgreSQL |
| k8s-manifests | chore | |

And from the working tree, one that is not in the committed roadmap at all:

| Delta | `delta_type` | Note |
|---|---|---|
| cookbook-and-runner | feature | Phase 8. Its `phase` is **implementation**, not complete — the code is written and on no ref |

Nine flows exist in `examples/flows/`, six committed and three not. A delta per
*work item* rather than per *flow* is the shape that matches the model: a flow
is an artifact a delta produces or changes, and `DeltaLink` with
`link_type="branch"` is how it points at one.

## What this page does not authorise

Committing another contributor's working tree. Landing #12 or #21. Choosing
whether qmcp's Phase 8 work goes on #21 or waits for it. Merging the delta
branch. Deciding the delta phase model is right — that is the review's job and
the review has not happened.
