# Run CI locally

Run the repository's CI checks before you push.

## The runner

```bash
python project-seed/ci/run_workflows_locally.py
```

This reads the workflow files in `.github/workflows/` and executes their actual steps. That is the point: running the commands you *think* a workflow contains is not the same as running the workflow, and the difference is where false "CI is green" claims come from.

## Options

All flags are optional:

| Flag | Default | Meaning |
|---|---|---|
| `--event` | `pull_request` | Which trigger to simulate |
| `--ref` | `main` | Branch for a `push` event |
| `--base-ref` | `main` | Pull request base branch |
| `--head-ref` | current branch | Pull request head branch |
| `--workflows` | `.github/workflows` | Directory of workflow files to run |

That table is checked against the tool rather than maintained beside it. This
page is executed by pytest, and the example below fails if a flag is added,
removed or renamed — so a reader can trust the table because a build would have
gone red otherwise.

    >>> import re, subprocess, sys
    >>> help_text = subprocess.run(
    ...     [sys.executable, "project-[seed](../ref/glossary.md#seed){ .glossary-term }/ci/run_workflows_locally.py", "--help"],
    ...     capture_output=True, text=True, check=True).stdout
    >>> documented = {"--event", "--ref", "--base-ref", "--head-ref", "--workflows"}
    >>> actual = set(re.findall(r"^\s+(--[a-z-]+)", help_text, re.M)) - {"--help"}
    >>> sorted(actual - documented)   # a flag the tool has and this page does not
    []
    >>> sorted(documented - actual)   # a flag this page claims and the tool lacks
    []

`check=True` is not decoration. doctest reports success for an example that
raises nothing and declares no output, so without it a `--help` that exited
non-zero would pass here.

## Individual checks

You can also run the underlying checks directly:

```bash
# Record index matches the records directory; no banned vocabulary
python project-seed/ci/adr_lint.py --records-dir records --index README.md

# One open pull request per contributor
python project-seed/ci/check_one_pr.py --repo <owner/name> --contributor <login>

# The branch targets the right base and carries what you think it carries
python project-seed/ci/check_pr_base.py --base main --head <branch>

# Every file has license and copyright metadata
python -m reuse lint
```

## Reporting results

When you report a local run, say what you ran and what it said — including which steps the runner could not reproduce. A local failure can be a real defect or an environment difference; establish which before reporting it.

## Related

- [project-seed/ci/run_workflows_locally.py](https://github.com/quaternionmedia/qm/blob/main/project-seed/ci/run_workflows_locally.py) — the runner
- [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) — what CI enforces today
