# Plan — Signals that governance prose has stopped inviting authorship

**Status: stub. Nothing here is built, and the decisions below are open.**

## The instance

`AGENTS.md` item 3, measured 2026-08-16 at `0e958c0`:

| | |
|---|---|
| Words | 840 |
| Paragraph breaks | 0 |
| Questions | 0 |
| Negations | 34 — one per 24 words |
| Absolutes | 22 |
| Average sentence | 24 words |

It is the most-read passage in the corpus, written by the operator with assistant-2026-08. A reader meets 840 unbroken words,
is told what to never do 34 times, and is asked nothing.

## The claim this plan rests on, which may be wrong

Prose can be correct and still foreclose. A passage with no questions, no
paragraph breaks and no marked-unsettled clause gives a reader nowhere to enter
and nothing to add — so the only available responses are comply, ignore, or
argue with the whole thing.

**That claim is untested here.** It may be that governance prose *should*
foreclose, and that the alternative produces documents nobody can act on. That
argument has not been had.

## Candidate signals, none of them settled

Offered as starting points, not as a specification:

- **Absolutes** — `never`, `always`, `exactly`, `only`, `whole`, `nothing`,
  `every`, `must`, `all`
- **Closure phrases** — "that is the job", "the whole safeguard", "and it is the
  only one", "nothing else"
- **Authority by anecdote** — "this has happened here", with no link to what
  happened
- **Negation density** — a ratio, threshold unknown
- **Block length without a break**
- **Questions per document** — zero is the signal
- **Absence of a `Pends on`-style marker** for what is genuinely unsettled

### Candidates added 2026-08-16, from a live incident

Three that are not about tone. Each shifts responsibility while reading as
neutral description, and all three were caught by the reviewer rather than by
any check.

- **An artifact as the grammatical subject of a harm.** *"after it nearly
  carried private names into a public repository"* — the nearest antecedent is
  the inventory, so the artifact takes blame for what a tool did. An artifact
  cannot carry anything anywhere.
- **Agentless passives in failure sentences.** *"a solved problem was
  reintroduced"*, *"the artifact carried"*. The actor is simply absent.
- **An unattributed instrument.** *"this tool"*, with nothing that says which.
  A failure attributed to an unnamed tool cannot be compared across incidents
  or counted per tool.

Worked example: `ledger.yaml` 2026-08-16-003. All three were in its first two
drafts.

**Answered for one of them.** The third is no longer a candidate: `tool:` is
required on every ledger entry and must resolve against `ci/tool-registry.yaml`,
on every entry rather than only the failures, because a register that named an
instrument in fault and stayed silent in credit would let it bank one and shed
the other. The first two remain candidates and nothing detects them.

**Open: which of these predict anything?** None has been correlated with a
reader failing to act. A linter built on untested signals would flag prose for
resembling a pattern nobody has shown to matter.

## Where this belongs, and why not here

**`quaternionmedia/looksatwords`** — *"A python module to make, gather, analyze,
and visualize language data."* It exists, it is the tool for this, and it is
**not in `ci/workspace.yaml`'s roster**, which is its own finding.

The corpus should consume that analysis, not implement it.
`records/DRAFT-governance-arrives-as-a-mechanism.md` §5 says converting beats
adding, and a corpus that writes its own linter for every concern becomes the
thing it warns about. `qm` would hold the thresholds and the decision about what
to do with a flag; `looksatwords` would hold the counting.

**Open: does `looksatwords` want this?** Nobody has asked. It has its own
purpose and this would be a consumer requirement arriving from outside.

## Decisions nobody has made

1. Is the foreclosure claim right, and how would we know?
2. Which signals earn their place, on what evidence?
3. Does a flag block anything, or only report? (This corpus's own answer
   elsewhere: report, because a check that blocks on style gets routed around.)
4. Does `looksatwords` take this, and on whose terms?
5. What is the corpus's own baseline, and is it allowed to get worse?

## What would make this plan wrong

A reader outside QM reads item 3 cold and acts on it correctly. Then the
measurements are describing a style somebody dislikes rather than a defect.
