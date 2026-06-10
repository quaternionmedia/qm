# QM-XXXX — Seams on Standard Protocols

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-09 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P3 — replaceability is the risk strategy |

## Context

License compliance does not protect against abandonment, governance collapse,
or maintainer loss — the failure modes that actually retire components. The
structural defense is integration shape: if every third party is reachable
only through an interface with multiple independent implementations, any
component failure is a swap, not a redesign. Proprietary *protocols* lock in
deeper than proprietary code, because they survive an open license.

## Decision

1. Third-party components integrate with QM systems only through protocols
   and formats having **multiple independent implementations** — e.g.
   RTSP/RTMP/HLS/WHIP, S3, SQL, REST+JSON+OpenAPI, MQTT, SMTP/IMAP, ACME,
   XMPP, Matrix. The project record selecting a component names the seam
   protocol(s).
2. **The replaceability test**, applied at selection: *could this component
   be replaced by a from-scratch implementation of the seam protocol alone,
   without changes on our side of the seam?* If no, the seam is wrong.
3. A component reachable only through a single-implementation API requires an
   explicit exception record at project level — status Proposed, naming the
   exit plan and an expiry-style revision trigger — before adoption. The
   exception documents risk; it does not waive the doctrine for the next
   decision.
4. The doctrine governs *seams to third parties*. Internal libraries within a
   control plane (ORMs, workflow engines) are house-stack choices, not seams,
   and are governed by the house-stack record.

## Consequences

- Design reviews carry the replaceability test as a checklist item.
- Component swaps become routine maintenance; project risk registers can
  honestly claim "the architecture is the mitigation."
- Cost accepted: standard protocols occasionally lag a vendor's proprietary
  fast path (features, latency). The delta is paid knowingly or routed to
  upstream contribution per the open-license record.

## Alternatives considered

1. **Abstraction layers in our code instead of protocol seams** — rejected:
   an adapter we write is a seam we must maintain forever; a protocol seam is
   maintained by the ecosystem.
2. **Vendor-API integrations with contractual exit clauses** — rejected:
   contracts compensate for lock-in; they do not remove it.

## Revision triggers

- An approved-protocol candidate emerges or collapses (e.g., a protocol's
  second implementation dies).
- Two or more projects request the same single-implementation exception —
  the doctrine needs a clause, not repeated exceptions.

## Amendments

*None.*
