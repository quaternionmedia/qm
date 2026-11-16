# Cameras as parts, easier pictures, less on the screen

*Decided with the owner on 2026-10-04, after a survey of a busy bench: a
camera pinned at the workbench, a picture taken, its shapes found, sized and
made; printer_1 pinned to a board; the Machine and Pictures open; at 1280 and
1024 px wide. It follows the consolidation
([consolidation-2026-10-03.md](consolidation-2026-10-03.md)) and changes the
pictures plan ([pictures-in-the-world-2026-09-26.md](pictures-in-the-world-2026-09-26.md))
where they meet: a camera is no longer pinned at a structure. `uv run
apothecary census` counts the page; the records below are drafted on the
governance branch and ratified by a person.*

## What the survey found

- A camera is not a thing in the world. It is a text badge and a wire
  pyramid over the structure it is pinned at: it cannot be selected, moved,
  aimed or found in Contents, and its badge prints the device's raw label (in
  the suites, a file path).
- Badges land on each other. A place badge and a machine badge both stand
  30 px above their structure's middle, so a camera at the workbench and
  printer_1's board badge print over each other at the site's top level --
  the board badge sits there before any camera is pinned.
- The Machine opens floating over the middle of the world, about 500 by 480,
  over the scene and the hint bar; a printer's Machine shows Flashing (sketch,
  board, Compile & upload) though Flash is disabled on printers.
- The header wraps to two rows once the breadcrumb grows; the toolbar's
  violations count repeats Site's problem list, which pushes Contents out of
  the panel; the hint bar never leaves.
- From nothing to pieces is five rings opened afresh: Pin here, Take picture,
  Find shapes, Size (then a width typed in Selected), Make all. Pictures lists
  file names.

## The end state

### A camera is a part

- A camera is a root structure of the site, as a printer is: `camera_1`,
  `camera_2`..., drawn as the library's bare webcam (a body and a lens, about
  90 x 30 x 30 mm) standing in the air where it is put. It is in Contents,
  moved with the handles, and checked for overlaps like any part; in the air
  it overlaps nothing.
- It is added two ways: the ring's **Camera › Add here** on a structure or
  the floor stands one above that place's middle, looking straight down, at a
  starting height; or a camera model is dropped from the library like any
  part.
- Which of this browser's cameras it is (its device) is chosen on its own
  ring -- today's Pin here list, Allow until the browser has been asked -- as a
  serial board is pinned to printer_1. A device is one origin's, as now.
- It can be **tilted and turned**. A selected camera wears the move arrows
  and a turn ring and tilt arc, as one compact set (see *Less on the screen*).
- **The lens.** A camera starts at a typical webcam's field of view, about
  60° across. The first width typed for one of its pictures -- the picture's
  width, or one shape's long side, in Selected (Size) -- teaches the camera
  its real field of view, which it keeps. From then on each picture is sized
  by the camera's pose; Size corrects.
- **Where a picture lands.** On the first upward-facing surface -- a
  structure's top, or the floor -- that the centre of the camera's view hits;
  that surface is the picture's place, as the bench or the floor is today.
  Pointed at a wall or the sky, the picture is kept with no place: drawn on
  the camera, and nothing is made from it until the camera is aimed down.
- A view keeps the pose and field of view its camera had when it was taken:
  moving a camera does not move pictures already taken. A picture maps onto
  its surface through a pinhole projection -- one mapping, from a point in the
  picture to a point on the surface, which the mat, the outlines, Make, Why
  this and re-sizing all use. A view with no camera (a dropped file, the
  floor's Add, every view taken before this) is the same mapping with no
  perspective.
- **Reset** keeps a camera a person added and stands it back where it was
  added, looking straight down, as it stands every other part back where
  the site's definition puts it; its device and learned lens stay, and so do
  the views taken from it. Only Remove takes a camera away.
- **Cameras pinned before this start fresh.** The cameras file is no longer
  read and is left where it is; views already taken keep their place and
  width.

### Taking pictures

- Selecting a camera shows, in Selected, its live preview, **Take picture**
  (a button with its own ring cell), and its recent pictures as thumbnails; a
  thumbnail's click draws that picture where it landed.
- With a camera selected, **P** takes a picture.
- Pictures lists every picture as thumbnails grouped by camera (pictures from
  no camera -- added files -- in a group of their own), not by file name.
- Taking and finding stay two steps, as decided on 2026-10-03.

### Less on the screen

- **Badges.** A thing wears at most one small icon badge, at its own spot --
  ⚡ a board, 📷 a camera, ▣ a picture's place -- never at a shared
  structure's middle. Its words (port, sketch, shape count) show on hover or
  selection. Badges that would overlap on screen step aside or merge into a
  count (×3) until zoomed in. Hover cards never overlap each other and keep
  room between themselves and the page's edges.
- **Handles.** Whenever a movable thing is selected, one compact set: the
  move arrows, and on a camera the turn ring and tilt arc.
- **Machine.** Open shows a board's Machine in the rail's tab strip, beside
  Pictures and Bench; it floats only when floated. Sections that do nothing
  for the board fold away: a printer's Machine has no Flashing.
- **One header row.** Choosing a site loads it (Load goes). The breadcrumb
  replaces Zoom Out (a crumb goes up; Backspace still does). Snap to grid,
  Detail and Assembly outlines move into one ⚙ **View** menu, ring-backed.
  The pill reads "prototype", the full text its tooltip. Nothing wraps at
  1024 px.
- **Problems once.** Site shows one folded line, "N problems ›"; the header's
  count opens it.
- **The hint bar** shows on a first visit and fades after a few actions; `?`
  brings it back.
- **Walls** are drawn faded, and a click in the world passes through them to
  what is behind or inside. A wall's row in Contents still selects it (drawn
  solid then, with its handles); ⚙ View › **Walls selectable** turns clicking
  them back on for the session. Walls are the parts of the wall category.

