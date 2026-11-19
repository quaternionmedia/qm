# Handoff — the docs, read for editing by what is said

**Stamped 2026-11-19.** `qm` `main` at `02fa287`, with this page's branch
`evolve/the-video-journey` at its tip; `qmcp` `main` at `8aece3e`, its
`feat/alfred-excerpts` at the tip [`the-video-journey.md`](the-video-journey.md)
§1 names; `alfred` `main` at `7fff7ae` and its open stack at `9bf5209`; `joe`
`main` at `188a2cb`; `vox` `main` at `1721e6f`; `otto` at `51a1b0e`, vendored
in alfred. Every page below was read at those commits and nowhere else.

**Keep everything local is in force** (`handbook/async-contract.md` §7): the
two branches this page names are committed and not pushed, and nothing here
is a pull request. The sentences in §3 are for the owner of the pages they
name.

## 0. The style of editing

A recording is heard by an engine, and the words come back with the moment
each was said. From then on the person edits by the words: deleting words
cuts the picture and the sound they were said over; choosing the stretches
that stand alone makes excerpts; captions are drawn from the same words; and
a person approves each step before anything is rendered or delivered. In this
estate joe hears, alfred holds the words and cuts by them, vox carries the
question between them, otto draws and mixes, and qmcp's flows put each choice
to a person. [`the-video-journey.md`](the-video-journey.md) is the step that
was missing and how it was built. This page is where a newcomer reads about
the whole, and what each page says.

## 1. Where a newcomer meets it

Each row is one page a newcomer passes, what it says at the stamp, and where
that stands: *holds* needs nothing, *fixed* is on one of the two local
branches, *proposed* is a sentence in §3 for its owner.

| Page | What it says | Stands |
|---|---|---|
| this site, `docs/index.md` | the performing family drives the video made before and after a show; nothing of how it is edited | holds: the front page names what, and a journey names how |
| this site, `docs/journeys/index.md` | three journeys: a clone to the first demo, bringing a set up, a model with an application; none through the editor | fixed: a fourth, [`cut-a-recording-by-what-is-said.md`](../../docs/journeys/cut-a-recording-by-what-is-said.md), the path through all five repositories, with its card and its place in the nav. It has no pictures: `uv run qm journey-pictures` takes them from a running stack, and this path needs Docker Desktop up |
| this site, `docs/projects/joe.md` | the lede is the host's repository description, *Realtime sheet music visualization* | proposed: a project with no pictures takes its lede from the host, since a `details` block in `ci/showcase.yaml` must name a picture the inventory knows (`ci/tests/test_cookbook.py`) and joe has none; the description is the owner's to set on the host (§3) |
| this site, `docs/projects/qmcp.md` | the lede is the host's description, *Quaternion MCP* | proposed likewise (§3) |
| this site, `docs/projects/alfred.md` | the lede says the editor; its *How a video gets made* steps say arrange, trim and cut, and nothing of the transcript | fixed: the Edit step names cutting by deleting words from the transcript, in `ci/showcase.yaml` |
| this site, `docs/families/performing.md` | drives a show, the video made before and after it | holds: the family record's words, generated |
| `qmcp` `README.md` | the role table's flow row: *alfred renders among them* | fixed: renders, captions, and a long recording cut into excerpts a person chooses |
| `qmcp` `docs/README.md`, `docs/roles.md`, `docs/setup/README.md` | each names the flow host by alfred's renders and captions | fixed: excerpts named in each |
| `qmcp` `docs/setup/flows.md` | the recipe commands, and no word of what the three alfred recipes do | fixed: one sentence each |
| `qmcp` `docs/integrations/index.md` | the alfred entry lists nine tools and two flows, and pages 10 and 11 | fixed: `alfred_project`, the excerpt flow, and page 12 |
| `qmcp` `docs/integrations/alfred.md`, `walkthrough/12-…` | the reference and the executable page | holds, on the branch |
| `alfred` `README.md` | *Make a video*: joe transcribes its sound, you cut it by deleting words, and otto renders it with its captions | proposed: the excerpts, in one clause (§3) |
| `alfred` `docs/index.md` | the Edit stage cuts the video by deleting words from its transcript; the family table's qmcp row says an assistant drives alfred through its tools | holds for the stage; proposed for the row (§3) |
| `alfred` `docs/guide.md` | the whole family walked for one short video; *Let an assistant drive it* lists nine tools and no flow | proposed: the tenth tool and the excerpt flow (§3); `the-video-journey.md` §3 (f) names it |
| `alfred` `docs/journeys.md` | *With an assistant*: list projects, transcribe and correct captions, render and deliver | proposed: one clause (§3) |
| `alfred` `docs/editing-by-text.md` | the rules of a cut, the words following the picture, undo and saving | holds; its complement, a selection kept rather than cut, is `the-video-journey.md` §3 (c) |
| `alfred` `docs/captions.md` | transcribing, editing by text, and the audio engine asked two things: a transcript, and an analysis of a library file | holds; `the-video-journey.md` §3 (b) names that route as the way the sound reaches the proposal |
| `joe` `README.md` | the audio engine of a video editor: what alfred uploads and what joe answers | proposed: what the words are for (§3) |
| `joe` `docs/paths/server.md` §2 | caption and analyse a video for an editor: words for captions, and beats, loudness and silences for cutting | proposed: one clause (§3) |
| `joe` `docs/media.md` | the audio engine of a video pipeline, every route | holds |
| `vox` `README.md` | the seam, naming no product by design; alfred's captions page links its media client | holds |
| `otto` `docs/timeline.md` | the in-point and the out-point, which is how an excerpt is cut | holds; otto's index names no editor, as an engine's should not |

