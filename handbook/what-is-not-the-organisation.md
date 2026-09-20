# Handbook — What Is Not the Organisation

**Routing.** The decision is `records/DRAFT-what-is-not-the-organisation.md`,
and this page restates it as the thing to do; where the two disagree the
record is what the organisation decided. `handbook/public-by-default.md` says
what opens; this is the other edge of the same line — what was never the
organisation's to open.

**Audience.** Anyone writing in a QM repository, human or agent, and above all
an agent closing a session.

---

## The rule, in one sentence each

A committed file states what is true of the organisation. Three things are
present whenever a file is written and are not the organisation:

- **The workstation** — a path through somebody's home layout, an editor or
  extension by name, a process seen running, how one operating system behaved
  once. It goes to a gitignored companion (`ci/workspace-local.yaml` for where
  a clone sits, `ci/workspace-private.yaml` for a private name) or nowhere.
- **The agent** — the tool driving the session named outside a `Tools:`
  note, its context, memory, modes, scratch files, or its own mishaps with a
  shell. It goes to the tool's memory or its adapter, never to a page.
- **The conversation** — what a person said, quoted or paraphrased, a link
  to it, its identifiers. A decision enters as a decision, never as reported
  speech.

**The test for a sentence:** would it be true on another person's machine, in
another tool, in a session that never happened?

What the rule leaves alone: the session as a unit of work, people as authors,
assignees and slot holders, a tool named once in a `Tools:` note, setup a
contributor must do once, and machine-scoped readings that are printed and
never committed. The record has the list with its reasons.

## Before a push

1. `uv run qm leaks` — the mechanical part: a home directory, a personal or
   IDE-made folder used as a path, a scratch path, a shared link, an archive
   path. It also runs as the `leak-check.yml` gate.
2. `uv run qm private-names --source host` — a private repository's name.
3. **Read the pages this cycle wrote** for what no pattern can see: an editor
   named, a process seen, a tool narrating itself, a person's words quoted
   into a constraint. A retrospective explains a reading or a decision; if a
   tool's mishap produced a corpus defect, the defect goes in and the mishap
   does not.
4. **The commit message describes the change**, and the pull request body
   the decisions, what ran, and what the branch holds. Neither names who
   asked, what was said, or which session did it.

`handbook/consolidation-runbook.md` Step 3 is where these run in the cycle.
