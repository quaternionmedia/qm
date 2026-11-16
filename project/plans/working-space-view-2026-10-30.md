# A working space, seen from every kind of evidence at once: a plan

*Slice 1's first two steps are built: a printer's polls kept as evidence, frame
sets kept with them, and the Working space window (`apothecary/evidence/`,
`docs/working-space.md`), walked from each of its doors in
`walkthrough/18-the-working-space.md`. The rest is not built, and its next step is the
Ender's cameras at the bench. The image models served through qmcp, an
always-optional source of readings off a picture, are planned beside it in
`project/plans/image-models-through-qmcp-2026-10-30.md`, not yet on this branch.*

## What this plans

A working space is a place where things are made and run: the garage with the
Ender 3 and its bench, a rig on a stage, the airgap's test rig, a server room.
Apothecary already knows such a place in pieces:

- the site draws what is meant to be there;
- a port says which board answers, and a poll what the printer is doing;
- a camera keeps a frame, and a picture read through a pinned face says which
  sockets have a plug;
- a person pins a board to a node, flashes a sketch, starts a print.

Each piece is right about what it sees and says nothing about the others.

This layer joins them into one view of the place, which answers four questions
at any moment:

- **What is here**: every subject some evidence speaks for, and every subject
  the site expects that nothing speaks for.
- **What state it is in**: each subject's properties, with every source's value
  side by side.
- **How we know**: for each value, where it came from (a person's word, an
  instrument, a reading off a picture, a model's guess, or a rule over other
  observations) and the evidence itself: the frame, the poll, the answer.
- **What changed**: between two moments, every transition, with the evidence
  on each side of it and the actions and directives nearest it in time.

Every line the view shows names the observations it rests on, and every
observation names its evidence. A line that cannot is not shown.

## The rules it stands on

Org records, which this layer applies and does not relax:

- *Nothing is both a claim and its own evidence*: a claim carries who made it,
  a measurement carries its method and its moment, and the two are shown
  together and never reconciled into one number.
- *A disagreement is a delta*: named by the address and field that disagree,
  neither value discarded; detection decides nothing, convergence is reported
  rather than concluded, and closing is a person's.
- *The monitoring seam, and instance identity*: a view reads a document and a
  collector reads the world; identity is asserted before a measurement is
  attributed; a view does not render a quiet state it has not earned.
- *Shrink the black box*: a model is never the check, and its calls go through
  qmcp, the one door that counts them.
- The charter's *a person is interrupted only by a decision*.

Apothecary's own:

