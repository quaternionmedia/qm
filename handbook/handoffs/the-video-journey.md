# Handoff — the video journey: a long recording offered as excerpts

**Stamped 2026-11-19.** `qm` `main` at `02fa287`; `qmcp` `main` at `8aece3e`;
`joe` `main` at `188a2cb`; `alfred` `main` at `7fff7ae`, its open stack at
`9bf5209`; `otto` at `51a1b0e`, vendored in alfred; `vox` `main` at `1721e6f`.
Every figure here was true at those commits and nowhere else. Re-derive before
acting on any of it.

**Keep everything local is in force** for the session that wrote this page
(`handbook/async-contract.md` §7). The qmcp branch below is committed and not
pushed, and no pull request is open for it or for this page. A session that
reads this does not push either as an oversight; it asks whether the rule has
been lifted, and lands them by §3 (f) when it has.

## 0. What the journey is, and what was missing

A video goes through alfred's four stages, Source, Edit, Render and Deliver.
alfred holds the project, its timeline and its captions; joe, reached through
vox, says what is said in the timeline's sound, word by word and when; otto
draws every frame and mixes the sound; qmcp drives alfred with its `alfred_*`
tools and puts each decision to a person on its human queue. alfred's
`docs/guide.md`, on its stack, walks that journey for one short video.

A long recording, a whole set, a talk, an interview, is one project, and what
is worth sharing from it is a few stretches that stand on their own. Between
the transcript and those excerpts there was no step: nothing in the five
repositories categorised a long transcript or found the stretches that stand
alone, though everything either side of that step existed. joe answers
whisper's segments with word times, silences, loudness and beats; alfred
keeps the words with a stretch-of-speech number and cuts a span by text;
otto's timeline expresses a sub-clip as a clip with an in-point and an
out-point; qmcp's render tool takes a raw timeline, so a sub-clip renders
without touching the project.

The step is placed by `records/DRAFT-build-the-seam-buy-the-engines.md` §3,
the ordering rule: which engine should own it upstream? Span-finding from the
transcript's timing is seam logic no engine owns; labelling by language is
nobody's engine yet, and goes to the local model behind a flag; the review
loop and the render are qmcp's already. So the step is a qmcp flow. A joe
route and an alfred panel were the alternatives put to the person, who chose
the flow; the alfred panel would stack above alfred's open pull requests and
cannot reach its `main` until they merge (`qm-queue.md` §4).

## 1. What is built, and where

Branch `feat/alfred-excerpts` of `qmcp`, in the worktree
`qmcp.worktrees/alfred-excerpts` beside the clone, cut from `main` at
`8aece3e`. Six commits, `6e187a4` to `763414c`, signed and not pushed: the flow, the
editor review's fixes (§4), a line length, the flow's output named an
excerpt, the onboarding naming the flow
([`docs-review-editing-by-what-is-said.md`](docs-review-editing-by-what-is-said.md)),
and the flow marking the project's timeline with its cues (below).

| Piece | Where | What it is |
|---|---|---|
| the steps | `qmcp/cookbook/alfred_excerpts.py` | `read_transcript` uses the captions alfred holds and transcribes only a project with none; `propose` cuts chapters at long pauses and spans at pauses and sentence ends within a length window; `label` titles chapters and sorts spans by a labeller, `local_model` being one over the OpenAI-style chat route; `excerpt_edl` cuts the project's timeline into an excerpt's own, each timeline clip re-timed as otto reads one, with no fade at a cut edge; `excerpt_captions` moves the captions into it; `queue_excerpt`, `review_request`, `approval_request` and `summary` as the other two alfred flows have them |
| the flow | `examples/flows/alfred_excerpts.py` | nine Metaflow steps over the module; the recipe `alfred-excerpts` in `qmcp/cli.py` and `qmcp_mcp.py` |
| the tools | `qmcp/tools/alfred.py` | `alfred_project` answers a project with its saved timeline and render settings; `alfred_render_enqueue` with `edl` takes a list of captions and a `caption_style`, burned in switched on |
| the checks | `tests/test_alfred_excerpts.py`, `tests/test_alfred_tools.py`, `tests/alfred_stub.py` (`add_project` takes an `edl`), `tests/test_examples_smoke.py`, `tests/test_qmcp_mcp.py` | the proposal, the cut timeline and the labeller alone; the tools against the stand-in; the flow file's steps end to end through a qmcp server and its queue, each way a run can end, each guard naming its mutation |
| the page | `walkthrough/12-a-long-recording-is-offered-as-excerpts.md` | runs under the ordinary test command |
| the docs | `docs/integrations/alfred.md` (the flow, the tools), `docs/tools.md`, `docs/setup/flows.md`, `docs/testing.md`, `docs/ROADMAP.md` | |
| the cues | `qmcp/tools/alfred.py` (`alfred_cues_set`), `qmcp/cookbook/alfred_excerpts.py` (`cues_of`, `mark`, the states), the flow's `_mark` | from `propose` on, the proposal is on the project's timeline as cues of the source `alfred-excerpts`: a cue per chapter and per span, each span's state following the run, so alfred's editor shows the run as it goes; an alfred without the route is printed and the run goes on |

