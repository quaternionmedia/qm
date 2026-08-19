# Getting started

What to do in your first hour with the QM corpus.

## What this is, in ordinary words

An organisation makes the same decisions over and over: how work gets reviewed,
when something counts as finished, what a new project starts from. Usually
those answers live in people's heads, and they drift.

This repository is where Quaternion Media writes them down instead. Every other
QM project points at it and follows what it says. A project may be stricter
than these rules; it may never be looser.

**What a "record" is.** One decision, written down: what was decided, what the
situation was, what else was considered, and what it costs. Not a guide and not
a tutorial — a decision, with its reasoning attached, so that a year later
somebody can see *why* rather than guess. They live in `records/` and they are
the only documents here that bind anybody. Everything else explains them,
points at them, or checks them.

**Why nothing is marked final.** Every record says `Proposed`. Making one final
takes a second person, and there is not a second person yet. That is a stated
position rather than an oversight: a step one person can complete alone is not
a check on anything.

**A warning about the words.** A few ordinary words are used here in a narrow
sense, and several mean more than one thing — *record*, *draft*, *gate*,
*review*, *phase*, *delta*. When a sentence stops making sense, that is usually
why. The [glossary](https://github.com/quaternionmedia/qm/blob/main/handbook/glossary.md)
sorts them out and is the shortest useful thing to read after this page.

## 1. Clone the repository

```bash
git clone https://github.com/quaternionmedia/qm.git
cd qm
```

## 2. Read the charter

Read [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md). It is short and states what QM believes. Everything else in the corpus is cut from it.

## 3. Learn the rules that bind

1. **Only `records/` binds.** Records are the only binding documents. Everything else points at them. `perspectives/` is opinion and binds nothing.
2. **Every record is `Proposed`.** None is ratified yet, and that is deliberate: ratification requires approval from a second active code owner.
3. **Every change arrives as a pull request** — from a typo fix to a new record. It is the audit record rather than a request for attention, and its author merges it once every gate is green. Nothing reaches `main` by direct push.
4. **Two moments need a human, and the pull request is neither**: ratifying a record, and putting a version tag on a project. A tag says a person read the change set, ran it against the real thing, and saw the checks pass. `main` is not a claim, so merging into it is not a release.

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
