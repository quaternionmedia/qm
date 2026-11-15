# The garage's two machines, read from what is recorded, 2026-11-07

The Ender 3 (`printer_1`) and the AnoleX 4060-Evo Ultra 2 (`cnc_router`),
each diagnosed from what this repository and the state folder already hold,
with neither machine plugged in: no port was opened, nothing was homed,
heated, jogged or written, and `~/.apothecary` was read and never written.
Where a finding needs the machine, it is a box below for a person at the
bench, and each recommendation says what it rests on -- a recorded fact, or
an assumption -- and how the bench confirms it. It starts from a bed relief
the viewer laid over the router, whose bed had never been measured.

It was read on main at 8601a5e, and where a line below says what the code
does, it is 8601a5e's. Three changes land beside it: a bed reading kept and
listed by the board that took it ([docs/firmware.md](../../../../docs/firmware.md#bed-leveling)),
the router's own reading, a table map ([docs/cnc.md](../../../../docs/cnc.md#in-the-page)),
and the `stored-mesh` and `probe-each-print` start pieces
([docs/slicer.md](../../../../docs/slicer.md#what-a-slice-is-composed-from)).

## The relief over the router is the Ender's

The relief is the Ender's bed, a probe taken on 2026-09-20, drawn over the
router's table because both boards have held the port name `/dev/ttyUSB0`
and a bed reading was listed by port name.

| What | Where it is established |
|---|---|
| The page asks the readings of the pinned port and draws the newest | `templates/fractal_viewer.html.j2`, `ensureMarks` and `refreshReading`: `GET /firmware/printers/leveling?port=<port>`, `records[0]` to `setMesh`; `machine_marks.js`'s `setMesh` draws nothing for a record without a mesh, so no relief is drawn by default |
| The readings of a port were every record whose `port` field is that name | `devices.leveling_records(port)` filtered on `rec.port == port` and nothing else |
| The router holds `/dev/ttyUSB0` | `~/.apothecary/firmware-state.json`: the CH340 (`0x1A86:0x7523`, no serial number, socket `1-1`) identified as `Grbl 1.3a · Grbl_ESP32` at 11:38:51Z on 2026-11-07, pinned to `garage/cnc_router.frame_system.controller` three seconds before |
| The readings under that name are the Ender's | `~/.apothecary/leveling/`: three records named `-dev_ttyUSB0` from 2026-09-20 and two named `-dev_ttyUSB1` from 2026-09-26, every one `firmware: Marlin TH3D UFW 2.94a`, every one's lines Marlin's `Bilinear Leveling Grid` |
| The page did ask, and was answered | the production server's request log: `GET /firmware/printers/where?port=/dev/ttyUSB0` and `GET /firmware/printers/leveling?port=/dev/ttyUSB0` at 11:38:50Z, one second before `POST /firmware/devices/identify`, and the readings asked again every six seconds after; `curl` of the same route on `:6283` answers the three Marlin records, newest `20260920T190143.380-dev_ttyUSB0` (a probe, range 0.877 mm), and `where` places them on `garage/cnc_router`, volume 400 × 600 × 80 |
| The same, without hardware | a copy of `~/.apothecary` under `APOTHECARY_STATE_DIR`, the simulated engine with `APOTHECARY_SIMULATED_ROUTER=/dev/ttyUSB0`: the leveling route answers the same three records for that port |

What else could produce a relief over the router, and why it is not that:
the demo's state (`.cache/demo/state/`) has no `leveling/` folder, and
production runs on `~/.apothecary`, not the demo's; the marks draw no mesh
unless a record with one is handed to them; and the router's Machine listed
no readings (its Bed level card was a printer's), so only the world showed it.

What a fix had to hold, as one case of keeping each machine's data its own:
a reading belongs to the board that took it, never to a port name, so a port
another board holds lists none of them; and a router shows no relief until
it has a reading of its own, which Marlin's `M420 V` cannot give it. On the
copy of the real state with a change of that shape, `/dev/ttyUSB0` answers no reading and
`/dev/ttyUSB1` the Ender's two from 2026-09-26. One cost any such change
carries: the five readings kept so far name no board, only the port each was
taken at.

The picture itself was not reproduced on the copy: with no board on the
port the site's device row carries no port, so the page makes no marks and
asks for no reading. On the production server at 11:38Z on 2026-11-07 the board was plugged in.

## The Ender 3, printer_1

### What is recorded

| | Recorded | Where |
|---|---|---|
| Firmware | Marlin TH3D UFW 2.94a (Jan 17 2025), machine type `TH3D EZABL`, 115200 baud | `firmware-state.json`, identified 2026-09-26 |
| Bridge | FTDI FT232R `0x0403:0x6001`, serial number `A106ZTEU`; pinned by that serial number to `creality_v422` in the universe `apothecary` | `firmware-state.json`, bound 2026-10-04 |
| Port names it has held | `/dev/ttyUSB0` (2026-09-20), `/dev/ttyUSB1` and `/dev/ttyUSB2` (2026-09-26) | the device records and the readings' names |
| Probe offset | `M851 X-44 Y-10 Z-3.15` | every reading |
| Leveling at power-up | off (`echo:Bed Leveling OFF`), fade height 10 mm | the two `read` records, six days apart, both after a power cycle |
| The stored mesh | 5 × 5, range 2.340 mm, tilt X +1.754 Y −0.466, corners FL −0.856 FR +1.075 BL −1.155 BR +0.473 against the mean; identical on 2026-09-20 and 2026-09-26 | `20260920T132512.468-dev_ttyUSB0`, `20260926T210453.925-dev_ttyUSB1` |
| The bed as probed, 2026-09-20 | range 0.877 mm, tilt X +0.530 Y −0.201, corners FL −0.207 FR +0.530 BL −0.347 BR +0.117 | `20260920T190143.380-dev_ttyUSB0` |
| The bed as probed, 2026-09-26 | range 0.830 mm, tilt X +0.523 Y −0.133, corners FL −0.279 FR +0.526 BL −0.304 BR +0.129 | `20260926T210823.479-dev_ttyUSB1` |
| Probe against probe | point by point the second is 0.07 mm above the first on average, at most 0.113 mm, nearly uniform across the bed | the two probe meshes, differenced |
| Conditions | cold: bed 14 to 16 °C, hotend 15 to 17 °C, in every reading | every reading |
| The print's start | `home` alone: heat, `G28`, prime; the `stored-mesh` (`M420 S1`) and `probe-each-print` (`G29`) start pieces were stubs at 8601a5e | `parts/ender3/slicer.json`, [docs/slicer.md](../../../../docs/slicer.md) |
| E-steps, PID | not recorded: `M503` answered 59 lines at the 2026-09-20 bench and they were not kept | [2026-09-20-ender-bench.md](2026-09-20-ender-bench.md) |

### What the numbers say

- **The mesh in the board's EEPROM is stale by about 1.5 mm.** The stored
  mesh (2.34 mm range) is the same bytes on 2026-09-20 and 2026-09-26, while
  the bed probed on both days is 0.83 to 0.88 mm out, the same shape within
  0.11 mm. Apothecary never writes EEPROM, so neither probe was stored, and
  the board boots with the old mesh and leveling off. What else would make
  the stored mesh stay the same: nothing probed between the reads stores
  itself -- a probe in Marlin stays in RAM until `M500`.
- **Turning the stored mesh on, as it is, would make the first layer
  worse.** `M420 S1` at a print's start would apply a 2.34 mm correction to
  a 0.85 mm bed. At 8601a5e the `stored-mesh` start piece was a stub, so no
  print did this; the piece that lands beside this record is refused until
  the newest probe's range is under the bound printer_1's profile holds, and
  0.83 mm is not.
- **The bed is trammed 0.85 mm out, front-right high and the left low.**
  From the probes: lower the front-right corner by about 0.5 mm and raise
  the two left corners by about 0.3 mm (the M4 screws under the bed have a
  0.7 mm pitch: about three-quarters of a turn and half a turn). The probe
  reaches no further right than X 176 (its offset is −44), so the bed's
  right edge is higher still than the mesh's right column.
- **The probe repeats.** Two probes six days apart agree to 0.11 mm at
  every point, with a uniform 0.07 mm shift that is a Z-offset or
  temperature difference, not the bed's shape. The EZABL can be trusted to
  measure what the tramming does.
- **Every reading is cold.** A glass or PEI bed at 60 °C is not the bed at
  15 °C; the mesh to print with is the one probed at printing temperature.
- **Whether `G28` keeps leveling on is unknown.** Marlin turns leveling off
  at `G28` unless the firmware restores it; the print's `home` start homes
  every axis. If it does not restore it, a print uses a mesh only through the
  `stored-mesh` piece.

### Recommendations

Each rests on the readings above unless it says otherwise.

1. Tram the bed by the corner buttons and paper (checklist C), to what the
   probe says: front-right down, left up. Confirm by Probe bed: a range
   under 0.3 mm expected, and what is left at the centre against the corners
   is the plate's bow, which tramming cannot remove.
2. Probe at printing temperature: heat the bed (Control › Bed 60 → Set), wait
   for the target, then Probe bed. Assumption: the bed moves with heat; the
   bench says by how much.
3. Store the probed mesh from the printer's own screen (Configuration ›
   Store Settings), since the seam refuses `M500` by design. Confirm by a
   power cycle and Read mesh: the record is the probed mesh, not the
   2.34 mm one.
4. Say whether `G28` keeps the mesh: after Probe bed (the record says
   leveling on), Home all, then Read mesh. If leveling is off, name the
   `stored-mesh` start piece (`M420 S1` after `G28`) in the printer's profile
   once a probe under its bound is stored; the piece reads the probe's range
   and cannot see whether it was stored, so storing it stays the bench's box.
   If on, the stored mesh is enough.
5. Read and keep `M503` whole, as the bench record of the day: `M92`
   (e-steps), `M301` and `M304` (PID), `M851`. Then a 100 mm extrusion
   test by the printer's own screen (the seam sends no extruder move) and a
   two-minute hold at 200 °C watched on the Machine's temperature chart: more
   than ±2 °C is a PID to tune from the printer's menu (`M303` is not a line
   the seam sends). Assumption: the firmware's defaults are untouched; the
   answers say.
6. Set the Z offset from the first layer, not the paper: a one-layer square
   printed from here, the offset adjusted on the printer's screen, stored,
   and the new `M851` kept in the record.
7. Keep the Ender's USB lead on the machine when the router is: a board's
   record counts for the board the port list finds on its port, by serial
   number for the FTDI, so the Ender's pin follows it to any port name.

## The router, cnc_router

### What is recorded

| | Recorded | Where |
|---|---|---|
| Controller | `Grbl 1.3a`, `Grbl_ESP32`, build `20211103`, 115200 baud; identified once, answering `ok` | `firmware-state.json`, 2026-11-07 11:38:51Z |
| Bridge | CH340 `0x1A86:0x7523`, no serial number, USB socket `1-1`; pinned by its port, `/dev/ttyUSB0`, to `cnc_router.frame_system.controller`, the socket kept beside the record | `firmware-state.json`, `seen` |
| `$$` | never read | this record |
| The machine | 400 × 600 × 80 mm travel, HGH15 rails, 1204 ball screws (4 mm lead), NEMA 23 closed-loop steppers, an 800 W trim router 8,000 to 24,000 rpm set by its own dial and switched by the controller, in a 65 mm clamp | `parts/anolex_4060_evo_ultra_2`, the maker's published figures |
| What the seam assumes | a move of 600 mm at most, feed 4000 mm/min, the spindle 24000 rpm, a probe 80 mm deep at 500 mm/min; home at the back right and the top of Z, the working area `mpos + travel` | `apothecary/firmware/grbl.py`, [docs/cnc.md](../../../../docs/cnc.md) |
| What the simulation answers to `$$` | travel 400/600/80, rates 4000/4000/2000, acceleration 200/200/100, 800 steps/mm, soft limits on, hard limits off, homing on, `$23=3`, `$30=24000`, `$10=1` | `grbl.SimulatedRouter.settings`: its own figures, not a recording of this controller |
| The demo walk | the Machine, pad, cut and stop against the simulation | [2026-11-03-router-walk.md](2026-11-03-router-walk.md) |

### What is unknown, and what it decides

Everything the controller's `$$` holds. Each unknown decides something the
page already draws or sends:

| Setting | Decides | Assumed | How the bench confirms |
|---|---|---|---|
| `$13` report inches | every position the page reads and draws | 0 (mm) | `$$`; `?` after a 10 mm jog reads 10, not 0.39 |
| `$32` laser mode | whether `M3` turns the router without a move; in laser mode a rapid switches it off | 0 | `$$`; Spindle On while idle turns the router |
| `$10` status report mask | whether `?` carries `Bf:`, the planner's room; a cut counts it when it is there and streams by each line's `ok` when it is not | either; `Bf:` is the better of the two | `?` in the log shows `Bf:15,…` with `$10=3`; `$10=1` streams by `ok` |
| `$130` `$131` `$132` travel | the working area drawn on the table, soft limits, the seam's `mpos + travel` | 400, 600, 80 | `$$` against the maker's figures; a jog to each end |
| `$110` `$111` `$112` max rate | the seam's feed cap (4000) and how a jog is answered | 4000, 4000, Z unknown | `$$`; the cap in `grbl.py` is held to it |
| `$120` `$121` `$122` acceleration | how a cut corners; ringing | unknown; the simulation's 200/200/100 are invented | `$$`, kept; changed only if cuts show ringing |
| `$100` `$101` `$102` steps/mm | whether 10 mm is 10 mm | 400 or 800 for a 4 mm lead at 1600 or 3200 pulses per turn | a 100 mm jog measured with a rule (±0.5) or a dial indicator (±0.02) |
| `$22` `$23` homing, direction | which corner is home; `mpos + travel` and the marks | on; back right, top of Z (`$23` with X and Y not inverted) | `$$`; Home, and note the corner |
| `$24` to `$27` homing feed, seek, debounce, pull-off | how Home behaves | unknown | `$$`, kept |
| `$20` soft limits | the controller refuses a move past the travel (`error:15`, `ALARM:2`); the seam's own bound is 600 mm per move, not the travel | on | `$$`; a jog past the travel refused |
| `$21` hard limits | a switch stops everything (`ALARM:1`); spindle noise can trip them | off | `$$`; the spindle at full speed a minute with `$21=1`: no alarm, or leave it off |
| `$30` `$31` spindle max, min | what `S` means to the controller's PWM; the seam caps at 24000 | 24000, 0 | `$$`; the dial sets the speed, `S` does not |
| `$6` `$5` `$4` probe, limit, enable invert | whether a probe touch is seen; `ALARM:4` or `5` when wrong | unknown | touch the plate by hand: `?` shows `Pn:P` |
| `$1` step idle delay | whether the motors hold between moves | unknown | `$$` |

The simulation's `$23=3` says X and Y home to their minimum, while the
simulation homes to the back-right maximum: the text is wrong of itself, not
of this machine, and a reader comparing the real `$$` with it should not
expect them to agree. That is a change to `grbl.SimulatedRouter.settings`.

### Recommendations

Each rests on the maker's figures and the seam's assumptions above, which is
why each ends at the bench.

1. Read `$$` first, with nothing armed, and keep the whole answer in a
   dated record: `uv run apothecary firmware printer <port> --query '$I'
   --query '$$'`. The seam's query list has `$$`, `$#`, `$G`, `$I`, `$N` and
   `?`; Grbl_ESP32's named settings beyond the numbered ones are read on its
   own web page or a serial terminal, not from here.
2. Before any jog: `$13=0` and `$32=0`. Either wrong makes the page's
   positions, or the spindle, lie. Assumption: the maker ships both at 0.
3. For a cut, `$10=3` so `?` carries `Bf:` and the cut counts the planner's
   room, where `$10=1` leaves it streaming by each line's `ok`, as a print
   does. Either works; the first keeps a hold and a poll flowing during a
   cut. Assumption: Grbl_ESP32 ships `$10=1`.
4. Hold the seam to `$$`: `$130` to `$132` against the part's 400 × 600 × 80,
   `$110` to `$112` against the feed cap, `$30` against the spindle cap. A
   figure that differs changes `grbl.py` and the part, not the controller.
5. Steps per millimetre by a measured jog, since a closed-loop driver's DIP
   switches set the pulses per turn and the maker's `$100` may not match
   them.
6. Homing and the corner: Home once, note the corner and `?`'s machine
   position after the pull-off. Then `$20=1` with the travel confirmed, so
   the controller, not the seam, refuses a move out of the working area.
   `$21` only after the spindle-noise test.
7. The spindle: `$30=24000`, `$31=0`; the trim router's dial sets the speed
   and the controller switches it, so a cut's `S` is what the file says and
   not what turns. Record the dial's position with each cut; the Cut card
   does not.
8. Tram the spindle to the table, then surface the spoilboard. With the touch
   plate, map the table (Probe table) or Probe Z at the four corners and the
   centre and read `[PRB:…]` for each: more than 0.2 mm across the table is
   the Z plate to tram first. Then a facing pass over the spoilboard with a surfacing bit,
   at the bit's maker's feed and depth (an assumption until a bit is chosen),
   from a CAM post's file, since the toolpath here is written from a part's
   declared cuts and no part declares the table yet.
9. Keep the router's USB lead in the socket it was pinned from (`1-1`): a
   CH340 has no serial number, so the socket is part of what tells the
   router's record from another board's.
10. Whether opening the port resets the controller (checklist I): if the
    banner lands in the log on Reconnect, never Release or Reconnect during
    a cut.

## Boxes for the bench checklist

Folded into [project/bench-checklist.md](../bench-checklist.md), in its
sections, which is where they are kept current; here they are as
recommended.

Setting up:

- [ ] `uv run apothecary firmware devices` with both leads in: the Ender's
      FTDI with its serial number, the router's CH340 without one; note which
      port name each took today, and the router's USB socket.

C. Motion, before the corners:

- [ ] `--query M503` from a terminal, the answer kept whole in a dated
      record: `M92`, `M301`, `M304`, `M851`, the `G29 W` points.
- [ ] The corners to the paper: front-right down about 0.5 mm, front-left and
      back-left up about 0.3 mm, then Home Z.

D. Levelling:

- [ ] Bed 60 → Set, the target reached, then Probe bed: the range under
      0.3 mm; note the centre against the corners.
- [ ] Store the mesh from the printer's screen (Configuration › Store
      Settings); power-cycle; Read mesh: the record is the probed mesh.
- [ ] After a probe, Home all, then Read mesh: leveling on or off; off means
      the `stored-mesh` start piece before any print with a mesh.
- [ ] The world: the relief over printer_1's bed is the newest reading;
      nothing over the router's table.

F. Slice and print:

- [ ] A one-layer square; the Z offset set on the printer's screen; the new
      `M851` kept.
- [ ] 200 °C held two minutes on the temperature chart: within ±2 °C, or PID
      from the printer's menu.
- [ ] 100 mm of filament by the printer's screen, measured; e-steps set and
      stored there.

I. The router, after `$$`:

- [ ] `$13=0`, `$32=0`; `$10=3`, so `?` shows `Bf:` (optional: `$10=1` streams by `ok`).
- [ ] `$130` to `$132` are 400, 600, 80; `$110` to `$112` against the feed
      cap; `$30=24000`, `$31=0`; `$120` to `$122` and `$24` to `$27` kept.
- [ ] A 100 mm jog in X measured with a rule or a dial indicator; `$100` to
      `$102` against the 4 mm lead.
- [ ] Home: the corner and the machine position after the pull-off; then
      `$20=1`.
- [ ] `$21=1`, the spindle at full speed a minute with no tool: no `ALARM:1`,
      or back to `$21=0`.
- [ ] The plate touched by hand shows `Pn:P`; Probe Z at the four corners and
      the centre, each `[PRB:…]` kept: more than 0.2 mm is the Z plate to tram.
- [ ] The spoilboard surfaced from a CAM post's file, the dial's position and
      the bit's feed and depth kept with the cut.

## Not done

- Nothing ran against either machine; every figure above is from the state
  folder, the records and the code, and every box is the bench's.
- The relief's picture was not reproduced on the state copy, for the reason
  above; the route's answer was.
- The fix is not in this record: it lands beside it, with the other cases of
  a port name standing for a board.
- A part declaring a facing pass over the spoilboard, so the toolpath here
  could surface it: not built. The simulation's `$23`: not
  changed.
