# Inventory: the package's docstrings, comments and `--help` texts

Area 3 of the timeless-docs sweep: `apothecary/**/*.py` and the `--help` of every command, read
on branch `build/timeless-docs`. Read-only. The modules' comments,
docstrings and `help=`/`description=` strings were extracted with their source line numbers
(`code-prose/`, by `extract_prose.py`) and read in full; the source was opened wherever a claim
needed checking. Line numbers are the source file's.

## 1. Verdict

The package is uneven. The `--help` texts and most docstrings are already written the way the
record wants: present tense, saying what a thing does, what it needs and what it refuses. Half
the modules (82 of 164) have nothing to sweep. The narration is concentrated. Five modules
hold a third of it: `menu.py`, `api.py`, `census.py`, `projects/parts/saved.py` and
`gathering/resolve.py`.

**What dominates is internal history in neutral words.** The stock phrases the gate can match
are rare (4 real hits). What the gate cannot see makes up nearly all of the 266 passages:

- owner decisions with dates and plan citations: "(the owner's answer of 2026-10-12)",
  "(loop 1, project/plans/…)", "Decided with the owner on…". Nearly 40 places.
- the names a thing had before: "the firmware page", "the monitor page", "in the cell Watch
  had", "the old, depth-capped viewers", "as it always was", "before the text was the truth".
- past failures given as reasons, mostly in `gathering/`: "an earlier version…", "a reviewer
  showed…", "the meter caught…", and tables of past measurements.

**Stale statements are the second problem: 23 of them.** Examples: `docs generate` says it
writes one workflow, and two are marked `docs`. A field description in `/openapi.json`
(`params_in`) names a value the code no longer accepts. `api.py` calls composite-node
rendering "future work", and it is served. `example_hierarchy.py` gives a printer height of
576, and it is 570. `datum_core.py` says "three numbers" are contested, and one is.
`registry.py` calls `fifel/` and `footpedal/` canonical root folders, and neither exists.
`slicer/__init__.py` says "the page's step comes later", and the page slices.

**Structural issues:**

- **Docstrings that duplicate walkthrough pages.** `cli/preflight.py` copies
  walkthrough/09, `cli/status.py` copies walkthrough/07, and `release.py` with
  `cli/release.py` copy walkthrough/10. Each copy tells the same incident. The viewer's
  vendored three.js story is in `api.py`, `cli/system.py` and walkthrough/04.
- **Live code pointing at dated plans.** `kernel-reference --help`, `kernel_compare.py`, the
  slicer package, `part_edits.py`, `texts.py`, `assignments.py`, `menu.py` and `census.py` all
  cite `project/plans/…`. When those plans retire to History, the code points at history.
- **No reference page for pictures.** The pictures/gathering/cameras area has no present-tense
  page in `docs/`. Its module docstrings (`vision/views.py`, `cameras.py`, `projection.py`,
  `gathering/*`) are the only reference, so explanations have nowhere to move to.
- **The datum story is told three times**, in `datum_core.py`, `datum_cap.py` and
  `datum_core_site.py`. `datum_cap.py:93-100` contradicts its own `contested={}`.
- **22 modules carry `PROTOTYPE — not ratified.`** The label is in capitals and does not name
  the record whose ratification it waits on.

## 2. Modules, worst first

Passages are counted as the sections below list them. A row that groups repeats counts each
place once. The 22 prototype labels are counted apart, in their own group row (pictures group).

