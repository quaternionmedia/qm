# Inventory: the page and the tests

Area: the comments in `templates/fractal_viewer.html.j2` and `apothecary/static/**/*.js` (vendor excluded);
the docstrings and comments in `tests/**/*.py` and `tests/e2e/*.py`; the comments in
`.github/workflows/*.yml`, `pyproject.toml` and `REUSE.toml`. Read at `wt-timeless`
(`build/timeless-docs`, c67725a). Every comment and docstring was extracted with its line
number and read; line numbers below are the source file's.

## 1. Verdict

**Moderate overall, concentrated, and almost all of it history.** About 308 narrating passages in
99 of the 164 files read (7 of 7 configuration files, 11 of 17 page scripts, the template, 53 of 97
unit-test files, 27 of 42 browser-test files); ornament is rare (a few capitals, one bold sentence)
and stale statements are few but real. The history takes three shapes. (1) **A test docstring that
tells its bug instead of its property** -- "used to ...", "Seen on the bench", "the review found",
"An earlier version ..." -- the largest group, heaviest in test_firmware_gcode, test_gathering,
test_working_together, the photo tests and test_onboarding; nearly every one already states the
property in its next sentence, so most fixes are a deleted sentence plus a retrospective line.
(2) **The page's consolidation story**: the monitor page, the firmware page, the cells Watch and
Monitor "had", the SCAD editor "where the read-only source stood", Load, Zoom Out and Regenerate STL
"gone". It is told in the template, machine.js, test_menu, test_one_machine, test_ring and
test_printer_ui -- the Watch/Monitor cell story at least four times. (3) **Provenance asides**:
dated plan citations and "(the owner's answer of 2026-10-xx)" in module headers, docstrings and the
ring's tests (roughly fifty plan mentions and thirty owner mentions by grep, the census ledger
included); each is a one-clause delete, and each will point at a retired plan once the plans move to
the History list. The page's own code (JS and template) is mostly clean present-tense prose; its
template keeps its history in the older navigation comments (axis swap, far plane, grid helpers,
the Contents tree). **Structural issues:** (a) `tests/test_census.py:14-460` is a ~450-line ledger in
a comment above one constant, and it is the only place the census's classification rules are
written down -- a reference page must exist before it is cut; (b) the three seed workflows are
byte-identical copies of qm's `project-seed/ci/`, so they are fixed upstream, and their shared
concurrency comment cites qm's own run counts as "this repository's", which is false here; (c) the
gate does not read `.j2` and matches "used to" with eight verbs only, so under `tests/` it reports 4
of these 236 test passages and none of the template's 35; (d) contradictions: doc_capture.py's
module docstring says it never writes on a normal run while its own `Walkthrough` class and the
conftest say every run writes its page; test_menu.py says the garage has thirteen pieces,
test_ring.py sixteen, and the code builds fourteen; test_menu.py:1959 says a camera is pinned at a
host while 1745 in the same file says it is a part; test_part_iteration.py says the server "does not
say yet" fields ParamField carries; the template's "all three printers" meets a garage of one.
**Walkthrough pages** are written by six browser tests (pages 11-16; listed under Browser tests),
whose page text is left to the walkthrough reviewer.

## 2. Files

### Configuration and CI

#### .github/workflows/adr-lint.yml -- moderate, 4 narrating passages
A seed file: byte-identical to qm's `project-seed/ci/adr-lint.yml` (diffed against the main
checkout's `governance/qm`). Every fix here is made in the qm seed and copied back, or the
"copy verbatim" contract breaks.

| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 22-26 | "codecartographer mounts it at docs/qm on its default branch to this day" | history / stale (another project's status); the sentence is also garbled ("so this is a / is named") | inline (in the qm seed) | "QM_SUBMODULE -- where this project mounts the governance submodule (governance/qm by default); named once here rather than per step." |
| 36-40 | "55 of this repository's 129 runs on 2026-08-11 came from five iterative pushes" | history + date + count; "this repository" is qm, so false in apothecary | inline (in the qm seed) | "A newer push to a pull request cancels the run it replaces." pytest.yml:11-12 already says it in two lines. |
| 3, 42 | "SEED FILE: copy verbatim"; "the run IS the record" | ornament (capitals for emphasis) | inline | "Seed file: copy verbatim ..."; "the run is the record of what that commit reported". |

#### .github/workflows/reuse-lint.yml -- moderate, 4 narrating passages
Seed file, identical to qm's `project-seed/ci/reuse-lint.yml`; same rule for fixes.

| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 11-13 | "and the gap the qmetronome onramp retrospective named" | history (provenance) | inline (in the qm seed) | End at "...cannot do": the retrospective is the corpus's, not this comment's. |
| 28-32 | "55 of this repository's 129 runs on 2026-08-11 came from five iterative pushes" | history + date + count; duplicate of adr-lint.yml:36 | inline (in the qm seed) | As adr-lint.yml: "A newer push to a pull request cancels the run it replaces." |
| 3, 34 | "SEED FILE"; "the run IS the record" | ornament | inline | Ordinary case. |

#### .github/workflows/submodule-check.yml -- moderate, 5 narrating passages
Seed file, identical to qm's `project-seed/ci/submodule-check.yml`. The `echo "::error::... Do NOT use 'git ls-remote'..."` at the end is a runtime message, not a comment; noted only (same capitals).

| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 12-16 | "Two QM projects have hit exactly that. qmetronome's v0.0.28 Alpha Release build broke" | history (who, when, how often; "apothecary hit the identical error on 2026-07-21") | retrospective → qm: the seed workflows | "Carried as a seed, so every QM project has it." The story fits the 2026-07-21 verify-before-fixing perspective or a seed retrospective. |
| 18 | "this check is SELF-CONTAINED rather than run from the governance submodule" | ornament | inline | "self-contained". |
| 31-35 | "55 of this repository's 129 runs on 2026-08-11" | history + date + count; duplicate (third copy) | inline (in the qm seed) | As adr-lint.yml. |
| 3, 37 | "SEED FILE"; "the run IS the record" | ornament | inline | Ordinary case. |

#### .github/workflows/license-check.yml -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 8-11 | "not the project's own (separately tracked) license metadata gap" | stale: pyproject.toml declares `license = "MIT"`, and LICENSE and LICENSES/MIT.txt exist (checked) | inline | "`apothecary` itself is excluded: this audits third-party dependencies; the project's own licence is declared in pyproject.toml and REUSE.toml." |

#### .github/workflows/pytest.yml -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 121 | "The browser tests write walkthrough pages 11 to 16." | count (true today: 11-16 are written by e2e modules; checked) | inline | "The browser tests write the walkthrough pages they demonstrate." A page 17 would make the range wrong silently. |

#### pyproject.toml -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 71 | "A deprecation in our own code is a failure now, not a warning nobody reads." | history ("now" narrates a change) | inline | "A deprecation warning raised from apothecary's own code fails the run." |

#### REUSE.toml -- moderate, 1 (one block)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 6-9 | "which is what this repository has claimed publicly since its README was written" | history (what was missing before); duplicate of the adoption-scope record §2 (`governance/qm/adr/DRAFT-constitution-adoption-scope.md`), which tells the LICENSE gap | delete (keep one line) | "MIT throughout, as README and LICENSE state; the reasoning is the adoption-scope record's." Lines 11-16 (datum's dependency, why not per-file headers) stay. |

### The page's scripts (`apothecary/static/**/*.js`, vendor excluded)

#### apothecary/static/anchors.js -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 23-24 | "(render on demand, the part-iteration plan of 2026-10-12)" | history: a dated plan cited as provenance | reference → docs/viewer.md | "(render on demand; docs/viewer.md)". When the plan retires, its decision lives in docs/viewer.md, and this pointer survives. |

#### apothecary/static/boards.js -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3-4 | "A board was drawn by six render functions and polled from four places" | history (what it replaced) + count | retrospective → apothecary: the viewer page | "Here a board is one record per port, which every drawer reads, so no two drawings of it disagree." |

#### apothecary/static/board_text.js -- moderate, 1 (two sentences)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 4-6 | "each used to write a board's state their own way -- the heater alone four times" | history ("used to write", "Each now writes"); the gate misses "used to write" | retrospective → apothecary: the viewer page (same story as boards.js) | "Every drawer of a board's state (the badges, Selected's Device line, the Machine, the device cards) writes it from here, so they agree." |

#### apothecary/static/machine_marks.js -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 248-251 | "the words the badge carried before it was an icon" | history | inline | "What a board's badge says: a printer's state, readings and job, a devkit's label and sketch; under them the board and its port." |

#### apothecary/static/panels.js -- light, 3 (one pattern)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 18-20, 65-67 (x3) | "a layout remembered from before the one rail (a left and a right rail)"; "a remembered panel the page no longer registers" | history phrasing a present behaviour | inline | State the constraint: "a remembered layout naming a left and a right rail is ignored whole"; "a remembered panel the page does not register is ignored". |

#### apothecary/static/widgets/assignments.js -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 2-3 | "(the part-iteration plan's "parameters and text, tied together", project/plans/part-iteration-2026-10-12.md)" | dated plan as provenance | reference → docs/viewer.md | Drop; the next paragraph already states the rule ("The text is the truth ..."). |

#### apothecary/static/widgets/machine.js -- moderate, 4
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3 | "A printer's Machine is what the monitor page was made of" | history | inline | "A printer's Machine: the header's link verbs and the control latch, the status cards, ..." |
| 41-43 | "(the monitor page, the other host, is a link to the world now)" | history ("now"); true: `/firmware/monitor` redirects (api.py:2489, checked) | inline | "`host` is "world"; /firmware/monitor opens the world's page with this Machine." |
| 34 | "(project/plans/slicer-2026-10-10.md)" | dated plan as provenance | reference → docs/slicer.md (exists) | "(docs/slicer.md)". |
| 27 | "mountMachine(root, { base, port, host, boards, kind, inPrinter, pin, say })" | stale: the function (line 250) also takes `variantFor` | inline | Add `variantFor` (a part drawn from an applied variant is sliced as drawn, line 972). |

#### apothecary/static/widgets/part_controls.js -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3 | "(the part-iteration plan of 2026-10-12, project/plans/)" | dated plan as provenance | reference → docs/viewer.md | Drop the parenthesis. |

#### apothecary/static/widgets/picture_list.js -- light, 2 (one pattern)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 8, 229 | "The gathering is a section of it until gathering leaves core (the pictures plan's Phase 1)" | plan forecast in present-tense text | inline | "The gathering is a section of it." The move belongs to the pictures plan. |

#### apothecary/static/widgets/scad_editor.js -- moderate, 3
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-3 | "where the part editor's read-only source stood in Selected (loop 2, the owner's answer of 2026-10-10" | history + owner's decision + date | inline | "The SCAD editor: a part's SCAD in CodeMirror 6, in Selected." The decision stays in the dated ui-flows plan. |
| 34 | "(the part-iteration plan's "parameters and text, tied together")" | dated plan as provenance | reference → docs/viewer.md | Drop; the sentence before it states the rule. |
| 181-183 | "one saved before its values were in its text does not, until it is saved again" | history explaining a constraint | inline | "a variant whose values are not in its text does not, until it is saved again." |

#### apothecary/static/widgets/sketches.js -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 67-68 | "Arduino's, as it was, when the status names none" | history | inline | "Arduino's when the status names none." |
| 138-140 | "each asked of a tool that is not there was a 503 in the console" | history | inline | "asking a tool that is not there answers 503 in the console." |

#### Clean (0): picture_marks.js, pictures.js, ring.js, widgets/pinned.js, widgets/tasks.js, widgets/toolchain.js

### templates/fractal_viewer.html.j2 -- moderate, 35 narrating passages in about 600 comments
The gate does not read `.j2` (its file types are .py, hash- and slash-commented files and .md), so
the largest prose file in this area is outside `--all`: line 988's "used to be" would be flagged if it <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory -->
were read. Most of the history lies in the older navigation code (axis swap, far plane, helpers, the
Contents tree) and is told as "the old ...", "used to", "now", and three duplicates of stories the
JS modules also tell.

| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 35-36 | "not as the longest one there is today: a site made from a picture no longer shifts" | history | inline | "As wide as the name of a site can be, so a long name never shifts the toolbar." |
| 313-317, 2507-2516, 2589-2597 (x3) | "same DOM shape as the old one-level Contents list"; "replacing the old flat, one-level Contents list" | history | inline | Drop the comparisons: "The hierarchy tree: indented rows, depth as left-padding; the caret is for browsing only." |
| 529-530, 5331-5345 (x2) | "in Selected where the read-only source stood"; "(loop 2, the owner's answer of 2026-10-10)" | history + owner + date; duplicate of scad_editor.js:1-3 | inline | "The SCAD editor: in Selected, floated over the world, or over the whole page." |
| 826-832 | "instead of the flat DEFAULT_COLOR every node used to share" | history | inline | "... category is what everything else falls back to before DEFAULT_COLOR." |
| 842-852 | "which was fine while every group was written into the program. It stopped being fine" | history (what was missing before) | retrospective → apothecary: the viewer page | "A group not in CATEGORY_COLORS gets a colour from its name: groups come from a picture's vocabulary, which grows. Same name, same colour." |
| 891-893, 4119-4134 (x2) | "(the part-iteration plan's timings)"; "The part-iteration plan's "parameters and text, tied together"" | dated plan as provenance | reference → docs/viewer.md | State the rule (the text is the one draft) and drop the plan's name. |
| 938-939 | "this prototype has no endpoint that reports the allowed set" | stale framing ("prototype"); the fact holds (api.py checks PRINTER_STATUSES, no route lists it; checked) | inline | "No endpoint reports the allowed set (example_hierarchy.PRINTER_STATUSES), so it is repeated here." |
| 985-988, 2347-2357 (x2) | "This used to be a fixed 20000 while the dolly clamp reached ~54000" | history + numbers from an earlier garage; told twice | retrospective → apothecary: the viewer page | "The far plane clears the dolly clamp plus the scene's extent behind the target; far and near both move per level." <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| 1027-1042 | "the "off by 90 degrees" orientation bug" | history (names a past bug) | inline | "Left uncorrected, a loaded STL's up lies along three.js's depth axis." |
| 1103-1111 | "in this exact example: all three printers have their own "belt_tensioner_boss"" | stale + count: `example_hierarchy.PRINTER_X_POSITIONS = [100.0]` builds one printer (checked) | inline | "bare names collide across siblings (every printer has its own belt_tensioner_boss)". |
| 1130-1133 | "or a migrated parts-library leaf" | history | inline | "or a parts-library leaf". |
| 1287-1293 | "Today that is the move arrows" | history ("today") | inline | "These are the move arrows ...". |
| 1334-1340 | "a remembered layout naming a panel that is gone (Jobs), or from before the one rail" | history; duplicate of panels.js | inline | "a remembered layout naming a panel the page does not register is ignored (panels.js)." |
| 1439-1444 | "what the firmware page was" | history | inline | Delete the aside (/firmware redirects to ?panel=bench, api.py:2483). |
| 1566-1574 | "drawn every frame, it had none to spare for typing" | history (past tense) | inline | "drawn every frame, it would have none to spare for typing." |
| 1770-1773 | "focusing alone left the panel unbuilt" | history | inline | "focusing alone leaves the panel unbuilt, so the leaf is selected too." |
| 1946-1950 | "therefore rendered an empty scene for the one thing a reader was asking" | history | inline | "A leaf has nothing beneath it, so a focused leaf renders itself: zooming into a part shows the part." |
| 2049-2053 | "they were never given spatial metadata, only geometry" | history (light) | inline | "they carry geometry but no spatial metadata". |
| 2307-2312 | "now a genuinely consistent global frame ... no longer needs the old maxZ/3 guess" | history | inline | "position and world_bounds share one global frame (api.py's _assembly_tree), so the true 3D centre is framed." |
| 2370-2380 (x2) | "the old standalone part viewer's updateHelpersForSize"; "further than the old 2.5x ... to the new clamp" | history | inline | "Rebuilt to what is in view; the ground reaches the dolly clamp, so it never ends mid-view." |
| 2518-2521 | "(a catalog of twenty parts)" | count (`apothecary census` computes it) | inline | "(a catalog's)". |
| 2929-2932 | "(the owner's word)" | history (owner's decision) | inline | Delete the parenthesis. |
| 3443-3445 | "Regenerate STL, which was Apply again, is gone." | history | delete | -- |
| 5437-5442 | "as a control's move always was" | history (light) | inline | "as a control's move is". |
| 5871-5879 | "(the bug this guard fixes: moving *any* item used to corrupt every already-real mesh" | history + a check described by what it caught | retrospective → apothecary: the viewer page | "This runs for every rendered node, so a real mesh is never re-scaled." |
| 5952-5954 | "A new object here moved the copy only, and the layout sent the old place." | history (past tense) | inline | "A new object here would move the copy only, and the layout would send the old place." |
| 7168-7188 | "same as the old standalone part viewer did" | history | inline | Delete the aside. |
| 7436-7437, 7687 (x2) | "what the monitor page's was"; "Watch and Monitor were this." | history | inline | Delete; the Watch/Monitor story is also apothecary/menu.py:1308 (code lane). |

### Unit tests (`tests/*.py`)

#### tests/conftest.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 10-16 | "where these options were first defined ... died on its own --start-server with "unrecognized arguments"" | history | inline (+ retrospective → apothecary: the test suite) | "Registered here, not in tests/e2e/conftest.py: pytest parses arguments before it loads a conftest below every named path, so an option there would not exist yet." |
| 162-167 | "waiting out a real board's silences (1.5 s settles, 5 s timeouts) was a minute of the run" | history (light) | inline | "... would add a minute to every run." |

#### tests/test_api.py -- moderate, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 128-133 | "/viewer no longer serves a standalone parts browser ... It used to redirect to whichever site sorted first" | history (the gate misses "used to redirect") | inline (+ retrospective → apothecary: the viewer page) | "/viewer redirects to api.py's DEFAULT_VIEWER_SITE, named, so registering a site never moves the front door." |
| 142 | "GET /parts/stl_renderer imported that module and answered 500." | history: the bug, not the property (the test asserts 404) | inline | "A part name from a URL is looked up, never imported: GET /parts/stl_renderer is a 404." |

#### tests/test_calibration_cube.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 86 | "An override without `size` reported a 20 mm cube; the SCAD's default is 10." | history (the bug) | inline | "An override without `size` keeps the SCAD's default 10 mm cube." |

#### tests/test_camera_parts.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 169-171 | "(the owner's decision of 2026-10-04)" | history (owner + date) | inline | Delete the parenthesis; the docstring already states the property. |
| 552 | "A host no longer offers Pin here; it offers Add here." | history | inline | "A host offers Add here, and no Pin here." |

#### tests/test_census.py -- heavy, 9 passages (one of them some 450 lines)
The heaviest passage in the area. Lines 14-460 are a per-phase ledger kept in a comment above
`VIEWER_CEILING`: every phase's before/after counts (computed by `apothecary census`), the owner's
answers with dates, branch merges, and every ring address that moved. The constant needs two lines.

| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 14-460 | "Pictures plan Phase 3, first commit ... Before: 137 controls of its own, 65 ring-backed" | history + count + owner's answers + dates + branch names | retrospective → apothecary: the page's controls and the ring; ring-address moves → CHANGELOG | Keep lines 14-16 only: "The viewer's controls of its own. A change that adds one raises this; one that removes one may lower it. `apothecary census` lists them." |
| 14-460 (within) | "census.TAKEN_BACK, the lasting exception for taking a thing back from the list that shows it" | still-true rules buried in the ledger (TAKEN_BACK, census.MARKS, what counts as a control) | reference → docs/viewer.md (or a new docs/census.md) | Move the classification rules to a reference page before the ledger is cut. |
| 763-764 | "Kept and the Gather panel are gone from the page ... so are the older panel's rows" | history | inline | "No row of a retired panel is in the tables." |
| 810-836 | "Consolidation Phase 2 held the ring-backed share where it was, 58 of 128" | history + count (every phase's share) | delete (the ledger's retrospective holds it) | "The ring-backed share does not fall below its floor; `apothecary census` gives the share." |
| 849, 888, 902, 950 (x4) | "Load and Zoom Out are gone from the header"; "the retired pages left nothing behind" | history-flavoured, but each names a property (absence) | inline | Keep as absence properties: "No control of the serial overlay ... is counted"; drop "gone"/"retired". |
| 14 | "The viewer's controls of its own today." | history ("today") | inline | "The viewer's controls of its own." |

#### tests/test_cli.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 49-50 | "`check` used to die on its first line for that reason." | history (gate misses "used to die") | delete the sentence | The docstring's first and third sentences state the property. |

#### tests/test_cli_guidance.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-3 | "(the onboarding plan, 2026-10-11)" | dated plan as provenance | inline | Drop the parenthesis. |

#### tests/test_contested_values.py -- heavy, 5
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3-9 | "`datum_core` had three. Two of them ... were disputed only by `parts/datum` ... this part replaced" | history | retrospective → apothecary: the datum parts | "A number two documents state differently is not settled by editing one." then the board_y paragraph. |
| 11-12 | "the black-box stub the seam serves today gives a specific 30 mm board" | history ("today") | inline | "the seam's black-box stub gives a 30 mm board." |
| 34-36 | "Retiring the part that disagreed is a resolution ... a dispute that no longer has two sides" | history | inline | "Wall thickness and fit clearance have one source, the house constants, so the index reports no dispute over them." |
| 95-98 | "The retired part's SCAD was cited by every candidate here" | history | inline | "Every candidate's citation names a file that exists: a citation is provenance only while a reader can look." |
| 108-111 | "a slider stopping exactly on it hands the user a value ... -- six of them did." | history + count | inline | Drop "-- six of them did." |

#### tests/test_datum_assembly.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 147-153 | "An earlier version filled in coordinates that were silently discarded, so every object rendered at the origin" | history | inline (+ retrospective → apothecary: scenes and rendering) | "Cube carries no position of its own; assert against the rendered SCAD, the artifact, since the model can look right while OpenSCAD's output is not." |

#### tests/test_defaults_are_the_scad.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1 | "(project/plans/part-iteration-2026-10-12.md)" | dated plan as provenance | reference → docs/parts-authoring.md | "A part's default is its SCAD file as saved (docs/parts-authoring.md)." Test name `test_no_part_has_none_today` also says "today". |

#### Clean (0): tests/firmware_helpers.py, tests/rendered_parts.py, tests/ring_helpers.py, tests/scripted_openscad.py, tests/slicer_helpers.py, tests/test_assignment_cases.py, tests/test_assignments.py, tests/test_browser_suite_is_not_gated.py, tests/test_catalog_geometry.py, tests/test_cli_extended.py, tests/test_cli_render_jscad.py (no prose), tests/test_cli_testing.py, tests/test_customizer_params.py, tests/test_datum_core_site.py, tests/test_demo.py

#### tests/test_docs_site.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 238-239 | "/walkthrough answered 404 (no README.md there) ... page 00 (Getting started) first once it is written" | history + stale: walkthrough/00-getting-started.md exists (checked) | inline | "/walkthrough is an index of its pages, in order, page 00 (Getting started) first." |

#### tests/test_example_parts_library.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-4 | "(prototype, unratified). Covers migrating the registered parts/ registry into leaf Assembly nodes" | status label that may be stale; "migrating" reads as history | inline | "Tests for the parts library as a fractal tree: each registered part a leaf Assembly node (apothecary/example_parts_library.py)." |

#### tests/test_failed_renders.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1 | "(project/plans/part-iteration-2026-10-12.md, item 1)" | dated plan as provenance | inline | Drop; the docstring states the rule in full. |

#### tests/test_firmware_api.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 31 | "/firmware leads to the viewer with the Bench open; the template is gone." | history | inline | Drop "the template is gone". |
| 40-41 | "The toolbar's Firmware and Monitor links went: Panels › Bench and a board's Machine replace them." | history | inline | "The toolbar links to no page of its own: Panels › Bench and a board's Machine are the ways in." |

#### tests/test_firmware_devices.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 399-400 | "Two read-modify-writes interleaved used to keep 12 of 200 pins and crash on a shared temp name." | history + count (gate misses "used to keep") | inline (+ retrospective → apothecary: the printer link) | "Interleaved read-modify-writes keep every record, and never share a temp name." |

#### tests/test_firmware_gcode.py -- heavy, 8
The bench's discoveries are told as "Seen on the bench" stories and "used to" bugs; each test states its property in its second sentence.

| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3-5 | "actually said over /dev/ttyUSB1 on 2026-09-19" | date + a port that moves, in a fixture's provenance (light) | inline | "replays a recording of a Creality mainboard running Marlin (TH3D UFW 2.94a), so the parsers meet real output." |
| 244-248, 1584-1588, 1648-1650 (x3) | "Seen on the bench: with HUPCL set the kernel drops DTR"; "the printer came back as /dev/ttyUSB0 after a night" | history (bench stories) | retrospective → apothecary: the printer link; inline | Keep each property: "With HUPCL set, the kernel drops DTR on close and the board reboots"; "A pin is kept as the bridge's serial number ..."; "`where` loads the site a pin names." |
| 975 | "--- review fixes: the monitor's address never reflects a raw port; polls carry the latch -" | history ("review fixes") | inline | "--- the monitor's address never reflects a raw port; polls carry the latch ---" |
| 1515 | "Its history is the printer's print jobs; the old record routes are gone." | history | inline | "Its history is the printer's print jobs; no record route answers." |
| 1709-1710, 1739-1740 (x2) | "One lost reply used to force-close the link under the print thread"; "The safe-off used to stop at its first unanswered line" | history (gate misses "used to force-close/stop") | retrospective → apothecary: the printer link; inline | "One lost poll reply mid-print keeps the link and the print"; "Every safe-off line is sent even when one goes unanswered: the heaters are among them." |

#### tests/test_firmware_modules.py -- light, 4
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3 | "The rust-2026-10-08 plan's *Firmware in Rust*:" | dated plan as provenance | reference → docs/firmware.md | "Each module says what it builds, finds its tools ... (docs/firmware.md)." |
| 65, 264, 322-323 (x3) | "Arduino first, as the seam was"; "the top level is Arduino's, as it was"; "as it always did" | history (light) | inline | Drop "as the seam was", "as it was", "as it always did". |

#### tests/test_firmware_ports.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 4 | "(the owner's decision of 2026-10-10)" | history (owner + date) | inline | Delete the parenthesis. |

#### tests/test_first_commands.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "the paths a newcomer takes first, which no other test walked" | history (what was missing before) | inline | "the paths a newcomer takes first: `serve` for real, the startup STL build, ..." |

#### tests/test_following_a_variant.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 2 | "(project/plans/part-iteration-2026-10-12.md, item 4)" | dated plan as provenance | inline | Drop. |

#### tests/test_garage_workbench.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 30-31 | "One printer for now (the owner's decision of 2026-10-04)" | history (owner + date); duplicated in test_geometry_from_elsewhere.py:215 | inline | "One printer: printer_1, which the real board is pinned to, at the bench's left end, the bench's middle clear." |

#### tests/test_gathering.py -- heavy, 12
The module's design is sound (each test names the mistake it holds shut), but the docstrings tell how
each mistake was found -- by "the meter", by "an independent reviewer" -- with counts of faults and folders.

| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3-5 | "Most of these are here because the meter, or a whole-folder run, caught something" | history | inline | "Each test names the mistake it holds shut, so removing one means arguing with the mistake rather than only with the test." |
| 438-445 | "An independent reviewer broke the first version ... twenty-four of twenty-seven deliberate faults" | history + count | retrospective → apothecary: photos and the gathering | Banner: "Each test below names the fault it holds shut." |
| 107, 519, 608-615 (x3) | "The exact failure the meter caught first."; "The escape hatch a reviewer walked through."; "the sorting built nine groups ... across fifteen folders" | history + count | retrospective → apothecary: photos and the gathering; inline | Drop each story sentence; the rest states the property. |
| 462-469, 478-486 (x2) | "A reviewer handed one folder in nine orders and got five different answers." | history; the two docstrings tell one story twice | inline | "The fit is as strict whichever picture comes first, so the answer does not depend on the order they arrive in." |
| 140-143 | "Requiring every match to fit threw away every real overlap" | history (an earlier rule) | inline | "Requiring every match to fit would throw away every real overlap, so the biggest agreeing set wins." |
| 629, 648, 672, 696 (x4) | "Pieces whose name does not end in a number were silently discarded."; "The upper of two was taken" | history: the bug, not the property | inline | State each property: "A piece whose name ends in no number is kept"; "The middle confidence of two is their mean." |

#### tests/test_gathering_accuracy.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 92-93 | "Measured at 18% to 41% of pairs answered, depending on what was drawn." | count (a measurement the run computes) | inline | "The floor sits below the lowest rate measured on the evidence folders, not at a rounder number." |

#### tests/test_geometry_from_elsewhere.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 214-215 | "One printer for now: the owner's decision of 2026-10-04." | history (owner + date); duplicate of test_garage_workbench.py:30 | delete | -- |

#### tests/test_gridfinity.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 213 | "Should be parts/gridfinity/gridfinity.stl, NOT inside submodule" | ornament (capitals) | inline | "parts/gridfinity/gridfinity.stl, outside the submodule". |

#### tests/test_hierarchy.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 158-160 | "a Feature (a leaf under the old model, with no children slot at all)" | history | inline | "Assembly is one recursive class: a Feature can carry a child Feature, so depth is unbounded." |

#### tests/test_job_api.py -- moderate, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3-6 | "A print is the job (consolidation Phase 3): the hand-typed queue ... is gone with its routes" | history | inline | "A print is the job: started by its machine's own route and listed here; nothing typed by hand marks a printer busy." |
| 165-166 | "(the owner's answer of 2026-10-10: kept, not shown in a job's row)" | history (owner + date) | inline | "(kept for the record, not shown in a job's row)". |

#### tests/test_jobs.py -- light, 3 (one pattern)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 4, 135, 204 (x3) | "the print records kept before jobs carried over as print jobs" | history phrasing of a present migration the code performs | inline | "a print record under prints/records is read as a print job" -- the constraint, without "before jobs". |

#### tests/test_jscad_renderer.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 57 | "The datum_core site holds a hull; rendering it raised TypeError." | history: the bug, not the property | inline | "A hull renders through JSCAD, as the datum_core site needs." |

#### tests/test_lighter_and_faster.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1 | "Lighter and faster (project/plans/part-iteration-2026-10-12.md, item 6)" | dated plan as provenance; the module is named for the plan item | inline | Start at "Binary STLs in the variant cache, ..."; the module name is a code decision outside this sweep. |

#### Clean (0): tests/test_e2e_shards.py, tests/test_finder_accuracy.py, tests/test_finder_geometry.py, tests/test_firmware_seam.py, tests/test_kernel_comparison.py, tests/test_made_part.py, tests/test_made_piece_geometry.py

#### tests/test_menu.py -- heavy, 25
The ring's tests carry the ring's address history: which cell Watch, Monitor, Fit or Float "had",
what moved "one level deeper", and the owner's answers with dates. The properties themselves are
sound; strip the provenance and keep the seat each option has.

| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 187 | "Only the outer ring used to be counted, so a submenu could hold twenty." | history; **flagged by `check_timeless.py --all`** | inline | "A submenu holds eight at most, as the outer ring does." <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| 136-145 | "This is the rule, not a nicety. Without it every dot was treated as a path separator" | history + ornament ("the rule, not a nicety") | inline | "Without it, every dot would be read as a path separator and `nozzle_0.4mm` would come back as `4mm`." |
| 421-426, 612-615 (x2) | "where hands learned it before Watch and Monitor became Open"; "Flash takes the cell Monitor freed" | history (address moves) | retrospective → apothecary: the ring and its addresses | "Control at 7, jog Y+ from a printer's node ⌗2728: an address people know by hand, so it stays." |
| 974-975, 986-991, 1020-1021 (x3) | "The canvas ring's Camera became Pictures, in the same seat"; "in the cell it has had since Phase 3"; "(it was 936)" | history | inline | State each seat: "Pictures sits after Pieces, Site, Group and View"; drop "since Phase 3", "it was 936", "no cell moved". |
| 1050 | "The retired panels are on no ring: the Comms log is in the Machine." | history (light) | inline | "No ring offers a Comms log: the log is in the Machine." |
| 1070-1074, 1110-1116, 1205-1214 (x3), 1278-1284, 1321-1322, 1431-1432 (x8) | "(the owner's choice of 2026-10-04)"; "(the owner's decision of 2026-09-27: no new ring shapes)"; "(loop 1's owner's answer)" | history (owner + date) | inline | Drop each parenthesis; keep the rule it carried where it is one ("the ring has no new shapes, so the floor's cells are under Pictures › Floor"). |
| 1110 | "(pictures plan, Phase 4)"; 1205 "(the part-editing spike's decision)" | plan provenance | inline | Drop. |
| 1252 | "the bench's ring ends as it did" | history (light) | inline | "the bench's ring ends with its own cells". |
| 1303-1304 | "The ring was full at eight: Float and Fullscreen are View's now, in the seat Float had" | history | inline | "A ring holds eight: Float and Fullscreen are under View, beside the ghost and Fit; History holds Undo and Redo." |
| 1467 | "(project/plans/slicer-2026-10-10.md)" | dated plan as provenance | reference → docs/slicer.md | "(docs/slicer.md)". |
| 1745-1746 | "A camera is no longer pinned at a place ... (Keep went before)." | history | inline | "A host's and the floor's Camera hold Add here alone; Take picture is a camera part's own." |
| 1882-1886 | "the level deeper the owner's decision accepts for the floor having no ring of its own" | history (owner) | inline | "the floor has no ring of its own, so its paths are a level deeper". |
| 1959-1960 | "the camera is pinned and takes pictures from its host's Camera" | stale: a camera is a part with its own ring (lines 1586, 1745 say so); also history ("left with") | inline | "No ring offers Allow at a host, Capture, Place, Unplace or Open as one." |
| 885 | "Thirteen pieces in the garage: two lettered groups, nothing lost." | count (not asserted; `_garage()` computes it, and the garage now has one printer) | inline | "Every piece of the garage, in lettered groups, nothing lost." |

#### tests/test_menu_routes.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 110 | "Flash holds Monitor's old cell, not to be chosen." | history | inline | "A printer keeps its own firmware: its Flash holds a cell and cannot be chosen." |

#### tests/test_param_controls.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "(project/plans/part-iteration-2026-10-12.md, item 3)" | dated plan as provenance | inline | Drop. |

#### tests/test_parameter_coverage.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 109-110 | "`-p knob_diameter=60` used to render the defaults and report success" | history (gate misses "used to render") | inline | "A name its SCAD does not declare is refused: OpenSCAD ignores an unknown -D and would render the defaults." |

#### tests/test_part_variants.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 257 | "`apothecary parts generate-stl -p x=12` left a variant as the part's STL." | history: the bug, not the property | inline | "A variant the command line made stays a variant: a later render never writes it over the part's STL." |

#### tests/test_parts_stl_generation.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 448 | "Should NOT be inside the submodule directory" | ornament (capitals); same as test_gridfinity.py:213 | inline | "Outside the submodule directory". |

#### tests/test_photo_hard_cases.py -- heavy, 6
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-7 | "Every test here came from an independent review ... Each one failed before it passed." | history | retrospective → apothecary: photos and the gathering | "The awkward inputs: ordinary photographs the friendly tests do not reach." |
| 47-48, 96-98, 137-138, 156, 196 (x5) | "Treating both as the width stretched every ordinary photograph by a third"; "Throwing it away built the panel a quarter turn out." | history: the bug in the past tense | inline | Present counterfactual or drop: "Treating both as the width would stretch it by a third." |

#### tests/test_photo_in_the_viewer.py -- heavy, 11
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3 | "The point of these is that almost nothing new had to be drawn." | history (light) | inline | "The viewer picks an arrangement by name, walks into it and filters by group: a piece's word as its group makes a filter by word." |
| 92-94, 100 (x2) | "without them the viewer drew a round cone"; "as finely as it always has" | history | inline | "without them the viewer would draw a round cone"; "as finely as any round primitive". |
| 114-118 | "A node gained no new fields, so the tree is the shape it always was" | history | inline | "What is known is in each piece's note, in words; a node carries no fields for it." |
| 194 | "The register held only what was decided in advance. A picture is not." | history | inline | "The register takes an arrangement it did not start with, as a picture's is." |
| 242-243, 287, 294, 301, 368 (x5) | "Naming it 'garage' used to replace the built-in garage, permanently."; "It used to hand back the same object" | history (four "used to" the gate misses) | inline (+ retrospective → apothecary: photos) | State each property: "A picture's arrangement cannot take a built-in name"; "Reset hands back a new object". |
| 354 | "The front door refused this. The serving door has to refuse it too." | history (light) | inline | "Import refuses this, and so does serving." |

#### tests/test_photo_shapes.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 349 | "The viewer calls this step Find shapes; the command took the same word." | history (light) | inline | "The command uses the viewer's word, Find shapes." |
| 469-470 | "A disc seen at 60-90 % of the picture was drawn half its size off" | history | inline | "A cylinder is already centred, so the words' corner shift does not move it: a disc is drawn where it was seen." |

#### tests/test_pictures_api.py -- light, 3
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 321 | "so two hundred pictures was minutes of one request" | history (light) | inline | "so two hundred pictures would be minutes of one request." |
| 328-330 | "the cameras file the pins were kept in is neither read nor written, and the old routes are gone" | history phrasing of an absence property | inline | "no cameras file is read or written, and no pin route for a camera answers." |
| 377-378 | "POST /photos/gather with build=true and name=garage replaced the viewer's default site" | history: the bug, not the property | inline | "A gathering never takes a built-in site's name: build=true with name=garage is refused." |

#### tests/test_primitives_transforms.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 56 | "A newline in a comment used to end the comment and start geometry." | history (gate misses "used to end") | inline | "A newline in a comment stays in the comment." |
| 68 | "Cylinder(r1=3) rendered `r=1` while the viewer drew a 3 mm cylinder." | history: the bug | inline | "Cylinder(r1=3) renders both ends at 3 mm, as the viewer draws it." |

#### tests/test_projection.py -- light, 5 (one pattern)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-6, 71, 134, 154, 179 (x5) | "as they always came out of their own formulas"; "is today's flat mat"; "where it always stood" | history: the mapping described against what came before it | inline | "a flat view's numbers come out of the mapping as its own formulas give them"; "is the flat mat". |

#### tests/test_readiness.py -- moderate, 4
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 77-80 | "were contested only by `parts/datum`, the single-piece tray this part replaced" | history; duplicate of test_contested_values.py:3-9 | delete | Keep "`board_y` is contested: both sources that disagree about the board are live." |
| 95-100 | "It once reported "no stubs remain" without looking ... the compound that replaced the single-piece `parts/datum`" | history | inline | "The stub check reads the assembly `build()` returns (a tuple); the bench drives `datum_core`, so that is where the stubs surface." |
| 109-110 | "`calibration_cube` was reported as fitted to datum's board" | history; same story as test_spaces.py:74 | inline | "A part the assembly does not place is told nothing of its stubs." |
| 312-316 | "Assuming `source_file.with_suffix('.stl')` looked in the wrong place" | history | inline | "Assuming source_file.with_suffix('.stl') would look inside the submodule, and a render there would leave untracked content in it." |

#### tests/test_render_queue.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "(project/plans/part-iteration-2026-10-12.md, item 7)" | dated plan as provenance | inline | Drop. |

#### tests/test_saved_variants.py -- moderate, 5
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1, 338 (x2) | "Save is a variant in git (decided 2026-09-27)"; "In its text (decided 2026-10-12)" | history (dates of decisions) | inline | Drop the parentheses. |
| 348 | "The file beside its SCAD is no place to keep them any more." | history | inline | "No file beside its SCAD keeps them." |
| 417-418, 468-469 (x2) | "A variant saved before the text was the truth: its values in its .variant.json" | history explaining a present compatibility case | inline | "A variant whose values are in a .variant.json beside its SCAD: ..." |

#### tests/test_site_api.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 146 | "one printer, for now" | forecast/history (light) | inline | "one printer". |
| 351-355 | "(edge 2: real geometry for composite nodes, not just leaves)" | an internal plan label a newcomer cannot resolve | inline | "(real geometry for composite nodes, not only leaves)". |

#### tests/test_slicer_api.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 368-369 | "asks the server on this machine, as the page will" | stale: the page slices now (machine.js Slice, POST /slicer/slice; checked) | inline | "asks the server on this machine, as the page does". |

#### tests/test_spaces.py -- moderate, 3
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 33-36 | "An adversarial pass found this: `KIND_OWNER['contested']` could be changed to anything" | history | inline | "The contested branch reads KIND_OWNER rather than typing the owner again: two places declaring one fact drift." |
| 74-75 | "`calibration_cube` was once reported as fitted to datum's board" | history; duplicate of test_readiness.py:109 | inline | "A part is told only about the black boxes it is fitted to." |
| 91-95 | "CI found this: on a fresh checkout nothing is rendered" | history | inline | "On a fresh checkout nothing is rendered: a bounds check that needs a render is not drift, which claims a comparison happened." |

#### tests/test_stays_local.py -- light, 3
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 314-315, 892-894 (x2) | "was seen to reach (strace of a real install, 2026-10-09)" | history (method + date of a measurement) | reference → project/validation/ (a dated record of each strace) | "Every host the Rust install reaches, and the step that reaches it; a build reaches none (project/validation/...)." |
| 330 | "espup's own update check went with espup" | history (light) | inline | "espup is not used, so nothing asks crates.io's API." |

#### tests/test_text_is_the_truth.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "(project/plans/part-iteration-2026-10-12.md, "parameters and text, tied together")" | dated plan as provenance | reference → docs/viewer.md | Drop; "The text is the truth, through the routes: ..." |

#### tests/test_the_walkthrough_is_named.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 46-48 | "(the loops plan, 2026-10-10)" | dated plan as provenance | inline | Drop; the reason (`apothecary test run` stays quick) is already given. |

#### tests/test_viewer_assets.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 46 | "Silence was the original defect; absence has to be visible." | history | inline | "A missing copy is said on the page, never left blank." |

#### tests/test_working_together.py -- heavy, 10
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 63-66 | "three tests here used to skip themselves ... how the whole question-ranking mechanism came to be deletable" | history + count | inline (+ retrospective → apothecary: photos and the gathering) | "Built by hand, so the tests that need an undecided pair never skip: a skip would let the ranking be deleted with the suite green." |
| 229-234 | "The way "a person's word wins" failed, on one answer and no odd input." | history | inline | Keep the scenario in the present and the last sentence: "A machine's disagreement is only a quarrel in a group the machine built." |
| 482-485 | "reading the composite size reported a question worth four as worth one" | history | inline | Drop the sentence; "merges the groups, not the composite" states the rule. |
| 642-645 | "and a reviewer pointed out the guard only covered half of it" | history | inline | "Both packages: the claim is about the whole path, and an import added to either half is caught." |
| 732-738 | "None of this was covered at all, which is how a mutation ... survived the whole suite" | history | retrospective → apothecary: photos and the gathering | Banner: "The command itself". |
| 795, 817, 830, 868-871, 931 (x5) | "The flagship refusal came out as thirty lines of internal detail."; "used to feed it its own examples" | history: the bug, not the property ("used to feed" missed by the gate) | inline | State each: "Disagreeing answers are refused in one line"; "Asking never replaces the answers file"; "A byte-order mark is read past". |

#### Clean (0): tests/test_models.py, tests/test_openscad_installer.py, tests/test_openscad_messages.py, tests/test_params_contract.py, tests/test_part_drafts.py, tests/test_parts_cli.py, tests/test_parts_parameters.py, tests/test_parts_wrappers.py, tests/test_picture_blanks.py, tests/test_picture_drift.py, tests/test_registry.py, tests/test_rust_installer.py, tests/test_scene_labels.py, tests/test_scene_render.py (no prose), tests/test_site_store.py, tests/test_slicer.py, tests/test_slicer_installer.py, tests/test_snowplow_part.py, tests/test_staging.py, tests/test_stl_renderer.py, tests/test_templates.py (no prose), tests/test_views_api.py

### Browser tests (`tests/e2e/*.py`)

**Tests that write walkthrough pages** (their page text is the walkthrough reviewer's and is skipped
here; their own docstrings and comments are inventoried below): `test_docs_photo_walkthrough.py` →
`walkthrough/11-photographs-into-pieces.md` and `test_docs_bench_walkthrough.py` →
`walkthrough/12-the-bench-as-it-is.md` (both marked `walkthrough`, run by `apothecary test run`);
`test_picture_to_print.py` → 13, `test_part_loop.py` → 14, `test_the_firmware_loop.py` → 15,
`test_scad_loop.py` → 16 (browser suite only). The writer is `doc_capture.py`'s `Walkthrough`,
through `conftest.py`'s `walkthrough` fixture. `test_docs_fractal_viewer.py` and
`test_docs_printer_monitor.py` write `docs/generated/` (only with `--generate-docs`), not the walkthrough.

#### tests/e2e/doc_capture.py -- moderate, 3
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-9 | "Only active when pytest runs with ``--generate-docs`` ... a normal test run ... never touches the filesystem here" | stale: the module's `Walkthrough` (line 270) writes its page on every run (conftest.py:416, this file's 221-233 say so; checked) | inline | "DocRecorder records only with --generate-docs; Walkthrough, below, writes its walkthrough page on every run of its test." |
| 239-241 | "and every run used to leave the tracked screenshots modified" | history (gate misses "used to leave") | inline | "a re-encode of the same picture is not a change, so an unchanged screenshot is left as committed." |
| 279 | "a loop's page (project/plans/ui-flows-2026-10-08.md)" | dated plan as provenance | inline | Drop the parenthesis. |

#### tests/e2e/picture_drift.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 26-30 | "Two runs of the walkthrough on one machine differed by a few dozen pixels ... (the commit that brought this check says by how many)" | history + a pointer into git history | inline | "Two runs on one machine differ by a few dozen pixels; a word of the hint bar is thousands." |

#### tests/e2e/test_bench.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-6 | "the firmware page's toolchain ... The consolidation plan's Phase 5 (project/plans/consolidation-2026-10-03.md)" | history + dated plan | inline | "The Bench: the toolchain, sketches, build and upload, raw flash and task log, a tab of the rail's strip; its verbs are cells of Panels › Bench." |
| 158-159 | "arduino-cli's install moved one level deeper (it was 936)" | history; duplicate of test_menu.py:1020 | inline | "Install is a ring of the toolchain modules, each with a cell of its own." |

#### tests/e2e/test_camera.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 17-18 | "The gathering is a section of Pictures until gathering leaves core." | plan forecast; same as picture_list.js:8 | inline | "The gathering is a section of Pictures." |

#### tests/e2e/test_docs_fractal_viewer.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 69-72, 150-151 (x2) | "which at the world's lower left was clipped by the canvas's edge"; "and covered the words above the heading" | history (past tense) | inline | "which the canvas's edge would clip at the world's lower left"; "and would cover the words above". |

#### tests/e2e/test_docs_photo_walkthrough.py -- moderate, 1 (writes walkthrough page 11)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 7-15 | "It used to be two demonstrations. A hand-written page of doctests walked the model half" | history; **flagged by `check_timeless.py --all`** (line 7) | retrospective → apothecary: the walkthrough | "The demonstration needs a browser and a server, everywhere, and the page says so." <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |

#### tests/e2e/test_edit_a_made_piece.py -- light, 2 (one pattern)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 120, 197-198 (x2) | "Regenerate STL, which was Apply again, is gone from both." | history; same as the template's 3443 | inline | "A made piece has no checklist; Apply is its rebuild." Drop the Regenerate STL mentions. |

#### tests/e2e/test_gathering_map_in_a_browser.py -- moderate, 3
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3-6 | "exactly the mistake this project has already made once: the viewer was read, believed, and did not work" | history | retrospective → apothecary: the viewer page | "So the map is driven rather than inspected: loaded with no network, in light and dark, every console message watched." |
| 79-82 | "The one that would have caught the viewer's own failure." | ornament (a check described by what it would catch) + history | inline | "Everything the page needs is inside it; with no network, this goes red here." |
| 229-230 | "Fifteen lines turns "somebody forgot" into a red build." | count + ornament (light) | inline | "The generator asserts its own artifacts exist, so a forgotten one fails the build." |

#### tests/e2e/test_less_on_screen.py -- moderate, 5
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "the cameras-and-clutter plan's Phase 2 (project/plans/cameras-and-clutter-2026-10-04.md)" | dated plan as provenance | inline | "Less on the screen: badges, handles, the Machine in the rail, one header row, problems once, the hint bar, walls." |
| 131-134 | "stood 30 px over their structures' middles and printed over each other. Each is an icon at its own spot now" | history | inline | "Each badge is an icon at its own spot -- the board inside the printer, the picture's corner -- and two in each other's way step aside." |
| 499-501, 609, 626 (x3) | "(choosing loads; Load is gone)"; "one ring down from where it was"; "where the list stood above Contents" | history | inline | Drop "Load is gone", "Zoom Out is gone", "from where it was", "where the list stood". |

#### tests/e2e/test_nothing_covers_a_control.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1 | "Nothing covers a control (the owner's word)" | history (owner) | inline | Drop the parenthesis. |
| 5-6 | "where it was once sticky over the parameters it heads" | history | inline | "The stage bar stands pinned above Selected's body, in its own space; squeezed, it scrolls in itself." |

#### tests/e2e/test_onboarding.py -- heavy, 6
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "What the onboarding review found a newcomer meets, through the page (project/plans/onboarding-2026-10-11.md)" | history ("the review found") + dated plan | inline | "What a newcomer meets, through the page: a printer's own Pin ..." |
| 313-314 | "A disabled Compile used to say only what it does" | history; **flagged by `check_timeless.py --all`** (line 313) | inline | "A disabled Compile says why it is disabled and what to do, and is enabled once that is done." <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| 280-283 | "Choosing parts_library put nothing in the address, so a reload went back to the garage" | history | inline | "The drop-down puts the site in the address, leaving the old site's focus, Machine and variants behind; a reload stays, Back and Forward go between." |
| 345-349 | "A printer's Device section said only "arduino-cli is not installed" ... it asks for neither now" | history | inline | "A printer says arduino-cli is wanted only to find its board, and the Bench asks for nothing it lacks a tool for." |
| 461-462 | "Walkthrough 11's last picture showed a Device row -- Query and Pin -- on a word piece" | history | inline | Start at "A piece made from a picture holds no board: ...". |
| 493-494 | "Only where a board belongs (the owner's word)" | history (owner); same as the template's 2929 and test_part_iteration_answers.py:505 | inline | Drop "(the owner's word)". |

