# ADR-XXXX — Adopt the QM constitution, and scope looksatwords to language corpora

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-26 |
| **Pends on** | §4 C1 and C2 — who holds copyright in this project's output, and which outbound class it falls into. Both are a person's decision and neither is settled by declaring a string in a file. |

## Context

looksatwords predates its adoption of this corpus. It gathers, generates,
analyses and visualises natural language: a conversation transcript or a news
article goes in, and what comes out is structure over that prose — who spoke,
which topics were live and when, where the conversation went off and whether it
came back, and what the sentiment did along the way.

The corpus is now vendored at `governance/qm`, pinned to this branch, with the
six seed workflows and the IDE discovery files in place. That makes the project
*instantiated* — it carries the governance machinery. It does not make it
compliant, and `adr/README.md` is explicit that the two are different things.
The decision-record-discipline record's adoption clause requires a project in
that position to enumerate its conflicts with org records rather than to imply
it has none.

Two facts about the surrounding work shape the scope half of this record.

**The org already has a repository that maps a corpus as a graph.**
`codecartographer` parses source code and draws its structure. The obvious
question on adopting a second visualiser is what stops the two becoming one
tool with two front ends.

**The org already produces the corpus this project is best aimed at.** `qmcp`
archives assistant conversations as threads and extracts from them the
decisions they settled; `dossier` carries those decisions through a lifecycle.
Both of them treat a thread as a *unit of work* and deliberately discard the
turns: `qmcp/threads/base.py` says so in its opening lines — "a hundred turns
producing three decisions; the three are the deltas, the turns are not". The
turns are exactly what this project reads.

## Decision

### §1 — This project adopts the QM constitution by reference

Org records bind it. Project records may tighten them, never relax them. The
pin is this branch's ancestry, per `adr/README.md`.

### §2 — The subject is language, and the subject is the border

looksatwords takes **natural language** as input and emits structure over it.
`codecartographer` takes **source code** as input and emits structure over it.
Neither is defined by its output: both draw a graph, both serve it in a
browser, and both will keep doing so. The corpus each reads is the whole
distinction, and it is the test to apply to any proposed change:

- A change that makes this project parse a programming language belongs in
  `codecartographer`.
- A change that makes `codecartographer` read prose — commit messages, code
  comments as discourse, review conversations — belongs here.
- A change that needs both is a **seam**, and it crosses as HTTP and a schema,
  never as an import. `DRAFT-seams-on-standard-protocols.md` governs.

The test is deliberately about the input and not about the vocabulary. "Thread"
means one thing here and another in `qmcp`; "graph" means one thing here and
another in `codecartographer`. A border drawn on shared words would have put
this project inside both of them.

### §3 — This project reads turns; it does not author decisions

Where a corpus of assistant threads is the input, the division with `qmcp` and
`dossier` is fixed here so it is not rediscovered later:

| | reads | emits | owns |
|---|---|---|---|
| `qmcp` | its own archive | threads, and the decisions extracted from them | the archive; it is the one author of a thread row |
| `dossier` | those decisions over a seam | a lifecycle — brainstorm through complete | the delta record |
| looksatwords | the **turns** inside a thread | topics, thread-continuity, tangents, sentiment over time | nothing in either of the others |

This project **never writes a thread row, a decision, or a delta**. It reads
prose and reports structure over it. That keeps `qmcp`'s "one record, one
author" rule intact, and it is the same restraint `dossier/src/dossier/threads.py`
states about itself in its own opening docstring.

What it adds that neither of the others can: `qmcp` names the three decisions a
thread settled; this names what the other ninety-seven turns were *about*, when
a topic was dropped, and which digressions never resolved. A run on 2026-08-26
over eight lines of a conversation about the `qmcp`/`dossier` seam recovered
`Harness`, `Panel`, `Port`, `Loopback`, `Http`, `Seam` and `Precondition` as
threads with their live intervals, and flagged two unresolved tangents, without
being given any of that vocabulary.

### §4 — Known conflicts with org records, and how each is pinned

Enumerating a conflict is not waiving it. No schedule is implied. Scope is
frozen per conflict while it stays open.

