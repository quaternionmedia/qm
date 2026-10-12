# Handoff — the performing family, consolidated and on origin

**Goal.** Land the core performing family's work (ShowRunner, ShowStopper,
carlos, joe, leo) as stacked pull requests, keep the family demo consistent
while it lands, and phase the rest of the family in after it.

**Stamp.** 2026-10-12. The commits in the state table are where each branch
stood on origin. Every count on this page is true at those commits only, so
re-derive it before you quote it. Facts carried over from a sub-agent are
marked *(reported)*; per `handbook/async-contract.md` §9 they are evidence, not
findings.

## Standing constraints

- **Peter merges** (D14). Every branch below is pushed; nothing is merged by a
  session.
- **Forge speech is Peter's** (D3). A comment or reply is drafted, Peter
  approves the text, and it carries a `Tools:` note. A pull request body
  carries one too.
- **Private names.** The private instrument is `private-34` in committed text.
  This machine maps the reference to its clone in the gitignored
  `ci/workspace-private.yaml`. Run
  `uv run qm private-names --source host --strict` before any push.
- **Commits are signed.** The corpus's signature gate refuses an unsigned
  commit made after 2026-08-15. Check `git log --format=%G?` on what you are
  about to push.
- **`VIRTUAL_ENV` points at the corpus clone's `.venv`** in this machine's
  shells; uv ignores it with a warning. Run qm's gates from a worktree with its
  own environment.

## Decided

| # | Decision | By |
|---|---|---|
| D1 | A single app's checks live in the app. Checks that coordinate apps (members up together, isolation, seams) live in qm. | Peter, 2026-10-10 |
| D2 | The demo runs each member's branch or pull request with active work. Where that is ambiguous, the app gets a stub CLI to conform to. | Peter, 2026-10-10 |
| D3 | Text posted to a forge under a person's account is drafted, approved by that person, and carries a `Tools:` note. See `perspectives/2026-10-09-a-comment-in-someone-elses-voice.md`. | Peter, 2026-10-09 |
| D4 | ShowRunner #30's split is mrharpo's. Peter opens nothing in ShowRunner beyond what mrharpo asks for. | Peter, 2026-10-10 |
| D5 | joe #24 and #25 are closed. #25 is retargeted to `main`, so it can reopen once qmcp's `--converse` lands. | Peter, 2026-10-10; done |
| D6 | ShowStopper `fix/textual-containers` is dropped. | Peter, 2026-10-10 |
| D7 | leo, after #61: the security lock fix first, then the walkthrough with its browser CI job. | Peter, 2026-10-10 |
| D8 | `private-34`'s pre-squash branch is kept on origin as `archive/pre-squash-2026-08-09-session`. | Peter, 2026-10-10; done |
| D9 | qmetronome #14 is closed. | Peter, 2026-10-10; done |
| D10 | Not now: relocking Cuelist-python #1, joe's pull-request deploys, and a forge-speech permission rule. | Peter, 2026-10-10 |
| D11 | The demo is not pushed until its commits, docs and tests agree. | Peter, 2026-10-10; done |
| D12 | The links between members are real app-to-app links, not relayed by the stage. | Peter, 2026-10-10; done |
| D13 | `--stage` skips each member's own check, because that check writes into the hub's show. Plain `qm family-demo` keeps the checks. | Peter, 2026-10-10 |
| D14 | Peter merges. Open work lands as stacked pull requests. | Peter, 2026-10-11 |
| D15 | The estate refresh is adopted as qm #138, with the demo stacked on it as #139. | Peter, 2026-10-10; done |
| D16 | ShowMidi's fix, hotplug docs and test scripts go onto #22's own branch, not a separate one. | Peter, 2026-10-11; done, merged as `aac3487` |
| D17 | Push every branch. Open pull requests where a branch stacks cleanly on an open one; otherwise list it here. Where mrharpo leads (ShowRunner, leo), push and list only. | Peter, 2026-10-12; done |
| D18 | Re-sign the unpushed qm commits before pushing them. | Peter, 2026-10-12; done |
| D19 | The fixes from the review of ShowRunner #39 go onto #39's own branch, and the review is posted. | Peter, 2026-10-12; done |

