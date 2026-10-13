# Plan — An instrument for reviewing 16 records consistently

**Status: stub for the tooling. The method and schema below are usable now, by
hand, and should be before anything is built.**

## The problem this solves

Sixteen records, read once, by one or more people, possibly across sessions. Read
freely, sixteen readings produce sixteen shapes: some catch contradictions, some
catch staleness, some produce a verdict and some do not. Nothing aggregates and
nobody can tell whether record 14 was read as carefully as record 1.

The corpus already has the failure written down: `handbook/handoffs/semantic-review-of-the-records.md`
names the four things to look for, and names nothing about how to record them.

## The shape, decided 2026-08-16

**Structured per record, then prose.** One entry per record, machine-readable, so
sixteen readings are comparable and the aggregate is countable. Then one
perspective drawing conclusions no schema can hold.

The split is the point: the structured half makes coverage checkable, the prose
half makes the reading worth having. Neither substitutes.

## The schema

Proposed for `review/semantic-2026-08.yaml`. Not yet written, not yet checked.

```yaml
schema: 1
reviewer: <a human>
started: <date>
records:
  - record: records/DRAFT-house-stack.md
    read_at_commit: <sha>

    # What this record uniquely binds. If two records answer this the same way,
    # one of them is redundant -- which is a finding.
    binds: "which components QM builds versus buys"

    # Named contradictions, each with both citations. Empty is a real answer.
    contradicts:
      - other: records/DRAFT-seams-on-standard-protocols.md
        where: "§3 here vs §2 there"
        summary: "..."

    # Universals `qm review` flagged, each resolved by a human.
    universals:
      - clause: "§2"
        verdict: requirement | claim
        note: "..."

    # Clauses that could go, with why. The corpus has never deleted one.
    clauses_to_cut: []

    # Mechanisms named that no longer exist or never did.
    stale_mechanisms: []

    verdict: ratify | amend | merge-with | split | delete | defer
    verdict_note: "one sentence"

    # Deliberately last. A low-confidence reading is worth recording as one.
    reviewer_confidence: high | medium | low
```

**Open:** whether `verdict` should exist at all before ratification is possible.
A verdict nobody can act on may just be pressure.

## The rigor questions, and the honest answer

- **How is a reading known to be careful?** It is not. Confidence is
  self-reported and that is a weakness, not a design.
- **What stops sixteen `verdict: ratify` from a tired reader?** Nothing
  mechanical. `contradicts: []` across all sixteen is the signal to distrust —
  the corpus has already found one record/entry-point contradiction, so zero
  between sixteen records is surprising rather than reassuring.
- **What if two people disagree?** Two entries, both kept. The schema has one
  `reviewer` per file for that reason.

## What could be built later, and should not be yet

`uv run qm review start` — walking a reviewer through the question set, writing
the YAML, resuming where it stopped. Worth building **after** one review has been
done by hand, because a tool built first would encode a method nobody has tried.

**Open:** does an interactive prompt help, or does it turn reading into
form-filling? The corpus's own evidence is that structure catches omissions and
that it also invites minimum-viable answers.

## Decisions nobody has made

1. One file per reviewer, or one per review round?
2. Does a record with no verdict block the milestone requirement, or is
   `defer` a legitimate end state for all sixteen?
3. Who reconciles two reviewers' entries, and does that reconciliation get
   recorded as a third?
4. Is `reviewer_confidence` load-bearing or decorative?
