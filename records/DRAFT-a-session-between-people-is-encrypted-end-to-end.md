# QM-XXXX — A Session Between People Is Encrypted End to End, Before It Exists

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-31 |
| **Pends on** | Nothing — the first consumer is named. `rad` builds it, in the `messaging/` host seam governed by its own record, and the seam reaches every rad host: `codecartographer`, a native Android port (referenced as `private-35`, a private repository), and any future host, all adopting one `Session` rather than reimplementing the protocol. `leo` remains a candidate for a document-collaboration session and is not the first. |
| **Principle** | `seams-on-standard-protocols` — replaceability is the risk strategy; `ownership-is-the-deliverable`; `decisions-are-documented` |
| **Restated in** | Nothing. |

## Context

This estate has no channel between two people. That is a measured fact, not an
assumption: the radial menu's adoption record declares zero runtime
dependencies and no network call, and lists acquiring one as a revision
trigger; the harness and dossier serve HTTP on loopback by deliberate
constant; MIDI carries clock and control with no confidentiality layer, to
hardware in the same room; and the one repository whose description says
*collaborator* carries thirteen packages and not one of them is a transport.

That absence is the opportunity this record takes. Security properties bolted
onto an existing transport inherit every compromise the transport already
made — session identifiers designed before anyone asked who could read them,
persistence layers that logged plaintext because logging predates the
threat model. The moment before the first wire exists is the only moment the
rule is free.

The rule is written against a specific failure the corpus already catalogues
in other domains: **a security claim nothing can exercise**. An "encrypted"
component with no channel, a checkbox cipher on a wire whose keys the server
holds, a transport that is confidential against outsiders and transparent to
the operator — each reads as protection and enforces nothing. So this record
binds the *shape* of a future thing rather than decorating a present one, and
its conformance clause is written so the first implementation can be measured
rather than believed.

## Decision

**Any session that carries content between two or more people crosses the
network encrypted end to end. The parties hold the keys; no relay, host,
or operator of this estate's infrastructure can read the content. This binds
from the session's first commit, not from its first audit.**

### §1 — What is a session between people

Content one person produces for another to see live or near-live: a shared
document being annotated, a collaborative editing surface, a remote rehearsal,
a shared control surface driving one performance from two rooms, chat beside
any of them. The test is the parties, not the payload: telemetry a machine
emits for a machine is a seam under the seams record, not a session under
this one.

### §2 — End to end means the ratchet family, not transport security

Transport encryption to a relay the operator controls is necessary and not
sufficient: it protects the wire and leaves the relay reading everything. A
conformant session uses an established, published protocol with **forward
secrecy and post-compromise security per message** — the Double Ratchet as
deployed by the Signal protocol family, or a successor with equivalent,
published, independently analysed properties. Per
`seams-on-standard-protocols`, the protocol is one with multiple independent
implementations; per `build-the-seam-buy-the-engines`, the cryptography is an
engine that is **selected, never written here**.

### §3 — The relay is blind by construction

Whatever routes the session — a moat ingress, a rendezvous service, a TURN
server — sees ciphertext, sender, recipient, and timing, and nothing else.
Metadata minimisation is a stated goal rather than a hard clause, because a
relay that cannot route is not a relay; content confidentiality against the
relay is the hard clause.

### §4 — Group sessions do not weaken the rule

A performance is rarely two people. Group sessions use the same family's
group constructions (sender keys, or a tree-based group agreement of the MLS
kind), and the arrival or departure of a member re-keys the session. A group
whose members cannot be removed cryptographically has a membership list and
not a boundary.

### §5 — What this does not cover, so the border is legible

Machine-to-machine seams (the topology JSON, the families file, the vector
sets) — those are governed by the seams record and are mostly *meant* to be
readable. Local pipes between processes on one machine. MIDI to hardware in
the room. Public performance output itself — a show is for an audience. And
availability: this record buys confidentiality and integrity, not uptime.

### §6 — Conformance is measurable before trust

The first implementation ships, alongside its transport, an executable
conformance surface in the same spirit as the radial menu's vector set: key
agreement transcripts that a second implementation can replay, a demonstrated
re-key on member change, and a demonstrated failure — a relay handed the
session log and shown unable to decrypt it. A session layer whose encryption
has never been seen to *withhold* content is a claim, per the charter's own
evidence principle.

## Consequences

**The first collaboration feature gets slower and more expensive.** Key
management, device identity, and session resumption are real costs paid
before the first shared cursor moves. That is the trade, taken with eyes
open: retrofitting the ratchet onto a shipped plaintext session has never
once been cheaper.

**The estate needs an identity story before its first session.** Ratchets
bind to device keys; device keys bind to people; authentik exists in moat and
is an *operator* identity, which §3 says must not be the session's trust
root. Reconciling those is design work this record creates and does not do.

**Nothing enforces this today, and nothing can.** There is no transport to
check. The record's teeth arrive with its first consumer, which is exactly
why the `Pends on` names that consumer as the open decision.

## Alternatives considered

**TLS to the relay and trust the operator.** The industry default and the
cheapest build. Rejected as the *foundation* because it makes the operator a
reader of every session, which turns a compromise of one machine in moat into
a compromise of every conversation ever relayed through it.

**Bake encryption into rad.** The request that prompted this record, taken
literally. Rejected with its own measurement: rad has no channel, no second
party, and a record declaring both facts load-bearing — a crypto layer there
would be a security claim nothing can exercise, contradicting rad's
zero-dependency clause without protecting anything.

**Wait for the first session feature and decide then.** Rejected on the
observed economics: the deciding moment would arrive as a feature deadline,
and every shipped plaintext session in the industry was once a team deciding
encryption could follow the demo.

**Write our own protocol.** Forbidden twice over — `build-the-seam-buy-the-engines`
selects engines rather than writing them, and novel cryptography without
published analysis is the canonical unexercisable claim.

## The first consumer, and its reach

`rad`'s `messaging/` seam is the first implementation, and it is deliberately
one implementation for many hosts. §2 of that record ships a `Session` and no
relay; §7 names the hosts that adopt it — `codecartographer` over a browser
transport, a native Android port over the platform keystore, and the reference
`index.html` adopting nothing by default. A downstream host supplies a
transport and a device-trust root and **never the protocol**, which is what
keeps one encryption guarantee across every rad rather than one per host. The
seam's conformance surface (that record's §6) is what a host replays to show it
adopted rather than approximated — the same discipline by which each host
replays the interaction vectors to show it drew the right menu.

## Revision triggers

- A second session transport, in a project that is not a rad host. rad's seam
  covers the rad family; a document-collaboration session in `leo`, or chat in
  another project, is a new consumer and tests whether §2's properties are
  stated engine-agnostically enough to be adopted a second time.
- The identity question in Consequences getting an answer anywhere. §5 of the
  rad record and this record's Consequences both defer it; the first project to
  answer it sets the pattern the rest adopt.
- A successor protocol family displacing the ratchet's properties (as MLS is
  doing for large groups) — §2 names properties, not a brand, and the named
  examples are updated to match the field.
- A session class that genuinely cannot ratchet — an audience-scale broadcast
  with per-viewer keys, for instance — which would need its own record rather
  than an exception here.

## Amendments

*(none)*
