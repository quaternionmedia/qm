# Handoff — the rest of qm's pull-request queue

**Stamped 2026-10-24.** `qm` `main` at `8a6002b`; `qmcp` `main` at
`a41f9a3`; `vox` `main` at `1721e6f`; `joe` `main` at `d72b65b`. Every figure
on this page was true at those commits and nowhere else. Re-derive each one
with `gh` and the tree before acting on it: the queue moves under other
sessions. Entries that name 2026-10-25 were re-derived later, at `qm`
`e225109` and `qmcp` `82b2d58`. The rest of the page holds at the stamp,
which those entries do not move.

[`voice-set-landing.md`](voice-set-landing.md) is the voice set, landed but
for `joe` #33 and #34; [`the-voice-loop.md`](the-voice-loop.md) is the loop.
This page is everything else open in `qm`.

## How this page is kept

This is the standing queue. A session keeps it current rather than writing a
handoff page of its own, unless its work needs a brief another session can
pick up alone; that page is then listed in the index and named here.

- **At open**, run `uv run qm queue`. It asks the host about every pull request
  and issue this page names and lists each one that merged or closed after the
  stamp. Every one it lists is a sentence here the host contradicts; read the
  page with that list beside it.
- **At close**, before the handoff's pull request is opened:
  - every pull request the session opened and left open is named here, with
    what clears it;
  - every one it merged or closed comes off, and an item it finished is deleted
    rather than marked done;
  - a decision that binds later sessions goes into §1, dated; a blocker into
    §3, unfinished work into §4, anything it could not verify into §5;
  - every figure the session relied on is re-derived, and only then is the
    stamp moved to the commits it was re-derived against;
  - `uv run qm queue` exits 0.
- **The check cannot see** a pull request this page never names, or whether a
  sentence claims a pull request is open, and a stamp moved without a re-read
  silences it. Those are read by the session.

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
6. **The entry documents' reading budget stays at 1200 lines**, though the
   load is below it: `records/DRAFT-governance-arrives-as-a-mechanism.md` §4's
   ratchet is not lowered to meet it. (2026-10-24)
7. **qmcp's adoption record is restated in two steps.** C2, C3 and C7 are
   restated on #235. C1, C5, C6 and C8 are restated only after #235 merges, in
   a pull request of their own based on `project/qmcp`. (2026-10-24)

## 2. `qm`'s open pull requests, and what clears each

Every pull request into `main` that this page carried has landed; what is open
is into project branches. `uv run qm stacks --repo quaternionmedia/qm` lists
them. Two causes account for most of the red: a project branch that took `main`
before the stack rule carries the old `slot` check, which refuses every pull
request into it after the first; and commits made on 2026-10-13 that the host
reads as unsigned.
`git log --format=%G?` here reads `N` or `E` for commits the host verifies, so
ask the host: `gh api repos/<owner>/<repo>/commits/<sha> --jq
.commit.verification`.

| Pull requests | Into | State at the stamp | Done when |
|---|---|---|---|
| #144, #147, #148, #149, #150, #151, #153, #156 | eight project branches | `slot` red, their branches on the old rule; otherwise green and conflict-free | `main` propagated into each branch (`propagate/<name>-<date>`, a merge, never a rebase), each pull request brought level, merged |
| #121, #145, #171, then #172 on #171, and #154 on #121 | `project/apothecary` | `slot` red; #121 has 33 of its 34 commits unsigned and #171 its one; #172 is the propagation, stacked on #171; #154 conflicts in `adr/README.md` | #171 and #172 closed; a propagation of current `main` straight onto the branch; #171 and #121 rebuilt signed per decision 3; #154 restacked on #121's rebuild |
| #146, #155, then #163 to #185 in order | `project/codecartographer` | the branch has the stack rule since #174; #155 `CLEAN`, its record stating its constraint and choices as its own; each later one carries the ones before it | each brought level and merged in order |
| #235 | `project/qmcp` | at 2026-10-25: 7 checks green, no review, head `7f2ff37`; it restates C2, C3 and C7 as read at `qmcp` `a41f9a3` | merged by a person (§3); then decision 7's second step, using the readings of C1, C5, C6 and C8 under "Outside this pull request" in #235's description; then `qmcp`'s governance pin bump (`the-voice-loop.md` §1) |

