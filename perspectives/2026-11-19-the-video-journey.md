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
and joe heard the span's fifty-one words in the excerpt, all of them.

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

## The timeline became lanes, and what that decided

The second ask of the session was the editor's timeline: synced text, audio,
clips, effects and queues. The decisions, in the order they were forced:

- **The clip strip stays the element it was.** Every tool and every browser
  test has `#timeline .clip` as its subject; the lanes wrap it rather than
  replace it, and a gesture on a clip is still the clip's.
- **One scale, one scroll box, one edge.** Every lane puts a second at
  `seconds x scale` pixels from the same left edge, and that is the whole of
  the synchronisation. A padding would have broken it, so there is none; the
  labels inherited centred text and sat in the middle of each lane, which the
  docs' own picture showed before a reader would have.
- **"Queues" was read as cues.** A lane of marked moments and stretches with
  a state, fed by the harness's queue through a route of alfred's own, so
  that alfred reads nothing from qmcp and the seam keeps its direction. The
  flow writes its proposal as cues of its own source, replacing its own and
  leaving another writer's, which is what lets the editor show a run as it
  goes without a second channel.
- **The sound is what already exists.** alfred served the engine's analysis
  of a library file before this slice; the Audio lane asks it once per file
  and draws each clip's window of it. The mix is otto's at render time, and
  the lane says so rather than drawing a guess.
- **Fades are read, not dragged.** The render request reads a fade of
  exactly one second as none, because older projects carry one nobody chose;
  a dragged fade would meet that rule at one second and vanish. Showing what
  renders was the honest half; the drag waits on the rule.
- **A cue does not follow an edit.** The captions and words follow the
  picture through one function; the cues could ride it, and the undo would
  have to carry them. That is a slice, not a corner, and the handoff names it
  rather than leaving it half-done.
- **Built in the clone, against the live stack.** The habit is a worktree per
  slice; the family stack serves the clone's checkout, and a lane is judged
  by looking at it, so the branch was cut in the clone and the handoff says
  where the clone now sits.

**What the gate said.** The browser gate against the family stack reported
forty-five reds. Most were the stack's: it runs with authentication skipped,
and every test that expects a refusal fails there, as do the ones that
expect the stub engine's words from a real joe. Three were the change's, each
found by a picture or a test and not by reading: an empty strip with no
height, so a page with no project open called the timeline hidden; the
centred labels; and a word's text drawn at the usual zoom into a box a few
pixels wide, which read as noise. A reader of the diff would have passed all
three.

**What was asked next, and done.** While the lanes were built, two more
asks arrived: the Media & templates panel split, with Media gaining ways to
act on a file and to upload one, and the timeline tools split from the
timeline. Both are panel splits in the same registry, and they were built
once the lanes were committed, as one more slice on the same branch. What
they decided: the library gains an upload route of its own, a multipart file
kept under its name only once the whole of it has arrived, rather than the
editor writing into `videos/` by some other door; a file of a name the
library holds is asked about, in place, not replaced; the Templates panel
sits on the phone's Edit switch and not on its Source stage, because a third
panel there left the project list one row, and arranging and titling is
Edit's work; the tools' row on a phone gives way as the timeline's region
did, down to one row that scrolls, because a row that held its height
squeezed the Transcript into a scroller and a drag across its words ran
away; and a saved arrangement from before the split gives way to the default
once, by the rule that already refused an arrangement lacking the timeline.
The suite's reds after the split were the suite reaching the templates and
the bin through the joint panel, which is what a split of a panel the tests
address by name costs, and one of them was this slice's own test reading a
library the page had listed before the file went up.

## The dev server went to the host

The stack came back after a reboot with Docker's engine down: its backend
crashed at start on a socket file the previous run had left, which Windows
would not rename or delete under the tools tried, and a second start hung at
the WSL bootstrap. A quarter of an hour went on that before the person asked
why the stack was being repaired at all, when the machine runs alfred
itself. Nothing in alfred's docs said it could: Get started lists Docker as
what you need, and the contributor guide's host instructions cover the test
suites.

The host route existed in the code and not on a page, and each gap in it
was small and undocumented: pdm's install, which refuses the lock unless the
groups are named; the site's poller, which spawns `npx` as a program Windows
does not have; the font check, which took the api down on a host without
`fc-list`; and text templates, which moviepy draws with ImageMagick. The
first is a line in the contributor guide, the second a different watcher,
the third a fix, and the fourth a row on the page. The page is
`docs/host-run.md`, and `./al family smoke` runs against the host as it does
against the stack, which is how the page knows what the host lacks.

The lesson for a session is the person's: when the documented route is
blocked, say so and ask before spending the time on the tooling that blocks
it. Repairing a vendor's socket file is not the work.

