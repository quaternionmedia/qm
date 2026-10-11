# Handoff — the performing family, consolidated and running locally

**Goal.** Land the core performing family's local work (ShowRunner,
ShowStopper, carlos, joe, leo) as stacked pull requests, keep the family demo
consistent while it lands, and phase the rest of the family in after it.

**Stamp.** 2026-10-11. The commits in the state table are where each branch
stood. Every count on this page is true at those commits only, so re-derive it
before you quote it. Facts carried over from a sub-agent are marked
*(reported)*; per `handbook/async-contract.md` §9 they are evidence, not
findings.

## Standing constraints

- **Keep it local.** Nothing below is pushed unless Peter says go (D14). The
  local-only commits are deliberate, not an oversight.
- **Forge speech is Peter's** (D3). A comment or reply is drafted, Peter
  approves the text, and it carries a `Tools:` note. A pull request body
  carries one too.
- **Private names.** The private instrument is `private-34` in committed text.
  This machine maps the reference to its clone in the gitignored
  `ci/workspace-private.yaml`, in the corpus clone and in `.int/dev/qm`. Run
  `uv run qm private-names --source host` before any push.
- **`VIRTUAL_ENV` points at the corpus clone's `.venv`** in this machine's
  shells. That `.venv` was damaged when another project's install landed in
  it, and Peter repairs it. Unset `VIRTUAL_ENV` for every command, and run
  qm's gates from a worktree with its own environment.

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
| D11 | The demo is not pushed until its commits, docs and tests agree. | Peter, 2026-10-10 |
| D12 | The links between members are real app-to-app links, not relayed by the stage. | Peter, 2026-10-10; done |
| D13 | `--stage` skips each member's own check, because that check writes into the hub's show. Plain `qm family-demo` keeps the checks. | Peter, 2026-10-10 |
| D14 | Peter merges. Pushes and pull-request creation wait on his go. Open work lands as stacked pull requests. | Peter, 2026-10-11 |
| D15 | The estate refresh is adopted as qm #138, with the demo stacked on it as #139. | Peter, 2026-10-10; done |
| D16 | ShowMidi's fix, hotplug docs and test scripts go onto #22's own branch, not a separate one. | Peter, 2026-10-11; done, merged as `aac3487` |

## State, as stacks (bottom first)

