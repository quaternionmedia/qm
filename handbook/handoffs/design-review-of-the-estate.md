# Handoff — A design review of qm, then of the estate

**Each part carries its own stamp.** Part 1 is stamped 2026-10-31 at `qm`
`main` `debf210`; Part 2 is stamped 2026-09-26 at `d6dc5cd`, the merge of
#120, with its estate figures read from the host that day. The method's
first run is apothecary #22: `review/2026-09-26` at `276d8b8` on origin,
cut from `1835b47`. Every figure below is true at its part's stamp and
nowhere else, and each names the command that re-derives it.

This corpus is reviewed first by the method apothecary #22 ran, then the
estate in the order below. The method is
[`handbook/design-review-runbook.md`](../design-review-runbook.md). This page
fits it to a governance corpus, hands over what was measured here as leads to
test, and orders the other repositories.

Read [`README.md`](README.md) for the rules every handoff shares, then the
runbook, then this page. Nothing else first.

---

## Part 1 — qm

**Stamped 2026-10-31.** `qm` `main` at `debf210`, the merge of #302. Phases 0,
1 and 3 of the runbook ran against that commit, read-only, scoped to a
stranger's first hour: whether someone with no context can adopt the corpus
from `main` alone and reach a working loop, and which gaps stop them first,
with outside testers arriving soon as the measure. The review states leads and
decides nothing: nothing is fixed, cut or merged by it. Phases 4 to 7 remain,
and the last section says what picks them up. Every figure below names the
command that re-derives it and is true at `debf210`; re-run before acting.
`perspectives/2026-10-31-the-strangers-first-hour.md` is the retrospective.

### Before the first command

- **The scope.** Ask the owner for it in the session and carry the answer
  verbatim into the audit and skeptic briefs, which are working files. The
  scope above is what the first run used; a later run asks again.
- **The dev extra.** `qm test`, `qm posture` and `qm mutate` need pytest, which
  is in the `dev` extra: bare `uv run qm test` exits 1 with `No module named
  pytest` and prints no remedy. Every `uv run` below that runs tests carries
  `--extra dev`.
- **The path, on Windows.** The site generator's extra fails to import at a
  deep checkout path (`ImportError: DLL load failed ... The filename or
  extension is too long`), and `git submodule add` with Git for Windows 2.37
  fails from a deep project path with `fatal: '$GIT_DIR' too big`. Measure from
  a short path, or the measurement describes the path.
- **Adapters.** `adapters/README.md` lists any that drive the runbook for one
  tool. None is required, and the runbook wins over each.
- **The four facts.** At the stamp, `uv run qm stacks --repo quaternionmedia/qm`
  lists the open pull requests, every one into a `project/*` branch; nothing is
  open into `main`. `uv run qm gates` lists the gates and what each cannot
  see.
- **Parallel sessions only on the owner's word in the session**, with the
  audit block and each count stated before its launch, as the runbook's
  *Before you start* says. The first run's audit block is in the retrospective.
- **Branches.** The review on `evolve/design-review-<date>`, cut from `main`;
  its retrospective on `perspective/<date>-<slug>`. Anything belonging to one
  project's records goes on a branch based on that `project/<name>`, never into
  the review's pull request.

### The objective, a draft to sharpen

Every rule the corpus states is either refused by a named mechanism on the host,
in CI or in preflight, with a test seen failing, or is labelled unenforced;
everything else in the repository shortens an adopter's path to a correct first
commit, or leaves. Read against a stranger's first hour, the second half is the
one that bites: a page that presupposes a sibling clone, a credential, a
person or a push right lengthens that path for everyone the corpus is about to
meet.

### Phase 0, as measured at the stamp