D17 and D19 are acts in ShowRunner beyond what mrharpo asked for, and Peter
asked for them after D4.

## State, as stacks (bottom first)

| Repo | Stack | Pull requests |
|---|---|---|
| qm | `main` `df1cb51` → `evolve/performing-estate-refresh` `39269ec` → `evolve/performing-family-demo` `4f8df09` | #138 ready, green; #139 draft on it, green |
| qm | `evolve/preflight-reports-environment` `9b03372`, from `main` | #161 ready, green |
| qm | `evolve/performing-family-consolidation` (this page) and `perspective/2026-10-09-a-comment-in-someone-elses-voice` `00f1256`, both from `main` | none |
| ShowStopper | `tests` `0b72bc4` → `feat/family-demo-contract` `d4668f1` → `feat/family-control` `c71b0d2` | #1 → #2 draft → #3 draft |
| carlos | `they` `a5540e7` → `fix/dials-cable-ends-and-scroll` `3e8800f` → `deps/they-batch-2026-10-09` `7750927` → `feat/family-demo-contract` `137f88c` → `feat/family-control` `91678af` | #17; the three above it have none |
| joe | #23's tip with `feat/transcript-lane` merged in, `restack/instruct-by-voice` `e15c83f` → `docs/walkthrough` `ed6e612` → `feat/family-demo-contract` `7c2923c` → `feat/family-control` `dad2a86` | none; #23 and #26 to #33 open unchanged |
| leo | `setlist` `8dce16c` (mrharpo) → `dependencies` `62cfd90` → `walkthrough` `93922ea` → `feat/family-demo-contract` `8e70e0d` → `feat/family-control` `dcc82c0` | #61 (mrharpo); none above it |
| ShowRunner | `fix/app-request-import` `11244d1` → `feat/ui-tests` `ce6dbed` → `feat/walkthrough` `6d37b67` → `feat/family-demo-contract` `8a8eb6a`; and `demo/family-stage` `a0059b6` (integrate `2b28210` plus the contract) → `feat/family-dispatch` `32a3097` | none; integrate is #30, draft |
| ShowRunner | `main` `aac3487` → `mrharpo/osc` `7c1d3cc` | #39 (mrharpo), green, review posted |
| looksatwords | `rescued/2024-09-02-flow-notebook`, `rescued/2024-11-30-cli-and-notebooks` | none |

Also on origin with nothing to do but delete once a person agrees:
`restack/readme-overview`, `restack/cookbook-voice-loop` and
`docs/walkthrough-after-docs` in joe. They restack #24 and #25, both closed (D5),
and `docs/walkthrough` replaces the third.

## ShowRunner #39 and the stack

#39 (mrharpo's Connection base and ShowOSC) carries eight fixes on its branch,
`2171b46..7c1d3cc`, one commit per runtime defect. Each adds a test that fails
before its fix. They cover a deadlock on Save, Reconnect or shutdown, an
offline TCP target stalling every send, relays sending the incoming address,
out-of-order dispatch, a TCP peer never reached again, NaN breaking the
monitor, unvalidated `args`, and MIDI virtual-port retries. The review comment
lists them. The `osc` extra now needs `python-osc>=1.10.2`. The three
socket tests in `tests/test_osc_live.py` skip in CI, which installs no extras.

Integration, checked with #39 at `2171b46` merged into `feat/family-dispatch`:

- Five conflicts, all additive:
  - `docs/ref/plugins.md`: both sections.
  - `show.toml`: the stack's live config plus #39's commented examples.
  - `pyproject.toml`: the stack's `python_version < '3.13'` rtmidi marker plus the `osc` extra.
  - `tests/test_plugins.py`: the count becomes 20.
  - `uv.lock`: relocked.
- The suite passed, the stack's tests plus #39's, none lost.
- `qm family-demo`, plain and `--stage`, passed: five of five cues delivered.

The stack's only edits to `midi.py` are #22's two original commits, which #39
contains. When #39 lands on `main`, the stack takes `main` with the same five
resolutions. That merge was not repeated at `7c1d3cc`.

#30 conflicts with `main` with or without #39. `db.py`'s import list wants the
union.

The hub then has two OSC senders: ShowProgrammer's `osc-targets` (and
ShowMixer for Ardour), and ShowOSC. Which one cues go through is undecided.

