# Handbook — The Asynchronous Multi-Agent Contract

**Routing.** Policy for how QM runs coding agents across repositories at the
same time. It binds QM's own conduct, not any project's design. Clauses here
that acquire a dispute get promoted to record form by
`handbook/public-by-default.md`'s promotion path; the two clauses already
mechanical name their check.

**Audience.** Every agent session opened in a QM repository, and the human
running them.

**Scope.** `project-seed/adr/README.md` is the contract for producing *one
record*, in *one session*. This page is the contract for running *many
sessions at once* — the constraints that only exist because a second session
is running somewhere else, on the same reviewer, the same workstation, and
sometimes the same repository.

---

## The shape of the problem

An agent finishes in minutes. A human reviews at human speed. Nothing in a
session makes the second fact visible to the first, so a session behaves
correctly by every rule it can see and still produces a queue nobody can
drain. Run six of them in parallel across six repositories — as QM did on
2026-08-09 — and the failures are not in any one session's work. They are in
what the sessions did to each other, and to the person they all report to.

Everything below is one of those. Each clause names the event that produced
it.

---

## 1. One open pull request per repository, per contributor

At any moment, a repository holds **at most one open pull request per human
contributor** for agent-produced work. Not one per task, not one per branch.
One per person, per repository.

Automation accounts are excluded — a contributor cannot close Dependabot's
pull request to make room for their own. Drafts count: a draft is still a
branch somebody must eventually read, and here drafts are the normal state,
so exempting them would exempt everything.

**Mechanical.** `project-seed/ci/check_one_pr.py`, wired as
`one-pr-check.yml`. It fails the pull request whose author already holds a
slot, and prints every slot in the repository so the reader can see which one
to fold into.

**The one exemption.** `--per-base <glob>` gives each base branch matching the
glob its own slot. It exists for a single shape: several long-lived branches
each pinned by a *different* downstream consumer, so a change to one is not a
change to another and combining them would invent a dependency between
unrelated projects. This corpus's `project/<name>` branches are that shape and
are the only known instance. The exemption is a glob someone passes and the
tool prints — an exemption nobody can see in the output has stopped being one.

**Folding has an order, and the order is the whole safeguard.** Close the
pull request **first**, then push its commits onto the branch that survives.
Pushing first *merges* it: the host sees the base now contains the head, marks
it merged with the pushed commit as the merge commit and whoever pushed as the
merger, and no review happened. The later `gh pr close` is a no-op against an
already-merged pull request, so it reports success while `--delete-branch`
silently does nothing. This has happened in this org.

## 2. Draft, assigned to the person who asked

Open every pull request with `gh pr create --draft`, and **never request a
review**. Add the person who asked for the work as **assignee**.

A ready pull request against a branch carrying `CODEOWNERS` requests review
from those owners the moment it opens — you name nobody, and the notification
cannot be recalled. "Open a pull request for human review", read literally by
an agent, is therefore the act of pulling a second person into work nobody has
tested. Leaving draft is the assignee's decision, made after their own
testing, and is not a formality standing in for your confidence in the diff.

This needed three corrections across two repositories before it was written
down this plainly. The third one was *"Your role is to tag me, not others."*

## 3. A pull request states decisions, not questions

Settle every input you are unsure of **before** you open it: ask in the
session, and wait for the answer. A pull request carrying the session's own
open questions hands the drafting back to the reviewer and calls it review.

This is distinct from a record's `Pends on` row, which names something *the
organisation* has not settled. A Proposed record naming one is this process
working. Your own unresolved question arriving as pull request text is not.

## 4. Concurrent sessions share one workstation

Two sessions in two repositories are two processes on one machine, and
nothing tells either that the other exists.

- **Never bind a default port.** On 2026-08-09 an Alfred session spent an
  afternoon measuring test results against `localhost:8000`, which was being
  served by Apothecary's API from another session. Every number it reported
  was about the wrong program. Two failing tests were investigated as defects
  in code that was never running.
- **Assert the identity of what you are talking to**, not its reachability. A
  200 from a port proves something is listening. Ask the server what it is —
  `/openapi.json`, a version endpoint, a banner — and record the answer next
  to the measurement.
- **A port you did not start is not yours to stop.** Move yourself.
- **Rule out the harness before reporting a defect.** A false defect report
  spends someone else's day, and in a parallel run it spends a session that
  was doing something else.

## 5. Two sessions in one repository declare themselves

