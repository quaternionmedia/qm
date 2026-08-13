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
| 1 | ~~Get the uncommitted flow work onto a ref~~ | qmcp | **done** — `feat/cookbook-and-metaflow-runner` at `21c442d`, pushed |
| 2 | Land #12 to free the slot | dossier | a human un-drafting it |
| 3 | Re-parent the delta migration, open the delta PR | dossier | step 2 |
| 4 | Create one delta per qmcp work item | dossier + qmcp | step 3 |

Nothing in 3 or 4 can start before step 2.

## Step 1 — done, and the parent commit was red

3,646 lines of untracked Python plus 20 modified files are now one commit,
`21c442d`, on `origin/feat/cookbook-and-metaflow-runner`: 33 files,
+4,215 / −797, cut from `feat/pydantic-ai-integration-docs` (`a3f827d`).
**No pull request** — qmcp's slot is held by #21, and a branch on origin is
what the risk needed.

The reason it mattered was not only that the work was unbacked. **The parent
commit's own suite is red**, established in a throwaway worktree at `a3f827d`
rather than by disturbing the tree:

| Tree | Result |
|---|---|
| `a3f827d`, the committed parent | **19 failed**, 146 passed, 10 skipped |
| `21c442d`, without optional extras | 232 passed, 15 skipped, **0 failed** |
| `21c442d`, with the `mcp` extra | **275 passed**, 14 skipped, 0 failed |

The 19 were one line: `ToolInvocation.execution_id` was `UUID` NOT NULL
against a code path that inserts without it, so every insert raised
`sqlite3.IntegrityError`. The uncommitted work had already fixed it to
`UUID | None`. Leaving that work on a disk was leaving the repository broken.

Three defects were in the work itself, all of the same shape — an optional
dependency that does not degrade to a skip:

- **`mcp` was declared nowhere**, and `qmcp_mcp.py` imports it at module
  level, so `tests/test_qmcp_mcp.py` failed *collection* and took all 275
  tests with it. Now an extra, and guarded.
- **The extra is capped below 2.0.** `mcp` 2.x removed
  `mcp.server.fastmcp.FastMCP` — `grep -rl "class FastMCP"` over the
  installed 2.0.0 distribution returns nothing — so an unconstrained
  `mcp>=1.0.0` resolves to a version the module cannot import.
- **`importorskip("mcp")` was not enough**: 2.x installs as `mcp`, so the
  top-level check passes and the import still dies. The guard names
  `mcp.server.fastmcp`, the module actually imported.

**One finding is not fixed and is not this branch's to fix.** The `openai`,
`pydantic-ai`, `anthropic` and `flows` extras are **not co-installable with
the pinned server stack**. `pydantic-ai` resolves `starlette` 0.50.0 → 1.6.0,
and `fastapi` 0.128.0 then raises `TypeError: Router.__init__() got an
unexpected keyword argument 'on_startup'` — 52 errors. Isolated with
`uv pip install --dry-run` per package: `mcp` alone touches starlette not at
all. Those four extras predate this work.

The branch carries three new flows (`plan_council.py`, `qc_release.py`,
`change_impact.py`), retires two (`local_dev_db.py`, `local_mcp.py` — git
recorded the first as a 52% rename into `qmcp/cookbook/persistence.py`, so its
history survives), and adds the roadmap's **Phase 8**. Until `21c442d` that
Phase 8 existed only on disk: the repository's roadmap ended at Phase 7 and
declared all phases complete, so a reader of the refs saw seven and a reader of
the disk saw eight.

**What remains a decision.** The branch has no pull request, because qmcp's
slot is held by **#21** (adopt the constitution, draft, additions-only).
Opening one needs #21 to land first, or this work goes onto #21 — which turns
an additions-only governance change into a feature branch. That is the
decision, and the push means nothing is at risk while it waits.

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
