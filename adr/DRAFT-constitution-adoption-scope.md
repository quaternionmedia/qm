# ADR-XXXX — QM Constitution Adoption Scope for factorio-server

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-04 |
| **Pends on** | Org-level ratification of the QM constitution records themselves (as with the other two sibling projects' adoption ADRs); additionally, two items inside this ADR are themselves left open rather than asserted — see §2 and §3 below and the baseline audit's "needs verification" rows. |

## Context

factorio-server vendors the org's constitution as a submodule at
`governance/qm`, on this project's dedicated branch `project/factorio-server`.
This project is a **self-hosted ops/deployment repo**: a `docker-compose.yml`
running the community-maintained `factoriotools/factorio:stable-rootless`
image, a `Makefile` wrapping day-to-day operations (start/stop/backup/restore/
security-check/etc.), and host-level ZeroTier networking binding the exposed
ports to a private overlay IP rather than the public internet. There is no
application code here in the sense the other two sibling projects have — this
repo *is* the control plane the org record's "build the seam, buy the
engines" doctrine describes, almost exactly as written. Of the three sibling
projects, this one is closest in shape to the corpus's reference instance
(streaming-infrastructure): a self-hosted service with a container image and
declarative ops.

factorio-server has two siblings sharing this constitution and a
`qm-factorio.code-workspace` dev layout: **factorio-sysops** (a Factorio mod
whose natural home for multiplayer testing is the dedicated server this repo
runs) and **datafactorio** (an out-of-game dashboard that could optionally be
deployed alongside the dedicated server, though nothing here requires it).
Each is a separate repository; this repo depends on neither at the source
level — it hosts a vanilla-plus-mods Factorio server regardless of whether
either sibling is in play.

## Decision

1. **Decision-record discipline — adopted in full, in effect starting with
   this ADR.** This project's `adr/` directory, its Draft → Proposed →
   Accepted lifecycle, and its squash/append-only rules govern from here
   forward.
2. **Open-license exclusion — adopted for everything this repo authors and
   operates; one component named as a conscious, out-of-scope dependency
   rather than silently ignored, one left genuinely open.**
   - The Factorio dedicated-server binary itself, inside the
     `factoriotools/factorio:stable-rootless` image, is proprietary
     (commercially licensed by Wube Software) — named explicitly, the same
     disposition qmetronome gave the Android OS and factorio-sysops gives the
     Factorio client: the platform being operated is not a candidate for the
     exclusion rule or its §3 remediation path any more than an OS kernel
     would be. The wrapping Docker image project (`factoriotools/factorio`)
     is itself open (MIT).
   - **Genuinely undecided, not decided by stealth:** ZeroTier's exact license
     posture for the pieces this repo actually touches (the host-installed
     `zerotier-cli`/`zerotier-one` client vs. the hosted ZeroTier Central
     coordination service this repo's README has admins authorize devices
     through) has not been verified against the open-license record's
     OSI/FSF bar as part of drafting this ADR — flagged `Pends on` rather
     than asserted compliant or non-compliant. §3's baseline audit records
     this as a row needing verification, not a pass.
   - No other proprietary component is knowingly in this repo's operated
     path.
3. **House stack — a third possible instance of the platform/tooling-mandated
   carve-out, flagged Proposed rather than asserted.** This repo has no
   Python in it at all — it's Makefile, bash (inside Make recipes), and YAML
   (docker-compose). Unlike factorio-sysops's Lua (mandated by a game engine's
   loader, no alternative exists) or qmetronome's Kotlin (mandated by
   Android's toolchain), Make/bash/Compose for *ops glue* is a genuine choice
   among viable alternatives — a Python/Click-based CLI wrapping the same
   `docker compose` calls is buildable and would fit the house stack directly.
   This ADR does not assert a carve-out here; it names the mismatch and
   leaves the disposition open, `Pends on` a decision about whether to
   rewrite the Makefile in the house stack or add "ops/infra glue" as a
   recognized carve-out category. Recorded as Proposed rather than picked
   silently, per the decision-record discipline's own rule.
4. **Seams on standard protocols — adopted, and a strong direct fit.** The
   Factorio game protocol (UDP 34197) and RCON (TCP 27015) are the vendor's
   own standard interfaces, not something this repo invents; ZeroTier is
   itself a replaceable network-overlay seam (WireGuard or Tailscale are
   drop-in alternatives per the replaceability test) — named as a revision
   trigger below rather than treated as permanent.
