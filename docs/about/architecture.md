# Architecture

!!! info "Source of truth"
    This is a summary of how the corpus structures governance. See [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md), [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md), and [Branch namespaces](../ref/namespaces.md) for the complete model.

## The branch-per-project model

Instead of copying the corpus into each project's repository, projects vendor this repo as a **submodule** and check out their own branch of it. This means:

- A project's decision records live on a `project/<name>` branch of the QM corpus, not in the project's own git history
- The project holds a submodule pointer to its branch tip
- When the org ratifies a new record, it reaches the project through a **propagation merge** — not a rebase, not a copy
- The project's own records stay on the same branch with their own numbering (`ADR-NNNN`)

This is called **adoption by reference**.

## Why this structure

### Single source of truth

The corpus is one place where all decisions live. When the org makes a decision, it doesn't need to be copied to 9+ projects — it propagates via git merge. One source of truth means no divergence, no "I updated it in one project and forgot the other."

### Governance as git state

The branch namespace is the entire project registry: a project that has no `project/<name>` branch is, by definition, not governed by the corpus. The same goes for decision records — they live where the branch ancestry says they should.

### Adoption discipline

Projects can't adopt casually. The fork procedure is eight steps with checks at each one. Projects are audited to ensure they have:

- The `governance/qm` submodule pointing to their branch
- The four CI workflows wired
- The seed files in place
- Records seeded in `adr/`

### Ratification as org action

When a record moves from `Proposed` to `Accepted`, it's a one-time human act in this repo. The ratification commit updates the index, flips the status, and names the record. That commit then propagates to every project in the next merge cycle, so all projects see the same set of binding records.

## How a project adopts

High level:

1. Add this repo as a submodule at `governance/qm`
2. Create a `project/<name>` branch here for the project's own records
3. Copy `project-seed/` into your project repository
4. Wire the four CI workflows that the seed ships
5. Seed your first records

See [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md) for the full procedure with checks.

## How updates reach a project

When the org updates the corpus:

1. A human reviews and ratifies a record on `main` (it moves from `Proposed` to `Accepted`)
2. A human merges `main` into the project's `project/<name>` branch via a `propagate/<name>-<date>` PR
3. This is a **merge**, never a rebase — the submodule pointer is pinned by ancestry, and rebasing breaks that pin
4. The project's `adr/` stays on its branch; the org's records reach the project through the parent commit

See [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) for details.

## Why records don't merge between projects

A `project/<name>` branch holds exactly one thing: how that project's governance deviates from the org. It is never merged into `main`. 

If a project record ever made it to `main`, its local decision would become an org record by accident — and the precedence rule would read backwards, with the project's own constraint binding every other project. The branch structure prevents this by making `project/<name>` a one-way valve: it receives `main`'s changes, but never gives back its own.

See [Branch namespaces](../ref/namespaces.md) for the mechanism that enforces this.

## Related

- [Branch namespaces](../ref/namespaces.md) — the namespace rules and enforcement
- [Record precedence](../ref/precedence.md) — how org and project records relate
- [Handbook: Forking a new project](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md) — the step-by-step procedure
- [Handbook: Propagation runbook](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) — how updates flow to projects
