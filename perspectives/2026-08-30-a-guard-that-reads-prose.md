# A Guard That Reads Prose Reports on Prose

| | |
|---|---|
| **Date** | 2026-08-30 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | assistant-2026-08, per `ci/tool-registry.yaml`, which wrote every defect below and found most of them only by breaking its own work |

---

## The shape

One session across apothecary and this corpus: a branch restored from an
archive, two demonstrations of one path folded into one, the first slice of a
surface migration, and one record drafted. Nine things went wrong. Six of them
share a shape the corpus has named twice already and which still caught a
session that had just read both namings.

**A check is an object, and the object is the easy thing to get wrong.** Not
the logic. The logic in every case below was correct and did what it said. What
was wrong was *what it was pointed at* — text about the thing, rather than the
thing.

## The guard that passed with the thing it guarded deleted

The walkthrough is now written by the run that asserts it, and the run has to be
one the ordinary test command selects. A demonstration nothing runs writes
nothing, so the committed page silently becomes whatever the last run that did
happen left behind. That is worth a guard, and the guard was:

    source = inspect.getsource(testing.test_run.callback)
    assert testing.DEMONSTRATION in source

Deleting the marker expression from the command left it green. `DEMONSTRATION`
is `"walkthrough"`, and the command's own docstring said *"Run unit tests, the
walkthrough, and optionally the browser tests"*. The guard was reading a
sentence describing the command and reporting on that.

The fix was not a better substring. It was giving the guard a different object:
the command's argv now comes out of a `run_command()` function, and the guard
hands that argv to pytest and asks what it collects. A docstring cannot satisfy
that.

**What it should tell the next session:** when the thing you want to assert is a
behaviour, a source scan will pass on the day the code is deleted and the
comment survives — which is exactly the day you need it. `records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md`
covers this and I broke it anyway; the mutation is what found it, and nothing
else would have.

## A mutation that never applied, reported as a guard holding

In the same batch, three guards were mutated. The second mutation's string
replacement did not match anything, so nothing was broken, the guard stayed
green, and I read that green as the guard being sound.

This is worse than not mutating at all. A mutation run that silently no-ops
manufactures evidence: it produces the same output as a guard with a hole and
the same output as a guard that is fine, and it is reported as the third.

Every mutation script written after that asserts its own replacement count
before running the check. There is still no standing check that a mutation
applied — the discipline lives in the shape of the scripts and nowhere else,
which is a thing to fix rather than a thing to be pleased about.

## Measuring my own scaffolding, twice, in a session that had read the page about it

**The lint baseline that was about black's defaults.** Before formatting my own
files I wanted to know whether they were already unformatted at `HEAD`. I copied
the `HEAD` versions to a temp directory and ran `black --check` on them. Four of
four "would be reformatted", which I nearly recorded as a pre-existing mess.
The copies were outside the repository, so black used its own default line
length rather than the project's hundred. Re-run with the project's settings:
all four clean. The mess was mine.

**A suite run whose sources changed underneath it.** A full run was in flight
when I formatted three files it was executing. The result would have described
the formatting, not the code. Killed and re-run rather than reported.

`perspectives/2026-08-11-measuring-your-own-scaffolding.md` is exactly this, and
`records/DRAFT-decision-record-discipline.md` §9 states it. Reading both did not
prevent either. What prevented the first from being published was noticing that
"all four files, at `HEAD`, unformatted" was too tidy to be true.

## Two greps that answered a different question

`grep -c $'\r'` on two files reported 246 and 131 — which were the files' total
line counts, because the pattern expanded to nothing and matched every line. The
tell was that the number equalled the line count.

`grep -ci 'ring'` on the viewer's markup reported twelve, in a viewer that has no
ring. All twelve were inside `stringify`, `toString`, `docstring`, `triggering`,
`rendering` and `coloring`.

Neither reached a report, and both were checked only because a round number
looked wrong. The corpus's item 10 names "a substring matching prose" as one of
its four original false readings. It happened twice more here.

## The near-miss: a generated document that looked wrong and was right

`governance-status.yaml` reports `open_prs: []` for apothecary. The apothecary
repository has six open pull requests. I had the sentence half written — a
generated document contradicting the tool that generates the slot report — when
the corpus's own rule caught it: name one other thing that would produce this
output. Reading `ci/governance_status.py`, the field counts pull requests **in
qm** whose base is `project/apothecary`. Zero is correct. Two documents about
two different populations, and the field name is the whole ambiguity.

A retraction would have been cheap here and the deflation would have read as
rigour. It would also have been wrong, which is `records/DRAFT-decision-record-discipline.md`
§8's other direction.

## What the join found that reading had not

The task was to fold two demonstrations of one path into one. A hand-written page
of doctests walked the model half; a browser run behind `apothecary docs
generate` walked the viewer half. The page said so itself, in its own closing
section: *"that is driven by `apothecary docs generate` rather than here"*.

Folding them surfaced three things, none subtle, all of which had survived
repeated reading:

- The page's closing instruction was `uv run apothecary test walkthrough`. There
  is no such command. `apothecary test --help` lists five subcommands and that
  is not one of them.
- The page's two headline figures — the viewer's controls, and the steps a
  person types — were typed into the prose by hand beside the meters that
  compute them.
- `--start-server` was registered in `tests/e2e/conftest.py`, which pytest does
  not load when the arguments are `tests/` and `walkthrough`. The joined command
  died on its own flag: `unrecognized arguments: --start-server`.

Three defects in the part a person reads and the part a person types, none of
which any test could see, all found by making one thing out of two. The page is
now written by the run, so the first two cannot recur: an instruction and a
figure that are emitted by the run are wrong only if the run is wrong.

## The handoff whose own numbers disagreed

The archive I picked up carried two pages about one suite. `HANDOFF.md` said 712
passing and two skipped. `HIL-REVIEW.md` said 697 and two. The machine collected
712 in total. Three figures for one subject, on pages whose shared warning was
that *a smaller number means something is switched off rather than passing* —
a warning with no number behind it a reader could use.

This is `records/DRAFT-few-integers-in-durable-text.md` from the receiving end.
The rule reads like tidiness until you are the session that has to decide which
of two numbers to trust and can trust neither.

## What now exists, and what does not

Exists, and has been watched failing:

- the collection guard, which asks pytest what the ordinary command collects;
- the guard that every option a ring offers is classified as the server's, the
  viewer's, or nobody's;
- the guard that everything classified as the server's has an arm in the route,
  asked behaviourally rather than by reading the route's source.

Does not exist, and each is a piece of work rather than a regret:

- anything that asserts a mutation applied before its result is believed;
- anything that stops a formatter running against a suite in flight;
- anything that checks the commands a page tells a reader to run exist. That one
  is cheap, and it would have caught `apothecary test walkthrough` on the day it
  was written.

## The one sentence

The corpus already says a check is evidence only after it has been seen to fail.
This session says something narrower and, I think, more useful: **when you watch
it fail, check that what you broke is what it was looking at.** Two of my three
mutations proved nothing — one because the guard's object was a docstring, one
because the break never happened — and both reported green, which is the same
thing a sound guard reports.
