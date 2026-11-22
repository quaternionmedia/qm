# Handoff — the algorithmic layer: from a long source to drafts, by recipe

**Stamped 2026-11-22.** `qm` `main` at `2617723`; `alfred` `feat/who-spoke`
at `e56b386e`, the top of eight branches stacked above `fix/no-caption-cap`
at `a0f7a32b`, with `feat/no-cue-cap` at `e73e5b42`, `feat/topic-titles`
at `bfcb0526`, `feat/recipe-editor` at `c9b92d4c`, `feat/scene-cuts` at
`d26c9784`, `feat/drafts-measured` at `bb5a969d`, `feat/open-in` at
`993bfc9e`, `feat/speakers-to-words` at `af0941b6`, `feat/trim-captions` at `5d4f062c` and `feat/fluid-tools` at `d8aa98dd` each cut from it, and `feat/labeller` at `0fc7b9aa` cut from `feat/topic-titles` (§5); `otto` `feat/scenes` at `0b0f558` above
its `feat/motion` at `eac657d`, which `feat/scene-cuts` pins; `looksatwords`
`feat/open-by-link` at `aeb22b6` above `test` at `7d9089d`; `qmcp`
`feat/alfred-drafts` at `6ee6d44`, cut from `feat/alfred-excerpts` at
`763414c`; `joe` `feat/speaker-turns` at `b2c0d00` above `main` at
`188a2cb`; `vox` `feat/speakers` at `588c09b` above `e630cb0`, which
`feat/speakers-to-words` pins and the rest of alfred's branches do not. Every figure on this page was true at
those commits and nowhere else; re-derive before acting on one.

This page is a plan: the round of feature work that takes alfred from an
editor a person drives by hand to one with an algorithmic layer over it. In
the editor the layer is a stage of its own, **Sculpt**, between Source and
Edit: Source brings a long recording in, Sculpt runs the algorithms over it
and leaves drafts, and Edit refines a draft by hand. The page
builds on [`the-video-journey.md`](the-video-journey.md), where the first step
of that layer, qmcp's `alfred-excerpts` flow, stands, and it carries the shape
of the layer, where each part of it lives, the pull requests in order with
what done looks like for each, what the person settled and what the round
leaves out. Of the work it names, every row, §2 (a) to (o), (j) in otto,
joe, vox and alfred with the words named by joe's turns, is built, each as a
local branch that is a pull request to open once *keep everything local* is
lifted; the first reading of (k)'s instrument over two real recordings is
taken, with no person's choices in it, so no default has moved
(`perspectives/2026-11-22-the-first-reading-of-the-instrument.md`). The built part runs on the host run (`docs/host-run.md`) over the
long recording: §6.

## 0. What the round is for

The person's brief: *take a long source, configure a few algorithms to filter
and edit it, and be left with drafts of several potential exports to refine
by hand*, with *a Sculpt step before Edit* where those algorithms run. On
what to take from a recording of a show, the person brought a collaborator's
advice: prioritise the sections with longer dialogue, even with a few breaks
in them, since talking holds the most interest; then look for spikes in the
dialogue's volume that happen at the same time as more motion than usual on
screen, which usually mark an exciting moment or a funny mishap; start with
clips of eight to twelve seconds, and from a recording of an hour and a half
to two hours shoot for about twenty-five of them, a count with a little
buffer built in. Three nouns carry the brief, and the advice is the first
recipe, §2 (e).

- **A source** is a project whose timeline is long: a recording of a show, a
  talk, an interview, a session. alfred holds it as any project, with its
  transcript as captions and as words timed one by one, and the audio
  engine's analysis of each file on its timeline.
- **A recipe** is a chain of algorithms over the source's timeline, words and
  sound, configured by a few knobs: steps that find the structure
  (*segment*), keep or drop stretches (*filter*), change the timeline
  (*edit*), and assemble a result (*compose*). A recipe is data a person
  chooses and sets, not code a person writes.
- **A draft** is what a recipe leaves: a project of its own, cut from the
  source, carrying its captions, its words and the record of how it was made.
  The editor opens it as it opens any project, and the person refines,
  renders and delivers it as they do any other.

What exists for each, at the stamp:

| For | What exists | Where |
|---|---|---|
| the source | a project's timeline; its captions and its words, each word with the stretch of speech it was heard in; the engine's analysis of each library file's sound: silences, the level over time (`peaks`), one loudness figure, tempo, beats and onsets, in the file's seconds; of its picture, nothing but its size, rate and length; cues on the timeline, drawn in a lane | alfred: `GET /project/{id}`, `/captions`, `/captions/words`, `GET /media/{name}/audio`, `/cues`; `otto.media.probe`; `docs/lanes.md` |
| the recipe | one chain, as a flow's parameters: chapters at long pauses, spans at pauses and sentence ends within a length window, titles and categories from the local model; and, as a precedent for a timeline made from data, a form project's `logic`, json-logic over its `fields` | qmcp `qmcp/cookbook/alfred_excerpts.py` (`propose`, `label`); alfred `docs/about/project.md` |
| the draft | a span cut to a timeline of its own, with its captions moved into it, rendered as an excerpt: a render, not a project, with no words; in the editor, stretches cut out of a timeline with the words and captions carried through, in the browser alone | qmcp `excerpt_edl`, `excerpt_captions`; alfred `website/src/ClipWindow.js` (`cutRanges`, `followClips`) |

The gaps between them are the round. Nothing turns a source into projects a
person refines; no algorithm hears the sound, so a song reads as a pause; the
only place to configure the chain is the flow's command line; the arithmetic
of a cut lives in the browser and the arithmetic of an excerpt in qmcp, and
neither can call the other; nothing scores a stretch, so the two signals the
advice names, how much is said and a spike in the level with motion at the
same second, are read by nothing, and the picture's motion is measured by
nothing in the family; and a long source met a count the day this page was
stamped, §2 (a).

## 1. The shape

```
source project
  │  read: the timeline, the words, the captions, each file's analysis of its sound and its picture
  ▼
segment   candidate windows of a length range, snapped to word edges · chapters at long pauses · sentences · silences · scene changes · speaker turns
  ▼
score     how much is said in a window · a spike in the level with more motion than usual at the same second · a title, a category or a score from a model
  ▼
filter    the top so many windows that do not overlap · by length · by a silence's length · filler words
  ▼
edit      cut ranges out (tighten the pauses, drop the fillers) · excerpt a span as its own timeline
  ▼
compose   one draft per window · one per chapter · the top windows to a target length · the whole source, tightened
  ▼
drafts    projects, each carrying its source, its spans, its recipe and its scores; cues on the source
```

**Where each part lives** is answered as `records/DRAFT-build-the-seam-buy-the-engines.md`
§3 asks: which engine should own it upstream, before the seam does.