| Measure | Command | At `debf210` |
|---|---|---|
| The suite, with CI's arguments | `uv run --extra dev qm test` | exit 1 on one test, `ci/tests/test_trio_demo.py::test_the_deployed_front_ends_agree`: its skip condition reads whether two ports answer rather than whether the sibling clones exist, so where other services answer those ports and no clone sits beside the checkout it runs and fails. Where nothing answers those ports it skips. Everything else passes; the skips are in the same file. The tree is clean afterwards |
| The preflight | `uv run --extra preflight qm preflight` | three steps of thirty-eight fail: the tooling tests, on that one test, and the two site builds, on the Windows path-length limit above; from a shorter path `zensical build --clean`, `ci/cookbook.py docs/families --site --check` and `ci/docs_audit.py` all exit 0 |
| Generated documents | `uv run qm docs check` | exit 1: `status/documents.yaml` lacks the row for the perspective #302 adds. No workflow runs this check |
| The standing queue | `uv run qm queue` | exit 1: three pull requests in other repositories merged since the page's stamp of 2026-10-24 |
| The structural pass over the records | `uv run qm review` | runs; its two findings naming `leak-check.yml` as absent are false, since `.github/workflows/leak-check.yml` and `project-seed/ci/leak-check.yml` both exist |
| Leaks | `uv run qm leaks` | clean |
| Timeless text | `uv run qm timeless --all --summary` | clean |
| The host's barriers | `gh api repos/quaternionmedia/qm/branches/main/protection`; `uv run qm rulesets`; `git ls-remote --tags origin` | `main` unprotected (404); none of the six drafted rulesets applied; no tags |
| The host's merge settings | `gh api repos/quaternionmedia/qm --jq '{allow_squash_merge,allow_rebase_merge,allow_merge_commit,delete_branch_on_merge}'` | all three merge methods allowed; branches deleted on merge |
| Sibling clones | `uv run qm estate` | every rostered repository `MISSING`, the corpus itself included, exit 0 |
| Test yield | `uv run --extra dev qm posture` | not measured: the baseline is red on the trio-demo test, so posture refuses to measure, which is the right refusal and leaves the guards' yield unknown at this commit |
| The command surface | `uv run qm --help` | 55 subcommands in one flat list |
| The entry path | `handbook/forking-a-project.md`, followed step by step into a scratch project | stops at step 2 for anyone without write access to this repository; the leads under *The fork* |
| CI | `gh run list --repo quaternionmedia/qm --limit 60 --json name,conclusion,createdAt,updatedAt` | every push gate on `main` in the window succeeded; one pull-request run cancelled by concurrency |

### The areas, as run

The runbook's ten areas for a governance corpus fold into four for this
scope, each read by one reader against a detached checkout nothing else
touched:

| Area as run | Folds in | Not covered, and why |
|---|---|---|
| The reader's path | areas 10, 5 and the contradictions of 9 | — |
| The adoption path, run | area 7, and the entry path of Phase 0 | the propagation half of 7: an adopter's lag needs the adopter |
| The working loop and its gates | areas 2, 3, 4 and 8 | yield (3): posture has no green baseline at this commit; the full classification of the command surface |
| The standing state at open | areas 6 and 5, and the attribution lead of 9 | — |
| — | area 1, record coherence | a stranger's hour does not reach the records' meaning; the semantic review is its home |
| — | the rest of 9 | integers, drafts in place and protocol budgets are a maintainer's reading, not a stranger's |

### Leads, as hypotheses, in the order a stranger meets them

Each is measured at `debf210` and is a hypothesis until re-run. Where an
ordinary explanation produces the same output, it is named: rule it out first
(`AGENTS.md` item 11). The two leads that cut something went through phase 3;
the section after this one has the verdicts, and the refuted one is not listed
here.

**At open: the reading.**

