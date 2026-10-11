# Handoff — consolidating the performing family's open work

**Goal.** Bring every open question across the core performing family
(ShowRunner, ShowStopper, carlos, joe, leo) and the members phased after it
down to a decision, then act on each decision in slot order. A row leaves this
page when it is acted on, and the page is deleted when it is empty.

**Stamp.** 2026-10-11. Facts carried from a session's sub-agents are marked
*(reported)*: they are evidence, not findings (`handbook/async-contract.md` §9).

## Decided

| # | Decision | By |
|---|---|---|
| D1 | Single-app checks live in the app. Coordinated checks, meaning members up together, isolation and seams, live in qm. | Peter, 2026-10-10 |
| D2 | The family demo runs each member's branch or pull request with active work. Where that is ambiguous, the app gets a stub CLI to conform to. | Peter, 2026-10-10 |
| D3 | Text posted to a forge under a person's account is drafted, approved by that person and carries a `Tools:` note. See `perspectives/2026-10-09-a-comment-in-someone-elses-voice.md`. | Peter, 2026-10-09 |
| D4 | ShowRunner #30's split is mrharpo's. Peter opens nothing in ShowRunner beyond what #22 asks for. | Peter, 2026-10-10 |
| D5 | joe #24 and #25 are closed and #25 is retargeted to `main`, so it reopens once qmcp's `--converse` lands. | Peter, 2026-10-10; done |
| D6 | ShowStopper `fix/textual-containers` is dropped. Its premise does not hold. | Peter, 2026-10-10 |
| D7 | leo, after #61: the security lock fix first, then the walkthrough with its browser CI job. | Peter, 2026-10-10 |
| D8 | `private-34`'s `pre-squash-2026-08-09-session` is kept on origin as `archive/pre-squash-2026-08-09-session`. | Peter, 2026-10-10; done |
| D9 | qmetronome #14 is closed. | Peter, 2026-10-10; done |
| D10 | Not now: relocking Cuelist-python #1, joe's pull-request deploys, and a forge-speech permission rule. | Peter, 2026-10-10 |
| D11 | Nothing of the demo is pushed until it is consistent: commits, docs and tests agree. That is its gate. | Peter, 2026-10-10 |
| D12 | The demo's links between members become real app-to-app links, built locally as part of the demo, not relayed by the stage. | Peter, 2026-10-10 |
| D13 | `--stage` skips each member's own check, because it would write into the hub's show. Plain `qm family-demo` keeps those checks. | Peter, 2026-10-10 |
| D14 | Peter merges. Pushes and pull-request creation wait on his go. | Peter, 2026-10-11 |
| D15 | qm `evolve/performing-estate-refresh` is adopted as #138, and the demo branch is stacked on it as #139. | Peter, 2026-10-10; done |

## Reconcile

Each repository's open work as a stack, bottom first. Each layer merges after
the one beneath it, by Peter (D14).

| Repo | Stack |
|---|---|
| qm | #138 → #139 |
| ShowStopper | #1 → #2 → `feat/family-control` |
| carlos | #17 → deps → contract → control |
| joe | restack → walkthrough → contract → control |
| leo | #61 → dependencies → walkthrough → contract → control |
| ShowRunner | held, per D4 |

## Ready, in slot order

| # | Act | Gate evidence |
|---|---|---|
| R1 | carlos: merge #17 (squash, like #16). Do not delete the branch from inside the clone, which has it checked out. | Checks green except `reuse`, which `GOVERNANCE.md` records as an accepted red. |
| R2 | carlos: push `deps/they-batch-2026-10-09` rebased on `they`, open it, and merge it when green. It supersedes #2, #3, #18 and #19. | 568 passed on `they` *(reported)*. Starlette 1.x needs the `TemplateResponse` fix it carries. |
| R3 | joe: merge #26 to #33 in order with merge commits, then push the restacked #23 and merge it, then open `docs/walkthrough`. | A guarded command list from the session *(reported)*. Every PR's CI green. |
| R4 | `private-34`: merge #1, close #2 as covered by it. | 229 passed locally *(reported)*. CI test runs are manual-only. |
| R5 | qmetronome: merge #15. | 5 of 5 checks green *(reported)*. |
| R7 | ShowStopper: #1 is open. mrharpo reviews it. | 10 passed, rechecked in a fresh worktree. |
| R8 | leo: after #61, `dependencies`, then `walkthrough`, one at a time. | 32 and 39 passed *(reported)*. |
| R9 | qm: `perspective/2026-10-09-a-comment-in-someone-elses-voice` and this branch wait for Peter's go (D14). | — |
| R10 | qm: #139, the demo branch, reworked under D1 and D2 and stacked on #138. | Reconciled with origin; its live runs are not yet done. |

