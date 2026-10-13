# ADR-XXXX — QM Constitution Adoption Scope for Apothecary

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-20 |
| **Pends on** | Org-level ratification of the QM constitution records themselves — every record in the adopted corpus is filed `DRAFT-*` at the pinned commit, so nothing is formally `Accepted` for this project to adopt. This record fixes *this project's* disposition against that corpus regardless, so a reader has one place to look rather than re-deriving it once org ratification lands. |
| **Checked against** | apothecary `77f75c8` (`build/governance`); the corpus at the pin (`project/apothecary`, `20e00bd`) and at `main` (`df1cb51`), whose records a pin bump brings |
| **Established by** | `uv tree --locked --no-dev` for the runtime closure, and each package's installed metadata and licence file; `apothecary/static/vendor/codemirror/packages.json` and three's `LICENSE` for the vendored libraries; each locked crate's `Cargo.toml` in the tools dir's vendored folder after `apothecary firmware install --rust-esp32`; the gridfinity submodule's `LICENSE`; the workflows as they stand in `.github/workflows/` |
| **Tools** | Drafted with Claude Code (Anthropic); the person who ratifies it is its contributor of record |

## Context

Apothecary vendors the org's constitution as a submodule at `governance/qm`,
on this project's dedicated branch `project/apothecary`. It is a
self-hosted Python toolkit -- Pydantic scene models compiled to OpenSCAD
and JSCAD, a Click command line, and a FastAPI server that serves one
viewer page on this machine -- plus a curated library of printable parts
under `parts/`. It drives programs it does not link: OpenSCAD renders,
arduino-cli, esptool, cargo and espflash build and flash boards, OrcaSlicer
slices, and git keeps a part's saved variants. It has no container image,
no database and no deployment pipeline; it runs as a `uv`-managed local
tool or a locally started server.

Apothecary is closer in shape to DataFactorio's disposition than to the
reference streaming-infrastructure instance: a non-container,
non-database, single-service Python project. It renders the *same* scene
graph through **two** independent target engines -- the `openscad` CLI
(native `.scad` → geometry/STL) and a JSCAD-module renderer
(`apothecary/jscad.py`, `apothecary render-jscad`, for OpenJSCAD-compatible
consumers) -- which makes the seams record's replaceability test visible in
this project's own architecture rather than only in its third-party
dependencies.

The project existed before it adopted the corpus, so
`decision-record-discipline` §5 asks for this record's substance to be a
table of every known conflict with an org record: the conflict, the record
it violates, what compliance would look like, and how the row is pinned.
A row records a conflict; it does not authorise it, create an exception
or soften the record it conflicts with.

## Decision

1. **Decision-record discipline — adopted in full.** This project's `adr/`
   directory (forked from `project-seed/adr/`), its Draft → Proposed →
   Accepted lifecycle, and its squash/append-only rules govern its
   records. The ADR-lint job (`.github/workflows/adr-lint.yml`, copied from
   `project-seed/ci/adr-lint.yml`) runs the lint from the submodule on
   every push to `main` and every pull request, and the index lists each
   draft by its whole title.

2. **Open-license exclusion — adopted, with the conflicts below
   enumerated.** The runtime closure is taken from `[project]
   dependencies` in `pyproject.toml` (`uv tree --locked --no-dev`); the
   `dev` and `preflight` groups -- the test runner, the linter, the browser
   tests, the local workflow runner -- are in no deployed runtime path, and
   open-license §5 puts them outside §1. The frontend assets are vendored
   (`apothecary/static/vendor/`), and the server's content security policy
   lets the page load from no other origin (the *Personal data stays on the
   device, by construction* record, §4). Every component, its licence and
   its disposition is in the component audit below. The gate that runs
   today is `.github/workflows/license-check.yml`: `pip-licenses` over the
   locked Python environment, against an allowlist, with the report kept as
   a build artifact; what it does not yet do is in the conflicts.

3. **House stack — adopted, with three conflicts enumerated.** FastAPI,
   Pydantic, Click, Jinja2 and pytest are the org's blessed Python stack.
   Where the project departs from the blessed set -- Rust in the
   repository, the viewer's shape, and `uv` in PDM's place -- the departure
   is a row below, not a carve-out.

