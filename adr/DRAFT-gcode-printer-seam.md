# ADR-XXXX — G-code printer seam: monitor printer controllers over the G-code line protocol

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-19 |
| **Pends on** | Nothing — ready for ratification. |
| **Checked against** | apothecary `4426724` (`build/governance`) |
| **Hardware evidence** | The suites run every path here against the scripted transport and the simulated engine. `docs/bench-checklist.md` in apothecary is the run on a printer that confirms §1's controls and §6's print, pause, cancel and emergency stop. |
| **Tools** | Drafted with Claude Code (Anthropic); the person who ratifies it is its contributor of record |

## Context

The garage site models a fleet of printers as Structures with a `status`
(`idle`, `printing`, `offline`, `maintenance`) and a build volume that jobs
are assigned against. A status a person types is only as current as their
last edit. A printer mainboard on the bench -- a Creality board behind an
FTDI bridge, running Marlin -- can say for itself whether it is printing,
and its temperatures, position and print progress, if something asks it.

This is a different kind of board from the ones the firmware toolchain seam
programs. It already runs a firmware; Apothecary does not build or flash it.
What it needs is a *monitor*: identify the controller, poll it, and reflect
what it says onto the scene node bound to it. That record keeps Apothecary's
own process off the ports it programs (a second opener corrupts reads on a
CP2102 bridge); a monitor cannot obey that, because polling is request and
response on one open port, so this record owns the exception and the rule
that makes it safe: one holder per port, enforced.

The protocol every 3D-printer host speaks to every controller is line-per-
command G-code over serial: a command out, response lines back, `ok` to
close the exchange, with a small set of well-documented query codes (`M115`
firmware info, `M105` temperatures, `M114` position, `M119` endstops, `M27`
SD progress, `M31` print time). Implementations on the controller side
include Marlin, RepRapFirmware, Klipper (through its Marlin-compatible
front), Prusa's firmware and Smoothieware; on the host side OctoPrint,
Pronterface/Printrun, Cura's USB printing and Repetier-Host. It passes the
seams record's replaceability test as written.

Two hardware facts shape the design. First, Creality boards wire the USB
bridge's DTR line to the microcontroller's reset, exactly like an Arduino,
and the kernel asserts DTR whenever the port is opened: whether opening the
port reboots the firmware depends on whether the *previous* program dropped
DTR when it closed. Most do. A running print then dies by accident. Second,
Marlin answers `M115` without a boot banner, so identification does not
need a reset at all.

## Decision

1. **The seam is G-code over serial.** `firmware/gcode.py` speaks the line
   protocol and parses Marlin's documented replies into Pydantic models
   (`PrinterInfo` from `M115` and its `Cap:` lines; `PrinterStatus` from
   `M105`/`M114`/`M119`/`M27`/`M31`). Parsers are pure functions tested
   against a transcript captured from a Marlin board. On its own, Apothecary
   sends only query codes. A person may send more, in two tiers, each an
   allowlist checked before anything reaches the port: **report-only
   queries** (`gcode.QUERY_CODES`: `M503`, `M119`, `M20`, `M420 V`, …) at
   any time, from the command line or a board's Machine on the page; and
   **operator controls** (`gcode.CONTROL_CODES`: heater targets with
   temperature caps, fan, homing, bounded jogs, steppers off, SD
   start/pause/abort, mesh on/off, the plain bed probe `G29`, a single
   bounded `G30`, breaking out of a heat-and-wait `M108` and the quickstop
   `M410`) only while a per-port **control latch** is armed -- an explicit
   act with a five-minute lifetime that every accepted command renews, that
   a released link drops, and that a Machine's *Control* surfaces as a
   toggle with its countdown. `M112` (emergency stop) is accepted
   regardless. A bed reading
   -- the stored mesh, probe offset and temperatures, with or without a
   probe first -- is the one composite the seam runs on its own: as a job
   that holds the link for the minutes a probe takes, refuses other
   traffic meanwhile (the emergency stop excepted), and saves what the
   firmware said as a record, so the readings before and after a turn of
   the bed screws can be compared. Nothing writes EEPROM or configures
   firmware.
2. **The byte transport is an engine slot.** A `Transport` protocol
   (`write`, `read(timeout)`, `pulse_reset`, `close`) with two engines:
   **pyserial** (BSD-3-Clause; any baud rate, 250000 included;
   Linux/macOS/Windows; a declared dependency), the serial engine, and
   **simulated**, an in-process pretend Marlin for demos and browser tests
   with no hardware. `APOTHECARY_SERIAL_ENGINE` names one, pyserial when it
   is unset; a name that is not an engine is refused with the list of
   engines. Nothing above the slot knows which engine is in use; unit tests
   run against a scripted transport and the browser tests against the
   simulated engine.