| The part | Who owns it | Why | At the stamp |
|---|---|---|---|
| hearing the words, the silences, the level over time, the beats | joe, through vox's contract | the audio engine | built: `peaks` is the level over time, `loudness` one figure per file |
| telling speakers apart; music from speech | joe | the engine that hears; nothing in the family does either | built, §2 (j): joe's `speakers` feature letters each turn's voice, and vox's contract carries it; music is not told from speech, and a sustained tone is lettered as a voice; the `speakers` operation reads the speaker each word carries and does not wait on it, §3 item 7 |
| motion in the picture over time, and scene changes | otto | the engine that reads frames, with the ffmpeg `otto.media.probe` runs | built, §2 (d) and (j): `otto.media.motion` and `otto.media.scenes` |
| a title, a category, a score for how well a stretch stands alone | a title from the topic the language engine has live over the stretch; a category and a score from the local model, reached by a contract that names no model, as vox's does | the reading already carries the topics; language is nobody's engine in the family | built, §2 (h): `ALFRED_LABELLER_URL` and `ALFRED_LABELLER_MODEL`, `utils/labeller.py`, over the chat route qmcp's `localmodel` stands up; the flow's labeller, in qmcp, over the same route |
| who spoke, which topics were live and when, where the talk went off and whether it came back | looksatwords, the language engine, reached by its conversation route | reading prose is its charter, and its border with codecartographer says so | built, §2 (l): `ALFRED_LANGUAGE_ENGINE_URL`, `utils/language_engine.py` |
| the arithmetic: windows and segments from times, the scores from what the engines measured, filters, a timeline cut, the words and captions carried through | alfred, the seam | it owns the project, the timeline, the captions and the words, and no engine should; a score is arithmetic over the engines' measurements | built, §2 (b) and (e): `utils/cut.py` and `utils/sculpt.py`, the browser's copy held equal by shared fixtures; qmcp's `propose` and `excerpt_edl` are retired by (i), and the stand-in alfred in qmcp's tests keeps an arithmetic of its own that claims nothing of alfred's |
| recipes as documents; drafts as projects with their provenance; the job that runs a recipe | alfred | lifecycle state is the seam's | built, §2 (e) and (f) |
| the review of each draft by a person, the run and its record, delivery | qmcp, the flow | its queue, its record | built, over alfred's drafts, §2 (i) |
| choosing recipes and their knobs; reading and dropping the drafts | the editor, on a Sculpt stage between Source and Edit | where the person is | built, §2 (g) |

The plan takes four positions, and §3 puts each to the person with its
alternatives.

1. **A draft is a project.** Only a project's timeline is editable; a render
   is an output and a cue is a mark. A draft carries `source`: the project it
   was cut from, the spans it took, the recipe and the values it ran with, and
   the scores it was chosen by.
2. **The arithmetic belongs to alfred, once, in Python**, with the browser's
   `cutRanges` and `followClips` held equal to it by one set of fixtures both
   run, and qmcp's `propose` and `excerpt_edl` retired into it, reached
   through a route and a tool.
3. **A recipe is data alfred validates and stores**, a few of them built in
   and seeded as `Announcement` is, each declaring its knobs as `fields` the
   editor draws with the form components it has.
4. **The first recipe scores windows; it does not cut at pauses.** The advice
   prizes dialogue with breaks in it, and a spike in the level with motion at
   the same second: both are scores over a candidate window, read from the
   words, the sound's level and the picture's motion, and neither needs a
   model. Pauses and sentence ends place a window's edges; they do not decide
   what is kept. A model's title or score comes later, and is optional.

## 2. The round, as pull requests

One change per pull request, stacked where one needs another and parallel
where not; each is cut from alfred's `fix/no-caption-cap` or from the row
above it that it needs, and stays local while *keep everything local* holds
(§5). The order is the advice's path: what the `highlights` recipe needs
comes first, and the labeller, the flow and the remaining engine work follow
it. Each row says what done looks like, and the check that goes red when it
is not.

- **(a) The counts come off.** Built: alfred `a0f7a32b`, `fix/no-caption-cap`.
  No count bounds a project's captions or its words; the refusal
  `too_many_captions` and its code are gone, with the tests that asserted
  it, and the pages say what bounds a project instead: its document, which
  the database refuses past its own size. §6 is the run. The cues' count
  goes the same way in (n).

- **(b) The cut's arithmetic, in alfred.** Built: alfred `7a0ccc86`,
  `feat/cut-arithmetic`, as planned, the fixtures recorded once from the
  browser's implementation and committed as the contract; a mutation to
  either side reddened its own suite. A module of pure functions over
  a timeline, its captions and its words: `cut_ranges` and `follow_clips`,
  the twins of `website/src/ClipWindow.js`, and `excerpt`, a span as a
  timeline of its own with its captions and its words moved into it, from
  qmcp's `excerpt_edl` and `excerpt_captions` plus the words, which the flow
  does not move. The browser's cases, today in `cut-ranges.spec.js` and
  `follow-clips.spec.js`, become JSON fixtures under `tests/fixtures/`, each
  a timeline, its captions and words, the ranges, and what comes out; pytest
  and the Node specs read the same files. Done is one set of fixtures read by
  both suites, and a mutation to either implementation reddening its suite.