| # | conflict | what it violates | established by | how it is pinned | what compliance looks like |
|---|---|---|---|---|---|
| C1 | Copyright is asserted in an individual | the outbound-licensing record §0 places copyright in Quaternion Media | `LICENSE` line 3, `pyproject.toml`'s `authors`, and `REUSE.toml`'s `**` block all read "Peter Kagstrom" | the files record the current state rather than declaring a different one | a person decides, and all three change together |
| C2 | Which outbound class this project falls into is undeclared | the same record requires the class to be named, not inferred from an identifier | `pyproject.toml` declares `license = {text = "MIT"}` and nothing states the class | MIT is what the repository already asserted; this record does not ratify it | the class named, and the identifier follows from it |
| C3 | One runtime dependency arrives from a CDN with no manifest | the open-license record's enforcement clause requires a dependency-manifest gate per package ecosystem | `looksatwords/frontend/index.html` line 9 loads `anime.min.js` 3.2.1 from `cdnjs.cloudflare.com`; there is no `package.json` in the repository | REUSE covers every committed file and cannot see a script fetched at page load | either vendor the file and licence it, or introduce the manifest and the gate that reads it |
| C4 | No service inventory and no baseline component audit | `adr/README.md`'s obligations table; neither is generated by any tool | absence | stated here | both written, per the obligations table |
| C5 | The tag gate has never run | `DRAFT-version-tags-are-claims.md` — a `v*` tag carries three claims | `tag-claims.yml` is wired and `run_workflows_locally.py` reports it skipped, not triggered by `pull_request` | no tag has been cut | the first tag exercises it, and the annotation names what the automated gate did not cover |

C3 has a consequence beyond licensing that is worth stating where a reader will
meet it: the visualisation's reveal animation depends on that CDN script. The
page degrades rather than breaking — there is a fallback path — but "the demo
works" is, today, a claim about a machine with network access.

### §5 — What this project takes as free, and what it will not take as free

The one dependency on a language model is a local Ollama on loopback. It is
free, so `DRAFT-no-unattended-spending.md` is satisfied rather than conflicted,
and this records how, because the satisfying arrangement is easy to lose:

- the host is not configurable and is loopback; the model is configurable and
  is `LOOKSATWORDS_OLLAMA_MODEL`;
- nothing here is scheduled, retried, or backfilled;
- the one test that reaches a model is marked `llm` and skips with a reason
  naming both the model it wanted and the models the machine holds.

**If a paid model is ever wired in, that record binds and this section is the
thing to reopen**, along with a `Budget` a person issues per command, on the
shape `qmcp/spend.py` already defines.

## Consequences

**Accepted costs.**

- The border in §2 means some work that would be cheaper as one repository will
  be done as two, and a seam will be paid for. That is the trade
  `DRAFT-build-the-seam-buy-the-engines.md` already makes for this org.
- §3 forbids the shortest path to a useful feature — writing a decision row
  directly into `dossier` — and requires asking the owner instead.
- C3 blocks an offline-complete demo until it is closed.

**Obligations created.**

- The six seed workflows run on every pull request here.
- The obligations table in `adr/README.md` is this project's to work through;
  C4 names the two that are furthest from done.
- Any change that starts parsing a programming language is out of scope under
  §2 and needs this record amended before it lands, not after.

## Alternatives considered

1. **Fold looksatwords into `codecartographer` as a second parser.** Both draw
   graphs of a corpus in a browser, and one repository would have meant one
   renderer, one deployment and one licence surface. It loses because the
   corpus is the border and nothing else is: a code graph's nodes are declared
   and its edges are resolvable, while a conversation's topics are inferred and
   its edges are a judgement a person has to be able to check. Merging them
   would have put a TF-IDF threshold and an import resolver behind one
   "accuracy" claim.

2. **Fold it into `qmcp` as a thread analyser.** The archive is right there and
   this project's best corpus is inside it. It loses on §3: `qmcp` is the one
   author of a thread row, and a module inside it that both reads turns and
   writes rows would erase the distinction that makes the archive auditable —
   the same argument `dossier` made when it chose a loopback seam over an
   import.

3. **Adopt the corpus and declare no conflicts.** Cheaper, and it is what a
   reader would infer from a fork that copied the seed cleanly. It loses
   because `adr/README.md` says a project is not compliant because it copied
   the seed, and C1 through C5 are all true today. A conflict table nobody
   writes does not make the conflicts go away; it makes the next person
   discover them one at a time.

4. **Defer the scope half and adopt only.** Adoption is mechanical and scope is
   a judgement, so splitting them would have let this land sooner. It loses
   because the org is standing up a fourth repository that draws graphs, and
   the question a reader will have on day one is what stops it becoming the
   second code tool. Answering that later means answering it after somebody has
   already had to guess.
