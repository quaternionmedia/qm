# Handoff — the rest of qm's pull-request queue

**Stamped 2026-10-24.** `qm` `main` at `bc38ab6`; `qmcp` `main` at
`bae518f`; `vox` `main` at `1721e6f`; `joe` `main` at `d72b65b`. Every figure
on this page was true at those commits and nowhere else. Re-derive each one
with `gh` and the tree before acting on it: the queue moves under other
sessions.

[`voice-set-landing.md`](voice-set-landing.md) is the voice set, landed but
for `joe` #33 and #34; [`the-voice-loop.md`](the-voice-loop.md) is the loop.
This page is everything else open in `qm`.

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
4. **"its minutes are billed"** stays in the workflow headers. (2026-10-17)
5. **Dependabot's updates are grouped per repository**: each repository's
   `dependabot.yml` carries `groups:`, so updates arrive as one pull request
   per ecosystem per interval, and an open ungrouped one is closed once its
   grouped replacement opens. (2026-10-24)

## 2. `qm`'s open pull requests, and what clears each

`uv run qm stacks --repo quaternionmedia/qm` lists them. Two causes account for
most of the red: a project branch that took `main` before the stack rule
carries the old `slot` check, which refuses every pull request into it after
the first; and commits made on 2026-10-13 that the host reads as unsigned.
`git log --format=%G?` here reads `N` or `E` for commits the host verifies, so
ask the host: `gh api repos/<owner>/<repo>/commits/<sha> --jq
.commit.verification`.

| Pull requests | Into | State at the stamp | Done when |
|---|---|---|---|
| #138, then #139 stacked on it | `main` | #138 conflicts with `main` in the document states, `loose-ends.json`, `families.json` and the walkthrough family pages, which regenerate, and in `ci/rollout.yaml`, `ci/tests/test_make_workspace.py`, `docs/usage/questions-a-new-developer-asks.md` and `handbook/adoption-audit-queue.md`, which do not; #139 a draft, its checks green | `main` merged into #138, the generated files regenerated and the other four resolved by hand, merged; #139 then retargeted, brought level, ready, merged |
| #168, #169 | `main` | conflicts in the document states and `loose-ends.json`; #168 also in the handoffs index | `main` merged in, generated files regenerated, both index rows kept, merged |
| #188 | `main` | conflicts in `perspectives/README.md` and `status/documents.yaml` | the same |
| #177 | `main` | conflicts in `ci/inbound.py` with #140's docstring sweep | resolved by hand, the code compared with both sides, merged |
| #173 (draft), #178 | `main` | their own commits unsigned on the host: six and nine; #173 also conflicts with `main` in `perspectives/README.md` | rebuilt signed per decision 3 from current `main`, the originals closed |
| #144, #147, #148, #149, #150, #151, #153, #156 | eight project branches | `slot` red, their branches on the old rule; otherwise green and conflict-free | `main` propagated into each branch (`propagate/<name>-<date>`, a merge, never a rebase), each pull request brought level, merged |
| #121, #145, #171, then #172 on #171, and #154 on #121 | `project/apothecary` | `slot` red; #121 has 33 of its 34 commits unsigned and #171 its one; #172 is the propagation, stacked on #171; #154 conflicts in `adr/README.md` | #171 and #172 closed; a propagation of current `main` straight onto the branch; #171 and #121 rebuilt signed per decision 3; #154 restacked on #121's rebuild |
| #146, #155, then #163 to #185 in order | `project/codecartographer` | the branch has the stack rule since #174; #155 `CLEAN`, its record stating its constraint and choices as its own; each later one carries the ones before it | each brought level and merged in order |
| #212 to #216, #218; #217 on #215, then #220 on #217 | `main` | each ready and level, but for the two drafts in their stack | each merged by its author once every gate is green; #217, then #220, moves down as the one beneath merges |
| #196 | `main` | level with `main`, green | merged |

