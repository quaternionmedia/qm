# Propagate a change

Carry an org-level change from `main` to an adopting project's branch.

!!! info "Authoritative source"
    The full runbook, including conflict handling, is [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md). This page covers the common case.

## When to propagate

- A [record](../ref/glossary.md#record){ .glossary-term } was ratified on `main` and projects need it.
- A project's branch has fallen behind and should catch up.

[Propagation](../ref/glossary.md#propagation){ .glossary-term } is a human decision. Nothing triggers it automatically.

## The procedure

Always use an intermediate `propagate/<name>-<date>` branch. Cut it **from the project's branch**, then merge `main` **into it**:

```bash
git checkout -b propagate/<name>-<YYYY-MM-DD> origin/project/<name>
git merge origin/main
# resolve any conflicts here
git push origin propagate/<name>-<YYYY-MM-DD>
```

Then open a pull request:

- **base:** `project/<name>`
- **head:** `propagate/<name>-<YYYY-MM-DD>`

```bash
gh pr create --draft --base project/<name> \
  --title "propagate: <name> <YYYY-MM-DD>"
```

A human reviews and merges — with a merge commit, not a squash and not a rebase. The merge commit is the new submodule pin: the branch's ancestry is the pin, so there is no hash to maintain by hand.

## Rules

- **Never rebase a project branch.** A downstream submodule pins its tip; a rebase breaks every pin.
- **Never use `main` directly as the head.** Always cut the intermediate branch, even when the merge is clean.
- **The pull request base is the project branch, not `main`.** `project-seed/ci/check_pr_base.py` refuses the wrong direction.

## Related

- [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md) — the full runbook
- [Branch namespaces](../ref/namespaces.md) — why the branches work this way
- [Architecture](../about/architecture.md) — the model behind propagation
