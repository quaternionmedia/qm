# ADR-XXXX — Firmware toolchain seam: program boards from Apothecary through toolchain modules

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-15 |
| **Pends on** | Human ratification of *QM constitution adoption scope for Apothecary*, which fixes this project's disposition toward externally-invoked copyleft binaries (its Consequences name `openscad` as the precedent this record extends). |
| **Tools** | Claude Code (Anthropic) assisted the 2026-09-19 revision (§6's scope, the cross-reference to the printer seam) and the 2026-10-10 revision (§2's modules, Rust for the ESP32, §6's port rule); the human who sponsored the work is the contributor of record. |

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

Not every sketch is Arduino's to build. The owner chose, on 2026-10-08, to
program the classic ESP32 in Rust as well (`esp-hal`, no_std): a build
`arduino-cli` cannot make, which this record's own revision trigger
anticipated. The engines for it -- `cargo` on Espressif's Xtensa Rust, and
**espflash** (MIT OR Apache-2.0) to flash -- are executables of the same
shape, and the owner asked that Arduino and the ESP32 be modules of one seam,
so that a later board family or language is a module added, not a redesign.

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
   and the web GUI. A sketch may also be a Cargo project in its part's
   folder (`parts/esp32_blink/rust/`), its `firmware.json` naming its
   toolchain. Every sketch is named with its toolchain
   (`esp32_blink@arduino`, `esp32_blink@rust-esp32`) wherever it is shown or
   asked for; a node that names the behaviour (`esp32_blink`) matches a board
   running either build, and the board's hello is the same. Apothecary does
   not compile, link, or flash anything itself.

2. **Toolchains are modules behind one interface; each module's engines
   are reached over a subprocess seam.** A module (`apothecary/firmware/
   modules/`) says what it builds (languages, board families), finds its
   tools, reports its status, installs them, and turns a build or a flash
   into steps: typed request → argv list → documented output parsed. Two
   exist. *Arduino*: arduino-cli is the build-and-upload engine (`--json`,
   both the v1.x wrapped and the 0.x bare shapes) and esptool the raw-flash
   engine. *Rust for the ESP32*: `cargo build --release --offline` builds
   from vendored crates, and espflash flashes. A later board family or
   language (the ESP32-C3 on stable Rust, AVR, the RP2040) is a module added
   to the registry. No engine is a declared Python dependency, so the
   dependency-manifest license gate is unaffected by construction; each
   remains a binary the user runs, exactly as `openscad` is.

3. **The installer fetches arduino-cli from Arduino's GitHub releases,
   pinned or latest, and refuses an archive whose SHA-256 does not match
   the release's published checksums.** It lands in
   `~/.apothecary/tools/arduino-cli/` (`APOTHECARY_TOOLS_DIR` overrides) — a
   `$HOME` path rather than an XDG data dir, because sandboxed editors point
   `XDG_DATA_HOME` at a per-revision tree that vanishes on update. Detection
   order for an existing install: `ARDUINO_CLI` env, the tools dir, `PATH`.
   esptool is detected, not installed: on `PATH`, bundled inside the esp32
   Arduino core, or as an importable module, in that order. For Rust on the
   ESP32, `apothecary firmware install --rust-esp32` fetches, into the tools
   dir and nowhere else: rustup-init, checked against the `.sha256` published
   beside it; espflash, checked against the SHA-256 GitHub publishes for the
   asset; Espressif's Xtensa Rust and rust-src, checked the same way (their
   release has no checksum file); and Espressif's LLVM and GCC, checked
   against their releases' own checksum files. Each archive is checked before
   it is opened, and no downloaded script runs: the Rust components are
   copied as their manifests list them, and the toolchain is linked into the
   tools dir's rustup. It then vendors each Rust sketch's crates, so every
   build afterwards reaches no host. Versions are pinned and move only in a
   commit that bumps them and re-runs the real install and an offline build.
   Each install flag installs its own module and nothing else. Detection for
   Rust: `CARGO` and `ESPFLASH` env, the tools dir, `PATH`; for every
   engine's variable, `none` means none.

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
   binary, and the GUI asks for confirmation before any write to a board. A
   Rust build remaps every folder it is made in (`--remap-path-prefix`) and
   its last step reads the whole image and fails if any of them appears, so
   no build path -- and so no user name -- reaches a flashed board.

