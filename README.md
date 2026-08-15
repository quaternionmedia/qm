# Quaternion Media Constitution

The org-level decision corpus: the philosophies that govern every QM project,
the process that keeps them coherent, and the proven template each new
project forks from. Projects adopt this corpus **by reference** and may
tighten its rules — never relax them.

## Start here

| You want to | Go to |
|---|---|
| Know what QM believes and why | `PRINCIPLES.md` — the charter, eleven principles, short |
| Read a specific decision | the index at the end of this file; each row links to its record |
| Work in this repo as a coding agent | `AGENTS.md` — read it before your first commit; start with `/cowork` |
| Run several agent sessions at once | `handbook/async-contract.md` — one PR per repo per contributor, and why |
| Stand up a new QM project | `handbook/forking-a-project.md` |
| Bring an existing project up to date | `handbook/propagation-runbook.md` |
| Know how far this corpus has got in governing itself | `handbook/governance-rollout.md` |
| See where every project actually stands right now | `governance-status.yaml`, and `ci/governance_render.py` to read it as a page |
| Read the status documents as an agent | `handbook/generated-documents.md` — paths, staleness budgets, and the `--format md` views |

Three things are worth knowing before anything else:

1. **Records in `records/` are the only binding documents.** Everything else
   points at them. `perspectives/` is opinion and binds nothing.
2. **Every record is `Proposed`.** None is ratified, and that is deliberate —
   ratification waits on a second active code owner, because a gate one person
   can satisfy alone is a gate in name only.
3. **Every change arrives as a pull request**, from a typo to a new record.
   Nobody merges their own work into `main`.

## Layout

```
qm/
├── PRINCIPLES.md     the charter — what QM believes, and why
├── records/          the org records; the only binding documents here
├── registers/        live org-level registers (carried patches)
├── handbook/         policy, status and procedures routed out of record form
├── perspectives/     attributed, dated, non-binding opinion
├── project-seed/     what a new project copies: adr/, ci/, ide/
├── ci/               org-level tooling, copied nowhere: the status generators
├── governance-status.yaml   generated; where every project stands, and when
├── harness-status.json      generated; PR slots, phases claimed, governance evidence
├── AGENTS.md         governance discovery for coding agents
├── adapters/         optional per-tool glue; the constitution depends on none of it
├── LICENSE           CC-BY-SA-4.0 corpus prose; LICENSES/ + REUSE.toml cover the rest
└── .github/          this corpus's own CI, CODEOWNERS, and branch-protection config
```

`CLAUDE.md` and `.github/copilot-instructions.md` are symlinks to `AGENTS.md`,
so any tool reading either gets its current bytes.

Each adopting project's own `adr/` directory — its decision records, as
opposed to the org's — lives on a dedicated branch of *this* repo
(`project/<name>`), not copied into the project's own git history. The
project vendors this repo as a submodule and checks out its own branch; see
"Forking a new project" below.

## Branch namespaces

`main` carries the constitution and nothing else. Six namespaces hang off it,
and a branch outside them is a mistake rather than a variation.

| Namespace | Holds | Lifetime |
|---|---|---|
| `project/<name>` | one adopting project's `adr/` | permanent — a downstream submodule pins its tip |
| `propagate/<target>-<date>` | `main` merged toward one `project/<name>` or `workspace/<slug>`; `<target>` is that project's name or that workspace's slug, which therefore may not collide | deleted after merge |
| `perspective/<date>-<slug>` | one perspective, staged for `main` | deleted after merge |
| `evolve/<slug>` | org-level work in progress | deleted after merge |
| `workspace/<slug>` | a research workspace that never merges back **to `main`** | permanent, terminal |
| `math/<slug>` | one exploration against a research workspace | deleted after merge into that workspace |

`propagate/*` was mandated by the propagation runbook and by the table below
while this list said there were four namespaces and that anything outside them
was a mistake — with eight such branches pushed. It is listed because the rule
that a branch outside these namespaces is wrong is only usable if the list is
complete.

`project/qmetronome` is the reference instance for a non-server runtime. **There
is no reference instance for a server/container runtime.**
`project/streaming-infrastructure` used to be named here as one and is not: no
`quaternionmedia/streaming-infrastructure` repository exists — `gh api` returns
404, and the generated document records that as its `repository` value — so
there is nothing it is an instance *of*. It is a design branch holding the plan
and `ADR-0001` that `main` moved off itself in `dec5c9c`, and it is tens of
commits behind — `governance-status.yaml` carries the current `behind_corpus`
figure, and this sentence deliberately does not, having already been wrong once
by naming one. Naming it as the reference invited a forker to copy the setup of a
project that was never set up.

