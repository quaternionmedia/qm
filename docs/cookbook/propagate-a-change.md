# Propagate a change

Getting an org-level update to an adopting project.

## When to propagate

A project receives org updates in two cases:

1. **A new record was ratified on `main`** — the org made a binding decision and it needs to reach projects
2. **Regular sync** — even if no records changed, periodic propagation ensures projects stay current

Propagation is a human action: someone decides "it's time" and creates the branch.

## The procedure

On the QM corpus repo (`quaternionmedia/qm`):

### Step 1: Create the propagate branch

```bash
git checkout main
git pull
git checkout -b propagate/<project-name>-<YYYY-MM-DD>
```

Use the project's name and today's date.

### Step 2: Merge main into the project's branch

```bash
git merge project/<project-name>
```

If there are conflicts, they should be minimal — `adr/` is the only place where project-specific content lives.

### Step 3: Push and open a PR

```bash
git push origin propagate/<project-name>-<YYYY-MM-DD>
gh pr create --title "propagate: <project-name> <YYYY-MM-DD>" --base project/<project-name>
```

**Note the base:** `--base project/<project-name>`, not `main`. The PR targets the project's branch, not the org.

### Step 4: Project review and merge

A human on the **project** team reviews and merges the PR into `project/<project-name>`. This bumps their submodule pointer to the new tip.

## Key rule

**Never rebase a project branch.** Always merge. The submodule pointer is pinned by ancestry, and rebasing breaks the pin.

See [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) for the full procedure with edge cases.

## Related

- [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) — the authoritative runbook with all steps
- [Architecture](../about/architecture.md) — how propagation fits the adoption-by-reference model
- [Branch namespaces](../ref/namespaces.md) — the `project/<name>` and `propagate/<name>-<date>` rules
