# Handoff — the rest of qm's pull-request queue

**Stamped 2026-10-24.** `qm` `main` at `8a6002b`; `qmcp` `main` at
`a41f9a3`; `vox` `main` at `1721e6f`; `joe` `main` at `d72b65b`. Every figure
on this page was true at those commits and nowhere else. Re-derive each one
with `gh` and the tree before acting on it: the queue moves under other
sessions. Entries that name 2026-10-25 were re-derived later, at `qm`
`7072174` and `qmcp` `82b2d58`, and every `qmcp` entry was read again at `qm`
`222ad7a`, `project/qmcp` `f4786fe` and `qmcp` `8aece3e`. Entries that name
2026-10-26 were re-derived at `qm` `fa376e0`, `qmcp` `8aece3e` and `joe`
`474307f`, and those that name 2026-10-27 from `qmcp`'s remote branches that
day. Entries that name 2026-10-31 were re-derived at `qm` `debf210`. The rest of the page holds at the stamp, which those entries do not
move.

[`voice-set-landing.md`](voice-set-landing.md) is the voice set, whose last
two `joe` pull requests merged on 2026-10-26, and the steps after it;
[`joe-open-set.md`](joe-open-set.md) is `joe`'s pull requests opened after it,
#35 to #58, which a person merges one at a time;
[`the-voice-loop.md`](the-voice-loop.md) is the loop;
[`apothecary-merge-queue.md`](apothecary-merge-queue.md) is apothecary's stack,
landed on its `main`, and how it keeps landing;
[`the-triplet.md`](the-triplet.md) is the triplet's graph leg, from the pages on. This page is everything else open in `qm`.

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

1. **A question to a person concerns what a change says or does**: what a
   page, a record, a check or a tool should state, and which of two readings
   of a rule is meant, one question at a time. How the change is delivered
   follows the corpus rules without a question: its branch and base, one pull
   request or two, landing it once every gate is green (`AGENTS.md` item 3),
   generated documents re-run rather than hand-merged, a propagation of `main`
   into a project branch, and deleting a branch whose every commit another
   branch holds. A step that would destroy work nothing else holds, such as
   unpushed commits or a ref `docs/ref/namespaces.md` names, is asked first,
   in terms of the work. (2026-10-18; widened 2026-10-26)
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
7. **Work is delivered into a repository, never to a hosted page**: a
   report, a demo, a preview or a handoff is a committed file, and reaches
   a reviewer as a pull request or as a page built and served locally
   (`records/DRAFT-work-is-delivered-into-a-repository.md`, on `main` since
   `d85dd12`). (2026-10-24)
8. **qmcp's adoption record is restated in two steps.** C2, C3 and C7 were
   restated by the pull request merged into `project/qmcp` as `6a4819a`.
   C1, C5, C6 and C8 come next, in a pull request of their own based on
   `project/qmcp`. (2026-10-24)

9. **A remembered approval covers runs that spend nothing, and nothing
   else.** Phase 11 of `qmcp`'s roadmap, habits into auto-approvals, is built
   on that reading of `records/DRAFT-no-unattended-spending.md`. (2026-10-31)
10. **`match_option`'s wider reading holds for every closed choice**, the
    approval dialog included: a hyphen is a word break, and of several options
    named the one covering the others wins. (2026-10-31)
11. **Instruct by voice sits in joe's Voice window**, which the dock opens from
    a transport button, a key or the Panels menu and closes after the stream or
    the queue ends, as joe's dock pull request has it. (2026-10-31)
12. **joe adopts the corpus after its open set has landed**: a joe pull request
    adds `governance/qm` by its HTTPS URL, the seed's `AGENTS.md` and
    workflows, and `project/joe` takes its propagation; nothing opens before
    the set is in. joe's README pull request and its lane-pages pull request
    stand for `voice-set-landing.md` §3's README and cookbook rows. (2026-10-31)
13. **`openai-whisper` becomes an optional `voice` extra of joe**, in a pull
    request after the set lands: joe without it serves the media API and the
    page, and says so where a voice route is asked. (2026-10-31)
