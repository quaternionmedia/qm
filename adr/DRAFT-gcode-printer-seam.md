# ADR-XXXX — G-code printer seam: monitor printer controllers over the G-code line protocol

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-19 |
| **Pends on** | Nothing — ready for ratification. |
| **Tools** | Drafted with Claude (Anthropic) against a Creality mainboard running Marlin TH3D UFW 2.94a; the sponsoring human is the contributor of record. |

## Context

The garage site models a fleet of printers as Structures with a `status`
(`idle`, `printing`, `offline`, `maintenance`) and a build volume that jobs
are assigned against. Until now that status was hand-edited. A real printer
mainboard plugged into the workbench — a Creality board, FTDI bridge, Marlin
firmware — makes it possible to drive the status from the machine itself
and to show temperatures, position and print progress in the viewer.

This is a different kind of board from the ones the firmware toolchain seam
programs. It already runs a firmware; Apothecary does not build or flash it.
What it needs is a *monitor*: identify the controller, poll it, and reflect
what it says onto the scene node bound to it. That record keeps Apothecary's
own process off the ports it programs (a second opener corrupted reads on a
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
   against a transcript captured from a real board. On its own, Apothecary
   sends only query codes. A person may send more, in two tiers, each an
   allowlist checked before anything reaches the port: **report-only
   queries** (`gcode.QUERY_CODES`: `M503`, `M119`, `M20`, `M420 V`, …) at
   any time, from the CLI, the overlay or the monitor; and **operator
   controls** (`gcode.CONTROL_CODES`: heater targets with temperature
   caps, fan, homing, bounded jogs, steppers off, SD start/pause/abort,
   mesh on/off) only while a per-port **control latch** is armed -- an
   explicit act with a five-minute lifetime that every accepted command
   renews, that a released link drops, and that the monitor's overlay
   surfaces as a toggle. `M112` (emergency stop) is accepted regardless.
   Nothing streams a job, writes EEPROM or configures firmware.
2. **The byte transport is an engine slot.** A `Transport` protocol
   (`write`, `read(timeout)`, `pulse_reset`, `close`) with two engines:
   **pyserial** (BSD; any baud rate, Linux/macOS/Windows; a declared
   dependency) chosen when importable, else the stdlib's **termios**
   (POSIX, standard baud table — enough for a 115200 board with nothing
   installed), plus **simulated**, an in-process pretend Marlin for demos
   and browser tests with no hardware. `APOTHECARY_SERIAL_ENGINE` pins one.
   Nothing above the slot knows which engine is in use; unit tests run
   against a scripted transport and the browser tests against the
   simulated engine.
3. **The link is held open, and reset is explicit.** A printer's port is
   opened once and kept by a registry (`PrinterLinks`) until released;
   polls reuse the link (~0.1 s each). DTR is left asserted on close so the
   next open — Apothecary's or another program's — does not reboot the
   board. The board is rebooted only on request (`--reset` / `"reset":
   true`), which is how a boot banner is captured; the default
   identification path never resets.
   Every exchange -- command, reply, boot banner, open/close/reset -- is
   kept in a per-port comms log on the server (a ring, owned by the
   registry so it outlives a reconnect), which is what the focused monitor
   page shows; a reset from that page is behind a confirmation.
4. **One holder per port.** The serial-monitor stream (`arduino-cli
   monitor`) and the printer link evict each other; an upload releases only
   the link of the port it writes to, never every printer's. The viewer's
   serial overlay polls a printer rather than streaming it. A release route
   hands the port to another program (a slicer, OctoPrint) on request.
5. **A poll drives the status of the node it is pinned to, or the nearest
   ancestor that carries one.** A printer's port is pinned to its
   *mainboard* node (each garage printer carries one inside its base
   enclosure); the board has no status of its own, so the poll writes its
   `state` — `idle`, `printing`, or `offline` when a poll fails — into the
   printer Structure above it, and the poll response names that node and
   the board it came `via`, so the viewer can refresh. Pinning the
   Structure directly is the same rule with zero hops. Two limits: nodes
   with no status anywhere up their path are left alone, and a hand-set
   `maintenance` is never overridden by a poll. The site-devices view
   refreshes printers whose link is already held and never opens a port
   itself.
6. **Not a print host.** Streaming a job to a printer, queueing, and
   webcam/timelapse are the domain of OctoPrint, Klipper/Moonraker and
   their kin. The latched controls in §1 are what a person standing at the
   machine would do from its own screen -- preheat, home, jog, pause --
   not a job pipeline. If Apothecary ever needs to *send* a print, P4's ordering rule
   applies first (which engine owns this?), and that is a new record — with
   a seams exception if the answer is one host's REST API.

## Consequences

- One new runtime dependency, pyserial (BSD-3-Clause), which clears the
  open-license record and the CI allowlist. The termios fallback keeps the
  seam usable with nothing installed, which is also what makes the engine
  slot honest: there are two implementations behind it from day one.
- `DeviceInfo` gains `serial_number` (from arduino-cli's port properties)
  and `printer` (the cached `M115` answer), so the device views tell a
  printer from a devkit without touching the port. The USB serial number
  is informational, not the device identity: some bridges ship a generic
  one (every CP2102 says `0001`), and Marlin's `UUID` is compiled into the
  build, shared by every board running it. Identity stays MAC-or-port.
- A pin to `/dev/ttyUSBn` is only as stable as the kernel's numbering. The
  documented optional remedy is a udev rule naming the port by the bridge's
  USB serial number; it is not required.
- Polling is driven by clients (the viewer overlay every 2 s, each poll
  scheduled after the previous returns; the site-devices view on request).
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
   remains the right answer for §6.
2. **Reuse `arduino-cli monitor` (already the serial engine for sketches)
   as the transport** — rejected: it is one-way in practice (stdin is not a
   reliable command channel), spends seconds on port discovery per open,
   and opens the port per stream — exactly the reset hazard §3 exists to
   remove.
3. **Enable Marlin's autoreport (`M155`) and stream, instead of polling** —
   rejected as the primary path: autoreport is lost on every reset, is
   temperature-only, and needs a long-lived stream per client. Polling over
   the held link answers everything the node needs at ~0.1 s; autoreport
   lines are tolerated in the same reads if a user enables it.
4. **A stdlib-only transport, no pyserial** — rejected because the standard
   termios table lacks 250000 baud, the other common Marlin rate, and POSIX
   `termios` does not exist on Windows. Kept as the fallback engine, not
   the only one.
5. **Let a poll set any bound node's status, including `maintenance`** —
   rejected: `maintenance` is a human statement about the machine that a
   cold, idle controller cannot contradict.
6. **A free-form G-code console** — rejected: one mistyped line heats a
   hotend or drives a bed into a nozzle. Two allowlists with bounds, and a
   latch in front of the one that moves anything, keep the failure mode
   to "refused" rather than "melted"; extending the lists is a deliberate
   edit here, not a runtime setting.

## Revision triggers

- Apothecary needs to send a print or motion command — §6: a new record.
- A second firmware family (RepRapFirmware, Klipper) is plugged in and the
  Marlin-shaped parsers miss something the viewer needs.
- A fleet view needs status fresher than the last client poll — add the
  background poller and amend §5's consequence.
- pyserial is relicensed or archived — the termios engine is already the
  exit; decide whether it needs the `BOTHER` extension for 250000 baud.
- The firmware routes are exposed beyond localhost — a separate record,
  shared with the toolchain seam's trigger of the same name.

## Amendments

*None.*
