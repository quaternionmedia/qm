# ADR-XXXX — One screen: the world, and what stands in front of it

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-04 |
| **Pends on** | Nothing — ready for ratification |
| **Tools** | Drafted with Claude Code (Anthropic) against `consolidate/2026-09-19`, and its counts at one screen measured on apothecary's `review/2026-09-26` by running `apothecary census`; the human who sponsored the work is the contributor of record. |

## Context

Apothecary shows a person three pages. The fractal viewer is the world: a
three.js scene of a site, navigated by zoom level, with a Contents tree, a
Selected panel and the ring. The printer monitor is one machine close up:
status, a temperature chart, the comms log, a latched control pad, the bed
reading, a print streamed from the host, and a second, small three.js
scene of the board in its printer. The firmware page is the bench: the
toolchain, sketches to compile and upload, tasks, and a card per board.
Each has its own toolbar, and each link between them leaves the page.

The census (`apothecary census`) counts what a page holds: on 2026-09-20
the three pages hold 148 controls of their own, 60 of them also on a ring
(viewer 54 / 15, monitor 64 / 41, firmware 30 / 4, the last with no ring).
The rad host integration record makes the ring the one way in with a
keypad cell for every option; that record is about *how* a thing is
chosen, not *where it is shown*, and it is the latter this record decides.

Two facts shape the choice. The world already knows where every board is
-- a pin names a node, the node has a place, and the monitor's small scene
draws the board *inside its printer* from the same geometry the world
draws. And the things a person looks at on the other two pages are mostly
about a place in the world: a printer's temperatures are the printer's; a
devkit's hello is the devkit's; a job's stage belongs beside the machine.
Only the toolchain and the comms log have no place.

Constraints: the tool runs on the person's machine and fetches nothing
from a website while in use (`apothecary/static/vendor/three/README.md`),
so the vendored three.js r160 with `OrbitControls`, `TransformControls`
and `STLLoader` is what there is; the browser tests hold the pages to
timing bounds and must keep doing so; the census is the meter and nothing
is reclassified to make a number smaller; human-only contributorship.

## Decision

1. **There is one screen, and it is the world.** The three.js scene of a
   site is the page. Everything else is drawn *in* it or stands *in front
   of* it; nothing replaces it. A page that today navigates away opens a
   panel instead.
2. **Three kinds of thing stand in front of the world, and only three.**
   *Anchors*: HTML fixed to a point in the world and re-projected every
   frame -- a machine's badge (state, temperatures, progress, a job's
   stage), a devkit's hello, a readout -- read, not operated: a click on
   one selects the node or opens its popup, and nothing on an anchor heats
   or moves a machine. *Popups*: panels tethered to an anchor, opened at
   the node, following it, drawing a leader to it -- the machine's cards,
   chart and latched controls; a devkit's serial; a piece's properties.
   *Panels*: windows for what has no place, docked in **one rail** at one
   side of the world (the right by default, moved by its swap) -- the
   site's *Site* panel (its tree with every problem marked and listed, its
   SCAD, every site's pins, its jobs) and *Selected* stacked, and below them
   a strip of tabs for *Pictures*, the *Bench* (the toolchain, sketches,
   flashing, tasks) and any docked machine -- collapsible, floatable,
   remembered per browser, and never able to push the world off the
   screen. A machine's popup holds everything about that board, printer or
   devkit, its one log included.
3. **What has a place in the world is drawn in the world.** The printer's
   body, its board, the nozzle marker that tweens to each poll and moves
   ahead of a jog, the bed's reading as a relief, the build volume: these
   are decorations the one scene attaches at the printer's node, driven by
   the same events the monitor's small scene answers today. The small
   scene goes once they are there.
4. **Every action keeps its cell.** A panel's verbs are ring verbs;
   opening a panel is a cell; a badge's click is a selection the ring
   already has. The census's ring-backed share does not fall in any phase
   of the move, and the census counts every control once, wherever it is
   mounted.
5. **The anchor layer is written here, not imported.** Forty lines that
   project a node's envelope through the camera and set a transform in the
   animation frame, with no layout reads; an anchor behind the camera or
   out of frame is hidden, an occluded one dimmed. No `CSS2DRenderer` is
   fetched; the vendored set does not grow for this.
