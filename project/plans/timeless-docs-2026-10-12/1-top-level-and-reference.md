# Inventory: top-level and reference pages

Area 1 of `project/plans/timeless-docs-2026-10-12.md`. Read in full on `build/timeless-docs`
(c67725a): `README.md`, `QUICKSTART.md`, `CONTRIBUTING.md`, `AGENTS.md`, `project/todo.md`,
`docs/README.md`, every `docs/*.md`, `tests/e2e/README.md`, `parts/README.md`,
`parts/{boards,ender3,datum_core,gridfinity}/README.md` (the last is this repository's
own file beside the submodule, not upstream's), `crates/*/README.md`.
`check_timeless.py --all` reports nothing in this area; every row below is a reader's find.

## 1. Verdict

The area is in good shape against §1 and §3: the pages are already written in the
present tense, there is no shouting, and most passages need nothing. What remains is
of four kinds. **History in neutral words**, 36 of the 75 rows: the slicer page
opens on "the owner decided how on 2026-10-10 … this page says what was built";
firmware.md's `/firmware/status` fields are "Arduino's as they always were"; two pages
describe legacy data by its past ("a variant saved before its values were in its
text", "the print records kept before jobs"); fitting-a-part.md "was written against"
`datum`. **Time-relative words** ("today", "yet", "a planned item", "not built yet"),
concentrated in the two crate READMEs and README's platform list. **Stale statements**,
few and checkable: tests/e2e/README.md's list of modules with servers of their own
misses five; project/todo.md's list of hidden stubs misses the three `test` ones;
docs/README.md lists finished plans in the present-tense index; firmware.md cites three
records in `governance/qm/adr/` that the pinned qm commit does not hold. No count a command
computes appears in prose. **Structure** is the
bigger problem. A newcomer has one clear entry (README "Start here" → walkthrough 00),
but README then restates the install and first commands at length, so the page holds
two paths. The clone, install and test commands are in four places (README,
CONTRIBUTING, AGENTS, walkthrough 00), the OpenSCAD per-platform list in three
(README, CONTRIBUTING's summary, the installer's docstring). README's viewer bullet and
its long camera paragraph are viewer.md's and walkthrough 13's material. The SCAD
assignment grammar is told three times (viewer.md, parts-authoring.md twice).
fitting-a-part.md is a proposal ("Status: proposed") filed among the reference guides.
parts/gridfinity/README.md is in another voice and tells a reader to move a pinned
submodule. project/todo.md overlaps the cleanup triage plan. Missing: a reference page for
pictures and cameras (the photo path has no guide, only README's paragraph, walkthroughs
11 and 13, and plans), one for configuration (sixteen `APOTHECARY_*` variables in
code, twelve named across six pages, none listed in one place), and one for sites and
assemblies.

## 2. Passages, by file

Problem kinds: history, ornament, stale, duplicate, count. Home: inline, reference →
page, retrospective → area, delete. Line numbers are of c67725a.

### README.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 12-20 | "A local FastAPI server and one page: a three.js world that zooms…" | duplicate | reference → docs/viewer.md | One sentence: a local server and one page, a world that zooms through sites, assemblies and parts, with its rail and ring; link viewer.md. |
| 21-27 | "Each board pinned in the viewer has one Machine … polled once whatever shows it" | duplicate | reference → docs/firmware.md | Keep "sketches compiled and uploaded, a Marlin printer monitored, a part sliced and printed as a job"; the Machine's internals are firmware.md's. |
| 47-89 | "## Install … Python 3.11+ and uv … git clone --recurse-submodules" | duplicate | reference → walkthrough 00 (steps) and docs/openscad.md (to be made) | The fourth copy of clone, sync, check (walkthrough 00 §1, CONTRIBUTING, AGENTS). README keeps Start here; Install shrinks to prerequisites and a link. |
| 68-77 | "Linux x86_64: the night's AppImage … Windows x64: the night's portable zip" | duplicate | reference → docs/openscad.md (to be made) | Per-platform install is told here, in CONTRIBUTING 16-20 in brief, and in `openscad_installer.py`'s docstring. One page owns it. |
| 77 | "Windows on ARM is not supported yet; it is a planned item." | history | inline | "Windows on ARM: refused; `APOTHECARY_OPENSCAD` names an OpenSCAD to use." Checked: no plan or todo lists it; only a validation checklist's "One day". |
| 107-119 | "In the viewer, a picture is taken by a camera, a part of the site." | duplicate | reference → docs/pictures.md (to be made) | A ring-by-ring procedure, walkthrough 13's loop told again. README keeps one line and links walkthrough 13 and the new page. |
| 121-127 | "Pictures live in one folder: APOTHECARY_PICTURE_ROOT, or else the folder…" | duplicate | reference → docs/pictures.md (to be made) | True (checked `api.py` picture root, `routes/pictures.py` sorts by mtime, `menu.NEWEST`); it is reference detail, not a README fact. |

### QUICKSTART.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 1 | "The quickstart is README.md: install, first commands and troubleshooting." | duplicate | delete | A page whose only content is a pointer; nothing in the repository links it (checked with grep). Delete, unless the owner knows of outside links. |

### CONTRIBUTING.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 16-20 | "Rendering STLs needs OpenSCAD: … (on Linux x86_64, macOS and Windows x64 the published build…" | duplicate | reference → docs/openscad.md (to be made) | Keep the one contributor fact: with the snapshot installed, `--slow` also renders the parts 2021.01 cannot. Link the rest. |
| 72-78 | "The rules are in AGENTS.md. In short: …" | duplicate | inline | The same three rules as AGENTS.md 16-22 and 81-84. Acceptable as a pointer; keep the bullets to one line each, so the two cannot disagree. |

Checked and true, no row: the CI table against `.github/workflows/` (five workflows; `pytest.yml`'s lint,
walkthrough, `--slow` unit tests, wheel job and three browser shards with the walkthrough
diff), "Nothing else is a gate", and the walkthrough pages each test writes.

### AGENTS.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 34-38 | "it isn't the intended, tested experience; see … for what was actually verified" | history, ornament | inline, upstream | Seed text from qm's `project-seed`: "…degrade to one-line pointers; the IDE-integrated governance discovery record says what each IDE reads." Fix in the seed, then re-sync. |
| 40-41 | "<!-- … this seed only carries the governance-discovery part. -->" | stale | delete | A seed scaffold comment; the project's section is below it. Keep only if the seed's re-sync tooling looks for it (check the seed). |
| 59-72 | "uv sync … uv run apothecary test run … uv run apothecary serve --demo" | duplicate | inline | The third command list (README, CONTRIBUTING). Keep it here, it is the agent's one page, and make README and CONTRIBUTING the ones that shrink. |
| 68 | "uv run apothecary openscad install --latest" | duplicate | inline | `--latest` is the default (`cli/openscad.py`); every other page writes `openscad install`. Drop the flag so the pages read alike. |

### project/todo.md

A backlog is about the future by nature, and its items may say what waits on what. The
rows are the passages that tell the past or have gone stale. Structurally, "Open in this
repository" restates rows of `project/plans/cleanup-triage-2026-10-08.md`; one of the two
should be the list and the other link it.

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 17 | "Its three screenshots are of the pages as they were on 2026-09-20." | history | inline | Drop the sentence: the record is dated, and so are its pictures. |
| 23 | "Photo gathering becomes an optional extra (decided 2026-09-26)." | history | inline | Drop "(decided 2026-09-26)"; the heading already says the round is decided. |
| 44-46 | "The hidden command stubs (system, install, testrun, dev, inventory, submodules, photo look)…" | stale | inline | Misses `test setup-e2e`, `test validate-e2e`, `test run-e2e` (checked `cli/testing.py`). Name the mechanism: "the stubs `cli/retired.py` makes go one release after hiding". |
| 58-59 | "It guesses now; a person's word already wins." | history | inline | "It guesses; a person's word wins over a guess." |
| 60-61 | "today they live in the file handed to --answers" | history | inline | "they live in the file handed to `--answers`." |
| 73-74 | "The plain-language proposal (project/plans/proposals/light-language.md, in git history)" | history | inline | A pointer a reader cannot follow: name the commit (`git log --all -- project/plans/proposals/light-language.md` finds 7c63846 removing it). |

Checked and true, no row: the JSCAD deep imports (`jscad.py`; `tests/test_jscad_renderer.py` runs
only `node --check`), the wheel's `include = ["apothecary*"]`, Phases 6 and 7 open in the
pictures plan.

### docs/README.md (the index)

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 30 | "A part's SCAD edited where its source stood" | history | inline | "where its source stood" narrates the page before the editor (a read-only source view). "A part's SCAD edited in Selected's editor". The phrase is also in walkthrough 16 and its test (areas 2, 4). |
| 61-66 | "One screen … done"; "Consolidation … done" | history | inline (a *History* list in this file) | Finished plans leave the present-tense table for a dated *History* list, per the owner's decision; their still-true decisions go to viewer.md. |
| 67, 71-73 | "Cameras and clutter … in four phases"; "The loops through the page"; "A managed slicer"; "Onboarding…" | history | inline (the *History* list), owner confirms | They read as finished: cleanup triage marks the cameras phases *Done (#30)*; pages 13-16 hold the four loops; slicer.md and walkthrough 00 are the built results. Area 5 confirms each. |
| 74 | "the next phase written out" | — | inline | Live plan; stays. Listed so the History split is complete: part-iteration, pictures, photo-finders, timeless-docs stay live; the two spikes are dated research. |
| 93 | "On a fresh clone the folder is empty" | stale | inline | `docs/generated/` is git-ignored and untracked, so a fresh clone has no such folder: "Until generated, there is no such folder." |

Checked and true, no row: `kernel-reference` is a command (`cli/main.py`), the `docs` marker is on
`test_docs_fractal_viewer.py` and `test_docs_printer_monitor.py` only, the walkthrough table's titles
match each page's heading, and the crates are not built by CI.
Structure: the index is the right shape (walkthrough, guides, crates, plans, generated). When the
reference pages proposed below exist, the Guides table gains them; the plans table splits into live
plans and *History*.

### docs/viewer.md

The best page in the area: a reference of the page's controls as they are. Three history
passages and one duplicate.

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 195-204 | "A part's values are the top-level assignments in its SCAD … as OpenSCAD's customizer has them" | duplicate | reference → docs/parts-authoring.md | The grammar is told here, at parts-authoring 147-158 and again at 170-185. Keep the page's behaviour here; link the grammar. |
| 241 | "What is typed in the SCAD is drawn once it reads, as before." | history | inline | "as before" reads as an earlier version. "…is drawn once it reads (see [The SCAD editor](#the-scad-editor))." |
| 334-335 | "or, for a variant saved before its values were in its text, that it does not" | history | inline | "or, for a variant whose values are in its `.variant.json` and not its text, that a merge does not apply them until it is saved again." Checked `saved.py`'s `old` branch. |
| 348-350 | "one saved before its values were written into its text has them written in when it is read" | history | inline | "a variant whose values are not in its text has them written in when it is read." |

Checked and true, no row: the 300 ms check and render delays (`SCAD_CHECK_MS`,
`SCAD_RENDER_AFTER_CHECK_MS`), the ring's seating order (`menu.PLACEMENT`), the 50 mm snap
(`SNAP_INCREMENT`).

### docs/firmware.md

A long reference page in good order. History is confined to a few clauses; the larger
finding is that its records are cited at a path where the pinned corpus does not hold them.

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 30-34 | "are modules today (…); a later family or language … is a module of its own" | history | inline | "Arduino … and Rust for the ESP32 … are the modules (`firmware validate` lists each); another family or language is a module beside them." |
| 35-36 | "its other fields Arduino's as they always were" | history | inline | "its other fields are the Arduino module's." The same phrase is in `firmware/service.py:34` (area 3). |
| 66-67 | "The record is *Personal data stays on the device, by construction* (governance/qm/adr/)." | stale | inline | Not at the pinned qm commit (20e00bd holds two drafts in `adr/`); it is on qm's `adr/firmware-toolchain-seam`. Move the pin when that merges, or name the branch meanwhile. |
| 82-84 | "a parts/rc/snowplow/controller/controller.ino, which does not exist yet, would be" | history | inline | "A sketch at `parts/rc/snowplow/controller/controller.ino` would be the sketch `controller`." The conditional already says it is an example. |
| 258 | "There is no licence gate over the crates yet." | history | inline | "No licence gate reads the crates: `license-check.yml` checks Python dependencies." |
| 453-454 | "goes through the same latch, allowlist and confirms as the button it replaces" | history | inline | "replaces" reads as a change. "…as the button with the same verb". |
| 514-515 | "the *G-code printer seam* record's sixth decision draws that line" | stale | inline | Same record path problem as 66-67; also cite by the decision's words, not its position. |
| 538-540 | "The print records kept before jobs (…) are carried over as print jobs the first time" | history | inline | "A print record under `~/.apothecary/prints/records/` is read as a print job, and the file is left where it is." Checked `jobs._carry_over_print_records`. |
| 580 | "ATTRS{serial}==\"<the bench board's serial>\", SYMLINK+=\"ender\"" | — | inline | Outside the rule: the example carries the owner's own bridge serial. A placeholder (`<S/N>`) serves the reader as well. |
| 636-638 | "The decision records are *Firmware toolchain seam* and *G-code printer seam* in governance/qm/adr/" | stale | inline | As 66-67: both are drafts on qm's `adr/firmware-toolchain-seam`, not at the pin. |

Checked and true, no row: the five-minute latch (`CONTROL_TTL_S = 300.0`), the replay guard
(`devices.py`), the scripted fakes, and the `$HOME` tools-dir reason (a constraint stated as a fact).

### docs/slicer.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 5-7 | "The owner decided how on 2026-10-10 (the plan); this page says what was built" | history | inline | "The decisions behind it are in [the plan](../slicer-2026-10-10.md). A slice runs from the server, the command line and the page." |
| 40-44 | "OrcaSlicer 2.4.2 leaves both empty and its fixed version numbers say 2.0.0.0" | stale (risk) | inline | The vendor fact stays (§4), but the version repeats `ORCASLICER_VERSION` and goes stale when the pin moves: "The pinned release leaves both empty…". |
| 69-70 | "The owner decided (2026-10-10) that the start of a print is composed from modules" | history | inline | "The start of a print is composed from modules, as they are wanted." |
| 114-115 | "asks that server, as the page will" | stale | inline | The page slices a made piece already (walkthrough 13): "as the page does". |
| 175-176 | "the owner switches by changing that line" | history | inline | "a person switches slicer by changing that line." |

### docs/parts-authoring.md

The reference for a part's contract, and the right home for the SCAD assignment grammar
(viewer.md should link here rather than restate it).

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 170-185 | "the top-level assignments before the first module or function, annotated the customizer's way" | duplicate | inline | The grammar told again, 147-158 having said it. Keep the route facts (`GET /parts/{name}/params`, `lists: false`, the 404) and point up to 147-158. |
| 213-216 | "Keeping a variant's parameters in the part's own description instead … is the aim, and a stub until then" | history | inline, reference → project/plans/part-iteration-2026-10-12.md | "`params_in: \"part-description\"` is a stub: a save that asks for it is refused, saying what it would do." The aim is the plan's. |
| 219-225 | "the part's editor in Selected holds its SCAD, where the read-only source stood" | history, duplicate | inline | "where the read-only source stood" narrates the earlier page. The paragraph restates viewer.md's SCAD editor; keep one sentence and the link. |

Checked and true, no row: `tests/test_docs_site.py` runs the wrapper block; the OpenSCAD search
order (`stl_renderer.find_openscad`) and gridfinity's minimum version. The search order belongs on
the proposed docs/openscad.md as well; leave it here and link it from there, not both.

### docs/fitting-a-part.md

A page with two purposes: a reference for the seam as built (black boxes, the owner of each
problem) and a proposal (the line, the rules) that names itself one. The proposal half belongs
in a draft record; the reference half stays.

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 4 | "`datum` is the consumer it was written against" | history | inline | "`datum` is its consumer;" |
| 9 | "Status: proposed; a record candidate for governance/qm, not yet drafted there." | history | inline, then a record (to be drafted) | A status line in a reference guide. Draft "The line" and "Rules" as a project record in `governance/qm/adr/`; this page then cites it and drops the status. |
| 100-106 | "Nothing has been released, so the consumer pins a commit by necessity" | stale (check) | inline | No git tag exists, as `release.py` reads it; but CHANGELOG has "## [0.1.0] - 2026-01-02". State what is checkable: "No version is tagged; `apothecary release` says what stands between this commit and one." Owner settles whether 0.1.0 was a release. |
| 103-105 | "datum apothecary --check reports the deviation while nothing is published" | — | inline | About another repository; not checkable here. Keep only if `datum`'s README says the same, else "`datum`'s CI checks the pin". |

Checked and true, no row: `button.scad` declares `walls = 3; tolerence = .4;` and
`PrintSettings` defaults to 1.2 and 0.2 (`models/units.py`); "print-validated" is
`datum_core.scad`'s own comment.

### docs/geometry-from-elsewhere.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 60-70 | "Two things worth knowing about OpenSCAD 2021.01, the version on most machines" | ornament, duplicate | reference → docs/openscad.md (to be made) | "worth knowing" announces importance. The 2021.01 limits are spread over README, viewer.md, parts-authoring.md and here; one page lists them, this one links. |
| 71-74 | "And the viewer, focused *inside* a node, draws the node's children, not the node" | duplicate (misplaced) | reference → docs/viewer.md | A rule of the world's drawing; it belongs under viewer.md's "The world". |
| 105-112 | "The garage's printer is an Ender 3 (parts/ender3): a 2018 original with the power supply…" | duplicate | delete (keep parts/ender3/README.md) | Near-verbatim of parts/ender3/README.md 3-10. Keep the `build_origin` paragraph here; link the part's README for the machine. |
| 114-117 | "an Arduino Uno R3, a Raspberry Pi 4 B, a Teensy 4.0, an ESP32-DevKitC V4…" | duplicate | delete (keep parts/boards/README.md) | The boards table's list told as prose. Keep where each lies on the bench; link the table. |
| 131-132 | "No mesh of anyone else's went into any of these; they are our own OpenSCAD" | history, duplicate | inline | "None contains another's mesh: each is this repository's OpenSCAD from published dimensions, MIT." Also parts/boards 22-24 and parts/ender3 13-14: say it once per part README. |

### docs/models.md

No rows. Present tense throughout, and its examples run as doctests (`tests/test_models.py`).

### docs/scene-json.md

Present tense; written in an older voice (en-dash field lists, "This document describes"),
which is style, not history.

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 3, 185 | "both on the CLI (render, templategenerate, validate)" | stale | inline | `render-jscad` reads the same scene JSON (`cli/render.py`); name it, and say in one line that a scene also renders to JSCAD (README promises it; no reference page says how). |
| 189 | "and will error with \"No scene input provided.\" if neither is supplied" | — | inline | Tense only: "and exits with…". Message checked in `scene.py`. |

### tests/e2e/README.md

Present tense and accurate except one enumeration that has fallen behind the suite.

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 38-49 | "test_printer_ui.py, test_ring.py, test_one_machine.py, test_bench.py … ask it for servers of their own" | stale | inline | Misses `test_part_iteration.py`, `test_part_iteration_answers.py`, `test_text_tied.py`, `test_onboarding.py`, `test_paths_people_take.py` (checked: each calls `start_server`). State the rule and the command: "`grep -l start_server tests/e2e` lists them"; keep the loops' benches. |
| 87-89 | "settled(page) waits until the level's geometry has loaded … and the canvas has drawn it" | stale (incomplete) | inline | `settled` also waits for the camera at rest and the badges' occlusion (`viewer_ready.py`): "…loaded, the camera is at rest and the canvas has drawn it." |

Checked and true, no row: `-k minimap` selects `test_minimap_advances_with_zoom_depth`;
`test_first_camera.py` uses the `chromium` channel and skips without it; the marker and
`browser_suite_only` check in `conftest.py`; three CI shards.

### crates/apothecary-core/README.md

A stub's README is about its future by nature; the rows are where it tells time ("yet",
"today", "that day") instead of stating what the stub is and what it is for.

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 4-7 | "**Not built yet**: the library exposes one function, version(), and nothing else." | history, ornament | inline | "A stub: the library exposes `version()` and nothing else (`src/lib.rs`), for [the Rust plan]'s core." Bold status off. |
| 9-18 | "## Its future hot paths … Where Python's speed shows today, in the order the plan lists them" | history, duplicate | reference → project/plans/rust-2026-10-08.md | The plan lists the same four paths (its line 61-62). Keep one sentence naming them and the link; drop "today" (also at 17-18, "which today runs in Pillow"). |
| 25-29 | "is not changed to build this crate … is a decision for that day" | history | inline | "`pyproject.toml` builds the `apothecary` package alone; the wheel carries none of this crate. How a working core would ship is undecided." |

Checked and true, no row: `abi3-py311` in `Cargo.toml`, matching `requires-python`.

### crates/apothecary-service/README.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 3-7 | "**Not built yet**: the binary prints that and exits non-zero." | history, ornament | inline | "A stub: the binary says so and exits 1 (`src/main.rs`)." The reason it exists (workspace, headers and checks settled first) stays. |
| 11-12 | "the plan leaves the choice open until it is made with the owner" | history | inline | "One of two jobs, undecided in the Rust plan; the first it takes is all of its first version." |
| 14-19 | "Today the Python server holds the serial port … what the Python side does today" | history | inline | Drop both "today": "The Python server holds the serial port…; docs/firmware.md says what it does." |
| 27-33 | "When it does something, CI needs a job that installs Rust … cargo license against the allowlist" | — | reference → project/plans/rust-2026-10-08.md | A future CI job's specification; it is plan content. Here: "Not built by CI or the Python suites; `cargo check --workspace` locally." |
| 39 | "# prints that it is not built yet; exits 1" | history | inline | "# prints that it is a stub; exits 1". The binary's own message says "not built yet" too (area 3). |

### parts/README.md

No rows. Checked: the three camera mounts' `part.json` each tag `"stub"`; the tree's folders exist.

### parts/boards/README.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 22-24 | "No mesh of anyone else's went into them; the dimensions are the specifications…" | history | inline | "They contain no one else's mesh: the dimensions are the specifications the makers publish so that things can be made to fit." This README is the home; geometry-from-elsewhere links it. |

### parts/ender3/README.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 13-14 | "No mesh of anyone's went into it." | history | inline | "It contains no one else's mesh." This README is the home for the machine's description (geometry-from-elsewhere 105-112 repeats it). |

### parts/datum_core/README.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 49 | "What has to be checked against a real board before this is printed in anger" | ornament | inline | "…before this is printed for use:" |

Checked and true, no row: `tolerence = .4` in both SCADs and `datum_cap`'s `lip_clearance = tolerence / 2`;
"print-validated" is the SCAD's own comment.

### parts/gridfinity/README.md

This repository's own README beside the submodule, in another voice from the rest (title-case
headings, a promotional opening) and with one wrong instruction.

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 3 | "a customizable and scalable storage solution that allows users to create organized storage units" | ornament | inline | "The Gridfinity bin: a part wrapping the `gridfinity-rebuilt-openscad` submodule's `gridfinity-rebuilt-bins.scad`." |
| 5-16 | "## Quick Start … git submodule update --init" | stale (incomplete) | inline | Missing the limit a reader meets first: the part needs an OpenSCAD newer than 2021.01 (`openscad_min_version`); `apothecary openscad install` puts one in. |
| 62-70 | "This repository includes a Git submodule … To initialize the submodule, run…" | duplicate | delete | Repeats 8-9 and README's clone line. |
| 72-76 | "Update the submodule to ensure you have the latest designs: git submodule update --remote --merge" | stale | inline | Wrong for a pinned submodule: the wrapper's defaults are the file's own and `tests/test_parameter_coverage.py` holds them. "The submodule is pinned; moving it is a commit that bumps the pin and passes the parameter-coverage test." |

## 2a. The structure as a whole

**A newcomer's path.** There is one, and it is clear at the top: README's *Start here* names
walkthrough 00 and three commands, `apothecary --help` ends with the same three, and walkthrough
00 takes it from there. What blurs it is README itself: after *Start here* come *Install*, *First
commands*, a camera procedure, the picture folder and a Python example, so a reader meets the path
and then a second, longer path on the same page. Recommended shape: README is what the project is,
*Start here*, *Where next*, *Troubleshooting* and the licence; *Install* shrinks to prerequisites
and the submodule note; everything procedural is walkthrough 00 or a reference page.

**Who each top-level page is for.** README: a person arriving. Walkthrough 00: that person's first
hour. CONTRIBUTING: a person changing the code (test loop, CI, where things go). AGENTS: an agent's
briefing and the governance rules (CLAUDE.md is a symlink to it). docs/README: the index. QUICKSTART:
no one (delete). project/todo.md: the backlog, overlapping the cleanup triage plan.

**Duplicates (one home each).**

| What | Told in | Home |
|---|---|---|
| Clone, sync, check, first serve | README 47-60, CONTRIBUTING 8-14, AGENTS 48-72, walkthrough 00 §1-4 | walkthrough 00 (person), AGENTS (agent); CONTRIBUTING keeps only Playwright |
| OpenSCAD per platform, and what 2021.01 cannot do | README 61-80, CONTRIBUTING 16-20, geometry-from-elsewhere 60-70, viewer.md 228, parts-authoring 170-172 and 251-252, `openscad_installer.py` docstring | docs/openscad.md (to be made) |
| The viewer's rail, ring and editors | README 12-20, viewer.md | viewer.md |
| A camera picture to a print | README 107-119, walkthrough 13, viewer.md 133-138, slicer.md 144-167 | walkthrough 13 (the loop), docs/pictures.md (the reference, to be made) |
| SCAD assignment grammar | viewer.md 195-204, parts-authoring 147-158 and 170-185 | parts-authoring 147-158 |
| The SCAD editor in the page | viewer.md 301-372, parts-authoring 219-225 | viewer.md |
| The Ender 3 and the boards | geometry-from-elsewhere 105-119, parts/ender3/README, parts/boards/README | the part READMEs |
| "No one else's mesh" | geometry-from-elsewhere 131-132, parts/boards 22-24, parts/ender3 13-14 | each part README, once |
| Commit rules | AGENTS 16-22 and 81-84, CONTRIBUTING 72-78 | AGENTS |
| Open work | project/todo.md "Open in this repository", cleanup-triage plan | one list, the other links it |

**Pages without a clear purpose.** QUICKSTART.md (a pointer nothing links). fitting-a-part.md
(half reference, half a proposal with a status line; the proposal belongs in a draft record).
parts/gridfinity/README.md (written for another audience, with a wrong update instruction).

**Contradictions.** fitting-a-part.md says nothing has been released; CHANGELOG has a dated
`[0.1.0]`. firmware.md cites three records in `governance/qm/adr/` that the pinned qm commit
does not hold (they are on qm's open `adr/firmware-toolchain-seam`). AGENTS writes `openscad install
--latest`, every other page `openscad install` (the same command; harmless, but it reads as two).

**What is missing.**
- **Pictures and cameras.** The `photo` group (`find`, `build`, `words`, `finders`, `check`, `view`,
  `gather`, `gather-check`) has no page beyond `--help`; README names only `photo view`. The picture
  root, `captures/` and `uploads/`, a camera's ring, finders and words are told in README's paragraph,
  walkthroughs 11 and 13, and plans.
- **Configuration.** Sixteen `APOTHECARY_*` variables in the code; twelve are named across six
  pages, four nowhere (`APOTHECARY_DEMO`, `APOTHECARY_OPENSCAD_RUNS`, `APOTHECARY_SIMULATED_PROGRESS`,
  `APOTHECARY_SIMULATED_SPEED`). No page lists them.
- **OpenSCAD.** No page owns installing it, choosing it (`find_openscad`), its versions' limits, or
  how many run at once.
- **Sites and assemblies.** What a site, a node, `part_ref`, a footprint and the layout check are is
  told in walkthroughs 03, 04 and 08, geometry-from-elsewhere's "Put it in a site" and
  fitting-a-part's ladder; no reference page. Lower priority than the three above.

## 3. Retrospectives this area would need

Few: most history here is a clause with no lesson, and the plans that hold the decisions are
dated already. One story is worth keeping.

- **apothecary: a part's values moved into its text** (2026-10-12)
  - Values once reached OpenSCAD on the side as `-D`, and a saved variant kept them in `.variant.json`; a merge did not apply them.
  - The page showed a read-only source in Selected; the editor took its place, and the controls and the text became one draft.
  - Variants saved before the change are still read: their values are written into the text on read, and the merge advice says so.
  - The lesson: two descriptions of one value drift; the text became the only one, with the model as its check.

Not needed, the dated plan already holds it: the slicer's decisions (`plans/slicer-2026-10-10.md`),
the Rust stubs (`plans/rust-2026-10-08.md`). No lesson, delete only: the print records before jobs,
the `/firmware/status` fields "as they always were", "a planned item" for Windows on ARM.

## 4. Reference pages to create or extend

| Page | New or extended | Takes in |
|---|---|---|
| docs/openscad.md | new | README 61-80; CONTRIBUTING 16-20; the 2021.01 limits from geometry-from-elsewhere 60-70, viewer.md 228, parts-authoring 170-172 and 251-252; `find_openscad`'s order (link parts-authoring 238-246); `APOTHECARY_OPENSCAD`, `APOTHECARY_OPENSCAD_RUNS` |
| docs/pictures.md | new | README 107-127; the `photo` commands; the picture root, captures and uploads; cameras, finders, words; links walkthroughs 11 and 13 |
| docs/configuration.md (or a table in docs/README.md) | new | every `APOTHECARY_*` variable, one line each, linking the page that explains it |
| docs/viewer.md | extended | geometry-from-elsewhere 71-74 (inside a node, its children are drawn); README 12-20's tour, already here |
| docs/parts-authoring.md | extended | the single statement of the assignment grammar (viewer.md and its own 170-185 link it) |
| docs/scene-json.md | extended | `render-jscad` and the JSCAD output README promises |
| a project record (drafted in `governance/qm/adr/`) | new | fitting-a-part.md's "The line" and "Rules" |
| docs/sites.md | new, later | sites, nodes, `part_ref`, footprints, the layout check, problem owners |

## 5. Suggested order

1. **Inline one-liners on the most-read pages**, no moves: README 77; AGENTS 68; slicer.md 5-7,
   69-70, 114-115, 175-176; viewer.md 241, 334-335, 348-350; firmware.md 30-36, 82-84, 258,
   453-454, 538-540; project/todo.md's six rows; the crate READMEs' "yet" and "today". Small, safe, and
   README, viewer.md and firmware.md are the pages people open.
2. **Stale fixes that need a check, not a decision**: tests/e2e/README 38-49 and 87-89;
   docs/README 30 and 93; scene-json 3 and 185; parts/gridfinity 5-16 and 72-76.
3. **Deletes of pure duplicates**: QUICKSTART.md (owner confirms no outside links);
   parts/gridfinity 62-70; geometry-from-elsewhere 105-117 and 131-132 down to links.
4. **The record citations**: firmware.md 66-67, 514-515, 636-638 — move the qm pin when
   `adr/firmware-toolchain-seam` merges, or name the branch until then.
5. **docs/README.md's History list**, with area 5 (which plans retire).
6. **New reference pages**, each in its own pull request, taking in the passages listed in §4:
   docs/openscad.md first (it absorbs the most duplication), then docs/pictures.md, then the
   configuration table. README's Install, camera and picture paragraphs shrink in the same pull
   requests that create their homes.
7. **fitting-a-part.md**: draft the record, then strip the page to the seam as built. Needs the
   owner, and the 0.1.0 question settled.

## Found outside this area, for the other inventories

- `apothecary/firmware/service.py:34` "as they always were" (area 3), same as firmware.md 35-36.
- `apothecary/openscad_installer.py:30,257` "not supported yet (a planned item)" (area 3), same as README 77.
- `crates/apothecary-service/src/main.rs` and `crates/apothecary-core/src/lib.rs` "not built yet", "nothing yet" (area 3).
- `apothecary/census.py:496` says Picture › Folder lists "the seven newest by name"; `routes/pictures.py:119` sorts by mtime (area 3, stale).
- "where its source stood" in walkthrough 16 and `tests/e2e/test_scad_loop.py`, `tests/test_census.py:375`, `templates/fractal_viewer.html.j2:530,5333` (areas 2 and 4).