Sessions on the same repository happened on 2026-08-09 in Apothecary
(*"there is one other active session"*) and in RAD (*"Another agent has
started the work parallel"*). Neither could see the other.

A session that finds evidence of another — an unexpected branch, a commit it
did not write, a dirty tree it did not dirty — **stops and reconciles before
writing.** Reconciling means naming what each branch carries and which commit
you are working against, not merging on the assumption that newer is better.

The reconciliation is written down where the next session finds it, which is
`handbook/handoffs/` at org level and the project's own handoff page inside a
project.

## 6. Every session opens with a context build and closes with a handoff

**Open** with `/cowork`. It re-derives the facts a session would otherwise
assume: which commit, which branch, which pull request slot is free, what the
governance pin points at, which gates exist, what the open handoffs are. The
alternative is a session that inherits its predecessor's beliefs, and *drafts
have no memory* — the numbers in any page were true when written.

**Close** with `/handoff`. A session that ends without one has produced work
only its own transcript explains, and the transcript is not in the repository.

## 7. Local-only is a standing state, and it overrides delivery

When the human says *keep everything local*, that holds until they lift it —
across compaction, across context loss, across a session that has forgotten
why. Nothing is pushed and no pull request is opened while it stands. Say so
in the handoff, so the next session does not read unpushed commits as an
oversight and "fix" them.

## 8. Report what you ran, and what you could not run

Run the gates: `project-seed/ci/run_workflows_locally.py` executes the
workflows' real steps. It does not reproduce `uses:` steps, the runner image,
or secrets — say so rather than letting a local pass stand for a remote one. A
local *failure* is a question rather than a verdict; establish which it is
before reporting it.

Two traps that produced false green in this org, both cheap to avoid:

- **A pipe replaces the exit code.** `tool | tail` reports `tail`'s status. A
  failing check read as passing, twice.
- **A passing test is not evidence until it has been seen to fail.** After
  writing a check's test, break the tool in the way the test names and confirm
  the test fails. Ten such mutations against one generator found two inert
  tests; the same exercise against `check_one_pr.py` found two more.

## 9. Another agent's report is evidence, not a finding

A subagent's summary, a previous session's handoff, and a status page are all
claims made by something that could be wrong in exactly the way you cannot
see. Treat them as inputs to verify, not conclusions to act on — and when you
carry one forward, carry the commit it was true at.

## 10. Human-only contributorship, in every commit

Do not add yourself, your model name, or any co-author trailer naming an
unmonitored address to any commit. Suppress your tooling's default trailer.
Tool involvement is disclosed as a `Tools:` note where the artifact calls for
one, never as a byline. See
`records/DRAFT-human-only-contributorship.md`.

---

## What the harness is, and where it lives

The clauses above are prose, and prose is not a harness. The harness is the
part a session executes:

| Piece | Path | Reaches a project by |
|---|---|---|
| The commands a session runs | `project-seed/ide/.claude/commands/` | copied at fork, refreshed at propagation |
| The context builder behind `/cowork` | `project-seed/ci/cowork_context.py` | run from the submodule |
| The slot check | `project-seed/ci/check_one_pr.py` + `one-pr-check.yml` | workflow copied, script run from the submodule |
| The branch check | `project-seed/ci/check_pr_base.py` | run from the submodule |
| The gate runner | `project-seed/ci/run_workflows_locally.py` | run from the submodule |
| This page | `handbook/async-contract.md` | read through the submodule mount |

**The sync is two-way, and each direction has a different gate.**

*Down* — org to project. `project-seed/` is the canonical copy, and this
corpus's own root points into it **for some IDE files but not the one that
matters most**:

| Root path | Mode | Resolves to |
|---|---|---|
| `.vscode/settings.json`, `.vscode/extensions.json` | `120000` | `project-seed/ide/.vscode/…` |
| `.claude/commands/*.md` | `120000` | `project-seed/ide/.claude/commands/…` |
| `CLAUDE.md`, `.github/copilot-instructions.md` | `120000` | the **root** `AGENTS.md` — not the seed |
| `AGENTS.md` | `100644` | **a second, genuinely different document** |

So editing the seed edits this repository's own harness in the same commit for
`.vscode/` and `.claude/`, and **not** for `AGENTS.md`: the root one is
org-facing, the seed's is project-facing, and a rule that belongs in both has to
be written twice. That is a real cost and the reason to know it is that
forgetting the second edit leaves the two saying different things — which has
happened. `symlink-integrity.yml` checks that the files which *are* symlinks
stay mode `120000`; it cannot notice a rule missing from one AGENTS.md.

A project picks seed changes up when its governance pin is bumped and the seed
files are re-copied — `handbook/propagation-runbook.md`, Part B. A merge does not
fix a copy.

*Up* — project to org. A session that finds the harness wrong where it is
running fixes it **in `project-seed/`**, on a branch of this repository, and
its own copy comes back down through propagation. A fix applied only to the
local copy is a fork of the constitution that nothing reports. This is the
direction that decays silently, which is why it is named here rather than
assumed.
