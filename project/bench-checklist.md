# The bench checklist: the Ender 3, the ESP32 and the router, for real

The suites hold every path below against the simulated printer, the
scripted devkit and the simulated router; this is how the same paths are
confirmed on the real Ender 3, a real ESP32 devkit and the AnoleX router. A
person runs it, at the bench. No test flashes a board or moves a machine.

Tick each box as it passes. When one fails, note the time and the port, and
download the board's log (the Machine's `⤓`): it holds every line sent and
what the board answered.

Prepare first. *Prepared, nothing plugged in* is done before any board is
connected, and every box after it assumes it passed: the machines' plans are
made and checked there, where nothing can move, and what follows only confirms
them on the machines.

**Safety.** Stay at the printer while anything heats or moves. Keep a hand
near its own power switch: it is faster than the page's ⏹ E-STOP, which is
always there and never asks. Heat and motion only with the bed clear and
nothing printing from its own SD card.

## Setting up

- [ ] `uv sync`, then `uv run apothecary check`: OpenSCAD, the slicer and the
      firmware toolchains each say what is installed.
- [ ] What is missing, once, with the network up:
      `uv run apothecary openscad install --latest`,
      `uv run apothecary slicer install`,
      `uv run apothecary firmware install --esp32` (arduino-cli and the ESP32
      core, for the Arduino blink),
      `uv run apothecary firmware install --rust-esp32` (Rust for the ESP32).
- [ ] `uv run apothecary serve` -- your own server and state, not `--simulated` --
      and open `http://127.0.0.1:6283/viewer`: it lands on the garage.

## Prepared, nothing plugged in

Every board unplugged: nothing here opens a port, and nothing can move.

- [ ] Copy the state folder aside before the session (`~/.apothecary`, its
      `tools` folder left out): pins, readings, kept files and plans live
      there, and a session that goes wrong is undone from the copy.
- [ ] `uv run apothecary firmware devices` lists none of the machines' bridges.
      Pinned (in Site's tabs) lists every pin as `📌 site › node ← identity`:
      note what each names, and take back any that stands on a node it should
      not. A pin's node says *not connected* in its Device section.
- [ ] **Plan the router.** Select `cnc_router`, ⊞ Windows › Machine view: its
      Machine opens with no board connected, its head saying so, its Cut card
      alone. Under *makes* choose `router_coupon`, **Toolpath**: the file is
      kept and chosen, listed with what it was written from; the preview
      slider draws its passes over the router's table, standing on the table
      from the working area's front-left corner (its zero is set at the
      machine); ▶ Cut stays refused, its title saying the board's. **Keep as
      plan**: the card says the plan kept.
- [ ] **Plan the printer** the same way: select `printer_1`, its Machine with no
      board, a part under *makes*, **Slice**, the preview's layers over its bed,
      **Keep as plan**.
- [ ] Close each Machine and open it again: the plan's part and file are chosen.
- [ ] In the router's Cut card, the printer's sliced file is listed *kept for a
      printer* and ▶ Cut stays refused for it; in the printer's card, the
      router's toolpath is listed *kept for a router*.

## Plugged in and pinned

- [ ] Plug the boards in. `uv run apothecary firmware devices`: the printer's
      board (an FTDI bridge, with a serial number) and the ESP32's (a CP2102
      bridge), each on its own port, and the router's CH340 with no serial
      number. Note which port name each took today, and the router's USB
      socket; the port numbers can swap between plug-ins, and a pin follows its
      board's serial number, or the router's bridge's make.
- [ ] **Pin the printer.** Select `printer_1` in Site. Its Device section lists
      the free ports: choose the printer's, **Pin**. The pin goes to the
      printer's mainboard, and when nothing is printing the page asks the
      board once what it is (M115): the status line says *asked it once what
      it is: Marlin …*, and `printer_1` wears its ⚡ badge.
- [ ] Open `printer_1`'s Machine: its plan's part and file are chosen.
- [ ] **Pin the ESP32.** Select `esp32_blink`, choose the ESP32's port,
      **Query**, **Pin**: `esp32_blink` wears its ⚡ badge.

The ring opens with **Ctrl + right-click** (or `m` on the selection). The
addresses below are cells pressed in order on a numeric keypad. Inside a
Machine, Ctrl + right-click opens the board's own ring (the device ring); from
`printer_1`'s ring the same cells sit under Device, cell 7 (`⌗7…`).

