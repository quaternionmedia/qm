# Handoff — the voice loop, and the three-process development environment

**Stamped 2026-10-04.** `qm` `main` at `df1cb51`; `vox` `main` at
`d94fe6b`; `joe` `main` at `2ba994d`; `qmcp` `main` at `ed01fc0`; `dossier`
`main` at `414be1c`. Nothing has merged on any of them since the previous
stamp; everything below §0 is open. Every figure here was true at those
commits and nowhere else. Re-derive before acting on any of it.

`vox` and `joe` carry no `governance/qm` submodule, so the cross-repository
state is recorded here and nowhere else. `vox` joined the roster on
2026-09-27, in `core`; `joe` is in `performer-display` and predates this
work.
[`hil-review-2026-10-04.md`](hil-review-2026-10-04.md) is the companion:
the whole open set reviewed as one, with the demo branches, the demonstration,
the decisions waiting on a person and the order the set lands in.
[`hil-review-2026-09-27.md`](hil-review-2026-09-27.md) holds the decisions
from the round before it. Nothing in this page is a decision.

The why of all of it is in three retrospectives, and not here:
`perspectives/2026-09-27-the-voice-loop.md`,
`perspectives/2026-09-28-the-loop-lands-its-remains.md` and
`perspectives/2026-09-28-the-voice-loop-meets-the-field.md`. The plan the
open work follows is Phase 10 of `qmcp`'s `docs/ROADMAP.md`, which is itself
on an open pull request (§1). **Continuity comes from qmcp, not the model**:
the loop's agent is a runtime qmcp calls -- the local model it stands up first
-- handed the project's earlier work from qmcp's own record.

---

## 0. What landed

Two rounds of merges, grouped by what they carry. The first built the loop
and landed by 2026-09-28; the second made it answerable from a page, and
ran to 2026-10-03.

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
deterministic engine or `--live` with a person at the speaker.

## 1. What remains, and what done looks like

- **`joe` records on one host API, and the other three are a reading of one
  run.** `joe` #20 moved capture to a callback stream, because WDM-KS
  implements no blocking read, and on the hardware that run used the WDM-KS
  entry recorded a second of finite samples while every MME, DirectSound and
  WASAPI input failed to open through both paths. The pull request attributes
  that to the audio engine's state on that machine rather than to the change,
  and the ranking of host APIs is exercised by tests, not by that run. *Done*
  is unchanged: one device on each host API recording a non-silent second, or
  the reason established rather than read off a single run.
- **`joe`'s Playwright specs run in CI, and the red has still not come.**
  joe #14 widened `e2e.yml` to pushes and pull requests; every run since has
  concluded `success` (`gh run list -R quaternionmedia/joe --workflow
  e2e.yml`, read 2026-10-03). What a red looks like there is untested. *Done*
  is one deliberate break dispatched, seen red, and restored.
- **`dossier`'s GIF re-encode is still only measured.** Nothing on `dossier`
  `main` has touched `docs/screenshots/first-run.gif` since #59, whose
  scratch-database run left it byte-identical; the re-encode needs the real
  database to reproduce.
- **The wider loop is built, on open pull requests, and waits on one review.**
  Speaking an instruction, the local model acting on it, and the answer spoken
  back is Phase 10 of `qmcp`'s roadmap; all four of its deliverables, a
  one-command demonstration, the standing conversation that makes it spoken
  from end to end, and the onboarding and cookbook that set it up and say what
  to say are open and green, and the review page above takes them as one.

**The open set at the stamp.** Every row is green on its checks; a draft is
one stacked on another open pull request, and nothing else.

