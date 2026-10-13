# The numbers were the distraction

**2026-08-18. One session, three repositories.** A retrospective, so it counts
things: a retrospective is about a period that has ended, and its figures are
findings rather than status. That distinction is the subject.

Tools: written with an AI coding assistant, reviewed and committed by a human.

## What the session was for

An org overview in dossier's terminal UI, dense enough to be a starting point
for a reader who has never seen the organisation. Then the data behind it:
narrow the local database to one owner, and make the units of work reflect
something real.

All of that landed. What is worth recording is the way it went, because the
operator stopped the session twice — once to say the corrections were
overwhelming, once to name the cause.

## The finding

**I spent more of this session correcting integers than writing code, and
almost none of those integers mattered.**

The pull request body I wrote opened with two counts. Both were wrong before
the branch merged — one because the suite grew, one because the database was
rescoped by the very next commit. Neither figure was load-bearing. Neither
would have changed a reviewer's decision. Both had to be found and fixed,
because a wrong number in a confident sentence makes a reader audit every other
sentence.

That is the actual cost, and it is not the author's time. A document that
carries stale figures gives a reader no way to tell which of its claims were
measured and which were incidental, so the reader checks all of them. The
argument can be entirely sound and still consume an afternoon.

`records/DRAFT-few-integers-in-durable-text.md` is the policy that came out of
it. The short version: prefer the relation to the count, and where a figure is
the point, name the command and the commit that produced it.

## Four defects, and one of them is the pattern

**1. An org overview that was not scoped to the org.** The masthead reported a
star total dominated by a third party's repositories, synced into the same
database as dependencies. The figure was arithmetically correct and completely
false as a statement about the organisation. Caught by checking which owner the
stars came from before surfacing the view — the ordinary cause, checked first.

**2. Two definitions of ownership in one codebase.** The overview's scoping read
one column; the purge fell back to a second. A row could have been counted in
the org's figures and deleted as somebody else's on the same afternoon. Now one
function, used by both.

**3. A new command group silently replaced an existing one.** Adding
`db backup` as a fresh `@cli.group()` named `db` took every alembic route with
it. Nothing errored: the group was simply redefined, and two unrelated tests
failed with a usage exit. A guard would not have found this; the existing tests
did, which is the argument for having them.

**4. A glyph aborted the command that had already done the work.** A checkmark
in a status line raised `UnicodeEncodeError` on a Windows console — *after* the
deletion committed. The command reported a crash for an operation that had
succeeded, which is the worst available ordering. Replacing the glyphs one at a
time would have fixed the ones somebody remembered; the fix is at the entry
point, where it covers messages not yet written.

**The pattern is 1 and 2 together.** Both are the same failure as the integer
problem in a different register: a figure or a rule stated in one place, and a
second copy elsewhere that nothing keeps honest. The database had two owners
for one row; the prose had two counts for one repository. Neither copy was
wrong when it was written.

## What worked

**Checking before surfacing.** The star total was checked against its owner
before the view went anywhere. That single query is the difference between a
demo and a false claim, and it cost nothing.

**Deriving units of work from evidence instead of typing them.** The old rows
were test residue with no description, branch, issue or pull request — so the
rule that removes them is "carries no evidence of work", stated and testable,
rather than a guess from the name. A name-length heuristic would have deleted a
real delta called `ci` and spared a junk one called `testhtr`.

**Asserting what is drawn.** The tests read the rendered screen rather than the
widget's styles, after a previous session's tests passed while the dashboard was
completely hidden. This session that discipline caught a real one: a phrase
absent from the screen because the SVG export encodes spaces as entities, which
would have quietly weakened every assertion into a single-word match.

## What to do differently

**Stop writing counts into prose.** The policy exists now; the habit does not.

**When a correction is needed, make it and move on.** Several of this session's
corrections were announced at more length than the fix deserved, which is its
own tax on a reader who is already managing three repositories.

**Name the second copy when creating it.** Every defect above is a second copy
of something: a second ownership rule, a second command group, a second count.
The moment to catch one is while writing it, not while reconciling it.
