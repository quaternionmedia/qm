# Handoff — The Two-Gate Model, and the Tag Gate That Enforces It

**What this closes.** A session that was asked to review the workspace, then
corrected on the most load-bearing fact in the corpus: **pull requests are
review and audit into `main`; human review happens at tagged releases.** Agents
get `main` clean and working. Human-reviewed pull requests that assign tags
drive releases.

*Stamped 2026-08-14. `qm` `main` at `104361a`. This page written on
`evolve/two-gate-reconciliation` at `547cc15`. `dossier` `main` at `604efb8`,
`qmcp` `main` at `85013c5`. Every figure below was true at those commits —
re-derive before acting on any of them.*

---

## Read this before you read the other pages

**Several handoff pages here predate the correction and describe the pull
request as a human gate.** They are not wrong about their own subject; they are
wrong about what a draft pull request is waiting for. If a page tells you to
open a draft and wait for somebody to leave draft, that instruction is stale.
`AGENTS.md` item 3 and `handbook/async-contract.md` §1–§2 are the statement now.

The short version, and it is short on purpose:

| | |
|---|---|
| A pull request | An audit record. Gates run, the diff stays readable. Its author merges it once every gate is green |
| `main` | Not a claim. `records/DRAFT-version-tags-are-claims.md` §4: `main`, a pull request and a local build are all drafts |
| The two human gates | Ratification, for what the corpus says. The version tag, for what a project ships. **Neither is the pull request** |
| Draft | Means unfinished. Not a holding pen for finished work |
| One PR per repo | A *sequencing* constraint, not a bandwidth one |

## Two branches, both pushed, neither with a pull request

**`evolve/two-gate-reconciliation`** — 5 commits over `evolve/git-hygiene-and-handoff`,
which it was cut from and whose 5 commits it therefore also carries.
`check_pr_base.py --base main --head evolve/two-gate-reconciliation` reports the
inheritance; paste that output into any description.

- `f7beee7` the two-gate model across `AGENTS.md`, its seed copy,
  `async-contract` §1/§2, the handoff rules, the propagation runbook, preflight
- `eccca8f` `records/DRAFT-the-read-document-governs.md` and
  `ci/check_restatements.py`, wired into `adr-lint.yml`
- `604a0a0` `project-seed/ci/check_tag_claims.py` and `tag-claims.yml`
- `01541f2` three retrospectives
- `547cc15` `ci/tag_audit.py`, the org-wide sweep

**`evolve/governance-loop-poc`** — cut from the branch above, so its base is
`evolve/two-gate-reconciliation` and not `main`.

- the governance loop's Phase 1: registries, five generators, the `/reflect`
  adapter, 35 tests, and the plan. **Its schema is consolidated** — see below
- `b069c90` a seed fix to `cowork_context.py`, which is why you can see any of
  this at all: it scanned `refs/heads` only, so a fresh clone reported a clean
  repository over any amount of pushed work

**Until 2026-08-14 all thirteen Phase 1 files were uncommitted, on one disk, and
the page describing them was one of them.** They are on a ref now. That is worth
knowing because it is the state a session should never leave work in, and this
corpus was in it for two days.

Both branches were pushed and no pull request was opened, because `qm`'s slot
holds #56 and #57 and `check_one_pr.py` reports `OVER subcontrabass: 2`. Landing
#56 frees it. The order after that is: open the pull request for
`evolve/two-gate-reconciliation` against `main`, land it, then the loop branch
against `main`.

## What is blocked, and by what

| Blocked | By |
|---|---|
| #56, #12, #21 merging | Nothing technical. All three are `CLEAN`, `MERGEABLE`, every check green. This session's tooling was denied the merge |
| A pull request for either branch above | `qm`'s slot, held by #56 and #57 |
| Propagation of the seed `AGENTS.md` change to twelve `project/*` branches | It carries what is on `main`. This is not on `main` yet, so propagation is strictly downstream — not a parallel task |
| `v*` tag-protection rulesets | `records/DRAFT-version-tags-are-claims.md` §7 asks for one. `gh api repos/quaternionmedia/{qm,dossier,qmcp}/rulesets` returns `[]` and `/tags/protection` returns 404 on all three. That is an access-control change to live repositories, and the owner's to make |

Nothing above is waiting on more work. It is waiting on merges and on one
settings change.

## One schema, not two — the decision, and where it lives

Two designs existed for the same table in `dossier`: the delta entity on
`wip/delta-entity-type-local`, and the governance loop's `SessionArtifact` /
`BreakObservation`. The reviewer decided: **one schema.**