The mathematical-limits experiments live on `workspace/math-experiments` —
non-binding, and reached from the perspective whose open questions they
investigate. A workspace is terminal in one direction only: nothing goes from
it to `main`, and `main` reaches it as a `propagate/*` pull request like any
project branch. Explorations against it run in parallel on `math/<slug>`
branches, several at a time by design, and do not consume the one-open-pull-
request slot. `handbook/research-workspaces.md` is the standard.

**A `project/<name>` branch is never merged into `main`.** Not once, not
squashed, not "just the shared part". It exists in perpetuity and holds exactly
one thing: how one project's governance deviates from `main`. Merging it would
move that project's `adr/` onto `main`, and `main` is the org namespace — so
one project's local decision would become an org record by accident, and the
precedence rule below would then read backwards, with the project's own record
appearing to bind every other project. Nothing in the tree would look wrong
afterwards; the records would simply be in the wrong namespace, and the next
project to adopt would inherit them.

So a `project/<name>` branch takes changes **in**, never gives them out:

| Direction | How |
|---|---|
| project-specific records arrive | a pull request whose **base** is `project/<name>`. Each such base holds its own slot under the one-PR rule, which is what the `--per-base 'project/*'` exemption is for |
| the branch is created | cut from `main`, `adr/` copied from `project-seed/adr/`, and **pushed** — see "Forking a new project" step 2. The initial content is not a pull request, because the only base it could target is a branch that does not exist yet |
| `main`'s changes reach it | `main` is merged **into** it, as a `propagate/<name>-<date>` pull request against it. Never a rebase: a downstream submodule pins the tip, and rebasing invalidates every pin |
| the project's own repository sees it | the submodule pointer, bumped by that same propagation |

A `project/<name>` branch is therefore never the *head* of a pull request,
whatever the base is and whatever it carries.
`project-seed/ci/check_pr_base.py` refuses that, and separately refuses any
branch carrying a top-level `adr/` at `main` — because the first check reads a
name, and a branch called anything at all can carry those files.

## Record namespaces and precedence

- **Org records:** `QM-NNNN`, numbered at ratification by this README's index.
- **Project records:** `ADR-NNNN`, numbered locally per project, starting at 0001.
- **Precedence:** QM records bind all projects. A project record may add
  constraints on top of a QM record; it may not waive one. A genuine
  exception is an *amendment to the QM record*, ratified at org level — never
  a project-level workaround.
- **Adoption by reference:** each project's `adr/` directory lives on its own
  branch of this repo, created from `main`. That branch's ancestry is the
  pin — no separate hash to hand-maintain. Org ratifications and amendments
  propagate by merging `main` into the project's branch — a reviewed commit,
  not an ambient change.

The drafting discipline (squash before ratification, append-only after,
numbering at ratification, one decision per record, banned-vocabulary lint)
is identical at both levels and is itself an org record: see
*Decision-record discipline* in `records/`.

**What binds, and what does not.** Only `records/` binds. The rest of this
corpus carries force by pointing at a record, never on its own authority:

| Directory | Force | If it conflicts with a record |
|---|---|---|
| `records/` | binding on every project | it *is* the rule |
| `registers/` | binding, as the record that creates it says | the record wins; the register is its data, not a second rule |
| `handbook/` | policy and status, binding on QM's own conduct | the record wins, and the conflict means the page needs promoting or correcting |
| `perspectives/` | none, by construction | no conflict is possible; a perspective is an opinion |
| `project-seed/` | none in itself | it is a template; the copy is governed where it lands |

A project record may tighten a `handbook/` page the same way it may tighten a
record. It may not relax either. If a handbook page ever needs to settle a
dispute rather than describe a practice, that is the signal to promote it to
a record — each page states its own promotion path.

## Forking a new project

The whole procedure — eight steps, each with the check that proves it worked —
is `handbook/forking-a-project.md`. In outline: add this repo as a submodule at
`governance/qm`, create a `project/<name>` branch here for the project's own
`adr/`, copy `project-seed/` into place, wire the four CI workflows the seed
ships, and seed the first records.

Do not improvise a lighter version. Most projects adopted so far are missing at
least one step — `harness-status.json`'s governance column is the current count,
and `ci/harness_dashboard.py harness-status.json --format md` prints it, so read
it there rather than trusting a number written into this sentence. It said
"three of the nine projects" until the ninth project stopped being the last one;
a count in prose rots silently while the document beside it is regenerated.

The submodule pin is the cheap part, and the copied files are where adoption
actually lives. That is why nothing reported the gaps for as long as it didn't:
the pin was the only thing being checked.

