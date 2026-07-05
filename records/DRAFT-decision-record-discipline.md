# QM-XXXX — Decision-Record Discipline

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-09 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P6 — decisions are documented or they didn't happen |

## Context

Decision documents drift in predictable ways: drafts accumulate references to
their own revision history, numbers get assigned before ratification and then
"renumber," supersession language leaks into documents never published. Drift
of this kind was observed and corrected in the org's first drafting round; the
discipline below makes prevention mechanical rather than memorial.

## Decision

1. Every QM project carries an `adr/` directory instantiated from the
   constitution's `project-seed/` — process contract, template, and CI lint —
   at project creation. A project without it is improvised, not instantiated.
2. The discipline at both levels is: **before ratification, documents have no
   memory; after ratification, they have nothing but memory.** Drafts are
   numberless, referenced by title, rewritten whole when positions change.
   Accepted records are append-only (dated Amendments); reversals are new
   records that supersede; numbers are assigned at ratification by the index,
   are permanent, and are never reused.
3. Ratification is a human commit. Assistants and contributors draft; a human
   flips status, assigns the number, updates the index, and names the record
   in the commit message.
4. Drafting sessions (human or AI-assisted) receive the process contract, the
   constitution, and the current index as inputs, and present a plan with a
   contradiction check before writing.

## Consequences

- CI lint in every repo rejects: banned vocabulary in drafts
  (`previously|originally|earlier draft|re-review|renumber|retroactive|
  supersedes the ... (stance|finding)|corrected`), numbered filenames not
  Accepted+, edits to an Accepted record outside its Amendments region,
  index/directory mismatches.
- Onboarding cost for contributors and assistants is the process contract —
  one page, supplied with every drafting session.
- Cost accepted: ceremony on small decisions. Mitigation: one-decision
  records can be short; brevity is compliant, absence is not.

## Alternatives considered

1. **Convention without enforcement** — rejected: the observed drift occurred
   *during* an attentive, two-party drafting round; unenforced convention
   does not survive contributor turnover.
2. **Full RFC process** — rejected as ceremony disproportionate to org size;
   records + lint capture the value at a fraction of the weight.

## Revision triggers

- The lint produces sustained false positives (vocabulary rules need tuning).
- A second governance artifact class emerges (e.g., runbooks) needing its own
  lifecycle — revisit whether this record generalizes or a sibling is needed.

## Amendments

*None.*
