# Handbook — Style Guide: Where Explanation Goes

**Routing.** The style guide `PRINCIPLES.md` P9 names and routes here, rather
than to a record: *"Taste encoded as constitutional law degrades both."* This
page states requirements an author can be held to. It creates no gate a human
does not apply at review, and promoting any clause to record form follows
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

## The one exception, and its boundary

A decision record's job *is* rationale: `TEMPLATE.md` requires Context and
Alternatives considered, and a record without them is not a record. That is
not a hole in the rule, because the two answer different questions:

- **A record** answers *why this decision* — prospective, bounded by the
  template, about a choice being made.
- **A retrospective** answers *why it went that way* — experience after the
  fact: what happened, what it cost, what a check would have caught.

An incident does not belong in a record's Context, and a design alternative
does not belong in a retrospective.

## Tests

Applied to a sentence you have just written:

1. **Does it survive a rewrite of the code it sits beside?** If yes, it is
   rationale, and it is in the wrong place if it is inline.
2. **Would a reader who disagrees with it still need it to use the thing?**
   If no, it is argument, not reference.
3. **Does it narrate an event?** Events belong in retrospectives. A file that
   explains what happened to it is a retrospective wearing another file's
   name.
4. **Is the README longer than the thing it introduces is deep?** Then it has
   stopped being an onramp.

## What this looks like when it is wrong

A comment block arguing for the design above the code implementing it. A
README that a reader finishes instead of leaving. A docstring that opens with
what the author believes about software. A configuration file whose header is
an essay about an incident — which is how this page came to be written; see
`perspectives/2026-08-09-explanation-in-the-wrong-place.md`.

Each is legible in isolation and costly in aggregate: rationale next to code
goes stale silently, because nothing tests it and a later edit has no reason
to revisit it. A retrospective is dated and attributed, so it is allowed to
age — it says what was true on a day, and reads correctly forever.

## Applying it to what already exists

This corpus does not currently satisfy this page, and neither does every
project adopting it. Migration is per-file, on the branch that is already
touching the file, rather than a sweep: when you edit a file, move the
explanation you find in it, and leave the facts. A sweep across files nobody
is otherwise touching costs review attention and buys nothing that waiting
does not.
