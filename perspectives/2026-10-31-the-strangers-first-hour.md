# The stranger's first hour — 2026-10-31

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-31 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Fable 5.1 coordinating; Claude Sonnet 5.5 on the four audit areas and the two skeptic passes |

The design review of this corpus that
`handbook/handoffs/design-review-of-the-estate.md` hands over ran on
2026-10-31 against `main` at `debf210`, by `handbook/design-review-runbook.md`,
trimmed to one scope: a stranger's first hour before the alpha. Can someone
with no context adopt the corpus from `main` alone and reach a working loop,
and which gaps stop them first, with outside testers arriving soon as the
measure. This page is how the review was run, what it was trimmed to and why,
and what the four audits say when read as one. The leads themselves, each with
its command, are in Part 1 of the handoff; this page carries the shape.

## What ran, and what did not

Phases 0, 1 and 3 of the runbook ran. Phase 0 was the lead's scripts against a
detached checkout of `main`'s tip, every output written to a file that ends
with its exit status and its finish time, so a reader can tell a finished
measurement from one still being written. Phase 1 was four readers, one per
area, on a cheaper model, each with a common preamble and an area brief as
working files outside the repository, with a forty-minute hard stop and a
forty-five-minute kill time stated before the launch. All four reported
inside fifteen minutes, so nothing is recorded as not run for want of time.
Phase 3 sent a skeptic to each finding that cut something: one finding of kind
`delete`, and one whose recommendation moves handbook content between pages,
which the handoff counts as a deletion. The count, two, was stated before the
launch.

Phase 2 did not run, by scope: a review that states leads fixes nothing, and
the one wrong answer the audits reproduce on `main` (a generated index missing
a row) is `main`'s to regenerate, which this review's own pull request does as
a side effect of adding a page. Phases 4 to 7 did not run: triage, execution
and the owner's decisions are the next session's, and the handoff says what
they start from.

## Why four areas and not ten