- *Personal data stays on the device* (qm#121, open): personal data lives in
  the state folder, the picture root and the page's `localStorage`, and nowhere
  else.
- Gathering's rule for a person's word (`apothecary/gathering/judgement.py`):
  it wins over the machine, it carries, and it is also a measurement; two
  people who disagree are refused, not averaged.

## The sources

| Source | What it says now | Where it is read |
|---|---|---|
| Cameras, one or several on a place | A frame at a moment, from a pose and a lens | `vision/cameras.py`; frames under `captures/`, or a concert's folder |
| Serial: a printer | Its state, heaters, position, endstops, filament, job progress, at each poll; what it is, at `M115` | `firmware/devices.py`, `gcode.py`; `PrinterStatus` |
| Serial: a board | Which port answers, its identity, its chip, its hello | `firmware/devices.py`: detected, probed, expected, observed |
| Sensors | A printer's thermistors, endstops and runout switch, through its poll; a lighting console's levels, received on the local network | the poll; `console_feedback.py` |
| A picture, read | Each control's value and each socket's plug, with why one was not read | `rig/look.py`, `rig/reading.py` |
| A person | Pins, faces pinned, answers, a print started, a sketch flashed | `bindings.py`, `rig setup`, `gathering/judgement.py`, the routes |
| Image models, optional | Quantity, size, shape, material, colour, through qmcp | the sibling plan |

## The model

### A subject

A subject is something the view says things about. Its address is the one
apothecary already uses for it:

| Subject | Address | Example |
|---|---|---|
| a node of a site | the site and the node's dotted path | `garage:printer_1.mainboard` |
| a part of a node | the node's address and a facet: a jack, a control, a heater, a face | `garage:printer_1.mainboard#jack:usb`, `garage:printer_1.mainboard#heater:bed` |
| a module of a rig | the rig's name and the module's id, as its `carlos.patch` has it | `subharmonicon-complex:dfam#control:cutoff` |
| a board no node names | `usb:` and its identity, as `wiring/patch.py` names it | `usb:A106ZTEU` |

A registered part (`part_ref`) is a kind and never a subject: two nodes drawn
from one part are two subjects.

Each source names things its own way: a camera by a region of its frame, serial
by a port, the firmware state by a board's identity, a person in words. The
layer keeps **links** from a source's name to a subject, and a link is itself
an observation, with its origin and its evidence:

| Link | Made by | Origin |
|---|---|---|
| a board's identity to a node | a pin (`ManualBinding`) | a person's word |
| | the board last flashed with the node's sketch (`binding_source` `sketch`) | a rule over the flash record |
| a port to a board's identity | its USB serial number or MAC, as it answers (`stable_identity`) | an instrument |
| a region of a frame to a face, a jack, a control | a face pinned by its four corners (`rig setup`) | a person's word |
| a camera to the subjects in its view | its pose and lens projected onto the site's footprints (`vision/cameras.py`, `projection.py`) | a rule over the site's geometry |
| a region to a subject | a model's label | a guess, never enough alone |

Two rules govern links, and each is already in the code in one place:

- **Identity before attribution.** An observation whose source name has no link
  to a subject is kept as an unattributed **sighting** and shown as one; it is
  never attached to the likeliest subject. A port answering with no pin is
  already `usb:<identity>` in the wiring, and a region of a frame that no face
  covers is a sighting the same way.
- **A pairing is made only when it is the one there is.** The concert follower
  moves a lead's plug to a socket only when one socket takes it
  (`rig/reading.py`). Links follow the same rule: two links that send one name
  to two subjects are a conflict, shown, and nothing is attributed through
  either until a person settles it.

A port's number moves between plugs; a link is to the board's identity, never
to the port, as a pin is now.

### An observation

One thing said about one subject at one moment:

| Field | Holds |
|---|---|
| `subject` | a subject's address, or a sighting: a source's own name, a port, or a frame and a region |
| `property` | from a closed list per facet: `present`, `state`, `firmware`, `plugged`, `value`, `temperature`, `target`, `progress`, `position`, `layer`, `endstop`, `filament`, `moving`, `clear`; the image models add `quantity`, `size`, `shape`, `material`, `colour` |
| `value`, `unit` | the value, and its unit: `°C`, `mm`, `fraction`, or none for a word |
| `confidence` | from 0 to 1 as its source gave it, never rounded up; empty where a source gives none |
| `origin` | its kind and what produced it (below) |
| `at` | when it was true: a frame's taken time, a poll's `polled_at` |
| `recorded_at` | when it was written, which may be later: a frame read afterwards |
| `view` | for a reading off a picture: the camera, and how well it sees the subject (*One thing measured many times at once*) |
| `evidence` | references to what it rests on: a frame and a region, a poll and its lines, a person's record, a qmcp invocation, other observations |

| Origin | Is | Carries |
|---|---|---|
| `stated` | a person's word: a pin, an answer, a face pinned, a directive's expectation | who said it |
| `measured` | an instrument: a port answering, `M115`, a poll's `M105`, `M27` and `M114`, a sketch's hello | the method: the command, the module that found the port |
| `read` | arithmetic over a picture, the same answer for the same pixels: `rig/look.py`'s controls and sockets, a difference between frames | the reader and its version; the contrast it read on, as the confidence |
| `guessed` | a model's answer, through qmcp | the tool, the model and its version, the qmcp invocation |
| `derived` | a rule in this layer over other observations: a lead seen because its board answers; a state carried until something changes it | the rule, and the observations it took |

**Unread is not a value.** A control the reader could not read, a face not in
the picture, a model that declined, a poll that timed out: each is an
observation that says so and why, as `look.Seen.why` does, and none of them
reads as absent, as idle, or as the value before. Absence is what an instrument
measures (a port that stopped answering) or what a person states.

### Agreement and disagreement

For a subject and a property, the view puts every source's latest value side by
side and says one of four things:

- **Agreed**: sources of two or more kinds give the same value within the
  window that pairs them. The USB lead to `printer_1` answering on its port, and
  a plug seen in the mainboard's USB socket in the frame kept with the same
  poll, is *seen both ways*. Several cameras through one reader are one kind:
  they agree as *seen from several angles*, which is weaker (*One thing measured
  many times at once*, below).
- **One kind of source**: one origin says, from one angle or several, and
  nothing of another kind is placed to.
- **Disagreed**: the values differ. Both are shown, each with its origin and
  evidence, and neither is the state. The disagreement is a delta: named by the
  subject and property, opened when first seen, and found again, not opened
  again, on the next frame or poll. When the values agree again the view says
  since when and leaves it open; a person closes it.
- **Unknown**: nothing has said, or everything that said is older than its
  budget.

Three precedences are decided:

- **A person's word wins over a guess.** Where a model's answer and a person's
  differ on a subject and property, the person's is the state, without
  argument. The guess is kept beside it: it is a case where the truth is known,
  and it scores the model, as an answer in gathering scores the sorting.
- **A guess never raises a level on its own.** `warn` or `fault` on a subject
  rests on at least one observation that is not a guess. A guess alone is shown
  as one, at `none`.
- **A person's word against an instrument or a reading is a disagreement** like
  any other, not a win. A person says the lead is in and the port does not
  answer: each is true of something, and which one it is, is the person's to
  say when they close it.

Levels are the wiring's (`none`, `ok`, `warn`, `fault`). A level is computed
from the observations by rules a test holds, and never set by hand.

### One thing measured many times at once

One subject's property is often measured more than once at the same moment,
and most often by several cameras on one place: a rig seen from the front of
the stage and from the side, a printer's bed from a camera beside it and from
one across the room, a row of racks from both ends. This is a different case from two kinds of
evidence agreeing, and the layer keeps it apart.

**One subject across angles.** Each camera has its own setup: `rig setup` is
run once per camera, and pins that camera's view of each face it sees. A setup
names the camera it belongs to, which the setup format does not hold yet (a
version 2 of `apothecary.rig-setup`). Two cameras' readings are of one subject
by any of four links:

- **Both setups pin a face of the same module**, so both cameras' readings of
  `dfam#control:cutoff` are of one subject by a person's word, given once per
  camera when the face was pinned.
- **A person links a pair**: this region of one camera's frame is that region
  of the other's. It is how a subject with no face in the catalogue is linked,
  the Ender's bed or its head, and it is a person's word.
- **Both cameras' poses are known.** Each camera is placed in the site by hand,
  or calibrated by a marker both of them see. A region one camera sees is then
  projected into the space and compared with what the other sees there. That
  link is `derived`, and is made only when the pairing is unique, as the
  concert follower pairs a moved plug: one region in the second camera's frame
  lands where the first's does, and no other. Two candidates is a conflict, and
  nothing is paired.
- **The content matches, and a person takes the suggestion.** Where a region of
  one camera's frame closely matches a region of another's, the layer suggests
  linking them. A suggestion is a guess and never a link: it is shown with how
  well the two match and both regions as its evidence, and becomes a link, a
  person's word, when a person takes it. One is offered only when one candidate
  matches well and clearly better than any other, the pairing rule again. With
  Pillow alone, faces already pinned in both cameras are matched, each laid flat
  through its own corners into the face's coordinates and compared there: that
  says which module a face just pinned in the second camera is. Finding a region
  in the second camera with nothing pinned there needs a feature matcher, which
  this repository does not have. A local feature matcher makes the suggestion,
  a new dependency that enters behind the licence gate, and an image model
  through qmcp, where one is installed, gives a second opinion beside it.

A region two cameras see and nothing links is two sightings until a link joins
them.

**Each angle is its own observation.** The angles are never merged when they are
written. Each reading carries its camera and frame as evidence, and in `view`
how well that camera sees the subject:

- pixels per millimetre on the face, from the face's corners in the frame and
  its size in the catalogue;
- how oblique the face is to the camera, from the same corners, or from the poses
  where they are known;
- the reader's confidence, the contrast it read on, as `rig/look.py` reads it;
- where it did not read, its `why`: a socket under `look.MIN_SOCKET_PX`, *too
  small in the picture to read*, is unread from that angle, whatever another
  angle says.

**Combining many of one.** A combination is `derived`: a rule over the angles'
observations, naming each one it took and the rule it applied. Angles that did
not read take no part.

Some properties are averaged and some are not, so the rule is declared per
property, in one table a test holds, and a site or a setup may name another for
one subject:

| Rule | Gives | Declared for |
|---|---|---|
| `mean` | the angles' values, weighed by how well each sees the subject, with their spread | a knob, a fader, a size, a position |
| `best` | the value from the angle that sees the subject best, the others shown beside it | a property one camera is placed for: the first layer, from the bed camera |
| `each` | no combined value: every angle's, side by side | a property whose angles are not comparable |
| `agree` | for a word, the value every angle that read it gives | `plugged`, a switch's side, a colour's name |

The weight is pixels per millimetre on the face times the reader's confidence.
Whatever the rule, angles further apart than the tolerance are a disagreement
between angles: each is shown with its view, none is averaged in or chosen, and
the disagreement is a delta like any other. The tolerance is the worst error
`apothecary rig check` measures for the kind of control, unless the property's
declaration names another, and the combined value records which it used. A word
has no vote: two angles that see a plug and one that sees an empty hole are a
disagreement, not a majority, since a majority is an average of words.

**How independent the angles are.** Several angles through one reader are one
kind of evidence. They share the reader's blind spots, the room's light and the
moment: a plug the reader takes for a hole under a stage's light, it takes for a
hole from every angle. So the view says *seen from two angles*, which is weaker
than *seen two ways* (a port and a picture). *Decided:* angles never count as
two kinds toward the agreement that clears a delta or sets a level. What a
second angle changes is whether the one kind read the subject at all, and how
tightly.

**Hidden, not absent.** A subject a player's hand or body blocks from one camera
is unread from that angle and read from another. Its state comes from the angles
that read it, and an angle that did not read it never makes it absent. With
every angle unread, the subject is unread, and its last value is *last known
at*. Telling a covered subject from its state is the next section's.

**One moment across cameras.** Cameras are not synchronised: each device keeps
frames on its own clock and cadence. There are two ways to one moment, and both
are used:

- **A frame set**: the cameras are triggered together. The page holds every Live
  camera, so when it keeps a frame for a poll it keeps one from each, under the
  poll's id, and the set is one moment by construction. This is the default
  wherever one page holds the cameras.
- **A pairing window**, for frames not kept together. Frames within the window
  are one moment, and the gap is shown. The window is no wider than the time in
  which the property is seen to change (a knob between two of the follower's
  frames, a lead between two polls) and than the slowest camera's interval;
  frames further apart are each their own moment, and the state is carried
  between them.

**Size without a stated scale** (*Later*). Two cameras with calibrated poses can
triangulate a point both see, which gives millimetres without a stated
reference: a third source of scale, beside a reference a person states and a
marker of known size. The image-models plan holds that a size without a scale is
a fraction of the picture and says so
(`project/plans/image-models-through-qmcp-2026-10-30.md`, on
`claude/image-models-qmcp-e257c5`); a triangulated size is `derived`, carries
both poses and their calibration as its evidence, and is no better than the
calibration, which is measured before it is trusted.

**Tested before it is trusted.** `rig/simulated.py` draws a rig through one
pinhole from `EYE`. The test draws the same rig at the same values from two eye
positions (`scene` given a second eye, the faces pinned for each), reads both,
and holds three things:

- the combined value is no worse than the best single angle, kind by kind,
  across the drawn pictures, by `measure`'s mean and worst error;
- a disagreement between angles is surfaced: one angle's picture is altered (a
  plug drawn in one view only, a pointer turned in one) and the result is a
  disagreement, not a value between the two;