A propagation's own `slot` check passes, because the merge brings the new
script; a pull request into the branch passes only once brought level after
it. The codecartographer propagation (#174) showed both. #219 is another
session's and outside this page.

## 3. Blocked on a person

- **`joe` #33's merge**, on a test by hand (`voice-set-landing.md` §4).
- **The decisions in `hil-review-2026-10-04.md` §3** and the two carried in
  `voice-set-landing.md` §4.

## 4. Unfinished, and what done looks like

- **`project/apothecary`'s unsigned history.** #121's 33 commits are unsigned,
  dated 2026-09-18 to 2026-10-13. `project/apothecary` is one of eight project
  branches without `signature-check.yml`, so nothing on a pull request into it
  refuses them. Done is #121 rebuilt signed per decision 3, and #154 restacked
  on the rebuild.
- **Dependabot's updates, grouped** (decision 5). At the stamp Dependabot holds
  125 of the org's 312 open pull requests. Done is every repository's
  `dependabot.yml` carrying `groups:`, and no ungrouped Dependabot pull request
  open.
- **The local workflow runner's ref name.** `run_workflows_locally.py` sets
  `GITHUB_REF_NAME` to `--ref`, `main` by default, for a pull-request event,
  where the host sets `<number>/merge`; on a project-branch pull request the
  ADR lint's *default branch carries no project records* step then reads red
  locally and green hosted. #198 is the change, with its test. Done is #198
  merged, and a local run of a project-branch pull request agreeing with the
  host.
- **codecartographer's `adr/TEMPLATE.md`** keeps five drafting-rule headings
  in capitals that the seed's template sets in plain case. Done is the copy
  re-made in a pull request into `project/codecartographer`.
- **The entry documents' reading load** is at 1200 of its 1200 lines, this
  page's row in the handoffs index included. The next line added to
  `AGENTS.md`, the charter, the async contract or the handoffs index needs one
  taken out, or the budget amended in its record.
- **The older handoff pages.** Step 7 of `handbook/consolidation-runbook.md`
  is applied to the voice pages and to the six pages the index tagged "read
  this first" or "read this second" on 2026-10-24, whose open items are carried
  below. Of the rest, none names an open pull request but
  `design-review-of-the-estate.md` (#121) and `hil-review-2026-10-04.md` (#138,
  #139), and several are blocked on a person's decisions; each is read by what
  it holds, not by its date, before it is retired or folded. Done is the
  runbook's verification.

### Carried from retired pages

Re-derived on 2026-10-24 unless marked *carried*; a carried item was not
re-checked and is re-derived before anyone acts on it.

- **`one-pr-check.yml` in every project.** On four projects' default
  branches; absent on alfred, apothecary, datum, dossier, factorio-sysops,
  qmetronome and rad, and not read for the private projects. Done is the
  workflow on every project's default branch, which follows the propagations
  in §2 and a copy in each project.
- **Unsubstituted placeholders.** Seven project branches' `adr/README.md`
  still reads `project/<name>`: alfred, apothecary, factorio-sysops,
  qmetronome, `private-32`, `private-33` and `private-34`.
  `project-seed/ci/check_placeholders.py` refuses it at each branch's next
  propagation. Done is that check clean on every project branch.
- **`handbook/async-contract.md` names an adapter's command** (`/cowork`), where
  a governance page names no tool. Done is the page stating the rule and
  pointing at `adapters/` for any mechanism.
- **rad.** Its numpad record (`adr/DRAFT-the-menu-addresses-nine-cells.md` in
  rad) is `Proposed`. Its records live in its own tree (`RECORDS_DIR: adr`)
  while `project/rad`'s `adr/` holds the template, and whether they move is
  undecided. Its conformance vectors carry no modality tag, so a keyboard-only
  host can run them only by curating a subset; that is a proposal to rad, not a
  local subset. The menu's cells (placement order, the empty centre,
  reachability by direction, the chord window) are not in the vectors.
- *Carried.* **dossier reaches every language model through qmcp** (decided
  2026-08-23), and nothing is built: dossier reads qmcp only through its schema
  seam. A conversation started from dossier needs a writable thread source in
  qmcp, and every send passes the budget gate in `qmcp/spend.py`.
- *Carried.* **The qmcp–dossier pair reconciles rather than connects**: a
  payload crosses as a file a person names. Done is one side reading the
  other's state with no filename on a command line, every figure keeping its
  age.
- *Carried.* **qmcp cannot cut a tag** while its suite skips tests on missing
  optional dependencies. Done is `check_tag_claims.py --test-output` accepting a
  captured run.
- *Carried.* **The public demo corpus**: the warm-up on demand, and the
  narrowing to public non-fork repositories at fetch rather than after.
- *Carried.* **dossier's `tests/ui` fixtures**: two duplicate `test_session`
  in the parent `conftest`, and three different fixtures sharing a name.
- *Carried.* **Two README structures**: the corpus README's routing table needs
  vocabulary a newcomer lacks, and dossier's opens with badges, screenshots and
  a quickstart before any prose. Each is a judgement about what matters most.

## 5. Not verified

- That a propagation clears `slot` on the eight branches in §2: established on
  `project/codecartographer` only.
- Tier 3 of the voice demonstration, a person at the microphone.
- #216's `edited` trigger on the three `main`-only gates. The local runner
  does not model a retarget, so it is first observed on the next stacked pull
  request retargeted onto `main`.

## 6. Standing constraints

- *Keep everything local* is **not** in force.
- Nothing of this page's work is unpushed.
- `main` is never pushed directly; everything arrives by a pull request.
- Project branches take changes in and never out: records reach them on a pull
  request based on `project/<name>`, and `main` reaches them as a
  `propagate/<name>-<date>` merge, never rebased.
- `qm` and `joe` delete a head branch on merge (`delete_branch_on_merge`), so
  `qm merge` reports a branch it could not delete after the host has already
  deleted it; read the stacked pull request's base, not the message. It refuses
  a pull request whose `slot` run is pending, which a body edit starts.
- `uv run qm docs check` runs in no workflow and no preflight step; run it
  before a pull request is ready.
