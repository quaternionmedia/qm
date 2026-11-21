# Handoff — the algorithmic layer: from a long source to drafts, by recipe

**Stamped 2026-11-21.** `qm` `main` at `5baf779`; `alfred` `feat/who-spoke`
at `e56b386e`, the top of eight branches stacked above `fix/no-caption-cap`
at `a0f7a32b` (§5); `otto` `feat/motion` at `eac657d`, which alfred pins;
`looksatwords` `test` at `7d9089d`; `qmcp` `feat/alfred-excerpts` at
`763414c`; `joe` `main` at `188a2cb`. Every figure on this page was true at
those commits and nowhere else; re-derive before acting on one.

This page is a plan: the round of feature work that takes alfred from an
editor a person drives by hand to one with an algorithmic layer over it. In
the editor the layer is a stage of its own, **Sculpt**, between Source and
Edit: Source brings a long recording in, Sculpt runs the algorithms over it
and leaves drafts, and Edit refines a draft by hand. The page
builds on [`the-video-journey.md`](the-video-journey.md), where the first step
of that layer, qmcp's `alfred-excerpts` flow, stands, and it carries the shape
of the layer, where each part of it lives, the pull requests in order with
what done looks like for each, what is proposed for the person to settle, and
what the round leaves out. Of the work it names, §2 (a) to (g) and (l) are
built, each as a local branch that is a pull request to open once *keep
everything local* is lifted; (h) to (k) are planned. The built part runs on
the host run (`docs/host-run.md`) over the long recording: §6.

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
| telling speakers apart; music from speech | joe | the engine that hears; nothing in the family does either | not built; pends on joe |
| motion in the picture over time, and scene changes | otto | the engine that reads frames, with the ffmpeg `otto.media.probe` runs | not built |
| a title, a category, a score for how well a stretch stands alone | the local model, reached by a contract that names no model, as vox's does | language is nobody's engine in the family | the flow's labeller, in qmcp, over the chat route qmcp's `localmodel` stands up |
| who spoke, which topics were live and when, where the talk went off and whether it came back | looksatwords, the language engine, reached by its conversation route | reading prose is its charter, and its border with codecartographer says so | built, §2 (l): `ALFRED_LANGUAGE_ENGINE_URL`, `utils/language_engine.py` |
| the arithmetic: windows and segments from times, the scores from what the engines measured, filters, a timeline cut, the words and captions carried through | alfred, the seam | it owns the project, the timeline, the captions and the words, and no engine should; a score is arithmetic over the engines' measurements | in the browser (`cutRanges`, `followClips`) and in qmcp (`propose`, `excerpt_edl`), twice over; no score anywhere |
| recipes as documents; drafts as projects with their provenance; the job that runs a recipe | alfred | lifecycle state is the seam's | not built |
| the review of each draft by a person, the run and its record, delivery | qmcp, the flow | its queue, its record | built, for excerpts |
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
  the database refuses past its own size. §6 is the run. What remains: the
  cues keep their count (`MAX_CUES`, `alfred/core/models/cues.py`), and a
  source several recipes have marked is where a long project meets it next;
  done is the same removal, and a refusal that names the document's size
  where a write would pass it, for captions, words and cues alike.

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
      said; `label`, a title, a category or a score where (h) gives a
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

- **(h) A labeller behind a contract.** `ALFRED_LABELLER_URL` names a chat
  route of the shape qmcp's `localmodel` serves, and alfred names no model:
  `alfred/core/utils/labeller.py` carries the prompts for a title, a
  category and a score, from the flow's `title_prompt` and `category_prompt`
  with a score added, and a stand-in for the tests as `tests/stubs/audio_engine.py`
  stands in for joe. `GET /health` reports the labeller as it reports the
  audio engine. A draft made without one has no title; the recipe runs all
  the same. Done is `label` running with a labeller and skipping without one,
  each a test, and the health report.

- **(i) qmcp follows the route.** Tools `alfred_recipes`, `alfred_drafts` and
  `alfred_drafts_status`; the `alfred-excerpts` flow's `propose` step calls
  `alfred_drafts` with the *excerpts* recipe, its review puts each draft to
  the person, approve renders the draft's timeline and reject drops it, and
  the run's summary, the spoken form, delivery and the record stay as they
  are. `propose`, `excerpt_edl` and `excerpt_captions` leave
  `qmcp/cookbook/alfred_excerpts.py`, the stand-in alfred in
  `tests/alfred_stub.py` grows the routes, and
  `walkthrough/12-a-long-recording-is-offered-as-excerpts.md` is rewritten
  over the tools. Done is the walkthrough running under the ordinary test
  command, and `docs/integrations/alfred.md` naming the tools.

- **(j) The engines, the rest.** otto: `otto.media.scenes`, scene changes by
  the ffmpeg it runs, as a list of seconds with a threshold, kept at `GET
  /media/{name}/scenes` as the analyses are; the `scenes` operation, so a
  window's edge prefers a scene change and a cut never lands inside a shot.
  joe: speaker turns, and music told from speech, as features of its media
  API, with vox's `Analysis` and `Capabilities` grown to carry them; the
  `speakers` operation. Each in its own repository as its own pull request,
  pinned here when released; joe's pends on joe.

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

