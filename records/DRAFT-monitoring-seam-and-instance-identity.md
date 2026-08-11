# QM-XXXX — The Monitoring Seam, and Instance Identity

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-11 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P3 — replaceability is the risk strategy; P6 — decisions are documented or they didn't happen |

## Context

The harness now reports the org's state from two committed documents, and the
generated-documents convention governs how they are made and read. Both are
generated from a git tree and a `gh` call: facts that hold for the
organisation, at a commit, wherever you stand.

The next thing the reviewer needs to see is not like that. Running six
concurrent sessions produces state that exists on *one workstation at one
moment* — which sessions are live, and which human gates are waiting on an
answer. `qmcp` is where that state lives: it holds a human-in-the-loop queue
over HTTP, and `dossier` is the dashboard that should show it.

Wiring a view to a live service is the obvious move, and three properties of
this particular service make it the wrong one. Each was established by reading
the code, not inferred from its shape.

**Reading the queue writes to it.** `GET /v1/human/requests/{id}` assigns
`status = EXPIRED` to a pending request whose `expires_at` has passed
(`qmcp/server.py:373-382`), and the session context manager commits on exit
(`qmcp/db/engine.py:69-74`), so the transition is persisted *by the read*. It
is also the only mechanism that ever produces `expired`; the list endpoint
applies no expiry, so the two endpoints disagree about the same row. Expiry is
terminal — the answer POST then returns 410, no endpoint un-expires a request,
and `CANCELLED` exists in the enum with no code path that sets it. A tab that
polled detail URLs to show who had answered would expire the gates it displayed
by looking at them, and the write it performed is a decision the human can no
longer make.

**The service cannot say which service it is.** `/health` returns
`{"status": "healthy", "version": __version__}`, and that version is a package
constant, byte-identical across every `qmcp` process on the machine and every
clone of it. The queue itself is a SQLite file resolved against one process's
working directory (`sqlite+aiosqlite:///./qmcp.db`, `qmcp/config.py:23`) behind
a port that defaults to `3333` (`qmcp/config.py:19`). So two clones have two
different queues, both answer `/health` identically, and nothing obtainable
over HTTP distinguishes them.

**A live read cannot be aged.** It has no `generated_at`, so it cannot be
stamped, budgeted, or quoted. A view that looks live and is an hour old is
worse than one that admits its age, because the first stops people checking.

The consequence that decided this record: a monitor built on a *roster* of
instances reports perfect health in the one case that matters. A stale entry —
a previous session's server, or another session's, still listening on a listed
port — answers `/health` 200 and returns zero gates, because its queue is a
different file. The document then reads `instances_reachable: 1`,
`gates_pending: 0`, every signal green, while a gate waits on a port nobody
listed. An empty gate list means "nobody is waiting on you", and that is the
single most harmful wrong answer this kind of document can give.

`records/DRAFT-seams-on-standard-protocols.md` governs seams to *third
parties* and says internal control-plane choices are not seams. This record
governs the internal one, and does not relax that record.

## Decision

1. **A view reads a document; a collector reads the world.** Exactly one
   component may open a socket to a monitored service: the generator. It
   writes a schema-versioned document, and every view — CLI, TUI, HTML,
   Markdown — parses that document and nothing else. A dashboard acquires no
   HTTP client. This extends the existing rule that a renderer may not run a
   command: a renderer may not make a request either, and for a stronger
   reason, because here the request mutates a human's pending decision.

2. **A machine-scoped document is never committed, and its generator refuses
   to write inside the repository** — the existing rule, applying whole rather
   than as a `local` sub-layer, because there is no machine-independent half of
   this document to keep.

3. **A committed policy carries no machine literal.** No port, no filesystem
   path, no `127.0.0.1`, no instance roster. What is committed is what is
   identical on every machine: the endpoint allowlist with a
   `side_effect: none | persists | creates` field per entry, so *which reads
   are writes* is a reviewed fact rather than a comment in a collector; the
   loopback-only rule; the permitted port range; and the per-call timeout. A
   staleness budget stays in the tool, as `ci/disk_status.py` keeps it, so two
   machines cannot disagree about when a figure stops being quotable.

4. **Instances are discovered, never enumerated.** A service that a monitor
   watches binds port 0 — the correct reading of "never bind a default port" —
   and writes a run-file to a machine-scoped directory outside every
   repository, carrying its port, its resolved database path, its start time,
   and the session declaration. The collector enumerates that directory. A
   session therefore becomes visible without editing a reviewed file, which
   the one-PR-per-repository rule would otherwise price at a contributor's
   whole slot.

