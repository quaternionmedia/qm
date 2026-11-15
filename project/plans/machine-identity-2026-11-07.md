# Each machine keeps its own: a plan

*Built: the stop goes to whatever is on a port, a port that changes hands
forgets what was held in memory for its last board, a bed reading is the board's
that took it, a pin or a flash kept by port is careful of the board that takes
the port, a kept file is sent to the kind of machine it was kept for alone, and a
machine is planned before its board is connected. Slice 6, the page's own marks
by board, is not built. Each slice is one pull request.*

## What this plans

Apothecary drives an Ender 3 (Marlin), a CNC router (GRBL) and ESP32 devkits
over serial. It finds each board by its port name, and a port name moves: the
Ender has come back as `/dev/ttyUSB0` after a night as `/dev/ttyUSB1`, and the
router's CH340 came up on `/dev/ttyUSB0`, a name the Ender once had. Much of
what the app keeps about a machine is keyed by that name, and much of what one
kind of machine does is reachable from another. So a board can wear another
board's record, and a file made for one kind of machine can be sent to the
other.

It has happened. The router wore the Ender's bed mesh, drawn as a relief over its
table, because bed readings are kept and fetched by port name alone. That is one
case of a family; this plan closes the family, not the case:

- **One answer to "which board is on this port, and what kind of machine is it".**
  Every record and every cache asks it, and nothing answers it again for itself.
- **A record belongs to the board that made it**, and a cache keyed by a port
  forgets its board when the port changes hands.
- **One kind of machine's work is refused on another at the server**, whatever
  the page believes, and the stop goes to whatever is on the port, in its own
  dialect.

## What was found

A read of the firmware seam, the jobs, the slicer, the toolpath, the preview,
the page's machine code and the family members, on main at 8601a5e. Each finding
names where it is; the ones marked *now* give a wrong outcome on the machines as
they are, the others need a sequence that has not happened yet.

### A board wearing another board's state

| What | Keyed by | Where | Outcome |
|---|---|---|---|
| Bed readings | the port name only; a reading records no board | `devices.leveling_records` (`rec.port == port`), the page's `refreshReading`, the Machine's `loadLevel` | *now*: the router wears the Ender's mesh; a second printer would show the first one's |
| A pin whose identity is a port name | the port name: `same_device` answers yes for any board there | `bindings.same_device`, then `_pinned_at`, `_sync_printer_status`, the family's `Machine` | *now* once the router is pinned from the port list (a CH340 with no serial number pins as its port): the Ender on that name takes the router's node, its polls write onto both, and a step for the router goes to the Ender |
| The last poll, the stream job, the bed-reading job, the comms log, the control latch, the held link | the port name, in server memory | `devices._LAST_STATUS`, `_PRINTS`, `_LEVELING`, `gcode.PrinterLinks`, `ControlLatch` | the next board on the port is shown the last one's state and log, refused as "printing", or found armed |
| A flash record made before the board was probed | the port name | `devices.make_flash_record`, `last_flash` | a printer later on that port "should run" the sketch, and the sketch's node binds to it |
| The page's machine marks, where a machine stands, a drawn toolpath, the board model | the port name, never cleared when the board changes | `ensureMarks`, `whereByPort`, `toolpathByPort`, `boards.js` | a page left open across a replug moves one machine's marks with another's polls |
| A device record | the port, checked against what the port list sees there | `FirmwareState.cached_device` | checked; trusted unchecked when the port list cannot be read |

### One kind of machine's work reachable from another

| What | Where kind is checked | Where it is not | Outcome |
|---|---|---|---|
| A kept file streamed to the other kind | nowhere: a kept file records no kind; a slice's and a toolpath's records do, and nothing reads them before a stream | `devices.start_print`, the family's `run` | *now*: `examples/gcode/dry-run-square.gcode` streams on the router: its `G28` moves it to a stored position, and its `G4 P500` dwells wait 500 s each, GRBL's `P` being seconds |
| A G-code check per dialect | one list for both | `gcode.check_gcode` | a file with Marlin's `M117` or `M84` is accepted for a cut; GRBL answers a code it does not take with `error:20`, and the link fails the cut at that line (`gcode.py` raises on an `error:` answer) |
| The stop | the server takes only the port's own dialect's stop | `devices.printer_control`, `normalise_control` | a Machine that takes a router for a printer sends `M112`; the server refuses it and nothing stops |
| A bed reading started on a router | the page hides the card; the server checks only for a link | `devices.start_leveling` | `G28` then `G29` sent raw to a router: it moves, then refuses |
| The page's kind for a board not yet known | four defaults that disagree | `machine.js` `kindOf` (printer), `machine_words.kindOf` (devkit), the page's `machineKindAt` (printer), `boards.watch` (printer) | a router not yet identified is drawn, polled and offered controls as a printer |
| Corner moves on a router | the ring refuses a bed reading, not a corner | `machine.js` `carryOut` | four `G1` moves a router accepts |

Kind is decided once, at identification (`devices._identify`, `PrinterInfo.machine`),
and read through `machine_kind`; that is sound, and the seam keeps it.

## The seam