## A port changes hands

A port's number is the socket's turn in a queue, not the board. These boxes put
one machine on the number another held; nothing in them moves a machine.

- [ ] With the printer polled and its control armed, unplug the printer and
      plug the router into the same socket, then reload the page (a page left
      open across a replug keeps its own picture of the port: the page's marks
      by board are [not built](plans/machine-identity-2026-11-07.md#not-built)). If the
      router takes the printer's port number, the Machine of that port shows
      none of the printer's temperatures, job or log, and its control is not
      armed; the router's polls drive nothing onto `printer_1`.
- [ ] Nothing of the printer's lies over the router's table, though the
      printer's readings were taken on that port number. Once the printer is back its bed wears
      the newest reading kept for its board.
- [ ] Pin the router (section I), then plug the printer into the router's
      socket: `cnc_router` does not take the printer, whose serial number its
      pin would have named; its node says *not connected*.
- [ ] With the router pinned, plug it into another socket and reload the
      page: whatever port number it takes, `cnc_router` holds it on that
      port, its pin still `usb:1a86:7523`.

## A. The link, nothing armed

- [ ] Open the printer's Machine: click its ⚡ badge, or `printer_1`'s ring ›
      Device › Open (⌗78). It opens as a tab beside Pictures, its state `idle`;
      the canvas ring's Panels › Windows › Machine view lays its sections out:
      temperatures near the room's in Status, the chart filling after a few
      polls in Temperature, the log in Log.
- [ ] Pull the filament out of the runout sensor: within one poll the endstop
      chip reads `filament OUT`; push it back → `present`.
- [ ] **⏻ Reboot**, pressed twice (the button says *again to reboot* after the first press), or the
      ring's Link › Reboot (⌗16): the boot banner lands in the log, the link
      is kept, the next poll answers.

## B. Armed: heat

- [ ] **⚙ Control**: the control pad pops out into a red window beside the world,
      headed *printer_1 armed: it can heat and move*, counting down from 5:00;
      its ⇥ Put back puts it in the Machine and ⧉ Pop out out again; the ring's
      Control › (⌗77) reads *Disarm*.
- [ ] Bed **45** → Set: `M140 S45` in the log, the bed card's target `/45°` on
      the next poll, the bar filling. **Off** → target 0.
- [ ] Hotend **150** → Set; watch it climb; **Off**. (Below printing
      temperature on purpose: nothing extrudes.)
- [ ] Fan to about 128 → Set: the part fan spins; **Off**.
- [ ] **900** in the hotend box → Set: refused before the port (`above 300` in
      the log, no `M104 S900` line).
- [ ] Five minutes with no command: the latch lapses, the pad goes.

## C. Armed: motion

- [ ] **Home XY**, then **Home Z**: X and Y home, the probe touches at the
      bed's centre, the position card reads X0 Y0 and a Z.
- [ ] Each axis alone: step **10**, then **X+**, **Y+** and **Z+** once each, so
      each is 10 mm from zero. **Home X**: only X returns to 0 and the log says
      `G28 X`; **Home Y** and **Home Z** the same, Z last, with the nozzle clear
      of the bed. A bare `G28` is never in the log for these; a Z home that Marlin
      refuses until X and Y are known is noted, with its words.
- [ ] Step **10**, **Y+**: the bed moves 10 mm; the nozzle marker over the
      printer in the world moves when the button is pressed, and the position
      card confirms within one poll. The ring's Control › Jog › Y+ (⌗728) does
      the same. **Y−** twice, then Motors › Off (⌗738).
- [ ] Before the corners, `uv run apothecary firmware printer <port> --query
      M503` from a terminal, its answer kept whole in a dated record: `M92`,
      `M301`, `M304`, `M851`, the `G29 W` points.
- [ ] The bed level card's corners, **FL**, **FR**, **BL**, **BR**: the nozzle
      parks at each corner at paper height; slide a sheet of paper under it.
      The newest probe's corners on the card say which stand high or low
      against the mean: turn each screw to the paper, then **Home Z**.
- [ ] **Extrude**, the first control that moves the extruder (from the Stream Deck's
      fourth knob, section J, or `POST /firmware/printers/command`): with the hotend at a
      temperature Marlin extrudes at (its own refusal below that is the only guard
      against a cold extrude) and filament loaded, `M83` then `G1 E5 F200`: the
      extruder pushes 5 mm; `G1 E-5 F200` pulls it back. `G1 E11 F200` and `G1 E5 F400`
      are refused before the port (`extrusion beyond 10 mm`, `extrusion feedrate above
      300`), and `G1 E5` with no feed is refused. Nothing is sent disarmed. After a print
      that left `M82`, `M83` is what makes the move relative: confirm the position
      card's E moves by 5, not to 5.

## D. Armed: levelling

- [ ] **▤ Probe bed**, or Control › Level › Probe (⌗748) → the dialog → the
      state card reads `leveling: homing`, then `probing`; the temperatures
      keep updating; a jog pressed meanwhile is refused (*a bed reading holds
      the port*). When it reads `saved`, the heatmap redraws and the history
      has a *probe* row: compare its range with the last one.
- [ ] **Mesh on**, then **Read mesh** (⌗746): the record says *leveling on*.
      Apothecary never writes the printer's EEPROM; to keep a mesh across a
      power cycle, store it from the printer's own screen.
- [ ] Bed **60** → Set, the target reached, then **▤ Probe bed**: the range
      under the printer's profile's bound (`measured.mesh_range_bound` in
      `parts/ender3/slicer.json`); note the centre against the corners.
- [ ] Store the mesh from the printer's screen (Configuration › Store
      Settings), power-cycle the printer, then **Read mesh**: the record is the
      probed mesh.
- [ ] After a probe, **Home all**, then **Read mesh**: leveling on or off. Off
      means a print with a mesh needs the stored-mesh start piece.
- [ ] Before naming `stored-mesh`: **▤ Probe bed** once more, warm, after
      the store: the piece reads the newest reading, which must be a probe
      under the bound.
- [ ] The world: the relief over `printer_1`'s bed is the newest reading, and
      nothing of the printer's lies over the router's table.

## E. Print from here

- [ ] *Print from here* → **Choose File** → `examples/gcode/dry-run-square.gcode`
      (nothing in it heats or extrudes): it lists as `dry-run-square.gcode ·
      23 lines`.
- [ ] A file that must be refused -- any `.gcode` with an `M500` line -- lists
      as *refused: line N: M500 saves settings to EEPROM*, and **▶ Print**
      stays refused for it.
- [ ] **▶ Print**, or Print › Send file (⌗794) → the dialog → the head homes
      and traces a 60 mm square 10 mm above the bed; the card shows the line
      in flight; the status line says the print started.
- [ ] **⏸ Pause** mid-square (⌗796): the head finishes what was queued and
      stops; **Resume** (⌗798).
- [ ] **■ Cancel**, pressed twice: `M104 S0`, `M140 S0`, `M107`, `M84` in the
      log; the history and Site's Jobs read *cancelled*; the status line says
      the print ended.
- [ ] Print it again to the end: *done · 23/23*, `dry run done` on the
      printer's screen, the state back to `idle`.

## F. Slice, then print a real piece

- [ ] Choose a part under *makes* in *Print from here* (or a made piece's
      ring › Slice) → **Slice**: OrcaSlicer's log in the card, then the kept
      G-code chosen, each setting with where it came from, and the slicer's
      estimate of time and filament.
- [ ] Before printing it, read the G-code's start in the card's file list
      (or the kept file): `G28` before the first extrusion, nothing added to Z.
- [ ] With `stored-mesh` named after `home` in the profile's `start.modules`,
      Slice again: `M420 S1` on the line after the last `G28`; with the newest
      reading a read, or a probe over the bound, the slice is refused saying
      which.
- [ ] With filament loaded: **▶ Print** it, and watch the first layer. Note
      any stutter on long straight moves.
- [ ] A one-layer square: the Z offset set on the printer's screen to it, and
      the new `M851` kept.
- [ ] Hotend **200** held two minutes on the temperature chart: within ±2 °C,
      or PID tuned from the printer's menu.
- [ ] 100 mm of filament extruded from the printer's screen and measured; the
      e-steps set and stored there.
- [ ] Optional, with a camera over the bench: the loop of walkthrough page 03
      on the real hardware -- Camera › Add here, Device, Take picture, Find
      shapes, Make, Part › Edit, Slice, Print.

## G. Stop, and let go

- [ ] With the printer idle, **⏹ E-STOP** (⌗71): it never asks; `Error:Printer
      halted. kill() called!` in the log, the next poll `offline`. **⏻ Reboot**
      brings it back.
- [ ] Armed, **Home all**, and **⏹ E-STOP** while it homes: `M112` is in the log
      before the homing's answer, and the axes stop at once if the firmware
      parses M112 early (`EMERGENCY_PARSER`), else when the homing ends -- note
      which. **⏻ Reboot** brings it back.
- [ ] **Release**: the link drops, the latch with it; `uv run apothecary
      firmware printer <the printer's port>` from a terminal answers without a
      boot banner; **⇄ Reconnect** in the Machine holds it again, also
      without one.

## H. The ESP32: the Rust blink, and the Arduino one beside it

- [ ] The **Bench** tab (or Panels › Bench › Bench, ⌗438): its toolchain card
      shows *Rust for the ESP32*, installed, with cargo's and espflash's
      versions; its install cell is Panels › Bench › Install › Rust ESP32
      (⌗4366). Choose sketch **esp32_blink@rust-esp32 · esp32** and the
      ESP32's port -- check it is not the printer's.
- [ ] **Compile** (⌗432): the log shows `cargo build --release --offline`
      and, last, *no build path in the image*. With the network unplugged,
      Compile again: it still builds.
- [ ] **Compile & upload** (Bench › Upload, ⌗434) → the dialog → espflash ends
      *Flashing has completed!*; the LED on GPIO 2 blinks once a second.
- [ ] `esp32_blink`'s ring › Device › Open (⌗18): the Sketch card reads
      *should run esp32_blink@rust-esp32 · esp32*. Device › Query (⌗14): the
      log says *heard esp32_blink say hello*, and the card *✓ matches*.
- [ ] **Listen** (⌗114): `apothecary esp32_blink: hello`, the chip line, then
      `blink 1`, `blink 2`, … once a second, the hello and chip line again
      every ten blinks. Note the chip line exactly.
- [ ] Flash **esp32_blink@arduino · esp32:esp32:esp32** the same way and
      compare: every line should read the same as the Rust build's. A
      difference is a defect of the Rust one.
- [ ] **Release**, then Device › Flash (⌗12): the Flashing card starts from
      the sketch the board should run.
- [ ] With arduino-cli out of the way (`ARDUINO_CLI=none uv run apothecary
      serve`): the ESP32 is still found -- its Machine says *found by
      rust-esp32* -- and **Listen** still hears the hello. Note whether opening
      the port reset the board; it should not. **Probe** asks espflash for
      the chip and its MAC (this one resets it).

## I. The router: the AnoleX 4060-Evo Ultra 2

The suites hold every path below against the simulated router; this is how
the same paths are confirmed on the real machine. Its controller has answered
`apothecary firmware printer <port>` at 115200 baud: `Grbl 1.3a · Grbl_ESP32`,
`Idle`, behind a CH340 bridge (`0x1A86:0x7523`) with no USB serial number, so a
pin is kept under the bridge's make, `usb:1a86:7523`, and keeps the kind of machine
its board answered as. The
rest of this section has not been walked, so the first boxes record what it says
([docs/cnc.md](../../../docs/cnc.md) says what is assumed). Stay at the machine while
anything turns or moves, with a hand on its own red stop: the page's ⏹ E-STOP
is the controller's soft reset, and the button is faster. Spindle and motion
only with the table clear and no tool in the collet until the last box.

- [ ] `uv run apothecary firmware devices` with the router's USB lead in: its
      port, the bridge's vid:pid and whether it has a serial number (a pin is
      kept under the serial number when it has one, under the bridge's make
      when it has not). Note them; the bridge so far is a CH340 without one.
