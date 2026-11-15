# The documentation, brought under "durable text states what is true"

*Begun on 2026-10-12. The rule is the governance record *Durable text
states what is true, not how it came to be*
(`governance/qm` records, `DRAFT-durable-text-states-what-is-true.md`;
Proposed in qm#136): durable text states what is true now and what to do
with it, for a reader who was not there -- present tense, no internal
history, no ornament -- and a repository's existing text is swept area by
area, each passage sent to one home. This plan is the sweep's triage for
apothecary: what each area holds, where each passage goes, and the order.
It is dated and about the sweep, so the rule's own §4 exempts it.*

## Decided with the owner

Asked one at a time on 2026-10-12:

- **A passage's homes** are the record's own: a short fact stays inline in
  the present tense; an explanation moves to the reference pages in
  `docs/`; a narrative moves to a dated retrospective; a duplicate or a
  stale statement with no lesson is deleted.
- **Retrospectives go to the governance corpus's `perspectives/`**, one
  dated file per area, on a perspective branch with its own draft pull
  request there, not into this repository.
- **Plans and validation records are dated and exempt.** `project/plans/` and
  `project/validation/` stay as written. A finished plan retires: it leaves
  the present-tense links and is listed under a dated *History* heading in
  `docs/README.md`, and each decision of it that is still true moves into
  the present-tense documentation, a record or the code's own docstring.
  The CHANGELOG is a release log and exempt too.
- **0.1.0 was never released.** It is a version number, not a release: no
  tag and no published build exist, so the CHANGELOG's `[0.1.0]` heading
  carries no date, and the docs say a consumer pins a commit until a first
  release is tagged.
- **The gate joins CI after the record is ratified.** Until then
  `check_timeless.py --all` is the sweep's measure, run from the record's
  branch; once qm#136 is ratified and the governance pin carries the tool,
  a CI step and preflight check the lines each change adds.

Asked one at a time on 2026-10-13 and 2026-10-14:

- **The fitting proposal is dropped.** `docs/fitting-a-part.md`'s line (the
  consumer owns requirements and interfaces, apothecary realization and
  manufacturability), its single-number test and its rules 1 to 5 are not
  drafted as a record; the page describes the seam as built.
- **The walkthrough puts the loops first.** After page 00 come the pages the
  browser tests write (11 to 16 when the sweep began, 01 to 06 after), then
  the other pages in their order (01 to 10, 07 to 16 after). Page names reach
  the docs, the tests and the package, so the renumbering is a step of its
  own after step 7, on a branch that carries every stack.
- **Whether a made piece is saved as a variant stays open.** The page gives a
  made piece no Save or Variants, and the personal-data record says it is
  saved as a part is; the record pends on the answer.

## The measure

`check_timeless.py --all` sees the shapes a pattern can match: shouting in
capitals and a short list of phrases that only narrate. Its report on this
branch is the starting count and each area's pull request reports it again.
Most of what the sweep is for -- history told in ordinary words, statements
the code no longer bears out, counts a command computes, the same thing
said on several pages -- only a reader finds, so each area is read in full.

## Areas

1. Top-level and reference pages: `README.md`, `QUICKSTART.md`,
   `CONTRIBUTING.md`, `AGENTS.md`, `project/todo.md`, `docs/*.md`, `tests/e2e/README.md`,
   the parts and crates READMEs.
2. The walkthrough: pages 00-10 written by hand, pages 11-16 written by the
   browser tests that hold them.
3. The package's docstrings, comments and `--help` texts.
4. The page's comments, the tests' docstrings, and the CI and project
   configuration's comments.
5. The plans and validation records: which retire, and where their
   still-true decisions go.

The inventory of each area -- every passage, its problem and its home --
is in `timeless-docs-2026-10-12/`, one file per area, read against the
branch at `c67725a`; a sweep re-reads each passage against the text as it
stands before changing it.

## What the reading found

- **Top-level and reference pages** are mostly present tense already. What
  they carry is decisions told as events, the same instructions on several
  pages (the install and test commands, OpenSCAD's platforms and limits, the
  SCAD grammar), and some statements the code no longer bears out.
  `QUICKSTART.md` points nowhere; `docs/fitting-a-part.md` is half a
  proposal.
- **The walkthrough's hand-written pages** state their constraints through
  the stories that produced them; its generated pages are mostly sound,
  with a few false statements in the tests that write them, and a shared
  header that claims more than it asserts.
- **The package's docstrings** carry the most: decisions cited by date or
  plan, the old names of things, and past failures given as reasons; and a
  set of statements the code contradicts, one of them in the API's own
  description.
- **The page's comments and the tests' docstrings** tell how bugs were found
  rather than what a test holds, and retell the page's consolidation in
  several files. The census's classification rules are written down only in
  its test's ledger.
- **Plans**: most are finished and retire; a few stay open, one to be split.
  Three draft records lag the code, and the bench checklist moves to a
  present-tense runbook.
- **The gate** sees little of this, and two of its findings are false
  positives: "was found in" describing a search's result in the present <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory -->
  tense.

## The order of the sweep

Each step is its own pull request into this branch, stating passage by
passage which home each went to, and reporting `check_timeless.py --all`.

1. **Statements the code contradicts**, everywhere: they are wrong today,
   whatever the rule.
2. **The front door**: `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, walkthrough
   page 00, `--help` and the API's descriptions; `QUICKSTART.md` goes.
3. **Plans retire**: `docs/README.md` lists the finished ones under
   *History*, each still-true decision moves to its present-tense home, and
   no present-tense page or message links a finished plan as current.
4. **Reference pages**: the duplicated explanations gathered into the pages
   they belong to (OpenSCAD, pictures, configuration, the census), and the
   pages that repeat them pointing there.
5. **The package, by module**, worst first.
6. **The page, the tests and the configuration's comments.**
7. **The walkthrough**: the hand-written pages' constraints stated as facts,
   the generated pages' words in their tests, the shared header made true.
8. **Retrospectives**: the stories each step moved out, gathered by area and
   proposed to the corpus's `perspectives/` in one draft pull request.
