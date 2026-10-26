# ADR-XXXX — Control Plane and Engine Boundary for qmcp

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-25 |
| **Pends on** | Two inputs a person has not settled. **(a)** Whether the clients qmcp ships beside its seam — the cookbook's Metaflow recipes and the agent library — stay in this repository as clients, or move to repositories of their own; §4 classifies them either way, and only their location is open. **(b)** Whether `vox` gains a release line, which decides whether it is an engine qmcp consumes or seam code kept in another repository (§5) |
| **Principle** | `build-the-seam-buy-the-engines` — custom code concentrates where sovereignty matters |

## Context

The build-the-seam org record requires each project to ratify a
control-plane instance record naming what its seam owns, what it refuses to
own, and size-smell thresholds as revision triggers. This is that record for
qmcp.

qmcp's place in the stack is set by records it does not own. The
monitoring-seam record makes it the live orchestration surface whose human
queue a collector reads and dossier displays. The CLIs-are-for-machines record
pairs a harness that runs things with a control panel that shows them, and
qmcp is the harness of that pair, dossier the panel. The
acts-that-are-a-person's record makes answering the human queue a person's
act, which nothing qmcp runs may perform.

What qmcp does has grown past what its own documents say it does. Measured at
qmcp commit `82b2d58`:

- **Twelve roles in one package.** Read from its command groups, routes and
  modules: a tool server; the human queue; answering that queue by speech; an
  instruction inbox that asks consent and acts in a project's clone; standing
  up the local model; the harness's self-report paired with dossier; a
  topology and orchestration designer; a Metaflow cookbook host; tools that
  drive alfred; an archive of assistant conversations; an agent schema and
  PydanticAI library; and a stdio MCP server over the repository
  (`qmcp_mcp.py`).
- **Size.** 27,481 lines of Python in `qmcp/` and `qmcp_mcp.py`. Of these,
  7,630 are clients of the server that ship beside it: `qmcp/agentframework/`
  (4,167), `qmcp/cookbook/` less `delta.py` (1,587),
  `qmcp/integrations/pydantic_ai/` (765), `qmcp/testing/` (581) and
  `qmcp_mcp.py` (530). The other 19,851 are the seam. `qmcp/cli.py` alone is
  3,085 lines across 20 command groups.
- **Routes.** 41, of which 17 are registered wherever the server binds and 24
  only on a loopback bind (`qmcp/server.py:186-205`): the design routes, the
  thread archive, the voice routes and the instruction inbox.
- **The server starts processes of its own**, four kinds, each from a
  loopback-only route: the standing conversation `serve --converse` runs
  beside the server (`qmcp/server.py:148`), a spoken answer to a human request
  (`qmcp/integrations/voice/service.py:174`), a spoken instruction
  (`qmcp/instructions/service.py:138`), and `qmcp instructions act`, which
  asks consent before it acts (`qmcp/instructions/service.py:240`). The
  server's own module docstring says "No orchestration logic"
  (`qmcp/server.py:9-14`).
- **The protocol in the name is spoken by one file.** The HTTP API is REST in
  the shape of MCP's tool calls; nothing under `qmcp/` speaks MCP's JSON-RPC
  (`grep -rln "jsonrpc\|tools/call" qmcp/` exits 1). `qmcp_mcp.py`, behind the
  `mcp` extra, is the only MCP server.
- **One database for every role.** A consent is a human request
  (`qmcp/instructions/act.py`); a gate `selfcheck` ran is a tool invocation.
- **Other projects' commands live here.**
  `qmcp/integrations/voice/vocabulary.toml` fixes the test and check commands
  of joe, vox and qm, which the instruction loop runs in their clones.
- **vox is imported, at a submodule pin.** It is QM-authored, public and
  licensed, and qmcp depends on it as an editable path dependency on
  `vendor/vox` (`pyproject.toml`, `[tool.uv.sources]`), not on a released
  version. Its source is 2,247 lines at `c0b9b18`. It and `pyttsx3` are
  default dependencies, so every role needs the submodule.

The engines qmcp orchestrates are reached across a protocol and are not
imported: the local model through Ollama's HTTP API, speech capture and
transcription through joe's HTTP engine contract (`vox.adapters.joe`), alfred
over HTTP, and Metaflow flows that run in Docker as clients of qmcp's HTTP
API. SQLite, through SQLAlchemy and Alembic, is the storage engine.

## Decision

1. **qmcp is the record the stack writes to, and its seam is `qmcp/` less the
   clients named in §4.** The seam owns:
   - the tool registry, tool invocation, and a row per invocation;
   - the human queue: a question's options, expiry and lifecycle, and the
     record of who answered;
   - the instruction record, the consent an act asks through the human queue,
     and the history of a project's earlier instructions that each act is
     handed;
   - the record of a gate run and the units of work derived from it;
   - the topology vocabulary, the orchestration plane's declaration of what a
     shape would do, and saved designs and components;
   - which server this is: the run-file and the identity on `/health`;
   - the policy deciding whether an act may run — consent, spend and the
     loopback rule — and the glue that reaches each engine.

