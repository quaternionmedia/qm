# Handoff — The Semantic Review of the Records

**Goal.** Read all fifteen records in one sitting, as one body, and find what no
check can: two records that contradict each other, a requirement that is wrong,
a universal phrased as a requirement, a decision the corpus has outgrown.

**Why it comes before the alpha.** People who did not build this corpus are
about to read it. `records/DRAFT-governance-arrives-as-a-mechanism.md` §6 is
explicit that the structural checks report structure and a human reads for
sense, and `ci/workspace.yaml`'s milestone block names `semantic-review-done`
as the one requirement that **cannot be measured**. Nothing will tell you it is
finished except your own statement that it is.

Read `handbook/handoffs/README.md` first for the rules that apply to all of
these, and [`two-gate-and-tag-teeth.md`](two-gate-and-tag-teeth.md) second — it
corrects the model several older pages still describe.

*Stamped 2026-08-14, on `evolve/governance-loop-poc`. Every figure below was
true at that commit. Re-derive with the commands in the next section rather
than quoting this page.*

---

## Start by running the structural pass, so you are not doing its job

```sh
uv run qm review            # 15 records as one body: enforcement, cites, reach
uv run qm docs states       # every document's state, and where the corpus stands
uv run qm gates             # what governs, and what each gate cannot see
```

`qm review` reported **14 structural findings** at the stamp: 11
`universal-to-read-by-hand` and 3 `enforced-but-does-not-say-so`. Those are the
*candidates*. It found no dangling citation and no unreachable record, and five
records came back with nothing at all.

**Do not treat its output as the review.** It cannot read a record for meaning,
cannot compare two records, and says so on every run. Its whole purpose is to
make your sitting shorter by handing you the mechanical half already done.

## The order, and why it is this order

Records are not independent. Read them in dependency order or you will re-derive
the same argument four times.

1. **`DRAFT-decision-record-discipline.md`** — governs how every other record is
   written. If it is wrong, everything downstream inherits it.
2. **`DRAFT-the-read-document-governs.md`** and
   **`DRAFT-governance-arrives-as-a-mechanism.md`** — the two written this week,
   both about how governance reaches a reader. **Read them against each other
   first.** They were drafted three hours apart by one session; whether they are
   one decision or two is a real question and nobody has asked it.
3. **`DRAFT-version-tags-are-claims.md`** — now the only human gate on releases.
   Everything about readiness depends on it being right.
4. **`DRAFT-human-only-contributorship.md`** — interacts with the unbuilt
   `commit-signatures` gate and with a second code owner arriving.
5. **`DRAFT-outbound-licensing.md`** and
   **`DRAFT-open-license-exclusion-and-upstream-remediation.md`** — read as a
   pair; they overlap and one amends the other's scope.
6. The rest in any order: house stack, seams, build-the-seam, contribution and
   sponsorship, phase ladder, monitoring seam, IDE discovery, one executable
   walkthrough.

## What to look for, in rough order of cost-if-missed

**Two records that contradict.** The failure this corpus has already had, once,
between a record and an entry point — `AGENTS.md` said a pull request was opened
"for human review" while the version-tags record said `main` asserts nothing.
Nobody has checked whether two *records* do the same thing to each other.

**A universal that is a claim.** `qm review` hands you eleven candidates. This
corpus writes requirements declaratively — *"Tags are annotated, never
lightweight"* is a rule in the same grammar as *"Every QM repository is
REUSE-compliant"* was a false claim. No pattern separates them; you have to
decide each one. §12 of the licensing record is the worked example, already
repaired, and the DCO clause in the same record is deliberately left for you.

**A decision the corpus has outgrown.** Several records predate the two-gate
correction, the CLI, and the gate registry. A record that assumes a human
reviews pull requests, or that names a mechanism now superseded, is stale in a
way no check sees.

**A requirement no project could satisfy.** Read at least two of them from the
position of `qmcp`, which has no licence, no `REUSE.toml`, and no test workflow.
If a record is unsatisfiable for a real repository, that is a finding about the
record.

**A record that should not exist.** Merging two, or deleting one, is a
legitimate outcome and cheaper now than after ratification.

## What to produce

**A perspective**, not a record — this is a reading, and readings are opinion
until the organisation acts on them. Name it
`perspectives/2026-MM-DD-the-first-semantic-review.md`, index it in
`perspectives/README.md`, and state plainly:

- which records you read, and in what order
- every contradiction found, with both citations
- for each of the eleven universals: requirement, or claim?
- which records you would merge, split or delete, and why
- **which record you would ratify first**, and what makes it the cheapest
  rehearsal of a five-step path nobody has walked

Then, separately, whichever repairs are small enough to make in the same branch.
A record that needs a structural rewrite gets its own pull request and its own
argument.

## The ratification rehearsal, which this unblocks

Ratification has never been performed in this corpus. The path is five steps and
step 3 renames `DRAFT-<slug>.md` to `QM-NNNN-<slug>.md`, enforced by a regex
nobody has ever hit. `ci/doc_status.py` now reports a filename-versus-Status
disagreement the moment step 2 happens without step 3, so the rehearsal has a
witness it did not have before.

**Do one.** Find out what breaks with a single cheap self-contained record,
rather than fourteen times over. That is `ratification-rehearsed` in the
milestone block, and it is the requirement most likely to surprise.

## What is not yours here

Ratifying anything — that is a human act and needs the second code owner.
Rewriting another record to match your reading before saying what the reading
was. Deleting a record without a pull request that argues for it. Adding a
clause: `DRAFT-governance-arrives-as-a-mechanism.md` §5 says converting beats
adding, and this corpus has measured twice that a clause without a mechanism
does not change behaviour.
