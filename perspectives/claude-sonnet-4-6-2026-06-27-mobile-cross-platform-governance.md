# Perspective — Where the Constitution's Server-Infra Assumptions Didn't Transfer, 2026-06-27

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Sonnet 4.6 (Anthropic), the drafting assistant for `qmetronome` — the org's first mobile/cross-platform-device project |
| **Role of this document** | A narrow, single-topic perspective (not a corpus audit): two places the constitution's enforcement mechanisms assumed a server-infrastructure project and didn't transfer, observed by building against them rather than by inspection, plus a proposal scoped to what's actually missing |

## 1. Standing and scope

This is deliberately not a Fable-5-style full corpus review. I drafted one
project, not the constitution, and I'm annotating where that project's actual
dependency graph hit the edge of two enforcement mechanisms — the open-
license exclusion record's remediation path and the house stack's
client-mandated-stack carve-out. Both gaps were found by building, not by
reading the constitution in the abstract: I only noticed the remediation-path
gap when I went to write qmetronome's ADR-0001-equivalent and discovered
there was no compliant disposition to write down for a real dependency the
project cannot ship without.

Evidence classes follow the convention Fable 5 established in this
directory: **E1** primary source read this cycle, **E2** multiple
independent secondary sources, **E3** single secondary source, **E4**
inference from convention, **E5** prior training knowledge, unverified this
cycle.

## 2. The finding

### 2.1 The open-license exclusion record's §3 assumes an upstream exists

qmetronome drives the Glyph Matrix, proprietary LED hardware on Nothing
Phone (3) and Phone (4a) Pro, through `com.nothing.ketchum.*`, a closed-source
binary AAR (`glyph-matrix-sdk-2.0.aar`) from the
[GlyphMatrix-Developer-Kit](https://github.com/Nothing-Developer-Programme/GlyphMatrix-Developer-Kit)
(E1: I fetched the kit, integrated the AAR, and read its decompiled class
signatures directly to get accurate API surfaces before writing against
them). The vendor publishes a compiled Java/Kotlin API and a manifest-
permission contract; it does not publish the wire protocol. There is no
independent or open reimplementation (E1: I looked for one as part of normal
integration work, found none, and the kit's own README offers no alternative
path).

ADR-0001 §3 gives exactly one compliant response to a capability gap: a PR
"to the closest part of the stack where the capability properly belongs."
That presupposes a part of the stack — an upstream open project — to send
the PR to. Here there isn't one; the gap is a single vendor's undocumented
hardware control surface, not a missing feature in an otherwise-open
component. ADR-0001's own Jibri/Chrome disposition is the closest precedent
in the corpus, and the difference is exactly what makes it not transfer: the
streaming project's Chrome dependency was *substitutable* (OBS/WHIP
composition, at the cost of one strategy, not the product). Nothing
comparable exists here — there is no qmetronome without Glyph Matrix support,
so "exclude the capability" is not a live response, only "exclude the
project."

What I did instead, documented as a project-level Proposed ADR rather than a
silent dependency line (`adr/DRAFT-glyph-matrix-sdk-dependency.md` in
qmetronome): isolate the closed dependency behind a checkable import
boundary (`com.nothing.ketchum.*` confined to two files, verified by grep —
E1, I ran it), so the rest of the app survives the vendor's disappearance
unmodified. This is the seams doctrine (P3), applied to a hardware vendor
instead of a network protocol — which is itself worth noting: P3 already
contains the right structural answer, the gap is narrower than "the doctrine
doesn't apply." It's that ADR-0001's disposition menu currently has two
outcomes — Included or Excluded-with-remediation — and no slot for "excluded
from the no-waivers rule's *spirit* of avoidability, included because the
capability is irreducible, mitigated by isolation rather than by waiver."
(Confidence: high that the gap exists as described; medium-high that
isolation is the right-shaped mitigant, since this is one project's instance
rather than a pattern proven across several.)

### 2.2 The house stack's carve-out is named for clients, not platforms

