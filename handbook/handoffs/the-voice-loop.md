# Handoff — the voice loop, and the three-process development environment

**Stamped 2026-10-18.** `qm` `main` at `157cbf6`; `vox` `main` at
`1721e6f`; `joe` `main` at `d72b65b`; `qmcp` `main` at `df42315`; `dossier`
`main` at `414be1c`. The voice set has landed apart from `joe` #33 and #34
(§1). Every figure here was true at those commits and nowhere else.
Re-derive before acting on any of it.

`vox` and `joe` carry no `governance/qm` submodule, so the cross-repository
state is recorded here and nowhere else. `vox` joined the roster on
2026-09-27, in `core`; `joe` is in `performer-display` and predates this
work.
[`hil-review-2026-10-04.md`](hil-review-2026-10-04.md) is the review of the
set, with the decisions it left to a person, and
[`voice-set-landing.md`](voice-set-landing.md) is how far its landing has got
and what is left of it. Nothing in this page is a decision.

The why of all of it is in the retrospectives, and not here:
`perspectives/2026-09-27-the-voice-loop.md`,
`perspectives/2026-09-28-the-loop-lands-its-remains.md`,
`perspectives/2026-09-28-the-voice-loop-meets-the-field.md` and
`perspectives/2026-10-15-the-voice-set-landing.md`. Phase 10 of `qmcp`'s
`docs/ROADMAP.md` is built and on `main`; the work after it follows `qmcp`'s
`docs/voice-loop-next-phases.md`, cleanup before new capabilities, and §6 is
that plan's Phase 0 at this stamp. **Continuity comes from qmcp, not the
model**: the loop's agent is a runtime qmcp calls -- the local model it
stands up first -- handed the project's earlier work from qmcp's own record.

---

## 0. What landed

Three rounds of merges, grouped by what they carry. The first built the loop
and landed by 2026-09-28; the second made it answerable from a page, and ran
to 2026-10-03; the third is the voice set, landed from 2026-10-12.

| Repository | Merged | What it carries |
|---|---|---|
| `joe` | #8–#13 | the application and the speech analysis reconciled on one line; the Python suite in CI, on both platforms, where it had run nowhere; an input device chosen and opened at a rate it accepts; paths through pathlib and one lockfile; the MIT license file |
| `joe` | #14–#19 | the Playwright specs on every push and pull request; diagnostics that survive the console; the listen route recording until the speaker stops, endpointed with a moving noise floor and a sustained-speech onset; `joe voice setup`, which finds, saves and proves the microphone |
| `joe` | #20–#22 | capture through a callback stream, which every host API implements, and only a microphone that has recorded is saved; a live conversation panel; pending `qmcp` requests answered by voice from the page |
| `vox` | #1–#6 | the deterministic closed loop, its artifacts written LF; the engine contract as a value, every product name in `vox.adapters`; an offline synthesizer and a live loop that creates its own input; `HANDOFF.md` replaced with the surface that exists; Apache-2.0 |
| `vox` | #7, #8 | the prompt played aloud, with `speak` returning when the audio ends; a `conversation` route in the engine contract and `HttpSTT.announce` |
| `dossier` | #58, #59 | `dossier dev doctor`, the three-process preflight; recorded artifacts written LF and `db-backups/` ignored |
| `qmcp` | #38–#47 | the HITL queue answered by voice; onboarding followable from a fresh clone; the voice seam a default dependency; the closed-choice dialog — options spoken, an answer naming one taken, noinput told from nomatch; the submodule moved to `vendor/vox`; both servers checked before anything is spoken; only answerable pending requests listed, oldest first, each asked once per run |
| `qmcp` | #48–#53 | the governance pin bumped; `qmcp cookbook voice`; the dialog's states announced to the engine; `POST /v1/human/requests/{id}/voice` and `GET /v1/human/voice`, loopback-only; `vendor/vox` at the conversation route; `uv run qmcp` as the one declared entry point |
| `qm` | #122, #124–#133 | this handoff and the three retrospectives; the design-review runbook; the estate reading the slot rule with the gate's exemption; the design-review consent routed through the harness queue; small pull requests — parallel when independent, stacked as drafts when dependent, the stack check, and retarget before delete; `main` propagated into `project/qmcp`; submodule URLs looked up by path |
| all four | the voice set | Phase 10 of `qmcp`'s roadmap on the local model: an open question answered by voice, the instruction inbox, acting on an instruction behind consent with continuity from `qmcp`'s record, the outcome said back, one standing spoken conversation started by `serve --converse`, its onboarding and cookbook, the vocabulary, declared checks run by voice; `vox`'s pause, hints, confidence and a voice that stops when interrupted; `joe`'s answers by key, live transcript, take confidence, answering over a question and the transcript pane; the durable-text record, its gate and the sweeps of `qm`, `qmcp` and `vox`. `voice-set-landing.md` lists each pull request |

