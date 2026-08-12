# QM-XXXX — One Executable Walkthrough per Repository

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-11 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P12 — show it by running it; P9 — minimal, legible deliverables |

## Context

Tests, reference docs, a demo and a cookbook are four names for one thing: a
worked example of the system behaving. The org has built that thing at least
seven times, in six repositories, and converged once.

The survey is unflattering and worth stating plainly. `dossier` has a
January reference suite that stalled, two documentation indexes that disagree
with each other, a screenshot suite that generates the README's images, and an
executable `disk cookbook` — four attempts, none aware of the others. `qmcp` has
sixteen reference documents totalling five thousand lines, a `cookbook` CLI
group, nine Metaflow demo flows, a smoke suite that imports them, and a second,
more abstract cookbook sitting uncommitted in a working tree since February.
`codecartographer` has forty-eight documents in two tiers, twenty superseded
ones in an archive, an in-app walkthrough, a Playwright suite that reads as one,
and an abandoned mkdocs build. `alfred` generates documentation *from* its
end-to-end suite and records five walkthroughs as video. `datum`'s prose *is*
its test suite. This corpus writes test names as governance sentences and never
built the documentation half.

The word does not even survive the trip: **"cookbook" means three unrelated
things across these repositories, and none of them is a document.**

The failure is not authorship. Every one of those artifacts was written
carefully, and several are good. The failure is that each needed a *second
thing kept in step with a first* — a document beside the code, a screenshot
beside the UI, a recipe beside the command it documents — and nothing made the
second thing cheaper to regenerate than to abandon. So they were abandoned, one
at a time, by people with better things to do.

**One instance converged, and it is the evidence this record rests on.**
`qmetronome` regenerates twenty-four screenshots, twenty-three recordings and
twenty-four user-guide pages from `./gradlew test` — the command a contributor
runs before opening a pull request — and they carry zero drift. Its screenshot
library runs permanently in *record* mode: it never compares, never gates. All
the regression protection sits in behavioural assertions in the same test
method, which drive the real production component through a real gesture and
assert what the engine did. The picture is a byproduct of the render those
assertions ran against.

The same repository contains the control. Two of its generated artifacts need a
*remembered* command: a changelog produced by a script, and a benchmark table
pasted from a device log. The changelog documents `v0.1.3`; the newest tag is
`v0.2.0`. Same author, same week, same standard — the artifacts riding the
command people already run are byte-perfect, and the ones requiring memory are
stale. That is the whole argument, and it needed no advocacy to produce.

## Decision

1. **Every QM repository carries exactly one `walkthrough/` at its root**, and
   it is the single path for development, onboarding and communication. Pages
   are `walkthrough/NN-<slug>.md`, ordinal first, ordered by filename. The
   convention is identical in this corpus and in every adopting project: a
   convention with a project-shaped hole in it is re-derived per project, which
   is how the org arrived at three meanings of "cookbook".

2. **The pages are executed by the repository's ordinary test command.** In a
   Python repository that is pytest with `--doctest-glob=*.md` and `walkthrough`
   on `testpaths` — four lines of configuration, no site generator, no second
   language in the toolchain, no build step, no committed rendered output.
   `datum` is the existence proof: `uv run --frozen python -m pytest -q -rs`
   gives `11 passed, 1 skipped` and there is no generator to maintain.

3. **The page is the executable, so there is no authority to settle.** The
   example a reader reads is the example that ran, and its printed output is in
   the page because the run produced it. When behaviour changes the page fails
   the build. This is mechanical because there is **no second copy** — the
   defect every prior attempt built a policing layer against has nowhere to
   occur.

4. **What text cannot hold is emitted by the test that asserts the behaviour,
   and recorded rather than verified.** A gesture, a rendered screen, a
   recording: a doctest cannot express these, and a repository whose subject is
   a user interface is not exempt from this record. For those:
   - the artifact is produced by the same execution as a **behavioural
     assertion**, against the real production component — not by a separate
     demo harness, which is a second copy wearing a different hat;
   - the artifact is **recorded, never compared**. A test that diffs images
     fails on a font and gets switched off; a test that asserts what the code
     did cannot be switched off without losing the test. Regression protection
     belongs in the assertion, and the picture is output;
   - the **generator asserts its own artifacts exist**. Fifteen lines turns
     "somebody forgot" into a red build.

5. **Regeneration rides the command contributors already run**, never a release
   step and never a documentation build. This is the clause the evidence is
   about: drift then arrives as an uncommitted diff in `git status`, which
   nobody can miss, rather than a staleness nobody sees.