#### tests/e2e/test_one_machine.py -- heavy, 8
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 3-12 | "The consolidation plan's Phase 4 ... the serial overlay is gone. Phase 5 (and the owner's decisions after Phase 4)" | history + plans + owner | inline (+ retrospective → apothecary: the ring and its addresses) | "A board's Machine is the one place for it -- state, one log, controls, pin, flashing -- read from one model that polls it once." |
| 95-96, 102-103, 142-143, 313-315 (x4) | "where Watch was; Monitor is gone"; "where hands learned them before Phase 4" | history (cell moves); duplicates test_menu.py:612 | inline | State the cells: "Device › Open opens the Machine; Flash, Query, Unpin, Rescan, Link, Control at 7: ⌗2728 jogs Y+." |
| 348-349, 513-514 (x2) | "as the monitor page's was"; "(The firmware page's device cards, each a board's Machine now.)" | history | inline | Drop both asides. |
| 228-229 | "The serial overlay, its toolbar toggle and the toolbar's look-for-boards tick-box are gone" | history phrasing of an absence property (light) | inline | "No serial overlay, toolbar toggle or look-for-boards tick-box; a browser that remembered the overlay open opens none." |

#### tests/e2e/test_part_iteration.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1 | "(project/plans/part-iteration-2026-10-12.md)" | dated plan as provenance | inline | Drop. |
| 9-11 | "What the server does not say yet -- a unit, an integer, a customizer's step, a choice" | stale: params.py's ParamField carries step, options, unit and integer (checked) | inline | "What the test parts do not declare -- a unit, an integer, a step, a choice, a vector -- is told to the page by answering its read." |

