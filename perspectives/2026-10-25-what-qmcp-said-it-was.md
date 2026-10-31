# What qmcp said it was — 2026-10-25

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-25 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

On 2026-10-25 a session opened in qmcp to review its onboarding and plan a
local development loop. It closed the drift it found, in qmcp and in this
corpus, reviewed the roles qmcp plays, drafted qmcp's control-plane record,
and reorganised qmcp's documentation by role. Everything stayed local by the
person's decision until the person lifted it the same evening. It then landed
as `qm` #258 to #261 and `qmcp` #116 and #117, and what it left open is in
`handbook/handoffs/qm-queue.md`. This page is why it went the way it did.

## Drift read in a project is often the corpus's past

The opening brief found six things wrong. Two of them, the status documents'
paths in `AGENTS.md` and the one-pull-request rule in the handoff index, were
already fixed on the corpus's `main`. qmcp's copy was right for its pin. The
pin was two commits behind `project/qmcp`, and `project/qmcp` was 325 commits
behind `main`.

The false assumption was that a stale sentence in a project is a defect in the
text, when it is usually a defect in propagation. The fix was the runbook's,
in order: a propagation branch for `project/qmcp`, a seed refresh stacked on
it, and a pin bump in qmcp that copies every seed file again from the new pin.

The check that would have caught it is a gate on how far a project's pin lags
`main`. `status/governance.yaml` carries `behind_corpus`, but it was 846 hours
old at the session's open, past its budget, and nothing gates on it. That gate
does not exist, and it is the next piece of work this page names.

## A docstring that was true in one repository

`cowork_context.py` said the default `--out` location was ignored by git. That
was true in the corpus, whose `.gitignore` lists `.harness/`, and false in every
project, where the brief became an untracked file. That file names the
machine's paths, and it is the dirty tree the next brief reports.

The tool now refuses an `--out` path inside the repository that git does not
ignore, and refuses to overwrite a tracked file. Tests cover both refusals, and
both were seen to fail with the guard removed. The claim had stayed true for
its author because the author only ever ran the tool where it held.

## A workstation fact is not drift

One of the six was that port 8000, joe's default, was held by Docker. That is a
fact about one machine on one day, and a committed page that said so would
state something about a workstation, not about the project. It was withdrawn
before anything was written. The handoff that declares the port allocation is
right to declare it, and right to say 8000 is the one to move first.

## The code outgrew its own description

qmcp's server module, its overview page and its README said the server does no
orchestration, runs no autonomous loop and speaks the Model Context Protocol.
At `82b2d58` the server starts the standing conversation and each consented
act in processes of its own, and only `qmcp_mcp.py` speaks the protocol on the
wire. Each sentence was true when written. Each later feature was added beside
it and none touched it.

`tests/test_declared_commands.py` keeps a page from naming a command that does
not exist, and it was seen to fail on a new setup page during this session. No
check can tell a page's description of the system from the system. The
control-plane record's size smells and its "a thirteenth role" trigger are the
nearest thing: they make growth a revision of a record rather than a sentence
that silently stops being true.

## The scaffolding moved under a measurement

While measuring the seam's size, a `git checkout main --` meant to read
`main`'s files switched the documentation worktree to `main`. That worked
because `main` was free: the primary checkout was on the governance branch.
That worktree's local-model baseline and its preflight were running in the
background, and they would have reported on `main` under the documentation
branch's name. The session's own change notices caught it. The run was stopped,
the worktree put back, and the run started again with the branch and commit
written at the top and bottom of each log.

The false assumption was that a measuring command reads and does not write.
`AGENTS.md` item 11 names the class. The check is the stamp in the log, and it
exists now only in this session's habit, not in the runner.

## A delegated inventory, verified before it was cited

A subagent inventoried qmcp's roles with line references. Two of its facts
were wrong in ways a citation would have carried forward. The vocabulary file's
path was wrong. Its size figure subtracted the whole cookbook package, which
holds the harness's `delta.py`. Every fact the control-plane record cites was
re-read at `82b2d58` first. The async contract's §9 is the rule, and nothing
mechanical enforces it.

## The base moved while the branches were being cut

The session fetched the corpus at its open and cut every corpus branch from
what it saw. While it worked, another session merged a restatement of qmcp's
adoption record into `project/qmcp`, and a handoff into `main` whose queue
page decided how that record is restated: C2, C3 and C7 first, C1, C5, C6 and
C8 next, each row kept and marked closed or open. This session had already
rewritten the same record its own way. It dropped the closed rows, and it
declared C1 settled by `REUSE.toml`, where the decision in force says C1 is
done only when a licence is declared at the root and in `pyproject.toml`.

The new base surfaced when the handoff's stamp was re-derived. The session
stopped, withdrew its restatement, cut the propagation and the record again
from the new tips, and rebuilt qmcp's pin against them. The false assumption
was that a base read at the open is still the base at the close. Nothing
re-reads the host between the two. `uv run qm queue` at close reads it, and
that is where this was seen; fetching before each branch is cut would have
seen it hours earlier, and no check asks for that.

## A red check that was the host not knowing

Run locally on unpushed commits, `signature-check.yml` reported a signed
commit as unverifiable, because the workflow asks the host and the host had
never seen the commit. `check_signatures.py --source git` reported it good. The
runner prints the failure without saying that the source was the host. A note
in the runner, when a host-sourced check meets a commit that is not on the
host, would turn that red into the answer. That note does not exist.
