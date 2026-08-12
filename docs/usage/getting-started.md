# Getting started

Your first hour with the QM corpus.

## Clone the repo

```bash
git clone https://github.com/quaternionmedia/qm.git
cd qm
```

## Read the charter

Open [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) — it is short and states what QM believes. These eleven principles govern everything below them.

## Understand the three invariants

From the README:

1. **Records in `records/` are the only binding documents.** Everything else points at them. `perspectives/` is opinion and binds nothing.
2. **Every record is `Proposed`.** None is ratified, and that is deliberate — ratification waits on a second active code owner, because a gate one person can satisfy alone is a gate in name only.
3. **Every change arrives as a pull request**, from a typo to a new record. Nobody merges their own work into `main`.

## Find what you need

| You want to | Go to |
|---|---|
| Know what QM believes in detail | Read [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) in full |
| Understand the records | See [Overview](../about/overview.md); then browse [records/](https://github.com/quaternionmedia/qm/tree/main/records/) |
| Fork a new QM project | [Forking a new project](first-project.md) — the step-by-step walkthrough |
| Know how projects relate to the org | [Architecture](../about/architecture.md) — the branch-per-project model |
| Understand branches and their rules | [Branch namespaces](../ref/namespaces.md) |
| Read the status of every project | [governance-status.yaml](https://github.com/quaternionmedia/qm/blob/main/governance-status.yaml) and [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md) for how to read it |
| See what's currently being worked on | [harness-status.json](https://github.com/quaternionmedia/qm/blob/main/harness-status.json) for pull request slots and in-flight work |
| Learn policy and procedure | [Handbook index](../ref/handbook.md) |
| Work here as a coding agent | [AGENTS.md](https://github.com/quaternionmedia/qm/blob/main/AGENTS.md) |

## Make your first change

Pick something small: a typo fix, an admonition clarification, a missing link. Then:

1. Branch: `git checkout -b evolve/<your-slug>`
2. Make the change
3. Commit: `git add . && git commit -m 'what you changed'`
4. Open a draft PR: `gh pr create --draft` (no review request)
5. Assign it to yourself or the person who asked for it
6. A human reviews and merges when ready

That's it. See [handbook/async-contract.md](https://github.com/quaternionmedia/qm/blob/main/handbook/async-contract.md) for the multi-session rules if multiple agents are working at once.

## Related

- [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) — the charter
- [AGENTS.md](https://github.com/quaternionmedia/qm/blob/main/AGENTS.md) — if you're a coding agent
- [Forking a new project](first-project.md) — when you're ready to adopt the corpus in a new project