- **(c) The sound of a timeline, in timeline seconds.** Built: alfred
  `b3771b61`, `feat/timeline-sound`, with one thing the plan did not have:
  the engine refused the long recording's raw file, which is over the
  gibibyte it takes in one upload, so a video's sound now goes to the engine
  alone, as a WAV otto writes from it (`utils/sound.py`), and every analysis
  is kept beside the library (`utils/analyses.py`) as well as in the api's
  memory, since the api restarts on every code change and the worker never
  asked. The engine's analysis
  is in each file's seconds: `peaks`, the level so many times a second,
  `silences`, and `loudness`, one figure for the whole file. A clip plays a
  window of a file at a place on the timeline. The Audio lane maps the peaks
  and the silences onto the timeline in the browser
  (`website/src/lanes/arith.js`); alfred gains the same mapping in Python,
  held equal to the lane's by fixtures as (b) is, and `GET
  /project/{id}/sound` answers a timeline's silences and its level over time
  in its own seconds, from the analyses alfred keeps per file. This is the
  video journey's §3 (b), placed: the flow hears the sound through this route
  rather than a tool per file. Done is the route, its refusals (no engine, a
  file it cannot analyse) by code, and the fixtures.

- **(d) Motion in the picture, over time.** Built: otto `eac657d`,
  `feat/motion`, committed in the submodule's checkout and pinned by alfred
  `665a6f78`, `feat/picture-motion`; not released, so the pin names a commit
  only this clone holds until otto's branch is pushed and released. With it,
  `fix/host-reload-waits` (`be2cdd91`): the host run's api reloader waited
  for ever while a browser tab streamed the recording from it, and now waits
  a bounded few seconds. The advice's second signal is a
  spike in the level *with more motion than usual on screen at the same
  time*, and nothing in the family measures motion. otto gains
  `otto.media.motion`: how much the picture changes from one moment to the
  next, measured at a reduced size with the ffmpeg it runs, as values so many
  times a second like `peaks`, published in a release alfred pins. alfred
  keeps it per file at `GET /media/{name}/motion` as it keeps the audio
  analysis, and `GET /project/{id}/motion` maps it onto the timeline through
  (c)'s arithmetic. A still picture and a template have none. Done is the
  measure in otto, with a test on a clip that moves and one that does not,
  made as otto's demo clips are; the two routes with their refusals by code;
  and the mapping's fixtures.

- **(e) Recipes.** Built: alfred `dcedf676`, `feat/recipes`, with one
  departure from §3 item 5: the built-in recipes are held in code
  (`utils/recipes_builtin.py`) and listed for every account by name, not
  seeded as copies, so a changed first value is one edit and an account that
  wants its own stores a copy. `spans` gained `chapter_pause`. A document
  `{name, label, description, fields, steps}`:
  `fields` as a form project declares them, `steps` a list of operations
  from a fixed set, each with its parameters, a parameter reading a field by
  `{"var": name}` as `logic` does. Validated at write, refused by code for an
  unknown operation or a value out of its range. Owned as projects are.
  `GET /recipes`, `POST /recipes`, `PUT /recipes/{id}`. The operations of
  this round, needing no engine beyond joe and (d):

    - *segment*: `windows`, candidates of a length between a shortest and a
      longest, laid every so often along the source, each snapped to begin at
      a word's start and end at a word's end and preferring a sentence's
      end; `chapters` (a pause); `sentences`; `spans` (a pause, the shortest
      and the longest); `silences` (longer than, from (c));
    - *score*: `dialogue`, how much is said in a window, words a second over
      its whole length, so a window with a break in it scores by what is
      said around the break and is not cut at it; `spikes`, where the level
      rises above its usual and the picture's motion is above its usual at
      the same second, each usual a baseline over the whole source, from (c)
      and (d), with a knob saying whether a spike counts only where words are
      said; `label`, a title from the topic the language engine has live
      over the candidate, and a category or a score where (h) gives a
      labeller, else skipped with a line in the job;
    - *filter*: `top`, the so many highest-scored candidates that do not
      overlap, the count given or scaled by the source's length; `keep` (a
      length window); `fillers` (the words to drop, from the transcript's
      words);
    - *edit*: `tighten` (every pause longer than one length cut to another);
      `excerpt` (each candidate as its own draft);
    - *compose*: `compose` (one draft per window; one per chapter; the top
      windows to a target length, in order; the whole); `render` (the draft's
      width, height and whether its captions are drawn, as its
      `render_settings` and caption style: a tall short with its captions
      burned in).

  Built in and seeded for every account as `Announcement` is: *highlights*,
  the advice's recipe, windows of a length range scored by `dialogue` and
  `spikes`, the top so many each as a draft of its own, its first values the
  advice's, a window of eight to twelve seconds and about twenty-five of them
  from a recording of an hour and a half to two hours, held as the recipe's
  defaults in code until (k) measures them; *teaser*, the same windows
  composed to a target length as one draft; *chapters*, one draft per
  chapter; *excerpts*, the flow's spans; *tight cut*, the whole source with
  its long pauses shortened and its fillers dropped; *quotes*, each sentence
  that stands alone as a short of its own. Done is each operation with a test
  of its edge, each built-in recipe run on a fixture with speech and motion
  in it, and `docs/drafts.md` saying what a recipe is and listing the
  operations.

- **(f) Drafts.** Built: alfred `8aae64ca`, `feat/drafts`, as planned, the
  measures moved into `utils/measures.py` so the worker and the api's routes
  share one; a project gained `description` for where a draft came from.
  Run on the host stack's long recording: the `highlights` recipe with its
  first values left its drafts in seconds once the recording was measured.
  `POST /project/{id}/drafts` with `{recipes: [{recipe,
  values}]}` starts a job the render worker runs, as a transcription is, kept
  on the source as its `drafts_job` with a state and a reason; each recipe
  leaves one or more projects carrying `source: {project, recipe, values,
  spans, scores, made_at}` with their captions and words moved, named
  `<source> – <recipe> <n>` with the chapter or the label as the description;
  the source's cues are written under the source `alfred-drafts`, a cue per
  span a draft took, `kind` `draft`, `ref` the draft's id, and they stay on
  the source when the draft is edited. `GET /project/{id}/drafts` lists a
  source's drafts and the job; `GET /project` carries `source`, so a list can
  group. A highlights run leaves dozens, so a draft can be let go of: `DELETE
  /project/{id}/drafts` names the drafts to drop, scoped to the source's owner
  and to drafts alone; a project that is not a draft keeps having no delete,
  as the ownership round decided (§3, 8). Refused by code: a source with no
  words (transcribe first), an unknown recipe, a source whose job is running,
  a drop naming a project that is not one of this source's drafts. Done is a
  run on the host stack's long recording leaving projects the editor opens,
  each with its words and its scores, and the refusals each a test.

- **(g) The Sculpt stage.** Built: alfred `56fabd5f`, `feat/sculpt-stage`,
  as planned, with the Recipes panel a tab beside Templates and the Drafts
  panel a tab beside Projects on the desktop; on a phone the rail's five
  stages fit only without their numbers, so there the labels alone name
  them. A fifth stage on the rail, between Source and
  Edit, with panels of its own: the recipes, each with its fields drawn by
  the form components, and **Sculpt**; the job followed as a render is on
  Deliver; the drafts, each with its scores and what it was cut from and by
  which recipe, each opening on Edit, and a selection of several to drop at
  once. The line under the rail says **Next: Sculpt** from Source and **Next:
  Edit** from Sculpt, and on a source with no words it says to transcribe
  first. The source's Cues lane shows what each draft took, and the Projects
  panel lists the drafts under their source, collapsed. On a phone, one stage
  at a time, as the rest. The stage joins `website/src/Stages.js` and every
  page that counts the stages, `docs/index.md`, `docs/journeys.md` and
  `docs/start.md` among them. `website/e2e/sculpt.spec.js` on the running
  stack, and the specs that walk the rail; a journey, *From a long
  recording*, in `docs/journeys.md`, with its **How?** from the rail's line.
  Done is the spec, the journey and the recorded recipe.

- **(h) A title from the reading, then a labeller behind a contract.** Two
  pull requests, in this order, both built; the title: alfred `bfcb0526`,
  `feat/topic-titles`, cut from `feat/who-spoke`. The title: `label` names
  each candidate by the topic the language engine has live over it, the one
  whose points within the span carry the most intensity, read through
  `utils/language_engine.py` once per run from the source's words and kept
  beside the library as the measures are, by the engine asked and a digest
  of the lines; `highlights`, `chapters`, `excerpts` and `quotes` carry the
  step, a draft is named `<source> – <title> <n>`, and its cue on the source
  with it. A span with no live topic keeps the recipe's name, no setting
  arrives, and a run without the engine, or whose engine fails, titles
  nothing and says why in the job. The labeller: alfred `0fc7b9aa`,
  `feat/labeller`, cut from `feat/topic-titles`. `ALFRED_LABELLER_URL` names
  the base of an OpenAI-style chat route, the shape qmcp's `localmodel`
  serves, `ALFRED_LABELLER_MODEL` the model it serves, and alfred names no
  model: `alfred/core/utils/labeller.py` carries the two questions, the
  flow's category prompt and a score for how well the stretch stands alone,
  answered as a whole number and scaled, and is handed to `sculpt.run` so
  the arithmetic reaches no model; `label` takes `categories` and `score`,
  asks a kept candidate at a time after the filters, stops at the first
  failure with a note, and without a labeller says why in the job; the
  draft carries `source.category` and `scores.label`, the Drafts panel shows
  the category, and `GET /health` reports the labeller as it reports the
  engines, `ok` only when the route also serves the model named. The tests
  stand in for the route with a mock transport, and the stacks pass the
  three settings. No built-in asks it; a stored copy of one with
  `categories` does.

- **(i) qmcp follows the route.** Built: qmcp `6ee6d44`,
  `feat/alfred-drafts`, cut from `feat/alfred-excerpts`. Tools
  `alfred_recipes`, `alfred_drafts`, `alfred_drafts_status` and
  `alfred_drafts_drop`; the `alfred-excerpts` flow's `propose` step calls
  `alfred_drafts` with the *excerpts* recipe, its knobs sent as text, and
  follows `alfred_drafts_status` to done within `--drafts-timeout`, taking
  as the proposal the drafts the run added and reading each one's captions
  with `alfred_captions`; its review puts each draft to the person, named as
  alfred named it; approve renders the draft's own timeline by its id, with
  the draft's captions burned in, and reject drops it, the rejected together
  once every answer is in; the labeller sorts a draft into a category and
  titles nothing, since the title is alfred's; the summary, the spoken form,
  delivery and the record stay as they were, the flow's cues now one per
  draft beside alfred's own. `propose`, `excerpt_edl` and `excerpt_captions`
  left `qmcp/cookbook/alfred_excerpts.py`; the stand-in alfred in
  `tests/alfred_stub.py` answers the recipes and drafts routes, its worker
  cutting drafts with an arithmetic of its own in `tests/alfred_cuts.py`;
  and `walkthrough/12-a-long-recording-is-offered-as-excerpts.md` runs over
  the tools, `docs/integrations/alfred.md` naming them. §6 is the run. What
  it does not do: run the Metaflow flow against the host run, which a
  person's check is.

- **(j) The engines, the rest.** Built, otto's and alfred's halves: otto
  `0b0f558`, `feat/scenes`, above `feat/motion`; alfred `d26c9784`,
  `feat/scene-cuts`, cut from `feat/who-spoke`, four commits, which pins
  otto's. `otto.media.scenes` finds where a video's picture cuts from one
  shot to another by ffmpeg's own scene score, decoded small and grey a few
  times a second, as the seconds each new shot begins at with the threshold
  they passed; `GET /media/{name}/scenes` answers it per file, kept as the
  motion is, and `GET /project/{id}/scenes` over a timeline, each video
  clip's own edges among the cuts; `utils/measures.py` carries the cuts to
  a run beside the sound and the motion. The `scenes` operation, a filter,
  moves each candidate's edges to the nearest cut within `within` seconds,
  so a draft is not cut in the middle of a shot, and says in the job when no
  cut was measured; the `speakers` operation, a segment, takes each turn a
  speaker takes from the speaker the words carry, (l), every speaker's or
  `who`'s alone, between `shortest` and `longest`, titled by the speaker.
  Neither built-in recipe carries them yet: a recipe of the account's does,
  §6. joe's half is built: joe `b2c0d00`, `feat/speaker-turns`, above
  `main`, in a worktree beside joe's clone; vox `588c09b`, `feat/speakers`,
  above the commit alfred pins, in the checkout under alfred. joe's media
  API answers a `speakers` feature: who is speaking when, told apart by the
  sound alone, as turns `{start, end, speaker}` in the upload's seconds with
  the voices lettered A, B and on in the order first heard, and how many
  were heard; `Modules/Speakers.py` reads the speech copy in blocks, takes
  the frames above the floor and within reach of the loud ones as speech,
  cuts it at pauses into short overlapping pieces, places each by its
  timbre and pitch, and merges pieces whose places lie under a fixed gate,
  at most eight voices, with no dependency added. vox's `EngineContract`
  names the feature and its keys, `Analysis` carries `speakers` as
  `SpeakerTurn`s with a `speaker_count`, and `Capabilities.features` reports
  it when the engine lists it. What it does not do, and says in joe's
  `docs/media.md`: know who; tell voices that sound alike apart, the same
  voice shifted a few semitones reading as one; tell music from speech, a
  sustained tone being lettered as a voice; give overlapping voices two
  labels; place a change with no pause closer than about half a second; or
  hear a voice under half a second as its own. The margin of its gate on
  real voices is modest, so another platform's voice pair may fall
  differently. alfred takes the turns to the words: alfred `af0941b6`,
  `feat/speakers-to-words`, cut from `feat/who-spoke`, pins vox at its
  `speakers` commit, and `POST /project/{id}/captions/speakers` asks the
  engine who is speaking when over the saved timeline's sound, one file at
  a time through `measures.sound_of` with the feature asked by name, moves
  the turns onto the timeline through the clips' windows
  (`utils/speakers.py`, a letter prefixed with the file's number where more
  than one file sounds), and gives each word that carries no speaker the
  letter of the turn its middle falls in; a word a person named keeps the
  name, and a person renames a letter to a name as before. The Transcript
  panel offers it as **Name speakers by the sound** under the transcription's
  line, waiting while the transcript has unsaved changes, and `GET
  /media/{name}/audio` takes `speakers` among its features. The `speakers`
  operation then reads the engine's letters as it reads a person's names.

- **(l) Who spoke, and what about.** Built: alfred `e56b386e`,
  `feat/who-spoke`. The person asked for it mid-round: *speaker highlighting
  and text updating* over the transcript, through looksatwords, the family's
  language engine. A transcript's words carry a `speaker`, named from the
  Transcript panel a paragraph at a time and saved with the words; the
  paragraphs' labels are coloured by speaker. With the engine beside the
  server (`ALFRED_LANGUAGE_ENGINE_URL`), `GET` and `POST
  /project/{id}/conversation` send the words as lines, `[m:ss] Speaker:
  words`, and answer the speakers, the topics live over time and the
  tangents, in timeline seconds; the panel shows them as chips that seek,
  and sends the words again a moment after they change, a cut, an undo or a
  speaker named, so the reading follows the text unsaved. `GET /health`
  reports the engine beside the audio engine; the stacks pass the setting
  through; `docs/editing-by-text.md` is the page. The engine reads the long
  recording's lines in about ten seconds and alfred keeps the reading by
  what was read. What it does not do: tell speakers apart by the sound,
  which is joe's, (j); draw the topics as a lane; let the engine's reading
  score a recipe's candidates, which is a `topics` operation for a later
  round.

- **(m) A recipe edited on Sculpt.** Built: alfred `c9b92d4c`,
  `feat/recipe-editor`, cut from `feat/who-spoke` beside the other two. The
  Recipes panel's Copy, on any recipe, and Edit, on one of the account's
  own, open it in the panel: its name, label and description, and its steps
  in order, each an operation chosen from `GET /recipes/operations` with its
  parameters drawn from what that lists, a blank one the operation's own and
  `$knob` a read of a knob; steps are added, removed and moved. Check asks
  `POST /recipes/check`, which checks as a write would and stores nothing,
  and a refusal is shown beside the step its sentence names; Save as mine
  stores it by `POST` or `PUT /recipes`, listed and ticked; Delete removes
  one of the account's own by `DELETE /recipes/{id}`; a built-in is never
  written. The spec copies *highlights*, has a step refused where it is and
  the copy saved, and runs a copy of *chapters* with a step changed, on the
  desktop and the phone. §6 is the run.

- **(n) The cues' count comes off.** Built: alfred `e73e5b42`,
  `feat/no-cue-cap`, cut from `feat/who-spoke` beside `feat/topic-titles`.
  `MAX_CUES` and `too_many_cues` are gone as the captions' count went, (a),
  with the tests that asserted them; a write of captions, words or cues the
  database would not take for the document's size, refused before it is sent
  or by the server, answers `project_too_large`, the sentence naming the
  size in the database's words, from `errors.written` around the two routes'
  writes. The worker's writes, a transcription's and a run's, are not behind
  it: a failure there is the job's to report, and it says the same size.

- **(k) Measured.** The instrument is built: alfred `bb5a969d`,
  `feat/drafts-measured`, cut from `feat/who-spoke`. A source remembers each
  draft dropped from it as `drafts_dropped`, its provenance as the draft
  carried it and how long its timeline was when it went, and `./al measured`
  reads every project and render from the host run's database and prints,
  per source and recipe, what was made, held, dropped, edited and rendered,
  with the mean length as made, as held and as rendered; a source is named
  by its id alone. The first reading is taken, at `bb5a969d` over the host
  run's database, with every built-in run over the long recording and a
  short second one and every draft kept: nothing dropped, since no person
  has chosen, and `edited` counting the two *tight-cut* drafts whose
  recipe's own steps shortened them, so the instrument reads a recipe's cut
  as a person's; the correction, a draft carrying its length as made for
  the instrument to compare against, is open on `feat/drafts-measured`
  (`perspectives/2026-11-22-the-first-reading-of-the-instrument.md`). What remains is a person's pass: the built-in recipes' drafts
  opened and kept or dropped, *highlights* first;
  what the person dropped, what they kept, and the difference between a
  kept draft's timeline and the timeline they rendered from it are the
  signal for each default: the window's length range, the count for a
  recording's length, the two baselines, and whether a dialogue spike counts
  only where words are said or anywhere, which takes a dropped prop with
  nobody speaking under the second reading only. The video journey's §3 (e)
  made concrete; a retrospective in `perspectives/` with the figures at
  their commit. No default moves before this; §6 holds the reading's
  figures, over two recordings and no person's choices.

- **(o) Open in the family's programs.** Built: alfred `993bfc9e`,
  `feat/open-in`, cut from `feat/who-spoke`, two commits; looksatwords
  `aeb22b6`, `feat/open-by-link`, above `test`, two commits. Where a thing
  in the editor has a page in another of the family's programs, the editor
  offers it: a transcribed timeline's job line offers **Open in joe**, the
  audio engine's own page, where its latest run is shown, and the
  transcript's reading offers **Open in looksatwords**, the reading on the
  language engine's page, opened by the id the engine keeps it under, which
  the conversation route now answers. `GET /health` names each page as
  `audio_engine.page` and `language_engine.page`, the engine's address
  unless `ALFRED_AUDIO_ENGINE_PAGE` or `ALFRED_LANGUAGE_ENGINE_PAGE` names
  one a browser can reach, since a stack reaches an engine by a name a
  browser cannot; looksatwords' page opens a saved conversation at
  `/?conversation=<id>`, as it was analysed, without analysing it again.
  qmcp has no page, so a cue's request has nowhere to open; joe keeps no
  library of alfred's files, so its link opens the engine, not the file.

## 3. Settled

Each item is a decision the person took, with what it was weighed against;
where one adds work, it names the §2 row that carries it.

1. **What a draft is.** A project with a `source` field, as (f) builds it.
   Against: a render, as the flow makes one, which cannot be edited; cues
   alone on the source, which mark but do not cut; a separate collection of
   drafts joined to projects, which keeps `Project` plain and costs a join on
   every list.
2. **Where the arithmetic lives.** alfred, in Python, the browser's copy held
   equal by shared fixtures, as (b) builds it. Against: left in qmcp, which
   keeps the editor out of it; the editor calling alfred for every cut, which
   costs an edit a round trip and breaks undo while a save is failing.
3. **Who runs a recipe.** Both the editor's Sculpt stage, (g), and qmcp's
   flow, (i), over one route. Against: the flow alone, which leaves the
   person configuring on a command line; the editor alone, which loses the
   queue's review and the run's record.
4. **How alfred labels.** A title from the topic the language engine has
   live over the draft's span, over the conversation route, first; then a
   category and a score from a chat route behind a contract, with the model
   behind qmcp's `localmodel` and alfred naming none: (h), in that order.
   Against: labelling only in the flow, which leaves a draft made on Sculpt
   without a title; a model inside alfred's image, which the family's records
   refuse; the labeller alone, which stands a second engine up for a title
   the reading already carries.
5. **Whose recipes.** Per account, with the built-in ones held in code and
   read by name by every account, so a changed knob is one edit; written
   through the API, (e), and edited on Sculpt, (m). Against: seeding copies
   into each account, which leaves a changed first value in every account's
   copy; built-in only, which makes every knob a release; the API alone,
   which keeps a person's own recipe off the stage they run it from.
6. **The counts.** The cues' count goes as the captions' did, (n), and the
   document's size is the one refusal. Against: a raised count, which is a
   number nothing updates; drafts that mark no cues, which empties the Cues
   lane of what each draft took.
7. **Scope.** The `speakers` operation reads the speaker each word carries,
   named a paragraph at a time on the Transcript, (l), and does not wait on
   joe; joe's hearing of speakers, (j), names the words nobody has. The
   score prompt's meaning of *stands alone*, and whether a dialogue spike
   counts only where words are said, are settled by (k), not before it.
8. **Dropping drafts.** A delete route scoped to a source's drafts, for its
   owner, as (f) builds it. Against: marking a draft dropped and hiding it,
   which keeps every project forever; leaving it to the person, whose list
   grows by dozens a run; a delete for every project, which the ownership
   round took away.

## 4. What this round does not do

- No new editing tool, and no second track: the editor lays its clips end to
  end, and a draft is cut on that model.
- No model in the first recipe: *highlights* reads the words, the level and
  the motion, and a title is a later, optional step, (h).
- Sculpt does not replace Edit: a draft is refined by hand, on Edit, with
  the tools the editor has.
- Nothing is delivered without a person: the flow's review stays, and
  Sculpt leaves drafts, not deliveries.
- No model in alfred's image, and no model named in alfred: the labeller is a
  URL.
- The Source stage lists what `GET /project` answers by default, and a
  database holding more projects than that page, as a long recording's
  drafts make, lists the rest nowhere; paging the Source stage is a round of
  its own.

## 5. Standing constraints

- **Keep everything local**, until the person lifts it: alfred's
  `fix/no-caption-cap` on `fix/host-run` on `feat/synced-timeline` on
  `docs/excerpts-in-the-family`, above alfred's open stack; qmcp's
  `feat/alfred-excerpts`; qm's `evolve/the-video-journey`, which carries this
  page. This round's eight branches stack above `fix/no-caption-cap`, each
  one commit, in this order: `feat/cut-arithmetic`, `feat/timeline-sound`,
  `feat/picture-motion`, `fix/host-reload-waits`, `feat/recipes`,
  `feat/drafts`, `feat/sculpt-stage`, `feat/who-spoke`; above the last, six
  more, each cut from it, parallel since none needs another:
  `feat/no-cue-cap`, `feat/topic-titles`, `feat/recipe-editor`,
  `feat/scene-cuts` (four commits), `feat/drafts-measured`, `feat/open-in`
  (two commits) and `feat/speakers-to-words`, the rest one commit each;
  the last pins vox's `feat/speakers`, so vox's branch lands before it;
  and `feat/labeller`, one commit, cut from `feat/topic-titles` and a
  draft against it until that one merges. Two more are cut from
  `feat/who-spoke` beside the seven and are outside the round's rows, each a
  pull request of its own against the branch beneath:
  `feat/trim-captions`, two commits, where every timeline tool acts on the
  Text lane's captions and words as it does on a clip and what it changed
  saves itself; and `feat/fluid-tools`, one commit, where the Timeline tools
  panel flows to fill its shape, as many tools to a row as it holds, so
  docked as a strip over the timeline it is one row.
  qmcp's
  `feat/alfred-drafts` is cut from its `feat/alfred-excerpts`, one commit,
  in a worktree beside qmcp's clone in a folder named `qmcp`; looksatwords'
  `feat/open-by-link` is above its `test`, two commits, in its clone. None
  pushed, no pull request open. otto's `feat/motion` and `feat/scenes`
  above it are branches in the submodule's checkout under `alfred/otto`, one
  commit each, not pushed; `feat/picture-motion` pins the first and
  `feat/scene-cuts` the second. vox's `feat/speakers` is a branch in the
  submodule's checkout under `alfred/vox`, one commit, not pushed, which
  `feat/speakers-to-words` pins, the clone's checkout sitting at alfred's
  pin while the clone is on any other branch; joe's
  `feat/speaker-turns` is one commit, not pushed, in a worktree beside
  joe's clone, and joe's clone sits detached at that commit so the host run's
  joe hears speakers, to go back to `main` when the branch lands. Landing is
  each as a pull request against the one beneath, in order, and the six
  above `feat/who-spoke` each against it; those that touch `docs/drafts.md`,
  `sculpt.py`, `recipes.py` and the changelog meet in small conflicts there
  as the later ones land.
- **alfred's clone is checked out on `feat/fluid-tools`**, with vox and
  otto at the stack's pins,
  which the host run serves on 1732 (`docs/host-run.md`), with its MongoDB
  on 27018, joe on 1059 and looksatwords on 8000, started from its own clone
  with `uv run looksatwords serve --no-open --port 8000` and
  `LOOKSATWORDS_DB` pointed at a scratch file, so its own database is left
  alone; the host run was started with `ALFRED_LANGUAGE_ENGINE_URL` naming
  it, and with `ALFRED_LABELLER_URL` and `ALFRED_LABELLER_MODEL` naming the
  local model server on 11434 and the model qmcp's `localmodel` installs.
  The alfred worktree beside the clone sits detached at
  `feat/trim-captions`'s first commit; `scripts/measured.py` reads the host
  run's database from a checkout of `feat/drafts-measured`. After a change
  of branch, or a restore of `website/src` from another ref, parcel's
  watcher has kept the old module graph and served the old bundle while
  its build failed; restart the run, and check the served bundle for a
  string the sources hold before measuring against it. The api reloads itself when its code changes, and has stalled twice
  while its log said "Reloading...", once with `fix/host-reload-waits`'s
  bounded wait on its command line, so the flag does not bound it; the sign
  is no "Started server process" after the line, and a route the file has
  answering 404, and `./al host down` then `up` is the route after a branch
  switch or an api edit. The worker does not reload, so a change to a task is
  the same. The site's watcher has crashed once
  on a temporary file of its own under Windows; `./al host` says when its
  process is gone, and `down` then `up` brings it back. A browser that
  opened the editor before a change holds the old bundle under the same file
  name until it fetches past its cache. `feat/no-cue-cap` has a worktree
  beside the clone, in a folder named `alfred`, since the tests that resolve
  the project from the folder's name pass there and not in one named for
  the branch; its tests run with the clone's virtualenv from the worktree's
  root, which imports the worktree's `alfred` ahead of the editable install;
  `feat/drafts-measured` sits there at this stamp. The vox checkout under
  alfred may sit on a branch of its own while joe's session works there,
  and alfred's `test_stack_settings` then reds on vox contract settings the
  stacks do not pass: that is the checkout, not the change, and vox goes
  back to alfred's pin before that test is read.
- **The host run's database holds the drafts the demos left**: the long
  recording's `highlights` runs, a draft per window, the later ten titled by
  the engine's topics, and its `chapters` runs, each a project under it on
  Source, to open or to drop from the Sculpt stage.
- **The host lacks fontconfig and ImageMagick**: a draft that carries a
  title card previews and renders only where ImageMagick is.
- **A long source's transcription runs in the worker** and takes as long as
  the engine takes; the editor's Transcript panel follows the job.
- **The projects in the host run's database are the person's**, and this
  page names none of them.

## 6. Verification

### For §2 (b) to (g) and (l), at alfred `e56b386e`

Each figure one run at that commit, in the host virtualenv, against the host
run on 1732 where a browser suite is named:

- the unit tier, every module but the three that record pictures: 1983
  passed, 37 skipped, 8 xfailed, 4 failed, the four this host's by their own
  reasons, none of them a file the round touches: the font probe, which
  needs fontconfig; the password-hashing guard, which reads source the store
  Python does not give; a preview-slot timing; a render reason spelt with a
  Windows path;
- otto's `test_motion.py`, `test_media.py` and `test_sound.py` at
  `eac657d`: 68 passed;
- the shared fixtures: `test_cut.py` 30 passed and `cut-fixtures.spec.js` 25
  passed over the same files; the mutation, the shift after a cut dropped,
  reddened 11 of each; `test_sound.py` and `lanes-fixtures.spec.js` over the
  sound fixtures, both green;
- the browser suite's `sculpt.spec.js` and `appearance.spec.js` on the
  `chromium` and `phone` projects: 19 passed, the `@slow` run of the
  `chapters` recipe through the real worker included; `conversation.spec.js`
  on both: 5 passed, 2 skipped, the skips the case for a server without a
  language engine; the rail's specs (`flow`, `navigation`, `projects`,
  `editor`): 10 passed for the cases that count the stages and list the
  projects. A run of every spec that walks the rail, before those fixes, was
  130 passed and 14 failed: 4 of mine, since fixed, the rest this host's
  known gaps, no ImageMagick (`422 GET /preview/template/title`), the auth
  bypass (two anonymous-visitor cases), the site's watcher down at that
  moment (one console error), and the phone's Source-room case, which fails
  on the branch beneath the round too;
- `black` and `ruff` clean; the seed's `check_timeless.py` 0 findings on
  every branch against the one beneath; `check_leaks.py` clean over 527
  tracked files;
- on the host run over the long recording: `GET /media/{name}/audio`
  answered in under 40 seconds through the extraction, `GET
  /media/{name}/motion` measured the recording at 4 values a second,
  `POST /project/{id}/drafts` with `highlights` left 25 drafts in about
  three seconds, each of 8 to 12 seconds scored by `dialogue` and `spikes`,
  and `GET /project/{id}/conversation` read 1572 lines through looksatwords
  in about ten seconds and from the kept reading in under a tenth after.
  No mutation was run on (c) to (l) beyond the fixtures'.

### For §2 (h), the title, at alfred `bfcb0526`, and (n) at `e73e5b42`

Each figure one run at that commit, in the host virtualenv; (h) in the
clone, (n) in its worktree:

- (h): the unit tier, every module: 2049 passed, 37 skipped, 8 xfailed, 4
  failed, the four this host's as above; the modules the change touches,
  `test_sculpt`, `test_drafts_task`, `test_language_engine`,
  `test_conversation_routes`, the recipes' and the drafts' route tests, the
  refusal codes and the docs' accounting: 249 passed; the mutation, every
  point of a topic counted wherever it falls, reddened 3, the two that title
  by what lies within a span and the one that names drafts by it; restored,
  all pass; `black` and `ruff` clean; the seed's `check_timeless.py --base
  feat/who-spoke` 0 findings; `check_leaks.py` clean over 533 tracked files;
- (n): the unit tier, every module: 2031 passed, 40 skipped, 8 xfailed, 8 failed: the host's font probe, preview-slot timing and Windows path, and the five of `test_stack_config` that compare the installed otto and vox with the submodule checkouts a worktree does not carry, which pass in the clone at `bfcb0526` and touch no file of the change; the modules the change
  touches, the cues' and captions' route tests, the refusal codes, the
  drafts task, the route inventory and the docs' accounting: 208 passed; the
  mutation, every write error refused as too large, reddened the one test
  that says a duplicate key is not this refusal; restored, all pass; `black`
  and `ruff` clean; `check_timeless.py --base feat/who-spoke` 0 findings;
  `check_leaks.py` clean over 533 tracked files;
- on the host run, restarted on `bfcb0526` with both engines reported ok: a
  `highlights` run asking ten over the long recording left ten drafts in
  about thirteen seconds, the engine's one read of its 1572 lines about ten
  of them, eight titled by a topic and two keeping the recipe's name for
  want of a point within their span, the job's notes empty, the reading
  kept beside the library, and the Sculpt stage's Drafts panel listing them
  by title.

### For §2 (m), at alfred `c9b92d4c`, and (i), at qmcp `6ee6d44`

Each figure one run at that commit; alfred's in the host virtualenv against
the host run on 1732, qmcp's in its worktree with the clone's virtualenv,
which imports the worktree's `qmcp`:

- (m): the unit tier, every module: 2040 passed, 37 skipped, 8 xfailed, 4
  failed, the four this host's as above; the recipe route tests, the
  refusal codes, the route inventory and the docs' accounting: 123 passed;
  the browser suite's `sculpt.spec.js` on the `chromium` and `phone`
  projects, the host run restarted on the commit: 8 passed and 4 failed, of
  which the two new editor cases passed, the `@slow` run of a copied
  *chapters* recipe through the real worker passed, and the one earlier
  `@slow` case failed on both projects at its last assertion, which looks
  for the source's draft group on the Source stage: the host run's database
  holds more projects than `GET /project` lists by default, so the group is
  past the page, a cap the Source stage meets with a long recording's drafts
  and this page names in §4; `black`, `ruff`, `check_timeless.py --base
  feat/who-spoke` and `check_leaks.py` clean; the cookbook regenerated;
- (i): `test_alfred_excerpts.py`, `test_alfred_tools.py` and the walkthrough
  page: 145 passed; the whole suite with every walkthrough, the governance
  and vox submodules checked out in the worktree first: 1802 passed, 12 skipped, 14 deselected;
  `ruff` clean on the files the change touches; qm's `check_timeless.py
  --base feat/alfred-excerpts` 0 findings; `check_leaks.py` clean. The flow
  was not run against the host run.

### For §2 (j), at otto `0b0f558` and alfred `d26c9784`, (k) at alfred `bb5a969d`, and (o) at alfred `993bfc9e` and looksatwords `aeb22b6`

Each figure one run at that commit, alfred's in the host virtualenv, (k)'s
in its worktree, against the host run on 1732 where a browser or a run is
named:

- (j), otto: `test_scenes.py` and `test_motion.py`: 21 passed; the
  mutation, the `select` filter dropped so every frame is a cut, reddened
  the test that finds the one cut and none in a still; restored, all pass.
  alfred: the unit tier, every module: 2062 passed, 37 skipped, 8 xfailed, 4
  failed, the four this host's as above; the modules the change touches,
  the scenes and motion routes, the sculpt arithmetic, the recipe model, the
  refusal codes, the inventory, the docs tests, the drafts task and the
  sound: 265 passed; `black`, `ruff`, `check_timeless.py --base
  feat/who-spoke` and `check_leaks.py` clean. On the host run: `GET
  /media/{name}/scenes` over the long recording found 30 cuts above the
  threshold in about three and a half minutes, `GET /project/{id}/scenes`
  answered 32 from the kept measure in milliseconds, and a stored recipe of
  the account's, *highlights* with a `scenes` step within two seconds, run
  through the worker, left six drafts of which two had an edge moved to the
  cut at 1495 s and four had no cut in reach; the first such run, before
  the cuts reached the worker's source, said so in the job's notes, which
  is how that gap was found.
- (j), joe and vox, each figure the session's that built them, read back
  here as the commits and one rerun: joe's suite, `pytest tests/ -m "not
  local"`, at `main`: 602 passed; at `b2c0d00`: 619 passed, the two
  platform-voice cases among them; `tests/test_media_speakers.py`: 16
  passed, rerun here after the hand-back; the mutations, one label for
  every piece, reddened 7 of the 16, and the block read without its pad
  reddened the one that holds the block features to librosa's on the whole
  signal; vox's suite at `588c09b`: 398 passed, and its walkthrough's
  mutations 79 of 79 caught, the new one a speaker's label read under a
  fixed key. The feature was calibrated on this machine's two system voices
  and pitch-shifted copies, not on a recording; the gate's margin there was
  modest. The vox checkout was put back at alfred's pin after the hand-back,
  and alfred's `test_stack_settings` then passed on `feat/open-in`.
