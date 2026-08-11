---
description: Open a governed session — build the whole context from the repository before writing anything.
argument-hint: [what you have been asked to do]
---

<!-- SEED FILE: part of project-seed/ide/, copied recursively onto the project
     root. The corpus's own .claude/commands/ holds symlinks back to this file,
     so there is one copy to edit. Delete this comment in the copy. -->

Open a co-working session in this repository. The point is that you start from
what the repository says, not from what a page, a handoff, or a previous
session believed. **Do not write, commit, push, or open anything during this
command.** It ends with a brief and a question, not with work.

The task, if one was given: **$ARGUMENTS**

## 1. Build the brief

Run the context builder and read all of its output:

```
python project-seed/ci/cowork_context.py --out .harness/session-brief.md
```

In a project that vendors the corpus, that path is
`governance/qm/project-seed/ci/cowork_context.py`. If the submodule is not
initialised the brief will say so — initialise it before continuing, because
every governance file is otherwise absent rather than unreadable, and a check
that looks for one will report the project as ungoverned.

Add `--offline` only if `gh` is unavailable. Then say in your first message
that the pull request slot is **unread**, not that it is free.

## 2. Read what governs you

In this order, in full:

1. `AGENTS.md` at this repository's root (or `governance/qm/AGENTS.md`).
2. `handbook/async-contract.md` in the corpus — the rules that exist only
   because other sessions are running right now.
3. `handbook/handoffs/README.md`, then **exactly one** handoff if you are
   picking one up.

## 3. Re-derive anything you are about to rely on

Every number in every page was true when written. The brief carries the commit
each of its own facts came from; a handbook table does not. Before quoting a
count, a status or a branch state from a document, check it.

## 4. Report back, and ask before writing

Open your first message with these, in this order:

- **The commit you are working against**, and the branch.
- **Your pull request slot**: free, already holding one you will add to, or
  over the limit. If over, say which pull requests and stop — folding is the
  human's call, and closing one is a decision with an order to it.
- **Whether *keep everything local* is in force.** If you cannot tell from the
  session, ask. It survives compaction and it overrides delivery.
- **Anything else in flight** — a dirty tree you did not dirty, a sibling
  branch, an unpushed commit. Reconcile before writing, not after.
- **Every question whose answer changes what you build.** Ask them now. A pull
  request states decisions; a question that arrives in one hands the drafting
  back to your reviewer.

Then stop and wait. The next instruction begins the work.

## What this command does not do

It does not fetch, merge, initialise, install, or start a server. If you need a
dev server later, bind a non-default port and ask the server what it is before
believing anything you measure against it — two sessions on one workstation is
the normal case here, and an afternoon has already been spent measuring the
wrong program.
