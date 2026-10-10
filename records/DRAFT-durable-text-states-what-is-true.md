# QM-XXXX — Durable Text States What Is True, Not How It Came To Be

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-10 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `decisions-are-documented` — decisions are documented or they didn't happen; `minimal-legible-deliverables` — minimal, legible deliverables |
| **Restated in** | `AGENTS.md`, `handbook/style-guide.md` |

## Context

Durable text is read by somebody who was not there: a new contributor, a
reviewer a year on, an agent opening the repository with no briefing. What
that reader needs from a docstring, a handbook page or a record is what the
thing is, what it does, what it cannot do, and what to do with it.

Text written during the work tends to carry the work's story instead: what
the code replaced, what it lacked before, which incident prompted a check,
how many attempts failed before one held. To the person who lived it, the
story is the reason the text matters. To a cold reader it is noise they must
read through to reach the instruction, about events they cannot see and
cannot verify.

The story also stops being true. `Nothing served the table` describes the
repository before a change; once the change lands, the sentence is about a
state the reader will never find. It sits beside code that has moved on, and
nothing tests it.

`decisions-are-documented` already settles where history lives: drafts have
no memory, and Git is the archaeology. Pull request bodies and dated
retrospectives in `perspectives/` carry the rest. Authoring rule 6 of
`project-seed/adr/README.md` states the same line for project records —
external history is context, internal history is noise — and no rule states
it for the rest of the durable text.

A second habit compounds the first: emphasis carried by volume. Whole
sentences set in capitals, a test introduced as the one that matters, a
check described by what it caught. Each reads as the author's conviction
rather than the reader's instruction, and when every docstring opens by
shouting, the emphasis stops marking anything.

## Decision

**Durable text states what is true now and what to do with it, for a reader
who was not there.**

Durable text is anything meant to be read later: module, class and function
docstrings and comments; `README.md` and `docs/`; handbook pages; walkthroughs;
`AGENTS.md` and `PRINCIPLES.md`; records; configuration headers; the notes a
generated view prints beside its tables.

1. **Present tense, about the thing as it is.** A sentence describes what the
   code, the page or the decision is and does, or tells the reader what to
   do. Limits are stated the same way: what the thing cannot see, and what a
   reader should therefore check for themselves.

2. **No internal history.** Durable text does not narrate how it came to be:
   what it replaced, what was missing before it, what was found, who found it,
   when, how often something failed, or what an earlier version said. That
   account belongs to the commit message, the pull request body, or a
   retrospective in `perspectives/`, each of which is dated by construction.
   Where the history explains a constraint a reader must respect, the
   constraint is stated as a present fact and the history is left out.

3. **No ornament.** Emphasis is earned by placement and plain words. Durable
   text does not set whole phrases or sentences in capitals, introduce itself
   as the important part, or describe a check by its catches. Bold marks a
   term or a short clause a reader must not miss, in ordinary case.

4. **What stays.** External history — an upstream relicense, a standard's
   revision, a vendor's status — remains context in a record, where the
   template already places it. A record's Context and Alternatives still
   answer *why this decision*, stated as forces and trade-offs rather than as
   events. Retrospectives, handoffs and a pull request's verification section
   are about a moment and are exempt, as each is dated or deleted.

5. **The mechanical part is a gate.** `project-seed/ci/check_timeless.py`
   refuses, on the lines a change adds, the shapes a program can recognise:
   a run of capitalised words set as a phrase, and the phrases that only
   narrate. It runs in this corpus and, from the seed, in every project. A
   deliberate exception is declared on the line with `timeless: allow` and a
   reason. What the check cannot recognise — a story told in neutral words —
   is for the author and the reviewer.

6. **Existing text is swept, not left for the next edit, and every passage is
   sorted.** Each repository's durable text is brought under §1 to §3 in its
   own pull requests, area by area, with the check's full report as the measure
   of what remains. Each passage the sweep touches goes to one of three homes:

   - **A short fact stays inline**, in the present tense: what the thing is,
     its contract, its limits.
   - **An explanation moves to the reference documentation** (`docs/`): a
     concept, a rule or a behaviour a user needs at length, especially one
     that spans several modules.
   - **A narrative moves to a dated retrospective** in the corpus's
     `perspectives/`: how the thing came to be, what was found and by what,
     and a lesson told as an event.

   The pull request that sweeps an area states, passage by passage, which home
   each one went to.

## Consequences

Docstrings and pages get shorter, and their first sentence becomes the
instruction a reader came for. A reader can trust that what a page says is
about the present, and can find the story, when they want it, in the history
Git already keeps.

The sweep has a cost: review attention across every repository, a new
retrospective for each area whose stories are worth keeping, and reference
pages that grow by the explanations they take in. Nothing is lost in the
sorting: a constraint a story held survives as a fact, and the story itself is
kept, dated, where a reader looking for it will find it.

The gate has a cost: an occasional false positive, declared with a reason
that is counted on every run, and a class of narrative it cannot see, stated
in its own output.

`handbook/style-guide.md` keeps the taste that is not a rule — the shape of
an opening sentence, punctuation, length — and is the procedure for this
record's clauses.

## Alternatives considered

1. **Leave it to the style guide, as `minimal-legible-deliverables` routes
   taste.** The guide already says inline text carries facts and never
   history, and the habit persisted across the corpus and its projects. A
   sentence that stops being true is a correctness problem, not a matter of
   taste, and a rule with no gate lost to the habit.

2. **Delete the stories, relying on Git to keep them.** Git does keep them,
   in a form nobody reads: a lesson recorded only in a deleted docstring is
   found by somebody who already knows to look. Several of the stories carry
   lessons no retrospective records, and moving them costs a page per area.

3. **Migrate per file, on the branch already touching it.** Text nobody is
   editing would carry the habit indefinitely, and every new reader meets it
   first. A sweep spends review attention once.

4. **Check whole files rather than added lines.** Every repository would fail
   until its sweep finishes, and the gate would be switched off. Checking
   added lines holds the line from now while the full report measures the
   sweep.

## Revision triggers

- The check's allowances grow faster than its findings shrink, which would
  mean its patterns misfire on ordinary prose.
- A repository's sweep finishes and its full report is clean, at which point
  the gate can read whole files there.
- A new kind of durable text appears that is about a moment by nature and
  needs §4's exemption.

## Amendments

*None.*
