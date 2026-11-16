# QM-XXXX — The Application Carries Its Tour, and the Harness Reviews It

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-11-15 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `show-it-by-running-it` — show it by running it; `interrupted-only-by-a-decision` — a person is interrupted only by a decision; `typing-schedules-interface-work` — a change that can only be typed schedules interface work |
| **Restated in** | `project-seed/ide/AGENTS.md` item 22; `handbook/the-tour.md` |

## Context

`records/DRAFT-version-tags-are-claims.md` makes a version tag assert three
things, and one of them is that a human manually tested the change set against
its real runtime. Nothing in the corpus says how that test is taken, where its
result is kept, or how a person finds out which parts of a repository are
waiting for it. So it is taken from memory, against whatever the person thought
to try, and the annotation states it in prose.

`records/DRAFT-one-executable-walkthrough.md` already produces what such a test
should be taken against: pages whose steps a test wrote, each with its words,
the picture the run took after the step's assertions passed, and what the page
showed. The same record lists in-app walkthroughs among the artifacts
repositories build beside the code and then abandon, and that failure is
specific: a guided path with text of its own is a second copy.

`apothecary` carries the instance this record rests on. It took three forms,
each taken by the person it was built for, and each failed in ways the next
answers.

The first form was a window of the application that showed the walkthrough one
recorded step at a time and kept a person's word on each:

- **It asked about every assertion.** A walkthrough holds one step per thing a
  test checked, and a person asked the same question that many times stops
  answering. The unit a person can judge is a *stage*: a place in a path through
  the application where there is something to explore.
- **It showed a state and left the person to reach it.** Reaching it is the
  system's work, and asking a person to do it spends the one resource that does
  not scale (`interrupted-only-by-a-decision`).
- **It was a window among the windows it toured.** Laying out the windows a
  stage needs moved or covered the tour itself.

The second form was a box above the application's own layout, on the paths the
application declares as journeys of ordered stages. It read the repository's
roadmap for its order, took the application to a stage only on a demonstration
instance, and kept an answer against the commit the server ran:

- **It refused the application as the person ran it.** The person reviewing the
  whole, on the real machines, opened it there and was told it did nothing
  because this was not the demonstration. Two servers stood side by side, one
  to be shown and one to be used, and the question of which was being reviewed
  had no good answer.
- **It spoke the language of review to a person finding their way.** Tests,
  demonstrations, commits and claims are words for planning and for judging
  evidence. A person in the application wants to know what a stage is, to be
  taken there, and to say how it is.
- **It kept planning and review in the repository of the thing planned.** The
  roadmap, its reader and the report of what was found lived beside the code,
  so each repository would build all three again, and the application carried
  a command whose subject was the project and not the application.

The third form separates the two. The application carries a tour of its own
journeys, which works wherever the application runs and keeps a person's
feedback. What the project claims, and the reading of that feedback against the
claims, are outside the application: the first in the project's branch of this
corpus, the second in the harness, `qmcp`.

`qmcp`'s own `docs/ROADMAP.md` has acceptance lines with boxes ticked by hand,
which is a claim serving as its own evidence
(`records/DRAFT-nothing-is-both-a-claim-and-its-own-evidence.md`), and none of
its lines says where the thing it claims can be seen.

## Decision

### 1. The application's repository holds the application

A repository holds its application: its code, its reference documentation, its
walkthrough, and the tour of §§3 to 7. **What the project plans, and what was
found of it, live in this corpus and in the harness.**

- **Planning is in the project's branch of the corpus.** `project/<name>`
  holds `project/` beside `adr/`: `adr/` is what the project decided,
  `project/` is what it plans and what was found. The roadmap of §2 is
  `project/ROADMAP.md`, and beside it stand the project's plans, its list of
  open work, the checklists a person ticks, and its dated records of what a
  run found.
- **Review is the harness's.** Reading a roadmap against what people said is
  `qmcp`'s (§8). The application carries no reader of a roadmap and no report
  on one.

`docs/ref/namespaces.md` states what a `project/<name>` branch holds, and is
amended with this record.

`records/DRAFT-a-projects-history-lives-in-the-corpus.md` gives a project
that adopts it a subtree of the corpus's site for its dated account. What is
dated in `project/` is that account's source: an adopting project's dated
records go on from `project/` to its subtree, and what is not dated, the
roadmap, the open plans, the list and the checklists, stays.

### 2. A project has one roadmap, and a line names what shows it

Every QM project whose repository carries a walkthrough has
`project/ROADMAP.md` in its branch of the corpus. Its acceptance lines are
checkbox items, in the order the project wants them taken. A line names what
shows it: a journey by its id, written `journey:<id>`, or walkthrough pages of
the repository by link, `walkthrough/NN-<slug>.md`.

