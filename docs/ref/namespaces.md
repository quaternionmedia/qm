# Branch namespaces

!!! info "Source of truth"
    This page is the canonical statement for branch conventions in the QM corpus. Cited as: [quaternionmedia/qm](https://github.com/quaternionmedia/qm) `docs/ref/namespaces.md`.

`main` carries the constitution and nothing else. Five namespaces hang off it, and a branch outside them is a mistake rather than a variation.

## The five namespaces

| Namespace | Holds | Lifetime |
|---|---|---|
| `project/<name>` | one adopting project's `adr/` | permanent — a downstream submodule pins its tip |
| `propagate/<name>-<date>` | `main` merged toward one `project/<name>` | deleted after merge |
| `perspective/<date>-<slug>` | one perspective, staged for `main` | deleted after merge |
| `evolve/<slug>` | org-level work in progress | deleted after merge |
| `workspace/<slug>` | a research workspace that never merges back | permanent, terminal |

## How a `project/<name>` branch works

A `project/<name>` branch is never merged into `main`. Not once, not squashed, not "just the shared part". It exists in perpetuity and holds exactly one thing: how one project's governance deviates from `main`. Merging it would move that project's `adr/` onto `main`, and `main` is the org namespace — so one project's local decision would become an org record by accident, and the precedence rule would then read backwards, with the project's own record appearing to bind every other project.

A `project/<name>` branch takes changes **in**, never gives them out:

| Direction | How |
|---|---|
| project-specific records arrive | a pull request whose **base** is `project/<name>`. Each such base holds its own slot under the one-PR rule, which is what the `--per-base 'project/*'` exemption is for |
| the branch is created | cut from `main`, `adr/` copied from `project-seed/adr/`, and **pushed** — see [Forking a new project](../usage/first-project.md), step 2. The initial content is not a pull request, because the only base it could target is a branch that does not exist yet |
| `main`'s changes reach it | `main` is merged **into** it, as a `propagate/<name>-<date>` pull request against it. Never a rebase: a downstream submodule pins the tip, and rebasing invalidates every pin |
| the project's own repository sees it | the submodule pointer, bumped by that same propagation |

A `project/<name>` branch is therefore never the *head* of a pull request, whatever the base is and whatever it carries. The check that enforces this is `project-seed/ci/check_pr_base.py`.

## Related

- [Record precedence](precedence.md) — how records in different namespaces relate to each other
- [Repository layout](repo-layout.md) — where project branches live in the broader structure
- [Handbook: Async contract](https://github.com/quaternionmedia/qm/blob/main/handbook/async-contract.md) — the rules that exist only because several agent sessions run at once
