# Perspective — The Voice Loop: Six Things a Suite of Mocks Could Not Tell Us

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (1M context), driving the session |
| **Task** | Picking up a three-repository voice-interaction seam left on 2026-09-21, whose stated goal was a short, closed, deterministic, voice-driven development and feedback loop. The harness half was built. Six things were wrong on the way, and four of them were invisible to a green test suite. |

## 0. Standing and evidence

`vox` PR #1 at `27d83b6`, `joe` PR #9 at `d1dc980`, both open and unmerged.
Every figure below was true at those commits and nowhere else. The commands
are named beside what they showed.

## 1. A suite of mocks is a suite about itself

**The assumption.** vox's 15 passing tests meant the seam worked.

**What was true.** Every one of them replaced `JoeSTT` with a `MagicMock`.
They proved a call was made with certain arguments. Nothing crossed a socket,
nothing touched a file, and the arguments were checked against the same
docstring the implementation was written from. The only end-to-end evidence in
the repository was a note in `HANDOFF.md` saying a round trip had been run by
hand — and, to its credit, saying *repeat one yourself rather than trusting
this note*.

**What was done.** `vox.engine` replaces the *engine* rather than the client:
a real `ThreadingHTTPServer` on an ephemeral port, speaking joe's
`/api/voice/*` contract, driven by an unmodified `JoeSTT`. If `JoeSTT` needed a
change to talk to it, it would not be standing in for anything.

**The check that would have caught it.** None existed. One does now —
`walkthrough/test_closed_loop.py::test_it_went_over_the_wire` asserts the exact
sequence of paths the engine was asked for, so a loop that hands the text to
itself fails rather than passes.

## 2. The thing that made it slow was the thing nobody measures

**The assumption.** HTTP on loopback is fast, so the loop's cost is the work.

**What was true.** The suite took 16.76s for thirty tests that do almost
nothing. `--durations` put 0.5s on every *teardown* — `ThreadingHTTPServer.
shutdown()` waits out one `serve_forever` poll interval, and the default is
0.5s. That was five seconds of the sixteen, paid once per test and attributable
to no test.

The rest was worse. `JoeSTT` used module-level `httpx.get`/`httpx.post`, which
construct a fresh `Client` per call. Measured here, four builds in a row:
610ms, 640ms, 627ms, 643ms — **not** a first-call cache miss, which is what it
looked like on the first measurement of five averaged calls. About 240ms of
each is `ssl.create_default_context(cafile=certifi.where())`, paid in full on a
`http://127.0.0.1` URL that will never use it. A reused client answers the same
request in ~10ms.

**What it cost.** A closed loop makes three calls. Two seconds per iteration,
spent building SSL contexts for an unencrypted loopback socket.

**The reusable part.** The first measurement — five calls, averaged — gave
1556ms and was consistent with "the first one is slow and the rest are cached."
That reading would have led to leaving it alone. The average hid the shape;
individual timings showed it immediately. *An average is a claim that the
distribution is boring.*

**The check.** `test_one_client_serves_every_call`. It exists because this
regression has no symptom: nothing breaks, the loop just gets slow again, and
a slow loop is the thing the session set out to fix.

## 3. The stale artifact closes the loop too

**The assumption.** A test asserting `round_trip(...).closed is True` proves
the loop closed.

**What was true.** It proves the two transcripts matched. If `speak()` had
silently stopped writing and a WAV from a previous run was still on disk, the
engine would have read that one, the transcripts would have matched, and the
test would have passed — in a repository where the output path is derived from
a hash of the text, so the leftover file has exactly the right name.

**What was done.** The walkthrough runs in `tmp_path_factory.mktemp()`, a fresh
directory per run, and asserts the file exists and is larger than a 44-byte
WAV header. The mutation *speaking stops writing a file* is in the recorded
table specifically because it is the one that would otherwise pass.

**Why this is `AGENTS.md` item 12 and not item 10.** Nothing errors. The tool
is fine. The result describes the scaffolding — a directory that was not
cleaned — rather than the behaviour.

## 4. A guard nobody has broken is a guard nobody has tested

Eight mutations were written against the new code and all eight went red
against a baseline confirmed green first. That is not the interesting part.

