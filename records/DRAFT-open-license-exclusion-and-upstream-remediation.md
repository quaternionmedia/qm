# QM-XXXX — Open-License Exclusion and Upstream-Contribution Remediation

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-09 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P1 — ownership is the deliverable; P2 — commons-first economics |

## Context

A component whose license permits the licensor to withdraw, re-price, or
re-platform it is a clause in someone else's contract embedded in our stack.
The industry supplies regular reminders — most recently MinIO, archived in
February 2026 after its community edition was progressively stripped in favor
of a ~$96k/yr commercial product. Notably its final releases were open
(AGPL): governance failed where license did not. Both risks need answers;
this record fixes the license criterion and the response to license change.
Governance risk is addressed structurally by the seams doctrine and each
project's risk register.

Nominally open components also carry proprietary dependencies in common
deployment paths (embedded proprietary browsers, closed GPU runtimes and
model compilers). A rule blind to deployment-path dependencies is compliance
theater.

## Decision

1. **Exclusion rule.** Every software component in any QM deployed runtime
   path carries an OSI-approved or FSF-free license: applications, libraries
   (transitive, SBOM-surfaced), kernel modules and drivers, base images,
   model weights and their toolchains, and all frontend assets (vendored,
   never CDN-loaded). Copyleft is explicitly acceptable and contractually
   handled, never technically avoided. Source-available regimes (BSL/BUSL,
   SSPL, Elastic 2.0, Commons Clause, Fair Source, PolyForm), field-of-use or
   user-count restrictions, restricted "open-weights," and freeware are
   excluded. **No waivers, no opt-ins.**
2. **Relicense protocol.** On a non-compliant relicense of an adopted
   component: freeze at the last compliant version (digest-pinned) and ratify
   a migration-or-fork record within **90 days**. The freeze is a tourniquet,
   not a treatment.
3. **Remediation by upstream contribution.** A capability gap is closed by a
   PR to the closest layer of the stack where it belongs, in that community's
   language and idiom — never by adopting a closed product, never by a
   private workaround. Subsidiarity decides "closest"; house preference
   governs what we build, not what we contribute. Pending patches are carried
   on public branches of public QM forks, applied at build time, registered
   in the org carried-patch register, and archived on merge. Upstream-dead or
   rejected: promote the fork to a maintained public QM project, or implement
   in the project's control plane if genuinely seam logic. Sponsorship may
   accompany contribution, particularly for review bandwidth.
4. **Enforcement.** Every project CI generates a machine-readable license
   report and fails the build on any license outside the encoded OSI
   allowlist, along the path matching its runtime shape: an SBOM per image
   for container and server runtimes, or a dependency-manifest report per
   package ecosystem for everything else (illustrative tooling, not a
   binding list — `com.github.jk1.dependency-license-report` for Gradle,
   `license-checker` for npm, `pip-licenses` for Python, `cargo-license`
   for Rust). Either path is generated, never hand-compiled, and is paired
   with a quarterly scan that watches pinned upstreams for license-file
   changes and archive status. Allowlist changes are amendments to this
   record.
5. **Scope boundary.** The floor is userspace plus kernel modules. Microcode,
   firmware, and BIOS/UEFI are out of scope — no bootable x86 stance
   satisfies the rule, and an unenforceable constitution is worse than an
   honest boundary. Coreboot-capable purchasing is encouraged, not mandated.

## Consequences

- Projects perform a baseline component audit at adoption and record
  dispositions in their instance records (the streaming project's ADR-0001 is
  the reference instance).
- Performance ceilings from open-driver-only paths are accepted as hardware
  cost, not sovereignty cost.
- Contribution latency is accepted deliberately: gaps become commons
  improvements — the business model expressed as engineering policy.

## Alternatives considered

1. **Documented proprietary opt-ins** — rejected: each is a future migration
   on someone else's terms.
2. **Waiver register** — rejected: an opt-in list with paperwork; §3 ensures
   a compliant response always exists.
3. **Copyleft-only or permissive-only** — rejected both ways: openness is the
   criterion; copyleft-vs-permissive is per-component fit.

## Revision triggers

- Any §2 relicense event (starts the 90-day clock).
- A carried patch exceeds two quarters without upstream movement
  (promote-or-drop).
- Material change to the OSI allowlist.

## Amendments

*None.*
