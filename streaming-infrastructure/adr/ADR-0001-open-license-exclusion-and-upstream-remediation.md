# ADR-0001 — Open-License Exclusion and Upstream-Contribution Remediation

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06-09 |
| **Scope** | Constitutional — governs all other ADRs in this project |

## Context

This project (the `qmstream` control plane and the surrounding streaming infrastructure) operates under the Quaternion Media philosophy: open-source maintainers first, consultants second; infrastructure that is completely self-owned and operable offline indefinitely.

A component whose license permits the licensor to withdraw, re-price, or re-platform it is a clause in someone else's contract embedded in our stack. The industry supplies regular reminders — most recently MinIO, whose community edition was progressively stripped through 2025 and archived in February 2026 in favor of a ~$96k/yr commercial product. Notably, MinIO's final releases were open (AGPL); it was *governance*, not license, that failed. Both must therefore be addressed: this ADR fixes the license criterion and the response to license changes; governance risk is handled by the seam architecture and the risk register in the design plan.

Several popular components in this problem domain are open source but carry proprietary dependencies in their common deployment paths (a proprietary browser embedded in a capture pipeline; closed GPU runtimes and model compilers behind "hardware-accelerated" defaults). A rule that ignores deployment-path dependencies would be compliance theater.

## Decision

### 1. Exclusion rule

Every software component in the deployed runtime path MUST carry a license approved by the Open Source Initiative (OSI) or recognized as free by the FSF. This applies to:

- Applications and services
- Libraries and language-level dependencies, transitive included (as surfaced by SBOM tooling)
- Kernel modules and userspace drivers required at runtime
- Container base images
- ML model weights and the toolchains required to produce or run them
- Fonts, player chrome, and all frontend assets (vendored, never CDN-loaded)

**Explicitly acceptable:** copyleft licenses (GPL, AGPL, LGPL, MPL). Copyleft is open. AGPL network obligations are compatible with — and aligned with — the QM model; they are handled contractually in client deployments, not avoided technically.

**Explicitly excluded:** proprietary licenses; "source-available" licenses including BSL/BUSL, SSPL, Elastic License 2.0, Commons Clause, Fair Source, and PolyForm; any license carrying field-of-use, user-count, or competition restrictions; "open-weights" model licenses with non-commercial or acceptable-use restrictions; freeware and gratis-but-closed binaries.

There are no waivers and no opt-ins. A capability that cannot be had compliantly is had via §3 or not at all.

### 2. Relicense protocol

When an adopted component relicenses out of compliance:

1. The deployed version is immediately frozen (digest-pinned). Prior versions remain under their original license and stay compliant.
2. A freeze is a tourniquet, not a treatment — a frozen component receives no patches. A migration-or-fork ADR MUST be ratified within **90 days** of the relicense event.
3. The event and disposition are recorded as an amendment to the affected component's ADR.

### 3. Remediation by upstream contribution

When a needed capability exists only in a non-open product, or an open component lacks it, the response is **not** adoption of the non-open product and **not** a private workaround. The response is a **PR to the closest part of the stack where the capability properly belongs, in the language and conventions most acceptable to that community.**

- **Subsidiarity:** the capability goes to the lowest layer that should own it — a protocol feature to the media router, a detection feature to the NVR, orchestration logic to our own control plane. "Closest" is judged by where that layer's maintainers would expect it, not by which language we prefer.
- **Their language, their idiom:** contributions are written in the target project's language, style, and test conventions, even when that is not our house stack. The Python preference governs what *we* build, not what we contribute.
- **Carrying mechanism:** while a PR is in review, the patch is carried on a **public branch of a public fork** under the QM GitHub org, applied at image-build time. No private patches. The fork is archived when the PR merges.
- **Upstream-dead or upstream-rejected:** the fork is promoted to a maintained public QM project, or — if the logic is genuinely seam logic — implemented in the control plane.
- **Sponsorship channel:** where a maintainer accepts sponsorship, contribution may be paired with sponsorship through the existing QM program, particularly for review bandwidth on our PRs.

### 4. Enforcement

