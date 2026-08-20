# Quaternion Media Constitution

## In plain terms

Every team keeps answering the same questions. How does work get reviewed? When
is something finished? What does a new project start from? Usually those
answers live in people's heads, and they drift.

This is where Quaternion Media writes them down instead. Every QM project
follows what is written here. A project can be stricter than these rules. It
can never be looser.

A few things will carry you a long way:

- **Decisions live in `records/`.** Nothing else here is binding. Everything
  else explains a record, points at one, or checks that we are keeping to it.
- **Nothing is marked final yet.** Every record says `Proposed`, on purpose.
  Making one final needs a second person to agree, and there is not a second
  person yet.
- **All work arrives as a pull request**, from a typo to a new rule. It is the
  paper trail, not a request for someone's attention. You merge your own once
  the automated checks pass.
- **Two moments need a person, and the pull request is not one of them.** Making
  a record final, and putting a version tag on a project. A tag means somebody
  read the change, ran it against the real thing, and watched the checks pass.
  Reaching `main` claims none of that.

If a page here says one thing and a record says another, the record is what we
decided and the page is wrong. Say so, and fix the page.

**One warning about the words.** A few everyday words are used here in a narrow
sense, and some of them mean more than one thing: *record*, *draft*, *gate*,
*review*, *phase*, *delta*. When a sentence stops making sense, that is usually
why. [handbook/glossary.md](handbook/glossary.md) sorts them out, and it is the
shortest useful thing to read after this.

