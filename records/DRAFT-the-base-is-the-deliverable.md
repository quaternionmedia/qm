# The base is the deliverable, and it is stable when a pass adds nothing

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-16 |
| **Namespace** | org |
| **Binds** | This corpus, and any project that adopts it |
| **Pends on** | Ratification. Nothing here is settled. |
| **Restated in** | `AGENTS.md` — the reading budget and the loop condition |

---

## 1. What is being built

**A self-governed corpus that accepts concurrent, overlapping, asynchronous and
conflicting feedback; integrates the improvements that are approved and
validated; and collects feedback and runs real tests to drive data-driven
iteration.**

That sentence is the deliverable. Every mechanism in this repository is either
serving it or is decoration, and the distinction is worth making out loud
because the mechanisms arrived one at a time from things that broke, and a fix
justifies itself locally without ever being asked what it is for.

Read as a set of requirements it has four parts, and they are not equally built:

| | | |
|---|---|---|
| **concurrent, overlapping, asynchronous** | more than one session, in more than one clone, at once | `handbook/async-contract.md`, the slot rule, `project/<name>` bases |
| **conflicting** | two contributors may disagree, and the corpus must hold both until something settles it | `Pends on`, `perspectives/` as opinion, precedence |
| **approved and validated** | two human gates: ratification and the version tag | `records/DRAFT-version-tags-are-claims.md` |
| **data-driven iteration** | the corpus measures itself and changes because of what it measured | `ledger.yaml`, the registries, the generated documents |

## 2. The base, and why naming it changes the work

The **base** is what must be true before a governance loop can run at all: one
entry point, claims separated from evidence, detectors that read artifacts,
attribution on every action, declared gaps, and predictions recorded before
acting.

Before it was named, the work was an open-ended sequence of justified fixes with
no definition of done. That is the failure mode this record exists to close: not
a wrong decision, an *unnamed deliverable*, which cannot be finished because
nobody can say what finishing would look like.

## 3. The acceptance criterion

**The base is stable when a full pass over it adds no ledger entry.**

A pass is a run of the loop: the tests, the gates, the mutation harnesses, the
generated documents, and a read of the corpus against the repository. An entry
is added when that pass finds something — a defect, a false claim, a rule with
no mechanism, a measurement that disagrees with its document.

The criterion is deliberately not *no failures*. A pass that finds a failing
test and fixes it adds an entry, and should. What it measures is whether the
ground is still moving: **an entry means the pass changed the base, so the next
pass is over different ground, so nothing before it was measuring the thing that
now exists.**

## 4. A pass that adds nothing must be recorded

This is the mechanism half, and without it §3 is a sentence rather than a test.

The ledger records **additions**. A pass that finds nothing leaves no trace, so
`no new entries` and `nobody ran it` are the same file. The criterion cannot be
read off an artifact that only grows when something goes wrong.

So a pass is recorded whether or not it found anything, in `passes:` alongside
`entries:`, and the entries it added are **computed from the ledger's own
length** rather than typed in — a hand-entered count of one's own findings is
the number most worth not trusting.

**A pass records the runs that went badly on the same terms as the ones that
went well.** A pass log that a contributor updates only after a good run is a
streak counter. The streak is only evidence if a bad pass is as recorded as a
good one, which is the same argument as `tool` being required on every ledger
entry rather than only the ones recording a fault.

## 5. What this does not assert

**A long streak does not mean the corpus is correct.** It means passes stopped
finding things, and a pass only finds what its checks look for. Most of what
this corpus asks for is judgement and has no detector at all — nine policies are
registered and two of them state that they can never have one. A stable base is
a floor that stopped moving, not a ceiling that was reached.

**Stability is not ratification.** Neither is it a tag. The two human gates are
unaffected by any streak: a corpus can be perfectly stable and entirely
unratified, which is what it is today.

**The criterion can be gamed by narrowing the pass**, and nothing detects that.
A pass that runs fewer checks finds fewer things. The defence is that a pass
records what it ran, in its own words, next to its result.

## 6. Alternatives considered

**Leave the criterion as prose in a retrospective.** It was, for one day. A
sentence in `perspectives/` binds nothing and is not read at the moment the
question arises, which is the failure `records/DRAFT-the-read-document-governs.md`
was written about.

**Count consecutive green CI runs instead.** CI measures the workflows, which
are a subset of a pass and the subset least likely to find anything new — they
are the checks that already exist. A green pipeline is the floor's floor.

**Require a human to declare stability.** That is the ratification gate, and
loading a second decision onto it would make the cheap signal wait on the
expensive one.