3. **The link is held open, and reset is explicit.** A printer's port is
   opened once and kept by a registry (`PrinterLinks`) until released;
   polls reuse the link (~0.1 s each). DTR is left asserted on close so the
   next open — Apothecary's or another program's — does not reboot the
   board. The board is rebooted only on request (`--reset` / `"reset":
   true`), which is how a boot banner is captured; the default
   identification path never resets. On POSIX the engine clears the port's
   hang-up-on-close flag (`HUPCL`), which is what leaves DTR asserted.
   Every exchange -- command, reply, boot banner, open/close/reset -- is
   kept in a per-port comms log on the server (a ring, owned by the
   registry so it outlives a reconnect), which is what a board's Machine
   shows; a reboot from a Machine asks to be pressed twice.
4. **One holder per port.** A devkit's serial stream -- the monitor of the
   toolchain module that found the port, `arduino-cli monitor` for
   Arduino's and the Rust module's own pyserial monitor -- and the printer
   link evict each other; a flash releases only the link of the port it
   writes to, never every printer's. A printer's Machine polls it rather
   than streaming it. While the link holds a port, the engine sets it
   exclusive (`TIOCEXCL` on POSIX), so another program's open fails rather
   than sharing it. A release route hands the port to another program
   (OctoPrint, a terminal) on request.
5. **A poll drives the status of the node it is pinned to, or the nearest
   ancestor that carries one.** A printer's port is pinned to its
   *mainboard* node (each garage printer carries one inside its base
   enclosure); the board has no status of its own, so the poll writes its
   `state` — `idle`, `printing`, or `offline` when a poll fails — into the
   printer Structure above it, and the poll response names that node and
   the board it came `via`, so the viewer can refresh. Pinning the
   Structure directly is the same rule with zero hops. Two limits: nodes
   with no status anywhere up their path are left alone, and a hand-set
   `maintenance` is never overridden by a poll. A job running on the
   machine -- a print, a bed reading -- marks the same node busy from the
   moment it begins, and its end lets it go back to `idle`. The site-devices
   view refreshes printers whose link is already held and never opens a
   port itself.
6. **A host for one print at a time, and no more than that.** The seam
   streams a sliced file to the printer itself: kept on the host, checked
   once as a whole against the same bounds a typed control meets (no
   settings writes, no firmware update, no kill, no temperature over the
   caps), then fed one line per `ok` -- the firmware's own flow control --
   as a job that keeps the link between lines for the polls and for the
   heater, fan and break-wait controls, and refuses motion, the SD card, a
   reset and a release until it ends. Pause stops the feed; cancel, a
   refused line and a silent one send a fixed safe-off (heaters and fan
   off, motors free, no blind park); the emergency stop ends it with
   nothing more sent. Every print is a record with its outcome. `build-the-seam-buy-the-engines`'s
   ordering question -- which engine owns this? -- is answered by §2 and
   §4 together: the seam already owns the line protocol and the held link,
   and a second holder of the port (OctoPrint, Moonraker) is exactly the
   contention §4 exists to prevent, so one print streamed over the link
   that is already open is the smaller thing. Queueing, watching or
   recording a print through a camera, and a print farm are not: they
   remain the domain of those hosts, and wanting one of them is the trigger
   below. Slicing is the record *Slicer seam: slice parts for a printer
   through slicer modules, OrcaSlicer first*: it makes the file this seam
   streams, and this seam neither slices nor knows which slicer made a
   file. A camera standing in a site takes the world's pictures (the
   record *Personal data stays on the device, by construction* names
   them), not a print's.

## Consequences

- One runtime dependency, pyserial, whose licence text is BSD-3-Clause (it
  declares `BSD`); the adoption scope's audit table carries it. The engine
  slot has two implementations behind it, pyserial and the simulated
  printer, and a second serial engine is an addition behind the same
  protocol.
- `DeviceInfo` carries `serial_number` (the bridge's USB serial number, from
  the port listing) and `printer` (the cached `M115` answer), so the device
  views tell a printer from a devkit without touching the port.
