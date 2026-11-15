# TODO

Part readiness, bounds drift and contested values are computed, not listed
here: run `apothecary problems`.

## Open in this repository

- JSCAD: generated modules import `@jscad/modeling/src/*` deep paths.
  `node --check` passes, but no test loads a module against the package.
- Packaging: the wheel ships `apothecary/` only. `parts/` and `templates/` are
  not in it, so an installed wheel cannot render a part.
- Pictures in the world, what is open: Phase 7, the old photo routes closed,
  after gathering leaves core (*Next round*):
  [project/plans/pictures-the-rest-2026-10-13.md](plans/pictures-the-rest-2026-10-13.md).
- A whiteboard to a model, what is left: the sorter leaning on a marker's colour, a camera aimed at a whiteboard, a note's words read freely through qmcp, and a whiteboard's history kept across a restart: [project/plans/whiteboard-loop-2026-11-09.md](plans/whiteboard-loop-2026-11-09.md#what-it-leaves).
- Optional local models behind the shape finder: [project/plans/photo-finders-local-models-2026-09-21.md](plans/photo-finders-local-models-2026-09-21.md).
- Image models as an optional source of measurements, through qmcp over MCP and only when a person asks: quantity, size, shape, material, colour, a label, a cover and a match in another camera's picture, as observations in the family's format beside the plain readers' and never over a person's word, with qmcp's own slice (MCP on its server, the vision tools, the weights fetched from a pinned list) in its repository: [project/plans/image-models-through-qmcp-2026-10-30.md](plans/image-models-through-qmcp-2026-10-30.md). A prototype of the journeys against a simulated qmcp is built (the Models window); [project/models-checklist.md](models-checklist.md) is what a person validates by hand.
- A stack's tabs drawn out of its layout's order: the vendored GoldenLayout 2.6.0 puts a tab back from a stack's ▾ list at the end of its row (`ts/controls/tabs-container.js`, `tryUpdateTabSizes`), not at its place, so a stack can show a tab where its layout does not hold it, and a reload draws the layout's order ([walkthrough 33](../../../walkthrough/33-windows-kept-over-a-reload.md), step 2). The vendored copy carries no local change; patching it, or putting the tabs back in order from `panels.js`, is the owner's choice.
- The tour, what it leaves ([docs/tour.md](../../../docs/tour.md)): a state only a fault brings (a quiet board, a router in alarm) is at its stage as a step to read, and the page is not taken to it; a camera's picture needs the browser's camera, so pages 01 to 03 go through it and no stage does; an assembly stepped into is a page and not yet a stage; seven of the eight journeys have no cell on the ring, whose Panels › Windows is full, and are entered from ⊞ Windows › Journeys; the box stands over the world, so what a stage frames can lie under it until it is dragged; Pin, and each journey's Choose, name no step to try; the command line is in no stage of its own (a part that does not load, a found tool with no version, a sketch built); a name typed into the box is not checked, so one person can give a word under another's; and a board found by its sketch and not connected is said to be "pinned to a board".
- The Models window, what its walk left ([project/models-checklist.md](models-checklist.md)): a person's word is kept by Models in memory, where the Working space should keep it and Models offer it; and the status bar keeps "choose a shape … first" in red after a shape is chosen, until the next action.
- A synth rig photographed through a concert, held in carlos: the first real photographs, the Ender's mainboard's power and USB through the camera aimed at the Ender, waiting for that camera (slice 4, rehearsed on an Uno's drawn pictures: `examples/rigs/uno-power-and-usb.json`, `apothecary rig setup`), then the DFAM and Subharmonicon, then the viewer's window for pinning faces, cues in the record, a mount and corner tabs printed; then the airgap's test rig and a server room: [project/plans/carlos-concert-rig-2026-10-29.md](plans/carlos-concert-rig-2026-10-29.md).
- The viewer across the efforts in flight, one observation module first, then the words and seats: [project/plans/ui-coordination-2026-10-31.md](plans/ui-coordination-2026-10-31.md).
- An irl hub of ShowRunner's class: apothecary as hearth's second exemplar, a
  procedure of steps on the blueprint in place of a cue list on a script, the
  machines, the boards and the cameras hosted in it and carlos, joe with vox,
  alfred with otto, datum, ira and ShowRunner reached beside it, every outcome
  kept in the evidence log; the hub, its machine and board members, the procedure
  fired step by step through it and the members it starts beside itself are built,
  the owner's questions open:
  [project/plans/irl-hub-2026-11-02.md](plans/irl-hub-2026-11-02.md).
- Carlos and joe in the family: each keeps `family/1` on its branch (carlos's
  `feat/hold-the-rig`, joe's `feat/family-control`), `hearth check` passes each and the
  hub's audit names the instance that took a delivery
  ([the first run](validation/2026-11-05-family-started.md)). Open around them: joe's
  branch has no pull request and carries three lines of work over its main
  (`docs/walkthrough`, `feat/family-demo-contract`, the family routes); joe's routes sit
  behind a capability, `JOE_ALLOW_FAMILY=1`, and a table's `start` has no environment
  field, so its command begins with `env`; a follower on joe's `/family/events` holds its
  stop open and a cross-site read of joe is refused by its guard; carlos's rack tab polls
  `/family/state` where `/family/events` streams; joe's `listen` and `say` are not started.
- A step answered 202 by a member beside the hub reads as fired for good: the hub could
  read that member's `/family/events`, as it reads a hosted member's state
  ([the first run](validation/2026-11-05-family-started.md)).
- What a port's record leaves open: a flash record kept before records named their board is
  still found by its port's name; a family home step on a port another board's record names is refused
  once, with nothing sent, and works on the next try; two identical converters swapped in
  one socket read as one board. None of it has met the real router or the real state file.
- `tests/e2e/durations.json` has no times for the browser tests the view banner added or
  renamed, so `--shard` balances without them until `apothecary test all --record-durations`.
- hearth's `web.router` declares GET and HEAD on one route, so FastAPI warns of duplicate
  operation ids at `/openapi.json`; the fix is hearth's.
- The reader as a hosted member of the irl hub, and a page reading the camera's actions
  ([project/plans/irl-hub-2026-11-02.md](plans/irl-hub-2026-11-02.md#order)).
- Waiting behind it, the bench as a rig carlos draws, slices 2 and 3 (a picture names a device, IO configuration): [project/plans/qm-family-carlos-2026-10-29.md](plans/qm-family-carlos-2026-10-29.md).
- A working space seen from every kind of evidence at once: its cameras, one thing from several angles among them, a printer's polls and a board's port, its sensors, a person's goals, directives and actions, and the image models' guesses, each line of the view opening its evidence. First the Ender's three cameras, on the bed for its timelapse, on the head and across the room, tied to its polls (frames kept with polls, then its lead, its motion and its bed seen two ways), then the rig through a concert, the airgap's test rig and a server room. Its first two steps are built and walked from each door in [walkthrough 18](../../../walkthrough/18-the-working-space.md); the next is the Ender's cameras at the bench: [project/plans/working-space-view-2026-10-30.md](plans/working-space-view-2026-10-30.md).
- Pictures lists every frame the Working space keeps with a poll as one of its camera's pictures, so a print fills it: those frames belong to the Working space, and Pictures would count them rather than tile them.
- Pictures without Pillow, a research effort: whether a library under an approved licence decodes JPEG and PNG, resizes and reads pixels as well and as fast as Pillow does here, and what moving would cost. Until it reports, Pillow stays, a conflict row in the adoption scope: [the governance plan's stub](plans/governance-2026-10-13.md#stubbed-pictures-without-pillow).
- The installers' hardening. A download is checked against its listed size
  and published SHA-256; not checked are the GPG `.asc` signatures beside
  OpenSCAD's and arduino-cli's downloads, the macOS app's code signature and
  Team ID, Windows Authenticode on `openscad.exe`, and a source build's
  tarballs (codeload publishes no checksum). A source build takes no nested
  submodules and no `.1` second build of a night. Windows on ARM is refused:
  no ARM64 snapshot is published.
- The footpedal on its board: section K of
  [project/bench-checklist.md](bench-checklist.md) has not been walked, so its
  build is known and its buttons' notes and the strip are not. It prints no
  `apothecary footpedal: hello`, since its serial line carries Hairless MIDI, so
  the made thing's Query hears its hello only from the scripted monitor of `serve --simulated`.
- The router at the bench. The AnoleX 4060-Evo Ultra 2 is drawn, its
  controller's dialect spoken and its Machine built against the simulated
  controller; the real controller has identified itself and nothing past that.
  Section I of [project/bench-checklist.md](bench-checklist.md) is what a person
  confirms there: what `$I` and `$$` say, whether its DTR resets the controller,
  which way it homes, and the bounds `apothecary/firmware/grbl.py` takes from the
  maker's figures. A toolpath has run on the simulated controller alone
  ([docs/cam.md](../../../docs/cam.md#not-built), [docs/cnc.md](../../../docs/cnc.md#not-built)).
- Following a running job along the previewed path: a job's lines sent map to a
  segment and the card does not use it yet; and a cut drawn as the tool's width, not
  its centre ([docs/toolpath-preview.md](../../../docs/toolpath-preview.md#not-built)).
- `tests/test_firmware_ports.py::test_listening_through_the_server_hears_the_hello_with_no_arduino_cli`
  listens a second time for one second on a stream that has already given the boot
  hello, so it needs the simulated devkit's tenth blink inside that second; on a machine
  loaded past its cores, as with `--workers` beside other runs, the blinks slow and the
  hello falls outside. It passes alone and in a serial run.
- `tests/e2e/test_one_machine.py::test_one_poller_per_board_whatever_draws_it` counts a
  board's status requests over four poll periods; on a machine loaded past its cores
  it counted three. It passes alone, and on a machine loaded below its cores.
- `apothecary preflight` on a stack not yet pushed reads signature-check as a defect:
  the workflow asks the forge (`--source host`), which has never been sent those
  commits. `apothecary/preflight.py`'s recorded differences could name it, covered here
  by `check_signatures.py --source git`.
- Page 06's picture of F5 comes in two forms from run to run: the SCAD editor at its
  left edge, or scrolled sideways, with the caret in view either way. Which one a run
  gets does not follow the commit, so a picture of it past the drift tolerance is not
  a change to the page.
- A check before a cut that its toolpath fits the travel from the work zero, in the
  Cut card, from the toolpath's recorded bounds and the controller's position: a cut
  zeroed too low or too high stops at its first move past the travel, with the
  spindle on (`ALARM:2`). It waits on the bench, which has not confirmed which way
  the machine homes (section I of [project/bench-checklist.md](bench-checklist.md)).
- What the round of unification left: the Machine's main window at full size (a
  person's call: doors are new controls, and opening as its view is against a
  tested decision), a cut's operation beside each poll in the Working space, and
  the as-cut measure in the Cut card:
  [project/plans/ui-refresh-2026-11-04.md](plans/ui-refresh-2026-11-04.md).
- A host-side bound on where the print head ends. Each jog's move is capped
  (`JOG_MAX_MM`), jogs one after another add up, and the firmware's soft
  endstops, after a homing, are what keeps the head on the machine
  ([docs/firmware.md](../../../docs/firmware.md)).
- Keyboard: the Contents tree's rows, carets and crumbs answer clicks alone.
  They are `li` and `span` elements with click listeners, and the canvas is
  the only element given a `tabindex`.
- The 2026-10-24 review's items not listed here
  ([project/plans/review-2026-10-24.md](plans/review-2026-10-24.md)): the
  four installers as one; the wrapper-import pattern; the example modules at
  the package root; a `docs/architecture.md`; the slowest browser file
  profiled, a marker on the order-dependent files, a JavaScript unit layer and the remaining
  `wait_for_timeout` calls.
- Starlette's test client warns that `httpx` is deprecated in favour of
  `httpx2` (seen at `conftest.py`'s import of `starlette.testclient`) once
  `httpx2` is not installed: move the test client to `httpx2`, or filter the
  warning where it is raised.
- The landing method has no command. A stack tested once on the tree `main`
  ends at ([CONTRIBUTING.md](../../../CONTRIBUTING.md)) is the
  [landing plan](plans/landing-the-stack-2026-10-20.md)'s `git
  merge-tree` loop, run by hand; and `apothecary test all` runs the unit part,
  then the browser files in file order, where the longest browser files first,
  beside the unit part, is the order that shortens a landing run.
- A phase's bound does not allow for a loaded machine: at a load of 12 on four
  cores the camera test (`test_docs_bench_walkthrough.py::test_the_bench_as_it_is`)
  ran 153 s against the 75 s it records, near the bound of twice the longest
  recorded test, so a little more load ends a run that is only slow.
- Walkthrough pictures that move with no change to the page: a full browser
  run rewrites a few by a few pixels (the masked clocks' shade, the SCAD
  editor's sideways scroll in page 06's), so a run leaves the tree changed.
  Such a run's pictures are not committed.
- Walkthrough picture 06-01 (taken on `main` in 3635934b) has a focus ring on
  the Cube size slider that two full browser runs of the stack above `main` no
  longer draw. No commit in the stack is found that explains it, so the picture
  stays as `main` has it until one is.
- A browser shard in CI was cancelled at its job's limit on #85's and #89's
  pushes with no test named. The browser suite runs in CI at a version tag
  alone, and none has run since; there, each phase's bound names a test that
  hangs.
- The walkthrough's lists, what their checks leave: a link's anchor is not checked,
  and the docs site's resolve test passes over a link into `generated/`.
- What a change reaches is read from import statements, so a helper named in
  `pytest_plugins`, loaded by importlib, `__import__` or its path, or read as text
  reaches no test; nor does a test or helper in a folder of tests/ other than
  e2e/, or a `.md` doctest under tests/. A changed test file does not run the
  checks that read every test file (`tests/test_e2e_helpers.py`, test_groups'
  one group per file), and `tests/e2e/durations.json`, which sets every test's
  bound, is no shared ground. None of these occurs in the suite today.
- The borders, what is open ([docs/boundaries.md](../../../docs/boundaries.md)):
  - `apothecary.firmware` holds the firmware toolchains, the machine seam (ports,
    Marlin, GRBL, a port's task) and the tool finder every installer uses; `slicer`,
    `cam`, `evidence` and `openscad_installer` depend on it for the last two.
  - What is cut can differ from what is drawn: `part_cuts` reads a variant's
    `params`, so an edit of its SCAD's body is drawn and not cut, and the router
    coupon's cuts restate its SCAD's 20 mm offsets as constants. No test compares
    a toolpath with the SCAD.
  - A router's travel has two sources: the page draws the tool at its position plus
    the node's build volume (the Machine card's volume is the Ender's until `where`
    answers), and the controller's own `$130`-`$132` are read by the table probe
    alone.
  - A variant is drawn on its `measured` box, off its envelope for a SCAD whose
    origin is not its corner. The fake OrcaSlicer ignores the model, so only the
    slicer's argv is tested.
  - A part's own STL: a slice of the part rebuilds it at its defaults and drops a
    CLI variant's sidecar, and `GET /parts/{name}/stl` does not say which
    parameters the file it serves holds.
  - The status listeners in `apothecary/api.py` act on loaded sites alone, where
    `where` reads every pin: a poll before the site is opened is not kept against
    its node.
  - A job's kind is chosen outside `apothecary/jobs.py`: `start_print` picks a cut
    by the machine's dialect, the upload route names `printer` and `router`, and
    the module's docstring says a mill registers `mill` where the code registers
    `cut` on a router.
  - Provenance ends at the kept file: a job names its slice or cut by a file id
    while the file is kept, a slice's record goes with its file, and a record names
    a cache key, not a saved variant's ref.
  - The simulated stand-ins say yes where the real tools say no: the scripted
    arduino-cli's devkit says hello by the uploaded folder's name, and the
    simulated Marlin answers `ok` to a line it does not script.
  - Four ways of finding a tool: `Tool.find` passes over a variable naming a
    missing file where OpenSCAD's variable is final; the tool status shape is
    defined twice; the Stream Deck's `ok` is "found", where `ModuleStatus.ok` says
    "can build and flash"; `finders/qmcp.py` names a qmcp extra `pyproject.toml`
    does not declare.
  - A cut asked for by port alone keeps its file under the port's name;
    `apothecary/cam/api.py` tells a `SlicerError` by its class's name; a node's path
    and a variant's key are matched by patterns written in three places.
- A part.json and a wrapper drop a key they do not know, unread, so a misspelt
  `display_rotation` (`displayRotation`) is ignored where the spelled one is
  refused; `extra="forbid"` on `Description`, `Provenance` and `BasePart` would
  refuse it, and no part.json in parts/ has a key they do not know. pydantic's
  calls that skip validators (`model_construct`, `model_copy`) and a subclass
  that declares the field get past it too.
- What `tests/test_cli_guidance.py` does not read: a wrong first word in prose
  ("until apothecary verify has passed"), the package's Python strings, a code
  span led by `python -m`, `.venv/bin/` or `$ `, AGENTS.md, `templates/*.md`, the
  tests' READMEs and the changelog, words after a command that takes none, a
  command joined from JS strings, and a word run on into `_` or `:`.

## Next round

Decided, not started. Each waits on what its line names.

- Photo gathering becomes an optional extra.
  `apothecary/gathering/` and its benches move behind
  `pip install apothecary[photos]` (`uv sync --extra photos` from a
  checkout), and `photo gather` names the extra when it is missing. How
  much of `apothecary/vision/` goes with it is settled then: the API's
  photo routes and `vocabulary/match.py` import from it.
  [Pictures in the world: what is open](plans/pictures-the-rest-2026-10-13.md)
  proposes an answer for a person to take or leave. The
  camera routes (`/sites/{s}/cameras`) and Pillow stay in core, because the
  bench walkthrough and `apothecary docs generate` use them. Split `gather` into steps only after
  the move.
- `api.py` into routers, with a lock on the site store; first a pure move,
  then the behaviour changes.
- The viewer template's inline script into modules, with the ring's verbs
  declared once (`data-action`) and a test that holds them.
- One registry for firmware ports. It drives real heaters and motion, so it
  lands with a bench session on the Ender
  ([project/bench-checklist.md](bench-checklist.md)).
- The unit suite under pytest-xdist.
- A licence gate for the Rust crates (the workspace's `Cargo.lock` and each Rust
  sketch's) and the vendored three.js and CodeMirror. `license-check.yml` gates
  Python packages alone; the rest is a conflict row in the adoption scope
  ([the governance plan](plans/governance-2026-10-13.md)). It ends, and the
  gate is built, at the first of: a second Rust sketch, a crate or a vendored
  library outside the allowlist, or the corpus's own gate for them.
- Photo gathering proposes and waits: `photo gather` lists what it would do
  and does nothing until a person says yes, as an image model is asked only
  when a person asks. A person's word already wins over a guess.
- A made piece saved as a variant: Save turns it into a part in the state
  folder, editable from then on, as the draft record *Personal data stays on
  the device* (§6) says. The page offers a made piece no Save now, and shows
  its SCAD read only.
- The review cycle in
  [project/plans/review-cycle-2026-10-24.md](plans/review-cycle-2026-10-24.md),
  taken as proposed: a merge queue tested once a batch, releases reviewed by
  area at a tag, shallow stacks, and the shared files split. The merge queue
  needs required checks, so it waits on `main`'s protection (*For a person to
  decide*).
- The hidden command stubs `apothecary/cli/retired.py` makes for the test
  command (`test setup-e2e`, `test validate-e2e`, `test run-e2e`) are removed
  one release after they were hidden.

## For a person to do

- Run [the bench checklist](bench-checklist.md) on the Ender and the
  ESP32: the governance records stand as written, confirmed by that run.
- Land apothecary's records in qm, in this order: qm#171 into
  `project/apothecary`; then qm#121 (seven records) merges
  `project/apothecary` in, keeping its own ADR list; qm#145 (the records
  address the charter by name) takes #121's text where they conflict; then
  qm#172, qm#197 and qm#211. Ratify the drafts proposed in #121 -- the
  firmware, G-code and slicer seams, one screen, rad host integration,
  personal data staying on the device, the adoption-scope amendment -- and
  move the `governance/qm` pin to `project/apothecary`'s tip, the pin alone
  in its commit. Until then the pin is `fb90ad4`, the head of #211's branch
  (`adr/apothecary-airgap-metrics`), which no other branch carries, so #211's
  branch stays.
- Propagate qm#226 (the seed's `AGENTS.md`, ADR index and editor settings
  read true in a project's copy) into `project/apothecary`: it is on qm's
  `main` and in no pin. Then copy the seed's `AGENTS.md` and `.vscode/`
  settings here again.
- Cut the first version tag. The browser suite, the Rust check, doc capture
  and the step-through tests run in CI there, and its run is the
  runtime-bound walkthrough pages' evidence (the walkthrough record's
  decision 7).
- Review rad#7 (a ring entered at an item); apothecary's ring follows what
  rad decides.

## For a person to decide

- Protect `main`? Not yet: the checks a merge waits on, the whole suite
  before a merge and the bot gate ([CONTRIBUTING.md](../../../CONTRIBUTING.md)) hold by
  convention. The review cycle's merge queue waits on it (*Next round*).
- Are the questions `photo gather --ask` ranks first the ones worth a minute?
  Only a person with a real folder of photographs can check.

## For governance/qm (file there)

- A run that goes green because tests were skipped reports success; nothing
  records what did not run.
- A green suite is not evidence until faults are injected and caught; no rule
  asks for it where a decision rests on a number.
- The plain-language proposal belongs there; its read-aloud check needs a
  second person. `git show 7c63846^:project/plans/proposals/light-language.md`
  prints it.
- A check that asks for credit to an address no human reads recurs on every
  change until the check changes or an exception is written.
- No rule says what information may leave for a project that sends data.
- Proposing a decision to a project has no category in the rulebook's list.
- *Personal data stays on the device* counts the one machine as the device,
  and a home cluster would be an amendment of its own. Storage, asking the
  video editor (alfred) for a frame, and any cluster deployment wait on the
  record's ratification.
- When keeping data on the device makes something impossible, neither
  building it badly nor leaving it out is the rule: each case is explored and
  its questions brought to the owner to reconcile. The same record could say
  so.
- A model's weights are a fetch of their own, not an install-time fetch: qmcp
  fetches them on a person's word, from a pinned list, and the host learns
  only what was fetched (the image-models plan's *Decided*). The same record
  names the download.
- The *Data retention* record, when drafted, settles where a person's answers
  about their photographs are kept and when one expires, with the other kinds
  of kept data. Until then they live in the file handed to `--answers`.
- A check that reads git trailers for credit (carlos's corpus pin, from
  qm#81's `seed/read-the-trailer`, not on qm's main) refuses `Tools: Claude
  Code` written as a commit's last paragraph, though the corpus names a
  `Tools:` note as how a tool is disclosed. It should tell a `Tools:` note from
  a byline before apothecary's pin takes it.
- qm#121's *Personal data stays on the device* does not name the console's
  receive-only UDP listeners (sACN on 5568, OSC on 8001), which
  `apothecary/stays_local.py` allows and [docs/lighting.md](../../../docs/lighting.md)
  describes.
- The apothecary handoff's records chain (`handbook/handoffs/apothecary-merge-queue.md`,
  §3) leaves out qm#121 and qm#145, which land between #171 and #172
  (*For a person to do*, above).
- No rule says how long a program keeps what it is given and what it makes,
  who forgets it, or how a person deletes it: qmcp's invocation rows,
  apothecary's observations and frames, carlos's states (*Data retention* in
  [the image-models plan](plans/image-models-through-qmcp-2026-10-30.md#records-it-needs)).
- `ci/interop-registry.yaml` has no row for carlos or joe, though each keeps `family/1`;
  the version pin and coverage line in each one's family test are in the shape it reads.
- The site and structure record's *Pends on* says no production
  implementation of `Assembly` exists; the API, the firmware bindings and
  the gathering are built on it (`apothecary/hierarchy.py`, which calls
  itself a prototype too).
