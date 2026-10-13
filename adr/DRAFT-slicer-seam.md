# ADR-XXXX — Slicer seam: slice parts for a printer through slicer modules, OrcaSlicer first

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-10 |
| **Pends on** | Human ratification of *QM constitution adoption scope for Apothecary*, which fixes this project's disposition toward externally-invoked copyleft binaries; OrcaSlicer is AGPL-3.0, run as a binary and never linked. |
| **Checked against** | apothecary `77f75c8` (`build/governance`); the releases OrcaSlicer and PrusaSlicer publish, read from their GitHub releases |
| **Established by** | the routes, the command line, the pins and the profile read from the code; the install's hosts and a slice's reach from a real install and real slices traced with `strace -f -e trace=network` (§7) |
| **Tools** | Drafted with Claude Code (Anthropic); the person who ratifies it is its contributor of record |

## Context

Apothecary drives a printer over G-code (the *G-code printer seam*
record) and makes pieces from pictures. That seam streams a file and does
not make one. A person who slices a part in a slicer of their own and
brings the file back through the Print card's file box takes the loop from
a picture to a print out of the page at its last step, and describes the
printer twice: once here, measured, and once in their slicer.

The G-code printer seam leaves slicing out, and asks of a slicer the
question `build-the-seam-buy-the-engines` asks of every capability:
which engine should own it upstream.

OrcaSlicer (AGPL-3.0) publishes native builds for Linux, macOS and Windows on
its GitHub releases, a command line that slices from profile files, and
vendor profiles, Creality's Ender-3 among them. It is an executable of the
same shape as the `openscad` binary this project already drives: invoked,
never linked or vendored.

The printer it slices for is printer_1, an Ender 3 whose firmware, build
volume and probe offset the bench measured (`docs/validation/
2026-09-20-ender-bench.md`). A part says what it needs printed through its
declared print settings, which `apothecary problems` already checks for.

## Decision

1. **Slicing is in scope, as a seam, not an engine.** Apothecary owns the
   slicer's installation and status, the printer's profile, the settings it
   derives from a part, the task that runs a slice, and what is kept.
   It does not slice anything itself. The engine that owns slicing is a
   slicer, bought and reached over its command line; a print host that
   slices (OctoPrint with a slicing plugin) runs a slicer beneath it and
   would make a print host a prerequisite for a slice, which the *G-code
   printer seam* record's first alternative rejects for the monitor. The
   file a slice makes is handed to that seam, which streams it and does not
   know which slicer made it.

2. **Slicers are modules behind one interface.** A module
   (`apothecary/slicer/modules/`) says what it slices (the technology, what
   it reads, what it writes), finds its program -- an environment variable,
   then the tools dir, then `PATH`; `none` means none -- reports its status,
   installs, states every setting with its origin and source, and turns a
   slice into steps: typed request → argv list → the slicer's documented
   files read. OrcaSlicer's command line is the first; another slicer is a
   module added, and the one used is the one asked for, else
   `APOTHECARY_SLICER`, else the printer's profile's.

3. **The installer fetches a pinned release from its publisher and checks
   it before it is opened.** `apothecary slicer install` fetches OrcaSlicer's
   release for the machine from its GitHub releases into the tools dir: on
   Linux the AppImage (run as it is, or extracted where there is no FUSE),
   on macOS the application out of the universal disk image, on Windows the
   portable archive; another platform is refused, naming what is published.
   The release publishes no checksum file, so the installer reads the digest
   GitHub publishes for the asset, requires it to equal the SHA-256 pinned
   in code, and only then downloads, hashing as it streams. The version and
   its digests move together, and only in a commit that re-runs a real
   install and a slice.

4. **A printer's profile is kept with the printer's part.** printer_1's is
   `parts/ender3/slicer.json`. It names the slicer's own vendor profiles it
   starts from -- read from the installed release at each slice, none copied
   into the repository -- and holds what the bench measured, each value with
   its source. What the bench measured but the slicer must not apply is held
   and marked so: the probe's offset, which the firmware applies when it
   homes, and the bed's unevenness. The start of a print is composed from
   modules the profile names (`start.modules`): it homes and levels
   nothing, and using the stored mesh, probing each print and a measured
   first-layer offset are stubs.