- (k): `test_measured.py` and `test_drafts_routes.py`: 22 passed; the
  refusal codes, the inventory and the docs tests green; `ruff`, `black`,
  `check_timeless.py --base feat/who-spoke` and `check_leaks.py` clean.
  `./al measured` over the host run's database, the figures with the
  commit and nowhere else: 155 drafts made and 155 held, 0 dropped, 3 edited
  and 1 rendered, over two sources; the long recording's *highlights* runs
  made 35 of a mean 9.8 s, its *chapters* runs 102 of a mean 80 s, and its
  one *teaser* was edited from 58.8 s to 56.3 s. No draft had been dropped
  through the route before the record began, and none of these is a person's
  choice; the instrument reads, and the measurement waits on the recordings
  and the choices.
- (o): the modules the change touches, the health report, the language
  engine, the conversation route, the refusal codes, the docs tests and the
  cookbook: 168 passed; `test_stack_settings` red on vox contract settings
  for speaker turns that the vox checkout carried at that moment from joe's
  session, which the stacks do not pass and this change does not add;
  `check_timeless.py --base feat/who-spoke` and `check_leaks.py` clean. On
  the host run, from a fresh browser: the long recording's Transcript panel
  offered **Open in looksatwords** at the engine's page with the reading's
  id, which opened there with every thread drawn and the text filled, and
  **Open in joe** at the engine's page. `conversation.spec.js` on the
  `chromium` and `phone` projects: 4 passed, 2 skipped, the skips the cases for a server without a language engine, the link's case among the passes. looksatwords' own
  suite at `aeb22b6`: 238 passed, 1 skipped.

