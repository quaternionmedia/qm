# Handoff — the rest of qm's pull-request queue, and qmcp's cleanup phases

**Stamped 2026-10-18.** `qm` `main` at `03670b8`; `qmcp` `main` at
`df42315`; `vox` `main` at `1721e6f`; `joe` `main` at `d72b65b`. Every figure
on this page was true at those commits and nowhere else. Re-derive each one
with `gh` and the tree before acting on it: the queue moves under other
sessions.

[`voice-set-landing.md`](voice-set-landing.md) is the voice set, landed but
for `joe` #33 and #34; [`the-voice-loop.md`](the-voice-loop.md) is the loop,
and its §6 is the baseline this page's `qmcp` work starts from. This page is
everything else open in `qm`, and the order `qmcp`'s own plan sets for the
loop's next work.

---

## 1. Decisions in force

1. **Mechanical or minor reversible items in `qm` are closed without a
   question per pull request**: a green pull request brought level with its
   base, generated documents re-run rather than hand-merged, a propagation of
   `main` into a project branch. Anything that changes what a page, a record
   or a check says is asked, one question at a time. (2026-10-18)
2. **A finding in a pull request's own text is fixed on that pull request**,
   one commit, before its merge is asked. (2026-10-17)
3. **Unsigned commits are rebuilt signed as new pull requests**, cut from the
   current base, and the original is closed with a line naming its
   replacement; nothing is force-pushed. Each rebuild is checked twice: `git
   patch-id --stable` equal for every commit and for the whole change, author,
   date and message unchanged; and every statement the change makes read
   again against the current base. (2026-10-18)
4. **`qmcp`'s cleanup phases come first.** `qmcp`'s
   `docs/voice-loop-next-phases.md` Phases 1 to 3 are taken in order before
   any new capability. The triage of this queue is then the loop's first
   worked example: its onboarding page, and the fixtures and cases its tests
   are drawn from. (2026-10-18)
5. **"its minutes are billed"** stays in the workflow headers. (2026-10-17)

## 2. `qm`'s open pull requests, and what clears each

`uv run qm stacks --repo quaternionmedia/qm` lists them. Two causes account for
most of the red: a project branch that took `main` before the stack rule
carries the old `slot` check, which refuses every pull request into it after
the first; and commits made on 2026-10-13 that the host reads as unsigned.
`git log --format=%G?` here reads `N` for commits the host verifies, so ask the
host: `gh api repos/<owner>/<repo>/commits/<sha> --jq .commit.verification`.

| Pull requests | Into | State at the stamp | Done when |
|---|---|---|---|
| #138, then #139 stacked on it | `main` | #138 conflicts with `main` in the document states and `loose-ends.json` only; #139 a draft, its checks green | `main` merged into #138 with those files regenerated, merged; #139 then retargeted, brought level, ready, merged |
| #168, #169 | `main` | conflicts in the document states and `loose-ends.json`; #168 also in the handoffs index | `main` merged in, generated files regenerated, both index rows kept, merged |
| #188 | `main` | conflicts in `perspectives/README.md` and `status/documents.yaml` | the same |
| #177 | `main` | conflicts in `ci/inbound.py` with #140's docstring sweep | resolved by hand, the code compared with both sides, merged |
| #173 (draft), #178 | `main` | their own commits unsigned on the host: six and nine | rebuilt signed per decision 3, the originals closed |
| #144, #147, #148, #149, #150, #151, #153, #156 | eight project branches | `slot` red, their branches on the old rule; otherwise green and conflict-free | `main` propagated into each branch (`propagate/<name>-<date>`, a merge, never a rebase), each pull request brought level, merged |
| #121, #145, #171, then #172 on #171, and #154 on #121 | `project/apothecary` | `slot` red; #121 has 33 of its 34 commits unsigned and #171 its one; #172 is the propagation, stacked on #171; #154 conflicts in `adr/README.md` | #171 and #172 closed; a propagation of current `main` straight onto the branch; #171 rebuilt signed; #121 rebuilt signed or kept, which is a person's call (§3); #154 restacked on #121's result |
| #146, #155, then #163 to #185 in order | `project/codecartographer` | the branch has the stack rule since #174; #155 green and `CLEAN`; each later one carries the ones before it | each brought level and merged in order, the records' wording settled first (§3) |

