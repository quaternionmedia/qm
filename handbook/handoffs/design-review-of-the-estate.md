# Handoff — A design review of qm, then of the estate

**Stamped 2026-09-26.** `qm` `main` at `d6dc5cd`, the merge of #120. The
method's first run is apothecary #22: `review/2026-09-26` at `276d8b8` on
origin, cut from `1835b47`. Estate figures were read from the host the same
day. Every figure below was true then and nowhere else, and each names the
command that re-derives it.

This corpus is reviewed first by the method apothecary #22 ran, then the
estate in the order below. The method is
[`handbook/design-review-runbook.md`](../design-review-runbook.md). This page
fits it to a governance corpus, hands over what was measured here as leads to
test, and orders the other repositories.

Read [`README.md`](README.md) for the rules every handoff shares, then the
runbook, then this page. Nothing else first.

---

## Part 1 — qm

### Before the first command

- **The charge.** It is not on this page and cannot be. Ask the owner for it in
  the session and carry the answer verbatim into the audit and skeptic briefs.
- **The dev extra.** `qm test`, `qm posture` and `qm mutate` need pytest, which
  is in the `dev` extra: bare `uv run qm test` exits 1 with `No module named
  pytest`. Every `uv run` below that runs tests carries `--extra dev`.
- **The adapter.** With Claude Code, `adapters/claude-code/skills/design-review/`
  drives the runbook; it is not linked here, so link it per
  `adapters/claude-code/README.md`.
- **The four facts.** At the stamp, `uv run qm slot --repo quaternionmedia/qm
  --per-base 'project/*'` showed the `main` slot free and one draft, #121 into
  `project/apothecary`, holding that base's slot for another session. Leave it
  alone. `uv run qm gates` lists the gates and what each cannot see.
- **Parallel sessions only on the owner's word in the session**, with the audit
  block and each count stated before its launch, as the runbook's *Before you
  start* says. Without that word, one session runs the phases in sequence.
- **Branches.** The review on `evolve/design-review-<date>`, cut from `main`; its
  retrospective on `perspective/<date>-design-review`. Anything belonging to one
  project's records goes on a branch based on that `project/<name>`, never into
  the review's pull request.

### The objective, a draft to sharpen

Every rule the corpus states is either refused by a named mechanism on the host,
in CI or in preflight, with a test seen failing, or is labelled unenforced;
everything else in the repository shortens an adopter's path to a correct first
commit, or leaves.

### Phase 0, as measured at the stamp

| Measure | Command | At `d6dc5cd` |
|---|---|---|
| The suite, with CI's arguments | `uv run --extra dev qm test` | 1508 passed, 17 skipped; 34 s in parallel, 56 s serial |
| The structural pass over the records | `uv run qm review` | 30 findings, 12 of them universals to read by hand and 7 dangling citations |
| Generated documents | `uv run qm docs check` | exit 1: `status/documents.yaml` has drifted |
| Leaks | `uv run qm leaks` | clean |
| Test yield, each minutes long: run in the background | `uv run --extra dev qm posture`, `uv run --extra dev qm mutate` | last baseline `.qm-posture.json`, 2026-08-21; no workflow runs either |
| The command surface | `uv run qm --help` | 48 subcommands |
| Weight | `git ls-files ci records` | `ci/` modules 21,535 lines, `ci/tests` 15,494, twelve `*-registry.yaml` plus three other `ci/*.yaml`; 39 records |
| The entry path | follow `handbook/forking-a-project.md` into a scratch repository and run its gates; for each rule in `AGENTS.md`, a branch that violates it | not run: which gate exits non-zero for which rule |
| CI | `gh run list --repo quaternionmedia/qm --limit 50 --json name,conclusion,createdAt,updatedAt` | not read |

Runtime is not this corpus's problem. What is in question is yield (does each
check discriminate) and weight (what `ci/` is for). Measure yield with the
corpus's own instrument, `handbook/test-posture.md`, rather than a new one.

### The areas

The runbook's general areas fold in here: test runtime becomes yield under
area 3, docs fall under areas 5 and 10, hygiene and dead weight under area 4.

