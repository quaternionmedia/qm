# Handoff — the voice loop, and the three-process development environment

**Stamped 2026-09-27, restamped after the merges below.** `qm` `main` at
`d1aca4f`; `vox` `main` at `4b2e64d`; `joe` `main` at `6e1ad16`; `qmcp`
`main` at `77b73ca`; `dossier` `main` at `b21ce32`. Every figure here was true at those commits and nowhere else.
Re-derive before acting on any of it.

`vox` and `joe` carry no `governance/qm` submodule, so the cross-repository
state is recorded here and nowhere else. `vox` joined the roster on
2026-09-27, in `core`; `joe` is in `performer-display` and predates this
work.
[`hil-review-2026-09-27.md`](hil-review-2026-09-27.md) is the companion:
what is waiting on a person, in the order it wants deciding. Nothing in this
page is a decision.

---

## 0. What landed

Fifteen pull requests merged, two of them the corpus's own.

| Repository | Merged | What it carries |
|---|---|---|
| `joe` | #8, #9 | the application, and the two lines reconciled; speech analysis; filename hardening extended to the voice route |
| `joe` | #10 | the Python suite in CI, on Windows, where it had never run anywhere |
| `joe` | #11 | input-device selection, and recording at a rate devices accept |
| `vox` | #1, #2 | the deterministic closed loop; artifacts written LF and mutated files restored byte-for-byte |
| `vox` | #3 | the engine contract as a value; every product name moved to `vox.adapters` |
| `vox` | #4 | an offline synthesizer, and a live loop that creates its own input |
| `vox` | #5 | `HANDOFF.md` replaced with the surface that exists |
| `dossier` | #58 | `dossier dev doctor`, the three-process preflight |
| `qmcp` | #38 | the HITL queue answered by voice, `vox` vendored at `d54a7f7` |
| `qm` | #122 | this handoff, the retrospective, and `vox`'s roster entry in `core` |
| `vox` | #6 | the Apache-2.0 license the wheel metadata was already claiming as MIT |
| `joe` | #12 | the MIT license file both metadata files were already claiming |
| `joe` | #13 | paths through pathlib, the suite green on ubuntu for the first time, one lockfile |
| `dossier` | #59 | recorded artifacts written LF, `db-backups/` ignored |
| `qm` | #126 | the estate reads the one-slot rule with the gate's own exemption |

**The full round trip runs.** Text through a real synthesizer, through
whisper, back out and back in:

```
uv run vox loop --echo-dir <engine's audio dir> --say "ship it on friday"
  heard:  'Ship it on Friday.'
  echoed: 'Ship it on Friday.'
  closed: True
```

`uv run vox loop --offline` closes the same loop in about two thirds of a
second with no engine, no model and no hardware.

## 1. What remains, and what done looks like

- **`joe` cannot record on several host APIs.** The rate fix changed
  WASAPI's complaint from `Invalid sample rate` to `Invalid device`, and
  MME and DirectSound return errors naming no cause. *Done* is one device
  on each host API recording a non-silent second, or the reason written
  down.
