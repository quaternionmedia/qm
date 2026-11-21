# Handoff — the algorithmic layer: from a long source to drafts, by recipe

**Stamped 2026-11-21.** `qm` `main` at `5baf779`; `alfred` `fix/no-caption-cap`
at `a0f7a32b`, above `fix/host-run` at `9250d669`; `qmcp` `feat/alfred-excerpts`
at `763414c`; `otto` as alfred pins it; `joe` `main` at `188a2cb`. Every figure
on this page was true at those commits and nowhere else; re-derive before
acting on one.

This page is a plan: the round of feature work that takes alfred from an
editor a person drives by hand to one with an algorithmic layer over it. In
the editor the layer is a stage of its own, **Sculpt**, between Source and
Edit: Source brings a long recording in, Sculpt runs the algorithms over it
and leaves drafts, and Edit refines a draft by hand. The page
builds on [`the-video-journey.md`](the-video-journey.md), where the first step
of that layer, qmcp's `alfred-excerpts` flow, stands, and it carries the shape
of the layer, where each part of it lives, the pull requests in order with
what done looks like for each, what is proposed for the person to settle, and
what the round leaves out. Of the work it names, one pull request is built,
§2 (a); the rest is planned.

## 0. What the round is for

The person's brief: *take a long source, configure a few algorithms to filter
and edit it, and be left with drafts of several potential exports to refine
by hand*, with *a Sculpt step before Edit* where those algorithms run. Three
nouns carry it.

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
| the source | a project's timeline; its captions and its words, each word with the stretch of speech it was heard in; the engine's analysis of each library file: silences, loudness, peaks, tempo, beats and onsets, in the file's seconds; cues on the timeline, drawn in a lane | alfred: `GET /project/{id}`, `/captions`, `/captions/words`, `GET /media/{name}/audio`, `/cues`; `docs/lanes.md` |
| the recipe | one chain, as a flow's parameters: chapters at long pauses, spans at pauses and sentence ends within a length window, titles and categories from the local model; and, as a precedent for a timeline made from data, a form project's `logic`, json-logic over its `fields` | qmcp `qmcp/cookbook/alfred_excerpts.py` (`propose`, `label`); alfred `docs/about/project.md` |
| the draft | a span cut to a timeline of its own, with its captions moved into it, rendered as an excerpt: a render, not a project, with no words; in the editor, stretches cut out of a timeline with the words and captions carried through, in the browser alone | qmcp `excerpt_edl`, `excerpt_captions`; alfred `website/src/ClipWindow.js` (`cutRanges`, `followClips`) |

The gaps between them are the round. Nothing turns a source into projects a
person refines; no algorithm hears the sound, so a song reads as a pause; the
only place to configure the chain is the flow's command line; the arithmetic
of a cut lives in the browser and the arithmetic of an excerpt in qmcp, and
neither can call the other; and a long source met a count the day this page
was stamped, §2 (a).

## 1. The shape

```
source project
  │  read: the timeline, the words, the captions, each file's analysis
  ▼
segment   chapters at long pauses · sentences · silences in the sound · scene changes · speaker turns
  ▼
filter    by length · by a silence's length · filler words · by loudness · by a label or a score
  ▼
edit      cut ranges out (tighten the pauses, drop the fillers) · excerpt a span as its own timeline
  ▼
compose   one draft per chapter · to a target length · the whole source, tightened
  ▼
drafts    projects, each carrying its source, its spans and its recipe; cues on the source
```

**Where each part lives** is answered as `records/DRAFT-build-the-seam-buy-the-engines.md`
§3 asks: which engine should own it upstream, before the seam does.

| The part | Who owns it | Why | At the stamp |
|---|---|---|---|
| hearing the words, the silences, the loudness, the beats | joe, through vox's contract | the audio engine | built |
| telling speakers apart; music from speech | joe | the engine that hears; nothing in the family does either | not built; pends on joe |
| scene changes in the picture | otto | the engine that reads frames, with the ffmpeg `otto.media.probe` runs | not built |
| a title, a category, a score for how well a stretch stands alone | the local model, reached by a contract that names no model, as vox's does | language is nobody's engine in the family | the flow's labeller, in qmcp, over the chat route qmcp's `localmodel` stands up |
| the arithmetic: segments from times, filters, a timeline cut, the words and captions carried through | alfred, the seam | it owns the project, the timeline, the captions and the words, and no engine should | in the browser (`cutRanges`, `followClips`) and in qmcp (`propose`, `excerpt_edl`), twice over |
| recipes as documents; drafts as projects with their provenance; the job that runs a recipe | alfred | lifecycle state is the seam's | not built |
| the review of each draft by a person, the run and its record, delivery | qmcp, the flow | its queue, its record | built, for excerpts |
| choosing recipes and their knobs; reading the drafts | the editor, on a Sculpt stage between Source and Edit | where the person is | not built |

The plan takes three positions, and §3 puts each to the person with its
alternatives.