A propagation's own `slot` check passes, because the merge brings the new
script; a pull request into the branch passes only once brought level after
it. The codecartographer propagation (#174) showed both.

## 3. Blocked on a person

- **`joe` #33's merge**, on a test by hand (`voice-set-landing.md` §4).
- **The codecartographer records' reported speech.** Their Context sections
  report the operator's words and narrate how each decision came about ("set
  by the operator when asked", "Rejected by the operator in exactly those
  words"), which `records/DRAFT-durable-text-states-what-is-true.md` and
  `records/DRAFT-what-is-not-the-organisation.md` rule out. The wording
  survives to the chain's last pull request. Whether to merge the chain and
  restate every record in one pull request after it, or reword each on the
  pull request that adds it, was asked and not answered.
- **`project/apothecary`'s unsigned history.** #121's 33 commits are unsigned,
  dated 2026-09-18 to 2026-10-13. No signature check runs on a pull request
  into a project branch, so nothing refuses them; rebuilding signed changes
  every hash on the branch #154 is stacked on.
- **The dependency bots' pull requests** across the estate, about half of the
  open ones: merge, batch or close is a policy, not a review.
- **The decisions in `hil-review-2026-10-04.md` §3** and the two carried in
  `voice-set-landing.md` §4.

## 4. Unfinished, and what done looks like

- **`qmcp` Phase 1**, reconciling the onboarding and architecture pages. Done
  is the plan's own: every onboarding command checked against the current CLI,
  the architecture and deployment pages agreeing with the code, and a reader
  able to tell which voice actions record, which edit a take, and which run a
  command. Phases 2 and 3 follow, each with its condition in the plan.
- **The triage loop**, after Phase 3: a read-only `qm triage` building the
  table in §2 from the host or from a recorded snapshot; the snapshot of this
  queue and its findings as offline fixtures (the old `slot` rule, the
  unsigned commits, generated-file conflicts, the re-sign check, the local
  runner's ref name); `qmcp` declaring it as a `qm` check; a scripted cookbook
  case; an onboarding page. Done is the classifier reproducing this queue's
  classes offline.
- **The local workflow runner's ref name.** `run_workflows_locally.py` sets
  `GITHUB_REF_NAME` to `--ref`, `main` by default, for a pull-request event,
  where the host sets `<number>/merge`; on a project-branch pull request the
  ADR lint's *default branch carries no project records* step then reads red
  locally and green hosted. Done is a seed change with a test, and a local run
  of a project-branch pull request agreeing with the host.
- **codecartographer's `adr/TEMPLATE.md`** keeps five drafting-rule headings
  in capitals that the seed's template sets in plain case. Done is the copy
  re-made in a pull request into `project/codecartographer`.
- **The entry documents' reading load** is at 1200 of its 1200 lines, this
  page's row in the handoffs index included. The next line added to
  `AGENTS.md`, the charter, the async contract or the handoffs index needs one
  taken out, or the budget amended in its record.
- **The older handoff pages.** Step 7 of `handbook/consolidation-runbook.md`
  was applied to the voice pages only. Of the other pages, none names an open
  pull request but `design-review-of-the-estate.md` (#121), and several are
  blocked on a person's decisions; each needs reading before it is retired or
  folded. Done is the runbook's verification.

## 5. Not verified

- That a propagation clears `slot` on the eight branches in §2: established on
  `project/codecartographer` only.
- Why `qmcp`'s suite skips nine tests at `df42315`; the count was read, not
  the reasons.
- Tier 3 of the voice demonstration, a person at the microphone.

## 6. Local state at the stamp

Nothing of this page's work is unpushed.

- `qm`: the clone on `main`, clean; `qm.worktrees/demo` on the demo branch.
- `qmcp`: the clone on `demo/voice-loop-2026-10-04`; `qmcp.worktrees/integration`
  detached. Three worktrees made by another session, each clean and on a
  branch with no upstream and no copy on origin: `alfred-captions` on
  `feat/alfred-captions`, `alfred-health` on `fix/alfred-health-shape`,
  `alfred-tools` on `feat/alfred-tools`, last committed on 2026-10-18. A
  session picking them up reconciles with the one that made them first.
- `vox` on `main` with `vox.worktrees/demo`; `joe` on its demo branch.

## 7. Standing constraints

- *Keep everything local* is **not** in force.
- `main` is never pushed directly; everything arrives by a pull request.
- Project branches take changes in and never out: records reach them on a pull
  request based on `project/<name>`, and `main` reaches them as a
  `propagate/<name>-<date>` merge, never rebased.
- `qm` and `joe` delete a head branch on merge (`delete_branch_on_merge`), so
  `qm merge` reports a retarget it could not make after the host has already
  made it; read the stacked pull request's base, not the message. It refuses a
  pull request whose `slot` run is pending, which a body edit starts.
- `uv run qm docs check` runs in no workflow and no preflight step; run it
  before a pull request is ready.
