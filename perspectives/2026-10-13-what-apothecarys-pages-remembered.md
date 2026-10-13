# What apothecary's pages remembered — 2026-10-13

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-13 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, in Claude Code, drafted from the sweep's notes |

`apothecary`'s top-level and reference pages -- the README, the contributor
and agent guides, `todo.md`, `docs/`, and the parts' and crates' READMEs --
were swept under `records/DRAFT-durable-text-states-what-is-true.md` in
quaternionmedia/apothecary#40, #42, #43 and #45. Most of what they said was
already in the present tense, and most of their history was a clause with no
lesson in it -- "today", "yet", "as before", "as it always was" -- which was
deleted. This page keeps the few stories worth keeping. Each was read at
`apothecary` `bdc0636`, the sweep's base, and checked against that
repository's history. The stories the package's docstrings carried are in
`2026-10-13-what-apothecarys-package-remembered.md` and
`2026-10-13-what-apothecarys-pictures-packages-remembered.md`.

## A part's values moved into its text

A part's values first reached OpenSCAD on the side, as `-D` definitions, and
the first saved variants (2026-10-10) committed their parameters as
`<stem>.variant.json` beside the SCAD. A merge of a variant's ref brought its
SCAD into the part and not its values. The same day, the SCAD editor took the
place in Selected where the part's source had been shown read-only, so the
page held two descriptions of one part: the controls' values, sent on the
side, and the text in the editor.

On 2026-10-12 the owner decided, in the part-iteration plan's "parameters and
text, tied together", that a control rewrites its parameter's line, a line
moves its control, and nothing is passed to OpenSCAD on the side for a part
whose SCAD the page edits. A save now writes the text alone. A variant saved
before that is still read: its values are written into its text when it is
read, listed or compared, and the merge advice says a merge does not apply
them until the variant is saved again.

The pages lagged the code by a day. At the sweep's base `docs/parts-authoring.md`
still said a save committed the parameters as `<stem>.variant.json`, which
the sweep's first step corrected as a statement the code contradicted, and
`docs/viewer.md` named the older variants by their past ("saved before its
values were in its text") rather than by where their values are. Two
descriptions of one value drift apart; the text is now the only one, and the
part's model is its check.

## A planned item with no plan

README's OpenSCAD list said Windows on ARM "is not supported yet; it is a
planned item", and the installer's docstring and its refusal said the
same. No plan listed it and no line of `todo.md` did. Its only trace
was the last line of the local-integration validation record's *Hardening,
after this branch* list (2026-09-21), "One day: Windows on ARM, natively",
and `todo.md` carried none of that list. A reader told that something is
planned takes it that somebody is tracking it. `docs/openscad.md` now says
the platform is refused and how to name an OpenSCAD installed another way,
and `todo.md` holds the installer's hardening as open work.

## A page that was half a proposal

`docs/fitting-a-part.md` was written on 2026-08-20 against `datum`, the
consumer the enclosure parts were drawn for. It was both the reference for
the seam between a project that owns facts about a physical thing and
`apothecary`, which owns geometry, and a proposal that said so: "Status:
proposed; a record candidate for governance/qm, not yet drafted there." Its
*The line* -- the consumer owns requirements and interfaces, `apothecary`
owns realization and manufacturability -- and five rules stood beside the
built half from then until the sweep, and no record was drafted. A reader
could not tell which sentences said what the code does and which said what
somebody wanted it to do.

The sweep kept the built half: the three objects and their ladder, the
black-box seam, a gate for each pair of descriptions, the pin, and the owner
of each open problem. Whether the proposal becomes a draft record is put to
the owner, and the page's previous version in `apothecary`'s history holds
its text.

## What the dated plans already hold

Three more stories left the pages and need no retelling here, because a dated
plan in `apothecary`'s `docs/plans/` is already their account:

- **The firmware seam.** It began as arduino-cli alone. The Rust plan,
  decided on 2026-10-08, made each toolchain a module (2026-10-09), and
  `/firmware/status` kept Arduino's fields at its top level beside the new
  list of toolchains. A print was a record of its own until the owner
  decided on 2026-10-03 that a print is a job, one operation a machine
  performs on a part; a record kept before then is read as a job.
- **The slicer.** It was decided with the owner one question at a time on
  2026-10-10, and its page was written after the build to say what had been
  built.
- **The Rust crates.** The same plan stubbed a core library and a service
  (2026-10-09) so that the workspace and its checks were settled before
  either did anything, and both READMEs opened on "Not built yet".
