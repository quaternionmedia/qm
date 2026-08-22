# The first ratification

**What this is.** A proposal that two records be the first this organisation
ratifies, and the manual review a person performs before doing it. Drafted by an
assistant; **the act is a person's** — `docs/ref/ratification.md`, and
`ci/attested-registry.yaml`.

**What it is not.** A claim that these two are the most important records. They
are the two whose evidence is strongest and whose scope is smallest, which is
what a first ratification should be optimised for.

**Stamped 2026-08-22.** Re-derive before acting; the commands are named.

---

## Why ratify anything now

Every org record is `Proposed`, and `docs/ref/ratification.md` says why: the
gate waits on a second active code owner, because GitHub does not count a pull
request author's own approval and a gate one person can satisfy alone is not a
gate.

That reasoning is about *who approves*, and it has not changed. What has changed
is that the mechanics have never been exercised. The ratification page carries a
warning found by reading the lint rather than by ratifying:

> Do the other four steps without renaming and CI fails with
> `index lists record 0001 with no matching file.`

**That warning is itself unratified evidence** — established against a fixture
rather than a real ratification, which is precisely the state P16 says is not
evidence yet. So the steps were performed wrongly on purpose while drafting
this, and **the warning turned out to describe only the safer of two failures.**

| What the ratifier did | What the lint said |
|---|---|
| Status flipped, index updated, **file not renamed** | `index lists record 0001 with no matching file` — fires, as documented |
| Status flipped, **nothing else** | **clean** — silent |

The second is the worse state: the record reads as ratified to any person who
opens it, and is invisible to every check, because both existing checks key on
the *filename*. `check_ratified_are_numbered` in `project-seed/ci/adr_lint.py`
now catches it, and `project-seed/ci/tests/test_adr_lint.py` proves it by
mutation.

**That hole was found by doing the thing wrongly, not by reading the lint** —
which is the argument for P16 arriving in the same breath as the first
ratification it governs. The first ratification is also the first test of the
ratification path, and it should be a record whose content nobody has to argue
about while the mechanics are being shaken out.

## The two proposed, and why these two

### 1. A knot is a cycle of obligation, not a cycle in the graph

`records/DRAFT-a-knot-is-a-cycle-of-obligation.md` — principle **P15**.

| | |
|---|---|
| **Why first** | Its claim was **measured before it was adopted**, on the organisation's own data, and the measurement is reproducible from the repository |
| **Scope** | Narrow. It changes how cycles are reported and states one earned mapping and one decorative one |
| **Cost if wrong** | Low and reversible. A reporting rule, not a stored format |
| **Argument surface** | Small. The finding — 42 loops, 0 knots — either reproduces or it does not |

The thing that recommends it: the record does not assert that the mathematics is
elegant. It says the symmetric walk produced forty-two rings and every one was
noise, and that a ratio nobody filters is a signal everybody learns to ignore.
That is a falsifiable sentence about this organisation's data.

### 2. A check is evidence only after it has been seen to fail

`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md` — principle
**P16**.

| | |
|---|---|
| **Why first** | It **unifies three sections already in force** rather than adding a fourth obligation, and its evidence is a natural experiment nobody designed |
| **Scope** | One sentence in a docstring per new guard. No gate, no threshold, no tooling |
| **Cost if wrong** | A few minutes per guard, recoverable by deleting one line |
| **Argument surface** | The counts. They describe one session at one commit and claim nothing beyond it |

The thing that recommends it: it makes an existing rule *findable*.
`records/DRAFT-decision-record-discipline.md` §7, §9 and §10 were in force, in
writing, and accurately described six failures **during the session in which
those six failures happened**. `AGENTS.md` item 16 already names that failure
mode — a decision that wins on precedence and loses on readership does not
govern. This is the repair.

### Why these two together

They are the two halves of one stance, and ratifying them apart would lose it:

- **P15** says: look for the structure a layer actually has, and *measure the
  claim before relying on it*.
- **P16** says: a measurement you have not seen fail is not yet a measurement.

P15 without P16 is how a corpus ends up naming things after theorems. P16
without P15 is rigour with nothing to be rigorous about. Each is the other's
guard.

## What they unify

Neither adds a new area of governance. Both **consolidate**, which is the
argument for going first — a ratification that reduces the number of separate
things a contributor must hold is cheaper to accept than one that adds to it.

| Already in force | Now stated once as |
|---|---|
| `decision-record-discipline` §7 — check a signal before reading it | P16, face one: the *tool* answered a different question |
| `decision-record-discipline` §9 — the scaffolding is part of the measurement | P16, face two: the *setup* is untested |
| `decision-record-discipline` §10 — a guard is not finished until someone routes around it | P16, face three: the *guard* is untested |
| P12 — show it by running it | P16 is P12 applied to the tests themselves |
| `deltas-compose` — a cycle is reported, never broken | P15 — *which* cycles are worth reporting |
| `a-route-is-an-address` — an address says two readings are about one thing | P15's measurement depends on it; the loops were found by walking addresses |

**The three sections stay where they are.** They hold the worked examples and
the examples are the value. What ratification changes is that they stop being
three habits to remember and become one principle with a name.

## What a person must decide, and nothing else can

Four questions. None is answerable by a check, which is why they are here.

