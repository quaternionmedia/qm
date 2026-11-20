# Branch namespaces

!!! info "Canonical"
    This page is the canonical statement of the branch rules for [quaternionmedia/qm](https://github.com/quaternionmedia/qm). Tools and other documents cite it as `docs/ref/namespaces.md`.

`main` carries the constitution and nothing else. The namespaces below hang off it. A branch outside them is a mistake, not a variation.

## The namespaces

| Namespace | Holds | Lifetime |
|---|---|---|
| `project/<name>` | one adopting project's `adr/` | permanent — a downstream submodule pins its tip |
| `propagate/<name>-<date>` | `main` merged toward one `project/<name>` or `workspace/<slug>` | deleted after merge |
| `perspective/<date>-<slug>` | one [perspective](../ref/glossary.md#perspective){ .glossary-term }, staged for `main` | deleted after merge |
| `evolve/<slug>` | org-level work in progress, or one project's records, cut from its `project/<name>` and opened against it | deleted after merge |
| `workspace/<slug>` | a research [workspace](../ref/glossary.md#workspace){ .glossary-term } that never merges back | permanent, terminal |
| `math/<slug>` | one exploration, cut from a `workspace/<slug>` branch and opened against it | deleted after merge into its workspace |

## The stage refs, which are not work namespaces

`test`, `dev`, `prod` and `main` are **stages** — claims about how far a change
has travelled, decided in the [record](../ref/glossary.md#record){ .glossary-term } *A stage is recorded, and `main` receives
releases rather than asserting them*. Work never happens on one: a branch is
still cut in one of the namespaces above, and a stage only ever receives
merges. `test` is the one rewritable ref in the model; the other three are
append-only. Until that record is ratified and the stages are pushed, they are
a local staging convention, and this section is what keeps a reader from
sorting them under "a branch outside them is a mistake".

## Rules for `project/<name>` branches

**A `project/<name>` branch is never merged into `main`.** Not once, not squashed, not partially. It exists permanently and holds exactly one thing: how one project's governance differs from `main`.

The reason: merging it would move that project's `adr/` onto `main`, the org namespace. The project's local decisions would then read as org records binding every other project — and nothing in the repository would look wrong afterward.

A `project/<name>` branch takes changes **in** and never gives them out:

| Direction | How |
|---|---|
| Project records arrive | A pull request whose **base** is `project/<name>`. |
| The branch is created | Cut from `main`, `adr/` copied from `project-seed/adr/`, then **pushed** — not opened as a pull request, because the only base it could target does not exist yet. See [Forking a new project](../usage/first-project.md), step 2. |
| `main`'s changes arrive | `main` is merged **into** the branch, through a `propagate/<name>-<date>` pull request. Never a rebase: a downstream submodule pins the tip, and a rebase breaks every pin. |
| The project's repository sees it | Through the submodule pointer, bumped by that same [propagation](../ref/glossary.md#propagation){ .glossary-term } merge. |

A `project/<name>` branch is therefore never the **head** of a pull request, whatever the base. The check `project-seed/ci/check_pr_base.py` refuses that, and separately refuses any branch that carries a top-level `adr/` aimed at `main`.

## Rules for `workspace/<slug>` branches and their explorations

**A `workspace/<slug>` branch is never merged into `main`**, and nothing in it binds. It takes changes in two ways: `main` arrives through a `propagate/<slug>-<date>` pull request, merged and never rebased, and research arrives through a `math/<slug>` exploration, cut from the workspace and opened against it. Several explorations are open at once by design; each is its own pull request and none is stacked.

An exploration's only legal base is a `workspace/*` branch. `project-seed/ci/check_pr_base.py` refuses a `math/*` head aimed at anything else, an intermediate base included. [Research workspaces](https://github.com/quaternionmedia/qm/blob/main/handbook/research-workspaces.md) is the procedure.

## Related

- [Record precedence](precedence.md) — how records in the two namespaces relate
- [Propagate a change](../usage/propagate-a-change.md) — the merge procedure
- [handbook/async-contract.md](https://github.com/quaternionmedia/qm/blob/main/handbook/async-contract.md) — the stacked-PR rule and the rest of the multi-session contract
