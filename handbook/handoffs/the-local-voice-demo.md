# Handoff — the voice loop's demo, run on one workstation

**Stamped 2026-10-11.** The demo branch `demo/voice-loop-2026-10-04` at `qm`
`80d206c`, `qmcp` `40f5de3`, `joe` `f3faa67` and `vox` `8f76671`, each the
pushed head on origin; the integration worktree's corpus pin at `012c903`.
Every figure here was true at those commits and nowhere else. Act 0 of the
runner re-derives the heads; re-derive anything else before acting on it.

[`the-voice-loop.md`](the-voice-loop.md) is the loop and its open set, and
[`hil-review-2026-10-04.md`](hil-review-2026-10-04.md) is the review of that
set and the order it lands in. This page is what they leave out: the demo
brought up on one workstation from the pushed demo branches, what each part
shows when it runs, and what it showed at the stamp. Nothing in it is a
decision.

---

## 0. What the demo is

Each of `qm`, `qmcp`, `joe` and `vox` has `demo/voice-loop-2026-10-04`: its
`main` with every open pull request of the set merged in, for running the set
together and never for merging. At the stamp each head carries every open pull
request of the set. What a head leaves out is listed by act 0 of the runner,
and was: dependency bumps in `qmcp` and `joe`, `joe` #4, and `qm`'s records
pull requests into project branches (#121, #144 to #156), none of which belong
to the set.

`qm`'s demo branch carries one file no pull request does:
`demo/voice_loop.py`, the runner in §2.

## 1. The workspace

Four checkouts at the demo heads, and one integration worktree.

| Repository | Where the demo branch is checked out | Made with |
|---|---|---|
| `qm` | a worktree beside the clone, `qm.worktrees/demo` by convention | `git -C qm worktree add ../qm.worktrees/demo demo/voice-loop-2026-10-04` |
| `qmcp` | any worktree of the clone, the primary one included | `git -C qmcp switch demo/voice-loop-2026-10-04` |
| `joe` | any worktree of the clone, the primary one included | `git -C joe switch demo/voice-loop-2026-10-04` |
| `vox` | any worktree of the clone, `vox.worktrees/demo` by convention | `git -C vox worktree add ../vox.worktrees/demo demo/voice-loop-2026-10-04` |
| integration | `qmcp.worktrees/integration`, beside `qmcp`'s clone | the runner, on its first run |

The runner finds the clones beside `qm`'s primary clone or one level up, as
`uv run qm demo` does; `QM_SIBLINGS`, a list of directories, replaces that.
It finds each demo checkout from its clone's worktree list, and names the
command when one is missing.

**The integration worktree is where the tiers run.** It is `qmcp`'s demo head
with `vendor/vox` at `vox`'s demo head and `governance/qm` at `qm`'s
`project/qmcp` with `qm`'s demo head merged in: the pins a bump leaves once the
set lands. The runner rebuilds it whenever any head moves, and runs
`uv sync --all-extras` there.

## 2. The runner

From `qm`'s demo checkout:

```
uv run python demo/voice_loop.py
```

It runs nothing that speaks, listens, spends or pushes. Its server binds
loopback on a free port over a database made for the run.

| Act | What it runs | At the stamp |
|---|---|---|
| 0 | each head against origin's demo head, clean; which open pull requests it carries; the integration worktree rebuilt if a head moved | all four equal and clean; the integration worktree rebuilt, corpus pin `012c903` |
| 1 | `qmcp/topology_designs.py`'s module docstring before (`origin/feat/topology-voice`) and after (the demo), scored by the durable-text gate | 66 lines and 10 findings, then 20 lines and none |
| 2 | a `qmcp` server from the integration worktree, asked to save designs the docstring describes | a council saved with its run refused; an advisory council saved; *ratify a record* refused as a person's act; a design naming a missing component refused with 422 |
| 3 | `uv run qmcp cookbook converse`: one whole spoken session, offline, on `vox`'s deterministic engine | exit 0 |
| 4 | `uv run qm demo --fixture`: one topology drawn by `dossier` and `codecartographer`, and the estate read by both | both agree on every box and arrow, and on every family placement |
| 5 | the durable-text gate over every tracked line of each demo head | `qm`, `joe`, `vox`: none; `qmcp`: 10, in its copies of three seed workflows and `qmcp/cli.py` |

Act 5's `qmcp` findings clear when `qmcp`'s governance pin moves past `qm`
#140 and the three workflows are copied again (`the-voice-loop.md` §1). Act 1
reports itself skipped once `feat/topology-voice` is gone from origin.

## 3. The three tiers

`qmcp`'s `docs/voice-loop-demo.md`, on its demo branch, is the onboarding:
what runs where, setup with a done-signal for each step, and its cookbook. The
tiers below run from the integration worktree.

- **Tier 1, nothing real.** `uv run qmcp cookbook voice`, `cookbook
  instruct`, `cookbook instruct --runtime scripted` and `cookbook converse`.
  At the stamp: five of five voice dialogs and two of two instruction loops
  ended as scripted, the scripted runtime carried the first instruction's
  finding into the second, and `converse` is act 3.
- **Tier 2, the local model.** `uv run qmcp localmodel check` reported the
  model served. `uv run qmcp cookbook instruct --runtime local` ran twice. The
  first failed: its second instruction reached the model's call limit of 8
  without an answer, and the run says so rather than reporting what was read.
  The second passed, and its second answer restated the first finding instead
  of saying what the file says `qmcp` is for. The check asserts that the second
  run is handed what the first found; what the model answers is read by a
  person (`the-voice-loop.md` §4).
- **Tier 3, a person at the microphone.** `uv run joe dev` in `joe`'s demo
  checkout and `uv run qmcp serve --converse --runtime local` in the
  integration worktree, then speech. Not run at the stamp. *Done* is the
  same as in `the-voice-loop.md` §1: run once with a person, and recorded.

## 4. Keeping the demo current

- **A pull request in the set gains a commit.** Merge its new head into that
  repository's demo branch and push the branch. In `qm`, a merge that
  conflicts only in generated documents is resolved by `uv run qm docs
  generate` for the conflicted files alone: the generator also re-surveys
  documents that read live state, and those keep their merged version. Then
  run the runner, whose act 0 rebuilds the integration worktree.
- **A pull request in the set merges.** Nothing changes for the demo, which
  already carries it.
- **The set has landed.** The demo branches, the integration worktree and this
  page go together.

## 5. What the demo cannot show

- **A person speaking.** Every take in tiers 1 and 2 is scripted.
- **Whether the local model's answers are right.** Tier 2 above is one
  measurement of two runs.
- **Open pull requests, without the forge.** Act 0 reads them with `gh` and
  says *unread* when it cannot.
- **The model service's state.** On the workstation the set was built on, the
  service was seen to stall partway through a reply; every call is capped, so a
  stall is a failed run naming the endpoint, and unloading the model frees it
  (`the-voice-loop.md` §4).

## 6. Standing constraints

- **Nothing here speaks or listens until a person starts tier 3.** The runner
  and tiers 1 and 2 do neither.
- **The demo branches are never merged**, and a commit made on one reaches
  nothing else.
- **`qmcp`'s suite deletes `./qmcp.db`.** The runner makes its own database;
  the suite needs `QMCP_DATABASE_URL` set to another path first
  (`the-voice-loop.md` §2).
- **Port 8000 is the first to move** when two loops run at once; `JOE_PORT`
  moves it.
