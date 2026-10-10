# Handbook — Style Guide: Where Explanation Goes

**Routing.** The style guide `PRINCIPLES.md` `minimal-legible-deliverables` names and routes here, rather
than to a record: *"Taste encoded as constitutional law degrades both."* This
page states requirements an author can be held to. One of them is a record:
`records/DRAFT-durable-text-states-what-is-true.md`, restated below under
*Timeless text*, which this page is the procedure for. Everything else here is
applied at review, and promoting a clause to record form follows
`handbook/public-by-default.md`'s promotion path.

**Audience.** Anyone writing in a QM repository, human or agent.

---

## The rule

**Every artifact has one job, and explanation has one home.** Four tiers, and
a sentence belongs to exactly one of them.

| Tier | Carries | Never carries |
|---|---|---|
| **Inline** — comments, docstrings | Clarifying facts about the code as it stands | Rationale, history, argument |
| **README** | A shallow onramp: what this is, how to start, where to go next | Depth. It is a table of contents that a reader passes through |
| **`docs/`** | The reference: contracts, interfaces, procedures, how to use the thing | Why the design is what it is |
| **`perspectives/`** — retrospectives | **Every why.** Rationale, incidents, what was learned, what an argument was | — |

**All whys go to retrospectives.** If a sentence answers *why is it like
this*, *what went wrong*, or *what we learned*, it belongs in
`perspectives/`, whatever file you happened to be editing when you wrote it.

## Timeless text

`records/DRAFT-durable-text-states-what-is-true.md` decides this, and this
section restates it. **Durable text states what is true now and what to do
with it, for a reader who was not there.** Durable text is anything read
later: docstrings and comments, `README.md` and `docs/`, handbook pages,
walkthroughs, `AGENTS.md`, records, configuration headers.

- **Present tense, about the thing as it is.** Say what it is, what it does,
  what it cannot do, and what the reader should do.
- **No internal history.** Not what the code replaced, what was missing
  before, what was found, by whom, when, or how often something failed. The
  commit, the pull request and the retrospective hold that. Where history
  explains a constraint, state the constraint and leave the history out.
- **No ornament.** No phrase set in capitals, no "the one that matters", no
  check described by what it caught. Bold marks a term or a short clause, in
  ordinary case.

A docstring that opens with a story becomes one that opens with the fact:

<!-- timeless: allow the struck-through quotation is the example of the habit -->
> ~~The table existed and nothing served it. A front end growing a designer
> had nowhere to put a design.~~
>
> Saved topology designs, over HTTP. A design is validated through its kind's
> configuration class and returned with the plane's verdict.

A limits section keeps its content and drops the volume: *What this cannot
do:* rather than the same words in capitals.

**The gate.** `uv run qm timeless` (in a project,
`python governance/qm/project-seed/ci/check_timeless.py`) refuses the
mechanical shapes on the lines a change adds; `--all --summary` measures what
remains in the whole repository. A deliberate exception is declared on the line
or the line above with `timeless: allow` and a reason. A story told in neutral
words passes the check and is the reviewer's to catch.

## Every home, and the class the tooling gives it

The four tiers above are where a *sentence* goes. This is where a *document*
lives.

**This table and `ci/doc_status.py`'s `classify` are one pair. When they
disagree, they are repaired together.**

| Home | Class | Holds | Binds |
|---|---|---|---|
| `records/` | `record` | Org decisions. Context and Alternatives are the exception below | Every QM project, once ratified |
| `handbook/` | `handbook` | Policy on QM's own conduct, and procedure with its verification | QM's conduct, not a project's design |
| `handbook/handoffs/` | `handoff` | Working instructions for the next session. Deleted when the work lands | Nobody. It is a note, and a stale one is a cost |
| `docs/` | `reference` | Contracts, interfaces, procedures, how to use the thing | Nobody. It describes rather than decides |
| `perspectives/` | `perspective` | Every why: rationale, incidents, what was learned | Nobody. Dated, attributed, non-binding |
| `protocols/` | `protocol` | A procedure run deliberately, and the record of its runs | Nobody. A protocol page owns the procedure, never the decision behind it |
| `curriculum/` | `curriculum` | A reading order, citing documents it does not restate | Nobody |
| `walkthrough/` | `walkthrough` | A worked example, executed by the ordinary test command | Nobody. It is evidence, per `show-it-by-running-it` |
| `PRINCIPLES.md`, `AGENTS.md`, `README.md` | `entry` | Read first, by everyone. Restates records it does not own, and declares each | Everyone reading them, which is why the restatement rule exists |

**`plans/` has no place in this table**, and `classify` calls it *not in a
governed directory*. A plan being executed is a handoff, a plan that was
executed is a retrospective, and a plan nobody is executing is neither; which
of those each file is, is a person's reading and not a rule.

