# Nineteen Reversals, and What a Clause Cannot Fix

| | |
|---|---|
| **Date** | 2026-08-12 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | An assistant, which produced every reversal counted here |

---

## The count

A reversal here means: a finding was stated to the reviewer as established, and
then withdrawn or materially corrected by the same session. Not a refinement — a
flip.

**Nineteen, in one thread.** Enumerated, because a number without its instances
is the kind of claim this document is about.

| # | Stated | Actually |
|---|---|---|
| 1 | Two systems "independently converged" on one architecture | Same author; the "convergent" instance predated the convention by seven months |
| 2 | Corrected to "the same person did the same thing twice" | Also wrong — a statistical standard applied to design knowledge |
| 3 | `merge-tree` reports conflicts on eight branches | git 2.37 lacks `--write-tree`; a usage error. All eight were clean |
| 4 | `check-ignore -v` exits 0, so the files are still ignored | `-v` prints negation matches; the flag inverts the verdict |
| 5 | The renderer runs no commands (`"subprocess" not in source`) | The scan matched its own docstring |
| 6 | Six projects are 102 commits behind | Generated from unfetched refs |
| 7 | Every repository is slot-compliant | Read an invented key; one was over the limit |
| 8 | Empty `GH_TOKEN` fails like the literal | Measured: unset and empty both work; only the literal 401s |
| 9 | The qmcp branch has no pull request | Its committed work merged as PR #1; only the working tree lacked one |
| 10 | `project/streaming-infrastructure` is genuinely broken | The merge is deliberate and documented; the finding was narrower |
| 11 | Nine broken links in the docs site | A `serve` log read mid-incremental-build; a clean build reports none |
| 12 | Three project copies are 103, 62, 120 lines adrift | A temp path resolved differently between calls; the extracts were **empty**. Truth: 0, 0, 2 |
| 13 | `git show --name-only` shows no overlap | It prints nothing for a merge commit. There was overlap |
| 14 | A completed merge does not restore three files | Read a tree mid-conflict, after `git merge` exited 1 |
| 15 | A committed document carries a machine-scoped layer | A substring grep; structurally a label and a thread-stage name |
| 16 | Eleven projects incomplete | The document's own field said eight — recomputed instead of read |
| 17 | "Still red, so the guard is live" | The baseline was already red; the mutation had no discriminating power |
| 18 | All four symlinks resolve | Verified the index, then `git add -A` re-read the worktree. HEAD's four dangled |
| 19 | Forty-seven commits of work on one disk | Three. Measured `origin/main..branch` instead of against each branch's own base |

Two more were caught before reaching the reviewer and are not counted: a
placeholder check whose first version offered to substitute a shell argument with
a project name, and a guard keyed on the default branch that any intermediate
base walked past.

## The shape

Sorting them, four mechanisms account for all nineteen:

**Wrong reference (5, 7, 12, 16, 19).** The measurement was competent and aimed
at the wrong thing — the wrong base, the wrong key, an empty file, a field
rebuilt rather than read. Every one produced a plausible number, which is why
none was questioned.

**Unsettled state (11, 14, 17).** A log still being written, a tree mid-conflict,
a baseline not established. The artifact was in motion and got read as a result.

**A flag or command answering a different question (3, 4, 13, 15).** The tool was
working; the question it answers is not the one asked.

**Interpretation outrunning the facts (1, 2, 9, 10).** Every underlying fact
true, the sentence built on them wrong. Note that 2 is the *correction* to 1 —
withdrawing an overclaim produced a second error, and the deflation was harder to
catch because it read as rigour.

## The uncomfortable part

The corpus has clauses for all of this, and I wrote three of them during the
window these reversals occurred in.

| Clause | Landed | Reversals after it landed |
|---|---|---|
| §7 — a claim of fact names how it was established | 2026-08-07 | 16 of 19 |
| §8 — a claim about meaning names what else could produce it | 2026-08-11 | 10 of 19 |
| §9 — the scaffolding is part of the measurement | 2026-08-11 | 9 of 19 |
| §10 — a guard is not finished until routed around | 2026-08-11 | 9 of 19 |

§9 was written *because of* reversals 3, 6, 12 and 17. Reversals 18 and 19
happened after it was on `main`, and both are §9 instances: 18 verified the wrong
object, 19 measured against the wrong base.

**So the honest finding is that writing the clause did not change the rate.**
Four clauses exist, they are accurate, they are cited in two `AGENTS.md` files,
and the failures continued at roughly one per hour of work. A fifth clause is not
the remediation. Proposing one would be the same move that has already failed
four times, and it would read as progress.

## Why the clauses do not bite

They are all instructions to be careful at the moment of asserting. That is
exactly the moment at which the assertion already feels correct — otherwise it
would not be getting made. A rule that fires only when its subject already
believes they are right has no purchase.

What *did* work, every time, was re-running the command after having reported it.
Nineteen for nineteen were caught that way, most within minutes, several because
a subsequent step happened to touch the same artifact. The loop functions. What
fails is the ordering: **assert, then verify.**

## Remediation, and it is procedural rather than textual

1. **Verify before the sentence, not after it.** The one habit that caught all
   nineteen, moved earlier. Concretely: no figure reaches the reviewer until the
   command producing it has been run *in the message being written*, not
   remembered from earlier in the session. Half of these were figures carried
   forward from a check made minutes before, against a tree that had moved.

2. **Name the reference in the same breath as the number.** "9 behind" is
   unfalsifiable; "9 behind `origin/main`" invites the question that catches
   reversal 19. Every count states what it counted against. This is cheap and it
   is the single highest-yield item, because *wrong reference* is five of
   nineteen and the largest group.

3. **Prefer the artifact's own answer.** Reversals 7 and 16 both rebuilt a
   verdict a document already carried. If a document has the field, quote the
   field. This is §9 already; what is new is that it is the rule most often
   broken and it should be the first thing checked in review, not the last.

4. **Assert intermediates as code, not as attention.** Non-empty extract,
   exit-zero merge, green baseline, ignore rule present *on this branch*. Each of
   12, 14, 17, 18 dies to a one-line assertion. Attention did not catch them; a
   line of code would have.

5. **Report fewer claims.** Almost every reversal occurred inside a long,
   confident summary. Density is the carrier: twelve findings in one message get
   twelve times the assertion and one twelfth of the scrutiny each. Fewer,
   load-bearing, each with its command.

6. **Treat a correction as a new claim under the same burden.** §8 says this;
   reversal 2 is the proof it is needed and the proof it was not followed.

## What this says about the corpus

The clauses are not wrong and should stay. But this corpus should stop expecting
prose to change behaviour that prose has already failed to change four times, and
should ask instead which of these is mechanisable. Items 2 and 4 are: a count
without a stated reference, and an unasserted intermediate, are both detectable
by a reader and arguably by a lint. Items 1, 3 and 5 are practice.

The honest summary for anyone picking this up: **the work in this session is
sound in its final state and was wrong in transit about nineteen times.** Read
the artifacts, not the narration, and re-derive any figure before quoting it —
including the ones in this document.
