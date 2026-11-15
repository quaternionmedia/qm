# A part through the subtractive loop, design to monitoring: a plan

*Slice 1 is built on this branch: a part declares the cuts that make it from
its stock, the app writes the router's toolpath from them, the toolpath is kept
and cut from the router's Machine, the job names the cut it is in, and the
simulated router keeps where the tool went, so a cut is measured against its
design and the design changed and cut again
(`walkthrough/20-a-part-through-the-router.md`, `docs/cam.md`). The rest is
not built; its next step is the real router at the bench.*

## What this plans

Apothecary's loop so far is additive: a picture or a parameter becomes a part,
a slicer turns the part into G-code, the printer prints it, its polls are kept
as evidence and the print is watched in the Working space. The router drawn
beside the printer (`docs/cnc.md`) is driven the same way, but the loop stops
at its door: a cut is a file a CAM post wrote elsewhere, and nothing here turns
a part into one.

This plan makes the subtractive loop whole, the same stations as the additive
one, each a step of the page, and makes it the loop the app is built around:

| Station | Additive, as built | Subtractive, this plan |
|---|---|---|
| Design | a part's parameters and SCAD, variants in git | the same part, and the cuts that make it from its stock |
| Toolpath | a slicer module, its profile, a slice record | the app's own toolpath from the part's cuts, a cut record |
| The job | Print from here, the job registry, the record | Cut from here, the same registry, the same record |
| Monitoring | polls, evidence, the Working space's hour | polls and evidence as built, the cut's own operation named |
| Measure | the printed piece against the design, by hand | the tool's path kept, as cut against as designed |
| Iterate | the part edited, sliced and printed again | the part edited, its toolpath written and cut again |

### Why the app's focus

A printer takes a sliced file and asks nothing back; everything a person
decides was decided before the slice. A router asks at every station: what
the stock is and where its zero stands, which tool, how deep a pass, where the
tabs go, whether the hole is the tool's size, what the controller is in when
it stops. That is where a design is iterated, and it is what this app is for:
every value with where it came from, every step a step of the page, the
machine's own words kept. The additive loop stays as built; the subtractive
one is where the next slices go.

## What exists

- The router as a part, its node, its stand and its controller
  (`parts/anolex_4060_evo_ultra_2`, `apothecary/example_hierarchy.py`).
- GRBL's dialect of the machine seam: identify, poll, bounded controls, the
  realtime characters, a cut streamed with the planner's room counted, the
  simulated controller (`apothecary/firmware/grbl.py`, `dialects.py`).
- The router's Machine in the page: Status, the pad, Cut from here, the log
  with the dialect's words, the badge and the marks
  (`apothecary/static/widgets/machine.js`, `docs/cnc.md`).
- The job registry's `cut` on a `router`, the job record, the evidence
  observations a router's poll makes (`apothecary/jobs.py`,
  `apothecary/evidence/printers.py`).
- The additive loop to mirror: the slicer's service, record and page step
  (`apothecary/slicer/`, `walkthrough/03-a-picture-to-a-print.md`).

## What is missing, by slice

### Slice 1: a part through the router, simulated (built)

- **A part says its cuts.** A part wrapper may declare, beside its geometry,
  the stock it is cut from and the 2.5D operations that make it: a pocket, a
  hole, the outline. The first such part is `parts/router_coupon`, a plate
  with a pocket and holes, its sizes parameters as any part's are.
- **The toolpath.** `apothecary/cam/` writes GRBL G-code from the cuts with
  one tool, the maker's feeds as bounds, a depth per pass, a safe height and
  the work zero at the stock's corner: pockets by rectangles inset from the
  wall by the tool's radius, holes bored in circles or plunged when they are
  the tool's size, the outline cut around in passes. A hole smaller than the
  tool is said and bored to the tool: the kind of fact a cut gives back to a
  design. The toolpath is checked as any streamed file is, kept where the
  Cut card keeps a file, and recorded beside it: tool, feeds, stock,
  operations, length, the estimate, what it refused.
- **The step of the page.** A router's Cut card has Toolpath where a
  printer's has Slice: what is chosen under makes gets its toolpath written
  for this router, kept and chosen, so ▶ Cut follows. A part's ring offers
  Toolpath when a router is pinned in the site, as Slice is offered for a
  printer.
- **The cut names its operation.** A streamed cut's lines carry the
  operation they belong to; the job says which it is in, and the Machine's
  progress line shows it beside the percentage.
- **As cut.** The simulated router keeps every move the tool makes below the
  stock's top, so a cut has a footprint to measure: the pocket as cut against
  the pocket as designed, the holes as bored.
- **One iteration, executed.** Walkthrough page 20 designs the coupon, writes
  its toolpath, cuts it on the simulated router, reads the job and the polls,
  measures the cut against the design, changes a parameter and cuts again.

### Slice 2: the bench

- The real controller answers the seam: section I of
  `project/bench-checklist.md`, its first replies kept as the Ender's are.
- A real cut of the coupon, its measurement by calipers kept as an
  observation beside the simulated footprint, and the stock's zero probed.
- Tabs on the outline, so a cut-out part is held; a climb or conventional
  choice; a second tool.

### Slice 3: the cut watched

- The Working space's hour for a router: its polls, the frames a camera
  over the table keeps with them, the cut's operation beside each.
- A camera's picture of the cut part read through a pinned face, as a
  photographed piece is, measured against the design.

### Not in this plan

- Three-axis surfacing from a mesh, or any toolpath from geometry rather than
  from a part's declared cuts.
- The controller's own web page, its SD card or WiFi: the seam is serial.
- A CAM post's file is still taken as it is; nothing here reads one back
  into operations.
