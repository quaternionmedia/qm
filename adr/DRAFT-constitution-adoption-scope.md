# ADR-XXXX — QM Constitution Adoption Scope for DataFactorio

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-04 |
| **Pends on** | Org-level ratification of the QM constitution records themselves — every record in the adopted corpus is still filed `DRAFT-*` at the pinned commit, so nothing is formally `Accepted` for this project to adopt yet. This ADR fixes *this project's* disposition against that corpus regardless, so a future reader has one place to look rather than re-deriving it once org ratification lands. |

## Context

DataFactorio vendors the org's constitution as a submodule at `governance/qm`, on
this project's dedicated branch `project/datafactorio`. DataFactorio is a
self-hosted Python service (FastAPI + SQLModel-backed SQLite + a browser-rendered
graph visualization) with a CLI entry point (`datafactorio serve`, `sync`,
`quickstart`, …) and no container image or deployment pipeline of its own today —
it runs as a `uv tool install`ed binary on a user's machine, watching a directory
Factorio writes JSON exports into. It is closest in shape to the org corpus's
reference instance (a self-hosted server project), but is not identical to it: it
ships no Docker image, has no database beyond a local SQLite file, and its only
"deployment" is `uv tool install`.

DataFactorio has two sibling projects sharing this constitution and a
`qm-factorio.code-workspace` dev layout: **factorio-sysops** (a Factorio mod that
can optionally export an IT-infrastructure JSON snapshot DataFactorio's parser
can ingest — see `factorio-sysops/docs/DATAFACTORIO-INTEGRATION.md`) and
**factorio-server** (a Docker/ZeroTier-based dedicated Factorio server, a
candidate deployment target for this dashboard). Each is a separate repository
with its own history, CI, and release cadence; nothing here imports source from
the others. The relationship is intentionally a **seam, not a dependency**: a
file-based JSON contract in one direction (factorio-sysops → DataFactorio),
optional co-location in the other (DataFactorio → factorio-server).

## Decision

1. **Decision-record discipline — adopted in full, in effect starting with this
   ADR.** This project's `adr/` directory (forked from `project-seed/adr/`), its
   Draft → Proposed → Accepted lifecycle, and its squash/append-only rules govern
   from here forward.
2. **Open-license exclusion — adopted directly, no carve-out needed.** Every
   runtime dependency clears the OSI bar (baseline audit below); DataFactorio
   itself ships under MIT. Unlike qmetronome's or factorio-sysops's dispositions,
   nothing here needs scoping down — this is a clean confirming instance of the
   record as written for a server-shaped project, modulo §5 (no container image
   exists to SBOM yet).
3. **House stack — adopted, no carve-out.** FastAPI, SQLModel, Pydantic, and
   Click are exactly the org's blessed Python stack; this project is a direct
   instance of P5, not an exception to it. The frontend is single-file/modular
   JS and CSS in `src/datafactorio/static/`, consistent with P5's stated
   complement ("single-file HTML/JS for visualization deliverables") — note the
   README's description of the frontend as "D3.js" is aspirational/historical:
   no `d3` package appears in `package.json` or as a vendored/CDN script; the
   force-directed graph rendering is hand-rolled JS. Corrected here so the
   baseline audit reflects what's actually shipped, not the README's phrasing.
4. **Seams on standard protocols — adopted, and this is where the sibling
   relationship is named.** The concrete seam is the watched-directory JSON
   contract: `datafactorio sync` imports any JSON dropped in the watch
   directory, keyed by a `source` field (`GraphStorage.import_file()` does not
   reject unrecognized top-level keys). factorio-sysops's Tier-1 export
   (`"source": "sysadmin"`, `it_nodes`/`it_edges`/`it_metrics`) is a second
   producer against that same seam, not a source-level dependency — DataFactorio
   has no build-time or import-time reference to factorio-sysops, and works
   identically with it absent. This is P3 (seams on standard protocols) applied
   to composing sibling repos, not just third-party vendor risk, and is the
   mechanism that keeps "standalone" and "build off each other" simultaneously
   true.
