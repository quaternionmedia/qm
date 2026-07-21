# ADR-XXXX — QM Constitution Adoption Scope for Apothecary

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-20 |
| **Pends on** | Org-level ratification of the QM constitution records themselves — every record in the adopted corpus is still filed `DRAFT-*` at the pinned commit, so nothing is formally `Accepted` for this project to adopt yet. This ADR fixes *this project's* disposition against that corpus regardless, so a future reader has one place to look rather than re-deriving it once org ratification lands. |

## Context

Apothecary vendors the org's constitution as a submodule at `governance/qm`, on
this project's dedicated branch `project/apothecary`. Apothecary is a
self-hosted Python toolkit (Pydantic scene models compiled to OpenSCAD and
JSCAD, a Click CLI, and a FastAPI service exposing a Three.js-based STL
viewer) plus a curated library of printable parts under `parts/`. It has no
container image, no database, and no deployment pipeline of its own today —
it runs as a `uv`-managed local tool or a locally-started FastAPI server, and
its only external runtime dependency of consequence is the `openscad` CLI
binary, invoked via subprocess and expected on `PATH`.

Apothecary is closer in shape to DataFactorio's disposition than to the
reference streaming-infrastructure instance: a non-container, non-database,
single-service Python project. It differs from DataFactorio in one structural
way worth naming up front: it renders the *same* scene graph through **two**
independent target engines — the `openscad` CLI (native `.scad` → geometry/STL)
and a hand-rolled JSCAD-module renderer (`apothecary/jscad.py`, for
OpenJSCAD-compatible consumers) — which makes the seams record's
replaceability test concretely visible in this project's own architecture
rather than only in its third-party dependencies.

## Decision

1. **Decision-record discipline — adopted in full, in effect starting with
   this ADR.** This project's `adr/` directory (forked from
   `project-seed/adr/`), its Draft → Proposed → Accepted lifecycle, and its
   squash/append-only rules govern from here forward. The ADR-lint CI job
   (`.github/workflows/adr-lint.yml`, copied verbatim from
   `project-seed/ci/adr-lint.yml`) enforces the drafting-vocabulary rule on
   every push and PR.

