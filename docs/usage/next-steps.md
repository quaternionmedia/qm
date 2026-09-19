# Next steps

What happens after a project has adopted the corpus.

## Propagation: staying in sync

When the org changes `main` — a ratified [record](../ref/glossary.md#record){ .glossary-term }, an updated procedure — the change reaches your project through a **[propagation](../ref/glossary.md#propagation){ .glossary-term } merge**:

1. Someone cuts a `propagate/<name>-<date>` branch from your `project/<name>` branch.
2. They merge `main` into it and open a pull request whose base is `project/<name>`.
3. A human reviews and merges. The merge commit is the new submodule pin.

The merge is never a rebase: your submodule pins the branch tip by ancestry, and a rebase would break the pin.

See [Propagate a change](../cookbook/propagate-a-change.md) for the commands, and [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) for the full procedure.

## Adoption audits

The org audits adopted projects to confirm each one has:

- the `governance/qm` submodule on the right branch,
- the four [seed](../ref/glossary.md#seed){ .glossary-term } CI workflows,
- the seed files (`AGENTS.md`, editor config) in place,
- records seeded on its branch.

See [handbook/adoption-audit-queue.md](https://github.com/quaternionmedia/qm/blob/main/handbook/adoption-audit-queue.md) for how audits run.

## The status documents

Two generated files on `main` track the state of the [corpus](../ref/glossary.md#corpus){ .glossary-term } and its projects:

| Document | Holds | May be stale after |
|---|---|---|
| `governance-status.yaml` | Where every project stands: branches, records, adoption artifacts | 168 hours |
| `harness-status.json` | Pull request slots, phases claimed, work in flight | 24 hours |

Both are refreshed by a person running a command, not by CI. Check the `generated_at` timestamp before quoting a number from either. See [Read status documents](../cookbook/read-status-documents.md).

## The project phase ladder

Each project reports a phase as a version number. Only the first rung is defined org-wide:

- **`v0.0.1` — governance.** The project has adopted the QM constitution. This rung means the same thing for every project.
- **Rungs above `v0.0.1`** are defined by each project in its own records. A rung a project has not defined is not yet meaningful for it.
- A project that states no phase defaults to `v0.0.1`.

See [records/DRAFT-project-phase-ladder.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-project-phase-ladder.md) for the full model.

## Related

- [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) — propagation in full
- [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md) — the status documents in full
- [Architecture](../about/architecture.md) — the model behind all of this
