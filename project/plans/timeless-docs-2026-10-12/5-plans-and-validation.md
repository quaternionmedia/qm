# Inventory: `project/plans/*.md` and `project/validation/*.md`

Read on `build/timeless-docs` at `c67725a`, in a worktree of its own. The
governance corpus in that worktree is empty, so
records were read in `<checkout>/governance/qm` (branch
`adr/firmware-toolchain-seam`, every `adr/` record still `DRAFT-*`, Proposed).
Plans and validation records are dated and exempt: no passage of them is
listed for rewriting. What is listed is each plan's state, where its
still-true decisions belong, and the present-tense text that leans on it.

## Verdict on the area

Most plans are finished and should retire; only four are open. Ten of the
fourteen plans describe work the code now carries in full: one-screen,
consolidation, cameras-and-clutter, cleanup-triage, ui-flows, slicer,
onboarding, rust, and the two research spikes (part-editing-in-the-browser,
rust-geometry-kernels). Their still-true decisions are mostly *already*
stated in present tense: `docs/viewer.md`, `docs/firmware.md` and
`docs/slicer.md` hold the UI, firmware and slicer decisions, the module
docstrings (`vision/views.py`, `vision/cameras.py`, `vision/projection.py`,
`projects/parts/saved.py`, `static/panels.js`, `static/widgets/machine.js`)
hold the model, and the draft records (`DRAFT-one-screen`,
`DRAFT-rad-host-integration`, `DRAFT-personal-data-stays-on-the-device`,
`DRAFT-firmware-toolchain-seam`, `DRAFT-slicer-seam`) hold the rules. So
retiring them takes little new prose. The bigger problem is
**structural**:
- `docs/README.md`'s *Plans and records* table lists all fourteen plans
  beside the guides as if each were current, and holds no records.
- `project/todo.md` sends a reader to four plans and a validation record as the
  place where open work lives. Two of those links are stale: the spike is
  done, and the pictures plan's Phase 6 was overtaken.
- About forty code docstrings and comments cite a plan by path as the reason
  for the code.
- **Superseded decisions still leak into present-tense text.** The
  page-16 row of `docs/README.md` says "rendered after a second of
  quiet", but the code waits 300 ms after a check that passes. Two draft
  records also keep earlier plan decisions that later plans reversed:
  tethered popups, and a made piece saved as a variant.

The validation area has two records:
- The **Ender bench** record holds a bench checklist a person still runs
  (sections A–G). Its ring addresses still match `apothecary/menu.py`.
- The **local-integration** record mixes three things: a runbook a person
  still runs (stays-local doors, OpenSCAD on each platform), instructions
  that `apothecary serve --demo` replaced, and an untracked hardening list.

**Missing reference pages:**
- `project/bench-checklist.md`, a present-tense runbook for the printer and the
  ESP32 at the bench.
- `docs/pictures.md`, covering pictures, cameras, views and pieces. The
  model is only in docstrings and in the 767-line pictures plan.

## At a glance

| Plan | State | Action |
|---|---|---|
| one-screen-2026-09-20 | Finished (one conditional note left) | Retire |
| consolidation-2026-10-03 | Finished | Retire |
| cameras-and-clutter-2026-10-04 | Finished (all four phases) | Retire |
| cleanup-triage-2026-10-08 | Finished as a triage; leftovers belong in `project/todo.md` | Retire after moving three person-items to `project/todo.md` |
| ui-flows-2026-10-08 | Finished | Retire |
| slicer-2026-10-10 | Finished in code; ratification of its records is a person's | Retire |
| onboarding-2026-10-11 | Finished | Retire |
| rust-2026-10-08 | Finished as decided (build, research, stubs) | Retire; two open questions to `project/todo.md` / the crates READMEs |
| rust-geometry-kernels-2026-10-09 (spike) | Finished as research; nothing to build from it until the service gets a job | Retire; keep it as the dated survey the service README cites |
| part-editing-in-the-browser-2026-09-27 (spike) | Finished: iterations 1–3 landed; iteration 4 is carried by part-iteration's next phase | Retire |
| pictures-in-the-world-2026-09-26 | **Open**: Phase 1 (gathering an extra) and Phase 7 (old `/photos` routes) | Split: keep Phases 1 and 7, retire the rest |
| photo-finders-local-models-2026-09-21 | **Open**: nothing built | Stay |
| part-iteration-2026-10-12 | **Open**: this round built; *The next phase* not built | Stay; split *The next phase* off when this round's PR merges |
| timeless-docs-2026-10-12 | **Open**: the sweep itself | Stay |

## Per plan

### one-screen-2026-09-20.md: finished, retire

**What was checked in the code:**
- `apothecary/static/anchors.js`, `machine_marks.js`, `panels.js` and
  `widgets/machine.js` all exist.
- `census.PAGES = (VIEWER,)`, which is one page.
- `/firmware` and `/firmware/monitor` redirect into the viewer
  (`api.py:2483`, `:2489`).
- No template is left for the monitor or the firmware page.
- `panels.js` has no popup, tether or leader code. Panels are rail or
  floating only.

What is left open is the plan's own conditional note: "split `widgets/machine.js`
when a host wants one part". That is not scheduled work, and it belongs in
`machine.js`'s header comment.

**History line:**
`- 2026-09-20 — [One screen](../one-screen-2026-09-20.md): the world as the one page, with anchors and panels in front of it, and the census as the meter.`

| Decision still true | Home |
|---|---|
| One page, the world; nothing replaces it; a page that navigated away opens a panel | Nowhere: `DRAFT-one-screen` §1, `docs/viewer.md` intro |
| Things in front of the world: anchors (read, not operated), panels in one rail | Nowhere: `DRAFT-one-screen` §2 (see superseded: popups), `static/panels.js` and `anchors.js` headers |
| What has a place is drawn in the world (body, board, nozzle marker, bed relief, build volume) | Nowhere: `DRAFT-one-screen` §3 |
| Every action has a cell; the census's ring-backed share never falls | Nowhere: `DRAFT-one-screen` §4, `apothecary/census.py` docstring |
| The census counts, the plan does not estimate; `VIEWER_CEILING` edited with a docstring | Nowhere: `tests/test_census.py` docstring. **Delete the history in that docstring** when its own area is swept (it narrates before and after for each phase) |
| Snappy: anchors projected in the animation frame with no layout reads; a popup opens within 300 ms | `anchors.js` header already says the first. The 300 ms bound lives in `tests/e2e/test_printer_ui.py`. Nowhere new |
| Plain layouts are not kept as kiosk views; old addresses redirect | Nowhere: `DRAFT-one-screen` §6, `docs/viewer.md` address table |
| `widgets/machine.js` is one file with sections; split it when a second host wants one part | Code docstring: add one sentence to `machine.js`'s header |
| `?machine=<port>` deep link kept in the address | Nowhere: `docs/viewer.md` address table |
| The printer's drawing encloses its board and build volume, held by `tests/e2e/test_printer_ui.py` | Nowhere: `docs/firmware.md:620` |
| Not in this plan: a second site at once, other browsers in tests, a mobile layout | Nowhere (non-goals; no present-tense home needed) |

**Superseded decisions:**
- **"Popups: panels tethered to an anchor … the machine popup, a devkit's
  serial popup, a piece's properties"** was reversed twice:
  - by the consolidation's *Decided after Phase 2* (one rail; a Machine
    docks into the strip);
  - by cameras-and-clutter's *Less on the screen* ("Open shows a board's
    Machine in the rail's tab strip … it floats only when floated").

  The code has no tethered popups. **`DRAFT-one-screen` §2 still names
  "Popups … tethered to an anchor … drawing a leader to it"**, and §7 cites
  this plan for the order of the move. Both are governance edits the owner
  should make before ratification.
- "The old routes keep answering until Phase 5" is moot: Phase 5 was built.

### consolidation-2026-10-03.md: finished, retire

**What was checked in the code:**
- Site and Selected sit in one rail with a tab strip (`panels.js` header,
  `docs/viewer.md` *The rail*).
- The job model is in place (`apothecary/jobs.py`, `routes/jobs.py`), with
  `GET /jobs/choices` listing every part or piece in the site.
- `apothecary photo look` is a retired stub (`cli/photo.py:109`) and
  `photo find` is live.
- A printer's Device › Flash is disabled, not absent (`DRAFT-rad-host-integration`
  line 151).
- `boards.js` is the one board model, with one poller.

**History line:**
`- 2026-10-03 — [Consolidation](../consolidation-2026-10-03.md): one page and one place per thing; Site and Selected over a strip of tabs, one Machine per board, the Bench, one Pictures panel, jobs over machine kinds.`

| Decision still true | Home |
|---|---|
| End state: Site (Contents, problems, SCAD, Pinned, jobs), Selected, Machine per board, Bench, Pictures | Nowhere: `docs/viewer.md` *The rail*, `DRAFT-one-screen` §2 |
| One log and one query box per board; one poller shared by everything that draws it | Nowhere: `static/boards.js` and `widgets/machine.js` headers, `docs/firmware.md` |
| Words: **View** (a picture pinned at a place), **Take picture** (pins, finds nothing), **Find shapes** (a step of its own); Camera › Keep gone | Code docstring `vision/views.py` already says it. Reference → `docs/pictures.md` (to be made) for a reader's glossary |
| Every message that ends a step names the next one | Nowhere: `docs/viewer.md` (status line paragraph), `README.md:113`. Add one sentence to `CONTRIBUTING.md` as a rule a contributor keeps, where UI text conventions belong |
| A job: kind, machine, part, input file, start/finish, outcome; a running job marks a printer busy; hand-typed Jobs gone | Nowhere: `apothecary/jobs.py` docstring, `docs/firmware.md:520-531` |
| Selected's status drop-down keeps "printing" as hand-set, beside idle, maintenance, offline | Nowhere: `docs/firmware.md:374`, `:531` |
| A print job may name any part or piece in the printer's site, not narrowed to what fits | Nowhere: `docs/firmware.md:522-523` |
| Addresses stay where hands learned them; Open took Watch's cell, Flash took Monitor's | Nowhere: `DRAFT-rad-host-integration` (stable addresses, line 187; the Flash exception, line 151) |
| A devkit's port is opened only when asked (Listen) | Nowhere: `widgets/machine.js` header, `docs/firmware.md` |
| Boards are found on request: no timed rescan | Nowhere: `docs/firmware.md:427` |
| A printer's Device › Flash shown disabled, the one exception to "absent, not greyed" | Nowhere: `DRAFT-rad-host-integration` lines 151–155 |
| A chosen picture is the ring's: Picture › Folder's eighth cell pins it | Nowhere: `apothecary/menu.py:797-800`, `widgets/picture_list.js` header |
| *Records this touches* (One screen, rad host integration, personal data §6 "view" for "look") | Nowhere: the three drafts now say "view" and "Pinned" (checked `DRAFT-personal-data…` line 295) |

**Superseded decisions:**
- *The end state* says "Machine (a popup tethered to its board)". That was
  reversed by its own *Decided after Phase 2* (one rail) and by
  cameras-and-clutter (the Machine in the strip).
- *The end state* says "the gathering as a section of it until gathering
  leaves core". That is still true; it is the open pictures Phase 1.

### cameras-and-clutter-2026-10-04.md: finished, retire

**What was checked in the code:**
- `parts/cameras/webcam` exists, with three `stub`-tagged camera parts
  (`webcam_desk_stand`, `webcam_clamp_arm`, `webcam_ceiling_mount`).