- a hidden angle never makes a subject absent: a patch drawn over a socket, or
  over a whole face, in one view leaves the state to the other view; drawn over
  both, the subject is unread.

Each is seen to fail first: a combination that averages across angles fails the
second, and one that reads a covered socket as empty fails the third. Drawn
pictures prove the plumbing and not the eyes, so each angle's own error on real
frames is measured on the first photographs from two cameras, as the Uno's
sockets are measured from one.

### Telling a covered subject from its state

A camera's view of a subject is lost in three ways, and each is unread with its
own `why`, never a value:

- **Covered**: something stands between the camera and the subject: a hand, an
  arm, a player's body, a cable draped across the face, a tool.
- **Unreadable**: nothing is in front, and the picture still cannot be read
  there: glare, a shadow too deep, blur, a socket too small in the picture
  (`look.MIN_SOCKET_PX`, already a `why`).
- **Out of view**: the face is not where its corners say: the camera knocked,
  the device moved.

**What the reader does now.** `rig/look.py` reads a socket as a plug unless its
centre is darker than the ring round it, so anything in front of an empty
socket that is not darker in the middle than at its edge is read as a plug. A
throwaway spike drew four things over an empty socket in `simulated.draw`'s
picture of `tests/test_rig.py`'s made-up synth: a patch in a hand's colour, a
dark sleeve, a cable crossing it, and a spot of glare. The reader called each
one a plug at its highest confidence; a soft shadow over the same socket it
read as empty. A covered socket is a confident wrong answer, so the confidence
does not catch it. A hand on a knob is mostly a hand turning it: the knob is
unread while it is held and read again when it is let go. What a hand does to
the reader's knobs and faders is not measured.