- **(k) Measured.** The built-in recipes run on several real recordings,
  *highlights* first, with every draft kept; what the person dropped, what
  they kept, and the difference between a kept draft's timeline and the
  timeline they rendered from it are the signal for each default: the window's
  length range, the count for a recording's length, the two baselines, and
  whether a dialogue spike counts only where words are said or anywhere, which
  takes a dropped prop with nobody speaking under the second reading only.
  The video journey's §3 (e) made concrete; a retrospective in
  `perspectives/` with the figures at their commit. No default moves before
  this.

## 3. Proposed for the person to settle

Each changes what is built. The position the plan takes is first, then what
it was weighed against.

1. **What a draft is.** A project with a `source` field. Against: a render,
   as the flow makes one, which cannot be edited; cues alone on the source,
   which mark but do not cut; a separate collection of drafts joined to
   projects, which keeps `Project` plain and costs a join on every list.
2. **Where the arithmetic lives.** alfred, in Python, the browser's copy held
   equal by shared fixtures. Against: left in qmcp, which keeps the editor
   out of it; the editor calling alfred for every cut, which costs an edit a
   round trip and breaks undo while a save is failing.
3. **Who runs a recipe.** Both the editor's Sculpt stage and qmcp's flow, over one
   route. Against: the flow alone, which leaves the person configuring on a
   command line; the editor alone, which loses the queue's review and the
   run's record.
4. **How alfred labels.** A contract, a URL, with the model behind qmcp's
   `localmodel`, and after the signals the advice names, since no score of
   the first recipe needs it. Against: labelling only in the flow, which
   leaves a draft made on Sculpt without a title; a model inside alfred's
   image, which the family's records refuse.
5. **Whose recipes.** Per account, written through the API this round, not
   edited on Sculpt, with the built-in ones held in code and read by name by
   every account; a changed knob is one edit. Against: seeding copies into
   each account, which leaves a changed first value in every account's copy;
   built-in only, which makes every knob a release.
6. **The counts.** The cues' count goes as the captions' did, and the
   document's size is the one refusal. Against: a raised count, which is a
   number nothing updates.
7. **Scope.** The score prompt's meaning of *stands alone*, and whether a
   dialogue spike counts only where words are said, are settled by (k), not
   before it; the `speakers` operation waits on joe.
8. **Dropping drafts.** A delete route scoped to a source's drafts, for its
   owner. Against: marking a draft dropped and hiding it, which keeps every
   project forever; leaving it to the person, whose list grows by dozens a
   run; a delete for every project, which the ownership round took away.

## 4. What this round does not do

- No new editing tool, and no second track: the editor lays its clips end to
  end, and a draft is cut on that model.
- No model in the first recipe: *highlights* reads the words, the level and
  the motion, and a title from the labeller is a later, optional step.
- Sculpt does not replace Edit: a draft is refined by hand, on Edit, with
  the tools the editor has.
- Nothing is delivered without a person: the flow's review stays, and
  Sculpt leaves drafts, not deliveries.
- No model in alfred's image, and no model named in alfred: the labeller is a
  URL.
- No editing of a recipe on Sculpt: a recipe is written through the API.

## 5. Standing constraints

- **Keep everything local**, until the person lifts it: alfred's
  `fix/no-caption-cap` on `fix/host-run` on `feat/synced-timeline` on
  `docs/excerpts-in-the-family`, above alfred's open stack; qmcp's
  `feat/alfred-excerpts`; qm's `evolve/the-video-journey`, which carries this
  page. This round's eight branches stack above `fix/no-caption-cap`, each
  one commit, in this order: `feat/cut-arithmetic`, `feat/timeline-sound`,
  `feat/picture-motion`, `fix/host-reload-waits`, `feat/recipes`,
  `feat/drafts`, `feat/sculpt-stage`, `feat/who-spoke`; none pushed, no pull
  request open. otto's `feat/motion` is a branch in the submodule's checkout
  under `alfred/otto`, one commit, not pushed, which `feat/picture-motion`
  pins. Landing is each as a pull request against the one beneath, in order.
- **alfred's clone is checked out on `feat/who-spoke`**, the stack's top,
  which the host run serves on 1732 (`docs/host-run.md`), with its MongoDB
  on 27018, joe on 1059 and looksatwords on 8000, started from its own clone
  with `uv run looksatwords serve --no-open --port 8000` and
  `LOOKSATWORDS_DB` pointed at a scratch file, so its own database is left
  alone; the host run was started with `ALFRED_LANGUAGE_ENGINE_URL` naming
  it. The api reloads itself when its code changes, now within a few seconds
  whatever a tab streams; the worker does not, so a change to a task is
  `./al host down` then `./al host up`. The site's watcher has crashed once
  on a temporary file of its own under Windows; `./al host` says when its
  process is gone, and `down` then `up` brings it back. A browser that
  opened the editor before a change holds the old bundle under the same file
  name until it fetches past its cache.
- **The host run's database holds the drafts the demo left**: the long
  recording's `highlights` run, a draft per window, each a project under it
  on Source, to open or to drop from the Sculpt stage.
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
