# Read status documents

Read `status/governance.yaml` and `status/harness.yaml` correctly.

## What they are

Two generated files, committed on `main`:

| Document | Holds | Refresh command | Stale after |
|---|---|---|---|
| `status/governance.yaml` | Where every project stands: branch state, records, adoption artifacts | `python ci/governance_status.py --write status/governance.yaml` | 168 hours |
| `status/harness.yaml` | Pull request slots, phases claimed, work in flight | `python ci/harness_status.py --no-local --write status/harness.yaml` | 24 hours |

CI does not regenerate them. A person runs the refresh command and commits the result.

## Check the age first

Each file carries a `generated_at` timestamp. Check it before quoting any figure: a stale number delivered with confidence looks checked, and is not.

`status/harness.yaml` also carries a `reading:` block inside the file — its own refresh command, staleness budget, and a `do_not` list. `status/governance.yaml` has no such block; its rules live only in [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md).

## Render them as pages

```bash
# status/governance.yaml → markdown
python ci/governance_render.py status/governance.yaml

# status/harness.yaml → markdown
python ci/harness_dashboard.py status/harness.yaml --format md
```

## What status/governance.yaml contains

Top-level keys: `schema`, `generated_at`, `generator`, `corpus`, `projects`, `org`, and `undefined`.

Each entry in `projects` reports, among other fields:

- `branch` — the project branch's commit, how far behind or ahead of the [corpus](../ref/glossary.md#corpus){ .glossary-term } it is, and the last [propagation](../ref/glossary.md#propagation){ .glossary-term }
- `records` — how many records the project has, and their statuses
- `adoption` — which adoption artifacts (submodule, workflows, IDE files, licensing) are present
- `repository` — facts about the project's own repository, or `unknown` with the reason

The file deliberately does not compute an "adopted: yes/no" verdict. The `undefined` key lists the terms it declines to compute, with the reason for each.

## What it refuses to do

A fact the generator could not establish is reported as `unknown` with the reason — never omitted, never defaulted to the reassuring value. Read `unknown` as "nothing was checked", not as "nothing is wrong".

## Related

- [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md) — the full rules for both documents
- [Repository layout](../ref/repo-layout.md) — where these files sit
