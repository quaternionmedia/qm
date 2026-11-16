# One way of doing each thing: a plan

*Built: the ten slices, as a local stack of branches, each holding its test,
and the whole suite run once on the stack's top. Nothing here is pushed: the
owner decides when the stack goes.*

## What this plans

Apothecary has one way of doing most things, and beside some of them a second: a
fact kept twice, a dialect's rule written in the other dialect's module, a helper
copied into a package that could not import it, a shape standing in for an
identity, a name kept for a caller that is gone. Each costs the same thing: a
reader who finds one of the two believes it is the whole, and a change made to
one leaves the other saying something else.

This plan names each with where it is and what else it could be before calling
it a shim, says which one standard it folds into, and cuts the work into slices
that a test holds: each slice carries a test that fails on the code beneath it.
Three rules bound it. Nothing is pushed. A feature or an effort is removed only
with the owner's yes, and a shim that keeps a record readable is replaced only
by a migration the owner approves. The viewer's front end
(`apothecary/static/`, `apothecary/templates/`, `apothecary/menu.py`), the test
suite's layout, `tests/conftest.py` and CI are other sessions' ground and are not
touched; a test that holds code a slice changes is.

## What was found

A read of the package at main 1e12ec58 (`apothecary/`, `parts/`, the docs the
code cites), with the tests and production's state folder read and never
written. Each finding names its place and what else could explain it.

### A dialect's rule in the other dialect's module

| What | Where | What else it could be |
|---|---|---|
| GRBL's file rules: the M codes GRBL takes, the dwell bound in GRBL's unit, the `G29` refusal, and the `machine == "router"` branch that applies them | `gcode.py`: `GRBL_M_CODES`, `GRBL_DWELL_MAX_S`, `_not_grbl`, `check_gcode`; `grbl.py`'s own section header says "what a file may carry is gcode.check_gcode" | `gcode.py` holds the shared link, so the shared walker over a file's lines belongs there; the rules a dialect adds do not |
| The spindle bound, the trim router's | `gcode.SPINDLE_MAX_RPM`, imported by `grbl.py` and `cam/models.py`; Marlin's control list has no `M3` | a printer with a spindle or a laser; none here, and Marlin's dialect refuses `M3` typed at it |
| The link's objection pattern naming GRBL's `error:N` and `ALARM:N` beside Marlin's `Error:` and `!!` | `gcode.ERROR_RE`, matched in `GcodeLink.command` | the link closes an exchange on either dialect's objection before a board is identified (`M115` on a GRBL controller answers `error:20`), so one pattern with both words is the simplest correct thing; the cost is a dialect's words outside its module, and a third dialect editing `gcode.py` |

### One fact, kept twice

| What | Where | What else it could be |
|---|---|---|
| The kind of machine a board drives, stored beside the dialect it answered in, when every constructor derives it from the dialect | `PrinterInfo.dialect` and `PrinterInfo.machine`; `gcode.identify_printer` and `grbl.identify_router` set `machine` from their module's `MACHINE`; `dialects.Dialect.machine` carries the same | a dialect driving two kinds of machine, a laser on GRBL say; that kind would bring its own identification, and the field back with it |
| A board's identity, two ways: the one a pin, a flash record and a job store (its MAC, else its bridge's serial number, else its port) and the one a reading is kept under (the same, else `usb:vid:pid`) | `DeviceInfo.identity`, `devices.stable_identity`, `bindings.same_device`; `occupants.key_of` | slice 10 folds the first onto the second: one key, `models.board_key` |
| The words for a streamed job (`a print`, `a cut`) and which kinds stream, beside the registry of operations | `devices.STREAMED`, `devices.WHAT_HOLDS`; `jobs.Operation` | the registry is pure of the firmware package by design; the nouns could ride the `Operation` all the same |
| A kind of machine as a boolean | `api._machines_in(..., router: bool)`, the pair `printers_in` and `routers_in` | two conveniences over one function; the boolean is what stops a third kind |

### A helper copied where a package could not import it

