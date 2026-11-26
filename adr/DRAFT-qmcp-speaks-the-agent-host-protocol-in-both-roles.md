# ADR-XXXX — qmcp speaks the Agent Host Protocol as a client and as a host

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-11-26 |
| **Pends on** | Two inputs. **(a)** How a turn started over the protocol states its budget. An act's budget defaults to zero, which declares and stops, and the protocol's turn carries no budget; §4 keeps that default until this is settled. **(b)** How qmcp knows who answered a consent request relayed by an attached client. §5 bounds the relay to the one case where the question has an answer without it |
| **Principle** | `build-the-seam-buy-the-engines` — custom code concentrates where sovereignty matters |

## Context

The Agent Host Protocol describes a server that runs agent sessions and the
clients that attach to it: an editor, a web page, a command line. The host
holds each session's state and several clients see the same state. Messages
are JSON-RPC, usually over a WebSocket, and the protocol prescribes no
transport. A client opens a session, starts a turn with a message, and reads
what the host streams back until the turn completes or fails. When an agent
wants to use a tool, the host can hold the call for a client to confirm. The
specification is published at
<https://microsoft.github.io/agent-host-protocol/> as a working draft with
released versions, and says its wire types may change.

qmcp already has both halves of that exchange in its own terms.
`qmcp/integrations/agents/` runs an instruction through a runtime chosen by
name, each an adapter that reaches an engine qmcp does not import. The
instruction record, the consent an act asks through the human queue, and the
rule that one act runs at a time are the seam's, by
`DRAFT-control-plane-and-engine-boundary.md` §1 and §3.

Three of that record's rules bear on the protocol. A route that starts a
process is registered only on a loopback bind. Answering a human request is a
person's, and a route that answers one without a person is a boundary
violation. A default dependency only one role needs, and a role beyond those
its Context counts, are both revision triggers.

`records/DRAFT-acts-that-are-a-persons-by-constitution.md` names answering the
queue as a person's act and welcomes carrying the question to wherever the
person is reading. `records/DRAFT-no-unattended-spending.md` makes consent to
a paid call consent to a stated amount.

## Decision

**qmcp carries the Agent Host Protocol on both sides: an Agent Host Protocol
host is one of its runtimes, and qmcp is a host that the protocol's clients
attach to. In both roles the instruction record, consent and the one-act rule
are qmcp's and are unchanged.**

1. **As a client, a host is a runtime.** An adapter in
   `qmcp/integrations/agents/adapters/` opens a session on a host named by a
   setting, starts one turn with the act's brief and the act's clone as the
   working directory, and returns what the host streamed as the act's outcome.
   The host is reached across the protocol and never imported.

2. **As a client, qmcp confirms nothing.** A tool call the host holds for
   confirmation is answered denied, and the outcome says how many were denied
   and which. The consent an act carries is consent to run that act; it is not
   consent to each thing a remote agent then asks for.

3. **As a host, a session's turn is an instruction acted on.** The agents the
   host advertises are qmcp's runtime names. A turn records an instruction and
   starts an act on it, in the clone the session names. What the act writes is
   what the host streams, and the act's end is the turn's end. The session
   adds no second record of the work: the instruction row and its outcome are
   the record.

4. **Consent and budget are the act's own.** A turn's act asks its consent on
   the human queue as every act does, and runs nothing until it is approved.
   Its budget is the act's default until **(a)** is settled.

5. **An attached client may relay a person's answer to that consent, on a
   loopback connection.** The host shows the request as the queue holds it and
   relays the one answer a person gives in the client, to the same refusals
   the queue makes for any answer. Nothing is selected in advance, nothing
   answers on a timer, and no approval is kept for a later request. A client
   attached from another address is shown the request and cannot answer it.
   `responded_by` names the protocol as the surface the answer came through.

6. **One act at a time holds.** A turn started while a conversation or an act
   runs is rejected with the reason, in the protocol's own rejection. The host
   queues nothing.

7. **The host's routes exist only on a loopback bind**, as every route that
   starts a process does.

8. **What qmcp does not serve is advertised as absent.** The protocol's
   terminals, change sets, resource watching and telemetry channels have no
   counterpart in qmcp. The host declares what it serves, and a client that
   asks for the rest is refused in the protocol's terms. Nothing is stubbed to
   look present.

9. **The protocol versions qmcp speaks are stated in one place**, and a peer
   that offers none of them is refused at the handshake, in either role.

10. **The transport library is an optional extra.** qmcp installed without it
    imports and serves everything else.

## Consequences

An instruction can be run on an agent another program hosts, and an editor
or a page that speaks the protocol can run qmcp's runtimes, without either
side importing the other.

The host role is a role beyond those the control-plane record's Context
counts, and a new route family. That record's trigger fires, and its Context
and seam measurement are read again with this role in them.

The host role needs things qmcp does not have: output streamed as it is
produced, where a runtime returns once; state synchronised across clients;
and a way to stop a turn. Each is built for this role or declared absent
under §8. The cost is accepted: it is the seam's size growing for a protocol
whose wire types may change.

A consent request becomes answerable from one more surface. The queue's
refusal of a second answer orders the surfaces. `responded_by` naming a
protocol is weaker than naming a person; on a loopback connection that is the
gap the command line already has, and it is **(b)**.

`ci/attested-registry.yaml`'s entry for answering the queue is unchanged: its
evidence is the response row, and the relay writes that row through the
queue's own route.

A turn that cannot state a budget runs under the default of zero, so over the
protocol an act declares what it would need and stops. That makes the host
role incomplete for any runtime that spends until **(a)** is settled, and the
incompleteness is the spending record working.

Tests hold each clause without a second program: a fake host for the client
role, a fake client for the host role, both over an in-process message
stream, and a test that starts the server off loopback and finds the host's
routes absent.

## Alternatives considered

1. **The client role alone.** It fits the control-plane record with no
   revision and adds one adapter. It lost because it leaves the programs that
   speak the protocol unable to reach qmcp's runtimes, its instruction record
   or its queue, and those programs are where a person already is.

2. **The host role alone.** It lost because the client role is the cheaper
   half and proves the wire against a real host before qmcp serves one.

3. **A separate server for the host role.** The seam would not grow. It lost
   to the control-plane record's own reasoning against splitting roles into
   servers: the turn is an act, and the act, its consent and the one-act rule
   live in this process.

4. **Reach those clients through qmcp's tool server instead.** No new
   protocol. It lost because a tool call is one request and one answer, and a
   session is a conversation with streamed output and a held confirmation;
   carrying one in the other would hide the consent step inside a tool
   result.

5. **A client attached from any address answers consent.** It lost to the
   same reasoning as the web window's record: off loopback the answerer is
   anyone who can reach the port.

6. **Wait for the protocol to settle.** The draft says its types may change.
   It lost because §9 pins what is spoken and the tests run without a peer,
   so a change in the protocol is a refused handshake and a failing test, not
   silent drift.

## Revision triggers

- **(a)** or **(b)** in **Pends on** is settled.
- The protocol publishes a version that removes or renames a message this
  record's clauses rest on: the session's creation, a turn's start and end,
  or the held confirmation.
- The host's routes are wanted off loopback.
- A second act is wanted while one runs.
- `DRAFT-control-plane-and-engine-boundary.md` is accepted with a seam
  measurement this role exceeds.
- `ci/attested-registry.yaml`'s entry for answering the queue changes what
  the act asserts or what enforces it.

## Amendments

*None.*
