# Open work

**What this is.** Everything known to be outstanding across `qm`, `dossier` and
`qmcp`, in one place, so nobody re-derives it from three repositories and a
conversation.

**What it is not.** A backlog anybody has committed to. Several of these are
decisions nobody has taken, and a few will turn out not to need doing — which is
cheaper to find out than to build for.

**Stamped 2026-08-21.** Re-derive before acting; the commands are named.

---

## Blocked on a person, and only a person

These are in `ci/attested-registry.yaml` because automating them would change
what they assert, not because they are risky.
`records/DRAFT-acts-that-are-a-persons-by-constitution.md` is the reasoning.

| | |
|---|---|
| **Ratify a record** | Every record everywhere is `Proposed`. Waits on a second active code owner |
| **Apply the `main` ruleset** | One command, `uv run qm rulesets --apply`. An agent must never run it |
| **Cut a version tag** | Nothing is tagged. `main` asserts nothing, which is correct and is not a release |

## Verification that has not happened

Not gaps in the code — gaps in what anybody has *established*.

- **Divergence has never fired for a real reason.** Every thread in the archive
  agrees with its source, across all three of them; the index carries the count
  and this page does not. Correct today, and every divergence seen so far was a
  bug that was then fixed. **The next export of a source already ingested is the
  test**: threads kept talking in should report `grew`. If they report
  `diverged`, that is either a real finding or a defect, and telling those apart
  is the point.
- **Both export readings are now verified against real exports**, Claude's on
  2026-08-20 and ChatGPT's on 2026-08-21 — every conversation in each parsed,
  none lost, none empty. What remains unverified is the *tree*: ChatGPT's format
  is a graph flattened to a sequence, so a conversation with regenerated replies
  is read as alternatives in a row. No export seen so far has exercised that,
  which is not the same as its being right.
- **The tag-determinism gate has never run as a workflow.** It needs a pushed
  `v*` tag and none exists, so it has only been exercised by running its inner
  commands by hand.
- **The fresh-setup path was proven on one machine, one operating system.**

## Decisions nobody has taken

- **Retention.** Nothing prunes: the thread index grows one history entry per
  change per thread, forever. Correct now, wrong at scale, and *what may be
  forgotten* is a record rather than a default.
- **Recoverable or auditable.** The archive keeps digests, not prior bodies. A
  divergence says *that* something changed and not *what it said before*.
  Storing prior bodies makes it recoverable, at real disk cost.
- **Whether a delta may span owners.** `plans/qmpm-standardisations.md` §1.
  Claude Code sessions dodge it by naming their repository; web conversations
  still go to a project somebody chose.
- **Whether an unmarked conversation should be read at all.** Extraction finds
  what a thread *marked*. Sending a whole conversation to a model to find out
  what it settled is a different act, and the cheaper habit may be the better
  one.
- **The `database` field in the harness payload** carries an operator's absolute
  path, and the control panel stores it. Keep, hash, or reduce to a basename.

## Known-imperfect, and named as such

- **`uv run qm config` reports violations that predate this work.** Every status
  document sits at the repository root where `handbook/config-standard.md` puts
  them under `status/`. A sweep across many files; not a gate.
- **The `private-names` gate checks against an undated companion.** It reports
  how many names it checked and not when that list was generated, so a
  repository made private since would not be in it. Nothing is leaking today —
  checked with `git grep`. The repair is to print the companion's `generated_at`
  and refuse past its staleness budget.
- **`ChatGPTThreads` flattens a conversation tree.** Regenerated replies arrive
  as alternatives in sequence. Stated rather than hidden; `same-as` exists for
  the day somebody wants to say two branches were one strand.
- **Two `dossier.db` files exist on the machine this was written on**, and only
  one holds anything. Which survives is an operator's call. What is no longer
  left to notice by eye: `dossier.diagnostics`' `live-database` check fails when
  the database being read is empty while a populated one is visible, and refuses
  to report an empty result as an empty archive when it cannot see past the
  working directory.
- **Three `dossier` test modules reload `dossier.cli` and two never restore it.**
  `importlib.reload` re-executes into the same module object, so a module that
  did `from dossier.cli import ...` keeps the old binding while the module
  attribute moves — the two disagree from then on. They are green today. A test
  file added beside them was not, and the failures landed in unrelated modules
  that pass in isolation, which is the hardest shape of failure to read.
  `tests/core/test_sources.py`'s header says what to do instead.

## Not started

- **`qmcp` cannot be tagged.** Its suite skips tests needing optional
  dependencies, and `metaflow` cannot run on Windows at all — `import fcntl` is
  POSIX-only. `dossier` reached a no-skips state; that method does not transfer.
- **The pair still reconciles by file for deltas.** The thread archive crosses
  over HTTP now; `qmcp deltas` and `dossier deltas ingest` still pass a file a
  person copies.
- **`qmcp deltas` emits the wrong subject** — cookbook pipeline steps, which are
  a demonstration rather than this project's units of work.
- **Only one project emits deltas.** "Deltas across projects" needs a second
  emitter meeting `dossier deltas from-prs` on the address.
- **Most of the rad menu is in the menu and not applied.** `dossier`'s command
  sheet at `docs/rad-commands.md` marks which; it is generated from the palette
  and the app's dispatch, so the split is read off the code rather than
  maintained. `Go` is wired throughout and `6.2` now syncs; the phase and note
  actions under `Do`, every filter under `Show`, and all three of `Reach` report
  "not applied yet" when pressed. `Reach` is the interesting one — its three
  wedges are the pair's seam, and two of them duplicate CLI routes that already
  work.
- **`rad`'s conformance vectors do not cover the numpad cells**, and its
  `DRAFT-rad-host-integration-standard.md` exists on one disk and no remote —
  while `codecartographer`'s committed handoff defers to it.
- **`alfred` holds unpushed work** across several branches with a dirty tree,
  while its `origin/main` last moved in January 2024.
- **`qmetronome` carries a `v0.0.25` tag on no remote** — a release claim nobody
  can fetch.

## Repaid this session, listed so nobody re-finds them

The roster's activity axes; the harness payload's `unknown`; the payload
contract generated from a real emitter; the delta composition vocabulary; the
`ask` address kind and the human queue crossing as rows; the thread archive,
index and archive semantics; the Claude export importer, verified; the
subagent-collision false divergences; `DOSSIER_DATABASE_URL` reaching all three
resolvers; the overview's missing stylesheet; three dead sort handlers; the
overview sections that scrolled inside a page that already scrolled; and
`OverviewPanel.refresh_overview` building a coroutine and dropping it, so
choosing an owner moved the field and left the screen where it was.
