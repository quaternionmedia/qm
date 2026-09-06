# QM-XXXX — A loose end is carried or dismissed, and open is the absence of both

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-09-06 |
| **Principle** | `P11 — Governance finds the reader, not the reverse` |

## Context

This corpus generates four status documents and each is correct. Each is also
read for exactly one question, and the questions do not overlap:

| Document | Answers |
|---|---|
| `harness-status.json` | where does each repository's pull-request slot stand |
| `doc-status.json` | what state is each document in |
| `gate-status.json` | what does each automated check refuse, and what can it not see |
| `governance-status.yaml` | where does each project stand against the corpus |

A question none of them answers is **what has this organisation started and not
finished**, because the evidence for it is spread across three of them. Measured
on 2026-09-06, from the committed documents and nothing else: three stalled
threads, one of them idle 23,204 hours; one repository over its pull-request
slot; twenty-seven records awaiting a human's ratification; forty-seven
documents nobody has reviewed; and seventeen gates each declaring, in its own
`cannot_see` field, something it knows it cannot check. Ninety-five items, every
one already written down, and no reader who has seen them together.

P11 is the principle at stake and it is about exactly this shape: *a
constitution nobody encounters doesn't bind — it just exists.* A loose end
recorded in a document read for a different question is in the same position. It
is not hidden and it is not tracked.

Two constraints shape any answer. The first is that the corpus already
distinguishes **claim** from **evidence** — a claim is something a human
asserted and is never derived from artifacts; evidence is something a generator
measured, with a timestamp. The second is that a generated document is rewritten
on every run, so anything a person writes into one lasts until the next
`uv run qm docs generate`.

## Decision

**A fifth generated document, `loose-ends.json`, joins the existing three. It
measures nothing of its own, and it carries a claim layer it never writes.**

1. **The document is a join.** Every fact in it is already a fact in a document
   this corpus generates. `ci/loose_ends.py` reads three committed files,
   reaches no network, and can hold nothing its sources do not. A collector that
   took its own reading would be a second place a rule gets defined, which is
   the split `ci/harness_status.py` states between a generator and a renderer,
   applied one layer up.

2. **Claims live in `registers/loose-end-claims.yaml`, an input.** The generator
   reads it and joins it on; nothing writes it back. This is the corpus's
   claim/evidence line drawn at the only place it could hold: a decision
   recorded inside a regenerated document does not survive the next run.

3. **There are two dispositions and `open` is neither.**

   - `carried` — somebody has picked it up and is following it. The item stays
     in the document; it leaves when its subject changes, not when somebody
     says so.
   - `dismissed` — somebody read it and deliberately let it go, with the reason.
   - **`open` is the absence of a claim and has no spelling.** Writing it down
     would turn "nobody has looked at this" into "somebody decided nothing", and
     those are different facts about the same row.

   An unrecognised disposition leaves the item open rather than closing it. A
   misspelling that quietly closed a finding is the failure a register of
   decisions can least afford.

4. **An item addresses its subject, not itself.** `ci/addresses.py` closes its
   `KINDS` set on purpose, and no `loose-end` kind is added. A loose end is
   always *about* something the grammar can already name — a pull request, a
   document, a gate's page — so each item carries an address with an existing
   kind, and a view that resolves addresses can navigate from any row to the
   thing it concerns. Where an address does not parse the item is still
   reported, with `address_parses: false`, because dropping it would hide a real
   finding.

5. **Conformance is shared, not owned.** `project-seed/loose-end-vectors.json`
   holds the cases, and `python ci/loose_ends.py --vectors` runs them. Any
   consumer that renders the document runs the same file, which is how two
   readings stay honest without one importing the other — the arrangement
   `project-seed/address-vectors.json` already uses for the grammar.

## Alternatives

**A sixth field on each existing document.** Every generator marks its own
unfinished items and each dashboard grows a section. Rejected because the
question is precisely the one that spans documents: the total is the finding,
and four partial totals is the state that exists today. It would also put the
claim layer in four places, and a person's decision would then be recorded
wherever the fact happened to be measured.

**An issue tracker.** GitHub issues, one per loose end, synchronised. Rejected on
two counts. It inverts the claim/evidence split — an issue is a claim-shaped
container holding derived evidence, and it goes stale the moment the underlying
document changes, with nothing to notice. And it moves the org's standing
question into a product the corpus reaches only over a seam, which
`P3 — Seams on standard protocols` would require an exception record to justify
for a single-implementation dependency.

**Persist the dispositions in the generated document and regenerate carefully.**
Rejected because "carefully" is the whole risk. The document is regenerated by a
gate, by a fork running seed scripts in place, and by anybody typing
`uv run qm docs generate`; a claim in that file is one command from gone, and
the command is one somebody is encouraged to run.

**Do nothing, and read the three documents together when it matters.** This is
the honest status quo and it is what P11 refuses: the facts are available to a
reader who already knows to look for them, which is not the reader the principle
is about. It also has a measurable cost — ninety-five items, and no evidence
anybody has seen the number.

## Consequences

**A number exists that did not.** Ninety-five is uncomfortable and it is the
point; a total nobody can see is not a smaller total.

**The total is not a backlog.** Seventeen of the items are gates declaring what
they cannot check — gaps somebody chose and wrote down. The document says so in
its `reading.do_not` block, because a figure that reads as a burn-down invites
somebody to burn it down.

**A new source is a new collector and nothing else.** Adding one is a function in
`ci/loose_ends.py` and a kind; it needs no change to the schema, the register, or
any consumer.

**Every consumer inherits the claim rule or fails a vector.** That is the
intended teeth: the vectors are the contract, and the first case is the one that
distinguishes an unclaimed item from a dismissed one.

**The document is only as fresh as its stalest input**, which is stated in the
file rather than here. Its budget matches the harness document's 24h, because
that is the source that moves.

**What this does not decide.** Which repositories consume the document, and by
what route — vendoring the corpus or reading it over a seam. That is a question
per repository and belongs in each one's own records.
