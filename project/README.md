# apothecary — what it plans, and what was found

`project/` holds what this project plans and what was found of it, beside
[`adr/`](../adr/README.md), which holds what it decided. The application's own
repository holds the application: its code, its reference documentation and its
walkthrough.

A path written `project/...` is this branch's. Any other path a page here names, and
every link that leaves this folder, is the application repository's, and holds where
this branch stands at `governance/qm` in a clone of it.

| | |
|---|---|
| [ROADMAP.md](ROADMAP.md) | What apothecary claims is built, in the order to take it, each line naming the journey or the walkthrough pages that show it. `qmcp tour` reads it beside the running application's journeys and the feedback kept on each stage. |
| [todo.md](todo.md) | What is open: each item what is left of something built, or a plan not started. |

## The checklists

What is ticked by a person before a stack is pulled and before a tag is cut. The
suites hold everything else.

| Checklist | |
|---|---|
| [The integration checklist](integration-checklist.md) | A stack, before it is pulled: the tree that will land, the suite once on its head, the pictures judged, the docs read together, preflight, the rows only a person sees, the pull requests and the landing |
| [The bench checklist](bench-checklist.md) | The Ender 3, an ESP32 and the router for real: pinning, the link, heat, motion, levelling, printing from here, slicing, the emergency stop, the Rust and Arduino blinks, and the router's homing, jogs, spindle, zero, probe and a cut |
| [The models checklist](models-checklist.md) | Image models through qmcp by hand, against the simulated qmcp: the Models window, asking about a shape, a person's word, switching an origin off, and each way qmcp can be missing |

## Plans

Open plans: each says what is decided and what is not built.

