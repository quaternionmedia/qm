# The tour — groundwork for adoption, family by family

**Status: an outline.** It decides nothing. The decision is
`records/DRAFT-the-application-carries-its-tour-and-the-harness-reviews-it.md`,
which is Proposed; this page lists what each family would have to have in place
to take the tour and the review that record describes, and in what order the
work unblocks.

**Stamped 2026-11-15.** Which repositories carry a walkthrough and a roadmap
was asked of the host's default branches on 2026-11-13, for the members
`families.json` lists as governed. A repository the host would not show, or
whose walkthrough is on another branch, reads here as having none. `alfred` was
read on 2026-11-15 at the top of its open stack of pull requests,
`docs/changes-by-family`, since its default branch is far behind it. Re-derive
before acting.

## What a project needs, in the order it can be built

Five things, each useful before the next exists. The first, third, fourth and
fifth are the application's and live in its repository; the second is the
project's and lives in its branch of this corpus.

| | What | Where | Needs first | Without it |
|---|---|---|---|---|
| 1 | **A walkthrough** the test command runs (`records/DRAFT-one-executable-walkthrough.md`) | the repository | nothing | there is nothing to review |
| 2 | **`project/ROADMAP.md`**, lines in the order to take them, each naming a journey or pages | the project's branch of the corpus | 1 | the review has no order, and every claim is shown by nothing |
| 3 | **Journeys as data**: ordered stages, each naming the steps that go through it | the repository | 1, and an interface with paths through it | the review is whole pages |
| 4 | **The box and its two documents**: the tour over the page, a word kept on a stage under a name and of a build, the tour and every word served | the repository | 3 | nothing is said of a stage |
| 5 | **A way to take the application to a stage**: a declared list per stage, from things the application already does, one test that reaches every stage on simulated machines, and one that a missing subject stops it short | the repository | 3 and 4 | the person reaches each stage by hand |

A project stops wherever its shape stops. A library with no interface is done
at 2: its review is its pages, read whole, from the command line.

## What the corpus and the harness owe first

- **The record ratified**, or adopted by a project as a draft with that said.
- **`qmcp tour`**: the reader of a project's roadmap and a clone's pages, and
  the review of both against a running application's two documents. A working
  instance is built on a local branch of `qmcp`, and reads `alfred` as it reads
  `apothecary`, with no change.
- **`project/` in the seed**, beside `adr/`, so a project branch is created
  with a place for its roadmap: `project-seed/project/`, which
  `handbook/forking-a-project.md` step 2 copies and `docs/ref/namespaces.md`
  names.
- **The tour documents' shape**: `project-seed/tour-schema.json` states both
  documents, `project-seed/tour-vectors.json` holds the cases an application
  and the harness hold to, and `project-seed/ci/tour_document.py` checks a
  served document or every case against the schema. A stage has no address
  of its own: the kinds in `docs/ref/addresses.md` are a closed set, and one
  for a stage waits on a reader that needs to link a word to a row elsewhere.
- **A check in the seed**, `project-seed/ci/check_roadmap.py`, says whether a
  roadmap's lines name journeys and pages that exist, and which lines are
  shown by nothing. It reports and gates nothing, because a line shown by
  nothing is a finding and not a fault. `project-seed/roadmap-vectors.json`
  holds the line grammar's cases, read the same by it and by `qmcp tour`.
- **The page an agent reads**: `handbook/the-tour.md`, and item 22 of
  `project-seed/ide/AGENTS.md` pointing at it. A project's `AGENTS.md` carries
  the item once it takes the seed's governance section again.
- **A rollout** in `ci/rollout.yaml` once two projects have adopted, so the
  claim and the evidence per project are generated and not kept here.

## By family

A member in more than one family is listed once, under the family whose tour
it would show first.

### core — the corpus and its tooling

- **`qmcp`**: has a walkthrough, and a `docs/ROADMAP.md` in its repository.
  Groundwork: its roadmap moved to its branch of the corpus, its acceptance
  lines linked to its pages; then it reviews itself. Its human queue and voice
  loop are journeys in waiting, and it has no page of its own, so its review
  is pages read whole.
- **`dossier`**: has a walkthrough, no roadmap. Items 2 and 3 once its
  terminal has paths through it worth calling journeys.
- **`qm`**: has a walkthrough, no roadmap. Pages read whole. Its roadmap is
  the open question in `plans/qmpm-standardisations.md`, and it should not be
  written until that plan says whether the corpus has one.
- **`codecartographer`**: no walkthrough on its default branch. It has the
  step rail that `apothecary`'s journeys were taken from, so its paths are
  already declared; its groundwork is the walkthrough, then the journeys as
  data and a box.
- **`rad`, `looksatwords`**: no walkthrough. Item 1 first.

### irl — matter, and the record of its making

