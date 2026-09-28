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

QM ran six sessions in parallel across six repositories on 2026-08-09. The
failures were not in any one session's work — each behaved correctly by every
rule it could see. They were in what the sessions did to each other: a port
already bound by another project's server, a branch neither session knew the
other had cut, a working tree two of them wrote to.

Nothing in a session makes another session visible to it. That is the whole
source of the clauses below, and each one names the event that produced it.

---

## 1. Small pull requests, stacked when one depends on another

**One pull request carries one change** — one feature, one fix, one record —
scoped so its diff can be read in one sitting. Two changes that could each land
alone are two pull requests.

**Independent changes go in parallel.** Each is its own branch, cut from the
base it targets, with its own pull request against that base. Each is marked
ready and merged by its author once its gates pass. There is no limit on how
many a contributor holds open at once.

**Dependent changes go in series, as a stack.** A branch that needs another
branch's work is cut *from that branch*, and its pull request's base *is* that
branch, so its diff shows only its own change. Only the bottom of a stack — the
pull request whose base is the real target — is ready. Every pull request above
it is a **draft, even when its work is finished**: ready means merge once green,
and merging it now would land it in its parent's branch rather than the target.

**When the bottom merges, the next one moves down, in this order.**

1. Merge the bottom with a merge commit. A squash or rebase rewrites the
   commits the next branch was cut from.
2. Retarget the next pull request onto the real target **before** the merged
   branch is deleted. Deleting a branch through git or the API closes every
   pull request based on it, and one whose base is gone cannot be reopened
   until the branch is restored. Only the host's own delete-on-merge setting
   retargets, and a repository need not have it on. `qm merge` does this step
   and the next.
3. Delete the merged branch.
4. Update the next branch from the target. Workflows filtered on the target
   branch never ran while it was stacked, and a retarget does not start them;
   the update is a push, and a push runs everything.
5. Mark it ready once its gates pass.

On 2026-09-28 this corpus's #128 merged with `gh pr merge --delete-branch`,
and #129, stacked on it, was closed rather than retargeted. Restoring the
branch, reopening #129 and retargeting it by hand recovered it; its
`registries` and `leaks` checks, which run only against `main`, then ran for
the first time on the update. The order lives in the base chain, where every
reader and every tool can see it, instead of in the head of the session that
cut the branches.

**Never close a pull request in favour of one that contains it.** On
2026-09-20, ShowRunner's #22 (ShowMidi, two commits) was closed unmerged
because every commit in it was contained in `integrate/2026-09-20`, which
opened as #30: twenty-two commits folding three pull requests and their
reconciliation into one. The rule then in force — one open pull request per
contributor — made that the correct move, and the result was one diff too large
to read in place of three that each could be. Under this rule #22 stays open
and ready against `main`, and the branch that builds on it opens as a draft
whose base is #22's branch.

Automation accounts are outside the rule: Dependabot's pull requests have their
own queue.

**Mechanical.** `project-seed/ci/check_one_pr.py`, wired as
`one-pr-check.yml`. It fails a pull request that is marked ready while its base
is the branch of another open pull request, and prints every open pull request
and the stack it sits in.

**Closing a pull request has an order, and the order is the whole safeguard.**
Where one must be closed and its commits carried elsewhere, close the pull
request **first**, then push its commits onto the branch that survives.
Pushing first *merges* it: the host sees the base now contains the head, marks
it merged with the pushed commit as the merge commit and whoever pushed as the
merger, and no review happened. The later `gh pr close` is a no-op against an
already-merged pull request, so it reports success while `--delete-branch`
silently does nothing. This has happened in this org.

## 2. Assigned to the person who asked, reviewed by nobody

**Never request a review.** Add the person who asked for the work as
**assignee**, and merge the pull request yourself once every gate is green.

A pull request is an audit record: it runs the gates and leaves the diff
readable. It is not a review request, because `main` asserts nothing —
`records/DRAFT-version-tags-are-claims.md` §4 — and a change that asserts
nothing has nothing for a reviewer to approve. The two human gates are
ratification and the version tag, and the tag is where a reviewer is named, by
the human cutting it.

Requesting a review pulls a second person in anyway, and against a branch
carrying a live `CODEOWNERS` it fires automatically the moment a pull request
opens: you name nobody and the notification cannot be recalled. This needed
three corrections across two repositories before it was written down plainly.
The third one was *"Your role is to tag me, not others."*

**Draft means unfinished, or stacked.** A draft is either work that is not
done, or a pull request waiting on the one beneath it in a stack (§1). It is
not a holding pen for anything else: a green pull request left in draft against
the real target is a change that never reached `main` — which is the opposite
of the job.

## 3. A pull request states decisions, not questions

Settle every input you are unsure of **before** you open it: ask in the
session, and wait for the answer. A pull request carrying the session's own
open questions hands the drafting back to the reviewer and calls it review.

This is distinct from a record's `Pends on` row, which names something *the
organisation* has not settled. A Proposed record naming one is this process
working. Your own unresolved question arriving as pull request text is not.

**And the body speaks as the contributor, to the world.** It is posted under a
human's account and it is their statement of the change, so it addresses
nobody: not who is to merge it, not what deserves their attention, not that no
review is wanted. Those are a session's words to the person who asked, and
posted under that person's name they read as the person talking to themself.
Say them in the session; write the third person where a person must be named.
`records/DRAFT-human-only-contributorship.md` clause 5 is the decision.

**Mechanical.** `project-seed/ci/check_pr_voice.py`, a step in
`one-pr-check.yml`: it refuses the second person and the handling phrases that
have leaked, leaves code and quotations alone, and cannot see the third person.

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
assume: which commit, which branch, which pull requests are open and how they
stack, what the
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
| The scripts a session runs | `project-seed/ci/` | run from the submodule, never copied |
| The context builder behind `/cowork` | `project-seed/ci/cowork_context.py` | run from the submodule |
| The stack check | `project-seed/ci/check_one_pr.py` + `one-pr-check.yml` | workflow copied, script run from the submodule |
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
| `.claude/commands/*.md` | `120000` | `adapters/claude-code/commands/…` — optional, outside the seed |
| `.claude/skills/design-review` | `120000` | `adapters/claude-code/skills/design-review/` — a directory; optional, outside the seed |
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