- A **license manifest** lives in the infrastructure repo. CI generates an SBOM (Syft, Apache-2.0) for every image and fails the build on any license outside the allowlist.
- The allowlist encodes the OSI-approved list; additions require an amendment to this ADR.
- A quarterly scheduled job re-scans pinned images and upstream repositories for license-file changes, relicense announcements, and archive status, opening an issue on any hit.

### 5. Scope boundary

The rule's floor is **userspace software plus kernel modules**. CPU microcode, device firmware, and BIOS/UEFI are out of scope — not because they don't matter, but because no bootable x86 stance satisfies the rule, and an unenforceable constitution is worse than an honest boundary. Hardware purchasing preference (coreboot-capable platforms, mainline-kernel drivers) is encouraged but not mandated here.

External network services (certificate authorities, package registries) are not licensed components; their availability risk is governed by the deployment ADR (offline mirrors, internal CA).

## Consequences

### Baseline component audit

The audit applied at adoption time to every component selected in the design plan:

| Component / path | License posture | Disposition |
|---|---|---|
| MediaMTX, MediaCMS, Frigate (core), Jitsi Meet (Prosody/Jicofo/JVB), Galène, FFmpeg (GPL-clean build), OBS, hls.js, PostgreSQL, Caddy, step-ca, coturn, SeaweedFS, Garage, faster-whisper + Whisper weights (MIT), OpenVINO, VAAPI / intel-media-driver, Syft, restic, k3s, Harbor, Podman | OSI-approved throughout | **Included** |
| Jibri (Jitsi's broadcast bridge, as documented) | Google Chrome stable — a proprietary binary — at the core of its capture path | **Excluded as shipped.** §3 remediation, if the capability is ever genuinely needed: contribute documented, tested Chromium support upstream to jitsi/jibri (Kotlin, their idiom). Multi-party composition meanwhile uses OBS-composition or WHIP-direct (see design plan). |
| TensorRT detector path | Closed runtime, proprietary kernel module | **Excluded.** Detection is OpenVINO on open drivers. |
| Coral Edge TPU path | Open runtime, closed model compiler | **Excluded** — a detector whose models we cannot compile is not owned. |
| NVENC encode | Proprietary kernel module | **Excluded.** Encode is CPU x264/x265 (GPL) or VAAPI on open Intel drivers. |
| Frigate+ subscription models | Proprietary, cloud-trained weights | **Excluded.** Bundled open models only. |
| FFmpeg `--enable-nonfree` builds (e.g. libfdk-aac) | Definitionally non-free | **Excluded.** Builds are GPL-clean; AAC via the native encoder or stream copy. |
| Docker Desktop | Proprietary | Not in the deployed path (Linux servers: Engine or Podman). Noted for workstation policy only. |

### Costs accepted

- **Performance ceiling:** CPU/VAAPI encode and OpenVINO inference trail their proprietary counterparts. Accepted: at this project's scale the delta is hardware money, not a bottleneck, and the gap closes with each Intel generation.
- **Contribution latency:** the PR-first path is slower than adopting a stopgap. Accepted deliberately — it converts our gaps into commons improvements, which is the QM business model expressed as engineering policy.
- **Carrying cost:** public fork branches require rebase discipline. Mitigated by keeping patches minimal and PR-shaped from the first commit.

## Alternatives considered

1. **Proprietary components as documented, conscious opt-ins** — rejected: every opt-in is a future migration on someone else's terms, and the terms change.
2. **Per-case waivers with a register** — rejected: a waiver register is an opt-in list with paperwork. §3 exists precisely so a compliant response to a capability gap always exists.
3. **Copyleft-only or permissive-only restriction** — rejected in both directions: *openness* is the constitutional criterion; copyleft-vs-permissive is a per-component fit question.
4. **Extending scope to firmware/BIOS** — rejected as unenforceable (§5); revisit if the coreboot ecosystem reaches the project's hardware.

## Revision triggers

- A §2 relicense event fires on any adopted component (starts the 90-day clock).
- A carried fork branch exceeds **two quarters** without upstream movement — forces the promote-or-drop decision.
- The OSI allowlist materially changes.
- Project scale grows to where CPU-encode cost materially exceeds open-driver hardware alternatives (re-examine encode hardware then; the exclusion rule itself is not in question).

## Amendments

*None.*
