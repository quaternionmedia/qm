# Next steps

After your project has adopted the corpus: propagation, audits, status documents, and governance phases.

## Propagation — keeping your project in sync

When the org ratifies a new record on `main`, it reaches your project through a **propagation merge** — not a copy, not a rebase.

A human on the org team:

1. Creates a `propagate/<name>-<date>` branch
2. Merges `main` into your `project/<name>` branch via this branch as a PR
3. You review and merge

Your `project/<name>` branch receives the org records without ever rebasing, so your submodule pointer stays pinned.

See [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) for the full procedure.

## Adoption audits

The org periodically audits projects to ensure they have:

- The `governance/qm` submodule at the right branch
- All four CI workflows wired and passing
- The seed files in place
- Records seeded correctly

See [handbook/adoption-audit-queue.md](https://github.com/quaternionmedia/qm/blob/main/handbook/adoption-audit-queue.md) for how audits work and how to prepare for one.

## Status documents

Two documents track the state of the corpus and all its projects:

### `governance-status.yaml`

Where every project stands: branches created, records adopted, adoption artifacts present, behind-corpus count.

- **Refresh:** `python ci/governance_status.py --write governance-status.yaml` (reads other repositories)
- **Staleness:** 168 hours
- **Rendering:** `python ci/governance_render.py governance-status.yaml` → markdown view
- **See:** [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md) for details

### `harness-status.json`

Pull request slots, phases claimed, governance evidence, and threads in flight.

- **Refresh:** `python ci/harness_status.py --no-local --write harness-status.json`
- **Staleness:** 24 hours
- **Rendering:** included in the file itself
- **See:** [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md) for details

Both are committed to `main`. They're not regenerated on every push — updates are human actions.

## The project phase ladder

Projects progress through governance maturity levels: Bootstrapping, Consolidated, Scaled. Each phase has specific requirements and gates.

See [records/DRAFT-project-phase-ladder.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-project-phase-ladder.md) for the ladder, what moves you between phases, and what obligations each phase carries.

## Related

- [Architecture](../about/architecture.md) — how the branch-per-project model works
- [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) — the full propagation procedure
- [handbook/adoption-audit-queue.md](https://github.com/quaternionmedia/qm/blob/main/handbook/adoption-audit-queue.md) — audit procedures
- [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md) — status document refresh and staleness
- [records/DRAFT-project-phase-ladder.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-project-phase-ladder.md) — the phase model