## Open: mrharpo's call (drafts need Peter's approval of the text, per D3)

- leo: the five dependabot PRs all conflict with #61. #59, #64 and #66 are superseded by it; #63 and #65 are behind v7 *(reported)*. #61 also commits `.backup` and `.patch` files, renders setlist titles nearly invisible, and has a README that understates the Node version.
- Stale drafts: holophonor #11, ludwig #9, QLab-python #2, TheatreMix-python's unopened `showrunner` branch, qmetronome #13 and joe #4.
- Archiving cesar and aes.

## Defects found, not yet filed (filing is outward, per D3)

| Repo | Defect | Provenance |
|---|---|---|
| ShowRunner | ShowMidi: a WinMM input dies after one replug, and the next unplug crashes or hangs the server | reproduced first-hand; fix on `fix/showmidi-winmm-input-reconnect`; see ShowMidi below |
| ShowRunner | ShowMidi: a replug faster than the reconnect interval leaves both directions dead while the status reads green, with or without the fix | reproduced first-hand on a virtual port; see ShowMidi below |
| ShowRunner | ShowMidi defects 2 to 5 | reported, stated in the #22 comment |
| ShowRunner, carlos | uvicorn hangs at shutdown on Windows after a connection reset | reported |
| leo `main` | the setlist lists one song fewer than its count (`per_page: -1`) | reported; `setlist` rewrote search |
| joe | Vite and API ports are hardcoded and collide with family defaults | reported |
| joe | the playback marker divides seconds by a frame count | inferred from code, not observed |
| joe | #7's failing check; its log has expired | unknown |
| carlos | the status bar covers the first drum row | reported, from a screenshot |

## ShowMidi

ShowRunner #22's head is `f8ae176`. The fix is `10dd04f`, which carries the
same patch as `75a4383` on origin's `fix/showmidi-winmm-input-reconnect`.

- On `f8ae176`, the input dies after one replug and the server crashes on the
  next unplug. Reproduced first-hand by the coordinator on a virtual port.
- On a Novation Launchkey 49, the replug gave rtmidi's "valid connection
  already exists" warning and the input monitor stayed empty, and the next
  unplug hung the server. Reproduced first-hand.
- `10dd04f` survives slow unplug cycles and fast flaps *(reproduced first-hand on a virtual port)*.
- On the Launchkey, `10dd04f` kept input working after every replug and the
  server up through every unplug. Peter unplugged by hand, and the coordinator
  watched. Two quick wiggles were both noticed, because USB re-enumeration
  outlasted a 2 s interval.
- A replug faster than the reconnect interval leaves both directions dead while
  the status reads green, on `f8ae176` and with the fix alike *(reproduced
  first-hand on a virtual port; not reproduced on the Launchkey)*. The fix does
  not cover it.
- `8bbce28` documents the hotplug behaviour in ShowRunner's plugin reference,
  on the fix branch.

Verification:

- `10dd04f`: 5 slow cycles and 40 flaps at a 0.5 s interval pass *(run first-hand)*.
- Fast replug: both directions dead with status green, 5 of 5, on `f8ae176`
  and on `10dd04f` *(run first-hand)*.
- Launchkey 49, `10dd04f`, 2 s interval: 3 of 3 slow cycles with input after
  each, 2 of 2 quick wiggles detected, and no crash or hang *(run first-hand)*.
- `gh pr view 22 --repo quaternionmedia/ShowRunner --json headRefOid`:
  `f8ae176`.
- `git show <commit> | git patch-id --stable`: `10dd04f` and `75a4383` both
  give `0bf4917`.
