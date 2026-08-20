# The demo found what the fix did not

**2026-08-19 into 2026-08-20.** The `qmcp`/`dossier` pair. Attributed, dated,
binds nothing.

Tools: written with an AI coding assistant, reviewed and committed by a human.

Companion to
[`2026-08-19-two-fixtures-that-agreed-with-nothing.md`](2026-08-19-two-fixtures-that-agreed-with-nothing.md),
which covers the defect in the seam itself. This one is about what came after:
building something that used the seam, and what that turned up which fixing it
had not.

## The shape of the session

Three phases, and each found things the one before had missed.

**Reading found the categories nobody could read.** Four comment headers in a
roster, holding a claim no check could see.

**Fixing found the fixtures.** Two suites, green, each verifying the seam
against a payload it had invented, neither of which had met the other side.

**Demoing found three more.** After the contract landed, after both suites were
green against real emitter output, after mutation runs killed every signal — a
demo that used the pair for one ordinary purpose broke it in three places.

That progression is the finding. Each phase was thorough on its own terms and
each left something only the next kind of work could see.

## What the demo broke that the tests did not

**The control panel could not be pointed at another database.** `DATABASE_URL`
was a module constant. There was no override, so anything wanting a scratch
database had to change directory. The suite never noticed because the suite
passes its lookups in as arguments — a design decision that is right, and that
made the one path a real caller takes invisible to it.

**A payload's links were read and dropped.** The address that joins the two
views, and the invocation that produced a finding, were never written. Every
test of `plan` passed, because `plan` is the decision layer and the defect was
in the write path underneath it.

**Links wrote only on create or update.** Fixed the first defect, ran it twice,
and the second run stored nothing — an unchanged delta skipped the pass. That
is exactly what a second run of a failing check looks like: same delta, new
invocation. The rows that accumulate were the rows being dropped.

None of these is exotic. All three sit between the tested units, in the part a
person actually types.

## The one that was mine

**I wrote demo data into the operator's live database.**

I had said I would use a scratch one. I set `DOSSIER_HOME`, which overrides
where the *config* lives, assumed it redirected the database, and ingested.
It went into `dossier.db` alongside a hundred and fifty-six real rows.

The recovery was fine — the rows were identifiable by name and by tool name,
they were deleted precisely, and the counts were checked back to where they
started. That is not the point. The point is that I stated an intention, took
an action I believed implemented it, and never checked the belief before the
irreversible step.

This corpus already has the rule. `AGENTS.md` item 12: *assert the intermediate
— non-empty, exit zero, baseline green — because every one of those was one
assertion from being caught.* One `ls` of the scratch directory before the
write would have shown it empty. I ran that command afterwards, diagnosing.

**A stated intention is not a configured one**, and the gap between them is
invisible from inside the session that has the intention.

The repair is the affordance that was missing: `DOSSIER_DATABASE_URL`, so the
scratch case is a thing you can ask for rather than a thing you arrange by
standing in the right directory. `qmcp dashboard --database` had existed all
along on the other side of the same seam.

## The fix that nearly reintroduced the bug it fixed

Adding the override to the CLI took one line and was wrong. `db upgrade`
resolves its target through `health.py`, not through the CLI constant — so an
override on the engine alone would have migrated one database while every query
ran against another, and reported success.

`dossier/health.py` exists *because of that exact failure*. Its opening
paragraph describes a fresh run dying on a missing column because the database
being opened was not the one anybody had migrated. The one-line fix would have
rebuilt it, in the module written to prevent it, while adding a feature whose
whole purpose is to stop writes going somewhere nobody asked.

**A partial override is worse than none**, because the caller now believes they
have redirected something.

## Two of my own tests were wrong, in two different ways

**One passed against the mutation it named.** `test_totals_are_never_coerced`
asserted that the function raises on an unknown. The coerced version raises too
— `int()` of a non-empty dict is a `TypeError` either way — so it was green
against the defect it was written for. The mutation run caught it. What
actually discriminates is a *missing* key, which the coerced form invents a zero
for.

**One asserted the prose.** A test that a green run produces no unit of work
checked that the phrase "unit of work" was absent from the report — and the
all-green message says "No unit of work follows from a green gate". It went red
on its own wording. Rewritten to assert that no delta name appears, which is
the property.

Those are the two failure modes of a test written by the same author as the
code: it can agree with the bug, and it can agree with the sentence.

## A smaller one worth naming

I read a gate's exit status as 0 when it was `tail`'s. The command was
`check_tag_claims.py ... | tail -12`, and the pipeline's status is the last
element's. This organisation has that registered as `exit-code-trap` in
`ci/pattern-registry.yaml` with `check_exists: false` — a rule it has named and
not made enforceable. It cost a minute here because the output plainly said
FAIL. It would cost more where the output was ambiguous.

## What I would tell the next session

**Build something with it before believing it works.** Not another test — a
use. The tests here were good: real fixtures, mutation-verified, contract-driven.
They still could not see the three defects between them, because a suite tests
units and a demo tests the path.

**Check the redirect before the write, not after.** Every irreversible action
has a cheap precondition, and the cost of asserting it is always smaller than
the cost of not having.

**When a fix touches a module that exists because of a failure, read why it
exists.** `health.py` said in its first paragraph what my one-line fix was about
to do.

**A demo that ends in success is a demo that was staged.** This one ends with a
delta at `planning` and a blocker that has not moved, because that is where the
repository actually is. The temptation to run one more step and show `complete`
was real, and taking it would have demonstrated the single thing the design
refuses to do.