- **`joe`'s Playwright specs run in CI, and the red never came.** The
  first dispatch of `e2e.yml` (joe #13) was expected red on the belief the
  specs needed a server nothing starts; it came back green, 25 passed,
  because `playwright.config.js` starts the dev server itself. joe #14
  widened the trigger to pushes and pull requests. The workflow has not
  yet been seen to fail, so what a red looks like there is still untested.
- **`dossier`'s GIF re-encode is still only measured.** The four
  line-ending writers are pinned (dossier #59, churn reproduced and then
  gone on the same run); the nine-byte `first-run.gif` re-encode needs the
  real database to reproduce, and the scratch-database run left the file
  byte-identical.
- **The approval case is exercised; the wider loop is not built.** The
  closed loop ran against the live engine on 2026-09-27
  (`uv run vox loop --echo-dir <the engine's audio dir> --say ...`,
  `closed: True`), and a real launch approval waits on the harness queue
  (§6). Speaking an instruction, an agent acting, and the result spoken
  back as a standing service remains unbuilt.

## 2. The development environment

Three processes on one workstation, in clones that cannot import each
other. `dossier dev doctor` is the preflight and rides `dossier` #58;
`dossier/docs/dev-loop.md` is the page.

| Role | Clone | Port | Moved by |
|---|---|---|---|
| harness | `qmcp` | 3141 | `DOSSIER_HARNESS_PORT` |
| panel | `dossier` | 1618 | `DOSSIER_PORT` |
| maps | `codecartographer` | 2718 | `CODECARTO_PORT` |
| speech | `joe` | 8000 | `JOE_PORT` |

The allocation is declared once in `dossier/src/dossier/threads.py`. Only
the harness is required. 8000 is the one to move first when two loops run
at once: it is the port anything grabs, and the one `dossier`'s `seam-port`
diagnostic exists because of.

**Set `DOSSIER_DATABASE_URL` before running `dossier`'s suite.**
`pytest_configure` shells `dossier dev purge` against whatever database the
CLI resolves. Measured 2026-09-27: 0 of 117 project rows in the working
database match any purge pattern, so a run that day destroyed nothing — and
several of the patterns are ordinary words such as `user/` and `doc/`.

## 3. Audio capture on this workstation

Measured 2026-09-27. None of it is visible in a device listing:

- **20+ input devices across four host APIs**, with the same microphone
  appearing four times under a byte-identical name.
- **The backend default is a capture card**, not a microphone.
- **Every device is natively 44100 or 48000 Hz.** Opening one at 16000
  failed on all four APIs, including the default — the path `record()` took
  before #11.
- **WDM-KS devices open without error and return garbage**: samples around
  `-2e38`, or NaN.

`joe voice level --every` records briefly from each input and reports peak
and RMS. Speak while it runs; the one that moves is the one to set as
`JOE_INPUT_DEVICE`.

## 4. What no check covers

- **No workflow runs `qm private-names`.** `registries.yml` excludes it
  deliberately: its admission test is that a check reads committed files and
  nothing else, and this one reads a gitignored companion or the forge. A
  private repository name reached a public repository through that gap on
  2026-09-27, and was resolved by making the repository public rather than
  by redacting.
- **Nothing detects a public repository vendoring a private submodule.**
  `check-submodule-refs` fails on it and reports it as a possibly-unpushed
  pin, naming the ambiguity in its own error text and giving the command
  that distinguishes them.
- **`vox`'s path-escape test is weaker on Linux**, where a backslash is an
  ordinary filename character and the 404 means *absent* rather than
  *refused*.
- **No test asserts what the synthesizer sounds like**, and none can. That
  whisper cannot read it is measured against a live engine, with a control,
  and recorded as `vox.synth.SPEECH_IS_NOT_TRANSCRIBABLE`.

## 5. Standing constraints

- *Keep everything local* is **not** in force.
- **`vox` is public as of 2026-09-27.** It was created private, which is why
  every check on `qmcp` #38 failed from 2026-09-22 onward: a public
  repository's runner cannot clone a private submodule.
- **`joe` now publishes to GitHub Pages.** Merging #8 brought the
  application onto a `main` that already carried `deploy.yml`, so a push
  builds the frontend and deploys it. Three files are published and none
  carries anything personal. Named here because it was not obvious before
  the merge.
- **`vox` is Apache-2.0 and `joe` is MIT**, decided and merged
  2026-09-27 (`vox` #6, `joe` #12); each repository's metadata had
  claimed a license no file granted.
- **The design-review launch waits on the harness queue**, not in a
  terminal: an approval request on the human queue (port 3141,
  `/v1/human/requests`, id `design-review-qm-audit-2026-09-27`,
  re-queued on expiry) states the exact count. A session picking this
  up reads the answer from the queue, launches on approve with the
  counts the request states, and puts the next phase's count back on
  the queue the same way. Answering by speech is one command:
  `uv run qmcp human voice <request-id>`.
- **Merged branches were not deleted** where `handbook/handoffs/README.md`
  places deletion outside what a handoff authorises.
