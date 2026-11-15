# Consolidation: fewer windows, one place per thing

*Decided with the owner on 2026-10-03, after a survey of every surface the
app draws. Built: Phases 1-6, each below marked done; the end state, with
the decisions taken after each phase at the end (one rail; a chosen picture
pinned from the ring, so Pictures has no Pin here), is the app as it is. It
finished the one-screen plan's Phases 4 and 5
([one-screen-2026-09-20.md](one-screen-2026-09-20.md)) and superseded the
pictures plan's Phase 5
([pictures-in-the-world-2026-09-26.md](pictures-in-the-world-2026-09-26.md)),
named where they meet. `uv run apothecary census` counts the one page; the
records below are drafted on the governance branch and ratified by a person.*

## What the survey found

Functions are spread across too many surfaces, and the same thing is drawn
or done in several places that disagree:

- One board's state is drawn by six render functions on four viewer surfaces
  (badge, Contents badge, Selected's Device section, the serial overlay, the
  Machine popup) and on two other pages (the monitor page, the firmware
  page's device cards). A printer is polled from four places; it has two logs
  with two query boxes; a printer's full view has nine ways in.
- Flashing a sketch exists only on the firmware page, so checking a board and
  flashing it is two pages; pinning a board exists only in the viewer.
- "Valid" means three things (layout, parameters, build readiness), shown in
  four places; the Validation panel's rows cannot be clicked and Contents
  does not mark an invalid piece.
- Jobs are names and volumes typed by hand, unlinked to the G-code a
  printer actually ran.
- Kept, Gather and Picture › Folder each list a different set of pictures;
  an older picture in the folder cannot be pinned at all. Kept holds board
  pins under Panels › Pictures.
- The word "look" is a verb (take a frame and find its shapes) and a noun (a
  picture pinned at a place), and Camera › Keep pins nothing.

## The end state

One page, the viewer. In front of the world, two docked panels and one
surface per machine:

- **Site** (a panel): the site's Contents as its body, invalid pieces marked
  in the tree; the site's problems at its top, each clickable to select its
  piece (the toolbar's count opens them); the site's generated SCAD as a
  section; **Pinned**, every site's pins (cameras, views, boards) each with
  its take-back, which Kept held; and the site's **jobs**.
- **Selected** (a panel), as now: the selection's facts and its editor.
- **Machine** (a popup tethered to its board, one per board, printer or
  devkit): its state, **one log with one query box** (the serial overlay and
  the Comms log are one), its controls, its sketch and flashing, its pin, and
  its jobs. One poller per board, shared by everything that draws it.
  Selected's Device section is one line and *Open*.
- **Bench** (a panel): the toolchain, cores, libraries, sketches,
  compile/upload, raw flash and the task log -- the firmware page's content.
- **Pictures** (a panel): every picture -- the folder's and the kept ones --
  each with its views and *Pin here*; Forget and Purge for the kept ones; the
  gathering as a section of it until gathering leaves core.

`/firmware` opens the viewer with the Bench open; `/firmware/monitor?port=`
opens it with that board's Machine open. The Validation, OpenSCAD, Jobs,
Kept, Gather and Comms log panels, the serial overlay and the two page
templates go.

## Words

- **View**: a picture pinned at a place (what "look" meant). Picture ›
  Views lists a place's views.
- **Take picture** (Camera): keeps a frame and pins it at the place as a
  view. **Find shapes** (Picture): runs a finder on the view drawn here. Two
  steps, each doing one thing; drop, paste and Picture › Add pin a view
  without finding, and Find shapes is the next step everywhere.
- Camera › Keep goes: Take picture always pins, and unpinning a view leaves
  the picture in the folder.
- Every message that ends a step names the next one (a camera pinned names
  Take picture; a view pinned names Find shapes; shapes found name Make).
- The walkthrough's screenshots are regenerated in full with the new words.

## Jobs

A **job** is one operation a machine performs on a part: a print on a
printer, a cut on a mill or a laser, whatever a machine's kind offers. It
records its kind, the machine, the part and the input file it ran (G-code
for a printer), when it started and finished, and how it ended. The
printer's Print card starts a print job, and its history is that printer's
job list; a mill would start a mill job the same way. The Site panel lists
the site's jobs. The hand-typed Jobs panel and its assign/done routes go;
a running job, not a hand-typed one, is what marks a printer busy. Selected's
status drop-down (maintenance, offline) stays as it is.

## Phases

Each phase ships with the browser suite green and the census run; the
walkthrough pages are regenerated in the last.

1. **Words.** View, Take picture, Find shapes; Keep goes; routes, ring
   labels, messages, code and docs use the same words; each message names
   the next step. *Done.*
2. **Site and Pictures panels.** Site takes Contents, the problems, the
   SCAD and Pinned; Pictures takes every picture and the gathering. The
   Validation, OpenSCAD, Kept and Gather panels go. *Done.*
3. **Jobs.** The job model over machine kinds; the Print card writes print
   jobs; Site lists them; the Jobs panel and routes go. *Done.*
4. **One Machine per board.** One log, one query box, one poller; the serial
   overlay goes; the Device section shrinks; a devkit gets a Machine too.
   *Done.*
5. **Bench and redirects.** The firmware page's sections become the Bench
   panel and a board's flashing joins its Machine; `/firmware` and
   `/firmware/monitor` redirect into the viewer; their templates go. *Done.*
6. **Pictures of it.** The walkthrough pages and the generated docs are
   regenerated in full; the census is run; the one-screen record's numbers
   are filled in for ratification. *Done in this repository: every
   walkthrough screenshot taken again and `apothecary docs generate` run,
   each picture showing what its caption names; the check the board view
   made (a printer's drawing encloses its board) held against the world. The
   record's numbers are what `apothecary census` prints, filled in on the
   governance branch for a person to ratify.*

## Records this touches

Drafted on the project's governance branch, ratified by a person:

- *One screen*: one page, with the Bench and the Machine; the census counts
  one page.
- *rad host integration*: the panels and rings as they end up; opening the
  ring at an address, and an intent carrying where the ring stood (also
  drafted as an input to rad's own record, in the rad repository).
- *Personal data stays on the device* §6: "view" for "look"; Pinned lives in
  Site.

## Decided after Phase 2

- **One rail.** Everything docks on one side, the right by default and
  moved by the rail's swap: Site and Selected stacked, and one tab strip
  below them for the docked panels (Pictures, the Bench, a docked Machine
  with its log in it). The other side of the screen is world. A Machine
  tethered to its board still stands in front of the world, and docks into
  the strip.
- **A chosen picture is the ring's.** Clicking a row in Pictures chooses it;
  Picture › Folder's eighth cell then pins the chosen picture, so any picture,
  not only the seven newest, is pinned from the ring.
- `apothecary photo look` is `apothecary photo find`, the word the viewer's
  Find shapes uses.

## Decided after Phase 3

- Selected's status drop-down keeps "printing" as a hand-set status (a
  print started outside apothecary, from the printer's own menu, is still
  shown as busy), beside idle, maintenance and offline.
- The part a print job names can be any part or piece in the printer's site;
  the list is not narrowed to what fits.

## Decided after Phase 4

- **Addresses stay where hands learned them.** Watch and Monitor became one
  Device cell, **Open** (where Watch was); the cell Monitor freed is taken by
  **Flash** when flashing joins the Machine (Phase 5), so Query, Unpin,
  Rescan, Link and Control keep their addresses (Control at ⌗7, jog Y+ from a
  printer's node ⌗2728).
- **A devkit's port is opened only when asked.** Opening its Machine shows
  its state and touches no port; **Listen** (a button, and a ring verb)
  starts the live serial stream and says it may reset the board.
- **Boards are found on request.** No timed rescan; Rescan from Selected, the
  ring or a Machine, and when a watched board goes quiet.

## Decided after Phase 5

- A printer's Device › Flash is shown disabled, not absent, so its later
  cells keep the addresses a hand learned (jog Y+ ⌗2728); the ring record
  states this as the one exception to "absent, not greyed".