## 2. What was fixed, and where

On `qm` `evolve/the-video-journey`: the journey page, with its glossary terms
linked by `uv run qm glossary-links`, its card in `docs/journeys/index.md` and
its line in `zensical.toml`; alfred's Edit step in `ci/showcase.yaml`, and the
project pages regenerated with `uv run qm cookbook docs/families --site
--write`, which changed alfred's page alone; this page and its row in the
handoffs index.

On `qmcp` `feat/alfred-excerpts`: the role table in `README.md`, the flow-host
lines in `docs/README.md`, `docs/roles.md` and `docs/setup/README.md`, the
recipes' sentences in `docs/setup/flows.md`, and the alfred entry in
`docs/integrations/index.md`, as one commit after the flow's own.

## 3. Proposed text, for the pages' owners

Each is one change to paste, written to the page's own voice. alfred's pages
are on its open stack, so each lands as one pull request above it; joe's are
on its `main`.

- **`alfred` `README.md`**, the *Make a video* paragraph, after *otto renders
  it with its captions*: `Or have qmcp offer the stretches of a long recording
  that stand alone, and render the ones you choose as excerpts of their own.`
- **`alfred` `docs/index.md`**, the family table's qmcp row: `an assistant
  drives alfred through its alfred_* tools, and its flows put each render, each
  transcript and each excerpt of a long recording to a person`.
- **`alfred` `docs/guide.md`**, *Let an assistant drive it*: the tool table
  gains `alfred_project`: `reads a project's saved timeline and render
  settings, which a timeline cut from it is cut from`, and a paragraph after
  it: `The alfred-excerpts flow reads the transcript alfred holds, cuts it
  into chapters at long pauses and spans at pauses and sentence ends, asks you
  about each span on qmcp's queue, renders each approved span as an excerpt of
  its own with its captions burned in, and asks you again with its link.
  qmcp's docs/integrations/alfred.md is the reference.`
- **`alfred` `docs/journeys.md`**, *With an assistant*: `…render and deliver,
  and offer the stretches of a long recording that stand alone as excerpts,
  each rendered once you choose it.`
- **joe's repository description on the host**, which this site's project
  page shows as its lede: `An audio workbench, and the audio engine of the
  video editor: it hears a recording and says each word and when it was said,
  and how the sound moves.`
- **qmcp's repository description on the host**, likewise: `The server an
  assistant works through: it runs the tools, holds the questions that wait
  for a person, and remembers each instruction it was given and what came of
  it.`
- **`joe` `README.md`**, *The audio engine of a video editor*, after *how it
  moves*: `The words are for captions, for cutting the video by deleting
  them, and for finding the stretches of a long recording that stand alone.`
- **`joe` `docs/paths/server.md`** §2, the opening line: `…and its beats,
  loudness, silences and waveform, for cutting and for finding the stretches
  that stand alone.`

## 4. What this review did not do

- Read alfred's pages as the site renders them: alfred's docs are served by
  its stack, which was down. They were read as files at the top of its stack,
  since its `main` holds none of them.
- Take the journey's pictures, for the same reason.
- Read any page a person has not reached: no newcomer walked these paths while
  the review watched.
The gates, locally, `uv run --extra preflight qm preflight` in the qm
worktree at `3ec7521`: 43 of 46 steps pass; the slot and signature steps ask
the host about a branch it does not have. The site rebuilt with the journey
page, 261 files, its links clean and the docs audit's two citation findings
the ones `main` carries. The CI tooling tests went red on two things that
commit had: a `details` block naming no picture, and the journey's glossary
terms unlinked; both are fixed in the commit after it, where
`uv run --extra dev qm test` passes whole: 2244 passed, 2 skipped, at `cbaafad`.
The runner reproduces no `uses:` step, runner image or secret.
