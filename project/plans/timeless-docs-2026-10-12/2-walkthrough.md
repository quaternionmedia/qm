# Inventory: the walkthrough (`walkthrough/00`–`16`)

Read at `wt-timeless` (`build/timeless-docs`, c67725a). `check_timeless.py --all` finds two
lines in this area: `05-contested-numbers.md:30` ("until recently") and <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory -->
`tests/e2e/test_docs_photo_walkthrough.py:7` ("used to be"). Everything else below was found <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory -->
by reading the files.

## 1. Verdict

The hand-written pages 00–10 are mostly in the present tense, and their doctests hold their
facts. Seven of them (04, 05, 06, 07, 08, 09 and 10) still carry internal history in plain
words: what replaced what, what a review found, how often something failed. Nearly every
time, the history is there to justify a constraint that can be stated as a present fact. A
few pages have light ornament ("the whole point", "the part that matters"). Pages 11–16 are
generated, and only page 11 carries history. They do have three §1 failures that the shared
header hides:

- **Page 14.** The "does not show" list says the words leave out which OpenSCAD measured,
  but steps 1, 3 and 11 print "(read from the STL)".
- **Page 15.** Step 1 prints `undefined: not installed`. The test reads `data-id`, but the
  slicer card carries `data-slicer`.
- **Page 16.** Steps 4 and 7 print a folder that changes from run to run
  (`/tmp/piP/w3/server2/variants.git`; the previous commit had `w2`). CI's
  `git diff --exit-code -- 'walkthrough/*.md'` (pytest.yml:122) cannot reproduce it.