1. **A draft is a project.** Only a project's timeline is editable; a render
   is an output and a cue is a mark. A draft carries `source`: the project it
   was cut from, the spans it took, the recipe and the values it ran with.
2. **The arithmetic belongs to alfred, once, in Python**, with the browser's
   `cutRanges` and `followClips` held equal to it by one set of fixtures both
   run, and qmcp's `propose` and `excerpt_edl` retired into it, reached
   through a route and a tool.
3. **A recipe is data alfred validates and stores**, a few of them built in
   and seeded as `Announcement` is, each declaring its knobs as `fields` the
   editor draws with the form components it has.

## 2. The round, as pull requests

One change per pull request, stacked where one needs another and parallel
where not; each is cut from alfred's `fix/no-caption-cap` or from the row
above it that it needs, and stays local while *keep everything local* holds
(§5). Each row says what done looks like, and the check that goes red when
it is not.

- **(a) The counts come off.** Built: alfred `a0f7a32b`, `fix/no-caption-cap`.
  No count bounds a project's captions or its words; the refusal
  `too_many_captions` and its code are gone, with the tests that asserted
  it, and the pages say what bounds a project instead: its document, which
  the database refuses past its own size. §6 is the run. What remains: the
  cues keep their count (`MAX_CUES`, `alfred/core/models/cues.py`), and a
  source several recipes have marked is where a long project meets it next;
  done is the same removal, and a refusal that names the document's size
  where a write would pass it, for captions, words and cues alike.

- **(b) The cut's arithmetic, in alfred.** A module of pure functions over
  a timeline, its captions and its words: `cut_ranges` and `follow_clips`,
  the twins of `website/src/ClipWindow.js`, and `excerpt`, a span as a
  timeline of its own with its captions and its words moved into it, from
  qmcp's `excerpt_edl` and `excerpt_captions` plus the words, which the flow
  does not move. The browser's cases, today in `cut-ranges.spec.js` and
  `follow-clips.spec.js`, become JSON fixtures under `tests/fixtures/`, each
  a timeline, its captions and words, the ranges, and what comes out; pytest
  and the Node specs read the same files. Done is one set of fixtures read by
  both suites, and a mutation to either implementation reddening its suite.