### For the tools on the Text lane, at alfred `5d4f062c`, and the fluid tools panel at `d8aa98dd`

Each figure one run at that commit, against the host run on 1732 serving
the branch, its served bundle checked for a string the branch's sources
hold:

- the Text lane: `lanes-text.spec.js`, the tools' arithmetic in Node: 21
  passed; `lanes.spec.js`, six tests of the tools on captions and words in
  the browser among its twelve: all pass. Three mutations, a word moving
  past its neighbours, only the pressed caption written and a word's edit
  saving the captions alone, reddened 2, 2 and 1; restored, all pass. The
  lanes, captions, follow-clips, cut-ranges, timeline-tools, transcript and
  editor specs on both projects: 168 passed, 8 failed; served the base's
  `website/src`, verified in the bundle, the same specs' failing tests
  failed alike but for one, a transcription test that timed out clicking
  Transcribe after the real engine's run before it and passes on the
  branch when run again: the template preview's 422 on this host, and
  joe's real hearing where the suite expects its stand-in.
  `dd3d8dc9`, the first commit, left the cookbook page stale; `5d4f062c`
  regenerates it and `test_cookbook.py` passes there. On the second
  recording, from a fresh browser, Slide moved a caption with both
  neighbours' near edges, Trim lengthened a word up to the next, and each
  saved itself, the words with the captions; its captions and words were
  put back and read back equal;
