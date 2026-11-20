# Perspective — The Voice Loop: Checks That Answered a Different Question

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (1M context) |
| **Task** | A three-repository voice-interaction seam, taken from a suite of mocks to a closed deterministic loop, and from three tangled branches to two merged lines. Most of what follows shares one shape: a check reporting on something other than what it appeared to be about. |

## 0. Standing and evidence

`joe` `main` at `fa0ce67`, `vox` `main` at `a9d7988`, `qmcp`
`feat/voice-interaction` at `cb071a6`. Figures below were true at those commits
and nowhere else. Each is named beside the command that produced it.

## 1. A suite of mocks describes itself

Fifteen vox tests passed. Every one replaced `JoeSTT` with a `MagicMock`, so
what passed was the assertion that a call had been made with certain arguments
— arguments taken from the same docstring the implementation was written from.
Nothing crossed a socket. The only end-to-end evidence was a note recording a
manual round trip, which said in its own text that it should not be trusted.

The engine is now replaced instead of the client: a `ThreadingHTTPServer` on an
ephemeral port speaking joe's `/api/voice/*` contract, driven by an unmodified
`JoeSTT`. A client needing changes to talk to a stand-in is not standing in for
anything.

**Caught by:** nothing then.
`walkthrough/test_closed_loop.py::test_it_went_over_the_wire` now asserts the
exact sequence of paths the engine served, so a loop that hands text to itself
fails.

## 2. An average is a claim that the distribution is boring

A suite of thirty near-trivial tests took 16.76s. Two costs, neither
attributable to any test:

`ThreadingHTTPServer.shutdown()` waits out one `serve_forever` poll interval,
default 0.5s, paid on every teardown — five of the sixteen seconds.

`JoeSTT` used module-level `httpx.get`/`httpx.post`, which construct a fresh
`Client` per call. Four consecutive builds measured 610, 640, 627 and 643 ms,
about 240 ms of each being
`ssl.create_default_context(cafile=certifi.where())`, paid on a
`http://127.0.0.1` URL that never uses it. A reused client answers in ~10 ms.
A closed loop makes three calls.

The first measurement averaged five calls and gave 1556 ms, which is consistent
with a slow first call and a warm cache, and would have led to leaving it
alone. Individual timings showed the shape immediately.

**Caught by:** `test_one_client_serves_every_call`, which exists because the
regression has no symptom other than slowness.

## 3. A stale artifact closes the loop as well as a real one

An assertion that `round_trip(...).closed is True` establishes that two
transcripts matched. Had `speak()` stopped writing, a leftover file from a
previous run would have been read instead — and the output path is derived from
a hash of the text, so the leftover carries exactly the right name.

The walkthrough runs in a fresh `tmp_path_factory` directory and asserts the
file exists and exceeds a 44-byte header. The mutation *speaking stops writing
a file* is recorded for this reason: it is the one that would otherwise pass.

## 4. A mutation harness is itself a check

Eight mutations were written and all eight went red against a baseline
confirmed green first. That establishes nothing until the harness is shown
capable of reporting otherwise, so it was given a mutation nothing catches —
rewording a `--help` string. It reported `INERT` and exited 1. Without that,
eight green rows and eight inert ones look identical.

## 5. A conflict's cause need not be where the conflict is

`joe` #9 read `CONFLICTING` and was stacked on another open pull request's
branch. The stacking was not the cause.

`joe`'s `main` held no `api.py`, `cli.py`, `pyproject.toml` or `tests/`;
retargeting would have produced a 22-commit diff under a title about speech, on
a base whose own tests cannot run. Separately, the base branch had moved five
commits ahead of the cut point, two of them hardening filename handling on the
routes the voice work touches. One `git ls-tree origin/main` distinguished the
two stories, and was run only after a plan had been agreed on the strength of
the first.

## 6. Two resolvers for one question, one of them hardened

`9e70fc9` hardened `_audio_file`. `POST /api/voice/transcribe` resolved through
`_resolve_audio_path`, which had none of those checks. Observed against the
branch, with `good.wav` present under `Data/Audio`:

| name | `/api/audio/{name}` | `/api/voice/transcribe?filename=` |
|---|---|---|
| `good.wav` | 200 | 200 |
| `good.wav.` | 404 | **200** |
| `good.wav ` | 404 | **200** |
| `good.wav\0` | 404 | **500** |

The endpoint transcribed a file under a name no listing shows, and answered a
NUL byte with an unhandled exception. Neither branch introduced it; it was
created by the hardening and the voice work arriving separately, each correct
alone.

**The first probe ran without the target file present** and returned 404 on
both routes, which reads as *hardened* and means *absent*. One command
separated a finding from its opposite, and the error pointed towards
reassurance.

**Caught by:** `_is_bare_filename`, shared by both resolvers, and
`test_both_resolvers_agree_on_every_bad_name`. Dropping the call from the voice
resolver reddens 6 tests; removing the trailing-dot rule from the shared helper
reddens 10 across both, which is the property worth having.

## 7. Position is not meaning

`VoiceApprovalLoop.run_once` mapped a spoken decision onto a request's
`options` by index — `options[0]` for yes. Every one of its tests passed
`["approve", "reject"]`, so the assumption was never exercised. A request
carrying `["reject", "approve"]` would have recorded a spoken "yes" as
`reject`, and nothing in a request states which position is which.

`choose_option` now reads the options, falling back to position only when none
is recognisable. Reverting it to pure position reddens 7 tests.

## 8. A public repository cannot vendor a private submodule

`qmcp` is public and vendors `vox`, which was created private. Every check on
`qmcp` #38 had failed since 2026-09-22 with `remote: Repository not found`
during submodule checkout — five failures, one cause, five days unnoticed
because draft status makes a red pull request unremarkable.

