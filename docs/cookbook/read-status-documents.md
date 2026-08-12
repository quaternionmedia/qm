# Read status documents

Interpreting `governance-status.yaml` and `harness-status.json`.

## What they hold

| Document | Holds | Refresh | Staleness budget |
|---|---|---|---|
| `governance-status.yaml` | Where every project stands: branches, records, adoption artifacts | `python ci/governance_status.py --write governance-status.yaml` | 168 hours |
| `harness-status.json` | Pull request slots, phases claimed, governance evidence, in-flight threads | `python ci/harness_status.py --no-local --write harness-status.json` | 24 hours |

Both are committed to `main`. They are not regenerated in CI — they're refreshed as human actions.

## Rendering

To read them as markdown:

```bash
# For governance-status.yaml
python ci/governance_render.py governance-status.yaml

# For harness-status.json (the rendering is in the file itself)
cat harness-status.json | jq .  # or just read it
```

In **dossier** (the QM audit tool), both are integrated into a dashboard:

```bash
dossier governance dashboard --corpus-dir <this repo> --refresh
```

With `--refresh` it regenerates both documents, so you get current state.

## Key fields in governance-status.yaml

- `schema` — format version
- `generated_at` — when this was last refreshed
- `projects` — array of project records with:
  - `name` — project name
  - `branch` — the `project/<name>` branch name
  - `repository` — public GitHub repo URL (or null if not yet created)
  - `adoption` — artifact checklist (submodule, workflows, seed files)
  - `records_adopted` — count of org records this project has
  - `behind_corpus` — how many commits the project's branch is behind `main`

## Key fields in harness-status.json

See the `reading:` block inside the file for the refresh command, staleness budget, and what not to do. The format is JSON; it's human-readable once you `jq` it or open it in an editor.

## When they go stale

- **governance-status.yaml**: 168 hours (7 days). If it's older, refresh it before quoting a number.
- **harness-status.json**: 24 hours. Refresh before relying on in-flight thread counts.

Check the `generated_at` timestamp in each. If you're going to quote a number from one, include the date — it says what was true on that day.

## Related

- [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md) — the full documentation on these files
- [Repository layout](../ref/repo-layout.md) — what these files are in the tree
