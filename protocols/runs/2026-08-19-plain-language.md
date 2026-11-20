# Run — Plain language review, 2026-08-19

**Protocol** `protocols/plain-language.md`. **Corpus** `main` at `341758e`,
plus this branch. **dossier** `main` at `546de67`. **qmcp** `main` at `31c6db8`.
Every figure below was true at those commits.

**Run by** an agent, at the operator's request. Reviewed by a human at merge.

---

## What the openings said

`uv run qm prose`, in each repository, before any change:

| repository | opened with |
|---|---|
| qm | *Every team keeps answering the same questions.* |
| dossier | *Decentralized project tracking and delta-centric change management for cross-domain teams.* |
| qmcp | *A spec-aligned Model Context Protocol (MCP) server built with FastAPI.* |

The corpus had been rewritten the day before, which is why its opening reads as
it does. The other two had not.

## What changed

**dossier** and **qmcp** open with a sentence naming a problem the reader
already has, before naming the thing that solves it. Neither tagline was
inaccurate; both required the reader to already know what a *delta* or a
*Model Context Protocol server* is in order to learn what the software does.

**The corpus's landing page** now links every word doing unusual work to its
definition — `record`, `Proposed`, `ratification`, the automated checks — and
`docs/ref/glossary.md` gained explicit anchors, plus entries for **Proposed**
and **Gate**, which the landing page used and the glossary did not define.

**`AGENTS.md` item 3** went from 840 words to 457, keeping every rule. Three of
its rules were retold in full from `handbook/async-contract.md` §1–§3; they are
now stated once and pointed at. The item number is unchanged because records
declare `Restated in: AGENTS.md item 3`.

## What the run found that prose review was not looking for

**A published link that 404s.** `docs/index.md` linked `../handbook/glossary.md`
— which is not published, because only `docs/` is deployed — on the same page as
a correct link to the same glossary. `qm docs audit` reported *links: 0
findings*, because it accepted any target that existed anywhere in the
repository. It now refuses a relative link that leaves the site, and a second
pre-existing dead link surfaced with it.

**Fragments were never checked.** The link regex discarded `#anchor` entirely,
so a fragment naming nothing passed and landed the reader at the top of a page.
Checked now, with the anchor slugs approximated rather than taken from the site
generator, and the tool says so when it complains.

**A stale item pointer, which this session created.** Inserting item 14 into
`AGENTS.md` renumbered everything below it, and
`records/DRAFT-the-read-document-governs.md` went on declaring *item 15* — which
is now a different rule. `check_restatements.py` stayed green because it verified
that the document cited the record *somewhere*. It now checks the item.

## What was left alone, and why

**The handbook and the records.** They are written for readers who have the
vocabulary, and that is correct. This protocol is about entry points.

**dossier's README below the tagline.** It opens with badges, four screenshots
and a quickstart before any prose. That is a structure question rather than a
sentence question, and changing it is a judgement about what a reader wants
first — which belongs to whoever owns that page.

**The corpus README's routing table.** Fifteen rows, and choosing one still
needs vocabulary a newcomer does not have.

## What this run could not see

Whether any of the new sentences is *true* to somebody who has never seen these
projects. Nobody outside the work read them. The protocol says to test an
opening by reading it to somebody outside the work, and that step was not
performed — it needs a person who is not the author.
