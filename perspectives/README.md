# Perspectives — Index and Response Status

| | |
|---|---|
| **Standing** | Attributed, dated, non-binding opinion — never ratified, never binding, cited by author and date. Distinct from `records/` (doctrine, ratified) and the `workspace/math-experiments` branch (experiments). |
| **Scope** | Every file in this directory, including primary-source transcripts that are evidence rather than opinion (marked as such below). |
| **Attribution** | Author names the human accountable for a perspective, never a tool or model — the binding half of `records/DRAFT-human-only-contributorship.md`. Tool involvement is disclosed as "Tools: \<name\>", in the file's own header and in this index's Notes column. That record permits the annotation rather than requiring it; this directory requires it, which is a tightening and is stated here so it is not mistaken for the record's own wording. |

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

**When Status gets looked at.** A ladder with no trigger produces its default
forever, which is what happened here: every row read `Unreviewed` while at
least one plainly met the `Responded` bar. So: a maintainer passes over this
table when a perspective is added, and again whenever an org record ratifies,
since a ratification is the most likely thing to have turned an opinion into
Responded. Neither is a deadline. `Unreviewed` on an old row is a fact about
maintainer attention rather than a fault in the perspective, and the column
exists to make that visible rather than to be cleared.

## Index

**Date** is this table's own field and is the citable date for a perspective,
since most headers carry Standing/Author/Tools/Task and no date of their own.
Where a file *does* carry a date — in a header row, or in its closing
signature — the two agree, and the file wins if they ever stop agreeing. Do
not read the date off the filename: the session transcript is named for
2026-06-09 and its header records creation on 2026-05-26.

**Notes** carries the `Tools:` annotation the Attribution row requires, plus
links to follow-on work where any exists. A claim in this column is checkable
against something, or it does not belong here.


| Date | File | Author | Kind | Status | Notes |
|---|---|---|---|---|---|
| 2026-05-26 | `session-transcript-2026-06-09.md` | — (raw transcript) | Primary source, not an opinion | Unreviewed | Working transcript behind this repo's initial content; created 2026-05-26, last updated 2026-06-10, filename reflects neither |
| 2026-06-09 | `claude-fable-5-2026-06-09.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Fable 5 |
| 2026-06-09 | `claude-fable-5-2026-06-09_philosophy.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Fable 5 |
| 2026-06-09 | `claude-fable-5-2026-06-09-mathematical-limits.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Fable 5 (addendum: Claude Sonnet 4.6, 2026-06-11). the `workspace/math-experiments` branch investigates this document's named holes (see its `math/README.md`) |
| 2026-06-27 | `claude-sonnet-4-6-2026-06-27-mobile-cross-platform-governance.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 4.6; qmetronome's server-infra-assumption gap findings |
| 2026-07-04 | `claude-sonnet-5-2026-07-04-qmetronome-onramp-retrospective.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 5. Facts, no Status implied: its §3 proposals 1, 2, 3 and 5 have corresponding text in the corpus today — `records/DRAFT-house-stack.md`'s "client- or platform-mandated" carve-out, `project-seed/ci/`, this file's Status values, and `README.md`'s first-project-of-a-new-class paragraph. Proposal 4 (a non-container license-gate pattern) is extended by `records/DRAFT-open-license-exclusion-and-upstream-remediation.md` §4 and has a worked instance in alfred's license-report workflow |
| 2026-07-05 | `2026-07-05-on-human-only-contributorship.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 5; responds to `records/DRAFT-human-only-contributorship.md` |
| 2026-07-08 | `claude-sonnet-5-2026-07-08-mobile-timing-precision-perspective.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 5; `docs/timing-accuracy-benchmark.md` (qmetronome repo) is the companion measured-target doc this perspective argues for |
| 2026-07-09 | `claude-sonnet-5-2026-07-09-first-beat-timing-retrospective.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 5; process retrospective on the same investigation the 2026-07-08 perspective covers technically |
| 2026-07-18 | `claude-sonnet-5-2026-07-18-test-timeout-halting-problem-retrospective.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 5; process retrospective on an unbounded-test-watching incident. `adr/DRAFT-enforced-test-timeouts.md` on `project/qmetronome` is the concrete response it discusses |
| 2026-07-21 | `2026-07-21-verify-before-fixing.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Sonnet 5; companion to codecartographer's `adr/DRAFT-verify-actual-consumption-before-editing.md` (project/codecartographer branch) |
| 2026-08-07 | `2026-08-07-alfred-brownfield-adoption.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Opus 5; first adoption by a project predating the corpus. Its §3 proposals 1–5 are drafted on the `evolve/from-alfred` branch; 6 and 7 are not |
| 2026-08-07 | `2026-08-07-verification-discipline-in-assisted-sessions.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Opus 5; self-audit of 17 false assumptions from the same session, none of which were caught by review. Its §4 proposals are drafted on `evolve/from-alfred` as `records/DRAFT-decision-record-discipline.md` §7 and the seed's verification obligations |
| 2026-08-08 | `2026-08-08-hardware-onramp-invisible-artifacts.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Opus 5; first hardware-project onramp; all five proposals of `claude-sonnet-5-2026-07-04-qmetronome-onramp-retrospective.md` verified landed in `5a7d34a`/`d1b8afc`; companion to the five drafts on the `project/datum` branch |
| 2026-08-08 | `2026-08-08-a-board-is-an-engine-you-sell.md` | Peter Kagstrom | Perspective | Unreviewed | Tools: Claude Opus 5; argues openness in physical products is reproducibility, and tests `records/DRAFT-build-the-seam-buy-the-engines.md` from the seller's side; proposes amendments to that record and to `records/DRAFT-seams-on-standard-protocols.md` |
