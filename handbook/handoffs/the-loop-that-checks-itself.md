# Handoff — the loop that checks itself

**Stamped 2026-08-21.** `qm` on `evolve/active-repos` at `a3dbc99`, `qmcp` on
`fix/a-count-nobody-took` at `f723aaf`, `dossier` on
`fix/refuse-a-count-nobody-took` at `4080b88`. Every figure was true at those
commits. Re-derive before quoting one.

**Nothing is pushed.** All three branches are local, per a standing instruction
at the top of the session. `qm` is 22 commits ahead of `origin/main`, `qmcp` 22,
`dossier` 19.

**What this page is.** What exists now, what it cannot do, and the four things a
next session would trip over. It is not a plan; `plans/open-work.md` is the
list, and `perspectives/2026-08-21-*.md` are the two retrospectives behind it.

---

## What is new since the last handoff

**A menu that can be documented.** Every rad command is numbered by the keys
that reach it — `6.2` is sync, `4.6` is ingest, `6.4` is the sweep — and
`dossier/docs/rad-commands.md` is generated from the palette and the app's own
dispatch. Unavailable commands are greyed and refuse every route to them (digit,
arrow, chord, rotate, and the highlight you were left on), because dropping one
would renumber every command after it.

**Inward diagnostics.** `dossier/src/dossier/diagnostics.py`: eight checks, each
written from a defect that happened this week and each invisible to a passing
suite at the time. All eight clean at the stamped commit. Seven mutations were
run and each fired, two of them across the seam.

**A feedback loop.** `qmcp/qmcp/feedback.py` runs the gates and the diagnostics
as one pipeline. Its interesting output is `unratcheted` — failures no check
covers, which is the queue that makes the next run stronger. Empty today.

**An orchestration plane.** `qmcp/qmcp/orchestration.py` declares, per topology,
whether running it spends, writes or decides. Two shapes run (`delegation`,
`crosscheck`), five are named as brainstorms rather than left looking like debt,
and `council` is refused here because its arbiter makes final decisions by
construction.

**A deterministic audit.** `qmcp/qmcp/audit.py` answers "what ran" and "what is
in flight" from records, over a UTC window the caller names. Nothing reads a
clock; nothing is inferred from a tool name.

**A sweep.** One change across every repository that declares a dependency, as
one delta with `part-of` parts, dispatched by work shape and batched for one
human approval per distinct edit.

**A local model.** `qwen2.5-coder:7b` on the GPU, weights on `E:`, and
`qmcp/qmcp/localmodel.py` prints the exact commands to rebuild it on a fresh
machine.

---

## The four things that will trip you

### 1. `harness-status.json` expires today

At the stamped commit it was **22.5 hours old against its own 24-hour budget**.
It has almost certainly gone stale by the time you read this.

Its `reading:` block carries the refresh command. **Fetch first.** That document
reads other repositories, and one generated from unfetched refs is a recorded
past defect in this corpus — it looks current and describes a state nobody is
in. `governance-status.yaml` is fine: ~23 hours against a 168-hour budget.

### 2. Two questions the records cannot answer

- **Which models ran.** 55 of 55 invocations recorded none. `qmcp.audit.record_model`
  exists and **nothing calls it yet**. Until something does, the audit correctly
  answers `unknown` for every row.
- **Which harness a delta is moving through.** 51 of 59 in flight have none
  recorded.

Both are one line at each call site. Neither is a bug in the query.

### 3. The topology registry replaces silently

`TopologyRegistry.register` is keyed by `TopologyType` and overwrites without
complaint. Two classes claiming one type do not collide — one wins by import
order. This cost a false `RUNS` declaration that a four-line check
(`orchestration.stubs()`) caught. If you implement another topology, do not
claim a type another class already holds until that is fixed.

### 4. Three `importlib.reload` tests remain

`test_database_override.py`, `test_harness.py`, `test_ingest.py`. Green, and the
hazard that once cost 63 unrelated failures. The real remedy is making
`dossier.cli`'s engine lazy, which is a refactor to take deliberately. The leak
diagnostic is calibrated to *unrestored* mutation, and this is written down here
so the calibration is a decision rather than a gap.

---

## How to see it work

The harness must be running for anything crossing the seam:
`uv run python -m qmcp serve` (port **3333** — both sides agree on that now, and
a diagnostic fails if they stop).

    uv run --no-sync python -c "from dossier.diagnostics import run; print(run().render())"
    uv run python -c "from qmcp.orchestration import render; print(render())"
    uv run dossier dashboard        # then m 6 4, or m 4 6, or m 6 2

Both walkthrough sets execute under the ordinary test command — six pages in
`dossier/walkthrough`, five in `qmcp/walkthrough`. The sweep and the composition
demos are pages 05 and 06.

---

## What was verified, and how

**Suites at the stamped commits.** dossier 828, qmcp 680.

**Three blind runs**, randomised order, harness up, seeds `856262548`,
`2165698300`, `3992251899` — 828 passed each. The first randomised run this week
found a state leak that a fixed order had hidden through five full passes;
`pytest-randomly` is now a dev dependency for that reason.

**The ChatGPT reading is verified.** Flagged unverified for weeks; checked on
2026-08-21 against a real export — 34 of 34 parsed, none with messages parsing
to zero turns, 354 turns at 116/238 human/assistant. Archive now 237 threads.

**The bridge agrees.** Harness and panel independently count `threads: 237,
diverged: 0` over `/v1/threads`. Scope any comparison to what the route claims
to carry: comparing an invocation count against a threads route reports a
disagreement that is a category error, which the first run did.

---

## What this pair still cannot do

- **Apply a sweep.** Batches carry prepared edits and an approval note naming
  every repository reached. Nothing writes to a working tree. That is the
  constitutional human gate and the standing local-only instruction, together.
- **Answer a judgement share.** The model is installed and no worker is
  registered for `judgement`, so 15 of 24 shares queue for a person. Registering
  one changes what runs and not the dispatcher.
- **Ratify anything.** Every record everywhere is `Proposed`, waiting on a
  second active code owner.

## Suggestions

Seven of them, ordered by what they would have saved, are in
`perspectives/2026-08-21-what-a-system-says-about-itself.md`. The one with no
guard anywhere is the first: **a docstring naming a symbol that does not exist**
was a real defect twice in one day, and nothing checks for it.
