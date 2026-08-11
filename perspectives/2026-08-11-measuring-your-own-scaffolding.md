# Measuring Your Own Scaffolding

| | |
|---|---|
| **Date** | 2026-08-11 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | Claude Opus 5, in a session that produced most of the errors described |

---

## The shape

A day of work on this corpus produced eleven false readings. Two were the kind
§7 already covers — a tool answering a question other than the one asked. Two
were §8 — every fact true and the sentence built from them wrong. The remaining
seven were something the corpus had not named, and they were the majority:

**the thing being measured was produced by the act of measuring.**

Nothing errored in any of them. That is the whole difficulty. A tool-version
mismatch announces itself eventually; a flag with inverted semantics can be
found by reading the man page. These produce a clean number, promptly, and the
number is about the scaffolding rather than the subject.

## The seven

**A comparison against files that were never written.** Three workflow copies in
another repository were diffed against the current seed and reported 103, 62 and
120 changed lines. That reads as a project badly adrift. The redirect target had
resolved to a different path than the one the diff then read, so all three
comparison files were empty and the "changed lines" figure was the *seed's own
line count*. The real answer was 0, 0 and 2 — one corrected sentence in one
file. A single `wc -c` on the extract would have caught it, and the fixed
procedure now has one.

**A merge read mid-conflict.** `git merge` exited 1. The next command listed
files and found three of them missing, which was reported as "a completed merge
does not restore these". It was a conflicted half-state. The corrected test
carried the merge to completion and produced a genuinely interesting answer —
that a neutralised merge permanently declines everything it neutralised — but
the first version had the right conclusion for the wrong reason, which is the
worst place to be, because it is unfalsifiable by the person who wrote it.

**Eleven branches of pure line-ending noise.** Refreshing a copied file on eleven
project branches used a text API whose write translated every newline. Each
branch reported two files changed with whole-file diffs. Git would have
normalised it away on commit, so nothing would have broken — the damage was that
a real one-file change was hidden inside eleven fake ones, and "2 files changed"
on every branch is precisely the uniform result §7 says to distrust.

**A mutation test that could not distinguish.** A guard was added and then
mutation-tested by removing it. The run was still red, which was read as "the
guard is live". The baseline had been red before the mutation for an unrelated
reason, so the test had no discriminating power in either direction. It was
reported as evidence. The corrected version establishes the baseline first, and
the second attempt then found that the *first* mutation had also been wrong —
it had removed the guard in a way that produced a different bug rather than the
original one.

**A verdict rebuilt instead of read.** A document carried a `precondition` field
with three values. Rather than read it, the field was reconstructed from the
raw sub-fields, and the reconstruction said eleven projects were incomplete when
the document's own answer was eight. This is the second instance of the shape:
an earlier one invented a key that did not exist at all, and every repository
consequently reported compliant — including one that was over its limit.

**A merge commit's file list.** `git show --name-only` on a merge prints nothing
by default. It was run to check whether an incoming commit touched any of the
same paths, printed nothing, and was reported as "no overlap". It had touched
one of them.

**A grep standing in for a structural check.** A committed document was searched
for the substring `local` to decide whether a machine-scoped layer had been
committed. Two hits, read as a problem. Structurally they were a *label*
explaining what the layer would contain, and a thread stage that happens to be
named `local` — neither a committed machine fact. The same grep would have
returned two hits whether the answer was yes or no.

## Why this class is the hard one

The corpus's existing disciplines both assume an adversary that can be
interrogated. §7 says check the signal — read the flag, check the version, run
it again. §8 says name what else could produce the meaning. Both work because
the thing you are suspicious of is *outside* you.

Here it is not. The empty file, the half-merged tree, the converted encoding,
the contaminated baseline — you made all of them, seconds ago, and they are
therefore the last place you look. Worse, each one produced a *plausible* answer.
Not a suspicious one. "This project has drifted a hundred lines" is exactly what
a stale copy looks like. The reading was wrong and the story was good.

The one honest signal available in all seven cases was an intermediate that
nobody asserted: is the file non-empty, did the command exit zero, is the
baseline green, does the document already answer this. Every single one was one
assertion from being caught. That is a cheap fix for a class of error this
frequent, which is the argument for making it a clause rather than a habit.

## The second lesson, which is about guards

Three independent holes were found in one new guard on the day it was written,
by an adversarial pass asked to satisfy the check while doing the forbidden
thing:

- it keyed on the default branch, so routing through any intermediate base
  walked past it, and the very change that introduced it was landing on such a
  base;
- it matched a branch *name*, so the identical tree under an innocuous name was
  clean — and the demonstration took one `git commit-tree`;
- CI ran it in a mode that would have failed every legitimate propagation,
  because the tool's own docstring distinguishes a refusal from an advisory and
  the caller did not read it.

The third is the one worth dwelling on, because the information needed to avoid
it was in the file being called, three lines from the top, and I had read that
file that morning to add the guard.

Break-it-and-watch-it-go-red is genuinely good practice and it did not help
here. It confirms a guard fires on the case you had in mind. The holes are
always the adjacent case, and by construction you cannot enumerate what you did
not think of. Somebody — or something — with the brief *pass this check while
violating it* finds them in minutes.

## What this cost, and what it bought

Nothing reached `main` broken. Every one of these was caught, most within
minutes, several by re-reading my own output before reporting it and several
more by an adversarial pass. The cost was rework and a number of confident
statements that had to be withdrawn in the same session they were made.

The thing worth keeping is that the correction rate was high *because the
session kept re-deriving*. The failures were not caught by care at the moment of
writing; they were caught by a habit of running the command again and looking at
what it actually printed. That is a mechanical habit, not a virtue, and it can
be written down — which is what §9 and §10 now are.

## Related

- `records/DRAFT-decision-record-discipline.md` §7, §8, §9, §10
- `perspectives/2026-08-11-inflation-deflation-and-what-discovery-looks-like.md`
  — the §8 failure, from the same period