- [ ] `uv run apothecary firmware printer <port> --query '$I' --query '$$'`:
      the firmware line (`Grbl 1.3a` is what the maker's listing says), the
      machine name, the build, the settings. Note whether opening the port
      reset the controller (a banner in the log), which way it homes (`$23`),
      the travel (`$130` to `$132`) and the maximum feeds (`$110` to `$112`);
      `apothecary/firmware/grbl.py`'s bounds are the maker's figures, and
      they are held to what `$$` says here.
- [ ] With `$$` read, the settings it needs. They are written from a GRBL
      terminal of your own choosing, never from here: Apothecary sends no `$`
      setting, and `--query '$$'` reads them back after each.
- [ ] `$13=0` and `$32=0`; `$10=3`, so a status report carries `Bf:` (or
      `$10=1`, and the host streams by `ok`).
- [ ] `$130` to `$132` read 400, 600 and 80; `$110` to `$112` against the feed
      cap; `$30=24000` and `$31=0`; `$120` to `$122` and `$24` to `$27` kept as
      they are, and noted.
- [ ] A 100 mm jog in X measured with a rule or a dial indicator: `$100` to
      `$102` against the 4 mm lead.
- [ ] **Home**: note the corner and the machine position after the pull-off;
      then `$20=1`.
- [ ] `$21=1`, then the spindle at full speed for a minute with no tool: no
      `ALARM:1`, else back to `$21=0`.
- [ ] The probe plate touched by hand shows `Pn:P`; **Probe Z** at the four
      corners and the centre, each `[PRB:…]` kept: more than 0.2 mm between
      them is the Z plate to tram.
- [ ] The spoilboard surfaced from a CAM post's file, the dial's position and
      the bit's feed and depth kept with the cut.
- [ ] **Pin the router.** Select `cnc_router` in Site, choose the port in its
      Device section, **Pin**: the pin goes to the controller in the control
      box, the status line says it was asked `$I`, and `cnc_router` wears 🪚.
      Pinned lists it as `garage › cnc_router.frame_system.controller ←
      usb:1a86:7523`, its bridge's make; `GET /firmware/pins` gives the pin
      `"kind": "router"`.
- [ ] Its Machine opens with its plan's part and file chosen, now with its
      board: ▶ Cut is offered.
- [ ] Open its Machine: `idle`, the controller's word beside it (`Idle`, or
      `Alarm` with homing required on power-up), the tool's work and machine
      positions, the spindle off, no pins on. Press each limit switch by
      hand: its pin shows within one poll and goes when let go.
