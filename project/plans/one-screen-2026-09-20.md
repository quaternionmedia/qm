# One screen: the world, and what stands in front of it

*Done. Phases 0-3 are this plan's: the anchor layer and machine badges
(`anchors.js`, `machine_marks.js`), the panel manager and rail
(`panels.js`), and the machine as one module (`widgets/machine.js`). Phases 4
and 5 were built by the consolidation plan's Phases 4 and 5
([consolidation-2026-10-03.md](consolidation-2026-10-03.md)): there is one
page, the viewer; the firmware page is the **Bench**, a tab of the rail's
strip, and the printer monitor is each board's **Machine**, in front of the
world; `/firmware` and `/firmware/monitor?port=` open the viewer with them;
the plain layouts and their templates are deleted. `uv run apothecary census`
counts the one page, and `tests/test_census.py` holds its numbers, its
docstring saying what was retired. Walkthrough pages 11 and 12 and the pages
`apothecary docs generate` writes show it as it is. The draft record* One
screen *takes its numbers from `apothecary census` on the governance branch,
and a person ratifies it.*

## The end state

Apothecary has three screens: the fractal viewer (the world), the printer
monitor (one machine, close up) and the firmware page (the toolchain and
the boards on the bench). The aim is **one main screen -- the world -- with
everything else in front of it**: things that belong to a place in the
world are drawn *at* that place and follow it as the camera moves, and the
windows the other two screens are made of become panels that open in front
of the world -- tethered to the thing they are about when they are about a
thing -- and never replace it. The ring is the way in to all of it, every
option with its keypad cell, and the census is the meter: at the end there
is one page, its count is the sum of what survived, and nothing was
reclassified to make it smaller.

```
 ┌──────────────────────────────────────────────────────────────────┐
 │ toolbar: site · zoom out · breadcrumb · ⌗ Ring                   │
 ├──────────────────────────────────────────────────────────────────┤
 │                                                                  │
 │   THE WORLD (three.js, full bleed, the only scene)              │
 │                                                                  │
 │        ┌ printer_1 · idle · 15°/15° ┐   ← anchored badge:      │
 │        │ ▤ mesh · leveling          │     follows the node     │
 │        └────────────╥──────────────┘                            │
 │              [printer body, board, nozzle marker, bed relief]    │
 │                                                                  │
 │  ┌ Contents ──────┐        ┌ printer_1 ─────────────────── ✕ ┐ │
 │  │ (docked panel) │        │ tethered popup: cards · chart   │ │
 │  │                │        │ control (latched) · bed · print │ │
 │  └────────────────┘        └──────────────╥──────────────────┘ │
 │                                           ╙─ leader to the node  │
 └──────────────────────────────────────────────────────────────────┘
```

Three kinds of thing in front of the world, and only three:

- **Anchors** -- HTML fixed to a point in the world, re-projected every
  frame: badges, the job callout, the nozzle marker's readout. They are
  read, not operated: a click selects the node or opens its popup; nothing
  on a badge heats or moves a machine.