- **(c) The sound of a timeline, in timeline seconds.** The engine's analysis
  is in each file's seconds; a clip plays a window of a file at a place on
  the timeline. The Audio lane maps the one onto the other in the browser
  (`website/src/lanes/arith.js`); alfred gains the same mapping in Python,
  held equal to the lane's by fixtures as (b) is, and `GET
  /project/{id}/sound` answers a timeline's silences and loudness in its own
  seconds, from the analyses alfred keeps per file. This is the video
  journey's §3 (b), placed: the flow hears the sound through this route
  rather than a tool per file. Done is the route, its refusals (no engine,
  a file it cannot analyse) by code, and the fixtures.

- **(d) Recipes.** A document `{name, label, description, fields, steps}`:
  `fields` as a form project declares them, `steps` a list of operations
  from a fixed set, each with its parameters, a parameter reading a field by
  `{"var": name}` as `logic` does. Validated at write, refused by code for an
  unknown operation or a value out of its range. Owned as projects are.
  `GET /recipes`, `POST /recipes`, `PUT /recipes/{id}`. The operations of
  this round, needing no engine beyond joe: `chapters` (a pause), `sentences`,
  `spans` (a pause, the shortest and the longest), `silences` (longer than,
  from (c)), `fillers` (the words to drop, from the transcript's words),
  `keep` (a length window), `tighten` (every pause longer than one length
  cut to another), `excerpt` (each span as its own draft), `compose` (to a
  target length, in order; one draft per chapter; the whole), `label`
  (a title, a category, a score, where (e) gives a labeller, else skipped
  with a line in the job), `render` (the draft's width, height and whether
  its captions are drawn, as its `render_settings` and caption style: a tall
  teaser with its captions burned in). Built in and seeded for every account
  as `Announcement` is: *chapters*, one draft per chapter; *excerpts*, the
  flow's spans; *tight cut*, the whole source with its long pauses shortened
  and its fillers dropped; *teaser*, the highest-scored sentences to a target
  length, in order; *quotes*, each sentence that stands alone as a short of
  its own. Done is each operation with a test of its edge, each built-in
  recipe run on the suite's speech fixture, and `docs/drafts.md` saying what
  a recipe is and listing the operations.

- **(e) A labeller behind a contract.** `ALFRED_LABELLER_URL` names a chat
  route of the shape qmcp's `localmodel` serves, and alfred names no model:
  `alfred/core/utils/labeller.py` carries the prompts for a title, a
  category and a score, from the flow's `title_prompt` and `category_prompt`
  with a score added, and a stand-in for the tests as `tests/stubs/audio_engine.py`
  stands in for joe. `GET /health` reports the labeller as it reports the
  audio engine. Done is `label` running with a labeller and skipping without
  one, each a test, and the health report.

- **(f) Drafts.** `POST /project/{id}/drafts` with `{recipes: [{recipe,
  values}]}` starts a job the render worker runs, as a transcription is, kept
  on the source as its `drafts_job` with a state and a reason; each recipe
  leaves one or more projects carrying `source: {project, recipe, values,
  spans, made_at}` with their captions and words moved, named `<source> –
  <recipe> <n>` with the chapter or the label as the description; the
  source's cues are written under the source `alfred-drafts`, a cue per span
  a draft took, `kind` `draft`, `ref` the draft's id, and they stay on the
  source when the draft is edited. `GET /project/{id}/drafts` lists a
  source's drafts and the job; `GET /project` carries `source`, so a list can
  group. Refused by code: a source with no words (transcribe first), an
  unknown recipe, a source whose job is running. Done is a run on the host
  stack's long recording leaving projects the editor opens, each with its
  words, and the refusals each a test.

- **(g) The Sculpt stage.** A fifth stage on the rail, between Source and
  Edit, with panels of its own: the recipes, each with its fields drawn by
  the form components, and **Sculpt**; the job followed as a render is on
  Deliver; the drafts, each saying what it was cut from and by which
  recipe, and each opening on Edit. The line under the rail says **Next:
  Sculpt** from Source and **Next: Edit** from Sculpt, and on a source with
  no words it says to transcribe first. The source's Cues lane shows what
  each draft took, and the Projects panel lists the drafts under their
  source. On a phone, one stage at a time, as the rest. The stage joins
  `website/src/Stages.js` and every page that counts the stages,
  `docs/index.md`, `docs/journeys.md` and `docs/start.md` among them.
  `website/e2e/sculpt.spec.js` on the running stack, and the specs that
  walk the rail; a journey, *From a long recording*, in `docs/journeys.md`,
  with its **How?** from the rail's line. Done is the spec, the journey and
  the recorded recipe.

- **(h) qmcp follows the route.** Tools `alfred_recipes`, `alfred_drafts` and
  `alfred_drafts_status`; the `alfred-excerpts` flow's `propose` step calls
  `alfred_drafts` with the *excerpts* recipe, its review puts each draft to
  the person, approve renders the draft's timeline and reject marks it, and
  the run's summary, the spoken form, delivery and the record stay as they
  are. `propose`, `excerpt_edl` and `excerpt_captions` leave
  `qmcp/cookbook/alfred_excerpts.py`, the stand-in alfred in
  `tests/alfred_stub.py` grows the routes, and
  `walkthrough/12-a-long-recording-is-offered-as-excerpts.md` is rewritten
  over the tools. Done is the walkthrough running under the ordinary test
  command, and `docs/integrations/alfred.md` naming the tools.

- **(i) The engines.** otto: `otto.media.scenes`, scene changes by the
  ffmpeg it already runs, as a list of seconds with a threshold, published
  in a release alfred pins; alfred `GET /media/{name}/scenes` kept as the
  audio analysis is; the `scenes` operation, so a cut never lands inside a
  shot and a chapter's edge prefers a scene change. joe: speaker turns, and
  music told from speech, as features of its media API, with vox's
  `Analysis` and `Capabilities` grown to carry them; the `speakers`
  operation. Each in its own repository as its own pull request, pinned
  here when released; joe's pends on joe.

- **(j) Measured.** The built-in recipes run on several real recordings,
  with every draft kept; the difference between a draft's timeline and the
  timeline the person rendered from it is the signal for each default, the
  video journey's §3 (e) made concrete; a retrospective in `perspectives/`
  with the figures at their commit. No default moves before this.

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
   `localmodel`. Against: labelling only in the flow, which leaves a draft
   made on Sculpt without a title; a model inside alfred's image, which
   the family's records refuse.
5. **Whose recipes.** Per account, with the built-in ones seeded; written
   through the API this round, not edited on Sculpt. Against: built-in
   only, which makes every knob a release.
6. **The counts.** The cues' count goes as the captions' did, and the
   document's size is the one refusal. Against: a raised count, which is a
   number nothing updates.
7. **Scope.** The score prompt's meaning of *stands alone* is settled by
   (j), not before it; the `speakers` operation waits on joe.

## 4. What this round does not do

- No new editing tool, and no second track: the editor lays its clips end to
  end, and a draft is cut on that model.
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
  page. New work of this round stacks above `fix/no-caption-cap`.
- **alfred's clone is checked out on `fix/no-caption-cap`**, which the host
  run serves on 1732 (`docs/host-run.md`), with its MongoDB on 27018 and joe
  on 1059. The api reloads itself when its code changes; the worker does not,
  so a change to a task, a transcription's included, is `./al host down`
  then `./al host up`.
- **The host lacks fontconfig and ImageMagick**: a draft that carries a
  title card previews and renders only where ImageMagick is.
- **A long source's transcription runs in the worker** and takes as long as
  the engine takes; the editor's Transcript panel follows the job.
- **The projects in the host run's database are the person's**, and this
  page names none of them.

## 6. Verification, for §2 (a)

At alfred `a0f7a32b`, in the host virtualenv, each figure one run at that
commit:

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