- the tools panel: two tests seeding a saved arrangement, the tools as a
  strip between the viewer and the timeline and as a column wide enough for
  three to a row, failed on the base's layout, 4 rows for 1 and 2 to a row
  for more than 2, and pass at the commit, with the zoom test; the
  two-column grid put back reddened both; restored, all pass. The
  timeline-tools, workspace, editor, flow, stacked, media, tools and
  journeys specs on both projects: 166 passed, 10 failed, 2 skipped: the
  suite's unauthenticated requests answered as this host run's skipped
  login answers them, the template preview's 422, and one phone Source
  stage test that fails alike with the base's CSS verified as served.
  `check_timeless.py --base feat/who-spoke`, `check_leaks.py` and the docs
  tests clean on both branches. From a fresh browser at 1280 by 800, the
  default column held the tools in three rows and the strip in one.

### For §2 (h), the labeller, at alfred `0fc7b9aa`, and the first reading of (k) at `bb5a969d`

Each figure one run at that commit, in the host virtualenv, against the
host run on 1732:

- (h): the unit tier, every module, with vox and otto at the branch's pins:
  2081 passed, 37 skipped, 8 xfailed, 4 failed, the four this host's as
  above; the modules the change touches, the labeller, the sculpt
  arithmetic, the drafts task and the health route, with the docs-accounted
  test: 111 passed; two mutations, a category read as the longest whatever
  the answer and a failing labeller skipped instead of ending the asking,
  reddened 2 and 1; restored, all pass; `black`, `ruff`,
  `check_timeless.py --base feat/topic-titles` and `check_leaks.py` clean.
  In the worktree, before the clone moved, the stacks' settings test
  reddened six times on the four speaker settings of vox's `feat/speakers`,
  which the clone's vox checkout then sat at and the venv imports: the
  checkout, not the change, and green once the checkout was at the pin;