4. **Seams on standard protocols — adopted.** The `.scad` text format
   (OpenSCAD's command line) and the OpenJSCAD module format
   (`apothecary/jscad.py`) are two target engines driven from the same
   `Scene`/`OpenSCADObject` graph: either rendering path can be dropped or
   swapped without touching the scene model. Every other engine is reached
   across a protocol seam its record names: boards over each toolchain's
   command line (*Firmware toolchain seam*), printers over the G-code line
   protocol (*G-code printer seam*), slicing over OrcaSlicer's command line
   and profile files (*Slicer seam*), the ring over rad's conformance
   vectors (*rad host integration for apothecary*).

5. **Build the seam, buy the engines — the control-plane instance.**
   - *What the seam owns:* the scene model and its compilation to SCAD and
     JSCAD; the parts library and the site hierarchy; the server, the
     command line and the viewer page with its anchors, panels and ring
     host; the census; the network guard; the task runners, the state
     folder and its records; the installers' policy (where a tool comes
     from, which version, which digest); and each seam's argv and output
     parsing.
   - *What it refuses to own, and who does:* the CSG kernel and STL export
     (OpenSCAD); compiling, linking and flashing (arduino-cli, esptool,
     cargo, espflash); slicing (OrcaSlicer); 3D drawing in the browser
     (three.js); code editing (CodeMirror); image decoding (Pillow); serial
     I/O (pyserial); a print queue, a camera on a print and a print farm
     (a print host, per the G-code record); the radial menu's contract
     (rad); version control (git).
   - *Size-smell thresholds,* each measured with `wc -l` at the commit a
     change lands on, and each, when crossed, `build-the-seam-buy-the-engines`'s
     ordering question asked of that part: the firmware seam, by its
     record's own trigger; `apothecary/firmware/gcode.py` past 2,000 lines;
     `apothecary/slicer/` past 4,000; `apothecary/api.py` past 4,000;
     `templates/fractal_viewer.html.j2` past 10,000; the shape finder's
     built-in (`apothecary/vision/plain.py`, pixel work an image library
     would own upstream) past 1,000. At apothecary `77f75c8` none is
     crossed.

6. **Contribution and sponsorship policy — adopted, with nothing to
   register.** No dependency is patched at build time: the installers fetch
   release archives and apply nothing, and the gridfinity submodule is
   unmodified (a saved variant of a gridfinity part is an overlay in the
   superproject, never an edit of the submodule). Nothing is in
   `registers/carried-patches.md` for this project.

7. **Public by default — adopted.** The repository is public on GitHub
   (`github.com/quaternionmedia/apothecary`) with a public issue tracker.
   It is MIT-licensed: `LICENSE`, `LICENSES/MIT.txt`, `REUSE.toml` (which
   annotates the vendored three.js and CodeMirror as MIT) and `license =
   "MIT"` in `pyproject.toml`; `reuse-lint.yml` holds every file to a
   declared licence.

8. **What the org records oblige this project to produce, walked.**

   | Obligation | Where it is | State |
   |---|---|---|
   | Baseline component audit | the component audit below | present |
   | Licence gates, cumulatively | `license-check.yml` (Python) | Python gated; C3 to C5 |
   | Service inventory | *Personal data stays on the device, by construction*, its service inventory | present; C7 |
   | Quarterly upstream scan | -- | absent; C6 |
   | Seam protocol named | each seam record, and §4 | present |
   | Control-plane instance record | §5, with the firmware seam's own trigger | present |
   | Risk register | the personal-data record's (privacy), and the governance risk register below | present |
   | Carried patches registered | §6 | none needed |

   The gates wired are `adr-lint.yml`, `submodule-check.yml` and
   `reuse-lint.yml` from the seed at the pin; `leak-check.yml` and
   `one-pr-check.yml` from the seed at `main`, run from copies of its
   scripts under `.github/qm-seed/` until the pin carries them; and
   `license-check.yml` and `pytest.yml` of the project's own.

## Conflicts

