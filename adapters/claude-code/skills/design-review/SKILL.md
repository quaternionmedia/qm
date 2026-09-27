---
name: design-review
description: Drive the QM corpus's design-review runbook with this CLI's Workflow tool - measure, audit by area with evidence, a skeptic on every deletion, triage into file-disjoint workstreams, execute in worktree lanes, integrate, and deliver one pull request with a verdict.
argument-hint: "[repository path or owner/name] [--plan-only]"
disable-model-invocation: true
---

# /design-review

Target: **$ARGUMENTS** (none means the repository this session is in;
`--plan-only` stops after the triage and reports in the session).

This file is a convenience over a method it does not own. The method is
`handbook/design-review-runbook.md` in the QM corpus, and the queue in
`handbook/handoffs/README.md` says which repository is next and how its areas
fit. Where this file and the runbook disagree, the runbook wins; the target's
own `AGENTS.md` wins on the target's rules. What follows is only what is
particular to driving the method with this CLI.

## Read first

- **The runbook, in full.** In a qm checkout, `handbook/design-review-runbook.md`;
  in an adopting project, `governance/qm/handbook/design-review-runbook.md` if
  its pin carries it; otherwise from the host with
  `gh api repos/quaternionmedia/qm/contents/handbook/design-review-runbook.md -H "Accept: application/vnd.github.raw"`.
  If none answers, stop. Do not rebuild the method from this file.
- **The handoff that names this repository**, if one does.
- **The target's conventions**: its `AGENTS.md`, `CONTRIBUTING.md`, and
  `git log -20 --format=full` for the commit style.

## The launches, and the count each states

Invoking this skill is the owner's direct request for parallel agents, for
this target only. Each launch still states its count and waits for a yes
(`records/DRAFT-no-unattended-spending.md` §2), and the session gets the audit
block first: start, predicted end, kill time, purpose.

| Launch | Script in [orchestration.md](orchestration.md) | Count to state |
|---|---|---|
| Audit | `design-review-audit` | one per area, plus skeptics up to the confirmed `skepticCap` |
| Triage | one agent | one |
| Execute | `design-review-execute` | one per workstream |
| Final lane | `design-review-execute` again, stacked on the others' tips | docs, then CI |
| Each owner decision that changes code | `design-review-change` | a build, one per lens, and up to three fix and gate rounds |

Count the runtime's own restarts in: in the first run (apothecary #22,
2026-09-26), fifteen workstreams took thirty-three starts.

## What this CLI does to a long run

- **Concurrency** is capped at the CPU count less two: two agents at a time on a
  four-core machine. Plan the wall clock with that, not with the agent count.
- **An agent silent for about three minutes is killed** and restarted, the
  threshold growing with each retry. Every prompt carries the background-and-poll
  rule; the RULES block in [orchestration.md](orchestration.md) has it.
- **Worktree isolation has a guard** that refuses compound shell lines with
  runtime variables or redirects near git, as possibly reaching the main
  checkout. Refusals burn attempts until the stall detector fires. Plain,
  literal commands, one per call.
- **The permission guard refuses a bulk `git rm`** as irreversible. The worker
  skips the step and says so; the lead runs it and the commit says who did.
- **A dead agent returns null**, and `parallel()` never rejects. Treat null as
  failed, never as done; never `Promise.all` over agents, because one rejection
  there ends every lane.
- **Resume, don't restart.** Edit the script (a done list, a raised cap) and
  relaunch with the run id: completed agents replay from cache.
- **The lead's session can drop while workers run on.** On return, read the
  run's journal for what each agent actually returned before trusting a
  completion notice.
- **Scripts cannot read the clock.** Pass dates in `args`.

## Where it lives

The canonical copy is `adapters/claude-code/skills/design-review/` in qm; link
it into a project's or a user's skills directory the way `../../README.md`
links the command files. A copy elsewhere is compared with qm `main` before
use, and the newer one is named in the session.
