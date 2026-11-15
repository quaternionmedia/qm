# A synth rig photographed through a concert, held in carlos: a plan

*Slices 1 and 2 are built, with a test that runs both apps end to end; slice 3
is built for the command line, and slice 4 is ready for its first photographs.
The apothecary side is on `explore/qm-family` (`apothecary/rig/`, `apothecary
rig`) and carlos's on its `feat/hold-the-rig`; neither is pushed. Slices 5 and
6 are not built.*

## What this plans

A camera looks down on a rig of a few synths. From each picture, apothecary
reads where every knob, fader, drawbar and switch stands, and which sockets
have a plug in them. It reads them against carlos's own drawing of each
device. Carlos holds the rig with those values and draws it. So, through a
concert, the rack in carlos is the rig on stage, and the readings kept along
the way are the concert's record: they can be sent to carlos again, in order,
afterwards.

This plan turns the family lane toward carlos's rigs. The
[bench plan](qm-family-carlos-2026-10-29.md) was the other way round: carlos
drawing apothecary's bench. Its slices 2 and 3 wait.

The same pipeline comes back to apothecary afterwards, one rig at a time: the
airgap's test rig, then a server room (*After the concert*).

## The two sides

The rule is the one the bench plan records: carlos holds and draws the rig,
and apothecary does everything else. Turned toward carlos's rigs, that splits
as follows.

**Carlos knows what the devices are.** Its catalogue entry for each device
says what it has and where each thing is:

- each parameter's range;
- each control's place on the panel, as fractions of the face, with its kind
  (`knob`, `fader`, `drawbar`, `encoder`, `switch`), its size, and a fader's
  orientation and travel;
- each socket's place and side;
- the device's real size, as a box in millimetres.

The rig itself is a `carlos.patch`: its devices, the leads between them, and
each module's parameter values. Carlos derives a knob's turn from its value
(−135° to +135° over the range), slides a fader to its value's fraction
("up is more"), and draws panels in its `irl` mode.

**Apothecary looks.** It owns:

- the camera, and the picture;
- where each device's face is in the picture;
- reading each control and each socket off the picture;
- following the frames through a concert;
- keeping the record.

Carlos's catalogue entries, and the rig, are read from carlos over the loopback,
or from a carlos checkout's `catalogue` folder. Apothecary keeps no copy of
them, apart from the copy a setup takes when its faces are pinned (below).

## The seam

The seam does not change: it is carlos's `hold` action on `POST /family/cue`,
from the bench plan. A reading is held as a `carlos.patch` and a state for each
module and lead:

- **The patch:** the rig's modules, each with the `parameters` it was read at,
  its leads, and `display.mode` `irl`. Carlos gets values, never rotations,
  which is what its format allows.
- **A module's state:** how many of its controls were read, and each one that
  was not, with the reason. Examples: an encoder turns without end; there was
  no pointer to see; the knob points past its sweep; the face is not in the
  picture.
- **A lead's state:** whether a plug was seen at both ends, at one end, or at
  neither, or whether an end is on a face the camera does not see. A plug seen
  in a socket that no lead names is a line on its module.
- **A socket's state:** each socket read that has something to say has a state
  of its own, by jack name: a plug seen in it, a lead's plug that is not, a plug
  no lead names, one too small in the picture to read. Carlos rings that socket
  in its level.
- **A plug moved:** a lead with one plug out, where the picture has a plug in a
  socket no lead names that takes the same plug the same way round, is held
  moved there, as a warning. That happens only where the pairing is the one
  there is. The follower carries the leads from frame to frame, so a rig
  re-patched between songs, a plug at a time, is followed a plug at a time.

Slice 1 needs nothing new from carlos.

## The setup

A setup document, `apothecary.rig-setup` version 1, says what a picture shows:

- the rig, as a `carlos.patch`;
- the catalogue entries of the devices in it, as carlos had them when the setup
  was made;
- for each module the camera sees, its face: the side, and the face's four
  corners in the picture, as fractions across and down.

The corners go top left, top right, bottom right, bottom left, the order
`apothecary/vision/projection.py` writes a picture's own corners in. Four
corners make the one mapping from a point on the face to a point in the
picture, a homography, so a face seen at a slant reads as well as one seen
straight on.

