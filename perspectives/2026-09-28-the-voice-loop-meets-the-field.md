# The voice loop meets the field — 2026-09-28

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-09-28 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

The voice loop was built from first principles, and then compared against
the open Python frameworks that solve the same problem. Every default quoted
below was read from that project's own source or README on this date; none
is remembered. What follows is why the baseline moved where it did, what it
declined to take, and the one defect the comparison did not find but the
first-time path did.

## What the field agreed on, and what was taken

**Turn-taking is a small state machine with hysteresis on both edges.**
SpeechRecognition waits for energy above a threshold, discards a phrase
shorter than `phrase_threshold` (0.3 s), and ends it after `pause_threshold`
(0.8 s) of quiet. Pipecat's analyser moves QUIET → STARTING → SPEAKING →
STOPPING, confirming onset only after `start_secs` (0.2 s). RealtimeSTT
requires `min_length_of_recording` (0.5 s). The loop's endpointer had the
trailing edge — its 0.8 s already matched SpeechRecognition — but no leading
one: a single loud block started the take, so a click or a cough before an
answer meant the person was cut off 0.8 s into their pause. It now needs
0.2 s of sustained speech, and a shorter burst is a transient.

**The noise floor moves.** SpeechRecognition tracks energy during non-speech
with an exponential average (damping 0.15 per second). The loop calibrated
once, on the loudest of its first blocks, so the person who answered the
instant a prompt ended — the most engaged responder — raised the bar above
their own voice and waited out the whole cap. The floor now starts from the
quietest calibration block and adapts with SpeechRecognition's time constant.

**A closed question is a grammar, and there are two kinds of failure.**
VoiceXML, the W3C's dialog standard, speaks a field's grammar in its prompt
and distinguishes *noinput* from *nomatch*. The loop re-asked every failure
the same way ("Sorry, I didn't catch that. Yes or no?"), never said which
words would work, and parsed only yes/no vocabulary — so a request whose
options were `["approve", "hold"]` could not be answered "hold" at all. That
request was one this session had itself put on the queue. The prompt now
says the options, an answer naming one is taken, and the re-ask says
whether nothing was heard or something unusable was, echoing the mishearing.

RealtimeSTT keeps a one-second pre-roll buffer so a late onset detection does
not clip the first syllable. The loop keeps every block from the stream's
start, so that hazard never existed here and nothing was added for it.

## A claim checked before it was made

faster-whisper gates transcription on voice activity, and the usual reason
given for that is whisper inventing text from silence. Before writing that
reason into anything, it was probed on this stack: joe's base whisper model
transcribed four seconds of digital silence and four seconds of room noise
to the empty string, both times. So the loop's new gate — skip the
transcriber when the endpointer heard no speech — is a latency and signal
change, letting a dialog say "I heard nothing" as a fact. It is not a guard
against invented text, which did not reproduce. A widely repeated reason is
still a claim about somebody else's inputs.

## What was declined, and why

- **A semantic end-of-turn model.** Pipecat's VAD stop is only 0.2 s because
  a separate model decides when a turn is truly over; LiveKit takes the same
  shape. That matters for open conversation, where a person pauses mid-thought.
  A yes/no approval is one short utterance, and energy endpointing is enough.
- **Barge-in.** Interrupting the speaker needs acoustic echo cancellation,
  which the frameworks get from a WebRTC transport. On one machine the
  microphone hears the speakers, so half-duplex with a clean hand-over is the
  correct behaviour for approvals, not a missing feature.
- **faster-whisper, for now.** It runs on CTranslate2 rather than PyTorch and
  claims up to four times whisper's speed at the same accuracy. That bears
  directly on an open decision — what joe's torch subtree is worth — and is
  recorded here as evidence for that decision, not taken as one.
- **Wyoming, for now.** Home Assistant's voice protocol — JSON-line headers
  with PCM payloads — has independent server implementations for speech
  recognition, synthesis and wake words. vox's engine contract is a bespoke
  HTTP surface with one real implementation. The seams doctrine asks a
  third-party component to be reached through an interface with several
  independent implementations, and Wyoming is that interface for this seam.
  An adapter for it is the next step for vox, not built here.

## The defect the comparison did not find

No framework survey would have found the failure that recurred most: `qmcp
human voice` reporting vox as not importable in a clone where vox was
installed. qmcp's editable install puts the project root on `sys.path`, and
the vox submodule sat at the root as a directory named `vox` with no
`__init__.py`. Python resolved `import vox` to that directory as an empty
namespace package, from any working directory, so the package's own names
were missing.

It hid for the reason this corpus keeps rediscovering. Every check run
against it imported a *submodule*, `vox.stt`, and submodules resolve under a
namespace package — so the checks passed while the command failed. They were
written after the belief that vox was installed, and could not have failed
against it. The fix moved the submodule to `vendor/vox`; the regression test
imports the real package with nothing faked, and was shown to go red with a
stray top-level `vox/` recreated before it was trusted green.

## A rule that differs by repository

qm's own contract now allows parallel pull requests when changes are
independent. qmcp pins an older seed that still enforces one open pull
request per contributor, and a second one opened there failed its slot
check until the first merged. A rule stated once in the corpus does not
reach an adopter until propagation carries it, and in the meantime the
adopter's gate is the rule that holds there.
