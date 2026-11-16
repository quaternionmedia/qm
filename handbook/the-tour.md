# Handbook — The Tour

**Routing.** The decision is
`records/DRAFT-the-application-carries-its-tour-and-the-harness-reviews-it.md`,
and this page restates it as the thing to do; where the two disagree the record
is what the organisation decided. `plans/the-tour-adoption.md` lists what each
project has of it.

**Audience.** Anyone, human or agent, working in a QM repository whose
application has a page or whose project has a walkthrough, and anyone writing a
project's roadmap.

---

## The standard, in one paragraph

An application carries a tour of its own journeys, a stage at a time, in a box
over its page. It is the application's built-in help and the place a person
gives feedback: `works` or `off` on a stage, under a name, kept with the commit
the application ran. What the project plans and what was found of it are not in
the application's repository: the roadmap, the plans, the open work, the
checklists and the dated records are in `project/` on the project's branch of
this corpus, beside `adr/`. The review is the harness's: `qmcp tour` reads the
roadmap against the journeys and the words the application serves.

## What a repository needs, in the order it can be built

Each is useful before the next exists, and a project stops where its shape
stops. A library with no page is done at the second: its review is its pages,
read whole.

1. **A walkthrough** the ordinary test command runs,
   `records/DRAFT-one-executable-walkthrough.md`.
2. **`project/ROADMAP.md`** on the project's branch of the corpus. Copy
   `project-seed/project/` beside `adr/` (`handbook/forking-a-project.md`,
   step 2). Each line is a checkbox, in the order the project wants it taken,
   and names what shows it: a journey as `journey:<id>` in a code span, or
   walkthrough pages by a link, `../../../walkthrough/NN-<slug>.md` from where
   the roadmap stands in a clone. A line that names neither is shown by nothing
   and stays, reported in those words.
3. **Journeys as data.** A journey is an id, a name and ordered stages; a stage
   is an id, a title, its own line (the one the application shows where it
   shows the journey), and what there is to try on it: the walkthrough steps
   that go through it, and the pages that show the same thing whole.
4. **The box and its two documents**: `GET /tour`, the journeys in order with
   each stage's line, what to try and its latest word; and
   `GET /tour/feedback`, every word kept, oldest first. Their shape is
   `project-seed/tour-schema.json`, with cases in
   `project-seed/tour-vectors.json`.
5. **A way to take the application to a stage**: per stage, an ordered list
   drawn from a short, closed list of things the application already does for a
   person, each named for the control that does it and done only where it is not
   so already. One test takes the application to every stage, on simulated
   machines as a person starts them, and holds that nothing was armed, started
   or sent; another holds that a stage whose subject is missing is stopped short
   of, saying what it needs. The test and the tour take the same actions, so a
   repository keeps one way of reaching each state.

Run in a clone, from its root, after each:

```sh
python governance/qm/project-seed/ci/check_roadmap.py --at <where the application runs>
python governance/qm/project-seed/ci/tour_document.py --at <where the application runs>
```

The first says per line whether each journey is served and each page is in the
clone, which lines are shown by nothing, and which served journeys no line
names; it reports and gates nothing. The second says whether the two documents
have the shape the harness reads, and exits 1 when they do not.

## The box

The journeys in their order; a stage's line; the application taken there; what
to try; one word. It stands above the application's own layout, where nothing
the application lays out moves or covers it, and it is moved, folded and closed.
A repository's rule for composing its interface does not reach it, because it is
not a section of that interface.

A word, as the record's section 7 has it:

- `works`, or `off`, and nothing else; `off` is refused without what is off, in
  the person's words;
- given under a name, asked once and remembered by the browser, and refused
  without one; the name is checked against nothing;
- kept with the stage, the name, the moment, the commit the application ran and
  whether its tree had changes beside it, and never rewritten: the latest on a
  stage is its feedback;
- of the build it was said of: once the application runs another commit, the
  word is still shown, as said of an earlier build, and the stage waits again.
  The box counts the words on the running build and opens on the first stage
  without one.

The application keeps the words in its own state, and serves them to its own
machine and no other. A server that takes words and is reachable from another
machine is the record's first revision trigger: a project whose server is says
so in its own records before it takes a word.

## What the tour never does

- **Arm, start, send or spend.** Taking the application to a stage stops short
  of anything `ci/attested-registry.yaml` lists, and of every act that is a
  person's: a print started, a render queued, a message sent.
- **Stand in for what a person brings.** Which device is which, a machine
  switched on, a photograph, a person's own footage: where a stage needs one
  that is not there, the application stops short, and the tour says what the
  stage needs and where in the application it is done.
- **Say anything of its own.** What it says of a stage is the stage's line and
  the headings of the steps it names. A sentence the tour needs is got by
  changing the application or its pages.
- **Speak the review's words.** Tests, demonstrations, commits and claims are
  for planning and judging evidence, not for a person finding their way.
- **Tick the roadmap.** A word is a measurement beside the roadmap's claim. A
  ticked line with a stage `off`, or with no word on the running build, is a
  disagreement, and neither side wins.

## Where planning lives

In `project/`, on `project/<name>`: `ROADMAP.md`, `todo.md`, `plans/`, the
checklists a person ticks, and `validation/` for the dated records of what a run
found. A change to them is a pull request based on `project/<name>`, from an
`evolve/<slug>` branch cut from it (`docs/ref/namespaces.md`). The repository's
code, documentation and tests name them there, at `governance/qm/project/`. A
file a test or a person at a machine feeds to the application is the
application's, and stays in its repository.

To move a repository's planning into `project/`: each page as it stands at the
commit that removes it, its links made to hold from `governance/qm/project/` in
a clone, and every reference in the repository repointed, in the commit that
removes them and moves the repository's `governance/qm` pin to the corpus
commit that adds them.

## The review

```sh
qmcp tour <clone> --at <where the application runs>
```

It reads the roadmap from the clone's `governance/qm/project/ROADMAP.md`, the
pages from the clone, and the two documents from the application, and reports
each line in the roadmap's order: its stages as `works` or `off` on the running
build, with who said it, as said of an earlier build, or as not yet said; its
pages, read whole; whether it is shown by nothing; and what the roadmap does not
name. Without the application it reports the roadmap and the pages and says the
stages are the application's to give. qmcp's `docs/tour.md` is its reference.

A tag's annotation may name the review at the tagged commit as what was
manually tested. The review cuts no tag and satisfies no gate.

## The instances to read

- **`apothecary`** has all five, for every path its page has: journeys in the
  order of the chain it manages, the application taken to each stage by a
  declared list and held by one test, and a stage that needs what a person
  brings saying so. Its `docs/tour.md` is the reference and names the code.
- **`alfred`**, a video editor in the browser, is the second: its journeys are
  the editor's user journeys over its four-stage flow, and its box is written in
  its own front-end idiom. Its `docs/tour.md` is the reference and names the
  code.

Read both before building a third: what they share is the standard, and what
differs is each application's idiom. Which branch each stands on is
`plans/the-tour-adoption.md`'s to say.