A ticked line is a claim that the thing is built. A line that names neither is
*shown by nothing*, and is reported in those words wherever the roadmap is
reviewed. It is not left out, and it is not counted as waiting.

Where the application's journeys form a chain, each handing the next what it
made, the roadmap takes them in the chain's order.

### 3. The unit of the tour is a stage

A **journey** is a path a person takes through the application, declared by
the repository as data it serves: an id, a name, and ordered **stages**, each
with an id, a name and one line saying what is there. A stage also names the
walkthrough steps that go through it, and the pages that show the same thing
whole.

The tour is the journeys, in the order the application declares them, and it
asks one thing of a person per stage. A recorded step is never a stage by
itself: it is something to try at its stage. A walkthrough page that belongs
to no journey is not in the tour; the review of §8 lists it under the roadmap
line that names it, as a page read whole.

### 4. The tour has no text of its own, and speaks the application's language

What the tour says of a stage is the stage's own line, which the application
shows where it shows the journey, and the headings of the walkthrough steps
the stage names. Nothing is authored for the tour. A tour that needs a
sentence the application and its pages do not have gets it by changing one of
them.

The tour speaks to a person finding their way. It does not speak of tests, of
demonstrations, of commits or of claims: those are the review's words, and the
review is elsewhere.

### 5. The tour takes the application to the stage, wherever it runs

Asked to, the application takes itself to a stage by the actions a person
would take to reach it: opening what the stage needs, choosing its subject,
entering it. Where a stage needs the work of the one before it, that work is
done first. The tour says what was done, then what the application said, and
the person explores.

- **The same on every instance.** The application does the same things
  whether its machines are real or simulated, and each acts on what is there.
  No instance is the one where the tour works.
- **Never an act that is a person's.** Taking the application to a stage stops
  short of anything `ci/attested-registry.yaml` lists, and of arming, starting
  or spending anything.
- **Never a stand-in for what a person brings.** Which device is which, a
  machine switched on, a photograph taken: where a stage needs one that is not
  there, the application stops short, and the tour says what the stage needs
  and where in the application it is done. With that done, the tour takes the
  application the rest of the way.

What takes the application to a stage is declared as data beside the journey:
an ordered list drawn from a short, closed list of things the application
already does for a person, each named for the control that does it. Each is
done only where it is not so already, so a stage can be gone to from anywhere
and gone to again. The tour says each thing it did in those terms.

A repository does not keep two scripts for reaching the same state. One test
takes the application to every stage, on simulated machines as a person starts
them, and holds that nothing was armed, started or sent; another holds that a
stage whose subject is missing is stopped short of, saying what it needs.

### 6. The tour is a box above the application, and the application's own

The tour is drawn above the application's own layout, where nothing the
application lays out moves or covers it, and it can be moved, folded and
closed. It is the application's built-in help and the place its feedback is
given, and each application with a page carries one, in this form: the
journeys in their order, a stage's line, the application taken there, what to
try, and one word.

A repository's own rule about how its interface is composed does not reach the
tour, because the tour is not a section of that interface.

### 7. Feedback is a person's word on one stage, kept by the application

- the options are closed: `works`, or `off`;
- `off` is refused without what is off, in the person's words;
- a word is given under a name, asked once and remembered by that browser,
  and refused without one;
- the record carries the journey and stage, who said it, the moment, the
  commit the application ran, and whether its tree had changes beside that
  commit;
- no word is given by default, and none is given to more than one stage at a
  time.

A word is never rewritten. A person who says something else of the same stage
adds another, and the latest is the stage's feedback.

**A word is of the build it was said of.** Once the application runs another
commit, what was said is still shown, as said of an earlier build, and the
stage waits for a word again. The tour counts the words on the build it runs
and opens on the first stage without one.

The application keeps the words in its own state and serves two documents: the
tour, which is its journeys in order, each stage with its line, what to try on
it and its latest feedback, with whether that is of the build now running; and
every word kept, oldest first. Their shape is `project-seed/tour-schema.json`,
with the cases both an application and the harness hold to in
`project-seed/tour-vectors.json`. It serves them to its own machine and no
other. The name is what a person typed, and is checked against nothing.

### 8. The review is the harness's

`qmcp tour` is pointed at a clone of the repository and at the running
application. It reads the roadmap from the project's branch of the corpus, the
walkthrough's pages from the clone, and the two documents of §7 from the
application, and reports each line of the roadmap in the roadmap's order: its
journey's stages as `works` or `off` on the build the application runs, with
who said it, as said of an earlier build, or as not yet said; its pages, read
whole; whether it is shown by nothing; and what the roadmap does not name, a
page or a journey.

The harness draws no box and keeps no feedback of its own. Without the
application running, it reports the roadmap and its pages and says the stages
are the application's to give.

### 9. A word is a measurement, and ticks nothing