| What | Where | What else it could be |
|---|---|---|
| Where the state folder is, and how a folder in it is made the person's alone, owned by the firmware package and reached from everywhere else by lazy import or by attribute | `devices.state_dir`, `devices.private_folder`; `jobs._state_dir`, `jobs._write`; `vision/cameras.py`, `evidence/frames.py`, `evidence/log.py`, `finders/switches.py`, `machine_plans.py`, `cam/service.py`, `slicer/service.py` | `jobs.py` imports nothing from the firmware package when it is imported, by its docstring, which is why its imports are lazy; a leaf both can import removes the reason |
| A record written whole or not at all, six times | `jobs._write`, `FirmwareState._save`, `vision/cameras.py`, `evidence/frames.py`, `finders/switches.py`, `slicer/service.py`: each `mkstemp` then `os.replace` | the STL renders' `os.replace(partial, ...)` look alike and are not: the partial file is OpenSCAD's |
| The program finder and the `.exe` suffix, copied from the firmware toolchains into the slicer modules | `slicer/modules/__init__.py`'s `Tool` and `exe` ("found as the firmware toolchains find theirs"); `firmware/modules/__init__.py`'s `Tool` and `exe`; `firmware/toolchains.py`'s `_exe` | the shapes differ by what the copy needed: a callable for the managed path and several names on `PATH`; that is the general shape, and the firmware's the special case of it |

### A shape standing in for an identity

| What | Where | What else it could be |
|---|---|---|
| A node is a board when it is an electrical leaf with no part inside a machine | `api._assembly_tree`: the `inside_machine` parameter and its clause, written for the router's controller before it had a part | a machine whose board no part draws; the controller is drawn from `parts/boards/anolex_grbl_esp32` now, tagged `board`, so `is_board` answers for it, and a described part is a dozen lines of JSON |

### A name kept for a caller that is gone

| What | Where | What else it could be |
|---|---|---|
| Retired command names, hidden, each naming its replacement | `cli/retired.py`; `inventory`, `system`, `install`, `submodules`, `testrun`, `dev`, `photo look` | `project/todo.md` records the rule: removed one release after they were hidden; no `v*` tag has been cut, so by that rule they stay |
| A kept file's kind read from the slice or cut record beside it, for a file kept before files said their kind | `devices._MADE_FOR`, `devices._with_its_kind` | production's state folder has no `prints/` folder at all; the demo's state folders are rebuilt |
| An OpenSCAD install with no manifest, read as the AppImage at `<date>/openscad` | `openscad_installer.LEGACY_EXECUTABLE` | production's tools folder holds one install, `2026.09.27`, with no manifest: the path is live and keeps a real install usable |
| The firmware status route's top-level fields, the Arduino module's, beside the per-module list that is the standard | `arduino.legacy_status`, `arduino.from_legacy`, `ToolchainStatus`'s `arduino_cli_*` and `esptool_*`; read by `cli/firmware.py`, `cli/system.py`, the page's `toolchain.js` and `sketches.js` | the page reads them, and the page is another session's |

### Efforts that may sit outside what the project is for

Named for the owner; none proposed for removal here.

| What | Size | Why it is named |
|---|---|---|
| `apothecary/shims/`: `KiCadProvider`, a provider that "will read KiCad, and today does not", `can_read_board()` always false; `t1_core_stub`, the datum board's hand-entered envelope | 100 lines, one consumer (`datum_bench`'s default), one test | a class whose every behaviour is its parent's; the seam it fixes is `BlackBoxProvider`, which stays |
| The kernel-comparison harness | `kernel_compare.py` (876), `cli/kernels.py`, one test | a measure with no kernel wired in; `docs/README.md` names it |
| The theatre: a site, a part, a lighting rig read from a console's export, sACN and OSC receivers | `theatre_site.py`, `lighting.py`, `console_feedback.py`, `routes/lighting.py`, `cli/lighting.py`, `parts/theatre` | a second site beside the garage; it is what the family's rig work leans on |
| The airgap part's analysis | `projects/parts/airgap.py` (987), `airgap_metrics.py`, `routes/airgap.py`, `cli/airgap.py`, the widget | a part with a computation beside it; its plan is in the todo |

