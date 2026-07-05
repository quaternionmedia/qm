# Perspectives — Index and Response Status

| | |
|---|---|
| **Standing** | Attributed, dated, non-binding opinion — never ratified, never binding, cited by author and date. Distinct from `records/` (doctrine, ratified) and `math/` (experiments). |
| **Scope** | Every file in this directory, including primary-source transcripts that are evidence rather than opinion (marked as such below). |
| **Attribution** | Author names the human accountable for a perspective; tool involvement, if any, is disclosed as "Tools: \<name\>" in Notes, never in Author — per `records/DRAFT-human-only-contributorship.md`. |

## Why this exists

Perspectives are the corpus's lowest-formality channel, deliberately kept
that way (see `claude-fable-5-2026-06-09_philosophy.md`'s own case for
preserving space that doesn't get forced through record-shaped process).
Low formality should not mean invisible: a perspective naming a real gap
deserves a visible outcome other than silence, without a second
ratification pipeline. This index is the whole mechanism.

## Status values

Status tracks whether a maintainer has looked at a perspective, never
whether its content is correct, resolved, or complete.

- **Unreviewed** — default for every perspective, existing and new, until a
  maintainer says otherwise.
- **Acknowledged** — a maintainer has read it; logged, no further
  commitment implied.
- **Responded** — concrete work exists because of it (a `math/` workspace,
  a `DRAFT-*` record, a proposal document), linked in the table below.
- **Declined** — a maintainer read it and decided, for a stated reason, not
  to act on it.

Setting Acknowledged, Responded, or Declined is a maintainer action. A
*fact* about linked follow-on work (the Notes column) is not the same as
setting Status and may be recorded by anyone — it's checkable independently
of judgment.

## Index

| Date | File | Author | Kind | Status | Notes (verifiable links only) |
|---|---|---|---|---|---|
| 2026-06-09 | `claude-fable-5-2026-06-09.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Fable 5 |
| 2026-06-09 | `claude-fable-5-2026-06-09_philosophy.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Fable 5 |
| 2026-06-09 | `claude-fable-5-2026-06-09-mathematical-limits.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Fable 5 (addendum: Claude Sonnet 4.6, 2026-06-11). `math/` topics 01–06 investigate this document's named holes (see `math/README.md`) |
| 2026-06-09 | `session-transcript-2026-06-09.md` | — (raw transcript) | Primary source, not an opinion | Unreviewed | Working transcript behind this repo's initial content |
| 2026-06-27 | `claude-sonnet-4-6-2026-06-27-mobile-cross-platform-governance.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 4.6; qmetronome's server-infra-assumption gap findings |
| 2026-07-04 | `claude-sonnet-5-2026-07-04-qmetronome-onramp-retrospective.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 5 |
| 2026-07-05 | `2026-07-05-on-human-only-contributorship.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 5; responds to `records/DRAFT-human-only-contributorship.md` |