- `apothecary/vision/cameras.py`, `camera_part.py` and `projection.py` are
  in place: a camera is a root structure, lens learning works, a picture
  lands on the first upward-facing surface, one device is one camera, and
  Reset stands a camera back where it was added.
- `cameras.json` is read nowhere in `apothecary/`.
- `P` and `?` are listed in `docs/viewer.md` *Keys*.
- ⚙ View appears with Walls selectable, and the faded walls and the ×N
  badge merging are described in `docs/viewer.md`.
- `picture_marks.js:26` draws the pyramid only while the camera is selected
  or live.
- The garage has one printer (`example_hierarchy.py:87`).
- The cleanup triage marks Phase 4 done (#30).

`docs/README.md:67` describes the plan only as "in four phases" and never
says it is done.

**History line:**
`- 2026-10-04 — [Cameras and clutter](../cameras-and-clutter-2026-10-04.md): a camera as a part of the site, pictures sized and taken from it, and less on the screen (icon badges, the Machine in the rail, one header row, faded walls).`

| Decision still true | Home |
|---|---|
| A camera is a root structure (`camera_N`), the library's webcam, in Contents, moved, overlap-checked | Nowhere: `vision/cameras.py` docstring. Reference → `docs/pictures.md` (to be made), one paragraph |
| Added by Camera › Add here (above a place, looking down) or dropped from the library; Add here never uses a stub | Nowhere: `docs/viewer.md:133` covers Add here. A camera is always drawn as `WEBCAM` (`vision/cameras.py`: "drawn as the library's bare webcam"), and `parts/README.md:13-15` marks the stubs |
| Device chosen on the camera's ring; one device, one camera | Nowhere: `vision/cameras.py` docstring |
| Lens: starts at a typical webcam's field of view; the first width typed teaches it; pictures sized at once from the starting lens | Nowhere: `vision/cameras.py`, `vision/views.py` docstrings. Reference → `docs/pictures.md` |
| Where a picture lands: first upward-facing surface the centre ray hits, else kept with no place | Nowhere: `vision/cameras.py` docstring (`lands`) |
| A view keeps its camera's pose and field of view; one pinhole mapping used by mat, outlines, Make, Why this, re-sizing | Nowhere: `vision/projection.py`, `vision/views.py` docstrings |
| Reset stands an added camera back where it was added; only Remove takes it away | Nowhere: `vision/cameras.py` docstring |
| Selected shows a camera's preview, Take picture, thumbnails; `P` takes a picture | Nowhere: `docs/viewer.md` (*The rail*, *Keys*) |
| Pictures listed as thumbnails grouped by camera | Nowhere: `widgets/picture_list.js` header |
| Badges: one icon per thing, words on hover; overlapping badges merge into ×N | Nowhere: `docs/viewer.md` *The world* |
| The Machine opens in the rail's strip and floats only when floated; a printer's Machine has no Flashing | Nowhere: `docs/viewer.md`, `widgets/machine.js` header |
| One header row; ⚙ View holds Snap, Detail, Assembly outlines, Walls selectable; View is a top-level canvas-ring cell with Fit inside | Nowhere: `docs/viewer.md` *The header*, *How the world is drawn* |
| Problems once: a folded line in Site, opened by the header's count | Nowhere: `docs/viewer.md` |
| The hint bar fades after a few actions; `?` brings it back | Nowhere: `docs/viewer.md` |
| Walls faded, clicks pass through; selectable from Contents or ⚙ View | Nowhere: `docs/viewer.md` *The world* |
| Camera stubs (desk stand, clamp arm, ceiling mount) are `stub`-tagged parts drawing only the webcam | Nowhere: each stub's `part.json` description |
| The garage has one printer, printer_1 | Nowhere: `example_hierarchy.py:87` comment. **That comment narrates "the owner's decision of 2026-10-04"**; area 3 should rewrite it in the present tense |
| A camera's pyramid shows only while selected or live | Nowhere: `picture_marks.js:26` |
| Part on a camera's ring edits position, turn, tilt, field of view | Nowhere: `vision/camera_part.py` docstring (it narrates "the owner's decision of 2026-10-04"; area 3) |
| *Offered and not chosen* (a picture on any face, a camera that only turns, and the others) | Nowhere: non-goals of a dated plan; they stay in the plan |

**Superseded decisions:**
- *The end state* says "the pill reads 'prototype', the full text its
  tooltip". It is still true (template line 668). Nothing reversed it.
- This plan reverses the pictures plan's "a camera is a badge at the
  structure it is pinned to", "a host holds at most one camera" and "a
  camera that looks sideways is not in this plan". The pictures plan's
  *End state* and *Not in this plan* must not be carried into present-tense
  docs.
- **`DRAFT-personal-data-stays-on-the-device` §6 still says "camera
  placements"** and "a camera at a piece". Cameras are now parts with a
  device record in `camera_parts.json`. The *Records this touches* line
  ("where a camera's device id and label are kept now that the cameras file
  is retired") should be confirmed in the record.

### cleanup-triage-2026-10-08.md: finished as a triage, retire

This is an ordering of items, not a plan with decisions. Every *Now* and
*This round* item is done:
- Each of the four *In flight* rows is marked done.
- The stack was split (#24–#36).
- `tests/e2e/durations.json` has `test_the_firmware_loop.py` and was last
  committed 2026-10-12.
- No `cameras.json`, Load or Zoom Out button is left in the code (`zoomOut()`
  remains as the crumb's function).
- The picture-drift item is closed by onboarding (`tests/e2e/picture_drift.py`
  warns in CI).

What remains is either computed by `apothecary problems` (the parts rows) or
already a `project/todo.md` line (JSCAD, xdist, the structure items, the
skipped-tests governance item, the hidden stubs).

**Three items exist only here and must move to `project/todo.md`**, under a new *For a
person to do* heading:
1. the Dependabot bumps, closed or rebased once the stack lands;
2. ratifying the governance drafts and bumping the governance pin;
3. reviewing rad#7 (open-at-an-item).

*Decide `datum_core.board_y`* is computed (`apothecary problems`, contested),
so it needs no line. The bench-checklist re-run is already `project/todo.md:17`.

**History line:**
`- 2026-10-08 — Cleanup, triaged: the open cleanup items sorted by kind and given an order, while the review branch was split into a stack.`

| Decision still true | Home |
|---|---|
| The order words (Now / This round / Next round / A person) | Nowhere: `project/todo.md`'s own headings carry the order |
| Data-only part wrappers as `part.json`, `api.py` into routers, the inline script into modules, one firmware port registry, gathering as an extra, the wheel carrying `parts/` | Nowhere: `project/todo.md` *Next round* lines 23–46 and *Open* line 12 |
| The owner's `~/.apothecary/cameras.json` is left in place, unread | Nowhere: the fact that it is unread is in the code (no reader); the owner's file is not documentation |

**Superseded decisions:** none. This plan made no decisions of its own.

Present-tense link to fix: `project/todo.md:8` names this page "the order to take these
in, with the work in flight". Delete that line when the plan retires.

### ui-flows-2026-10-08.md: finished, retire

**What was checked in the code:**
- Each of the four loops has its browser test going round twice:
  `tests/e2e/test_part_loop.py::test_designing_a_part_twice_round`,
  `test_scad_loop.py::test_editing_a_parts_scad_twice_round`,
  `test_the_firmware_loop.py` (Arduino then Rust, and Rust alone), and
  `test_picture_to_print.py::test_a_picture_to_a_print_twice`.
- Walkthrough pages 13–16 exist and are written by the browser suite
  (`tests/e2e/README.md:74-82`).
- A made piece's Print cell exists (`menu.py:1051`).
- A job records its picture and camera (`jobs.py:90-96`).
- `?variant=` is in the address (`docs/viewer.md` address table).

**History line:**
`- 2026-10-08 — [The loops through the page](../ui-flows-2026-10-08.md): designing a part, editing its SCAD, firmware, and a picture to a print, each built out and held end to end by a browser test.`

| Decision still true | Home |
|---|---|
| Four loops, each held by one browser test that goes round at least twice through the page's own controls and ring cells, asserting what a person sees | `walkthrough/00-getting-started.md:97` says it for a reader. For a contributor, reference → `tests/e2e/README.md`: one sentence ("a loop's test goes round twice through the page's controls and ring cells") beside the loop-page paragraph at :74 |
| A walkthrough page per loop, written by its test from the browser suite only, so `apothecary test run` stays quick | Nowhere: `CONTRIBUTING.md:43`, `tests/e2e/README.md:74-82` |
| A loop needing hardware is tested against fakes and the simulated printer; its real run is a bench-checklist step | Reference → the bench runbook (`project/bench-checklist.md`, to be made); `docs/firmware.md:620-630` says it for firmware |
| An applied variant lives in its tab's URL; the part's own STL stays the default; a variant drawn subtly marked (amber) | Nowhere: `docs/viewer.md` address table and *The world* |
| Where OpenSCAD gives no summary the STL is measured in Python, and the answer says which (`measured_from`) | Nowhere: the generate route's docstring states it (`apothecary/api.py:642`, `measured_from: "summary"`, else the STL measured), and the answer is in `/openapi.json` |
| Defaults has a ring cell; the part's ring holds the whole loop (Edit, Defaults, Apply, Revert) | Nowhere: `docs/viewer.md` *The ring*, `menu.py:1220-1231` |
| A made piece's ring has Print, opening the pinned printer's Machine with the piece chosen | Nowhere: `docs/viewer.md:143`, `docs/firmware.md:504` |
| A print job records the picture and camera its piece came from, not shown in its row | Nowhere: `apothecary/jobs.py` docstring |
| When a print ends the status line says so, or that it failed and why | Nowhere: `widgets/machine.js` header (`say`) |
| The SCAD editor lives in Selected, floated or fullscreen; variants listed in two places | Nowhere: `docs/viewer.md` *The SCAD editor* |

**Superseded decisions:**
- "an editor in the page with … a render after a second of quiet" (loop 2)
  was replaced by part-iteration item 9 (check 300 ms after typing, render
  ~300 ms after a passing check). The code agrees with part-iteration
  (`SCAD_CHECK_MS = 300`, `SCAD_RENDER_AFTER_CHECK_MS = 300`,
  `templates/fractal_viewer.html.j2:894-895`). **`docs/README.md:30` still
  says "a change rendered after a second of quiet"**, so the superseded
  decision has leaked into present-tense text.
- "A variant's parameters are kept in a file beside its SCAD in the
  variant's commit for now" was replaced by part-iteration's *parameters and
  text, tied together* ("the variant's separate parameters file goes").
  `saved.py`'s docstring states the present rule and keeps `.variant.json`
  only for reading older saves.
- "the check debounced and a superseded render cancelled" is still true. The
  timings themselves are part-iteration's.

### slicer-2026-10-10.md: finished, retire

**What was checked in the code:**
- `apothecary/slicer/` (modules, installer, profiles, compose, service) is
  in place.
- `parts/ender3/slicer.json` exists.
- `docs/slicer.md` describes the install, the profile, the compose pieces
  with their stubs, print settings from the part, the routes, *Every slice
  is kept*, Slice on the ring and in the Print card, and switching slicers.

Its three *Open until built* items are settled:
- **Storage** is decided, *Every slice is kept* (`docs/slicer.md:132-139`).
- **Declaration** is decided: `print_settings` on the wrapper
  (`docs/slicer.md:87-104`).
- **The licence disposition** is drafted as `DRAFT-slicer-seam` and an
  adoption-scope amendment, on the governance branch (`adr/` commit
  `e0213fe`). Ratifying them is a person's act and belongs on `project/todo.md`,
  not in this plan.

**History line:**
`- 2026-10-10 — [A managed slicer](../slicer-2026-10-10.md): OrcaSlicer behind a slicer interface, installed like OpenSCAD, the printer's profile kept with its part, print settings from what each part declares.`

| Decision still true | Home |
|---|---|
| OrcaSlicer behind a slicer interface; another slicer is a module; the owner switches by one profile line | Nowhere: `docs/slicer.md` *Another slicer*, `slicer/__init__.py` |
| Installed by apothecary: pinned release, checked before it is opened, tools dir, three platforms, a refusal elsewhere; a pin moves only in a commit that re-runs install and a slice | Nowhere: `docs/slicer.md` *Installing it* (lines 17–48) |
| The printer's profile is kept with its part, from OrcaSlicer's Ender-3 profile plus what the bench measured | Nowhere: `docs/slicer.md` *The printer's profile* |
| Print settings come from the part; the printer fills the rest; each value says where it came from | Nowhere: `docs/slicer.md` *Print settings from the part* |
| Slice is a step of the page; Print follows Slice | Nowhere: `docs/slicer.md` *In the page* |
| The bed: measured offset and mesh held with their source, adding nothing to G-code; start pieces composed as modules, `stored-mesh`, `probe-each-print`, `first-layer-offset` stubs | Nowhere: `docs/slicer.md:60-85` |
| Filament: the printer's one (Creality Generic PLA); choosing another is a stub | Nowhere: `docs/slicer.md:83-84` |
| Made pieces slice with the printer's values; a word's print settings are a stub | Nowhere: `docs/slicer.md:90-94` |
| Every slice kept until forgotten in the Print card | Nowhere: `docs/slicer.md:132` |
| `apothecary slicer slice` reaches made pieces through the running server | Nowhere: `docs/slicer.md:114-121` |
| Kept as built: record lasts as long as its file; an unknown nozzle refused; wall → nozzle-wide loops; tolerance reported, not passed; parts arranged, not turned; a kept file named for its part | Nowhere: `docs/slicer.md` (table at :96-101, :132-139). "Arranged on the bed and not turned" and "named for its part" are not in `docs/slicer.md` (grep for arrang/turned/named finds nothing). **Reference → `docs/slicer.md` *Slicing*: one sentence each** |
| A slicer seam record beside the firmware seam; personal-data lines; adoption-scope names OrcaSlicer (AGPL-3.0, run as a binary, never linked) | Governance record: already drafted (`DRAFT-slicer-seam.md`, `DRAFT-personal-data…` line 386, `DRAFT-constitution-adoption-scope`) |
| (part-iteration item 7) Slice follows the drawn variant, its record naming it | Reference → `docs/slicer.md` *Slicing* or *In the page*: one sentence. It is stated only in `docs/viewer.md:276-278` |

**Superseded decisions:**
- "Today a person slices elsewhere and brings G-code back" is history, and
  the plan's own.
- "Where the G-code is kept … open until built" was answered by its own
  *Decided after the server side*.

**Present-tense text that narrates this plan:**
- `docs/slicer.md:5`: "The owner decided how on 2026-10-10 ([the plan](../slicer-2026-10-10.md));
  this page says what was built". This is history and a plan link, and should
  be deleted (the page is already present tense).
- `docs/slicer.md:69`: "The owner decided (2026-10-10) that the start of a
  print is composed …". Rewrite inline: "The start of a print is composed
  from modules …".
- `apothecary/slicer/__init__.py:3`: "Decided with the owner on 2026-10-10
  (project/plans/…)". It is also stale: "the page's step comes later", but the
  page's Slice exists.
- `slicer/compose.py:4`, `slicer/profiles.py:5`,
  `slicer/orcaslicer_installer.py:52`, `vocabulary/word.py:42,48`,
  `widgets/machine.js:34`, `menu.py:1032`, `tests/test_menu.py:1467` and
  `tests/test_census.py:359` cite the plan.
- `parts/ender3/slicer.json` lines 6 and 10 give "the owner's decision of
  2026-10-10 (project/plans/slicer-…)" as a value's `source`. That is a data
  field, so cite `docs/slicer.md` instead.

### onboarding-2026-10-11.md: finished, retire

**What was checked in the code:**
- `apothecary serve --demo` is in place (`cli/server.py:77-108`,
  `apothecary/demo.py`).
- `walkthrough/00-getting-started.md` exists.
- The header's Docs link is there (`templates/fractal_viewer.html.j2:700`),
  as is Panels › Docs.
- Make selects its piece and a printer's Pin pins its mainboard
  (`docs/viewer.md:135`, `:146-152`).
- `apothecary test run` is the ordinary command (`CLAUDE.md`,
  `CONTRIBUTING.md:38`).
- Browser tests use only `--start-server` or `--base-url`
  (`CONTRIBUTING.md:38-40`).
- `tests/e2e/picture_drift.py` warns in CI (`pytest.yml:114-118`) and never
  fails.
- `tests/e2e/test_onboarding.py` exists.

**History line:**
`- 2026-10-11 — Onboarding at the top of the stack: a newcomer's path, the docs, the suites and the pictures reviewed; serve --demo, a Getting started page, one ordinary test command, pictures held to their captions.`

| Decision still true | Home |
|---|---|
| `serve --demo`: a state folder of its own, an idle simulated Ender on printer_1's mainboard, a simulated ESP32, scripted firmware tools; slices with a real OrcaSlicer when installed; a banner | Nowhere: `serve --help` (`DEMO_HELP`), `docs/viewer.md:36-38`, walkthrough 00 |
| Make selects the piece it made; Add here selects the camera | Nowhere: `docs/viewer.md:135` |
| A printer's Pin pins its mainboard and says so | Nowhere: `docs/viewer.md:146-152` |
| A Docs link in the header, ring-backed by Panels › Docs | Nowhere: `docs/viewer.md:31-33` |
| Walkthrough 00 is the newcomer's page; the README's *Start here* and `apothecary --help` point to it; page 01 onward is the library's tour | Nowhere: `docs/README.md` walkthrough table, `CLAUDE.md` |
| `apothecary test run` = unit suite + walkthrough, the browser part in its own pytest; `test all` adds every browser test; `pytest -q` the inner loop | Nowhere: `CONTRIBUTING.md`, `CLAUDE.md` |
| A browser test uses only its own server or one named on purpose | Nowhere: `CONTRIBUTING.md:38-40` |
| Pictures deterministic (edges clear of faces, `settled()` before every picture, the simulated bed seeded by place, fixed-size blanks, every STL built first); CI warns, never fails, on a picture drifting past a tolerance | Nowhere: `tests/e2e/picture_drift.py` docstring, `tests/e2e/README.md:68-90` (`settled`, blanks). Check: `tests/e2e/README.md` does not name `picture_drift.py` (grep found nothing). **Reference → `tests/e2e/README.md`, one line naming the warning step** |

**Superseded decisions:** none.

The *What the review found* section is dated narrative, and stays in the
plan. No retrospective is needed, because the plan is itself the dated record.

Present-tense citations: `tests/e2e/test_onboarding.py:2`,
`tests/test_cli_guidance.py:3` ("the onboarding plan, 2026-10-11") and
`tests/test_census.py:387`.

### rust-2026-10-08.md: finished as decided, retire

**What was checked in the code:**
- Firmware toolchain modules: `apothecary/firmware/modules/`,
  `toolchains.py`, `rust_installer.py`.
- espup is not run. The installer lays out archives "as espup lays them
  out" (`rust_installer.py:13-30`).
- `parts/esp32_blink/rust/` exists.
- `<name>@<toolchain>` naming (`firmware/models.py:103`).
- Panels › Bench › Install is a ring of modules (`docs/viewer.md` *The
  ring*).
- `crates/apothecary-core` and `crates/apothecary-service` are stubs.
- `apothecary kernel-reference` and `tests/test_kernel_comparison.py` exist.

The plan's own end state was firmware built, the kernel researched, and the
service and core stubbed. All of it holds. Two open questions are not
scheduled work:
- the service's first job;
- whether to try a kernel.

The crates READMEs already state both as open, so nothing open is lost by
retiring the plan.

**History line:**
`- 2026-10-08 — [Rust](../rust-2026-10-08.md): firmware in Rust for the ESP32 behind modular toolchains, a Rust geometry kernel researched and compared by numbers, a Rust service and core stubbed.`

| Decision still true | Home |
|---|---|
| The first board is the classic ESP32; Rust `esp32_blink` says what the Arduino one says; esp-hal, espflash, Xtensa Rust | Nowhere: `docs/firmware.md` *Rust for the ESP32* (:185-194) |
| Toolchains are modules behind one interface; a family or language added is a module | Nowhere: `docs/firmware.md:30-32`; governance record `DRAFT-firmware-toolchain-seam` |
| A Rust sketch lives with its part, a Cargo project with `firmware.json` | Nowhere: `docs/firmware.md:109-118` |
| Fetched at install time only and vendored; builds run `cargo --offline`; tool lookup: env var, tools dir, `PATH` | Nowhere: `docs/firmware.md:197-243`, `:54`; `DRAFT-personal-data…` lines 161-173, 266-273, 385-388 |
| Nothing is flashed to a real board by a test; the bench's ESP32 is a bench-checklist step | Nowhere: `docs/firmware.md:620-630`. Reference → the bench runbook (to be made) for the step itself |
| Ports: each module brings its own; Rust finds ports with pyserial and listens itself | Nowhere: `docs/firmware.md:23`, `:55-56`; `DRAFT-firmware-toolchain-seam` §6 (revised in place, commit `271f873`, line 136) |
| espup dropped; apothecary fetches and checksums the archives itself | Nowhere: `docs/firmware.md:212-218`, `rust_installer.py` docstring |
| Naming: `<sketch>@<toolchain>` everywhere a sketch is named; a node expecting `esp32_blink` matches either build | Nowhere: `docs/firmware.md:122-126`, `firmware/models.py:103` |
| Install is a ring of the toolchain modules | Nowhere: `docs/viewer.md` *The ring* (Panels › Bench › Install) |
| Pins move by hand in a commit that re-runs install and offline build; no cargo licence gate yet | Nowhere: `docs/firmware.md:252-258`, `rust_installer.py:40-47`. **The docstring ends "(The owner's decision of 2026-10-10, project/plans/rust-2026-10-08.md.)"**; delete that sentence in area 3 |
| Install flags install only what they name; `check` and the Bench say what is installed | Nowhere: `docs/firmware.md:201-204` |
| No absolute build path (so no user name) in a flashed image | Nowhere: `docs/firmware.md:245-250` |
| Arduino `esp32_blink`: a hello every ten blinks | Nowhere: `docs/firmware.md:194` |
| The service and the core: crates that build and do nothing; neither in the wheel nor run by the suites | Nowhere: `crates/*/README.md`, `docs/README.md` *The Rust workspace*, `Cargo.toml:1-3` |
| The comparison (corpus, measures, adapter) and `kernel-reference` stay in the package beside `census` | Nowhere: `docs/README.md:56-59`, `apothecary/kernel_compare.py` docstring |
| The service's first job stays open until it is built; its README names both candidates | Nowhere: `crates/apothecary-service/README.md` *What it is for* |
| A kernel whose build fetches something (manifold-csg's cmake clone) is settled when tried: the fetch drafted into the personal-data record, or the source vendored at install | Reference → `crates/apothecary-service/README.md`, one sentence under the renderer candidate. Not stated anywhere present-tense (only in this plan and the spike) |

**Superseded decisions:**
- *Firmware in Rust* names "espup" for installing Xtensa Rust. Its own
  *Decided after the firmware build* §2 reversed that. The present docs say
  "espup itself is not used" (`docs/firmware.md:217`).
- "only arduino-cli and esptool open a devkit's port" was the toolchain-seam
  record's rule. §1 here reversed it, and the amendment is drafted.

**Present-tense links to this plan:**
- `crates/apothecary-core/README.md:6` and
  `crates/apothecary-service/README.md:5`: "a stub for [the Rust plan]
  ("Planned and stubbed only")".
- `Cargo.toml:2`, `docs/firmware.md:638` ("the toolchain modules extend the
  first ([rust-2026-10-08.md])"). Cite the record instead.
- `apothecary/firmware/rust_installer.py:47`,
  `tests/e2e/test_the_firmware_loop.py:6` and `tests/test_census.py:315`.

### rust-geometry-kernels-2026-10-09.md (spike): finished as research, retire

The question it asked has an answer: which kernel to try first, and why. No
kernel is wired in. `apothecary/kernel_compare.py` holds no kernel by design,
and `tests/test_kernel_comparison.py` skips until one is. Trying
`manifold-csg` is not scheduled; it waits on the service getting the renderer
job (`crates/apothecary-service/README.md`). So nothing in the spike is open
work. It is a dated survey, which a present-tense page may cite *as* the
dated survey. Its prose about crates is external and dated ("as the
registries showed them that day"), which §4 of the rule allows.

**History line:**
`- 2026-10-09 — [A Rust geometry kernel](../rust-geometry-kernels-2026-10-09.md): a spike surveying which Rust kernel could render scenes to STL without OpenSCAD (Manifold bindings, csgrs, boolmesh, truck, Fornjot, OCCT) by licence, build, coverage and maturity; Manifold's bindings first.`

| Decision still true | Home |
|---|---|
| A kernel must cover the eleven scene nodes; OpenSCAD's spheres and cylinders are polygons, so an adapter builds primitives as OpenSCAD does or says which it measured | Code docstring: `apothecary/kernel_compare.py` (the corpus and protocol). One sentence on "the reference's primitives are polygons" belongs there; it is not stated now |
| How it would be called: a binary taking scene JSON and writing STL, called by `subprocess` like OpenSCAD, fetched at install time; not a PyO3 library first | Reference → `crates/apothecary-service/README.md` *What it is for* (the renderer bullet): one sentence on the calling shape |
| The Rust side owns the translation `render()` does (fn → facets, Rotate's two forms, Cylinder's radii rule, Import's order, implicit top union); `jscad.py` is the precedent | Code docstring: `kernel_compare.py` adapter protocol, one line pointing at `jscad.py` |
| Which to try first: `manifold-csg` (same algorithm as the reference, every node, Apache-2.0 OR MIT; cost: C++ build and a first-build network clone); second `csgrs` 0.20.1; not truck, Fornjot, OCCT | Nowhere: `crates/apothecary-service/README.md:20-24` already names Manifold through its Rust bindings first. The *why* stays in the dated spike, cited as such |
| A Rust dependency needs the licence check extended: Rust in the job, `cargo license --json` against the same allowlist; `Apache-2.0 OR MIT` passes, MPL-2.0 is on the list, LGPL-2.1 needs a decision | Nowhere: `crates/apothecary-service/README.md:27-33` states the CI job. The LGPL point is the open-license record's (`DRAFT-open-license-exclusion-and-upstream-remediation`) |

**Superseded decisions:** none.

**Present-tense links to this spike:**
- `docs/README.md:58` ("([the spike](../rust-geometry-kernels-2026-10-09.md), …)").
  Keep it, but say "the 2026-10-09 survey".
- `crates/apothecary-service/README.md:22` ("on one of the kernels in [the
  kernel spike]"). Keep it, dated.
- `apothecary/kernel_compare.py:3` and `apothecary/cli/kernels.py:32` (the
  `--help` docstring of `kernel-reference`). A dated survey cited from a
  `--help` text reads as current. Rewrite it as "the question a Rust kernel
  answers (the 2026-10-09 survey in project/plans)", or drop the path from
  `--help`.

### part-editing-in-the-browser-2026-09-27.md (spike): finished, retire

**What was checked in the code:**
- Iterations 1–3 are marked *Landed* in the spike itself, and the code
  bears them out:
  - `openscad_installer.py`;
  - `projects/parts/variants.py`, `openscad_messages.py`,
    `customizer.py`, `drafts.py`, `saved.py`, `routes/part_edits.py`;
  - `static/widgets/scad_editor.js`;
  - the vendored CodeMirror with its README.
- Iteration 4 (handles) is not built. part-iteration's *The next phase*
  carries it ("Handles in the 3D view (the spike's fourth iteration)").
- Option C (wasm in the page) is a standing "not now".

The spike has no open work of its own. **`project/todo.md:14` still lists it under
*Open in this repository*** ("a spike with a recommended order"), which is
stale. Delete that line.

**History line:**
`- 2026-09-27 — [Designing a part from the browser](../part-editing-in-the-browser-2026-09-27.md): a spike measuring the part loop, OpenSCAD 2021.01 against a Manifold snapshot, and what other tools do; fast renders, parameters from the SCAD, then an editor in the page.`

| Decision still true | Home |
|---|---|
| The fast path may depend on an OpenSCAD development snapshot; the CLI installs the newest meeting a part's floor or one pinned by date; `apothecary check` names each part's OpenSCAD and whether it has Manifold | Nowhere: `README.md:61-75`, `docs/parts-authoring.md:241-243`, `openscad_installer.py` docstring |
| A snapshot download is a tool fetch written into the personal-data record before the code lands | Nowhere: `DRAFT-personal-data…` §2 (line 164) |
| A saved edit is a variant in git: a ref of the part's own (`refs/apothecary/variants/<part>/<name>`), built with plumbing, never touching the working tree, the index or the branch; listed from the refs; making one the source is a merge the person does | Nowhere: `saved.py` docstring, `docs/parts-authoring.md:200-212`, `docs/viewer.md` *The SCAD editor* |
| A content-addressed cache of variants keyed on SCAD, includes, overrides, OpenSCAD version and backend; two tabs never race | Nowhere: `projects/parts/variants.py` docstring ("two tabs applying different values never write the same file. A changed include is a different key") |
| OpenSCAD's messages parsed to `{line, message}` for 2021.01 and snapshots; errors marked on their lines | Nowhere: `openscad_messages.py`, `docs/viewer.md` |
| A newer request from the same page cancels the older run; the check waits for the controls to rest | Nowhere: `docs/viewer.md` *The part editor*, `api.py` generate route |
| Every part gets controls: the `Params` model, else the SCAD's customizer parameters where this OpenSCAD can list them (not 2021.01) | Nowhere: `docs/parts-authoring.md:168-186` |
| A vendored CodeMirror 6 with a small OpenSCAD mode, not Monaco | Nowhere: `apothecary/static/vendor/codemirror/README.md` |
| A Python-geometry part shows its generated SCAD read-only; a draft or save of it is a 403 | Nowhere: `docs/parts-authoring.md:228-230`, `docs/viewer.md` |
| **Not now: OpenSCAD compiled to wasm in the page**: it duplicates the server, puts GPLv3 object code in the page, and needs `wasm-unsafe-eval` in the CSP; revisit only for a static export, after the licence review | **Not stated in any present-tense text** (grep for wasm/WebAssembly outside plans finds only a test fixture). Reference → `docs/parts-authoring.md`, one sentence under *Editing a part's SCAD* ("OpenSCAD runs on this machine's server, never in the page: …"), or a governance record if the owner wants it binding |
| Handles bound to one length parameter, writing the parameter, never the source | Stays in the open part-iteration plan (*The next phase*) |

**Superseded decisions:**
- "**One editor, tethered to the part**, that also opens a shape found in a
  picture" (*Decided*, 2026-09-27). The editor is in Selected, floated or
  fullscreen (ui-flows, *Decided while building*). A made piece's SCAD is
  read only and its editor drives its model (part-iteration, *A part whose
  SCAD is generated*). No present-tense page repeats the tethered version.
- "a render after a second of quiet" (iteration 3) became 300 ms after a
  passing check (part-iteration item 9). **It leaked into
  `docs/README.md:30`.**
- "its parameters in `<stem>.variant.json` beside the SCAD" (iteration 3,
  *Landed*, and *Decided*: "commits the edited SCAD and its parameters") was
  replaced by part-iteration's *The text is the truth*: a variant's values
  are its SCAD's assignments, and the file is read only for older saves
  (`saved.py:33-41`). **It leaked into `docs/parts-authoring.md:200-204`**
  ("`POST /parts/{name}/saved` with `{name, scad, params}` commits the SCAD,
  and the parameters as `<stem>.variant.json` beside it"). That text is now
  stale and needs an inline rewrite in area 1. Its "params_in:
  part-description is the aim" sentence (:209-212) is still true
  (`saved.KEPT_IN`, default `"text"`).
- "The viewer starts `committed` from the model's defaults" (the loop
  today) is history, and was fixed by `GET /parts/{name}/state`.

**Present-tense links to this spike:**
- `project/todo.md:14`.
- `apothecary/projects/parts/saved.py:5-6` ("decided 2026-09-27, see
  project/plans/part-editing-…").
- `apothecary/routes/part_edits.py:5`, `apothecary/menu.py:1214` ("the
  part-editing spike's decision").

### pictures-in-the-world-2026-09-26.md: open, split it

**What is built:**
- Phases 0, 2, 3 and 4, by its own header.
- `vision/views.py` (the view store, host and floor, provenance,
  `forget_made`), `routes/views.py`, `static/picture_marks.js` and
  `pictures.js`.
- The made-piece overlap wrapper (`site_store.py:68-79`).
- `NO_STORE` on picture routes (`routes/pictures.py:285`).
- `census.TAKEN_BACK`.

**What is open:**
- **Phase 1, gathering leaves core.** `apothecary/gathering/` is still in
  the package, and `pyproject.toml` has no `photos` extra. It is also
  `project/todo.md:23-33` (*Next round*).
- **Phase 7, the old doors closed.** `POST /photos`, `GET /photos/{name}`,
  `DELETE /photos/{name}` and `GET /photos/{name}/picture` still answer
  (`api.py:1698-1811`). `vision/shelf.py` exists, and `apothecary photo
  view` is still a command (`cli/photo.py:302`).

**Contradiction to settle.** Phase 6 (Selected tethered to the selection) is
called "not built: Selected stays in the one rail" in the plan's own
header. `project/todo.md:15` lists it as still open. The code has no tether at all
(`panels.js` has no tether or leader code), and the consolidation's *one
rail* decision overtook it. **Recommend the owner confirms Phase 6 is
dropped**; then delete it from `project/todo.md:15`.

**Split:**
- Keep a short open plan, either "pictures-in-the-world, the rest" or the
  existing file cut down, holding Phase 1 (with *For a person*'s
  how-gathering-leaves-core question) and Phase 7.
- Retire the rest under the History line below. It is 767 lines, and most
  of its text is the *design walk* of a model that the code docstrings now
  state.

**History line:**
`- 2026-09-26 — [Pictures in the world](../pictures-in-the-world-2026-09-26.md): a picture pinned at a place as a view, its shapes made into pieces standing there, every surface of the camera panel given a home in the world (Phases 0 and 2–4; Phase 5 overtaken by the consolidation).`

| Decision still true | Home |
|---|---|
| A picture enters the world only as a view at a host (a root structure with a footprint, not a made piece, not a camera) or the floor; a view is data attached to a place, not a node; SCAD, STL, validation and jobs never see one | Nowhere: `vision/views.py` docstring. Reference → `docs/pictures.md` (to be made) |
| The floor is a selection beside the site, not a node (`@floor`, `host: ""`); reached by the canvas ring's Pictures › Floor | Nowhere: `vision/views.py`, `docs/viewer.md:127-128` |
| No verb switches the site as a side effect | **Not stated in present-tense text or in `DRAFT-one-screen`** (the plan proposed it for §1). Governance record → `DRAFT-one-screen` §1, or `docs/viewer.md` one sentence |
| A piece made from a shape is a root structure of the same site, standing where the shape was seen; overlap-checked in every site; an unsized shape is never made | Nowhere: `vision/views.py` docstring, `site_store.py:68-79` |
| A piece's provenance (picture, host, camera, shape index, a copy of the shape, extent as made, word, finder, scale) kept outside the site store, so it finds its outline after the view is gone | Nowhere: `vision/views.py` docstring |
| Already-made shapes decided by the recorded extent, not the live footprint; Make all skips them and says how many | Nowhere: `vision/views.py` docstring (:18-26, "the extents an already-made shape is read against") and `Extent` (:187). Reference → `docs/pictures.md` for a reader |
| Cascades: forgetting a kept picture unpins its views and leaves pieces marked; Purge does it for every kept one, never the folder's own; unpinning never deletes a picture; Reset clears made pieces and the made map | Nowhere: `DRAFT-personal-data…` §6 (lines 296–301), `vision/views.py:722-769` |
| Picture lists in the ring are the seven newest; the eighth cell acts on the one chosen in its panel | Nowhere: `apothecary/menu.py:797-800`, `widgets/picture_list.js` |
| Kept rows' take-back buttons (Unpin, Forget) are the one control no ring backs (`census.TAKEN_BACK`) | Nowhere: `apothecary/census.py:572-590`, `DRAFT-rad-host-integration` lines 118–124 |
| No new ring shapes: the floor is reached from Pictures › Floor, a shape from its host's Picture; Make, Make all, Drop carried by the server | Nowhere: `DRAFT-rad-host-integration` lines 132–160, `menu.py` `CARRIED_BY` |
| Views are in memory until the record says what "this machine" is | Nowhere: `vision/views.py` docstring; the question is `project/todo.md:50-53` |
| Nothing picture-shaped is stored in the browser, its HTTP cache included (`no-store`) | Nowhere: `routes/pictures.py:285`, `DRAFT-personal-data…` §6 |
| The browser offers another finder only where one can read the picture | Nowhere: `menu.py:919` (Find shapes › the other finders) |
| *Not in this plan*: merging `cameras.json` and firmware bindings; a look's offset on its host; pictures upright on a wall; looks below the root; persistence across restart; `photo find` outside the picture root | These stay in the dated plan. "Pictures upright on a wall" is still a non-goal (cameras-and-clutter, *Offered and not chosen*) |

**Superseded decisions (do not carry into present-tense docs):**

| Earlier decision here | Reversed by |
|---|---|
| "a **look**" (the word), Camera › Look, Camera › Keep | consolidation, *Words*: **view**, **Take picture**, **Find shapes**; Keep is gone |
| **Kept** as one panel (Phase 5), the §6 list | consolidation: Site's **Pinned** and the **Pictures** tab (`test_census.py:42` still narrates "The Kept stub (the pictures plan's Phase 5…)", which is history for area 4) |
| A camera is a **badge** at the structure it is pinned to, in `cameras.json`; Pin here / Unpin; "a host holds at most one camera" | cameras-and-clutter: a camera is a part (`camera_N`) added by Add here and taken away by Remove; two at one place show as an overlap |
| A look's scale is the one width; "the last width typed is its camera's default" (`mm_across` on the camera) | cameras-and-clutter: the first width typed teaches the camera's **field of view**; a camera's views are sized at once through a pinhole (`vision/views.py`) |
| "a camera that looks sideways" not in this plan; a picture is always a view from above | cameras-and-clutter: turn and tilt, a picture landing on the first upward-facing surface |
| Phase 6, Selected tethered to the selection | consolidation, *one rail* (see the contradiction above) |
| "*pin* is the UI's one verb pair" (cameras, boards and pictures alike) | cameras-and-clutter: a camera is added and removed, not pinned (`docs/viewer.md:133`, `census.TAKEN_BACK` "pinned-camera-remove") |
| "a made piece is edited by its parameters only and **never saved as a variant**" | Its own *Decided by the owner (2026-09-27)* reversed it ("a made piece … may be saved as a git variant"). Then **part-iteration** ("a part whose SCAD is generated (the snowplow, a made piece) stays one way") and the code (`menu.py:1238-1242`: Save only for a part from the parts folder) went back to "no Save". **`DRAFT-personal-data-stays-on-the-device` §6 (line 299-300) still says "a made piece is a part, and is saved, varied and committed as a part is"**, so the record inherited the reversed decision. The owner should edit the record or the code |
| The part editor "tethered to the part" opening a piece | ui-flows: in Selected (see the spike) |

**Present-tense links to this plan:**
- `project/todo.md:15`, `:29`.
- `apothecary/static/widgets/picture_list.js:9` ("the pictures plan's Phase
  1"). This one is legitimate as open-work pointer while Phase 1 is open;
  it moves to `project/todo.md`'s wording once the plan splits.
- `apothecary/census.py:578`, `tests/test_census.py:42`,
  `tests/test_menu.py:1110`, `tests/e2e/test_picture_in_the_world.py:10`
  ("Phase 4 of the pictures plan pins it by a drop instead") and
  `tests/e2e/test_site_panel.py:9`.

### photo-finders-local-models-2026-09-21.md: open, stays

The plan says of itself "Nothing in this page is built", and the code agrees:
- there is no `apothecary/finders/` package;
- there is no `entry_points(group="apothecary.finders")`;
- there is no `Backend` descriptor, `recorded` finder, `LoopbackModel` or
  `aruco` finder;
- `vision/finder.py` still has the two built-ins, `stated` and `plain`.

What it shares with built work:
- The **cache** it specifies is built (`apothecary/vision/cache.py`, by the
  pictures plan's Phase 2). Its docstring cites "the photo-finders plan" for
  the key, which is legitimate while that plan is open.
- Its *Pends on* finder-choice row is answered: Find shapes › the other
  finders (`menu.py:919`).

**Still open:**
- Phases 0–5, all of them.
- Three *Pends on* rows:
  - the SPDX licence gate;
  - `CC0-1.0` on the allowlist (the org's);
  - whether a one-time model download counts as an install-time fetch
    (already `project/todo.md:54-55`).

**Should it split?** No. It is one unbuilt design. Its *The seam as it
stands* section is dated description and has gone partly stale. "The
browser's camera panel never sends one" is no longer true, since the camera
panel is gone and the ring offers finders. The section is exempt, but the
plan's next revision should refresh it before Phase 0 starts.

**Superseded decisions:** none reversed. The phrase "the pictures plan's
Phase 2 builds this cache" is now simply done.

**Present-tense links:**
- `project/todo.md:16` points to it as open work. That is correct while it is open.
- `apothecary/vision/cache.py:3` ("Keyed as the photo-finders plan keys
  it"). Acceptable while open, but better to state the key and drop the
  pointer, since the docstring already lists the four parts of the key.
- `project/validation/2026-09-21-local-integration.md:124-125` renders it as a
  docs-site check. That one is dated and exempt.

### part-iteration-2026-10-12.md: open, stays (split when this round merges)

**This round is built.** `build/timeless-docs` sits on `c67725a`, "Merge
build/pi-page into build/part-iteration". The checks behind that:
- **Tighten 1–10:**
  - `tests/test_failed_renders.py`;
  - `openscad install --extract` (`cli/openscad.py:53`, the installer's
    docstring);
  - `tests/test_param_controls.py`;
  - kept work in `sessionStorage` (template :902, :4535-4561);
  - F5, F6 and Ctrl+S in the SCAD editor (`docs/viewer.md` *The SCAD
    editor*);
  - `tests/test_following_a_variant.py`;
  - overlays and trash (`saved.py`);
  - `SCAD_CHECK_MS = 300` and `SCAD_RENDER_AFTER_CHECK_MS = 300`;
  - `GZipMiddleware` and `IMMUTABLE` (`api.py:206-209`, `:605`).
- **Improve:**
  - Recent applies, Undo and Redo;
  - Ghost and `GET /parts/{name}/compare`;
  - rename, duplicate, history, restore and trash;
  - `fitSelected` (`f`);
  - `tests/e2e/test_render_on_demand.py`;
  - `tests/test_render_queue.py`.
- ***Parameters and text, tied together*:**
  - `projects/parts/assignments.py`, `texts.py`,
    `tests/test_text_is_the_truth.py`,
    `tests/test_defaults_are_the_scad.py`, `tests/e2e/test_text_tied.py`;
  - Part › Variants › a variant's ring (`docs/viewer.md:142-143`).

`docs/viewer.md` *The part editor* and *The SCAD editor* already describe all
of it in the present tense.

**Still open: *The next phase, planned and not built*.** None of the
following is in the code:
- auto-apply: no toggle;
- clearance while iterating: no per-tab clearance check;
- a new part from a template: there is no `apothecary parts new` and no
  canvas New cell;
- handles in the 3D view;
- promote a variant to the part's source: `saved.KEPT_IN`'s
  `part-description` is still a stub;
- OpenSCAD's presets.

**Split:** once `build/part-iteration` merges, retire the plan's review
findings and its three *Decided* sections under the History line below.
Then either:
- move *The next phase* into a new dated plan (e.g. `part-next-<date>.md`);
  or
- move it into `project/todo.md` *Next round*, one line each, with the two owner
  questions ("auto-apply on by default?", "a new part as a ref or into the
  checkout?") under *For a person to decide*.

**History line (at the split):**
`- 2026-10-12 — [Iterating on a part, tightened](../part-iteration-2026-10-12.md): the part and SCAD loops reviewed and timed; errors as failed renders, real controls, kept work, OpenSCAD's keys, variants drawn where they stand, history, compare, variant management, and a part's controls and its SCAD as one text.`

| Decision still true | Home |
|---|---|
| An error at any level fails a render: drawn greyed with a "failed at line N" flag, never a variant, Save refused; the check runs with the staged values | Nowhere: `docs/viewer.md` *The part editor* ("A failed render") |
| Extracting the snapshot is opt-in (`openscad install --extract`); `apothecary check` says how much faster | `openscad install --help` and `openscad_installer.py` docstring say it. Reference → `README.md`'s OpenSCAD list (:66-69), one clause for Linux x86_64. `README.md` does not mention `--extract` now |
| Real controls: a number box beside each slider, integer steps, the customizer's step, enums as choices, a nested model as a group, captions | Nowhere: `docs/viewer.md:216-228` |
| Units declared on the field: `json_schema_extra={"unit": …}` on a model's field, or the customizer comment's unit word; nothing shown where none is declared | The customizer half is in `docs/parts-authoring.md:154`. **The model half is only in `projects/parts/params.py:68,310`.** Reference → `docs/parts-authoring.md` *Adding a parameter*, one sentence |
| Work kept per tab: draft and staged numbers in the tab's storage, offered back on reload; leaving warns; each part keeps its editor and undo | Nowhere: `docs/viewer.md:285-294`. **Governance:** `DRAFT-personal-data-stays-on-the-device` §6 (line 286) says the browser's `localStorage` "holds a panel layout" and names no other browser storage. The page now also keeps SCAD drafts and a made piece's or a camera's staged numbers in `sessionStorage`, and a hint-seen flag in `localStorage` (template :1166, :4535-4561). The record should say so |
| OpenSCAD's keys in the editor only: F5 check, F6 / Ctrl+Enter render, Ctrl+S save | Nowhere: `docs/viewer.md` *The SCAD editor*, *Keys* |
| A variant is drawn where it stands; the envelope line amber with the difference; below-the-floor flagged | Nowhere: `docs/viewer.md:270-278` |
| Slice and the checklist follow the drawn variant; the checklist reads the pinned printer's build volume | `docs/viewer.md:276-278` says it. Reference → `docs/slicer.md`, one sentence (see slicer) |
| The merge advice names the repository the ref lives in; a submodule's part saves an overlay in the superproject; an edit of the upstream file is refused; drafts beside a submodule's part are ignored there | Nowhere: `saved.py` docstring, `docs/viewer.md:328-339`, `docs/parts-authoring.md:135-145` |
| The SCAD loop: check 300 ms after typing, render ~300 ms after a passing check, a newer edit cancels it; the cache keyed on compiled CSG, so a comment-only edit draws at once; a stale render says so | Nowhere: `docs/viewer.md:303-316`. **Stale elsewhere: `docs/README.md:30`** |
| Lighter: binary STLs; immutable variant URLs; gzip; Regenerate folded into Apply; Download SCAD downloads the edit; a made piece's Apply redraws only the piece; Apply disabled up front where this OpenSCAD cannot build | Nowhere: `variants.py` docstring, `api.py:206-209`, `docs/viewer.md:229-230`, `:316-318`, `:297-299` |
| History and undo, Recent applies; Ghost and Compare; rename, duplicate, history, restore; Delete to `refs/apothecary/trash/`, emptied only by a confirmed step | Nowhere: `docs/viewer.md` *The part editor*, *The SCAD editor*; `saved.py` docstring |
| Fit-selected (`f`, Part › View › Fit) keeps Selected open; the world drawn only on change; a bounded render queue, "queued" shown | Nowhere: `docs/viewer.md:281-283`, `:88-92`, `:244-246` |
| The text is the truth both ways; one undo history; values never passed on the side; a variant's SCAD carries its values; older variants have theirs written in when drawn | Nowhere: `docs/parts-authoring.md` *In the page, the text is the truth*, `docs/viewer.md:194-214`, `saved.py` |
| A part's default is its SCAD as saved; a model still checks values; a model default disagreeing with the SCAD's literal is flagged by `apothecary problems` | Nowhere: `docs/parts-authoring.md:135-145` |
| A computed assignment: a control showing its value, Replace or Keep it computed; only top-level assignments get controls | Nowhere: `docs/viewer.md:203-208`, `assignments.py` docstring |
| A part whose SCAD is generated (snowplow, made piece) stays one way, read only | Nowhere: `docs/viewer.md:213-215` |
| Every variant action has a cell (Part › Variants › name › …, Variants › Deleted) | Nowhere: `docs/viewer.md:141-143`, `:345-362` |

**Superseded decisions:** none of its own. This plan is what supersedes
ui-flows' "second of quiet" and "parameters file" and the spike's
`.variant.json`.

**Present-tense citations of this plan:**
- `saved.py:25`, `:151`; `projects/parts/assignments.py:3`;
  `projects/parts/texts.py:3`; `menu.py:1244`; `census.py:143`, `:159`,
  `:194`.
- `static/anchors.js:24`; `static/widgets/assignments.js:2-3`;
  `widgets/part_controls.js:3`; `widgets/scad_editor.js:34`;
  `templates/fractal_viewer.html.j2:893`, `:4121`.
- In the tests: `test_part_iteration.py:1`,
  `test_part_iteration_answers.py:1`, `test_part_loop.py:14`,
  `test_scad_loop.py:16`, `:677`, `test_render_on_demand.py:1`,
  `test_text_tied.py:1`, `test_defaults_are_the_scad.py:1`,
  `test_failed_renders.py:1`, `test_following_a_variant.py:2`,
  `test_lighter_and_faster.py:1`, `test_param_controls.py:1`,
  `test_render_queue.py:1`, `test_text_is_the_truth.py:1`, and
  `tests/test_census.py:400`, `:426`, `:452`, `:823`.

Most say "the part-iteration plan's X" as the reason, so when the plan
retires each should name the behaviour (e.g. "the text is the truth") and
drop the path. Several also narrate ("Before: 137 …", "what this round
adds", "since the part-iteration plan"), which is area 3 and 4 history.

### timeless-docs-2026-10-12.md: open, stays

This is the sweep itself. Its *Areas* list and "The inventory of each area …
follow below once read" are open by definition. Its *Decided with the owner*
section holds decisions that outlive the sweep, and the plan should hand
them on before it retires:
- **A finished plan retires to a dated History list in `docs/README.md`; its
  still-true decisions move to present-tense docs, a record, or the code's
  docstring.** Reference → `docs/README.md`, one sentence under the new
  *History* heading. Also `CONTRIBUTING.md`, beside the commit-message rule,
  so a contributor finishing a plan knows to retire it.
- **Retrospectives go to the governance corpus's `perspectives/`**, one dated
  file per area. That belongs in governance: the record itself or
  `governance/qm/perspectives/README.md`.
- **The gate joins CI after qm#136 is ratified.** That is a `project/todo.md` *For
  a person* line, since it waits on ratification.

**History line (when the sweep's last area merges):**
`- 2026-10-12 — [The documentation, swept](../timeless-docs-2026-10-12.md): every durable text brought under the record on durable text; each passage sent inline, to a reference page, to a retrospective, or deleted.`

## Validation records

### 2026-09-20-ender-bench.md

It is a dated record of what was verified on 2026-09-20 (the *What was
verified* table, *What the numbers say about the machine*), followed by a
checklist a person still runs.

**What I checked of the checklist's addresses.** They are relative to a
board's device ring inside the Machine. I verified them against
`apothecary/menu.py` (`_device_ring_on_top`, `control_options`, seats
8, 6, 2, 4, 9, 3, 1, 7):
- Link = 1 › Reset 6 gives ⌗16.
- Control = 7: Arm or Disarm ⌗77, Stop ⌗71, Jog 2 › Y+ ⌗728, Level 4 ›
  Probe ⌗748 and Read ⌗746, Print 9 › Send file ⌗794 and Pause ⌗796.

All of them are current. Section G's node-ring addresses (⌗28 Open, ⌗24
Query, ⌗22 Flash) match the Device ring (Open 8, Query 4, Flash 2).

| Instructions a person still runs | Belongs in a runbook? |
|---|---|
| *Manual checklist* preconditions: printer powered, bed clear, `apothecary serve`, opening the printer's Machine (by `?machine=`, Open, or its badge), the ring's addresses inside a Machine, a hand on the power switch | **Yes** → `project/bench-checklist.md` (to be made), *Before you start* |
| A. Link, no arm: the filament runout read, Reset board | Yes, same page |
| B. Arm and heat: the latch, bed and hotend set and off, fan, a refused 900 °C, the latch lapsing after 5 minutes | Yes |
| C. Motion: home, jog Y+ with the nozzle marker ahead of the poll, the four corner paper checks | Yes |
| D. Leveling: Probe bed (the port held, a jog refused), Mesh on and Read mesh; the seam never writes EEPROM | Yes. "The seam never writes EEPROM" is already a present fact in `docs/firmware.md`; the runbook links it |
| E. Print from here: `examples/gcode/dry-run-square.gcode` (it stays where it is; `tests/test_docs_site.py:162` serves it), an `M500` file refused, Print, Pause, Resume, Cancel, a run to the end | Yes |
| F. Stop and let go: E-STOP, Reset, Release, a terminal reopen without a boot banner, Reconnect | Yes |
| G. The ESP32's Rust `esp32_blink`: install, validate, Compile offline, Compile & upload, Query and Listen, comparing with the Arduino build, `ARDUINO_CLI=none` | Yes. `walkthrough/15-firmware.md:113`, `docs/firmware.md:625-630` and `tests/e2e/test_the_firmware_loop.py:24,183` then point to the runbook, not the dated record |
| "Anything refused, wrong, or slower …: note the time and the port, and download the comms log" | Yes, as the runbook's *When something fails* |

**What stays only in the dated record:**
- the *What was verified* table, with its timings and suite counts;
- the defects fixed on the day;
- *What the numbers say about the machine*: the 2.34 mm range, the tilt and
  the offsets. `parts/ender3/slicer.json` cites these as measurement
  sources, which is correct for a dated measurement.
- The paragraph about addresses "as they were on the day: Device › Open
  took Watch's cell (8) and Flash took Monitor's (2)". This is history; the
  runbook states the addresses as they are.

**Present-tense links:**
- `docs/firmware.md:632-634` ("is the seam against a real Ender mainboard,
  with a checklist for what needs control armed"). That would point to the
  runbook.
- `docs/slicer.md:62`, `parts/ender3/slicer.json:21,29,33,42,54,60`: dated
  measurement sources. Keep these.
- `project/todo.md:17` ("The bench checklist re-run on the one page … Its three
  screenshots are of the pages as they were on 2026-09-20"). The open item
  is real; it should name the runbook. The screenshot remark is history:
  delete it.
- `project/todo.md:40`, `walkthrough/15-firmware.md:113`,
  `tests/e2e/test_the_firmware_loop.py:24`, `:183`.

### 2026-09-21-local-integration.md

This is a dated handoff for `review/2026-09-26`. Its sections fall into
three kinds:

| Section | Still run? | Home |
|---|---|---|
| Intro, *How to walk it*, the two-server setup | Partly superseded: the "demo one" built by hand from `ARDUINO_CLI=…`, `APOTHECARY_SERIAL_ENGINE=simulated` etc. (§5's block) is what `apothecary serve --demo` now does (onboarding; `cli/server.py:77-108`). The demo's printer is idle, not "printing" | Stays dated |
| §0 *What the design review changed that you will notice* | No: history of a review ("it raised NotImplementedError before", "the docs refresh is `--refresh-docs` now", retired commands) | Stays dated; nothing moves |
| §1 Setup (`git status -sb # ## review/2026-09-26`, the pin `20e00bd`) | No: tied to a branch and a pin | Stays dated |
| §2 Personal data stays on the device: the four refused connections, `serve --host 0.0.0.0` refused, uvicorn refused at the socket, the `curl` Host/Origin/Sec-Fetch checks, the LAN refusal, `arduino-cli.yaml`, the proxy-free child, `strace`, the picture-root refusal, `drwx------`, `tests/test_stays_local.py` | **Yes**: a door-by-door audit a person can rerun after any change to the guard | **Runbook** → `docs/stays-local-audit.md` (to be made), or a section of the record's own *verification*. The record's §7 already names the tests; this is the hand-run half |
| §3 Geometry from elsewhere: the Ender and boards drawn on the bench, `parts import` of a brick and its refusals, the union limit | Partly: the import steps are a good smoke test, but `docs/geometry-from-elsewhere.md` and walkthrough 12 already hold them as present-tense text and a test-written page | Nowhere new. The union-limit check is in `docs/geometry-from-elsewhere.md` ("which the docs page names") |
| §4 One screen: the rail, tabs, `~`, ⇄, floating, problems, the ring, badges, `/firmware` redirects | No longer needed by hand: `docs/viewer.md` states each control, and the browser suite (`test_less_on_screen.py`, `test_site_panel.py`, `test_bench.py`, `test_one_machine.py`) holds them | Stays dated |
| §5 The camera and the pictures | Covered by walkthrough 12 and 13 and `serve --demo` | Stays dated |
| §6 The printer without hardware | Covered by `serve --demo` and walkthrough 13 and 15 | Stays dated |
| §6 With hardware: `firmware boards` not writing `inventory.yaml`'s cache; pin → relief and nozzle on the Ender's bed; **the picture-to-print loop with a real camera and the real board** | **Yes** | **Runbook** → `project/bench-checklist.md`, beside the Ender checklist (a section *The loop with real hardware*) |
| §7 The docs, §8 suites and gates | No: `CONTRIBUTING.md`, `walkthrough/09-preflight.md` and `apothecary preflight` hold these; the `git log … # six records` line is tied to a branch | Stays dated |
| §9 OpenSCAD on every platform: Linux x86_64 (FUSE and no FUSE), macOS (universal app, codesign Team ID, Gatekeeper, Rosetta), Windows x64 (zip, Defender), Windows on ARM (refused), Linux arm64 (source build: apt line, timings, no fetch during build, `--jobs 1` on 2 GB) | **Yes**: CI covers none of these platforms, and the steps prove an install on each | **Runbook** → `docs/openscad-platforms.md` (to be made), or a *Proving an install on each platform* section of `README.md`'s OpenSCAD part. The same shape will serve `slicer install`, whose platforms are the same |
| *Results* table | Part of each run | It goes with each runbook as a fill-in table, or stays dated |
| *For a person*: ratify the records on qm#121, bump the governance pin, rad#7 | Open acts | → `project/todo.md` *For a person to do* (the same three as the cleanup triage's leftovers) |
| *Hardening, after this branch*: GPG `.asc` checks on OpenSCAD and arduino-cli downloads, macOS signature and Team ID in code, Windows Authenticode, source-build tarball integrity, nested submodules and `.1` builds, Windows on ARM natively | **Open work tracked nowhere else.** `openscad_installer.py:30` and `:39-41` state two of them as present limits; `project/todo.md` has none of them | → `project/todo.md` *Open in this repository*, one line each (or one line "installer hardening", listing them) |

**Present-tense links:**
- `tests/test_site_api.py:203` ("the one violation
  project/validation/2026-09-21-local-integration.md's …"). This is a test
  explaining itself by a dated checklist; area 4 should state the fact.
- `docs/README.md:80`.

## Superseded decisions, in one place

Each row below is a decision an earlier plan made and a later one reversed.
**Leaks** marks present-tense text that still carries the earlier decision.

| Earlier decision | Where | Reversed by | Leaks into present-tense text |
|---|---|---|---|
| Popups tethered to an anchor, with a leader (the Machine, a devkit's serial, a piece's properties) | one-screen; consolidation *End state* | consolidation *one rail*; cameras-and-clutter (the Machine in the strip) | **`DRAFT-one-screen` §2** (governance) |
| Selected tethered to the selection (Phase 6) | pictures | consolidation *one rail* | **`project/todo.md:15`** lists it as open |
| One Kept panel as the §6 list (Phase 5) | pictures | consolidation (Site's Pinned + Pictures) | `tests/test_census.py:42` narrates "The Kept stub" (history, area 4) |
| "Look", Camera › Look, Camera › Keep | pictures | consolidation *Words* | None found (`git grep` for "a look"/"looks" outside plans hits only ordinary English) |
| A camera is a badge pinned at a structure, kept in `cameras.json`; Pin here / Unpin; one camera per host | pictures | cameras-and-clutter | **`DRAFT-personal-data…` §6** still says "camera placements" and "a camera at a piece" (governance; check wording against `camera_parts.json`) |
| The last width typed is a camera's default `mm_across` | pictures | cameras-and-clutter (the first width typed teaches the field of view) | None found |
| A picture is always a view from above; no sideways camera | pictures *Not in this plan* | cameras-and-clutter (turn and tilt, first upward-facing surface) | None found |
| A made piece may be saved as a git variant | pictures, *Decided by the owner (2026-09-27)* | part-iteration (a generated SCAD stays one way); code has no Save for a made piece (`menu.py:1238-1242`) | **`DRAFT-personal-data…` §6 line 299-300**: "a made piece is a part, and is saved, varied and committed as a part is" (governance; the owner chooses which is true) |
| One editor tethered to the part | spike *Decided* | ui-flows (in Selected, floated or fullscreen) | None found |
| A SCAD edit renders "after a second of quiet" | spike iteration 3; ui-flows loop 2 | part-iteration item 9 (300 ms after a passing check) | **`docs/README.md:30`** (page 16's row) |
| A variant's parameters in `<stem>.variant.json` beside its SCAD | spike; ui-flows | part-iteration *The text is the truth* | **`docs/parts-authoring.md:200-204`** ("commits the SCAD, and the parameters as `<stem>.variant.json` beside it") |
| espup installs Xtensa Rust | rust *Firmware in Rust* | rust *Decided after the firmware build* §2 | None (`docs/firmware.md:217` says espup is not used) |
| Only arduino-cli and esptool open a devkit's port | `DRAFT-firmware-toolchain-seam` (record) | rust §1 (each module brings its own) | None: the draft was revised in place (commit `271f873`; §6, line 136: "a port is opened only by the toolchain module that found it") |
| The browser's camera panel never sends a finder | photo-finders *The seam as it stands* | pictures and consolidation (Find shapes › other finders) | None outside the dated plan |
| `localStorage` holds a panel layout (and, implied, nothing else of the page's) | `DRAFT-personal-data…` §6 | part-iteration item 4 (work kept in the tab's `sessionStorage`) and the hint bar's seen flag | **`DRAFT-personal-data…` §6 line 286** (governance) |

## Present-tense pages that link a plan as if it were current

### Markdown

| Page:line | What it says | Fix when the plan retires |
|---|---|---|
| `docs/README.md:58` | "the reference a Rust geometry kernel is compared with ([the spike](../rust-geometry-kernels-2026-10-09.md)" | Keep the link, labelled as the 2026-10-09 survey |
| `docs/README.md:61-80` | The whole *Plans and records* table lists 14 plans and 2 validation records beside the guides; one-screen and consolidation say "done", cameras-and-clutter "in four phases" | Replace with *Open plans* (pictures (split), photo-finders, part-iteration, timeless-docs) and a dated *History* list (the lines above, newest first); validation records under a dated *Records* list. The heading says "and records" but lists no governance records |
| `docs/README.md:30` | page 16 "rendered after a second of quiet" | Stale (not a link): "rendered once a check passes" |
| `docs/firmware.md:632-634` | the bench validation as "the seam against a real Ender mainboard, with a checklist" | Point to `project/bench-checklist.md`; keep the dated record as the measurement source |
| `docs/firmware.md:637-638` | "the toolchain modules extend the first ([rust-2026-10-08.md](../rust-2026-10-08.md))" | Cite `DRAFT-firmware-toolchain-seam`'s amendment; drop the plan |
| `docs/slicer.md:5` | "The owner decided how on 2026-10-10 ([the plan](../slicer-2026-10-10.md)); this page says what was built" | Delete (history) |
| `docs/slicer.md:69` | "The owner decided (2026-10-10) that the start of a print is composed …" | Inline: "The start of a print is composed …" |
| `docs/slicer.md:62` | the bench record as the firmware's source | Keep (dated measurement) |
| `project/todo.md:8` | "The order to take these in … is [the cleanup triage]" | Delete |
| `project/todo.md:14` | the part-editing spike as open work | Delete (finished) |
| `project/todo.md:15` | pictures "Phase 6 … and Phase 7" | Phase 7 only, once the owner confirms Phase 6 is dropped; link the split plan |
| `project/todo.md:16` | photo-finders | Keep (open) |
| `project/todo.md:17` | the bench checklist re-run, "Its three screenshots are of the pages as they were on 2026-09-20" | Point to the runbook; delete the screenshot remark |
| `project/todo.md:29-30` | "[The pictures plan]'s Phase 1 proposes an answer" | Keep while Phase 1 is open; link the split plan |
| `project/todo.md:40` | the bench record for the port-registry bench session | Point to the runbook |
| `crates/apothecary-core/README.md:6` | "a stub for [the Rust plan] ("Planned and stubbed only")" | "a stub: it builds and does nothing yet" (drop the plan) |
| `crates/apothecary-service/README.md:5` | the same | the same |
| `crates/apothecary-service/README.md:22` | "on one of the kernels in [the kernel spike]" | Keep, dated: "the 2026-10-09 survey" |
| `walkthrough/15-firmware.md:113` | "step G of the bench checklist (project/validation/2026-09-20-ender-bench.md)" | Point to the runbook. This page is written by `test_the_firmware_loop.py`, so the edit is in that test (:183) |
| `Cargo.toml:2` | "See project/plans/rust-2026-10-08.md ("Planned and stubbed only")" | Point to `crates/*/README.md` |
| `parts/ender3/slicer.json:6,10` | "the owner's decision of 2026-10-10 (project/plans/slicer-…)" as a value's `source` | `"source": "docs/slicer.md, What a slice is composed from"` |

`README.md`, `QUICKSTART.md`, `CONTRIBUTING.md`, `AGENTS.md`,
`tests/e2e/README.md`, `docs/viewer.md`, `docs/parts-authoring.md`,
`docs/models.md`, `docs/scene-json.md`, `docs/fitting-a-part.md` and
`docs/geometry-from-elsewhere.md` link no plan (`git grep` for `plans/`, "the
… plan", "the spike").

### Code, comments and tests (areas 3 and 4 will meet these)

These cite a plan by path or by name as the reason for the code. When the
plan retires, each should state the behaviour and drop the pointer. Most
also narrate who decided and when.

| Plan cited | Places |
|---|---|
| one-screen / consolidation | `census.py:67`, `:87`; `tests/e2e/test_bench.py:4`, `test_one_machine.py:3` |
| cameras-and-clutter | `tests/e2e/test_less_on_screen.py:1-2`; plus "the owner's decision of 2026-10-04" in `example_hierarchy.py:87`, `vision/camera_part.py` |
| ui-flows (the loops plan) | `menu.py:1224`, `:1230`; `routes/menu.py:214`; `widgets/scad_editor.js:3`; `tests/e2e/doc_capture.py:279`; `test_part_loop.py:1`, `:702`; `test_scad_loop.py:1`; `test_picture_to_print.py:2`; `test_the_firmware_loop.py:4`, `:14`; `tests/test_census.py:325`; `tests/test_the_walkthrough_is_named.py:46` |
| slicer | `slicer/__init__.py:3` (stale: "the page's step comes later"), `slicer/compose.py:4`, `slicer/profiles.py:5`, `slicer/orcaslicer_installer.py:52`, `vocabulary/word.py:42`, `:48` (a user-facing string: "with the printer's values (project/plans/slicer-2026-10-10.md)"), `widgets/machine.js:34`, `menu.py:1032`, `tests/test_menu.py:1467`, `tests/test_census.py:359` |
| onboarding | `tests/e2e/test_onboarding.py:2`, `tests/test_cli_guidance.py:3`, `tests/test_census.py:387` |
| rust | `firmware/rust_installer.py:47`, `tests/e2e/test_the_firmware_loop.py:6`, `tests/test_census.py:315` |
| rust-geometry-kernels | `kernel_compare.py:3`, `cli/kernels.py:32` (in `kernel-reference --help`) |
| part-editing spike | `projects/parts/saved.py:5-6`, `routes/part_edits.py:5`, `menu.py:1214` |
| pictures | `census.py:578`, `widgets/picture_list.js:9`, `tests/test_census.py:42`, `tests/test_menu.py:1110`, `tests/e2e/test_picture_in_the_world.py:10`, `tests/e2e/test_site_panel.py:9` |
| photo-finders | `vision/cache.py:3` |
| part-iteration (open) | 30-odd places, listed under part-iteration above |
| validation records | `tests/test_site_api.py:203`, `tests/test_docs_site.py:162` (serves `dry-run-square.gcode`; fine), `tests/e2e/test_the_firmware_loop.py:24`, `:183` |

`apothecary/vocabulary/word.py:48` puts a plan's path into a message a person
reads at run time (a refusal's text). That is the one place where the pointer
reaches a user, not only a reader of the source.

## The History list for `docs/README.md`, ready to paste

Below is the block for the finished plans, newest first. The open plans'
lines are added when they finish. pictures-in-the-world and part-iteration
get theirs at their split.

```markdown
## History

Plans and research that are finished, by date. Each is a dated record of what
was decided and why; what is still true of it is stated in the guides above,
the governance records, or the code it describes.

- 2026-10-11 — Onboarding at the top of the stack: a newcomer's path, the docs, the suites and the pictures reviewed; serve --demo, a Getting started page, one ordinary test command, pictures held to their captions.
- 2026-10-10 — [A managed slicer](../slicer-2026-10-10.md): OrcaSlicer behind a slicer interface, installed like OpenSCAD, the printer's profile kept with its part, print settings from what each part declares.
- 2026-10-09 — [A Rust geometry kernel](../rust-geometry-kernels-2026-10-09.md): a spike surveying which Rust kernel could render scenes to STL without OpenSCAD, by licence, build, coverage and maturity; Manifold's bindings first.
- 2026-10-08 — [The loops through the page](../ui-flows-2026-10-08.md): designing a part, editing its SCAD, firmware, and a picture to a print, each built out and held end to end by a browser test.
- 2026-10-08 — [Rust](../rust-2026-10-08.md): firmware in Rust for the ESP32 behind modular toolchains, a Rust geometry kernel researched and compared by numbers, a Rust service and core stubbed.
- 2026-10-08 — Cleanup, triaged: the open cleanup items sorted by kind and given an order, while the review branch was split into a stack.
- 2026-10-04 — [Cameras and clutter](../cameras-and-clutter-2026-10-04.md): a camera as a part of the site, pictures sized and taken from it, and less on the screen.
- 2026-10-03 — [Consolidation](../consolidation-2026-10-03.md): one page and one place per thing; Site and Selected over a strip of tabs, one Machine per board, the Bench, one Pictures panel, jobs over machine kinds.
- 2026-09-27 — [Designing a part from the browser](../part-editing-in-the-browser-2026-09-27.md): a spike measuring the part loop and what other tools do; fast renders, parameters from the SCAD, then an editor in the page.
- 2026-09-20 — [One screen](../one-screen-2026-09-20.md): the world as the one page, with anchors and panels in front of it, and the census as the meter.

### Records from the bench

- 2026-09-21 — [Local integration run-through](../../validation/2026-09-21-local-integration.md): a checklist for the review branch, section by section.
- 2026-09-20 — [Ender bench](../../validation/2026-09-20-ender-bench.md): the printer seam against a real Marlin board, and what the bed measured.
```

## `project/todo.md` lines this area produces

- **Delete**:
  - `:8`, the cleanup triage as "the order";
  - `:14`, the spike, which is finished;
  - `:15`'s "Phase 6", once the owner confirms it is dropped.
- **Edit `:17`**: "The bench checklist ([project/bench-checklist.md]) run on the
  one page with the Ender." Drop the screenshot remark.
- **Add under a new *For a person to do*:**
  - ratify the governance drafts (one screen, personal data, rad host
    integration, the firmware, G-code and slicer seams, the adoption-scope
    amendment) and bump the pin;
  - review rad#7;
  - close or rebase the Dependabot bumps once the stack lands;
  - after qm#136 is ratified, add `check_timeless.py` to CI and preflight.
- **Add under *For a person to decide*:**
  - whether pictures' Phase 6 (Selected tethered) is dropped;
  - whether a made piece may be saved as a variant (the record says yes,
    the code says no);
  - part-iteration's two owner questions, when its next phase moves here.
- **Add under *Open in this repository*: installer hardening.** That covers
  GPG `.asc` checks for OpenSCAD and arduino-cli, the macOS signature and
  Team ID checked in code, Windows Authenticode, the integrity of
  source-build tarballs, nested submodules and `.1` builds, and Windows on
  ARM natively. These come from the local-integration record's
  *Hardening*.
- **Add under *Next round*: part-iteration's *The next phase***, if the owner
  prefers `project/todo.md` to a new dated plan: auto-apply, clearance while
  iterating, a new part from a template, handles, promoting a variant to
  the source, and OpenSCAD's presets.

## Reference pages this area needs

| Page | New or extend | What it holds | From |
|---|---|---|---|
| `project/bench-checklist.md` | **New** | The present-tense runbook at the bench: before you start; A–F for the Ender (link, arm and heat, motion, leveling, print from here, stop and let go); G for the ESP32 (Rust then Arduino, `ARDUINO_CLI=none`); the loop from a picture to a print with a real camera and board; what to write down when something fails. Addresses as `menu.py` seats them today | Ender bench *Manual checklist*; local-integration §6 *With hardware* |
| `docs/pictures.md` | **New** (optional; the docstrings carry the model today) | Pictures, cameras, views and pieces for a reader: a host and the floor; a view is data at a place; Take picture and Find shapes; where a picture lands; the lens learned from the first width; one pinhole mapping; a piece's provenance and the already-made rule; forget, purge, reset; what is kept where (pointing at the personal-data record) | pictures *What each thing is*; cameras-and-clutter *A camera is a part*; consolidation *Words*; `vision/views.py`, `cameras.py`, `projection.py` |
| `docs/openscad-platforms.md`, or a section of `README.md` | **New** (or extend) | Proving an OpenSCAD install on each platform CI does not run: Linux x86_64 with and without FUSE, macOS (universal app, signature, Gatekeeper, Rosetta), Windows x64, Windows on ARM refused, Linux arm64 from source. The same shape applies to `slicer install` | local-integration §9 |
| `docs/stays-local-audit.md`, or the record's own verification section | **New** (or governance) | The doors checked by hand: outbound connections refused, binding refused, Host, Origin and Sec-Fetch answered 403, nothing on the LAN, the arduino-cli config, no proxy in a child, `strace`, the picture-root refusal, file modes; `tests/test_stays_local.py` as the automated half | local-integration §2 |
| `docs/README.md` | Extend | *History* (above); *Open plans*; one sentence that a finished plan retires here | timeless-docs *Decided* |
| `docs/parts-authoring.md` | Extend | Fix `:200-204` (`.variant.json` is gone; the values are in the text); a unit declared on a model field (`json_schema_extra={"unit": …}`); OpenSCAD never runs in the page (the wasm decision) | spike, part-iteration |
| `docs/slicer.md` | Extend | Slice follows the drawn variant; parts arranged and not turned; a kept file named for its part. Delete `:5` and rewrite `:69` | slicer, part-iteration |
| `docs/firmware.md` | Extend | `:632-638` point to the bench runbook and to the record, not to the plan | rust, the bench record |
| `tests/e2e/README.md` | Extend | A loop's test goes round twice through the page's controls and ring cells; name `picture_drift.py`'s warning | ui-flows, onboarding |
| `CONTRIBUTING.md` | Extend | A step's message names the next step; a finished plan retires to `docs/README.md`'s History | consolidation, timeless-docs |
| `README.md` | Extend | `openscad install --extract` for the fast start on Linux x86_64 | part-iteration item 2 |
| `crates/apothecary-service/README.md` | Extend | The renderer's calling shape (scene JSON in, STL out, a subprocess); a kernel whose build fetches is settled when tried (drafted into the record, or vendored at install) | rust-geometry-kernels, rust |

## Retrospectives this area needs

None of its own. Plans and validation records are dated documents, exempt
under §4. Each already *is* the narrative of its round ("What the survey
found", "What the review found", "Decided after Phase N"), and retiring a plan
keeps it in place under History. Moving that narrative into `perspectives/`
would duplicate it.

The other areas will produce narrative that points here. Those
retrospectives can **cite** these plans as their sources rather than
restate them:
- the census docstrings' before-and-after counts;
- "the owner's decision of 2026-10-04" in code;
- `test_census.py`'s phase-by-phase notes.

Three such retrospectives would cover them:
- "apothecary: one screen" (one-screen, consolidation, cameras-and-clutter);
- "apothecary: the part loop" (the spike, ui-flows, part-iteration);
- "apothecary: the bench" (the two validation records, rust, slicer).

## Suggested order

1. **Fix the two leaks of superseded decisions** in present-tense pages:
   `docs/README.md:30` ("second of quiet") and
   `docs/parts-authoring.md:200-204` (`.variant.json`). These are stale facts
   a reader acts on, and each is a one-line edit.
2. **`project/todo.md`**: delete `:8` and `:14`; edit `:17`; add the hardening line,
   the *For a person to do* items and the two decisions. It is short and
   read often, and it points at plans more than any other page.
3. **`docs/README.md`**: replace the *Plans and records* table with *Open
   plans* and *History* (the block above). Change `:58` to "the 2026-10-09
   survey".
4. **Retire the plans whose decisions need no new prose**, which is to say
   only the History line and the link fixes:
   - one-screen, consolidation, cameras-and-clutter, cleanup-triage, ui-flows
     and onboarding;
   - then rust and the kernel spike, with the two crates README sentences;
   - then the part-editing spike, with the `parts-authoring.md` wasm
     sentence and unit sentence;
   - then slicer, with the `slicer.md` sentences and `:5` and `:69`.
5. **`project/bench-checklist.md`**, from the Ender record's checklist and
   local-integration §6. Then repoint `docs/firmware.md:632`, `project/todo.md:17`
   and `:40`, and `test_the_firmware_loop.py:183`, which regenerates
   walkthrough 15. The platform and stays-local runbooks follow, if the
   owner wants them as pages.
6. **The pictures split**, after the owner answers Phase 6 and the made-piece
   question. `docs/pictures.md` comes with it, if wanted.
7. **The governance edits** go to the owner on the qm branch, not in this
   repository:
   - `DRAFT-one-screen` §2 (popups) and §7 (the plan as the order);
   - `DRAFT-personal-data…` §6 (camera placements, made pieces saved as
     variants, browser storage);
   - "no verb switches the site" for `DRAFT-one-screen` §1.
8. **part-iteration's split**, once `build/part-iteration` merges.
9. **The code and test citations** are areas 3 and 4's to do. They should
   follow step 4, so each retired plan's citations go in the same pass as
   its History line.
