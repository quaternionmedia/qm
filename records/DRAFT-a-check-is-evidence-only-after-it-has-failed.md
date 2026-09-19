# QM-XXXX — A Check Is Evidence Only After It Has Been Seen to Fail

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-22 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P16 — a check is evidence only after it has failed; P12 — show it by running it; P6 — decisions are documented or they didn't happen |
| **Restated in** | `PRINCIPLES.md` P16; `AGENTS.md` item 13 |
| **Unifies** | `records/DRAFT-decision-record-discipline.md` §7, §9, §10 |

## Context

This corpus already says three things that turn out to be one thing.

- **§7** — check a signal before reading it; name one other thing that would
  produce the same output.
- **§9** — the scaffolding you measure with is part of the measurement; nothing
  errors and the result describes your own setup.
- **§10** — a guard is not finished until someone has tried to route around it.

Each was written after a different failure, and each was read as advice about
care. They are not. They are three symptoms of one fact: **reading a check does
not tell you what it checks.** Only running it against a world where it should
fail does.

The evidence is a natural experiment nobody designed. Over one long session
across four repositories, thirty distinct defects were found. They divide
cleanly by *what found them*:

**Found by reading — code, tests, or documents, carefully, by somebody looking
for defects:** the count is not zero, but every one was a defect of *shape* —
a route that did not exist, a docstring that said three where the answer was
five. Not one was a defect of *behaviour*.

**Found by making something fail on purpose:** a guard that keyed on a branch
name and passed on identical content renamed; an agreement check that compared
sets, so three parallel edges compared equal to one; a palette marker with no
mapping, silently becoming the shape its author had chosen it to differ from; a
"does not create the file" test whose path had a missing parent, so it passed
with its own guard removed; two browser tests that **skipped** and reported
green; two windows that "agreed" because both read the same field.

Six of those were tests written *in that session, by the same author, to check
those exact properties*. They were read after writing. They were wrong anyway.

**The asymmetry is the finding.** Reading is good at absence and bad at
falsehood. A missing route is visible on the page; a check that passes for the
wrong reason looks exactly like a check that passes.

## Decision

**A check is not evidence until it has been observed to fail for the reason it
exists.** Until then it is scaffolding: it may be correct, and nothing so far
distinguishes it from a check that asserts nothing.

Three obligations follow, and they are cheap because they are mechanical.

**1. A new guard is broken before it is trusted.** Change the code the guard
protects so the guard *should* fire, and watch it go red. A guard that stays
green under that change does not check what its name says.

**2. The mutation is written down where the guard is.** One line in the
docstring: `Mutation: <the change> and this fails.` It is the only durable
record of what was actually established, and it tells the next reader what to
re-run when they doubt the guard.

**3. A skip is not a pass, and neither is an empty assertion.** A test that
does not run establishes nothing, and a test whose subject is absent
establishes nothing. Both report green. Where a test must skip — a sibling
repository absent, an optional dependency missing — it carries the reason, and
the reason is about the *environment*, never about the subject.

**What this does not say.** It does not say every test needs a mutation: a test
that fails the moment its subject is deleted is already evidence, and most are.
It says a guard whose failure has never been observed is unproven, and that
this is a state to leave rather than a standard to meet.

## What this unifies

The three sections of `records/DRAFT-decision-record-discipline.md` stay where
they are — they hold the worked examples, and the examples are the value. What
changes is that they stop being three habits and become one rule with three
faces:

| Section | Reads as | Is really |
|---|---|---|
| §7 | be careful reading results | the *tool* answered a different question; run it where the answer differs |
| §9 | be careful with fixtures | the *setup* is untested; make it fail |
| §10 | be thorough with guards | the *guard* is untested; make it fail |

P12 is the same shape one level up: a document that describes behaviour is
unproven until the behaviour produced it. This record is P12 applied to the
checks themselves — **the tests are documentation of behaviour too, and they
drift the same way.**

## Alternatives

**Require mutation coverage as a gate.** `uv run qm mutate` exists and could be
made to fail a pull request. Rejected for now: a mutation-score threshold
rewards tests that survive random edits, which is not the same as tests that
fire on the intended one, and a number would be gamed the way coverage is. The
obligation here is per-guard and stated in prose next to the guard, which is
cheaper and points at the right thing.

**Say nothing and rely on the existing three sections.** Rejected on evidence:
they were in force, in writing, accurately describing all six failures, during
the session in which all six happened. The corpus's own `AGENTS.md` item 16
says a decision that wins on precedence and loses on readership does not
govern. Three sections in a long record lost on readership; one principle with
a name may not.

## Consequences

**A guard costs more to add.** Writing it, breaking it, watching it fail,
restoring it — call it a few minutes. Against that: six of thirty defects in
one session were guards that did not guard, and each was found later and more
expensively.

**Some existing guards are unproven and will stay so.** Nothing here reaches
back over work already done. A guard nobody has broken is not a defect; it is an
unknown, and
`records/DRAFT-a-knot-is-a-cycle-of-obligation.md` §2 is the corpus's rule for
those: unknown is a value, never zero.

**"The suite is green" becomes a weaker sentence.** It should be. Four green
suites are what let every one of those six defects live for at least a round.

## Verification

At the commit this record was written against, in the session that produced it:

- Mutations run against new guards: **17**, of which **16** fired as intended
  and **1** did not — the "does not create the file" test, which passed with
  `mode=ro` removed because its path had a missing parent directory. The test
  was repaired and the mutation then fired.
- Guards found to assert nothing, by breaking them or by a selector matching
  nothing: **6**.
- Defects found by reading alone that were defects of behaviour rather than
  shape: **0**.

Those figures describe one session at one commit. They are the reason for the
decision, not a claim about any other period.
