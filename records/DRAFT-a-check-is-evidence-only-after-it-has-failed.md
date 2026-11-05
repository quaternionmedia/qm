# QM-XXXX — A Check Is Evidence Only After It Has Been Seen to Fail

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-22 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `a-check-is-evidence-after-it-fails` — a check is evidence only after it has failed; `show-it-by-running-it` — show it by running it; `decisions-are-documented` — decisions are documented or they didn't happen |
| **Restated in** | `PRINCIPLES.md` `a-check-is-evidence-after-it-fails`; `AGENTS.md` item 13 |
| **Unifies** | `records/DRAFT-decision-record-discipline.md` §7, §9, §10 |

## Context

This corpus says three things that are one thing.

- **§7** — check a signal before reading it; name one other thing that would
  produce the same output.
- **§9** — the scaffolding you measure with is part of the measurement; nothing
  errors and the result describes your own setup.
- **§10** — a guard is not finished until someone has tried to route around it.

Each reads as advice about care, and is not. They are three symptoms of one fact: **reading a check does
not tell you what it checks.** Only running it against a world where it should
fail does.

Defects divide cleanly by *what finds them*:

**Reading** — code, tests or documents, carefully, by somebody looking for
defects — finds defects of *shape*: a route that does not exist, a docstring
that says three where the answer is five. It does not find defects of
*behaviour*.

**Making something fail on purpose** finds the rest: a guard that keys on a
branch name and passes on identical content renamed; an agreement check that
compares sets, so three parallel edges compare equal to one; a palette marker
with no mapping, silently becoming the shape it was chosen to differ from; a
"does not create the file" test whose path has a missing parent, so it passes
with its own guard removed; a browser test that **skips** and reports green;
two windows that "agree" because both read the same field.

A test written by its author to check exactly such a property, and read after
writing, can be wrong in exactly these ways. The Verification section gives the
figures for one session at one commit.

**The asymmetry:** reading is good at absence and bad at
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

`show-it-by-running-it` is the same shape one level up: a document that describes behaviour is
unproven until the behaviour produced it. This record is `show-it-by-running-it` applied to the
checks themselves — **the tests are documentation of behaviour too, and they
drift the same way.**

## Alternatives

**Require mutation coverage as a gate.** `uv run qm mutate` exists and could be
made to fail a pull request. Rejected for now: a mutation-score threshold
rewards tests that survive random edits, which is not the same as tests that
fire on the intended one, and a number would be gamed the way coverage is. The
obligation here is per-guard and stated in prose next to the guard, which is
cheaper and points at the right thing.

**Say nothing and rely on the existing three sections.** Rejected: they can be
in force, in writing, accurately describing a failure, while it happens (see
Verification). The corpus's own `AGENTS.md` item 16
says a decision that wins on precedence and loses on readership does not
govern. Three sections in a long record lost on readership; one principle with
a name may not.

## Consequences

**A guard costs more to add.** Writing it, breaking it, watching it fail,
restoring it — call it a few minutes. Against that: a guard that does not
guard is found later and more expensively.

**Some existing guards are unproven and will stay so.** Nothing here reaches
back over work already done. A guard nobody has broken is not a defect; it is an
unknown, and
`records/DRAFT-a-knot-is-a-cycle-of-obligation.md` §2 is the corpus's rule for
those: unknown is a value, never zero.

**"The suite is green" becomes a weaker sentence.** It should be: a green suite
is what lets a guard that does not guard live for at least a round.

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
