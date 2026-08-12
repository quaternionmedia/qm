# The governance status seam — what exists, and what a human must settle

**What this is.** `ci/governance_status.py` emits `governance-status.yaml`, a
document describing the state of governance across the org.
`ci/governance_render.py` turns that document into one self-contained HTML page.
CI verifies the document against the commits it names. Nothing else in this
corpus decides what governance means.

**Read `handbook/handoffs/README.md` first.** The build is done; what remains
here is the seam contract, so a module can be lifted out and replaced without
anyone re-deriving a rule, and the questions the build surfaced that only a
human can answer.

---

## The seam, and what each side may not do

```
   git + gh  ──►  ci/governance_status.py  ──►  governance-status.yaml  ──►  a reader
                  the only thing that            the contract              render_html,
                  knows what a rule means                                  dossier, a job
```

| Module | May | May not |
|---|---|---|
| `governance_status.py` | run `git` and `gh`, read-only | write to any repository, call a mutating `gh` subcommand, invent a rule the corpus does not define |
| the document | carry facts and stamps | carry a verdict, a threshold, or a severity |
| a reader | sort, colour, roll up, join | run git, re-derive a governance fact, write back |

**A reader that needs a fact the document lacks changes the generator**, in one
place, reviewed once, and every reader gets it. A convenience computation in a
renderer is a second definition of a governance rule, which is what the
document exists to prevent.

## Two layers, and why only one is checkable

`git` is a pure function of the commits the document names: same commits, same
answer, forever. `github` is observation — someone opens a pull request and
yesterday's answer is wrong through nobody's fault.

So `--check` re-derives **only** the git layer, against the commits the
document already names, with no network and no credential. Its claim is *"this
document faithfully renders the commits it names"* and never *"the world has
not moved"*. That is why it works in a fork pull request, and why it does not
go red every time `main` advances.

The comparable key set is derived from what `git_layer()` actually emits, not
from a pattern over field names. An earlier draft used a regex, which meant a
renamed field would silently drop out of the only gate — the check would keep
passing while checking less. `test_no_git_layer_key_is_treated_as_an_observation`
pins it.

## `{unknown: <reason>}` is a value of every type

Any field, at any depth, may arrive as the single-key mapping
`{unknown: "<why>"}` instead of its declared type. `behind_corpus` is an int or
that mapping. `open_prs` is a list or that mapping.

**A reader must type-check every field.** An int column cannot hold a mapping,
and a reader that coerces it gets a blank — and blank reads as fine, which is
the exact failure the whole arrangement is written against. For a relational
reader, a nullable value column beside an `unknown_reason` column keeps the
distinction alive across the mapping.

`null` is not `unknown`. `last_propagation: null` means *never propagated*,
which is a fact the generator established.

## The red paths, as built

Every signal has a test in which it reports bad, and — more importantly — each
of those tests has been run against the defect it names. `ci/tests/` currently
holds 51 tests for the generator and 16 for the renderer. Ten mutations were
applied to the tool one at a time and every one was caught by the test that
describes it. **A test that passes against the broken tool is inert, and this
repository has shipped two of those.** Repeat the mutation exercise before
trusting any new signal.

| Signal | Reports bad when |
|---|---|
| `behind_corpus` | the branch is genuinely behind |
| `last_propagation` | never merged the corpus; a feature merge does not count; the corpus's own merges do not count |
| `adr_template_vs_merge_base` | the copy was edited after it was taken |
| `readme_seed_comment_left_in` | the fork's step 2 was never finished |
| records | counted from the ref, never from the working tree |
| project refs absent | `projects` is unknown, never an empty list |
| github unreachable | unknown with the reason, never `false` and never `[]` |
| `--check` | a doctored field, a commit not in the clone, a document naming no corpus commit |
| the renderer | absent document, unknown distinct from value, drift distinct in form |

### The four bugs that reached a running tool, all caught by running it

Kept because each is a shape, not an incident. `ls-tree` without `-r` reported
a directory of ten records as empty. Walking every reachable merge counted the
corpus's own thirteen merges as thirteen propagations. `gh api` without
`--paginate` returned the first hundred of a hundred and nine repositories and
declared three existing projects nonexistent. And a `--jq` expression asking for
`.licenseInfo.spdxId` — a key that endpoint does not have — reported every
repository in the org as unlicensed, in a tidy table.

None of them crashed. All four produced a clean, confident, wrong answer.

## Questions for a human