- (h) on the host run: `GET /health` reported the labeller configured and
  ok against the local model server on 11434; a stored copy of *highlights*
  with four categories and `score` ran over the short recording in 10 s
  and left 9 drafts, 5 explanation, 3 story, 1 planning, scores 0.2 to 0.8;
  a cold model answered its first question in 76 s and a warm one in about
  a second; from a fresh browser the Drafts panel showed the nine
  categories beside the recipe and the scores;
- (k): the second recording transcribed through joe at `b2c0d00`, 32
  segments and 350 words; six built-ins over it, 41 drafts in 5 s; three
  over the long recording, 112 in 10 s; `scripts/measured.py` from the
  `feat/drafts-measured` worktree over the host run's database: made 317,
  held 317, dropped 0, edited 5, rendered 1, the per-recipe lines in the
  retrospective.

### For the words named by the sound, at alfred `af0941b6`

Each figure one run at that commit, in the host virtualenv, against the
host run on 1732 with joe at `b2c0d00`:

- the unit tier, every module: 2047 passed, 37 skipped, 8 xfailed, 4
  failed, the four this host's as above; the modules the change touches,
  the speaker arithmetic, the captions and audio routes, the refusal
  codes, the inventory, the stacks' settings and the docs tests: 298
  passed; the mutation, the words a person named renamed too, reddened 3;
  restored, all pass; `black`, `ruff`, `check_timeless.py --base
  feat/who-spoke` and `check_leaks.py` clean;
