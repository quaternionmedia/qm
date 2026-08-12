---
icon: lucide/book-open
---

# QM Governance

The Quaternion Media constitution: the decisions that govern every QM project, the process that keeps them consistent, and the template each new project starts from.

**Projects adopt this corpus by reference.** A project may tighten these rules, but never relax them.

## Read this first

1. **Only `records/` binds.** Records are the only binding documents. Everything else points at them. `perspectives/` is opinion and binds nothing.
2. **Every record is `Proposed`.** None is ratified yet, and that is deliberate: ratification requires approval from a second active code owner.
3. **Every change arrives as a pull request** — from a typo fix to a new record. Nobody merges their own work into `main`.

## Where to go

=== "Understand"

    **Learn what QM is and how it works**

    - [Overview](about/overview.md) — the corpus, its principles, and the records
    - [Architecture](about/architecture.md) — the branch-per-project model
    - [History](about/history.md) — how the corpus evolved

    Or start with the [charter](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md): eleven principles, short.

=== "Get started"

    **Your first hour with the corpus**

    - [Getting started](usage/getting-started.md) — clone, read, and make your first change
    - [Forking a new project](usage/first-project.md) — adopt the corpus in a new project
    - [Next steps](usage/next-steps.md) — propagation, audits, and project phases

=== "Do a task"

    **Practical recipes**

    - [Draft a record](cookbook/draft-a-record.md) — write a decision
    - [Add a perspective](cookbook/add-a-perspective.md) — document an opinion or incident
    - [Propagate a change](cookbook/propagate-a-change.md) — send org updates to a project
    - [Run CI locally](cookbook/run-ci-locally.md) — test before you push
    - [All recipes](cookbook/index.md)

=== "Look it up"

    **Reference**

    - [Branch namespaces](ref/namespaces.md) — the five branch conventions
    - [Record precedence](ref/precedence.md) — how org and project records relate
    - [Ratification](ref/ratification.md) — how records become binding
    - [Repository layout](ref/repo-layout.md) — the directory tree
    - [Handbook index](ref/handbook.md) — policy and procedure
    - [Glossary](ref/glossary.md) — key terms

## For coding agents

If you are an AI agent working in this repository, start with [AGENTS.md](https://github.com/quaternionmedia/qm/blob/main/AGENTS.md). It states four facts to establish before writing anything — the commit, your pull request slot, what else is in flight, and which gates exist — and names the plain scripts that establish them. How you gather them is your choice; `adapters/` holds optional glue for particular tools and nothing depends on it.

## See also

- [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) — the charter
- [The repository on GitHub](https://github.com/quaternionmedia/qm)