## Ratification

Ratification is a human action at both levels: a commit that flips Status to
Accepted, assigns the number from the index, updates the index, and names the
record in the commit message. Assistants draft; humans ratify.

Ratification is the last human gate, not the only one. **Every change to this
corpus arrives as a pull request**, from a typo fix to a new record, and the
merge is a human's act. Assistants and contributors work on a branch —
`evolve/<slug>`, `perspective/<date>-<slug>`, or the relevant
`project/<name>` — and open a PR; nobody merges their own work into `main`,
and nothing reaches `main` by direct push. The branch protection that makes
this mechanical rather than customary is described in the repository's
rulesets; the rule stands whether or not the tooling is enforcing it on a
given day.

## Index — org records

| # | Title | Status | Date |
|---|---|---|---|
| — | [Decision-record discipline](records/DRAFT-decision-record-discipline.md) | Proposed | 2026-06-09 |
| — | [Open-license exclusion and upstream-contribution remediation](records/DRAFT-open-license-exclusion-and-upstream-remediation.md) | Proposed | 2026-06-09 |
| — | [Seams on standard protocols](records/DRAFT-seams-on-standard-protocols.md) | Proposed | 2026-06-09 |
| — | [Build the seam, buy the engines](records/DRAFT-build-the-seam-buy-the-engines.md) | Proposed | 2026-06-09 |
| — | [House stack](records/DRAFT-house-stack.md) | Proposed | 2026-06-09 |
| — | [Contribution and sponsorship policy](records/DRAFT-contribution-and-sponsorship-policy.md) | Proposed | 2026-06-09 |
| — | [Human-only contributorship](records/DRAFT-human-only-contributorship.md) | Proposed | 2026-07-05 |
| — | [IDE-integrated governance discovery](records/DRAFT-ide-integrated-governance-discovery.md) | Proposed | 2026-07-05 |
| — | [Outbound licensing of QM work](records/DRAFT-outbound-licensing.md) | Proposed | 2026-08-08 |
| — | [Version tags are claims](records/DRAFT-version-tags-are-claims.md) | Proposed | 2026-08-08 |
| — | [The project phase ladder](records/DRAFT-project-phase-ladder.md) | Proposed | 2026-08-09 |
| — | [The monitoring seam, and instance identity](records/DRAFT-monitoring-seam-and-instance-identity.md) | Proposed | 2026-08-11 |
| — | [One executable walkthrough per repository](records/DRAFT-one-executable-walkthrough.md) | Proposed | 2026-08-11 |

**Every record is `Proposed`, and that is a decision rather than a backlog:
ratification waits on a second active code owner.** GitHub does not count a
PR author's own approval, so a ratification gate one person can satisfy alone
is a gate in name only. The mechanisms are not waiting — the discipline is
enforced by CI today. See `handbook/governance-rollout.md` for what is
enforced, what is written but not yet mechanical, and what the wait costs.

Handbook (policy, not records):

| Page | What it answers |
|---|---|
| `handbook/forking-a-project.md` | Standing up a new project, with the check that proves each step worked |
| `handbook/governance-rollout.md` | How far this corpus has got in governing itself, and what ratification waits on |
| `handbook/propagation-runbook.md` | How an org change reaches an adopted project, in both repositories |
| `handbook/adoption-audit-queue.md` | Which projects are audited, and how the next agent runs the rest |
| `handbook/public-by-default.md` | When work may be closed, and the path to promoting that to a record |
| `handbook/style-guide.md` | Which tier a sentence belongs in: inline, README, `docs/`, or a retrospective |
| `handbook/async-contract.md` | The rules that exist only because several agent sessions run at once |
| `handbook/research-workspaces.md` | What a workspace binds, how `main` reaches one, and how explorations run in parallel |
| `handbook/generated-documents.md` | The committed status documents, how stale each may be, and how a dashboard is built |
| `handbook/handoffs/` | Work an asynchronous agent can pick up cold, and the order between the pieces |

### Obligations that fall due at ratification

- **Open-license record → the streaming design branch.** When it is Accepted,
  the `ADR-0001` on `project/streaming-infrastructure` receives a dated
  amendment recording adoption-by-reference. Its body is untouched. Called "the
  reference project" here until "Branch namespaces" above stopped calling it
  one: there is no `quaternionmedia/streaming-infrastructure` repository, so the
  obligation falls on a design branch and on nothing else.

Some records describe machinery that costs nothing to run before ratification.
Where that is true the machinery is live and the record's Status is still
`Proposed`; the two are independent. `handbook/governance-rollout.md` holds the
current inventory, so there is one place to update rather than two that drift.