| Repository | PR | Branch → base | Carries |
|---|---|---|---|
| `qmcp` | #54 | `docs/the-spoken-instruction` → `main` | Phase 10 as built, and Phase 11, habits into auto-approvals, which covers only runs that spend nothing |
| `qmcp` | #55, **draft**, on #54 | `docs/roadmap-current-state` → `docs/the-spoken-instruction` | the roadmap's test counts replaced by the relation to the command, and Phase 9's voice route stated |
| `qmcp` | #56 | `feat/preflight-command` → `main` | `uv run qmcp preflight`, a dispatcher to the seed workflow runner |
| `qmcp` | #58 | `feat/free-text-answers-by-voice` → `main` | **deliverable 1.** An open question answered by voice: the transcript read back, recorded on `record`, a transcript's closing stop not doubled |
| `qmcp` | #60 | `chore/vox-pause-pin` → `main` | `vendor/vox` at the head of `vox` #10's branch |
| `qmcp` | #61, **draft**, on #60 | `feat/instruction-inbox` → `chore/vox-pause-pin` | **deliverable 2.** The instruction inbox: recorded against a project by whole-word roster matching, spoken with the long pause, nothing run |
| `qmcp` | #62, **draft**, on #61 | `feat/act-on-instruction` → `feat/instruction-inbox` | **deliverable 3.** Acting on an instruction: consent asked for every runtime; a brief from qmcp's record carrying the project's earlier work; the clone remembered; `local`, the model on the machine reading the clone with tools that cannot write; a coding assistant's command line behind the same contract, given the same brief and resuming nothing |
| `qmcp` | #63, **draft**, on #62 | `feat/result-spoken` → `feat/act-on-instruction` | **deliverable 4.** The outcome said back; `qmcp cookbook instruct` runs the loop offline; the README states qmcp as the local model backend |
| `qmcp` | #64, **draft**, on #63 | `feat/live-model-demo` → `feat/result-spoken` | `qmcp cookbook instruct --runtime local`, continuity on the real local model in one command; `docs/voice-loop-demo.md`, the loop in three tiers |
| `qmcp` | #65, **draft**, on #64 | `feat/spoken-conversation` → `feat/live-model-demo` | one standing spoken conversation, started by `qmcp serve --converse`: two commands, then nothing typed; waiting questions asked aloud; the clone found by name; a stalled model call recovered once |
| `qmcp` | #66, **draft**, on #65 | `fix/voice-loop-review` → `feat/spoken-conversation` | the loop's tests and documents reviewed against its code: the branches no test reached tested, `localmodel check` reporting whether the model is served, the documents corrected |
| `qmcp` | #71, **draft**, on #70 | `feat/instruction-vocabulary` → `feat/tacit-agreement` | an instruction's take hinted with the project names it is likely to carry |
| `qmcp` | #70, **draft**, on #69 | `feat/tacit-agreement` → `fix/audible-voice` | a confident instruction agreed to tacitly unless interrupted; the read-back's word is `agree` |
| `qmcp` | #69, **draft**, on #68 | `fix/audible-voice` → `feat/answer-controls` | the voice heard: `vendor/vox` at `vox` #12's branch; the consent said with the clone's folder; setup checks the output |
| `qmcp` | #68, **draft**, on #67 | `feat/answer-controls` → `docs/voice-dev-loop-guide` | closed questions hint and offer their options to the engine; "repeat" re-asks without spending a retry; prompts leave the turn open so the engine cues the person |
| `qmcp` | #67, **draft**, on #66 | `docs/voice-dev-loop-guide` → `fix/voice-loop-review` | `docs/voice-loop-demo.md` as the loop's onboarding -- what runs where, the workspace, setup with a done-signal per step, the three tiers -- and its cookbook, what to say |
| `vox` | #13, **draft**, on #12 | `feat/listen-confidence` → `fix/sapi-playback` | `confidence_key` on the contract; a listen keeps how sure the engine was |
| `vox` | #12, **draft**, on #11 | `fix/sapi-playback` → `feat/answer-hints` | the platform voice played through SAPI on Windows, on an output that can be named |
| `vox` | #11, **draft**, on #10 | `feat/answer-hints` → `feat/pause-parameter` | `hint_param` on `EngineContract`; `options` on an announcement |
| `vox` | #10 | `feat/pause-parameter` → `main` | `pause_param` on `EngineContract`, sent only when the contract names it |
| `vox` | #9 | `docs/handoff-restamp` → `main` | `HANDOFF.md` at the current tips |
| `joe` | #23 | `feat/instruct-by-voice` → `main` | **Instruct by voice** on the page |
| `joe` | #24, **draft**, on #23 | `docs/readme-overview` → `feat/instruct-by-voice` | the README's overview: joe's two jobs, and the local model doing the work once a person approves |
| `joe` | #25, **draft**, on #24 | `docs/cookbook-voice-loop` → `docs/readme-overview` | the cookbook's recipe for joe's half of the voice dev loop |
| `joe` | #26 | `feat/short-answer-recognition` → `main` | a take transcribed as English, as one utterance, toward its hint, with a beam when short |
| `joe` | #29, **draft**, on #28 | `feat/take-confidence` → `feat/live-transcript` | a listen says how sure it is of its transcript |
| `joe` | #28, **draft**, on #27 | `feat/live-transcript` → `feat/turn-controls` | the take shown as it is written, its words strikable, every segment kept as a datapoint |
| `joe` | #27, **draft**, on #26 | `feat/turn-controls` → `feat/short-answer-recognition` | answers by key or button, `~` held to keep a turn open, and tones that let the loop run by ear |
| `qm` | #134 | `evolve/reuse-lint-runs-locally` → `main` | the REUSE lint through `uvx`; reaches `qmcp` at its next pin bump |
| `qm` | #135 | `evolve/voice-loop-handoff-2026-10-03` → `main` | this page and its review page |