`SessionArtifact` is gone. `DeltaNote` absorbs it — five nullable columns
(`source`, `repo`, `branch`, `artifact_path`, `imported_at`) — and
`BreakObservation` keys on `delta_note.id`. `ProjectDelta` is unchanged.
One migration, the re-parented `005_delta_tables` renamed `009_delta_and_loop`.

**This changes the ordering.** Phase 2 now depends on
`wip/delta-entity-type-local` landing, which it did not before. That branch is
on no remote, 17 ahead and 16 behind `origin/main`, and has never had a pull
request. So: #12 lands, the delta branch is pushed and reviewed and lands, then
Phase 2. `dossier-delta-review.md` is the review brief and it is still current.

The full statement is in `perspectives/2026-08-13-the-mechanical-governance-loop.md`
Layer 4 and `handbook/handoffs/governance-loop-poc.md` Phase 2, both on
`evolve/governance-loop-poc`.

## What is now mechanical that was customary

`records/DRAFT-version-tags-are-claims.md` §7 said its §1 was "mechanical rather
than customary" and nothing read a tag.

- `project-seed/ci/check_tag_claims.py` refuses a lightweight tag, a name that
  is not `vMAJOR.MINOR.PATCH[-prerelease]`, and an annotation missing
  `Reviewed-by`, `Manually-tested`, `Automated-gate` or `Not-covered`.
  `--test-output` refuses a run reporting a skip, rerun, retry, xfail or error.
- `tag-claims.yml` runs it on a `v*` push. Deliberately **not** on
  `pull_request`: one bad legacy tag would fail every unrelated pull request in
  the repository, for a reason its author cannot fix.
- `ci/tag_audit.py` sweeps the roster from the host and imports
  `check_annotation` from the seed script, so there is one definition of the
  rule. `--from-json` takes a captured payload, which is how its tests run
  without a network.

**Run it, do not quote this page:** `python ci/tag_audit.py`. At the time of
writing it reported **zero repositories ready**: alfred, datum, `private-32` and
qmetronome all failing; nine with no `v*` tag at all, which §4 says is a state
rather than a violation. alfred `v0.2.0` and datum `v0.0.1` are lightweight;
qmetronome has 16 tags of which `v0.0.25` is lightweight; every annotated tag in
the org fails on all four fields, because they predate the requirement.

The nearest demo is `private-32` or qmetronome — they already tag annotated, so
the gap is annotation content rather than practice.

## What the new checks cannot do

Both print their own limits on every run, and the limits are larger than the
checks. Do not report either as more than it is.

`check_tag_claims.py` cannot tell whether the review or the manual test
happened; it reads an annotation a human wrote. It does not gate tag *creation* —
that needs the ruleset above. It cannot establish determinism, only refuse a run
that announces its absence.

`check_restatements.py` cannot tell that a restatement and its record say
different things, and cannot find a restatement nobody declared. Distinguishing
a restatement from a citation is reading, not matching — `README.md`'s record
index names every record and restates none. So it verifies the declarations that
exist rather than discovering the ones that do not.

## Evidence, and how to reproduce it

```sh
python project-seed/ci/run_workflows_locally.py     # 19 executed step(s) passed
python -m pytest project-seed/ci/tests ci/tests -q  # 408 passed
python ci/tag_audit.py                              # the org sweep
python ci/check_restatements.py                     # declarations pair up
```

The runner does not reproduce `uses:` steps, the runner image, or secrets, and
it logs `tag-claims.yml` as skipped because that workflow is not triggered by
`pull_request`.

**Mutation results, because a test that has only been seen green has not been
tested.** 7 mutations against the tag gate and 9 against the restatement check,
all caught, baseline green before and after each run.

Three of those reported false on the first pass, in three different ways: one
mutation was a no-op (`^` and `.match` are redundant anchors, so removing either
alone leaves the guard standing), one hit dead code (an exclusion list sitting
beside a whitelist, since deleted), and one test was genuinely weak (asserting a
substring that appears in two different failure messages). **A green mutation is
one of four things and only one of them is an inert test.**
`perspectives/2026-08-14-teeth-and-what-the-mutations-said.md` has the full
account.

## What this page does not authorise

Ratifying anything. Cutting a tag. Applying a ruleset. Merging #56, #12 or #21
without your own testing — they are green, and green is not the gate.
Force-pushing either branch. Pushing fixes onto `wip/delta-entity-type-local`,
which is another contributor's unreviewed branch.
