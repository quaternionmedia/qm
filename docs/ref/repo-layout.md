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
├── governance-status.yaml generated: where every project stands
├── harness-status.json    generated: PR slots and work in flight
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

Do not edit these by hand:

| File | Refresh command |
|---|---|
| `governance-status.yaml` | `python ci/governance_status.py --write governance-status.yaml` |
| `harness-status.json` | `python ci/harness_status.py --no-local --write harness-status.json` |

Both are committed; CI does not regenerate them. See [Read status documents](../cookbook/read-status-documents.md) and [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md).

The `site/` directory (the built documentation) and `.cache/` (the build cache) are generated and not committed.

## Where project records live

An adopting project's records are **not** in this tree. They live on that project's `project/<name>` branch, as a top-level `adr/` directory that exists only there. See [Branch namespaces](namespaces.md) and [Architecture](../about/architecture.md).

## Related

- [Branch namespaces](namespaces.md) — the branch model
- [Handbook index](handbook.md) — what each [handbook](../ref/glossary.md#handbook){ .glossary-term } page answers