- A board's identity, which its pins and flash records key on, is its MAC,
  else its bridge's USB serial number, else its port, so a pinned printer
  is found again when the kernel numbers its port differently. Some bridges
  ship a generic serial number (every CP2102 says `0001`), and two such
  boards without a MAC share an identity; Marlin's `UUID` is compiled into
  the build, shared by every board running it, and is not used. A board
  with neither a MAC nor a serial number is pinned by its port, which is
  only as stable as the kernel's numbering.
- Polling is driven by clients (a printer's Machine at the shortest
  interval anything watching it asks for, each poll scheduled after the
  previous returns and none while the page is hidden; the site-devices view
  on request).
  Poll and scan routes are synchronous handlers that FastAPI runs in its
  threadpool, so the event loop never waits on a serial port or on
  `arduino-cli`, whose ~2 s port scan is cached for two seconds. There is
  no background poller in the server, so a node's status is only as fresh
  as the last client to ask. Accepted: it keeps the server free of threads
  that outlive requests, and a poller is a small addition if a fleet view
  needs it. Browser tests hold the viewer to timing bounds under polling.
- Marlin replies are the reference. RepRapFirmware and Klipper differ in
  detail (`M408`/JSON on RRF; Klipper's `M115` is terse); the parsers are
  written to tolerate missing fields, and a second firmware family is a
  parser addition behind the same models, not a redesign.

## Alternatives considered

1. **OctoPrint (or Moonraker) as the engine, Apothecary talking to its REST
   API** — lost for the monitor: it makes a print host a hard prerequisite
   for showing a temperature, and each host's API is single-implementation,
   so the seam would be *worse* than the wire protocol underneath it. It
   remains the right answer for what §6 leaves out.
2. **Reuse `arduino-cli monitor` (the Arduino module's serial monitor)
   as the transport** — rejected: it is one-way in practice (stdin is not a
   reliable command channel), spends seconds on port discovery per open,
   and opens the port per stream — exactly the reset hazard §3 exists to
   remove.
3. **Enable Marlin's autoreport (`M155`) and stream, instead of polling** —
   rejected as the primary path: autoreport is lost on every reset, is
   temperature-only, and needs a long-lived stream per client. Polling over
   the held link answers everything the node needs at ~0.1 s; autoreport
   lines are tolerated in the same reads if a user enables it.
4. **A stdlib transport (`termios`), alone or as a fallback beside
   pyserial** — rejected alone because the standard termios table lacks
   250000 baud, the other common Marlin rate, and POSIX `termios` does not
   exist on Windows. Rejected as a fallback because pyserial is a declared
   dependency, so an install without it does not occur: a second
   implementation of the same port handling would be tested for a machine
   that does not exist, and would be one more place for the DTR handling
   in §3 to be missed.
5. **Let a poll set any bound node's status, including `maintenance`** —
   rejected: `maintenance` is a human statement about the machine that a
   cold, idle controller cannot contradict.
6. **A free-form G-code console** — rejected: one mistyped line heats a
   hotend or drives a bed into a nozzle. Two allowlists with bounds, and a
   latch in front of the one that moves anything, keep the failure mode
   to "refused" rather than "melted"; extending the lists is a deliberate
   edit here, not a runtime setting. A streamed file is not a console: it
   is checked whole before the first line, behind the same latch.
7. **Filling the firmware's buffer ahead of its `ok`s (line numbers and
   checksums, `N…*…`)** — rejected for now: it is faster on a slow serial
   link, but a resend protocol is a second state machine to get right, and
   at 115200 baud one line per `ok` keeps a Marlin planner fed. A print
   that stutters on a real machine is the trigger to revisit.

## Revision triggers

- A print queue, a camera watching or recording a print, or more than one
  printer fed at once is wanted — §6: a new record, and
  `build-the-seam-buy-the-engines`'s ordering question again with a host's
  REST API as a candidate answer.
- A streamed print stutters on a real machine — alternative 7: line
  numbers and checksums, or a buffer ahead of the `ok`s.
- A second firmware family (RepRapFirmware, Klipper) is plugged in and the
  Marlin-shaped parsers miss something the viewer needs.
- A fleet view needs status fresher than the last client poll — a
  background poller, and the polling consequence above with it.
- pyserial is relicensed or archived — the open-license record's relicense
  protocol; a stdlib engine behind the same `Transport` protocol (`termios`
  with the `BOTHER` extension for 250000 baud) is the nearest exit on
  POSIX, and Windows has none.
- The firmware routes are exposed beyond localhost — a separate record,
  shared with the toolchain seam's trigger of the same name.

## Amendments

*None.*
