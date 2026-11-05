# A green suite and eight holes

**2026-08-21.** The harness/control-panel pair, and a day of building on it.
Attributed, dated, binds nothing.

Tools: written with an AI coding assistant, reviewed and committed by a human.

The perspective behind `dossier/src/dossier/diagnostics.py` and
`qmcp/qmcp/feedback.py`.

## The sentence that was already true

`qmcp/selfcheck.py` has carried this since it was written:

> WHAT IT CANNOT SEE. Whether a check is the right check. Whether a passing gate
> is enforcing anything — **every defect this organisation has found in its own
> tooling was a check that reported success while enforcing nothing**, and
> running that check here reports success too.

That was written as a limitation. It reads now as a specification, because a day
of work produced eight defects and **the suite was green through every one of
them**. Not green afterwards — green while they were live, in the exact runs
that were being used to decide the work was finished.

Here they are, because a list of defect classes with no instances is a taxonomy
and a list with instances is evidence.

| what broke | what a green suite saw |
|---|---|
| Ingest button handled on a modal document viewer that does not compose it | 756 passed |
| That button pushed off the right edge of the screen by an unstyled input | 756 passed |
| Threads tab composed, columns defined, facet written — and no loader, ever | 776 passed |
| Sweep tab blank behind a gate that returns early with no project selected | 801 passed |
| Panel looking for the harness on 8000 while it served on 3333 | 776 passed |
| Tests reaching a real socket, so results depended on what was listening | 756 passed, differently each time |
| A module attribute assigned and never restored | 776 passed, in that order only |
| `view.harness` dispatched by nothing, nameable by no wedge | 742 passed |

## What they have in common

Not a shared cause. A shared *shape*: every one is a **join between two things
that were each correct**.

A button and a handler, both fine, on different classes. A tab and a loader,
both fine, never introduced. A port constant, correct in each repository,
disagreeing across the seam. A test and its fixture, both fine, sharing a
process. A menu and a document, both fine, drifting apart.

A test suite examines things. These were all joins, and a join is not a thing —
it is the absence of a thing, and there is nothing to write a test *about* until
somebody notices which absence matters.

That is why they were invisible. Not because the tests were bad; because the
tests were tests.

## What the diagnostic is, and what it is not

`dossier selfcheck` is eight checks, each one written from a specific failure
above and each naming that failure in its `found_because`. Not a category
somebody imagined — I know exactly what each is for, because I broke it first.

**It is honest about its ceiling.** Its own docstring says the reading of a
green run is "none of the seven things that went wrong before have gone wrong
again". It cannot find the ninth. Nothing can, until the ninth happens.

**Its first run found a defect in itself.** Two tabs reported as unfilled —
`tab-overview` and `tab-details` — which fill themselves by yielding a panel
widget rather than a loader. A false positive on the first run of a diagnostic
is worse than the defect it hunts: it is the beginning of people waving it
through.

**And one of its checks was tuned tighter than its evidence.** The leak check
originally flagged every `importlib.reload`, reporting seven findings — four in
files that reload inside a `finally` and have been green through four randomised
full runs. I narrowed it to the mechanism that actually leaked: a module
attribute assigned and never put back. That is not softening a check to get
green. Softening would have been suppressing the finding; this was matching the
check to the failure it was written from, and saying so in the code.

## The mutation is the check

Seven guards, seven mutations, each observed to fire — including two across the
seam, where breaking `qmcp/config.py` turns the panel's diagnostic red.

**Two did not fire on the first attempt, and they failed differently.**

One was an insufficient mutation: `tab-sweep` is routed twice, so removing one
route left the other. The guard was fine and my test of it was not.

The other was a real hole. The network check asked whether `autouse=True`
appeared anywhere in `conftest.py`. It appears twice. Taking `autouse` off the
network fixture left the check green — a guard that would have reported the
suite protected while it was reaching the network again. It now reads the
syntax tree for that named fixture.

The distinction matters: `records/DRAFT-decision-record-discipline.md` §10 says
a guard is not finished until somebody has tried to route around it, and the
attempt has to be able to distinguish "my mutation was too weak" from "the guard
is". Both look identical from the pass line.

## The ratchet, which is the only part that improves anything

`qmcp/feedback.py` runs both self-checks as a pipeline. Running them repeatedly
finds recurrences. That is worth something and it is not improvement.

What makes the next run better than this one is `unratcheted`: failures that no
check was written for. A failure a check already covers is a recurrence — the
loop working. A failure nothing covers is a hole, found by hand or by a person
hitting it, and closing it means writing the check as well as the fix.

Today's queue is empty, which is the least interesting possible reading: it says
the eight known holes are closed and says nothing about the ninth.

**Nothing schedules it.** No cron, no timer. A loop that ran itself would be the
unattended thing `records/DRAFT-no-unattended-spending.md` is about, and the two
stages are subprocesses rather than agents — the model on this machine is local,
and most of what the loop does is a parser's work anyway.

## The thing I keep getting wrong

Three times today I reported a result from a pipeline whose exit code was
`tail`'s rather than the command's. Once it said `exit 0` over `1 failed, 741
passed`.

I have now written this down twice in two different repositories and hit it a
third time in between. It is not a knowledge problem. The fix that worked was
mechanical: write to a file, echo `$?` on its own line, read the file.

The general form — and the reason it belongs in a retrospective rather than a
note to myself — is that **a convenience in how a result is displayed silently
replaced the result**. `| tail` is presentation. It ate the exit status. That is
the same shape as everything in the table above: two correct things, and a join
nobody was examining.

## What I would tell the next session

Write the check when you fix the defect, not later. Every entry in
`diagnostics.py` exists because I had just been bitten, and the ones I would
have added "when there was time" are the ones that would have been guesses.

Mutate the guard, and when it does not fire, find out which of the two reasons
it was. I nearly recorded a working guard as broken and a broken guard as
working, in the same five minutes.

And run the suite in a random order. It cost nothing to install and it found a
leak on its first run that a fixed order had hidden through five full passes.