The inherited handoff recorded *"Test suites are green in all three"*, which
was true locally and said nothing about CI, and CI was never mentioned.

`check-submodule-refs` deserves its own note: it failed correctly and its error
text named the alternative cause — *"This check cannot tell that apart from a
private submodule remote that an unauthenticated runner cannot read"* — with
the command that distinguishes them. A check that states what it cannot
distinguish is worth more than one that guesses.

`vox` is now public, which resolved all five.

## 9. A leak reached a public repository through a gate nobody runs

A handoff page naming a private repository was committed and pushed to a public
one. Every gate on that pull request was green.

`qm private-names` detects exactly this and **is run by no workflow**.
`registries.yml` excludes it deliberately, and states the admission test: a
check on a runner reads committed files and nothing else, and this one reads
either a gitignored companion or the forge. The check's own docstring
nevertheless read *"CI runs it that way"* — an instruction and a claim
disagreeing, with the claim being the reassuring one. The docstring is
corrected; the gap is stated rather than closed, since closing it requires
either a gate that reds a pull request for a reason its author cannot fix, or a
runner credentialed to enumerate private repositories.

The redaction became unnecessary when `vox` was made public. The gap did not.

## 10. A signature check reporting on what the forge has seen

`signature-check` reported a commit as `signature could not be checked` while
`git log --format=%G?` and `git verify-commit` both reported a good signature
on the same commit in the same clone. The step exports `GH_TOKEN` and asks the
forge, and the commit had not been pushed. Pushing it turned `E` into `G`
without touching the commit.

`E` is *cannot check*, distinct from `N`, *no signature* — a distinction worth
reading before concluding a commit is unsigned, and one that survived only
because the two sources were compared rather than the first being believed.

## 11. A suite that had only ever run in one place

`joe`'s Python tests ran on no runner. Its single workflow builds and
publishes the frontend and reads no Python, so every result the suite had ever
produced came from one Windows workstation. Reconciling the two branches made
a workflow possible for the first time, and the first run on `ubuntu-latest`
reported two things Windows cannot show.

`OSError: PortAudio library not found`, at collection, before any test ran.
`sounddevice` binds a native library that its Windows wheel bundles and its
Linux wheel does not; `capture.py` imports it at module scope and `api.py`
imports `capture`. Installing `libportaudio2` cleared it.

Then 74 passed and 6 failed, all in `tests/test_main.py`, all one cause:

    midi_path: str = f"{current_path}\Data\Output\{iteration}\MIDI\\"

Paths composed with literal backslashes are one filename component on Linux
rather than a directory structure. The same line is the source of the
`invalid escape sequence` warnings on `\D`, `\O` and `\M`, which a later
Python raises rather than warns. The defect is years old, unrelated to any of
this work, and had nowhere to surface.

The workflow runs on `windows-latest`, which is where the application runs, and
records the above in its own comment. A matrix is worth adding once those paths
go through `pathlib`; adding it first would mean either a permanently red job
or one marked `continue-on-error`, which is a green check standing where
nothing is enforced.

## 12. A recorded artifact that churned, and a harness that did not restore

Both found on the authoring machine, after CI had passed on both.

`Path.write_text` translates newlines to the platform separator. The
walkthrough's artifact is therefore written CRLF on Windows and LF on Linux,
so every local test run left `walkthrough/closed-loop.md` reported modified
while the runner's drift gate saw nothing. `git diff` printed no lines and the
file was 1466 bytes against a committed 1424: the whole difference was 42 line
endings. A drift gate that passes on one platform while the authoring platform
shows a dirty tree teaches a contributor to ignore it.

The mutation harness had the same fault with worse consequences. It read each
target with `read_text` and restored it with `write_text`, so a LF source file
came back CRLF, and a run left four tracked files under `vox/` modified — by a
harness whose entire contract is to leave no trace. An earlier check had
compared *content* after a run and reported clean, which was true: content was
identical every time and the bytes were not. The check and the defect passed
each other.

Both writers now pin the newline. The harness reads and writes bytes and
asserts its own restore, because putting tracked source back is the one thing
it must never get quietly wrong.

## 13. Two defects introduced here

**An escape written through a heredoc, twice.** A replacement targeting
`"\\" in filename` failed to match, so the first of two substitutions silently
did nothing while the second succeeded, leaving `api.py` calling an undefined
function. It surfaced because a `grep` hit *count* was checked rather than an
exit status. Later in the same session the identical mechanism collapsed a
`newline="\n"` argument into a literal line break and broke
`walkthrough/test_closed_loop.py`. This failure mode was written down before
either happened, and the second occurrence came after the first had been
diagnosed. The rule that actually holds is narrower than "be careful": text
containing backslash escapes is written with an editor, never assembled inside
a shell heredoc.

**A fixture colliding with the one it borrowed from.** A new `voice_dirs`
fixture created `Data/Audio` under the same `tmp_path` as the existing
`audio_dir` fixture, and the single test requesting both failed with
`FileExistsError` across eleven parametrizations. Composing a fixture means
reading what it builds, not what it is named.

## 14. What the loop still does not establish

The deterministic engine carries text faithfully because it is a codec. It
establishes the seam, the HTTP contract, the file handoff and the loop closing,
and says nothing about whisper, which is the component that can mis-hear. The
two claims are separated deliberately and the recorded artifact says so in its
own text, so that `closed: True` is not read as comprehension.

What is deterministic is asserted. What cannot be is run by hand and reported
as a different claim. The failure this is arranged against is a green suite
quietly becoming the evidence for something it never touched — which is where
this began.

*Peter Kagstrom, 2026-09-27. Tools: Claude Opus 5 (1M context).*