1. **Is the knot/loop distinction the right one to bind the organisation to**,
   or is it one session's convenient reading of one relation set?
2. **Is P16's obligation proportionate?** It costs a few minutes per guard,
   forever, against six defects found in one session. Is that the right trade at
   this size?
3. **Should P16 have teeth beyond prose?** The record rejects a mutation-score
   gate and says why. That rejection is a judgement, not a finding.
4. **Is ratifying anything at all right while there is one code owner?** The
   page says the gate waits on a second. Going ahead is a decision to treat
   these two as the exception, and the reason must be written down if so.

---

# The manual review checklist

**For a person, before ratifying either record.** Every line is a thing to look
at with your own eyes; the commands are here so nothing has to be re-derived.

The order matters: **the mechanics come last.** A record whose content is wrong
should not reach the renaming step.

## A — Before you start

- [ ] **You are not the sole approver by accident.** `docs/ref/ratification.md`
      says the gate waits on a second active code owner. If you are proceeding
      anyway, write the reason in the ratifying commit — a documented exception
      is governance; an undocumented one is a broken gate.
- [ ] **Establish the commit.** `git rev-parse --short HEAD` and
      `git status --short`. Every figure below was true at some commit and
      nowhere else.
- [ ] **Your pull request slot is free.** `uv run qm slot --repo <owner/name>`.

## B — Is the record true?

- [ ] **Reproduce the measurement in the record you are ratifying.**
      For P15: `uv run qm addresses` and the relation walk the record names.
      **Do not accept the record's own figure** — the point of ratification is
      that somebody checked.
- [ ] **The numbers in the record match what you just ran**, or the record says
      which commit its numbers came from and you agree that is enough.
- [ ] **Name one other thing that would produce the same result.** For P15: are
      the forty-two loops an artefact of how `crosses` is stored rather than a
      fact about the work? For P16: were the six unproven guards unproven
      because of the rule's absence, or because of one author's habits?
- [ ] **The record states what it did *not* establish.** A record with no such
      section is a record that has not looked.

## C — Is it the organisation's decision, or one session's?

- [ ] **Read the Alternatives section and disagree with it once.** If you cannot
      construct the argument for a rejected alternative, the section is
      decoration.
- [ ] **The record binds behaviour you are willing to be held to** — including
      on a day when it is inconvenient.
- [ ] **The consequences are affordable.** For P16 specifically: you are
      accepting a few minutes per new guard, forever.
- [ ] **Nothing in it names a vendor or a product** where an invariant would do.

## D — Does it agree with what it touches?

- [ ] **`uv run qm restatements`** exits zero — every declared restatement pairs
      up.
- [ ] **Read the `Restated in` targets yourself.** The check proves the
      declarations pair; it *cannot* tell that a summary and its record
      disagree. For these two: `PRINCIPLES.md` P15 and P16, and `AGENTS.md`
      items 10, 12, 13.
- [ ] **Where the summary and the record differ, the record is what the
      organisation decided** and the summary is repaired — never the reverse.
      `AGENTS.md` item 16.
- [ ] **The unification table above is accurate**: open
      `records/DRAFT-decision-record-discipline.md` §7, §9, §10 and confirm P16
      states each of them and adds nothing you did not intend.

## E — Only now, the mechanics

`docs/ref/ratification.md` has the canonical five steps. One commit:

- [ ] Status flipped to `Accepted`.
- [ ] Number assigned from the index (`QM-NNNN`).
- [ ] **File renamed** `DRAFT-<slug>.md` → `QM-NNNN-<slug>.md`. **This is the
      step that is mechanically enforced and was documented nowhere** — skipping
      it fails CI with a message naming the index rather than the filename.
- [ ] Index updated.
- [ ] The record named in the commit message.
- [ ] **No co-author trailer, no model name, no vendor address.**
      `records/DRAFT-human-only-contributorship.md`.

## F — After, before it is believed

- [ ] **`uv run --extra preflight qm preflight`.** Expect the two environment
      failures — the signature step asks the forge and has no token locally, and
      the slot step needs an open pull request. **Say which you established:** a
      defect or an environment difference.
- [ ] **`python project-seed/ci/adr_lint.py --records-dir records --index README.md`**
      exits zero. This is the check that catches a missed rename.
- [ ] **In the spirit of P16, break it once.** Two failures, not one, and they
      are different:
      - Flip Status to `Accepted` and add the index row **without renaming the
        file**. The lint fails with `index lists record 0001 with no matching
        file` — the case `docs/ref/ratification.md` documents.
      - Flip Status to `Accepted` and **change nothing else**. The lint fails
        with `Status 'accepted' but the filename carries no number`.
      Then restore, and confirm the lint is clean again.
- [ ] **Any obligation the record says falls due at ratification** has been
      started or explicitly deferred in writing.

---

## What this proposal does not establish

- **That these are the right two.** They are the two with the strongest evidence
  and the smallest scope. A reader who thinks a different record should go first
  is disagreeing about strategy, not about facts.
- **That the ratification mechanics work.** They have been checked against a
  fixture and never run. Section F's break-it step is what would establish it.
- **That one code owner is enough.** The page says it is not. Going ahead is a
  decision this document proposes and does not make.