- [ ] **A home is proved first.** Before any switch is pressed, **Home Z**: refused, and
      the status line says which way Z will seek, how fast and how far, that its switch
      has not been seen and that it has not been jogged that way. Jog Z 1 mm that way and
      watch: the tool rises. Press Z's switch by hand for two seconds and let go: the
      pins show `Z`, and with `$21=1` the controller is in alarm (`ALARM:1`). **Home Z**
      now goes. The same for X and for Y, each the way it homes.
- [ ] **⚙ Control**: the pad, headed *cnc_router armed: it can turn and move*.
      **Home** (`$H`): the gantry seeks its switches, the state card reads
      `running (Home)` and then `idle`, the machine position reads the
      pull-off near zero. Note which corner is home.
- [ ] Each axis alone, with the tool well clear of the work and a hand on the red
      stop: step **10**, **X−**, **Y−**, **Z−** once each, then **Home Z** first, so
      the tool clears the work, then **Home X**, then **Home Y**. Each sends `$HZ`,
      `$HX`, `$HY` with no bare `$H`; the state card reads `running (Home)` then
      `idle`, and only that axis goes to its switch and pulls off, the other two
      readings unchanged. Only the bench answers whether this Grbl_ESP32 build takes
      a single-axis home: an `error:` or an `ALARM:` in the log is the answer, noted
      with its number, and `$H` stays the way to home.