## The journey is longer than the slice

The first run of the session rendered nothing with alfred's worker: Docker
Desktop was down, so the steps were driven as functions, the way the
walkthrough drives them, against joe and otto alone. With the stack up the
flow reached a live alfred through the tools that already drive it, and at
the session's end a run was walked to its last line, every excerpt approved
twice and delivered. That walk approved everything, which proves the path
and not the judgement; a person reading each excerpt is the run that would.
After it, the sound in the proposal, a selection rendered from the editor,
and an excerpt as a project of its own are each a decision by the seam rule
before they are code.

## A count stood where a bound belonged

The first long recording put through the host run transcribed to the end and
was then refused by alfred itself: more captions than a project may carry.
The count had been chosen as a guess with a reason beside it, a thousand
being well over an hour of speech, and the reason was true of the recordings
the editor had met until then. What the count stood for was something else,
the size of the document the database will hold, and that it never measured.
So the guard enforced the guess and not the bound, and it did so after the
engine had spent its whole run on the sound: the cost of a number in code is
paid at the moment it is finally wrong, and by then everything upstream of it
has been done. The fix removed the counts on captions and words rather than
raising them, since a raised count is the same guess with a later expiry, and
left the document's own size as what bounds a project. The lesson is the one
the corpus states for prose, applied to a constant: a number in code that
stands for a quantity it does not measure is a claim with an expiry date,
and the tests that held it in place proved only that the guess was enforced.

## The round that followed the plan

The plan page was written one session and built the next, as eight branches
stacked above the one that took the count off. What the page could not
know, the build found, and each finding was of a kind the corpus already
names.

The engine's cap met the raw file first. The plan sent a library file to
the audio engine as it stood; the long recording is over the gibibyte the
engine takes in one upload, and the transcription had only ever passed
because it sends a mixed WAV. So a video's sound now goes to the engine
alone, as otto writes it, and the analyses are kept beside the library,
since an api that restarts on every edit, and a worker that never asked,
would otherwise each measure the recording again. The lesson is the one
from the count a session before, met from the other side: a limit stated by
the engine, not by alfred, and a code path that had never carried the
largest thing it would be given.

The scaffolding stalled twice, and each time the first reading was wrong.
The api's reloader announced a reload and kept serving old code for an hour
of edits: not a failed import, which the log would have shown, but a
browser tab streaming the recording from the api, which the reloader waited
on for ever. The site's watcher died on a temporary file of its own. A
browser pane showed the old bundle after a hard reload, because the dev
build keeps one file name whatever its content. None of these was the
change under test, and each one looked like it until the ordinary cause was
named: the reloader got a bounded wait as a branch of its own, the watcher
was restarted by hand, and the bundle was fetched past the cache.

The fixtures did the work the twin needed. The browser's cut arithmetic
and alfred's are one set of recorded cases, read by both suites, and the
mutation that dropped the shift after a cut reddened eleven cases on each
side. What the fixtures cannot do is choose themselves: they were recorded
from the implementation that had tests, once, and are the contract from
then on; a recorder in the repository would have let a regression on one
side rewrite them.

The built-in recipes are code, not seed. The plan said seeded, as the
announcement project is; built, a seeded copy in every account would have
put the advice's first values, held until they are measured, into every
account's own document, where a later measurement could not reach them.
Held in code and read by name, a changed value is one edit, and an account
that wants its own stores a copy.

The second half of the brief arrived mid-build. Speaker highlighting and
text updating over the transcript were asked for while the recipes were
being written, and they fitted the ordering rule without a change to it:
reading prose is looksatwords' charter, so alfred reached it by its
conversation route as it reaches the audio engine by vox's contract, named
nothing of it but two routes, and kept the reading by what was read. The
engine answered the whole recording in seconds, which the plan had not
measured and would have guessed longer.

The settlement moved what the build had changed the ground under. Of the
plan's eight proposals, five were taken as written and three were not, and
each of the three had the same cause: a fact the page was written without.
The labeller was to be the first thing that named a draft; by the time the
person settled it, the language engine already read the topics live over
every span, so a title comes from the reading first and the chat route is
kept for what the reading cannot give. The `speakers` operation was to wait
on the audio engine hearing speakers apart; the transcript's words carry a
speaker a person names, so it reads those, and the engine's hearing names
the rest when it comes. A recipe was to be written through the API only,
with the stage setting knobs; seen on the stage, the gap between setting a
knob and changing a step was one panel wide, and a round was added for it.
The plan asked its questions early, as the page says it should; the build
answered one of them and reopened two before the person reached them, which
is the ordinary course, and the reason the questions were written down.