The header on pages 11–16 ("Every sentence below was emitted by a test that had just
asserted it") overclaims. The intro, the runtime note, the STL sentence and the "does not
show" list are fixed strings, and that is how page 14's bullet went stale.

There are also structural problems:

- **Mixed audiences.** The numbered sequence mixes four audiences: setup (00), library
  concepts through `datum_core` (01–06, 08), contributor and maintainer process (07, 09, 10),
  and demonstrations (11–16).
- **Routing.** Page 00 sends a newcomer to 13–16 first and then "01 onward". It never
  mentions 11 or 12, and its summary of 01 onward leaves out 07, 09, 10, 11 and 12.
- **Missing reference pages.** Pages 09 (preflight) and 10 (releases) are contributor policy
  with no reference page in `docs/`.
- **Duplication.** Pages 05, 06 and 08 present the one `board_y` dispute three times. Pages
  04 and 05 both doctest the one-page redirect. Pages 02 and 05 restate the part editor,
  which page 14 and `docs/viewer.md` already describe.
- **Inconsistencies.** Page 00 serves on port 8000, while 02–04 use 8765. Page 02 sends the
  reader to page 04 to select a part, but page 14 covers that.

## 2. Tables

Problem kinds: history / ornament / stale / duplicate / count. A row marked **ok** is a
passage of a generated page that needs no edit; it is listed for its source line. On the
hand-written pages, lines without a row are clean.

### 00-getting-started.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 88–93 | "one rail beside it holds Site … and Selected, over a strip of tabs" | duplicate | reference → `docs/viewer.md` (its rail section, :161–178) | Keep one sentence: the page opens on the garage, and [the viewer] describes its controls. |
| 97–99 | "so the words there are what the page says today" | stale (overclaim; see the header row) | inline | "…each written as it goes by the browser test that walks it." |
| 108–114 | `"rewritten by every run of the browser suite" in page…` | coupling | inline | The doctest quotes doc_capture.py:348. Change both in one commit, or this doctest fails. |
| 156–162 | "Page 01 onward is the library's tour: what a part is…" | stale (incomplete) | inline | The list leaves out 07, 09, 10, 11 and 12. Name each, or route by the regrouping in §6. |

### 01-a-part.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 28–29 | "and — the part that matters to anything assembling around it — an envelope" | ornament | inline | "…a description, a category and an envelope, the box anything assembled around it relies on." |
| 46–48 | "It exits non-zero on drift, so it belongs in CI." | stale (no workflow runs `parts verify`; I grepped `.github/workflows/`) | inline | "It exits non-zero on drift, so it can gate a build." (Page 06:88 says the same.) |

### 02-fitting.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 5–6 | "and the split is the whole seam" | ornament | inline | "…every dimension in it is one of two kinds:" |
| 39–41 | "it can only be edited, which is the loop this tooling replaces" | history | inline | "A number only in the SCAD cannot be staged or validated, so every top-level number has a parameter (`tests/test_parameter_coverage.py`)." |
| 51–53 | "`datum_core` carried six of those after the cover moved to `datum_cap`" | history | retrospective → apothecary: the datum parts | End the sentence at "renders nothing when moved." |
| 79–86 | "and **Apply** is the only thing that renders" | stale (a SCAD edit renders 300 ms after its check passes, and F5 renders too: page 16, steps 3 and 11) | inline + reference → `docs/viewer.md` | "A parameter renders on Apply." The rest repeats page 14 (steps 3–9) and viewer.md:71; link to them. |
| 113 | "`apothecary serve`, then select the part — page 04" | stale (wrong pointer) | inline | Page 04 does not select a part. Point to page 14. |
| 118 | `uv run apothecary serve --port 8765` | stale (00 and the README use the default 8000) | inline | `uv run apothecary serve`. |

### 03-an-assembly.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 68–70 | `curl localhost:8765/sites` … | stale (port) | inline | `localhost:8000`, the port page 00 starts. |

### 04-serving-it.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 17–19 | "rather than waiting for someone to drag something" | history (contrast with an earlier behaviour) | inline | "…so Site's SCAD section fills on load:" |
| 25–30 | "Loading three.js from a CDN meant the page worked only for a browser…" | history | retrospective → apothecary: the viewer; inline | "The viewer serves three.js itself, so the page draws with no network:" Keep the `jsdelivr` doctest. |
| 43–45 | "The firmware page's address opens it… the printer monitor's with that board's Machine" | history (names retired pages) | inline | "`/firmware` opens the viewer with the Bench in front, and `/firmware/monitor?port=…` with that board's Machine." (Checked: api.py:2489.) |
| 55 | `apothecary serve --port 8765` | stale (port) | inline | `apothecary serve`. |

### 05-contested-numbers.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 28–37 | "This page listed three until recently. `walls` and `tolerence` were disputed…" | history (flagged by the gate) | retrospective → apothecary: the datum parts | Delete the story and its walls/tolerence doctest; page 02:19–21 already pins those values. <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| 39–43 | "That is a real resolution, not a silencing…" | history around a principle | reference → `docs/fitting-a-part.md`; inline | Keep the rule: "A candidate's source must be readable; a candidate citing a deleted file is removed with it." |
| 45–49 | "That is the whole reason… The wall thickness is settled now" | ornament + history | inline | Show the consequence with `board_y` (40 vs 30 mm of envelope) instead of the retired `walls=2.4`. |
| 57–61 | "Selected carries every parameter as a control, contested ones first" | duplicate (`docs/viewer.md`, page 14) | reference → `docs/viewer.md` | One line and a link. Contested-first is still true (template :4077). |
| 63–71 | "there is no second page onto the same object" | duplicate (page 04, "One page") + history | delete; move the doctest to 04 | Keep the `/viewer/parts/<name>` redirect beside page 04's `/firmware` doctest. |
| 88–90 | "the endpoint and the dashboard read the declaration" | stale (no page is called a dashboard; the controls are in Selected) | inline | "…`/parts/<name>/params` and the part's controls in Selected read it." |

### 06-ready-to-build.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 23 | "Three states, and the middle one is the whole point." | ornament | inline | "Three states: pass, blocked and unknown (readiness.py:34–36). `unknown` means the check could not run…" |
| 31–36 | "This module shipped that defect twice. First it read `build()`…" | history | retrospective → apothecary: build readiness | Delete. Lines 24–25 already state the constraint ("never counts as ready"). |
| 38 | "It is part-specific now" | history ("now" marks a change) | inline | "The stub check is per part, and its answer differs between parts:" |
| 51–54 | "It did not always: the seam arrived with `parts/datum`…" | history | retrospective → apothecary: the datum parts | End at "inherits the board and mounting-surface stubs." |
| 59–61 | "Note which way round the good news runs" | ornament | inline | "The pass belongs to the part with no claims on it; the unknown to the one with unmeasured dependencies." |
| 69–71 | "page 05 is where that is turned" | duplicate (the `board_y` dispute is on 05, 06 and 08) | inline | Keep as a link; see §6 for merging 05, 06 and 08. |

### 07-status-and-progress.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 17–19 | "this CLI has already died once on a check mark" | history | inline; retrospective → apothecary: preflight and CI | "A Windows console defaults to cp1252, which most glyphs are not in, so every mark goes through `_safe_echo`." |
| 19–22 | "Click is in the blessed set… an org-level record it would not earn here" | present constraint, wrong home | reference → `CONTRIBUTING.md` (dependencies) | Move it to where dependencies are decided. |
| 44 | "one OpenSCAD render per part, tens of seconds each" | stale (the time depends on the OpenSCAD; page 00 installs a fast one) | inline | "one OpenSCAD render per part". |
| whole page | — | structure | reference → new `docs/cli.md` (or `CONTRIBUTING.md`) | A page for someone writing CLI commands, not a newcomer step. Its doctests can stay as a page there. |

### 08-problems-and-solutions.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 28 | "The interesting field is who can close it:" | ornament | inline | "Each problem names who can close it:" |
| 34–38 | "Four owners, and each means something different…" | duplicate (`docs/fitting-a-part.md`, "who owns each open problem") | reference → `docs/fitting-a-part.md` | Keep one statement of the owners; link from here. |
| 52–57 | "It did not always. An adversarial pass changed `KIND_OWNER[\"contested\"]`…" | history (what a review found) | retrospective → apothecary: build readiness and the problems index | "Every problem's owner is read from `KIND_OWNER`; no kind names its own:" Keep the doctest. |

### 09-preflight.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 5–8 | "`main` is unprotected, no ruleset is applied" | stale-prone (a GitHub setting; not checked, since that needs the network) | reference → `CONTRIBUTING.md` | Quote the corpus rule (gates are signals); leave the repository settings out of the text. |
| 25 | "That is not tidiness:" | ornament | inline | Drop it. |
| 26–29 | "In the sibling project that difference was not theoretical — one workflow's `uv sync --locked`…" | history (another project's incident) | retrospective → apothecary: preflight and CI | Keep: "the runner shares one environment where CI gives each job a fresh machine." |
| 72–73 | "The same check catches the quieter failure" | describes a check by what it catches | inline | "It also reports an excuse whose workflow was renamed or deleted." |
| 77–82 | "this repository has been caught by it more than once: an `npm ci` step…" | history (how often it failed) | retrospective → apothecary: preflight and CI | Keep: "`uses:` steps are not reproduced, and the runner image is not this machine." |
| 84–91 | "which has not had a propagation merge since 2026-08-11" | date in present tense (true at the pin, 20e00bd; qm main has `resolve_bash()`) | inline | "On Windows, the pinned runner's bare `bash` reaches WSL's alias. The fix is on qm `main` and arrives with the next propagation merge." |
| whole page | — | structure | reference → `CONTRIBUTING.md` (or a new `docs/preflight.md`) | Contributor process, not a newcomer step. |

### 10-being-depended-on.md

| line(s) | quote | problem | home | rewrite or note |
|---|---|---|---|---|
| 6 | "clause 2 of the enclosure record" | missing reference | inline | Name the record and say where it lives (the datum repository); link it. |
| 21–23 | "That obligation was documented only in the consumer's repository…" | history (what was missing) | delete | This page is the documentation. |
| 54–59 | "Nothing here has ever been released… the version has stood at 0.1.0" | count/status a command computes; history | inline | "`apothecary release` says what is published. While nothing is, a consumer pins a commit, and clause 5 is unmet here." (Checked: no tags today.) |
| 61–65 | "Nobody has to remember to tighten it later — … and nobody does." | ornament | inline | Keep the fact (datum reports the deviation and fails once a release exists); drop the aphorism. |
| whole page | — | structure | reference → new `docs/releasing.md` | Maintainer policy. |

### Pages 11–16: the shared header, footer and STL sentence

| md line(s) | quote | problem | home | rewrite or note | source |
|---|---|---|---|---|---|
| 11–16: 3–7 | "**This page is written by the run it describes.** Every sentence below was emitted…" | ornament (a whole sentence in bold) + stale (overclaim: the intro, runtime, STL line and "does not show" are fixed text) | inline + reference → `tests/e2e/README.md` | "Written by `tests/e2e/<module>`; each numbered step is said just after the test asserts it." Change 00:112 in the same commit. | doc_capture.py:344–357 |
| 11–16: 10/11 | "**Runtime-bound.** …" | ok | — | Bold labels a term. | doc_capture.py:361 |
| 11–16: 12/13 | "Its pictures were taken once every part's STL that OpenSCAD version 2021.01…" | ok (hard to read) | inline | "Its pictures draw each part from an STL that OpenSCAD X built; a part X cannot build is drawn from an older STL, or as its box." | parts_built.py:101–105 |
| footers | "Run it yourself: …" | ok | — | | doc_capture.py:381–397 |
| (code) | "written by the run that asserts it, on every ordinary run" | stale (13–16 are written by the browser suite only) | inline | "…by the run that asserts it: the ordinary command for 11–12, the browser suite for 13–16." | doc_capture.py:224–228 |
| (code) | "every run used to leave the tracked screenshots modified" | history | inline | "…so a run that changes no pixels leaves the committed picture as it is." | doc_capture.py:240–241 |
| (code) | "a loop's page (project/plans/ui-flows-2026-10-08.md)" | pointer into a dated plan that will retire | inline | Name pages 13–16, not the plan. | doc_capture.py:278–283 |

### 11-photographs-into-pieces.md — source `tests/e2e/test_docs_photo_walkthrough.py`

| md line(s) | quote | problem | home | rewrite or note | source |
|---|---|---|---|---|---|
| 1 | title | ok | | | :92 |
| 8 | "and shows the result in the viewer it already had" | history (what was built for it) | inline | "…and shows the result in the viewer." | :94–98 |
| 10 | "which is the price of this page and the viewer's page being one page" | history (refers to the merge of two pages) | inline | "Its second half needs a browser and a running server." | :101–104 |
| 16–22 | step 1, "A photograph becomes shapes" | ok | | | :129–135 |
| 24–30 | step 2 | ok | | | :140–148 |
| 32–38 | "It is measurably lower when the finder is wrong" | not asserted (the run checks only 0 < c < 1; I found no unit test making the claim) | inline | Assert it, cite the test that measures it, or drop the sentence. | :153–160 |
| 40–47 | step 4 | ok | | | :169–179 |
| 49–56 | step 5 | ok | | | :186–195 |
| 58–65 | step 6 | ok | | | :204–213 |
| 67–73 | "and the whole language is five of them" | count (defined in code: `ABOUT_A_PAIR` + `ABOUT_ONE`, judgement.py:94–95) | inline | Compute it in the f-string from the two tuples. | :221–224 |
| 75–83 | step 8 | ok | | | :238–248 |
| 85–91 | step 9 | ok | | | :253–258 |
| 93–97 | step 10 ("now" is the run's own) | ok | | | :272–278 |
| 99–106 | step 11 | ok | | | :284–291 |
| 108–112 | "No drawing code was written for any of this." | history (what development did) | inline | "An arrangement built from a photograph is an ordinary arrangement, drawn as any site is." | :306–309 |
| 114–123 | step 13 | ok | | | :315–321 |
| 125–129 | step 14 | ok | | | :331–337 |
| 131–135 | step 15 | ok | | | :350–355 |
| 137–139 | step 16 | ok | | | :364–368 |
| 141–147 | "a tool that is pleasant to demonstrate… Unifying means it reaches nothing" | ornament + the language of a plan; the step is off-topic | delete here; reference → `docs/viewer.md` (the census) | The census of controls says nothing about photographs. The shown count is the run's own, which is fine wherever it goes. | :371–378 |
| 149–154 | "What this page does not show" (4 bullets) | ok | | | :106–115 |
| (docstring) | "It used to be two demonstrations…" | history (flagged by the gate) | retrospective → apothecary: the walkthrough | Keep lines 3–5 and 15–18 of the docstring. | :7–13 <!-- timeless: allow quoting a phrase the check flags, in the sweep's own inventory --> |
| (docstring) | "A walkthrough that cannot fail is a screenshot with a caption." | ornament | inline | "Holds the step's chips from the other side: no word, no chip." | :385 |

### 12-the-bench-as-it-is.md — source `tests/e2e/test_docs_bench_walkthrough.py`

| md line(s) | quote | problem | home | rewrite or note | source |
|---|---|---|---|---|---|
| 1 | title | ok | | | :105 |
| 8 | intro | ok | | | :106–113 |
| 10 | runtime | ok | | | :114–120 |
| 16–23 | step 1 | ok | | | :147–159 |
| 25–32 | step 2 | ok | | | :166–175 |
| 34–41 | step 3, a sidecar part | ok (page 01:5–17 says the same; link from 01) | | | :183–196 |
| 43–50 | step 4 | ok | | | :205–216 |
| 52–56 | step 5 | ok | | | :229–235 |
| 58–62 | step 6 | ok | | | :244–250 |
| 64–68 | step 7 | ok | | | :259–265 |
| 70–74 | step 8 | ok | | | :276–281 |
| 76–80 | step 9 | ok | | | :325–334 |
| 82–86 | step 10 | ok | | | :340–345 |
| 88–94 | step 11 | ok | | | :360–366 |
| 96–100 | "the seven newest by modification time, an older one as its last cell" | a number from code (`NEWEST`, menu.py:797–799) inside a single 120-word sentence | inline | Split into a Pinned sentence and a Pictures sentence; compute "seven" from `NEWEST`. | :459–473 |
| 102–110 | step 13 | ok | | | :528–538 |
| 112–120 | step 14 (the shown errors are stays_local's: area 3) | ok | | | :547–558 |
| 124–127 | "These pictures were made with it." | duplicate (the STL sentence at line 12) | delete | Keep the rest of the bullet. | :130–132 |

### 13-a-picture-to-a-print.md — source `tests/e2e/test_picture_to_print.py`

| md line(s) | quote | problem | home | rewrite or note | source |
|---|---|---|---|---|---|
| 1 / 9 / 11 | title, intro, runtime | ok | | | :269 / :270–277 / :278–284 |
| 17–25 | step 1 | ok | | | :320–328 |
| 27–33 | step 2 | ok | | | :338–343 |
| 35–43 | step 3 | ok | | | :357–364 |
| 45–53 | step 4 | ok | | | :379–386 |
| 55–63 | step 5 | ok | | | :392–399 |
| 65–73 | step 6 | ok | | | :408–416 |
| 75–83 | step 7 | ok | | | :473–485 |
| 85–94 | step 8 | ok | | | :509–516 |
| 96–104 | step 9 | ok | | | :543–552 |
| 106–115 | step 10 | ok | | | :579–586 |
| 117–125 | step 11 | ok | | | :606–612 |
| 127–135 | step 12 | ok | | | :641–650 |
| 137–147 | step 13 | ok | | | :690–699 |
| 151 | "the camera's and the printer's real runs are steps of the bench checklist" | missing reference | inline | Add the path, as page 15 does: `project/validation/2026-09-20-ender-bench.md`. | :289–291 |
| 152–153 | the other "does not show" bullets | ok | | | :292–299 |
| (docstring) | "the fourth loop of the loops plan (project/plans/ui-flows-2026-10-08.md)" | pointer into a dated plan (area 4) | inline | Say what the module holds, not which plan asked for it. | :1–2 |

### 14-designing-a-part.md — source `tests/e2e/test_part_loop.py`

| md line(s) | quote | problem | home | rewrite or note | source |
|---|---|---|---|---|---|
| 1 / 9 / 11 | title, intro, runtime | ok | | | :706 / :708–719 / :720–726 |
| 17–25 | step 1 (shown: `_envelope`) | ok, but see line 132 | | | :754–766; :283–287 |
| 27–36 | step 2 | ok | | | :413–421 |
| 38–47 | step 3 | ok, but see line 132 | | | :448–458 |
| 49–53 | step 4 | ok | | | :797–803 |
| 55–57 | step 5 | ok | | | :810–814 |
| 59–67 | step 6 | ok | | | :828–840 (shown from :495–542) |
| 69–75 | step 7 | ok | | | :844–850 |
| 77–83 | step 8 | ok | | | :854–861 |
| 85–93 | step 9 | ok | | | :866–874 |
| 95–101 | step 10 | ok | | | :880–887 |
| 103–112 | step 11 | ok, but see line 132 | | | :897–904 |
| 114–120 | step 12 | ok | | | :909–916 |
| 122–126 | step 13 | ok | | | :682–689 |
| 130–131 | first two "does not show" bullets | ok | | | :728–732 |
| 132 | "which it is depends on the machine's OpenSCAD, so the words here leave it out" | stale (steps 1, 3 and 11 print "(read from the STL)", so the page changes with the machine's OpenSCAD) | inline | Strip the parenthesis in `_envelope`'s shown text (:287). The bullet then holds. | :733–735 |
| 133 | last "does not show" bullet | ok | | | :736–738 |
| (docstring) | "(the part-iteration plan, project/plans/part-iteration-2026-10-12.md)" | pointer into a dated plan (area 4) | inline | Drop it, or keep it only while that plan is in progress. | :1, :14 |

### 15-firmware.md — source `tests/e2e/test_the_firmware_loop.py`

| md line(s) | quote | problem | home | rewrite or note | source |
|---|---|---|---|---|---|
| 1 / 9 / 11 | title, intro, runtime | ok | | | :162 / :164–172 / :173–179 |
| 19 + 23–28 | shown `undefined: not installed`; the text says "arduino-cli and Rust for the ESP32" | stale/defect: the slicer card has `data-slicer`, not `data-id` (toolchain.js:112 vs :125), and arduino-cli is never a `.tc-module` (toolchain.js:96) | inline | Read `m.dataset.id \|\| m.dataset.slicer` at :224–227, and name what the card actually lists. | :229–239 |
| 30–36 | step 2 | ok | | | :249–254 |
| 38–45 | step 3 | ok | | | :260–266 |
| 47–58 | step 4 | ok | | | :289–301 |
| 60–68 | step 5 | ok | | | :319–327 |
| 70–77 | step 6 | ok | | | :335–343 |
| 79–91 | step 7 | ok | | | :362–375 |
| 93–101 | step 8 | ok | | | :388–399 |
| 103–109 | step 9 | ok | | | :408–413 |
| 113–116 | "does not show" (4 bullets) | ok | | | :181–194 |
| (docstring) | "(the loops plan, 2026-10-10)" | a date in present-tense text (area 4) | inline | Drop the plan and the date. | :4, :14 |

### 16-editing-a-parts-scad.md — source `tests/e2e/test_scad_loop.py`

| md line(s) | quote | problem | home | rewrite or note | source |
|---|---|---|---|---|---|
| 1 / 9 / 11 | title, intro, runtime | ok | | | :324 / :326–336 / :337–342 |
| 17–21 | step 1 | ok | | | :373–379 |
| 23–27 | step 2 | ok | | | :406–415 |
| 31 | "300 ms after the check passes rendered as Apply renders" | a number from code typed into a string (`SCAD_RENDER_AFTER_CHECK_MS`, template :895) | inline | Read the constant, or say "soon after". `docs/README.md` says "a second of quiet": stale there (area 1). | :431–433 |
| 39–47 | shown "The ref is in /tmp/piP/w3/server2/variants.git…" | stale (a folder that changes per run; the previous commit had `w2`; CI's `git diff --exit-code` cannot match it) | inline | At :457, swap the server's folder for a fixed word; blank `FOLDER` in `#status` for the picture. | :449–459 |
| 49–53 | step 5 | ok | | | :467–474 |
| 55–59 | step 6 | ok | | | :485–490 |
| 61–69 | step 7 shown, the same folder | stale (as at 39–47) | inline | The same fix, at :512. | :506–514 |
| 71–75 | step 8 | ok | | | :528–535 |
| 77–79 | step 9 | ok | | | :549–555 |
| 81–87 | step 10 | ok | | | :570–576 |
| 89–97 | step 11 | ok | | | :589–598 |
| 99–107 | step 12 | ok | | | :626–634 |
| 109–111 | step 13 | ok | | | :651–656 |
| 117 | "When a variant was saved. It differs on every run…" | stale (incomplete) | inline | Add the server's clone folder to what is left out. | :349–350 |
| 115, 116, 118 | the other "does not show" bullets | ok | | | :344–348, :351–352 |
| (docstring) | plan pointers to ui-flows and part-iteration | area 4 | inline | As for page 14. | :1, :16 |

## 3. Retrospectives this area needs (qm `perspectives/`, one dated file each)

1. **apothecary: the datum parts**
   - `parts/datum`, a single-piece tray, was replaced by the compound `datum_core` + `datum_cap`.
   - `datum_core` was left with six orphan parameters when the cover moved to `datum_cap`.
   - The `walls`/`tolerence` dispute (2.4/0.2, citing a record that lacked them) was retired
     along with its only source.
   - The black-box seam moved from `parts/datum` to `datum_core`.
   - The obligation to publish was written only in datum's repository until page 10.
2. **apothecary: build readiness and the problems index**
   - The checklist read `build()` as one object and reported "no stubs remain".
   - It then reported datum's stubs for every part, `calibration_cube` included.
   - An adversarial pass showed that the contested branch typed its owner instead of reading
     `KIND_OWNER`.
3. **apothecary: the viewer**
   - three.js came from a CDN. Offline, the canvas, tree and SCAD were empty while
     "Layout valid" still showed.
   - Site's SCAD waited for a drag.
   - The firmware page and the printer monitor were folded into the one page as redirects.
   - The "dashboard" name was still used for the controls.
4. **apothecary: preflight and CI**
   - In the sibling project, one workflow's `uv sync --locked` stripped another's tools, and
     the licensing gate failed for it.
   - An `npm ci` postinstall that a local cache hid.
   - Seven tests read STLs that existed only locally.
   - The CLI crashed on a check mark under cp1252.
   - The pinned runner's bare `bash` hit the WSL alias; the pin was last propagated
     2026-08-11.
5. **apothecary: the walkthrough**
   - The photo path had two demonstrations, and the page produced by `docs generate` went
     stale. They were joined into page 11.
   - Every run rewrote the tracked screenshots until pictures were compared by pixel.
   - The loop pages 13–16 moved to the browser suite only.

## 4. Reference pages to create or extend

- **`docs/viewer.md`** (extend): staging, Apply, Defaults and the variant mark in the part
  editor (from 02:79–86 and 05:57–61); three.js is vendored, so the page works offline
  (04:25–39); the census of controls (11, step 17).
- **`docs/fitting-a-part.md`** (extend): a candidate's source must be readable (05:39–43);
  how to record candidates (05:86–90); reconcile the owners with 08:34–38.
- **`docs/parts-authoring.md`** (extend): every top-level number has a parameter
  (02:37–53); the readiness checklist and its three states (06).
- **New `docs/cli.md`**, or a section of `CONTRIBUTING.md`: status marks, ASCII marks and
  cp1252, Click only (07).
- **`CONTRIBUTING.md`**, or a new `docs/preflight.md`: preflight (09). It covers one
  invocation per workflow, the scratch environment, `LOCAL_DIFFERENCES`, what a pass does not
  prove, and the Windows `bash` constraint.
- **New `docs/releasing.md`**: consumers (`consumers_waiting`), `apothecary release --check`,
  clause 5 and the two acts (10).
- **`tests/e2e/README.md`** (extend): how a walkthrough page is written. That covers which
  text is asserted and which is fixed, `browser_suite_only`, what is blanked or left out, and
  the CI diff check. The page header can then be one line.

## 5. Suggested order for the sweep

1. **Page 00** (the most read): lines 97–99, 156–162 and the trim at 88–93. Doctested; no
   browser run needed.
2. **The three §1 defects in the generated pages.** Each is a line or two in a test:
   test_part_loop.py:287 or :733–735; test_the_firmware_loop.py:224–227;
   test_scad_loop.py:457, :512 and :349. Regenerate with the three modules. This also makes
   CI's walkthrough diff reproducible.
3. **Ports and pointers:** 02:113, 02:118, 03:68–70, 04:55; 01:28–29, 01:46–48; 05:88–90
   ("dashboard").
4. **History in 04, 05, 06 and 08,** with the retrospectives "the datum parts", "build
   readiness…" and "the viewer" drafted alongside. Page 05's doctest is rewritten around
   `board_y`.
5. **Pages 07, 09 and 10:** move the explanation into the new reference pages, leaving short
   pages or none (see §6). Write the retrospective "preflight and CI" here.
6. **The generated header and the page 11 text**, in one commit: doc_capture.py:344–357,
   parts_built.py:101–105, page 11's intro, runtime and steps 12 and 17, its docstring, and
   00:112. Then regenerate 11–16.
7. **Restructure last** (§6). It renames screenshots, because the ordinal is in each file name
   (doc_capture.py:314). It also touches 00's `1[3-6]` glob, `docs/README.md`, and the
   "walkthrough 13/14/16" strings in the tests.

## 6. Structure: the walkthrough as a whole

- **Purpose per page.** These pages have a clear purpose: 00 (setup), 01–04 (a part, its
  numbers, an assembly, the API), 06 (readiness), 11–12 (demonstrations) and 13–16 (loops).
  Page 05's purpose is now thin: once the history is gone it is one dispute and a recipe.
  Pages 07, 09 and 10 serve a contributor or maintainer, not a newcomer.
- **Repetition.**
  - The `board_y` dispute appears on 05, 06 (L63–71) and 08 (the "contested" kind). Merge
    them into one page, "What stands between a part and a print": contested numbers, then
    readiness, then the problems index.
  - The one-page redirect is doctested on both 04 and 05.
  - The part editor is described on 02 and 05, and also on 14 and in `docs/viewer.md`.
  - Sidecar parts appear on 01 and 12 (step 3), which is fine as a demonstration; link them.
  - On page 12 (lines 12 and 127), the STL sentence and the last bullet say the same thing.
- **Order for a newcomer.** Page 00 already routes a newcomer to the loops first. The numbers
  put the loops last and contributor policy in the middle. A clearer sequence would be:
  - 00, setup;
  - the four loops (now 14, 16, 13, 15);
  - the demonstrations (11, 12);
  - the library concepts (01, 02, 03, the merged 05/06/08, 04);
  - with 07, 09 and 10 moved to `CONTRIBUTING.md` or `docs/`, their doctests kept wherever
    they land.

  Until the pages are renumbered, page 00:156–162 should at least name every page.
- **Cross-area notes.**
  - Area 1, `docs/README.md`: the walkthrough is "run by `pytest walkthrough`" (true only of
    00–10), and page 16 is described as rendering "after a second of quiet" (the code says
    300 ms).
  - Area 3: the "dashboard" comments at `datum_core.py:176` and `base.py:27`.