| Area | First questions |
|---|---|
| 1 Record coherence, read mechanically | Which pairs bind the same thing: the-read-document-governs and governance-arrives-as-a-mechanism; nothing-is-both-a-claim-and-its-own-evidence and a-check-is-evidence-only-after-it-has-failed; the loose-end, delta, knot and granularity cluster? Which records are process notes rather than decisions, by the charter's own test? Do `qm review`'s candidates hold? Could the set shrink without losing a decision? |
| 2 Ceremony against enforcement | For each rule in `AGENTS.md` and the records, what stops a violation today: the host, CI, preflight, or nothing? What would applying `A-main.json` break? Can a tag pass `tag-determinism` with this suite? Which gates would a small team keep if each had to earn its place? |
| 3 Tooling correctness | Does each `ci/gate-registry.yaml` entry's `gates:` and `refuses:` match its workflow's `on:` and its code? Do path filters exclude what a job executes? What do mutation yields say today for the direction guard and the record lint? Which tests assert on the real corpus, and which only on fixtures? |
| 4 Tooling scope and weight | Which modules serve a record's enforcement, which one workstation, which a demo? Which subcommands does a workflow, a runbook or nobody run (`ci/tool-registry.yaml`)? Which registries have a consumer? What could move to a repository of its own, and does the seed's run-in-place contract allow it? |
| 5 Routing sprawl | Which handoffs describe landed work? Which plans are live? Which handbook pages narrate history the style guide sends to perspectives? Are the two glossaries two sources of truth? |
| 6 Generated documents | Which are read by a gate, a person, or nobody? Which are past their budget? Why did one drift on `main` unnoticed? Should generated state be committed at all? |
| 7 Seed drift and propagation | How far behind is each project branch, and is every pin reachable (`uv run qm pins --root <adopter clone>` per adopter, or `status/governance.yaml` after `uv run qm docs generate`; run in qm itself it finds no submodules)? Which seed workflows does each adopter carry? Does the forking procedure list what the seed holds? Is one propagation pull request per project per change sustainable? |
| 8 Branch and pull request hygiene | Is the five-namespace list the rule or a fiction? Which remote branches are merged, stranded or parked (`uv run qm branches`)? Do the host's merge settings match `handbook/merge-review.md`? |
| 9 Self-application | Does the corpus obey its own records on integers, conversation, drafts in place, attribution and protocol budgets? |
| 10 The reader's path | What is the least an agent reads before a correct first commit, here and in an adopter? How many places restate one rule? Does `project-seed/ide/AGENTS.md` carry the current contract to adopters? |

### Leads, as hypotheses

Each was measured at the stamp and is a hypothesis until re-run. Where an
ordinary explanation could produce the same output, it is named: rule it out
first (`AGENTS.md` item 11).

**Area 2.**
- *Nothing on the host enforces a rule.* `gh api
  repos/quaternionmedia/qm/branches/main/protection` answered 404, "Branch not
  protected"; `uv run qm rulesets` showed six drafted and none applied; every
  owner line in `.github/CODEOWNERS` starts `#=`. Applying a ruleset is a
  person's act ([`apply-the-main-ruleset.md`](apply-the-main-ruleset.md)): the
  review recommends and never applies.
- *Neither human gate has been exercised.* `git ls-remote --tags origin` printed
  nothing; `status/documents.yaml` shows none Accepted.
- *`tag-determinism` would refuse this corpus's own suite on a runner.* All 17
  skips are `ci/tests/test_trio_demo.py`, which needs sibling clones; that
  output fed to `python project-seed/ci/check_tag_claims.py --test-output`
  printed `FAIL <test run> - 17 skipped -- §3` and exited 1. Rule out a runner
  that has the clones.
- *Record pull requests into `project/*` run a reduced, older gate set.* `git
  ls-tree origin/project/apothecary .github/workflows/` listed 7 workflows
  against `main`'s 15; #121 ran 5, with no leak check, signatures or
  registries; `leak-check.yml` triggers on `main` only. Rule out a record that
  intends project branches to carry fewer gates.

**Area 3.**
- *`ci-tooling-tests` does not run on changes to the pages it executes.* Its
  `paths:` filter is `ci/**`, `project-seed/ci/**` and its own file; its steps
  run `walkthrough/` and `docs/cookbook/` as doctests.
- *A generated document drifted on `main` and nothing noticed.* `uv run qm docs
  check` printed `FAIL document states status/documents.yaml` and exited 1; the
  missing row is the perspective #120 added (regenerated by the pull request
  that queued this page). No workflow runs `qm docs check`,
  and it skips harness and families for want of a check mode.
