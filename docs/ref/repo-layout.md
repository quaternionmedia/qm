# Repository layout

!!! info "Scope"
    This page describes [quaternionmedia/qm](https://github.com/quaternionmedia/qm), the corpus repository itself. An adopting project's layout is described by the seed it copies.

## The tree

```
qm/
├── PRINCIPLES.md          the charter: what QM believes, and why
├── README.md              the entry point
├── AGENTS.md              instructions for coding agents
├── CLAUDE.md              symlink to AGENTS.md
├── TEMPLATE.md            the record template
├── records/               org records; the only binding documents
├── registers/             live org-level registers (carried patches)
├── handbook/              policy, status, and procedures
├── perspectives/          dated, attributed, non-binding opinion
├── project-seed/          what a new project copies: adr/, ci/, ide/
├── ci/                    org-level tooling: the status generators
├── docs/                  this documentation site
│   ├── families/          generated: a page per family
│   ├── projects/          generated: a page per project
│   │   └── <name>/        a project's dated history: its timeline, round log and retrospectives
│   └── show/              the showgraphs: pictures a tool drew, with their show documents
├── includes/              the front page's showcase, generated and included by docs/index.md
├── families.json          generated: every family and its members, from the family record
├── ci/showcase.yaml       the showcase: pictures a person picked for each project
├── status/governance.yaml generated: where every project stands
├── status/harness.yaml    generated: open PRs and work in flight
├── .github/               CI workflows, CODEOWNERS, ruleset config
├── adapters/              optional per-tool glue; nothing depends on it
├── LICENSE                CC-BY-SA-4.0, for corpus prose
├── LICENSES/              full license texts
└── REUSE.toml             per-path license and copyright metadata
```

## Symlinks

`CLAUDE.md` and `.github/copilot-instructions.md` are symlinks to `AGENTS.md`, so any tool reading either gets its current content. `.vscode/` symlinks into `project-seed/ide/`, which is the single source for what a project copies.

Nothing vendor-specific is in `project-seed/`. Anything there is copied into every adopting project and would become an org standard by accident, so per-tool glue lives in `adapters/<product>/` instead — optional, and the governance text depends on none of it.

## Generated files

Do not edit these by hand. `ci/doc_status.py` lists them, and `status/documents.yaml` gives each one's refresh command under `refresh`. `uv run qm docs generate` runs most of the generators in one pass, the site's pages among them, and `uv run qm docs check` says which outputs are stale. The site's pages have a command of their own:

| Files | Refresh command |
|---|---|
| `docs/families/`, `docs/projects/` but a project's subtree, `includes/` | `uv run qm cookbook docs/families --site --write` |
| `docs/projects/<name>/timeline.md` and `git.yaml` | `uv run qm timeline <name> --write`, which reads the project's clone |

They are committed, and CI regenerates none of them. The `docs-audit` workflow refuses a family page, project page, front-page snippet or project timeline that no longer matches its sources, per [the project-page record](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-a-project-page-shows-what-was-picked-and-what-was-drawn.md). The pictures under `docs/show/` are drawn by codecartographer's `uv run codecarto show export`, and are regenerated rather than edited. See [Build these docs](../usage/build-these-docs.md), [Read status documents](../usage/read-status-documents.md) and [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md).

The `site/` directory (the built documentation) and `.cache/` (the build cache) are generated and not committed.

## Where project records live

An adopting project's records are **not** in this tree. They live on that project's `project/<name>` branch, as a top-level `adr/` directory that exists only there. See [Branch namespaces](namespaces.md) and [Architecture](../about/architecture.md).

## Related

- [Branch namespaces](namespaces.md) — the branch model
- [Handbook index](handbook.md) — what each [handbook](../ref/glossary.md#handbook){ .glossary-term } page answers
