# The video journey, and the step it lacked — 2026-11-19

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-11-19 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Code (Claude Fable 5.1), driving the session under review |

A session opened on `qm` to review the performing family, alfred, otto, joe,
vox and qmcp, as the route a video takes, and to build and test the part of
that route that categorises a long recording and finds the stretches of it
that stand alone for review. The work is on `qmcp`'s `feat/alfred-excerpts`,
unpushed under *keep everything local*, and
`handbook/handoffs/the-video-journey.md` is the handoff. This page is why it
went the way it did.

## The gap was established before it was built

**Assumption:** a family this far along has a step for this somewhere, under
some other name.

The five repositories were searched for the words such a step would use:
chapter, scene, segment, topic, highlight, summary, excerpt, clip. Every hit
was either otto's clip model, alfred's stretch-of-speech number on a word, or
a caption's segment count. Everything either side of the step existed: joe
answers segments with word times and silences; alfred keeps the words and
cuts a span by text; otto's timeline holds a sub-clip as an in-point and an
out-point; qmcp's render tool takes a raw timeline. The step itself did not.
Half an hour of reading saved a slice built beside something that already
did the job, which is the ordinary outcome of not looking.

## Which engine should own it was asked first

`records/DRAFT-build-the-seam-buy-the-engines.md` §3 orders the question:
which engine should own a capability upstream, before the seam takes it.
Span-finding from a transcript's timing is a few comparisons of seconds, and
no engine owns it; labelling by what is said is language, which no engine in
the family does, and the local model does behind a flag; the review loop and
the render are qmcp's already. So the step is seam logic and lives in a qmcp
flow. A route on joe would have made the engine decide what stands alone,
which is not a property of sound; a panel in alfred would have stacked above
alfred's open pull requests and reached nobody until they merge.

The placement was put to the person as one question with a recommendation,
beside the question *keep everything local* requires, and the answers were
taken as decisions. Nothing was built until both were in.

## The checks were evidence only after they failed

The suite for the new module went red on its first run in nineteen places.
Four were the checks themselves: a fixture with half the captions its
expectations assumed, a harness that split a request's id at a dash the run
id also carries, an expectation for a folded offset computed wrong by hand,
and a cut timeline that ran past the fixture's own duration. One was the
code: the opening of a span dropped a closing quote after its full stop,
which the test for openings caught and the fix restored. The walkthrough page
failed twice, both times on its prose rather than its code: once expecting
the whole first sentence where the function cuts an opening to a length, once
claiming a clip's own fade out stays where the span cuts the clip's end too.
A page that runs is a page whose prose is checked.

The counts that follow are from that session's runs and nowhere else: nineteen
red, then two, then none in the files the change touches.

## The scaffolding was part of the measurement, three times

**A nine-second video under a two-minute recording.** The first timeline
built to render a cut laid alfred's demo clip under the whole recording's
sound, which otto allows: a video shorter than its clip holds its last frame.
Cutting a span at seventy-seven seconds out of it put an in-point past the
end of a nine-second file, which otto refuses, rightly. The cut was correct
and the source was wrong. A full-length video made by looping the demo under
the sound, as a recording in alfred's library would be, rendered in a second,
and joe heard the span's fifty-one words in the clip, all of them.

**A background run that reported success over six failures.** The suite was
run in the background with its exit code appended to its own log, and the
task reported the exit code of the appending. The log's last line said six
failed. The async contract names this trap as a pipe replacing an exit code;
it is the same trap with a semicolon.

**A worktree named for its branch.** Three continuity tests resolve the
project from the clone folder's name, and a worktree called
`alfred-excerpts` is not on the roster. They pass on the clone. The three
reds were the folder, and the handoff says so rather than the suite being
called green.

## What the real run says, and what it does not

The recording was synthesised with the system voice: one voice, five parts on
distinct subjects, clean silences of the lengths the script chose. On that
input joe's silences were the script's pauses, the proposal's chapters were
the script's parts to the tenth of a second, and the local model's twelve
answers were right in eleven and empty in one. The ordinary cause of a result
that clean is an input that clean. A real show has music under speech,
applause, a room, and two people talking at once; whisper's segments and
silences will move, and the four defaults that cut the proposal have been
measured on nothing but this. The handoff asks for several real recordings
with their proposals kept before any default moves, which is what `qmcp`'s own
next phases ask of the voice loop. The empty title, a chapter of one sentence,
is one observation, and belongs to that pass rather than to a fix now.

The local model answered every prompt within its timeout, in sixty-eight
seconds for twelve, with no stall. One run says it can; it does not say it
will.

## The journey is longer than the slice

Nothing here has been rendered by alfred's worker: Docker Desktop was down,
so the steps were driven as functions, the way the walkthrough drives them,
against joe and otto alone. The flow reaches a live alfred through tools that
already drive it, and the handoff's first item is that run. After it, the
sound in the proposal, the editor showing what was proposed, and a clip as a
project of its own are each a decision by the seam rule before they are code.