Two of the rows the settlement added were built the same afternoon, as
parallel branches off the stack's top, since neither needed the other. The
title rule was chosen from the data before it was written: the engine's
points over the long recording fall at whole seconds, most of them within
ten of the next, so a window of ten seconds usually holds a few, and the
topic whose points within the span weigh most is the title; on the first
live run eight windows of ten were titled and two held no point at all,
which the rule leaves with the recipe's name rather than reaching outside
the span for a guess. The cues' count went as the captions' had, and what
replaced it was the one refusal the earlier removal had described and not
written: the database's own refusal of a document past its size, caught at
the two routes that write captions, words and cues and answered with its
sentence, which names the size. The second branch's tests ran in a worktree,
as the habit is, in a folder named for the project and not the branch, since
the continuity tests read the project from the folder's name, which the
section above on scaffolding had already recorded; this time it was read
before the suite ran rather than after.

The last two rows of the round, the recipe editor and the flow over the
drafts route, were built the same evening, and three things the scaffolding
did were read before they were believed. The api's reloader stalled again
after a branch switch, with the bounded wait from earlier in the round on its
command line: the log said it was reloading and a route the file plainly had
answered 404, which is the shape the earlier stall had, so the flag is
recorded as not bounding it and the restart as the route, rather than the
reload being trusted because a fix for it had landed. The browser pane's own
page stopped populating after that restart while a fresh browser against
the same server rendered everything, and the pane was set aside as the odd
instance once a token-less probe from a fresh browser had shown the server
and the bundle sound; what the pane was doing is not known and is written
down as not known. And the one earlier browser case that went red did so at
the Source stage, where it looks for a draft group that the project list no
longer reaches: the host run's database had grown past what the list
answers by default, a cap the demo itself had filled, which the plan now
names as a round of its own rather than a flake. The flow's rewrite retired
qmcp's cut arithmetic into alfred, as the seam rule had placed it a session
earlier; what the stand-in alfred keeps is an arithmetic of its own, for
leaving drafts that look like alfred's, and the page that runs it says so,
so nobody reads a stand-in's cut as alfred's.

The round's last rows went the way the corpus says a round goes, and two of
them were read before they were believed. The scene measure's first live run
through the worker left six drafts and a note that no cut had been measured,
while the api had measured thirty a minute before: the measure was kept and
read, and the recipe's source was never given it, a gap of one line that a
green unit suite had not covered because no test asked the run for its
cuts; the note in the job was the finding, and the test that asks is the
fix. The measuring instrument of (k) read the host run's database and
reported one hundred and fifty-five drafts held and none dropped, which is
true and says nothing about the recipes: no draft had been dropped through
the route before the record began, and the drops the demos made were a
session's, not a person's. The figures are on the page with their commit
because that is where a figure belongs, and the sentence beside them says
they measure the instrument's reach and not the defaults. The links into
the family's other programs took a setting of their own, the page a browser
opens rather than the address the stack calls, because the two differ
inside Docker and nothing in the health report said which was which; the
engine's conversation id was the one thing the reading had not kept, and
once kept it was the whole of the link. joe's half of hearing speakers apart
went to a session of its own, in a worktree beside joe's clone, on the
person's word, and its vox changes sat in the checkout alfred imports while
it worked, which turned one of alfred's suites red on settings alfred had
not read an hour before; the red was read as the checkout before it was
read as the change.

That session's hand-back was read as a report and not as proof: its two
commits were found where it said, its sixteen speaker tests were run again
here and passed, and the vox checkout was put back at alfred's pin, at
which alfred's suite went green again. What it built was calibrated on the
machine's two system voices and shifted copies of them, since no recording
with two known voices was to hand, and it said so with the margin it
measured; that is the shape of every default in this round, a first value
held until a real recording measures it, and the page carries it as one.

Taking the turns to the words was the shortest row of the round and the one
that reached furthest: the engine's letters sit on the words exactly where a
person's names sit, so the transcript's labels, the language engine's
reading and the `speakers` operation all took them without a change, and a
person renames a letter the way they name a paragraph. What it cost was
honesty about the engine's borders: each file is lettered on its own, so a
timeline of several files prefixes the letters, and the page says so rather
than pretending A is one person across files. The first naming of the long
recording took the engine's time whole, since nothing had asked it for
speakers before, and the route says that a second ask is quick because the
answer is kept, which is the same shape as the measures a session earlier.

The last two rows closed on the 22nd, and the second of them has a
retrospective of its own, `2026-11-22-the-first-reading-of-the-instrument.md`: the labeller sits behind a
route of the shape the family already serves and alfred names no model,
which kept the vendor out of the code as the plan said it would; and the
instrument's first reading over two real recordings held no person's choice
and one count that described the instrument rather than the recipes.
