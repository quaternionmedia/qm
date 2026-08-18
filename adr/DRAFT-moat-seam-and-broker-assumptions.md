# ADR-XXXX — The moat seam, and preparing for a broker change nobody has specified

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-17 |
| **Pends on** | The chart being deployed once, and the ACL-namespace decision the kickoff handoff records as blocked on a human |

## Context

frizzle does not deploy its broker. moat does. The two repositories move on
separate schedules, which makes the interesting failure neither a bug in
frizzle nor a bug in moat, but a change in one that the other did not expect.

The seams record asks that a record selecting a third-party component name the
protocol it is reached over and answer the replaceability test. The
dependency-disposition record does that for the MQTT client library. This one
covers the *deployment* — the broker moat runs — which is a different seam with
a different failure mode and no library to swap.

The whole coupling is a socket and a configuration. frizzle calls nothing in
moat; moat calls nothing in frizzle. That is worth stating because it bounds
what can break.

Two configurations already exist and already disagree: `docker/mosquitto.conf`,
which frizzle develops against, and the draft wrapper chart bound for
`moat:charts/mosquitto/`. The chart is unverified inference — written by
reading moat's `whoami` and `home-assistant` idiom, never templated against
the cluster.

## Decision

**§1. The seam is MQTT and a configuration, and nothing else.** No API, no
shared library, no coupling either way beyond the wire. `src/frizzle/broker.py`
is the only module importing the client. Replacing the broker costs frizzle
nothing, because frizzle speaks MQTT rather than Mosquitto; replacing the
client library is a rewrite of one file against an unchanged protocol.

**§2. The assumptions frizzle makes about the broker are enumerated, not
discovered.** They are: it is reachable; it accepts frizzle's CONNECT; it
permits a `qm/#` subscription **and delivers on it**; it accepts publishes to
every `qm/` domain; it honours QoS 1; it retains `cfg/` for late joiners; it
delivers only subscribed topics; it has a measurable payload ceiling; and it
either does or does not hold a session across a reconnect.

**§3. Each is checkable in one command.** `frizzle broker-check` probes them
and states, per assumption, what frizzle relies on, what the broker did, and
what the difference costs the bus. It exits non-zero when frizzle cannot work
against that broker and says the fault is in the transport. It is written to be
read by someone who owns moat and not frizzle.

**§4. The likely changes are configuration, not code.** `BrokerConfig` carries
TLS (`tls`, `tls_ca_file`, `tls_insecure`) and session continuity
(`client_id`, `persistent_session`) as well as credentials. The chart turns on
auth, ACLs and persistence, and terminates TLS somewhere; meeting any of those
with a rebuild would be the wrong day to be editing `broker.py`.

**§5. The known deltas, read off the two configurations.**

| Assumption | dev broker | moat chart | Consequence |
|---|---|---|---|
| Authentication | anonymous | `allow_anonymous false` + password file | frizzle can be given credentials; nothing decides where they come from |
| Authorisation | none | `acl_file` | frizzle subscribes `qm/#`, the broadest filter on the bus |
| Persistence | `false` | `true` | with no client id, every reconnect is a new session |
| TLS | none | Traefik for websockets; 8883 a Phase 3 question | expressible; untested against a real certificate |
| Payload ceiling | 100 000 | broker default | measured by the payload recipe, never assumed |

**§6. The ACL is singled out, because it fails quietly.** An ACL granting
`qm/frizzle/#` and withholding the rest of `qm/#` is the plausible half-measure:
it looks like least privilege and reads as correct. The broker accepts the
subscription and delivers nothing from other projects. frizzle journals its own
traffic, reports itself healthy, and the bus quietly has no memory of anyone
else.

The probe therefore tests the wildcard by publishing to **another project's**
subtree. Measured both ways against a broker configured that way: probing
frizzle's own subtree is delivered and passes; probing another project's is
silent and fails. The probe target is the whole difference between catching
this and certifying it.

## Consequences

- A broker change that would have arrived as a recipe failing in the middle now
  arrives as a named assumption with a stated cost. That is the entire claim;
  it does not prevent any change.
- Verified against a broker configured the way the chart says — auth on, a
  password file, an ACL granting only `qm/frizzle/#`. Without credentials the
  probe reports the auth failure; with them it reports the silent ACL, which is
  invisible to every other check frizzle has.
- Persistence and client identity now have to be decided together. Turning on
  `persistent_session` without a stable `client_id` asks the broker to keep a
  session nobody claims, which is worse than neither, so both default off and
  the probe says so rather than choosing.
- The probe is an inspection and must stay one. It cleans up after itself,
  including the retained `cfg/` message its own publish test produces — an
  inspection with a side effect is not an inspection, and a stale retained
  probe is exactly what makes a later diagnosis wrong.
- Everything here describes a broker read from a file. The chart has never been
  deployed, so the deltas are predictions until it has been.

## Alternatives considered

1. **Wait for the chart to be deployed, then adapt.** The obvious order, and it
   loses because the adaptation would be written under time pressure, against a
   symptom rather than a cause, on the day the bus stops journaling. The
   amqtt episode is the rehearsal: a non-conformant broker produced a bare
   `KeyError` in a recipe, pointing at the wrong file, and the broker was at
   fault.

2. **Assert the assumptions in the recipes.** They already exercise most of
   them, and that is the problem: a recipe failing says a recipe failed. The
   diagnosis has to be separable from the demonstration, and readable by
   someone who owns the broker and has never read frizzle's source.

3. **Have moat publish a contract frizzle validates against.** Cleaner in
   principle, and it loses because it is a second coupling — a document that
   can itself go stale, in a repository frizzle does not control, to describe a
   broker frizzle can simply ask.

4. **Pin the broker version and forbid configuration drift.** It loses because
   the drift is the point: auth, ACLs and TLS are things moat *should* turn on,
   and a seam that only works while the other side stands still is not a seam.

## Revision triggers

- The chart is deployed for the first time, at which point every delta in §5
  becomes an observation rather than a prediction.
- The ACL-namespace question resolves — whether Frigate and Home Assistant
  share the QM namespace decides what `qm/#` even contains.
- Native TLS on 8883 moves from a Phase 3 question to a decision.
- frizzle gains a credential source, which is currently undecided.
- Home-automation traffic starts bridging into `qm/moat/...`, making the
  wildcard subscription's contents a moat concern rather than a frizzle one.
- A broker change reaches production that `broker-check` did not name, which
  means an assumption is missing from §2.

## Amendments

*None.*