`apothecary/firmware/occupants.py`, one module, one question: **who is on this
port now.** Its answer, an `Occupant`, is the port, the board's own key, its
identity as pins store it, its kind (`printer`, `router`, `devkit`, or none while
unknown), its dialect and its firmware's name, built from the device record
`cached_device` has already checked against the port list.

- **The board's key** is its MAC or its USB bridge's serial number when it has
  one. A bridge with none, as the router's CH340, is keyed by its maker and
  product (`vid:pid`, in one case): that follows the board across port numbers,
  and two such bridges of one make on the machine at once are told apart by
  nothing, so while both are present, records under that key are attributed to
  neither: a new reading is refused saying why, and the list is empty.
- **A port that changes hands**: the port list remembers what it last found on
  each port, kept while the port is empty; when another board is found there,
  one function, `devices.forget_port`, lets go of every cache the firmware
  package keys by a port: the last poll, a finished job, the held link, the
  latch and the comms log. Those caches are read only after the port list, so
  nothing reads the last board's state before it is forgotten.
- **Kind at the server**: a job's file, a bed reading, a control line and a
  family step each ask the occupant's kind, and refuse on a mismatch, with what
  to do instead. An occupant of unknown kind gets nothing that moves it but the
  stop.

## The slices

Each is a pull request; a slice that needs another's work stacks on it.

1. **The stop always reaches the board** (`build/stop-always-sent`; built). A
   stop asked in either dialect's word goes as the stop of what is on the port:
   `RESET` to a router for a printer's `M112`, and `M112` to a printer for a
   router's `RESET`. `docs/cnc.md` and `docs/firmware.md` say so.
2. **A port that changes hands forgets its board** (`build/port-changes-hands`;
   built). The port list remembers what it last found on each port; another
   board found there makes `devices.forget_port` let go of the last poll, a
   finished job, the link, the latch and the comms log. The link registry and
   the latch read the port list before they answer, so no reader gets around it.
   Held by tests that run a print on the simulated printer, put the router on
   its port, and ask each of the page's questions first.
3. **Who is on a port, and a bed reading belongs to the board that took it**
   (`build/readings-by-board`; built). `apothecary/firmware/occupants.py`
   answers the port's board, its key and its kind; its first reader is the bed
   reading. A reading records its board's key and kind; readings are listed for
   the occupant's key; a reading kept before this, with no key, is the
   occupant's only when it is a printer on the port the reading was taken on
   whose firmware is the one the reading names. A reading is listed for, and
   laid over, the board of the kind that took it: a printer's bed reading, a
   router's table map ([docs/cnc.md](../../../../docs/cnc.md#in-the-page)). A stored mesh is
   read on a printer alone, and no reading is taken while a key is shared. Held
   by tests that take a reading on the simulated printer and put the router on
   its port, and by a browser test that starts with a printer's reading kept
   under the router's port name.
4. **A kept file says which kind of machine it is for** (`build/files-by-kind`,
   on 5; built). A file records
   `printer` or `router`: Choose File records the Machine's kind, a slice
   records `printer`, a toolpath `router`. A stream refuses a file of the other
   kind, and one that records none, saying how to keep it for this machine. The
   check is per dialect: a router's file is refused for a code GRBL does not
   take, and a dwell over a minute is named with its unit.
5. **A pin and a flash kept by port name are careful of the board on the port**
   (`build/pins-by-board`, on 3; built). A pin by port never matches a board
   with a MAC or a serial number, which its own pin would have named; it keeps
   the kind of machine its board answered as, learnt the first time it answers,
   and never matches a board that answers as another. A flash kept by the port
   of an unprobed devkit records the devkit's key and counts for it alone, and a
   board that answers as a printer or a router is never said to run a sketch.
6. **The page keeps a machine's marks by board** (not built). Marks, where a
   machine stands and a drawn toolpath would be rebuilt when the board on a
   node's port changes; one function would say a board's kind, and a board not
   yet identified would be of no kind, never a printer. The server now forgets
   and refuses whatever the page believes; a page left open across a replug is
   what is left.
7. **A machine planned before it connects** (`build/machine-plans`, on 4;
   built). A part says the kind of machine it is (`BasePart.machine`), so a
   machine with no board connected opens its Machine as its plan: what it will
   make, its toolpath or slice written by its node and drawn over it, kept as
   that machine's plan and chosen whenever its Machine opens, with its board or
   without. A cut part's ring offers Toolpath to a router with no board.

`project/bench-checklist.md` is kept with each: a slice that changes what a person
sees at the bench changes its box.

## Not built

- Two serial-less bridges of one make at once (above): told apart by nothing
  the bridge says; a USB socket's location would tell them apart until one is
  moved.
- A generic serial number, as some CP2102 bridges carry (`0001`), is trusted as
  unique.
- Evidence, the jobs' history and kept print records from before a slice keep
  what they recorded; they are read by the new key where they have one.
- A job's history is matched by identity, which for a board with no serial number
  is its port: a serial-less board on the router's port name would be shown the
  router's jobs as its own. A job recording the occupant's key and kind would
  close it; it shows history, and sends nothing.
