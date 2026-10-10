# Handbook — Auditing the Remaining Adoptions

**Routing.** Operational status and working instructions, not a decision
record. It weighs no alternatives. Delete the queue section when it empties;
keep the method section, which is the part that generalises.

**You are probably an agent with no memory of the audits already run.** That
is the normal case. Everything you need is here, in
`handbook/propagation-runbook.md`, and in the repository itself. Do not trust
a summary of repository state — including this page's — over `git`.

---

## The queue

Every `project/*` branch names a repository that can be read, except
`streaming-infrastructure`, which names none. The table says which have been
audited.

**This table is the queue, not the state.** It says which projects an audit has
been through and what class of defect each turned up — facts that stay true.
Current state is `status/governance.yaml` and `status/harness.yaml` at the root,
and `ci/harness_dashboard.py status/harness.yaml --format md` prints it.

Cells such as "commits unpushed locally" or "has no remote" describe one
workstation at one moment, go stale within days, and do not belong on a
committed page — the same rule that keeps the machine-scoped documents out of
git.

| Project | qm branch | Own repo | Audited | What an audit found, or would look for |
|---|---|---|---|---|
| qmetronome | ✅ | ✅ | **yes** | Carried an inline ADR lint predating the seed; the seed's `submodule-check.yml` was generalized from its own fix |
| apothecary | ✅ | ✅ | **yes, re-done** | The first audit read the working tree and reported a machine. The re-do is the origin of the rule: audit `origin`, never the checkout |
| datum | ✅ | ✅ | **yes** | Pin named a commit on no remote, and the submodule fetched from a filesystem path — the enabling mechanism for an unreachable pin |
| alfred | ✅ | ✅ | no | Its `.gitmodules` on `main` names only `alfred/otto`; the corpus submodule is not there. Adoption work is on an unpushed local branch |
| codecartographer | ✅ | ✅ | no | Mounts the corpus at `docs/qm` rather than the seed's `governance/qm`, so any check keyed on the seed path must look it up by path |
| `private-32` | ✅ | ✅ | no | Private; resolve the reference with `uv run qm inventory --resolve private-32` |
| dossier | ✅ | ✅ | no | Adopted late and completely; useful as the control case |
| `private-33` | ✅ | ? | no | Private; resolve the reference with `uv run qm inventory --resolve private-33` |
| factorio-sysops | ✅ | ? | no | — |
| loopwall | ✅ | ? | no | Branch took `main` by a direct merge with no pull request |
| qmcp | ✅ | ✅ | no | Adopted 2026-08-11 with nine conflicts recorded rather than fixed; three are shared-workstation hazards |
| streaming-infrastructure | ✅ | n/a | n/a | **Not an adopting project.** No `quaternionmedia/streaming-infrastructure` repository exists (`gh api` → 404). A design branch holding the plan and `ADR-0001` that `main` moved off itself; `LICENSE` and two records will not arrive by merging — see the session handoff |

Re-derive every column before acting on it.

## What one audit is

Walk `handbook/propagation-runbook.md` end to end. Both parts: the
`project/<name>` branch in this repo, **and** the project's own repository.
The second is where serious findings come from, because the first is the part
people remember to check.

Then, per project, expect roughly:

- one PR into `project/<name>` for the seed copies a merge cannot fix;
- one propagation PR, if the branch is behind;
- one PR into the project's own repo for whatever adoption skipped.

Keep them separate. They have different reviewers and different risk.

## The rule that decides where a fix goes

**If two projects could have the same defect, the fix belongs in
`project-seed/`, not in the project.**

A defect one project hits and fixes locally is carried silently by the others
until each hits it in turn; a fix in the seed reaches all of them.

So when you fix something in a project repo, ask what would have prevented it
everywhere, put *that* in the seed, and let the project's own PR be a verbatim
copy. A fix that lands only where it was found is a fix that will be needed
again.

## How the process evolves

An audit changes the process, in ways that reading the procedure does not
predict. The loop:

1. **Run the procedure exactly as written**, including the steps that look
   unnecessary. The point is to find out where it is wrong.
2. **When a step misleads you, that is the finding** — bigger than whatever
   you were looking for. A diagnostic that reports a false all-clear is worse
   than no diagnostic, because it ends the investigation.
3. **Fix the page before the run ends.** Not "note it for later": the next
   agent has no memory and will be misled identically.
4. **Record what the run found**, in `handbook/governance-rollout.md`, in one
   or two lines. A finding nobody can see did not happen.
5. **Say which step found it.** That is what tells the next person which
   steps are earning their place.

Worked examples of the shape:

- A "has propagation ever run?" check that matches any merge commit gives a
  false all-clear when a project merges its own feature branch — on the one
  question the step exists to answer.
- A conflicted propagation has no working pull-request shape with
  `head=main`: GitHub commits the resolution to `main`.
- A conflict resolved by keeping both sides passes, then conflicts again on
  the next propagation — the same insertion arriving from two directions is
  not something git can reconcile.

## Verification

Each of these produces a confident wrong answer:

- **`git -C /c/...` under Git Bash on Windows** silently returns nothing.
  Use `C:/...` for `-C`.
- **`git submodule status | head -1`** reads whichever submodule sorts first,
  and a repository can have several. Name the path:
  `git submodule status governance/qm`.
- **Piping a check through `head`/`tail` reads the pipe's exit code**, not the
  check's.
- **Checking for a filename** reports "absent" when a project implemented the
  same behaviour its own way. Search for the behaviour.
- **A negative test that never ran** passes. If you assert a check fails on
  bad input, watch it fail before you believe it.

- **A working tree is not a repository.** `git ls-files`, `ls`, and every
  filesystem check answer for whatever branch happens to be checked out, which
  during an audit is frequently a branch you created. Read the remote default
  branch — `git cat-file -e origin/main:<path>` — or you will report your own
  unpushed work as the project's state.
- **A branch is not its base.** A PR carries everything between its base and
  its head, which is not the same as what you committed. Before opening one:
  `git merge-base <base> <head>`, then the commit count, file count and author
  of each commit. A branch cut from the wrong parent is internally consistent
  and passes every check.

- **Hand-running a workflow's commands** is not running the workflow: a
  workflow can call a console script that is not on PATH, which no hand-run
  equivalent notices. Use `project-seed/ci/run_workflows_locally.py`, and say
  which steps it cannot reproduce.

State which commit you are working against at the start, and re-derive branch
counts rather than reading them from any document, this one included.

## What you may not do

Ratify anything. Merge to `main` or to a `project/*` branch. Delete a branch.
Force-push. Rewrite a branch a submodule pins — and if you find one that was
rewritten, the runbook has the recovery path.

Open pull requests, and settle your open questions with a human **before**
opening them rather than inside them.
