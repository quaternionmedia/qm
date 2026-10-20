# Handoff — Governance Loop PoC

**Goal of the session.** Plan and implement Phase 1 of a closed governance dev
loop: structured session artifacts, pattern and shape indexes, a coverage gate,
a counterfactual query tool, and a `/reflect` adapter command. The work follows
from the `thirteen-breaks` perspective, which established that clauses without
mechanical enforcement do not change session behaviour.

*Stamped 2026-08-13. Branch `evolve/git-hygiene-and-handoff` at `470419a`.
Every file count and test number below is true at this commit and working-tree
state. Re-derive before acting.*

---

## What is on disk — uncommitted

All thirteen files below are untracked or modified on the working tree.
**None are committed.** They are not on PR #56.

| File | Kind | Status |
|---|---|---|
| `ci/pattern-registry.yaml` | Registry; org-level policy | untracked |
| `ci/shape-registry.yaml` | Registry; org-level policy | untracked |
| `ci/session_record.py` | Generator: write break artifact | untracked |
| `ci/pattern_index.py` | Generator: aggregate by pattern | untracked |
| `ci/shape_index.py` | Generator: aggregate by shape | untracked |
| `ci/check_pattern_coverage.py` | Gate: exits non-zero on coverage gaps | untracked |
| `ci/counterfactual_query.py` | Query: prospective shape lookup | untracked |
| `ci/tests/test_governance_loop.py` | 35 tests; **35/35 green** | untracked |
| `adapters/claude-code/commands/reflect.md` | `/reflect` slash command | untracked |
| `perspectives/2026-08-13-the-mechanical-governance-loop.md` | Architecture plan | untracked |
| `perspectives/2026-08-13-thirteen-breaks-and-the-five-that-became-yours.md` | Source perspective | untracked |
| `.gitignore` | +`perspectives/artifacts/` | modified |
| `perspectives/README.md` | +two index rows | modified |

**Test run to reproduce:**
```sh
python -m pytest ci/tests/test_governance_loop.py -v
# 35 passed in 0.72s
```

**Local CI to reproduce:**
```sh
python project-seed/ci/run_workflows_locally.py
# 18 executed step(s) passed.
```

The governance loop tests are not yet wired into `run_workflows_locally.py`.
That is the last step before the Phase 1 PR.

---

## The branch situation

These files **must not be committed to `evolve/git-hygiene-and-handoff`.**
That branch carries PR #56 ("Order the handoff queue by expected delta, correct
the delta review, and name the qmcp milestone") and this work has nothing to do
with it.

The one-PR rule (`check_one_pr.py`) means the governance loop work cannot have
its own PR slot until #56 lands. The ordering is:

1. #56 merges to `main`.
2. New branch `evolve/governance-loop-poc` is cut from the resulting `main`.
3. The thirteen files above are committed to that branch (in two commits: the
   registries + generators first, the tests second — or one commit, the PR
   body explains both).
4. A PR is opened — `gh pr create --assignee mrharpo`, no reviewer — and
   merged by its author once every gate is green.

**Do not cut the branch from `470419a`.** If you do, the PR will carry #56's
commits under a different title, which is the misbranched-PR failure the corpus
already has a check for. Cut from `main` after #56 lands.

**If #56 has not yet landed** when you pick this up: keep the files as they are
on the working tree, do not commit them, and wait. The working tree is clean in
the sense that nothing is staged. `git stash` is also fine if you need the
working tree clear.

---

## What Phase 1 is (and is not)

Phase 1 is everything in this repository. It is the generators, the registries,
the tests, and the `/reflect` adapter. It does not touch dossier or qmcp.

Phase 1 is complete and working. The plan document at
`perspectives/2026-08-13-the-mechanical-governance-loop.md` describes all five
phases. The next two sessions (one for dossier, one for qmcp) are Phases 2–4.
Phase 5 is propagation.

**Phase 1 is self-contained.** Even without Phases 2–5, the generators run
locally, the gate is callable from `run_workflows_locally.py`, and `/reflect`
produces structured artifacts. The loop is closed at the file-system layer. The
dossier and qmcp layers are additive, not prerequisite.

---

## What the plan says about the next phases

Read `perspectives/2026-08-13-the-mechanical-governance-loop.md` in full before
picking up Phase 2 or 4. The short version:

**Phase 2 — dossier (storage + API).**
**One schema, extending the delta entity rather than adding tables beside it.**
Four nullable columns on `DeltaNote` (`source`, `repo`, `branch`,
`artifact_path`, `imported_at`) and one new table, `BreakObservation`, keyed on
`delta_note.id`. `ProjectDelta` is unchanged. The revision is the re-parented
`005_delta_tables`, renamed `009_delta_and_loop`, carrying both.

This makes Phase 2 depend on `wip/delta-entity-type-local` landing, which it did
not before. That branch exists on no remote, is 17 ahead / 16 behind
`origin/main`, and has never had a pull request —
[`dossier-delta-review.md`](dossier-delta-review.md) is the brief. The ordering
is: #12 lands, delta branch is pushed and reviewed and lands, then Phase 2.

New CLI: `dossier governance loop sync`. New endpoints: `GET
/governance/patterns`, `GET /governance/shapes`, `POST
/governance/session-artifacts`. New test: `test_governance_loop.py` asserting
`subprocess` absent from parser and API (same assertion that governs the
existing governance parser). Single PR on a new branch in the dossier repo.
dossier's PR slot is currently held by #12 — that must land first.

**Phase 3 — dossier (TUI dashboard).**
New "Loop" tab in the Textual TUI. Pattern panel (DataTable, WARN colour on
gaps), Shape panel (counterfactual detail: path-taken vs path-avoided side by
side). Key bindings: `s` (sync), `q` (query), `Enter` (expand). Document age
always visible. Single PR.

**Phase 4 — qmcp (harness + HITL gate).**
Four new MCP tools: `cowork_context`, `record_break`, `query_shapes`,
`check_coverage`. HITL gate: when `check_coverage` finds uncovered patterns
above threshold, creates a `HumanRequest` with options `draft-check`,
`approve-gap`, `defer`. `defer` is tracked as a count distinct from
`check_exists: false`; three deferrals above threshold stays in WARN.
**Critical constraint**: coverage gap `HumanRequest` objects must have
`expires_at: null` — the existing qmcp read-expires-on-read hazard (named in
qmcp's AGENTS.md) would silently close the gate without a decision if an
`expires_at` is set.

---

## Open questions for a human

None are decisions this session was authorised to make. All four change scope or
timeline.

| # | Question | Stakes |
|---|---|---|
| Q1 | Should Phase 2 wait for dossier #12 to land, or can a governance-loop branch start now on top of `governance/refresh-seed-copies`? | A stacked branch that depends on #12 creates the ordering-problem the one-PR rule exists to prevent. Waiting is simpler. |
| Q2 | Should the governance loop tests be added to `run_workflows_locally.py` before the Phase 1 PR, or as a separate commit? | A pre-PR addition is cleaner. A separate commit documents the intent. Either is fine; pick once so the PR history is readable. |
| Q3 | Does Phase 1 belong on this corpus branch, or on a `project/*` branch? | It is org-level tooling (`ci/`) and org-level adapter (`adapters/`), so it belongs on an `evolve/*` branch of this corpus, not on a project branch. This is stated here because the plan document's scope could be read as project-scoped; it is not. |
| Q4 | Is there a preference for the Pattern panel's colour on `defer` vs `false`? | The plan says both are WARN. If `defer` warrants a distinct colour, that is a one-line change to `dashboard_style.py`. |

---

## What to read before picking this up

1. `perspectives/2026-08-13-the-mechanical-governance-loop.md` — the full plan.
2. `perspectives/2026-08-13-thirteen-breaks-and-the-five-that-became-yours.md` — the source session it responds to.
3. `handbook/handoffs/README.md` — the queue and ordering constraints for all open work.
4. `ci/tests/test_governance_loop.py` — the full test suite; the fixtures are the best documentation of the schema.

If you are picking up Phase 2 (dossier): also read `dossier/src/dossier/parsers/governance.py`
and `dossier/src/dossier/corpus.py`. The new code follows those two files'
patterns exactly; reading them first means the new code will look familiar rather
than invented.

If you are picking up Phase 4 (qmcp): also read `qmcp/AGENTS.md` fully,
specifically the section on `GET /v1/human/requests/{id}` and the expiry hazard.
That section is the single most important constraint for the HITL gate
implementation.
