# Handoff — the voice loop, and the three-process development environment

**Stamped 2026-09-27.** `qm` `main` at `d6dc5cd`; `vox` `main` at `d54a7f7`;
`joe` `main` at `6e1ad16`; `qmcp` `main` at `d834916`; `dossier` `main` at
`d42967a`. Every figure here was true at those commits and nowhere else.
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

Six pull requests merged, all in repositories outside the corpus.

| Repository | Merged | What it carries |
|---|---|---|
| `joe` | #8, #9 | the application, and the two lines reconciled; speech analysis; filename hardening extended to the voice route |
| `joe` | #10 | the Python suite in CI, on Windows, where it had never run anywhere |
| `joe` | #11 | input-device selection, and recording at a rate devices accept |
| `vox` | #1, #2 | the deterministic closed loop; artifacts written LF and mutated files restored byte-for-byte |
| `vox` | #3 | the engine contract as a value; every product name moved to `vox.adapters` |
| `vox` | #4 | an offline synthesizer, and a live loop that creates its own input |

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
- **`joe` carries two Python lockfiles.** `pdm.lock` is from 2024-12-29 and
  nothing reads it; `uv.lock` is current. `requirements.txt` is a third
  list and omits `httpx`, which `pyproject.toml` declares. *Done* is one
  source of truth and the others deleted.
- **`joe` composes paths with literal backslashes.**
  `Modules/utilities.py` builds `f"{current_path}\Data\Output\..."`, which
  is one filename component on Linux and the source of `invalid escape
  sequence` warnings a later Python raises. Six tests fail on
  `ubuntu-latest` for this one reason; 74 pass. *Done* is `pathlib`, after
  which `joe` #10's workflow can become a matrix instead of Windows only.
- **`joe`'s Playwright suite runs nowhere.** `tests/e2e/` needs browser
  binaries and a live server. *Done* is a workflow watched going red.
- **`dossier`'s suite rewrites four files with platform line endings** on
  every run — `docs/rad-commands.md` and three SVGs — and re-encodes a GIF
  by nine bytes, so `git status` shows drift that is not drift. The same
  defect was fixed in `vox` by pinning `newline="\n"` in the writers.
- **`dossier`'s `db-backups/` is not ignored.** It is empty, so nothing is
  tracked today; a backup written there would appear as untracked.
- **The human loop is not built** — speaking an instruction, an agent
  acting, the result spoken back. `qmcp human voice` is its approval case,
  and the harness beneath it is now deterministic enough to iterate on.

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
- **Merged branches were not deleted** where `handbook/handoffs/README.md`
  places deletion outside what a handoff authorises.