- *`qm review` resolves paths two ways, and reports a false positive.* It says
  the Enforcement clause of `records/DRAFT-what-is-not-the-organisation.md`
  names a missing `leak-check.yml`; `.github/workflows/leak-check.yml` and
  `project-seed/ci/leak-check.yml` both exist. `ci/record_review.py` checks
  Enforcement with `(root / p).exists()` and citations with an `rglob` fallback.
- *`docs-audit` claims to refuse unreachable pages and has no code for it.* Its
  registry entry says it refuses "a page the navigation does not reach"; `grep
  -in 'reach\|orphan\|nav' ci/docs_audit.py` found nothing; `docs/ref/addresses.md`
  is in no nav entry, and `python ci/docs_audit.py` exited 0. Rule out the site
  build step warning about it, which was not tested.
- *The gate registry can disagree with a trigger and still render ok.*
  `namespace-guard` declares `gates: [main, push]`; its workflow triggers on
  `project/**` only. Direction is still refused on every pull request by
  `one-pr-check.yml`, so this is a claim defect, not a hole.
- *The guards that matter most have the weakest measured yield, and nothing
  re-measures.* `.qm-posture.json` gives `check_pr_base.py` 32.7% and
  `adr_lint.py` 63.6%; no workflow mentions `mutate` or `posture`;
  `handbook/gates.md` says three of adr-lint's four sub-checks cannot fire on
  any ref CI runs against.

**Area 4.**
- *The tooling outgrew the doctrine.* Non-merge numstat on `main` since
  2026-08-01: `ci/` +41,354 lines, `records/` +7,117. The disk, devloop,
  workspace, trio-demo, harness and dashboard modules come to about 7,100
  lines; `ci/disk_reclaim.py` deletes one machine's caches; `ci/trio_demo.py`
  ties the corpus to three product repositories. `pyproject.toml` calls this "a
  corpus of prose, not a Python project".
- *`uv run qm estate` cannot answer the question it is named for.* It reads
  clones beside the corpus, and without them it reported every rostered
  repository missing.

**Area 5.**
- *The handoff queue breaks its own delete-on-land rule.* Rows say *built*,
  *done*, *landed as #114 and #115*, *closed and left standing on purpose*; the
  footer is stamped 2026-08-14 while rows cite 2026-09-20; 18 of the 23 pages
  were last touched on or before 2026-08-31 (`git log -1 --format=%cs --
  <page>`); `governance-loop-poc.md` names a branch gone from the remote.
- *Two glossaries*, `handbook/glossary.md` and `docs/ref/glossary.md`, and
  `docs_audit` reports no duplicates.
- *`plans/`* holds several self-declared stubs in the one home the style guide
  leaves unplaced; `perspectives/README.md` marks every row Unreviewed.

**Area 6.**
- *Committed status documents outlive their own budgets.* `status/harness.yaml`
  was generated 2026-09-20 against a 24-hour budget; the 168-hour ones
  (governance, gates, rollout, inventory) run out during 2026-09-27.
  `status/inventory.yaml` is JSON. `loose-ends.json` shows nothing claimed.

