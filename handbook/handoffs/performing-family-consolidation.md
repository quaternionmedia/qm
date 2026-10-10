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

## Open: a decision Peter owns

| # | Question | Recommendation | Unblocks |
|---|---|---|---|
| Q1 | Merges are refused by the session harness's permission check. Should a session merge its own green pull request, as `AGENTS.md` item 3 says? Or does Peter run the merges? | Allow it in Peter's repositories. Peter merges nothing in mrharpo's, because he reviews those. | every R row |
| Q2 | ShowRunner #30: does Peter split it into the sequential series, or ask mrharpo first? mrharpo wrote that he plans to split it himself. | Ask first: draft the question for approval. | R6 |
| Q3 | joe #24 and #25 document `qmcp serve --converse`, which is not on qmcp `main` yet. | Close both now and reopen #25 restacked once qmcp lands. | R3 |
| Q4 | ShowStopper `fix/textual-containers`: its message's premise does not hold *(reported, rechecked: Textual 0.86.3 still has `HorizontalGroup`)*. | Drop it, or cut it to the colour change after #1. | — |
| Q5 | leo, once #61 lands: the security lock fix or the walkthrough first? | Security first. | R8 |
| Q6 | leo's walkthrough puts a browser job back into CI. | Yes. It is the single-app check D1 asks for. | R8 |
| Q7 | loopwall `pre-squash-2026-08-09-session`: its tree equals origin `main` at `60a6147` *(reported)*. Only the commit messages are unique. | Push it as an archive ref. | — |
| Q8 | Cuelist-python #1 does not lock against ShowRunner `main` *(reported)*. | Relock it against `main` now, as a small PR on its own. | — |
| Q9 | qmetronome #14 (Copilot drafts, assigned to Peter). | Close it. #15's body says its premise does not hold. | — |
| Q10 | joe's `deploy.yml` deploys pull-request builds to Pages. The live site is an unmerged build *(reported)*. | One `if:` as its own PR, after the walkthrough. | — |
| Q11 | An `ask` permission rule on forge speech: `gh pr comment`, `gh issue comment`, `gh pr review`, and `gh api` comment writes. | Add it. | — |
| Q12 | qm `evolve/performing-estate-refresh` is three unpushed commits plus uncommitted work, stamped 2026-09-21. It holds the simultaneous-run plan this family's demo builds on. | Peter says whether its session is gone. If it is, land it before the demo branch. | R10 |

## Ready, in slot order, once Q1 is answered

| # | Act | Gate evidence |
|---|---|---|
| R1 | carlos: merge #17 (squash, like #16). Do not delete the branch from inside the clone, which has it checked out. | Checks green except `reuse`, which `GOVERNANCE.md` records as an accepted red. |
| R2 | carlos: push `deps/they-batch-2026-10-09` rebased on `they`, open it, and merge it when green. It supersedes #2, #3, #18 and #19. | 568 passed on `they` *(reported)*. Starlette 1.x needs the `TemplateResponse` fix it carries. |
| R3 | joe: merge #26 to #33 in order with merge commits, then push the restacked #23 and merge it, then open `docs/walkthrough`. | A guarded command list from the session *(reported)*. Every PR's CI green. |
| R4 | loopwall: merge #1, close #2 as covered by it. | 229 passed locally *(reported)*. CI test runs are manual-only. |
| R5 | qmetronome: merge #15. | 5 of 5 checks green *(reported)*. |
| R6 | ShowRunner: after Q2, open `fix/app-request-import`, then `feat/ui-tests`, then `feat/walkthrough`, one at a time. | Each green locally *(reported)*. |
| R7 | ShowStopper: #1 is open. mrharpo reviews it. | 10 passed, rechecked in a fresh worktree. |
| R8 | leo: after #61, `dependencies`, then `walkthrough`, one at a time. | 32 and 39 passed *(reported)*. |
| R9 | qm: `perspective/2026-10-09-a-comment-in-someone-elses-voice`, `evolve/performing-family-demo` and this branch wait for Peter's qm slot. Several of his qm PRs are open. | — |
| R10 | qm: the demo branch, reworked under D1 and D2. | In progress. |

## Open: mrharpo's call (drafts need Peter's approval of the text, per D3)

- ShowRunner #30's split (Q2).
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