**Ways to tell, each with what it misses:**

1. **The picture's own limits.** A socket whose samples reach the picture's
   white limit is *washed out*, and one at its black limit *too dark to read*.
   It catches glare and nothing else, and costs nothing.
2. **The face against its own reference.** Each face keeps a reference look:
   the frame it was pinned on, or the latest frame in which it read clean. A
   control or socket is read only where the face just round it (the panel
   outside its ring, a label, a neighbour's nut) still looks as it does in the
   reference. In the spike, comparing each socket's surround with the reference
   frame marked the hand, the cable and the glare over the socket they covered,
   the hand also over part of a neighbour's surround it reached, and did not
   mark a plug pushed in with nothing in front. It missed the dark sleeve, whose
   grey is close to the panel's: it misses whatever looks like what it covers.
   Light changes the reference as surely as a hand does, under a stage's light
   above all, so levels are compared after the face's own shift in brightness is
   taken out, or edges in place of levels, whichever measures better on real
   frames. A drawn plug has no cable; a real plug's cable hangs across the face
   below it and must not mark every socket under it covered, so how much of a
   surround may differ before its socket is covered is measured on real frames
   too.
3. **Time.** A cover arrives and leaves: a surround changes and changes back
   within seconds, where a re-patch changes one socket's centre and leaves its
   surround as it was. So a change of state is taken once it has held across
   frames with the surround clean in each, and a cover is seen as the
   surround's own change, arriving and leaving. It catches the dark sleeve
   wherever the sleeve crosses something on its way in (a neighbour's nut, a
   pointer, a label), and not on a face with nothing to cross. It reports a
   change a frame or two late.
4. **Another angle, by parallax.** A cover stands in front of the face, so two
   cameras see it over different parts of the face: a hand over a socket from
   the front covers another socket, or none, from the side. A face's own marks
   fall on the same place in the face's coordinates from both. Two angles that
   disagree about a socket, each covered somewhere else, are a covered subject,
   not a changed one. It is the one test that does not depend on how the cover
   looks, and it needs a second camera on the face.
5. **A person at the subject, from a wider camera.** Motion in a room camera's
   view over the region a face occupies marks that face's readings in the span
   as possibly covered. It is coarse, holding the readings while anyone stands
   at the rig, and it records that someone was there, never who.
6. **A model's guess** that something covers a face, through qmcp. A guess may
   withhold a reading, making it unread, and never makes one: it only ever
   lowers what the layer claims.

Telling a hand by the colour of skin is not proposed: it reads people's bodies,
misses a glove, a cable and a tool, and differs from one person to the next.

**What the view does with a covered reading.** It is unread, *covered*, and
never a value, and the subject's state carries as *last known at*. A change
found when the cover lifts is reported as having happened while covered,
between the last clean frame and the first clean one after it, never at the
moment the cover lifted.

**The order proposed** (*Open*, 2), settled after the demo on the Ender's real
frames: the picture's limits and the reference
surround in the reader first, as new whys of `look`'s; time in the follower,
which already carries leads from frame to frame; parallax once two cameras see
one face; a person at the subject and a model's guess after them. Each is tested
on drawn pictures with the covers the spike drew, each seen to fail first: the
dark sleeve is the case the reference surround misses and time or parallax must
catch. Then on real frames, at the bench: a hand over the Uno's sockets, a lead
draped across its edge.

### Time

Three things carry time, and the layer keeps them apart:

- **Frames**: a picture taken at a moment, by a camera standing somewhere.
  `captures/` names them by the moment, a concert folder by order;
  `rig/concert.py`'s `taken` reads the moment from a PNG's text, a JPEG's EXIF
  time or the file's time, and the observation records which it was.
- **Polls**: a sample taken on a schedule: a printer every couple of seconds, a
  port scan, a hello. A poll gets an id when it is written, and
  `last_statuses()`, the newest poll per port, becomes a history.
- **Events**: something that happens at a moment: a flash, a job beginning and
  ending (`jobs.py`'s `LISTENERS`), a pin made, a plug moved (derived from two
  frames), a cue fired, a directive given, a person's action.

A **state** is derived: a property holds the value an observation gave it until
another changes it. The concert follower's leads, carried from frame to frame,
are this rule for one property. Each kind of source has a **staleness budget**,
past which its last value is shown as *last known at*, not as *is*: a poll after
a few of its periods, a frame after the camera's cadence. The view does not show
a quiet state it has not earned.

Pairing in time is exact where it can be built in, and a window where it cannot:

- a frame kept *for* a poll carries the poll's id, so the pair is exact;
- a frame and a poll kept apart are paired by nearest time within the poll's
  period, and the gap is shown;
- a frame whose clock is not this machine's (a phone's time-lapse) carries its
  time source and is never paired exactly.

