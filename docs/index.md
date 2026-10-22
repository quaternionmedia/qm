---
icon: lucide/book-open
---

<p class="qm-eyebrow">Quaternion Media · governance</p>

# QM Governance

<p class="qm-lede">Every team keeps answering the same questions. How does work get reviewed? When is something finished? What does a new project start from? This is where Quaternion Media writes the answers down. Every QM project follows what is written here, and a project can be stricter than these rules, never looser.</p>

[![The QM families as a desk of channel strips: performing, holding instruments, performer-display and show-control, then civic, core, games, infra and irl, each with a meter lit by the share of its members that is governed.](families/families.svg){ .qm-picture }](families/index.md)

The estate, by what each repository drives. `performing` holds the three families that put on a show, a repository that drives two things is in both, and each meter is lit by the share governed. The families are decided in [the family record](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-a-family-is-bordered-by-what-it-drives.md); [every family has a page](families/index.md).
{ .qm-caption }

## Read this first

If you read nothing else, read this. It is the part that catches people out.

1. **Decisions live in `records/`.** Nothing else here is binding. Everything else explains a [record](ref/glossary.md#record), points at one, or checks that we are keeping to it.
2. **Nothing is marked final yet.** Every record says [`Proposed`](ref/glossary.md#proposed), on purpose. Making one final is [ratification](ref/glossary.md#ratification), and it needs a second person to agree. There is not a second person yet.
3. **All work arrives as a pull request**, from a typo to a new rule. It is the paper trail, not a request for someone's attention. You merge your own once the automated [checks](ref/glossary.md#gate) pass.
4. **Two moments need a person, and the pull request is not one of them.** Making a record final, and putting a version tag on a project. A tag means somebody read the change, ran it against the real thing, and watched the checks pass. Reaching `main` claims none of that.

Every word above that is doing unusual work links to its definition. If a sentence stops making sense, the word is usually why — [the glossary](ref/glossary.md) has the rest.

## Where to go

<div class="grid" markdown>

<div class="card" markdown>

**understand**

What QM is and how it works.

- [Overview](about/overview.md) — the [corpus](ref/glossary.md#corpus){ .glossary-term }, its principles, and the records
- [Architecture](about/architecture.md) — the branch-per-project model
- [History](about/history.md) — how the corpus evolved
- [The charter](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) — what QM believes, and the record each principle produces

</div>

<div class="card" markdown>

**get started**

Your first hour with the corpus.

- [Getting started](usage/getting-started.md) — clone, read, and make your first change
- [Questions a new developer asks](usage/questions-a-new-developer-asks.md) — first-week questions, and the command that answers each
- [Forking a new project](usage/first-project.md) — adopt the corpus in a new project
- [Next steps](usage/next-steps.md) — [propagation](ref/glossary.md#propagation){ .glossary-term }, audits, and project phases

</div>

<div class="card" markdown>

**do a task**

Practical recipes.

- [Draft a record](cookbook/draft-a-record.md) — write a decision
- [Add a perspective](cookbook/add-a-perspective.md) — document an opinion or incident
- [Propagate a change](cookbook/propagate-a-change.md) — send org updates to a project
- [Run CI locally](cookbook/run-ci-locally.md) — test before you push
- [All recipes](cookbook/index.md)

</div>

<div class="card" markdown>

**look it up**

Reference.

- [Branch namespaces](ref/namespaces.md) — the five branch conventions
- [Record precedence](ref/precedence.md) — how org and project records relate
- [Ratification](ref/ratification.md) — how records become binding
- [Repository layout](ref/repo-layout.md) — the directory tree
- [Handbook index](ref/handbook.md) — policy and procedure
- [Protocols index](ref/protocols.md) — the reviews somebody runs on purpose
- [Glossary](ref/glossary.md) — key terms

</div>

</div>

## For coding agents

If you are an AI agent working in this repository, start with [AGENTS.md](https://github.com/quaternionmedia/qm/blob/main/AGENTS.md). It states four facts to establish before writing anything — the commit, your open pull requests, what else is in flight, and which gates exist — and names the plain scripts that establish them. How you gather them is your choice; `adapters/` holds optional glue for particular tools and nothing depends on it.

## See also

- [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) — the charter
- [The repository on GitHub](https://github.com/quaternionmedia/qm)
