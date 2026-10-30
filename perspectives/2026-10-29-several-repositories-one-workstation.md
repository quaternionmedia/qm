# Several repositories, one workstation — 2026-10-29

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-29 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review; a second session, working in codecartographer, ran its part on request; a third, working in alfred, coordinated the shared stack |

The person asked for a definition of how several of the estate's
repositories run and are watched on one workstation at once, demonstrated and
proven on this workstation with the other sessions on it.

The definition already existed in part.
`records/DRAFT-monitoring-seam-and-instance-identity.md` decides that a server
declares itself with a run-file outside every repository, and that a collector
finds it by that declaration and matches it against the server's own answer.
qmcp did its half: it writes a run-file and states its pid, port, start time and
a database fingerprint on `/health`. Nothing did the collector's half, and no
other repository declared anything. `qm dashboard` started a person's surfaces
on fixed ports and reported a port as "something is listening"; `qm
family-demo` reserved a range of ports for the performing family and kept its
own manifest.

So the session built the collector (`qm instances`), a wrapper that declares a
server that does not declare itself (`qm instances run`), run-files for what
`qm dashboard --start` launches, and the procedure
(`handbook/running-several-repositories.md`). Then it ran them.

## The run

The machine had restarted at 17:56 local time, so nothing was serving, and a
reading started from an empty workstation with one leftover.

| Step | Who | What was running | What `qm instances` said |
|---|---|---|---|
| 1 | this session | nothing | qmcp's run-file from before the restart: `stale` |
| 2 | this session | four surfaces by `qm dashboard --start`, and a second qmcp on a port the system chose, with its own queue and session name | two qmcp `identified`, told apart by pid and port; codecartographer and looksatwords `answering`; apothecary `stale`; the leftover `stale`, *another process answers its port* |
| 3 | the codecartographer session | its first try | refused by the `qm` CLI before anything started |
| 4 | both | the codecartographer session's server beside this session's, from the same checkout | two codecartographer rows, by session and port |
| 5 | this session | three faults, made on purpose | `mismatch`, `stale` and `undeclared`, each named |
| 6 | this session | `prune`, then `prune --yes` | the four run-files whose process was gone, and no others |
| 7 | the codecartographer session | its server stopped | its run-file `stale` |
| 8 | this session | everything stopped, then pruned | *No run-file declares a server here.* |

Step 2, as read:

```
repo               session            pid   port  state       why
apothecary         dashboard        19364   6283  stale       pid 19364 is gone; the run-file outlived it.
codecartographer   dashboard        31468   2718  answering   the port answers; /health answered 404
looksatwords       dashboard        13084   1414  answering   the port answers; the server does not say which one it is
qmcp               agent-b          24460  53474  identified  its health answer names this pid and port
qmcp               -                33644   3141  identified  its health answer names this pid and port
qmcp               -                51320   3141  stale       pid 51320 is gone; the run-file outlived it. Another process answers its port.
```

Step 5, as read:

```
repo              session                pid   port  state       why
fault             mismatch-on-purpose   3600   3141  mismatch    port 3141 answers as pid 33644, not 3600
looksatwords      dashboard            13084   1414  stale       pid 13084 is gone; the run-file outlived it.
...
HELD WITHOUT A RUN-FILE  (reserved ports something listens on)
 18400  the family demo's range
```

The three faults were a run-file planted to declare a live process on another
server's port, a surface killed outright rather than stopped, and a plain HTTP
server on a port in the family demo's range that nothing declared.

The alfred session announced one shared alfred and joe for both its demo and
this one, by the person's choice, and asked that no second be started. This
session started none, and looked at both ports with `--port` at every reading
after the announcement. The stack was not up while the readings were taken, so
how the collector reads a running container stack is not shown here; by
construction it is `undeclared`.

## A run-file outlives its server, and a port check cannot tell

**Assumption:** a run-file in the directory means a server is up.

The leftover from before the restart named pid 51320 on 3141. Once the
dashboard's qmcp was up, the same port answered `/health` with 200, and a
check by port would have attributed the leftover's identity, and its queue, to
the new server. This is the case the record is written against, and it took a
restart to produce rather than a test.

**The check exists:** the collector asks the operating system for the pid
before it dials the port, and a mutation that reverses the order turns the
test red.

## The dashboard said "started" of a server that never ran

**Assumption:** a surface's command runs the same way on every clone.

apothecary's clone was checked out on a branch whose `serve` has no `--demo`,
which the dashboard's command passes. The process exited at once; the
dashboard had already printed its pid, and its own report later read the port
as "nothing listening" without saying why. The collector read the run-file as
`stale`, which is the first place the failure was visible.

**No check exists** in the dashboard itself. `qm-queue.md` §4 carries it:
`--start` waits for the port, or says it did not answer.

## The CLI refused to run anywhere but the corpus

**Assumption:** a command any session calls works from that session's
checkout.

This session wrote the brief to the codecartographer session without running
the command from another repository first. The `qm` CLI refused, because
every other command it routes reads corpus-relative paths. Behind the refusal
was a second defect: inside the corpus, the CLI moves into its root before
dispatching, so `instances run` would have started codecarto in the qm
checkout. The other session stopped at the error and sent it back as it
printed, which is what found both.

**The check exists:** `ci/cli.py`'s `ANYWHERE` names the commands that touch
only machine-scoped paths, and a test starts a child through the CLI from a
directory outside the corpus and reads the child's working directory back. It
fails with `instances` dropped from the set.

## Only qmcp says which server it is

**Assumption:** a health route identifies a server.

qmcp's names its pid; looksatwords' answers without one; codecartographer's
checkout served no health route at all. So every server but qmcp read as
`answering`, attributed by its run-file and nothing else, and the collector's
closing sentence that every server is identified was never printed, though no
fault was present at step 6. That is decision 7 working: a quiet state is
printed only when earned.

**No check exists** in the other repositories. `qm-queue.md` §4 carries it.

## Every stop here ends the process outright

**Assumption:** a stopped server withdraws its run-file.

The codecartographer session stopped its background command with its
ordinary task stop; the wrapper's cleanup never ran and its run-file stayed.
`qm dashboard --stop` ends the process tree with a forced kill, so qmcp, which
withdraws its own run-file on a clean shutdown, left both of its files behind.
The collector read all three as `stale`, and `prune --yes` removed them.

**The check exists** for reading them: `stale` and `prune`. The handbook says
what a stop leaves, and `qm-queue.md` §4 carries `--stop` withdrawing the
run-files of the tree it ends.

## Defects this session caused

- **The brief before the trial.** The command sent to the other session had
  not been run from another repository's checkout. One trial from
  codecartographer's directory would have found the refusal before anyone
  else spent a turn on it.
- **The first mutation script** used a `/tmp` path that native Python on
  Windows does not resolve, and reported a missing file instead of a result.
  It was rerun with the Windows path before any mutation was counted.
- **The handbook's first draft** said interrupting the wrapper withdraws its
  run-file. The run showed the ordinary stop does not, and the page now says
  what each stop leaves.

## What this did not prove

- A running container stack read by the collector: the shared alfred stack
  was not up during the readings.
- joe served under the wrapper: the person's choice put joe in the shared
  stack, so no session served a second one.
- That a server answering is serving the commit its checkout is on.
- Anything on a second machine.