The family with the instance, and the one where taking the application to a
stage happens beside real machines.

- **`apothecary`**: has all five for every path its page has: eight journeys in
  the order of the chain it manages, a part designed through to a drawing read
  back into parts, the application taken to each stage by a declared list and
  held by one test, a machine with no board taken as the site plans it, and a
  stage that needs what a person brings saying so. Its roadmap, plans, list
  of open work, checklists and dated records stand in `project/`. Groundwork
  left: the states only a fault brings, held as steps to read.
- **`datum`**: has a walkthrough, no roadmap. Items 2 and 3.
- **`alfred`**: the second instance, drafted on top of its open stack. Its
  journeys are the editor's user journeys (`docs/journeys.md`) over its four
  stages, Source, Edit, Render and Deliver: served at `GET /tour` with each
  stage's line taken from the rail and its steps read from that page, a box in
  the editor's own front-end idiom, and a stage reached by three things the
  editor already does, a project opened, a stage chosen, a panel brought
  forward. Its roadmap and its one plan, the backend test plan, stand in
  `project/` on `project/alfred`. Groundwork left:
  - **No walkthrough.** What a stage names to try is the journey's own steps
    on `docs/journeys.md`, not walkthrough steps, so the review has no pages
    to read whole, and its claims no journey shows are shown by nothing.
  - **No test reaches every stage.** Item 5's two tests belong in its browser
    suite, which needs its dev stack.
  - **The rail's words are in two places**: the site's stage list and the
    server's journeys, held equal by a test, because the API image and the
    site are built apart. One place means the rail reads them from
    `GET /tour`.
  - **Words are kept only by a server started to keep them**, and a production
    stack refuses to start with that setting, since `alfred` in production
    answers more than its own machine. That a public server never takes a word
    tightens the record; whether `alfred` in production should take them is
    the record's first revision trigger.
- **The family's rule for item 5**: the tour arms nothing, starts nothing and
  sends nothing to a machine, and pins no device a person has not named. A
  member that drives hardware adopts item 5 with a test that holds exactly
  that, on simulated machines of its own.
- **Ungoverned members** adopt the walkthrough record before any of this.

### instruments, performing and performer-display — the sound, the show, the player

Taken together, because the same repositories are in all three.

- **`carlos`**: has a walkthrough, no roadmap. It holds and draws a rig in a
  page, so it can carry a box. Items 2 to 4; a rig drawn from a file is what
  its stages stand on.
- **`loopwall`**: no walkthrough. Item 1.
- **`qmetronome`**: no `walkthrough/` at its root on the default branch,
  though it is the instance the walkthrough record rests on, with pictures
  regenerated by its test command. It is not a web page: whether the box has a
  form for an application that is not a page is a question this family raises
  and the record does not answer.
- **Sound is not in a picture.** A stage whose point is what is heard has
  nothing recorded that a person can read. Such stages are gone to and
  explored, with nothing to try listed under them.

### show-control — the room

No member is governed. The groundwork is the constitution and the walkthrough
record, and nothing here applies until then.

### games — play

`factorio-sysops` is governed and has no walkthrough. Item 1. A game's journey
is a session, and what taking it to a stage means for one, a save loaded, is
plausible and unbuilt.

### infra — where a thing runs

`streaming-infrastructure` is governed; the host did not show it. A review of
infrastructure is pages read whole: taking it to a stage would be an act on
the real thing that is a person's.

### commons — the public

No member is governed. Nothing to plan yet.

## Order

1. Land `apothecary`'s instance, so the record cites what is on a default
   branch, and its roadmap in its branch of the corpus.
2. The record, to ratification.
3. `qmcp tour`, landed. From here a project with items 1 and 2 has a review at
   the command line.
4. `project/` in the seed, the schema of the tour documents, the roadmap
   check and the handbook page, with the record.
5. `alfred`, the second application with a page, on top of its stack once that
   lands, with its roadmap on `project/alfred` and its pin moved there.
6. Further adopters, one per shape: `carlos` (a page, no machines), `datum`
   (pages whole), `codecartographer` (journeys already declared).
7. The rollout document, and the remaining members as each reaches item 1.

## What this outline does not know

- Whether an ungoverned repository's walkthrough exists under another name.
- What any member but `apothecary` and `qmcp` would name as its first journey.
  That is its maintainer's to say, and the roadmap is where it is said.
- Whether the box can serve an application that is not a web page.
- Whether a third application's box should share a script. Two applications'
  boxes are one form and two scripts: `apothecary`'s is plain DOM with the page
  supplying how a stage is reached, `alfred`'s is written in its front-end
  framework, and each reaches a stage through things only its own page does.
  What they share is the two documents, which the seed states, and the rules
  of a word, which the handbook page does; a shared script would carry neither
  and would need a framework of its own.
- How a stage whose point is sound is shown.
