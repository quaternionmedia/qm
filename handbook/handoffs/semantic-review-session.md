# Session Instruction — Reviewing the Records

**Read [`semantic-review-of-the-records.md`](semantic-review-of-the-records.md)
first.** That page says why the review matters and what order to read in. This
one is the method: the same questions, in the same order, for every record, so
sixteen readings are comparable.

**This is a prompting sequence, not a form.** If a question does not apply,
write why. `not applicable` is an answer; a blank is a gap.

---

## Before the first record

Write the header, once:

```yaml
schema: 1
reviewer: <your name>
started: <date>
corpus_commit: <sha you are reading at>
records: []
```

Then answer these two, in prose, before reading anything:

> **What do you expect to find?** Name it now. The ledger's own evidence is that
> a projection written afterwards is not a projection, and a review that
> confirms an unstated expectation cannot be distinguished from one that
> invented it.
>
> **What would make you stop and ask rather than record a verdict?** Decide the
> threshold before you meet it.

## For each record, in dependency order

The order is in the other page. Do not read alphabetically — records inherit
from each other and reading out of order re-derives the same argument.

### 1. Read it whole, once, without notes

No annotation on the first pass. The corpus's recurring failure is reading a
proxy instead of the thing, and note-taking on a first pass turns a record into
the notes about it.

### 2. Then answer, in this order

> **What does this record bind that no other record binds?**
> One sentence. If you cannot write it, that is the finding — say so.
>
> **Does it contradict another record?**
> Both citations, or `[]`. Zero across all sixteen is surprising, not
> reassuring: one record/entry-point contradiction has already been found here.
>
> **`uv run qm review` flagged universals in Decision clauses. For each: requirement or claim?**
> This corpus writes requirements declaratively, so no pattern separates them.
> Deciding is the job the check cannot do.
>
> **Which clause would you delete?**
> Name one, or say why none. Nothing has ever been deleted from a record here,
> which is either discipline or accumulation, and nobody has checked which.
>
> **Does it name a mechanism that exists?**
> `records/DRAFT-version-tags-are-claims.md` §7 claimed to be mechanical for six
> days while nothing read a tag.
>
> **Could a project satisfy this today?**
> Read at least two records from `qmcp`'s position: no licence, no `REUSE.toml`,
> no test workflow. A requirement no real repository can meet is a finding about
> the record.
>
> **Verdict, and how confident.**
> `ratify | amend | merge-with | split | delete | defer`, one sentence, and
> `high | medium | low`. Low confidence recorded is worth more than high
> confidence assumed.

### 3. Write the entry before opening the next record

Schema in [`plans/semantic-review-instrument.md`](../../plans/semantic-review-instrument.md).
Writing it later is reconstruction, and reconstruction is the failure the ledger
exists to prevent.

## When to stop and ask rather than continue

- **Two records contradict.** Do not pick a winner alone. Precedence says which
  document wins; it does not say which decision the organisation meant.
- **A record is unsatisfiable for a real project.** That may be the record, or it
  may be the project, and the answer is not in the record.
- **You would delete something load-bearing.** Deleting a clause is a governance
  change wearing an editorial hat.
- **You have written `ratify` five times in a row.** Not necessarily wrong.
  Worth a pause.

## After the sixteenth

**Write the perspective.** Not a record — this is a reading, and a reading is
opinion until the organisation acts on it. `perspectives/README.md` has the
conventions.

It must state, whatever else it says:

- what you expected before starting, and whether you found it
- every contradiction, with both citations
- which record you would ratify **first**, and why it is the cheapest rehearsal
  of a five-step path nobody has walked
- what you did not do, and what a second reader should check

Then set `semantic-review-done` against the milestone in `ci/workspace.yaml` —
by saying so, because nothing can measure it. That is the point of it being the
one requirement on the list that is not mechanisable.

## What is not yours

Ratifying. Rewriting a record to match your reading before the reading is
written down. Deleting a record without a pull request that argues for it.
Recording a verdict on a record you did not read whole.