The roadmap's line is the claim; the feedback is what was measured. They stay
separate documents (`records/DRAFT-project-phase-ladder.md` §4). `qmcp` never
writes to a roadmap.

A line ticked with a stage `off`, or with no word on the build being run, is a
disagreement, reported as one, and neither side wins
(`records/DRAFT-a-disagreement-is-a-delta.md`).

A tag's annotation may name the review at the tagged commit as what was
manually tested. The feedback cuts no tag and satisfies no gate.

## Consequences

- The manual test a tag asserts has a place to be taken, which is the
  application as the person runs it, with the application already standing
  where the question is about, and a record of what was said against which
  commit.
- A person is reviewing one thing. There is no second server whose purpose is
  to be toured, and a repository's simulated machines are for its tests.
- The application's help does not need the harness. The review does: it needs
  the harness, the clone and the application running, and it says so when one
  is missing.
- Each project owes a roadmap in its branch of the corpus, in the order it
  wants its work taken, whose lines name journeys or pages. Writing them is
  where a project finds the things it claims and cannot show.
- A project's plans, its list of open work, its checklists and its dated
  records of what a run found leave its repository for `project/`, and the
  repository's documentation, code and tests name them there. A file a test
  or a person at a machine feeds to the application is the application's and
  stays.
- Every commit sets the tour's count back to nothing said on this build. That
  is what "tested at this commit" costs, and why an earlier word is kept in
  view and not discarded.
- A repository with a page owes its journeys as data, a way to take the
  application to a stage, and the two documents of §7.
- A test and the tour reach a stage by the same actions, so a stage's test is
  written to be replayed. A state only a fault brings about is not reached by
  the tour, and stays at its stage as steps to read.
- `apothecary`'s roadmap, plans, list of open work, checklists and dated
  records move to its branch of the corpus, its reader and its command to
  `qmcp`, and its box stays, working on the server a person runs.
- A name typed into a browser is not authentication. This is accepted for a
  server that answers its own machine, and is the first revision trigger.
- Every application builds a box. The form is small and stated in §6; a second
  application's box is the moment to ask whether it is one script.

## Alternatives considered

1. **One question per recorded step.** It is the walkthrough read back
   exactly, and the instance was built that way first. It lost when the person
   it was built for stopped answering: the count of questions was the count of
   assertions, and a step is not a place to explore.
2. **Show the stage and leave reaching it to the person.** Nothing to build in
   the application. It lost because reaching a state is sequencing, which is
   the system's work, and because a person who reaches it another way has
   tested something else.
3. **The tour as a window of the application.** It needs no new surface and
   obeys the application's own rule for its interface. It lost because the
   tour lays out the windows it sits among.
4. **Take the application to a stage only on a demonstration instance.** No
   action of the tour can then touch a real machine or a person's state. It
   lost when the person reviewing the application opened the tour where they
   were working and it declined: a tour that works only somewhere else is not
   the application's help, and a review taken on a demonstration is of the
   demonstration. What that rule protected is kept by the two rules that
   replace it: nothing armed, started or spent, and nothing stood in for what
   a person brings.
5. **The harness holds the box and the answers.** One box for every
   repository, and one place to ask what a person has checked. It lost because
   the application's help would then need the harness running to say anything
   at all, and because a word on a stage is the application's own function,
   as its settings are. The harness reads the words; it does not own them.
6. **The roadmap in the repository's `docs/`.** Readable where the code is. It
   lost because a roadmap is the project's plan and not the application's
   documentation, and kept there it draws its reader and its report into the
   application after it.
7. **A tour written as its own steps.** It would read better than a stage's
   line. It lost to the walkthrough record's finding: a second copy is
   abandoned, and then the manual test is taken against a description of
   software that has since changed.
8. **The roadmap orders the box.** One order for planning and for help. It
   lost because the box would then show lines the application cannot stand on,
   and need the roadmap to open; the journeys already have an order, and where
   they form a chain the roadmap follows it.
9. **The tour ticks the roadmap's boxes.** One document instead of two. It
   lost because the claim would then be written by its own evidence, and a
   disagreement between them, which is the useful signal, could not exist.
10. **One roadmap for the organisation, in this corpus.** Closer to
    `plans/qmpm-standardisations.md`. It lost for now because it rests on
    items that plan has not decided; a project's own roadmap is readable
    today, and its lines can become deltas without changing what they name.

## Revision triggers

- A server that takes feedback is reachable from another machine.
- Taking the application to a stage is found to have armed, started, sent or
  spent something, or to have written what was a person's to say.
- A stage said to work is found to have been reached by actions its test does
  not take.
- A tagged release ships a defect in a stage the review held as `works` at
  that commit.
- `plans/qmpm-standardisations.md` decides how a roadmap's line and a delta
  relate.
- A second application builds a box.
- A repository adopts that has no page, and its review is pages read whole
  throughout.

## Amendments

*None.*