#### tests/e2e/test_part_iteration_answers.py -- moderate, 3
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "The page as the server now answers it (project/plans/part-iteration-2026-10-12.md, part 2's Phase B)" | history ("now") + dated plan | inline | "The page as the server answers it, through the page's own controls: ..." |
| 251 | "The owner's answer of 2026-10-12:" | history (owner + date) | inline | Start at "Part › Variants › a name is a ring ...". |
| 505 | "The owner's word: Selected's Device section is on a board" | history (owner) | inline | Start at "Selected's Device section is on a board ...". |

#### tests/e2e/test_part_loop.py -- light, 3 (writes walkthrough page 14)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1, 13-14, 702 (x2) | "Loop 1, designing a part (project/plans/ui-flows-2026-10-08.md)"; "(the loops plan)" | dated plan as provenance | inline | Drop the plan citations; "so `apothecary test run` stays quick" already gives the reason. |
| 198-199 | "that answer has been seen to take over 5 s" | history (an observation) explaining a constant | inline | "on a machine loaded with OpenSCAD runs, that answer can take over 5 s." |

#### tests/e2e/test_paths_people_take.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1 | "Paths a person takes that no other browser test walked" | history (what was missing before) | inline | "Paths a person takes: the bare /viewer address ... and a made piece's Print cell." |