5. **Print settings come from the part, the printer's fill the rest.** A
   part's declared print settings are mapped onto the slicer's, and every
   value in a slice says whether it came from the part, the printer's
   profile or the slicer's base. A declaration the printer cannot honour is
   refused (a nozzle it does not have). A made piece declares nothing yet,
   and a vocabulary word declaring settings for the pieces made as it is a
   stub; the printer's filament is its one filament, and choosing another is
   a stub.

6. **A slice is a background task, and every slice is kept.** `POST
   /slicer/slice` returns a task, polled as firmware tasks are, cancelled by
   stopping the slicer's process group; one slice runs at a time. The G-code
   goes where the Print card's file box keeps a file, checked as an upload
   is, so Print follows Slice. Each slice is a file of its own until a
   person forgets it there; its record -- what was sliced, for which
   printer, every setting and its source, the slicer's own estimate, its
   messages by line -- lasts as long as the file. The command line slices a
   library part itself, and a made piece through the running server.

7. **A slice reaches no host and opens no port.** The slicer runs with a
   data folder of the slice's own; a traced slice looked up no name, opened
   no socket and wrote only under the state folder. Its install reaches the
   GitHub release hosts alone, through the one tool fetch the *personal data
   stays on the device* record allows. Slicing writes files; sending one to
   the printer is the printer seam's, after a person presses Print.

## Consequences

- The loop from a picture to a print stays in the page; a person needs no
  slicer of their own for a printer apothecary knows.
- A third external binary is run under the copyleft clause's
  invoked-not-linked disposition. Nothing of OrcaSlicer's is committed or
  conveyed: the person's own machine fetches it from its publisher, and the
  profile only names OrcaSlicer's profiles. Committing a flattened copy of
  one, or bundling the binary, would change that and comes back here first.
- The profile carries the bench's measurements with their sources, so a
  value that drifts from the machine is visible where it is kept.
- The install is large and its pins move by hand; a bump costs a real
  install and a slice, on purpose.
- The macOS and Windows installs are held by tests with fakes until a
  person runs them; on Windows the slicer is a windowed program, so its
  version is read from the executable when it prints none to a pipe.

## Alternatives considered

1. **The person slices elsewhere** -- it keeps apothecary small, but the
   loop leaves the page at its last step, and the printer apothecary has
   measured is described twice, once in the person's slicer.
2. **PrusaSlicer's command line** -- mature and documented, AGPL-3.0 as
   OrcaSlicer is, with Creality's Ender-3 among its vendor profiles. It lost
   on how it is published: its GitHub release (2.9.6) carries a Windows
   installer and archive and a macOS disk image and no Linux build, which
   it publishes on Flathub instead. Installing it on Linux would mean
   driving flatpak, a second package manager fetching from its own remote
   outside the one tool fetch the *Personal data stays on the device, by
   construction* record allows, where OrcaSlicer's one release (2.4.2)
   carries AppImages for Linux x86_64 and arm64, a universal macOS disk
   image and portable archives for Windows x64 and arm64, from one host. A
   reader who weighs PrusaSlicer's command line above that would choose it,
   and the module interface keeps it a module away.
3. **CuraEngine** -- the engine alone, needing Cura's printer definitions
   assembled by hand and no single configuration file; the most work to
   drive well.
4. **The slicer's own profiles as they ship** -- simplest, but nothing the
   bench measured would reach the G-code.
5. **A person's own exported profiles** -- matches how a person already prints,
   but keeps the printer's description outside the repository and its
   review.

## Revision triggers

- OrcaSlicer relicenses off an OSI licence, is archived, or goes twelve
  months without a release -- the open-license record's clock starts; the
  module interface makes the swap a module.
- OrcaSlicer's command line or profile format changes so a pinned bump no
  longer slices -- the bump waits, and the module changes with it.
- A second printer, or a second slicer module, is added -- §2 and §4 are
  re-read against it.
- A stub in §4 or §5 is built -- it is named here as a module that is
  chosen, with its source.
- The slicer is run anywhere but the person's own machine -- AGPL-3.0 §13
  is re-read before that ships.

## Amendments

*None.*
