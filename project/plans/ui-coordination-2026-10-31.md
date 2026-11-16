# One page for every effort: a plan

*Plans are dated and exempt from the durable-text rule. The efforts below are
on local branches, none of them pushed yet: the family lane
(`explore/qm-family`, on `build/iterate-ui`), the working-space stack
(`build/evidence-log`, `build/evidence-frames`) and the image-models branch
(`claude/image-models-qmcp-e257c5`).*

## What this plans

Several efforts are adding to the viewer at once, each from its own plan:
- the Working space;
- the image models;
- the rig's faces pinned on a camera's picture;
- the bench drawn in carlos;
- the lighting console;
- pictures and their gathering;
- a made piece kept as a part;
- the README served in the app.

Each plan placed its own surfaces. This page puts them on one page: what each
effort shows and from where, the words they share, where they collide, and the
order the collisions are settled in. It plans seats and words, not code. Every
section stays a window (*Windows, not folds*: no rails, floats or overlays).

## The page as it stands

**Windows**, each registered through `panels.register`:

| Window | Door |
|---|---|
| Site, Problems, Pinned, Jobs, SCAD | Panels › Site |
| Selected | Panels › Selected |
| Pictures, Gather | Panels › Pictures; Gather also from the canvas ring's Pictures |
| Bench (the toolchain, sketches and task log) | Panels › Bench |
| Machine and its sections, the Control pad | Panels › Machine, while a machine is pinned |
| Part's sections | Part › Edit, Part › View › SCAD |
| Airgap | Panels › Airgap |
| Lighting | none: ⊞ Windows alone, while the site has a rig |
| Settings | View › Settings |

**Rings** hold at most eight options with labels of at most twelve
characters (`apothecary/menu.py`, `MOST_OPTIONS`, `LONGEST_LABEL`):
- **Full:** Panels; a printer's ring; a host's Picture ring.
- **One free cell:** the canvas ring's top level.
- **Room:** Panels › Site holds five, with room for three; Panels › Pictures
  holds two.

## What each effort adds

| Effort | State | Window | Doors | Its words |
|---|---|---|---|---|
| The Working space | built, `build/evidence-frames` | Working space | Panels › Site › Workspace; a printer's Camera › Workspace | observation, evidence, frame set, sighting, subject |
| The image models | prototype, the image-models branch | Models, a stack beside the world | Panels › Pictures › Models (Models, Ask, Colour, Material) | observation, guess, ask |
| The rig's faces (the concert plan's slice 3) | planned | "a window where a person drags the corners onto the camera's picture" | none yet | face, setup, reading |
| The bench drawn in carlos | routes built (`/sites/{s}/wiring`) | none: its plan defers a Bench window | none | lead, patch, state, unexpected |
| Lighting, a devkit's LED, the footpedal | on `build/iterate-ui` | Lighting; the LED on the board's badge | Lighting has none | fixture, cue |
| Pictures and gathering | built; gathering to propose and wait (*project/todo.md*) | Pictures, Gather | as above | picture, view, capture |
| A made piece kept as a part | decided (*project/todo.md*) | Part's | a Save cell on the made piece | Save as variant |
| The README in the app | decided (*project/todo.md*) | a page, as `/docs` is | Panels › Docs opens a browser tab | |

## Where they collide

