# A red on main, read as the disk

**2026-10-31.** One session coordinating the cleanup of an estate: the
worktrees of five clones, the pull requests open against `main`, two drafts
that existed on one disk alone, and six delegated branches. Attributed, dated,
binds nothing.

Tools: Claude Fable 5.1 coordinating; Claude Sonnet 5.5 on the six delegated
branches; reviewed and committed by a human.

The session landed what was green, resolved what conflicted, and committed what
was stranded. One reading went wrong four times in a row, and the mechanics of
landing many branches at once cost more than any one of them. Both are below.

## The step's wording named a disk, so four readers blamed the disk

**Assumption:** a check that is red on a clean `main` is red for an environment
reason.

The docs audit's families step prints *no longer describe this disk*. Three
delegated sessions ran it, saw `docs/families/index.md` out of date on their
branch, ran it on the clean clone's `main`, saw the same, and reported an
environment difference. The coordinator read three agreeing reports as
confirmation, wrote the finding into the queue page in those words, and merged
on. The host's run of the same step, on the next pull request that touched
`docs/`, was red with the same two pages. Regenerating from `main` changed one
count: the rostered repositories that state no family, one before #248 and two
after it. #248 had moved the roster; #285 carried the page as generated before
it; each was green at its own tip. Red on `main` meant `main` was stale.

Three things made the wrong reading easy. The step's own sentence names the
disk, and a reader takes a check's wording for its semantics;
`records/DRAFT-decision-record-discipline.md` §7 says a check tells you what its
author meant. Agreement among readers who all started from the same sentence is
not independent evidence; `handbook/async-contract.md` §9 says a delegated
report is a claim to verify, and the coordinator verified the claim's fact,
red on `main`, and inherited its meaning. And the ordinary cause was never
named before the interesting one was accepted: a generated page is stale when
its inputs moved after it was generated, which one `git log` on `families.json`
would have shown.

What caught it was the host, because the audit ran where a person's reading did
not. The gate gap underneath, that `docs-audit.yml` runs on pull requests alone
and never on a push to `main`, is in the queue page's §4 with what done looks
like.

## Every landing re-conflicted every other branch

**Assumption:** a branch brought level with `main` stays level long enough to
land.

Six branches each regenerated the same three index documents. Each landing
changed those files on `main`, so each remaining branch conflicted again on
exactly them, and a session that had brought its branch level found it behind
within minutes. The resolution was always the same: take `main`'s copy,
regenerate, commit, push, wait for the host. By the third round it was a short
script, the landing itself another, and the two chained in the background
while other work went on. The queue page's item on index regeneration names
the three commands.

The cheaper shape would have been to land the index-touching branches one at a
time from the start and to let the branches that touch no index land in
parallel. Which branches touch an index is visible in the diff before any agent
is started.

## The guard refused the second merge, correctly

**Assumption:** a chain of merges can be issued back to back.

`qm merge` refused the second, third and fourth pull request in a chain with
*mergeable is UNKNOWN*, because the host recomputes mergeability lazily after
each merge. The guard fails closed, as the queue page records; the session added
a poll before each merge and the chain ran. Nothing to change in the guard.

## Scripts before agents, and where agents still earned their place

Two surveys the plan had assigned to agents were one shell script, run over
five clones in under a minute. The conflict resolution and the gates were left
to agents, one per branch, on the cheaper model, and each came back with the
pushed commit, the step list and what it could not establish. That is the shape
the brief asked for, and the shape that made the misreading visible later:
every report carried the command and the output, so the correction could be
made from the reports rather than by rerunning them.

## What a tool may not do is still a line in the handoff

The worktrees carrying the governance submodule, in two clones, could be
removed only by force, and the session's permission to force was not granted.
The containment proof for each was established and the removals are written
down for the person, with the proof beside each. A cleanup that stops at a
permission boundary and says so is cleaner than one that routes around it.
