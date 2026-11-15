# Iterating on a part in the page, tightened

*Reviewed on 2026-10-12 at the top of the stack (`build/onboarding`): every
step of designing a part and editing its SCAD used for real, timed from
input to result on the OpenSCAD snapshot and on 2021.01, its code paths
read, and set against OpenSCAD's own editor, CadQuery and build123d, and
Onshape and FreeCAD. Decided with the owner one question at a time. It
follows the browser-editing spike
([part-editing-in-the-browser-2026-09-27.md](part-editing-in-the-browser-2026-09-27.md))
and the loops plan ([ui-flows-2026-10-08.md](ui-flows-2026-10-08.md)).*

## What the review found

- **A failed `assert` is drawn as a good variant** on the snapshot, which
  writes the geometry built before the error and exits 0; the page marks the
  line red and says the variant was regenerated. The check runs without the
  staged values, so an error only some values trigger is never caught there.
- **The snapshot pays its AppImage's start on every run**: 0.35-0.9 s of
  every check and render, which extracted take 0.1-0.25 s.
- **Number controls are sliders alone**, stepped on odd fractions; integers
  cannot be set, enums are fake sliders or text, a nested model is a text
  box holding "[object Object]", and no unit or description shows.
- **A grown variant is drawn in the wrong place** -- centred on the old
  envelope, half through the floor -- and nothing says its size has left
  its declared envelope.
- **Slice and the readiness checklist act on the saved part**, not the
  variant on screen, and the checklist gives command-line advice for a
  build volume the pinned printer already has.
- **Work is easy to lose**: a draft and staged numbers go on a reload, F5
  reloads the page, Ctrl+S does nothing, undo goes when another part is
  selected, and a Save can overwrite a variant silently.
- **The merge advice is untrue** where the variants live in another
  repository; a part inside a submodule (gridfinity) is saved at the wrong
  place, and its drafts dirty the submodule.
- **The SCAD loop's floor is a fixed second of quiet**; a comment-only edit
  renders again; an older render can land after a newer error.
- **Seeing what changed is hard**: nothing frames the part being edited, no
  before and after, and variants compare only with the part's own SCAD.
- **Smaller**: the variant cache holds ASCII STLs four to five times the
  binary size, uncompressed and uncached by the browser; a made piece's
  Apply redraws the whole site; renders run without a limit; the view
  redraws every frame, so a machine without a GPU crawls.

## Decided: tighten

1. **An error is a failed render, drawn greyed and flagged.** Any message at
   error level fails the render: the partial geometry the snapshot wrote is
   drawn greyed with a red "failed at line N" flag, never cached as a
   variant, and Save is refused. The check runs with the staged values.
2. **Extracting the snapshot is opt-in.** `apothecary openscad install
   --extract` (and for an install already made) extracts it for the fast
   start; the default stays the smaller AppImage, and `apothecary check`
   says how much faster extracting would make each run.
3. **Real parameter controls**: a number box beside each slider; integers
   step by one; the customizer's own step; enums as choices; a nested model
   as a group; descriptions as captions; **units declared on the field**
   (`json_schema_extra={"unit": ...}` on a model's field, the bracket or
   trailing word of a customizer comment), none shown where none is
   declared.
4. **Work is kept, per tab.** A part's draft and staged numbers are kept in
   the tab's own storage and offered back on a reload; leaving with unsaved
   work warns; each part keeps its editor's state, undo included, while
   others are selected; focus stays after Apply; a variant's name clears
   once its text has moved on, so Save never overwrites one silently.
5. **OpenSCAD's keys in the editor**: F5 checks and draws, F6 renders and
   draws, Ctrl+S saves a variant, Ctrl+Enter applies; outside the editor
   the browser's keys are untouched.
