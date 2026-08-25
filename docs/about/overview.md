# Overview

!!! info "Source of truth"
    This page is a summary. The full text is in [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) and the records in [records/](https://github.com/quaternionmedia/qm/tree/main/records). If this page and a source disagree, the source is correct.

## What QM is

The Quaternion Media constitution is a shared decision corpus. It holds the principles that govern every QM project, the process that keeps projects consistent, and the template each new project starts from.

Projects adopt the [corpus](../ref/glossary.md#corpus){ .glossary-term } **by reference**:

1. A project may add constraints on top of the corpus.
2. A project may not waive a corpus constraint. An exception requires an amendment to the corpus itself, ratified at the org level.
3. The corpus is one shared rule set, not a template that projects copy and change.

## The four artifact classes

| Artifact | Binding? | What it holds |
|---|---|---|
| **[Record](../ref/glossary.md#record){ .glossary-term }** (`records/`, `adr/`) | Yes, once `Accepted` | One decision, with context, alternatives, and consequences |
| **[Register](../ref/glossary.md#register){ .glossary-term }** (`registers/`) | Yes, as defined by the record that creates it | Living data, such as carried patches |
| **[Handbook](../ref/glossary.md#handbook){ .glossary-term }** (`handbook/`) | On QM's own conduct only | Policy and procedure |
| **[Perspective](../ref/glossary.md#perspective){ .glossary-term }** (`perspectives/`) | No | Dated, attributed opinion: incidents, retrospectives, lessons |

## The charter

[PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) states eleven principles. In brief:

1. **Ownership is the deliverable** — systems must keep working if every vendor and upstream disappears.
2. **Commons-first economics** — capability gaps are closed upstream; sponsorship is a first-class budget line.
3. **Seams on standard protocols** — third-party components connect only through protocols with multiple independent implementations.
4. **Build the [seam](../ref/glossary.md#seam){ .glossary-term }, buy the engines** — custom code goes in the small control plane; engines are selected, not written.
5. **One house stack, deeply known** — QM's own repositories use one stack; contributions use the target community's stack.
6. **Decisions are documented or they didn't happen** — a decision that lives only in a chat log is not owned by the organization.
7. **Public by default** — work ships in the open unless a specific, named reason requires otherwise.
8. **Systems over heroics** — operations are declarative, automated, and observable; nothing depends on one person's late-night effort.
9. **Minimal, legible deliverables** — legibility is respect for the reader and the future maintainer.
10. **Credit tracks accountability, not output** — authorship names people who can answer for a change, never tools.
11. **Governance finds the reader, not the reverse** — governance is placed in the files a reader already opens.

Each principle names its enforcement mechanism. Read the full charter for the reasoning.

## The records

Twelve org records are drafted and awaiting ratification. Every one is marked `Proposed`, because [ratification](../ref/glossary.md#ratification){ .glossary-term } requires a second active code owner. The [records index](https://github.com/quaternionmedia/qm/blob/main/README.md#index--org-records) links to each record.

## Related

- [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) — the full charter
- [Architecture](architecture.md) — how the principles shape the repository structure
- [Record precedence](../ref/precedence.md) — how records bind projects
