# What the push found — 2026-10-12

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-12 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

The session resumed the performing family's readiness checks and then put
every branch on origin. Along the way it reviewed ShowRunner #39 against the
family's stack and fixed what the review found. The state is in
`handbook/handoffs/performing-family-consolidation.md`. This page is why it
went the way it did.

## Unsigned commits behind a uniform reading

The two qm branches under #138 and #139 held commits that a stopped session
had made unsigned. The first reading missed it. Locally, `git log
--format=%G?` printed `E`, *cannot be checked*, for every commit, including
those already on `main`, and the preflight's signature step said the same.
A result that uniform describes the tool, not the commits. `git verify-commit`
on one of them answered *good signature*. With that control in hand, the
`N`s stood out. Re-signing them before the push kept every tree, parent and
message, and #138 went green.

What would have caught it sooner: reading a control before the uniform
result. The preflight still reports a signed commit as uncheckable on this
machine. It names no fallback, so a reader has to know to run
`verify-commit`.

## A ledger the queue did not show

The previous session's handoff for this work sat on an unpushed branch, in
that session's own worktree. It recorded that Peter opens nothing in
ShowRunner beyond what mrharpo asks for. This session pushed six branches
there, and later commits onto #39, each at Peter's explicit request, before
reading that ledger. The acts were asked for. The ledger was still the
decision of record, and nothing pointed at it. The queue on `main` cannot list
a page that exists on one disk, and `qm estate` counts a one-copy branch's
commits without reading what they carry.

What would have caught it: reading every one-copy branch's
`handbook/handoffs/` before acting on its repositories. That check does not
exist. The page is now on origin and in the queue, which closes this
instance only.

## The estate's one-copy count matches names

`qm estate` reported `private-34`'s `pre-squash-2026-08-09-session` as
committed work with one copy. Every commit on it was already on origin, under
`archive/pre-squash-2026-08-09-session`. The survey compares a branch with
its namesake, so a branch renamed on push reads as unpushed for good. The
ordinary reading, that the work is unpushed, was wrong. `git rev-list
--not --remotes` settled it.

## A review taken as evidence, then as findings

A sub-agent reviewed #39 and reported eight defects as reproduced. Each was
run again first-hand from its script, and its cited code was read, before
any of it was repeated. All eight held. The re-run cost minutes, and it is
what made the review postable.

## A test that waits on its own defect

The first run of the deadlock and timed-bundle tests did not fail; it hung.
A live fixture's teardown called `close_all()`, which waited on the very
defect the test asserts, for an hour. A test whose cleanup can block on the
defect needs a bound. The fixture now closes on a daemon thread with a
timeout, and the red run ends in seconds.

## A declared floor is a claim

The fixes use python-osc's `strict_timing` and its TCP timeout. The extra
declared `python-osc>=1.9`. Installing 1.9.0, 1.9.3 and 1.10.0 in turn showed
that none has either; 1.10.2 is the first that does. The lock held 1.10.2, so
every run passed and said nothing about the floor. A minimum-versions run would
catch the next one. None exists.