- *The first-change recipe assumes write access and a named requester, and
  no page gives an outsider's path.* `README.md` *Contributing*, `AGENTS.md`
  item 3 and `docs/usage/getting-started.md` step 5 say to assign the person
  who asked and merge it yourself; there is no `CONTRIBUTING` file, and no
  first-hour page says fork, who is assigned when nobody asked, who merges, or
  what the gates do on a fork. This is the gap that closes the loop for an
  outside tester. `ls CONTRIBUTING*`; `grep -rln -i "outside contributor\|without
  write access" README.md AGENTS.md docs/usage handbook/async-contract.md`
  prints nothing.
- *The mandatory reading is over its own budget, and the sources disagree
  about it.* `status/documents.yaml` `reading_load` totals the four documents
  it measures at seven lines over the budget of
  `records/DRAFT-governance-arrives-as-a-mechanism.md` §4, with
  `within_budget: false`; `handbook/handoffs/qm-queue.md` §1 item 6 says the
  load is below it; `AGENTS.md` calls itself short on purpose at close to
  three thousand words. The set `AGENTS.md` sends a reader to before a first
  edit (itself, the charter, the README, the queue and the async contract) is
  over an hour at a reading pace, and with the status documents it names in
  the same breath, close to three; the measured set omits the README and the
  queue. Rule out drift in the generated document, which `qm docs check`
  reports at this commit; the sentence in the queue is contradicted either
  way. `grep -n -A14 reading_load status/documents.yaml`; `cat AGENTS.md
  PRINCIPLES.md README.md handbook/handoffs/qm-queue.md
  handbook/async-contract.md | wc -w`.
- *Two neutral pages name one adapter's slash commands as the way to open and
  close a session.* `README.md`'s Start-here row says *start with `/cowork`*,
  and `handbook/async-contract.md` §6 opens with `/cowork` and closes with
  `/handoff`; the tool-neutral route (`uv run qm brief`,
  `project-seed/ci/cowork_context.py`) is named only in that page's table.
  `grep -n "/cowork\|/handoff" README.md handbook/async-contract.md`.
- *The standing queue is red at open, is mostly about other repositories, and
  names people and private references.* `uv run qm queue` exits 1 on a clean
  `main`; §2 and §3 name pull requests into `project/*` branches a stranger
  cannot act on, §4 is the largest section, and the page names a maintainer
  by first name, `private-NN` references and `ci/workspace-private.yaml`,
  which the stranger does not have. The stranger-relevant part is *How this
  page is kept* and a few of the decisions in force, of which `AGENTS.md`
  restates one (item 19). `awk '/^## /{print NR": "$0}'
  handbook/handoffs/qm-queue.md`.
- *The handoffs index carries two stamps that disagree.* `handbook/handoffs/README.md`
  reads *Re-read on 2026-10-25* above its table and *Stamped 2026-08-14* in
  its footer, with paragraphs describing the harness as newly landed and two
  rows naming people as the blocker. `grep -n "Re-read on\|^\*Stamped"
  handbook/handoffs/README.md`.
- *The status documents a stranger is told to read instead of re-deriving are
  host snapshots they cannot refresh.* `status/harness.yaml` carries a 24-hour
  budget and is the longest file in the reading; a refresh needs a host
  login; a workflow reads only `status/governance.yaml` and
  `status/inventory.yaml`. `grep -rln "status/harness.yaml"
  .github/workflows` prints nothing.
- *On Windows without symlinks, `CLAUDE.md` is a nine-byte pointer, and the
  remedy is the last section of `AGENTS.md`.* The pointer files are mode
  `120000` in the index (`git ls-files -s CLAUDE.md
  .github/copilot-instructions.md`); a checkout without `core.symlinks`
  writes the target's name, and a tool that reads only that file gets a
  filename. Rule out a Git for Windows installed with symlink support, where
  nothing differs. Not run at this commit; derived from git's semantics.
- *The drafting contract `AGENTS.md` item 7 mandates is a seed file addressed
  to a project.* `project-seed/adr/README.md` opens as a seed to copy and
  speaks of the project's decision memory and `ADR-XXXX`; the org drafter's
  template is the root `TEMPLATE.md`, which no first-hour page names. `grep
  -rn "TEMPLATE.md" --include=*.md . | grep -v "adr/TEMPLATE\|project-seed"`.
