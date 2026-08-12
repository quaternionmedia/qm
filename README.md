# Quaternion Media Constitution

This repository holds the decisions that govern every Quaternion Media project: the principles, the process that keeps projects consistent, and the template each new project starts from. Projects adopt this corpus **by reference**. A project may tighten these rules, but never relax them.

**Full documentation:** [docs/](docs/index.md) — also rendered at
[quaternionmedia.github.io/qm](https://quaternionmedia.github.io/qm/) once Pages is enabled.

## Read this first

1. **Only `records/` binds.** Records are the only binding documents here. Everything else points at them. `perspectives/` is opinion and binds nothing.
2. **Every record is `Proposed`.** None is ratified yet, and that is deliberate: ratification requires approval from a second active code owner.
3. **Every change arrives as a pull request** — from a typo fix to a new record. Nobody merges their own work into `main`.

## Start here

| You want to | Go to |
|---|---|
| Know what QM believes and why | [PRINCIPLES.md](PRINCIPLES.md) — the charter, eleven principles |
| Understand how the corpus works | [Overview](docs/about/overview.md) and [Architecture](docs/about/architecture.md) |
| Set up a new QM project | [Forking a new project](docs/usage/first-project.md) |
| Learn the branch and record rules | [Branch namespaces](docs/ref/namespaces.md) and [Record precedence](docs/ref/precedence.md) |
| See where every project stands | [governance-status.yaml](governance-status.yaml); [handbook/generated-documents.md](handbook/generated-documents.md) explains how to read it |
| Work here as a coding agent | [AGENTS.md](AGENTS.md) — read it before your first commit; start with `/cowork` |

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

Every record is `Proposed` because ratification requires a second active code owner. GitHub does not count a PR author's own approval, so a gate one person can satisfy alone would not be a real gate. See [handbook/governance-rollout.md](handbook/governance-rollout.md) for what is enforced today and what waits.

## Contributing

Work on a branch in one of the five namespaces — [Branch namespaces](docs/ref/namespaces.md) lists them, and a branch outside them is a mistake rather than a variation. Open a draft pull request (`gh pr create --draft`) and assign the person who asked for the work. A human reviews and merges. See [Branch namespaces](https://quaternionmedia.github.io/qm/ref/namespaces/) and [handbook/async-contract.md](handbook/async-contract.md).

## Licence

Corpus prose is CC-BY-SA-4.0. See [LICENSE](LICENSE), [LICENSES/](LICENSES/), and [REUSE.toml](REUSE.toml) for full details.
