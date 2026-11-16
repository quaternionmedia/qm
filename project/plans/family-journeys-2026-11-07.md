# The family's journeys through the viewer: a plan

*A plan, dated. Built: slices 1 to 3, less text, the card that surfaces its next
step, and a step and a member as doors, then the Procedure beside the world
while a site has a procedure, and the family as a focused system. Each slice is one branch of a local stack,
built in the order listed once the owner says yes to it.*

## What this plans

The viewer holds the irl family's hub: its members, a site's procedures, each
step fired on GO, and what each member answered. It also holds the loops a step
fires on, a print or a cut on a machine, a sketch flashed to a board, a picture
pinned at a piece. The page shows all of it, but as windows and cards that stand
where they were added, each explaining itself in text, and with controls drawn
disabled until something elsewhere is done. This plan shapes the page round
the paths a person takes through the family's work:

- **less text**: the sentences that stand in a window telling a person what to
  do go, and a window says what it has;
- **options surface as they are ready**: a control appears when what it needs
  holds, in place of one drawn greyed beside the reason;
- **windows grouped into journeys**: the family's windows are one group, each
  step of a procedure is a door to the window its member works in, and one
  view lays the family's work out together.

It plans words, seats and shape in the terms of
[ui-coordination-2026-10-31.md](ui-coordination-2026-10-31.md) and
[ui-refresh-2026-11-04.md](ui-refresh-2026-11-04.md): every section a window
(*Windows, not folds*), the kinds' words in one module, the census's count of
the page's controls left where it is (`apothecary census`).

## What the walk found

Walked on `apothecary serve --demo` at 1280 by 800, from main at 1e12ec58,
window by window, the Procedure's steps fired until a machine's step was
refused. The before pictures are beside this plan in the session's notes.

**The windows**, as ⊞ Windows and a stack's + list them: Views (Default, Part,
Machine, Airgap); Site (Site, Problems, Pinned, Jobs, SCAD, Working space,
Procedure); Selected; Pictures (Pictures, Gather, Models); Tools (Bench,
Settings); Part (Parameters, SCAD, Variants, History, Readiness); Airgap and
its eleven sections; a Machine and its sections while a board's Machine is
open.

**The family on screen** is the Procedure window alone, under Site, closed
until asked for, and nothing else of the page says there is a family:

- its members are three dots and three words, `board`, `camera`, `machine`,
  with how each is reached in a tooltip; a member is no door to the window it
  works in, and a member beside the hub (carlos, joe) has no link to its page;
- a step's node is text, `garage:printer_1.frame_system.mainboard`;
- a machine's step refused says *arm its control first*, and the demo's step
  adds *in the Machine window*: the Machine is not open, nothing opens it, and
  the person finds the printer in Site, opens its Machine, ticks Control,
  comes back and presses GO again;
- a devkit's steps, the flash and the hello, run in the `board` member; the
  task's output and the hello are in the devkit's Machine, its Flashing and
  its Log, which nothing opens;
- the hub's audit, what each member answered (`GET /family/`, `last`), is on
  no window; a step shows its own last outcome only;
- the Procedure's and the family's verbs are the ring's Panels › Site ›
  Procedure › GO and Start over, under Site.

**Controls that wait disabled**, each saying why in its tooltip:

| Where | Waits for |
|---|---|
| Print and Cut: Slice or Toolpath | a part chosen under makes |
| Print and Cut: ✕ (forget the file) | a file chosen |
| Print and Cut: Keep as plan, and *none kept* beside it | a part or a file chosen |
| Print and Cut: ▶ Print or ▶ Cut | a file chosen, of this kind of machine, with a board connected |
| Print and Cut: ⏸ Pause, ▶ Resume, ■ Cancel | a job running, and paused for Resume |
| Bed level and Table map: ▤ Probe bed, ▦ Probe table, the corners | control armed (the server refuses; the page offers them) |
| Bench: Flash | esptool installed |

**Text that stands in a window telling a person what to do:**

| Where | Says |
|---|---|
| Pictures | *Choose a picture to pin it from the ring: Picture › Folder, at a structure or the floor* |
| Pictures, empty | *no pictures in the folder yet: take one with a camera, drop one on the world, add some here, or put some in the folder* |
| Selected, on every piece that can host one | *Pictures at X: ⌗ Camera › Add here stands a camera above X, looking down; ⌗ Picture › Add pins a picture from disk, and ⌗ Picture › Folder one already in the folder, any chosen in Pictures; m, or Ctrl+right-click, opens the ring* |
| Print and Cut, the card's title | *· no SD card needed: the file streams over the link, one line per ok* (a router's: *a CAM post's file, or the part's toolpath, streams over the link, one line per ok*) |
| Print and Cut, idle | *nothing printing from here* |
| Bed level, Table map, empty | *no reading yet — Read mesh, or arm control and Probe bed*; *no map yet — clip the probe's lead to the table, arm control, and Probe table* |
| Jobs, empty | *none yet: a print started from the Print card of a printer pinned here is listed here* |
| Procedure, no procedure | *No procedure under X yet: docs/family.md says how one is written* |
| The status line, on a Machine or a view opened | two sentences naming the next step and where it is |
| The hint bar over the world | the essentials, once, fading as they are used |
| The demo's line above the header | what the demo is and how to leave it |

