# ADR-XXXX — Glyph Matrix SDK Dependency

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-27 |
| **Pends on** | Org-level disposition for closed hardware-vendor SDKs gating a specific physical capability (see `docs/governance-perspective.md` and the corresponding `qm` perspective) |

## Context

qmetronome's entire reason to exist is driving the Glyph Matrix, a proprietary
LED hardware feature on Nothing Phone (3) and Phone (4a) Pro. The only way to
address that hardware is `com.nothing.ketchum.*`, shipped as a closed-source
binary, `glyph-matrix-sdk-2.0.aar`, in the
[GlyphMatrix-Developer-Kit](https://github.com/Nothing-Developer-Programme/GlyphMatrix-Developer-Kit)
under the Glyph SDK End User License Agreement, that kit's `LICENSE.md`. The
agreement licenses use of the SDK for integrating it in an application,
forbids redistributing it except as the agreement authorises, and forbids
commercial use without the vendor's written permission.
The vendor has published a Java/Kotlin API surface and a manifest-permission
contract; it has not published the underlying wire/hardware protocol, and no
independent or open reimplementation exists.

The org's open-license exclusion record requires every runtime-path
component to carry an OSI/FSF-approved license, with no waivers, and provides
exactly one compliant response to a capability gap: upstream contribution
(§3) to "the closest layer of the stack where the capability belongs." That
mechanism presupposes an open project to contribute to. There isn't one here
— the gap is a single hardware vendor's undocumented control surface, not a
missing feature in an otherwise-open stack. The record's own Jibri/Chrome
precedent is the closest analog and the clearest illustration of why it
doesn't transfer cleanly: Jibri's Chrome dependency was *substitutable* (the
project routed around it with OBS/WHIP composition, at the cost of one
composition strategy). The Glyph Matrix SDK dependency is not substitutable
without forgoing the project's entire reason to exist.

## Decision

qmetronome depends on the closed `glyph-matrix-sdk-2.0.aar`, named and bounded
rather than hidden:

1. **Isolation as the mitigant.** Every import of `com.nothing.ketchum.*` is
   confined to `app/src/main/java/media/quaternion/qmetronome/glyph/` — verified
   by grep at the time of writing: exactly two files
   (`GlyphMatrixToyService.kt`, `MetronomeGlyphService.kt`). The tempo engine
   (`engine/`), MIDI clock handling (`midi/`), visualizer algorithms
   (`visualizers/`), and UI (`ui/`) import nothing from the closed SDK and
   would survive the vendor's disappearance, a relicense, or a competing
   open-hardware Glyph-equivalent appearing, unmodified.
2. **No alternative is adopted in its place.** This is not a "proprietary
   components as documented opt-ins" waiver (rejected pattern, per the org
   record) — there is no second vendor, no open substitute, and no feature
   reduction that preserves the product while dropping the dependency.
3. **The boundary is the enforcement mechanism**, in the same spirit as the
   org's SBOM gate: a CI check restricts `import com.nothing.ketchum` to
   files under `glyph/`, so a future change that lets the closed dependency
   leak into the engine/visualizer/UI layers fails CI rather than passing
   silently.
4. **The binary is fetched, not kept.** The project's repository does not
   hold the AAR. The build takes it from the Developer Kit at a pinned
   commit and refuses a file whose SHA-256 is not the one written in
   `app/build.gradle.kts`. The project redistributes nothing of the
   vendor's in source form, and a file changed upstream fails the build
   instead of entering it.
5. **The app's licence carries a linking permission.** The app is licensed
   GPL-3.0-or-later, which alone does not permit conveying it combined
   with a library under the vendor's agreement. Its licence carries the
   GPL's section 7 additional permission, SPDX
   `GPL-3.0-linking-exception`, with this SDK named. The permission is the
   app's licensors' and grants nothing in the SDK.

## Consequences

- The project carries a closed-source binary in its dependency tree,
  unconditionally and by design — a real, accepted departure from the org's
  no-waivers exclusion rule, not a theoretical one.
- The blast radius of that departure is small and checkable: two files, both
  thin glue between the engine's `BeatPhase`/`IntArray` output and the
  vendor's `GlyphMatrixManager.setMatrixFrame()` call. A vendor SDK breaking
  change costs a rewrite of `glyph/`, not the project.
- The app remains fully functional (tempo engine, MIDI sync, click audio, on
  screen matrix preview) with the Glyph Matrix feature entirely absent — the
  closed dependency is additive to a working open core, not load-bearing for
  it. This is the practical version of "ownable if the vendor disappears
  tomorrow": the app downgrades, it does not die.
- A checkout without the AAR needs the Developer Kit reachable for its
  first build. If the vendor removes the file or the kit, no fresh checkout
  builds until the address is moved or the dependency dropped.
- The agreement's text does not settle whether a published APK that
  contains the SDK is within its grant, and a commercial release needs the
  vendor's written permission. Neither is obtained by this record.
- No SBOM/digest-pinning/quarterly-scan apparatus exists yet for this
  dependency, because the existing tooling targets server images. A
  dependency-license report for the APK's bundled libraries (e.g. the Android
  Gradle Plugin's own license-report tooling, or a Syft run against the AAR)
  is a reasonable adaptation and is left as follow-up work, not asserted here
  as already done.

## Alternatives considered

1. **Don't build Glyph Matrix support** — rejected: this is the project's
   reason to exist, not a feature among several.
2. **Wait for/contribute an open reimplementation of the protocol** —
   rejected as not currently available: the vendor has not published the
   wire protocol, only a compiled SDK, so there is no upstream to contribute
   to. Revisit if that changes (see revision triggers).
3. **Treat this as a silent, undocumented exception** — rejected: the org's
   own discipline (`decisions-are-documented`, "decisions are documented or they didn't happen")
   is the reason this ADR exists instead of an unremarked Gradle dependency
   line.

## Revision triggers

- Nothing Technology Limited publishes the Glyph Matrix wire protocol or an
  open reference implementation appears — re-evaluate §3 remediation.
- The vendor relicenses the SDK, discontinues it, or it stops working on a
  new Nothing OS version — the isolation boundary in Decision §1 determines
  the actual migration cost; this ADR should be amended with the observed
  cost when/if that happens.
- The Developer Kit stops serving the pinned file, or the vendor replaces
  the agreement - Decision §4's address and the reading of the terms in
  Context are re-established against what the vendor publishes.
- The org ratifies a disposition for closed hardware-vendor SDKs (the pended
  input) — this ADR is rewritten (if still Proposed) or superseded (if
  Accepted) to align.
- The `glyph/`-only import boundary is violated and the CI check designed to
  catch that fails to catch it — the enforcement mechanism itself needs
  revisiting, not just the violation.

## Amendments

*None.*