**Branch `feat/synced-timeline` of `alfred`**, in the clone itself, cut from
`docs/excerpts-in-the-family` at `86a6708b` so that it lands above alfred's
open stack and that branch, at `a0109db3`, five commits signed and not
pushed. Above it, **`fix/host-run`**, at `9250d669`, four commits signed
and not pushed: the api's font check copes
without `fc-list`, `./al host` starts, reports and stops the api, a render
worker, the site and joe as processes on the host against a MongoDB, and
`docs/host-run.md` is that run, which this clone serves on 1732. Above that,
**`fix/no-caption-cap`**, at `a0f7a32b`, one commit signed and not pushed, is
the clone's checkout: no count bounds a project's captions or its words, the
first pull request of the round
[`the-algorithmic-layer.md`](the-algorithmic-layer.md) plans. In the clone and
not a worktree because what serves on 1732, the family stack or the host
run, serves the clone's checkout, and the lanes were built against it
live. The timeline is lanes on
one time axis, at one scale, in one box that scrolls sideways; alfred's
`docs/lanes.md` is the reference.

| Piece | Where | What it is |
|---|---|---|
| the lanes | `website/src/lanes/Lanes.js`, `lanes.scss` | the ruler, the clips (`#timeline`, unchanged, the tools' subject), the words and the captions, the sound's loudness, each clip's fades and opacity, and the cues, with one playhead down all of them; a press on a lane seeks, a word, a caption or a cue seeks to its start; the lanes draw what is in view, and the Text and Audio lanes redraw only when what they show changes |
| the arithmetic | `website/src/lanes/arith.js` | the ruler's ticks for a zoom, the view, the clips laid end to end, the envelope sampled over a clip's window no finer than a pixel, the fades as `chosenFade` reads them (moved to `ClipWindow.js` so the render request and the lane share one rule), the cues' rows; imports nothing of the page |
| the sound | `website/src/lanes/sound.js` | the engine's `peaks` and `silences` per library file from `GET /media/{name}/audio`, asked once per file while the page is open |
| the cues | `website/src/cues/store.js`, `alfred/core/models/cues.py`, `alfred/core/routes/cues.py` | a project's cues, `GET` and `PUT /project/{id}/cues`, a writer's `source` replacing its own and keeping another's; read again every few seconds while any cue waits; the whole-project update keeps them, and `too_many_cues` is the refusal |
| the loading | `website/src/OttoTimeline.js` | the captions, the words and the cues load once the session is confirmed, not only when the project opens: under the development bypass the session is confirmed after, and the words never loaded unless the Transcript panel was showing |
| the checks | `website/e2e/lanes-arith.spec.js` (Node), `website/e2e/lanes.spec.js` (the running stack, the lanes' data served), `screens.spec.js` (the docs' picture), `tests/unit/test_cues_routes.py`, `tests/integration/test_cues_api.py`, the route inventory, the ownership list and the refusal codes | |
| the docs | `docs/lanes.md` and its place in the nav, `docs/index.md`, `docs/guide.md`, `docs/api/index.md`, `docs/api/errors.md`, `docs/cookbook.md` (regenerated), `website/e2e/README.md`, `CHANGELOG.md` | |
| the library written to | `alfred/core/routes/media.py` | `POST /media`, a multipart upload kept under its own file name once the whole of it has arrived, refused for a name the library cannot hold, holds already (unless `replace=true`) or a size past the limit, each with its code; `DELETE /media/{name}` |
| the panels | `website/src/panels/Media.js`, `Templates.js`, `Tools.js`, `Timeline.js`, `layout/registry.js`, `default_layout.js`, `flow.js` | Media and Templates are two panels, and the timeline's tools a third beside the timeline, which takes its own panel's whole width; on a phone the tools are a row over it that gives way as the timeline does. Media filters a long list, shows each file's kind, adds files from this device by a picker or a drop with how far each has got, asks before replacing a file of a name the library holds, and deletes a file asked twice. A saved arrangement that lacks the tools gives way to the default, as one lacking the timeline did |
| the checks | `tests/unit/test_media_uploads.py`, the refusal codes' three cases, `website/e2e/media.spec.js` (the panel's uploads, the replace question, a refusal in the server's words, the three panels in their places), and every spec that reached the templates or the bin through the joint panel, which now reach them where they are | |
| the host run | `scripts/host.py` (`./al host`: `status`, `up`, `down`), `scripts/family.py` (`ensure_joe`, lent to it), `al`, `tests/unit/test_host.py`, `docs/host-run.md`, its links from `docs/start.md`, `docs/develop.md`, `docs/commands.md`, `docs/configuration.md`, `README.md`, `AGENTS.md` and the nav, `CONTRIBUTING.md`'s install line, `alfred/main.py` (`installed_fonts`, `checkFonts`), `tests/unit/test_fonts_check.py`, `tests/integration/conftest.py`, `CHANGELOG.md` | on `fix/host-run`: `./al host up` starts joe as the family does, then the api with its reloader, the worker on celery's solo pool and parcel's watcher with its reload server on loopback, from the checkout's own environment against `ALFRED_HOST_DB`, refusing first when the api's port answers, the site's is in use, there is no environment or `node_modules`, or nothing answers at the database; `./al host` says what answers and what started; `./al host down` stops what it started and leaves the rest. Where there is no `fc-list` the api says so at start and leaves the font list as it was, and the integration tier keeps the hook; `pdm install` names its groups, since the `docs` group is locked apart and pdm before 2.29 selects every dev group whenever one is named |

What a span is comes from the transcript alone: when the words were said and
whether a caption ends a sentence. Nothing in the flow hears the sound, so a
song the engine wrote no words for is a pause, and where it falls is a
chapter's edge. The defaults, a chapter at four seconds of silence, a span at
one, between ten and ninety seconds, are the module's constants and the
flow's parameters, and §3 (e) says what moving them waits on.

## 2. What was run, and what it said

A verification section, so bare counts belong here; each is one run at the
commits above, on one workstation.

**The suite, in the worktree**, `uv run pytest tests walkthrough -q`: the new
checks and the walkthrough page pass with the rest, bar three
`tests/test_cookbook_instruct.py` continuity tests that fail in any worktree
named for its branch and pass on the clone, because the check resolves the
project from the clone folder's name: 1798 passed, 12 skipped, 3 failed, at
`6e187a4` in the worktree. `uv run ruff check` is clean on the files the change adds;
the clone's `main` is not clean under it, and no workflow runs it.

**The journey on a real recording, with joe alone.** Docker Desktop was not
running, so alfred's dev stack and the containerised flow could not start;
the steps were driven as functions, as the walkthrough drives them. A 146 s
recording was synthesised with the system voice: five parts on distinct
subjects, with 1.6 s between paragraphs and 7 s between parts, standing for
songs. joe's media API, on an ephemeral loopback port checked by its OpenAPI
title, transcribed it with whisper's base model in 20 s, 32 segments, and
reported seven silences of a second or more, every one of them a pause the
script put there. `propose` over those segments made five chapters whose
edges are the five parts' edges to the tenth of a second, and seven spans,
each inside one part; the two stretches left out were the nine-second goodbye
and one stretch too short to join. The local model (`qwen2.5-coder:7b` over
Ollama, 45 s per prompt) labelled all twelve prompts in 68 s: every span's
category right (greeting, story, story, story, announcement, story, story),
four chapters titled sensibly, and the first chapter, one sentence long,
given no title at all.

**The cut, through otto and back through joe.** A full-length video was made
by looping a demo clip under the recording's sound, as a recording in
alfred's library would be. Span 5, the announcement, cut from a one-clip
timeline over it with `excerpt_edl`, rendered with otto in alfred's own
environment (`renderMultitrack`, 320 by 180) in one second; joe transcribed
the rendered excerpt and heard the span's 51 words, all 51 of them, in order.
otto there is on pydantic 1, otto's pydantic-2 change being stacked and
unmerged, so the timeline was built with `parse_obj`.

A first attempt cut the span from a nine-second demo video laid under the
whole recording: the in-point at 77 s named a moment the video did not have,
and otto would have refused it, rightly. The scaffolding was wrong and the
cut was right; the full-length video fixed the scaffolding.

**The gates, locally.** `uv run qmcp preflight --event pull_request
--base-ref main` in the qmcp worktree at `6e187a4`: 13 of 15 steps pass. The
test step's three reds are the continuity tests above. The signature step
reads the one commit as `E`, a signature this git could not check, while
`git log --format=%G?` in the same worktree reads it as `G`; the runner's
git finds no key to check it against, and the host verifies the signature at
the push. `uv run --extra preflight qm preflight` in the qm worktree: 45 of
47 steps pass. The slot step asks the host about a branch it does not have.
The documents index drifted by the two pages this branch adds; it was
regenerated with `ci/doc_status.py`, the states view with
`ci/doc_dashboard.py` and the loose-ends file with `ci/loose_ends.py`, each
alone rather than through the whole generator, which in a worktree without
the private companion writes private names (`qm-queue.md` §4). The docs
audit's two citation findings stand on `main` as well. The runner reproduces
no `uses:` step, runner image or secret.

**The review's fixes and the rename**, the commits after the first, ran the
excerpt tests, the page, the tool tests, the recipe lists and the examples
smoke test green in the worktree, and ruff clean on the files they touch. The
whole suite at `68dce45`: 1799 passed, 12 skipped, the same 3 continuity
failures. The preflight was not run again after `6e187a4`.

**Against a live alfred.** With Docker Desktop up, `./al family up` from
alfred's checkout at `9bf5209`, with `JOE_FFMPEG` naming ffmpeg in the
environment it starts joe with: a joe started without it answers every upload
503, which the flow reported as the engine's failure and ended the run asking
nobody, as it should. `./al family smoke`: 8 pass, 1 skip, the skip its sound
check reading the first few library files, which are the silent demo clips.
A project of one clip, the 146 s show, made through `POST /project`;
`uv run qmcp cookbook run alfred-excerpts --project-id <id> --label-with local
--categories song,story,announcement,greeting --deliver True` from the
worktree: the flow in its container reached qmcp on the host, had alfred
transcribe the timeline through joe (40 captions, 32 segments, done in about
twenty seconds), proposed five chapters and seven excerpts, titled the chapters
with the local model over the host's Ollama, and put excerpt 1 on the queue,
where it waits for a person. Through the tools alone, excerpt 5 was rendered
by alfred's worker at 1920 by 1080 with its 7 captions burned in and downloaded
through its signed link, 15.1 s of video and sound.

**The lanes and the cues**, at alfred `499abe8a` and qmcp `763414c`.
alfred's Python suite in Docker, `./al pt`: formatting and lint green, and
2059 tests passed, 9 skipped, 8 expected failures, 1 failed, the docs rule
that a page named for a timeline is a project's history on qm's site; the
page was renamed in the commit after, and that rule ran green on the host with
the other docs rules, 34 passed. The host's environment is on pydantic 1 and
cannot run the route tests, which is why the suite runs in Docker. The run at
the commit before had the cookbook stale by the two new specs, regenerated
with `node website/e2e/cookbook.js`, and four files unformatted, formatted
with the suite's Black. In Node, the lanes' arithmetic spec: 14 passed, with
the cut and follow specs 46. The browser gate, `npx playwright test` for the
`chromium` and `phone` projects against the family stack: 453 passed, 45
failed, of which 42 are the stack's, which runs with authentication skipped
and a real joe where the suite expects its stub, and 3 the change's: an empty
clip strip with no height, so a page with no project open called the timeline
hidden; the lane labels centred; and a word's text drawn at the usual zoom
into a box a few pixels wide. All three fixed, the editor's specs rerun: 216
passed, 4 failed, two the skipped authentication and two drags across the
Transcript panel's words. The same two drag tests with the website's sources
set aside on the same stack: the desktop one fails there too, the phone one
passes; the phone one was the lanes' height squeezing the panel into a
scroller, bounded since, and the final rerun of the lanes, transcript, phone
stack, appearance and flow specs: 90 passed, 1 failed, the desktop drag test
the baseline fails. The docs' picture was taken by the screens spec on the
running stack, and the journey's three by the shot script over alfred's own
Playwright, the pinned one having no Chromium here.

qmcp at `763414c`: `uv run pytest tests walkthrough -q` in the worktree, 1810
passed, 12 skipped, 3 failed, the folder-name continuity tests above; ruff
clean on the files the commit touches; `uv run qmcp preflight --event
pull_request --base-ref main`: 13 of 15 steps pass, the two reds the
signature step's `E` and the suite's three, as before. `uv run --extra
preflight qm preflight` in the qm worktree at `cc03056`: 45 of 47 steps
pass, the base and signature steps asking the host about a branch it does
not have, and `uv run qm docs check` finds no generated document drifted.

**The run marks the timeline.** The excerpt flow run again on the live
project after the server was restarted with the tool: its proposal is on the
project as cues of the source `alfred-excerpts`, read back from
`GET /project/{id}/cues` as 12, five chapters titled by the local model and
seven excerpts, the first `waiting` on the queue and the rest `proposed`, and
drawn in the editor's Cues lane, which `docs/journeys/pictures/editor-lanes.png`
shows. The run before it ended at its four-hour review timeout with its
request still on the queue, where it stays, unanswered, beside the new one.

**The panels and the library's uploads**, at alfred `a0109db3`. The
editor's browser specs against the family stack, the three panels in place:
first 36 failed and 250 passed, the reds the suite reaching the templates and
the bin through the joint panel, the layout tests measuring the tools inside
the timeline's region, a saved arrangement without the tools, which an
arrangement cannot do without, the phone's Source stage squeezed by a third
panel and its tools row holding its height, and the stack's own; the suite
pointed at the panels' places, the templates given to the phone's Edit switch
and the tools row let give way, the same specs: 4 failed, 267 passed, three
the baseline's or the stack's and one this page's own test reading a library
the page had listed before the file went up; then the affected specs: 126
passed. `./al pt`: formatting and lint green, 2075 tests passed, 9 skipped, 8 expected failures, after a run at the commit before had the upload limit's test reading a default bound when the helper was defined and a nameless part answered by FastAPI's own 422. The docs'
pictures were retaken by the docs project on the running stack, 31 passed and
the guide's walk skipped: it needs the suite's stub engine, so the guide's
eight pictures still show the joint panel until `./al recipes` runs on that
stack. `POST /media` and `DELETE /media/{name}` were tried on the live api
with curl: a file kept, the second send refused as `media_exists`, replaced
with `replace=true`, deleted, and the second delete a 404. A saved
arrangement from before the split gives way to the default once, which is
the existing rule for an arrangement lacking a panel the editor cannot do
without, and the live editor showed the eleven tabs after one reload.

**The run, walked to its end.** The queue's fourteen requests were answered
`approve` with `uv run qmcp human respond`, each as the run put it up. The
seven spans were rendered by alfred's worker at 1920 by 1080 with their
captions burned in, 2 to 7 each; the first was reported rendered after 293
seconds of following and the rest within 45 and then at once, the worker
having rendered them while the first was followed. Each was put to the
queue with its link and approved, and each delivered to `local`: seven
files in alfred's `deliveries/`, named by render id, 10 to 18 seconds long.
The run's last line counts 7 offered, 7 approved, 7 rendered, 7 approved as
excerpts, 7 delivered; the project's cues read back with every excerpt
`delivered` and its render id as `ref`; the editor's Deliver stage lists
each as `delivered → local`, and its Cues lane draws the seven green, which
`docs/journeys/pictures/editor-lanes.png` and `editor-deliver.png` show.
The run before it, whose request outlived its review timeout, is no longer
on the queue.

**The host run**, at alfred `63ddf30b`, with Docker's engine down: its
backend crashed at start on a stale socket file it could not rename, and a
second start hung at its WSL bootstrap. A MongoDB 8.0 on loopback 27018,
parcel's watcher on 1733, the api on 1732 with its reloader, the worker on
celery's solo pool and joe on 1059. `GET /openapi.json` says `Alfred API`;
`/health` reports the database, one worker and the audio engine ok; the
editor opens with the two seeded projects and the six-file library, no
console errors, and the Timeline demo's clips drawn in the lanes. The
first start failed in `checkFonts` on the missing `fc-list`; with the fix
the start-up log says so and the api starts. `./al family smoke` against
it: 6 pass, 3 fail, the three one cause, text templates without
ImageMagick (template preview 422, timeline preview 422, the render
failed building `title`). The unit tier on the host virtualenv, at the
lock with pdm 2.29: the docs, font-check, blocking-calls and task-runner
modules, 65 passed and 31 skipped; the font test red under its mutation,
an absent `fc-list` read as an empty list (1 failed), and green restored.
black and ruff clean on the changed files.

**`./al host up`**, at alfred `9250d669`, with the hand-started processes
ended first: joe started from its checkout on 1059, then the api, the
worker and the site, and the command's own lines named each address.
`./al host` reported the api answering as Alfred API, the site's port in
use, the database and joe answering, and four processes running from its
record; `/health` reported the database, one worker and the audio engine
ok; `./al family smoke` against it 6 pass, 3 fail, the same three as
above; the editor loaded from it with the seeded projects. The unit tier's
host, family, task-runner, loop and docs modules: 119 passed, 31 skipped,
black and ruff clean.

**Not run.** alfred's site built with mkdocs, whose nav and links the
suite's docs rules check in its place.

## 3. What remains, and what done looks like

The round after this page, an algorithmic layer over the editor as a Sculpt
stage between Source and Edit, is planned in
[`the-algorithmic-layer.md`](the-algorithmic-layer.md), which places (b) and
(d) below within it.

- **(a) Against a live alfred.** Run to its end, as §2 says: every span
  approved on the queue, rendered, approved from its link and delivered to
  `local`. What remains is `./al family smoke` extended to call
  `alfred_project` and to analyse a library file with sound wherever it
  sorts, and a run answered by a person reading each excerpt rather than
  approving them all.
- **(b) The sound in the proposal.** alfred serves the engine's analysis of a
  library file, its silences, loudness and tempo, at `GET /media/{name}/audio`
  (alfred's `docs/captions.md`, *Analysing library media*), and qmcp has no
  tool for it, so the proposal hears nothing: a song reads as a pause, and
  music under speech reads as speech. Done is an `alfred_media_audio` tool,
  then the silences and the loudness folded into `propose` beside the
  transcript's pauses, measured as (e) asks.
- **(c) The editor renders a selection as an excerpt.** The Transcript panel
  already turns a selection of words into a span of seconds
  (`Transcript.spans()`, `website/src/captions/transcript.js`) and cuts it out
  with **Cut**; a sibling **Excerpt** would keep only it, posting `/render` with
  the timeline cut as the flow cuts one, named for the project and the words,
  and Deliver would list it as the flow's excerpts are listed. That is the
  editor's half of this step, with no chapter view drawn: a person refines a
  span where the words are, by selecting. It stacks above alfred's open pull
  requests; done is that stack merged first (`qm-queue.md` §4,
  `hil-review-2026-10-31.md` §4), then the button as one pull request on it,
  and §4's rows 3, 5 and 10 each as one more.
- **(d) An excerpt as a project of its own.** An approved span could become an
  alfred project named for the recording and the span, with its captions,
  for the editor to refine; that needs a project-creating tool and a decision
  on where an excerpt's identity lives. Done is the record, then the tool.
- **(e) The defaults, measured.** The pause, chapter pause, shortest and
  longest are untested on a real show: music, applause and speech over
  music will move whisper's segments and silences. Done is the flow run on
  several real recordings with the proposals kept, before any default moves,
  as `qmcp`'s `docs/voice-loop-next-phases.md` Phase 6 asks of the voice
  loop. The empty title for a one-sentence chapter belongs to the same pass.
- **(g) The panels, further.** Media, Templates and the timeline's tools are
  three panels on `feat/synced-timeline` (§1), and the library takes uploads.
  What remains: the upload limit is a constant in `routes/media.py`, not a
  setting; a deleted file is not checked against the timelines that name it,
  so a render of one fails at otto's check rather than at the delete; the
  Media panel offers no way to hear or watch a file before it is placed, and
  the audio engine's analysis of a file (`GET /media/{name}/audio`) is drawn
  only once the file is on the timeline; and the guide's eight pictures still
  show the joint panel, since the guide's walk needs the suite's stub engine
  and is retaken by `./al recipes` on that stack. Done is each as a pull
  request on the branch's stack.
- **(h) The lanes, further.** A cue stays at its timeline seconds when an
  edit moves the picture, so the flow's cues describe the timeline as it was
  read; done is cues followed through `followClips` as the captions are,
  with the undo carrying them, and the flow re-reading the timeline when an
  excerpt is queued. The fades are read in the FX lane and not dragged; a
  dragged fade meets `chosenFade`, which reads exactly one second as none.
  The editor writes no cue of its own; a mark dropped at the playhead wants
  the following first. The Audio lane draws each file, not the mix. A lane's
  label covers the start of whatever sits at second 0 of that lane, a chapter's
  first letters for one.
- **(i) The host run, further.** `./al host up` does not start the
  database: a MongoDB must answer where `ALFRED_HOST_DB` points, and the
  page says how to run one from a folder. A text template's preview on a
  host without ImageMagick is refused
  as though its fields were missing (`preview/template`, 422): the refusal
  should name what the engine lacks. Fontconfig and ImageMagick on a host
  are the person's to install; the page says what each gives. Done is each
  as a pull request on the branch's stack.
- **(f) Landing, once keep-local is lifted.** Push `feat/alfred-excerpts`,
  open its pull request against `qmcp` `main` with the person who asked as
  assignee, run `uv run qmcp preflight --event pull_request --base-ref main`
  on the pushed branch, and merge it green; the recipe's description reaches
  `qmcp_mcp.py`'s list with it. This page's own pull request opens against
  `qm` `main` from `evolve/the-video-journey`. alfred's `feat/synced-timeline`
  opens against `docs/excerpts-in-the-family`, a draft until that lands, and
  retargets as the stack merges, and `fix/host-run` and `fix/no-caption-cap`
  above it the same way;
  alfred's suite runs in Docker, `./al pt`,
  and the browser gate from `website/` against the running stack.

## 4. The editor, as the excerpt flow meets it

alfred's editor was reviewed against the flow by its sources at `9bf5209`,
the top of its stack, and the screenshots its docs commit; the editor itself
needs the Docker stack, which was down, so nothing here was clicked. Each
row says what a person does, what the editor shows them, and where that
stands. The rows that are the flow's own are fixed on `feat/alfred-excerpts`;
the rows that are the editor's wait on alfred's stack, under §3 (c).

| # | A person | What they meet | Where it stands |
|---|---|---|---|
| 1 | reads a span's request by voice through joe's Voice window | the whole prompt spoken, every caption line of a span, up to ninety seconds of words read aloud | fixed: each request carries `context.spoken`, the question in a breath, which the voice adapter speaks in place of the prompt. The other two alfred flows read their links aloud and carry no spoken form |
| 2 | corrects a misheard word in the Captions tab while the review waits, then approves the span | the excerpt burned the words the flow read at its start | fixed: the captions are read from alfred when the excerpt is queued, as the caption flow reads them |
| 3 | opens Deliver to find the excerpts | renders newest first, the account's across every project, twelve rows shown; a run's excerpts arrive in reverse order, and a run of more than twelve pushes a project's other renders off the list | the flow's: excerpts are queued in span order, so the list reads last excerpt first. The editor's: no filter by project and no page past twelve (`VISIBLE_RENDERS`, `website/src/Stages.js`) |
| 4 | reads an excerpt's row in Deliver | the name `<project> - excerpt <n>` and, small and grey beside it, a description naming the project by its twenty-four-digit id | fixed: the description names the project and the chapter, and the label when there is one |
| 5 | wants to watch a rendered excerpt before approving it | the approval carries a signed download link; the editor's viewer shows the timeline and never a render, and Deliver offers Download alone | the editor's: a render is watched outside the editor, by downloading it, for every flow alike |
| 6 | wants to refine a span the flow proposed, in the editor | the Transcript shows paragraphs, one per stretch the engine heard, and selects words; nothing shows a chapter, a span or a time range, and the request names times the panel cannot take | the timeline's Cues lane draws each chapter and each span where it falls, coloured by where it stands, and a press on one puts the playhead at its start; what remains is §3 (c), a selection rendered as an excerpt |
| 7 | reads the word *clip* | the project card says `4 clips`, meaning items on the timeline, and otto's clip is the timeline's; a render named `clip 2` would mean an excerpt | fixed: the flow's output is an excerpt, in its names, its requests and its last line, and *clip* is the timeline's word in every repository |
| 8 | approves a span with no render worker running | Deliver says why a queued render is not moving (`RendererNotice`); the flow ends that excerpt `no renderer` after `--queued-timeout` | holds: both say the same thing |
| 9 | uses a phone | one stage at a time; Deliver's rows carry name, description, size, length and state in a narrow column | the editor's: a long description wraps; nothing hides it. Not seen on a screen |
| 10 | asks for help from the rail's line | the line under the rail and its **How?** name the four stages and never an excerpt or an assistant's request | the editor's: the *With an assistant* journey names what the tools do and not where their requests are answered |

What the review did not do: click anything, measure a phone, or watch a
person. Each row's claim is a reading of the code named in it, at the commit
named above.

## 5. Standing constraints

- **Keep everything local**, until the person lifts it: this branch, `qmcp`
  `feat/alfred-excerpts`, `alfred` `docs/excerpts-in-the-family`,
  `feat/synced-timeline`, `fix/host-run` and `fix/no-caption-cap`, and `joe`
  `docs/what-the-words-are-for`.
- **alfred's clone is checked out on `fix/no-caption-cap`**, the stack's top,
  which the host run serves on 1732 (`docs/host-run.md`), as the family
  stack does when Docker's engine is up; `docs/excerpts-in-the-family` has
  its worktree beside the clone. A session that wants the clone on the stack's top checks it out
  with the stack down, or serves another checkout on another port.
- **The family's joe needs `JOE_FFMPEG`** in the environment `./al family up`
  runs in, where ffmpeg is not on the `PATH`.
- **Never bind a default port.** joe ran on `--port 0` and was asked its
  title before it was trusted; the voice loop's joe is on 8000 and the
  family's on 1059. The host run's MongoDB is on 27018, so the stack's
  27017 stays free; its api holds 1732 as the stack's would, so `./al dev`
  refuses to start beside it and names it.
- **A worktree named for its branch is not the clone**: qmcp's continuity
  tests resolve the project from the folder's name and go red there.
- **alfred's host virtualenv is at `pdm.lock`**, pydantic 2 included, made
  with pdm 2.29 and the groups named, as `CONTRIBUTING.md` says; pdm before
  2.29 refuses the install.
- **A background run's exit code is the last command's.** Read the log's
  own summary line.