#### tests/e2e/test_picture_in_the_world.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 190 | "Its words: the place, the picture drawn there, and what was found in it." | **flagged by `check_timeless.py --all`** ("was found in"): a false positive, a present description of the finder's result | inline | "... and the shapes in it." (or a `timeless: allow` with a reason) <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| 10 | "Phase 4 of the pictures plan pins it by a drop instead." | stale forecast: drops pin views now (test_the_loop.py:446); the fixture still pins through the API | delete | -- |

#### tests/e2e/test_picture_to_print.py -- light, 1 (writes walkthrough page 13)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "the fourth loop of the loops plan (project/plans/ui-flows-2026-10-08.md)" | dated plan as provenance | inline | "A picture to a print, round twice through the page, held end to end." |

#### tests/e2e/test_printer_ui.py -- heavy, 9
Its tests were written against the monitor page and kept when that page became the Machine; the docstrings still tell that move.

| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 9-10, 272-273, 520-522, 815-816, 1117-1120, 1133 (x6) | "the tests that drove the monitor page drive that Machine"; "The monitor page's board view held this; the world that replaced it holds it now." | history | inline | Drop each comparison: "the Machine's ids", "the world holds it", "m opens its device ring". |
| 519-521 | "(A node's STL arrives in its parent's frame; drawn untranslated, the printer sat a bench-width away.)" | history (the bug) | inline | "(A node's STL arrives in its parent's frame, so it is translated.)" |
| 908-909 | "A print record kept before a print was a job ... carried over as a print job" | history phrasing of a present migration (as test_jobs.py) | inline | "A print record under prints/records is in the printer's history as a print job." |
| 1149-1151 | "(A wall-clock bound here measured the machine's load, not the page.)" | history (light) | inline | "(A wall-clock bound would measure the machine's load, not the page.)" |