**Area 7.**
- *The seed drifted from its procedure and its adopters.* `project-seed/ci/`
  holds 7 workflows; `handbook/forking-a-project.md` step 4 names "all four"
  plus the leak check, never `signature-check.yml` or `tag-claims.yml`, and
  narrates its own history. apothecary carries 3 of the 7, and its `adr-lint`
  and `submodule-check` differ from the seed's. `git rev-list --left-right
  --count origin/main...origin/project/apothecary` printed `324 13`.

**Area 8.**
- *The namespace rule is not the practice.* `README.md` calls a branch outside
  the five namespaces "a mistake"; the heads in `gh pr list --state all --limit 200
  --json headRefName` include
  `fix/`, `adr/` (every project-record pull request), `handoff/`, `seed/` and
  `docs/`.
- *Host settings contradict the runbook.* `gh api repos/quaternionmedia/qm`
  shows `delete_branch_on_merge=false` and `allow_squash_merge=true`;
  `handbook/merge-review.md` says never squash. Merged branches stay on the
  remote (`adr/codecartographer-index-current`, merged as #116), and three
  `evolve/` and `perspective/` branches have no pull request.
- *`8229a40` may be a direct push to `main`.* `git rev-list --first-parent
  --no-merges --since=2026-08-12 origin/main` lists it, and its only associated
  pull request is #105, into `project/dossier`. Rule out a fast-forward merge
  whose association was lost: read the repository's event history before
  saying so.

**Area 9.**
- "Eleven principles" at `README.md:44`, `docs/about/overview.md:27` and
  `docs/about/index.md:5`; `uv run qm edges` counts 17.
- Figures in `ci/run_tests.py`'s docstring, `pyproject.toml` and
  `.qm-posture.json` are stale against the Phase 0 table; `AGENTS.md` calls
  `qm --help` "the whole surface" and names seven commands.
- `README.md` says every record is Proposed; some are Draft.
- The handoffs README says both "merge it yourself once the gates are green" and
  that none of these pages authorise "Merging to `main`"; `AGENTS.md` item 3
  says the first.
- `perspectives/session-transcript-2026-06-09.md` is a conversation, which
  `records/DRAFT-what-is-not-the-organisation.md` puts outside the
  organisation; several perspective filenames carry a model's name, which the
  same record allows only in a `Tools:` note.
- `uv run qm protocols`: the security review is past its budget; history-archive
  and curriculum have never run.

**Area 10.**
- `AGENTS.md` calls itself short at 2,702 words, and calls `README.md` plus
  `PRINCIPLES.md`, about 6,000 words, short. The pull request model is
  restated in `AGENTS.md`, the handoffs README, `handbook/async-contract.md`
  and twice in `README.md`. apothecary's `AGENTS.md` is an older, shorter copy
  of `project-seed/ide/AGENTS.md`.

### What the corpus already has, and how the review uses it

- **The semantic review of the records**
  ([`semantic-review-of-the-records.md`](semantic-review-of-the-records.md),
  [`semantic-review-session.md`](semantic-review-session.md),
  `plans/semantic-review-instrument.md`) has never run, and is scoped to fifteen
  or sixteen records where there are now 39. Do not do its reading. Check
  whether its scope, order and schema still fit, re-scope it in place to the
  current set, and name it in the triage as a follow-on a person does. Flag a
  record contradiction only where it is mechanical, such as `README.md` against
  the Status rows.
- **`uv run qm review`**: candidates, not verdicts. Check the tool as well as
  consume it.
- **`protocols/`**: cite the runs, recommend which protocols survive, re-run one
  only when an area needs it.
- **`plans/first-ratification.md`, `plans/v0.0.1-review-packet.md`,
  `plans/v0.0.1-blockers.md`**: inputs to area 2.
- **Decisions waiting on a person** ([`hil-review-2026-08-25.md`](hil-review-2026-08-25.md),
  [`apply-the-main-ruleset.md`](apply-the-main-ruleset.md)): say which are still
  live; start no parallel list.
- **`qm posture` and `qm mutate`**: re-run them rather than invent a yield
  measure.
- **The retrospectives**: several are narrow reviews already
  (`2026-08-21-a-green-suite-and-eight-holes.md`,
  `2026-08-23-the-rules-with-nothing-behind-them.md`,
  `2026-08-25-defects-between-two-green-suites.md`). Mine them for what
  recurs; do not re-derive them.

### What "cut" means here

Deleting handoffs whose work landed, moving any method they hold to a runbook;
deleting plans nobody executes, the second glossary, and tooling nothing
consumes; proposing that workstation and demo tooling move to a repository of
their own. A record is merged or retired only in a pull request that argues for
it, as a draft rewritten in place; ratification stays a person's. A change to
`project-seed/` reaches adopters only by propagation, one pull request per
project, never inside this one.

For phase 3, a finding that merges, retires or moves a record, a handbook page
or a seed file counts as `delete` and goes to a skeptic, whose caller search
includes every `project/*` branch and adopter pin.

### Before the pull request

- `uv run --extra dev qm test`, and `uv run --extra preflight qm preflight` in
  the background, saying of each failure whether it is the environment or a
  defect, and how you know.
- `uv run qm leaks` and `uv run qm private-names --source host --strict`.
  Without the private roster it exits 1 *unverified*; record that as
  unverified, not as a failure.
- When generated inputs change, `uv run qm docs generate` then `uv run qm docs
  check`. `main` carried a drift at the stamp (area 3); the pull request that
  added this page regenerated it, so the lead is why nothing noticed, not a
  drift still to fix.
- Push the review branch, never `main`. Then `uv run qm branch --base main
  --head <branch>`, which reads origin and refuses an unpushed branch, pasted
  into the body.
- Merge commits only. The body speaks as the contributor, in the third person,
  states decisions, and requests no review; the owner is the assignee. The
  owner's questions are asked in the session.
- Records: drafts rewritten in place, none of the words `AGENTS.md` item 9
  bans, the drafting contract in `project-seed/adr/README.md`; a restatement
  names its record and the record names it back.
- Few integers in durable text; the verification section is the exception.
  Every why goes to the retrospective. No local path, session identifier,
  address, workstation detail or conversation in a committed file.
- Commits: the owner is the author, no co-author trailer, no tool as author,
  the body ends with a `Tools:` line, and every one is signed:
  `git log --format='%G? %h %s' origin/main..<branch>`, where `N` stops the
  branch (`handbook/consolidation-runbook.md` Step 3).

### Done looks like

- One pull request from `evolve/design-review-<date>` whose body follows the
  runbook's shape, with the verification section run on its tip, left open
  with the owner as assignee. It retires governed pages, so the handoffs
  README's no-merge rule holds here over `AGENTS.md` item 3's merge-yourself;
  area 9 settles which should hold in general.
- The Phase 0 table re-run on the tip, before and after, in the body's place of
  *Faster*: yields from `qm posture` for the guards, `ci/` lines, the
  mandatory-reading lines in `status/documents.yaml`, and the `AGENTS.md` rules
  a seeded violation is refused for.
- The owner's questions answered in the session, and recorded in the body as
  decisions.
- Every handoff whose work landed deleted, and the queue refilled
  (`handbook/consolidation-runbook.md` Step 7).
- The semantic review re-scoped to the current records and queued as a person's
  work.
- A retrospective in `perspectives/`.
- This part deleted from this page. Part 2 stays until the estate is done.

## Part 2 — the other repositories

### The ordering rule

Two measurements sort repositories into tiers; within a tier, upstream goes
first. **Adopts** means a `governance/qm` submodule in `.gitmodules` on the
host, not a roster claim. **Active** means a human commit on any branch within
30 days, `dependabot/` branches excluded, dated by commit and never by push
time.

| Tier | Who | Depth |
|---|---|---|
| 0 | qm | full |
| 1 | adopted and active | full. A contract publisher or document producer goes before whatever implements, renders or pins it; ties by rostered consumers, then by commits in 90 days |
| 2 | adopted but not active, or half-adopted | full or reduced. A half-adoption is settled first |
| 3 | not adopted, active | full. Consumers first; repositories sharing a seam and a lens run as one batch |
| 4 | not adopted, quiet for one to twelve months | triage only: keep, archive or adopt, for the owner |
| 5 | nothing human for over a year and no dependant, or no repository | none. The owner writes an attention claim into `ci/workspace.yaml` |

Each run starts from the tip of that repository's in-flight work. apothecary is
the reference run and is not queued again. `ci/rollout.yaml` orders by family,
which puts cold repositories ahead of live ones and the most-implemented
contract last; this order follows consumers and activity instead.

### Re-deriving it

`uv run qm estate` needs clones beside the corpus. From the host instead:

```sh
uv run qm inventory       # attention claimed, and recency of the default branch
uv run qm interop         # who implements which contract
gh api repos/quaternionmedia/<name>/contents/.gitmodules -H "Accept: application/vnd.github.raw"
gh api graphql -f query='{repository(owner:"quaternionmedia",name:"<name>"){refs(refPrefix:"refs/heads/",first:100){nodes{name target{... on Commit{committedDate}}}}}}'
gh search code "quaternionmedia/<name>" --owner quaternionmedia   # consumers; default branches only
```

`qm inventory` reads only the default branch, so a repository whose work lives
on a branch reads cold there; the query per repository is what finds it.
`status/governance.yaml`, after `uv run qm docs generate`, gives each adopted
project's seed workflows and how far its branch is behind.

### The order at the stamp

Private repositories appear by reference only, from the 2026-09-20 inventory.
Open one only on a machine holding the private roster, and never write its
name.

| Order | Repository | Tier | Fitting the lenses |
|---|---|---|---|
| 1 | rad | 1 | The contract codecartographer and dossier implement and rad-godot ports: the vectors as the contract; versioning, since it claims none (`uv run qm interop`); conformance across implementations; whether its deterministic gate is deterministic in practice; the single-file reference; its Pages deploy, red on `main`; diary files at the root; image weight |
| 2 | qmcp | 1 | Producer of the topology documents and the harness archive: the tool surface, schemas and errors; the topology contract, absent from the interop registry; the human approval path, voice included; tests that reach into sibling repositories; the lock against the dependabot queue. Start from `main` plus #38 |
| 3 | dossier | 1 | Renders both upstreams: widget architecture, with a refactor branch in flight; rendering against rad's and qmcp's documents; test runtime; plans shipped as docs; font and SVG licensing; a governance submodule URL that needs a key |
| 4 | codecartographer | 1 | The second renderer, under dossier's lens: the vendored rad core against the vectors; the API boundary and frontend; frontend tests; docs weight and handoffs; whether its private submodule leaves outsiders unable to build |
| 5 | looksatwords | 1 | Consumes qmcp's archive: the API surface; tests CI does not gate; fixtures built from conversation data; vendored or built JS; image weight |
| 6 | datum | 1 | Pins apothecary: review the `wp3-firmware` tip once apothecary #21 and #22 merge; envelope versioning and its schema gate; the MQTT harness; firmware failure modes; docs as tests; diary files at the root |
| 7 | private-33 | 1 | App lenses, plus the seed pieces it lacks |
| 8 | carlos | 2 | Heaviest churn after the core, all older than the 30-day window, and nobody on it: whether the device catalogue matches the real gear; frontend; `vendor/` licensing; the image and release gate; diary files; a non-standard default branch |
| 9 | qmetronome | 2 | Android: clock accuracy, audio scheduling against the UI thread, measured drift; lifecycle and background audio; USB-MIDI; release signing across two workflows; instrumented against JVM tests; committed GIFs and binaries |
| 10 | private-36 | 2 | Settle adoption first: seed files, no submodule |
| 11 | private-34 | 2 | Reduced scope |
| 12 | factorio-sysops | 2 | Triage depth: docs outweigh code, no tests |
| 13 | ShowRunner, with Cuelist-python and ShowStopper | 3 | After its #30 lands: the plugin contract; a device dropping mid-cue, the counterpart of apothecary's printer link; cue timing; migrations; UI tests; the dependabot queue; Cuelist-python's sibling-path dependency and committed database |
| 14 | rad-godot, golfvs, private-38 | 3 | One Godot lens: loop and physics determinism; rad's vectors replayed in CI, where rad-godot has none; provenance of committed native binaries; autoload singletons; gdUnit4 value against runtime; export per platform; asset licensing |
| 15 | joe | 3 | Decide first whether it is a sketch or a product; then personal data from the microphone, beside qmcp's voice work |
| 16 | leo | 3 | Frontend; collaboration and sync; licensing of committed fonts, charts and a PDF; no tests |
| 17 | moat | 3 | Start from `plans/moat-remediation.md`, not a fresh audit: secrets and state, least privilege, declared against running, the failing chart publish |

**Tier 4, triage only:** benchmark (settle the roster's claim that it is a
current consumer), waveofhormuz, TheatreMix-python and QLab-python (with
ShowRunner's outcome), ludwig, private-32 (adopt, or drop its project role),
uPhonor with holophonor (one lineage decision), scad-chess (or fold it into
apothecary as a part set).

**Tier 5, an attention claim and no review:** alfred, midiphonor, stomp, wolf,
aes, ztgui, ira, cesar, private-03, private-05, private-07, private-23,
private-26, and streaming-infrastructure, which has no repository on the host.

**Unplaced:** otto, janus, al-admin, karaoke-kiosk and obsidian-templates are
public and were pushed within 30 days, but are not rostered. A person rosters
them before this order can place them.

### In each project

- The project's own `AGENTS.md` and conventions govern the run; this corpus
  reaches it through its pin.
- A defect two projects could share is fixed in `project-seed/`, and the
  project's copy follows by propagation (`handbook/adoption-audit-queue.md`).
- A governance decision the review raises is drafted as a record on a branch
  based on that project's `project/<name>` in this corpus.
- When a review lands, update its row here. When the order is exhausted, delete
  this page.

## What is not yours

Ratifying anything. Applying a ruleset. Cutting a tag. Merging to `main` or to a
`project/*` branch without the owner's word in the session. Deleting a branch.
Force-pushing. Rewriting a branch a submodule pins. Writing a private
repository's name.