**What changed** between two moments is the list of transitions in that span,
per subject and property, each with the evidence before and after it and the
nearest actions and directives before it. The view shows nearness and never
says *because*: a lead plugged a minute after a person flashed a board may have
been plugged for another reason.

### Directives, actions and goals

These are a person's records, kept beside the observations and addressed the
same way:

- **A goal** is what the person is working toward: *print the bracket in PETG*,
  *the Uno's power and USB read true*. It names the subjects it concerns and,
  where it can, a *done when* written over observations: the job ended `done`,
  and the bed is not empty in the frame after. When that holds, the view
  reports the goal *met*, and the person closes it, or drops it. Done is a
  claim about work, and the layer does not make it. A goal nobody has touched
  for a set time is shown as stale and offered for closing; it stays open until
  the person closes it.
- **A directive** is an instruction about the space. Some say what to keep: *a
  frame at each poll while printing*, *watch the USB lead*. Some state an
  expectation, which becomes a `stated` observation to compare against: *the
  bed stays under 60 °C*, *the DFAM's cutoff is at noon for this song*. The site
  as drawn is already a directive of this kind: a node that names firmware is
  expected plugged in.
- **An action** is something done. What apothecary does at a person's word, it
  records without asking: a flash, a print started or cancelled, a pin, a
  camera added or moved, an answer given. What a person does by hand, a lead
  plugged or a spool changed, is observed or stated.

A model may propose a goal or a directive. It is a proposal until a person takes
it, and is recorded as theirs only then.

## What it stores, and where

The layer adds no fourth place for personal data:

- **The state folder** (`state_dir()`, private as the firmware state is), one
  folder per space:
  - `observations/`, one append-only JSON-lines file a day, written under the
    state lock;
  - `links.json`, the links, each with its origin;
  - `intent.jsonl`, the goals, directives and actions;
  - `deltas.json`, the disagreements, open and closed, keyed by subject and
    property.
- **The picture root**: the frames, under `captures/` as now, or in a concert's
  folder. An observation points at a frame by its path and a region, and the
  layer copies no picture. A concert's `readings.jsonl` stays beside its frames
  as the concert's own record, which the layer reads.
- **The page's `localStorage`**: the window's layout, and nothing about the
  space.

The package reads personal data, so it is an install point of the stays-local
guard, as `rig` and `gathering` are. Nothing of what it keeps is committed: it
writes only under the state folder, which the demo keeps in the checkout's
git-ignored `.cache/demo/`. A person's goals and directives
are personal data like the rest. Backups are the person's.

A frame at every poll of a long print is a frame every couple of seconds for
hours, from each of the Ender's three cameras, so slice 1 keeps a frame set when
the poll's state changes and at every 5 % of the print's progress, never closer
together than ten seconds, and the bed camera's frame at each layer; a directive may set other numbers. Frames kept with polls live
under a **size budget per printer**, 5 GB unless the person sets another. Past
it the oldest are deleted first, a timelapse's frames only when no other kept
frame is left; a picture a person took by hand is never counted or deleted. The
folder's size against its budget is shown where its frames are listed.

What is recorded about people: subjects are things, and a person appears as a
claimant or an actor, by the name they give. That someone was at a subject, from
motion in a room camera's view, is recorded as presence, never who. A model's
sighting of a person is not recorded.

## What reads it

A collector reads the world, and a view reads a document. The layer is three
parts:

- **Collectors** write observations to the log, each from one source: an entry
  in `STATUS_LISTENERS` for printer polls, one in `jobs.LISTENERS` for jobs, the
  wiring's port scan, the picture route when a frame is kept, the rig
  follower's readings, the routes a person acts through, qmcp's answers.
- **The view** reads the log and writes one document, `apothecary.evidence`
  version 1: for a space, a moment and a span, the subjects, their properties
  with every source's value and origin, the agreements, the open deltas, the
  transitions and the goals. It is pure: the log is its argument, and it imports
  nothing that opens a port, a file or a socket.
