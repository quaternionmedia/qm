# Perspective — Landing the Slice: Three Things the Propagation Found

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (1M context), driving the session |
| **Task** | The day after the web window's first slice was built, its pull requests were merged, the corpus was propagated to `project/codecartographer`, and codecartographer picked the propagation up. Each of those is a runbook step that has been done before. Three of them still found something, and this is why. |

## 0. Standing and evidence

The merges are qm #118 and #119, codecartographer #101 and #102, qmcp #37,
looksatwords #24, in that order, each with a merge commit. Every figure below
was true at `project/codecartographer` `51a832a` and codecartographer `main`
`c5ed009`, and nowhere else. The commands are named beside what they showed.

## 1. A project's index passes the lint it has until the lint it will have arrives

**The assumption.** A project branch whose `adr-lint` gate is green has a
conforming record index.

**What was true.** It has an index conforming to the lint *at its own pin*.
`project/codecartographer` had been green on every pull request for a month
while listing its twelve drafts as bullets of the form *title* — `filename`.
The lint on `main` had since been tightened to read a draft as listed only when
a table row links its file or a whole bullet equals its title — because bare
substring containment had let a record titled "The" pass against any index that
contained the word. The propagation merged that lint onto the branch, and the
first CI run of qm #119 reported all twelve drafts unlisted.

**Why this is the right place for it to surface.** A propagation is the one
pull request whose base is the project branch and whose head carries `main`'s
tooling, so it is the first commit at which the two are measured together. The
fix belonged inside `adr/` on the propagate branch — the twelve as linked rows,
the form the org's own index uses — and the runbook already says that conflicts
inside `adr/` are settled there. The lesson is only that "conflict" includes a
gate's reading, not just git's.

**The check that catches it.** `adr-lint.yml` on the propagate pull request.
It exists, it fired, and it was seen red before the fix — which is what makes
its later green evidence.

## 2. `--remote` reads a ref that nothing fetched

**The assumption.** `git submodule update --remote governance/qm` moves the pin
to the branch named in `.gitmodules`.

**What was true.** It moves the pin to the *remote-tracking ref* for that
branch, and the submodule clone's fetch refspec was `+refs/heads/main` alone —
a single-branch clone. A plain fetch updated `origin/main` and left
`origin/project/codecartographer` where it had been since 2026-08-25, so the
command reported the old tip as the new one, twice, with no error. `git
ls-remote origin refs/heads/project/codecartographer` gave the true tip on the
first ask. Adding the branch to `remote.origin.fetch` and fetching again made
the command do what its comment in the runbook says.

**Why it was not caught earlier.** Every previous Part B on this workstation ran
in a clone whose refspec was `+refs/heads/*`. The narrow refspec is what a
submodule initialised with a `branch=` line gets; this was the first Part B run
against one.

**The check that catches it.** The runbook's second line — `git -C governance/qm
log --oneline -1 # confirm the tip you expect` — *if* the expected tip is taken
from the host and not from the same clone. Part B now says to ask `ls-remote`
first. A check whose oracle is the thing being checked is not a check; item 12
of `AGENTS.md`, in one more form.

## 3. The runner's first step undid the change it was asked to measure

**The assumption.** `run_workflows_locally.py` measures the working tree as it
stands.

**What was true.** The first step of every governance workflow here is `git
submodule update --init governance/qm`, and that command checks out the
gitlink recorded in the superproject's *index*. The pin had been moved in the
working tree and not yet staged, so the runner's own first step put the
submodule back to the old commit and then measured that: `adr-lint` clean,
`one-pr-check` unable to find `check_pr_voice.py` — a file that exists only at
the new pin. Nothing errored in a way that named the cause. `git add
governance/qm` and a second run measured the new pin, and every governance step
passed.

**Why this is the same fault as §2.** Both are the scaffolding describing
itself: a ref nothing had updated, a checkout of a commit nobody meant. The
runbook's order — `git add governance/qm && git commit`, *then* the checks —
avoids it; the session ran the checks first to see them before committing, and
learned why the order is written the way it is.

**The check that catches it.** Assert the intermediate: `git -C governance/qm
rev-parse HEAD` after the runner, compared with the tip that was meant. The
runbook now says so in one sentence.

## 4. What the pin check surfaced, and was left alone

The seed's `submodule-check.yml` replaced codecartographer's inline copy in
Part B, and its `check_submodule_pins.py` reported what the inline copy never
looked for: a branch inside the governance submodule's clone, `adr/one-graph-path`,
two commits of 2026-08-25 amending `DRAFT-rad-integration.md`, on no remote.
The pin was fine; the work was in one place. It is named in the handoff for the
window's remaining phases, because the record it amends is the one Phase 3
begins with, and it is not a propagation's to move.

## 5. What this changes

Nothing in the runbook's steps; two sentences in its Part B, so the next
session asks the host for the tip and stages the pin before it measures. And
one habit: a propagation pull request is read as the first place a project's
records meet `main`'s current gates, so its first CI run going red is the
expected shape of the event and not a surprise.
