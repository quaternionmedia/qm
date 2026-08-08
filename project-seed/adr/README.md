# Architecture Decision Records — Process & Handoff

<!-- SEED FILE: copy verbatim into this project's own branch of the qm repo
     (project/<name>, created from main) as adr/README.md, and delete this
     comment. See root README.md's "Forking a new project" section. -->

This directory is the project's decision memory. This file is the contract
for producing and maintaining it. The discipline exists because decision
documents drift in a specific, predictable way — drafts accumulate references
to their own revision history, numbers get assigned before ratification and
then need "renumbering," and supersession language leaks into documents that
were never published. The rules below make the discipline mechanical instead
of dependent on any one contributor's (or assistant's) memory.

## Adopted org records

This project adopts the QM constitution by reference. Org records bind this
project; project records may tighten them, never relax them. A genuine
exception is an amendment ratified at org level.

This directory lives inside the `governance/qm` submodule, on this
project's own dedicated branch (`project/<name>`, created from `main`) -
not copied into this project's own git history. The branch's ancestry *is*
the pin: there is no separate commit hash to hand-maintain here. `git log
--first-parent` on this branch shows exactly which org state was adopted
and when it was last refreshed.

Bumping the pin is merging `main` into this branch - a normal git
operation, reviewed the same way any other commit to this branch is.

## The one rule that prevents most drift

> **Before ratification, documents have no memory. After ratification, they
> have nothing but memory.**

- A **draft** is rewritten in place as understanding improves — squashed, as
  if the final position had been held from the beginning. Git is the
  archaeology; prose is not. A draft never says "previously," "supersedes the
  earlier stance," or "corrected in review."
- An **Accepted** ADR is append-only. Its body is never silently edited.
  Changes are dated entries under **Amendments**; reversals are a new ADR
  that **supersedes** it. Supersession is a relation between *ratified*
  documents only.

## Lifecycle

```
Draft ──▶ Proposed ──▶ Accepted ──▶ (Amended*) ──▶ Deprecated | Superseded by ADR-NNNN
  ▲           │
  └── squash ─┘   (any change before Accepted = rewrite in place)
```

| Status | Meaning |
|---|---|
| **Draft** | Being written. Numberless (`ADR-XXXX`). Rewritten freely. |
| **Proposed** | Complete; pending a named input (`Pends on`) or ratification. Numberless. |
| **Accepted** | Ratified. Number assigned. Append-only from here. |
| **Deprecated** | No longer applies; nothing replaced it. Body intact. |
| **Superseded** | Replaced by a named ADR. Body intact, header points forward. |

## Numbering

Numbers are assigned **at ratification, by the index below, in order of
acceptance** — never during drafting. Drafts reference each other by *title*.
Once assigned, a number is permanent; gaps are fine; numbers are never
reused. Project numbering is local (`ADR-NNNN`); org records are `QM-NNNN`.

## Authoring rules

1. **One decision per ADR.**
2. **Org records are constitutional** — component selections must pass the
   open-license record; gaps route through its upstream-contribution
   remediation; seams pass the replaceability test.
3. **Alternatives are written honestly** — each with the real reason it lost.
4. **Every ADR has revision triggers** — observable events, not vibes.
5. **Open questions are not decided by stealth** — undecided input → status
   Proposed with an explicit `Pends on`.
6. **External history is context; internal history is noise.**
7. **Build-time patches are registered** in the org carried-patch register
   before the patch ships.

## Drafting-session handoff (humans and AI assistants alike)

**Inputs to provide the session:** this file; the pinned org records
(minimally the open-license record); the current index; the project design
plan and any ADRs being touched.

**Session obligations:** plan first, with a contradiction check against the
org records and the index; squash continuously (the chat may discuss a
position change; the document may not); never assign numbers, never
renumber, never write supersession language into a draft; mark pending human
decisions as Proposed with `Pends on`; end by outputting drafts, the proposed
index diff, and the open-question list. Ratification — status flip, number
assignment, index update — is a **human commit** naming the record.