2. **Open-license exclusion — adopted, with two named gaps and one
   pre-existing repo-hygiene gap surfaced by the baseline audit below.**
   Every Python and npm dependency in the runtime path clears the OSI bar
   (baseline audit below). Two items do not cleanly clear the *record's*
   full text, distinct from the license-identity question:
   - §1 requires frontend assets to be "vendored, never CDN-loaded."
     `templates/viewer.html.j2` loads Three.js (MIT) via a jsDelivr CDN
     import map (`https://cdn.jsdelivr.net/npm/three@0.160.0/...`). The
     *license* is compliant; the *delivery mechanism* is not — the viewer
     does not work offline and depends on a third party staying up. Flagged
     as a gap to remediate (vendor the pinned Three.js build and
     `OrbitControls`/`STLLoader` addons into the served static assets),
     not adopted as a carve-out.
   - The project's own package metadata (`pyproject.toml`) declares no
     `license` field and the repository ships no `LICENSE` file, despite
     `README.md` asserting "MIT License. See LICENSE for details." and
     displaying an MIT badge. `pip-licenses` accordingly reports
     `apothecary` itself as `UNKNOWN` (excluded from the enforcement scan
     below for that reason — the gate audits dependencies, not the
     project's own unresolved disposition). This is a legal/authorship
     decision — who the copyright holder is stated as — not something
     this ADR decides by drafting it; it is named here as a gap for human
     disposition, and the same gap exists in sibling project
     `datafactorio` as of this writing, so it is worth a resolution that
     covers both rather than a one-off fix.
   - §4 enforcement is wired via the dependency-manifest path (this project
     ships no container image): `.github/workflows/license-check.yml` runs
     `pip-licenses` against the locked dependency set on every push/PR,
     failing on anything outside an explicit OSI/FSF-cleared allowlist, and
     uploads the generated report as a build artifact. This is the "generated,
     never hand-compiled" enforcement §4 requires, wired in this same round
     rather than deferred.

3. **House stack — adopted, no carve-out.** FastAPI, Pydantic, and Click are
   exactly the org's blessed Python stack; Jinja2 (also listed) renders the
   viewer template and the `.scad`/`.jscad` output templates. The frontend
   (`templates/viewer.html.j2`) is single-file HTML/JS, consistent with P5's
   stated complement — modulo the CDN-vendoring gap named in §2, which is a
   delivery-mechanism defect in that single file, not a stack deviation.

4. **Seams on standard protocols — adopted, and this project is a clean
   instance of it in its own architecture, not just in vendor selection.**
   The `.scad` text format (OpenSCAD CLI) and the OpenJSCAD module format
   (`apothecary/jscad.py`) are two independently-implemented target engines
   driven from the same Pydantic `Scene`/`OpenSCADObject` graph — concretely,
   the replaceability test the seams record asks for: either rendering path
   can be dropped or swapped without touching the scene model. The
   `openscad` binary itself is an external seam (subprocess + stable CLI/file
   contract), not a linked library, so it can be swapped for another
   OpenSCAD-compatible implementation without a code change.

5. **Build the seam, buy the engines — adopted, and names the actual engine.**
   Apothecary's own control plane is the Pydantic scene graph, the CLI, and
   the FastAPI service; the bought engine is OpenSCAD itself (the CSG kernel
   and STL exporter) via its CLI, plus Three.js in the browser for STL
   rendering (once vendored per §2). Nothing here is written that OpenSCAD or
   Three.js should properly own.

6. **Contribution and sponsorship policy — adopted mechanically, currently
   inactive.** No dependency is locally patched at build time (baseline audit
   below); nothing to register in `governance/qm/registers/carried-patches.md`
   today.

7. **Public by default (handbook policy) — adopted, already the case.** This
   repository is public on GitHub (`github.com/quaternionmedia/apothecary`)
   with a public issue tracker; the MIT-license *intent* is stated in
   `README.md` even though the machine-readable disposition is the open gap
   named in §2.

## Consequences

- A baseline component audit (required by the open-license record at
  adoption), compiled by running `pip-licenses` against the locked
  environment (`uv sync --locked --dev`) and reading `package.json` — the
  same tooling now wired as this project's own §4 enforcement, not a
  hand-compiled one-off list:

  | Dependency (runtime) | License | Notes |
  |---|---|---|
  | fastapi, pydantic, pydantic_core | MIT | web framework + validation |
  | starlette, uvicorn, httpcore, idna | BSD-3-Clause | ASGI stack |
  | Jinja2 | BSD License | templates (`.scad`/`.jscad`/viewer HTML) |
  | MarkupSafe | BSD-3-Clause | Jinja2 dependency |
  | click | BSD-3-Clause | CLI |
  | anyio, annotated-doc, charset-normalizer, typing-inspection, urllib3 | MIT | transitive |
  | typing_extensions | PSF-2.0 | transitive |
  | playwright, pyee | Apache-2.0 / MIT License | browser automation (E2E; also see dev table) |
  | `@jscad/web` (npm, viewer-only asset, not imported by the Python package) | MIT | OpenJSCAD.org viewer bundle |

  | Dependency (dev-only, never shipped) | License |
  |---|---|
  | pytest, pytest-cov, black, pre_commit, ruff, PyYAML, h11, pluggy, python-slugify | MIT / MIT License |
  | pytest-asyncio, coverage, pytest-playwright, requests | Apache-2.0 / Apache Software License |
  | pytest-base-url, certifi, pathspec | MPL-2.0 |
  | httpx, Pygments, colorama, nodeenv | BSD License |
  | filelock | Unlicense |
  | distlib | Python Software Foundation License |

  Every dependency (runtime and dev) clears the OSI-approved bar; no
  proprietary or source-available component is in the dependency tree. The
  external `openscad` binary (GPL-2.0-or-later, invoked via subprocess, never
  linked or vendored) is explicitly acceptable under the exclusion rule's
  copyleft clause and is out of scope for the Python dependency-manifest gate
  by construction (it is not a Python or npm package).
- Two named gaps from §2 are accepted as open follow-ups, not silently
  resolved by this ADR: vendoring Three.js, and giving `apothecary` (and
  `datafactorio`) an actual `LICENSE` file plus a `license` field in
  `pyproject.toml` consistent with the README's existing MIT claim.
- No carried-patch register entry is needed today (§6).
- This ADR is the natural place to update if/when Apothecary gains a
  container image (making the SBOM-per-image enforcement path live instead
  of the dependency-manifest path), or takes on a patched dependency
  (revisiting §6).

## Alternatives considered

1. **Treat DataFactorio's or the streaming-infrastructure project's ADR-0001
   as sufficient and skip an Apothecary-specific one** — rejected: neither
   audits this project's actual dependency tree or its two-renderer
   architecture; P6 ("decisions are documented or they didn't happen")
   requires this project's own audit to exist here.
2. **Fold the CDN-vendoring gap into the enforcement mechanism as a
   suppressed exception** — rejected: the open-license record allows no
   waivers or opt-ins; the gap is named and left open rather than
   technically silenced.
3. **Treat the missing `LICENSE` file as out of scope for a governance
   ADR** — rejected: the gap was surfaced *by* doing the license audit this
   record requires, and P6 argues for recording it here rather than letting
   an audit artifact quietly disappear once this ADR is filed.
4. **Fail CI on the `apothecary` package's own `UNKNOWN` license disposition
   until §2's gap is fixed** — rejected for this round: it would block every
   build on a naming/legal decision that isn't this ADR's to make
   unilaterally; `--ignore-packages apothecary` scopes the gate to actual
   dependencies while the gap stays visible in this document instead of
   silently passing.

## Revision triggers

- Any org record in the pinned corpus is ratified (`Accepted`, numbered
  `QM-NNNN`) — re-check this ADR's dispositions still match the ratified
  text.
- Three.js is vendored (closes the §2 CDN gap) or a `LICENSE`
  file/`pyproject.toml` license field is added (closes the §2 metadata gap)
  — both should land as dated amendments here, not silent fixes.
- Apothecary gains a container image or deployment pipeline — the
  "dependency-manifest, not SBOM" disposition in §2 should be re-examined.
- The `governance/qm` submodule pin is bumped — re-verify this ADR's
  dispositions still match the new pinned text.

## Amendments

*None.*
