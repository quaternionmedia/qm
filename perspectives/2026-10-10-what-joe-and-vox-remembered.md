# What joe and vox remembered — 2026-10-10

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-10 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5 |

`joe`'s and `vox`'s docstrings, comments and pages carried the history of
building a voice loop on one Windows workstation: what failed, what was
measured, which defect each test pins. Under
`records/DRAFT-durable-text-states-what-is-true.md` that text now states
facts, and its explanations moved to `joe`'s `docs/modules.md` and `vox`'s
`README.md`. This page keeps the stories. They were read at `joe` `a198858` and
`vox` `6db2694`; figures are as the passages gave them, and none was measured
again.

## A stand-in has to be able to fail

Before `vox.engine` existed, every `vox` test replaced the HTTP client with a
`MagicMock`, which proved a call was made and nothing about the wire. The
offline engine replaced the engine instead of the client, and a test was added
that the round trip really crossed the wire, because without it the suite
would have passed if `round_trip` handed the text to itself.

The engine was built to refuse what it could not have produced. Without a
marker in its codec, `decode_wav` would have read a recording of a human voice
as whatever its samples spelled, and answered with confident nonsense rather
than an error.

The contract went the same way. `vox` had one speech-to-text class named for
the engine it talked to, with that engine's routes spelled inline, and the
`EngineContract` defaults were taken from `joe` when it was the only engine.
Renaming the class and moving the paths into a dataclass changed nothing on its
own: a default that is the only value ever used is a hardcoding with a longer
spelling. So the tests run the whole loop against `ALIEN`, a contract sharing
nothing with the default.

The stand-in and the real engine disagreed once and nobody knew. The session's
default echo name was `out/echo.wav`, on the reasoning that an engine only
requires a name to resolve inside its own directories. `joe` refuses any name
containing a separator, because accepting one is how a path traversal gets in;
`vox`'s own engine was laxer, and the two had never run together, so the
default answered 404 on its first run against `joe`. The default became
`echo.wav`, and a test asserts a bare name.

## A workstation's audio is not a specification

One machine listed twenty inputs, and the same microphone appeared three or
four times, once per host API, under byte-identical names. Every device entry
now carries its host API.

Recording once forced 16 kHz mono. Every input on that machine was natively
44100 or 48000 Hz, and asking for 16000 failed on all four host APIs with four
different errors -- WASAPI said "Invalid sample rate", the others said less --
so nothing could record, the backend's own default included. Opening a device
on its own terms and converting afterwards was the only order that worked.

One WDM-KS input opened without error and returned values around -2e38:
uninitialised memory, not sound. The level meter read that as the loudest
device on the machine and recommended it, which was worse than the silence it
was written to find. The first guard, `peak > 1.5`, let a NaN run straight
through and printed `peak nan` as the loudest device; it became
`not (peak <= 1.5)`.

The level sweep recorded through a callback and the endpointed recorder through
`stream.read`, which WDM-KS does not implement, so `joe voice setup` chose a
device by its sweep and then could not record from it. The recorder moved to a
stream callback, and ranking became loudness for the microphone and host-API
preference for the entry, since WDM-KS reads loudest precisely because it
bypasses the system mixer. On another machine the default input was a capture
card, and a loop recording silence from it looked exactly like a loop that
misheard.

The voice going out had its own failures. pyttsx3's loop did not play on the
workstation: after `save_to_file`, `say` with `runAndWait` returned in 0.09 s
for a 2.8 s sentence, a conversation spoke every line into files while the
person heard nothing, and re-initialising the engine then hung. SAPI's own
`Speak` into a stream played each sentence for exactly its length, three in a
row, and the adapter has driven SAPI directly on Windows since. `save_to_file`
alone once left a live loop recording a person who had heard only silence,
which is why `speak` plays by default and returns only when the audio ends.

## A measurement needs its control

`HttpSTT` came to hold one `httpx.Client` for its life because constructing one
cost about 620 ms on the workstation -- about 240 ms of it building an SSL
context, paid whether or not the URL was `https`. The closed loop made three
such calls, so the module-level `httpx.post` spent about two seconds an
iteration doing nothing; a reused client answered in about 10 ms.

The formant synthesizer was measured against a live engine running whisper
`base` on 2026-09-27, and whisper did not read it. The control is what made
that a finding: real synthesis through the identical path came back as
"approve the deploy.", so the failure belonged to the synthesizer and not the
pipeline. The account of it had drifted -- `synth.py` said whisper returned
unrelated text and called the synthesis two-formant, while the README and the
test said whisper returned empty and the code drives three resonators per
vowel. The durable text now says only that whisper does not read it.

The barge-in echo level was first tracked rather than learned once. A voice
rises over several blocks into its first word, and a level that followed it
climbed ahead of it: on a virtual cable, an answer twice the question's
loudness never began. The level is now learned over the first blocks and held.
Elsewhere, truncating `max_duration / block_seconds` with `int` shortened every
wait by one block, because 0.3 / 0.1 is 2.999... in floating point.

## What an editable install hides

`packages = ["vox"]` shipped a wheel with no `vox/adapters/` in it, because an
explicit list is not recursive, and the editable install used in development
resolves against the source tree and hid it entirely. `joe`'s `Modules/` went
uninstalled the same way, long enough for a console script to fail in
somebody's hands. No test suite could have caught either, so a CI step builds
the wheel and reads its manifest. That check itself passed when it should not
have until a leftover `*.egg-info/` was found keeping the adapters in the wheel
after the declaration was removed; it now clears `build/` and `*.egg-info/`,
and the case was verified in a pristine copy of the tree.

## Line endings are content to git

`vox`'s mutation harness restored files with `write_text`, which writes the
platform's separator, so restoring an LF file on Windows put CRLF back and left
four files reported modified by a harness whose job was to leave no trace. The
content was identical, which is why a content check missed it; the harness has
compared bytes since. The closed-loop artifact had the same habit: `git status`
reported it modified after every local run until `newline="\n"` was pinned,
and a contributor read that as the drift the file exists to rule out.

## Small defects with large symptoms

- `vox loop` wrote `said.wav` only in its offline branch, so against a real
  engine it transcribed a file nothing had created and died on a 404.
- `vox doctor` caught `SystemExit` to let a refused voice name through, but
  `typer.Exit` is not a `SystemExit`, so the refusal was reported as a
  synthesis failure with the wrong exit code.
- `joe`'s two routes that take a file name disagreed: `/api/audio/{filename}`
  refused aliases such as `good.wav.` and `/api/voice/transcribe` accepted
  them, and a NUL byte raised a 500. Both now share `_is_bare_filename`; the
  defect was disagreement, so the fix was agreement.
- Under a MinTTY terminal, click's console writer raised `OSError` on the
  wrapped stderr, and the one message that mattered -- "nothing above
  silence" -- died inside its own printing.
- A hard-coded port 8000 cost an afternoon measuring another session's server;
  the offline engine binds an ephemeral port, and its server's poll interval was
  shortened after the default half-second, waited out on every teardown, turned
  out to be most of the suite's runtime.

## Continuous integration that was not running

`joe`'s Python suite ran nowhere until `tests.yml` existed: the application and
the only workflow that reached it lived on two branches that diverged on
2024-04-19 and were reconciled on 2026-09-27. When `e2e.yml` was first
dispatched on 2026-09-28 it was expected to fail, on the belief that the specs
needed a server nothing started; it came back green, because
`playwright.config.js` starts the dev server itself, and the trigger was widened
to match the Python suite's.
