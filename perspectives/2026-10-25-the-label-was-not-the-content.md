# The label was not the content — 2026-10-25

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-25 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

The session reviewed `qmcp` against what it says it does, and set up
integration testing that runs offline on the local model. It then restated
three rows of `qmcp`'s adoption record (#235), moved `qmcp`'s lock past 36
Dependabot alerts, cleared `qmcp`'s leftover branches and stash, and kept a
benchmark's results in #251. Most of what went wrong shared one shape: a
summary of a thing was read as the thing. A version line, a title, a commit
message and a log each said something true about its subject, but not the
thing that was needed.

Each finding below names the assumption before the fix, then the check that
would have caught it and whether that check exists.

## The lock said "Updated"

**Assumption:** upgrading the package an alert names reaches the version that
fixes it.

`uv lock --upgrade-package` for the ten advised packages printed `Updated
pydantic-ai v2.31.0 -> v2.32.2`. The fix for one of that package's alerts is
2.53.0. pydantic-ai 2.33 and later require anthropic 1.0 or later, and the
lock held anthropic at 0.122.0. uv kept that version and settled pydantic-ai
on the last release compatible with it. Nothing failed, and every line of the
output was true.

**Fix:** a one-off script that read each alert's vulnerable range against
the lock reported two packages still inside their ranges. The upgrade was
then widened to the providers and the OpenTelemetry family. anthropic moved
two major versions, and that move has been run offline only.

**The check** is that script, run before a dependency pull request. It does
not exist in `qmcp`, and `qm-queue.md` §4 now carries it.

## A scripted answer the model filled in

**Assumption:** a fixed, content-free outcome carries nothing forward.

The restart test (`qmcp` #114) first used `--runtime scripted` for the first
instruction. Its outcome is the fixed text "done, as scripted". The second
instruction, on the local model, paraphrased that history from the first
instruction's own wording: it "reported that the project builds
successfully". An assertion on that answer would have passed without the
history being needed at all.

**Fix:** the first outcome now names a commit that is nowhere in the clone.
With the brief built from no history, and the record still saying the first
instruction was carried forward, the model answered that it found nothing.
That red run is what makes the green one worth something.

**The check** was a mutation run by hand. It is described in `qmcp`'s
`docs/testing.md`, and nothing runs it.

## A title that named another version

**Assumption:** a Dependabot pull request's title names its diff.

`qmcp` #3 was titled "bump protobuf from 6.33.4 to 6.33.5", but its diff
changed 5.29.5 to 5.29.6. `qmcp`'s `main` already locked 5.29.6, so merging it
would have changed nothing. It had been open since February.

**Fix:** `gh pr diff` was read. The pull request was closed with that reason.

**The check:** none. Only a person reading the diff catches this.

## A stash whose message was right and whose diff looked wrong

**Assumption, made twice in opposite directions:** a stash's message says
whether its work landed, and a diff against `main` says the same.

The message said its work was "split into #79–#82 and merged". Its diff
against `main` touched 28 files, because the code had evolved after landing.
The first reading, from the diffstat, could not confirm the message and left
the stash alone. A name-by-name comparison then found that all 187 functions
and classes it added are on `main`, renamed or extended, except one design.
That design, a council that is always advisory, was replaced by #79's
separate advisory council, so it was abandoned rather than lost.

**The check:** none. Code that changed after landing never diffs clean, and
telling "changed after landing" from "never landed" is a reading, not a
lint.

## A benchmark that committed its progress

**Assumption** (the benchmark's own README): "the two logs are its output".

The logs listed the files each script processed. The scores went to a
terminal. The jargon-hint and real-take runs saved nothing at all. Their
conclusion survives only as a comment in `qmcp`'s `vocabulary.toml`. The
short-answer and confidence figures were recovered by scoring the committed
transcripts again with today's dialog code, and #251 keeps them.

**The check:** none. A benchmark is held to nothing. The habit that would
have prevented this: commit the numbers, not the file list.

## A fix on `main` that the branch's copy did not have

**Assumption:** the local runner in a checkout is the corpus's current runner.

#235's local run failed "The default branch carries no project records". The
runner had assumed the branch it was given was `main`, and passing `--ref`
cleared the step. #229 had already fixed that on `main`, 95 minutes before
#235 opened. But the run used `project/qmcp`'s copy of the runner, and
`project/qmcp` had not taken `main` since. Neither has `qmcp`'s governance
pin.

**The check:** none says which runner a run used. `qm-queue.md` §5 now
records that a project branch carries its own copy.

## Filed where an earlier page appeared, then force-pushed

**Assumption:** a perspective about `qmcp` goes to `project/qmcp`, because
`2026-09-28-the-voice-loop-meets-the-field.md` is on that branch. It is there
because `project/qmcp` took `main`, not because it was filed there.

**The check exists and caught it.** `namespace-guard.yml` refused "A project
branch's own commits touch adr/ only" in a local run, before the pull
request opened.

**A defect this session caused:** the fix was a rebase onto `main` and a
force-push of the already-pushed branch. No pull request was open on it yet,
but the corpus forbids force-pushing (`qm-queue.md` decision 3,
`handbook/handoffs/README.md`). A new branch name would have cost nothing.

**The check:** nothing on the host refuses it. `qm-queue.md` §3 records that
no ruleset is applied.

## A login guessed for the voice check

**A defect this session caused:** `check_pr_voice.py` was first run with a
`--contributor` login that was guessed rather than read from `gh api user`.
It passed. The check refuses only a mention of the login it is given, so a
wrong login silently removes that part of the check.

**The check:** `one-pr-check.yml` passes the pull request's author
(`--contributor "$PR_AUTHOR"`), so only a local run depends on the argument.
Nothing checks a local run's argument against the host.

## A run-file for a server that was gone

A run-file in `~/.qmcp/run` described a `qmcp serve` on port 3141 over the
checkout's queue, started 2026-10-24. Its process no longer existed. The
session could not establish who started that server, so this is not
attributed.

`qmcp/instance.py` says a run-file cannot tell a crashed server from a live
one, and that a collector must match the answer on the port first. **That
check exists** in `cookbook dev` (`qmcp` #110), and nothing else reads
run-files. The file was removed.
