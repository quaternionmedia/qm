# Quaternion Media Constitution

The org-level decision corpus: the philosophies that govern every QM project, the process that keeps them coherent, and the proven template each new project forks from. Projects adopt this corpus **by reference** and may tighten its rules — never relax them.

**See the full documentation:** [quaternionmedia.github.io/qm](https://quaternionmedia.github.io/qm/)

## Read this first

Three things are worth knowing before anything else:

1. **Records in `records/` are the only binding documents.** Everything else points at them. `perspectives/` is opinion and binds nothing.
2. **Every record is `Proposed`.** None is ratified, and that is deliberate — ratification waits on a second active code owner, because a gate one person can satisfy alone is a gate in name only.
3. **Every change arrives as a pull request**, from a typo to a new record. Nobody merges their own work into `main`.

## Start here

| You want to | Go to |
|---|---|
| Know what QM believes and why | [PRINCIPLES.md](PRINCIPLES.md) — the charter, eleven principles, short |
| Understand the corpus and how it works | [Overview](https://quaternionmedia.github.io/qm/about/overview.md) and [Architecture](https://quaternionmedia.github.io/qm/about/architecture.md) on the docs site |
| Fork a new QM project | [Forking a new project](https://quaternionmedia.github.io/qm/usage/first-project.md) — eight steps with checks |
| Learn branch and record rules | [Branch namespaces](https://quaternionmedia.github.io/qm/ref/namespaces.md) and [Record precedence](https://quaternionmedia.github.io/qm/ref/precedence.md) |
| See where every project stands | [governance-status.yaml](governance-status.yaml), rendered at [handbook/generated-documents.md](handbook/generated-documents.md) |
| Work here as a coding agent | [AGENTS.md](AGENTS.md) — read it before your first commit; start with `/cowork` |

## Layout

```
qm/
├── PRINCIPLES.md          the charter — what QM believes, and why
├── records/               the org records; the only binding documents
├── registers/             live org-level registers
├── handbook/              policy, status and procedures
├── perspectives/          attributed, dated, non-binding opinion
├── project-seed/          what a new project copies
├── ci/                    org-level tooling
├── docs/                  this documentation site (GitHub Pages)
├── governance-status.yaml generated; where every project stands
├── AGENTS.md              governance discovery for coding agents
├── .github/               CI workflows and branch protection
└── LICENSE, LICENSES/     CC-BY-SA-4.0 corpus prose; REUSE.toml covers all
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

**Every record is `Proposed`, and that is a decision rather than a backlog: ratification waits on a second active code owner.** GitHub does not count a PR author's own approval, so a ratification gate one person can satisfy alone is a gate in name only. See [handbook/governance-rollout.md](handbook/governance-rollout.md) for what is enforced and what the wait costs.

## Contributing

Work on a branch: `evolve/<slug>` for org-level changes, `perspective/<date>-<slug>` for opinions, `project/<name>` for project records. Open a draft PR (`gh pr create --draft`), assign it to the person who asked for it, and let a human review and merge. See [Branch namespaces](https://quaternionmedia.github.io/qm/ref/namespaces.md) and [handbook/async-contract.md](handbook/async-contract.md) for the rules.

## Licence

This corpus is CC-BY-SA-4.0. See [LICENSE](LICENSE), [LICENSES/](LICENSES/), and [REUSE.toml](REUSE.toml).