5. **Identity is asserted before a measurement is attributed.** The collector
   matches the run-file's port, database path and start time against the port
   it dialed and the response it got. On any mismatch, or a port answering
   with no run-file, the instance's gates become `{"unknown": "<reason>"}`.
   Refusing to emit gates that cannot be attributed is better than emitting
   them under the wrong session's name.

6. **Two facts are reported that a roster-shaped document cannot express**:
   instances declared but not found, and instances found but not declared. The
   second is a finding in its own right, as a lightweight tag is a finding
   rather than a release. Until a service can state its own identity, the
   document carries a top-level `roster_completeness` unknown and every view
   names the queue as *the gates of the instances it could identify*, never as
   *the gate queue*.

7. **A view may not render a quiet state it has not earned.** A whole-list
   unknown must survive into storage as a synthetic row, so a table cannot be
   empty while an instance is unreadable. "Nobody is waiting on you" may be
   printed only when no instance is unknown, no instance's gate list is
   unknown, and the document is within its budget. Otherwise the count is
   rendered as *at least N* with the unreadable instances named in the same
   sentence. A bare count never appears next to nothing.

8. **Measuring and acting stay separate tools**, as `ci/disk_status.py` and
   `ci/disk_reclaim.py` already are. Answering a gate is a second tool,
   dry-run by default, requiring the exact option string, and re-reading the
   live service rather than trusting a document that may be an hour old.

9. **Shared code is split along the capability line, not the duplication
   line.** A module a renderer may import holds no `subprocess` and no `os`;
   `run` and `inside_corpus` live in a module generators import. A guard on
   this is written over the transitive import closure, not over the text of
   one file: `assert "subprocess" not in source` passes on a renderer that
   imports a module that imports subprocess, and also passes on code that
   deletes the prose and adds the call.

10. **The transport is an injected callable**, so the collector's own tests
    drive it against recorded responses — offline, no socket, no import of the
    monitored service — and can assert structurally that no detail URL is ever
    requested for a row whose stored status is `pending`. The live round trip
    is an acceptance procedure run in the monitored service's own suite, where
    binding loopback on port 0 is already normal, and it is reported as an
    acceptance run rather than as CI coverage. The corpus's own suite binds no
    port.

## Consequences

- The dashboard keeps working when the service is down, and says so with an
  age. Nothing in a view's read path is a socket.
- A service that wants to be monitored owes two things it does not owe today:
  a run-file, and an identity endpoint. Until the second exists, the document
  carries an unknown rather than a guess, and that unknown is the argument for
  building it.
- Cost accepted: the reviewer sees the queue one refresh behind rather than
  live. Given that a live read expires the gates it displays, one refresh
  behind is the feature.
- `qmcp` is not yet governed — no `AGENTS.md`, no `.github`, no `LICENSE`, no
  submodule — and nothing the harness depends on should read a repository with
  no gates. Onboarding it precedes wiring it.

## Alternatives considered

**A tab that polls the API.** Rejected on the write, not on taste: the polling
endpoint persists a terminal state transition. Also inverts the design, since
every normalisation — naive-versus-`Z` datetimes across the same row, the
`failed`/`error` vocabulary split between the API enum and the metrics label,
paging with no total available anywhere — would live in each view and again in
the next one.

**A committed instance roster, on the disk-policy precedent.** Rejected
because the precedent refutes it. `ci/disk-policy.yaml` carries the heading
*paths are written against the environment, not against one machine*, expands
`${VAR}`, and makes an unset variable an unknown with a reason. A roster of one
workstation's ports is the machine literal that file exists to avoid, and
committing it publishes one session's Tuesday as an org fact.

**Environment-variable indirection in the policy** (`${QMCP_PORT}`). Better
than literals and still insufficient: a session that did not export the
variable is not `unknown`, it is absent, and absent renders as an empty
queue — the one wrong answer. Discovery has no such hole.

**A pre-allocated port per session.** A default port with extra steps, and it
fails §4 for the same reason.

**Making the collector able to answer a gate too.** Rejected on the ratified
split: a collector that can also act is one flag away from acting on a number
that was wrong.

## Revision triggers

- The monitored service gains an endpoint stating its own identity — resolved
  database path, port, start time — and a real row total. Decisions 5 and 6
  shrink to reading it, and the `roster_completeness` unknown is retired.
- No `GET` in the monitored service persists a state change. Decision 1's
  second reason weakens to the ordinary one, and the `side_effect` field
  becomes a check rather than a warning.
- A second machine-scoped document appears. The shared parts named in
  decision 9 are extracted at that point, not before.

## Amendments

None.