The entries are copied into the setup on purpose. The faces were pinned against
one drawing of each device, and the reading has to use that same drawing. If
carlos's layout changes later, the setup is made again; it is not quietly read
against the new layout.

## Reading a control

Every reading is made in face coordinates and sampled from the picture through
the face's mapping. The picture is Pillow's, in grey, as the plain finder reads
it, with nothing else installed. Sizes are carlos's drawing sizes read as
millimetres: at size 1, a knob is 18 mm across, a socket 11 mm, and a fader's
cap 10 mm by 5 mm. That holds until real photographs measure them (slice 4).

| Kind | Read as | Unread when |
|---|---|---|
| `knob` | The angle round a ring inside the knob where it differs most from the ring's middle value: the pointer. The angle sets the value over carlos's 270° | The ring has no pointer to see, or it points into the gap at the bottom |
| `fader`, `drawbar` | The point along the travel, averaged across the slot, where it differs most from the travel's middle value: the cap. Up, or right, is more | Nothing along the travel stands out |
| `switch` | Whichever half of the body is lighter: the lever. Up is the top of the range | The halves are alike |
| `encoder` | Never | Always: it turns without end, so a picture shows no position |
| socket | A plug, unless the centre is darker than the ring round it by enough to be an empty hole | The face is not in the picture |

Every result carries a confidence: the contrast it was read on.

## The path

1. **A picture read against carlos's panels.** *Built.* What it includes:
   - the setup document;
   - the reader above;
   - pictures of a rig drawn at known values through a pinhole camera, so
     every answer is known;
   - `apothecary rig check`, which measures the reader on those pictures;
   - `apothecary rig read`, which reads one picture;
   - `apothecary rig follow`, which reads a folder of frames in order, holds
     each reading in carlos, and keeps the record beside the frames;
   - `apothecary rig simulate`, which draws a concert: songs that move a few
     controls each and pull or push a plug between them, and from the fifth
     song on move one of a lead's plugs to another socket.

   Drawn pictures prove the plumbing, not the eyes: the same drawing rules
   both draw them and read them.
2. **Carlos turns in place.** *Built*, on carlos's side, where it only draws.
   When a hold has the same devices on the same sides, carlos turns each
   control that moved where it stands, re-patches the leads that changed (each
   one gone taken out, each new one put in, the rest left), and puts the new
   states on the elements already drawn, rather than drawing the rack again;
   a different rig is drawn afresh. A module's state may carry `controls`, a
   state by parameter name, and apothecary gives one to every control it did
   not read -- warn for one it could have read, none for an encoder -- which
   carlos draws faded, its title saying why.

   **The full test**, `tests/e2e/test_carlos_concert.py`, runs carlos from the
   checkout `CARLOS_CHECKOUT` names, follows a drawn concert of the
   Subharmonicon example into it, and holds an open rack tab to each frame's
   truth: every knob and fader within 3% of its range, the same elements from
   the first frame on, the stray plug's device a warning and the pulled lead a
   fault.
3. **Faces pinned on a real photograph.** *Built for the command line:*
   `apothecary rig setup --picture PHOTO --face MODULE=SIDE:x1,y1,...,x4,y4`
   pins each face by its four corners, in the photograph's pixels as an image
   viewer shows them, and writes the setup; `--rig` names a rig file. What
   remains is a window in apothecary's viewer where a person drags the corners
   onto the camera's picture, the first guess from the site's camera pose, the
   setup kept in the state folder like a camera's record.