## The journeys

Each is a path a person takes; the windows are the ones it passes through, in
order, and the family's part is which member works it.

| Journey | Begins at | Passes through | The family's part |
|---|---|---|---|
| **Start a site** | the Procedure | a step, the window of the member it fires on, GO, the outcome, the next step | the whole of it: the hub, its members, the steps, GO, the audit |
| **Print a part on a machine** | a machine's badge, its row, a part's ring | the Machine: makes, Slice or Toolpath, the file, its path previewed, control armed, ▶, the job, Jobs | the `machine` member: a step's `home`, `run`, `pause`, `resume` |
| **Flash a board** | a devkit's row, the Bench | the devkit's Machine: Sketch, Flashing, the Log's hello | the `board` member: a step's `flash`, `expect` |
| **A picture to a piece** | a piece's ring, Pictures | a camera, Take picture, Pictures, Find shapes, Make, Selected, Parameters, then the machine's journey | the `camera` member, a page's to read |
| **Design a part** | a part's ring | Selected, Parameters, SCAD, Variants (the Part view) | none; left as it is |

The first is the family's own, and the next three are what its steps fire on.
A step is where the journeys join: a step on a machine's node is the machine's
journey from its Machine, a step on a devkit's node the board's.

## The slices

Each is one branch, stacked on the one before it, each with the browser tests
that hold it, gated by `apothecary test run`, with `apothecary test all` once
on the top. A page changed on purpose is committed with its walkthrough
pictures past `tests/e2e/picture_drift.py`'s tolerance, each looked at.

### 1. Less text

The sentences in the table above go, and a window says what it has:

| Where | Becomes |
|---|---|
| Pictures' standing sentence | nothing; the line says *X chosen* while a picture is chosen, and is empty otherwise |
| Pictures, empty | *no pictures yet* |
| Selected's *Pictures at X* paragraph | nothing: the piece's ring holds Camera and Picture, and the ring's cells say what each does |
| Print and Cut, the card's note | nothing: the title alone, *Print from here* or *Cut from here* |
| Bed level, Table map, empty | *no reading yet*; *no map yet* |
| Jobs, empty | *none yet* |
| Procedure, no procedure | *no procedure under X yet* |
| The status line, on a Machine or a view opened | one clause: what opened, and the one thing that is next |

The hint bar, the demo's line and every tooltip stay: a tooltip is read when
asked for, the hint bar fades once used, the demo's line says how to leave it.
Held by `test_pictures_panel.py`, `test_first_camera.py`, `test_printer_ui.py`,
`test_router_ui.py`, `test_the_demo.py`; the pictures of walkthrough pages 02,
03, 05 and 18 that show these windows follow.

### 2. The Print and Cut card surfaces its next step

The card draws the step a person is at and the ones after it as they become
possible, in the loop's order; a control is in the page, as the census counts
it, and hidden until what it needs holds:

| Control | Surfaces when |
|---|---|
| makes, and Choose File | always: the two ways in |
| Slice or Toolpath | a part is chosen under makes |
| the file's row: the files kept, and ✕ | a file is kept for this machine |
| preview | a file is chosen |
| Keep as plan | a part or a file is chosen; *none kept* goes, and a kept plan is said as now |
| ▶ Print or ▶ Cut | a file is chosen; disabled only while a job runs, or the board is not connected, and its tooltip says which |
| ⏸ Pause, ■ Cancel | a job is running from here |
| ▶ Resume | the job is paused |
| the progress line and bar | a job is running or has run |

The Bed level and Table map cards the same: Read mesh always on a printer, the
probe and the corners once control is armed. `tests/e2e/test_focused_systems.py`
names `#print-start` as what the Print window shows; it names `#print-part`.
Held by `test_printer_ui.py`, `test_router_ui.py`, `test_machine_plans.py`,
`test_toolpath_preview.py`, `test_onboarding.py`; walkthrough 03's and 21's
pictures of the card follow.

### 3. A step is a door, and so is a member

The Procedure window leads to where each step's work is:

- **A step's node is a button**: pressed, the node is selected at its level
  and its window opened, as a Jobs row opens its machine: a machine's or a
  board's Machine (`openMachine`), the camera's Pictures. On a node with no
  board pinned it says so, as `noMachine` does.