6. **A variant is drawn where it stands**: placed by its measured bounds,
   Footprint updated, the envelope line amber with the difference when
   measured and declared part, and a part below the floor flagged.
   (Clearance against neighbours is the next phase's.)
7. **Slice and the checklist follow the drawn variant**: the variant's STL
   is sliced and its record names the variant; the checklist reads the
   pinned printer's build volume.
8. **The merge advice is true**: it names the repository the ref lives in
   and says a variant's parameters are not applied by a merge. A part inside
   a submodule saves an **overlay** in the superproject's ref -- a small
   SCAD that includes the upstream file and sets the edited values -- so the
   submodule is never touched; an edit to the upstream file itself is
   refused with that reason. Drafts beside a submodule's part are ignored
   there.
9. **The SCAD loop renders soon after a passing check**: the check 300 ms
   after typing stops, the render about 300 ms after it passes, a newer
   edit cancelling it; the cache keyed on what OpenSCAD compiles, so a
   comment-only edit draws at once; a render from older text says so.
10. **Lighter and smaller**: binary STLs in the variant cache; variant URLs
    cached as immutable; responses compressed; Regenerate STL folded into
    Apply; Download SCAD downloads the edit when there is one; a made
    piece's Apply redraws only the piece; the snowplow's generated SCAD
    refreshed after Apply; Apply disabled up front where this OpenSCAD
    cannot build the part.

## Decided: improve, this round

- **History and undo**: undo and redo for staged numbers, and this tab's
  recent applies as a list to draw again from the cache.
- **Before and after, and compare**: a ghost of the saved part, or of the
  previous variant, with the size's difference; two variants side by side
  or overlaid, with a diff between them.
- **Variant management**: rename and duplicate, a variant's history with a
  restore, and **Delete moves the ref to `refs/apothecary/trash/`** --
  restorable from a *Deleted* fold, emptied only by a separate, confirmed
  step.
- **Frame the part being edited**: a Fit-selected cell and key that frames
  the part and keeps Selected and its editor open.
- **Render on demand**: the 3D view draws only when something changes.
- **A bounded render queue**: at most a few OpenSCAD runs at once, the rest
  shown as queued.

## The next phase, planned and not built

Each is written out so it can be built as it stands, and is not this
round's work.

- **Auto-apply while iterating.** Like OpenSCAD's customizer auto-preview:
  a set of numbers that passes its check renders when the controls rest,
  cancelling as they move, through the bounded queue. A toggle in the
  editor, ring-backed; whether it is on by default (and off on 2021.01) is
  for the owner when it is built.
- **Clearance while iterating.** The drawn variant's measured bounds go into
  the site's checks for this tab: overlaps with its neighbours and the
  pinned printer's build volume, flagged on the part and in Site's
  problems, before anything is saved.
- **A new part from a template.** The canvas ring's New › a name and a
  category writes a described part (`part.json` and a SCAD from
  `templates/basic.scad.j2`) and opens it in the editor; `apothecary parts
  new` does the same from the command line. Whether it is written as a
  variant ref or into the checkout is for the owner when it is built.
- **Handles in the 3D view** (the spike's fourth iteration): a handle bound
  to one length parameter; the mesh scales while dragging and renders on
  release, writing the parameter, never the source.
- **Promote a variant to the part's source.** The stub made real: a
  variant's parameters written into the part's own description
  (`part.json`, or its model's defaults) and the SCAD regenerated from it,
  on a branch, never the working tree.
- **OpenSCAD's presets.** Read and write OpenSCAD's own `<part>.json`
  parameter sets, so a preset made in OpenSCAD is a variant here and back.

## Work

Two parts, on branches of their own from `build/part-iteration`:

1. **The server**: errors as failed renders; the extract flag; units in the
   schema and the customizer; Slice, the checklist and the build volume
   following a variant; the merge advice, overlays and submodule drafts;
   binary STLs, cache headers and compression; the cache keyed on the
   compiled CSG; the render queue; variant rename, duplicate, history,
   restore, trash and compare.
2. **The page**: the controls; kept work and keys; the greyed failure;
   placement and the envelope's difference; the timings; the history,
   before-and-after and compare views; the variants' management; framing;
   render on demand -- wiring the server's new answers as they land.

Each holds its loop with a browser test that goes round it, and walkthrough
pages 14 and 16 are taken again when both are in.

## Decided: parameters and text, tied together

Asked of the owner on 2026-10-12, after the server's half was built:

- **The text is the truth, both ways.** Moving a control rewrites that
  parameter's assignment in the editor's text, keeping its line's comment
  and range; editing an assignment in the text moves its control. Controls
  and text are one draft, checked and rendered as one, and one undo history
  holds both. Values are no longer passed to OpenSCAD on the side for a part
  whose SCAD the page edits; a saved variant's SCAD carries its values, so
  merging a variant applies them, and the variant's separate parameters
  file goes. A variant saved before this has its parameters written into
  its text when it is drawn.
- **A part's default is its SCAD file as saved.** Defaults puts the part's
  own text back. A part's Python model still checks values -- ranges, types,
  whole numbers -- but no longer passes them on the side; where a model's
  default and its SCAD's literal disagree, `apothecary problems` and the
  part's checklist flag it.
- **A computed assignment** (`wall = size * 0.1;`) gets a control that shows
  the value it gives, marked as computed with its expression; moving it asks
  once, then replaces the expression with the plain value in the text, an
  edit undo takes back. Only top-level assignments get controls, as
  OpenSCAD's customizer does.
- **A part inside a submodule** is edited as its overlay: the editor holds
  the include line and the assignments set, each control writing its line
  there, with the upstream file one step away and read only; Save keeps
  the overlay's text as the variant.
- **A part whose SCAD is generated** (the snowplow, a made piece) stays one
  way: its controls drive its model, and the generated text follows each
  check, read only.
- **Every variant action has a cell.** Part › Variants › a variant's name
  opens a ring of what can be done to it -- draw, rename, duplicate,
  history, compare, delete -- and Part › Variants › Deleted holds the trash;
  choosing a variant moves one level deeper than it was.
