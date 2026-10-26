# What whisper heard — 2026-10-25

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-25 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, re-deriving the figures from the benchmark's committed results |

On 2026-10-11 a benchmark measured how joe's transcription and qmcp's spoken
dialogs read synthesized speech. It lived on qmcp's `bench/voice-recognition`
branch (commit `7928d82`), which was never proposed and has since been
removed. This page keeps what the benchmark found. Every figure below was
re-derived on 2026-10-25 from the transcripts and confidence files in that
commit. The short answers were scored by qmcp's dialog code at `82b2d58`.

What was measured is narrow, and that is the first finding:

- **The speech** is synthesized by the two Windows SAPI voices installed on one
  machine, David and Zira.
- **The transcriber** is whisper's `base` model, running on the CPU.
- **Each clip is heard three ways:** clean; with Gaussian noise at 15 dB SNR;
  and clipped, with the first 60 ms after onset cut, like a take that starts a
  beat late.

The audio was not committed, so a re-run on another machine would measure
other voices.

## Short answers: a hint rescues the noisy and late takes

The clips are ten answers the loop's dialogs ask for: `record`, `again`,
`approve`, `hold`, `yes` (twice: once as consent, once as "more"), `no`,
`stop listening`, "Q M C P" and `vox`. Both voices speak each one at 160 and
230 words a minute, which gives 40 clips and 120 takes. Each take is scored
by what the dialog would do with it (`parse_yes_no`, `match_option` and
`choose_option`), not by whether every word matches.

| Whisper setting | Clean | Noise | Clipped | All | Seconds a take |
|---|---|---|---|---|---|
| Defaults | 40/40 | 37/40 | 22/40 | 99/120 | 1.05 |
| English, no carried-over text | 40/40 | 37/40 | 23/40 | 100/120 | 0.71 |
| … with the question's options as the initial prompt | 40/40 | 40/40 | 29/40 | 109/120 | 0.69 |
| … and beam search, width 5 | 40/40 | 40/40 | 34/40 | 114/120 | 1.15 |

- **Clean speech** is read right under every setting.
- **Noise** costs only `vox`, heard as "box" three times. The hint wins all
  three back.
- **Clipping** is where the settings differ.
  - Without a hint, clipped takes lose `hold` ("gold", "fold", "behold"),
    `approve` ("proof"), "Q M C P" ("UMCP") and `vox`.
  - With the hint, the 11 takes still missed are either heard as nothing at
    all (4 of them) or heard as words nobody said.
  - Beam search wins 5 more clipped takes, at a cost of 0.46 s more per take
    on the CPU.

qmcp's closed questions were already passing their options to the
transcriber as a hint when this ran (`4a9d673`, 2026-10-04). So this
benchmark measured a choice already made; it did not prompt that choice.

## Instruction-length sentences: project names

The second set is eight sentences an instruction might be, such as "Deploy
qmcp to the pi." and "Move the vectors from vox into qmcp.". Both voices
speak each one at two SAPI rates (−2 and +3), and each recording is heard the
three ways, which gives 96 takes. Each take is transcribed the way joe
transcribed one at the time: English, no carried-over text, and beam search
on takes of 3 s or less. Word error is measured against the sentence,
ignoring case and punctuation.

| | Clean | Noise | Clipped |
|---|---|---|---|
| Takes heard word for word | 22/32 | 15/32 | 14/32 |
| Mean word error | 0.065 | 0.095 | 0.137 |

A spoken instruction cannot do without its project names, and they fared
like this:

| Name | Heard as said | Heard instead |
|---|---|---|
| qmcp | 58/60 | "UMCP" twice, both on clipped takes |
| joe | 12/12 | |
| qm | 12/12 | |
| vox | 12/24 | "box": all 8 noisy takes, 2 clean, 2 clipped |
| pi | 0/12 | "pie", "pot", "pipe" |

Two sentences were never heard word for word, for different reasons:

- "Deploy qmcp to the pi." failed because "pi" never came back as written.
- "Summarise the open pull requests in qm." failed because whisper spells the
  first word "Summarize". The dialog would not mind that word error.

In short, noise costs `vox`, and whisper never writes `pi` at all.

## Whisper's confidence does not separate right from wrong

For each instruction take, the benchmark kept whisper's confidence: the
exponent of the segment's average log-probability. Every take came back as a
single segment, so the minimum and the mean are the same number on all 96.
51 of the 96 takes were word for word.

| Confidence at least | Takes | Word for word | Wrong | Worst word error |
|---|---|---|---|---|
| 0.60 | 62 | 36 | 26 | 0.57 |
| 0.65 | 38 | 30 | 8 | 0.20 |
| 0.70 | 21 | 17 | 4 | 0.14 |
| 0.75 | 1 | 1 | 0 | 0.00 |

No threshold lets a take skip its read-back without also letting wrong words
through. Above 0.70 there are still four wrong takes, among them "Move the
vectors from box into QMCP." at 0.708. Above 0.75, only one take of the 96
remains. qmcp reads every open answer back as a closed choice between `agree`
and `again`, and this table is the evidence that it has to.

## What was not kept

Three of the benchmark's scripts only printed their results and saved
nothing:

- `jargon_hint.py` hinted each project's terms on 48 takes of 12
  jargon-heavy sentences.
- `real_hint.py` and `real_gain.py` read joe's recorded takes.

What those runs showed survives only as a conclusion, in qmcp's
`qmcp/integrations/voice/vocabulary.toml`. On synthesized speech the terms
helped the jargon be heard, but on the first real takes they lowered
whisper's confidence and lost one take's words. So the terms reach the
transcriber only when `QMCP_VOICE_HINT_TERMS` is set.

## What it bears on

Phase 10 of qmcp's roadmap lists "Whether project names transcribe reliably"
as unmeasured.

- **On synthesized speech it is now measured.** `qmcp`, `joe` and `qm` are
  reliable. `vox` is not, once there is noise. And a target like "the pi" is
  never written as said.
- **On a person's voice it is still unmeasured.** The clips that would answer
  it are real takes, and this benchmark did not keep them.