- [ ] Step **10**, **X−**, **Y−**, **Z−** once each: the tool moves 10 mm, the
      work position follows within one poll, and the marker in the world
      moves the same way over the table; a jog past the travel is refused by
      the controller (`error:15`) and said so in the log.
- [ ] **Spindle On** at 8000 with no tool: the router turns and the card reads
      the speed; **Off**. 30000 in the box → Set: refused before the port.
- [ ] **XYZ zero here**, then jog away and **Go to zero**: the tool returns.
      **Z zero here** with the plate under the collet, then **Probe Z** 25 mm:
      the touch is in the log (`[PRB:…:1]`) and `$#` says where.
- [ ] **The plate's thickness.** Measure the touch plate with calipers, put the figure in
      **plate**: it is there after a reload. Clip the lead to the bit and touch
      the clip to the plate by hand: **Pins on** shows *probe*. Plate on the stock under
      the bit, **Probe Z to plate**: the bit comes down, touches, lifts 5 mm; the work Z
      reads the thickness plus 5, and `$#` has it in G54 with G92 at zero. E-STOP, Unlock:
      the work Z is still there. With the clip off, **Probe Z to plate** from 60 mm up
      with a depth of 10: it touches nothing, says so, sets nothing, and the controller
      is in alarm.
- [ ] **▦ Probe table** in the Table map card, the probe's lead closing at
      every point of the grid (clipped to the table, or the plate under the
      whole grid): the question in the router's words, the spindle off and a
      homing, then a touch at each of nine points, the card counting them. The
      map is kept, listed in the card's history and laid over the table in the
      world where its points were probed. Note how long a point takes and that
      each probe reaches the table; more than 0.2 mm across the map is the Z
      plate to tram.
