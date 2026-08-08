# ADR-XXXX — An MQTT Client Library Is a Test Dependency of the Wire Harness

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-08 |
| **Pends on** | Nothing — ready to be argued |

## Context

The org house-stack record fixes a blessed set for code QM builds and requires
a record, org-level, for anything outside it before that dependency appears in
review. Its carve-outs — contributions in a target community's idiom, client-
or platform-mandated stacks, and engines — do not cover this case. An MQTT
broker is an engine and is selected rather than written; a client library
linked into QM's own code is a dependency.

The topic contract is documented and exercised, but only through an in-process
fixture. That fixture proves the envelope and the contract's retention rules;
it proves nothing about the wire. The milestone's second assertion asks for a
firmware-emitted event to round-trip the documented topic and validate against
the schema, in CI, with no hardware attached. Nothing in the blessed set speaks
MQTT, so the assertion is unreachable without a client.

The gap is not cosmetic. The failures a wire test catches are the ones an
in-process fixture structurally cannot: a topic string that is correct in the
constant and wrong in the firmware, a retained flag set on the wrong topic, a
payload that is valid JSON and the wrong encoding, a last-will that never
fires. Each of those is invisible to a fixture that never serializes to a
socket.

Two candidate shapes exist. A client-only library leaves the broker to be
provided by the environment. A combined broker-and-client library in pure
Python would let the harness run with nothing installed, at the cost of
importing a second MQTT protocol implementation into the dependency tree — and
`amqtt`, the leading option of that shape, resolves to eleven transitive
packages including a CLI framework, a terminal-rendering library and a
password-hashing library, none of them blessed and none of them needed to
publish a JSON payload.

## Decision

1. **`paho-mqtt` is adopted as the MQTT client**, for the host-side wire
   harness. It is the Eclipse Foundation's reference Python client, it is
   dual-licensed **EPL-2.0 OR BSD-3-Clause** — both OSI-approved, and the
   dual grant lets a downstream recipient take the permissive limb — and it
   has **no required transitive dependencies**.
2. **It is a development dependency and never a runtime one.** Firmware
   publishes; nothing in the shipped Python package needs to speak MQTT. It
   sits in the `dev` group, and the harness imports it lazily inside functions
   rather than at module scope, so the runtime package loads without it. A
   runtime import is a review failure. This mirrors the conformance gate's
   validator dependency, and the two are deliberately the same shape.
3. **The harness is broker-agnostic and depends on no broker-specific
   behaviour.** It targets any broker reachable at a configured address. CI
   runs Eclipse Mosquitto because it is the reference implementation of the
   seam protocol, not because the harness requires it, and a harness that
   would fail against EMQX, NanoMQ or VerneMQ is a defective harness rather
   than a configuration detail.
4. **The broker is an external prerequisite, declared like any other.** The
   wire cookbook is collected only when a broker is reachable, and is skipped
   with a stated reason otherwise, so a contributor with no broker still runs
   the rest of the suite and is told precisely what they did not run. A
   silently-skipped test is worse than an absent one.
5. **This record adds a constraint and waives none.** The house-stack record
   requires a record before review; this is that record.

## Consequences

- The milestone's second assertion becomes reachable, and the class of defect
  named in Context becomes detectable rather than merely unlikely.
- Accepted cost: a second dependency outside the blessed set, carried for
  tests. The friction of writing this record is the mechanism working.
- Accepted cost: the full suite now has an external prerequisite. That is
  house-normal — apothecary's own suite requires the `openscad` CLI on `PATH`
  and browser binaries for its end-to-end tests — but it does mean "run the
  tests" is no longer a single self-contained command on a bare checkout, and
  clause 4 exists so the difference is announced rather than discovered.
- Obligation created: the lazy-import boundary in clause 2 has to hold as the
  harness grows, and clause 3's broker-agnosticism is a claim nothing
  currently tests, since CI runs exactly one broker. It is enforced by review
  until a second broker is worth the CI minutes.
- Two out-of-set dependencies now exist, both for the same underlying reason:
  a project whose seam is a wire protocol needs protocol tooling that a
  web-application stack never does. That is an observation about the blessed
  set's shape, not a complaint, and it is recorded here so a third instance is
  recognizable as a pattern rather than argued from scratch.

## Alternatives considered

1. **`amqtt`, a combined pure-Python broker and client.** Genuinely
   attractive: it would make the wire test run everywhere with no external
   prerequisite, which is a real property that clause 4 gives up. It lost on
   dependency surface. Eleven transitive packages, several substantial and
   none blessed, is a large permanent addition to buy a convenience in one
   test path — and it imports a second implementation of the very protocol the
   seam is defined in, which is a strange thing for a project whose premise is
   that the protocol has many independent implementations to take on as a
   dependency rather than as an engine.
2. **`aiomqtt`.** An async wrapper over `paho-mqtt`, so it inherits the same
   client and adds an asynchronous interface. It lost because the harness has
   no concurrency requirement, and an async interface would push `asyncio`
   into documentation examples that are executed as tests, where it costs
   legibility for a reader and buys nothing.
3. **Shell out to `mosquitto_pub` and `mosquitto_sub`.** It lost because it
   trades a declared, license-checkable dependency for an undeclared binary
   prerequisite that no manifest records and no license gate sees.
4. **Skip the wire test and rely on the in-process fixture.** It lost on
   honesty. The fixture cannot catch the failures in Context, and the
   milestone's assertion would be reported green on evidence that does not
   support it.
5. **Write a minimal MQTT client.** It lost on the seam-and-engines ordering
   rule, and it fails the project's own premise: a protocol chosen because it
   has many independent implementations does not need one more, written by the
   party who benefits least from maintaining it.
6. **Petition to add an MQTT client to the org blessed set.** It lost on
   scope. One project needing protocol tooling is not evidence the house stack
   is short something; the corpus's standard is that a second project asking
   the same question is the signal to promote a clause.

## Revision triggers

- A second QM project adopts an MQTT client, which by the corpus's standard
  makes this an org-level question.
- Something in the shipped package needs to publish or subscribe, which
  invalidates clause 2's premise that firmware is the only publisher.
- `paho-mqtt` is abandoned, or its dual grant narrows such that neither limb
  satisfies the open-license criterion.
- The harness is found to depend on broker-specific behaviour, which means
  clause 3 has failed and either the harness or the claim needs correcting.
- A third out-of-set dependency arrives for the same protocol-tooling reason,
  which turns the pattern noted in Consequences into something the org should
  decide rather than each project rediscovering.

## Amendments

*None.*
