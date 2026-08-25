# Perspective — Defects Between Two Green Suites: What One Local Integration Round Found

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5, the assistant that wrote both sides of the seams described here and then ran them against each other |
| **Task** | A short retrospective on one session spent running `qm`, `qmcp` and `dossier` together on one machine, rather than testing each. Four defects were found. Every one of them sat between two passing test suites, and one of the four had been introduced by this same assistant earlier in the same session. |

## 0. Standing, scope, and evidence base

One session, one machine, three repositories at named commits. Every figure is
one run at one commit.

- **E1** — directly observed: process output, HTTP status codes, payload
  contents, `pytest` results.
- **E2** — read from the repositories: source, comments, git history.
- **E3** — inference, marked where it appears.

## 1. What was done

The harness was started on loopback (`uv run qmcp serve`). Then, against the
running process:

1. `dossier`'s topology reader was pointed at it and asked for the `governed`
   shape at each of its three levels.
2. `qmcp`'s own client was constructed with its own defaults and asked for
   `/health`.
3. A governed run was executed twice — once against a zero budget, once against
   an authorised one and a local stub — and both outcomes were posted to the
   live human queue.
4. The harness payload was regenerated and read back through `dossier`'s reader.

That is the whole method. It is not a technique; it is turning the things on.

## 2. What it found

**One seam was correct and is reported first**, because a green result obtained
by running something is evidence and deserves the same weight as a red one. The
topology seam needed no change: `governed` reached `dossier` at all three
levels, with its refusal arrows and its `spends` declaration intact, through
code neither side had been changed to accommodate.

**The client could not reach the server.** `MCPClient()` defaulted to port 3333;
the server serves 3141. The client this package ships could not talk to the
server this package starts (E1: `ConnectError` on the default, `{'status':
'healthy'}` on the explicit address).

The interesting part is the provenance. `qmcp/config.py` carries a comment
explaining that 3333 is what the harness *used to* serve while a control panel
looked on 8000, and that the mismatch had the panel reporting an absent archive
while the harness served two hundred threads (E2). The port was moved to fix
that. Four call sites did not move with it. **The comment recording the lesson
outlived the correction it described**, and nothing in either suite noticed,
because no test on either side constructs a default client and points it at a
default server.

**The human queue truncated in silence.** One constant, `RECENT = 10`, capped
both the invocation window and the queue of questions waiting on a person. A
queue of fifteen crossed as ten — the ten *oldest* — and the payload said
nothing about the five it dropped (E1). Both governed runs had been queued
moments earlier; neither appeared. A person acting on `dossier`'s Outstanding
list was acting on a work list that had quietly discarded the most recently
asked.

**A refusal and a draft read identically to a person.** Both surfaces that show
the queue carry `prompt` and not `context`. A governed run's state was in the
context, so `qmcp human list` showed two rows with the same text, separable only
by reading the identifier suffix (E1).

**And the fourth was this session's own.** A documentation page merged earlier
the same session told a reader to `curl localhost:8000` — a third port, wrong in
a fourth way, written by the assistant that had just read the comment explaining
why 8000 was wrong. It was found in the first minute of the round.

## 3. The pattern, which is the reason to write this down

Every defect above sat between two passing suites.

`qmcp`'s tests were green. `dossier`'s tests were green. The two projects even
share generated payload vectors, produced by the real emitter rather than
hand-written, precisely so that neither side tests against its own invention.
None of that helped, and the reason is structural rather than a lapse:

- The client's default was tested — as a string, against itself.
- The server's port was tested — as a setting, against itself.
- The payload's queue was tested on both sides — **against a payload that had
  already been truncated**, which both sides agreed was a queue.

A check on each side of a seam is not a check on the seam. Two suites agreeing
about a truncated list produce two green results and one wrong answer, and the
agreement is what makes it invisible: each side is correct about the thing it
was given.

This is the corpus's own P16 in a form the record does not yet state. P16 says a
check is evidence only after it has been seen to fail, and the mutation
discipline that follows from it operates *within* a component. The seam has no
owner, so it has no mutation, so nobody has watched it go red.
`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md` would be
stronger for saying so. **This is a suggestion for a maintainer, not a change to the record.**

## 4. What it cost, and what that suggests

The round took part of one session including the fixes. It produced four
defects, of which two — the silent truncation and the unreachable client —
would have been found by a user rather than by a test, and one had been shipped
in this same session.

The observation worth keeping is not "integration testing is good". It is
narrower and more actionable: **the defects were in the places where two
correct things meet, and every one of them was visible within a minute of the
processes actually running.** No fixture reproduced them. No amount of care
within either repository would have.

E3, and offered as opinion rather than finding: the reason this is rare is that
starting three processes is manual and slightly tedious, while running a suite
is one command. That is a tooling gap rather than a discipline gap, and the
remedy is a command that stands the three up together — which does not exist
today and is not proposed here, because proposing it is cheap and it is the
maintainer's call whether the estate is stable enough to be worth one.

## 5. What to distrust in this document

The measurements are checkable and were checked by running them. The
explanations — particularly the claim in §3 about *why* two green suites missed
these — are mine, and the alternative reading is duller and may be right: that
nobody had gotten around to it yet, and no structural account is needed.

One further caution. Three of the four defects were introduced or last touched
by the same assistant that then found them, which makes this a report on its own
work. The finding rate says something about the method; it says nothing
reassuring about the author.