| Repo | Stack | Pushed |
|---|---|---|
| qm | `main` `df1cb51` → #138 `evolve/performing-estate-refresh` local `d287fce` (origin `3bb5503`) → #139 `evolve/performing-family-demo` local `709f32f` (origin `4801a3c`) | both PR branches are ahead of origin |
| qm | `evolve/performing-family-consolidation` (this page) and `perspective/2026-10-09-a-comment-in-someone-elses-voice` `901d0d8`, both cut from `main` | no |
| ShowStopper | #1 `tests` `0b72bc4` → #2 `feat/family-demo-contract` `d4668f1` → `feat/family-control` `c71b0d2` | #1 and #2 yes; control no |
| carlos | `they` `a5540e7` → #17 `fix/dials-cable-ends-and-scroll` `3e8800f` → `deps/they-batch-2026-10-09` `7750927` → `feat/family-demo-contract` `137f88c` → `feat/family-control` `91678af` | #17 yes; the rest no |
| joe | `restack/instruct-by-voice` `e15c83f` (#23 with `feat/transcript-lane` merged in, so it fast-forwards #23) → `docs/walkthrough` `ed6e612` → `feat/family-demo-contract` `7c2923c` → `feat/family-control` `dad2a86` | no; #23 and #26 to #33 are open on origin unchanged |
| leo | #61 `setlist` `8dce16c` (mrharpo) → `dependencies` `62cfd90` → `walkthrough` `93922ea` → `feat/family-demo-contract` `8e70e0d` → `feat/family-control` `dcc82c0` | no |
| ShowRunner | `main` `aac3487` includes ShowMidi (#22). Held locally per D4, all cut before that merge: `fix/app-request-import` `11244d1` → `feat/ui-tests` `ce6dbed` → `feat/walkthrough` `6d37b67` → `feat/family-demo-contract` `8a8eb6a`, and separately `demo/family-stage` `a0059b6` (integrate `2b28210` plus the contract) → `feat/family-dispatch` `32a3097` | no |

The two qm PR branches were reworded locally to keep a private name out of a
commit message. Pushing them is a fast-forward of origin; check with
`git rev-list --count <local>..origin/<branch>`, which must be 0.

## The machine: a manual integration loop

- **Dev checkouts:** each core member is a worktree at
  `repos/qm/.int/dev/<member>`, on its top branch. The qm harness runs from
  `.int/dev/qm`.
- **Live loop:** `uv run qm family-demo --dev --open --work <repos>/qm/.int`,
  run from `.int/dev/qm`. The stage is on 18405. Vite members hot-reload, and
  Python members restart when a file changes.
  `docs/cookbook/develop-a-family-member.md` is the full loop.
- **Gate before a commit:** the member's own suite, then `qm family-demo` both
  plain and with `--stage`, using `--work <repos>/qm/.int/g --port-offset 100`.
- **Performing workspace:** `repos/performance-machine.code-workspace` is
  written by `qm workspace --family show-control --family instruments --family
  performer-display --include qm`. It resolves every member, `private-34`
  included, through the private companion.

## Unfinished, and what done looks like

- **qm #138 and #139 pushed** (Peter's go). Done when both fast-forward origin,
  and the #138 body's docs-check claim is corrected: the commit it described
  failed `qm docs check` until the cookbook regeneration that is now in it.
- **Member stacks opened as stacked pull requests** (Peter's go), in the order
  of the table above. Done when each layer is a pull request on the one beneath
  it and every layer is green.
- **ShowRunner's held stack, rebased onto `main`.** ShowMidi landed after these
  branches were cut, and `demo/family-stage` carries the older ShowMidi from
  integrate. Done when `feat/family-dispatch` sits on `main`, its suite and
  `qm family-demo --stage` pass, and mrharpo has been asked through a draft
  Peter approves (D3, D4).
- **`private-34` in the demo.** It is declared in the instruments phase and not
  run. Done when it implements the contract: `serve` on a given port without
  opening a system browser, and `check` against `/wall/state`. A seam to the
  hub is a separate question: its ShowRunner driver is a stub.
- **Handoff queue consolidation** (`handbook/consolidation-runbook.md` Step 7):
  not done in this pass. Many qm pull requests from other sessions are open.

## Blocked, and on whom

- **Peter:**
  - every push and merge;
  - the qm `.venv` repair;
  - two pushed commit messages that name the private instrument (`444f510`,
    `f208a2c` on #138 and #139), which only a history rewrite of those pull
    requests removes;
  - carlos #17's merge.
- **mrharpo:**
  - ShowRunner #30's split, and whether the held branches above are wanted;
  - leo #61;
  - the stale drafts holophonor #11, ludwig #9, QLab-python #2,
    TheatreMix-python's `showrunner` branch, qmetronome #13 and joe #4;
  - archiving cesar and aes.

## Not verified

- The member stacks' new CI workflows have not run on a hosted runner, and their
  browser pages have not run on Linux *(reported)*.
- The ShowRunner shutdown hazard: its server leaves child processes that must
  be forced at shutdown, in every run. Cause not established.

## ShowMidi, landed

#22 merged as `aac3487`. It carries the WinMM input fix: a client whose close
fails is retired instead of reused. It also carries `scripts/midi/hotplug.py`
(virtual-device harness), `scripts/midi/watch.py` (hand-test watcher) and
`docs/cookbook/midi-hotplug.md`, whose results table is the record. One
limitation stays open there by design: a replug inside one reconnect interval
is not noticed. It reproduces on a virtual port and did not occur on a
Launchkey 49.

## Defects found, not yet filed (filing is outward, per D3)

| Repo | Defect | Provenance |
|---|---|---|
| ShowRunner | ShowMidi defects 2 to 5 from the first #22 comment | reported |
| ShowRunner, carlos | uvicorn hangs at shutdown on Windows after a connection reset | reported |
| leo `main` | the setlist lists one song fewer than its count (`per_page: -1`) | reported; `setlist` rewrote search |
| joe | Vite and API ports are hardcoded and collide with family defaults | reported |
| joe | the playback marker divides seconds by a frame count | inferred from code, not observed |
| carlos | the status bar covers the first drum row | reported, from a screenshot |