| Page | |
|---|---|
| [A whiteboard to a model, and round again](plans/whiteboard-loop-2026-11-09.md) | A drawing in marker as a way in, the fifth loop and a heads-up layer towards designing for making: writing and diagrams sorted apart, a person's word kept at every step, the whiteboard a part of the site, a photograph squared and laid in front of it, cuts, notes with a way out to qmcp and looksatwords, round again, and the whiteboard's history scrubbed and placed elsewhere; every slice built ([walkthrough 30](../../../walkthrough/30-a-whiteboard-round-twice-through-the-page.md)), what it leaves named |
| [Integrating the local stacks](plans/integration-2026-11-07.md) | Every local stack cut from `main` at 1e12ec58 -- testing, the fixes, standardize, homing, family, streamdeck -- finished, merged in landing order into one tree, tested once as a whole by the integration checklist, its owed fixes taken home, and landed, its push priced before it is made: the phases, the conflicts found and each one's resolution, and what only the bench shows |
| [One way of doing each thing](plans/standardization-2026-11-07.md) | What the package does two ways and the one standard each folds into: a dialect's rules in its own module, one module for the state folder, one finder for every bought engine, a board by its part, a kind of machine from its dialect; in slices, three of them removals, each approved before it was built; what is left, named with its reason |
| [Journeys: window sets and a rail of steps](plans/journeys-2026-11-11.md) | A path through the page held as one: the windows it passes through laid out together as a view, and a numbered rail of its steps in the header, the step a person is on filled and Next naming the one after, taken from codecartographer's step rail and alfred's stage rail; *Print a part on a machine* first, Choose, Shape, Slice, See, Print; in slices |
| [The family's journeys through the viewer](plans/family-journeys-2026-11-07.md) | The page shaped round the paths through the family's work: the sentences telling a person what to do gone, a control surfacing when what it needs holds, a procedure's step and a member each a door to the window its work is in, and the family one focused system with a view of its own; in four slices, each a branch |
| [The Stream Deck + at the bench](plans/stream-deck-2026-11-07.md) | An Elgato Stream Deck + three ways: a part on the garage's workbench from the maker's figures, a device programmed from here (its keys and strip drawn, its presses, turns and touches heard, through a module beside Arduino's and Rust's and a simulated deck the demo shows), and a controller whose knobs jog the chosen machine's axes through the control latch, the dialect's bounds and its own stop; in slices, with the questions it decided |
| [Each machine keeps its own](plans/machine-identity-2026-11-07.md) | One answer to which board is on a port and what kind of machine it is; every record and cache keyed by it, a port that changes hands forgetting its board, one kind's work refused on another at the server, and the stop always sent; in slices: the stop, the port's forgetting, readings by board, pins by board, files by kind and machines planned before their board built; the page's marks by board not |
| [A part through the subtractive loop](plans/subtractive-loop-2026-11-04.md) | The loop the app is built around from here, on the router beside the Ender: a part's declared cuts, the app's own toolpath, Cut from here, the cut's operation named, the simulated router's footprint measured and one iteration executed (built); then the bench, then the cut watched |
| [Pictures in the world: what is open](plans/pictures-the-rest-2026-10-13.md) | Gathering out of core as an extra, and the old photo routes closed: the two phases of the pictures plan not built |
| [The shape finder, with a model behind it](plans/photo-finders-local-models-2026-09-21.md) | Optional local models behind the photo finder: the seam, the plugin shape, what reach is lawful, the phases |
| [Image models through qmcp](plans/image-models-through-qmcp-2026-10-30.md) | Image models as an always-optional source of measurements, served by qmcp on this machine: the vision tools' contract, observations beside the plain readers' and never over a person's word, how each degrades, which come first and how each is measured, qmcp's own slice, the records and the owner's questions |
| [Iterating on a part, tightened](plans/part-iteration-2026-10-12.md) | The part and SCAD loops reviewed and timed, and this round built: errors as failed renders, real controls, kept work, OpenSCAD's keys, variants drawn where they stand, history, compare, variant management; its next phase written out |
| [Governance, brought up to the corpus](plans/governance-2026-10-13.md) | The audit of apothecary's governance and audit documents against the corpus, and what is decided: the guard's install points, licence conflict rows, the serial removed, drafts, the bench checklist |
| [Reviewed: the systems, the tests and the docs](plans/review-2026-10-24.md) | The whole read once for gaps at the top of the stack: safety, the code's shape, what the tests run and where, their duplication and time, the docs against the page, and what stands on origin; each gap with its evidence and a next step |
| [A review cycle at ten times the requests](plans/review-cycle-2026-10-24.md) | How requests are reviewed and landed, measured, and a proposed cycle that holds at ten times as many: machines gate a request and its author merges it, a merge queue tests batches once, releases are reviewed by area at a tag, stacks stay shallow, shared files are split |
| [Focused systems](plans/focused-systems-2026-10-22.md) | The Airgap as the standard for a focused layout, the Part and the Machine on it, one registry every system is configured through, and Board, Lighting, Fit and build and Bench after them |
| [The documentation, swept](plans/timeless-docs-2026-10-12.md) | Every durable text brought under the governance record on durable text: present tense, no internal history, no ornament; the triage by area and the order; its notes on each area in [its folder](plans/timeless-docs-2026-10-12/) |
| [The bench as a rig carlos can draw](plans/qm-family-carlos-2026-10-29.md) | Carlos, in the instruments family, holding and drawing the bench as apothecary sees it: the bench written as a `carlos.patch` with each board's and lead's state and sent whenever it changes (built, with a demo), a picture naming a device, IO configuration, and carlos's one action |
| [A synth rig photographed through a concert, held in carlos](plans/carlos-concert-rig-2026-10-29.md) | Carlos's rigs, bolstered from apothecary: each knob, fader, switch and socket read off a camera's picture against carlos's own panels and held in carlos frame by frame through a concert, turned in place, with a test of both apps end to end (built, on drawn pictures); the first real photographs, power and USB into an Uno; then the airgap's test rig and a server room |
| [A working space, seen from every kind of evidence at once](plans/working-space-view-2026-10-30.md) | One view of a place (what is here, what state it is in, how it is known, what changed) from its cameras (one thing from several angles among them), ports and polls, sensors, a person's goals, directives and actions, and optional image models, every line opening its evidence and every disagreement kept; first the Ender's three cameras (on the bed for its timelapse, on the head, across the room) tied to its polls; not built |
| [One page for every effort](plans/ui-coordination-2026-10-31.md) | The viewer's windows, doors and words across the efforts in flight (the Working space, the image models, the rig's faces, the bench in carlos, lighting, pictures): where they collide, one observation module, and the order the collisions are settled in. |
| [An irl hub of ShowRunner's class](plans/irl-hub-2026-11-02.md) | Apothecary as hearth's second exemplar: a procedure of steps on a blueprint in place of a cue list on a script, each step's family block delivered over `family/1` to the printer, the boards and the cameras hosted in the hub and to carlos, joe with vox, alfred with otto, datum, ira and ShowRunner beside it, every outcome kept in the evidence log; each member's verbs, what it has and what it needs, the order of the work and the owner's questions; the hub, its machine and board members and the procedure are built ([the family's hub](../../../docs/family.md)), the rest is not |

## History

Plans and research that are finished, newest first. Each is a dated record
of what was decided and why; what is still true of it is stated in the
guides above, the governance records, or the code it describes. A plan
whose work is done leaves the table above for this list.