14. **joe's open set lands in `joe-open-set.md`'s order, merged by the session
    that readies each pull request** once its gates are green and its §4 fix is
    on it; the checklist in `joe-manual-validation.md` is walked against
    `main` afterwards, and a finding becomes a fix pull request. This
    supersedes that page's decision 1. (2026-10-31)
15. **`status/governance.yaml`'s open questions are settled**: records on
    project branches are listed per project and do not count in the corpus's
    figure; CI holds no credential for private repositories, and whoever opens
    a pull request touching the status documents regenerates them, the owner
    weekly otherwise; gap detail about a private project is published by
    reference; a committed status document and the refusal to commit a gate's
    output square as `handbook/generated-documents.md` states; a project's
    vendored copy is true at its pin, which is its stamp. (2026-10-31)
16. **loopwall is public and is rostered by name.** The repository rostered
    as `private-34` was made public on 2026-10-31; its roster row carries its
    name, and the pages and fixtures that name it by reference are renamed in
    a sweep of their own. (2026-10-31)
17. **benchmark's `main` requires no status check for now**: the three
    contexts its protection named came from a matrix its workflow no longer
    has, and the workflow runs on pushes to `main` alone. A pull request gives
    `deploy.yml` a `pull_request` trigger, after which the protection requires
    `test`. (2026-10-31)
18. **The design review of this corpus runs from its handoff page**, Part 1
    only, with the owner's charge: a stranger's first hour before the alpha.
    The consent request that waited on the harness since 2026-09-28 is
    superseded by that start. (2026-10-31)
19. **A shared workflow is exercised from a consumer before it merges**:
    the organisation's shared Python workflows, moved to Node 24 actions with a
    Python version, submodules and pip arguments as inputs, were taken on
    holophonor's run of the black and ruff workflows at the branch, and merged.
    (2026-10-31)

## 2. `qm`'s open pull requests, and what clears each

No pull request into `main` is this page's; every one it names is into a
project branch. `uv run qm stacks --repo
quaternionmedia/qm` lists them. Two causes account for most of the red: a
project branch that took `main` before the stack rule carries the old `slot`
check, which refuses every pull request into it after the first; and commits
made on 2026-10-13 that the host reads as unsigned.
`git log --format=%G?` here reads `N` or `E` for commits the host verifies, so
ask the host: `gh api repos/<owner>/<repo>/commits/<sha> --jq
.commit.verification`.

| Pull requests | Into | State at the stamp | Done when |
|---|---|---|---|
| #147, #148, #149, #150, #151, #153, #156 | seven project branches | `slot` red, their branches on the old rule; otherwise green and conflict-free | `main` propagated into each branch (`propagate/<name>-<date>`, a merge, never a rebase), each pull request brought level, merged |
| #144 | `project/alfred` | `slot` red on the old rule; `project/alfred` carries `main` since its propagation of 2026-10-31 (`d324759`) | brought level with `project/alfred`, merged |
| #121, #145, #171, then #172 on #171, and #154 on #121 | `project/apothecary` | `slot` red; #121 has 33 of its 34 commits unsigned and #171 its one; #172 is the propagation, stacked on #171; #154 conflicts in `adr/README.md` | #171 and #172 closed; a propagation of current `main` straight onto the branch; #171 and #121 rebuilt signed per decision 3; #154 restacked on #121's rebuild |
| #146, #155, then #163 to #185 in order | `project/codecartographer` | the branch has the stack rule since #174; #155 `CLEAN`, its record stating its constraint and choices as its own; each later one carries the ones before it | each brought level and merged in order |