#### tests/e2e/test_render_on_demand.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "(the part-iteration plan of 2026-10-12)" | dated plan as provenance | reference → docs/viewer.md | Drop; render on demand belongs in docs/viewer.md. |

#### tests/e2e/test_ring.py -- moderate, 4
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 143-144 | "Open (the board's Machine) where Watch was, Flash where Monitor was ... where it was before Phase 4" | history; the fourth telling of the Watch/Monitor story | inline | "Device's cells: Open, Flash, ..., Control in cell 7." |
| 350-351 | "inside it the ring is its device ring, as the monitor page's was" | history | inline | Drop "as the monitor page's was". |
| 94 | "appended, so no cell above moved" | history (light) | inline | "appended after every cell above". |
| 450-452 | "Sixteen pieces: grouped in small lettered groups" | count; contradicts test_menu.py:885 ("Thirteen"); `create_example_site()` builds 14 top-level pieces (checked) | inline | "The level's pieces, grouped in small lettered groups ..." |

#### tests/e2e/test_scad_loop.py -- moderate, 3 (writes walkthrough page 16)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-3, 16 | "(project/plans/ui-flows-2026-10-08.md) ... in the editor where the read-only source stood" | history + dated plans | inline | "Loop 2, editing a part's SCAD, gone round in the page: ... its SCAD edited in the editor ..." |
| 361 | "the SCAD in an editor where the read-only source stood" | history | inline | "Part › Edit: the SCAD in its editor." |
| 674-681 | "The onboarding review found the way back stuck: after a SCAD edit, Part › Defaults staged" | history ("the review found") | inline | "After a SCAD edit nothing is staged; Defaults puts the part's own SCAD back, and Apply draws the saved part, the mark and ?variant= gone." |

