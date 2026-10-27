# Handoff — joe's open set, #35 to #58, landed one merge at a time

**Stamped 2026-10-26.** `joe` `main` at `474307f`; `joe`'s
`integrate/open-prs` at `6ff1f67`; `qm` `main` at `fa376e0`. Every figure on
this page was true at those commits and nowhere else. Re-derive each one with
`gh` before acting on it: an assistant session's Auto-fix watches #35 to #50
and merges `main` into one the host reports conflicting (`0a469eb` on #47).

[`voice-set-landing.md`](voice-set-landing.md) is the voice set, landed through
`joe` #34. This page is every `joe` pull request opened after it, what is
recorded against each, and how each is readied. Delete it when they have
landed or closed.

---

## 1. Decisions in force

Each asked of Peter on its own, 2026-10-24 to 2026-10-26, in the session that
opened #39 to #58:

1. **A person clicks every merge**, as `voice-set-landing.md` decision 2. Each
   pull request is readied, shown, and its merge asked for, one at a time;
   `uv run qm merge --repo quaternionmedia/joe --pr <n> --yes` merges.
2. **What the audit of 2026-10-25 found against an open pull request is fixed
   on it as it is readied**, one commit, before its merge is asked (§4), as
   `voice-set-landing.md` decision 6. What it found on `main` went out as #53
   to #58.
3. **`joe`'s user paths are three lanes** -- the music page, the voice loop,
   joe as a server -- a page each in `docs/paths/`. Every page spec carries
   one lane tag and is named on its lane's page; `npm run check:paths` holds
   the two together (#52).
4. **`joe`'s page is a GoldenLayout dock** by codecartographer's and alfred's
   standard: the visualiser alone by default, every other window opened from a
   transport button, a key or the Panels menu. The window buttons are icons
   (#51).
5. **`joe run` and `POST /api/run` choose their recordings**: the newest,
   those named, or every one with `--all` or `?all=true` (#55).
6. **`docs/revamp-audit.md` is deleted** (#57).
7. **#51 and #52 land last.** Their base, `integrate/open-prs`, merges #33 to
   #58 and records how each conflict between them was resolved.
8. **There is one demo, the sum of the open set**: `joe.worktrees/demo`,
   detached at #52's head (§8).

## 2. What has landed

| Pull request | Merged as | Readied by |
|---|---|---|
| #33, the transcript lane | `c7dccf4` | Peter's test by hand on the demo, by step 4 of `docs/paths/voice-loop.md` §4; `a74eb57` made the README say when a take's words go, and gave the lane spec's scripted events their `at` |
| #34, `joe`'s timeless text | `474307f` | `main` merged in (`d3d4508`), its body's Branch block and base line rewritten |

## 3. What is open

| Pull request | Branch, base | At the stamp |
|---|---|---|
| #50, a take's recording kept relative to the voice folder | `feat/relative-take-paths`, `main` | draft, `CLEAN`; §4 |
| #39, #40, #41, the transcript's folds, clamps and day names | `feat/fold-empty-takes` on `main`, then each on the one before | #39 ready, #40 and #41 drafts |
| #42, #43, #44, #45, #46, #47, #48, #49, page and voice fixes | each on `main` | ready, `CLEAN`; #46 in §4; #47 has `main` merged in |
| #53, the specs' own servers | `test/specs-own-servers`, `main` | ready |
| #54, no machine setting reaches a Python test | `test/python-settings-fixture`, `main` | ready; §4 |
| #55, `joe run` choosing its recordings | `feat/run-chooses-files`, `main` | ready |
| #56, `main`'s docs say what its code does | `docs/main-says-what-is-true`, `main` | ready |
| #57, `docs/revamp-audit.md` deleted | `docs/drop-revamp-audit`, `main` | ready |
| #58, `main`'s specs and tests check what they say | `test/main-checks-what-it-says`, `main` | ready, **conflicts with `main`** |
| #36, #37, #38, #35, the media stack | `feat/video-audio-engine` on `main`, then `docs/media-engine`, `fix/security-defaults`, `docs/tighten-language` | #36 ready, the rest drafts; §4 |
| #51, the dock; #52, the lanes | `feat/golden-layout` on `integrate/open-prs`, `docs/user-paths` on it | drafts; **`playwright` fails on the hosted runner** (§6) |

An order that keeps the conflicts small, not decided: #50; #39 to #41; #42 to
#49; #53 to #58; #36, #37, #38, #35; then #51 and #52. #4 (`p5`) and #7
(Dependabot) are older than the set and outside this page.

## 4. Recorded against each, to fix as it is readied

- **#36.** No test reads `DEFAULT_TTL` or `JOE_MEDIA_TTL`; the hour the tests
  use is the fixtures' own 3600.
- **#38.**
  - The take-recording route, `GET /api/voice/takes/{take}/audio` from #33, is
    gated on #38's `transcripts` capability, with its row in
    `tests/test_access.py`'s table, a **Capability:** line in `docs/api.md`,
    and its rows in `docs/api.md`'s and `docs/security.md`'s tables.
    `integrate/open-prs` `c5eb698` and `83ddd1b` are the reference.
  - The two "serving everything" specs pass before `/api/health` answers.
  - `docs/api.md`: the Host list leaves out `*.localhost`; "every route but the
    health check and the vocabulary" leaves out `/openapi.json`, `/docs` and
    `/redoc`; a page in `JOE_ALLOWED_ORIGINS` may POST, not DELETE.
  - `docs/contributing.md` says joe "was started as `backend`"; `cli.py`
    prints "Load results with `joe backend`" and "its Backend capture".
  - `test_another_site_cannot_embed_a_recording` asks for
    `/api/voice/control`, not a recording;
    `test_an_upload_on_its_way_in_is_not_served` never asks for the file.
- **#46.** `docs/api.md` says to select "Browser"; the select reads **Browser
  mic**.
- **#50.** The datapoints reference does not say a take's `audio` is relative
  to `Data/Voice/`; the take-audio tests serve from the real `Data/Voice`, not
  the test's own folder.
- **#54, with #36 and #55.** Its `MACHINE_SETTINGS` lists `JOE_AUDIO_FILE`,
  which #55 stops reading, and lacks #36's `JOE_MEDIA_*`. Whichever of the
  three lands last carries the change.
- **#58.** `main` merged in, its conflict resolved.
- **#51 and #52.** Retargeted onto `main` once everything under them has
  landed, `main` merged in with `integrate/open-prs`'s merges as the reference
  resolution, and the failure in §6 found and fixed.

## 5. Blocked on a person

- **Every merge** (§1, decision 1).
- **Whether #56 and #52 stand for `voice-set-landing.md` §3's README and
  cookbook rows**, which ask for one pull request each from `main` carrying the
  demo branch's README and cookbook as facts. #56 states `main`'s README as
  its code is; #52 folds the cookbook's recipes into the lane pages and
  deletes it.
- **Branches to delete**: `demo/voice-loop-2026-10-04`, and
  `integrate/open-prs` once #51 has landed.
- **The two decisions `voice-set-landing.md` §4 carries**: whether `joe`
  carries the corpus, and whether `openai-whisper` becomes an optional extra.

## 6. Open failures, and what was not verified

- **#51 and #52 fail `playwright` on the hosted runner** at
  `tests/e2e/voice.spec.js:170`, "every state looks different from every
  other": runs `40263211370` and `40263296474`, 126 passed and 1 failed each,
  nine of the ten voice states reading `rgb(85, 85, 85)`. The same 127 specs
  passed locally at both heads, and the spec is `main`'s and passes there. A
  colour read while its transition runs, or read from a Voice window that is
  parked, would each give that output; neither is ruled out.
- A take once shown plays from the browser's cache after its recording is
  deleted: `GET /api/voice/takes/{take}/audio` sends no `Cache-Control`. Seen
  on the demo on 2026-10-26; nothing is filed.
- The transport's groups are checked side by side at 1024 and 1280 pixels
  only.
- A panel told it is shown a frame after its window opens (#51) has no spec
  that fails without it.
- No test drives joe's mic, a live recording, `GET /api/results/latest` or
  `POST /api/voice/transcribe`; the lane pages say so.
- `LABEL_W` is defined in three files, and `capture.py` has no test; #57's
  body names both.
- On the integration under load, two `qmcp` specs timed out once; they passed
  51 repeats after it, and the whole suite passed.
- Auto-fix watches #35 to #50, not #51 to #58.

## 7. How each step was done

1. **Merge**, as `voice-set-landing.md` §6 step 1. `joe` deletes a head branch
   on merge, so `qm merge` reports "not deleted" for one already gone.
2. **Bring one level**: `git merge origin/main` in the pull request's
   worktree beside the clone (`joe.worktrees/<slug>`), signed, its checks run,
   then pushed. `integrate/open-prs` holds every conflict between #33 and #58
   met so far, resolved.
3. **The page's specs on the branch's own build.** Before #53 lands, a
   branch's `playwright.config.js` reuses whatever answers on `:3000`, which
   can be the demo. A config of its own runs `npm run dev -- --port 3300
   --strictPort` with `reuseExistingServer: false` and `testDir` set to the
   worktree's `tests/e2e`. A worktree without `node_modules` takes a junction
   (`mklink /J`) to another worktree's whose `package-lock.json` is the same;
   `rmdir` the junction before removing the worktree, or the removal follows
   it.
4. **Python**: `PYTHONPATH=<worktree> <another worktree>/.venv/Scripts/python.exe
   -m pytest tests/ -q`, run from the worktree; #54's import check fails from
   outside it.
5. **Text**: from the corpus clone, `uv run qm timeless --base origin/main
   --root <worktree>` and `uv run qm leaks --root <worktree>`; with #52,
   `npm run check:paths`.
6. **Body**, as `voice-set-landing.md` §6 step 6. `check_pr_base.py` runs from
   inside the `joe` worktree, after the push.
7. **Seen red**: each fix or new check undone, its spec or test run and seen
   failing, then restored.

## 8. Local state at the stamp

Nothing is unpushed but `joe.worktrees/review`. No server the session started
is running.

- The `joe` clone: `demo/voice-loop-2026-10-04` at `f3faa67`, clean. Its
  untracked `.claude/launch.json` starts the demo: `joe-demo-api` (uvicorn on
  `127.0.0.1:8020`, every `JOE_ALLOW_*` set, `tighten`'s venv, `PYTHONPATH`
  the demo) and `joe-demo-page` (`npm run dev` on `:3000` with
  `JOE_API_URL=http://127.0.0.1:8020`).
- `joe.worktrees/demo`: detached at `70ede34`, #52's head, with a `Data/` of
  its own whose takes point into it.
- `joe.worktrees/paths` (#52), `topics` (#58), `panel-keys` (#47, its
  `node_modules` a junction to `transcript-lane`'s), `security` (#38) and
  `tighten` (#35): level with origin.
- `joe.worktrees/transcript-lane` and `timeless`: #33's and #34's branches,
  merged and deleted on origin.
- `joe.worktrees/review`: detached at `422fe96`, a review build of 2026-10-24
  that `integrate/open-prs` replaces.
- alfred's Docker containers hold `127.0.0.1:8000` and `:8001`, so the demo's
  API is on `8020`. A `joe` API on `127.0.0.1:8010` from `tighten`'s venv,
  started 2026-10-26 at 10:22 UTC and not by the session that wrote this page,
  is left running.