A propagation's own `slot` check passes, because the merge brings the new
script; a pull request into the branch passes only once brought level after
it. The codecartographer propagation (#174) showed both. On 2026-10-26
`project/codecartographer` took `main` at `2c4cb11` again, at merge `4084965`, so
each pull request into it is behind its base until brought level.

## 3. Blocked on a person

- **qmcp's control-plane record**, `adr/DRAFT-control-plane-and-engine-boundary.md`
  on `project/qmcp` (2026-10-25), is `Proposed` and pends on two inputs: (a)
  whether the clients `qmcp` ships beside its seam, the cookbook's flows and
  the agent library, stay in its repository; (b) whether `vox` gains a
  release line, which decides whether it is an engine `qmcp` consumes or seam
  code.
- **Applying the rulesets.** `.github/rulesets/README.md` sets out the staged
  path and shows the host at stage 0, no ruleset applied. Stage 1 is a person
  running `apply.sh`; an agent never does.
- **A shared-conversation link in `main`'s history**, named in
  `views-declare-what-they-need.md`: recoverable from commit `0c1ac0b`, and it
  still answers. Removing it from the working tree did not remove it from
  history; revoking it where it was shared is the one act that closes this,
  and it is the owner's.
- **cathy's real-export demo** waits on the owner's download of the site's
  export, placed as `export.xml` beside a `cathy.toml` in a folder that
  belongs to the site and never in cathy's repository.
- **alfred #113**, a configuration change of 2023 by another contributor,
  is left as it is for now, with alfred's branches that exist on one disk
  alone and titanharvest's design branch.
- **The decisions in `hil-review-2026-10-31.md` §4**: alfred's and
  titanharvest's branches that exist on one disk alone; the worktrees only a
  person may remove.

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
  Dependabot pull request and no open alert. Its one leftover Dependabot
  branch, whose pull request was closed on 2026-10-25 because `main` already
  locks the version it set, was deleted on 2026-10-27 at the person's word.
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
- **alfred's detail page shows its pictures.** Its seven screenshots are on
  alfred's stack from alfred #126, `integrate/wave-6`, up, and not on its
  `main` (2026-10-29), so its page on the site shows each as waiting. Done is
  alfred's stack merged, then
  `uv run qm inventory --write` and `uv run qm cookbook docs/families --site
  --write` in a pull request here.
- **The namespaces are declared by hand, in several places.**
  `docs/ref/namespaces.md` is canonical; `AGENTS.md` item 3, `README.md` and
  `.github/rulesets/E-naming.json` each restate it, and
  `project-seed/ci/check_pr_base.py` carries its own prefixes. A copy in
  `handbook/governance-rollout.md` had drifted before it became a pointer.
  Done is one declaration from which the table and the ruleset are generated
  and which the base check reads. The design is in
  `handbook/handoffs/exploration-namespace.md`'s "Decisions taken, 2026-08-15"
  on `evolve/exploration-branch-namespace` at `22d7319`.
- **Nothing checks that `AGENTS.md`'s verification discipline reaches a
  project.** `project-seed/ide/AGENTS.md` is a real file in adapted wording, so
  a rule added to the root page reaches forks only when someone copies it.
  Done is a check that fails when a discipline rule in the root page has no
  counterpart in the seed's. `ci/check_discipline_parity.py` on
  `evolve/exploration-branch-namespace` at `22d7319` is a draft of one.
- **`qm references` overstates what retiring a merged branch loses.** For a
  branch whose tip is on `main`, it says a reference left behind points at
  nothing; the cited commit and pull request survive, and only the name stops
  resolving. Done is the report saying so when the tip is an ancestor of the
  base. (2026-10-26)
- **A pushed branch ahead of its copy is not checked for a holder.** `qm
  estate`'s *ahead* and the census's *stranded* count unpushed commits against
  the branch's own remote copy only, so commits another remote branch holds
  read as on this disk alone. Done is the held reading, confirmed by the host,
  applied to those classes too, with a fixture case for each. (2026-10-26)
- **`qm estate` run from a worktree surveys a different estate.** Its default
  search root is two directories above the module, and the private companion
  is read beside the module; from a sibling worktree the first is a level too
  deep and the second is absent, and on 2026-10-26 it found 22 of the 39
  clones a run from the clone finds. Done is a run from a worktree finding the
  same clones as a run from the clone.
- **The private-name check fails on `main`.** At `fa376e0`, `uv run qm
  private-names --source host --strict` finds 25 occurrences, most of them in
  `docs/show/`, where a file path or a word in a public repository equals a
  private repository's name. Done is the check clean, by redaction in the
  show generator or by an allowance with a stated reason. (2026-10-26)

- **Two green pull requests left a generated page on `main` stale, and no gate
  saw it.** The pull request that put cathy in the roster moved the roster,
  and the one that drew every showgraph as a Showcase carried
  `docs/families/index.md` as generated before it; each passed
  `docs-audit.yml` at its own tip, and
  merged in that order they left `main`'s page one rostered repository
  behind. The audit runs on `pull_request` alone, filtered to `docs/**` and
  the generator's inputs, so `main` was never checked after either merge and
  the red surfaced on the next pull request that touched `docs/`, as a
  failure its branch did not cause. Three local runs the same day read the
  step's wording, *no longer describe this disk*, as an environment
  difference; the host's run and a regeneration from `main` showed the same
  one-line drift. Done is the audit running on every push to `main` as well,
  so a stale generated page is `main`'s red and not the next contributor's,
  and the step saying *stale against its committed inputs* rather than
  naming a disk. `hil-review-2026-10-31.md` §5 names the three pull requests.
  (2026-10-31)

- **benchmark's workflow runs on pull requests.** `deploy.yml`'s `test` job
  runs on pushes to `main` alone, so no pull request into benchmark produces
  a check its protection could require. Done is a `pull_request` trigger for
  the `test` job, `deploy` kept to pushes to `main`, and the protection
  requiring `test` again. (2026-10-31)
- **loopwall by name.** The roster row carries the name; the pages and
  fixtures that name it by reference, `private-34-simultaneous-run.md`,
  `ci/family-demo.yaml`, two tests and the show documents under `docs/show/`,
  still read `private-34`. Done is every tracked file naming it, the show
  documents regenerated, and `git grep private-34` empty. (2026-10-31)
- **joe's voice extra and joe's adoption** follow the set's landing
  (decisions 12 and 13). Done is each as its own joe pull request, and
  `project/joe` level with `main`.
- **cathy's stack lands.** cathy#1 moves its governance pin to
  `project/cathy`'s tip and merges; #2 is retargeted onto `main` before the
  adopt branch is deleted, readied, merged; #3, then #4 brought level with
  `tests/test_convert.py` keeping both sides. Done is no open pull request in
  cathy and its suite passing on `main`. Beside it, the independent bypass
  pass on `tests/test_network_boundary.py` that cathy's `AGENTS.md` item 12
  asks for, with a narrower brief than the one a safety classifier stopped.
  (2026-10-31)
- **The governance generator's `undefined` block is static text**, and its
  entry on the `propagate/*` namespace is stale: `docs/ref/namespaces.md`
  declares that namespace. Done is the entry removed or computed from the
  namespaces page, and `fix/*` checked the same way. (2026-10-31)
- **The checklist is walked.** `joe-manual-validation.md` against joe's
  `main` once the set is in; a finding becomes a fix pull request. (2026-10-31)

### Carried from retired pages

Re-derived on 2026-10-24 unless marked *carried*; a carried item was not
re-checked and is re-derived before anyone acts on it.

- **`one-pr-check.yml` in every project.** On four projects' default
  branches; absent on alfred, apothecary, datum, dossier, factorio-sysops,
  qmetronome and rad, and not read for the private projects. Done is the
  workflow on every project's default branch, which follows the propagations
  in §2 and a copy in each project. alfred's copy is the seed's file
  verbatim, and passes on its stack as it stands on 2026-10-29: every stacked
  pull request is a draft, and alfred #117, the bottom one, is ready on
  `main`. alfred's `main` has no governance submodule yet, and its stack
  pins `e76827d`, where neither script the workflow runs exists;
  `project/alfred` carries both since its propagation of 2026-10-31, voice
  step exempting automation accounts included. The copy
  goes onto alfred's stack with a pin bump, and reaches its `main` when the
  stack lands.
- **Unsubstituted placeholders.** Six project branches' `adr/README.md`
  still reads `project/<name>`: apothecary, factorio-sysops, qmetronome,
  `private-32`, `private-33` and `private-34`.
  `project-seed/ci/check_placeholders.py` refuses it at each branch's next
  propagation, so the propagation substitutes it, as alfred's did on
  2026-10-29. Done is that check clean on every project branch.
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
- **qmcp's adoption record, C1, C5, C6 and C8** (decision 8). Their readings
  at `qmcp` `a41f9a3` are under "Outside this pull request" in the
  description of the pull request merged into `project/qmcp` as `6a4819a`.
  Done is a pull request based on `project/qmcp` that restates the four
  rows, then a `qmcp` pin bump that takes it. `qmcp`'s pin has been `f4786fe`
  since 2026-10-25, and that commit does not carry the four rows.
- **Three of qmcp's tests name the project after the checkout's directory.**
  `qmcp/instructions/check.py:403` resolves `project or clone.name`, so three
  tests in `tests/test_cookbook_instruct.py` fail in any checkout not named
  `qmcp`, a worktree among them. Done is those tests passing the project's
  name. (2026-10-25)
- **No gate measures how far a project's pin lags `main`.** On 2026-10-25,
  until the propagation merged into `project/qmcp` as `777a275`, `qmcp`'s pin
  was two commits behind that branch and the branch 343 behind `main`. Most
  of the drift a `qmcp` session read at its open was that lag. `status/governance.yaml` carries
  `behind_corpus`, and nothing gates on it. Done is a check that goes red past
  a stated lag, seen to fail.
- **A host-sourced check meets an unpushed commit.** Run locally,
  `signature-check.yml` reports a signed commit the host has not seen as
  unverifiable, where `check_signatures.py --source git` reports it good.
  Done is the runner saying which source answered. (2026-10-25)
- **The local runner says nothing of an uncommitted tree.** It runs in the
  checkout, and on 2026-10-25 a run over edits not yet committed measured the
  commit before them; the same run after the commit measured the edits. The
  inference is that the steps reading what a change adds read `git diff`
  against the base, which sees commits only, while the steps reading files
  see the tree. Done is the runner refusing, or naming the dirty paths, when
  the tree has uncommitted changes, seen to fire. (2026-10-26)
- **`qm branches` read landed work as held by this clone alone.** On
  2026-10-25 it listed `adr/qmcp-control-plane`,
  `fix/qmcp-seed-refresh-2026-10-25` and `propagate/qmcp-2026-10-25` so, and
  `git merge-base --is-ancestor` then found each tip in `project/qmcp`. Which
  path through `project-seed/ci/branch_census.py` produced it was not traced:
  its patch comparison reads the default branch alone, which fits, and its
  holder search reads every remote branch, which should have found
  `project/qmcp`. Done is the case reproduced in a test and the census
  reading it as held. (2026-10-26)
- **`qm docs generate` has no mode for a page's own indexes.** A pull request
  that adds a page needs `status/documents.yaml`, `handbook/document-states.md`
  and `loose-ends.json` regenerated; the full generator also rewrites the
  host-sourced documents, and on 2026-10-26 ran past five minutes. Done is
  that mode, or `handbook/consolidation-runbook.md` Step 8 naming
  `ci/doc_status.py`, `ci/doc_dashboard.py` and `ci/loose_ends.py` for it. Until then the three steps are
  `ci/doc_status.py --write status/documents.yaml`,
  `ci/doc_dashboard.py status/documents.yaml --out handbook/document-states.md`
  and `ci/loose_ends.py --write loose-ends.json`, run after taking `main`'s
  copy of each conflicting file; every pull request that lands re-conflicts
  every other open one on those three files, and each is brought level the
  same way, once per landing.
- **Only qmcp says which server it is.** `qm instances` identifies a server
  whose health answer names its pid and port; on 2026-10-29 qmcp's did, and
  codecartographer's checkout served no health route, and looksatwords'
  health named no pid. Every other server reads as `answering`, attributed by
  its run-file alone. Done is each serving repository's health route naming
  its pid and port, as `qmcp/instance.py` does, and `qm instances` reading it
  as `identified`. (2026-10-29)
- **The family demo declares nothing.** `qm family-demo` keeps its members in
  a manifest, so while it runs every member reads as a listener nobody
  declared in its range, and a member this machine registers reads as
  `missing`. Done is the demo writing a run-file for each member it starts,
  with the run's name as its session. (2026-10-29)
- **qmcp's pages that predate its roles.** `docs/architecture.md` draws three
  planes, and the instruction loop appears in it only as a departure it names;
  the archive and speech do not appear. `qmcp tools list` lists the built-in
  tools only, where `GET /v1/tools` lists the `alfred_*` tools too. Done is
  each describing what the code does. (2026-10-25)
- **qmcp declares no licence where a packager reads one.** At `qmcp`
  `82b2d58` it carries `REUSE.toml` (MIT for `**`), `LICENSES/` and a REUSE
  lint workflow, but no root `LICENSE` and no `license` key in
  `pyproject.toml`. Done is a licence declared in both places, and C1
  restated in its adoption record (decision 8).
- **qmcp's roadmap still calls project names unmeasured.** Phase 10's
  constraints in `qmcp`'s `docs/ROADMAP.md` say "Whether project names
  transcribe reliably is unmeasured", and
  `perspectives/2026-10-25-what-whisper-heard.md` measures it on synthesized
  speech. Done is that line citing the perspective. Making that change was
  asked on 2026-10-25 and not yet answered.
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
- **Branches across the estate**: each repository's leftover one-copy
  branches landed or retired, and merged branches pruned, until `uv run qm
  estate` reports none. On 2026-10-26 `uv run qm estate --offline` reports
  one-copy work in codecartographer (one branch, one commit) and `private-38`
  (one branch, 60 commits), each checked out by a session at work that day.
  alfred's seven feature branches are *held*, every commit on a pushed
  branch, so deleting them loses only the names. `qmcp`'s were pruned on
  2026-10-25 at the person's word, and the one Dependabot branch above on
  2026-10-27; its remote holds `main` alone.
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
  runner. The local run of the pull request merged into `project/qmcp` as
  `6a4819a` needed `--ref` for that step to pass, because neither that branch
  nor `qmcp`'s pin had #229. Both have it at `f4786fe`, and no local run of a
  pull request into `project/qmcp` has been made since.
- `qmcp`'s provider SDKs as locked at `82b2d58` (anthropic 2.3.0, google-genai
  2.33.0, logfire 5.3.0) against their services. `-m live_anthropic` and the
  `--live` cookbook checks were not run. The offline suite, the local-model
  tests and the preflight passed.
- The figures in `perspectives/2026-10-25-what-whisper-heard.md` on a
  person's voice: they come from synthesized speech only.
- A holder the host has deleted or moved, as `qm estate` and the branch census
  read it online: exercised against a local bare remote only. Against the
  host, only holders whose tip equals the tracking ref have been read.
- That `joe`'s transcript lane was tested by hand before it merged on
  2026-10-26 (`joe` `c7dccf4`), as `voice-set-landing.md` decision 5 asked:
  its pull request carries no comment or review saying so. The session that
  asked for its merge records Peter's test (`joe-open-set.md` §2).
- That `docs-audit.yml`'s second step, *the pages match the corpus*, is green
  on `main`: every local run on 2026-10-31 skipped it, because the families
  step before it failed first (§4).

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
- A propagation pull request goes red on `namespace` once `main` moves past
  the commit it merged: the guard compares every file the merge brings with
  `main`'s tip. Merging `main` into the `propagate/*` branch again clears it;
  alfred's propagation took it so on 2026-10-29.
