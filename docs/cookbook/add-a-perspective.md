# Add a perspective

Write a [perspective](../ref/glossary.md#perspective){ .glossary-term }: dated, attributed, non-binding opinion.

## What a perspective is for

- **Rationale** — why something was done the way it was
- **Incidents** — what went wrong and what was learned
- **Retrospectives** — how a piece of work actually went
- **Opinion** — an argued position, signed and dated

What does *not* belong here: new rules (those are records) and procedures (those are [handbook](../ref/glossary.md#handbook){ .glossary-term } pages). See [handbook/style-guide.md](https://github.com/quaternionmedia/qm/blob/main/handbook/style-guide.md) for the routing table.

## Name the file

```
perspectives/<YYYY-MM-DD>-<slug>.md
```

Example: `2026-08-09-explanation-in-the-wrong-place.md`

## Write the header

A perspective opens with a title and a key-value table. The fields are **Standing**, **Author**, **Tools**, and **Task** (a **Date** row is optional; the index carries the citable date):

```markdown
# Perspective — <Title>

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | <Human name> |
| **Tools** | <Model name, and what it did> |
| **Task** | <One paragraph: what this perspective covers> |
```

Two rules from [records/DRAFT-human-only-contributorship.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-human-only-contributorship.md):

- **Author names a human** — the person accountable for the content, never a tool or model.
- **Tool involvement is disclosed in the Tools row**, both in the file and in the index. In this directory the disclosure is required, not optional.

## Open the pull request

Perspectives go on a `perspective/<date>-<slug>` branch:

```bash
git checkout -b perspective/<YYYY-MM-DD>-<slug>
git add perspectives/<YYYY-MM-DD>-<slug>.md
git commit -m 'perspective: <title>'
git push origin perspective/<YYYY-MM-DD>-<slug>
gh pr create --draft
```

## Update the index

Add a row to the table in [perspectives/README.md](https://github.com/quaternionmedia/qm/blob/main/perspectives/README.md): Date, File, Author, Kind, Status, and Notes. New perspectives start with Status `Unreviewed`; only a maintainer changes that. The Notes column carries the Tools disclosure and links to any follow-on work.

## Related

- [perspectives/README.md](https://github.com/quaternionmedia/qm/blob/main/perspectives/README.md) — the index and its rules
- [handbook/style-guide.md](https://github.com/quaternionmedia/qm/blob/main/handbook/style-guide.md) — what goes where