#### tests/e2e/test_site_panel.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 8-9 | "Pinned is what Kept's pins list was (the pictures plan's Phase 5)" | history | inline | "Pinned lists every site's pins: a camera and a view pinned in garage are taken back ..." |
| 77-80 | "the retired panels are gone: ... Validation, OpenSCAD, Kept and Gather are no panels" | history phrasing of an absence property (light; test name too) | inline | Keep the property; the test name is a code decision outside this sweep. |

#### tests/e2e/test_text_tied.py -- light, 1
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 1-2 | "(project/plans/part-iteration-2026-10-12.md, "parameters and text, tied together")" | dated plan as provenance | reference → docs/viewer.md | Drop; the next sentence states the rule. |

#### tests/e2e/test_the_demo.py -- light, 2
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 11 | "**No real serial port is touched, and a test says so.**" | ornament (a whole sentence in bold) | inline | Ordinary case. |
| 410-413 | "it ran last of all, on a second demo of its own, and found none" | history (past tense) | inline | "without it, pytest would run it last, on a second demo, with none of the first one's pictures." |

#### tests/e2e/test_the_firmware_loop.py -- light, 2 (writes walkthrough page 15)
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 4-6, 14 (x3) | "Loop 3 of the flows plan (project/plans/ui-flows-2026-10-08.md)"; "(the loops plan, 2026-10-10)" | dated plans as provenance | inline | Drop; the stated reason ("so `apothecary test run` stays quick") stands. |
| 435 | "arduino-cli, as it was" | history (light) | inline | "arduino-cli's Install". |

#### tests/e2e/test_viewer.py -- light, 3
| line(s) | quote (≤ 15 words) | problem | home | rewrite or note (≤ 25 words) |
|---|---|---|---|---|
| 102-103 | "the breadcrumb is the way out (Zoom Out is gone)" | history | inline | Drop the parenthesis. |
| 247-250 | "The library was consolidated to underscore case after links to `datum-core` had been handed out." | history explaining a constraint | inline | "A link naming `datum-core` lands on datum_core: the lookup accepts the hyphen, and the redirect canonicalises the focus." |
| 296-297 | "(about 54000 on the garage)" | count, computed per level; the template's comment carries the same number as history | inline | Drop the number. |

#### Clean (0): tests/e2e/browsers.py, tests/e2e/conftest.py, tests/e2e/parts_built.py, tests/e2e/ports.py, tests/e2e/shards.py, tests/e2e/test_api_e2e.py, tests/e2e/test_assignments_in_the_page.py, tests/e2e/test_docs_bench_walkthrough.py (writes page 12), tests/e2e/test_docs_printer_monitor.py, tests/e2e/test_first_camera.py, tests/e2e/test_pictures_panel.py, tests/e2e/test_the_loop.py, tests/e2e/test_viewer_regressions.py, tests/e2e/test_world_resize.py, tests/e2e/viewer_ready.py

Out of scope but adjacent: `tests/e2e/README.md` is markdown, not in this area's list, and no other lane names it; it was not read.