None of these can be settled by an agent, and none of them blocks the tool: each
one is a field the document deliberately does not emit, or a choice it records
rather than makes. The document's own `undefined:` block carries the first five
so a reader meets them there rather than here.

**1. Is `adopted` a governance predicate at all?** The corpus states only the
negative — *"Being pinned is not being adopted, and nothing reports the
difference"* — and `DRAFT-decision-record-discipline.md` §6 explicitly refuses a
compliant/non-compliant axis. Today the document emits the artifacts each
repository carries and derives no boolean.
*Options:* facts only, forever · a record defining the predicate · adopt the
corpus's existing two-state language, *instantiated vs improvised*.

**2. What ref is seed drift measured against?** Against the corpus tip all nine
branches drift and the signal restates `behind_corpus`. Against each branch's
merge-base, two drift — codecartographer and streaming-infrastructure — and the
signal means *the copy was edited*. Both are emitted; neither is called the
answer.

**3. May the document attach a state name to `behind_corpus`?** Currently a
number with no threshold. `handbook/propagation-runbook.md` names *"a dispute
about whether a project is current"* as precisely what would force its own
promotion to a record — so colouring a cell red at N commits creates the teeth
without the record.

**4. Are `propagate/*` and `fix/*` legitimate namespaces?** The runbook
instructs creating them, eight exist on origin, and `README.md` says a branch
outside its four namespaces *"is a mistake rather than a variation"*. Ruleset E
excludes only the four. No namespace-conformance signal can exist until this is
resolved.

**5. There is no map from `project/<name>` to a repository.** The runbook says
so outright. The generator assumes `<org>/<name>`, records that assumption in
the document, and reports unknown — never unadopted — when the repository
cannot be read. `project/streaming-infrastructure` has no repository at all,
which may be a monitoring gap or a finding.

**6. Do project records count in the corpus census?** They are counted per
project, and the corpus block covers `records/` on `main` only. Worth knowing:
`README.md` says there is no worked example of a ratified record, and
`project/streaming-infrastructure` carries an Accepted ADR-0001.

**7. Should CI have a credential that can read private repositories?** Three
governed projects are private. An Actions `GITHUB_TOKEN` is scoped to this
repository, so a CI-run generation would report a third of the fleet as missing
everything — an authentication artifact that reads like the worst-adopted
projects in the org. Today nothing in CI generates, only `--check`, which needs
no credential; the document is generated by a human whose `gh` login can see
them. *Options:* leave it human-run · an org-read PAT · a GitHub App token
scoped to the nine.

**8. Is adoption-gap detail about private repositories publishable?** The
committed document names three private projects and lists what each is missing.
That is a map of where governance is weakest, in a public repository. Private
repositories *outside* the governed set are counted and not named, by default —
`--name-private-repositories` turns that off and the document records which way
it ran.

**9. Who refreshes the document, and how often?** Nothing does today: it is a
dated snapshot, refreshed when a human runs `--write` and opens a PR. A bot
pushing to `main` would need an explicit carve-out from `AGENTS.md`'s
never-push-`main` rule, which is a decision about what the human gate is for.

**10. A committed generated artifact contradicts one of our own sanity
checks.** `perspectives/2026-08-08-reading-the-proxy-instead-of-the-thing.md`
says *"Refuse to commit what a gate generated"* — and this session untracked
`licenses.json` on exactly that reasoning. The document is committed by
deliberate instruction, and it is a different animal (a reviewed artifact, not
a gate by-product), but the tension is real and is named here rather than
resolved quietly.

**11. Everything on `main` propagates.** The document will ride into all nine
`project/*` branches and into every project's vendored `governance/qm`. Since
nothing regenerates it automatically, that is one occasionally-changed file
rather than continuous churn — but every project vendors a permanently stale
org-wide status file it cannot refresh.

## Running it

```sh
python ci/governance_status.py --write governance-status.yaml   # needs gh
python ci/governance_status.py --check governance-status.yaml   # offline
python ci/governance_render.py governance-status.yaml --out status.html
python -m pytest project-seed/ci/tests ci/tests -q
python project-seed/ci/run_workflows_locally.py
```

Run both test directories in one command. Each passes alone and they collided
on the module name `conftest` when first run together — which is what the local
workflow runner exists to surface before CI does.

## What is not yours here

Answering any of the eleven questions. Emitting a field for a term the corpus
does not define. Adding a threshold, a severity, or a colour rule to the
document. Teaching the renderer to run git.
