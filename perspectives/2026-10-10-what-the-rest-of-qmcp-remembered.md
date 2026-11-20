# What the rest of qmcp remembered — 2026-10-10

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-10 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5 |

`perspectives/2026-10-10-what-the-topology-docstrings-remembered.md` kept the
stories from `qmcp`'s topology modules. This page keeps the rest: the thread
archive, the harness's views of itself, the database, the client and server,
the local-model runtime and the voice loop. Under
`records/DRAFT-durable-text-states-what-is-true.md` their docstrings now state
facts, and the explanations moved to `qmcp`'s `docs/threads.md`,
`docs/self-checks.md` and `docs/integrations/voice.md`. Every story below was
read at `qmcp` `955a1f3`; figures are as the passages gave them.

## Reading real conversations

The Claude and ChatGPT readers were written from the documented formats with
no export to hand, then checked against real ones: on 2026-08-20, 94 Claude
conversations, every one detected and none with messages parsed to zero turns;
on 2026-08-21, 34 ChatGPT conversations, all parsed, 354 turns split 116 to the
person and 238 to the assistant -- the ratio a real archive has and a broken
reading does not. Each was one export from one account on one date. The
ChatGPT format stores a tree, and flattening it was chosen over picking a path,
because a chosen path looks correct and a flattened one looks like what it is.

The first `survey` counted files rather than reading them, so forty files with
three malformed would have surveyed as forty and fetched as thirty-seven, and a
board would have been quietly short. Reading every file was affordable because
nothing in the module spends. The first `classify` checked only that the old
turn ids were a prefix of the new ones, so an edited conversation reported as
having grown by zero turns: a divergence filed as the ordinary case.

Keying a Claude Code thread on `sessionId` alone collapsed subagent sidechains
-- forty-six files shared one id on the machine where it was found -- and the
index read each overwrite as the thread diverging: seven divergences on a
first index of a real machine, none real. A false divergence is worse than a
missed one, because a reader who finds the first seven are noise stops looking
at the eighth. A sidechain became its own thread, `part-of` its session.

Consolidation began when the archive held about two hundred threads and almost
every one was about some project while nothing said so. Measured on the real
archive, 33 threads crossed more than one project and the largest named 11 of
13: a status sweep, a roster review or a handoff that enumerated every
repository came out looking like a conversation about all of them, and became
its own kind. Pointed at `codecartographer`, "named in at least two turns"
admitted a 5,153-turn session naming it in 0.3% of turns beside a 63-turn
session naming it in 12.7%; fourteen threads "about" it were four, and a share
threshold was added, off by default.

## Unknown is a value

The dashboard's first payload schema emitted `0` for a count it could not
take, which made a database missing its tables indistinguishable from a
harness that had run nothing, and its consumer stored the zero as fact. The
terminal renderer's docstring claimed the table counts told them apart; they
did not. The test was named `..._count_as_zero_rather_than_raising`: not
raising was right and never the question, and returning zero was the error. The
fix took the corpus's convention: unknown is a value, says why, and is not zero.

One constant once sized both the invocation window and the queue of work. A
queue of fifteen arrived as ten, the five dropped were the most recently asked,
and nothing said so -- found by queueing two governed runs against a live
harness and finding neither in the payload.

When the audit was written, measured on the real database, 55 of 55
invocations recorded no model, and 51 of 59 deltas in flight had no harness
recorded; a report showing only the eight would have described a tenth of the
work. Those were the honest state of the record, not defects in the query, and
the remedy for the first was deliberately small: the model written into the
parameters every invocation already stores.

## One owner, decided once

Four modules -- later counted as seven -- typed `quaternionmedia/qmcp` into
their own constants, and consolidation wrote the roster's owner in as a
literal, so a fork of the harness emitted addresses and relations claiming to
belong to this organisation. `qmcp.addresses` had the vocabulary and nothing
decided the owner, so every caller decided for itself. `qmcp.identity` became
the one place, reading the git remote rather than a setting, because a setting
can disagree with reality and nothing notices. Its test guards against "the
fifth one".

## A port and an address that moved

`MCPClient()` defaulted to `http://localhost:3333` while the server answered on
3141, so the client the package shipped could not reach the server it started:
established by running both, `health()` raised `ConnectError` on the default
and answered with the port given. 3333 was what the harness served while a
control panel looked on 8000 -- a mismatch that once had the panel reporting an
absent archive while the harness served 203 threads. The server moved and four
call sites, found by grep, did not; the literal had been in five places. The
ports were then chosen from constants -- pi, phi and e -- with `1337` already
taken on the workstation and 8000 the common default.