1. **Two observation modules.** The working-space stack and the image-models
   branch each wrote `apothecary/evidence/observation.py` and its
   `__init__.py`, and they also both change `menu.py`, `api.py`,
   `census.py` and its test. Both files implement `qm.observation` version 1
   with an `apothecary` block, as the image-models plan decided ("one format
   with the working-space layer's"), but they were written apart. The two
   branches do not merge, so the demo shows the family lane and the
   working-space stack, and the models branch on its own.
2. **One word, several things.**
   - **Bench:** the toolchain window, the bench drawn in carlos, and the
     garage's workbench host.
   - **View:** a picture pinned on a place, a window layout, the Working
     space's document reader, and an observation's `view` field.
   - **Picture, frame, capture:** Take picture keeps a frame under `captures/`
     and makes it a view. A Working space frame goes through the same route and
     makes none. The models plan says picture throughout.
   - **Reading and observation:** "reading" is the rig reader's, with origin
     `read`; "observation" is the format both modules write.
   - **Working space:** the window is titled Working space, and its ring
     cell says Workspace, to fit twelve characters.
3. **Seats.**
   - A printer's ring is full, which is why Workspace went under Camera.
   - "Save as variant" is fifteen characters.
   - Models sits after Gather in Panels › Pictures. When gathering moves
     behind an optional install and Gather goes, Models' address moves, and
     an address should hold still.
   - Beside the world, SCAD, the control pad and Models each take a stack of
     their own.
4. **A person's word in two windows.** Models keeps a person's word about a
   shape, and the Working space plan answers its decisions in its own window.
   Both write `stated` observations.
5. **A window with no door.** Lighting is reached only from ⊞ Windows, and
   `docs/viewer.md`'s list of groups leaves it out.

## The proposal

**One module for observations, the working-space stack's.** That stack is
lower: its evidence log already writes observations, and its window reads them.
It is also the stricter, and apothecary tightens the shared format, never
relaxes it: a closed list of properties, a subject's address checked against
its pattern, typed evidence references, a value of any shape (a print head's
position is x, y and z), times that carry a zone. The image-models branch is
rebased onto it and brings the four things the module lacks, then reads and
writes through it:
- **A subject that is a region of a picture:** the picture's digest, the
  region and its box. The Working space plan's "a frame and a region" needs it
  too.
- **`origin.by` as a record:** a reader's name, or a model's name, version and
  weights, with its `key()`, which switching a model off and trusting it look
  up. The printer poll's string becomes `{"name": …}`.
- **Evidence references to a picture** (its digest, path and box) **and to a
  model's invocation,** beside a poll, a pin, a frame, an observation and a
  record.
- **The models' properties in the closed list:** label, quantity, size, shape,
  material, colour, covered, match, rgb. With them come `overruled` in the
  apothecary block, `generic()` for the family's other apps, and the format's
  name and version on every record.

Whichever of the two lands first, the other takes the module as it landed. The
models branch goes up as a pull request after its rebase.

**Each window answers one question.**
- **Working space: what is known, and since when.** Every observation about a
  subject, from any source: a poll, a frame, the rig reader's readings, a
  model's guesses, a person's word. A model's guesses are rows beside the
  reader's, marked as guesses; the plan already calls them that. The bench's
  disagreements with what its ports say (a lead missing, a device unexpected)
  are rows of the subjects they name, not a second Bench window. A subject row
  that carlos also holds opens it in carlos.
- **Models: asking.** Which models there are, what each may be asked, and
  asking about a shape or a region. Its answers land as observations, and the
  Working space shows them. A person's word goes to the Working space's
  decisions: Models offers it, and the Working space keeps it.
- **Faces: pinning a face on a camera's picture.** One window serves three
  plans: the concert's slice 3, the Ender's faces (the working-space plan's
  slice 3, the bench plan's first camera tie) and the models plan's "rig's
  window". Its door is a camera's ring, Camera › Faces. The corners are dragged
  on the picture in the window, never drawn over the world.
- **Bench keeps its one meaning:** the toolchain window.

**Words.** In the page's text and labels:
- **Picture:** any image a person keeps or a camera takes.
- **Frame:** a picture kept with a poll.
- **View:** a picture pinned on a place. A window's arrangement is a
  **layout**.
- **Reading:** what the rig reader read.
- **Guess:** what a model answered.
- **Word:** what a person said.
- **Observation:** stays in the format and the code, not in the page's text.
- **Capture** stays the folder's name alone.

**Seats.**
- The made piece's cell is **Save variant**, twelve characters.
- Panels › Pictures seats Pictures, Models, then Gather, so Gather's going
  leaves Models where it is.
- Windows opened beside the world share one stack, as tabs, rather than each
  taking a stack.
- Lighting gets a door: Panels › Site › Lighting, one of Panels › Site's three
  free cells, and its group in `docs/viewer.md`.
- The README is served at `/readme`, rendered as `/docs` is, and Panels › Docs
  opens it as it opens the rest.

## The order

1. **The observation module,** settled before either stack is pushed: the
   working-space stack keeps it, and the models branch rebases onto it with
   its four additions. The demo then merges all three.
2. **The words,** renamed in the open stacks before they land, while it costs
   a rename and not a migration.
3. **The small seats:** Save variant, the Models seat, Lighting's door, the
   README's route.
4. **Faces,** once the Ender's camera is up: its pictures are the first a face
   is pinned on.
5. **The bench's disagreements as Working space rows,** after the camera
   ties.
6. **One stack beside the world,** when a fourth window would take a stack
   there.

## Decided

- **2026-10-31, the owner:** the working-space stack's observation module
  stays, and the models branch adds its four things to it when it rebases.

## Open, for the owner

- The words above.
- Faces as one window for three plans, behind Camera › Faces.
- The bench's disagreements as Working space rows, not a Bench window.
- Save variant as the made piece's label.