P5 carves out client-mandated stacks explicitly; it has no equivalent
language for *platform*-mandated ones. Android application development has
no Python-native path to a real APK touching Compose, a vendor AIDL service,
and `MidiDeviceService` registration (E1: this is simply what building the
app required — Kotlin against the Android SDK, no alternative toolchain
considered viable). The reasoning P5 already uses for client contracts
applies identically: house preference governs what *we* build when there's a
choice; something external decides when there isn't. The carve-out's
*shape* is right; its *name* assumes the external decider is always a
contract. A platform is also an external decider. (Confidence: high — this
is a naming/scope gap, not a disagreement with the underlying principle.)

## 3. Proposal

Not a record — this is exactly the kind of input a perspective should
surface and a human should weigh, per the corpus's own process. Scoped
narrowly to what's actually missing, not a request to rewrite either
principle:

1. **Recognize "client/device application" as a distinct project class**
   alongside infrastructure projects, with its own ADR-0001-equivalent
   template addressing distribution surface (app stores, sideloading) and
   closed hardware/platform SDKs, in place of — not in addition to — the
   SBOM/digest-pinning/offline-mirror apparatus built for server runtimes
   QM operates end-to-end. qmetronome is one instance; I'd wait for a second
   before generalizing the template further than "a slot exists."
2. **Add a third disposition to the open-license exclusion record's menu**
   for closed hardware-vendor SDKs gating an irreducible physical capability:
   *isolated, named, and bounded* — conditions being (a) no open alternative
   exists at the protocol level, (b) the capability is not substitutable
   without abandoning the project's purpose, (c) the dependency is confined
   to a checkable import boundary, enforced in CI the same way the SBOM gate
   enforces the exclusion rule itself. This is additive to §3, not a
   replacement — §3 remains the right answer whenever an upstream exists.
3. **Generalize P5's carve-out language** from "client-mandated" to
   "client- or platform-mandated stacks," with the same house-preference-
   governs-what-we-build-not-what-we're-forced-to-build logic already
   ratified.

## 4. What I'd watch — falsifiable, with confidence

1. **The isolation disposition (§3.2) will get its first real stress test
   if/when Nothing Technology Limited changes the Glyph Matrix SDK's terms
   or discontinues it** — qmetronome's `adr/DRAFT-glyph-matrix-sdk-
   dependency.md` names this as a revision trigger and predicts the migration
   cost is contained to two files. That's checkable when it happens.
   (Confidence: medium that it happens within a few years for any single
   small hardware vendor; high that the isolation boundary holds if it does.)
2. **A second mobile/cross-platform QM project will either confirm this
   perspective's gaps as a pattern or reveal them as specific to closed
   hardware integration rather than mobile development generally** — e.g. a
   project with no proprietary hardware dependency might find the house-stack
   gap (§2.2) but not the license-exclusion gap (§2.1). I'd weight the
   proposal in §3.1 down if that's what happens, since one project isn't
   enough evidence for a whole new class. (Confidence: low on which way it
   resolves — this is genuinely the open question, not a prediction I have a
   strong prior on.)
3. **The grep-based import-boundary check, once wired into CI, will be the
   actual enforcement that matters more than this document** — perspectives
   are non-binding by design; the lint that fails a build is not. I'd treat
   the CI gate's existence (or absence) a year from now as the real signal
   of whether this proposal was adopted in spirit, regardless of whether any
   record was formally amended. (Confidence: high that this is the right
   thing to watch, independent of which way the org decides.)

## 5. Closing position

The constitution's enforcement mechanisms were extracted from one project's
observed reality (streaming infrastructure), which the corpus is honest about
elsewhere (Fable 5's perspective, §2.1: the seams doctrine "fired twice
before it was even written"). The same honesty suggests the mechanisms
should be expected to need a second data point before they're load-bearing
for a different *kind* of project, not just a different instance of the same
kind. This document is that second data point's first report, not a verdict.

— Peter Kagstrom, drafted with Claude Sonnet 4.6, 2026-06-27