6. **A board is described from three independent sources, and the GUI
   shows where they disagree.** *Detected*: the serial port and USB bridge,
   by each module's own finding (`arduino-cli board list` for Arduino;
   pyserial's port list, which opens nothing, for Rust). *Probed*: chip
   model, revision, MAC and flash size (`esptool flash_id`, or espflash's
   `board-info` where there is no esptool; both reset the board), cached per
   port.
   *Expected*: a `FlashRecord` Apothecary writes on every successful upload
   — sketch, FQBN, SHA-256 of the uploaded binary and of the sketch sources —
   keyed by MAC when known, else by port, kept in
   `~/.apothecary/firmware-state.json` (machine state, never committed), and
   compared against the tree on every view (source edited since; newer build
   never uploaded; sketch gone). *Observed*: serial output through each
   module's own monitor. A sketch identifies itself by printing
   `apothecary <name>: hello` at boot **and periodically** (every few
   seconds) — periodically because the monitor takes longer to attach than
   a boot banner lasts, and a protocol that depends on catching boot is a
   protocol that fails whenever it matters. For the boards this record
   programs, a port is opened only by the toolchain module that found it,
   through that module's own engines, one holder at a time: for Arduino,
   arduino-cli (monitor, upload) and esptool; for Rust on the ESP32,
   espflash (flash, board-info) and Apothecary's own serial monitor --
   pyserial, run as a process of its own, opening the port exclusively with
   DTR and RTS de-asserted so that listening does not reset the board. The
   server process itself still opens no devkit's port, because a second
   opener was observed to corrupt reads on a CP2102 bridge. A port two
   modules find belongs to the first (Arduino's, when arduino-cli is
   installed). A board Apothecary *monitors* rather than
   programs — a printer mainboard speaking G-code — is the deliberate
   exception, held to one holder per port; that is the *G-code printer
   seam* record's decision, not this one's.

7. **Serial output streams as server-sent events, and any task pre-empts
   it.** `GET /firmware/devices/stream` keeps one monitor per port, the
   finding module's; a board's Machine in the viewer shows it as the board's
   one log. Starting any task stops every
   monitor first (an upload needs the port more than an overlay does) and
   the overlay reconnects when the task ends. Bytes are paced through a
   token bucket refilled at the wire rate: a burst the UART could not have
   delivered, or a verbatim repeat arriving faster than the wire could
   resend it, is a bridge replay and is dropped; three in a row reopen the
   port with a marker line. Genuine output is never throttled — the bucket
   refills as fast as the wire can fill it.

8. **Surfaces.** CLI: `apothecary firmware {install [--rust-esp32],
   validate, boards, cores, libraries, sketches, compile, upload, flash-bin,
   devices, probe, listen}`; `apothecary check` reports each module's state
   alongside OpenSCAD. GUI: the viewer's Bench panel (toolchains and their
   installs, a ring of the modules; sketches; compile and upload) and a
   board's Machine (its sketch, flashing, its log); `/firmware` opens the
   viewer with the Bench. API: `/firmware/status`, `/toolchains` (+
   `/toolchains/{id}/install`), `/boards`, `/boards/all`, `/cores`,
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
- A part needs a board family or language no module builds (ESP-IDF
  native, Zephyr, the ESP32-C3 in Rust, bare-metal RP2040) — add a module
  per §2, and say in §6 how it finds and opens its ports.
- Espressif changes how it publishes the Xtensa toolchain, or a pinned
  version is bumped — §3's install is re-run for real and offline-built
  before the bump lands.
- `apothecary/firmware/` plus its CLI exceeds roughly 4,000 lines, or the
  flash-record file grows into something that wants a schema migration — P4 size smell; re-examine what an engine should
  own.
- The server gains any non-localhost binding or authentication — §5's
  threat model changes and this record must be revisited before that ships.
- The *adoption scope* record is ratified — re-check §2's reliance on its
  copyleft disposition against the ratified text.

## Amendments

*None.*
