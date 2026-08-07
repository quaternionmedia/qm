# ADR-XXXX — Object Storage Seam

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-07 |
| **Pends on** | Nothing — ready for ratification. The decision stands on its own; only its implementation is outstanding. |
| **Principle** | P3 — replaceability is the risk strategy |

## Context

Rendered video is uploaded to Google Cloud Storage and served to clients
through time-limited signed URLs. The integration goes through Google's own
Python SDK: `google.cloud.storage`, a `storage.Client`, a bucket handle, and
`blob.generate_signed_url`.

The SDK is Apache-2.0, so the license report passes it without comment. That
is not the problem. The problem is the shape: `google.cloud.storage` is an
interface with exactly one implementation, so every call through it is a call
that only one vendor can answer. Applying the seams record's replaceability
test — could this component be replaced by a from-scratch implementation of
the seam protocol alone, without changes on our side? — the current answer is
no. Replacing the provider means rewriting our code.

The surface is small. Object storage is reached from one module of roughly
forty lines, doing two things: upload a rendered file, and mint a signed
download URL. Both have direct equivalents in the S3 API, which the seams
record already names among protocols with multiple independent
implementations. Google Cloud Storage itself exposes an S3-compatible
interface, so speaking S3 does not require changing providers — it decouples
the two questions.

## Decision

1. **The object-storage seam is the S3 API.** Alfred reaches object storage
   through an S3 client speaking the S3 protocol, and through no
   provider-specific SDK.

2. **The current integration is non-compliant and is recorded as such**, in
   the constitution-adoption record's table alongside the project's other
   known conflicts. This record decides the target; it does not claim the
   target has been reached.

3. **No exception is sought.** The seams record provides for a project-level
   exception record when a component is reachable only through a
   single-implementation API. That mechanism is for a component with no
   protocol-shaped alternative. This one has an obvious alternative, on a
   protocol the org record already blesses, over a forty-line surface. Asking
   for an exception would be asking permission to keep something nobody
   intends to keep.

4. **The provider choice is deliberately separated from the protocol
   choice.** Adopting the S3 seam does not decide whether Google Cloud Storage
   remains the provider. Once the seam is S3, that becomes a routine operational
   decision — a configuration change, not a redesign — which is the entire
   point of the doctrine.

5. **The remaining sovereignty exposure is named rather than implied.** An S3
   seam makes the provider replaceable. It does not make a hosted service
   ownable-offline, which P1 asks for and which no protocol choice can
   deliver. Whether a self-hosted S3 implementation should back this in a
   deployed instance is a separate decision, not settled here.

## Consequences

- Provider replacement becomes a credentials-and-endpoint change instead of a
  code change, and the risk that a pricing, policy, or availability decision
  by one vendor forces engineering work is removed.
- The application gains the ability to run against a local S3 implementation
  in development and test, which the vendor SDK does not permit without
  reaching the real service.
- Cost accepted: signed-URL generation and credential handling differ enough
  between the SDK and an S3 client that this is a real port rather than an
  import swap, even at forty lines.
- Cost accepted: an S3 seam is a lowest-common-denominator interface, and any
  provider-specific capability adopted later would reopen this decision. None
  is in use today.
- §5 stands: after this lands, object storage is replaceable but still
  remote. That is an improvement, not a completion, and the record says so
  rather than letting the seam imply more sovereignty than it delivers.

## Alternatives considered

1. **Keep the vendor SDK and file a seams exception record.** Rejected: an
   exception documents a risk that cannot presently be avoided. This one can
   be avoided cheaply, on a blessed protocol. Filing an exception here would
   convert a small port into a permanent recorded carve-out, and the seams
   record warns specifically that an exception documents risk without waiving
   doctrine for the next decision.
2. **Write an internal storage abstraction and keep the SDK behind it.**
   Rejected on the org record's own reasoning: an adapter QM writes is a seam
   QM maintains forever, whereas a protocol seam is maintained by the
   ecosystem. It would also leave the code untestable without the real
   service, which is one of the concrete costs being paid now.
3. **Move to a self-hosted object store in the same decision.** Rejected: it
   bundles a protocol decision that is cheap and clear with a deployment
   decision that is neither. The protocol change is what makes the deployment
   change routine later, so doing it first is strictly ordered, not merely
   convenient.
4. **Serve rendered files directly from the application** and drop object
   storage. Rejected: it moves large-file delivery into the control plane,
   which the control-plane record forbids, and trades a replaceability
   problem for a scaling one.

## Revision triggers

- The S3 client replaces the vendor SDK — this record's implementation gap
  closes and the adoption record's corresponding row clears.
- A capability is required that the S3 API cannot express — the seam choice
  itself is back in question, not just the provider.
- A self-hosted object store is proposed for a deployed instance — §5's open
  question becomes a decision.
- The S3 API stops satisfying the multiple-independent-implementations test
  the seams record requires — unlikely, and exactly the event that would
  invalidate this record's premise.

## Amendments

*None.*
