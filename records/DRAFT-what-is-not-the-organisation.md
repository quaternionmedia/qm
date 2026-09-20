# QM-XXXX — The Workstation, the Agent and the Conversation Are Not the Organisation

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-20 |
| **Namespace** | org |
| **Binds** | This corpus, and any project that adopts it |
| **Pends on** | Whether `leak-check.yml` joins the seed workflows `records/DRAFT-project-phase-ladder.md` requires for v0.0.1. The seed ships it either way; the ladder decides whether its absence counts against a project. |
| **Principle** | `public-by-default` — what opens is the organisation's work, and the burden sits on closing; `credit-tracks-accountability` — a tool is an instrument a person directs, not a party, and so not a subject; `decisions-are-documented` — a decision enters as a decision |
| **Restated in** | `AGENTS.md` item 17; `project-seed/ide/AGENTS.md` item 14; `handbook/what-is-not-the-organisation.md` |

## Context

Every QM repository is public by default, and the corpus is read by people
and tools that were not present when a page was written. A page is written on
one machine, by one tool, in one conversation, and each of those three is
present and vivid at the moment of writing. Nothing in the writing tools
distinguishes a fact about the organisation from a fact about the afternoon.

The corpus already covers two edges of this. `records/DRAFT-human-only-contributorship.md`
keeps a tool out of the byline; `records/DRAFT-going-private-is-an-act-with-obligations.md`
keeps a private repository's name out of a public file, and
`project-seed/ci/check_leaks.py` keeps out a home directory, a
shared-conversation link and a conversation archive's path. Between those
edges a wide class went uncovered and was found committed in one cycle: a
path through a personal folder in the public roster, a handoff explaining
that a clone could not be moved because an editor held the folder, a process
seen running on one machine reported as a possible second session, a
retrospective section on the tool's own mistakes with a shell, and a standing
constraint written as *"the instruction was …"* — a person's words, reported
into a page that anyone can read.

Each of those was true. None of it was the organisation's, and once pushed to
a public repository none of it is recoverable from history.

## Decision

**A committed file states what is true of the organisation.** Three things
are present whenever a file is written and are not the organisation, and no
committed file describes them:

| Not the organisation | What it looks like on a page | Where it belongs |
|---|---|---|
| **The workstation** | a path through somebody's home layout; an editor or extension by name; a process seen running; how one operating system behaved once | the gitignored companions — `ci/workspace-local.yaml` for where a clone sits, `ci/workspace-private.yaml` for a private name and its paths, the inventory's local files — or the tool's own memory |
| **The agent** | the tool driving a session, named anywhere but a `Tools:` note; its context, memory, modes or permissions; its scratch files; its own mishaps with a shell or an editor; its subagents | the tool's memory; its adapter under `adapters/`; the session transcript, which is not in the repository |
| **The conversation** | what a person said, quoted or paraphrased; a link to it; its identifiers | nowhere. A decision enters as a decision — a record, a roster line, a constraint stated flatly — never as reported speech |

The test for a sentence is whether it would be true on another person's
machine, in another tool, in a session that never happened.

### What this does not forbid

- **The session as a unit of work.** `handbook/async-contract.md` governs
  many sessions at once, and a handoff records what one left: branches,
  commits, pull requests, what is blocked and on whom. That is state of the
  repositories.
- **People, where the organisation needs them.** An author on a perspective,
  an assignee on a pull request, a contributor holding a slot. A name is not
  a conversation.
- **A tool, once, in a `Tools:` note** — the disclosure
  `records/DRAFT-human-only-contributorship.md` permits and
  `perspectives/README.md` requires. The note names the tool and does not
  narrate it.
- **Setup a contributor must do once**, such as the fresh-clone section of
  `AGENTS.md`. That instructs anyone on that platform; it reports no machine.
- **Machine-scoped readings that are printed and never committed.** The
  estate survey, the cookbook's disk view and the harness's local layer each
  describe one disk on purpose and say so in their own output. This decision
  is about what is committed.

### A retrospective explains a decision, not a tool

`perspectives/` is where every why goes, and a why is about a reading or a
decision: what was assumed, what was true, which check would have caught it.
A tool's own operating mishap teaches the organisation nothing and does not
go in. If the mishap produced a defect in the corpus, the defect and its
check go in; the mishap does not.

### Commit messages and pull request bodies

A commit message describes the change. A pull request body states the
decisions the change carries, what was run, and what the branch holds.
Neither says who asked, what was said, or which session did it: the audit
record is the diff and the gates, and a message that narrates the
conversation behind it has published the conversation.

## Enforcement, and its edge

`project-seed/ci/check_leaks.py` refuses a tracked file that carries a home
directory, a path through a personal or IDE-made folder, a path into a
session's scratch space, a shared-conversation link, or a conversation
archive's path. The seed ships it as `leak-check.yml`, and this corpus runs
its own copy on every pull request into `main`. `ci/policy-registry.yaml`
lists the invariant with that detector.

The check sees paths and links. It cannot see an editor named in prose, a
process somebody saw, or a quotation; a pattern for those would fire on every
page that legitimately discusses editors or quotes a record, and a check
people turn off is worse than none. For those the reader is the check, and
`handbook/consolidation-runbook.md` Step 3 is where that reading happens,
before a push.

## Consequences

- A committed file that names where a clone sits on one disk, which editor
  held it, or what a tool did with its shell is a defect, fixed where it is
  found.
- One machine's layout has a home: `ci/workspace-local.yaml`, gitignored,
  adds candidate paths to a public roster entry by name. The committed
  roster's paths are the conventions — `<name>` and `qm/<name>` — and
  `ci/tests/test_roster.py` refuses a public entry whose paths leave them.
- A standing constraint a person sets is written as the constraint, not as
  the sentence that set it. Where it disagrees with another page, the
  disagreement is stated and left for a person.
- Handoffs are transient and go when their work lands; pages written before
  this record are not rewritten for it. What the check finds is fixed where
  it is found; what it cannot find is fixed when the page is next touched.

## Alternatives considered

**Pattern-match the prose.** A list of editor names, agent-mechanics words and
reported-speech phrases, refused wherever found. Rejected: `records/DRAFT-ide-integrated-governance-discovery.md`
names editors on purpose, `handbook/async-contract.md` is about agent
sessions, and every record quotes another. A pattern that fires on
legitimate pages is one people turn off, and then the mechanical part it did
catch goes with it.

**Leave it to the private-names rule.** Rejected: that rule covers a
repository's name and nothing else, by its own docstring, and the cycle that
produced this record was clean under it.

**Keep the workstation in the roster, since the roster is where paths are.**
Rejected: the roster's paths are where a clone goes on any machine — a
convention — and one machine's exception published as a convention misleads
every other machine. The local companion costs one gitignored file.

**Say nothing, and rely on care.** Rejected: that is this decision without
the sentence, and the cycle that produced it was run with care.

## Revision triggers

- The check gains a way to see a class it cannot see today, in which case
  the edge stated above moves.
- The ladder decides whether `leak-check.yml` is required for v0.0.1, which
  resolves the `Pends on` row.
- A legitimate use of a personal-folder path or a scratch path in a
  committed file appears; it is declared with `leaks: allow` and a reason, and
  the pattern is reconsidered if declarations accumulate.
