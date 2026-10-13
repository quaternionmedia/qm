# ADR-XXXX — One screen: the world, and what stands in front of it

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-04 |
| **Pends on** | Nothing — ready for ratification |
| **Checked against** | apothecary `4426724` (`build/governance`); its counts are `apothecary census`'s, run there |
| **Tools** | Drafted with Claude Code (Anthropic); the person who ratifies it is its contributor of record |

## Context

A tool that shows a world and the machines in it can show them on
separate pages: the world, a three.js scene of a site navigated by zoom
level; a machine close up -- its status, a temperature chart, the comms
log, a latched control pad, the bed reading, a print streamed from the
host; and a bench -- the toolchain, sketches to compile and upload,
tasks, a card per board. Each page then has its own toolbar and its own
controls, each link between them leaves the page, and a printer's
temperatures are read on a page that does not show the printer.

The census (`apothecary census`) counts what a page holds: every control
of its own, and which of them are also on a ring. The rad host integration
record makes the ring the one way in, with a keypad cell for every option;
that record is about *how* a thing is chosen, not *where it is shown*, and
it is the latter this record decides.

Two facts shape the choice. The world knows where every board is -- a pin
names a node, the node has a place -- and draws a board inside its printer
from the same geometry it draws the printer with. And what a person looks
at about a machine is mostly about a place in the world: a printer's
temperatures are the printer's; a devkit's hello is the devkit's; a job's
stage belongs beside the machine. Only the toolchain and the comms log
have no place.

Constraints: the tool runs on the person's machine and fetches nothing
from a website while in use (`apothecary/static/vendor/three/README.md`),
so the vendored three.js r160 with `OrbitControls`, `TransformControls`
and `STLLoader` is what there is; the browser tests hold the page to
timing bounds; the census is the meter and nothing is reclassified to
make a number smaller; human-only contributorship.

## Decision

1. **There is one screen, and it is the world.** The three.js scene of a
   site is the page. Everything else is drawn *in* it or stands *in front
   of* it; nothing replaces it, and nothing navigates away from it.