| module | verdict | passages | what dominates | stale |
|---|---|---|---|---|
| apothecary/menu.py | heavy | 19 | owner/date/plan citations (10); "in the seat X had" ring-address history (6) | -- |
| apothecary/api.py | heavy | 17 | the one-page/one-viewer history; incidents told in past tense | 4 (module docstring, store banner, composite nodes, old viewers) |
| apothecary/projects/parts/saved.py | heavy | 15 | the `.variant.json` format told as "before" (11); decision dates (3) | -- |
| apothecary/census.py | heavy | 14 | "the firmware page / monitor page" (6); plan citations (4) | -- |
| apothecary/gathering/resolve.py | heavy | 14 | past failures as reasons; reviewer stories; a measurement table | -- |
| apothecary/gathering/arrangement.py | heavy | 7 | "the meter caught"; "the important part"; a measurement story | -- |
| apothecary/firmware/devices.py | moderate | 8 | incidents (the print killed, pins dropped); "as it always was" | 3 |
| apothecary/routes/part_edits.py | moderate | 8 | "from a caller before the text was the truth" (in /openapi.json) | 1 (`params_in`) |
| apothecary/firmware/models.py | moderate | 7 | owner date; the formats "before modules / before jobs" | 1 |
| apothecary/example_hierarchy.py | moderate | 7 | "the newer additions", the wall that moved | 2 (576 mm; "two boards") |
| apothecary/projects/parts/datum_core.py | moderate | 6 | the parts/datum story | 1 ("three numbers") |
| apothecary/spaces.py | moderate | 5 | "an adversarial pass caught"; a count; ornament | -- |
| apothecary/gathering/questions.py | moderate | 5 | past failures; "a reviewer showed" | -- |
| apothecary/gathering/judgement.py | moderate | 5 | past failures; a computed count | -- |
| apothecary/hierarchy.py | moderate | 5 | "additive", "used to", "replaces the four classes" | -- |
| apothecary/gathering/combine.py | moderate | 4 | "an earlier version"; past failures | -- |
| apothecary/projects/parts/texts.py | moderate | 4 | "decided with the owner on…", "now", "still" | -- |
| apothecary/cli/preflight.py | moderate | 4 | duplicate of walkthrough/09 with its incidents (in --help) | -- |
| apothecary/projects/parts/readiness.py | moderate | 3 | bug stories ("used to report…") | -- |
| apothecary/firmware/modules/arduino.py | moderate | 3 | "as it always was / before there were modules" | -- |
| apothecary/projects/parts/datum_cap.py | moderate | 2 | the parts/datum story | 1 (contradicts `contested={}`) |
| apothecary/cli/docs.py | moderate | 2 | "it was produced here once" | 2 |
| apothecary/cli/status.py | moderate | 2 | "has already died once on a check mark"; duplicate of walkthrough/07 | -- |
| apothecary/vision/** (8 modules) | light | 9 | owner dates; past-tense failures | -- |
| apothecary/vocabulary/** (2 modules) | light | 7 | counts ("five words"); past-tense failures | -- |
| apothecary/slicer/** (6 modules) | light | 7 | "decided with the owner on 2026-10-10" (4) | 1 ("the page's step comes later") |
| apothecary/gathering/picture_map.py | light | 4 | counts from one run; past failure | -- |
| apothecary/firmware/gcode.py | light | 4 | the monitor page; a duplicate of docs/firmware.md | 2 |
| apothecary/jobs.py | light | 3 | "the print records kept before jobs" | -- |
| apothecary/openscad_installer.py | light | 3 | "before install.json"; "not supported yet (a planned item)" | -- |
| apothecary/cli/parts.py | light | 3 | "nothing has been keeping the two honest" (in --help) | 1 |
| apothecary/site_store.py, stays_local.py | light | 2 each | "yet"; "an strace of a real slice" | -- |
| apothecary/gathering/bench.py | light | 2 | "an earlier version"; "the worst failure this code has had" | -- |
| apothecary/projects/registry.py | light | 2 | dead root folders called canonical | 1 |
| apothecary/projects/parts/stl_renderer.py | light | 2 | a timing measurement; "as before" | -- |
| apothecary/firmware/api.py, modules/__init__.py, rust_installer.py | light | 2 each | the pages this router served; "Two modules today"; owner date | -- |
| apothecary/kernel_compare.py, cli/release.py | light | 2 each | dated plan as reference; "no way to learn until it was written down" | -- |
| 19 more modules | light | 1 each | see their sections: `datum_core_site.py` (gate hit), `gathering/models.py`, `signature.py`, `datum_bench.py`, `assignments.py`, `parts/__init__.py` (stale), `skeleton.py` (stale), `firmware/serial_monitor.py`, `service.py`, `scripted.py`, `firmware/__init__.py` (stale), `release.py`, `routes/pictures.py`, `routes/menu.py`, `cli/kernels.py`, `cli/server.py`, `cli/photo.py`, `cli/openscad.py` | 3 |
| PROTOTYPE label | -- | 22 places | ornament and an unnamed status | -- |

Total: 244 narrating passages in 72 modules, plus 22 labels (10 modules carry only the
label). 82 of 164 modules are clean. Among the `--help` texts, 5 passages need a change, all
listed under the CLI.

## 3. The gate's findings under `apothecary/`

`check_timeless.py --all` reports 11 findings in the whole repository. Six are under
`apothecary/`; the other five are in `tests/` and `walkthrough/` (areas 2 and 4).

| finding | real? | row |
|---|---|---|
| `api.py:1517` "used to be" | real | api.py 1517-1520: inline + retrospective <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| `census.py:114` "was found in" | **false positive**: "The page was read and nothing was found in it" describes the refusal, in the present | -- <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| `datum_core_site.py:34` "used to be" | real | datum_core_site.py 34-36: inline + retrospective <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| `gathering/models.py:6` "was found in" | **false positive**: "enough was found in it" describes a picture, in the present | -- <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| `gathering/resolve.py:409` "used to be" | real | resolve.py 409-415: inline + retrospective <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| `hierarchy.py:220` "used to be" | real | hierarchy.py 220-221: inline <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |

For the record's tool: `was (found|caught|discovered) in` matches present-tense descriptions
of a search result. Both false positives use the shape "nothing/enough was found in it". <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory -->
The pattern could require a narrating subject, or the two lines could carry
`timeless: allow` with a reason.

## 4. Stale statements (§1), each checked

| where | says | is | checked |
|---|---|---|---|
| cli/docs.py:3-9 | "What is left here is the fractal viewer workflow" | the printer monitor is also a docs workflow | `tests/e2e/test_docs_printer_monitor.py:64` |
| cli/docs.py:214-217 | "The picture walkthrough asks the server to look at a picture" | no `docs`-marked test uses the picture folder | both `test_docs_*` marked `docs` |
| cli/parts.py:275-278 (in --help) | "nothing has been keeping the two honest" | `parts verify` and `checklist` do | the commands |
| firmware/__init__.py:5-10 | the engines are arduino-cli and esptool | the Rust module drives cargo and espflash; pyserial lists and monitors | `modules/rust_esp32.py`, `serial_monitor.py` |
| firmware/devices.py:3-4 | "Three views of one board" | five are listed | the docstring |
| firmware/devices.py:338-340 | "the firmware page" | `/firmware` is a redirect to the Bench | `api.py:2483` |
| firmware/devices.py:1340 | "``arduino-cli monitor`` processes" | may be the pyserial monitor | `listener_argv` |
| firmware/gcode.py:541-543, 1104-1105 | "the monitor shows" / "the monitor's control overlay" | a board's Machine | `api.py:2489` |
| firmware/models.py:562 | identity is "MAC or port" | also the bridge's serial number | `models.py:323, 545` |
| api.py:1-11 | API for scenes, parts and a part viewer | it also serves sites, pictures, firmware, slicer, jobs and part edits | the routers in `api.py:212-226` |
| api.py:1158-1161 | site state is "lost on restart" | cameras are kept across a restart | `site_store.py:9-11, 49-53` |
| api.py:1380-1384 | composite rendering is "future work" | `GET /sites/{name}/nodes/{path}/stl` serves it | `api.py:1904`; template :7172-7201; `viewer.py:3-6` |
| api.py:1435-1447 | `structures` is for "the old, depth-capped viewers" | no viewer reads it | grep of the template and static JS |
| projects/registry.py:96, 114, 128 | `fifel/` and `footpedal/` at the root are canonical | both live under `parts/`; the branches are dead | `ls` |
| projects/parts/datum_core.py:174 | "Three numbers … state differently" | one (`board_y`) | `contested` at 186-202 |
| projects/parts/datum_cap.py:93-100 | "The same disagreement datum_core carries" | `contested={}` | the line below it |
| projects/parts/__init__.py:3-5 | each module is a wrapper exposing `Part` | no `Part` class; 12 modules are machinery | grep |
| projects/parts/skeleton.py:16 | `<repo>/apothecary/apothecary/projects/parts` | `<repo>/apothecary/projects/parts` | the file's path |
| example_hierarchy.py:77 | Ender height "576" | 570 | `ender3.py:28` |
| example_hierarchy.py:654 | "two boards" | `BENCH_BOARDS` plus the mainboard | `example_hierarchy.py:124` |
| routes/part_edits.py:613-615 (in /openapi.json) | `params_in`: "'variant-file' (beside its SCAD)" | the default is `text`; `variant-file` is refused | `saved.py:150-165` |
| slicer/__init__.py:18-19 | "the page's step comes later" | the Machine's Print card slices | `static/widgets/machine.js:976` |

Checked and true: `cli/system.py:89-91` (the static "Layout valid" chip,
`templates/fractal_viewer.html.j2:702`); `cli/preflight.py:3-4` (`main` unprotected, 0
rulesets: `gh api`); the "for one release" of the retired commands (no release since 0.1.0);
the qm hierarchy record is still a DRAFT (so "(prototype, unratified)" is true); "Two finders
ship" (`finder.py:69-70`); "two scripted serial ports" (`firmware/scripted.py:60-66`).

## 5. Retrospectives this area needs (qm `perspectives/`, one dated file each)

**apothecary: gathering pictures**
- One-to-one matching let a coincidence lock the real match out (resolve.py:231-236, arrangement.py:145-146).
- The "every shape accounted for" exception made the rule unreachable, and a reviewer walked through it (resolve.py:409-415).
- Nine orders of one folder gave five results; the sort fixed it (resolve.py:577-582).
- The contradiction check broke groups a person had built (resolve.py:632-634).
- Answers about unreadable pictures were dropped silently (resolve.py:833-835; judgement.py:281-282).
- The meter caught the missing arrangement check: a square, a disc and a triangle joined unrelated photographs (arrangement.py:3-6).
- The fit tolerance went from 10% to 4% by measurement (arrangement.py:40-45); the 1.8 ratio table (resolve.py:143-155).
- The fit depended on hand-in order (arrangement.py:124-126).
- Twelve unrelated photographs were chained through weak seams, which scoring per occasion could not see (bench.py:310-314).
- Questions ranked by composite size; 22 s inside the loop; a dead guard deleted by a reviewer; the sheet piling up and overwriting notes; its own examples fed back (questions.py:86-88, 123-125, 132-133, 172-177, 212-214).
- The UTF-8 BOM that turned the first name into nobody (judgement.py:249-252).
- Pieces dropped when not numbered; middles laid wide parts on top of each other; one name replacing another (combine.py:60-62, 172-175, 222-226).
- A reset that did nothing while appearing to work (vision/shelf.py:84-87); a panel built a quarter turn out (plain.py:250-252).

**apothecary: datum_core and its numbers**
- parts/datum retired: its 2.4/0.2 values cited a record that does not contain them (datum_core.py:177-185, datum_cap.py:93-100).
- The `show` enum split into datum_cap (datum_core.py:143-145, datum_cap.py:7-10); the seam moved from parts/datum (datum_core.py:96-99, 124-125).
- Twelve defaults restated in the assembly and kept in step by a test, then read instead (datum_core_site.py:34-36).
- The readiness check read (Scene, Assembly) as one object and reported "no stubs remain" (readiness.py:466-468); calibration_cube was told about a board (477-479).
- A bare Cube at the origin while the Python model looked right (datum_bench.py:128-131); a contested value caught lying dormant (spaces.py:110-112).

**apothecary: one page, one viewer**
- The parts browser and the Site browser absorbed into the fractal viewer (api.py:2469-2471, 2512-2517, 2548-2558).
- The firmware page and printer monitor became the Bench and a board's Machine, with their links kept (api.py:2476-2495, census.py:65-67, 86-89, 249, 332-359, menu.py:654, 1308-1312, firmware/api.py:5-7, gcode.py).
- Ring cells kept their addresses through each change (menu.py:549, 661, 684, 1079, 1245, 1308-1312).
- `scad` attached only after a drag (api.py:1517-1520); the CDN copy of three.js that left the page empty (api.py:194-197).
- The JSCAD viewer's flags (cli/server.py:97-98); the depth-capped viewers (api.py:1435-1447).

**apothecary: the printer link** (shared with area 1's printer pages)
- Closing the link mid-print killed the print and left the heaters on (devices.py:639-641).
- ttyUSB0 became ttyUSB1 overnight; pins moved to the bridge serial (models.py:326-328).
- Interleaved read-modify-writes dropped pins (devices.py:113-115); a CP2102 under a realtime kernel repeated bytes (devices.py:1502-1503).
- Real silences cost the unit suite a minute (gcode.py:610-612).

**apothecary: CI and preflight**
- A green local suite hid a CI failure more than once (cli/preflight.py:50-53).
- In the sibling project, one workflow's `uv sync --locked` stripped the next workflow's tools (cli/preflight.py:119-123).
- Five workflows failed alike on a missing shell (cli/preflight.py:71-73).
- The CLI died on a check mark under cp1252 (cli/status.py:23-24).

**apothecary: the walkthrough and generated docs** (shared with area 2)
- The walkthrough was once produced by `apothecary docs`, and the remembered page went stale (cli/docs.py:3-9).

**apothecary: part editing in the browser** (shared with the part-iteration plan)
- Variants that kept values in `.variant.json`, then "the text is the truth" (saved.py:33-37 and its 10 repeats, part_edits.py, texts.py:3).
- Controls built by the page were not counted by the census (census.py:158-159).

**apothecary: firmware toolchain modules**
- The seam became the Arduino module "otherwise unchanged", with fields "as they always were" (the 8-place pattern).
- The scripted bench moved out of tests/ (scripted.py:10-11); espup's own install was replaced (rust_installer.py:664-666).

## 6. Reference pages to create or extend

- **docs/pictures.md (new).** Views and places, the one mapping, cameras and their lens, made
  pieces, the gathering's rules and why each threshold is shaped as it is, the finders and
  their limits. Module docstrings in `vision/` and `gathering/` then point here. Material:
  `vision/views.py:1-48`, `vision/projection.py:1-35`, `vision/cameras.py:1-34`,
  `gathering/resolve.py`, `arrangement.py`, `judgement.py`, `questions.py` (the present-tense
  rewrites).
- **A dated validation record in project/validation/ (new): the gathering's and the finder's
  measured thresholds.** The tables in `resolve.py:143-155`, `arrangement.py:40-45`,
  `plain.py:53-56`, `judgement.py:3-5` and `models.py:286-290` move there. Each constant's
  comment then says what it is and names the record.
- **docs/viewer.md (extend): the ring's address rule.** A cell, once given, keeps its number,
  and new options are appended. This replaces the six "in the seat X had" comments in
  `menu.py` (549, 661, 684, 1079, 1245, 1308-1312).
- **docs/kernels.md (new), or docs/README.md "The Rust workspace" (extend).** The kernel
  comparison: corpus, reference, measures, tolerances. `kernel-reference --help` and
  `kernel_compare.py:3-4, 700-703` point here instead of at the dated spike.
- **docs/openscad.md (new), or docs/parts-authoring.md (extend).** Which OpenSCAD renders
  (`APOTHECARY_OPENSCAD`, the installed snapshot, PATH), the queue of runs, and 2021.01 against
  a snapshot. Material: `stl_renderer.py:138-151` (without the timing story),
  `openscad_installer.py`, `cli/openscad.py`.
- **CONTRIBUTING.md (extend), "moving a pinned tool".** The pin-bump procedure
  (`rust_installer.py:40-47`, `orcaslicer_installer.py:48-52`) stated once. The module comments
  keep the rule.
- **No new page** for the duplicates of walkthrough/04, 07, 09 and 10: the docstrings shrink
  to a pointer.

## 7. Suggested order for sweeping this area

1. **The `--help` texts and the `/openapi.json` descriptions**, which are read the most and
   are the smallest change: `preflight` (50-53), `parts verify` (275-278), `elephant-walk`'s
   "Note:", `openscad install`'s "yet", `kernel-reference`'s plan link, and `part_edits.py`'s
   `params_in` (stale) and its "from a caller before the text was the truth" (171-172,
   609-610). One commit.
2. **The 23 stale statements** (section 4). Each is a fact made true again: small, safe and
   checkable. One commit per package (cli, firmware, api, projects, examples, slicer). Flag the
   dead `fifel/`/`footpedal/` branches for the cleanup triage rather than deleting them in a
   docs sweep.
3. **The mechanical patterns.** First the owner/date/plan parentheticals (nearly 40). Then the
   22 prototype labels, each naming its record. Then "as it always was" (8). Then "today"/"yet"
   counts (`Two modules today`, `One module today`, `five words`). A commit each: reviewable
   by diff alone.
4. **Duplicates of walkthrough pages.** `cli/preflight.py`, `cli/status.py`, `cli/release.py`,
   `release.py`, `api.py:194-197`, `cli/system.py:89-91` and the `api.py` store banner shrink
   to a sentence and a pointer.
5. **The named format.** `saved.py`, `part_edits.py` and `texts.py`: name the `.variant.json`
   format once and use the name instead of "before the text was the truth" (15 places).
6. **The one-page history.** `menu.py`, `census.py`, the `api.py` redirects, together with the
   docs/viewer.md address rule. This needs the "one page, one viewer" retrospective drafted
   first, so nothing is lost.
7. **The datum story.** `datum_core.py`, `datum_cap.py`, `datum_core_site.py`, `readiness.py`,
   `datum_bench.py`, after its retrospective.
8. **`gathering/`, last.** It is the largest rewrite (43 passages). It needs
   docs/pictures.md, the validation record and the "gathering pictures" retrospective first,
   and its voice is deliberate, so the owner should see one module (`resolve.py`) rewritten
   before the rest follow.


# Module sections (groups worst first; within a group, heavy, then moderate, then light, most passages first)

## Group: the server's core -- api, menu, census, stays_local, docs_site, site_store, datum_core_site, demo, jobs, spaces

### apothecary/menu.py -- heavy -- 19 passages (4 rows)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 548, 686-688, 726-727, 1032, 1047, 1214, 1224, 1229-1230, 1234, 1244 (x10) | "(the owner's answer of 2026-10-12)" / "(loop 1, project/plans/ui-flows-2026-10-08.md)" | history (owner chose, dates, plan citations) | inline | Drop each parenthetical. The decision is the code and the sentence around it. Plans that are finished retire to History. |
| 549, 661-662, 684, 1079, 1245, 1308-1312 (x6) | "in the seat Fit had" / "in the cell Watch had; Watch and Monitor were two ways" | history | inline + reference → docs/viewer.md (the ring's addresses) | State the rule once in docs/viewer.md ("a cell, once given, keeps its number; new options are appended"). Each comment then says where the option sits, e.g. "Open is the board's Machine; Control at 7." |
| 654-655 | "the task log -- what the firmware page was -- a tab of the rail's strip" | history | inline | Drop "what the firmware page was". |
| 1081, 1478-1480 (x2) | "until gathering leaves core" / "is not on any ring yet -- when it arrives" | history (plan in code) | inline | "and Gather, the gathering's report." / "The commit that follows a drag is not on a ring." Put plans in a plan or project/todo.md. |

Kept: 10 (rad's nine-cells record, a reference); 677-678, 731, 1270, 1276, 1283 ("appended, so no cell before it moves"): these state the address rule in the present.

### apothecary/api.py -- heavy -- 17 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 1-11 | "This module provides REST API endpoints for: ... 3D viewer for part preview" | stale | inline | The routes now cover sites, pictures, views, cameras, firmware, slicer, jobs and part edits. Say "the server's routes; /openapi.json lists them" instead of the old three-item list. |
| 194-197 | "with the network switched off, fetching it meant the viewer never loaded at all" | history, duplicate | inline | "Kept here, not fetched: with the network off, or a CDN dropped by an ad blocker or proxy, the page's script never runs." Same story in `cli/system.py:89-91` and walkthrough/04:30. |
| 246-247 | "(GET /parts/stl_renderer used to import that module and answer 500)" | history | inline | Drop the parenthetical: "Only a registered part: a name from a URL is never turned into an import path." |
| 688-689 | "at most ``limit`` run at once (two; see ... ``RUNS``)" | count | inline | "at most ``limit`` (stl_renderer's ``RUNS``) run at once": the number lives in the constant. |
| 1158-1161 | "Known limitation: in-memory only, lost on restart" | stale, duplicate | delete (keep site_store.py's) | Cameras a person added are kept across a restart (`site_store.py:9-11, 49-53`); this banner omits it. Point at site_store.py instead. |
| 1380-1384 | "the viewer falls back to a bounding-box wireframe ... real CSG rendering of composite nodes is future work" | stale, ornament ("not a bug") | inline | Composite nodes render through `GET /sites/{name}/nodes/{path}/stl` (api.py:1904; viewer template :7172-7201). "Returns None for anything richer; the viewer draws those from the node's STL." |
| 1411-1412 | "drawn without them it was a round cone" | history | inline | "a wedge is a cylinder of three facets, and without them it would draw as a round cone." |
| 1435-1436, 1446-1447 | "for the old, depth-capped viewers" / "the only depth the old, depth-capped viewers ever showed" | history, stale | inline | No viewer reads `structures` now (only tests and API clients). "Unlike ``_structure_summary`` (the root's direct children, in ``structures``) ..." |
| 1517-1520 | "``scad`` used to be attached only by the layout route" | history (gate hit) | inline + retrospective → apothecary: the viewer and the one page | "Every read carries ``scad``: it is string generation over a tree in memory, not an OpenSCAD process." <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| 2469-2471 | "There is no longer a standalone parts browser or bare Site browser" | history | inline | "The default entry point of the one viewer (``site_viewer``)." |
| 2476-2480 | "The firmware page and the printer monitor were pages of their own; ... (the consolidation plan's Phase 5)" | history, plan citation | inline | "`/firmware` and `/firmware/monitor` redirect to the Bench and a board's Machine: links to them exist outside the app." |
| 2494-2495 | "A port of the wrong shape is dropped, as the page dropped it" | history | inline | "A port of the wrong shape is dropped: the viewer opens with nothing in front of it." |
| 2512-2517 | "Absorbs both previous viewers ... the old part-viewer experience, no longer a separate page" | history | inline | "Navigates any registered site's tree; the parts library is the `parts_library` site, a part one of its leaves." |
| 2548-2551 | "This deep-link survives because links to it were handed out, but it now lands" | history, ornament | inline | "Links to it exist outside the app, so it lands in the viewer focused on the part." Drop "Two pages onto one object is how a codebase ends up...". |
| 2554-2558 | "The library was consolidated to underscore case and links to `datum-core` were handed out before that" | history | inline | "Focus on the part's registered name: a link may spell it `datum-core`, which the lookup accepts." |
| 2565 | "The project's first APIRouter, mounted last." | history | inline | "Mounted last: its handlers reach back into the helpers above, ..." (seven routers are mounted at 212-226). |

Kept: 1156 "(prototype, unratified)" and 2512 "(prototype)": still true, since the hierarchy record is `DRAFT-site-structure-substructure-feature-hierarchy.md` in qm/adr. 1602-1605 ("the day somebody points it at a network") is a present-tense reason. 2273/2439 "today" mean the current moment of a run.

### apothecary/census.py -- heavy -- 14 passages (6 rows)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 65-67, 86-89 (x2) | "the only page there is since the firmware page and the printer monitor became" | history, plan citation, duplicate | inline | "It is one page, the viewer (`/firmware` and `/firmware/monitor` redirect to it)." Delete the rest of 86-89; api.py:2476 holds the redirects. |
| 249, 332-334, 351-352, 358-359 (x4) | "as the monitor page had it" / "(a list on the firmware page)" | history | inline | Name the widget as it is: "The Bench's sections (widgets/toolchain, sketches, tasks.js), named by class: the Bench and a board's Flashing card mount them." |
| 142-143, 158-159, 194-195, 548-550 (x4) | "(the part-iteration plan of 2026-10-12)" / "since the part-iteration plan: built by the page before it, they were not counted" | history, plan citation | inline | Drop the citations; 158-159: "written there as markup, so the census counts them." |
| 204 | "The SCAD editor where the part's read-only source stood" | history | inline | "The SCAD editor (widgets/scad_editor.js): ..." |
| 341-342, 348-349 (x2) | "Rust for the ESP32 today" / "OrcaSlicer today" | count, history | inline | "Every other toolchain module, drawn from the status beside arduino-cli, one Install each." The list is the registry's. |
| 374 | "the gathering's section until gathering leaves core" | history (plan in code) | inline | "and the gathering's section". Same as menu.py:1081. |

Gate hit 114 ("nothing was found in it"): **false positive**. It describes the refusal, in the present. <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory -->
Kept: 29-30 "**This is the meter.**" (a short clause in bold); 575-580 (cites records for a lasting exception, present tense).

### apothecary/spaces.py -- moderate -- 5 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-4 | "so a reader does not have to run five commands" | count | inline | "so a reader does not have to run each command and hold the answers." |
| 20 | "**Scope, stated so its absence is not mistaken for silence.**" | ornament | inline | "**Scope.**" |
| 110-112 | "and an adversarial pass caught this one lying dormant." | history (what caught it) | inline + retrospective → apothecary: reviews and gates | Keep "From the table, not typed again here." Drop the rest. |
| 136-140 | "and calling that drift told a reader the declared size disagreed" | history | inline | "Nothing measured, nothing drifted: on a fresh checkout no part is rendered, and the missing render is open on its own as `unprintable`." |
| 154-155 | "WP-4 produces the schematic" | stale-risk (an external work package) | inline | "the consuming project's to supply (its schematic)". Not checked: WP-4 is datum's. |

### apothecary/jobs.py -- light -- 3 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3 | "A job is a print on a printer today" | history ("today") | inline | "A job is a print on a printer; a cut on a mill or a laser would be one the same way." |
| 19 | "readable by this account alone, as the print records were" | history | inline | Drop "as the print records were". |
| 25-32, 353 | "**The print records kept before jobs** ... nothing writes there any more" | history, duplicate | inline | "**Print records** (`prints/records/*.json`, a format nothing writes) are read once and carried over as print jobs: ..." Same as firmware/models.py:504-508. |

### apothecary/site_store.py -- light -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3, 9 | "Sites carry no real persistence layer yet" / "Known limitations, stated rather than hidden" | history ("yet"), ornament | inline | "Sites have no persistence layer: ..." / "Limits: ...". |
| 86-90 | "The register was built with everything it holds decided in advance, which is fine while" | history (light) | inline | "The register holds the arrangements written into the program; one built from a picture is added while the server runs, so the viewer can show it." |

### apothecary/stays_local.py -- light -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 40-41 | "and it reaches no host (an strace of a real slice)" | history (how it was found) | inline | "and it reaches no host." The strace evidence belongs in a validation record or the slicer PR. |
| 82-87 | "**The named exception, not yet built:** *secured user accounts*." | history (plan in code) | inline | "**The named exception:** secured user accounts, which have no code path until a record accepts them; this module is what would change." |

### apothecary/datum_core_site.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 34-36 | "These used to be typed out again here, twelve of them, kept in step" | history, count (gate hit) | inline + retrospective → apothecary: reviews and gates | "The parts' own defaults, read from their parameter models rather than restated." The lesson ("a gate compensating for a duplication") goes to the retrospective. <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |

Kept: 10-11 (the test still compares the SCAD defaults: `tests/test_datum_core_site.py:57-65`); 62 "no parameter model exposes yet" (a present limit).

**Clean:** `docs_site.py`, `demo.py`.

## Group: pictures -- apothecary/gathering/**, apothecary/vision/**, apothecary/vocabulary/**

**Group verdict.** The gathering package (sorting many pictures) is the most narrated code in
the repository. Almost every threshold and guard is justified by the incident that produced it:
"an earlier version", "a reviewer showed", "the meter caught", "was this module's most common
mistake", plus tables of past measurements. The reasoning is often good and much of it is a
real constraint. The fix is the same each time: state the constraint in the present ("X would
do Y") and move the stories and measurement tables to a retrospective or a dated validation
record. vision/ is clean present-tense prose apart from its labels and a few owner dates.
19 modules here carry the line `PROTOTYPE — not ratified.` (3 more in G5).

### apothecary/gathering/resolve.py -- heavy -- 14 passages (8 rows)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 109-112, 124-126, 248-250, 266-267, 438-441 (x5) | "moved every size at once and lost the real matches" / "Trusting it at two turned one honest refusal into three confident mistakes" | history (past failures as reasons) | inline | Conditional present: "...would move every size at once and lose the real matches." / "At two it moves with every wobble in the finder." |
| 143-155 | "The number was measured, not chosen. Across fifteen folders of twenty-seven drawn photographs:" | history (a measurement table), count | reference → a dated record in project/validation/ (gathering thresholds) | Inline: "1.8: the loosest ratio at which `photo gather-check` mixes no group; see <record>." |
| 50-52 | "Measured: the plain finder's confidence is reliably lower when it is wrong" | history (measurement), ornament ("decorative") | inline | "The plain finder's confidence is lower when it is wrong (`photo check` measures it), so this threshold separates." |
| 231-236 | "An earlier version picked the best partner for each shape here" | history | inline + retrospective → apothecary: gathering pictures | "Not one-to-one: a coincidence that looks slightly more alike would lock the real match out. Which pairing is real is the arrangement's question." |
| 359-360, 374-377 (x2) | "This is the check that stopped two unrelated pictures being merged." / "was this module's most common mistake when it was first measured" | ornament (a check by what it caught), history | inline | "Matched one at a time, not in place: a coincidence." / Drop the last clause. |
| 409-415 | "there used to be an exception for ... and a reviewer walked straight through it" | history (gate hit), ornament | inline + retrospective → apothecary: gathering pictures | "Always three shapes lined up: with one shape each, coverage is 100% and the arrangement check cannot run." <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| 577-582, 632-634 (x2) | "and it did: a reviewer handed the same folder in nine different orders" / "and it was destroying groups a person had built" | history | inline + retrospective → apothecary: gathering pictures | "Sorted by name: the answer does not depend on arrival order." / "This check destroys groups, so it never breaks one a person built." |
| 833-835 | "Every one of these was silently dropped once" | history | inline | "An answer never applied is said out loud: a person may name a picture nothing could be read from." |

### apothecary/gathering/arrangement.py -- heavy -- 7 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-6 | "it was added because the meter caught its absence: without it, two photographs" | history, ornament (what it caught) | inline + retrospective → apothecary: gathering pictures | "This check turns a coincidence into evidence: shapes matched one at a time cannot tell a shared square, disc and triangle from a real match." |
| 17 | "**Two known limits, stated rather than hidden.**" | ornament | inline | "**Two limits.**" |
| 40-45 | "At ten percent — the first guess, which looked generous and harmless — ten pairs" | history (measurement) | reference → the same validation record as resolve.py:143-155 | Inline: "Four percent: genuine pairs fit within two, unrelated ones from four up." |
| 61 | "``kept`` is the important part." | ornament (§3's own example) | inline | "``kept`` says which matches belong to one move-and-scale; ..." |
| 124-126 | "and a reviewer showed the consequence: handing the same two photographs in in the other order" | history | inline | "That makes the check 1/scale stricter one way round; dividing by the square root of the scale makes it the same both ways." |
| 145-146 | "is what let a coincidence take the place of the real match and block it" | history, duplicate | inline | "would let a coincidence take the real match's place". Same as resolve.py:231-236. |
| 172-173 | "Demanding that every match fit therefore threw away every real overlap — the meter caught exactly that." | history, ornament | inline | "Demanding that every match fit would throw away every real overlap." |

### apothecary/gathering/questions.py -- moderate -- 5 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 86-88 | "Reading the composite size here made the valuable questions look worthless" | history | inline | "Reading the composite size here would make the valuable questions look worthless." |
| 123-125 | "Recomputing it inside the loop made this take twenty-two seconds on two hundred photographs" | history, count | inline | "Worked out once, not per pair: inside the loop it would dominate the run." |
| 132-133 | "was dead code, which a reviewer showed by deleting it with no effect." | history | delete | Keep the first sentence ("a pair they have ruled on is already excluded by the verdict alone"). |
| 172-177 | "The sheet was appending its whole question block every run" | history | inline | "Splitting on the line keeps the machine's block from piling up each run, and keeps a person's notes when the sheet is written elsewhere." |
| 212-214 | "uncommenting the instructions by accident fed the sheet its own examples back" | history | inline | "with the gaps marked, so an uncommented instruction is never read as an answer." |

Kept: 3 ("Two hundred photographs is nineteen thousand nine hundred pairs"): arithmetic, not a count a command computes.

### apothecary/gathering/judgement.py -- moderate -- 5 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-5 | "Measured on drawn pictures it finds about a fifth of the groups that are there." | count (a number `photo gather-check` computes) | inline | "On drawn pictures it finds a minority of the groups (`apothecary photo gather-check` says how many)." |
| 61-63 | "It was chosen so that it can be read aloud to somebody" | history (light) | inline | "It reads aloud to somebody who does not do this work, the test every page here passes." |
| 204-206 | "Left to itself this came out as a wall of internal detail" | history | inline | "Pydantic's own message is internal detail with no line number." |
| 249-252 | "the first name in the file quietly became a name nothing answered to" | history | inline | "without it the first name in the file would be one nothing answers to." |
| 281-282 | "Left unchecked the second one simply vanished." | history | inline | "Unchecked, the second would vanish." |

Kept: 7-48 ("two Tuesdays" and so on): a present argument for arithmetic, in the module's own voice.

### apothecary/gathering/combine.py -- moderate -- 4 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 60-62 | "two pieces sharing one name meant the second quietly replaced the first" | history | inline | "two pieces sharing one name would let the second replace the first unseen." |
| 91-94 | "two sightings of something the finder was not sure about *at all* came back at twenty-five per cent" | history | inline | "...would come back at a quarter: confidence out of two admissions of ignorance." |
| 172-175 | "An earlier version looked only at the numbered ones and dropped the rest without a word" | history | inline | "Every piece of the other picture, numbered or not: a piece vanishing unsaid is the failure this module exists to prevent." |
| 222-226 | "Measuring only the middles of the pieces reported three arrangements nearly four thousand units across" | history | inline | "Measured from where each piece sits and how big it is: middles alone would lay wide parts on top of each other." |

### apothecary/vision/** -- light -- 9 passages (besides the labels)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| cameras.py:437, camera_part.py:7 (x2) | "(the owner's decision of 2026-10-04)" | history (owner, date) | inline | Drop the parenthetical. |
| projection.py:213 | "On a flat picture that is the shape's sides times ``W`` and its own turn, as they always were." | history | inline | Drop "as they always were". |
| shelf.py:84-87 | "returning the live one made resetting a picture-built arrangement do nothing at all" | history | inline | "Returning the live one would make Reset do nothing while appearing to work." |
| plain.py:250-252 | "throwing it away built the panel a quarter turn out" | history | inline | "throwing it away would build the panel a quarter turn out." |
| plain.py:53-56 | "Measured: drawn at 3-6% ... naming was right 33% of the time" | history (a measurement) | reference → the gathering/finder validation record | "Below this, naming is unreliable (`photo check` measures it), so the confidence is pulled down." |
| compose.py:3 | "The important decision here is what happens when nobody has said how big" | ornament | inline | "When nobody has said how big the picture is, the pieces are still placed, unsized, ..." |
| compose.py:134-137 | "importing it up there made the two packages depend on each other" | history (light) | inline | "Imported here: at the top the two packages would import each other." |
| cache.py:3 | "Keyed as the photo-finders plan keys it:" | history (plan citation) | inline | "Keyed by the picture's hash, the finder's backend, the model's digest and the prompt's version." |
| album.py:9-16 | "the same argument was already made for links ... Nothing new was needed." | history (light) | inline | "A fact about a piece belongs beside the tree, as links do, so the tree renders unchanged. The join is the dotted path." |

**Clean in vision/ apart from the label:** `views.py`, `projection.py` (but 213), `piece.py`,
`models.py`, `geometry.py`, `bench.py`, `stated.py`, `finder.py` ("Two finders ship": true,
`finder.py:69-70`), `__init__.py`, `gathering/looking.py`, `gathering/report.py`.

### apothecary/vocabulary/** -- light -- 7 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| starter.py:1, 102 (x2) | "The five words we start with." / "Five words, all guesses." | count | inline | "The starter words." / "The vocabulary as it stands: every word a guess." |
| starter.py:6-7 | "built out of pieces the tool already had — nothing new was invented" | history (light) | inline | "Each is built from the tool's own primitives." |
| starter.py:34-35, 44-45, 50-51 (x3) | "without this, every disc, post and wedge was drawn half its size away" / "as finely as it always was" | history | inline | Conditional present: "would be drawn half its size away" / "would put a mesh wider than the footprint" / "faceted as the longer side's circle is". |
| word.py:42 | "The owner's decision of 2026-10-10 (project/plans/slicer-2026-10-10.md):" | history | inline | Start at "A piece made from a picture slices with the printer's values; ...". |

**Clean:** `vocabulary/match.py`, `vocabulary/__init__.py` (apart from the label).

### apothecary/gathering/picture_map.py -- light -- 4 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 77-79 | "giving each the room a whole group needs pushed the groups off the top" | history | inline | "...would push the groups off the top of the screen." |
| 176-180, 220-222 (x2) | "On eighteen photographs there were a hundred and four of them" | history, count | inline | "Undecided pairs far outnumber answers; drawn as lines they would hide them. They are counted on the picture they touch." |
| 24-25 | "Checked with the validator on the all-pairs list in both light and dark" | history (light) | inline | "Two hues and a neutral, each clear of the contrast floors against the others in light and dark." |

### apothecary/gathering/bench.py -- light -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 222-225 | "An earlier version overlapped by so little that typically one shape was in both" | history | inline | "The two windows share several shapes: one shared shape is no evidence, and the sorter rightly says so." |
| 310-314 | "This exists because scoring occasion by occasion missed the worst failure this code has had." | history | inline + retrospective → apothecary: gathering pictures | "Scoring occasion by occasion cannot see a chain built across occasions; handing a folder in at once can." |

### apothecary/gathering/models.py -- light -- 1 passage, and the label

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 286-290 | "on made-up pictures with known answers it has never joined photographs that were plainly unrelated" | history (a measurement) | inline | "The sorting is conservative, not infallible: `photo gather-check` measures how often it joins two that merely look alike." |
| 18 | "PROTOTYPE — not ratified." | ornament (label in capitals) | inline | See the group row below. |

Gate hit 6 ("enough was found in it"): **false positive**. It describes a picture, in the present. <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory -->

### apothecary/gathering/signature.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 63-64 | "is how a close-up came to be judged a separate object" | history, duplicate | inline | "would judge a close-up a separate object". Same as resolve.py:124-126. |

### Group row: the `PROTOTYPE — not ratified.` label -- 22 places

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| gathering/__init__.py:15, models.py:18; vision/__init__:12, album:18, cache:16, camera_part:24, cameras:36, compose:13, finder:14, models:8, piece:22, plain:15, shelf:16, stated:11, views:50; vocabulary/__init__:7, match:8, starter:9, word:12; hierarchy.py:3, example_hierarchy.py:5, example_parts_library.py:3 (x22) | "PROTOTYPE — not ratified." | ornament (a word in capitals) and an unnamed status | inline | "A prototype: the record that governs it, <name>, is a draft." Name the record so a reader can check the status. Done once, it is a sed. |

## Group: parts and projects -- apothecary/projects/**

### apothecary/projects/parts/saved.py -- heavy -- 15 passages (4 rows)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 5-6, 24-25, 150-152 (x3) | "(decided 2026-09-27, see project/plans/part-editing-in-the-browser-2026-09-27.md)" / "(the owner's answer of 2026-10-12, ...)" | history (decision dates, plan citations) | inline | Drop each parenthetical: "...to a ref of the part's own, in the repository that tracks the part's SCAD." The rule stands without its date. |
| 33-37, 70, 167, 286-287, 332-333, 416-417, 598, 645-646, 799, 885-887, 936-937 (x11) | "A variant saved before that kept its parameters beside its SCAD" / "a variant from before keeps them in a file" | history (a format told as "before") | inline | Name the format: "A variant whose commit holds `<stem>.variant.json` keeps its values there; served, they are written into its SCAD." Then "a `.variant.json` variant" everywhere. |
| 551 | "``params``, from a caller that still sends values on the side" | history ("still") | inline | "``params``, from a caller that sends values on the side, are written into the text first". |

### apothecary/projects/parts/datum_core.py -- moderate -- 6 passages (one stale)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 96-99 | "This seam arrived with ``parts/datum``, the single-piece tray this part supersedes." | history | delete + retrospective → apothecary: datum_core and its numbers | The function's first paragraph says what the seam is. |
| 124-125 | "`parts/datum` called these usb_w/usb_h; the core names them for what they are" | history | inline | "The board's own keepouts choose the edge connector's opening." |
| 143-145 | "It used to branch on a ``show`` parameter that selected between the tray and the cover" | history | inline | "One object, one envelope: the tray's. The cover is ``datum_cap``." |
| 174 | "Three numbers this project's own sources state differently." | stale, count | inline | `contested` holds one parameter, `board_y`, with two candidates (checked lines 186-202). "A number this project's sources state differently: ..." |
| 177-185 | "`walls` and `tolerence` were contested only by parts/datum ... Retiring it settled both" | history | inline + retrospective → apothecary: datum_core and its numbers | "`walls` and `tolerence` are the house constants; a part that differs says why (clause 3). board_y is contested: two sources disagree." |
| 93-94 | "a hand-entered stub today, a KiCad outline later" | history (light, "today/later") | inline | "a hand-entered stub (shims/kicad.py) or a KiCad outline". |

Kept: 7-8 "no schematic exists yet", a present limit. The contested note (line ~194) agrees with it.

### apothecary/projects/parts/texts.py -- moderate -- 4 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3 | "Decided with the owner on 2026-10-12 (project/plans/part-iteration-2026-10-12.md," | history | inline | Start at "For a part whose SCAD the page edits, nothing is passed to OpenSCAD on the side." |
| 7-8 | "A caller that still sends parameters has them written into the text first" | history ("still") | inline | "A caller that sends parameters has them written into the text first (``with_params``)." |
| 25 | "the SCAD is the default now" | history ("now") | inline | "the SCAD is the default, and `apothecary problems` and a part's checklist say where the model says otherwise." |
| 130 | "(a caller from before overlays)" | history | inline | Drop the parenthetical. |

### apothecary/projects/parts/readiness.py -- moderate -- 3 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 361 | "the SCAD as saved is the part's default (decided 2026-10-12)" | history | inline | Drop "(decided 2026-10-12)". |
| 466-468 | "Reading it as one object made this check report "no stubs remain"" | history (a bug story) | inline + retrospective → apothecary: reviews and gates | "build() returns (Scene, Assembly); the stubs are the assembly's." |
| 477-479 | "This used to report the bench's stubs for every part in the library" | history | inline | "Only for a part the assembly places: a part the bench does not use is fitted to none of its boards." |

### apothecary/projects/parts/datum_cap.py -- moderate -- 2 passages (one stale)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 7-10 | "Split out of datum_core rather than selected by a parameter there." | history | inline | "A part of its own, not a mode of datum_core: one part, one envelope, and the enclosure record asks for separate pieces around one core." |
| 93-100 | "The same disagreement datum_core carries ... Nothing contested remains. ... a resolution, not a silencing" | stale (self-contradicting), history, duplicate, ornament | inline | `contested={}`, but datum_core contests `board_y`. "Nothing contested: `walls`/`tolerence` are the house constants. `board_y` is contested on datum_core, whose footprint this follows." |

### apothecary/projects/registry.py -- light -- 2 passages (one stale)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 96, 114, 128 | "Detects 'fifel', 'footpedal', and 'parts' directories" / "(canonical location under 'fifel/')" | stale | inline (and a dead-code note) | No `fifel/` or `footpedal/` at the root: both are under `parts/` (checked). The comments call dead branches canonical. Flag the branches for the cleanup triage. |
| 45 | "Every caller that guessed wrote a stray file in there." | history | inline | "A caller that guesses writes a stray file into the submodule." |

### apothecary/projects/parts/stl_renderer.py -- light -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 144-148 | "timed on a four-core machine, two renders at once each took a sixth to a third longer" | history (a measurement) | reference → `docs/openscad.md` (new) or delete | Keep the rule: "every run beside the newest render makes it later; two still let a check go beside a render." |
| 151 | "one cancelled while it runs is stopped, as before." | history | inline | "one cancelled while it runs is stopped." |

### apothecary/projects/assemblies/datum_bench.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 128-131 | "An earlier version of this function did exactly that: every object in the scene sat" | history | inline + retrospective → apothecary: reviews and gates | "Cube carries no position of its own, so a bare Cube renders at the origin: each block is wrapped in a Translate." |

### apothecary/projects/parts/assignments.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-4 | "The text is the truth (project/plans/part-iteration-2026-10-12.md, "parameters and text, tied together")" | history (plan citation) | inline | "The text is the truth: ..." docs/viewer.md:199-200 already states the page's side. |

### apothecary/projects/parts/__init__.py -- light -- 1 passage (stale)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-5 | "Each module in this package corresponds to a .scad file ... Modules expose a `Part` class" | stale | inline | No module defines `Part`. Wrappers expose `DEFAULT` and `Params`, and 12 modules here are machinery (stl_renderer, variants, saved, ...). Say both. |

### apothecary/projects/parts/skeleton.py -- light -- 1 passage (stale)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 16 | "Fallback: <repo>/apothecary/apothecary/projects/parts -> parents[3] == <repo>" | stale | inline | The file is `<repo>/apothecary/projects/parts/skeleton.py`: "<repo>/apothecary/projects/parts/skeleton.py -> parents[3] == <repo>". |

**Clean:** `variants.py`, `customizer.py`, `gridfinity.py` (45-47 is upstream history, §4),
`params.py`, `drafts.py`, `calibration_cube.py`, `base.py`, `described.py`,
`openscad_messages.py`, `ender3.py`, `footpedal.py`, `fifel.py` (42 "originally lies along Y"
is the SCAD's orientation, not history), `rc_snowplow.py`, `rc/**`, `parametric_star.py`,
`contranot.py`, `couch_block.py`, `dryerknob.py`, `matboard_cutter_mount.py`, `solderfan.py`,
`star_cookiecutter.py`, `v_slot.py`, `assemblies/__init__.py`, `projects/__init__.py`.

**Group pattern:** the datum story (parts/datum retired, its 2.4/0.2 values, the `show` enum)
is told three times: `datum_core.py:96-99, 124-125, 143-145, 177-185` and
`datum_cap.py:7-10, 93-100`. One retrospective should hold it, and each comment should say
what the part is now.

## Group: firmware, installers, release, preflight, kernel_compare

### apothecary/firmware/devices.py -- moderate -- 8 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-4 | "Three views of one board, kept deliberately separate so the GUI can show" | stale / count | inline | The list below has five bullets (Detected, Probed, Expected, Observed, Identified). "Views of one board, kept separate so the GUI can show where they disagree:" |
| 113-115 | "two read-modify-writes interleaved used to drop each other's pins" | history | inline | "...both write the state file, and two read-modify-writes interleaved would drop each other's pins." |
| 338-340 | "the viewer's board model, a Machine and the firmware page each ask for it" | stale | inline | `/firmware` is a 307 to the viewer's Bench (`apothecary/api.py:2483`); there is no separate firmware page. Say "a Machine and the Bench". |
| 351-352 | "arduino-cli's "not installed", as it always was, when Rust is not installed either" | history | inline | "...the first one's refusal is the answer: arduino-cli's "not installed" when Rust is not installed either." |
| 639-641 | "Closing the link here killed the print under its thread and left the heaters on" | history (incident) | inline + retrospective -> apothecary: the printer link | "One lost reply mid-print is not a dead board: closing the link here would kill the print and leave the heaters on; ..." |
| 1237-1238 | "or from its bytes for a file kept before descriptions carried one" | history | inline | "The kept file's hash: from its description when it carries one, else from its bytes." |
| 1340 | "Open ``arduino-cli monitor`` processes, one per port, stoppable as a group." | stale | inline | `open()` runs `listener_argv`, which may be the Rust module's pyserial monitor. "Open serial-monitor processes (arduino-cli's or `serial_monitor.py`), one per port, stoppable as a group." |
| 1502-1503 | "some USB-UART bridges (seen on a CP2102 under a realtime kernel) occasionally hand back" | history (light) | inline | Keep the mechanism; state the hardware fact: "some USB-UART bridges (a CP2102 under a realtime kernel, for one) hand back bytes they already delivered". |

Checked: `state_file()` is `state_dir()/"firmware-state.json"` with `APOTHECARY_STATE_DIR` override (line 22 true);
the page re-listens after a task (`static/boards.js` `streamStopped` retries every `RETRY_MS`; line 1343 true);
`firmware printer` and `upload` CLI commands exist (line 114 true). Lines 162-163 ("the next save would have
erased...") and 1211-1212 ("the failure this exists to prevent") are present-tense rationale, not flagged.

### apothecary/firmware/models.py -- moderate -- 7 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 104-106 | "messages (the owner's decision of 2026-10-10)" | history (owner chose, date) | inline | Drop the parenthetical; the rule stands as stated. |
| 184-185 | "the fields above are Arduino's, as they were before there were modules." | history | inline | "Every toolchain module, Arduino's first; the fields above are Arduino's alone." docs/firmware.md:35 carries the same phrase ("as they always were"). |
| 326-328 | "the same printer came back as ``/dev/ttyUSB0`` after a night as ``/dev/ttyUSB1``" | history (incident) | inline + retrospective -> apothecary: the printer link | "A port name is the socket, not the board: the kernel may renumber it after a replug or reboot; the bridge's serial number stays." |
| 352-353 | "A record kept before a sketch was always named with its toolchain was an Arduino one's" | history | inline | "A record with no ``sketch_id`` (or one without ``@``) is an Arduino sketch's: name it ``<name>@arduino``." |
| 497 | "None for a file kept before it was recorded" | history | inline | "# of its bytes; None when its description carries none (``devices._sha256_of`` hashes the bytes then)" |
| 504-508 | "as it was kept before a print was a job. Nothing writes one any more" | history | inline | "A print record in the ``prints/records/`` format. Nothing writes one; ``jobs.py`` reads each once and carries it over as a print job." |
| 562 | "identity: str  # DeviceInfo.identity: MAC or port" | stale | inline | `DeviceInfo.identity` (line 323) and `Identity` (line 545) also allow the USB bridge's serial number: "MAC, bridge serial number, or port". |

Checked: `PRINTER_STATUSES` is `["idle", "printing", "offline", "maintenance"]` in `apothecary/example_hierarchy.py:96`
(line 421-422 true). `FlashRecord._named` does what 352-353 describes (the comment's fact is true; only its framing narrates).


### apothecary/firmware/modules/arduino.py -- moderate -- 3 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-4 | "What the seam was before there were modules, moved behind the interface and otherwise unchanged" | history | inline | "A sketch is `<folder>/<folder>.ino` with an optional `firmware.json`; a build names a board (its FQBN); ..." (keep the facts that follow). |
| 108-109 | "in the shape ``GET /firmware/status`` has always had" | history | inline | "...in the shape of `GET /firmware/status`'s top-level fields; never raises." |
| 194 | "Raises when arduino-cli is not there, with the message it always had." | history | inline | "Raises when arduino-cli is not there, saying so." |

### apothecary/firmware/gcode.py -- light -- 4 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 14-27 | "**The link is held open, and reset is explicit.** Creality boards wire DTR to reset" | duplicate | reference -> docs/firmware.md | Same explanation as docs/firmware.md "Reset is deliberate, never incidental" and "One holder per port". Keep two sentences and the pointer. |
| 541-543 | "a page reload (it lives in the server), so the monitor shows polls made by" | stale | inline | `/firmware/monitor` is a redirect; the log is a board's Machine's. "...so a board's Machine shows polls made by other clients too." |
| 610-612 | "waiting out real silences cost the unit suite a minute" | history / count | inline | "1 against hardware; the tests' scripted boards answer at once, so the tests set it near 0 rather than wait out real silences." |
| 1104-1105 | "It exists so the monitor's control overlay cannot heat or move a machine" | stale | inline | "...so a printer's Machine's control overlay cannot heat or move a machine from a stray click." |

Line 11 "passes the replaceability test" is present-tense rationale against the charter; not flagged. Line 54's
"Jan 17 2025" is a sample of a firmware's reply, data not history.

### apothecary/openscad_installer.py -- light -- 3 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 30 | "**Windows on ARM** is not supported yet (a planned item)" | history (plan in code) | inline | "**Windows on ARM** is not supported, nor is anything else; ..." The plan belongs in a plan or project/todo.md. |
| 317 | "Before install.json, an install was the AppImage itself, at <date>/openscad." | history | inline | "An install with no install.json is the AppImage itself, at `<date>/openscad`." (A present constraint: such installs exist on disk.) |
| 344-345 | "else the AppImage an install made before there was one" | history | inline | "...where `install.json` says it is, else the AppImage at `<date>/openscad`." |

Kept: 87-88 (OpenSCAD's own `--enable=manifold` spelling) and 244-245 ("In 2025 the AppImage carried a build number") are upstream history, §4.

### apothecary/firmware/api.py -- light -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 5-7 | "The pages this router served ... are the Bench and a board's Machine ... now" | history | inline | "``/firmware`` and ``/firmware/monitor`` are not this router's: they redirect to the Bench and a board's Machine (``apothecary/api.py``)." |
| 195-196 | "An Arduino sketch's FQBN, as the request names it (required, as it always was)" | history | inline | "An Arduino sketch's FQBN, as the request names it (required); None for a module's sketch..." |

Checked: the two redirects exist at `apothecary/api.py:2483` and `:2489`. Line 110 "shell out to arduino-cli /
esptool" is true (esptool is still used by `modules/arduino.py` and `cli/firmware.py flash-bin`).

### apothecary/firmware/modules/__init__.py -- light -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 10 | "Two modules today:" | count, history ("today") | inline | "The modules:" -- `_registry` is the list; the count drifts as modules are added. |
| 13-14 | "Its routes, messages and sketches are the ones the seam had before there were modules." | history | inline / delete | Delete, or "Its sketches are `<folder>/<folder>.ino`; `/firmware/*`'s top-level fields are its." |

### apothecary/firmware/rust_installer.py -- light -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 46-47 | "(The owner's decision of 2026-10-10, project/plans/rust-2026-10-08.md.)" | history (owner chose, date, plan) | inline | Drop the parenthetical; "The pins move by hand" stands as the rule. The bump procedure could also go to docs/firmware.md. |
| 664-666 | "an ``esp`` that is a folder of its own -- espup's install, before there was this --" | history | inline | "an `esp` that is a folder of its own (espup's install) is uninstalled by rustup first." |

### apothecary/kernel_compare.py -- light -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-4 | "The question (``project/plans/rust-geometry-kernels-2026-10-09.md``) is whether a kernel" | structural: dated plan as reference | reference → `docs/kernels.md` (new) | Same as `cli/kernels.py:31-33`. The plan retires to History; the question and the corpus get a present-tense page. |
| 700-703 | "These are where the first comparison starts, not findings: the first real run says" | history (a sequence of work) | inline | "Starting tolerances, not findings: each changes in a commit that records the run that justified it." |

### apothecary/firmware/serial_monitor.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3 | "The Rust module needs no arduino-cli (the owner's decision of 2026-10-10)" | history (owner chose, date) | inline | Drop the parenthetical. Same pattern as models.py:104-106 and rust_installer.py:46. |

### apothecary/firmware/service.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 34-35 | "The top-level fields are the Arduino module's, as they always were" | history | inline | "The top-level fields are the Arduino module's; `toolchains` holds every module's status, Arduino's first." |

### apothecary/firmware/scripted.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 10-11 | "They were the unit tests' alone; ``tests/firmware_helpers.py`` imports them from here now" | history | inline | "`tests/firmware_helpers.py` imports them from here: a command a person runs does not import from the tests." |

### apothecary/firmware/__init__.py -- light -- 1 passage (stale)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 5-10 | "The engines that actually compile and flash are bought ... ``arduino-cli`` ... and ``esptool``" | stale | inline | Two engines named; the Rust module drives cargo and espflash, and pyserial lists and monitors ports (`modules/rust_esp32.py`, `serial_monitor.py`). Name each module's engines, or point at `modules/`. |

### apothecary/release.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 10-14 | "and it was documented in only one direction: a contributor here had no way to learn" | history, duplicate | inline | "That clause binds this repository too: publishing is how geometry reaches the consumer. This module answers it with a command." Same story in `cli/release.py:3-7`. |

**Clean in this group:** `firmware/bindings.py`, `image_paths.py`, `installer.py`, `sketches.py`,
`tasks.py`, `toolchains.py`, `modules/rust_esp32.py`, `preflight.py`. Kept: `toolchains.py:181`
(arduino-cli 0.x vs 1.x output: upstream history); `preflight.py:9-11` ("a gap wearing a
reason") and `:32-33` ("each was observed by running preflight") are present-tense rules about
the entries.

**Group pattern -- "as it always was":** the toolchain-modules refactor left the same phrase
in eight places: `api.py:195-196`, `devices.py:351-352`, `models.py:184-185`, `service.py:34`,
`modules/__init__.py:13-14`, `modules/arduino.py:3-4, 108-109, 194`. docs/firmware.md:36 has
it too ("its other fields Arduino's as they always were"). One sweep commit fixes all of them.
"The owner's decision of 2026-10-10" appears three times (`models.py:106`,
`serial_monitor.py:3`, `rust_installer.py:46`).

## Group: routes, slicer, hierarchy, examples, shims, models, root modules

### apothecary/routes/part_edits.py -- moderate -- 8 passages (one stale, in /openapi.json)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 613-615 | "Where its parameters are kept: 'variant-file' (beside its SCAD); 'part-description' is a stub" | stale (an API field description) | inline | The default is `"text"` and `KEPT_IN` has no `variant-file` (`saved.py:150-165`). "Where its values are kept: 'text' (in its SCAD); 'part-description' is a stub, refused." |
| 4-5 | "The second and third iterations of project/plans/part-editing-in-the-browser-2026-09-27.md, server side." | history (plan citation) | inline | "The SCAD editor's server side (docs/viewer.md)." |
| 171-172, 609-610 (x2) | "Values on the side, from a caller before the text was the truth" | history (in /openapi.json) | inline | "Values sent on the side: written into the text first." |
| 312, 472 (x2) | "``params``, where a caller still sends them, are written into it first" | history ("still") | inline | "``params``, where a caller sends them, are written into it first". |
| 916, 967 (x2) | "A render from before the text was the truth had its values on the side." | history | inline | Name the format as in saved.py: "A render recorded with `params` (values on the side) ..." |

### apothecary/example_hierarchy.py -- moderate -- 7 passages (two stale)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 77 | "PRINTER_HEIGHT = ender3.OVERALL.z  # 576, with a spool on the holder" | stale | inline | `ender3.OVERALL.z` is 570 (`projects/parts/ender3.py:28`). "# 570, with a spool on the holder", or drop the number. |
| 654 | "and two boards the firmware seam can talk to" | stale, count | inline | `BENCH_BOARDS` (124) plus the mainboard is more than two. "and the boards the firmware seam can talk to". |
| 29-30 | "and that the newer additions (the building, fixtures, storage, CNC router)" | history | inline | "and that the rest (the building, fixtures, storage, CNC router) overlap nothing either". |
| 84-88 | "(the owner's decision of 2026-10-04: one printer in the garage for now)" | history (owner, date, "for now") | inline | Drop the parenthetical; the layout says one printer. |
| 154-159 | "Width (x) is doubled (3000mm -> 6000mm) by moving the east wall out" | history | inline | "Width is 6000 mm, set by the east wall; storage_shelving and cnc_router are placed from GARAGE_MAX.x so they stand against it." |
| 181-183 | "if that wall ever moves again -- see GARAGE_MAX's comment on why this needed updating last time." | history | inline | "so it stays flush against the east wall wherever that is." |
| 296-298 | "a shape the old Feature class (a leaf with no children slot at all) could not represent" | history | inline | "one level deeper than the record's four: Assembly is unbounded in depth." |

### apothecary/hierarchy.py -- moderate -- 5 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-11 | "It is additive: ``Scene`` and every existing primitive/boolean/transform are untouched. ... build on this module now" | history | inline | "A prototype under the draft hierarchy record. Scene and the primitives do not depend on it; the API and the parts library build on it." |
| 23-25 | "remain as the vocabulary — ... *worked example* of configuring the fractal model, not gone" | history | inline | "``Site``, ``Structure``, ``Substructure`` and ``Feature`` are the vocabulary: thin factories over ``Assembly``, ..." |
| 142-143 | "The single algorithm that replaces what the four fixed classes used to need three separate implementations for" | history | inline | "One algorithm for every level: gather positives ..." |
| 220-221 | "Generalizes what used to be Site-only overlap-checking" | history (gate hit) | inline | "Checks every level of the tree, not only a site's direct children: ..." <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| 76 | "used for the render comment and for future revision/diff messages" | history (plan in code) | inline | "used for the render comment". |

### apothecary/slicer/** -- light -- 7 passages (one stale)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| __init__.py:18-19 | "The routes are ``api.py``'s; the page's step comes later." | stale | inline | The page slices: Slice on a ring and the Machine's Print card (`static/widgets/machine.js:976`). "The routes are ``api.py``'s; the page's Slice is the Print card's." |
| __init__.py:3, compose.py:4-5, profiles.py:4-5, orcaslicer_installer.py:51-52 (x4) | "Decided with the owner on 2026-10-10 (project/plans/slicer-2026-10-10.md):" | history (owner, date, plan) | inline | Drop each; the bullets and rules stand as present facts. docs/slicer.md:5, 69 carry the same phrase (area 1). |
| modules/__init__.py:12 | "One module today:" | count, history | inline | "The modules:" (the registry is the list). Same as firmware/modules/__init__.py:10. |
| modules/orcaslicer.py:33 | "today ``home``, OrcaSlicer's own start for the printer" | history ("today") | inline | "printer_1's profile names ``home``: OrcaSlicer's own start, which homes and does no levelling; ..." |

Kept: `orcaslicer_installer.py:91-93` (the provenance of the pinned digests, which a reader needs to check a pin) and `:35-36` (upstream's own history).

### apothecary/routes/pictures.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 30-32 | "the cameras pinned at places before it, and the file they were kept in, are no longer read" | history | delete | Keep "A camera is a part standing in a site (vision/cameras.py, routes/cameras.py)." |

### apothecary/routes/menu.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 213-216 | "the loop from a picture to a print (project/plans/ui-flows-2026-10-08.md)" | history (plan citation) | inline | Point at walkthrough/13, which shows the loop, or drop the citation. |

**Clean:** `routes/views.py`, `routes/cameras.py`, `routes/jobs.py`, `routes/__init__.py`,
`slicer/api.py`, `slicer/service.py`, `slicer/models.py`, `example_parts_library.py` (apart
from its label), `shims/**`, `models/**`, and the root modules `__init__`, `__main__`,
`booleans`, `core`, `example`, `jscad`, `meshes`, `objects`, `primitives`, `scene`, `templates`,
`transforms`, `version`, `viewer` (`viewer.py:3-6` confirms the api.py:1380 stale finding:
composite nodes fetch their STL).

## The CLI: `apothecary/cli/**` and every `--help`

Read: all 21 modules' comments, docstrings and `help=` strings, and the `--help` of all 68
commands and groups (58 shown, 10 hidden), dumped with click from the worktree's own install
(`code-prose/help.txt`). The `--help` texts are the click docstrings and `help=` strings of
`apothecary/cli/*.py`, so a row below that is visible in `--help` says so ("in --help").

Verdict: the help texts are in good shape -- present tense, imperative or descriptive, each command
saying what it does and what it needs. The narration sits in module docstrings and a few
comments, and in two `--help` texts a person reads (`preflight`, `parts verify`). Three module
docstrings repeat their walkthrough page (preflight / 09, status / 07, release / 10) with
incident stories in them. `docs generate`'s docstring is stale: it names one workflow where
two are marked `docs`. `kernel-reference`'s help sends a reader to a dated plan.

### apothecary/cli/preflight.py -- moderate -- 4 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-6 | "CI is not a barrier on this repository -- `main` is unprotected and no ruleset" | duplicate | delete (keep walkthrough/09) | Same text as walkthrough/09-preflight.md:5-7. Docstring: "`apothecary preflight`: run the CI workflows here, before a push; walkthrough/09 says why." (Checked: main unprotected, 0 rulesets via `gh api`.) |
| 50-53 (in --help) | "which is how a green local suite hid a CI failure here more than once" | history | inline + retrospective → apothecary: CI and preflight | "...a fresh runner does not, so a green run here can still fail in CI." |
| 71-73 | "Five failing workflows all saying the same thing about a shell is noise" | count, ornament | inline | "Refuse to report gates red for a reason not about them: a missing shell would fail every workflow alike." |
| 119-123 | "That difference is not cosmetic -- in the sibling project, one workflow's `uv sync --locked`" | history, duplicate | inline + retrospective → apothecary: CI and preflight | "CI gives each job a fresh machine; here one workflow's `uv sync --locked` would strip the tools a later one needs." Story is in walkthrough/09:27 too. |

### apothecary/cli/docs.py -- moderate -- 2 passages (one of them stale)

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-9 | "**This does not produce the walkthrough.** ... It was produced here once" | history, ornament, stale | inline + retrospective → apothecary: the walkthrough and generated docs | "The walkthrough is written by the tests that assert it, not here. This writes the workflows marked `docs`: the fractal viewer and the printer monitor." Stale: "What is left here is the fractal viewer workflow" -- `tests/e2e/test_docs_printer_monitor.py:64` is also `@pytest.mark.docs`. Bold whole sentence is ornament. |
| 214-217 | "The picture walkthrough asks the server to look at a picture" | stale | inline (or delete with the env setting) | No test this command runs uses `picture_folder` (checked both `test_docs_*` marked `docs`; the photo walkthrough is not marked `docs`). Say what the folder is for now, or drop it. |

### apothecary/cli/status.py -- moderate -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 3-5 | "Colour and glyphs were being chosen per command, so the same outcome looked different" | history | inline | "These are the marks every command uses, so one outcome looks the same from any command, and the progress bar every long loop uses." |
| 23-24 | "Windows still defaults to cp1252 and this CLI has already died once on a check mark" | history, duplicate | inline | "The marks are ASCII: a Windows console defaults to cp1252, which cannot print a check mark." Same story at walkthrough/07-status-and-progress.md:17-18. |

### apothecary/cli/parts.py -- light -- 3 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 275-278 (in --help) | "and nothing has been keeping the two honest" | history, stale | inline | "A wrapper's get_bounds is hand-written beside hand-written OpenSCAD; this measures how far they differ, which is how wrong anything consuming the envelope is." (`checklist` and this command keep them honest now.) |
| 494 | "Otherwise, use template rendering (legacy/generic)." | history | inline | "Otherwise, the template's include stub." |
| 633 (in --help) | "Note: This imports STL files, not SCAD modules, for reliable rendering" | ornament | inline | Drop "Note:": "It imports STL files, not SCAD modules, so it renders however a part defines its modules." |

### apothecary/cli/release.py -- light -- 2 passages

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 5-7 | "a contributor here had no way to learn that until it was written down" | history | inline | End at "geometry reaches a consumer by publishing." walkthrough/10-being-depended-on.md holds the explanation. |
| 47-49 | "The consumer's side of this is already automated" | history (mild) | inline | "The consumer's side is automated: it reports the deviation while nothing is published and fails once something is." (A claim about datum; not checked from here.) |

### apothecary/cli/kernels.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 31-33 (in --help) | "(see project/plans/rust-geometry-kernels-2026-10-09.md and tests/test_kernel_comparison.py)" | structural: dated plan as reference | reference → `docs/kernels.md` (new) or docs/README.md "The Rust workspace" | Point at the present-tense page; the plan retires to History when finished. |

### apothecary/cli/server.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 97-98 | "The JSCAD viewer these named is served by no route; the flags do nothing" | history | inline | "`--viewer-path` and `--no-viewer` are accepted and ignored, hidden, until the next release, so scripts passing them keep working." |

### apothecary/cli/photo.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 536-538 | "Writing over somebody's notes because they used two different file names is not a thing to do once." | ornament | inline | Keep the first sentence; drop the last. |

### apothecary/cli/openscad.py -- light -- 1 passage

| line(s) | quote (<= 15 words) | problem | home | rewrite or note (<= 25 words) |
|---|---|---|---|---|
| 84 (in --help) | "Windows on ARM not supported yet" | history (mild: "yet") | inline | "Windows on ARM  not supported". |

**Clean:** `cli/__init__.py`, `census.py`, `firmware.py`, `inventory.py`, `main.py`, `render.py`,
`retired.py`, `slicer.py`, `spaces.py`, `system.py`, `testing.py`. Checked: `system.py:89-91`'s
"static 'Layout valid' chip" is still true (`templates/fractal_viewer.html.j2:702`).

**Kept, with reasons:** the 10 hidden retired commands (`dev`, `install`, `inventory`,
`photo look`, `submodules`, `system`, `test run-e2e`, `test setup-e2e`, `test validate-e2e`,
`testrun`) say "Retired: use X". A retired command exists to say that, so the text is a present
fact. `retired.py` and `photo.py:108` keep them "for one release", and no release has been cut
since 0.1.0 (CHANGELOG `[Unreleased]`), so that is still true. Deleting the stubs at the next
release removes the passages. `photo gather`'s "You are better at this than it is" (449-459, in
--help) is a claim that motivates `--answers`, not ornament.