## The one exception, and its boundary

A decision record's job *is* rationale: `TEMPLATE.md` requires Context and
Alternatives considered, and a record without them is not a record. The two
answer different questions:

- **A record** answers *why this decision* — prospective, bounded by the
  template, about a choice being made, stated as forces and trade-offs.
- **A retrospective** answers *why it went that way* — experience after the
  fact: what happened, what it cost, what a check would have caught.

An incident does not belong in a record's Context, and a design alternative
does not belong in a retrospective.

## Tests

Applied to a sentence you have just written:

1. **Will it still be true after the next commit?** If it describes an earlier
   state of the code or page, it is history.
2. **Does it survive a rewrite of the code it sits beside?** If yes, it is
   rationale, and it is in the wrong place if it is inline.
3. **Would a reader who disagrees with it still need it to use the thing?**
   If no, it is argument, not reference.
4. **Does it narrate an event?** Events belong in retrospectives. A file that
   explains what happened to it is a retrospective wearing another file's
   name.
5. **Is the README longer than the thing it introduces is deep?** Then it has
   stopped being an onramp.

## The first thing a stranger reads

The rules above say where explanation goes. This one is about how the opening
of a page is written, and it applies to whatever a reader meets first: the
README, the documentation landing page, the top of a getting-started guide.

**Write the first sentence for somebody who does not yet know why they should
care.** A real sentence, with a verb, in words they already have. Precision is
what the rest of the page is for.

An opening like this one fails a newcomer:

> The Quaternion Media constitution: the decisions that govern every QM
> project, the process that keeps them consistent, and the template each new
> project starts from.

It is accurate. It is also not a sentence — a colon and a list of abstractions,
with no verb — and it spends *constitution*, *corpus*, *govern* and *adopt by
reference* before the reader has any footing. Somebody who already understands
the corpus reads it as dense and correct. Somebody who does not reads it as a
wall and leaves.

Three habits carry most of the cost, and all three feel like care while you are
writing:

- **A definition where a reason belongs.** Say what a thing is *for* before
  saying what it *is*. A reader who knows why will tolerate a long definition;
  one who does not will not reach it.
- **Qualification in the opening line.** The exception, the caveat and the
  boundary are true and they are not the first thing. Put them a paragraph
  down, where they inform rather than obstruct.
- **A sentence that needs the punctuation to parse.** Em-dashes, colons and
  parentheticals stacked in one sentence usually mean two sentences are hiding
  in it. Split them.

**This is not a licence to be vague.** Nothing here says to drop a fact, soften
a claim, or leave out what a check cannot see. It says to order the same
material so that the reader is still present when the precise part arrives.
Every qualification removed from an opening line belongs somewhere further down
the same page.

**Test it by reading the first sentence to somebody outside the work.** If they
cannot say what this is for, the sentence has not started yet.

## What this looks like when it is wrong

A comment block arguing for the design above the code implementing it. A
docstring that opens with the story of how its module came to exist. A README
that a reader finishes instead of leaving. A configuration file whose header is
an essay about an incident. `perspectives/2026-08-09-explanation-in-the-wrong-place.md`
holds the reasoning.

Each is legible in isolation and costly in aggregate: rationale and history
next to code go stale silently, because nothing tests them and a later edit has
no reason to revisit them. A retrospective is dated and attributed, so it is
allowed to age — it says what was true on a day, and reads correctly forever.

## Applying it to what already exists

Existing text is swept, per the record's §6: each repository's durable text is
brought under these rules in its own pull requests, one area at a time, with
`check_timeless.py --all --summary` as the measure of what remains.

**Every passage the sweep touches is sorted into one of three homes**, and
nothing is dropped unsorted:

| What the passage is | Where it goes | How to tell |
|---|---|---|
| **A short fact** | Stays inline, in the present tense | It says what this code is, takes or returns, or cannot do, in a sentence or two, and is wrong if the code changes |
| **An explanation** | `docs/`, the reference page for the area | A concept, a rule or a behaviour a user needs at length, often true of several modules at once; it is still true next month |
| **A narrative** | A dated retrospective in the corpus's `perspectives/` | It tells how something came to be, what was found, by what, or what was learned, as an event |

A passage often holds all three. *"The plane declared that the pipeline ran,
the registry held the stub, so `stubs()` checks every `runs` declaration"*
splits into a fact for the docstring (`stubs()` lists registered shapes still
inheriting the base `run`), an explanation for the docs (a `runs` declaration
is checked against the registry), and a story for the retrospective (the
afternoon the plane said a stub ran). The sweeping pull request lists each
passage and its home, so a reviewer can check that nothing was lost.