## The machine: a manual integration loop

- **Dev checkouts:** each core member is a worktree at
  `repos/qm/.int/dev/<member>`, on its top branch. The qm harness runs from
  `.int/dev/qm`. The held loop from 2026-10-11 is stopped; nothing listens on
  18400 to 18700.
- **Live loop:** `uv run qm family-demo --dev --open --work <repos>/qm/.int`,
  run from `.int/dev/qm`. `docs/cookbook/develop-a-family-member.md` is the
  full loop.
- **Gate before a commit:** the member's own suite, then `qm family-demo` both
  plain and with `--stage`, using `--work <repos>/qm/.int/g --port-offset 100`.
  The last gate passed both forms at the tips above.
- **Wave 0, rest of the family:** `private-34`'s suite and TheatreMix-python's
  pass from clean clones. The other later members have no suite.

## Unfinished, and what done looks like

- **qm, in order:** Peter merges #161 and #138. #139 is retargeted to `main`
  and marked ready, then merged. The status documents are regenerated on the
  new `main` as their own pull request. Done when `qm docs check` is clean and
  `status/harness.yaml` is inside its budget. A stash in the corpus clone holds
  the stopped session's regeneration; it is superseded by that pull request.
- **`the-performing-estate-refreshed.md`** arrives with #138, stamped
  2026-09-20, and this page replaces it. Done when it is deleted after #138
  merges. Its open residue is folded below.
- **carlos:** draft pull requests for the three layers above #17, each based
  on the one beneath it.
- **joe:** a base for `docs/walkthrough` once #23's stack lands. Then its
  stack becomes draft pull requests.
- **ShowRunner:** after #39 lands, `feat/family-dispatch` takes `main` with
  the resolutions above. Whether the held branches are wanted is mrharpo's
  (D4).
- **`private-34` in the demo:** its contract, `serve` without a system browser
  and `check` against `/wall/state`. Its seam to the hub is separate; its
  ShowRunner driver is a stub.
- **The rest of the family:** each later member's `needs` in
  `ci/family-demo.yaml`.

From the 2026-09-20 estate page, still open: Cuelist-python #1, qmetronome
#15, carlos #17, leo #61, ShowRunner #30. ShowStopper's
`fix/textual-containers` is on origin, waiting to be deleted (D6). dossier and
looksatwords each keep a `feat/loose-ends` branch with no pull request, by
decision. The eighteen synthesis questions still gate the first stubs.

## Blocked, and on whom

- **Peter:**
  - every merge;
  - the qm `.venv` repair;
  - two pushed commit messages that name the private instrument (`444f510`,
    `f208a2c` on #138 and #139), which only a history rewrite of those pull
    requests removes;
  - deleting the three joe leftovers;
  - which OSC sender cues use.
- **mrharpo:**
  - #39's merge;
  - #30's split, and whether the held ShowRunner branches are wanted;
  - leo #61;
  - the stale drafts holophonor #11, ludwig #9, QLab-python #2, qmetronome #13
    and joe #4;
  - archiving cesar and aes.

## Not verified

- The member stacks' CI workflows have not run on a hosted runner, and their
  browser pages have not run on Linux *(reported)*.
- The ShowRunner shutdown hazard: its server leaves child processes that must
  be forced at shutdown, in every gate run with or without #39. Cause not
  established.
- #39's fixes were integrated with the stack only at `2171b46`, not at
  `7c1d3cc`.

## Defects found, not yet filed (filing is outward, per D3)

| Repo | Defect | Provenance |
|---|---|---|
| ShowRunner #39 | `GET /midi/` changed shape; `midi.out` never fires; `/osc` nav entry without python-osc | read, not run; named in the #39 review |
| ShowRunner | ShowMidi defects 2 to 5 from the first #22 comment | reported |
| ShowRunner, carlos | uvicorn hangs at shutdown on Windows after a connection reset | reported |
| leo `main` | the setlist lists one song fewer than its count (`per_page: -1`) | reported; `setlist` rewrote search |
| joe | Vite and API ports are hardcoded and collide with family defaults | reported |
| joe | the playback marker divides seconds by a frame count | inferred from code, not observed |
| carlos | the status bar covers the first drum row | reported, from a screenshot |