2. **Two kinds of thing stand in front of the world, and only two.**
   *Anchors*: HTML fixed to a point in the world and placed through the
   camera on every frame the world draws -- a machine's badge (state,
   temperatures, progress, a job's stage), a devkit's hello, a readout --
   read, not operated: a click on one selects its node or opens its
   Machine, and nothing on an anchor heats or moves a machine. *Panels*:
   windows, docked in **one rail** at one side of the world (the right by
   default, moved by its swap or its grip) or floated over it -- *Site* (the
   site's tree with every problem marked and listed, its SCAD, every
   site's pins, its jobs) and *Selected* stacked at the rail's top, and
   below them one strip of tabs for *Pictures*, the *Bench* (the
   toolchain, sketches, flashing, tasks) and each open *Machine* --
   collapsible, resizable, remembered per browser, and never able to push
   the world off the screen: the rail is never wider than half the page.
   A Machine holds everything about one board, printer or devkit, its one
   log included.
3. **What has a place in the world is drawn in the world.** The printer's
   body, its board, the nozzle marker that tweens to each poll and moves
   ahead of a jog, the bed's reading as a relief, the build volume: these
   are decorations the one scene attaches at the printer's node
   (`apothecary/static/machine_marks.js`), driven by the same board events a
   Machine answers. There is no second scene.
4. **A control keeps its cell wherever it is mounted.** A panel's verbs
   are ring verbs; opening a panel is a cell; a badge's click is a
   selection the ring already has; a Machine's and the Bench's controls
   carry the same ring address in any panel. The census counts every
   control once, wherever it is mounted, and lists the ring address of
   each one that has one; a take-back row the personal-data record asks
   for is named as one (`census.TAKEN_BACK`).
5. **The anchor layer is written here, not imported.**
   `apothecary/static/anchors.js` projects each anchor's point through the
   camera and sets a transform; an anchor behind the camera or well outside
   the canvas is hidden and one behind something in the scene is dimmed,
   tested with a ray every few frames. Badges keep out of each other's
   way in the same layer: two that would overlap step aside, three or more
   merge into a count until the view comes close enough to part them, and
   an open card keeps clear of other cards and of what the page asks it
   to. A badge's size is read when what it says changes, an open card's on
   each frame it is placed. No `CSS2DRenderer` is fetched; the vendored set
   does not grow for this.
6. **The firmware addresses open the world.** A Machine's and the Bench's
   content are modules under `apothecary/static/widgets/`, mounted by the
   world's panels. `/firmware` opens the world with the Bench, and
   `/firmware/monitor?port=` opens it with that board's Machine, in the
   site where the board is pinned; the viewer is the one page template,
   and no plain layout is kept as a kiosk view.

## Consequences

- One scene, one camera, one set of navigation rules: what a person learns
  in the world applies to everything, and a machine is looked at where it
  stands rather than on a page about it.
- A Machine and the Bench are modules mounted by panels, so they can be
  mounted anywhere a panel is; the census counts them once.
- Anchors are placed on each frame the world draws, and the world draws
  when something in it changes. With a dozen boards in a site this is
  trivial; the timing bounds in the browser tests are the check, and a
  site with hundreds of pinned boards is the trigger below.
- Nothing is fetched: the anchor layer and the panel manager are the
  project's own, MIT-licensed with the rest, and the open-license audit
  table does not change.
- The census counts one page. `apothecary census` lists every control the
  viewer holds, the ring address of each one that has one, and the take-back
  rows; `VIEWER_CEILING` in apothecary's `tests/test_census.py` holds the
  count, and is raised only in the change that adds a control. A control
  that duplicates a ring verb or another surface -- a second log and query
  box, a second poller, a page of links -- is not kept.
- rad is asked nothing new: a panel's verbs are ring verbs, which the
  nine-cells record already covers.

## Alternatives considered

1. **Separate pages with a shared toolbar and links** — the cheapest thing.
   Lost because every link leaves the world, and a machine's temperatures
   shown on a page that does not show the machine is the thing this record
   exists to stop.
2. **A machine and the bench in iframes over the world** — reachable and
   in front, in an afternoon. Lost because an iframe is a page inside a
   page: its ring is not the world's ring, its census is its own, nothing
   in it can be placed against the world, and the modules would keep two
   hosts' worth of page around them.
3. **`CSS2DRenderer` / `CSS3DRenderer` from three's addons** — the
   standard way to anchor HTML to a scene. Lost on the vendoring rule:
   nothing is fetched while a person is using the tool, adding files to the
   vendored copy brings code that knows nothing of badges keeping out of
   each other's way, and the projection is the smallest part of the layer;
   it is written here.
4. **A frontend framework for the panels** -- the house stack's
   frontend-application instance (mithril with a parcel build), or React or
   Svelte. Lost because the viewer is one server-rendered template with ES
   modules and vendored libraries and no build step, and the panels are a
   registry, a z-order and a drag: a framework would bring a build step
   and the largest dependency tree in the project for the smallest part of
   the page. The house-stack standing of the viewer's shape is the adoption
   scope's to state.
5. **Keep a small board scene beside the world** — lost because two
   scenes of the same geometry disagree the moment one is edited, and the
   world already draws the printer.
6. **Leave the bench a page of its own** — considered, since the
   toolchain has no place in the world. Lost because a devkit *is* a thing
   at a place: its hello, what it should run and its flashing belong to
   its Machine at its node, and what is left -- the toolchain, sketches and
   tasks -- is a tab in the rail, one press from the world rather than a
   page away from it.
7. **Popups tethered to an anchor** -- a machine's cards opened at its
   node, following it, with a leader line to it. Lost because a panel docked
   in the rail or floated over the world holds the same cards without
   covering the machine it is about, and a popup per machine is a second
   kind of window to place, keep clear and count.

## Revision triggers

- A site with more pinned boards than anchors can be placed for within
  the frame budget the browser tests hold — the anchor layer needs
  culling by distance or a limit, and the bound in the tests says so.
- A person asks for a plain layout as a kiosk view (a screen beside the
  printer showing only its Machine) — §6 is revisited, and the census
  counts the kiosk as a page of its own.
- rad ratifies a record about panels — this record adopts it, as the rad
  host integration record adopts the nine-cells record.
- The vendoring rule changes — alternative 3 is reconsidered.
- The census's ring-backed share -- the controls `apothecary census` lists
  with a ring address, over the controls of the viewer's own -- falls below
  half. At apothecary `4426724` it is above half.

## Amendments

*None.*