**Verification obligations:** state at the start which commit the session is
working against, and check it is the one that matters — a review of a stale
branch is a confident claim about code nobody is running. Establish claims of
fact by execution rather than from memory: run the command, read the output,
record what was run. This applies hardest to the three cases that look least
like they need it —

- *a tool's behavior* — flags, defaults and output formats are the single
  most common source of confident error, and cost under a minute to check;
- *a documented step* — verify the artifact it produced, not that the step
  ran. Its instructions were written by someone for whom they worked;
- *your own setup* — before reporting a defect in the project, rule out the
  harness. A false defect report spends someone else's day;
- *the source versus the artifact* — a grep over `src/` is evidence about
  `src/`. A build step, a routing layer or a module nothing imports sits
  between what you read and what runs, and each can leave the source reading
  exactly as claimed while the running system behaves differently. Claims
  about a deployed system are settled against the deployed system.

A claim that has not been reproduced is marked as inference rather than
stated flatly. And **a passing test is not evidence until it has been seen to
fail**: run the negative case, or the test may be passing for a reason
unrelated to what it claims to cover.

**Delivery is always a pull request.** A session works on a branch and opens
a PR; it does not commit to, merge into, or push a shared branch directly,
and it does not merge its own work. This holds for every change a session
makes, not only for the ratifying commit — a mechanical fix, a typo, and a
new record all arrive the same way, because the review is where a human takes
responsibility for what the corpus says. A session that cannot open a PR
stops and hands the branch back rather than merging it.

**A pull request states decisions, not questions.** Every input the session
was unsure of is settled before the PR is opened — asked in the session, and
waited on. A PR carrying the session's own open questions hands the drafting
back to the reviewer and calls it review, which is the opposite of the
handoff this contract exists to produce. This is distinct from a record's
`Pends on` row: that names an input *the organisation* has not settled, and a
Proposed record naming one is this process working correctly.

**Session prohibitions.** Two kinds, and they are enforced differently.

*Mechanically checked:* the banned-vocabulary set the ADR lint enforces over
prose. `project-seed/ci/adr_lint.py` is its single source — read the set
there rather than from a copy, because a copy drifts. Quoting the set inside
a code span is not a violation; the check reads prose only.

*Not checked, and therefore on you:* assigning a number before ratification,
writing supersession language into a draft, framing an adoption-time rule as
though it reached backwards, and editing an Accepted body outside its
Amendments region. The last of these the lint does catch; the first three are
shapes rather than strings, and no regex recognises them reliably.

## CI enforcement

The ADR lint enforces four checks: banned vocabulary in drafts; numbered
filenames not Accepted+; Accepted bodies modified outside Amendments; and
index/directory mismatch. It ships as a ready-to-run workflow at
`project-seed/ci/adr-lint.yml` — copy that file into `.github/workflows/`
verbatim, the same discipline as `adr/` itself.

Only the workflow is copied. It runs
`governance/qm/project-seed/ci/adr_lint.py` out of the submodule, so the
checks are always the version this project's governance pin points at, and a
fix to the lint reaches every project on its next pin bump instead of
needing N copies updated.

The vocabulary check reads prose only — fenced code, inline code spans, and
HTML comments are excluded. A document that *quotes* the banned list is
describing the rule, not breaking it, which is why the template's own
drafting-rules comment and the discipline record's own enumeration do not
trip it.

The license gates required by the org open-license record are doctrine
rather than one fixed script, and they are cumulative: wire an SBOM per
image for container and server runtimes **and** a
dependency-manifest-plus-allowlist gate for each package ecosystem the
project ships, along with the service inventory that record's §6 requires
and no scanner can produce. A project with more than one runtime shape has
more than one obligation, not a choice among them. All of it runs in the
same pipeline as the ADR lint — the constitution and its enforcement ship
together.

## Index

| # | Title | Status | Date |
|---|---|---|---|
| | | | |

Drafts in flight (numberless, by title): —
