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
`8aece3e`. Five commits, `6e187a4` to `701e7c6`, signed and not pushed: the flow, the
editor review's fixes (§4), a line length, the flow's output named an
excerpt, and the onboarding naming the flow
([`docs-review-editing-by-what-is-said.md`](docs-review-editing-by-what-is-said.md)).

| Piece | Where | What it is |
|---|---|---|
| the steps | `qmcp/cookbook/alfred_excerpts.py` | `read_transcript` uses the captions alfred holds and transcribes only a project with none; `propose` cuts chapters at long pauses and spans at pauses and sentence ends within a length window; `label` titles chapters and sorts spans by a labeller, `local_model` being one over the OpenAI-style chat route; `excerpt_edl` cuts the project's timeline into an excerpt's own, each timeline clip re-timed as otto reads one, with no fade at a cut edge; `excerpt_captions` moves the captions into it; `queue_excerpt`, `review_request`, `approval_request` and `summary` as the other two alfred flows have them |
| the flow | `examples/flows/alfred_excerpts.py` | nine Metaflow steps over the module; the recipe `alfred-excerpts` in `qmcp/cli.py` and `qmcp_mcp.py` |
| the tools | `qmcp/tools/alfred.py` | `alfred_project` answers a project with its saved timeline and render settings; `alfred_render_enqueue` with `edl` takes a list of captions and a `caption_style`, burned in switched on |
| the checks | `tests/test_alfred_excerpts.py`, `tests/test_alfred_tools.py`, `tests/alfred_stub.py` (`add_project` takes an `edl`), `tests/test_examples_smoke.py`, `tests/test_qmcp_mcp.py` | the proposal, the cut timeline and the labeller alone; the tools against the stand-in; the flow file's steps end to end through a qmcp server and its queue, each way a run can end, each guard naming its mutation |
| the page | `walkthrough/12-a-long-recording-is-offered-as-excerpts.md` | runs under the ordinary test command |
| the docs | `docs/integrations/alfred.md` (the flow, the tools), `docs/tools.md`, `docs/setup/flows.md`, `docs/testing.md`, `docs/ROADMAP.md` | |

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

**Not run.** An excerpt approved from its link and delivered to `local`,
which waits on the queue's answers.

## 3. What remains, and what done looks like

- **(a) Against a live alfred.** Run, as §2 says, to the first question on
  the queue, with one excerpt rendered by alfred's worker through the tools.
  What remains is a span approved on the queue, its excerpt approved from its
  link and delivered to `local`, which is a person's answers; and `./al family
  smoke` extended to call `alfred_project` and to analyse a library file with
  sound wherever it sorts.
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
- **(f) Landing, once keep-local is lifted.** Push `feat/alfred-excerpts`,
  open its pull request against `qmcp` `main` with the person who asked as
  assignee, run `uv run qmcp preflight --event pull_request --base-ref main`
  on the pushed branch, and merge it green; the recipe's description reaches
  `qmcp_mcp.py`'s list with it. This page's own pull request opens against
  `qm` `main` from `evolve/the-video-journey`. alfred's `docs/guide.md`, on
  its stack, counts qmcp's alfred tools as nine; with `alfred_project` they
  are ten, and its table gets the row when that page is next touched.

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
| 6 | wants to refine a span the flow proposed, in the editor | the Transcript shows paragraphs, one per stretch the engine heard, and selects words; nothing shows a chapter, a span or a time range, and the request names times the panel cannot take | the editor's: §3 (c), as a selection rendered rather than a view drawn |
| 7 | reads the word *clip* | the project card says `4 clips`, meaning items on the timeline, and otto's clip is the timeline's; a render named `clip 2` would mean an excerpt | fixed: the flow's output is an excerpt, in its names, its requests and its last line, and *clip* is the timeline's word in every repository |
| 8 | approves a span with no render worker running | Deliver says why a queued render is not moving (`RendererNotice`); the flow ends that excerpt `no renderer` after `--queued-timeout` | holds: both say the same thing |
| 9 | uses a phone | one stage at a time; Deliver's rows carry name, description, size, length and state in a narrow column | the editor's: a long description wraps; nothing hides it. Not seen on a screen |
| 10 | asks for help from the rail's line | the line under the rail and its **How?** name the four stages and never an excerpt or an assistant's request | the editor's: the *With an assistant* journey names what the tools do and not where their requests are answered |

What the review did not do: click anything, measure a phone, or watch a
person. Each row's claim is a reading of the code named in it, at the commit
named above.

## 5. Standing constraints

- **Keep everything local**, until the person lifts it: this branch, `qmcp`
  `feat/alfred-excerpts`, `alfred` `docs/excerpts-in-the-family` and `joe`
  `docs/what-the-words-are-for`.
- **The family's joe needs `JOE_FFMPEG`** in the environment `./al family up`
  runs in, where ffmpeg is not on the `PATH`.
- **Never bind a default port.** joe ran on `--port 0` and was asked its
  title before it was trusted; the voice loop's joe is on 8000 and the
  family's on 1059.
- **A worktree named for its branch is not the clone**: qmcp's continuity
  tests resolve the project from the folder's name and go red there.
- **otto in alfred's environment is on pydantic 1** until otto's
  pydantic-2 pull request merges.
- **A background run's exit code is the last command's.** Read the log's
  own summary line.