6. **One registry is the content; every surface reads it.** Where a walkthrough
   has an index, a table of contents, an in-app help screen or a generated page
   set, those are renderings of a single declared list, and the entry's
   identifier is simultaneously its filename on every side. Renaming then cannot
   desynchronise, because there is one name.

   **No hand-maintained parallel list is permitted to shadow that registry.**
   `qmetronome`'s one fragile joint is a `.gitignore` that un-ignores each
   generated asset with forty-seven hand-written lines, checked against nothing.
   It is the only step in an otherwise closed pipeline that a contributor can
   silently skip, and it is precisely the shape the rest of the design exists to
   remove.

7. **A skip is not a pass, and a page that always skips is deleted.** Pages
   declare their runtime in their opening line:
   - **Hermetic** — no port bound, no network, no container, no browser. Pages
     `01` upward are hermetic until one genuinely cannot be. These run in CI on
     every pull request, and they are the reason this record does not oblige the
     corpus's own suite to acquire a socket.
   - **Runtime-bound** — a broker, a database, a browser, a daemon. These run in
     a job that **provisions the runtime and asserts it is reachable before
     collection**, so an absent service fails the build instead of vanishing
     into a skip count.

   A page that skips in every environment the org can provision is deleted, not
   carried. A demonstration nobody can run is not documentation; it is a claim.

8. **Onboarding and cookbook are separate pages and stay separate.** Onboarding
   is the first build — per-platform, with expected output and the failure modes
   named. The cookbook is a command table for somebody already set up. One
   document trying to be both serves neither, and `qmetronome` keeps them apart
   deliberately, with its contributing guide explicitly refusing to duplicate
   the onboarding page.

9. **Name what cannot be automated, and give it a written manual plan.**
   `qmetronome` carries a 265-line USB-MIDI test plan because a closed vendor
   library and real device calls cannot be shadowed. Honesty about the boundary
   is what keeps the automated half credible; an unstated boundary reads as
   coverage.

10. **The walkthrough is vendored, not copied.** A project gets the runner
    configuration from `project-seed/`, and its pages are its own. Copies rot
    and this corpus has the measurement: `apothecary`'s ADR workflow inlined its
    check instead of calling the shared one, froze at the 2026-07-04 seed, and
    sits seven seed revisions behind while the generated status document counts
    it as present.

## Consequences

- A newcomer has one path, and finishing it proves they can build, run and
  change the system — because each page executed on their machine.
- The reviewer's manual-validation checklist at release becomes "the walkthrough
  passed", which is a claim CI can make.
- Cost accepted, and it is real: generated media committed to a tracked path
  costs repository size — seventeen megabytes of recordings in `qmetronome`'s
  history — bought for rendering with no build step. A project may decline the
  media tier; it may not decline decision 3.
- Cost accepted: doctests are strict about whitespace and exception text, which
  makes some examples awkward to write and is the honest reason to keep pages
  short.
- Nothing here obliges an existing artifact to be deleted on adoption. Decision
  7 obliges deletion only of a page that can never run.

## Alternatives considered

**Generate the documentation from the tests** — `alfred`'s and `dossier`'s
direction. Sound, and both instances are in step today. Rejected as the default
because it costs a second toolchain, a committed build artifact and a guard test
to police the copy, and it can only ever hold the copy equal to a source that is
itself unread. Decision 4 keeps it for exactly the case where prose cannot
substitute, which is where `qmetronome` uses it and where it earns those costs.

**A documentation site** — `codecartographer`'s abandoned mkdocs build.
Rejected: a build step nobody runs produces a site nobody regenerates, and the
archive of twenty superseded documents in that repository is what that looks
like after a year.

**A cookbook as a CLI subcommand** — `dossier disk cookbook` and `qmcp
cookbook`. These are good tools and they stay. Rejected as the org-wide answer
because they document by running the product, so they cannot introduce it: a
reader must already have the product working, which is the one thing onboarding
cannot assume.

**Keep the status quo and write a style guide entry.** Rejected because the
status quo already includes seven careful attempts. The problem was never that
people did not know they should document; it is that the second copy was
cheaper to abandon than to maintain.

## Revision triggers

- A second repository's walkthrough diverges from the path convention in
  decision 1. The convention is then not carrying its weight and the record is
  re-cut around what the two have in common.
- A hermetic page acquires a runtime dependency without moving to the
  runtime-bound tier. Decision 7's tiering has failed and needs a check rather
  than a declaration.
- The doctest form proves unworkable for a repository whose examples are
  genuinely not text. Decision 4 becomes the default there and the record says
  which repositories are in which mode.
- `qmetronome`'s `.gitignore` negation list is either generated from the
  registry or removed. Decision 6's prohibition then has a worked instance
  rather than a named counter-example.

## Amendments

None.