### What `check_timeless.py --all` reports under `tests/`

Four findings, all `narrative` (run at `wt-timeless`, c67725a):

| finding | verdict | row above |
|---|---|---|
| `tests/test_menu.py:187: narrative: used to be` | true positive: history in a test docstring | test_menu.py, 187 |
| `tests/e2e/test_docs_photo_walkthrough.py:7: narrative: used to be` | true positive: the story of joining two demonstrations | test_docs_photo_walkthrough.py, 7-15 |
| `tests/e2e/test_onboarding.py:313: narrative: used to say` | true positive: the bug, not the property | test_onboarding.py, 313-314 |
| `tests/e2e/test_picture_in_the_world.py:190: narrative: was found in` | false positive: "what was found in it" is the finder's result, described in the present | test_picture_in_the_world.py, 190 <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |

The gate sees four of the 236 test passages listed here. It misses the many "used to" with other
verbs (`used to write / redirect / keep / force-close / stop / render / end / feed / leave / skip /
print / replace / remove / hand back / die / share` -- well over a dozen in this area), every "Seen on the
bench", "the review found", "(the owner's answer of ...)", and every plan citation. It does not read
`.j2` at all, so `templates/fractal_viewer.html.j2` (35 passages, among them a literal "This used to
be a fixed 20000") is outside `--all`. A gate that widened `used to` to any verb, and read `.j2` as
slash- and HTML-commented, would catch most of the "used to" rows without new false positives in
this area.

## 3. Retrospectives this area needs

Each is one dated file in the qm corpus's `perspectives/`.

**apothecary: the viewer page**
- Six render functions and four pollers drew one board and disagreed; one board model and one writer replaced them (boards.js:3, board_text.js:4).
- The far plane, fixed at 20000, clipped the garage when the dolly clamp reached ~54000 (template 985, 2347).
- A group named from a picture's vocabulary got no colour and no filter chip, so it was invisible (template 842).
- Moving any item re-scaled every real mesh on screen into a screen-filling artefact (template 5871).
- /viewer redirected to whichever site sorted first, so registering a site moved the front door (test_api.py:128).
- The viewer was read and believed and did not work offline; the gathering map is driven instead (test_gathering_map_in_a_browser.py:3, 79).
- The board and place badges printed over each other at the garage's top level (test_less_on_screen.py:131).
- The monitor page and the firmware page became a board's Machine and the Bench; Regenerate STL, Load and Zoom Out went (machine.js:3, template 1439, test_printer_ui.py, test_one_machine.py, test_edit_a_made_piece.py:197).

**apothecary: the ring and its addresses**
- Watch and Monitor became Open; Flash took Monitor's cell, so Control returned to 7 and ⌗2728 survived (test_menu.py:421, 612; test_one_machine.py:313; test_ring.py:143).
- The census ledger: every phase's control counts, ring-backed share and address moves (test_census.py:14-460, 810).
- The owner's answers that seated View, Variants, Print and the Device section (test_menu.py, test_part_iteration_answers.py:251, 505).

**apothecary: the printer link**
- With HUPCL set the kernel dropped DTR on close and the Ender rebooted on the next open (test_firmware_gcode.py:244).
- The port renumbered overnight and a pin made by port name pointed at nothing (test_firmware_gcode.py:1584).
- `where` said nothing was pinned before the garage had loaded (test_firmware_gcode.py:1648).
- One lost poll reply closed the link under a print; the safe-off was never sent and the heaters stayed on (test_firmware_gcode.py:1709).
- The safe-off stopped at its first unanswered line (test_firmware_gcode.py:1739).
- Interleaved writes of the state file kept 12 of 200 pins (test_firmware_devices.py:399).

**apothecary: photos and the gathering**
- An independent review broke the picture path; every hard-case test failed before it passed (test_photo_hard_cases.py:1).
- A mutation review: 24 of 27 injected faults were caught by nothing (test_gathering.py:438).
- One folder in nine orders gave five answers (test_gathering.py:462, 478); one matching shape made two photographs one thing (519).
- Self-skipping tests made the question ranking deletable with the suite green; --answers was ignored and --ask overwrote notes (test_working_together.py:60, 732).
- A picture's arrangement named 'garage' replaced the built-in site (test_photo_in_the_viewer.py:287; test_pictures_api.py:377).

**apothecary: the datum parts**
- Retiring `parts/datum` settled wall thickness and fit clearance; `board_y` stays contested (test_contested_values.py:3; test_readiness.py:74).
- The stub check read build()'s tuple as an Assembly and reported "no stubs remain" (test_readiness.py:94).
- calibration_cube was reported as fitted to datum's board (test_readiness.py:108; test_spaces.py:74).
- Scene objects rendered at the origin while the Python model looked right (test_datum_assembly.py:147).

**apothecary: the test suite and the walkthrough**
- Options defined in tests/e2e/conftest.py made `pytest tests walkthrough` die with "unrecognized arguments" (tests/conftest.py:10).
- Two demonstrations, one of them stale behind a remembered command, became one walkthrough written by its run (test_docs_photo_walkthrough.py:7).
- A re-encoded screenshot left the tracked pictures modified on every run (doc_capture.py:239).

**qm: the seed workflows** (the qm corpus's own, since the three files are verbatim seed copies)
- qmetronome's v0.0.28 build and apothecary on 2026-07-21 both hit "not our ref"; the check was carried as a seed (submodule-check.yml:12-16).
- 55 of 129 runs on 2026-08-11 came from iterative pushes, which set the concurrency rule (adr-lint.yml:36, reuse-lint.yml:28, submodule-check.yml:31).

## 4. Reference pages this area needs

- **docs/viewer.md** (exists) already states render on demand (line 88), the ring (line 94) and "The parameters and the SCAD are one draft" (line 195). Every plan citation for those decisions in anchors.js, assignments.js, part_controls.js, scad_editor.js, the template (891, 4119) and the tests (test_text_is_the_truth.py, test_render_on_demand.py, test_text_tied.py) can point here instead. Check that the part editor section also states the staging rules (check on rest, Apply renders, ghost, recent applies) before the plans retire.
- **docs/census.md** (to be made, or a section of CONTRIBUTING.md): what `apothecary census` counts -- controls of its own, ring-backed, places the page listens, `census.MARKS`, `census.TAKEN_BACK` as the lasting exception -- and how the ceiling and the share's floor move. Today those rules exist only inside the ledger at test_census.py:14-460.
- **docs/slicer.md** (exists): Slice as a step of the page, the target of machine.js:34 and test_menu.py:1467.
- **docs/firmware.md** (exists): the toolchain modules, the target of test_firmware_modules.py:3.
- **docs/parts-authoring.md** (exists): "a part's default is its SCAD as saved", the target of test_defaults_are_the_scad.py:1.
- **project/validation/** (dated, exempt): a record of each strace that fixed an installer's host list (test_stays_local.py:314, 892), so the test can cite it instead of carrying the date.

## 5. Suggested order

1. **The seed workflows, upstream first** (adr-lint, reuse-lint, submodule-check): fix in qm's `project-seed/ci/`, re-copy. Three duplicate concurrency comments, two capitals, one stale aside, one story. Smallest, and every QM project gains.
2. **pyproject.toml, REUSE.toml, license-check.yml, pytest.yml**: four one-line edits, one of them a stale claim.
3. **The four gate findings** (test_menu.py:187, test_docs_photo_walkthrough.py:7, test_onboarding.py:313, test_picture_in_the_world.py:190): the measure moves from 4 to 0 under tests/.
4. **The stale rows** (doc_capture.py:1-9, test_menu.py:1959, test_part_iteration.py:9, test_slicer_api.py:368, test_docs_site.py:238, test_picture_in_the_world.py:10, machine.js:27, template 1103, license-check.yml:8, test_menu.py:885 vs test_ring.py:450): each says something false today.
5. **JS module headers** (11 files, 20 passages): most-read by anyone opening the page's code; mostly plan citations and one-clause history.
6. **The template**: the old navigation comments (axis, far plane, helpers, Contents tree) and the four retellings of the monitor/firmware pages; 35 passages in one file.
7. **Unit tests, light files first**, then the heavy ones in one PR each with their retrospective drafted alongside: test_firmware_gcode.py (the printer link), test_gathering.py + test_working_together.py + test_photo_*.py (photos), test_contested_values.py + test_readiness.py + test_spaces.py (datum), test_menu.py (the ring).
8. **test_census.py's ledger last**: write docs/census.md and the ring retrospective first, move the ring-address moves to CHANGELOG if they are wanted there, then cut lines 17-460 to the two-line rule.
9. **Browser tests**, with test_printer_ui.py, test_one_machine.py and test_onboarding.py after the viewer-page retrospective exists.
