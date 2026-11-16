# The Stream Deck + at the bench: a plan

An Elgato Stream Deck + -- eight LCD keys in two rows of four, a touch strip
under them and four knobs under that -- comes into apothecary three ways: as a
part in the library, standing on the garage's workbench where a person stands
at the machines; as a device apothecary programs, its keys and strip drawn from
here and its presses, turns and touches heard; and as a controller for the two
machines, its knobs jogging the axes of the machine chosen on it through
everything that already bounds a person's jog. Each is a slice below, and each
slice is one pull request.

## What each part makes true

**A part in the library.** `parts/stream_deck_plus/` holds the deck drawn from
the maker's published figures, with the numbers the maker does not publish
assumed and named as such in its README, as `parts/boards/anolex_grbl_esp32`
names its own. Its wrapper, `apothecary/projects/parts/stream_deck_plus.py`,
declares its parameters and its envelope, and tags it for what it is: a
controller with keys, knobs and a touch strip, over USB. The garage's workbench
carries it as the node `stream_deck`, at the bench's right end behind the
boards, facing the front and within reach of a person standing at the bench;
it stands outside the clear stretch where a picture pinned at the bench is
laid, so a pinned picture stands where it does without it. The site's layout
checks hold it on the bench, and every walkthrough picture that shows the
bench's right end shows it.

