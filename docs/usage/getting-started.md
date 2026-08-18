# Getting started

What to do in your first hour with the QM corpus.

## 1. Clone the repository

```bash
git clone https://github.com/quaternionmedia/qm.git
cd qm
```

## 2. Read the charter

Read [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md). It is short and states what QM believes. Everything else in the corpus is cut from it.

## 3. Learn the three invariants

1. **Only `records/` binds.** Records are the only binding documents. Everything else points at them. `perspectives/` is opinion and binds nothing.
2. **Every record is `Proposed`.** None is ratified yet, and that is deliberate: ratification requires approval from a second active code owner.
3. **Every change arrives as a pull request** — from a typo fix to a new record. Nobody merges their own work into `main`.

## 4. Find what you need

| You want to | Go to |
|---|---|
| Read the principles in full | [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) |
| Understand the records | [Overview](../about/overview.md), then [records/](https://github.com/quaternionmedia/qm/tree/main/records) |
| Set up a new QM project | [Forking a new project](first-project.md) |
| Understand how projects relate to the org | [Architecture](../about/architecture.md) |
| Learn the branch rules | [Branch namespaces](../ref/namespaces.md) |
| See where every project stands | [governance-status.yaml](https://github.com/quaternionmedia/qm/blob/main/governance-status.yaml); how to read it: [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md) |
| Learn policy and procedure | [Handbook index](../ref/handbook.md) |
| Work here as a coding agent | [AGENTS.md](https://github.com/quaternionmedia/qm/blob/main/AGENTS.md) |

## 5. Make your first change

Pick something small — a typo, a broken link, an unclear sentence. Then:

1. Create a branch: `git checkout -b evolve/<slug>`
2. Make the change and commit it.
3. Open a draft pull request: `gh pr create --draft`. Do not request a review.
4. Assign the person who asked for the work.
5. A human reviews and merges.

If several agent sessions run at the same time, the rules in [handbook/async-contract.md](https://github.com/quaternionmedia/qm/blob/main/handbook/async-contract.md) apply. The most important one: one open pull request per repository, per contributor.

## Next

- [Forking a new project](first-project.md) — adopt the corpus in a new project
- [Cookbook](../cookbook/index.md) — recipes for common tasks
