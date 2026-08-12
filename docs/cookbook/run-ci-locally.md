# Run CI locally

Testing your changes before pushing.

## The script

The seed ships a helper script:

```bash
python project-seed/ci/run_workflows_locally.py
```

This runs the same checks that CI runs on your branch, so you can catch issues before pushing.

## What it checks

The script runs:

- `adr-lint.py` — validates your record index
- `check_one_pr.py` — ensures one open PR per contributor
- `check_pr_base.py` — guards branch naming and refusal rules
- `reuse-lint` — validates copyright and license metadata

For org-level work (on `main`), there's also:

- `namespace-guard.py` — on `project/*` branches, guards that you're only touching `adr/`

## Usage

```bash
# Run all checks
python project-seed/ci/run_workflows_locally.py

# Run a specific workflow by name
python project-seed/ci/run_workflows_locally.py --workflow adr-lint

# See all options
python project-seed/ci/run_workflows_locally.py --help
```

The script reads your current git state (branch, staged files, commits) so it gives you feedback on what you've actually written.

## Before pushing

Run the script, fix any errors it reports, commit again, and push:

```bash
python project-seed/ci/run_workflows_locally.py
# fix any issues
git add . && git commit -m 'fix: ...'
git push
```

Now when you open the PR, CI should pass on the first try.

## Related

- [project-seed/ci/run_workflows_locally.py](https://github.com/quaternionmedia/qm/blob/main/project-seed/ci/run_workflows_locally.py) — the script itself
- [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) — what's enforced vs. written-only