The address module said the shared conformance vectors were unreachable
because the corpus pin predated them; by the time of the sweep the pin carried
them and the test ran them.

## The database

A migration autogenerated without a naming convention emitted
`create_foreign_key(None, ...)`, which raised after earlier statements had
committed and left a half-migrated database at an unchanged revision; the
recovery was a restore from backup, and `env.py` gained the naming convention.
The first version of the check for it scanned whole files and matched the
comment in the migration that explains the rule. Another autogenerated
migration added enum columns NOT NULL with no default, which succeeded only
because the database happened to be empty.

A server started against a database whose schema had moved on returned 500 on
every read of one endpoint, the reason visible only in a log traceback; that
cost a day, and `drift` now asks the question before the first request does. A
drift check reading all of `SQLModel.metadata` reported five tables missing
that were never meant to be there, once anything had imported the cookbook.
The database path was once read from the URL as a path, creating an empty
database beside the real one.

## Claims nobody had checked

Six of ten `uv run qmcp ...` commands named in docstrings did not resolve. The
modules imported, their functions worked and their tests passed, so nothing
was red. The first run of the check found a seventh nobody had looked for, and
an early version reported a document wrong on the strength of a test path read
as a subcommand -- the check answering a different question.

`FeedbackTopology` first registered itself as the pipeline. `register`
replaces silently, so `TopologyRegistry.get(PIPELINE)` returned the stub or
the feedback pipeline depending on what had been imported; a test asking
whether the registered pipeline overrides `run` found it.

Before `tests.yml`, five checks reported on every pull request and none
executed a test, so a green pull request meant the governance checks passed
while a reader took it to mean the code worked. `tag-determinism.yml` failed on
its first run because the suite skipped tests needing optional dependencies,
which meant the repository could not cut a tag -- already true, and visible
nowhere. The corpus had twice read a failing check as passing because a pipe
replaced the exit code.

The first walkthrough's list of payload keys was a sorted copy of the keys
written into the page, so it passed whatever the emitter returned. The
dashboard tests built their databases from hand-written DDL that agreed with
the models only by coincidence, and the two sides of the payload seam each had
a fixture that agreed with the other and with nothing else, until shared
vectors replaced both. A self-check test asserted that "unit of work" was
absent, and the all-green message contained the phrase.

## What Windows hid

`qmcp.client` exported only `MCPClient`, so `examples/flows/approved_deploy.py`
could not import `HumanRequestExpiredError` -- broken everywhere and invisible
on Windows, where `import metaflow` fails on `fcntl` and the flow cannot be
imported at all. The first CI run on Linux found it in sixteen seconds. An
unpinned `uv pip install` once dragged `starlette` forward and broke 52 tests.
`uv run qmcp serve` once printed a note sending the person to `python qmcp
serve`, typed wrongly, which is how a standard-library shadowing problem was
found.

## The local model and the voice loop

Asked with the service's own tool definitions, the pinned local model put its
tool call in the reply's text rather than the structured field, or skipped the
tools and answered from nothing; the tools became a protocol stated in the
prompt. Seen live, it alternated between rereading one file and searching for
a phrase it had invented until the step bound ended the run, so a repeated read
is now answered with a request to answer. On the workstation, the service's
runner stopped producing tokens partway through a reply, with every later call
queued behind it until the model was unloaded; the unload-and-retry-once
recovery came from that.

The first install plan set `OLLAMA_MODELS` and pulled without restarting the
service, which had read its environment at start, so 4.4 GB went to a system
drive with 460 MB free while another drive had 302 GB; the restart step was
added, beside a comment that had warned about it. `ollama run`, which reads
stdin, hung for ten minutes with no terminal, and the plan's last step became
an API call.

The approval loop once re-asked an unanswered request at once, repeating the
question to an empty room every few seconds. The tacit-agreement threshold was
set from synthesized instructions, where whisper's base model scored 0.5 to
0.75 and the wrong takes above 0.7 were near misses ("box" for "vox"). On a
real take, the transcriber spelled the project "camcp" without the project
names as a hint and "qmcp" with them. `vox` and `pyttsx3` were once an extra,
and a plain `uv sync` stripped them mid-session. Said aloud, the consent's clone
path ran to half a minute, and "1 run(s)" was read with its parenthesis.

## Docstrings that had outlived their code

The sweep found sentences that were simply no longer true: the thread sources
described as stubs while they read local exports and the session store; the
address vectors described as unreachable while the test ran them; the feedback
pipeline's gates stage described as running the self-check while it runs the
suite; and a module docstring carrying a stray `from qmcp import identity`
inside its last sentence. Each is the cost the record names: a story beside the
code stops being true, and nothing tests it.
