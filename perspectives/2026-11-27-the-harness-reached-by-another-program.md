# The harness reached by another program: what was believed, and what held

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-11-27 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Fable 5.2, driving the session under review, wrote this page. No second reading was made of it |

One session, from 2026-11-25 to 2026-11-27, widened what reaches `qmcp`
beside its own command line. codecartographer's web window gained a read-only
Harness panel (codecartographer#172, open). `qmcp` gained tools that read
`apothecary` (qmcp#145), a runtime that drives an agent another program hosts
(qmcp#144), a route that serves the Agent Host Protocol's clients (qmcp#146),
and a turn over that route that asks consent for one run, answerable from a
client on the same machine (qmcp#147). The decision is
`adr/DRAFT-qmcp-speaks-the-agent-host-protocol-in-both-roles.md` on
`project/qmcp`; the plan for a local model that answers for the workshop is
`plans/the-shop-assistant.md`. Figures here are of `qm` at `ffe6863`, `qmcp`
at `fa657bc` and `project/qmcp` at `46198d3`.

Each belief below is marked **established**, with how, or **inference**.
Where the how is the session's own account of a command it ran, and the
output was not kept, the entry says so.

## A page told the team a default that the queue listed as undecided

**Established**: #366 merged a step into
`docs/journeys/use-a-model-with-an-application.md` saying a turn over the
protocol cannot state what it may spend, so the harness runs nothing, with a
troubleshooting row for `issued against 0 runs`. The same day's queue, §3,
listed how a turn states its budget as blocked on a person. The answer came
within hours, and #368 replaced the step and the row.

The belief was that a page for the team describes what `main` does at the
moment of writing. It does, and the page was true for a few hours. But the
behaviour it described was the side of an open question that happened to be
merged first, and a reader of the journey could not tell that from a settled
design. The request was to update the docs for team development after the
work, and the work was not finished: one of its inputs was waiting.

The check that would have caught it is a reading of §3 before writing a page
about the same subject. Nothing runs that reading. A page could name the
open input it rests on, as a record's `Pends on` row does; no page here does,
and `qm glossary-links` and `qm docs check` look at neither.

## Two roles read from one source agree with each other

**Established**: the client role and the host role were each written from the
protocol's type definitions at one commit of its repository, and each was run
against a stand-in and against the other.

Their agreement is the weakest evidence in the work, and it is the only
evidence that either speaks the protocol. Both carry one reading of the
definitions. If that reading is wrong in a way the definitions permit, each
role is wrong the same way and the pair passes. The Lean reader of
`2026-11-24-a-reader-written-without-its-language.md` is the same shape: a
thing tested against its writer's picture of a language.

A small instance showed on the last day. A probe written by hand sent
`initialize` with a version the host does not speak, and the host refused it
and named the versions it does. The refusal was correct, and it was also the
first time anything not built from the session's own picture of the protocol
had spoken to the host.

The check is a run against a host and a client somebody else wrote. It does
not exist, and the queue's §5 says so. It is the next piece of work on the
protocol, ahead of anything that adds to either role.

## Three tests passed and held nothing

**Established**, by the session's account of its mutation pass on qmcp#147;
the output was not kept. Each new test was run against a version of the code
with its behaviour broken. Three stayed green.

- The test of a queue refusal built its acts with no queue, so the path it
  named never ran.
- The test of a skipped answer carried no value, and was rejected for the
  missing value before the skip was read.
- The test loop attached as a client from another address, so every answer in
  it was refused for where it came from, and a mutation that let any client
  answer changed nothing.

Each was a test whose name said one thing and whose setup made another thing
true first. Each was repaired so that its mutation goes red, and the mutation
is named in its docstring.

The belief was the ordinary one: a test that passes, with a name that
describes the behaviour, checks the behaviour. Charter
`a-check-is-evidence-after-it-fails` is the rule, and it held here because it
was applied to every test and not to a sample. The pass was driven by a
script kept in no repository, as `qmcp` has no command for it. `qm mutate`
exists in this corpus and nothing like it travels to a project.

## The test server raised another error than the real one

**Established**, by the session's account: under the test server the queue's
refusal arrived as an error of a different class than the one `qmcp`'s own
client raises when it runs as a server. The handler had been written for the
second and let the first through as a crash.

The repair reads any error that carries a response, and lets every other
error through. **Inference**: that it holds where `qmcp` runs as a server.
The real run of the relay, on a server started for the purpose, answered
`approve` once and `hold` once; neither is a refusal. The queue's §5 carries
this.

The belief was that a test client stands in for the real one in every
respect a handler can see. The check is one refused answer over a real
socket: an answer to a request already answered. It was not run.

## A failed edit emptied the file it was editing

**Established**: a script that read a file, replaced passages and wrote it
back passed an illegal line-ending argument to the write. The write truncated
the file and then raised. A new test file in a `qmcp` worktree stood at zero
bytes and was written again whole.

The session caused this. The belief was that a write which raises has written
nothing. The file was new and uncommitted, which is the one state in which
nothing else held its content.

The check is the size of every file a script writes, read after any non-zero
exit and before a second run. It is a habit and not a tool. Committing a new
file before a script edits it would make the loss a `git checkout`.

## The harness served none of it until it was started again

**Established**: `qm dashboard` on 2026-11-27 reported the harness on 3141 as
listening. The session had last started it on 2026-11-25, before qmcp#144,
and by its own account of earlier requests that harness answered `healthy`
and served no `/v1/ahp` and no `apothecary` tool; it was not asked again
before it was stopped. After `qm dashboard --stop harness` and
`--start harness`, the route answered and the tool list named the
workshop's.

For two days the queue and the journey said `qmcp` serves the protocol's
clients, in the present tense, and the one `qmcp` a person on this
workstation could reach did not. Each page was true of `main`. The health
answer names a pid, a port, a database and a start time, and no commit, so
nothing a reader could ask would have said the running server was older than
the pages. `2026-11-25-sharing-a-dev-state.md` found the same gap in a
shared alfred.

Two smaller facts sit beside it. The harness runs from the main clone's
environment, so a `uv run` there that needed to replace the installed command
failed on the locked file, and the session ran `qmcp` commands from a
worktree for the rest of its work. And the session did not restart the
harness on its own after each merge, which was right: a restart drops what
the server holds, and it is a person's to ask for.

The check is a health answer that names the commit. It does not exist, and
the queue's §4 now carries it.

## A submodule stood off its pin, and was put back before anyone asked why

**Established**: at the close, `git status` in the `qmcp` clone showed
`governance/qm` modified, checked out at an earlier tip of `project/qmcp`
than the commit `main` pins. No command of this session moved it, by a
search of the session's own commands. `git submodule update governance/qm`
put it at the pin, and the clone read clean.

**Not established**: who moved it, or whether it was meant. The session
restored it first and looked for the cause second, which is the wrong order
where other sessions share the clone. The commit it stood at is on the host,
so nothing was lost, but a deliberate checkout would now read as never having
been made.

The check exists and was not run: fact C of `AGENTS.md`, what else is in
flight in this clone, was established at the open and not again after the
clone was fast-forwarded. A fast-forward does not move a submodule, so the
state can also come from nothing more than a merge that changed the pin.

## Figures typed, and figures no repository can reproduce

**Established**: the body of #368 carried a head commit that was not the
branch's, typed where the command's output should have been pasted; it was
corrected by an edit before the merge. And the comparison of three local
models in `plans/the-shop-assistant.md` ran once per model from a script kept
in no repository, which the plan's *Measured* section and the queue's §5
both say.

The first is a slip the branch report exists to prevent, and it prevents it
only when its output is pasted whole. The second is a figure with a date and
no command. The plan says so, which keeps a reader from trusting it, and
does not let a reader repeat it. The assistant as a `qmcp` command, with the
question set as its test, is what would replace the script; it is the plan's
second step.

## What the runs showed, and what was not run

On a server started for the purpose, with a database of its own: a client on
a loopback socket started a turn, was shown the consent as the protocol's
input request, answered `approve`, and the runtime ran; the queue's row
named `agent-host-protocol` as who responded. A second turn answered `hold`,
and nothing ran.

Not run: either role against another program; a turn on the harness
`qm dashboard` starts; a refused answer over a real socket; a client attached
from another address over a real network, which the tests hold through the
address the hub is told; the page's example against a running server.