- **Renderers** read that document and nothing else:
  - **The viewer.** A window, as every section of the page is (`panels.js`),
    called *Working space*, opened two ways: from a printer's ring, under its
    Camera (Camera › Workspace, since a ring's label holds twelve characters),
    on that printer's timeline; and from Panels › Site › Workspace, on every
    subject of the site. It lists the subjects with their
    states, and each line opens its evidence: a frame with its region drawn, a
    poll's lines, a person's record. A strip under it scrubs through time, and
    *what changed* is the span between two marks. The 3D view can colour a node by its level.
    `GET /sites/{s}/evidence?at=&since=` answers the document.
  - **Carlos.** The seam does not change: the hold action on `POST
    /family/cue`, a `carlos.patch`, and each module's, lead's and jack's state
    as a level and its lines. The lines come from the document, so each says
    what it rests on: *seen: answering on its port; seen plugged in camera_1 at
    14:02*, or *disagree: answering on its port; no plug seen in camera_1 at
    14:02*. Carlos judges none of it, and refuses fields it does not define, so
    the evidence stays in apothecary. What reaches carlos and qmcp names a frame
    by its path and region and a poll by its id, and never carries a picture.
  - **qmcp's human queue** (`POST /v1/human/requests`). Only a decision goes
    there: a delta at `warn` or `fault` that has not converged within its
    budget, a sighting that needs a person to say what it is, a goal reported
    met. A request carries the subject, both values with their origins, and the
    evidence by reference; the answer comes back as a `stated` observation or a
    link, its claimant the person who answered. The same decisions can be
    answered in the window; qmcp is the door for a person away from it, its
    voice path among them.
  - **The command line**, for machines and debugging: `apothecary evidence
    show`, `apothecary evidence changed --since`.

`apothecary problems` lists the open deltas beside its problem space
(`apothecary/spaces.py`), which is a different thing. This layer is called
*evidence* in code, so the two do not meet by name.

## What exists, and what it generalises

| Here now | What it does | What this makes of it |
|---|---|---|
| `wiring/patch.py`: `Evidence`, `State`, `ModuleState`, `LeadState` | The bench's states (present or absent, firmware, leads seen or declared, how known) as levels and lines, with the evidence beside the patch | The closest thing to this view, for the bench at one moment. `Evidence` becomes observations with origins; `_state`'s lines become a renderer over the document, with the same levels by the same rules; the patch stays |
| `firmware/devices.py`: detected, probed, expected, observed, identified | Five views of one board, kept apart so the page can show where they disagree | Five origins; the principle is this plan's, for one board |
| `devices.last_statuses()`, `STATUS_LISTENERS` | The newest poll per port, in memory, and the hook every poll passes | A collector on the hook, and a history in place of the newest alone |
| `firmware/bindings.py`: `NodeBinding.binding_source` | A board tied to a node by a pin or by its sketch | Links, each with its origin |
| `jobs.py`: a job's record, `LISTENERS` | When a print began and ended, and how far it got | Events, and what a goal's *done when* reads |
| `slicer/models.py`: `Estimate.layers` | The count of layers the slicer wrote into the G-code | Which layer of how many each timelapse frame is |
| `vision/cameras.py`: pose, lens, `lands` | Where a camera stands and where its centre ray lands | Which subjects each camera can see; several cameras on one place |
| `rig/look.py`: `Seen`; `rig/reading.py`: faces, `held` | Each control and socket read off a picture, with why one was not | `read` observations, unread kept as unread, a face as a link; covered, washed out and out of view as new whys |
| `rig/concert.py`: frames in order, leads carried, `readings.jsonl` | A rig followed through time, a plug moved only when the pairing is unique | The state-carrying rule and the pairing rule, made general |
| `rig/simulated.py`: a rig drawn through one pinhole; `rig check`'s error per kind | The reader measured on pictures whose every answer is known, from one eye | The two-angle test, and the tolerance past which angles disagree |
| `gathering/judgement.py` | A person's word wins, carries and scores; two people who disagree are refused | The precedence of a person's word, for every subject |
| `console_feedback.py`: `ConsoleState` | A console's levels, received on the local network | A sensor stream of the same shape, for a theatre |
| `airgap_metrics.py`: `airgap/metrics/1` | The Airgap panel's prediction, as a document a view reads | An expectation beside the test rig's readings |
| `Assembly.status` | One value on a node, overwritten by each poll's site sync | A summary drawn from the document; the history is the log's |

What it replaces, once each renderer reads the document: the wiring's
line-building in `_state`, and `_LAST_STATUS` as the only memory of a printer's
polls. Slice 1 replaces nothing.

## The first slice: the Ender seen by its cameras and by its port

Three cameras go on the Ender 3 to tie printer monitoring to them, each placed
for its own work:

| Camera | Placed | Sees | Reads first |
|---|---|---|---|
| bed | close on the bed | the bed, the first layer, the print growing | a frame at each layer, the print's timelapse; the bed clear or not before a start |
| head | close on the hotend and the extruder | the nozzle, the extruder's feed, the carriage and the gantry moving | `moving`, beside the poll's `printing` |
| room | further away | the whole printer and the space round it: bed, gantry, spool, the mainboard's edge and its lead | the lead into the mainboard; the bed and the head again, from a second angle |

The bed and room cameras both see the bed, and the head and room cameras both
see the head, so the Ender gives many of one from its first frames. The Ender
3's bed moves front to back and its gantry up and down: a camera fixed to the
bed keeps the print still in its frame, as a timelapse wants, and one fixed to
the frame watches the bed slide (*Open*, 3).

What is ready: `camera_1`, added on `printer_1`'s ring, its device one of the
browser's cameras, with Live and Take picture; the printer's Machine polling
it; the mainboard's polls reaching carlos as lines; `rig setup` and `rig
follow`. `camera_1` takes whichever of the three places its mount suits, and
the other two are added on the same ring. The bench plan's *Next: a camera on
the Ender* names three pieces the tie needs. This slice puts them in order and
lays the layer under them, one pull request a step, stacked.

1. **The log, and polls into it.** The observation, its origin, the evidence
   reference and the append-only log in the state folder; a collector on
   `STATUS_LISTENERS` that writes each poll of a pinned port as observations of
   the node it is pinned to (`present`, `state`, each heater's `temperature` and
   `target`, `progress`, `position`, `endstop`, `filament`), and a poll of an
   unpinned port as a sighting. Each poll gets an id, and its raw lines are its
   evidence. A test on `serve --demo`'s simulated Ender holds it: polls in,
   observations out, the pin as their link.
2. **Frames kept with polls.** The page holds the cameras and drives the polls,
   so the page keeps the frames: while the Ender's cameras are Live and
   `printer_1` is polled, a frame set (one frame from each Live camera) when the
   poll's state changes and at every 5 % of progress, never closer together
   than ten seconds, each frame posted to the picture route (`POST
   /photos/pictures?site=&camera=`) with the poll's id. The route keeps the
   frames under `captures/` as now, and writes each as evidence beside that
   poll. That is a print's record of polls and pictures, readable as a timeline
   before any picture is read, and a folder `rig follow` reads, kept under the
   printer's size budget. The *Working space* window's first form is
   `printer_1`'s timeline, opened from its ring or from the site's menu: state
   and heaters as a strip, each camera's frames in a row at their polls. It starts with
   `camera_1` alone and takes the others as they are mounted. Whether one page
   holds three cameras streaming at once depends on the USB bus and each
   camera's format, and is found at the bench; a camera the page cannot open is
   unread, with why, and never absent (*Open*, 4).
3. **The lead, seen two ways.** The Ender's mainboard face laid out: the USB
   socket and the power inlet placed as fractions of their face, as the Uno's
   edge is, measured off the room camera's own frames, and pinned once with
   `rig setup`. Each kept frame is read through the face, and the USB lead's
   `plugged` from the picture stands beside its port's `present`. The lead's
   state in carlos says both, and where they disagree. A socket the room camera
   sees under `look.MIN_SOCKET_PX` is unread, *too small in the picture to
   read*, and the lead is then seen one way, which the view says. It is
   validated as the Uno is: the lead in and out by hand with the camera fixed,
   and what was read against what was there, in `project/validation/`.
4. **Moving, seen two ways.** A frame compared with the frame before it inside
   the head camera's view of the carriage and gantry: `moving`, read, with the
   difference as its confidence, beside the poll's `printing` or `idle`. A print
   the poll calls printing while nothing moves across several frames is a delta
   at `warn`: a pause, a stall, or a camera knocked aside. The view names those
   and decides none. This is arithmetic, not a model; changing light is its
   known weakness, and it is measured on the Ender's own frames before any
   threshold is trusted.
5. **The bed, and its timelapse.** A `layer` is a new highest height in the
   poll's `M114` position that holds into the next poll, since a lift between
   moves rises and falls again; the slicer's estimate gives how many layers it
   wrote. At each layer the bed camera's frame is kept, numbered as which layer
   of how many, and the frames in order are the print's timelapse, a strip in
   the window. The frame is kept at the poll after the layer changes, with the
   head wherever it is then. Before a start, the bed camera's frame against its
   reference of the empty bed reads the bed `clear` or not: the reference of
   *Telling a covered subject from its state*, applied to a whole bed. The view
   shows it beside a print being started, and refuses nothing.
6. **Many of one, on real frames.** The bed from the bed and room cameras, and
   the head's motion from the head and room cameras, each combined by its
   property's rule or kept as a disagreement between angles; a hand in front of
   one camera, unread there and read from the other; each angle's error
   measured on the Ender's own frames.

After step 4 the four questions have answers for one printer: `printer_1`, its
mainboard and its lead are here; it is printing, at these temperatures, and seen
moving; that is known by its port and by its cameras, each line opening its
poll or its frame; and the window shows what changed in the last hour. The image
models' readings (whether a part is on the bed, its colour, a print gone to
spaghetti) arrive as guesses once the sibling plan's first slice is built, and
change none of the above.

## The slices after it

Each follows once the one before it reads real evidence.

- **The rig through a concert.** The concert's readings become `read`
  observations of the rig's modules, the follower's carried leads the derived
  state, and the hub's cues events (the concert plan's slice 5). A setlist is a
  directive: each song's expected values beside the readings. Two cameras on
  one rig, each with its own setup pinning the faces it sees, kept as a frame
  set where one page holds both, or paired within a window where each writes
  its own folder. A knob both see is combined with its spread and *seen from two
  angles*; one a player stands in front of is unread in one camera and read in
  the other, never absent; a fader the two read further apart than `rig check`'s
  error for faders is a disagreement between angles, both shown. The simulated
  concert is drawn from both eyes first, as *Tested before it is trusted* has
  it.
- **The airgap's test rig.** Three origins for one property: the Airgap panel's
  prediction (`airgap/metrics/1`), the dials and gauges read off a picture, and a
  board on the rig reporting over serial. A board's readings need a line format
  for sensors, which is a seam of its own (*Open*, 1).
- **A server room.** Racks are faces, patch panels are sockets, a camera looks
  along each row, and the room as drawn is the expectation. A row seen from both
  ends is many of one at its plainest: a port far down the row is too small in
  the picture to read from the near end and read from the far one, so each port's
  state comes from the angle that sees it, and a port both read is combined or
  is a disagreement between them. What a switch says
  of its own ports arrives over the network, which the stays-local guard
  refuses; until a record allows it, the room is known by camera and by what a
  person states.

## The governance it needs

Drafted when its slice is built, in `governance/qm/adr/` on
`project/apothecary`, and ratified by a person:

- **A project record for the evidence model**: the observation's fields, the
  origin kinds, unread as no value, identity before attribution, a pairing only
  when unique, a person's word over a guess, a guess never raising a level on
  its own, every rendered line naming its observations, and many of one: each
  angle its own observation, a suggested link no link until a person takes it,
  the combining rule declared per property, angles past the tolerance a
  disagreement whatever the rule, no vote, angles one kind of evidence, a
  covered reading unread and never a value. It tightens the org records above.
  Its teeth are tests, each seen to fail: a renderer handed an observation with
  no evidence refuses it; a guess alone yields `none`; two links for one name
  attribute nothing; the two-angle test's three holds; a socket drawn covered
  reads unread.
- **An amendment to *Personal data stays on the device*** (qm#121, open). §6
  names the log, the links, and a person's goals and directives in the state
  folder, and the frames' retention; §1 names the new package as an install
  point. It also says whether carlos and qmcp, reached over loopback on this
  machine and each keeping its own database, are *here*: carlos already holds
  the bench's states, and qmcp would hold a person's questions and answers. A
  capture on the server, once it is built (*Later*), is a subprocess outside the
  socket guard that the record names, as it names OpenSCAD.
- **For governance/qm**: whether *A disagreement is a delta* covers a working
  space's runtime state. Its rule (one delta per address and field, closed by a
  person) fits this layer; its queue is the organisation's, and a garage's lead
  disagreeing with its port does not belong in it. A project cannot relax an
  org record, so the record's scope has to say where it stops.
- The site hierarchy record (`DRAFT-site-structure-substructure-feature-hierarchy`)
  gains a reader of its node addresses, and a facet after them that is this
  layer's.

## Open, for the owner

Each is settled where it names, not before.

1. **A line format for a board's sensor readings**, beside its hello: a
   standard one with more than one implementation (*Seams on standard
   protocols*), or the hello's own form extended. Settled when the airgap's
   test rig is built.
2. **Telling a covered subject**: which tests come first (proposed: the
   picture's limits and the reference surround, then time, then parallax);
   which frame is a face's reference (the one it was pinned on, or the latest it
   read clean); how much of a surround may differ before its subject is
   covered, with a real plug's cable not marking every socket under it; and how
   many frames a change holds before it is taken. Settled after the demo, on the
   Ender's real frames.
3. **The Ender's camera mounts**: the bed camera on the bed, still to the print,
   or on the frame, watching the bed slide; the head camera on the carriage,
   moving with the nozzle, or on the frame; the room camera where the
   mainboard's edge is large enough in its picture to read. Settled at the
   bench.
4. **Three cameras on one page**: whether the page holds them streaming at
   once; if not, which camera a second page takes until the capture on the
   server (*Later*). Settled at the bench.

## Later

In no slice yet; each waits on what it names.

- **A capture on the server**, a subprocess reading the camera devices, so a
  long print keeps its frames with no page open. It is outside the socket guard,
  so the personal-data record names it, as it names OpenSCAD. It waits on the
  page's frame sets running on the Ender.
- **Size by triangulation**, from two cameras with calibrated poses: a third
  source of scale, beside a reference a person states and a marker of known
  size. It waits on poses calibrated and their error measured.
- **The head parked for each timelapse frame**, by a hook at each layer change
  in the G-code the slicer writes. It is the printer's seam, and waits on the
  timelapse.
- **A start that waits on the bed seen clear.** This layer shows `clear` beside
  a print being started and refuses nothing; holding a start is the printer's
  seam, and waits on `clear` read true on the Ender's own frames.

## Decided

- **2026-10-30:** a layer that correlates a working space's cameras, sensors,
  serial feedback, a person's directives, actions and goals, and image models'
  readings into one view is queued, planned and not built. Its first slice ties
  the Ender's camera to its polls. The image models through qmcp are an
  always-optional source, planned on their own.
- **2026-10-30:** the layer plans for one thing measured many times at once,
  above all one subject seen from several camera angles. Each angle is its own
  observation, carrying how well its camera sees the subject. A number is
  combined with its spread and a word is agreed or not, never voted. Angles that
  differ beyond the reader's measured error are a disagreement, never an
  average. Several angles through one reader are one kind of evidence. An angle
  that does not see a subject never makes it absent.
- **2026-10-31:** two cameras' readings are linked by a face pinned in both, a
  person linking a pair, known poses (placed by hand or calibrated by a marker
  both see), or a suggestion from matching content that a person takes.
  Combining is declared per property (a weighted mean, the best-placed angle,
  each angle alone, or agreement for a word), and a site or setup may name
  another for one subject; whatever the rule, angles past the tolerance are a
  disagreement. The weight is pixels per millimetre times the reader's
  confidence, and the tolerance `rig check`'s worst error for the kind unless a
  property names another. Frames are one moment as a frame set where one page
  holds the cameras, and otherwise within a window no wider than the property's
  time to change and the slowest camera's interval.
- **2026-10-31:** the Ender has three cameras: one on the bed for the first
  layer and the print's timelapse, one on the hotend, the extruder and the moving
  parts, and one further away on the whole printer. Triangulation as a source of
  scale is later. A covered subject is unread and never a value, and the ways to
  tell one are planned with what each misses.
- **2026-10-31:** the first demo is slice 1's first two steps on `serve --demo`:
  the simulated Ender's polls in the log, frame sets from its cameras kept with
  them, and the *Working space* window showing `printer_1`'s timeline, opened
  from the printer's ring and from the site's menu. The page takes the frames;
  a capture on the server is later. A frame set is kept when the poll's state
  changes and at every 5 % of progress, never closer than ten seconds. Kept
  frames live under a 5 GB budget per printer, the oldest deleted first and a
  timelapse's last, pictures taken by hand never. A person's word against an
  instrument is a disagreement to close. People are recorded as presence,
  never who. Only references reach carlos and qmcp, and qmcp's queue takes
  unsettled `warn` and `fault` deltas, sightings to name and goals met. A goal
  untouched for a set time is shown as stale. The matcher behind a suggested
  link is local first, with a model as a second opinion. The names are
  `apothecary/evidence/`, `apothecary.evidence` and *Working space*.
