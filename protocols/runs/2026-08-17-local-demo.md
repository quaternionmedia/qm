# Local demo run — 2026-08-17

**The review list.** Two demos, both built, both run on this machine, both
covered by tests. Everything below was true at the commits named and nowhere
else.

| | |
|---|---|
| **Protocol** | `protocols/local-demo.md` |
| **Operator** | Peter Kagstrom |
| **Machine** | Windows 11, Python 3.13.3, no Docker daemon running |
| **Tools** | assistant-2026-08. See `ci/tool-registry.yaml` |

---

## 1. qmcp — the agent harness

| | |
|---|---|
| Repository | `quaternionmedia/qmcp` |
| Branch | `governance/adopt-constitution` (PR **#21**, draft) |
| Commit | `7723599`, pushed to `origin/governance/adopt-constitution` |
| Demo | `examples/demo_agent_harness.py` |
| Test | `tests/test_demo_agent_harness.py`, 8 tests |
| Baseline before | 278 passed, 11 skipped |
| Suite after | **286 passed, 11 skipped** |

```
$ uv run python examples/demo_agent_harness.py
server           QMCP Server 0.1.0
health           healthy
tools registered ['echo', 'planner', 'executor', 'reviewer']
audit log        0 invocation(s) before

planner          error=None  id=c02d32d5-92a3-4598-bf73-a34542820739
executor         error=None  id=580d28cb-b58c-4b91-8e46-f94fc542cd44
reviewer         error=None  id=b9532e20-d725-4589-a055-477d4e947b8d

audit log        0 -> 3 invocation(s)
                 reviewer   success  0ms
                 executor   success  0ms
                 planner    success  0ms

3 of 3 calls reached the audit log.
```

**Why the audit count is the claim.** Recording an invocation is the code path
that was broken on `main`: `ToolInvocation.execution_id` was `UUID NOT NULL`
against an insert that supplies none, so every call raised
`sqlite3.IntegrityError` and 19 tests failed. A demo printing only a planner's
reply would have passed against that.

The sequence is agent-shaped rather than three unrelated calls — the planner's
plan is what the executor receives, and the executor's result is what the
reviewer judges.

**Cannot be run locally, and why:** the Metaflow flow layer. `import metaflow`
fails in `metaflow/sidecar/sidecar_subprocess.py` on `import fcntl`, which is
POSIX-only. The documented route is Docker, and the daemon is not running here
(`docker --version` reports 28.0.4; the engine pipe is absent). Nine flows in
`examples/flows/` are therefore **unverified on this machine** — unchanged from
the 2026-08-12 handoff, and not a regression.

## 1b. qmcp — one workflow step, reconciled with a dossier delta

| | |
|---|---|
| Repository | `quaternionmedia/qmcp`, same branch |
| Commits | `27d9ef1` (decoupling), `c7183d0` (the seam), both pushed |
| Seam | `qmcp/cookbook/delta.py`, 24 tests |
| Demo | `examples/demo_step_as_delta.py`, 12 tests |
| Suite after | **322 passed, 11 skipped** |

```
$ uv run python examples/demo_step_as_delta.py
step             summarizer  (from CHANGE_IMPACT_PIPELINE)
as a delta       phase=planning  type=feature  links=0
row dossier gets {"name": "summarizer", "title": "Summarizer", "description": "You summarize
                  engineering changes...", "phase": "planning", "delta_type": "feature",
                  "priority": "medium"}
after running    phase=complete
after review     phase=review  invocation=['b9532e20-d725-4589-a055-477d4e947b8d']
review missing   phase=implementation  (not complete: something is outstanding)
rebuilt from it  summarizer  tool=reviewer  criteria=['risk', 'completeness']
identity matches True
swapped output   TerseSummary  identity still matches True
```

**The seam is a schema, not an import.** Nothing in qmcp imports dossier, and a
test asserts it on the source. dossier's `ProjectDelta` is on an unmerged branch
and is not a qmcp dependency; an import would mean neither project ships without
the other, which is the opposite of interchangeable. What crosses is a dict
whose keys are dossier's column names, so the consumer writes
`ProjectDelta(**delta["delta"], project_id=resolved)`.

**`project_id` is deliberately outside the row.** It is required, has no
default, and is an integer primary key qmcp cannot know. The `project` key
beside the row carries `owner/repo` for the consumer to resolve. An earlier
draft of the module claimed the row constructed on its own; reading the model
showed it does not.

**Phase is derived from execution facts, never judgement:** declared but not run
→ `planning`; ran and declared no review → `complete`; ran and its declared
review happened → `review`; ran and the declared review did not happen →
`implementation`. Only the last one could flatter, and it is the one the tests
pin hardest — reporting unreviewed work as complete is the failure worth
preventing.

**What made this possible was a decoupling, and it was a real defect.** The four
`AgentStep`s of the change-impact pipeline were defined inside
`examples/flows/change_impact.py`, which imports Metaflow at module level — and
`import metaflow` dies on Windows at `import fcntl`. Four pure step
descriptions were unreachable on this platform because of the executor they were
filed with. They now live in `qmcp/cookbook/change_impact.py`; the flow imports
and re-exports them, so nothing that referenced them breaks, and a test asserts
the new module names no flow runtime.

**Unverified, and named as such:** the consumer half. Nothing has inserted one
of these rows into a dossier database. The column names were checked by reading
`ProjectDelta` on `origin/feature/delta-entity-type`, which is evidence and not
execution. *Done* looks like a test in dossier that ingests a payload from this
schema — which needs the delta entity on dossier's `main` first, and that is
blocked behind #12 and the two alembic heads.

## 2. dossier — the TUI

| | |
|---|---|
| Repository | `quaternionmedia/dossier` |
| Branch | `governance/refresh-seed-copies` (PR **#12**, draft) |
| Commit | `ad8e656`, pushed to `origin/governance/refresh-seed-copies` |
| Demo | `examples/demo_tui.py` (`--live` for the real dashboard) |
| Test | `tests/test_demo_tui.py`, 10 tests |
| Baseline before | 341 passed, 1 skipped |
| Suite after | **351 passed, 1 skipped** |

```
$ uv run python examples/demo_tui.py
database         demo.db (temporary, 3 project(s) seeded)
app title        Dossier
tree nodes       ['? Other (3)', '? dossier', '? qm', '? qmcp']
seeded projects  ['qm', 'dossier', 'qmcp']
key bindings     ['q','r','s','a','o','/','f','?','`','l','d','c','space','ctrl+a','escape','tab','shift+tab','x','X']
pressed ?        screen is now HelpScreen
pressed a        screen is now AddProjectModal
pressed /        focus is now Input

3 of 3 seeded projects appeared on the dashboard.
```

The `?` in the tree nodes is a folder emoji this console cannot encode; the
findings keep the real label and only the transcript is degraded.

Headless is the default because `run_test` drives the real widgets and bindings
and a test can run it. `--live` opens the actual dashboard on the same seeded
scratch database, because a dashboard is a thing somebody should look at.

**Cannot be run locally, and why:** anything needing the network — GitHub sync,
repository scan, live issue and pull-request data. The three project rows are
fixtures written by the demo, and their presence is not evidence that syncing
works.

## What both demos were wrong about first

Recorded because the wrong reading looked exactly like a real failure in both
cases, and neither was.

| symptom | looked like | actually |
|---|---|---|
| `status=None` on all three qmcp calls | three failed invocations | `ToolInvokeResponse` has no `status` field. Status is on the audit record |
| `projects shown []` in dossier | the seed failed | projects are `#project-tree` nodes, and Tree nodes are not widgets, so a widget scrape cannot see one |
| `UnicodeEncodeError` on the transcript | the demo crashed | a running Textual app replaces `sys.stdout`, so an encoding guard measured Textual's stream and not the terminal |

## Findings worth a decision, not fixed here

1. **`dossier.cli` builds its engine at import time** from
   `DATABASE_URL = "sqlite:///dossier.db"` — a relative path, so the database
   is whichever directory you launched from. The demo works around it by
   swapping the module engine and putting it back.
2. **qmcp's `create_app` hardcodes `level="INFO"`** from `settings.debug` and
   never reads `settings.log_level`, which exists. Setting it and expecting
   quiet is a setting that is not the setting that gets read.
3. **Both slots are held by green draft pull requests.** qmcp #21 and dossier
   #12 are both `draft`, and both handoffs record them as ready. `AGENTS.md`
   item 3: draft means incomplete, and under the two-gate model there is nobody
   at the far end of that queue. Until one lands, neither repository has a free
   slot.
4. **`uv run qm mutate` cannot be pointed at another repository.** `ROOT` is the
   corpus, and the route exposes no `--root`, so the mutation discipline this
   corpus asks for cannot be applied to qmcp's or dossier's tooling. The three
   modules added here are covered by tests and by no mutation pass, and that is
   a weaker claim than the corpus makes about its own.
5. **A step's identity is now a cross-project contract with one owner.**
   `SCHEMA = 1` in `qmcp/cookbook/delta.py` is a promise about key names that
   dossier will depend on, and nothing in dossier references it yet. This is
   the "how corpora interact" question in miniature, and it wants a record on
   `project/qmcp` — each `project/<name>` branch in the corpus holds its own
   slot, so that PR is available now even while `main`'s slot is held.

## Pushed, and what the green checks actually cover

All four commits are on `origin` as fast-forwards. No branch was rewritten and
no force push was made; `gh api repos/<r>/activity` records `push`, not
`force_push`, for both.

| repo | branch | pushed | PR | checks |
|---|---|---|---|---|
| qmcp | `governance/adopt-constitution` | `05010a4..c7183d0` | **#21**, still draft | 5 pass, `CLEAN` |
| dossier | `governance/refresh-seed-copies` | `ae183d1..ad8e656` | **#12**, still draft | 6 pass, `CLEAN` |
| qm | `evolve/protect-main-handoff` | earlier | **#66**, open, green | 8 pass, `CLEAN` |
| qm | `evolve/governance-protocols` | earlier | none — `main`'s slot holds #66 | not run |

Every commit on both project branches carries a good signature (`%G?` = `G`).

**The green checks on #21 and #12 do not mean the tests pass.** Neither project
runs a test suite on a runner:

| repo | workflows | test gate |
|---|---|---|
| qmcp | `adr-lint`, `one-pr-check`, `submodule-check` | **none** |
| dossier | `adr-lint`, `license-check`, `reuse-lint`, `submodule-check` | **none** |

`grep -rl pytest .github/workflows/` returns nothing in either. So **322 passed**
in qmcp and **351 passed** in dossier are local results only, and every test
added by this run — 8 for the harness demo, 24 for the delta seam, 12 for the
step demo, 10 for the TUI demo — is enforced by nothing outside this machine.
That is the same shape as the four registry checks the corpus found wired into
no workflow, arriving one repository along. The corpus gates its own tooling
with `ci-tooling-tests.yml`; neither fork has an equivalent, and `project-seed`
does not ship one.

**Both pull requests are now wider than their titles.** #21 reads *Adopt the QM
constitution, and land the cookbook and flow runner* and now also carries two
demos and the delta seam — defensible, since the 2026-08-12 handoff already
names it the demo branch. #12 reads *Refresh the seed workflow copies* and now
carries a TUI demo, which is unrelated work on a governance branch. Both were
pushed to their existing branches because `handbook/async-contract.md` §1 says a
held slot means add to the open pull request or wait, and waiting was not the
instruction.

## What needs a decision

Everything is pushed. Four decisions remain, none of which an agent should take.

**1. Both pull requests are green and still `draft`.** `AGENTS.md` item 3: draft
means incomplete and nothing else, and under the two-gate model there is nobody
at the far end of a draft queue. Leaving #21 and #12 in draft is what has kept
both slots spent for days. Un-drafting is the operator's act, not least because
the scope question below should be settled in the same breath.

**2. Their titles no longer describe them.** #21 has gained two demos and the
delta seam; #12 has gained a TUI demo unrelated to seed copies. Either retitle
them to match, or split the demo work back out once a slot frees.

**3. Neither project gates its tests.** Every test written for these demos runs
on one machine and nowhere else. A `ci-tooling-tests.yml` equivalent belongs in
`project-seed/` so every fork gets one, which makes it an org-level change with
its own slot — not something to bolt onto either project branch.

**4. `SCHEMA = 1` is a cross-project contract with one owner and no record.**
`qmcp/cookbook/delta.py` promises key names dossier will depend on, and nothing
in dossier references it yet. It wants a decision record on the corpus's
`project/qmcp` branch, which holds its own slot and is therefore available now
even while `main`'s slot is held by #66.

Nothing here is unpushed, and nothing was force-pushed.