- *`AGENTS.md` numbers two lists from 1, and "the whole surface" names seven
  commands of fifty-five.* The four facts and the twenty items both start at
  1, so *item 3* has two referents; the sentence on `uv run qm --help` names
  stacks, branch, gates, tags, docs, preflight and brief. `grep -c '^    [a-z]'`
  over the help output; `grep -n "^[0-9]\+\. " AGENTS.md`.

**The four facts.**

- *Two of the four opening commands need a host credential and do not say
  so.* With none, `uv run qm stacks --repo quaternionmedia/qm` prints `gh
  auth login` and exits 1, and `uv run qm queue` exits 2 with *the host does
  not know qm 8a6002b, the page's stamp*, which reads as a fault in the page.
  `env GH_TOKEN= GH_CONFIG_DIR=/nonexistent uv run qm queue`.
- *`uv run qm estate` reports the stranger's own clone `MISSING` and exits
  0.* Its search root is two directories above the module and its roster
  paths assume a layout; a checkout under any other name finds nothing,
  fifty rows long. Rule out the checkout's directory name: a clone at
  `<root>/qm/qm` is the layout `ci/workspace.yaml` names.
- *Bare `uv run qm test` fails on a missing module and prints no remedy.* No
  first-hour page names `--extra dev`; `AGENTS.md` names `--extra preflight`
  twice. `grep -rn "extra dev" AGENTS.md README.md handbook/async-contract.md`
  prints nothing.
- *On a Windows console the corpus's dashes print as replacement
  characters.* `uv run qm gates | head -1` prints the title with a replacement
  character where the dash is; with `PYTHONIOENCODING=utf-8` it prints the
  dash. The console code page, not the data; cosmetic.

**The first gates.**

- *`qm docs check` is red at `main`'s tip, no workflow runs it, and the
  regeneration step is in a page the stranger is not sent to.* The three
  index documents (`status/documents.yaml`, `handbook/document-states.md`,
  `loose-ends.json`) change in most pull requests, so every landing
  re-conflicts every other; the instruction lives in
  `handbook/generated-documents.md` and `handbook/consolidation-runbook.md`,
  not in `AGENTS.md`. `grep -n "docs generate\|docs check" AGENTS.md` prints
  nothing; `grep -ln "docs check\|generate_docs" .github/workflows/*` prints
  nothing.
- *Path filters leave tests unrun for files they cover.*
  `ci-tooling-tests.yml` filters on `ci/**` and `project-seed/ci/**` while
  running pytest over `walkthrough/` and doctests over `docs/usage/`;
  `docs-audit.yml` runs on `pull_request` alone with a `docs/**` filter, so a
  stale generated page is the next contributor's red and not `main`'s. Read
  the `on:` blocks.
- *The trio-demo test's skip condition reads two ports, not the sibling
  clones it needs.* A machine with those services up and no clones gets a red
  suite and a red posture baseline. `ci/tests/test_trio_demo.py`, the
  `skipif` above `test_the_deployed_front_ends_agree`.
- *`qm review` resolves a bare workflow name against the repository root.*
  `ci/record_review.py` tests `(root / p).exists()`, so an Enforcement clause
  naming `leak-check.yml` reports it absent while both copies exist.
- *The gate registry overstates two gates.* `docs-audit`'s entry promises to
  refuse a page the navigation does not reach, and `grep -in
  'reach\|orphan\|nav' ci/docs_audit.py` prints nothing; `namespace-guard`
  declares `gates: [main, push]` while its workflow triggers on `project/**`
  only, and the preflight prints `SKIP namespace-guard.yml` on `main`.
  Direction into `main` is still refused by `one-pr-check.yml`, so this is a
  claim defect.