### Modules past one concern

| What | Where | Why it is left |
|---|---|---|
| The devices module: the port list, the state file, hashes, the scan, identification, the dialect helpers, status, control, bed readings, kept files, the print job, serial streams | `firmware/devices.py`, nine sections | a split moves about a hundred and thirty references in the tests and the suite's shared helper (`tests/firmware_helpers.py` patches `_PRINTS` and `_LEVELING` by module), which another session is restructuring; a split through a re-export is a shim. The cut is written below under *What is left* |
| The shared transport and Marlin's dialect in one module | `firmware/gcode.py`; `grbl.py`'s docstring says the link, the log, the latch and the registry are shared | the module's name is in every test, doc and the serial engine's variable; a rename is churn with no behaviour to hold it |

## The standard each folds into

- **A dialect's words live in the dialect's module.** `gcode.py` says Marlin's,
  `grbl.py` GRBL's, `dialects.py` composes them, and nothing else names a
  dialect. A rule over a file is a `Dialect`'s, as its poll and its stop are.
- **The state folder has one module.** `apothecary/state_folder.py` is the one
  place that knows where the folder is, how a folder in it is made the
  person's alone, and how a record reaches it whole. Every package imports it
  plainly; nothing imports the firmware package for it.
- **One finder for every bought engine.** `Tool`, in `firmware/toolchains.py`
  beside `tools_dir`, found the same way whatever the engine.
- **A node is a board because its part is one.** The boards library tags a
  board `board`; a controller nobody has drawn is a described part.
- **A fact is kept once; what follows from it is computed.** The kind of machine
  a board drives follows from the dialect it answered in.
- **A name is kept while a caller exists**, and its expiry is written down where
  the name is.

## The slices

In order, bottom to top; each is one branch cut from the one beneath, one
commit, gated before the commit by the tests the slice reaches and ruff (the
first three by `apothecary test run`), with `apothecary test all` once on the
top. "Holds it" is the test that fails on the code beneath the slice.