5. **Build the seam, buy the engines — adopted, and this repo is close to a
   textbook instance.** The "engine" bought is the Factorio dedicated server
   itself (packaged by the `factoriotools/factorio` image); the seam is this
   repo's Makefile + docker-compose.yml, deliberately boring, holding the
   only state that matters operationally (`.env`, `data/`). No control-plane
   code beyond that exists here, matching the doctrine's stated shape more
   directly than either sibling project.
6. **Systems over heroics (P8) — already the operating model, worth
   recording rather than just cross-referencing.** `make backup`/`make
   restore`/`make security-check`/`make network-info` are already declarative,
   scriptable operations recreatable from version control — no SSH-freeform
   administration is documented as the supported path. This repo is the
   concrete instance P8 names as belonging to "each project's deployment-
   and-provenance record."
7. **Contribution and sponsorship policy — adopted mechanically, currently
   inactive.** No dependency is locally patched at build time; nothing to
   register in `governance/qm/registers/carried-patches.md` today.
8. **Public by default (handbook policy) — adopted, already the case.** This
   repository is public on GitHub (`quaternionmedia/factorio-server`). The
   `.env` file (ZeroTier network ID, RCON password file path) is the named,
   justified exception (credentials/operational secrets), consistent with
   the policy's own carve-outs — `.env` is gitignored; only `.env.template`
   is committed.

## Consequences

- Two items are left open rather than resolved by this ADR: ZeroTier's
  license posture (§2) and whether Make/bash/Compose ops tooling needs its
  own house-stack carve-out or should migrate to the house stack (§3). Both
  are named `Pends on` items rather than silently decided, per the
  decision-record discipline's explicit rule against deciding open questions
  by stealth.
- Baseline component audit, compiled by reading `docker-compose.yml` and
  `.env.template` rather than a generated SBOM — Phase 3 of the rollout
  wires an SBOM-per-image gate to make this mechanically verifiable:

  | Component | License posture | Disposition |
  |---|---|---|
  | `factoriotools/factorio:stable-rootless` (wrapper image) | MIT | Included |
  | Factorio dedicated server binary (inside the image) | Proprietary (Wube) | Named, out of scope — the platform being operated, not authored (§2) |
  | Docker Engine / Compose | Apache-2.0 | Included |
  | ZeroTier client (`zerotier-one`, host-installed) | **Needs verification** | Proposed / Pends on — not yet checked against the OSI/FSF bar (§2) |
  | ZeroTier Central (hosted coordination service) | **Needs verification** | Proposed / Pends on — external network service, may fall under the record's "external network services... not licensed components" scope boundary, not yet confirmed (§2) |

- No carried-patch register entry is needed today (§7).
- This ADR is the natural place to update once the two `Pends on` items
  resolve, or if this repo ever adds a Python-based operational tool
  alongside (or instead of) the Makefile.

## Alternatives considered

1. **Assert ZeroTier is compliant without checking, since it's widely known
   as "open source"** — rejected: ZeroTier's licensing has genuinely changed
   over the product's history and differs between the client and the hosted
   controller service; asserting compliance without the check would be
   exactly the kind of silent stretching this ADR's siblings (qmetronome,
   factorio-sysops) were careful to avoid for their own platform questions.
2. **Assert Make/bash is fine under house stack without discussion, since
   it's "just glue"** — rejected: the house-stack record's carve-out language
   is specifically for *client- or platform-mandated* stacks; ops glue with a
   viable Python alternative doesn't obviously qualify, and picking silently
   here would set an unreviewed precedent for every future ops-shaped QM
   project.
3. **Treat this repo as out of scope for the constitution entirely, since
   it's "just infra"** — rejected: it is the org's clearest instance yet of
   "build the seam, buy the engines" and P8 in practice; excluding it would
   discard the best-fitting example in the corpus rather than record it.

## Revision triggers

- Any org record in the pinned corpus is ratified (`Accepted`, numbered
  `QM-NNNN`) — re-check this ADR's dispositions still match the ratified
  text.
- ZeroTier's license posture is verified (§2) — resolves that `Pends on` item
  either direction.
- A decision is made on the Make/bash-vs-house-stack question (§3) — resolves
  that `Pends on` item; if the answer is "carve-out," propose generalizing the
  house-stack record's carve-out language to cover ops/infra tooling
  explicitly (it currently only names client- and platform-mandated stacks).
- ZeroTier's own licensing or governance changes (relicense, acquisition,
  central-service deprecation) — triggers the seams doctrine's replaceability
  test against WireGuard/Tailscale.
- The `governance/qm` submodule pin is bumped — re-verify this ADR's
  dispositions still match the new pinned text.

## Amendments

*None.*