- 2026-11-04 — [One page for two machines](plans/ui-refresh-2026-11-04.md): the kinds' words in one module, one badge grammar, a section's title by kind, the card in the loop's order, the Working space on any machine, the palette in one sheet; what it left is in [project/todo.md](todo.md).
- 2026-10-20 — [Landing the stack on main](plans/landing-the-stack-2026-10-20.md): every open pull request and the governance records it pins, reviewed once as a whole and merged into `main` bottom first, the order checked by merging each branch in turn; what is still open of its *After* is in [project/todo.md](todo.md).
- 2026-10-10 — [A managed slicer](plans/slicer-2026-10-10.md): OrcaSlicer behind a slicer interface, installed like OpenSCAD, the printer's profile kept with its part, print settings from what each part declares.
- 2026-10-09 — [A Rust geometry kernel](plans/rust-geometry-kernels-2026-10-09.md): a survey of which Rust kernel could render scenes to STL without OpenSCAD -- Manifold bindings, csgrs, boolmesh, truck, Fornjot, OCCT -- by licence, build, coverage and maturity; Manifold's bindings first.
- 2026-10-08 — [The loops through the page](plans/ui-flows-2026-10-08.md): designing a part, editing its SCAD, firmware, and a picture to a print, each built out and held end to end by a browser test.
- 2026-10-08 — [Rust](plans/rust-2026-10-08.md): firmware in Rust for the ESP32 behind modular toolchains, a Rust geometry kernel researched and compared by numbers, a Rust service and core stubbed.
- 2026-10-04 — [Cameras and clutter](plans/cameras-and-clutter-2026-10-04.md): a camera as a part of the site, pictures sized and taken from it, and less on the screen (icon badges, the Machine in the rail, one header row, faded walls).
- 2026-10-03 — [Consolidation](plans/consolidation-2026-10-03.md): one page and one place per thing; Site and Selected over a strip of tabs, one Machine per board, the Bench, one Pictures panel, jobs over machine kinds.
- 2026-09-27 — [Designing a part from the browser](plans/part-editing-in-the-browser-2026-09-27.md): a spike measuring the part loop, OpenSCAD 2021.01 against a Manifold snapshot, and what other tools do; fast renders, parameters from the SCAD, then an editor in the page.
- 2026-09-26 — [Pictures in the world](plans/pictures-in-the-world-2026-09-26.md): a picture pinned at a place as a view, its shapes made into pieces standing there, every surface of the camera panel given a home in the world (Phases 0 and 2 to 4; Phases 1 and 7 continue in [what is open](plans/pictures-the-rest-2026-10-13.md)).
- 2026-09-20 — [One screen](plans/one-screen-2026-09-20.md): the world as the one page, with anchors and panels in front of it, and the census as the meter.

### Records from the bench

- 2026-11-14 — [What was said of the tour](validation/2026-11-14-what-was-said-of-the-tour.md): the five words given in the tour's box while it still took the roadmap's lines, as they were kept, and what came of each.
- 2026-11-07 — [The garage's two machines, read from what is recorded](validation/2026-11-07-machine-setup.md): where the relief the viewer lays over the router comes from, the Ender's stored mesh against its probes, the router's settings never read and what each decides, and the boxes the bench needs.
- 2026-11-05 — [The family started through the hub](validation/2026-11-05-family-started.md): one procedure with a step for every member, carlos and joe real and started by the hub, what each did and what running it found.
- 2026-11-05 — [Family integrations](validation/2026-11-05-family-integrations.md): how each family member's seam with apothecary stands, each checked against the member itself.
- 2026-11-03 — [The router walked in the demo](validation/2026-11-03-router-walk.md): the AnoleX 4060-Evo Ultra 2's Machine, pad, cut and stop against the simulated controller, step by step, each step approved from its picture and the live page, and what the walk changed.
- 2026-10-12 — [OpenSCAD runs at once](validation/2026-10-12-openscad-runs-at-once.md): the timing behind the queue's default of two.
- 2026-10-11 — [Walkthrough picture drift](validation/2026-10-11-walkthrough-picture-drift.md): how far two runs' pictures differ, behind CI's tolerance.
- 2026-10-10 — [What the installs reach](validation/2026-10-10-what-the-installs-reach.md): the hosts the Rust and slicer installs reached under strace, and that a build and a slice reach none.
- 2026-09-21 — [Local integration run-through](validation/2026-09-21-local-integration.md): a checklist for the review branch, section by section.
- 2026-09-20 — [Ender bench](validation/2026-09-20-ender-bench.md): the printer seam against a real Marlin board, and what the bed measured.
- 2026-08-28 — [Gathering thresholds](validation/2026-08-28-gathering-thresholds.md): what the gathering's and the finder's thresholds were measured at.