The handoff fits ten areas to a governance corpus. A stranger's first hour
touches six of them and only grazes the rest, so the ten fold into four, each
named for the stretch of the hour it covers: the reader's path (areas 10 and 5,
and the contradictions of 9), the adoption path run end to end into a scratch
project (area 7, and the entry path the runbook's Phase 0 asks for), the
working loop and its gates (areas 2, 3, 4 and 8), and the standing state a
stranger reads at open (areas 6 and 5, and the attribution lead of 9). Record
coherence, area 1, is dropped: a stranger does not reach the records' meaning
in an hour, and the semantic review the corpus already queues is that
reading's home. The rest of area 9, integers, drafts in place and protocol
budgets, is a maintainer's reading and is dropped too. Yield, the half of area
3 the handoff cares about most, could not be measured: the posture instrument
refuses a red baseline, and the baseline is red at this commit for the reason
in the next section.

Merging areas cost one thing. Two readers reached the same four gaps from
different sides, which is confirmation, and the handoff carries each once.

## Phase 0, and what the scaffolding did to it

Three of the Phase 0 measurements describe the review's own setup rather than
the corpus, and each took a second run to tell apart. The suite fails one test
at `debf210`, the trio demo's deployed-front-ends check, because its skip
condition asks whether two ports answer rather than whether the sibling clones
it needs exist; on the measuring machine other sessions' services answered
those ports and no clone sat beside the detached checkout, so a test that
skips on a stranger's machine ran and failed. The same failure turns the
posture baseline red, so test yield is unmeasured at this commit. And two
steps of the preflight, the site builds, fail with a Windows path-length error
from the detached checkout's deep scratch path; from a shorter path the build,
the generated-pages check and the docs audit all exit 0. Each is a finding
about the corpus too (a skip condition reading the wrong signal; a toolchain
that fails at a deep path with a message about a filename), and none is the
headline it looked like on first reading. `AGENTS.md` item 12 is the rule, and
this review needed it three times in an hour.

The rest of Phase 0 stands: `qm docs check` red on a missing index row with no
workflow to catch it; `qm queue` red against a stamp a week old; no branch
protection, no applied ruleset and no tag on the host; every rostered
repository `MISSING` to `qm estate` from a checkout with no siblings; leaks and
timeless text clean.

## What the audits found, read together

The four audits reached one verdict from four directions. **The corpus is
written for the person who already holds it.** Its first page tells a reader
to establish four facts, and two of the four commands need a host credential
the reader is not told to have, a third needs sibling clones the reader does
not own and reports its own clone missing with a clean exit, and the fourth
works. Its first-change recipe says to assign the person who asked and merge it
yourself; there is no contributing page, no outsider's path, and `main` is
unprotected, so write access is the only barrier and the only one nobody
names. Its fork procedure is careful and verifiable at every step, and its
second step pushes a branch to this repository, which an outsider cannot do,
with nothing before step 0 saying so. Its standing queue, which the first page
says to read at open, names a maintainer by first name, private references and
a companion file the reader does not have, and is red against its own stamp.

The second shape is **the gate that reports green while enforcing nothing, now
on the reader's side of the glass.** The reading budget is measured and
rendered as over, and a decision in force says it is under; nothing fails on
it. The gate registry promises a refusal the audit's code does not contain, and
declares a guard on `main` whose workflow triggers elsewhere. A path filter
leaves the tests unrun for the pages they execute. The generated-documents
check that would catch a stale index runs in no workflow. The earlier
retrospectives on this corpus (`2026-08-21-a-green-suite-and-eight-holes.md`,
`2026-08-23-the-rules-with-nothing-behind-them.md`,
`2026-08-25-defects-between-two-green-suites.md`) each describe this shape
in tooling; the stranger meets it in prose and in the help screen, where
fifty-five subcommands sit in one flat list and the page that calls the list
the whole surface names seven.

The third is **Windows**. The pointer files that carry governance to a tool
that reads only `CLAUDE.md` are symlinks, and without one setting a Windows
clone gets a nine-byte filename where the instructions should be; the remedy
is the last section of the longest page the stranger is told to read first.
The fork procedure's copy command lands the same files as regular files on
Windows and the working repair is a paragraph deep. A deep path breaks the
submodule add on an older Git for Windows and the site generator on any. Each
is stated somewhere in the corpus; none is stated where the stranger is when
they meet it.

What the audits did not find matters as much. The README's records index
matches every record's own status row. The one glossary covers every word the
README warns about; the handoff's lead about two glossaries is stale, and the
second one is gone. The "merge it yourself" clauses agree across every page
that restates them. Step 3 of the fork, the one with the longest warning about
phantom refs, behaves exactly as its page says, and the seed's ADR lint goes
red on a real banned form with the file and line. The suite and the preflight
leave the tree clean. The pages are honest about their own age: every status
document carries its stamp, its budget and its refresh command inside the
file.

## What the skeptics did to the deletions

Two findings went to skeptics and the pass earned its place twice over. The
one finding of kind `delete`, eight subcommands with no caller, is refuted: five
of the eight run in two workflows or are named in the gate registry and the
devloop module, and the other three are wired through the dispatcher and named
in a registry and an adapter command. The audit's scan matched one literal
spelling of a call and nothing else, which it said itself, and the skeptic's
first search found the callers. A deletion that reads as obvious from a help
screen is the kind the runbook sends a skeptic to, and this is why.

The second, splitting the standing queue and moving three of its decisions into
`AGENTS.md`, is upheld and trimmed in four places. The parser behind `qm
queue` reads the whole text, so a split breaks nothing mechanical; the cost is
in every page that cites the queue by section, and in perspectives whose
section citations are durable text. One of the three decisions is already in
`AGENTS.md`, so it does not move; one belongs to the reading-budget record and
restating it in `AGENTS.md` would raise the load it limits; one restates no
record at all. And the cheapest change for the stranger is smaller than a
split: the page's own close rule says the check exits 0, and it does not. The
skeptic's correction is what the triage should start from, not the finding's
recommendation.

## What this review cannot claim

It did not run the fork against a pushed `project/<name>` branch, because
pushing is a write to the organisation's repository, so everything after
step 2 was measured against a local stand-in. It did not run the Windows
symlink case from a clone without `core.symlinks`; that lead is derived from
git's semantics. It did not classify all fifty-five subcommands by what each
needs, only counted their callers. It did not measure test yield, for the
reason above. It did not read the records for meaning, and it did not ask
whether the host asks a maintainer to approve workflow runs on a pull request
from a fork, which would be one more barrier on the outsider's path and is a
host setting this review did not read. Every lead is a hypothesis with the
command that produced it beside it, and the commit it was measured at is
`debf210`; a later reader re-runs the command before acting.