2. **The seam refuses to own:**

   | Not the seam's | Whose |
   |---|---|
   | capturing and transcribing speech | joe, behind vox's engine contract |
   | the synthesizer qmcp speaks with | `pyttsx3`, reached through vox |
   | generating text from a clone | the local model Ollama serves, or another runtime |
   | running a flow's steps | Metaflow, in Docker |
   | rendering and captioning media | alfred |
   | showing the record, and a window to answer the queue in | dossier; codecartographer draws shapes; joe's page shows the conversation |
   | which projects exist, and the checks each runs | the roster in `governance/qm`, and each project for its own checks |
   | answering a human request | a person |

   Importing a speech, model, media or flow engine into the seam is a boundary
   violation, and so is a route or a command that answers a human request
   without a person.

3. **The seam acts only after consent, and starts a process only for a person
   at this machine**: a conversation, a spoken answer or a spoken instruction
   that person started, or an act that person consented to. Each is started
   from a route registered only on a loopback bind. That the server starts
   processes is part of the seam's job — orchestration triggers are the
   seam's by the org record — and the server's own description says so.

4. **The clients qmcp ships are classified as clients, not seam.** The
   cookbook's recipes and flows (`qmcp/cookbook/` less `delta.py`,
   `examples/flows/`, `docker/`), the agent library (`qmcp/agentframework/`,
   `qmcp/integrations/pydantic_ai/`), the test harness (`qmcp/testing/`) and
   the stdio MCP server (`qmcp_mcp.py`) reach the seam through its HTTP API or
   its public Python surface, and are excluded from §6's seam size. Where they
   live is (a) in **Pends on**.

5. **vox is seam code until it is released.** Under the org record's §5, a
   dependency on an unreleased surface is not an engine. Until vox publishes a
   release that qmcp depends on at a version, vox's lines count toward qmcp's
   seam size, and qmcp depends only on what `vox.adapters` and vox's
   synthesizer export. Whether vox gains a release line is (b) in **Pends on**.

6. **Recognised leaks, capped rather than blessed:**
   - `qmcp/integrations/voice/vocabulary.toml` holds other projects' check
     commands. No other project's commands are added to it; the direction is
     each project declaring its own checks where the roster finds them.
   - The `cookbook` command group holds both the Docker recipes (§4's clients)
     and the offline checks of the voice and instruction paths (seam). No
     command of a third kind is added to it.
   - One database holds every role's rows. No role adds a table another role
     reads without going through the seam's own queries.

## Consequences

- A reader setting qmcp up can tell which part is the seam and which parts
  are clients shipped beside it, and qmcp's docs are organised by the same
  roles.
- The seam measures 19,851 lines, plus vox's 2,247 while §5 holds: about
  22,100, which is more than one person holds whole. §6's thresholds are set
  against that figure rather than a target, so they detect growth from here
  rather than declaring the present size healthy.
- Cost accepted: the clients stay in this repository until (a) is settled,
  so one sync installs them all, and the size measure has to subtract them by
  path.
- Cost accepted: the server's description changes from "no orchestration" to
  orchestration that waits for consent, which is a claim the suite has to keep
  true: nothing acts before "approve", and nothing answers a human request.
- Obligation: the three leaks in §6 are named in qmcp's docs where a reader
  meets them, and each is a revision trigger below.

## Alternatives considered

1. **Count everything in `qmcp/` as seam.** Rejected: the cookbook's flows and
   the agent library reach the server the way any client does, and counting
   them makes the size smell measure what the repository happens to carry
   rather than what the control plane does. A client moved to its own
   repository would then read as the seam shrinking.
2. **Keep the description "no orchestration" and move the conversation and
   the act out of the server.** Rejected: starting an act a person consented
   to is an orchestration trigger, which the org record assigns to the seam,
   and moving it out would put the consent check and the act in two
   processes that each have to trust the other.
3. **Treat vox as an engine because QM authored it and it has its own
   repository.** Rejected: authorship and location are the wrong test. The
   org record classifies by what a component is consumed as, and a path
   dependency on a submodule couples qmcp to vox's unreleased surface, which
   is exactly what its §5 says makes code seam code.
4. **Split the roles into separate servers now.** Rejected for this record:
   the roles share one human queue and one record by design, and a split is a
   decision with a migration behind it. The size smells below are what force
   it if it is needed.

## Revision triggers

- The seam, measured as in Context and less §4's clients, exceeds 30,000
  lines of Python, vox included while §5 holds.
- `qmcp/cli.py` exceeds 4,000 lines, or gains a 21st command group.
- A route that writes is registered off loopback beyond the human queue and
  tool invocation.
- A default dependency is added that only one role needs.
- A speech, model, media or flow engine is imported into the seam.
- Another project's command is added to `vocabulary.toml`, or a third kind of
  command to the `cookbook` group.
- (a) or (b) in **Pends on** is settled.
- A thirteenth role appears: a command group or route family that serves none
  of the twelve in Context.

## Amendments

*None.*