- [ ] **⏸ Hold** mid-jog of 50 mm: the gantry stops where it is, `hold
      (Hold:0)`; **▶ Resume**: it finishes the move.
- [ ] **⏹ E-STOP** while jogging: the soft reset, the banner in the log, the
      state `alarm` with `3` (reset while in motion); **Unlock** (`$X`) or
      **Home** brings it back. The log says `RESET` went: a stop goes as the
      stop of the board on the port, whichever word for it was sent.
- [ ] *Cut from here* → `examples/gcode/dry-run-square.nc` (a square 10 mm
      above the table, the spindle off): kept for a router, listed with its line
      count; a file with a `$` line or `M6` lists as refused and ▶ Cut stays
      refused. The printer's `examples/gcode/dry-run-square.gcode`, kept with
      this Machine's Choose File, lists as refused, and the log names each
      refusal: `M117`, `M84` and every `G4 P500` (500 s to GRBL).
- [ ] The plan's toolpath, with no tool and the spindle off: jog the tool over
      the stock's front-left corner with the cut's depth under it and the safe
      height over it, **XYZ zero here**, then the preview draws the passes from
      the zero where the tool stands. Run it 10 mm above the stock (zero 10 mm
      high) before any real cut: each operation is named on the progress line.
- [ ] **▶ Cut** → the dialog → the tool traces the square; **Pause** holds it
      mid-side, **Resume** goes on; **Cancel**, pressed twice: a hold, the
      reset, the spindle off, the job *cancelled* in Site's Jobs; cut again to
      the end: *done*.
- [ ] With a tool and stock, the first real cut from a CAM post's file, the
      spindle at its dial's speed: watch the first pass.

## J. The Stream Deck +

Plug the deck in and close Elgato's own software first: it holds the device, and two
programs cannot. Nothing here moves a machine; the knobs' jogs are further down.

- [ ] `uv sync --extra deck`, then `sudo apt install libhidapi-libusb0` (Debian and
      Ubuntu). `uv run apothecary check` lists *Stream Deck +* with both tools found;
      the Bench's card says the same, and its Install is greyed.
- [ ] `uv run apothecary firmware decks` lists the deck as `0x0fd9:0x0084`, 8 keys,
      4 knobs, and opens nothing: the deck's screen is as it was. Without the udev
      rule for the device, a command that acts on it says it cannot be opened.
- [ ] `PUT /firmware/decks/{id}/keys/0` with `{"text": "X+", "colour": "blue"}` (the
      id is the one the list gave): key 0, top left, shows *X+* on blue. The strip
      takes `PUT .../strip`. `GET .../keys/0/image` is the picture sent.
- [ ] Press each key, turn each knob a click each way, press each knob, tap the strip,
      hold it and drag across it. `GET .../events` lists each: a key's press and
      release, a knob's steps (clockwise positive), the press, and the touch's
      kind and strip coordinates (the strip is 800 wide, 100 tall).
- [ ] `POST .../release`, then draw a key again: the deck is opened afresh.

Then the knobs. The printer and the router are pinned as in sections C and I, the bed
clear and the tool clear of stock. Start the layout with
`POST /firmware/decks/{id}/control` `{"on": true}` (or `APOTHECARY_DECK_CONTROL=1`).
Keep a hand on each machine's own power switch: it is faster than the deck's stop keys.

- [ ] The top row shows **PRINTER**, **ROUTER**, **STEP**, **DISARM** (grey, *nothing
      armed*); the bottom row **STOP**
      (printer_1), **STOP** (cnc_router), a dark key and a bright red **STOP ALL** last,
      under the right hand; the strip says *printer_1 · disarmed* and the printer's X, Y,
      Z. **ROUTER** turns the second key green and the strip says *cnc_router*.
- [ ] Disarmed, turn every knob: nothing moves, the strip says *disarmed*, and the control
      latch is still disarmed.