**The full round trip runs.** Text through a real synthesizer, through
whisper, back out and back in:

```
uv run vox loop --echo-dir <engine's audio dir> --say "ship it on friday"
  heard:  'Ship it on Friday.'
  echoed: 'Ship it on Friday.'
  closed: True
```

`uv run vox loop --offline` closes the same loop with no engine, no model and
no hardware. **Answering a request by voice from a page is two commands**,
one per server: `uv run joe dev` in `joe`'s checkout and `uv run qmcp serve`
in `qmcp`'s; `qmcp`'s `docs/integrations/voice.md` is the page for the rest,
and `uv run qmcp cookbook voice` is the check, offline on `vox`'s
deterministic engine or `--live` with a person at the speaker. **Speaking an
instruction is two commands as well**: `uv run joe dev` and `uv run qmcp
serve --converse --runtime local`; `qmcp`'s `docs/voice-loop-demo.md` is its
onboarding.

## 1. What remains, and what done looks like

- **`joe` #33 and #34.** #33, the transcript lane, waits on a test by hand;
  #34 is stacked on it. The README and cookbook pull requests that replace
  the closed #24 and #25 follow #34. `voice-set-landing.md` §3 says what done
  is for each.
- **A person at the microphone.** Every take so far was scripted, which says
  nothing about a real one. *Done* is tier 3 of `qmcp`'s
  `docs/voice-loop-demo.md` -- `uv run joe dev`, `uv run qmcp serve --converse
  --runtime local`, and then speech -- run once and recorded.
- **`qmcp`'s next phases.** `docs/voice-loop-next-phases.md` orders the work:
  Phase 0, re-establishing the baseline, is §6; Phase 1 reconciles the
  onboarding and architecture pages; Phase 2 bounds the transcript's storage
  and rendering cost; Phase 3 makes the declared checks' boundaries explicit.
  New capabilities come after.
- **The governance pin bump in `qmcp`.** `governance/qm` is at `235708c`. The
  bump copies again the six seed workflows `qmcp` carries and adds
  `timeless-check.yml`, takes the REUSE step through `uvx` (§4), and retires
  the `AGENTS.md` paragraph about that step. `voice-set-landing.md` §3 lists
  it with the other steps after the set: Phase 10's boxes on the roadmap, the
  two read-back helpers made one, `vendor/vox` moved to `vox`'s `main`, and the
  demo branches deleted.
- **`joe` records on one host API, and the other three are a reading of one
  run.** `joe` #20 moved capture to a callback stream, because WDM-KS
  implements no blocking read, and on the hardware that run used the WDM-KS
  entry recorded a second of finite samples while every MME, DirectSound and
  WASAPI input failed to open through both paths. The pull request attributes
  that to the audio engine's state on that machine rather than to the change,
  and the ranking of host APIs is exercised by tests, not by that run. *Done*
  is unchanged: one device on each host API recording a non-silent second, or
  the reason established rather than read off a single run.
- **`dossier`'s GIF re-encode is still only measured.** Nothing on `dossier`
  `main` has touched `docs/screenshots/first-run.gif` since #59, whose
  scratch-database run left it byte-identical; the re-encode needs the real
  database to reproduce.
- **What a standing conversation keeps.** `joe` keeps every take as a file;
  a retention rule is the review page's decision 5.
- **The command-line runtime against the real tool.** Its command line and its
  reading of the output are asserted; it has not been run, because the tool is
  not on the workstation the set was built on.
