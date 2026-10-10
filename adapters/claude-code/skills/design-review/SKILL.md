---
name: design-review
description: Drive the QM corpus's design-review runbook with this CLI's Workflow tool - measure, audit by area with evidence, a skeptic on every deletion, triage into file-disjoint workstreams, execute in worktree lanes, integrate, and deliver one pull request with a verdict.
argument-hint: "[--plan-only]"
disable-model-invocation: true
---

# /design-review

Target: the repository this session is in. Nothing launches before its count is
confirmed, so invoking this spends nothing until the first yes: Phase 0 runs as
scripts, and the audit's count is stated. `--plan-only` stops after the triage
and reports in the session; the audit, verify and triage launches still run.

This file is a convenience over a method it does not own. The method is
`handbook/design-review-runbook.md` in the QM corpus, and the queue in
`handbook/handoffs/README.md` says which repository is next and how its areas
fit. Where this file and the runbook disagree, the runbook wins; the target's
own `AGENTS.md` wins on the target's rules. What follows is only what is
particular to driving the method with this CLI.

## Read first

- **Run from a checkout of the target itself.** Workers get worktrees of the
  session's repository; to review another, clone it and start the session there.
- **The runbook, in full.** In a qm checkout, `handbook/design-review-runbook.md`;
  in an adopting project, `governance/qm/handbook/design-review-runbook.md` if
  its pin carries it; otherwise from the host with
  `gh api repos/quaternionmedia/qm/contents/handbook/design-review-runbook.md -H "Accept: application/vnd.github.raw"`.
  If none answers, stop. Do not rebuild the method from this file.
- **The handoff that names this repository**, if one does.
- **The target's conventions**: its `AGENTS.md`, `CONTRIBUTING.md`, and
  `git log -20 --format=full` for the commit style, which the RULES block in
  [orchestration.md](orchestration.md) carries to every worker.

## The launches, and the count each states

Invoking this skill is the owner's direct request for parallel agents, for
this target only. Each launch still states its count and waits for a yes
(`records/DRAFT-no-unattended-spending.md` §2), and the session gets the audit
block first: start, predicted end, kill time, purpose.

| Launch | Script in [orchestration.md](orchestration.md) | Count to state |
|---|---|---|
| Audit | `design-review-audit` | one per area |
| Verify | `design-review-verify` | one per open deletion not yet judged; the script launches nothing unless its list is the confirmed length |
| Triage | `design-review-triage` | one |
| Execute | `design-review-execute` | one per workstream |
| Final lane | `design-review-execute` again, stacked on the others' tips | one per workstream in the lane: docs, then CI |
| Each owner decision that changes code | `design-review-change` | a build, one per lens, and up to three rounds of a fix and a gate |

The runtime restarts an agent that stays silent and states no limit on how
often, so no count can include restarts: say so beside the count, and let the
kill time bound them. At the kill time the lead stops the run (`TaskStop` with
its task id) and confirms in `/workflows` that no agent is still running; a
script cannot read the clock to stop itself.

## What this CLI does to a long run

- **Concurrency** is capped at `min(16, CPU count - 2)` agents per workflow
  (the workflow reference in CLI 2.1.283). Plan the wall clock from the cap,
  not the agent count.
- **An agent that stays silent is killed and restarted.** The reference gives
  no threshold. Every prompt carries the background-and-poll rule; the RULES
  block in [orchestration.md](orchestration.md) has it.
- **Depending on the permission mode, an isolated worktree can refuse a
  compound shell line** with runtime variables or redirects near git, as
  possibly reaching the main checkout. Refusals burn attempts until the agent
  is restarted. Plain, literal commands, one per call.
- **Depending on the permission mode, an irreversible git step such as a bulk
  `git rm` can be refused.** The worker skips the step and says so; the lead
  runs it.
- **A dead agent returns null**, and `parallel()` never rejects. Treat null as
  failed, never as done; never `Promise.all` over agents, because one rejection
  there ends every lane.
- **A resume replays.** Relaunching with the run id works only in the session
  that started the run, after stopping it, and returns every call whose prompt
  and options are unchanged from the cache, a failure as readily as a success.
  Use it to finish a run that was stopped. Retry a failure with a fresh launch:
  the verify launch with `judged` passed back, or lanes that carry only the
  unfinished workstreams. After the lead's session drops the run id cannot be
  resumed; relaunch the same way.
- **The lead's session can drop while workers run on.** On return, read the
  run's journal for what each agent actually returned before trusting a
  completion notice.
- **Scripts cannot read the clock.** Pass dates in `args`.

## Where it lives

The canonical copy is `adapters/claude-code/skills/design-review/` in qm; link
it into a project's or a user's skills directory as `../../README.md` shows. A
copy elsewhere is compared with qm `main` before use, and the newer one is
named in the session.
