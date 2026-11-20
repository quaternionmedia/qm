# Local demo run — 2026-08-27

**The review list.** The trio demo grew a second act: one thread from the
harness, read three ways by three repositories under their own interpreters.
Everything below was true at the commits named and nowhere else.

| | |
|---|---|
| **Protocol** | `protocols/local-demo.md` |
| **Operator** | Peter Kagstrom |
| **Machine** | Windows 11, Python 3.13.3, no network reached |
| **Tools** | Claude Opus 5. See `ci/tool-registry.yaml` |
| **Published** | No. Nothing here left the machine, and every branch named below has exactly one copy |

---

## What it demonstrates

The first act is unchanged: `qmcp` emits a topology, `dossier` and
`codecartographer` draw it, and the windows agree about every box, every arrow,
and which edges nobody measured.

The second act is new and is about **the work that landed in parallel this
week**. The harness serves one thread and says what it settled; then:

| Reader | Reads | Reports | Held to |
|---|---|---|---|
| `qmcp` | the thread | what it settled, and which shapes a caller could run *now* given only a built harness (`orchestration.runnable_now`, from #34) | — |
| `looksatwords` | the turns | which topics they carried, which tangents never resolved, and the seam's own conversion counts | the harness's two turn counts; **no decision emitted** |
| `dossier` | the subject | which of its views could answer with that subject selected, and what the rest wait on (`readiness.survey`, from #55) | handed the same thread |
| `codecartographer` | the subject's clone | the system that repository declares, derived (`system_composer`, local branch) | present on disk, or stated absent |

**looksatwords is not a fourth window, and making it one would have been a
lie.** Its adoption record on `project/looksatwords` (§3) fixes what it does:
qmcp names the handful of decisions a thread settled; looksatwords reads the
*turns* underneath — the ninety-seven that were not decisions — and says what
they were about, authoring nothing in either of the others. So it is held to
the seam rather than to a picture: it must report the harness's own `turns`
and `turns with prose` counts, which its seam code says are two different
facts and which a truncation would silently move, and it must emit no `settled`,
`deltas` or `decisions` key.

| | |
|---|---|
| Demo | `ci/trio_demo.py` |
| Test | `ci/tests/test_trio_demo.py`, 35 tests (33 passed, 2 skipped: the trio was not up) |
| Command | `uv run qm demo` — both acts; `--skip-readers` stops after the first and says so |
| From a worktree | `QM_SIBLINGS=<dir>;<dir>` replaces where siblings are looked for; a worktree is beside nothing |

## The commits

| Repository | Branch | Commit | Signed |
|---|---|---|---|
| `qm` | `evolve/one-thread-three-readers` | this record's commit | G |
| `qmcp` | `main` | `42a2eae` (#34 merged) | merge |
| `dossier` | `feat/the-terminal-replays-the-governed-vectors` | `7f71897` | G |
| `looksatwords` | `feat/adopt-the-governance-corpus` (another session's, 14 ahead of origin) | `7d9089d` | G |
| `codecartographer` | `feat/the-monitor-derives-the-system` (worktree; the shared checkout is on another session's branch) | `23d4599` | G |
| `rad` | `evolve/consolidate-rad` (worktree) | `ae1066e` | G |

Nothing is pushed, per the standing instruction. `uv run qm branches` counts
every one of these in its at-risk column, which is the correct answer.

## The run, on the stated fixture

```
[1] qmcp serves one thread, and says what it settled
    thread       fixture/fixture-one-thread
    title        How the panel reads the thread archive
    data         fixture
    turns        8, of which 7 carry prose
    settled      1 delta(s): How the panel reads the thread archive
    runnable now pipeline, compound -- given only a built harness
                 delegation   short of workers
                 crosscheck   short of workers
                 ensemble     short of budget
                 debate       short of budget
                 chain        short of budget
                 council      short of person

[2] looksatwords reads the turns
    speakers     Assistant, Operator
    topics       Panel (6), Archive (5), Harness (4), Loopback (3), Schema (3), Port (2), Http (1), Setting (1)
    tangents     1, 0 unresolved
    turns        8 total, 7 with prose, 7 used

[3] dossier says which views could answer, with codecartographer selected
    ready        16 of 18 views (13 declare a need)
    waiting on   harness: Topology, Harness

[4] codecartographer derives codecartographer's system from its clone
    this checkout of codecartographer does not carry the derived system monitor
    (feat/the-monitor-derives-the-system) -- not read

THE SEAM
  2 reader(s) read the thread the harness served: looksatwords, dossier
  looksatwords reported the harness's own turn counts and emitted no decision:
  qmcp says what the thread settled; looksatwords says what the other turns were about.
```

**The fixture carries one empty turn on purpose.** `8 turns, 7 with prose` is
the seam's two counts differing, and the comparison is only worth making if they
can. `council short of person` is the one no argument lifts — a person decides,
and the demo does not have one.

With `QM_SIBLINGS` pointing at a root holding the codecartographer worktree and
`--subject moat`, the fourth reader runs:

```
[4] codecartographer derives moat's system from its clone
    derived      24 component(s), 6 edge(s), from moat at 16a595a
    roles        1 application, 21 chart, 1 deployer, 1 infrastructure
```

That is the homelab moat describes, not the moat repository: charts from
`Chart.yaml`, groot's six deploy edges from its ArgoCD `Application` manifests,
tofu from `*.tf`, tower from a `Dockerfile`.

## The run, on the real archive

Also run against the thread archive on this machine, which is **not reproduced
here and must not be published** — the demo prints thread titles and session
identifiers, which is right locally and wrong anywhere else. In aggregate: a
thread of 34 turns (33 with prose) that qmcp's reading said was about the
subject was served; looksatwords reported the same two counts, eight topics and
thirteen unresolved tangents; the seam held.

Two findings from that run, neither fixed here because neither is this
repository's:

- **The thread qmcp chose was a résumé.** `consolidate.about` said it was about
  `codecartographer` because the name appears often enough — which is the
  reading's rule working as written, on a document that lists projects. The
  demo shows the reading; it does not judge it, and says so.
- **looksatwords showed a speaker called `human`.** Its seam maps `user`,
  `assistant` and `system` to speaker names; claude-code threads use `human`,
  which fell through to the raw role. Cosmetic, and on another session's
  in-flight branch — noted for that session rather than edited under it.

## What building it found

**The previous run of this protocol is invisible to `uv run qm protocols`.**
`ci/protocols.py` keys a run on its filename -- `<date>-<protocol id>.md` --
and the 2026-08-21 record is named `trio-demo`, which is no protocol's id. So
the view reported the last local demo as 2026-08-17, eleven days stale, while a
run from six days ago sat beside it. This record is named for the protocol; the
older file is left where it is, and renaming it is a one-line change for
whoever next touches that directory.


**Three guards passed green through mutations that emptied them**, all in one
afternoon, all the same shape:

1. The border check (`looksatwords emits no decision`) was tested by asserting
   its *message* appeared in the source. Emptying the check and keeping the
   string passed. Now `_seam_problems(served, found)` is a function, and the
   test feeds it an over-count and an authored `settled` key.
2. The derive-target resolution was mutated back to the Python-project rule
   and the demo reported `not beside this clone` for a different reason —
   the run happened to use a checkout without the module, so the guard under
   test was never reached. Re-run against the checkout that carries it, the
   mutation showed `moat not beside this clone`, which is the defect.
3. The JSON's `agreed` field stayed `true` when the second act failed, with
   the disagreement sitting in `problems` beneath it. Found by mutation 1's
   first run, before any test asked.

And one more of the week's pattern: the interpreter test asserted **exactly
two** subprocess call sites and failed the day a third kind of process was
added — while saying nothing about whether the third used the right
interpreter. It now asserts that every `subprocess.run` resolves its own
project's interpreter, whatever the count.

## What this did not establish

- That the topics are right. looksatwords reports what its extractor found.
- Anything about the running services. Every reader ran on a pipe; dossier's
  readiness was measured against a harness address nobody answers on, so the
  two views that need one read as waiting, on purpose. `--over-http` does not
  yet cover the second act.
- Anything about `rad`'s cell layer or `dossier`'s delta drift — both landed
  this week and neither has a place in a demo about one thread. They have
  their own executable pages (`walkthrough/07-…` in dossier; `npm run gate`
  in rad).