| # | Conflict | Record | What compliance looks like | How it is pinned |
|---|---|---|---|---|
| C1 | Pillow 12.3.0, in the runtime closure (it reads every picture: the shape finder, the gathering, a made piece's texture), declares `MIT-CMU`. Its licence file is the PIL licence, which SPDX names `MIT-CMU`, and that identifier is on neither the OSI nor the FSF list, so §1 excludes it as written. Its wheel also bundles native libraries (libjpeg-turbo, libpng, libtiff, libwebp, FreeType, HarfBuzz, lcms2, OpenJPEG, libavif with AOM and dav1d, Brotli, zlib, zstd, liblzma, libxcb and others), each under the licence its section of Pillow's `LICENSE` reproduces, which no gate reads | open-license §1, §4 | Pillow replaced by an image library whose licence and bundled libraries §1 admits, at its quality and speed for decoding JPEG and PNG, resizing and pixel access (the research `todo.md` links); or the organisation's settlement of `MIT-CMU`, which open-license's own `Pends on` names, admits it. Scope frozen: no second package reads pictures | `license-check.yml`'s typed allowlist names `MIT-CMU`, so the gate passes Pillow by an entry §4 does not let a project encode; no test fails when Pillow leaves |
| C2 | typing_extensions 4.15.0, pulled in by pydantic and fastapi, declares `PSF-2.0`, which is on neither list. Its licence file is the whole Python licence stack -- the history, PSF License Version 2, BeOpen, CNRI and CWI, with the documentation's code under 0BSD as well -- which SPDX names `Python-2.0`, OSI-approved and FSF-free | open-license §4 (its normalization entry is `main`'s text) | a normalization entry `PSF-2.0` → `Python-2.0` in a generated allowlist's normalization table, recorded with what was read (this row's reading of `typing_extensions-4.15.0.dist-info/licenses/LICENSE`) | `license-check.yml`'s typed allowlist names `PSF-2.0` |
| C3 | The licence gate's allowlist is typed into the workflow, not generated from SPDX's `osi_approved` ∪ `fsf_libre` with its provenance; it compares the raw strings packages declare (`BSD License`, `Apache Software License; BSD License`) without normalizing them to SPDX identifiers; and it admits identifiers §1 does not (`MIT-CMU`, `PSF-2.0`) while refusing ones §1 does (the LGPL family, among others) | open-license §4 (normalization and no local exception at the pin; the generated allowlist at `main`) | a generated allowlist file, committed with its source, criterion and date; each declaration normalized to SPDX before comparison, the deprecated fields read; an unresolvable declaration a failure; normalization entries made after reading a licence file (C2) | none; the workflow's `--allow-only` line is the evidence |
| C4 | The gate scans `uv sync --locked --dev`, the whole development environment, where this record takes the closure from `[project] dependencies` | open-license §5 (`main`'s scope boundary) | the report over the runtime closure as §2 states it, with the groups named in the workflow; over-reporting stays the fallback when the closure cannot be computed | none |
| C5 | Rust crates and vendored JavaScript are ungated: the crates `parts/esp32_blink/rust/Cargo.lock` names are compiled into an image flashed to a board, and `apothecary/static/vendor/` holds three.js and CodeMirror; the Python gate is the only one. Each declares a licence §1 admits (the component audit), and nothing generates or checks that | open-license §4, cumulative | a dependency-manifest report and gate for each: Cargo's lockfile (`cargo-license` or the corpus's own), and the vendored manifest (`codemirror/packages.json`, three's version), each against the generated allowlist. The trigger that ends the gap: a second Rust sketch, a crate or a vendored library whose licence the allowlist does not admit, or the corpus's own gate for Rust or JavaScript. Scope frozen: no second Rust sketch and no new vendored library before the gate | none |
| C6 | No quarterly upstream scan watches the pinned upstreams for a licence-file change or an archive | open-license §4 | a scheduled workflow over the pinned upstreams -- OpenSCAD, arduino-cli, esptool, espflash and Espressif's Xtensa toolchain, OrcaSlicer, three.js, CodeMirror, gridfinity-rebuilt-openscad, rad, and the locked PyPI and crates.io packages | none; no workflow in `.github/workflows/` has a `schedule:` |
| C7 | A service the installers reach is replaced by a one-line edit to a fixed list in the source (`TOOL_SOURCES`, `PACKAGE_INDEXES`, the installers' pins), reviewed as a change to the personal-data record, rather than by configuration: a setting naming where to fetch from is a door that record's §2 closes | open-license §6 | an org-level reading of §6 for install-time tool fetches under a network guard, which settles whether a reviewed source edit is the configuration change §6 asks for | `tests/test_stays_local.py`'s tool-fetch tests hold the list and its two callers |
| C8 | Rust is written in the repository with no org-level record adding it: two stub crates under `crates/` (a PyO3 core and a service, built by nothing and carried by no wheel) and the ESP32 sketch in Rust beside its Arduino one. Firmware for a microcontroller could be the platform carve-out, but Arduino's C++ builds for the same board | house-stack §2 | an org-level record adding Rust, with the blessed set's alternatives weighed, or the crates and the Rust sketch removed. Scope frozen: the crates stay stubs, and no Rust is built into what the wheel ships | the root `Cargo.toml`'s workspace comment; no test |
| C9 | The viewer is a long-lived interface -- state, addresses, panels, a ring, an editor -- written as one server-rendered template with ES modules, widget modules and vendored libraries, and no build step: neither a single-file visualization deliverable nor the frontend-application instance (mithril with a parcel build) | house-stack §1, §2 | an org-level record for this shape, or the viewer moved to the frontend-application instance. Scope frozen: no framework and no build step added before the record | none |
| C10 | Packaging and its lockfile are `uv` (`uv.lock`), with setuptools building the wheel, where the blessed set names PDM | house-stack §1 | PDM with its committed lockfile, or an org-level record for `uv` | none |

## Component audit

The runtime closure (`uv tree --locked --no-dev` at the commit named
above), each package's licence as declared and as its licence file reads:

| Component | Version | Declared | Licence file | Disposition |
|---|---|---|---|---|
| fastapi, annotated-doc, pydantic, pydantic-core, typing-inspection, anyio | as locked | `MIT` | MIT | admitted |
| annotated-types, h11 | 0.7.0, 0.16.0 | `MIT License` classifier; `MIT` | MIT | admitted |
| starlette, uvicorn, click, idna, markupsafe | as locked | `BSD-3-Clause` | BSD-3-Clause | admitted |
| jinja2 | 3.1.6 | `BSD License` classifier | BSD-3-Clause | admitted; normalized by reading (C3) |
| pyserial | 3.5 | `BSD`, no licence file in the wheel | BSD-3-Clause (its repository's `LICENSE.txt`) | admitted; normalized by reading (C3) |
| typing-extensions | 4.15.0 | `PSF-2.0` | the Python licence stack | C2 |
| pillow | 12.3.0 | `MIT-CMU` | the PIL licence, with its bundled libraries' | C1 |

Vendored in `apothecary/static/vendor/`, served from this origin:

| Component | Version | Licence | Disposition |
|---|---|---|---|
| three.js, with `OrbitControls`, `TransformControls`, `STLLoader` | 0.160.0 | MIT (`three/LICENSE`) | admitted; ungated (C5) |
| CodeMirror 6 and its dependencies, as `codemirror/packages.json` lists them | as listed, each with its integrity hash | MIT, each | admitted; ungated (C5) |

Compiled into a firmware image a person flashes: the crates
`parts/esp32_blink/rust/Cargo.lock` names. Each declares MIT, Apache-2.0,
ISC, or an expression with one of them -- `MIT OR Apache-2.0` and its
reorderings, `Unlicense OR MIT`, `Zlib OR Apache-2.0 OR MIT`, `Apache-2.0
OR BSL-1.0`, and `(MIT OR Apache-2.0) AND Unicode-3.0` -- so each passes §1
by an OSI-approved choice; a few use the deprecated `MIT/Apache-2.0` and
`Apache-2.0 / MIT` forms, which a normalizing gate reads as an `OR`. Ungated
(C5).

Read by the renderer: `parts/gridfinity/gridfinity-rebuilt-openscad`, a
submodule of SCAD the parts include, MIT by its `LICENSE`. Admitted.

Run, never linked, vendored or conveyed -- each fetched by the person's own
machine from its publisher at a pinned, checked version, or found on
`PATH`, and run as a separate process over its command line and files:

| Program | Licence | Reached by |
|---|---|---|
| OpenSCAD | GPL-2.0-or-later | the renderer; `apothecary openscad install` |
| arduino-cli | GPL-3.0 | the *Firmware toolchain seam* |
| esptool | GPL-2.0-or-later | the *Firmware toolchain seam* (found, not installed) |
| cargo, Espressif's Xtensa Rust, espflash | MIT OR Apache-2.0 | the *Firmware toolchain seam* |
| Espressif's GCC | GPL-3.0 with its runtime library exception | the *Firmware toolchain seam* (the linker) |
| OrcaSlicer | AGPL-3.0 | the *Slicer seam* |
| git | GPL-2.0-only | saved variants of a part |

The copyleft clause of §1 admits each, invoked rather than linked, so the
artifact the project distributes stays MIT. OrcaSlicer's licence adds a
network clause (§13) for a modified program offered over a network; the
binary is unmodified and the server listens on this machine alone, and
running it anywhere else is the slicer record's revision trigger.

## Governance risk register

What could withdraw, re-price or stop maintaining a selected component,
and the exit. The privacy risks are the personal-data record's.

| Component | Risk | What would show it | Exit |
|---|---|---|---|
| OpenSCAD development snapshots | the renderer installs a dated snapshot from `files.openscad.org`, a build that is not a release | the snapshot listing gone or stale | a source build at a commit (the installer's Linux arm64 path), or a release `openscad` on `PATH` |
| arduino-cli, esptool | each is one vendor's tool (Arduino, Espressif) | a relicense, an archive, a year with no release | the *Firmware toolchain seam*'s modules: another build tool is a module |
| Espressif's Xtensa Rust and espflash | the Xtensa target is Espressif's fork of the Rust compiler, not upstream Rust | the fork's releases stop, or lag the pinned versions | the Arduino module builds the same board; an upstream Xtensa target ends the fork |
| OrcaSlicer | a community fork, AGPL-3.0, with no single vendor behind it | a relicense, an archive, a year with no release | the *Slicer seam*'s modules: another slicer is a module |
| pyserial | the serial engine has had no release since 3.5 | an archive, or a Python release it breaks on | a stdlib engine behind the same `Transport` protocol on POSIX (the *G-code printer seam*'s trigger) |
| Pillow | C1; the only image library in the closure | C1's settlement, or the research's answer | the research `todo.md` links |
| three.js, CodeMirror | vendored copies at fixed versions, each maintained upstream by a small group | a relicense or archive upstream (C6 would see it) | the vendored copy keeps working; a replacement is a change to the page's modules |
| rad | the ring's contract is the organisation's own, a private package at `0.0.0` | rad's record not ratified, or its vectors changing | `apothecary/static/ring.js` is this project's implementation, held to rad's vectors (*rad host integration for apothecary*) |
| gridfinity-rebuilt-openscad | one maintainer's library, pinned as a submodule | an archive or a relicense upstream (C6) | the pinned commit keeps rendering; the parts that include it are the ones affected |

## Consequences

- The conflict table is this project's compliance surface. A row leaves
  it in the change that resolves it, and a conflict found is a row added;
  the project points at the table instead of claiming compliance it does
  not have.
- Each row's scope is frozen while it is open: no second package reads
  pictures (C1), no second Rust sketch or new vendored library lands
  before its gate (C5), the Rust crates stay stubs (C8), and the viewer
  takes no framework or build step (C9).
- The *Firmware toolchain seam* and *Slicer seam* records pend on this
  record's ratification for the copyleft disposition above, so both wait
  with it on the organisation's ratification of its own records.
- This record is the place to change if apothecary gains a container
  image (the SBOM-per-image path joins the dependency-manifest one), takes
  on a patched dependency (§6), or adds a component (the audit).

## Alternatives considered

1. **Treat DataFactorio's or the streaming-infrastructure project's
   ADR-0001 as sufficient and skip an Apothecary-specific one** — rejected:
   neither audits this project's dependency tree or its two-renderer
   architecture, and `decisions-are-documented` requires this project's own
   audit to exist here.
2. **Name the gaps in prose rather than a table** — rejected:
   `decision-record-discipline` §5 makes the table the compliance surface,
   and a gap described only in prose drifts from the code as the code
   changes, until a closed gap is still asserted as open.
3. **Remove Pillow and typing_extensions before adopting** — rejected:
   Pillow reads and resizes every picture the project takes in, and no
   alternative is known to cover its decoding, resizing and pixel access
   at its quality; typing_extensions comes with pydantic and fastapi, so
   removing it removes the web stack. Enumerating both, with what
   compliance looks like, is what §5 allows.
4. **Write a project-local Rust and JavaScript licence gate now** —
   rejected for the present: one Rust sketch's crates and two vendored
   libraries each declare a licence §1 admits, read from their manifests,
   and a gate written here would be a second copy of one the corpus's seed
   would carry. C5 stays open with the trigger that ends it.

## Revision triggers

- Any org record in the pinned corpus is ratified (`Accepted`, numbered
  `QM-NNNN`), or the `governance/qm` pin is bumped — the dispositions and
  the obligations walk in §8 are re-checked against that text.
- A component enters the runtime closure, the vendored libraries, a
  firmware sketch's lockfile or the programs run — its row in the audit,
  and a conflict row if §1 does not admit it.
- A conflict's compliance lands — the row leaves the table in the same
  change.
- C5's trigger: a second Rust sketch, a crate or vendored library whose
  licence the generated allowlist does not admit, or the corpus's own gate
  for Rust or JavaScript.
- The organisation settles `MIT-CMU` (open-license's `Pends on`) — C1
  follows it.
- A threshold in §5 is crossed — `build-the-seam-buy-the-engines`'s ordering
  question for that part.
- Apothecary gains a container image or a deployment pipeline — the
  SBOM-per-image path is added to §2.

## Amendments

*None.*
