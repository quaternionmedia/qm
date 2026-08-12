---
icon: lucide/book-open
---

# QM Governance

The Quaternion Media constitution: the org-level decision corpus that governs every QM project, the process that keeps them coherent, and the template each new project forks from.

**Projects adopt this corpus by reference** and may tighten its rules — never relax them.

---

## What you want to do

<!-- Cards layout using the Material Mkdocs approach -->

=== "📖 Understand"

    **Learn what QM is and how it works**

    - [Overview](about/overview.md) — The corpus, its principles, and the records
    - [Architecture](about/architecture.md) — The branch-per-project model
    - [History](about/history.md) — How the corpus evolved
    
    Or start with the [charter](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) (11 principles, short read).

=== "🚀 Get started"

    **Your first hour with the corpus**

    - [Getting started](usage/getting-started.md) — Clone, read, and make your first change
    - [Forking a new project](usage/first-project.md) — Adopt the corpus in your project (8 steps)
    - [Next steps](usage/next-steps.md) — Propagation, audits, and governance phases

=== "🔧 Do something"

    **Practical recipes**

    - [Draft a record](cookbook/draft-a-record.md) — Write a decision
    - [Add a perspective](cookbook/add-a-perspective.md) — Document opinion or an incident
    - [Propagate a change](cookbook/propagate-a-change.md) — Send org updates to your project
    - [Run CI locally](cookbook/run-ci-locally.md) — Test before you push
    - [More recipes](cookbook/index.md) — Status documents, building docs, and more

=== "📚 Look it up"

    **Reference and specs**

    - [Branch namespaces](ref/namespaces.md) — The five namespace conventions (canonical)
    - [Record precedence](ref/precedence.md) — How org and project records relate
    - [Ratification](ref/ratification.md) — How records move from Proposed to Accepted
    - [Repository layout](ref/repo-layout.md) — The directory tree
    - [Handbook index](ref/handbook.md) — Policy and procedure
    - [Glossary](ref/glossary.md) — Key terms

---

## The three invariants

Before anything else, know these:

1. **Records in `records/` are the only binding documents.** Everything else points at them. `perspectives/` is opinion and binds nothing.
2. **Every record is `Proposed`.** None is ratified, and that is deliberate — ratification waits on a second active code owner, because a gate one person can satisfy alone is a gate in name only.
3. **Every change arrives as a pull request**, from a typo to a new record. Nobody merges their own work into `main`.

---

## For coding agents

If you're an AI working here, start with [AGENTS.md](https://github.com/quaternionmedia/qm/blob/main/AGENTS.md). Run `/cowork` first.

---

## See also

- [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) — the charter (11 principles)
- [README.md](https://github.com/quaternionmedia/qm/blob/main/README.md) — the repo onramp
- [GitHub](https://github.com/quaternionmedia/qm) — the source repository
