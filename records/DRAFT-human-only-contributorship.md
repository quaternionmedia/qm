# QM-XXXX — Human-Only Contributorship

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-05 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P10 — credit tracks accountability, not output |

## Context

Contributor and author fields across the corpus currently mix two different
kinds of party without saying so. `perspectives/README.md`'s Index table
lists "Claude Fable 5" and "Claude Sonnet 5" in the same Author column a
human name would occupy. Separately, default assistant tooling commonly
appends a `Co-Authored-By: <model> <noreply@vendor.tld>` trailer to commits —
an address nobody reads, standing in the same field a human's monitored
address would.

A contributor is a party who can be asked why a change was made, held to a
commitment made in review, and reached at a real address if something breaks.
A model name or an unmonitored `noreply@` address cannot do any of that —
crediting it as author doesn't honor a contribution, it just launders an
unanswerable field into looking answerable. This is not a claim that tools
add no value; a tractor's work shows up in the yield, a calculator's in the
arithmetic, an LLM's in the diff. None of them are the party accountable for
the result, and accountability, not effort or output volume, is what the
author/contributor field exists to record.

## Decision

1. **Contributor and author fields — commit authorship and co-authorship,
   perspective bylines, CREDITS-style recognition — name human actors only.**
   A contributor is someone who can be asked why, and reached to answer.
2. **Tool involvement is recorded, not credited.** A project or record may
   keep a Tools/Notes annotation — naming software, models, or hardware
   substantially involved in producing an artifact, for provenance and
   reproducibility — kept visibly separate from, and never substituting for,
   the human byline. The human who ran the tool is the contributor of record
   regardless of how much of the output the tool produced.
3. **No commit trailer, author field, or byline may name an address that is
   not a monitored inbox reachable to a human accountable for the content.**
   This bans co-author trailers pointing at model-vendor `noreply@` addresses
   or similar unmonitored addresses, whether added by default tooling or by
   hand. Naming a human is always fine, including a human who works at or
   through a tool vendor; the ban is on unreachable addresses standing in for
   accountability, not on disclosing that a tool was used.
4. This governs attribution metadata — commit trailers, bylines, index
   entries, and each perspective file's own header table and closing
   signature. Existing commits are not amended; commit history is left
   alone. Perspectives are different: they carry no ratification gate (see
   Standing in `perspectives/README.md`), so their non-conforming Author
   fields — the `perspectives/README.md` index, and the individual header
   table, byline, and signature line inside each affected file — are
   migrated on their own schedule rather than waiting on this record's own
   ratification. Migrating them is a metadata correction (who is named as
   accountable), not a rewrite of a perspective's substance, so it carries
   none of the append-only weight a ratified record's body would.

## Consequences

- CI/PR review gains a check: a commit trailer, or a new perspective/record
  byline, naming a non-monitored address or a tool/model as author fails
  review.
- `perspectives/README.md`'s index schema gains a Tools/Notes annotation
  distinct from Author; its existing entries crediting model names, plus the
  affected files' own header tables and closing signatures, were migrated to
  a named human sponsor directly (see that directory's own history) rather
  than held pending this record's ratification.
- Default assistant commit tooling that appends a
  `Co-Authored-By: <model> <noreply@...>` trailer must be suppressed or
  overridden for qm and any project adopting this record — stated, for now,
  as an explicit instruction to drafting sessions rather than a mechanical
  check. That is a known soft spot, not a design choice: this corpus's own
  decision-record-discipline record rejected "convention without
  enforcement" as insufficient in a different context, and the same
  argument applies here until a commit-msg hook or CI grep exists to back
  the instruction up.
- Cost accepted: some provenance detail (exactly which model or version
  produced a given diff) moves from a prominent commit trailer to a
  lower-visibility Tools note. The org has decided that the signer being
  reachable matters more than that granularity being load-bearing.

## Alternatives considered

1. **A distinct non-authorial trailer for tools (e.g. `Generated-by:`)** —
   folded in as the Tools/Notes mechanism in §2, but rejected as the sole
   fix: it still invites new byline-adjacent fields for tools when the actual
   objection is that an unmonitored address represents nobody who can answer,
   not that the field was labeled "author."
2. **Ban tool use in drafting or code entirely** — rejected: the objection is
   unreachable credit, not tool use itself; the org's own drafting process
   runs through assistants throughout.
3. **Credit tools that "meaningfully contributed," leave the line to
   judgment** — rejected: no stable line separates a keyboard from a linter
   from an LLM by "meaningful contribution"; the only line that holds is
   whether the named party can be asked why and can answer.

## Revision triggers

- A tool becomes a legally recognized author in a jurisdiction QM operates
  in — would force reconciling this record with law, not just house style.
- The Tools/Notes annotation is used to smuggle credit back in, or becomes
  contentious in review — the record needs a firmer format, not repeated
  exceptions.
- The instruction-only commit-trailer ban is missed by a new contributor or
  a fresh drafting session — the point at which "stated instruction" needs
  to become a mechanical check (commit-msg hook or CI grep) rather than
  staying an accepted gap.

## Amendments

*None.*
