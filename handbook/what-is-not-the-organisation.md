# Handbook — What Is Not the Organisation

**Routing.** Policy for what a committed file in a QM repository may describe.
`handbook/public-by-default.md` says work opens unless a named reason closes
it; this page is the other edge of the same line — what was never the
organisation's to open. Clauses that acquire a dispute are promoted to record
form by that page's promotion path. The mechanical part is checked by
`uv run qm leaks`; the rest is the writer's.

**Audience.** Anyone writing in a QM repository, human or agent, and above all
an agent closing a session.

---

## The rule

**A committed file states what is true of the organisation.** Three things are
always present when the file is written and are not the organisation, and
none of them enters it:

| Not the organisation | What it looks like on the page | Where it belongs instead |
|---|---|---|
| **The workstation** | a path through somebody's home layout; an editor or extension by name; a process seen running; how one operating system behaved once | the gitignored companions (`ci/workspace-local.yaml`, `ci/workspace-private.yaml`, the inventory's local files); the tool's own memory |
| **The agent** | the tool driving the session named outside a `Tools:` note; its context, memory, modes or permissions; its scratch files; its own mishaps with a shell or an editor; its subagents | the tool's memory and its adapter under `adapters/`; the session transcript |
| **The conversation** | what a person said, quoted or paraphrased ("the instruction was…", "asked for…"); a link to it; its identifiers | nowhere. A decision enters as a decision — a record, a roster line, a note on a page that states the outcome — never as reported speech |

The test for a sentence is whether it would be true on another person's
machine, in another tool, in a session that never happened. A roster line
saying a clone goes at `qm/<name>` passes. A handoff saying a clone could not
be moved because an editor held the folder does not: the editor and the folder
were one afternoon's, and the next reader has neither.

## What this does not forbid

- **The session as a unit of work.** `handbook/async-contract.md` governs many
  sessions at once, and a handoff records what one left: branches, commits,
  pull requests, what is blocked and on whom. That is state of the
  repositories, and it stays.
- **People, where the organisation needs them.** An author on a perspective,
  an assignee on a pull request, a contributor holding a slot. A name is not a
  conversation.
- **A tool, once, in a `Tools:` note** — the disclosure
  `records/DRAFT-human-only-contributorship.md` permits and
  `perspectives/README.md` requires. The note names the tool; it does not
  narrate it.
- **Setup a contributor must do once**, such as `AGENTS.md`'s fresh-clone
  section for symlinks. That is an instruction to anyone on that platform,
  not a report of one machine.
- **Machine-scoped readings that are printed and never committed.**
  `uv run qm estate`, `uv run qm cookbook` with no argument, and the local
  layer of the harness all describe one disk on purpose, and each says so in
  its own output. The rule is about what is committed.

## A retrospective explains a decision, not a tool

`perspectives/` is where every *why* goes, and a why is about a reading or a
decision: what was assumed, what was true, what check would have caught it.
A tool's own operating mishap — an escaping mistake in a shell, a permission
it lacked, a file it wrote to the wrong place — is the tool's to remember and
teaches the organisation nothing. If the mishap produced a defect in the
corpus, the defect and its check belong on the page; the mishap does not.

## Commit messages and pull request bodies

A commit message describes the change. A pull request body states the
decisions the change carries, what was run, and what the branch holds. Neither
says who asked, what was said, or which session did it; the audit record is
the diff and the gates, and a message that narrates the conversation behind it
has published the conversation.

## The check, and its edge

`uv run qm leaks` refuses a tracked file that carries a home directory, a path
through a personal folder or an IDE's projects folder, a path into a session's
scratch space, a shared-conversation link, or a conversation archive's path.
It runs in `registries.yml` on every pull request. It cannot see an editor
named in prose, a process somebody saw, or a quotation — a pattern for those
would fire on every page that legitimately discusses editors, and a check
people turn off is worse than none. For those, the reader is the check, and
the handoff contract asks the reader to look.

## Applying it to what already exists

Handoffs are transient and go when their work lands; the pages written before
this one are not rewritten for it. What the check finds is fixed where it is
found. What the check cannot find is fixed when the page is next touched.