- [ ] Arming from the deck: hold **ROUTER** for a second and let go: the strip says to long
      press again within 5 s, and control is still disarmed (the Machine's pad). Wait
      6 s, hold it again: still disarmed. Hold it twice within 5 s: the strip says
      *armed* with the minutes left, and the Machine's pad pops out red as ⚙ Control's
      does. A short press, **STEP** or a knob between the two holds breaks the pair.
      The second hold counts from when it is begun: held three seconds, it still arms.
- [ ] Armed, **DISARM** is blue and says *every machine*. Press it: the strip says
      *disarmed*, the key goes grey, the Machine's pad goes back, and a knob turned moves
      nothing. It stops nothing: press it while a jog of 50 mm is under way and the jog
      finishes.
- [ ] With the router armed (from the deck or the Machine's ⚙ Control). **STEP** to 1 mm, then knob 1
      one click clockwise: X moves 1 mm toward +X and the X key shows the new position
      within a poll (on the strip); counter-clockwise, back. Knobs 2 and 3 the same on Y and Z. At
      10 mm, a fast turn of 70 clicks is refused (`move beyond 600`) and nothing moves.
- [ ] With the spindle off, knob 4 does nothing and the strip says *spindle off*. Start
      it at 8000 from the Machine, with no tool: knob 4 one click clockwise reads 9000,
      the strip's S says so; held clockwise it stops at 24000 and never above.
- [ ] Router's **STOP** while a jog of 50 mm is under way, control disarmed: the soft reset,
      the banner in the log, the spindle off, and the printer untouched. Then the machine's
      own switch: note which stopped the gantry sooner, in a dated record.
- [ ] **STOP ALL** with both machines doing something (the spindle turning, the hotend
      heating): the printer halts (`M112`) and the router resets, each in its own log, and
      the strip names both. Unplug one machine's USB and press it again: the other still
      stops and the strip names the one it could not reach.
- [ ] Choose **PRINTER**, arm its control, bed clear. Knobs 1 to 3 jog X, Y and Z in the
      chosen step, each one `G91`, `G1 .. F3000`, `G90` in the board's log, and the
      printer is left in absolute positioning. Disarmed again, the same turn sends
      nothing.
- [ ] Knob 4 on the printer, the hotend at a temperature Marlin extrudes at, filament
      loaded: one click clockwise pushes 1 mm (`M83`, `G1 E1 F200`), counter-clockwise
      pulls it back. Below Marlin's minimum, the board refuses and the log says so.
      The printer's **STOP** halts it (`M112`) and the page's E-STOP does too.

## K. The footpedal

The pedal is an Arduino Uno (or a Nano, with `--fqbn
arduino:avr:nano:cpu=atmega328old` for a CH340 clone) wired as
[parts/footpedal/footpedal.ino](../../../parts/footpedal/footpedal.ino) says: six
buttons, on pins 2, 3, 4, 5, 8 and 7, and the LED strip's data on pin 6. Its
serial line carries MIDI for Hairless MIDI, so it says no hello and Query does
not find it.

- [ ] `uv run apothecary firmware install --avr`, then `uv run apothecary
      firmware libraries --install FastLED@3.10.5 --install "Control
      Surface@2.1.2"`: the versions its `firmware.json` pins.
- [ ] The **Bench** tab: choose sketch **footpedal@arduino · arduino:avr:uno**
      and the pedal's port -- check it is not the printer's. **Compile**
      (⌗432) ends with the sketch's size; **Compile & upload** (⌗434) ends
      without an error.
- [ ] Release the port, and open it in Hairless MIDI at 115200 baud, its MIDI
      out to a monitor. Press and release each button: a Note On and a Note
      Off on channel 1, notes 1 to 6 in the pins' order above (C#-2 to F#-2
      where C-2 is note 0).
- [ ] Send notes 1 to 8 to the pedal from Hairless's MIDI in: each lights one
      LED of the strip, and its Note Off puts it out.

## Results

| Section | Date | Passed | Notes |
|---|---|---|---|
| Setting up | | | |
| Prepared, nothing plugged in | | | |
| Plugged in and pinned | | | |
| A port changes hands | | | |
| A. The link | | | |
| B. Heat | | | |
| C. Motion | | | |
| D. Levelling | | | |
| E. Print from here | | | |
| F. Slice and print | | | |
| G. Stop and let go | | | |
| H. The ESP32 | | | |
| I. The router | | | |
| J. The Stream Deck + | | | |
| K. The footpedal | | | |
