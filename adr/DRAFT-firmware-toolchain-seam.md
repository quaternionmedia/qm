# ADR-XXXX — Firmware toolchain seam: program boards from Apothecary via arduino-cli and esptool

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-15 |
| **Pends on** | Human ratification of *QM constitution adoption scope for Apothecary*, which fixes this project's disposition toward externally-invoked copyleft binaries (its Consequences name `openscad` as the precedent this record extends). |

## Context

Several parts in the library are not only geometry. The footpedal is an
Arduino running MIDI firmware (`parts/footpedal/footpedal.ino`, FastLED +
Control Surface); the modular RC snowplow is headed the same way. Until now
Apothecary rendered the enclosure and left the microcontroller to a separate
tool with no link back to the part — the design record of a physical object
stopped at the plastic.

The two engines that matter are both mature, openly licensed, and built for
exactly this: **arduino-cli** (GPL-3.0; Arduino's own CLI for boards, cores,
libraries, compile and upload, with a stable `--json` output contract and a
versioned release pipeline publishing SHA-256 checksums) covers AVR, ESP32,
ESP8266, RP2040, SAMD and anything else with a board-manager index; and
**esptool** (GPL-2.0-or-later; Espressif's flasher) covers raw binary flashing
of Espressif chips outside the Arduino build model. Neither is a Python
library Apothecary would link; both are executables with a documented CLI —
the same shape as the `openscad` binary this project already drives, and
the adoption-scope record's audit already classes that shape as acceptable
under the open-license record's copyleft clause because it is invoked, never
linked or vendored.

Apothecary is a `uv`-managed local tool plus a localhost FastAPI server
(P5 house stack). The server executes binaries and opens serial ports on
the machine it runs on; nothing in this decision changes its localhost
binding or adds authentication, and nothing should — a firmware workbench
is a local control, not a service.

## Decision

1. **Firmware programming is in scope for Apothecary, as a seam, not an
   engine.** Apothecary owns: discovery of sketches under `parts/`
   (`<folder>/<folder>.ino`, arduino-cli's own layout rule, with an optional
   `firmware.json` sidecar carrying a default FQBN, required cores and
   libraries, and a human note); installation and validation of the
   toolchain; input validation; and streaming of engine output to the CLI
   and the web GUI. Apothecary does not compile, link, or flash anything
   itself.

2. **arduino-cli is the build-and-upload engine; esptool is the raw-flash
   engine.** Both are reached over a subprocess seam (`apothecary/firmware/
   toolchains.py`): typed request → argv list → documented output parsed
   (`--json` for arduino-cli, both the v1.x wrapped and the 0.x bare shapes).
   Neither is a declared Python dependency, so the dependency-manifest
   license gate is unaffected by construction; both remain GPL binaries the
   user runs, exactly as `openscad` is.

3. **The installer fetches arduino-cli from Arduino's GitHub releases,
   pinned or latest, and refuses an archive whose SHA-256 does not match
   the release's published checksums.** It lands in
   `~/.apothecary/tools/arduino-cli/` (`APOTHECARY_TOOLS_DIR` overrides) — a
   `$HOME` path rather than an XDG data dir, because sandboxed editors point
   `XDG_DATA_HOME` at a per-revision tree that vanishes on update. Detection
   order for an existing install: `ARDUINO_CLI` env, the tools dir, `PATH`.
   esptool is detected, not installed: on `PATH`, bundled inside the esp32
   Arduino core, or as an importable module, in that order.

4. **Every engine invocation from the GUI is a background task with a
   polled log; one task runs at a time.** `POST /firmware/…` returns a task
   id; `GET /firmware/tasks/{id}?since=N` returns new lines. A second request
   while one runs is a `409`, not a queue — two uploads racing for one serial
   port is never intended. The CLI runs the identical argv synchronously
   through the same `stream()` helper, so the two paths cannot drift.

5. **Inputs that become argv are validated by shape, never interpolated
   through a shell.** FQBN (`vendor:arch:board[:opts]`), serial port
   (`/dev/…` or `COMn`), core id (`vendor:arch`) and chip name each have a
   regex; sketch names resolve only to discovered sketches; esptool image
   paths resolve only inside the repository tree. Uploads compile first and
   flash the fresh build (`--build-path` → `--input-dir`), never a stale
   binary, and the GUI asks for confirmation before any write to a board.

6. **A board is described from three independent sources, and the GUI
   shows where they disagree.** *Detected*: the serial port and USB bridge
   (`arduino-cli board list`). *Probed*: chip model, revision, MAC and flash
   size (`esptool flash_id`, which resets the board), cached per port.
   *Expected*: a `FlashRecord` Apothecary writes on every successful upload
   — sketch, FQBN, SHA-256 of the uploaded binary and of the sketch sources —
   keyed by MAC when known, else by port, kept in
   `~/.apothecary/firmware-state.json` (machine state, never committed), and
   compared against the tree on every view (source edited since; newer build
   never uploaded; sketch gone). *Observed*: serial output through
   `arduino-cli monitor`. A sketch identifies itself by printing
   `apothecary <name>: hello` at boot **and periodically** (every few
   seconds) — periodically because the monitor takes longer to attach than
   a boot banner lasts, and a protocol that depends on catching boot is a
   protocol that fails whenever it matters. Only arduino-cli and esptool
   ever open the port: Apothecary's own process never does, because a
   second opener was observed to corrupt reads on a CP2102 bridge.

7. **Serial output streams as server-sent events, and any task pre-empts
   it.** `GET /firmware/devices/stream` keeps one `arduino-cli monitor` per
   port; the firmware page shows it inline and the fractal viewer floats it
   over the 3D view as a toggleable terminal. Starting any task stops every
   monitor first (an upload needs the port more than an overlay does) and
   the overlay reconnects when the task ends. Bytes are paced through a
   token bucket refilled at the wire rate: a burst the UART could not have
   delivered, or a verbatim repeat arriving faster than the wire could
   resend it, is a bridge replay and is dropped; three in a row reopen the
   port with a marker line. Genuine output is never throttled — the bucket
   refills as fast as the wire can fill it.

8. **Surfaces.** CLI: `apothecary firmware {install, validate, boards,
   cores, libraries, sketches, compile, upload, flash-bin, devices, probe,
   listen}`; `apothecary check` reports toolchain state alongside OpenSCAD.
   GUI: `/firmware`, a single-file HTML/JS page (P9) in the fractal viewer's
   visual language, linked from its toolbar; the viewer's "Serial log"
   toggle. API: `/firmware/status`, `/boards`, `/boards/all`, `/cores`,
   `/sketches`, `/devices` (+ `/probe`, `/listen`, `/stream`), and the
   task-returning `POST`s.

## Consequences

- The footpedal gains a `firmware.json` (`arduino:avr:uno`, FastLED, Control
  Surface). Its sketch does not currently compile against the *current*
  versions of those libraries (Control Surface 2.x changed the `note()` API
  and its STL fallback collides with FastLED 3.10's); that is a content
  defect in the sketch, surfaced by this seam rather than caused by it, and
  is left for the part's owner — `firmware.json` can pin `Name@Version` if
  the old combination is wanted.
- Cost accepted: the first `core install esp32:esp32` is a multi-hundred-MB
  download into `~/.arduino15`; the GUI offers it as an explicit button, the
  installer never pulls a core the user did not ask for.
- Cost accepted: the toolchain seam adds roughly 2,400 lines of control-plane
  Python (models, two engine wrappers, installer, task runner, device
  state, serial streaming, routes, CLI) and one page plus an overlay; P4's
  size-smell trigger applies (below).
- Cost accepted: the replay guard is a workaround for a bridge/driver fault
  Apothecary cannot fix. It is bounded (drop, then reopen, then give up with
  a message), observable (marker lines in the log), and confined to the
  seam. It should be registered upstream against the driver if the fault is
  ever reproduced outside this one bench.
- `parts/esp32_blink` is the reference implementation of the announce
  protocol in §6 and the smoke test for a fresh board or toolchain.
- Obligation: the seam's tests run against a scripted fake `arduino-cli`
  (`tests/conftest.py`), so CI needs no toolchain, serial port, or network.
  The one E2E test asserts the page is honest about toolchain state in both
  the installed and missing cases.
- Obligation: the replaceability test holds by construction — a different
  build tool (PlatformIO, a bare `avr-gcc`/`avrdude` pair, `idf.py`) is a
  new class with the same six methods, and the GUI, CLI and task runner do
  not change. This record should be amended, not rewritten, when one lands.

## Alternatives considered

1. **PlatformIO as the engine** — rejected for now: it would cover more
   ecosystems from one tool, but it is a Python package with its own
   dependency tree (pulling it into the manifest gate and the house
   `uv.lock`), its project model wants a `platformio.ini` per sketch rather
   than the bare `.ino` the library already holds, and its board/core
   installs are larger. It remains the obvious second engine class under
   §2 when a part needs a non-Arduino framework.
2. **Link esptool as a Python dependency** (`pip install esptool`, call its
   API) — rejected: it would put a GPL-2.0-or-later package into an MIT
   package's runtime dependency set, and esptool's Python API is not the
   stable contract its CLI is. Detecting an installed esptool and invoking it
   keeps the same disposition as `openscad`.
3. **Let the GUI accept an arbitrary sketch path** — rejected: the server
   executes what it is handed; confining sketches to `parts/` and images to
   the repository is the difference between a workbench and a remote shell.
4. **Queue tasks instead of returning 409** — rejected: a queue hides the
   fact that a board is mid-flash; the GUI's disabled buttons and busy pill
   tell the user what is happening, and a CLI user gets the same answer.
5. **Do nothing; keep firmware in the Arduino IDE** — rejected: it leaves
   the part's design record incomplete (P6) and the toolchain unreproducible
   per machine (P8: no snowflake dev laptops).

## Revision triggers

- arduino-cli or esptool relicenses off an OSI license, is archived, or goes
  twelve months without a release — starts the open-license record's §2
  clock; the seam makes the swap a component change.
- A part needs a framework arduino-cli cannot build (ESP-IDF native, Zephyr,
  bare-metal RP2040) — add the engine class per §2 and amend §6.
- `apothecary/firmware/` plus its CLI exceeds roughly 4,000 lines, or the
  flash-record file grows into something that wants a schema migration — P4 size smell; re-examine what an engine should
  own.
- The server gains any non-localhost binding or authentication — §5's
  threat model changes and this record must be revisited before that ships.
- The *adoption scope* record is ratified — re-check §2's reliance on its
  copyleft disposition against the ratified text.

## Amendments

*None.*
