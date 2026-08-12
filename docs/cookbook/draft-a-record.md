# Draft a record

Writing a decision record at the org or project level.

## Get the template

Copy [TEMPLATE.md](https://github.com/quaternionmedia/qm/blob/main/TEMPLATE.md) (org) or `adr/TEMPLATE.md` (project):

```bash
# Org-level (on evolve/<slug> branch)
cp TEMPLATE.md records/DRAFT-<what-you-decided>.md

# Project-level (on your project branch)
cp adr/TEMPLATE.md adr/DRAFT-<what-you-decided>.md
```

## Fill in the sections

The template has required sections:

- **Status** — start as `Proposed` (no number yet)
- **Context** — what decision needed to be made and why
- **Decision** — what you decided
- **Alternatives considered** — what else you thought about
- **Consequences** — what changes as a result

See [TEMPLATE.md](https://github.com/quaternionmedia/qm/blob/main/TEMPLATE.md) for the full structure and what each section means.

## Follow the drafting discipline

Before opening a PR:

- **One decision per file** — if your decision has two parts, split them
- **No banned vocabulary** — grep for `previously`, `originally`, `earlier draft` etc. (see `project-seed/ci/adr_lint.py` for the full list)
- **Squash before review** — keep the file's git history clean before you open the PR

See [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) section on discipline for what's checked and what's still manual.

## Open a draft PR

```bash
git add records/DRAFT-*.md  # or adr/DRAFT-*.md for a project
git commit -m 'draft: <title>'
git push origin evolve/<slug>
gh pr create --draft
```

Assign it to yourself or the person who asked for the work. A human reviews the record.

## After review

A human may ask for changes (the record is still `Proposed` and editable). Once approved, a human ratifies it:

1. Flips Status to `Accepted`
2. Assigns a number (`QM-NNNN` for org; `ADR-NNNN` for project)
3. Updates the index (`README.md` for org; `adr/README.md` for project)
4. Makes a commit naming the record in the message

The number is not assigned until this moment.

## Related

- [TEMPLATE.md](https://github.com/quaternionmedia/qm/blob/main/TEMPLATE.md) — the template and its sections
- [Record precedence](../ref/precedence.md) — org vs. project records
- [Ratification](../ref/ratification.md) — moving from `Proposed` to `Accepted`
- [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) — what discipline is enforced
- [records/DRAFT-decision-record-discipline.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-decision-record-discipline.md) — the full discipline record
