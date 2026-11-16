# OpenSCAD runs at once: the timing behind two

*The timing behind `OPENSCAD_RUNS = 2` in
`apothecary/projects/parts/stl_renderer.py`, the default number of OpenSCAD
runs that go at once ([openscad.md](../../../../docs/openscad.md#how-many-run-at-once)). It
was recorded in a comment beside the number when the queue was built, in
commit `b4b667e` (2026-10-12), and is kept here as it was recorded.*

On a four-core machine:

| Renders at once | Each one's time, against one alone |
|---|---|
| 1 | as long |
| 2 | a sixth to a third longer |
| 4 | nearly twice as long |

What a person waits for is their newest render, and every run beside it makes
it later; two still let a check go beside a render, or a check's two exports
go together. A machine with a single core runs one. `APOTHECARY_OPENSCAD_RUNS`
sets another number.
