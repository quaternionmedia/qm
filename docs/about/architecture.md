# Architecture

!!! info "Source of truth"
    This page is a summary. The full model is in [Branch namespaces](../ref/namespaces.md), [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md), and [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md).

## The branch-per-project model

Projects do not copy the [corpus](../ref/glossary.md#corpus){ .glossary-term } into their own repositories. Instead:

- Each project's decision records live on a `project/<name>` branch **of this repository**.
- The project adds this repository as a git submodule, checked out on that branch.
- When the org ratifies a new [record](../ref/glossary.md#record){ .glossary-term }, it reaches the project through a merge of `main` into the project's branch. This is called **[propagation](../ref/glossary.md#propagation){ .glossary-term }**.
- The project's own records stay on its branch, numbered `ADR-NNNN`.

This arrangement is called **[adoption by reference](../ref/glossary.md#adoption-by-reference){ .glossary-term }**.

## Why it works this way

**One source of truth.** All org decisions live in one place. An org-level change propagates to every project by a git merge, so there are no per-project copies to drift apart.

**The branch list is the project registry.** A project that has no `project/<name>` branch is, by definition, not governed by the corpus. There is no separate list to keep in sync.

**Adoption is checked, not assumed.** The fork procedure has eight steps, each with a check that proves it worked. Projects are audited afterward to confirm the submodule, the CI workflows, the [seed](../ref/glossary.md#seed){ .glossary-term } files, and the first records are all in place.

**[Ratification](../ref/glossary.md#ratification){ .glossary-term } happens once.** When a record becomes `Accepted` on `main`, the next propagation merge carries it to each project. Every project sees the same set of binding records.

## How a project adopts

In outline:

1. Add this repository as a submodule at `governance/qm`.
2. Create a `project/<name>` branch here for the project's own records.
3. Copy `project-seed/` into the project repository.
4. Wire the four CI workflows the seed ships.
5. Seed the first records.

The full procedure, with the check for each step, is [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md). See also the [tutorial outline](../usage/first-project.md).

## How updates reach a project

1. A human ratifies a record on `main`.
2. Someone cuts a `propagate/<name>-<date>` branch from the project's branch and merges `main` into it.
3. That branch becomes a pull request whose base is `project/<name>`. A human reviews and merges it.
4. The merge is always a merge commit — never a rebase. The project's submodule pins the branch tip by ancestry, and a rebase would break every pin.

See [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) for the full procedure.

## Why a project branch never merges into `main`

A `project/<name>` branch holds one thing: how that project's governance differs from the org's. It receives changes and never gives them back.

If a project branch merged into `main`, that project's records would land in the org namespace. A local decision would then read as an org record binding every other project — and nothing in the repository would look wrong afterward. The branch rules prevent this, and `project-seed/ci/check_pr_base.py` refuses such a pull request.

See [Branch namespaces](../ref/namespaces.md) for the rules.

## Related

- [Branch namespaces](../ref/namespaces.md) — the namespace rules and how they are enforced
- [Record precedence](../ref/precedence.md) — how org and project records relate
- [Forking a new project](../usage/first-project.md) — the adoption tutorial
