# Handoff — consolidating the performing family's open work

**Goal.** Bring every open question across the core performing family
(ShowRunner, ShowStopper, carlos, joe, leo) and the members phased after it
down to a decision, then act on each decision in slot order. A row leaves this
page when it is acted on, and the page is deleted when it is empty.

**Stamp.** 2026-10-10. Facts carried from a session's sub-agents are marked
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
| D8 | loopwall `pre-squash-2026-08-09-session` is kept on origin as `archive/pre-squash-2026-08-09-session`. | Peter, 2026-10-10; done |
| D9 | qmetronome #14 is closed. | Peter, 2026-10-10; done |
| D10 | Not now: relocking Cuelist-python #1, joe's pull-request deploys, and a forge-speech permission rule. | Peter, 2026-10-10 |

## Open: a decision Peter owns

| # | Question | Recommendation | Unblocks |
|---|---|---|---|
| Q1 | Merges are refused by the session harness's permission check. Peter: "stack PRs for now". But a stacked PR still takes the one-PR slot, so in carlos it turns the `slot` gate red on both PRs. | To settle: stack in repositories with no slot gate, and hold where the gate exists. | every R row |
| Q12 | qm `evolve/performing-estate-refresh` is three unpushed commits plus uncommitted work, stamped 2026-09-21. It holds the simultaneous-run plan this family's demo builds on. | Peter says whether its session is gone. If it is, land it before the demo branch. | R10 |

## Ready, in slot order, once Q1 is answered

| # | Act | Gate evidence |
|---|---|---|
| R1 | carlos: merge #17 (squash, like #16). Do not delete the branch from inside the clone, which has it checked out. | Checks green except `reuse`, which `GOVERNANCE.md` records as an accepted red. |
| R2 | carlos: push `deps/they-batch-2026-10-09` rebased on `they`, open it, and merge it when green. It supersedes #2, #3, #18 and #19. | 568 passed on `they` *(reported)*. Starlette 1.x needs the `TemplateResponse` fix it carries. |
| R3 | joe: merge #26 to #33 in order with merge commits, then push the restacked #23 and merge it, then open `docs/walkthrough`. | A guarded command list from the session *(reported)*. Every PR's CI green. |
| R4 | loopwall: merge #1, close #2 as covered by it. | 229 passed locally *(reported)*. CI test runs are manual-only. |
| R5 | qmetronome: merge #15. | 5 of 5 checks green *(reported)*. |
| R7 | ShowStopper: #1 is open. mrharpo reviews it. | 10 passed, rechecked in a fresh worktree. |
| R8 | leo: after #61, `dependencies`, then `walkthrough`, one at a time. | 32 and 39 passed *(reported)*. |
| R9 | qm: `perspective/2026-10-09-a-comment-in-someone-elses-voice`, `evolve/performing-family-demo` and this branch wait for Peter's qm slot. Several of his qm PRs are open. | — |
| R10 | qm: the demo branch, reworked under D1 and D2. | In progress. |

## Open: mrharpo's call (drafts need Peter's approval of the text, per D3)

- leo: the five dependabot PRs all conflict with #61. #59, #64 and #66 are superseded by it; #63 and #65 are behind v7 *(reported)*. #61 also commits `.backup` and `.patch` files, renders setlist titles nearly invisible, and has a README that understates the Node version.
- Stale drafts: holophonor #11, ludwig #9, QLab-python #2, TheatreMix-python's unopened `showrunner` branch, qmetronome #13 and joe #4.
- Archiving cesar and aes.

## Defects found, not yet filed (filing is outward, per D3)

| Repo | Defect | Provenance |
|---|---|---|
| ShowRunner | ShowMidi: a WinMM input crashes on its second unplug | reproduced first-hand; fix pushed as `fix/showmidi-winmm-input-reconnect` |
| ShowRunner | ShowMidi defects 2 to 5 | reported, stated in the #22 comment |
| ShowRunner, carlos | uvicorn hangs at shutdown on Windows after a connection reset | reported |
| leo `main` | the setlist lists one song fewer than its count (`per_page: -1`) | reported; `setlist` rewrote search |
| joe | Vite and API ports are hardcoded and collide with family defaults | reported |
| joe | the playback marker divides seconds by a frame count | inferred from code, not observed |
| joe | #7's failing check; its log has expired | unknown |
| carlos | the status bar covers the first drum row | reported, from a screenshot |
