# Handoff — the web window, first slice

**Stamped 2026-09-20.** `qm` `main` at `23e4d35` (#115 merged); this page's
branch `evolve/the-web-window` rebased onto it; `codecartographer` `main` at `4e30271`;
`qmcp` `main` at `3e25711`; `looksatwords` `main` at `32d3371`; `rad` `main` at
`a39d3bf`. Every figure here was true at those commits and nowhere else. The
next session re-derives before acting: `uv run qm slot --repo <owner/name>`,
`gh pr checks`, and the branch check name their own answers.

The plan this slice implements is [`plans/the-web-window.md`](../../plans/the-web-window.md).
Read it first; this page is only where the work stands.

---

## 1. State

Six branches, five pull requests, nothing merged. **Nothing reaches `main`
without Peter's click** — stated by him on 2026-09-20 and the standing rule for
every branch below.

| Repository | Branch | Carries | Pull request |
|---|---|---|---|
| qm | `evolve/the-web-window` | the plan; `ci/dashboard.py` gains a fourth surface (`prose`, `looksatwords`, root two) and drops the retired standalone `/topology` page from the web surface's list; `docs.yml` stops naming a deploy branch that no longer exists; this page and its retrospective; the regenerated document index | opened once #115 had merged and freed the `main` slot — see the pull request list |
| qm | `adr/codecartographer-index-current` | the project's `adr/README.md` names `governance/qm` rather than `docs/qm` and lists the rad adoption among its drafts | **#116** → `project/codecartographer`, gates green |
| codecartographer | `evolve/the-estate-frame` | the estate frame (Phase 0 and 1 of the plan); the local `test` branch's four commits minus its governance-pin bump; the slot workflow checking out only the governance submodule; the canvas drawing an edge's colour, width and style from where gJGF puts them; the capability and overview kinds joined to the palette | **#100**, gates green once #99 (another session's) was closed and the slot check re-ran |
| qmcp | `evolve/the-topology-routes` | `/v1/orchestration/plane`, `/v1/orchestration/runnable`, `/v1/topology/schema/{kind}`, `/v1/topologies` over the existing table, walkthrough 07 | **#36**, gates green |
| looksatwords | `evolve/the-harness-routes-documented` | the harness routes documented and guarded, a per-thread topics document, the port from the corpus's allocation, a stub archive shared by the tests | **#23**, gates green |
| rad | `evolve/authored-graph-verbs` | a Proposed record: an authored-graph mode for the ring, with candidate vectors, not applied | **#6**, `verify` was pending when this was written |

Every working tree is clean. The branches were built in worktrees under the
session scratchpad, not in the clones under `repos/qm/`, because another
session was committing in the `qm` clone throughout; those worktrees are
disposable and the branches are on `origin`.

## 2. What is unfinished, and what done looks like

- **The qm plan pull request.** Done when #115 has merged and
  `evolve/the-web-window` is opened against `main`, gates green. Do not open it
  while #115 is open: one slot, one pull request.
- **The `topology` address kind in the corpus.** qmcp #36 addresses saved
  designs as `<owner>/<repo>/topology/<name>` and says beside the constant that
  the corpus does not know the kind. Done when `docs/ref/addresses.md` and
  `project-seed/address-vectors.json` carry it, on a qm branch, and qmcp's
  shared-vectors test still passes. Not started.
- **looksatwords' port test skips in the canonical layout** until the qm branch
  lands — the row it reads is on `evolve/the-web-window`. Done when that
  merges and the test runs rather than skips beside a current qm clone.
- **rad's proposal wants the host-side half.** Its first `Pends on` item is
  codecartographer's own record carrying the divergence in its `Pends on` row
  naming `rad`. Done when that row exists on `project/codecartographer`.
- **The seed's `one-pr-check.yml` cannot check out a project with a private
  submodule.** (Its check did, on #100, report a real thing the moment it could
  run: a second pull request opened by another session.) codecarto's copy departs from the seed for the reason its
  `adr-lint.yml` already gives. The seed itself is not changed here; done when
  the seed's copy takes the same shape or the departure is written into the
  seed's README as the known exception.
- **Phases 2 to 6 of the plan** are not started. Phase 2 (the live flow on the
  shape) should begin by reading the unpushed local branch
  `feat/the-monitor-derives-the-system` in the codecartographer clone — its
  `system_composer.py` and `derived_system.ts` are the idea, written against a
  renderer `main` has since deleted.

## 3. Blocked, and on whom

- **Every merge**, in every repository above.
- **Eight remote branches in this corpus carry content `main` lacks**, left
  from another session's audit of the remote on 2026-09-20 (its 35 name-only
  branches — every tip an ancestor of `main` or of its project branch, verified
  twice by that session and once more here — were deleted from this one). Each
  is a person's call, with the reading established here:

  | branch | reading, and the evidence |
  |---|---|
  | `evolve/carlos-in-the-roster` | superseded: `main`'s carlos entry carries the same claim plus a family. Delete |
  | `evolve/the-slot-orders-the-remediation` | superseded: `main`'s `plans/moat-remediation.md` is this one plus a lint allowance. Delete |
  | `perspective/2026-08-15-a-namespace-with-one-direction`, `perspective/2026-08-15-stating-a-constraint-is-not-enforcing-it` | two retrospectives never landed, one commit each, plus a generated `harness-status.json` that must not land with them. Land the two pages via one pull request if still wanted, else delete |
  | `evolve/frizzle-kickoff-handoff`, `perspective/2026-08-13-frizzle-kickoff` | a handoff and a perspective whose file names carry a private repository's name (it appears in `ci/workspace-private.yaml`). Do not land as they are; they belong in that repository or need redaction |
  | `evolve/exploration-branch-namespace` | six commits: a `workspace/*` namespace proposal, workflow edits, `ci/check_discipline_parity.py` and its test. Partly landed elsewhere; wants a reader before anything is done |
  | `workspace/math-experiments`, `math/hierarchical-complexity` | explorations on an old base; the first is cited from `perspectives/README.md`. Keep, or retire the citation with them |