## Stubs for later

Asked for on 2026-10-04: the library's other camera models are present as
stubs -- a webcam on a desk stand, on a clamp arm, and on a ceiling mount. Each
is a part folder tagged `stub`, its description saying what it will be, and
draws only the webcam for now. Add here never uses a stub.

Offered on 2026-10-04 and not chosen, kept here for a later round:

- A picture landing on any face, walls and machines' sides included, with
  pieces standing out from it -- needs every part to have an orientation.
- A camera that only turns about its vertical axis, or only looks straight
  down.
- Learning nothing: a width typed per picture, the pose only placing it.
- The ring reopening at each next step (Take picture → Find shapes → Make
  all); Take picture finding too.
- Handles only in a Move mode, or only on hover.
- Badges keeping their words and moved apart with leaders; or only the
  selected thing's badge.
- A compact Machine card beside its machine in the world.
- Walls picked with Alt-click.
- Cameras pinned before this becoming camera parts above their structures.

## Phases

Each phase ships with the browser suite green and the census run.

1. **Camera parts.** The camera's record and part; Add here; its pose;
   the projection and the place a picture lands; the learned field of view;
   views keeping their camera's pose; Make, Why this and re-sizing through
   the one mapping; the webcam and the three stubs in the library; the
   cameras file retired.
2. **Less on the screen.** The header in one row and the View menu; problems
   once; the hint bar; the pill; badges as icons with room around them; the
   Machine in the rail and a printer's without Flashing; faded walls passed
   through; the compact handles.
3. **Cameras in the world.** The camera drawn, selected and moved; its ring
   (device, Live or Still, Take picture, Remove); turn and tilt handles;
   Selected's camera (preview, Take picture, thumbnails); P; the mat,
   outlines and frustum drawn through the projection; Pictures as thumbnails
   by camera.
4. **Pictures of it.** The walkthrough and the generated docs regenerated;
   the census run; the records' numbers filled in for ratification.

## Records this touches

Drafted on the project's governance branch, ratified by a person:

- *One screen*: the header's controls, the View menu, and the census's
  numbers.
- *rad host integration*: a camera's ring and the View menu's cells.
- *Personal data stays on the device*: where a camera's device id and label
  are kept now that the cameras file is retired.

## Decided after Phase 1

Asked of the owner on 2026-10-04, after the camera's server side was built:

- **The garage has one printer for now.** printer_2 stood on the workbench's
  middle, so a camera added at the bench looked down on the printer's top and
  its picture lay there, as the first-top rule says. printer_2 and printer_3
  go from the garage; printer_1, which the real board is pinned to, stays.
  The rule stays as it is.
- **A camera's pictures are sized at once**, from its starting lens, so Find
  shapes and Make all need no width typed; a width typed later teaches the
  lens, and pieces made before re-size with it.
- **Part on a camera's ring** edits the camera's numbers -- position, turn,
  tilt and field of view -- in Selected, as Part › Edit opens a part's.
- **One device, one camera.** Choosing a device for a camera takes it off any
  other camera. Two cameras added at one place still stand in one spot and
  show as an overlap, and the Print card's parts still include cameras.

## Decided after Phase 2

Asked of the owner on 2026-10-04, after the screen was cleared:

- **A camera's pyramid** (lens to where its picture lands) is drawn only
  while the camera is selected or live; unselected, a camera shows its body
  and its latest picture lying on the surface.
- **View is a top-level cell of the canvas ring**, and Fit moves inside it
  (View › Fit), so Fit's address changes; Snap to grid, Detail, Assembly
  outlines and Walls selectable are View's other cells.
- Kept as built: two badges in each other's way step aside and three or
  more merge into a count; a Machine floated and then closed opens docked
  again; a board pinned inside a printer and not yet identified keeps its
  Flash cell, which says why when pressed; the ring's label for Walls
  selectable is "Select walls".

## Decided after Phase 3

Asked of the owner on 2026-10-10: at the garage's default view a camera over
the bench is a third badge beside printer_1's ⚡ and the picture's ▣, and the
three merge into ×3 until zoomed in. Kept as built: a board's badge merges
like any other, and the count's card lists each with the board's state in
its row.