- **Two bounds nobody has set.** `run_forever` has no bound on an idle queue,
  and a standing worker needs one.
- **Merged branches in every repository above.** Some remain and some are gone;
  `handbook/handoffs/README.md` places deletion outside what a handoff
  authorises, and `uv run qm branches` says what deleting one would cost.

`joe`'s Playwright specs have been seen red: on 2026-10-05 a run on #32's
branch failed an assertion on the transcript pane's entry count, and the
commit after it passed.

## 2. The development environment

Three processes on one workstation, in clones that cannot import each
other. `dossier dev doctor` is the preflight, landed as `dossier` #58;
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

**Point `QMCP_DATABASE_URL` at a path of your own before running `qmcp`'s
suite.** `qmcp test` unlinks `./qmcp.db` before the run and again after it,
and that file is the human queue; `qmcp`'s `AGENTS.md` carries this and the
`--clean=False` alternative. The cookbook checks make a database for the
run; the suite as a whole is not promised to.

## 3. Audio capture on the engine's machine

Measured 2026-09-27 and 2026-09-29. None of it is visible in a device
listing:

- **Twenty or more input devices across four host APIs**, with the same
  microphone appearing once per host API under a byte-identical name.
- **The backend default is a capture card**, not a microphone.
- **Every device is natively 44100 or 48000 Hz.** Opening one at 16000
  failed on all four APIs, including the default.
