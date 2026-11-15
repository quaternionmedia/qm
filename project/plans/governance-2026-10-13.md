# Apothecary's governance and audit documents, brought up to the corpus

*An audit on 2026-10-12 read apothecary against what the Quaternion Media
corpus expects of an adopting project: the project's branch of the corpus
and its pin, the seed's copies in this repository, the commit and pull
request conventions, and the draft records in qm#121 against the code at
the top of the stack. Decided with the owner one question at a time on
2026-10-13. Plans are dated and exempt from the durable-text rule.*

## What the audit found

- The personal-data record names install points for the network guard
  (the server, the command line and the packages that read personal data)
  and says the geometry library installs nothing; the code installs the
  guard on `import apothecary`, and a test holds that.
- The G-code printer seam describes a serial engine that is gone; the
  firmware seam's own size trigger has fired; the one-screen and rad
  records quote census figures and pages that have moved on; the slicer
  record's second alternative gives no reason of its own.
- The adoption scope's audit has no conflict table and leaves out Pillow,
  pyserial, the vendored three.js and CodeMirror, the Rust crates and the
  gridfinity submodule; two runtime dependencies declare licences SPDX does
  not approve as written (Pillow's `MIT-CMU`, typing_extensions'
  `PSF-2.0`); the licence gate covers Python packages only.
- The record index fails the corpus's current lint, and the project's
  branch of the corpus is far behind its main; the seed's copies here
  match the pin's seed, not the current one.
- The bench board's USB serial number and some home paths are committed.
- A stacked pull request was marked ready.
- No hardware run is on record for the printer's heat, motion, streaming,
  pause, cancel and emergency stop, or for the Rust flash.

## Decided

- **The record is right about the guard; the code moves.** The guard is
  installed by the record's install points; `import apothecary` alone
  installs nothing, so a program using the geometry library keeps its
  network. The test that holds the opposite is inverted, with a
  fresh-interpreter check per install point.
- **Pillow and typing_extensions are conflict rows** in the adoption scope,
  not exceptions: the open-licence record admits no local exception, and a
  row records a conflict without waiving it. They stay until an alternative
  is good enough to replace them; a research effort into alternatives is
  stubbed (below).
- **The Rust and JavaScript licence gap is a conflict row** in the adoption
  scope, with the trigger that ends it: a second Rust sketch, a
  crate or a vendored library outside the allowlist, or the corpus's own
  gate for them.
- **The board serial and home paths are removed going forward**, replaced
  by placeholders; history keeps the old text. The seed's leak check runs
  in CI so new ones are refused.
- **Only the bottom of the stack is ready**; every stacked pull request is a
  draft and becomes ready when the one below merges. The seed's one-PR
  check runs in CI.
- **The owner runs the bench checklist** on the Ender and the ESP32; the
  records stand as written and are confirmed by that run. The checklist is
  made present tense and current for the page as it is.

## Work

- **In this repository**: the guard's install points and their tests; the
  serial and paths replaced; the leak and one-PR checks wired in; the
  bench checklist made present tense (`project/bench-checklist.md`); the
  research stub below. The seed's copies and the pin move after the
  corpus's propagation, below.
- **In the corpus (qm)**: #121's records rewritten in place to match the
  code and these decisions -- the conflict table and the full audit table
  in the adoption scope, with both conflict rows; the G-code seam without its
  removed engine; the firmware seam's size re-examined; the one-screen and
  rad records naming `apothecary census` rather than quoting it; the
  slicer record's alternatives; the index passing the current lint. Then the
  seed refresh and the propagation into `project/apothecary`, in the order
  the corpus's one-pull-request-per-slot rule allows, and the pin bump here.

## Stubbed: pictures without Pillow

Pillow reads, writes and resizes every picture: the photo finder, the
gathering, the made pieces' textures. A research effort is to find whether
an approved-licence alternative covers what apothecary uses -- decoding
JPEG and PNG, resizing, pixel access -- at the same quality and speed, and
what moving would cost. Until it reports, Pillow stays, a conflict row in
the adoption scope.