- **A step fired opens the section its member works in**, where that Machine
  is open, as a verb that acts on a section opens it: `home` and `run` the
  Status, `flash` the Flashing, `expect` the Log. A Machine that is not open
  is not opened by a fire; the node's button is the door.
- **A refused machine's step** keeps the member's words, and its node's button
  stands right after them, so the way to the latch is one press.
- **A member's name is a door** too: `machine` and `board` to the Machine of the
  node the next step names, `camera` to Pictures, a member beside the hub to
  its page in a new tab (its `url`, from `GET /family/`), a pull member to
  nothing. A member the hub started says its state beside its name, as now.

GO never arms a latch, and a delivery changes nothing it does not say: the
decision in [family.md](../../../../docs/family.md#its-own-members) holds. `procedure.js`
takes an `open(node)` from the page; the page hands it its own `openMachine`.
Held by `test_procedure_window.py`.

### 4. The family is a focused system

The family is one subject in windows of its own, as the Part, the Machine and
the Airgap are: one entry of `apothecary/systems.py`, which the page, the ring
and the tests read.

- **Main window: Procedure**, group **Family**, with the steps and GO alone.
- **Members**, a section: each member, how it is reached, its state where the
  hub started it, and its door (slice 3's). It is the top of the Procedure
  window today, moved into a window of its own, closed until asked for.
- **Deliveries**, a section: the hub's audit, newest first, each delivery's
  step, member, status, milliseconds and the instance that took it, read from
  `GET /family/` and asked again while the window is shown.
- **Family view**, a cell of Panels › Windows after Airgap view and an entry of
  ⊞ Windows after Airgap: the world; the Procedure beside it, tall; Members
  and Deliveries under it; Jobs, the Working space and Selected in the
  column. A Machine that is open stays where it is; the view does not lay one
  out, since a step's door opens it.
- **⊞ Windows and a stack's +** list a FAMILY group: Procedure, Members,
  Deliveries. Site's group loses Procedure.
- **The ring** keeps Panels › Site › Procedure, GO and Start over where they
  are: addresses hold still, and Panels has its eight cells. Panels › Windows
  gains Family view after Airgap view, as `VIEWS` reads the registry.

Held by `tests/test_systems.py` and `tests/e2e/test_focused_systems.py` from
the registry (a line each in `OPENING`, `SHOWS`, `VERB`, `LINK`, `EMPTY`),
`test_window_manager.py`, `test_procedure_window.py`, `test_menu.py`,
`test_ring.py` and `test_site_panel.py` where they list Site's windows; the
README's map row for the family names the Family view; `docs/viewer.md`'s
systems table and `docs/family.md` say the windows.

## Pages with pictures

A walkthrough page that describes something a person does in the page is written
by the browser test that does it, its pictures a byproduct of the test asserting
what a person sees, recorded and never compared, its words fixed in the test
(AGENTS.md item 13; `tests/e2e/README.md`, *The two recorders*). Pages 19 to 23
are hermetic doctest pages with no pictures, though each describes a thing a
person does in the page. Each slice that reshapes a window adds the page's side
of what that window does, a runtime-bound page of its own linked from the
hermetic one, with short text in the present tense saying what a person does
and sees:

| Slice | Page | Written by |
|---|---|---|
| 2 | 24, *A cut from the card*: the Cut card from makes to a cancelled cut | `tests/e2e/test_router_ui.py` |
| 3 | 25, *A procedure through the window*: the family, a step's door, GO, a refusal, the outcome | `tests/e2e/test_procedure_window.py` |
| 4 | 25 gains the Family view, Members and Deliveries | the same |

## Questions the owner decides

Asked one at a time, each from a picture of the demo left at that step:

1. the plan's shape: these four slices, in this order;
2. whether the Procedure opens in the page's own layout, beside the world,
   giving its room away while the site has no procedure, so the family is on
   screen without being asked for (every walkthrough picture would follow);
3. slice 4's Members and Deliveries as windows, or the members kept at the top
   of the Procedure and the audit left to the log.

## What it leaves

- The camera as a pull member read by the page, the reader as a member, a step
  that fires itself: [irl-hub-2026-11-02.md](irl-hub-2026-11-02.md)'s order.
- carlos and joe in the demo's table, so Members shows a member beside the hub:
  the demo starts none.
- The demo's step notes, *Arm its control in the Machine window first: GO never
  does*, in `apothecary/demo.py`: a Python seam another session is
  standardizing. With a step's door built, the note says what the door does;
  it is left for that session, or a one-line change after.
- The routes: every window above reads a route that is there (`/family/`,
  `/family/beside`, `/sites/{s}/procedures/{p}`). None is added.
- A remembered layout left by a Machine view and a reload stands the world
  narrow between Procedure and Selected: the window manager's, not this plan's.
