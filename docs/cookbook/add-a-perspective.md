# Add a perspective

Writing a perspective: attributed opinion, incident report, or process retrospective.

## What goes in perspectives

Perspectives are the place for:

- **Rationale** — why a design decision was made, what alternatives were weighed
- **Incidents** — what went wrong, what was learned
- **Process retrospectives** — how an activity played out, what could improve
- **Dated opinion** — "here's what I think about this situation"

**What doesn't belong**: new rules (those go in records), procedure steps (those go in handbook), code comments (use records instead).

See [handbook/style-guide.md](https://github.com/quaternionmedia/qm/blob/main/handbook/style-guide.md) for the complete tier table.

## File naming

Perspectives are dated and named by author:

```
perspectives/<YYYY-MM-DD>-<slug>.md
```

Example: `2026-08-09-explanation-in-the-wrong-place.md`

## File structure

Start with a header naming the author and tools used:

```markdown
---
Author: Your Name
Date: YYYY-MM-DD
Tools: Claude Sonnet 5
---

# <Title>

<Content>
```

The Tools field is **required if a language model was involved**, per [records/DRAFT-human-only-contributorship.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-human-only-contributorship.md). Omit it if it was purely human work.

## Open a draft PR

Perspectives go on a `perspective/<date>-<slug>` branch:

```bash
git checkout -b perspective/YYYY-MM-DD-<slug>
git add perspectives/<YYYY-MM-DD>-<slug>.md
git commit -m 'perspective: <title>'
git push origin perspective/YYYY-MM-DD-<slug>
gh pr create --draft
```

## After the PR merges

Once merged to `main`, add a row to [perspectives/README.md](https://github.com/quaternionmedia/qm/blob/main/perspectives/README.md) with:

- Date (from your filename)
- File (the markdown filename)
- Author (your name)
- Kind (Perspective, Primary source, etc.)
- Status (Unreviewed, Acknowledged, Responded, Declined)
- Notes (any follow-on work this perspective triggered)

A maintainer will set the Status when they review the index. You can fill in Notes if there's follow-on work.

## Related

- [perspectives/README.md](https://github.com/quaternionmedia/qm/blob/main/perspectives/README.md) — the index, standing, and attribution rules
- [handbook/style-guide.md](https://github.com/quaternionmedia/qm/blob/main/handbook/style-guide.md) — the tier table: where explanation goes
- [records/DRAFT-human-only-contributorship.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-human-only-contributorship.md) — the rule on tool attribution
