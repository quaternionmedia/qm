# The bench as a rig carlos can draw: a plan

*Slices 1 and 4 are built, on `explore/qm-family` (`apothecary/wiring/`) and,
for carlos's hold, on carlos's `feat/hold-the-rig`, with a test that runs both
apps end to end; neither is pushed. Slices 2 and 3 are not built, and wait: the
lane turned toward carlos's own rigs, in
[A synth rig photographed through a concert](carlos-concert-rig-2026-10-29.md).
Next is a camera on the Ender (below).*

## What this plans

Apothecary knows what is on its bench in pieces: a port and what answered on
it, the sketch last flashed there, the scene node a board is pinned to, a
picture of the bench. Carlos, in the instruments family
([quaternionmedia/carlos](https://github.com/quaternionmedia/carlos)), draws a
rig from real gear, patched on the face its sockets are on, and writes the whole
rig as one versioned JSON document, `carlos.patch`.

The plan joins them into one loop: a picture names a device, the wiring and the
IO configuration say what it is joined to, and a pipeline keeps the rig as
written beside the rig as observed, so that where they disagree is something
both pages show.

## The two sides as they stand

Apothecary (`irl`):

- `firmware/devices.py` holds five views of a board on a port: detected,
  probed, expected, observed (its hello) and, for a G-code firmware, identified
  (`M115`). A board's identity is its MAC, else its USB bridge's serial number,
  else the port.
- `firmware/bindings.py`: `bindings_for_site` gives one row per scene node
  that names firmware or has a device pinned to it, with the board on it now.
- `parts/boards/` draws five boards from their makers' drawings; a
  described board's `part.json` carries its bounds in millimetres.
- `vision/`: the finders (`stated`, `plain`) find shapes and do not name them.
  `FoundShape.label` is read only by `ScaleReference.known_shape`. A local model
  behind the finder is [its own plan](photo-finders-local-models-2026-09-21.md).
- `lighting.py` already uses *rig* and *patch*, for a theatre's fixtures and
  their DMX addresses. This work is called *wiring* so the two stay apart.

Carlos (`instruments`; default branch `they`, read at a5540e7, and
`feat/family-control` at 91678af):

- A catalogue: one JSON file per device, addressed `<maker>.<model>`; each
  socket says its signal, its carrier, its connector and the side it is on;
  `layout.box` is the device's size in millimetres. The connector and category
  vocabularies are closed.
- `carlos.patch` version 3: modules, connections (output end first), groups,
  display, MIDI bindings. Unknown fields are refused. `POST
  /api/patch/validate` checks a document; the browser additionally refuses a
  type or a jack its build does not have.
- `POST /family/cue` and `GET /family/state`, on `feat/family-control` only:
  a hub loads one of carlos's shipped examples or turns the rack, and every
  open tab draws what the server holds. Persistence waits on carlos's
  datastore decision.
- Outbound calls are planned, never sent.

## The seam

Connect, not merge (the draft record *a family is bordered by what it
drives*). Apothecary writes `carlos.patch` documents and catalogue entries in
carlos's own device-file format, and reaches carlos over REST; neither imports
the other's source. The replaceability test holds: anything that reads a
`carlos.patch` could stand where carlos stands.

Carlos refuses unknown fields, so how apothecary knows each module (the port,
the identity, the binding, the firmware) travels beside the document, never
inside it.

## The loop

1. **Declared**: a `carlos.patch`, the rig as somebody wrote it.
2. **Observed**: what apothecary sees: ports, probes, hellos, bindings,
   pictures.
3. **Reconciled**: the rig as it is, as a `carlos.patch`, with the evidence for
   each module and every disagreement with the declared one.
4. **Shown**: in carlos's rack, which holds what it is sent; on apothecary's
   Bench later.
5. **Acted on**: a board plugged in, a sketch flashed, a lead moved, or the
   declared rig edited. Then observed again.

The disagreements are of five kinds:

| Kind | Means |
|---|---|
| missing | declared, and nothing observed answers for it |
| unexpected | observed, and not declared |
| wrong firmware | running other than what was flashed, or flashed from an older source (`ExpectedFirmware`) |
| unplaced | a node whose part has no catalogue entry, so it has no type to be |
| unobserved lead | declared, and invisible to apothecary (a 3.5 mm lead is): kept, marked, never *missing* |

## Slices

1. **The bench as a patch** (built). `apothecary/wiring/` writes a site's
   tree, bindings and ports as a `carlos.patch`: a module per node whose part
   has a catalogue entry, one per board on a port no node names, the computer
   apothecary runs on as `apothecary.host`, and a USB lead to it from every
   expected board and every board answering. The evidence, each module's and
   lead's state, and the unplaced nodes come beside it. `GET /sites/{s}/wiring`
   answers them all; `GET /sites/{s}/wiring/patch` answers the document alone,
   for carlos's Import. The entries are in `apothecary/wiring/catalogue/`, in
   carlos's file format.
2. **A picture names a device.** An identification is a ranked list that may
   decline. First by footprint: the plain finder's rectangle and a stated
   scale give millimetres, compared with each board's bounds. The ratio alone
   cannot tell a Teensy 4.0 from an ESP32 devkit (both about 2:1) or an Uno
   from the Creality board (about 1.3), so without a scale it declines between
   them, and what USB says is plugged in breaks the tie. The name goes into
   `FoundShape.label`, which `known_shape` already reads. Then a tag engraved
   on a printed case, and a local model as the finders plan has it. Measured
   with a bench like `vision/bench.py` before any number is quoted.
3. **IO configuration.** `firmware.json` gains an `io` block (pin, role,
   direction, signal) that becomes jacks on the board's entry (header pins on
   its top face) and connections at pin level: the footpedal's switches, the
   blink sketch's LED. A sketch can say its own in its hello, so the declared
   pins and the running ones compare.
4. **The loop closed** (built, against the site as drawn). `serve --carlos
   URL` sends the garage's wiring to carlos as a hold at the start and again
   whenever it changes (`wiring/carlos.py`'s `Follower`, every two seconds);
   `POST /sites/{s}/wiring/send` sends it now. Carlos draws it, so a board
   plugged in or flashed on the apothecary side is redrawn in carlos's rack.
   A printer's polls are part of it: while its Machine polls it, the
   mainboard's state says what the last poll found -- printing, how far through
   its job and how long in, its heaters -- and warns when it is offline or in
   maintenance. `tests/e2e/test_carlos_bench.py` holds the loop with a real
   carlos: the bench held at the start, a flash through apothecary's upload
   route drawn in an open tab without a reload, and the printer's poll said
   under its mainboard. Not built: a Bench window on apothecary's own page,
   and a lead that apothecary cannot observe (an audio lead) declared anywhere
   but in the site as drawn.

## What carlos needs

One action, in its repository: `/family/cue` takes `{"hold": {patch,
devices, states}}` beside `patch` and `turn`, holds it, and answers it in
`/family/state`, and an open tab draws it -- the held devices for that rig
only, its cables as sent, and each module's and each lead's state as a level
and its lines. Its catalogue, its lead list and its routes stay as they are.

Checked on 2026-10-29 with carlos's own `patch_format.load` and
`catalogue.load_device`, from a clone, on the garage with its mainboard
pinned: both branches accept the document. On `feat/family-control` the
footpedal's entry loads as it is, and the others are refused for the board and
computer categories and the `micro-USB` connector, which is why a held rig's
devices are checked for their shape rather than against carlos's vocabulary.
On `they` every entry is refused, since its sockets have no `carrier` and no
`data` signal. A USB socket's carrier is written out, because carlos's loader
refuses the default `direct` for a USB connector rather than inferring it.

## Decided

The owner's, on 2026-10-29:

- **Carlos only holds and draws the rig, from outside; everything else is
  apothecary's.** Apothecary observes, identifies, configures, reconciles and
  sends; carlos holds what it is sent and draws it, its connections and their
  states, judging none of it. A held rig's cables are drawn as they are sent,
  whether or not carlos's own lead list has the cable.
- **The device entries travel with the rig.** Apothecary sends the entries a
  rig names beside it, and carlos holds them for drawing that rig; carlos's
  catalogue does not change.
- **The declared rig is the site as drawn.** A node that names firmware or has
  a device pinned to it is expected plugged in, with a USB lead to the
  computer; a board placed and naming neither is on the bench and not
  expected.
- **Carlos draws four states**: present or absent (and a port no node names,
  unexpected), firmware, leads seen or only declared, and how each board is
  known.
- **Work in flight is taken as it is**: this branch stacks on
  `build/iterate-ui`, and carlos's side builds on `feat/family-control`'s
  `/family/cue`, as a third action beside `patch` and `turn`.
- **The first demo is the simulated bench**: `serve --demo`'s simulated Ender
  and devkit, sending to a carlos on this machine.

## The demo

The simulated bench, sending to a carlos on this machine. In carlos's clone, on
`feat/hold-the-rig`:

    uv run carlos serve --port 4186 --state <a folder for its database>

and in this checkout:

    uv run apothecary serve --demo --port 6284 --carlos http://127.0.0.1:4186

Then `http://127.0.0.1:4186/rack` is the garage's rig as apothecary sees it:
printer_1's mainboard present and pinned, the ESP32 devkit and the footpedal
expected and absent with their leads drawn broken, the scripted Uno and devkit
answering on ports no node names, and the Uno lying on the bench, not
expected. Flashing `esp32_blink` onto the devkit from apothecary's page
(`http://127.0.0.1:6284/viewer`, the devkit's Flash sketch) turns it present in
carlos's rack within two seconds, its port no longer unexpected; the footpedal
on the scripted Uno does the same.

## Next: a camera on the Ender

The owner aims a camera at the Ender 3 next, to tie printer monitoring to it.
What is ready for it:

- **The camera.** A camera is a part of the garage (`camera_1`), added on
  printer_1's ring with Camera › Add here, its device one of the browser's
  cameras; Live shows its video and Take picture keeps a frame in `captures/`
  ([pictures.md](../../../../docs/pictures.md#cameras)).
- **The monitoring.** The printer's Machine polls it -- state, progress,
  heaters -- and each poll now reaches carlos as lines under printer_1's
  mainboard, beside what the port says: present, Marlin as it answered `M115`,
  pinned by its serial number.
- **The reading.** `apothecary rig` reads sockets off a photograph through a
  face pinned by its corners (`rig setup`), and follows a folder of frames as
  they come (`rig follow --watch`); a board's power and USB leads are its first
  validation ([the concert plan](carlos-concert-rig-2026-10-29.md), slice 4).

What the tie still needs, once the camera's pictures show what it sees:

1. **The Ender's faces laid out.** The sides of the printer the camera sees,
   with the sockets on them (its power inlet, the mainboard's USB) placed as
   fractions of each face, as the Uno's edge is; measured off the camera's
   own pictures.
2. **Frames kept with the polls.** While a print runs and the camera is live,
   a frame kept at each poll, or each step of progress, beside the poll it was
   kept at: a print's record of pictures and polls, and a folder `rig follow`
   reads.
3. **Two kinds of evidence for one lead.** The USB lead to printer_1 is seen
   by its port answering, and could be seen in the picture as well; the lead's
   state in carlos says both, and which disagree.

Which of these comes first is the owner's to say once the camera is up. The
concert plan's first real photographs are of this mainboard's power and USB
leads ([its slice 4](carlos-concert-rig-2026-10-29.md#the-path)), so the faces
laid out serve both.

## After carlos

The family record names more members that meet apothecary's bench: `stomp`
(in both `irl` and `instruments`, beside the footpedal), `datum`, and the
show-control hub whose cues carlos's `/family/cue` answers. None of them has
been read for this plan.