| # | Branch | What changes | Holds it |
|---|---|---|---|
| 1 | `build/state-folder-leaf` | `apothecary/state_folder.py`: `state_dir`, `private_folder`, `write_whole`. `devices` reads them from there and keeps no name of its own; `jobs`, `vision/cameras`, `evidence`, `finders/switches`, `machine_plans`, `cam/service`, `slicer/service` import the leaf; the six whole-or-not-at-all writes are `write_whole`. Tests that name `devices.state_dir` name the leaf | `apothecary.jobs` lists the jobs in a process that never imports the firmware package; the package has one reader of `APOTHECARY_STATE_DIR` |
| 2 | `build/one-tool` | One `Tool` and one `exe` in `firmware/toolchains.py`, the general shape (a callable for the managed path, the names on `PATH`); both module registries use it; the firmware's tools name their managed path as a callable | a tool named by its variable with `~` in it is found by a firmware module; `slicer.modules` has no `Tool` of its own |
| 3 | `build/file-check-per-dialect` | `Dialect.check_file`; `gcode.check_file` is the shared walker (the codes no streamed file carries, a `$` line); `gcode.check_gcode(text)` is Marlin's, with its temperature caps; `grbl.check_gcode(text)` is GRBL's, with its M codes, its dwell bound, `G29`, and the spindle bound, which moves with `SPINDLE_MAX_RPM` to `grbl.py`; `devices.save_print_file` asks the kind's dialect; `cam/models` reads the bound from `grbl`; `docs/cam.md`, walkthrough pages 19 and 20 | `grbl.check_gcode` refuses a spindle over the bound and `gcode.check_gcode` does not; a router's file is refused the same lines through the dialect as through `grbl` |
| 4 | `build/objection-per-dialect` | `gcode.ERROR_RE` is Marlin's words; `gcode.OBJECTIONS` is every dialect's, each dialect adding its own when it is imported; `grbl.OBJECTION_RE` is `error:N` and `ALARM:N`, and `explain` reads its number from it | Marlin's pattern does not match `error:20`; GRBL's is among the link's objections; a bad line to the simulated router still raises with the words |
| 5 | `build/board-by-part` | `_assembly_tree` loses `inside_machine` and its clause; a node is a board when `is_board(part_ref)` | an electrical leaf with no part inside a machine is not a board; the router's controller is, by its part |
| 6 | `build/kind-from-dialect` | `PrinterInfo.machine` is computed from `dialect` through one map in `firmware/models.py`; `gcode.MACHINE` and `grbl.MACHINE` read the map; the JSON a record and the API carry keeps the key | `PrinterInfo(dialect=GRBL).machine == "router"`; a record stored with a kind that disagrees with its dialect reads as the dialect's |
| 7 | `build/retired-names-gone` | *Approved 2026-11-07.* The seven names and `cli/inventory.py` go; `cli/retired.py` stays for `cli/testing.py`'s three, which are the test command's; `test_cli.py`'s rows; the CHANGELOG; `project/todo.md`'s rule | `apothecary inventory` is "No such command" |
| 8 | `build/shims-gone` | *Approved 2026-11-07.* `t1_core_stub` moves to `projects/parts/datum_core.py`; `KiCadProvider` goes, `datum_bench` defaulting to a `StubProvider` holding the stub; `docs/fitting-a-part.md` | `apothecary.shims` does not import; `build()` serves the same board |
| 9 | `build/kept-file-kind` | *Approved 2026-11-07.* `_MADE_FOR` and `_with_its_kind` go; a kept file's kind is what it was kept with | a kept file with no kind beside a cut record has no kind |
| 10 | `build/one-key-per-board` | *Approved 2026-11-07, with no reader of the state file's old shape.* `models.board_key` is a board's one key, which `DeviceInfo.identity`, `occupants.key_of`, a pin and a flash record use; `DeviceInfo.names` and `bindings.same_device` tell a pin's or a record's board; a make shared by two bridges plugged in names neither; `FlashRecord.board` goes; `serial_monitor`'s devkit reads `flashed_to(port)`; the wiring names an unnamed board by its own key or its port | the router pinned by its make is found on another port and named by neither twin; a CH340 devkit flashed before its MAC was read keeps its flash, and counts for neither twin; a flash made beside a twin is the port's |

## What was decided

Four things were decided on 2026-11-07. The three removals: the retired
command names (the recorded rule said one release after hiding, and no release has
been cut), the `shims` package, and the kept file's inferred kind. And one key per
board, migrated with no reader of the state file's old shape, since a state it
would read can be rebuilt: a pin kept by port stays a typed pin by port, and a flash
record kept by port names a board with no key of its own. The `LEGACY_EXECUTABLE`
path is live and kept. The four named efforts stay.

## What is left, and why

- **The devices split.** `firmware/leveling.py` (the records, `readings_of`,
  `LevelingJob`, `start_leveling`), `firmware/prints.py` (the kept files,
  `PrintJob`, `start_print`, `_file_fits`), `firmware/streams.py`
  (`SerialStreams`, `listen`, `stream_lines`), each importing `devices` for the
  state, the links and the dialect; `forget_port` names each module's port-keyed
  cache. No re-export: every caller names the new module, the suite's helper
  included. After the test restructuring lands, so the two do not collide.
- **The status route's top-level fields.** The CLI and the page read the
  per-module list instead, and `legacy_status` goes. The page is the viewer
  session's; a follow-up once that lands.
- **A kind of machine as a word in `api.py`.** `machines_in(site, kind)` keyed
  by the job registry's kinds, with each kind's statuses; the firmware route's
  `^(printer|router)$` built from the registry. Small, and `api.py` is shared
  ground; after the viewer session.
- **The operation's nouns.** `Operation.what` carrying "a print" and "a cut";
  `devices.WHAT_HOLDS` goes.
- **A part with both a wrapper and a `part.json`.** The registry says the
  sidecar wins; no part has both. A readiness problem for a part that does
  would make the rule one.
- **The OpenSCAD manifest.** A migration writing `install.json` for an install
  that has none, then `LEGACY_EXECUTABLE` goes; production's tools folder holds
  the one it would migrate.