A propagation's own `slot` check passes, because the merge brings the new
script; a pull request into the branch passes only once brought level after
it. The codecartographer propagation (#174) showed both. #222, a draft into
`main`, is another session's and outside this page.

#251, into `main`, is a perspective that keeps the results of a voice
benchmark from a `qmcp` branch that has since been deleted. At 2026-10-25 its
9 checks are green, it has no review, and its head is `1ee9155`. It is done
when a person merges it (§3).

## 3. Blocked on a person

- **`joe` #33's merge**, on a test by hand (`voice-set-landing.md` §4).
- **#235's and #251's merges.** #235 changes a record and #251 adds a page,
  so each is asked (decision 1).
- **qmcp's open adoption decisions**, as #235 states them:
  - C3: two sessions started in one checkout share one queue, through the
    default port 3141 and a database path relative to the working directory.
  - C7: `POST /v1/human/responses` authenticates nobody.
  - C4: a `GET` writes `EXPIRED`.
  - Phase 11 of `qmcp`'s roadmap, auto-approvals from habits, is built only
    after the corpus has read it.
- **The decisions in `hil-review-2026-10-04.md` §3** and the two carried in
  `voice-set-landing.md` §4.
- **quaternionmedia/.github#9**, a draft on that repository's `main`: a Python
  version, submodules and pip arguments for the shared Python workflows, on
  Node 24 actions. Every action version it pins exists upstream; nothing in
  that repository runs the workflows it changes, so its one green check says
  nothing about them. Its review is a person's.
- **Applying the rulesets.** `.github/rulesets/README.md` sets out the staged
  path and shows the host at stage 0, no ruleset applied. Stage 1 is a person
  running `apply.sh`; an agent never does.
- **A share link committed on `main`**, in
  `views-declare-what-they-need.md`; `uv run qm leaks` allows it by a stated
  reason. Redact it, or confirm the link is dead.
- **rad's Pages.** GitHub Pages is disabled for rad, which its `deploy` job
  needs; a repository setting.
- **Held pull requests:** datum #2, alfred #113 and benchmark #7 — merge or
  close. (apothecary's, which this list also held, merged on 2026-10-24.)
- **Six questions about `status/governance.yaml`** that its `undefined:` block
  does not carry: whether project records count in the corpus census; whether
  CI gets a credential that can read private repositories; whether gap detail
  about private projects is published, now that it names them by reference;
  who refreshes the document; how a committed generated artifact squares with
  refusing to commit what a gate generated; and the stale copy every project
  vendors with the corpus.

## 4. Unfinished, and what done looks like

- **`project/apothecary`'s unsigned history.** #121's 33 commits are unsigned,
  dated 2026-09-18 to 2026-10-13. `project/apothecary` is one of eight project
  branches without `signature-check.yml`, so nothing on a pull request into it
  refuses them. Done is #121 rebuilt signed per decision 3, and #154 restacked
  on the rebuild.
- **Dependabot's updates, grouped** (decision 5). At the stamp Dependabot holds
  125 of the org's 312 open pull requests. Done is every repository's
  `dependabot.yml` carrying `groups:`, and no ungrouped Dependabot pull request
  open. At `qmcp` `82b2d58`, `qmcp` has no `dependabot.yml`, no open
  Dependabot pull request and no open alert. Its one Dependabot branch,
  `dependabot/uv/protobuf-6.33.5`, outlived its pull request. That pull request
  was closed on 2026-10-25 because `main` already locks the version it set.
- **The signature gate reads an SSH signature as none.** `check_signatures`
  runs `git` with no allowed-signers file, so a commit the host verifies by an
  SSH key reads `N` and fails the gate; #198's and #202's did, and landed as
  their rebuilds #229 and #230. Done is the gate reading the host's
  verification, or an allowed-signers file it is given.
- **The status generator names private repositories without the companion.**
  `uv run qm docs generate` in a checkout without `ci/workspace-private.yaml`
  writes a private project's branch name into `status/harness.yaml` and, from
  it, `loose-ends.json`; `uv run qm private-names --source host --strict`
  catches it before a commit, and runs in no workflow, so only a local run
  does. Done is the generator refusing to write, or redacting from the host,
  when the companion is absent.
- **The merge guard fails closed on a host hiccup.** `qm merge` reads the
  base's workflows from the host before it will merge; one read failing reports
  the gates as unknown and refuses, which happened once on #188 and merged on
  the retry. Done is a bounded retry inside the read, with the refusal kept for
  a read that keeps failing.
- **No gate refuses a conflict marker.** A cherry-pick continued past an
  unresolved index conflict committed `<<<<<<<` lines on a local branch; a
  count before pushing caught it. Done is a check, run on the lines a change
  adds, that refuses a conflict marker.
- **codecartographer's `adr/TEMPLATE.md`** keeps five drafting-rule headings
  in capitals that the seed's template sets in plain case. Done is the copy
  re-made in a pull request into `project/codecartographer`.
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
- **A project record relaxes a QM record.** qmetronome's glyph-matrix draft on
  `project/qmetronome` still calls itself "a real, accepted departure" from
  the QM record it relaxes. Done is the draft tightened, or the departure
  taken to the org as an amendment.
- **qmcp declares no licence where a packager reads one.** At `qmcp`
  `82b2d58` it carries `REUSE.toml` (MIT for `**`), `LICENSES/` and a REUSE
  lint workflow, but no root `LICENSE` and no `license` key in
  `pyproject.toml`. Done is a licence declared in both places, and C1
  restated in its adoption record (decision 7).
- **qmcp's roadmap still calls project names unmeasured.** Phase 10's
  constraints in `qmcp`'s `docs/ROADMAP.md` say "Whether project names
  transcribe reliably is unmeasured"; #251 measures it on synthesized speech.
  Done is that line citing #251's perspective once #251 merges. Making that
  change was asked on 2026-10-25 and not yet answered.
- **qmcp's `flows` extra asks for `pydantic-ai[openai]`**, an extra that no
  pydantic-ai release from 2.31 to 2.61 provides, so uv warns on every lock.
  Done is the extra naming what it needs.
- **No check reads qmcp's lock against open advisories before a pull
  request.** On the change that took `qmcp`'s lock past its 36 alerts (merged
  2026-10-25 as `82b2d58`), `uv lock --upgrade-package` stopped pydantic-ai at
  2.32.2, below the 2.53.0 that fixes one of its alerts, and reported it as
  updated. A one-off script that compared each alert's range with the lock
  caught it. Done is that comparison as a preflight step, or the reason it
  cannot be one.
- **Two lightweight tags**, `alfred@v0.2.0` and `datum@v0.0.1`, assert what
  `records/DRAFT-version-tags-are-claims.md` §6 says a lightweight tag cannot.
  Done is each replaced by an annotated tag or removed, by a person.
- **The governance document's `undefined:` block is partly stale.** Its
  `adopted` entry is answered by the phase-ladder record, and its
  `propagate/*` half by the namespaces page; `fix/*` stays outside the
  namespaces. Done is `UNDEFINED` in `ci/governance_status.py` saying so.
- **`qm estate --trial-merge`** does not exist. Done is the survey trial-merging
  each one-copy branch and reporting conflicts per file.
- **`check_signatures` on a commit the host has not seen** says "could not be
  checked", the words it uses for a keyring gap. Done is "not on the host".
- **Two views of one dataset.** dossier's and qmcp's dashboards showing the same
  rows by address: dossier runs the shared address vectors in its suite (its
  autolinker still slugs); pre-grammar dossier rows are migrated, or declared
  re-synced; qmcp's delta payload, which emits addresses through
  `qmcp/addresses.py`, moves its `SCHEMA` to 2; then each dashboard renders the
  other's rows.
- **The governance loop's Phases 2–4** are unbuilt: dossier's storage, API and
  Loop tab, and qmcp's coverage tools and human-in-the-loop gate. Their design
  is in `perspectives/2026-08-13-the-mechanical-governance-loop.md`.
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
- *Carried.* **qmcp's work planned as dossier deltas**, one per work item:
  topology runtime execution, a CI pipeline, the human-in-the-loop API, an
  async runner, authentication, webhooks, storage backends, Kubernetes
  manifests, and the cookbook and runner.
- *Carried.* **Branches across the estate**: each repository's leftover
  one-copy branches landed or retired, and merged branches pruned, until
  `uv run qm estate` reports none. `qmcp`'s were pruned on 2026-10-25 at the
  person's word, and its remote holds `main` and the one Dependabot branch
  above.
- *Carried.* **A guard for dossier's threaded UI workers**: a test that fails
  when a worker that can reach the network is missing from
  `tests/ui/conftest.py`'s stub list.
- *Carried.* **A check that every `project/<name>` branch has a roster entry**,
  treating an unmatched private branch as unknown where the companion is
  absent.

## 5. Not verified

- That a propagation clears `slot` on the eight branches in §2: established on
  `project/codecartographer` only.
- Tier 3 of the voice demonstration, a person at the microphone.
- That a local run of a project-branch pull request now agrees with the host
  on the ADR lint's *default branch carries no project records* step, which
  #229 changes the runner for. A project branch carries its own copy of the
  runner. At `b5775fa`, `project/qmcp` does not have #229, and neither does
  `qmcp`'s governance pin, `235708c`. #235's local run therefore needed
  `--ref` for that step to pass.
- `qmcp`'s provider SDKs as locked at `82b2d58` (anthropic 2.3.0, google-genai
  2.33.0, logfire 5.3.0) against their services. `-m live_anthropic` and the
  `--live` cookbook checks were not run. The offline suite, the local-model
  tests and the preflight passed.
- #251's figures on a person's voice: they come from synthesized speech only.

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
- The host's own retarget, when a merged branch is deleted, starts no
  `pull_request` workflow: #217, #220 and #139 ran nothing at theirs. A body
  edit fires `edited`. `qm merge` refuses a pull request whose `main`-only
  gates never ran, and a push to its branch starts them.
- `uv run qm docs check` runs in no workflow and no preflight step; run it
  before a pull request is ready.