- **Popups** -- panels tethered to an anchor: they open at the node, follow
  it, and draw a leader to it (the machine popup, a devkit's serial popup,
  a piece's properties).
- **Panels** -- free or docked windows with no place in the world: the
  comms log, the bench, the Contents tree, Jobs. Nothing docked can push
  the world off the screen.

What is drawn *in* the world rather than in front of it: the printer's
body, the board, the nozzle marker, the bed relief, the build volume.

Rules that hold throughout:

1. **The world is never replaced.** A panel opens in front; a popup opens
   at; a page that today navigates away opens a panel instead. The old
   routes keep answering until Phase 5, on the same modules.
2. **Every action has a cell.** A panel's verbs are ring verbs; opening a
   panel is a cell; the census's ring-backed share must not fall in any
   phase.
3. **Snappy.** Anchors are projected in the animation frame with no layout
   reads; polls stay asynchronous and coalesced; a panel's content mounts
   lazily; the browser tests keep their timing bounds (a badge follows the
   camera within a frame, a popup opens within 300 ms).
4. **The census counts, the plan does not estimate.** Each phase ends with
   `uv run apothecary census` on the pages that exist, and the test that
   holds the numbers is edited with its docstring saying why.

## Left open by phases 1-3

- A devkit's *hello* on its badge: done; one model of each board
  (`boards.js`) holds what its Machine heard, and every drawer reads it.
- A jog moving the world's nozzle ahead of the poll from another page: there
  is no other page; a jog from a Machine moves the marks on its own event.
- The machine popup's URL deep link: done, `?machine=<port>`, kept in the
  address while a Machine is open.
- `widgets/machine.js` is one file with sections (status, chart, log,
  control, bed, print, flashing); split it when a host wants one part without
  the rest. Open.
- `board_view.js`: deleted with the monitor page. Its check that a printer's
  drawing encloses its board and its build volume is held against the world
  (`tests/e2e/test_printer_ui.py`).

## Phase 4 — The bench in front of the world

*Built by the consolidation's Phases 4 and 5: the Bench is a tab of the
rail's strip, the device cards are each board's Machine, and Device › Link holds
Listen and Probe on a devkit (identifying is Device › Query). There is no
plain layout.*

- `widgets/toolchain.js` (install, cores, libraries), `sketches.js`
  (pick, compile, upload, esptool), `tasks.js` (the running task, cancel,
  history), `devices.js` (the cards, minus the board view -- the world
  shows the boards). Mounted as the **Bench** panel, docked right, and as
  `/firmware` in a plain layout.
- The device cards' verbs join the ring, so the firmware page's controls
  of its own get cells: `Probe`, `Identify` and the serial `Listen` (named
  so, because Camera › Live is the pictures plan's) join Device › Link
  where they apply, because the Device ring on a printer already holds
  eight; proposed as an edit to the rad record's Link cell (see the
  pictures plan's *For a person*).
- Tests: the firmware-page suite runs on both hosts.

## Phase 5 — One screen

*Built by the consolidation's Phase 5, the plain layouts deleted with their
templates. The generated docs stay two workflows, both on the one page
(`tests/e2e/test_docs_fractal_viewer.py`, `test_docs_printer_monitor.py`).
Re-running the bench checklist on the one screen
([`2026-09-20-ender-bench.md`](../validation/2026-09-20-ender-bench.md)) is a
person's, at the bench.*

- `/` and `/viewer/sites/{name}` are the app. `/firmware` and
  `/firmware/monitor` redirect into the world with the right panel open;
  the plain layouts are kept only if a person asks for a kiosk view, else
  deleted with their templates and their tests folded into the world's.
- The census counts one page; `PAGES` is one entry; the number is what
  survived and the docstring says what was retired and why.
- The docs walkthroughs become one (`tests/e2e/test_docs_one_screen.py`),
  the firmware doc's page-by-page sections become panel-by-panel; the
  bench checklist is re-run on the one screen.
- The draft record *One screen* is proposed for ratification with the
  numbers filled in.

## Pictures, in their own plan

Pictures, cameras and found shapes take the same frame in
[pictures-in-the-world-2026-09-26.md](pictures-in-the-world-2026-09-26.md):
it retires the camera panel, and its last phase closes the old photo routes
together with Phase 5 above.

## What is decided here, and what a person decides

Decided by this plan (change it here, not in the code): the three kinds of
thing in front of the world; the world is never replaced; every action has
a cell; the old routes live until Phase 5; the census is the meter.

Decided by the owner (the consolidation plan): the plain layouts do not
survive as kiosk views, and their addresses redirect into the viewer; the
Bench is in the world, a tab of the rail's strip.

For a person: the edit to the rad record's Link cell that Phase 4 proposes
(on a devkit, Listen and Probe after Reconnect, Reset and Release, as built);
the record's ratification.

## Not in this plan

A second site on the screen at once; a browser other than Chromium in the
tests; a record of rad's for tethered popups (a popup is a panel, and a
panel's verbs are ring verbs, so nothing new is asked of rad); a mobile
layout.
