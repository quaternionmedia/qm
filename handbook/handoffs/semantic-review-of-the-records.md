# Handoff — The Semantic Review of the Records

**Goal.** Read every record in one sitting, as one body, and find what no
check can: two records that contradict each other, a requirement that is wrong,
a universal phrased as a requirement, a decision the corpus has outgrown.

**Why it comes before the alpha.** People who did not build this corpus are
about to read it. `records/DRAFT-governance-arrives-as-a-mechanism.md` §6 is
explicit that the structural checks report structure and a human reads for
sense, and `ci/workspace.yaml`'s milestone block names `semantic-review-done`
as the one requirement that **cannot be measured**. Nothing will tell you it is
finished except your own statement that it is.

Read `handbook/handoffs/README.md` first for the rules that apply to all of
these. This page is the brief and the method: why, in what order, and the same
questions for every record so that every reading is comparable.

*Stamped 2026-08-14, on `evolve/governance-loop-poc`. Every figure below was
true at that commit. Re-derive with the commands in the next section rather
than quoting this page.*

---

## Start by running the structural pass, so you are not doing its job

```sh
uv run qm review            # every record as one body: enforcement, cites, reach
uv run qm docs states       # every document's state, and where the corpus stands
uv run qm gates             # what governs, and what each gate cannot see
```

`qm review` reports structural findings of two kinds,
`universal-to-read-by-hand` and `enforced-but-does-not-say-so`. Those are the
*candidates*. At the stamp it found no dangling citation and no unreachable
record.

**Do not treat its output as the review.** It cannot read a record for meaning,
cannot compare two records, and says so on every run. Its whole purpose is to
make your sitting shorter by handing you the mechanical half already done.

## The order, and why it is this order

Records are not independent. Read them in dependency order or you will re-derive
the same argument several times.

1. **`DRAFT-decision-record-discipline.md`** — governs how every other record is
   written. If it is wrong, everything downstream inherits it.
2. **`DRAFT-the-read-document-governs.md`** and
   **`DRAFT-governance-arrives-as-a-mechanism.md`** — both about how governance
   reaches a reader. **Read them against each other first.** Whether they are
   one decision or two is a real question and nobody has asked it.
3. **`DRAFT-version-tags-are-claims.md`** — the human gate on releases.
   Everything about readiness depends on it being right.
4. **`DRAFT-human-only-contributorship.md`** — interacts with the
   `commit-signatures` gate and with a second code owner arriving.
5. **`DRAFT-outbound-licensing.md`** and
   **`DRAFT-open-license-exclusion-and-upstream-remediation.md`** — read as a
   pair; they overlap and one amends the other's scope.
6. The rest in any order.

## What to look for, in rough order of cost-if-missed

**Two records that contradict.** The failure this corpus has already had, once,
between a record and an entry point — `AGENTS.md` said a pull request was opened
"for human review" while the version-tags record said `main` asserts nothing.
Nobody has checked whether two *records* do the same thing to each other.

**A universal that is a claim.** `qm review` hands you candidates. This corpus
writes requirements declaratively — *"Tags are annotated, never lightweight"* is
a rule in the same grammar as *"Every QM repository is REUSE-compliant"* was a
false claim. No pattern separates them; you have to decide each one. §12 of the
licensing record is the worked example, already repaired, and the DCO clause in
the same record is deliberately left for you.

**A decision the corpus has outgrown.** Several records predate the two-gate
correction, the CLI, and the gate registry. A record that assumes a human
reviews pull requests, or that names a mechanism now superseded, is stale in a
way no check sees.

**A requirement no project could satisfy.** Read at least two records from the
position of `qmcp`, which has no licence. If a record is unsatisfiable for a real
repository, that is a finding about the record.

**A record that should not exist.** Merging two, or deleting one, is a
legitimate outcome and cheaper now than after ratification.

## The method, for every record

**This is a prompting sequence, not a form.** If a question does not apply,
write why. `not applicable` is an answer; a blank is a gap.

### Before the first record

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

### For each record, in the order above

**1. Read it whole, once, without notes.** The corpus's recurring failure is
reading a proxy instead of the thing, and note-taking on a first pass turns a
record into the notes about it.

**2. Then answer, in this order.**

> **What does this record bind that no other record binds?**
> One sentence. If you cannot write it, that is the finding — say so.
>
> **Does it contradict another record?**
> Both citations, or `[]`. Zero across every record is surprising, not
> reassuring: one record/entry-point contradiction has already been found here.
>
> **`uv run qm review` flagged universals in Decision clauses. For each: requirement or claim?**
> This corpus writes requirements declaratively, so no pattern separates them.
> Deciding is the job the check cannot do.
>
> **Which clause would you delete?**
> Name one, or say why none.
>
> **Does it name a mechanism that exists?**
> `records/DRAFT-version-tags-are-claims.md` §7 claimed to be mechanical for six
> days while nothing read a tag.
>
> **Could a project satisfy this today?**
> A requirement no real repository can meet is a finding about the record.
>
> **Verdict, and how confident.**
> `ratify | amend | merge-with | split | delete | defer`, one sentence, and
> `high | medium | low`. Low confidence recorded is worth more than high
> confidence assumed.

**3. Write the entry before opening the next record.** Schema in
[`plans/semantic-review-instrument.md`](../../plans/semantic-review-instrument.md).
Writing it later is reconstruction, and reconstruction is the failure the ledger
exists to prevent.

### When to stop and ask rather than continue

- **Two records contradict.** Do not pick a winner alone. Precedence says which
  document wins; it does not say which decision the organisation meant.
- **A record is unsatisfiable for a real project.** That may be the record, or it
  may be the project, and the answer is not in the record.
- **You would delete something load-bearing.** Deleting a clause is a governance
  change wearing an editorial hat.
- **You have written `ratify` five times in a row.** Not necessarily wrong.
  Worth a pause.

## What to produce

**A perspective**, not a record — this is a reading, and readings are opinion
until the organisation acts on them. Name it
`perspectives/2026-MM-DD-the-first-semantic-review.md`, index it in
`perspectives/README.md`, and state plainly:

- what you expected before starting, and whether you found it
- which records you read, and in what order
- every contradiction found, with both citations
- for each universal `qm review` flagged: requirement, or claim?
- which records you would merge, split or delete, and why
- **which record you would ratify first**, and what makes it the cheapest
  rehearsal of a five-step path nobody has walked
- what you did not do, and what a second reader should check

Then, separately, whichever repairs are small enough to make in the same branch.
A record that needs a structural rewrite gets its own pull request and its own
argument. Then set `semantic-review-done` against the milestone in
`ci/workspace.yaml` — by saying so, because nothing can measure it.

## The ratification rehearsal, which this unblocks

Ratification has never been performed in this corpus. The path is five steps and
step 3 renames `DRAFT-<slug>.md` to `QM-NNNN-<slug>.md`, enforced by a regex
nobody has ever hit. `ci/doc_status.py` reports a filename-versus-Status
disagreement the moment step 2 happens without step 3, so the rehearsal has a
witness.

**Do one.** Find out what breaks with a single cheap self-contained record,
rather than once per record. That is `ratification-rehearsed` in the milestone
block, and it is the requirement most likely to surprise.

## What is not yours here

Ratifying anything — that is a human act and needs the second code owner.
Rewriting another record to match your reading before the reading is written
down. Deleting a record without a pull request that argues for it. Recording a
verdict on a record you did not read whole. Adding a clause:
`DRAFT-governance-arrives-as-a-mechanism.md` §5 says converting beats adding,
and this corpus has measured twice that a clause without a mechanism does not
change behaviour.
