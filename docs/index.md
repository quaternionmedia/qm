---
icon: lucide/book-open
---

# QM Governance

Every team keeps answering the same questions. How does work get reviewed? When is something finished? What does a new project start from? Usually those answers live in people's heads, and they drift.

This is where Quaternion Media writes them down instead. Every QM project follows what is written here. A project can be stricter than these rules. It can never be looser.

If you read nothing else, read this next section. It is the part that catches people out.

## Read this first

1. **Decisions live in `records/`.** Nothing else here is binding. Everything else explains a [record](ref/glossary.md#record), points at one, or checks that we are keeping to it.
2. **Nothing is marked final yet.** Every record says [`Proposed`](ref/glossary.md#proposed), on purpose. Making one final is [ratification](ref/glossary.md#ratification), and it needs a second person to agree. There is not a second person yet.
3. **All work arrives as a pull request**, from a typo to a new rule. It is the paper trail, not a request for someone's attention. You merge your own once the automated [checks](ref/glossary.md#gate) pass.
4. **Two moments need a person, and the pull request is not one of them.** Making a record final, and putting a version tag on a project. A tag means somebody read the change, ran it against the real thing, and watched the checks pass. Reaching `main` claims none of that.

Every word above that is doing unusual work links to its definition. If a sentence stops making sense, the word is usually why — [the glossary](ref/glossary.md) has the rest.

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