- *The gates page says nothing blocks a merge, and the stranger reads "merge
  it yourself" first.* `handbook/gates.md` is reached from `qm gates` or a
  link; `AGENTS.md` item 3 is read before it. `uv run qm gates --check
  handbook/gates.md` exits 0.

**The fork.**

- *Step 2 of `handbook/forking-a-project.md` pushes a `project/<name>` branch
  to this repository, and neither it nor `docs/usage/first-project.md` says
  that needs write access or a maintainer.* Every later step rests on the
  push: step 3's pin, step 4's submodule check, step 6's records. A stranger
  stops here, and the pages do not say so before step 0. `grep -n -i "write
  access\|permission\|maintainer" handbook/forking-a-project.md
  docs/usage/first-project.md` prints nothing.
- *Step 2's verify line refuses an unpushed branch for a reason other than
  the guard, and reads as a pass.* `uv run qm branch --base main --head
  project/<name>` before the push prints *exists locally but not on origin*,
  exit 1; the page says a refusal proves the guard. Run it after the push,
  and quote the guard's own message.
- *Step 2 says copy `adr/` verbatim, and the verbatim copy keeps `<name>`,
  which the seed's `adr-lint.yml` does not refuse.* `check_placeholders.py`
  runs in this repository's `.github/workflows/adr-lint.yml` and not in
  `project-seed/ci/adr-lint.yml`. `grep -n check_placeholders
  project-seed/ci/adr-lint.yml` prints nothing.
- *Step 4's local runner needs pyyaml, a signed-in `gh` and an `origin`, and
  the page names none of them.* On a project with none, four of nine steps
  fail, and `check_one_pr.py` without `gh` on the path ends in a raw
  `FileNotFoundError`. `python governance/qm/project-seed/ci/run_workflows_locally.py`
  from a fresh project.
- *Step 5's `cp -a` on Windows lands the two pointer files as regular files,
  and the remedy that works is a paragraph deep.* `git ls-files -s CLAUDE.md
  .github/copilot-instructions.md` reads `100644` after the copy; the
  `git update-index --cacheinfo 120000,<sha>,<path>` route on the same page
  yields the seed's blobs. `AGENTS.md`'s one-time setup acts on a fresh clone,
  not on an index already holding regular files.
- *Step 6's lint refuses fewer forms than the banned list the pages give,
  and a draft needs an index row the step does not mention.* `adr_lint.py`
  matches *previously* and *originally* only in narrating constructions, by
  design; a stranger who breaks it with a bare *previously* sees green and
  concludes the lint is dead. A draft with no row under *Drafts in flight* in
  `adr/README.md` is refused, and step 6 does not say to add one.
- *Step 4's workflow set disagrees with the seed directory and with
  `docs/usage/next-steps.md`.* The handbook names four plus the leak check;
  `project-seed/ci/` holds eight, three of whose headers say *copy
  verbatim*; next-steps says four. `ls project-seed/ci/*.yml`.
- *The seed's `AGENTS.md` omits rules the root page carries, one of which a
  seed gate enforces.* Items 4, 5, 14, 16 and 18 of the root page have no
  counterpart in `project-seed/ide/AGENTS.md`, while `project-seed/ci/timeless-check.yml`
  ships; the seed's item 6 has no counterpart in the root. Diff the item
  lists by rule.
- *On Windows, step 1 fails from a deep project path with an opaque git
  error.* `git submodule add` under Git for Windows 2.37 prints `fatal:
  '$GIT_DIR' too big`; from a short path the same command succeeds. Rule out
  the git version first.

**The first pull request.**

- *Every pull request runs the signature gate, and no first-hour page says
  how to sign.* `signature-check.yml` triggers on every `pull_request`;
  `grep -in "sign" AGENTS.md README.md` prints nothing about signing; the one
  page that mentions it, `docs/usage/questions-a-new-developer-asks.md`,
  gives no steps and is linked from neither. Rule out host-side signing of a
  web-editor commit, which is not tested.