- **Answering the human queue from the web** — deferred by decision on
  2026-09-20 and noted in the plan; not to be built until reviewed.

## 4. What could not be verified, marked as such

- The local workflow runner passed nine steps of ten in codecartographer; the
  tenth was `pip install reuse` in a uv venv without pip. The REUSE tool run
  with its encoding extra reports compliant, and the hosted `reuse` gate is
  green. *Inference:* the local failure is the environment, not the work.
- looksatwords' e2e and screenshot suites were not run (they drive a browser
  and start servers). *Inference:* the recorded pictures may have moved with
  the UI; `uv run looksatwords screenshots` re-records them.
- rad's candidate vectors were replayed against the reference core by a
  scratch runner, not by the repository's runner, which has no branch for the
  new suite type. That is the record's own statement of the situation.
- Whether qmcp's name-collision check races: two POSTs with one name could hit
  the unique index and answer 500 rather than 409. Read from the code; not
  observed.

## 5. Standing constraints

- **Nothing pulled to `main` without Peter's explicit approval.** Pull requests
  are fine. This overrides `AGENTS.md` item 3's *merge it yourself*.
- Not *keep everything local*: pushing and opening pull requests is allowed and
  was done.
- Human-only contributorship on every commit: no trailer, no model name. Every
  commit above is signed and carries the contributor's name only. Pull request
  bodies close with a `Tools:` note, as qm #115 does.
- The retirement pass over the other handoff pages that the `/handoff` contract
  asks for was **not done here**: `handbook/handoffs/README.md` was being edited
  by another session on #115's branch at the time, and two branches rewriting
  one table is the conflict `async-contract.md` §5 exists to prevent. This page
  is added to the queue as one row; the retirement pass belongs to whichever
  session next holds the `main` slot with a clean view of the directory.