4. **Real photographs, starting simple.** The first photographs are not of a
   synth. They are of one board with the leads every board has, power and USB:
   the Ender's mainboard, through the camera aimed at the Ender ([the bench
   plan](qm-family-carlos-2026-10-29.md#next-a-camera-on-the-ender)), its power
   inlet and USB socket laid out on the faces that camera sees once its pictures
   show them. The Uno is the rehearsal: `examples/rigs/uno-power-and-usb.json`
   is an Uno with a supply's lead in its barrel jack and a USB lead to the
   computer, apothecary's Uno entry lays the two sockets out on the edge they
   share, and `rig check --rig` measures the reader on drawn pictures of it.
   Then, for the mainboard:
   - photograph its sockets with each lead in and out, the camera fixed;
   - pin the edge once with `rig setup --picture`;
   - read each photograph with `rig read`, and write down which leads were in;
   - record what was read against what was there in `project/validation/`.

   Only once the sockets read true does the synth rig's turn come: knobs set by
   hand and written down, and the setup picture teaching each control its own
   look (which way the pointer is lighter, the knob's real sweep, what an empty
   socket looks like).
5. **A concert, live.** During a show, the camera keeps a frame every few
   seconds in `captures/`. `rig follow --watch` reads each new frame as it
   arrives; what remains is tying each reading to the hub's cue, the one
   carlos already holds, so the record is the show's.
6. **Printed for the rig.** From the parts library: a camera mount for a mic
   stand or a desk edge, and a corner tab for each synth, so the setup comes
   back the same at the next gig.

## Taken as the start

These defaults were chosen when slice 1 was built. Each one is a default, not a
decision the owner has made yet.

- **What a concert is:** a folder of frames, in time order by name. The record
  is `readings.jsonl` beside them.
- **Where the frames come from:** anything that writes pictures into a folder,
  whether the viewer's camera, a phone's time-lapse or ffmpeg. The follower
  reads a folder; it does not drive a camera.

## Decided

- **2026-10-29:** carlos's rigs are bolstered from apothecary, not the other way
  round; the airgap's test rig and a server room follow, each in turn.
- **2026-10-30:** go as far as is reasonable without real pictures, with
  carlos's JavaScript tested here and a full test of carlos with the demo synth
  rig; real pictures are validated first on something much simpler, power and
  USB into a device (slice 4).
- **2026-10-30:** carlos is tested for many small leads that change often. In
  carlos: a held rig's leads are re-patched in place; a lead it could not draw
  (to a jack its device lacks, two outputs or two inputs, sent twice) is refused
  rather than left off the rack; a socket carries a state of its own; a lead the
  patch names input first keeps its state. In apothecary: a socket too small in
  the picture to read is said so (`look.MIN_SOCKET_PX`), since below it drawn
  sockets were read wrong as surely as large ones were read right; each socket
  is sent its state; a plug moved is followed (*The seam*).
- **2026-10-31:** the first real photographs are of the Ender's mainboard, its
  power and USB leads, through the camera aimed at the Ender, and wait for that
  camera; the Uno's drawn pictures stay the rehearsal.
- **2026-10-31:** the owner's rig is the DFAM and the Subharmonicon, carlos's
  `moog.subharmonicon.complex` example: the Subharmonicon clocks the DFAM, and
  the DFAM returns through its VCA to a Qu-24 seen from the back. Two synths
  face the camera, and the desk is behind them. Its photographs follow the
  mainboard's; nothing about the eyes is known until real photographs are read.

## After the concert

Each one follows in turn, once the one before it reads real pictures:

- **The airgap's test rig.** The airgap part, built and on a test rig, with its
  dials and gauges read as this reads a synth's controls. The readings stand
  beside what the Airgap panel predicts for the same settings.
- **A server room.** Racks are faces, patch panels are sockets, and a camera
  looks along each row. The readings say which ports have a lead in them,
  against the room as drawn.

## The demo

Carlos runs from its `feat/hold-the-rig` clone, on 4186, as in the bench
plan's demo. Then:

```bash
uv run apothecary rig simulate --carlos http://127.0.0.1:4186 --out .cache/concert
uv run apothecary rig follow .cache/concert --carlos http://127.0.0.1:4186 --pace 1
```

The first command draws the concert's frames, with its setup and the truth of
each frame. The second sends them to carlos one a second, as a replay of the
concert. Carlos's rack draws the Subharmonicon and the DFAM in `irl` with every
knob and fader where the frame shows it. A lead whose plug was pulled is drawn
as a fault until it goes back in, and carlos turns the rack in place from frame
to frame.

The first photographs go through the same commands with the Uno's rig. A drawn
session of it comes first:

```bash
uv run apothecary rig simulate --rig examples/rigs/uno-power-and-usb.json --out .cache/uno --frames 1
uv run apothecary rig read .cache/uno/frame-0003.png --setup .cache/uno/setup.json
```

Then, for a photograph, the edge's four corners in its pixels, read off any
image viewer:

```bash
uv run apothecary rig setup --rig examples/rigs/uno-power-and-usb.json --picture uno.jpg --face uno=left:x1,y1,x2,y2,x3,y3,x4,y4 --out uno-setup.json
uv run apothecary rig read uno.jpg --setup uno-setup.json
```
