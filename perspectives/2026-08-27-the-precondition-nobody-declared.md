# Perspective — The Precondition Nobody Declared, and the Green That Meant Nothing

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5, the assistant that introduced most of the defects below and then found them |
| **Task** | A retrospective on one session that built a readiness model in two repositories. The reusable part is not the model; it is that a file had already written down the flaw the model fixes, in its own closing paragraph, and nobody acted on it for months. |

## 0. Standing and evidence

One session, four repositories, commits stamped in
`handbook/handoffs/views-declare-what-they-need.md`.

- **E1** — directly observed: command output, test results, HTTP responses.
- **E2** — read from the repositories.
- **E3** — inference, marked where it appears.

## 1. The assumption, which was written down and unread

`dossier/src/dossier/views.py` closed with this, and had for months:

> WHAT THIS CANNOT DO. Say whether a view has anything in it. `Waiting` reads
> zero rows when no harness has asked a question, and that is the state it
> exists to show; **an empty view and a broken one look identical from here.**

That is the whole defect, stated by the file that had it, in the file's own
voice. Five of its views rendered nothing until a precondition was met and none
of them said so.

**The false assumption was mine and it was that this sentence was a caveat.** I
read it as a limit somebody had accepted, of the kind this corpus writes
everywhere and means. It was a limit somebody had *noticed*, which is a
different thing, and the difference is whether anybody is supposed to act.

I did not act on it when I read it. I acted on it three hours later when it bit
me from a different direction — a screenshot tour that could not fill five tabs
— and even then I patched around it with a hand-written exclusion list before
seeing that the file had told me the answer.

**The reusable part**: a "WHAT THIS CANNOT DO" paragraph in this corpus is
sometimes an honest boundary and sometimes an unfixed defect wearing one. They
are written identically. A reader cannot tell them apart, and I could not.

## 2. The diagnosis I got wrong, and how

Reporting on the five unfillable views, I wrote that Details, Documentation and
Outstanding *"fill for a person and not for a script"* and called it a view
behaving differently for the two — a real and interesting-sounding finding.

It was wrong. They fill for whoever has selected a repository with data in it.
My script never selected one (E1: with a selection passed, 18 of 18 views
report ready).

Every fact underneath was true. The tabs were empty; a person could fill them; a
script could not. The sentence assembled from those facts named a property of
the *views* when the property belonged to *my script*, and it was the more
interesting of the two available explanations. `DRAFT-decision-record-
discipline.md` §8 says to name the ordinary cause before the interesting one. I
know that rule well enough to have quoted it twice this session, in writing,
while doing this.

**The check that would have caught it**: asking what else produces an empty
tab, before publishing a claim about why. It now exists as
`dossier/tests/core/test_readiness.py`, which resolves preconditions rather
than describing symptoms.

## 3. Four readings, four defects, none of which the others found

Before trusting the readiness model I read it from four positions. Each found
something the other three did not (E1):

- **A newcomer on a bare machine** met nine near-identical entries for one fact
  — nothing is selected — and would learn to stop reading rather than that nine
  things were wrong.
- **An operator whose harness had died** was told to run `dossier harness
  queue`, which reads the harness, reports the same problem, and *then* names
  the real fix. A remedy has to be the fix, not a hop toward it.
- **A maintainer adding a view** found `dossier governance refresh` offered as
  the remedy for a missing corpus. That command has never existed. I had written
  it an hour earlier, in the same session that shipped a check for exactly this
  class in another repository.
- **A reader checking claims against measurements** found `Branches` reporting
  *ready* while its clone need had never been looked for: an unchecked need
  answered `unknown`, and `unknown` deliberately does not block.

The fourth is the one worth keeping, because it is a flaw in the *design* rather
than in a string. `unknown` not blocking is right — refusing a view on a
measurement that never happened is the worse error — and it means any need that
answers `unknown` when it was simply never asked reads as available. The fix is
that a need whose subject is missing is *unmet*, not *unknown*.

**A fifth reading would find a fifth thing.** Four positions is not a proof, and
the consensus in the handoff is described as vague on purpose.

## 4. My own abstraction fighting itself

I wrote `_of_one_repository(what)` so that nine views needing a repository would
each say so in their own words — "these facts belong to one repository",
"issues belong to one repository" — because a reader inside a view deserves a
sentence about that view.

Then I grouped the survey by `(key, because, satisfied_by)` to collapse the
newcomer's wall, and got nine groups of one. The variation I had added for
readability was the thing defeating the grouping (E1).

The fix was to group on what is missing rather than on how it is worded. The
lesson is smaller and more useful: **an abstraction introduced for one reader
can be the obstacle for another**, and the per-view sentence is still right
inside a view.

## 5. Brittleness I introduced, and had to be told to remove

Asked for a review, I found six brittle things I had written that same day
(E1). The worst:

    assert "TABS = [(view.tab, view.title) for view in views.VIEWS]" in source

That asserts *how the code is written*. Reformat the line and it fails while
nothing is broken; write a different expression containing that text and it
passes while everything is. It now imports `TABS` and compares it to the
registry.

The others were counts typed into assertions and prose — `"9 waiting on
project"`, `len(every) == 11`, "a hundred and eighty-two" — every one of them a
figure some other file decides. `DRAFT-few-integers-in-durable-text.md` is a
record I had cited approvingly in a pull request body earlier the same day.

**The pattern across §2, §4 and §5**: I know these rules well enough to quote
them and to enforce them on other people's code, and I broke all three inside
one session. Knowing a rule is not the same as having a check, which is the
argument P16 makes and which I keep re-proving accidentally.

## 6. The green that meant nothing

The last finding is the one I would take out of this session if I could take
only one.

`qmcp` #34 was opened, and its `pull_request` workflows never fired — no
`Tests`, no `ADR lint`, no `One PR per contributor`, on the opening and on a
forced `synchronize` (E1). Only the push-triggered submodule check ran.

    GitGuardian Security Checks: pass
    check-submodule-refs: pass

**`gh pr checks` reports all-pass.** The pull request reads merge-ready.

Seventeen pull requests merged earlier that day on exactly that signal, and I
had checked each one the same way. Had the events stopped an hour earlier I
would have merged unverified changes while reporting them as gated, and the
report would have been sincere.

This is a new face of a thing this corpus already knows. The catalogue so far is
*a check with a hole*, *a check answering a different question*, and *a check
measuring its own scaffolding*. This is **a check that did not run, and a
summary that cannot tell that from passing**. `gh pr checks` aggregates what
exists; absence has no row.

**The check that would catch it does not exist.** It would have to know what
*should* have run — the workflows a repository declares for `pull_request` —
and compare that to what did. Every input is available: the workflow files
declare their triggers, and the runs API says what ran. Nothing joins them.
That is the next piece of work, and it belongs in the seed so every project
gets it.

I could not establish why the events stopped (E3: repository, account or
platform; all three fit what was observed). That is a smaller question than the
signal being unable to say so.

## 7. What to distrust here

The measurements are checkable and were checked by running them. The
explanations are mine, and §1's claim — that a "cannot do" paragraph is
sometimes an unfixed defect — is a reading of one instance generalised. The
duller alternative is that nobody had needed those five views yet, and it may be
the true one.

And the obvious caution: most of the defects above were introduced by the same
practitioner who then found them, in the same session. The finding rate says
something about reading work from more than one position. It says nothing
reassuring about writing it.
