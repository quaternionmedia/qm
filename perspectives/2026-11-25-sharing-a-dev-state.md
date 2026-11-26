# Sharing a dev state: what was believed, and what held

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-11-25 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Code (Claude Opus 5.5), driving the session under review, wrote this page. No second reading was made of it |

One session assessed how a QM application can be shared in its development
state before alpha, with alfred as the test bed. It asked its questions one at
a time, recorded the answers as
`records/DRAFT-a-familys-dev-state-is-shared-to-invited-devices.md` (#355,
then #357), and built the first path for alfred as `./al share`, with a
joining guide for people with no technical background, open as
quaternionmedia/alfred#169 against `feat/who-spoke`. On the way it fixed the
local workflow runner twice (#358, #360). Figures here are of `qm` at
`866c097` and alfred's `feat/sharing-the-family` at `323448b`.

Each belief below is marked **established**, with how, or **inference**.

## The machinery to share alfred lives only on its unmerged stack

**Established**: `git show origin/main:dev.yml` publishes the api as
`8000:80`, on every interface, and `origin/main:al` has no `family`, `host`
or `share`.

Everything that makes alfred shareable at all, the loopback default, the
opt-in that widens it, the warning when the login bypass is on as well, the
family loop and the host run, sits on the stack that waits for an approving
review. So whatever alfred shares is shared from a branch head, and the
docs site's line telling a reader to open port 8000 is true of `main` and of
nothing anyone develops on. A share serving commits, rather than `main`, is
what this forces, and the record's manifest is how it is written down.

## A shared alfred was already running, and said nothing about itself

**Established**: `uv run qm instances --port 1732` listed 1732 and 1059 as
*held without a run-file*; asked, they answered `Alfred API` and `Joe API`,
and the process on 1732 ran uvicorn with `--reload` from the main clone's
working tree.

The workstation already shared alfred between sessions, by the rule that the
owning session starts it once. What it served was whatever branch that clone
had checked out, reloaded on every save, and nothing could say which commit
that was. That is the gap §3 and §4 of the record close for a share. The
check that would show it, `qm instances`, does see the port; it cannot see
the commit, and `./al share` does not yet write a run-file either, so the
share's ports read as unknown to it too. That is the next piece of work.

## The record claimed a property of the network before the network was chosen

**Established**: the Principle row as #355 merged it said no request to a
share passes through a relay somebody else runs. The network chosen was a
ZeroTier network, which relays packets through ZeroTier's own servers when
two devices cannot reach each other directly.

The sentence was written to contrast tunnels, from what a tunnel does, and
not checked against what the alternative it was praising does. #357 rewrote
the row and §1 in place: enrollment decides who reaches a share; relays carry
packets encrypted and decide nothing. No check reads a record's claims
against the product a project then picks; the reader is that check, and here
the reader was the session itself, a day late.

## Docker was not down; it was crashed

**Inference, then established.** The session read *daemon not reachable* as
Docker Desktop not running, started it, and waited. The backend's own log
said it had crashed at once: a socket left at
`%LOCALAPPDATA%\docker-secrets-engine\engine.sock` by an earlier crash could
not be renamed aside, and every delete without elevation answered Windows
error 1920. An administrator removed it, and Docker started in seconds.

The ordinary cause was the right first guess and the wrong one to wait on.
`docker info` answers the same way for a stopped engine and a crashed one;
the backend log tells them apart. No check in alfred's `./al` reads it, and
the dialog the crash raises offers a factory reset that would have taken the
engine's whole data disk.

## The runner could not run alfred's gates

**Established**: `run_workflows_locally.py` raised `TypeError` on alfred,
whose `CI.yml` is `on: [push, pull_request]`, and stopped before any later
workflow.

The runner's tests wrote every workflow with `on:` as a mapping, so the list
and single-event forms Actions accepts had never been read. #358 normalises
all three, with two tests that fail on the old code. The runner had been used
on alfred before only through stacked preflights that never reached `CI.yml`'s
turn, which is how a crash on alfred's oldest workflow went unseen.

## Smaller faults, all the session's own

- **A test's first red was its fixture.** The clone made for the unpushed
  commit test had nothing checked out, because its origin's `HEAD` named no
  branch; the code was right. Caught by reading the traceback before the
  code.
- **The escape-through-a-heredoc trap recurred** while extending the mutation
  script: a `\n` meant as two characters became a line break, and Python
  refused the file. It is recorded as a standing warning, and it still
  happened; the refusal, not the warning, caught it.
- **A guard without a recorded mutation is a draft.** Each of the share's
  fourteen guards was broken once and seen to go red, and each mutation is
  written beside its test in `tests/unit/test_share.py`.

## A local run of the gates rewrote the workstation's git identity

**Established**: after a pull-request run of alfred's workflows,
`git config --global user.name` answered `qm-bot`, and the global file's
modification time was the minute that run reached `docs.yml`. alfred's next
commit was authored by the bot.

The belief was that running the gates locally only reads. The runner executes
each step on the machine it runs on, with that machine's credentials, and it
read a step's `if:` but never a job's. So `docs.yml`'s push-only `deploy` job
ran on a pull request: its `git config --global` step rewrote the identity,
and its `mike deploy --push` step failed only because `mike` was not on
`PATH`. The fix in #358 is what let the run reach `docs.yml` at all; the
crash it fixed had been standing between the runner and that job.

#360 makes the runner evaluate a job's `if:` and skip any job whose condition
it cannot read; a test holds each half, and alfred's deploy job now reports
itself skipped. What does not exist yet is the guard that would have made the
job harmless even if it ran: steps executed with a scratch global git
configuration and home, so no step can write the workstation's. That is the
next piece of work. The same run rewrote `website/yarn.lock` and left a
`license-reports/` folder in alfred's checkout; comparing `git status` before
and after the run caught those, and the comparison was made for the first run
and not the second.

The mis-authored commit was on a pushed draft. It was rebuilt on a new
branch, every commit's patch id, message and author date checked equal, and
the draft closed with a line naming the replacement, as the queue's rule for
unsigned commits has it; nothing was force-pushed. Resetting the identity was
refused to the session, rightly: it is the person's.

## Joining a member found what the unit tests could not

**Established**: `./al share move looksatwords=main` failed with no
`pyproject.toml` in the share's clone.

A clone made without a checkout has `HEAD` at its origin's default branch.
`check_out` checked out only when `HEAD` differed from the commit, so a member
served at its default branch got an empty tree. alfred and joe were served at
feature branches, and the tests' repositories had no default branch, so
nothing had exercised the case. The fix checks out by force every time, and a
test builds exactly that clone and fails without it.

## The phone found what the desktop did not

**Established**, by opening the share's own address in a browser at a phone's
width.

- The footer's **User documentation** link answered 404: the share built the
  site and not the docs. The share now builds the docs from the served commit,
  with the image `./al prod` pins, and a test fails if the two images differ.
- alfred's login page offers **Create an account** and **Forgot password** on
  every server. On a share the first is refused and the second sends nothing.
  The joining guide says so; the page itself does not, because the site cannot
  tell that a server takes no registrations. That is alfred's next piece of
  interface work.
- Nothing in alfred's site needs a secure origin, which is what lets a share
  serve it over plain `http` on a private address. A feature that needs the
  camera or the microphone in the browser would change that.

## What the live run showed

At `323448b`: alfred, joe and looksatwords `serving`; alfred listening on
loopback and the share's network address only, the engines on loopback only,
the database nowhere; registration refused and `/users/me` answering 401; a
throwaway account made, logged in, snapshotted, deleted, restored and logged
in again, then removed with its snapshot. Not run: a second device reaching
the share over the network, because none had joined.