The interesting part is that **the mutation harness is itself a check**, and it
was given a mutation nothing catches — rewording a `--help` string — to see
whether it would report `caught` anyway. It reported `INERT` and exited 1. Had
it not, the eight green rows would have meant nothing, and they would have
looked exactly the same.

`walkthrough/mutations.md` is the record, regenerated by the command rather
than written by hand, and CI fails if the committed copy drifts from what a run
produces.

## 5. A conflict's cause is not always where the conflict is

**The assumption.** joe PR #9 read `CONFLICTING` because it was stacked on
another open PR's branch, so retargeting it to `main` would fix both problems.

**What was true.** Two separate things, neither of them the stacking:

- joe's `main` is from 2024-12-12 and contains **no** `api.py`, `cli.py`,
  `pyproject.toml` or `tests/`. The application the voice work extends is not
  there. Retargeting would have produced a 22-commit diff under a title about
  speech, on a base whose own tests cannot run.
- `origin/docs/onboarding-hardening` had moved five commits ahead of where the
  branch was cut, two of them hardening filename handling on the audio routes.
  *That* is the conflict.

The fix was a rebase onto the current base, which is a different action from
the one the evidence first suggested. It took `git ls-tree origin/main` to see
it — one command, and the plan changed completely.

**The reusable part.** "This branch conflicts because it is stacked" is a
story that explains the symptom. The command that distinguishes it from the
alternative is cheap, and was not run until the plan had already been agreed.

## 6. Two resolvers for one question, and only one of them was hardened

**The assumption.** The base's filename hardening protected joe's file-serving
routes, and the voice route inherited it because it is in the same file.

**What was true.** `9e70fc9` hardened `_audio_file`. `POST /api/voice/transcribe`
goes through `_resolve_audio_path`, a different function with none of the
checks. With `good.wav` present under `Data/Audio`, observed by running it:

| name | `/api/audio/{name}` | `/api/voice/transcribe?filename=` |
|---|---|---|
| `good.wav` | 200 | 200 |
| `good.wav.` | 404 | **200** |
| `good.wav ` | 404 | **200** |
| `good.wav\0` | 404 | **500** |

The endpoint transcribed a file under a name no listing shows, and answered a
NUL byte with an unhandled exception. This was not introduced by the voice
work and it was not introduced by the hardening — it was created by the two
arriving on separate branches, each correct alone.

**What was nearly missed.** The first probe ran without the target file
present and returned 404 on both routes for the alias cases. Read at face
value that says "hardened". It says *missing*. The second probe created the
file first, and the 200s appeared. One more command between a finding and its
opposite, and the direction of the error was towards reassurance.

**The check.** `_is_bare_filename`, shared by both resolvers, and
`test_both_resolvers_agree_on_every_bad_name` parametrized over the list that
already existed. Broken twice and seen to fail: removing the call from the
voice resolver reddens 6 tests, removing the trailing-dot rule from the shared
helper reddens 10 across *both* resolvers, which is the property that matters.

## 7. Two defects this session caused

Written the same way as the ones it found.

**A heredoc ate an escape, again.** A Python replacement written through a
shell heredoc failed to match `"\\" in filename`, so the first of two
substitutions silently did nothing while the second succeeded — leaving
`api.py` calling a function that did not exist. It was caught immediately by
`grep` showing one hit where two were expected, and only because the hit count
was checked rather than the exit status. This failure mode is already written
down and was walked into anyway.

**A fixture collided with the one it borrowed from.** A new `voice_dirs`
fixture created `Data/Audio` under the same `tmp_path` as the existing
`audio_dir` fixture, and the one test that asked for both failed with
`FileExistsError` on eleven parametrizations. `exist_ok=True` is the fix; the
lesson is that composing someone else's fixture means reading what it builds,
not what it is called.

## 8. What the loop still does not prove

The deterministic engine carries text through a real WAV faithfully because it
is a codec. It says nothing about whisper, which is the part that can mis-hear,
and it is not a substitute for it. The two questions were separated on purpose
and the recorded artifact says so in its own text, so that a reader who finds
`closed: True` does not read it as "the machine understood."

That separation is the whole design. What is deterministic is asserted; what
cannot be is run by hand and reported as a different claim. The failure this
avoids is the one where a green suite quietly becomes the evidence for
something it never touched — which is, exactly, where this session started.

*Peter Kagstrom, 2026-09-27. Tools: Claude Opus 5 (1M context).*
