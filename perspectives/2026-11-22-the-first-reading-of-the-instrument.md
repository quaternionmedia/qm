# The first reading of the instrument — 2026-11-22

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-11-22 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Code (Claude Fable 5.1), driving the session under review |

The algorithmic layer's plan, `handbook/handoffs/the-algorithmic-layer.md`,
holds one row that is a measurement rather than a build: its (k) asks that
the built-in recipes run over real recordings with every draft kept, that
the instrument built for it be read, and that no default move before a
person's choices are in that reading. This is the first reading, taken at
the commits named below, in the session that also built the round's last
open row, the labeller. It found what it was expected to find, and one thing
it was not.

## What ran

The host run served alfred's `feat/speakers-to-words` at `af0941b6`, with
joe at `b2c0d00` as its audio engine and looksatwords as its language
engine. The library held two real recordings: the long one, an hour and a
quarter of several people talking, already transcribed and named by the
sound in the session before, and a short one of two and a half minutes,
which had a file in the library and no project. The short one was given a
project and transcribed through the audio engine for this, 32 segments and
350 words. Every built-in recipe then ran over it, and the three not yet run
over the long recording ran there, *excerpts*, *tight-cut* and *quotes*,
through `POST /project/{id}/drafts` with each recipe's first values. The
runs took seconds: the six over the short recording left 41 drafts in five
seconds, the three over the long one 112 in ten. The long recording's
earlier runs stayed where they were: *highlights* at several commits of the
round, *chapters* twice, and the titled *highlights* of a stored recipe.

## The reading

The instrument is `scripts/measured.py` on alfred's `feat/drafts-measured`
at `bb5a969d`, run from that branch's worktree against the host run's
database:

```
scripts/measured.py --db mongodb://127.0.0.1:27018 --name alfred
```

In all: made 317, held 317, dropped 0, edited 5, rendered 1. Per recipe,
the mean length as made and as held, in seconds:

| Recipe | Long recording | Short recording |
|---|---|---|
| `chapters` | 102 drafts, 80 s | 5 drafts, 23 s |
| `excerpts` | 86 drafts, 19 s | 7 drafts, 14 s |
| `highlights` | 35 drafts, 9.8 s, one rendered | 9 drafts, 9.9 s |
| `quotes` | 25 drafts, 4.1 s | 18 drafts, 4.9 s |
| `teaser` | 1 draft, 59 s made, 56 s held | 1 draft, 57 s |
| `tight-cut` | 1 draft, 4446 s made, 3367 s held | 1 draft, 146 s made, 113 s held |

A stored copy of *highlights* with titles left 12 more over the long
recording, and a stored copy with categories left 9 over the short one; a
synthetic demo project of ten seconds holds five drafts of its own.

## What the reading means

`dropped 0` is not a verdict on the recipes. Nobody has opened these drafts
and chosen; the session kept every one, as the row asks, and the instrument
reads choices, so it read none. The signal the row names, the kept against
the dropped and the rendered timeline against the kept, does not exist yet,
and so no default moves: not the window's length range, not the count for a
recording's length, not the two baselines, not whether a spike counts only
where words are said. What the reading does give is the recipes' own shape
on real speech, which nothing synthetic had shown. *highlights* lands in the
middle of its eight-to-twelve-second window on both recordings. *quotes*
stays under five seconds. *chapters* at its default pause of four seconds
cuts an hour and a quarter into a hundred stretches averaging eighty
seconds, which a person will likely find too fine; that is a guess until
they say so, and saying so is what the row is for.

## What was not expected

`edited 5`. The instrument reads a held draft as edited when its timeline is
longer or shorter than the spans it took by more than a frame. Both
*tight-cut* drafts read as edited, and nobody edited them: the recipe's own
`tighten` and `fillers` steps shorten the timeline inside its spans, and its
spans are the whole source, so the recipe's work reads as a person's. The
two tight cuts of the demo project read the same way. The long recording's
*teaser* reads edited by two and a half seconds, which no hand in this
session did, and the instrument cannot say whether that is the composition's
own arithmetic or a stray edit from an earlier session. So `edited`
conflates what a recipe cut with what a person cut. The correction is for a
draft to carry the length it had when it was made, and for the instrument to
compare the held length against that rather than against the spans; it is a
small change on `feat/drafts-measured` and the handoff carries it as open.
This is the shape AGENTS.md's item 12 names: the instrument is fine and its
first reading described its own definition before it described the recipes,
and the count was believed for a moment because it arrived with the others.

## The labeller's first run, beside it

The round's other open row closed the same day: alfred `0fc7b9aa`,
`feat/labeller`, above `feat/topic-titles`, puts a labeller behind an
OpenAI-style chat route, `ALFRED_LABELLER_URL` and `ALFRED_LABELLER_MODEL`,
with alfred naming no model, and a `label` step with categories or `score`
asks it a kept candidate at a time. Its first run was over the short
recording's nine highlights, with the local model server qmcp's `localmodel`
stands up as the labeller: the drafts were sorted and scored in ten seconds,
five as explanation, three as story, one as planning, and the scores for
standing alone ran from 0.2 to 0.8, eight of the nine at 0.2 or 0.3. A cold
model answered the first question in 76 seconds and a warm one in about a
second, which is why the default timeout is two minutes. The low scores are
a reading of the prompt as written against conversational speech by this
model; whether that is the model, the prompt or the clips is for a person to
judge with the clips in front of them, and the score sits under `label`,
after the `top` filter, so it moves nothing until a recipe reads it. From a
fresh browser the Drafts panel showed each sorted draft's category beside
its recipe and its scores.

## Where it stands

The measuring part of the round is in place end to end: recipes over real
recordings, every draft kept, the instrument reading them, the labeller's
category and score on the drafts it was asked about. What is missing is the
one input nothing in a session may supply, a person's choices over the
drafts, and until they exist the first values stay what the plan calls
them: a collaborator's advice, held until measured.
