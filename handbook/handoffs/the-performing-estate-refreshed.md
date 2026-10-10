# Handoff — the performing estate, refreshed and mapped

**Transient.** Delete this page when its work lands.

## Stamp

Every figure on this page is true at these commits and nowhere else.
Re-derive before quoting — `uv run qm estate --by-family` is the reading, and
`gh pr list -R quaternionmedia/<repo>` is the pull-request reading.

| repository | ref | commit | date |
|---|---|---|---|
| qm | `origin/main` (#115 and #116 merged); this page's branch `evolve/performing-estate-refresh` is **local only** because #117 holds the slot | `23e4d35` | 2026-09-20 |
| qm | `origin/project/codecartographer` (#116 merged) | `d10bb28` | 2026-09-20 |
| codecartographer | `origin/main`; #100 open; its `governance/qm` pin `9161c3f` is behind the project branch above | `4e30271` | 2026-09-20 |
| ShowRunner | `origin/integrate/2026-09-20`, **#30** open; #12, #16, #22 closed unmerged as contained | `2b28210` | 2026-09-20 |
| leo | `origin/setlist`, **#61** open (a second contributor's pull request, advanced by a merge); #67 closed as contained | `8dce16c` | 2026-09-20 |
| joe | `origin/docs/onboarding-hardening`, **#8** open | `9e70fc9` | 2026-09-20 |
| Cuelist-python | `origin/fix/install-and-packaging`, **#1** open | `64cce43` | 2026-09-20 |
| qmetronome | `origin/governance/pin-project-tip`, **#15** open | `145f60c` | 2026-09-20 |
| ShowStopper | `origin/fix/textual-containers`, pushed, **no pull request** — see below | `66ab4f3` | 2026-09-20 |
| carlos | `origin/fix/dials-cable-ends-and-scroll`, #17 open | `3e8800f` | 2026-08-22 |
| dossier, looksatwords | `origin/main`; each also holds a pushed `feat/loose-ends` one commit ahead of `main`, no pull request, by decision | `bd322d3`, `32d3371` | 2026-09-20 |
| the rest of the performing estate | `origin/main` (or `master`), level, clean | — | 2026-09-20 |

## What exists now

**The performing estate is surveyed and mapped.** Every member of
`show-control`, `instruments` and `performer-display` was refreshed,
installed where it can be installed, tested where a suite exists, and read for
seams — each report verified by a second reading whose job was to refute it —
and the sixteen were joined into one document: a state table, a seam map by
protocol, the hubs, a design for local integration stubs sequenced
smallest-first, consolidation, risks, what could not be verified, and
eighteen questions for a person. No stub was written; the design is the
deliverable. The document is not committed anywhere yet (see below).

The findings a next session most needs:

- ShowRunner's only live wires out are OSC to its `osc-targets` and HTTP to
  itself; QLab sync, TheatreMix, ShowStopper and lighting are scaffolds or
  prose. Nothing at the display end (joe, leo) or the tempo end (qmetronome)
  listens on a network.
- QLab-python and cesar share one SLIP/OSC codec with the same framing
  defects; one hangs the receive thread on a `0xDB` byte.
- Cuelist-python, QLab-python and TheatreMix-python import ShowRunner by an
  editable path source; all three locks drift on every ShowRunner dependency
  change. Within one family, so not a protocol-rule violation; a portability
  hazard.
- No cross-family import exists. The two cross-family non-protocol crossings
  are an executable path (holophonor #11 → uPhonor) and shell provisioning
  (george → holophonor's JACK host).
- Suites exist in seven of the sixteen repositories; qmetronome's runs only in
  CI (no Android platform here); Cuelist-python could not install from its own
  lock until #1.

**A workspace opens one family or several, with the corpus first.** `uv run
qm workspace --family <name>`, repeatable, checked against `families.json`,
landed in #115; `--include qm` (this branch) puts the corpus beside the
members, so a session opened in the workspace finds `AGENTS.md`, `/cowork`
and this page first. The performing machine's workspace is
`uv run qm workspace --family show-control --family instruments --family
performer-display --include qm`, and it resolves all seventeen when each
repository is cloned at its `qm/<name>` candidate. Future work on the
performing estate is done from that workspace.

**ShowRunner has one base.** #30 carries `main` plus the three pull requests
it supersedes (#12 ⊂ #16, and #22), a `python_version < '3.13'` marker on the
`midi` extra (python-rtmidi ships no wheel for 3.13 on Windows), and two real
defects from `main` fixed (`Request` undefined in `app.py`, `logger` imported
twice). 174 tests and 7 browser tests pass on 8765.

**leo's two threads are one.** #61 now holds the filter drawer merged with
the setlist builder: the drawer's setlist filter reads the builder's setlists
beside the legacy store, every search row carries the builder's button, the
CLI is packaged again without the backend a prior merge had removed, and the
browser tests address the rows the app renders.

**joe's confirmed defects are fixed on #8**: a path traversal on two API
routes (bare-name and containment guard, thirty-three tests, the guard
hardened against trailing-dot and NUL aliases by the verifying pass), a
route-order bug that failed six browser tests, and a lock that any plain run
rewrote.

**Cuelist-python installs** (#1): lock, declared dependencies, no phantom
console script, the stray database untracked, uploads parsed in memory.

**qmetronome's governance pin** moves to the project branch tip on #15, the
one-line extraction from copilot's #14.

## What is unfinished

- **Merge the green pull requests, in order.** qm #117 first (it holds qm's
  slot and carries the pull-request-voice gate); codecartographer #100 (then
  reopen #99, or fold its one `.gitignore` line); ShowRunner #30 (then delete
  the three superseded branches, let the ten dependabot lock pull requests
  rebase, and rebase #15 — see question 1); leo #61 (then delete
  `uv-refactor`, close dependabot #59/#64/#66, rebase #63/#65); joe #8 (then
  close #4, delete `p5` and `librosa`, rebase #7); Cuelist-python #1;
  qmetronome #15 (then fold #13/#14 into one human pull request); carlos #17
  (red only on the org-wide REUSE gate; the merge message names the catalogue
  socket schema change). Done: each merged, each follow-up branch deleted,
  `uv run qm estate --by-family` reporting no one-copy branch in these
  repositories.
- **Bump codecartographer's governance pin** to `d10bb28` once #100 clears
  its slot. Done: a one-line pull request, `submodule-check` green.
- **File the estate synthesis** where the organisation keeps plans. Done: a
  `plans/` page in this corpus (or a decision that it stays a working
  document), on a pull request after #117.
- **ShowStopper `fix/textual-containers`** rests on a false premise — the
  locked Textual version exports `HorizontalGroup`, so the commit's rename
  claim is wrong; the change also adds a focusable stop per row and drops the
  dev group from the lock. Done: re-scoped to the colour change with the dev
  group re-locked, or closed, per question 2.
- **The first stubs**, once questions 1, 2, 4, 16 and 17 are answered:
  ShowRunner's recording OSC sink, the fake QLab in QLab-python with
  Cuelist-python's first tests, then a listener at each of ShowStopper, leo,
  joe and a clock master for qmetronome. Done: each on its own pull request
  with the port it binds reported, never a default port.
- **TheatreMix-python's `origin/showrunner`** (nine commits, never a pull
  request, tests green against #30): open it after replacing the path source
  per question 4, regenerating its lock, fixing the `showrunner_command`
  signature and adding the page its nav entry points at.

## Blocked on a person

The eighteen questions in the synthesis §7, of which these gate the next
round: cue numbering int or `str | None` (decides ShowRunner #15); which
ShowStopper is canonical (decides the branch above and two stubs); the
path-dependency policy for the three plugin repositories; whether the
performer-display hub is a ShowRunner plugin over WebSocket (needs CORS);
where the estate's tempo master lives; whether wolf, cesar and aes are
archived.

Also: the two `feat/loose-ends` commits in dossier and looksatwords (no pull
request by decision), and every merge above.

## Could not be verified (inference)

- qmetronome's unit suite did not run anywhere but CI; the pin bump touches
  no Kotlin (E2), and CI's verdict on #15 is the evidence.
- The browser suites of ShowRunner, leo and joe ran on non-default ports on
  one machine; their CI does not run them (E2, from the workflow files).
- The estate survey's seam grades were each checked by a second reading, but
  a seam neither reading looked for is invisible to both.
- Which of the two clones of codecartographer a roster reader resolves is a
  machine fact; the roster's first candidate wins.

## Standing constraints

- **Not local-only for delivered work**: every branch named above is pushed
  and every pull request is open. **This page's branch is local only** until
  #117 clears qm's slot; a session that finds it unpushed should open the
  pull request, not fold it.
- One open pull request per repository, per contributor; a superseded pull
  request is closed before anything is pushed onto its base.
- A pull request body speaks as its contributor and addresses nobody
  (`project-seed/ci/check_pr_voice.py`, arriving with #117).
- Every merge is a person's act in these repositories.
