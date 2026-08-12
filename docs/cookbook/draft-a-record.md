# Draft a record

Write a decision record, at the org level or the project level.

## Copy the template

```bash
# Org record (on an evolve/<slug> branch)
cp TEMPLATE.md records/DRAFT-<slug>.md

# Project record (on the project's own branch)
cp adr/TEMPLATE.md adr/DRAFT-<slug>.md
```

The file stays named `DRAFT-*.md` until a human ratifies it. Numbers are assigned at ratification, not before.

## Fill in the template

The template opens with a header table:

| Field | What it holds |
|---|---|
| **Status** | Starts at `Draft` or `Proposed` |
| **Date** | Date of the last status change |
| **Pends on** | For `Proposed`: the open question this record waits on, or "Nothing — ready for ratification" |
| **Principle** | The `PRINCIPLES.md` heading the record is cut from |

Then five sections:

1. **Context** — the situation that requires a decision
2. **Decision** — what is decided, stated so it can be enforced
3. **Consequences** — what changes as a result, good and bad
4. **Alternatives considered** — each alternative, and why it lost
5. **Revision triggers** — the conditions under which this record should be revisited

An **Amendments** section starts as "*None.*" and is only used after ratification.

## Follow the drafting rules

- **One decision per record.** If your draft contains two decisions, split it.
- **No drafting narration.** These words fail the lint in a draft record: "previously", "originally", "earlier draft", "re-review", "renumber", "retroactive". Drafts are rewritten in place, not narrated.
- **Squash before ratification.** A draft's history is not kept; the ratified record is.

The template's own comment blocks state the full rules. The lint that enforces them is `project-seed/ci/adr_lint.py`.

## Open the pull request

```bash
git add records/DRAFT-<slug>.md
git commit -m 'draft: <title>'
git push
gh pr create --draft
```

Assign the person who asked for the work. Do not request a review.

## What happens at ratification

Ratification is a human act, and only a human performs it:

1. Status flips to `Accepted`.
2. The record gets its number (`QM-NNNN` or `ADR-NNNN`) from the index.
3. The index is updated.
4. The commit message names the record.

After that, the body above the Amendments section does not change. Changes arrive as dated amendments.

## Related

- [TEMPLATE.md](https://github.com/quaternionmedia/qm/blob/main/TEMPLATE.md) — the template, with the full drafting rules
- [Ratification](../ref/ratification.md) — the ratification mechanics
- [records/DRAFT-decision-record-discipline.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-decision-record-discipline.md) — the discipline this recipe summarizes