- **WDM-KS devices open without error and return garbage** — samples around
  `-2e38`, or NaN — and WDM-KS implements no blocking read, so a stream
  opened for `read()` fails with *Blocking API not supported yet*. Capture
  goes through a callback for that reason (`joe` #20).
- **At the 2026-09-29 run, every MME, DirectSound and WASAPI input failed to
  open**, while the WDM-KS entries opened; §1 says what that does and does not
  establish.

`uv run joe voice setup`, in the engine's checkout, is the route to a
microphone. It tries every input while the person talks, ranks microphones by
loudness and each microphone's entries by host API with WDM-KS last, and
saves only an entry that recorded the test sentence. The choice is read at
record time; `uv run joe voice devices` marks it and `JOE_INPUT_DEVICE`
overrides it. `joe voice level --every` still exists and only measures.

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
- **`uv run qmcp preflight` reads the REUSE step red in a uv virtual
  environment**, with *No module named pip*: `qmcp`'s pinned seed installs the
  tool with pip, and `uv`'s environment ships none. `qm` #134 runs the step
  through `uvx` on `qm`'s `main`; `qmcp` takes it with the governance pin
  bump (§1), and until then the hosted gate is the one to read.
- **Whether project names transcribe reliably, and what a sentence-length
  utterance costs in latency, are unmeasured** — named as such in Phase 10's
  constraints, and resolution confirms rather than trusts so the first does
  not have to be.
- **Nothing checks what the local model says.** The tests assert what is sent
  to it and how its replies are read, over a stand-in transport; its answers
  are judged by the person who approved the run (§6 has one reading). On the
  workstation the set was built on, the model service's runner was seen to
  stall partway through a reply after reusing a cached prompt, with later
  calls queued behind it; every call is capped, so a stall is a failed run
  naming the endpoint, and unloading the model frees it.

## 5. Standing constraints

- *Keep everything local* is **not** in force.
- **Every act is asked, for every runtime**, the local model included. Growing
  a habit of approval into a rule is Phase 11, after Phase 10 has been used,
  and only for runs that spend nothing.
- **`vox` is vendored at `vendor/vox`**, never at the repository root:
  `git submodule update --init vendor/vox` before `uv sync --all-extras`,
  and the pin is deliberate rather than floated.
  `perspectives/2026-09-28-the-voice-loop-meets-the-field.md` carries why
  the root is refused.
- **The microphone is chosen by `uv run joe voice setup`**, saved in the
  engine's checkout and read at record time, so a running backend uses it on
  its next recording. `JOE_INPUT_DEVICE` in the backend's environment still
  overrides it.
- **`vox` is public as of 2026-09-27**, and `joe` publishes to GitHub Pages:
  a push to `main` builds the frontend and deploys three files, none of them
  personal.
- **`vox` is Apache-2.0 and `joe` is MIT**, decided and merged 2026-09-27
  (`vox` #6, `joe` #12).
- **`qmcp`'s pinned seed carries the parallel-pull-request rule**, since its
  governance pin at `235708c` includes the corpus merge that stated it. A
  project branch of the corpus that took `main` before that merge enforces one
  open pull request per contributor in its `slot` check until `main` is
  propagated into it.
- **The design-review launch waits on the harness queue**, not in a
  terminal: an approval request on the human queue (port 3141,
  `/v1/human/requests`, id `design-review-qm-audit-2026-09-27`,
  re-queued on expiry) states the exact count. **The queue was not read for
  this stamp**: the harness was not running (`curl http://127.0.0.1:3141/health`
  answered nothing), so whether that request is still pending is established
  by `uv run qmcp human list` against a running server and not by this page.
  A session picking it up reads the answer from the queue, launches on approve
  with the counts the request states, and puts the next phase's count back the
  same way. Answering by speech is one command:
  `uv run qmcp human voice <request-id>`.
- **Merged branches are not deleted by a handoff**, where
  `handbook/handoffs/README.md` places deletion outside what one authorises.

## 6. The baseline at the stamp

Phase 0 of `qmcp`'s `docs/voice-loop-next-phases.md`, run on 2026-10-18 from
a worktree of `qmcp` `main` at `df42315`, `vendor/vox` at `c0b9b18` and
`governance/qm` at `235708c`, on the workstation the set was built on. Nothing
in it spoke or listened.

| Evidence | Kind | Result |
|---|---|---|
| `uv run --frozen --all-extras pytest -q`, `QMCP_DATABASE_URL` at a scratch path | offline, deterministic | 1422 passed, 9 skipped, 2 deselected (the hosted-model tests) |
| `uv run qmcp cookbook voice`, `cookbook instruct`, `cookbook instruct --runtime scripted`, `cookbook converse` | tier 1: offline, every take scripted, `vox`'s deterministic engine | 5 of 5, 6 of 6, 2 of 2, 1 of 1 `[ok]` |
| `uv run qmcp localmodel check` | the model service, asked and not generating | `qwen2.5-coder:7b` served on the local GPU |
| `uv run qmcp cookbook instruct --runtime local` | tier 2: the local model, no network | both cases `[ok]` in 156 s; the second instruction carried the first and what it found |
| `uv run qmcp preflight` | the seed workflow runner | 9 of 10 steps passed; *Install REUSE* red for the reason in §4 |
| tier 3, a person at the microphone | live device | not run |

**What tier 2's green asserts.** Continuity: the second instruction is handed
the first and what it found. Not the answers, which at this run were weak. The
first named `README.md` and did not quote it as asked; the second searched
seven times for phrases the model had made up, then quoted a heading where a
sentence was asked for. That matches what the review page records of the
model, and it bears on any loop that leans on its reading.

**Where each part is, and what tests it.** The voice seam is
`qmcp/integrations/voice/` (`adapter.py`, `service.py`, `check.py`,
`vocabulary.py` with `vocabulary.toml`); the instruction loop is
`qmcp/instructions/` (`dialog.py`, `spoken.py`, `act.py`, `continuity.py`,
`converse.py`, `check.py`, `service.py`); the runtimes are
`qmcp/integrations/agents/`. Their tests, by the modules each exercises:
`test_voice_integration.py` and `test_voice_route.py` the adapter and the
route; `test_instructions_spoken.py`, `test_instructions_resolve.py` and
`test_instructions_route.py` recording and resolution; `test_instructions_act.py`,
`test_cli_instructions_act.py`, `test_agents_runtime.py` and
`test_agents_local.py` acting and the runtimes; `test_converse.py`,
`test_server_converse.py`, `test_spoken_iteration.py` and
`test_tacit_agreement.py` the standing conversation; `test_vocabulary.py`,
`test_vocabulary_authoring.py` and `test_declared_checks.py` the vocabulary and
the checks it declares; `test_cookbook_voice.py` and `test_cookbook_instruct.py`
the offline checks above.