`qmcp` #57 (an MCP tool for a coding-assistant session to ask the queue) and
#59 (recall from a coding assistant's session store) were closed unmerged: the
loop's agent is a runtime qmcp calls, and its continuity is qmcp's own record.

**Each repository has a demo branch**, `demo/voice-loop-2026-10-04`: its
`main` with every open pull request above merged in order. It is for testing
and demonstrating the set together, never for merging; the set lands through
its own pull requests, in the order the review page gives.

**What remains after the set lands:**

- **A person at the microphone.** Every take so far was scripted, which says
  nothing about a real one. *Done* is tier 3 of `qmcp`'s
  `docs/voice-loop-demo.md` -- `uv run joe dev`, `uv run qmcp serve --converse
  --runtime local`, and then speech -- run once and recorded.
- **What a standing conversation keeps.** `joe` keeps every take as a file;
  a retention rule is the review page's decision 5.
- **The pin moves to `vox`'s merge commit.** #60 pins `vendor/vox` at the
  head of a branch; once `vox` #10 merges, the pin moves to the commit on
  `vox` `main`, and `uv run qm pins` is the check.
- **One dialog, written twice.** #58's open question and #61's instruction
  dialog read back and confirm the same way, each with its own copy of the
  helper that says back what was heard. Once both are on `main`, one serves
  both.
- **The roadmap's boxes, and `qmcp`'s own pages.** #54's lists tick nothing
  yet. `qmcp`'s `AGENTS.md` (from #56) explains a step that installs with pip
  red under the local runner; once `qm` #134's pin bump leaves no such step,
  that paragraph goes in the same change.
- **The command-line runtime against the real tool.** Its command line and its
  reading of the output are asserted; it has not been run, because the tool is
  not on the workstation the set was built on.
- **Two bounds nobody has set.** `run_forever` has no bound on an idle queue,
  and a standing worker needs one.
- **Merged branches in every repository above.** Some remain and some are gone;
  `handbook/handoffs/README.md` places deletion outside what a handoff
  authorises, and `uv run qm branches` says what deleting one would cost.

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
- **The local workflow runner cannot run the REUSE step green in a uv
  virtual environment**, because the pinned seed installs the tool with pip
  and `uv`'s environment ships none. `qm` #134 moves the step to `uvx`;
  until that reaches `qmcp`'s pin, the seed runner reports that step red for
  an environment reason — and so will `uv run qmcp preflight` once #56
  merges, since it dispatches to the same runner — and the hosted gate is
  the one to read.
- **Whether project names transcribe reliably, and what a sentence-length
  utterance costs in latency, are unmeasured** — named as such in Phase 10's
  constraints, and resolution confirms rather than trusts so the first does
  not have to be.
- **Nothing checks what the local model says.** The tests assert what is sent
  to it and how its replies are read, over a stand-in transport; its answers
  are judged by the person who approved the run. On the workstation the set
  was built on, the model service's runner was seen to stall partway through
  a reply after reusing a cached prompt, with later calls queued behind it;
  every call is capped, so a stall is a failed run naming the endpoint, and
  unloading the model frees it.

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
  governance pin at `235708c` includes the corpus merge that stated it. Several
  ready pull requests stand open there at once with green slot checks, and the
  stack check refuses a ready one stacked on another. A fork pinned behind that
  commit still enforces one open pull request per contributor.
- **The design-review launch waits on the harness queue**, not in a
  terminal: an approval request on the human queue (port 3141,
  `/v1/human/requests`, id `design-review-qm-audit-2026-09-27`,
  re-queued on expiry) states the exact count. **The queue was not read for
  this stamp**: the harness was not running (`curl http://127.0.0.1:3141/health`
  refused the connection), so whether that request is still pending is
  established by `uv run qmcp human list` against a running server and not by
  this page. A session picking it up reads the answer from the queue, launches
  on approve with the counts the request states, and puts the next phase's
  count back the same way. Answering by speech is one command:
  `uv run qmcp human voice <request-id>`.
- **Merged branches are not deleted by a handoff**, where
  `handbook/handoffs/README.md` places deletion outside what one authorises.
