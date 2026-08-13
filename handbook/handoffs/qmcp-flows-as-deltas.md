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
| 1 | ~~Get the uncommitted flow work onto a ref~~ | qmcp | **done** — folded into **#21**, which is now the demo branch |
| 2 | Land #12 to free the slot | dossier | a human un-drafting it |
| 3 | Re-parent the delta migration, open the delta PR | dossier | step 2 |
| 4 | Create one delta per qmcp work item | dossier + qmcp | step 3 |

Nothing in 3 or 4 can start before step 2.

## Step 1 — done, and the parent commit was red

3,646 lines of untracked Python plus 20 modified files are one commit,
`05010a4`, on `origin/governance/adopt-constitution` — **#21**, which now
carries the constitution adoption *and* the cookbook work and is the branch
the flows are demonstrated from. It is 3 commits and 48 files over `main`.

The two were folded because qmcp holds one slot and the adoption alone could
not be demonstrated: **the suite on `main` is red**, established in a
throwaway worktree at `85013c5` rather than by disturbing the tree.

The cookbook commit was cherry-picked, and `git patch-id --stable` reports the
same id (`54416c25…`) before and after, so the fold changed nothing. The
separate branch it came from was deleted once that held.

| Tree | Result |
|---|---|
| `a3f827d`, the committed parent | **19 failed**, 146 passed, 10 skipped |
| the work, without optional extras | 232 passed, 15 skipped, **0 failed** |
| the work, with the `mcp` extra | 275 passed, 14 skipped, 0 failed |
| the work, `uv sync --all-extras` | **278 passed**, 11 skipped, 0 failed |

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

**Install through the lock, and a warning about what happens otherwise.**
`uv sync --all-extras` is sound: **278 passed, 11 skipped, exit 0**, with
`starlette` 0.50.0, `fastapi` 0.128.0, `pydantic-ai` 1.44.0 and `mcp` 1.25.0.

`uv pip install pydantic-ai` — unpinned, bypassing `uv.lock` — is not. It
resolves `pydantic-ai` 2.x, which drags `starlette` to 1.6.0, and `fastapi`
0.128.0 then raises `TypeError: Router.__init__() got an unexpected keyword
argument 'on_startup'` in 52 tests. That is a property of installing outside
the lock, **not** of the extras: an earlier draft of this page recorded it as
"the extras are not co-installable with the pinned stack", which is false and
was measured against a venv the session itself had broken. `uv sync` restores
it.

The branch carries three new flows (`plan_council.py`, `qc_release.py`,
`change_impact.py`), retires two (`local_dev_db.py`, `local_mcp.py` — git
recorded the first as a 52% rename into `qmcp/cookbook/persistence.py`, so its
history survives), and adds the roadmap's **Phase 8**. Until `05010a4` that
Phase 8 existed only on disk: the repository's roadmap ended at Phase 7 and
declared all phases complete, so a reader of the refs saw seven and a reader of
the disk saw eight.

## What the demo actually does, and what it cannot do here

Run against the branch, server on a **non-default port** (8931) and asked what
it was rather than merely pinged — `/openapi.json` returns `QMCP Server 0.1.0`,
9 paths:

```
tools registered: ['echo', 'planner', 'executor', 'reviewer']
planner error   : None
audit log       : 2 -> 3 invocations recorded
```

The last line is the point: recording an invocation is the exact code path that
raised `sqlite3.IntegrityError` on `main`, so the demo exercises the fix rather
than describing it. Every run redirected to a scratch database through
`QMCP_DATABASE_URL`; the operator's `./qmcp.db` is byte-identical afterwards.

**Metaflow cannot run natively on this platform at all.** `import metaflow`
fails in `metaflow/sidecar/sidecar_subprocess.py` on `import fcntl`, which is
POSIX-only. The flows' docstrings say *"On Windows, run via Docker"* — that is
a requirement, not a preference, and it is worth stating as one. The Docker
path needs the engine actually running: `docker --version` reports 28.0.4 while
the daemon pipe is absent, so `docker compose run` fails with
`open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file
specified`. The flow layer is therefore **unverified on this box**; everything
under it is verified.

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