- on the host run: the long recording's words were named through the route in about fourteen minutes, the engine's one pass over the whole sound: 7977 of 9247 words took a letter, 7833 of them one voice, the rest spread over seven letters of a few words each, and the words heard in no turn stayed unnamed; from a fresh browser the Transcript panel offered the button and 1086 of its 1572 paragraphs read one letter, 448 stayed Unknown. Asked directly, the engine answered a one-minute tone in under a second as one voice and five minutes of the recording's sound in about two seconds as five voices over 92 turns, where the whole recording had read as mostly one: the engine's letters on a real recording are a first value a person corrects, which joe's own page says.

### For §2 (a), at alfred `a0f7a32b`

In the host virtualenv, each figure one run at that commit:

- the unit modules the change touched, `test_captions_routes`,
  `test_caption_mapping`, `test_caption_parsing`, `test_refusal_codes`,
  `test_render_captions` and `test_transcription`: 278 passed;
- the database tier's `test_captions_api.py` against the host run's MongoDB
  on 27018, in a database of its own that the tier drops: 20 passed;
- the mutation, a count of a thousand put back into `checked_captions`: of
  the eight new `however_many` tests, 5 failed, the 2 on words passed, and
  the database tier's 1 skipped without `DB_URL`; restored, all pass;
- black and ruff clean; the seed's `check_timeless.py --base fix/host-run`
  0 findings; `check_leaks.py` clean over 470 tracked files;
- the host run restarted on the commit, `GET /health` reporting the database,
  one worker and the audio engine ok, and the long recording's transcription
  queued again with 202; its outcome is not on this page.