5. **Build the seam, buy the engines — not applicable, stated rather than
   silently skipped.** This doctrine assumes a control-plane architecture
   orchestrating selected external engines (media routers, databases,
   transcoders) behind standard-protocol seams. DataFactorio's FastAPI process
   and its embedded SQLite file are not an orchestration layer over external
   engines in that sense — there is nothing here to "buy." If DataFactorio ever
   grows an orchestrated external dependency (e.g. a swapped-in Postgres, a
   message queue), that is new architecture warranting its own ADR, not a
   retrofit of this one.
6. **Contribution and sponsorship policy — adopted mechanically, currently
   inactive.** No dependency is locally patched at build time (§ baseline audit);
   nothing to register in `governance/qm/registers/carried-patches.md` today.
7. **Public by default (handbook policy) — adopted, already the case.** This
   repository is public on GitHub (`github.com/quaternionmedia/datafactorio`)
   with a public issue tracker and MIT license; no closed material exists here.

## Consequences

- No gap-closing carve-out was needed for this project (contrast factorio-sysops
  and factorio-server, both of which scope §3/§2 down for their shape) — worth
  recording as a second clean instance of the reference shape, alongside the
  streaming-infrastructure project, rather than only cataloguing where the
  corpus doesn't fit.
- A baseline component audit (required by the open-license record at adoption),
  compiled by reading `pyproject.toml` and `package.json` rather than a
  generated SBOM — §4 of the open-license record adopts tooling (Phase 3 of the
  rollout plan) to make this mechanically verifiable going forward:

  | Dependency | License | Notes |
  |---|---|---|
  | fastapi, uvicorn | MIT | web framework + ASGI server |
  | sqlmodel, pydantic | MIT | ORM / validation |
  | click | BSD-3-Clause | CLI |
  | httpx | BSD-3-Clause | HTTP client |
  | semver | BSD-3-Clause | version parsing |
  | networkx | BSD-3-Clause | graph algorithms |
  | numpy, scipy | BSD-3-Clause | numerics |
  | pytest + plugins (dev only) | MIT | never ships |
  | `@playwright/test` (dev only, npm) | Apache-2.0 | never ships |

  Every shipped dependency clears the OSI-approved bar; no proprietary or
  source-available component is in the runtime path.
- No carried-patch register entry is needed today (§6).
- This ADR is the natural place to update if/when DataFactorio adds a container
  image (making the SBOM-per-image enforcement path live), swaps SQLite for an
  orchestrated external database (revisiting §5), or takes on a patched
  dependency (revisiting §6).

## Alternatives considered

1. **Treat the reference (streaming-infrastructure) project's ADR-0001 as
   sufficient and skip a DataFactorio-specific one** — rejected: the reference
   project's baseline audit is about its own components (MediaMTX, Frigate,
   etc.), which says nothing about this project's actual dependency tree; P6
   ("decisions are documented or they didn't happen") requires this project's
   own audit to exist here, not be inferred by analogy.
2. **Describe the factorio-sysops/factorio-server relationship as a formal
   dependency in this ADR's Decision section** — rejected: it isn't one.
   DataFactorio has no import-time or build-time reference to either sibling;
   overstating the coupling would misrepresent what "standalone" means for this
   project and contradict §4's seam framing.
3. **Leave the README's "D3.js" description uncorrected here** — rejected: the
   baseline audit is required to reflect what's actually shipped; silently
   letting a stale description stand in the governance record while writing an
   accurate table next to it would be the exact kind of small inconsistency the
   decision-record discipline exists to catch.

## Revision triggers

- Any org record in the pinned corpus is ratified (`Accepted`, numbered
  `QM-NNNN`) — re-check this ADR's dispositions still match the ratified text.
- DataFactorio gains a container image or deployment pipeline — §2/§5's
  "no carve-out needed" disposition should be re-examined against the fuller
  reference-shape requirements (SBOM-per-image, offline mirrors) at that point.
- factorio-sysops's export format changes in a way that breaks the `source`-keyed
  JSON contract in §4.
- The `governance/qm` submodule pin is bumped — re-verify this ADR's dispositions
  still match the new pinned text.

## Amendments

*None.*
