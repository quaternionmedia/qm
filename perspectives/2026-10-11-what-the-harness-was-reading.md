# What the harness was reading

**2026-10-11.** Consolidating the performing family and testing ShowMidi's
reconnect. Attributed, dated, binds nothing.

Tools: Claude Opus 5.5, which made the mistakes described and wrote this page;
reviewed and committed by a human.

Five findings from one session. Each began as a reading of a check that looked
right, and in each the check was answering something else.

## A docs check passed on a tree the commit did not hold

**Assumption:** `qm docs check` passing in the clone meant it passed on the
commit just made.

The merge regenerated more documents than were committed. The cookbook stayed
regenerated in the working tree, uncommitted, so the check read the tree and
passed. The commit failed the same check, and a pull request body said it
passed.

**Would have caught it:** a clean `git status` asserted before any gate is
quoted. That is `AGENTS.md` item 12, unapplied. No mechanical check exists.

## A watcher read the log nothing wrote to

**Assumption:** the server's console log carries its dispatch lines.

They go to `show.log`. And the mapping waited for note 60, while the
Launchkey's C at its default octave is note 48. A pressed key and a dead input
produced the same silence, so the first hand test could not tell them apart.

**Would have caught it:** proving the input before unplugging anything. The
watcher now maps every note and CC and reads `show.log`, and the hand-test
steps start with a key press that must register.

## A recovery check measured a different defect

**Assumption:** after a burst of flaps, a fresh plug tests recovery.

When the last unplug was shorter than the reconnect interval, the fresh plug
landed inside it. So the check measured the fast-replug limitation, not
recovery. One run reported a regression the code did not have.

**Would have caught it:** waiting for the disconnect to be seen before
replugging. The harness now does.

## An install went into another project's environment

**Assumption:** a tool run inside a worktree installs into that worktree.

`VIRTUAL_ENV` pointed at the corpus clone's `.venv`, and pdm honoured it. A
member's packages, and older versions of the corpus's own, landed in the
corpus's environment.

**Would have caught it:** the harness now sets `UV_PROJECT_ENVIRONMENT` for
members. Nothing guards the shell variable itself; that is open.

## A hypothesis was offered before it was tested

**Assumption:** a cookbook that differed from a scratch worktree was an
artefact of where it ran.

It was the same uncommitted regeneration as the first finding, seen from
another side. The test that settled it ran the branch from both locations; it
should have come before the explanation.