**Programmed through apothecary.** `apothecary/firmware/deck.py` is the device
seam: a deck is found on USB by Elgato's vendor id `0x0fd9` and the Stream Deck
+'s product id `0x0084`, each key's image and the strip's are rendered here
(Pillow, a label on a colour, 120 by 120 pixels a key and 800 by 100 the strip,
as the device takes them) and sent, and what the deck reports -- a key pressed
or released, a knob turned by so many steps or pressed, the strip tapped or
dragged -- is read as events. The transport is `python-elgato-streamdeck`
(`streamdeck` on PyPI, MIT, no Python dependency of its own), taken as the
optional dependency `deck`; it loads the system's hidapi through ctypes and
connects to nothing off this machine. `apothecary/firmware/modules/stream_deck.py`
is the module beside Arduino's and Rust's: it says what it can do, finds its
two tools -- the Python package and the HID library -- and names what installs
each where one is missing; the Bench, `apothecary check` and
`GET /firmware/toolchains` draw it with no change of their own. A simulated deck
(`APOTHECARY_SIMULATED_DECK`, under the simulated serial engine) stands in for
the device as `SimulatedPrinter` stands in for the Ender: it keeps the images it
is sent and takes its events from a route, so the demo shows one and every test
runs against it. Routes under `/firmware/decks` list the decks, show one as it
is drawn (each key's image is the bytes the deck was sent), set a key or the
strip, and read its events.

**A controller for the machines.** `apothecary/firmware/deck_control.py` runs
one layout on a deck it is started for (`APOTHECARY_DECK_CONTROL`, or a route): the top row's keys choose the machine --
`printer_1`, `cnc_router` -- and hold the jog step, which cycles through 0.1,
1 and 10 mm; the bottom row holds the stops, two classes of them: keys four and
five stop printer_1 and cnc_router, dark red, each by its own dialect's stop,
and key seven, bright red and last, nearest a hand resting on the knobs, stops
every machine, each by its own; none needs control armed. The strip says which
machine, whether its control is armed, the chosen machine's last poll, the step
and its state. Knobs one to three are
X, Y and Z: a turn is a jog of that many steps on its axis. The fourth knob is
the chosen machine's fourth quantity: on the router the spindle's speed
(`M3 S..`, in steps of 1000 rpm, bounded at `gcode.SPINDLE_MAX_RPM` as the
pad's On is, and sent only while the spindle is on); on the printer the
extruder, 1 mm a step, through the one bounded line slice 4 adds to Marlin's
allowlist, since the page bounds no extrusion to reuse.
Every line is sent as `devices.printer_control` sends a person's line from the
pad: nothing goes unless the port's `ControlLatch` is armed, the line is
normalised in the port's dialect (`$J=G91 G21 X.. F..` for GRBL, `G91` then
`G1 X.. F..` then `G90` for Marlin), each stays inside the dialect's bounds,
and a stop key sends `devices.emergency_stop_for(port)`, the one line that
always goes.
A machine's control is armed in its Machine window or by two sequential long presses
of its key (below), through the same `ControlLatch`, and the strip says so while it
is not. The machine's own red button stays the
faster stop, and the docs say so.

## What was found

- **The device.** `python-elgato-streamdeck`'s `ProductIDs.py` carries
  `USB_VID_ELGATO = 0x0FD9` and `USB_PID_STREAMDECK_PLUS = 0x0084`, and its
  `StreamDeckPlus.py` the deck's shape: `KEY_COUNT = 8` in `KEY_COLS = 4` by
  `KEY_ROWS = 2`, keys `120 x 120` pixels in JPEG, `DIAL_COUNT = 4`, the
  touch strip `800 x 100` pixels in JPEG
  ([the library](https://github.com/abcminiuser/python-elgato-streamdeck)).
  Its input report is one of three: key states (type 0), a touch (type 2:
  a short tap, a long press or a drag with its two points), or the dials
  (type 3: a turn as a signed step count per dial, or a press).
- **The maker's figures.** Elgato's technical specifications page gives the
  Stream Deck + as `140 x 138 x 110 mm`, `465 g`, eight LCD keys, four 360°
  encoders with a push function, and an LCD touch panel of `108 x 14 mm`
  ([the page](https://help.elgato.com/hc/en-us/articles/10567379685901-Elgato-Stream-Deck-Technical-Specifications)).
  The stand is part of the device. The key's physical size, its pitch and the
  face's angle are not published: the part assumes them, and its README says
  which numbers are assumed.
- **The library's licence and reach.** `streamdeck` 0.10.0 on PyPI declares
  `MIT`, on `license-check.yml`'s allowlist, and no `requires_dist`. Its
  transport, `LibUSBHIDAPI.py`, loads `libhidapi-libusb.so` (Linux),
  `libhidapi.dylib` (macOS) or `hidapi.dll` (Windows) through `ctypes`,
  enumerates without opening a device, and makes no network connection. The
  system library is the one thing to install outside `uv`: on Debian and
  Ubuntu, `libhidapi-libusb0`. This machine has none, so a real deck cannot be
  opened here, and no test opens one.
- **The seam the controller rides.** A jog from the page is
  `POST /firmware/printers/command`, which is `devices.printer_control`:
  `is_emergency_stop` lets a stop through in either dialect's word, else
  `normalise_control` in the port's dialect (`gcode.CONTROL_CODES` and
  `grbl.CONTROL_CODES`, each bounded: `JOG_MAX_MM`, `FEED_MAX`), then the
  latch (`ControlNotArmed` when it is not armed), then the job holding the
  port (`PortHeld`), then the dialect's `control`. A line the deck sends goes
  through the same function, so it can bypass none of it.
- **Where a module plugs in.** `firmware/modules/__init__.py`'s `_registry`
  lists the modules; the Bench's toolchain widget (`widgets/toolchain.js`)
  draws every module's label, tools, problems and Install from
  `GET /firmware/status`'s `toolchains`, `apothecary check` lists each with
  what it can do, and Panels › Bench › Install has a cell per module from
  the same registry. A module that builds nothing refuses `build` and `flash`
  and recognises no sketch; its `can` says what it does instead.
- **The world.** A structure on the bench is an `Assembly` in
  `example_hierarchy.py` with a `part_ref` and a footprint, named in
  `BENCH_MOUNTED_STRUCTURES`; `tests/test_garage_workbench.py` holds each on
  the bench's top and inside its footprint, overlapping nothing. A picture
  pinned at the bench is laid in the widest stretch of its top that nothing
  stands on (`apothecary/vision/free_space.py`), between the printer and the
  boards; a deck anywhere in that stretch moves every pinned picture, and the
  tests and pages that place one with it. Behind the boards at the bench's
  right end, it moves none.
- **The extruder.** The Machine's pad has no extrude control, and
  `gcode.CONTROL_CODES` takes no `E` move, so the page bounds no extrusion
  for the deck to reuse. The spindle's speed is bounded: `grbl.CONTROL_CODES`
  takes `M3 S..` up to `SPINDLE_MAX_RPM`.
- **Pages and pictures.** The walkthrough pages written by the browser suite
  show the bench (01 to 06 and 18); a structure added to it changes their
  pictures, which are committed with the change that made them, judged with
  `tests/e2e/picture_drift.py`. Pages 24 and 25 are taken by a stack in
  flight, so the deck's pages are 26 and 27.

## The slices

Each is a pull request; each stacks on the one before it, since each reads
what the one beneath it adds.

1. **The part, on the bench** (`build/stream-deck-part`). `parts/stream_deck_plus/`
   (the SCAD, a README naming the maker's figures and the assumed ones), its
   wrapper with `Params` and the envelope `140 x 138 x 110`, the `stream_deck`
   node on the workbench's right end, the layout tests, and the pictures of
   the pages that show the bench. Held by the wrapper's tests, the garage's
   layout tests, the pinned picture's place and `apothecary parts verify`.
2. **The deck seam, its module and the simulated deck**
   (`build/stream-deck-module`, on 1). `firmware/deck.py`, the module, the
   `deck` extra in `pyproject.toml` and `uv.lock`, the routes under
   `/firmware/decks`, `apothecary firmware decks`, the demo's simulated deck,
   `docs/stream-deck.md`, the configuration page's variable, section J of the
   bench checklist. Held by `tests/test_firmware_deck.py` against the
   simulated deck, a stand-in for the library's device and the library's own
   dummy transport: found, drawn, heard, a listing opening nothing.
3. **The deck in the page** (`build/stream-deck-window`, on 2). The Deck
   window drawing a deck as it is, its keys as the images it was sent, the
   strip, the knobs and the events heard; a simulated deck is pressed, turned
   and tapped from it; the `stream_deck` piece's Open Deck and a cell of
   Panels lead to it. Walkthrough page 26, written by
   `tests/e2e/test_deck.py`, with its pictures.
4. **A printer takes a bounded extrude** (`build/marlin-extrude`, on 3). One
   relative `E` move on Marlin's control allowlist, at most 10 mm at most
   300 mm/min with its feed named, and `M83` beside it; the bound named in
   `docs/firmware.md`, a bench row for the real extrude. In a commit of its
   own because it is the first control that moves the extruder; its tests are
   red on the code beneath.
5. **The knobs jog the machines** (`build/stream-deck-jogs`, on 4).
   `firmware/deck_control.py`: the layout, the machine chosen on the deck, a
   knob's steps as one bounded jog through `devices.printer_control`, refused
   and said on the strip while control is not armed, one stop key, the fourth
   knob, and arming by two sequential long presses of a machine's key; started
   when `APOTHECARY_DECK_CONTROL` asks or a route does. The bench checklist's
   rows for the knobs, arming and the extrude. Held by
   `tests/test_firmware_deck_control.py` against the simulated deck and the
   demo's simulated printer and router: a turn disarmed sends nothing, armed
   sends the dialect's jog and nothing past its bound, the printer returns to
   absolute positioning, one long press alone arms nothing.
6. **Two classes of stop** (`build/two-stop-classes`, on 5). A stop key for
   each machine and one for every machine, the readouts moved to the strip, the
   armed machine's readouts followed by a poll. Walkthrough page 27, written by
   `tests/e2e/test_deck_jog.py`. Held by the same file: a machine's key reaches
   that machine alone, the everything key reaches each machine's own stop and
   goes on past one that cannot be reached, the stop goes whatever the latch
   says.

## Its questions, decided

Each decision below is built.

Decided: the fourth knob is the chosen machine's fourth quantity, the
router's spindle speed (steps of 1000 rpm, at most `SPINDLE_MAX_RPM`, only
while it turns) and the printer's extruder (1 mm a step); the jog step is a
key, the top row's third, cycling 0.1, 1 and 10 mm. The printer's extruder
takes the bounded line of slice 4.

Two classes of stop: a key per machine, each sending that machine's
own stop, and one that stops every machine at once with each one's own. The everything
key is the bottom row's last, key seven, nearest a hand resting on the knobs, bright red
where the per-machine stops are dark; the per-machine stops are keys four and five. None
needs control armed, as the page's E-STOP does not; the everything key goes on to the
next machine when one cannot be reached. The readouts X, Y, Z and the fourth quantity
are on the strip, since the bottom row is the stops'.

Arming from the deck is two sequential long presses of the machine's key. A
press held `LONG_PRESS_S` (0.8 s) chooses the machine and says on
the strip that a second will arm its control; a second long press of the same key
within `ARM_WINDOW_S` (5 s) of the first being let go arms it through the page's
`ControlLatch`, for the latch's own five minutes. One long press alone, a second
after the window, a short press, another key or a knob between them, or a long
press of the other machine's key arms nothing; the tests hold each.

The deck stands at the bench's right end behind the boards, chosen over the
router's stand. No question is open.

## Not built

- A real deck at the bench: `project/bench-checklist.md`'s section J is what a person
  confirms there, the knobs and the stop keys against each machine's own switch
  among it, and no test opens a HID device.
- Any deck but the Stream Deck +: a deck with no knobs is listed and drawn,
  and drives nothing.
- A key layout a person edits: the layout is the controller's, in code.
- A deck pinned to its node as a board is pinned to its port: the deck is
  found by its serial number, and the `stream_deck` node leads to the Deck
  window without a pin.