6. **The old routes open the world.** The monitor's and the bench's
   content are modules under `apothecary/static/widgets/`, mounted by the
   world's panels. `/firmware` opens the world with the Bench, and
   `/firmware/monitor?port=` opens it with that board's machine, in the
   site where the board is pinned; the two pages and their templates are
   gone, and no plain layout is kept as a kiosk view.
7. **The order of the move** is the plan's (`docs/plans/one-screen-2026-09-20.md`):
   the meter first; anchors and the world's decorations; panels; the
   machine in front of the world; the bench; one screen. Each phase is
   shippable on its own with its tests, its docs and its census count.

## Consequences

- One scene, one camera, one set of navigation rules: what a person learns
  in the world applies to everything, and a machine is looked at where it
  stands rather than on a page about it.
- The monitor and the bench are rewritten as modules. That is the cost,
  and it is accepted: it is the same code in smaller files with two hosts,
  and the census says whether anything was lost.
- Anchors and popups are re-projected every frame. With a dozen boards in
  a site this is trivial; the timing bounds in the browser tests are the
  check, and a site with hundreds of pinned boards is the trigger below.
- Nothing is fetched: the anchor layer, the panel manager and the leader
  lines are the project's own, MIT-licensed with the rest, and the open-
  license audit table does not change.
- The census counts one page. On 2026-09-20 three pages held 148 controls
  of their own, 60 of them on a ring; at one screen the world holds 116, 60
  of them on the ring, and listens in 77 places. Nothing was reclassified to
  make the number smaller: the controls that went were duplicates of a
  ring verb or of another surface (a second log and query box, a second
  poller, a page of links), and those that stayed without a cell are named
  (`census.TAKEN_BACK`, the take-back rows the personal-data record asks
  for). `VIEWER_CEILING` in apothecary's `tests/test_census.py` holds the
  count, with the before and after of each phase in its note.
- rad is asked nothing new: a popup is a panel and a panel's verbs are
  ring verbs, which the nine-cells record already covers.

## Alternatives considered

1. **Three pages with a shared toolbar and links** — the cheapest thing,
   and what there is now. Lost because every link leaves the world, and
   a machine's temperatures shown on a page that does not show the machine
   is the thing this record exists to stop.
2. **The monitor and the bench in iframes over the world** — reachable
   and in front, in an afternoon. Lost because an iframe is a page inside
   a page: its ring is not the world's ring, its census is its own, a
   popup cannot tether across the frame, and the two-host module split
   (§6) would never happen.
3. **`CSS2DRenderer` / `CSS3DRenderer` from three's addons** — the
   standard way to anchor HTML to a scene. Lost on the vendoring rule:
   nothing is fetched while a person is using the tool, and adding files
   to the vendored copy for forty lines of projection is the wrong trade;
   the projection is written here.
4. **A single-page framework (React, Svelte) for the panels** — lost on
   the same rule and on scale: the panels are a registry, a z-order and a
   drag; a framework would be the largest dependency in the project for
   the smallest part of it.
5. **Keep the small board scene beside the world** — lost because two
   scenes of the same geometry disagree the moment one is edited, and the
   world already draws the printer.
6. **Leave the bench a page of its own** — considered, since the
   toolchain has no place in the world. Lost because a devkit *is* a thing
   at a place: its hello, what it should run and its flashing belong to
   its machine at its node, and what is left -- the toolchain, sketches and
   tasks -- is a tab in the rail, one press from the world rather than a
   page away from it.

## Revision triggers

- A site with more pinned boards than anchors can be projected for within
  the frame budget the browser tests hold — the anchor layer needs
  culling by distance or a limit, and the bound in the tests says so.
- A person asks for a plain layout as a kiosk view (a screen beside the
  printer showing only its machine) — §6 is revisited, and the census
  counts the kiosk as a page of its own.
- rad ratifies a record about panels or tethered popups — this record
  adopts it, as the rad host integration record adopts the nine-cells
  record.
- The vendoring rule changes — alternative 3 is reconsidered.
- The census's ring-backed share falls in any phase — the phase is not
  done.

## Amendments

*None.*