- *The voice check refuses an ordinary polite body.* `check_pr_voice.py` on
  *Please let me know if you want changes* exits 1 on the second person; the
  rule is stated in `AGENTS.md` item 3 in terms of what a session says, and
  there is no pull request template.
- *"Merge it yourself once every gate is green" assumes write access, and no
  page says what an outsider does.* The same gap as the first lead under *At
  open*, met again at the end: `main` is unprotected, so write access is the
  only barrier, and `grep -n -i "write access\|collaborator" AGENTS.md
  README.md handbook/async-contract.md` prints nothing.
- *"A branch outside the namespaces is a mistake" is enforced by nothing, and
  most heads on origin are outside them.* `docs/ref/namespaces.md` lists six
  namespaces; `git ls-remote --heads origin` shows `adr/*`, `demo/*` and
  `fix/*` heads beside them, the `adr/*` ones carrying every project-record
  pull request; `project-seed/ci/check_pr_base.py` refuses three directions
  and no unknown prefix. Rule out a page that documents `adr/<slug>` under
  another phrasing. `git ls-remote --heads origin | sed 's#.*refs/heads/##' |
  grep -vc '^\(project\|propagate\|perspective\|evolve\|workspace\|math\)/\|^main$'`.
- *Nine perspective filenames carry a model's name.* The index names the
  human author and carries the `Tools:` note the attribution rule asks for;
  the filename reads as a byline. `ls perspectives | grep -i
  "claude\|gpt\|gemini\|sonnet\|opus\|fable"`.

**After the hour.**

- *The page after adoption assumes someone with rights.*
  `docs/usage/next-steps.md` says *someone cuts a `propagate/<name>-<date>`
  branch* and *the org audits adopted projects*; every pointer on it exists,
  and none says how an outside project is rostered, who ratifies, or what the
  first working cycle is.
- *No protocol is on the first-hour path, and two have never run.* `uv run qm
  protocols`: the security review is past its budget; history-archive and
  curriculum have never run. Nothing before the alpha depends on them.

### The skeptic pass

Two findings cut something, and each went to a skeptic whose brief was to
refute it.

- *Eight subcommands have no caller* — **refuted.** `config`, `lanes`,
  `ledger`, `policies` and `restatements` run in
  `.github/workflows/registries.yml` and `adr-lint.yml`, or are named in
  `ci/gate-registry.yaml` and `ci/devloop.py`; `patterns`, `session` and
  `tags` are wired in `ci/cli.py` and named in `ci/pattern-registry.yaml` and
  an adapter command. The audit's scan matched the literal `uv run qm <sub>`
  and nothing else. What survives is the recommendation that was never a
  deletion: a help screen grouped into the loop's commands and the rest.
- *Split the standing queue and move three decisions into `AGENTS.md`* —
  **upheld, trimmed.** `ci/queue_page.py` reads the stamp and the pull
  request numbers from the whole text, and no workflow, gate or test reads the
  page, so a split breaks no parser; it does edit every page that cites the
  queue by section (`grep -rl "qm-queue" --include=*.md --include=*.py
  --include=*.yaml .`), and section numbers cited from perspectives stay where
  they are. Decision 7 is already `AGENTS.md` item 19 and does not move;
  decision 6 belongs to `records/DRAFT-governance-arrives-as-a-mechanism.md`
  §4, which `ci/doc_status.py` enforces, and restating it in `AGENTS.md`
  raises the load it limits; decision 1 restates no record. The cheapest
  change for the stranger needs no split: make the page's *exits 0* close
  rule true, or remove it from the page and from
  `handbook/consolidation-runbook.md`. The triage counts this as an edit
  across the citing pages, not a deletion.

### What the corpus already has, and how the review uses it