**Full documentation:** [docs/](docs/index.md) — also rendered at
[quaternionmedia.github.io/qm](https://quaternionmedia.github.io/qm/) once Pages is enabled.

## Start here

| You want to | Go to |
|---|---|
| Know what QM believes and why | [PRINCIPLES.md](PRINCIPLES.md) — the charter, eleven principles |
| Understand how the corpus works | [Overview](docs/about/overview.md) and [Architecture](docs/about/architecture.md) |
| Read a specific decision | the index at the end of this file; each row links to its record |
| Work here as a coding agent | [AGENTS.md](AGENTS.md) — read it before your first commit; start with `/cowork` |
| Run any of it | `uv run qm --help` — one entry point for every governance operation here |
| Run several agent sessions at once | [handbook/async-contract.md](handbook/async-contract.md) — one PR per repo per contributor, and why |
| Set up a new QM project | [Forking a new project](docs/usage/first-project.md) |
| Bring an existing project up to date | [handbook/propagation-runbook.md](handbook/propagation-runbook.md) |
| Learn the branch and record rules | [Branch namespaces](docs/ref/namespaces.md) and [Record precedence](docs/ref/precedence.md) |
| Know how far this corpus has got in governing itself | [handbook/governance-rollout.md](handbook/governance-rollout.md) |
| See where every project stands | [governance-status.yaml](governance-status.yaml); [handbook/generated-documents.md](handbook/generated-documents.md) explains how to read it |
| Know which checks actually govern, and what each one misses | [handbook/gates.md](handbook/gates.md) — says plainly whether anything blocks a merge |
| Know what state a document is in before trusting it | [handbook/document-states.md](handbook/document-states.md), or `uv run qm docs states --state proposed` |
| Look up a word this corpus uses in its own way | [handbook/glossary.md](handbook/glossary.md) |

The same four points again, in the corpus's own words, with the reasoning the
plain version leaves out:

1. **Records in `records/` are the only binding documents.** Everything else
   points at them. `perspectives/` is opinion and binds nothing.
2. **Every record is `Proposed`.** None is ratified, and that is deliberate —
   ratification waits on a second active code owner, because a gate one person
   can satisfy alone is a gate in name only.
3. **Every change arrives as a pull request**, from a typo to a new record. The
   pull request is an audit record, not a request for attention: its author
   merges it once every gate is green.
4. **There are exactly two human gates**, ratification and the version tag, and
   the pull request is neither — `records/DRAFT-version-tags-are-claims.md` §4.
   `main` is not a claim, so merging into it is not a release.

## Layout

```
qm/
├── PRINCIPLES.md          the charter: what QM believes, and why
├── records/               the org records; the only binding documents
├── registers/             live org-level registers
├── handbook/              policy, status, and procedures
├── perspectives/          attributed, dated, non-binding opinion
├── project-seed/          what a new project copies
├── ci/                    org-level tooling
├── adapters/              optional per-tool glue; nothing here is depended on
├── docs/                  the documentation site (GitHub Pages)
├── governance-status.yaml generated; where every project stands
├── harness-status.json    generated; PR slots, phases, governance evidence
├── AGENTS.md              instructions for coding agents
├── .github/               CI workflows and branch protection
└── LICENSE, LICENSES/     CC-BY-SA-4.0 for corpus prose; REUSE.toml covers the rest
```

## Index — org records

| # | Title | Status | Date |
|---|---|---|---|
| — | [Decision-record discipline](records/DRAFT-decision-record-discipline.md) | Proposed | 2026-06-09 |
| — | [Open-license exclusion and upstream-contribution remediation](records/DRAFT-open-license-exclusion-and-upstream-remediation.md) | Proposed | 2026-06-09 |
| — | [A disagreement is a delta](records/DRAFT-a-disagreement-is-a-delta.md) | Proposed | 2026-08-17 |
| — | [Few integers in durable text](records/DRAFT-few-integers-in-durable-text.md) | Proposed | 2026-08-18 |
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
| — | [The read document governs](records/DRAFT-the-read-document-governs.md) | Proposed | 2026-08-14 |
| — | [Governance arrives as a mechanism](records/DRAFT-governance-arrives-as-a-mechanism.md) | Proposed | 2026-08-14 |
| — | [The ledger](records/DRAFT-the-ledger.md) | Proposed | 2026-08-15 |
| — | [Attention is a claim, activity is measured](records/DRAFT-attention-is-a-claim-activity-is-measured.md) | Proposed | 2026-08-19 |
| — | [CLIs are for machines and for debugging](records/DRAFT-clis-are-for-machines-and-debugging.md) | Proposed | 2026-08-20 |
| — | [Deltas compose, and a tangle is a fact](records/DRAFT-deltas-compose.md) | Proposed | 2026-08-20 |
| — | [Acts that are a person's by constitution](records/DRAFT-acts-that-are-a-persons-by-constitution.md) | Proposed | 2026-08-20 |
| — | [Whether something is a delta is a perspective](records/DRAFT-granularity-is-a-perspective.md) | Proposed | 2026-08-20 |
| — | [Nothing unattended spends money](records/DRAFT-no-unattended-spending.md) | Proposed | 2026-08-20 |

Every record is `Proposed` because ratification requires a second active code owner. GitHub does not count a PR author's own approval, so a gate one person can satisfy alone would not be a real gate. See [handbook/governance-rollout.md](handbook/governance-rollout.md) for what is enforced today and what waits.

## Contributing

Work on a branch in one of the five namespaces — [Branch namespaces](docs/ref/namespaces.md) lists them, and a branch outside them is a mistake rather than a variation. Open a pull request, assign the person who asked for the work, request no reviewer, and merge it yourself once every gate is green. See [handbook/async-contract.md](handbook/async-contract.md).

| Page | What it answers |
|---|---|
| `handbook/forking-a-project.md` | Standing up a new project, with the check that proves each step worked |
| `handbook/governance-rollout.md` | How far this corpus has got in governing itself, and what ratification waits on |
| `handbook/propagation-runbook.md` | How an org change reaches an adopted project, in both repositories |
| `handbook/adoption-audit-queue.md` | Which projects are audited, and how the next agent runs the rest |
| `handbook/public-by-default.md` | When work may be closed, and the path to promoting that to a record |
| `handbook/style-guide.md` | Which tier a sentence belongs in: inline, README, `docs/`, or a retrospective |
| `handbook/async-contract.md` | The rules that exist only because several agent sessions run at once |
| `handbook/generated-documents.md` | The committed status documents, how stale each may be, and how a dashboard is built |
| `handbook/gates.md` | **Generated.** Every automated check, what it refuses, what it cannot see, and whether any of it blocks a merge |
| `handbook/glossary.md` | Words this corpus uses narrowly, and the ones it uses in more than one sense |
| `handbook/handoffs/` | Work an asynchronous agent can pick up cold, and the order between the pieces |

## Licence

Corpus prose is CC-BY-SA-4.0. See [LICENSE](LICENSE), [LICENSES/](LICENSES/), and [REUSE.toml](REUSE.toml) for full details.
