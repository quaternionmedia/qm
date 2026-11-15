# Focused systems

*Dated 2026-10-22. The Airgap is the standard for a focused layout; the Part
and the Machine take the same form, on one foundation that every system is
configured through, and Board, Lighting, Fit and build and Bench follow on
it. Decided with the owner: a system opens its main window alone, and every
section is closed until asked for. Decided 2026-10-23: a link to a subject is a
request, opening the sections its entry names for a link; the column beside
the world holds three or four stacks, the rest grouped as tabs; and a window
with nothing to show is minimised.*

## What a focused system is

A focused system is one subject the page focuses on -- a rotor/stator pair,
a part, a board -- and what it is made of on the page:

- **A main window**: the subject and its verbs. The Airgap's is the machine
  drawn at its angle, its scrub and its verbs; the Part's is Selected; the
  Machine's is the board's head -- its link verbs, its control latch, its
  emergency stop -- and what it is.
- **Sections**, each a window of its own, grouped under the system in the
  header's ⊞ Windows and a stack's +: a figure, a picture, a document, a
  list. A section draws at its window's size.
- **A view**: the main window, every section and the world laid out
  together, a cell of Panels › Windows and an entry of ⊞ Windows.
- **Its verbs**: a ring of its own, each also a button of its main window.
  A verb that acts on a section opens it: the Airgap's Sweep opens Sweep.

Opening a system shows its main window alone. Every section is closed until
asked for -- from a stack's +, from ⊞ Windows, by a verb that acts on it, or
by the system's view -- and once open it is remembered with the layout.

## One foundation

Every system is configured the same way, in one place: an entry of
`apothecary/systems.py` -- its id, title and group, its main window, its
sections (id, title, what each holds), its view's layout in window ids, its
cell in Panels › Windows, and whether it lives only while its subject is
open (a board's Machine). Everything else reads that entry:

- **The page** (`static/systems.js`, given the registry as the page is
  rendered): each system's windows registered, its group, its view, the
  windows a remembered layout may hold; the widget that fills them mounted
  the first time any of them is shown, and each section handed its window.
- **The ring** (`menu.py`): Panels › Windows has a cell per system's view.
- **The tests**: each widget's sections are the registry's, the ring's view
  cells are the registry's, and the page's windows and views are the
  registry's.

A widget then has one shape: `mount(slot, { sections, ... })` fills the
main window's slot and moves each section's content into its window, as the
Airgap's does. Adding a system is an entry and a widget; adding a section is
a line in the entry and a block in the widget's markup.

## The systems

### Airgap (the reference)

Main window: the machine, its scrub, its verbs. Sections: Metrics, Winding
functions and gap field, Gap map, Phase inductance and commutation,
Co-energy and torque, Harmonic overlap, Run-up, Rotor orbit and stator
modes, Vibration spectrum, Rig, Sweep. It moves onto the foundation first,
with nothing on the page changing: its hand-made registration and view give
way to its entry.

### Part

Main window: Selected -- the piece, its part, what it is drawn from, its
envelope and ghost, Download SCAD, and the staged-changes bar (Apply,
Revert, Defaults, Undo, Redo, Ghost) with what the last apply said.
Sections:

- **Parameters**: the part's numbers as controls, tied to its text.
- **SCAD**: the editor. It is a window of its own always, so Part › View's
  Pop out becomes the cell that opens it, and Dock goes; Fullscreen stays.
- **Variants**: the saved variants, each drawn again from its row, and the
  compare.
- **History**: this tab's recent applies, each drawn again from the cache.
- **Readiness**: the build checklist.

Part › Edit asks for the editor, so it opens Parameters. The view lays out
Selected, Parameters, SCAD and the world, Variants, History and Readiness
beside them.

### Machine

It lives while a board's Machine is open, one board at a time. Main window:
the head (the link verbs, the control latch, ⏹ E-STOP), the board and its
link, and its state. Sections, a printer's or a devkit's as the board is:

- **Status** (printer): hotend, bed, position, SD print, endstops and
  filament.
- **Temperature** (printer): the chart.
- **Print** (printer): Print from here -- files, makes, Slice, the print.
- **Bed level** (printer).
- **Sketch** (devkit): what it should run against what it was heard saying.
- **Flashing** (devkit): the form and the task's output.
- **Log**: the board's one log.

The control pad stays what it is: a loud window of its own while the latch
is armed. A verb that acts on a section opens it: a piece's Print or Slice
opens Print; Device › Flash opens Flashing.

## Next systems

Each in its own round, on the foundation, after the Machine.

- **Board (EE)**: a devkit's firmware loop as one subject -- the Bench's
  toolchains and sketches, build and upload, the task log, the serial
  output, the port it is pinned to and the pins it is wired to.
- **Lighting (EE)**: a site's rig -- its fixtures by hanging position, the
  levels a console sends (sACN, OSC), what has no DMX address and is set by
  hand, the patch.
- **Fit and build (HW)**: a structure's mechanical readiness -- envelopes
  declared and measured, contested numbers, what is ready to build, the
  problems, what stands where and what it rests on.
- **Bench (HW)**: what stands on the bench -- printers, boards and cameras,
  drawn from their makers' drawings, with their pins and ports.

## Work, in order

*As of 2026-10-24, the first three are done on `build/window-views`, and the
fourth but for `docs/firmware.md` and `project/bench-checklist.md`, which
describe the Machine as one panel ([the review](review-2026-10-24.md#docs));
the next systems are what remains.*

1. **The foundation**, with the Airgap on it and nothing on the page
   changed: `apothecary/systems.py`, `static/systems.js`, the page and the
   ring reading them, the tests that hold them together.
2. **The Part** on it: Selected as its main window, its sections as windows,
   the ring's Part verbs opening the sections they act on.
3. **The Machine** on it.
4. The docs (`docs/viewer.md`'s windows, `docs/airgap.md`, the walkthrough
   pages that show the Part and the Machine) and the walkthrough's pictures
   taken again, each looked at.
5. The next systems, one round each.