- **The semantic review of the records**
  ([`semantic-review-of-the-records.md`](semantic-review-of-the-records.md),
  `plans/semantic-review-instrument.md`) has not run, and is scoped to a
  smaller set than `records/` now holds (`git ls-files records | grep -c
  DRAFT-`). Do not do its reading. Re-scope it in place to the current set, and
  name it in the triage as a follow-on a person does.
- **`uv run qm review`**: candidates, not verdicts, and it carries the false
  positive above.
- **`protocols/`**: cite the runs; re-run one only when an area needs it.
- **`plans/first-ratification.md`, `plans/v0.0.1-review-packet.md`,
  `plans/v0.0.1-blockers.md`**: inputs to the enforcement area.
- **Decisions waiting on a person** (`handbook/handoffs/qm-queue.md` §3): say
  which are still live; start no parallel list.
- **`qm posture` and `qm mutate`**: re-run them rather than invent a yield
  measure, once the trio-demo test's skip condition reads the clones.
- **The retrospectives** `2026-08-21-a-green-suite-and-eight-holes.md`,
  `2026-08-23-the-rules-with-nothing-behind-them.md` and
  `2026-08-25-defects-between-two-green-suites.md` each describe a check
  that reports success while enforcing nothing; the path-filter, registry and
  `qm review` leads above are the same shape.

### What "cut" means here

Deleting handoffs whose work landed, moving any method they hold to a runbook;
deleting plans nobody executes and tooling nothing consumes; proposing that
workstation and demo tooling move to a repository of their own. A record is
merged or retired only in a pull request that argues for it, as a draft
rewritten in place; ratification stays a person's. A change to
`project-seed/` reaches adopters only by propagation, one pull request per
project, never inside this one.

For phase 3, a finding that merges, retires or moves a record, a handbook page
or a seed file counts as `delete` and goes to a skeptic, whose caller search
includes every `project/*` branch and adopter pin. A deletion under
`project-seed/` cannot stand from a machine that cannot search the private
adopters.

### Before the pull request

- `uv run --extra dev qm test`, and `uv run --extra preflight qm preflight` in
  the background, saying of each failure whether it is the environment or a
  defect, and how you know. From a deep path on Windows, two site-build steps
  fail on the path; the trio-demo test fails wherever the two ports answer and
  no clone sits beside the checkout.
- `uv run qm leaks` and `uv run qm private-names --source host --strict`.
  Without the private roster it exits 1 *unverified*; record that as
  unverified, not as a failure.
- When a page is added, `python ci/doc_status.py --write status/documents.yaml`,
  `python ci/doc_dashboard.py status/documents.yaml --out handbook/document-states.md`
  and `python ci/loose_ends.py --write loose-ends.json`, then `uv run qm docs
  check`.
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
- Commits: the owner is the author; one line saying what is now true, with
  nothing after it; no co-author trailer and no tool named; and every one
  signed: `git log --format='%G? %h %s' origin/main..<branch>`, where `N` stops
  the branch (`handbook/consolidation-runbook.md` Step 3).

### What remains, and done looks like

Phases 4 to 7 have not run. The next session takes the leads above as the
upheld set, with the skeptic verdicts applied, and:

- runs the triage (phase 4) into file-disjoint workstreams, with the fork
  pages, the opening commands and the first-hour pages as the *now* set;
- asks the owner, in the session, the decisions the leads cannot settle: who
  pushes a `project/<name>` branch for an outside project, or whether a fork of
  this repository is a supported route; whether an outside tester merges, or
  is assigned to someone who does; whether the reading budget's measured set
  gains `README.md` and the queue; whether the three index documents stay
  committed;
- executes the workstreams (phase 5) in lanes, one pull request from
  `evolve/design-review-<date>`, with the Phase 0 table re-run on the tip
  before and after;
- deletes every handoff whose work has landed and refills the queue
  (`handbook/consolidation-runbook.md` Step 7);
- re-scopes the semantic review to the current records and queues it as a
  person's work;
- then deletes this part from this page. Part 2 stays until the estate is done.

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
