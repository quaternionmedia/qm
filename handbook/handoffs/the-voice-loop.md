# Handoff — the voice loop: what landed, and the one thing that did not

**Stamped 2026-09-27.** `qm` `main` at `d6dc5cd`; `vox` `main` at `a9d7988`;
`joe` `main` at `fa0ce67`; `qmcp` `main` at `d834916` with
`feat/voice-interaction` at `cb071a6`. Every figure here was true at those
commits and nowhere else. Re-derive before acting on any of it.

`vox` and `joe` carry no `governance/qm` submodule, and `vox` is on no roster.
The cross-repository state is therefore recorded here and nowhere else.
`vox/HANDOFF.md` is the per-repository page and holds the verification
commands.

---

## 0. State

| Repository | Pull request | Outcome |
|---|---|---|
| `joe` | #8 — the application | merged, `e32eb73` |
| `joe` | #9 — speech analysis | merged, `fa0ce67` |
| `vox` | #1 — the deterministic loop | merged, `a9d7988` |
| `qmcp` | #38 — voice-answered HITL | **open, ready, green, unmerged** |
| `joe` | #10 — the Python suite in CI | merged, `03839f6` |

`joe`'s two lines are reconciled. `main` had diverged from the application's
branch at `a9685fc` (2024-04-19) and carried one commit since — the one adding
`.github/`. The merge kept both workflow files and produced a tree where
`uv run --frozen pytest tests/` reports 80 passed and `npm ci && npm run build`
both exit 0.

`vox` is now **public**. It was created private, which is why every check on
`qmcp` #38 had failed since 2026-09-22: a public repository's runner cannot
clone a private submodule. Five failures, one cause.

## 1. What remains

**`qmcp` #38 is one click.** All seven checks pass, the branch is
`MERGEABLE`/`CLEAN`, and it is no longer a draft. Merging it is the last step
of the chain above.

Unfinished work, each with what done looks like:

- **The live half is unproven by anything automatic.** No test starts a real
  joe and drives whisper, and none drives real `pyttsx3`. The offline engine is
  a codec wearing joe's HTTP contract: the seam is proven, transcription
  accuracy is not. *Done* is a recorded run of `uv run vox loop` without
  `--offline` against a live backend, with the transcript kept beside the
  claim.
- **`joe` composes paths with literal backslashes.**
  `Modules/utilities.py` builds `f"{current_path}\Data\Output\{iteration}\MIDI\\"`,
  which is one filename component on Linux rather than a directory structure,
  and is also the source of `invalid escape sequence` warnings that a later
  Python raises. Six tests in `tests/test_main.py` fail on `ubuntu-latest` for
  this one reason; 74 pass. The merged workflow runs on `windows-latest`
  and reports 80 passed. *Done* is those paths going through `pathlib`, after
  which that workflow can become a matrix instead of Windows only.
- **`joe`'s Playwright suite runs nowhere.** `tests/e2e/` needs browser
  binaries and a live server, and neither is set up. The Python suite is
  covered by `joe` #10, the first workflow in that repository to read any
  Python. *Done* for the E2E half is a workflow that has been watched going
  red.
- **The human loop is not built** — speaking an instruction, an agent acting,
  the result spoken back. `qmcp human voice` is its approval case. The harness
  was built first so this has something deterministic to iterate against.
- **`qmcp`'s 11 skipped tests are not a pass.** They are unexamined, and that
  repository's tag-determinism gate treats skips as a failure at tag time.

## 2. Blocked on a person

- **Whether `vox` joins the roster, and in which family.** It appears in no
  `ci/workspace.yaml` entry and no `families.json` member list. Membership is a
  claim a person makes and is never inferred.
- **Whether `joe` should carry the corpus.** Without a `governance/qm`
  submodule none of the gates, the slot check or `/cowork` reach it.
- **The torch subtree.** `joe`'s lock grew from 82 packages to 113 and the 31
  added are torch, triton and CUDA — the subtree `00d8077` had removed. They
  were unused leftovers then and are load-bearing now, so re-adding them does
  not undo that commit. A lean default install and a working `joe voice` can
  both be had through an optional `voice` extra. That is a decision and was
  left as one.

## 3. What no check covers

- **No workflow runs `qm private-names`.** `registries.yml` excludes it
  deliberately, because its admission test is that a check reads committed
  files and nothing else, and this one reads a gitignored companion or the
  forge. The consequence was observed rather than theorised: a handoff page
  naming a private repository was committed and pushed to a public one, and
  every gate on that pull request was green. The docstring claiming CI runs it
  has been corrected; the gap is stated rather than closed, because closing it
  means either a gate that reds a pull request for a reason its author cannot
  fix, or a runner credentialed to enumerate the organisation's private
  repositories.
- **Nothing detects a public repository vendoring a private submodule.**
  `check-submodule-refs` fails on it, but reports it as a possibly-unpushed
  pin, and names the ambiguity in its own error text rather than resolving it.
  Draft status kept that red invisible for five days.
- **The path-escape case `..\outside.wav` is weaker on Linux**, where a
  backslash is an ordinary filename character and the 404 means *absent* rather
  than *refused*. The `../` cases exercise containment on both, and the
  mutation dropping the containment check is caught by those.

## 4. Standing constraints

- *Keep everything local* is **not** in force.
- **`joe`'s `package-lock.json` is dirty and was dirty on arrival** — +387/−201,
  on no branch. It was stashed for the rebase and restored to that exact state.
  It is uncommitted by decision, not by oversight.
- **Merged branches were not deleted.** `handbook/handoffs/README.md` places
  branch deletion outside what a handoff authorises, so `docs/onboarding-hardening`
  and `feat/voice-interaction` remain.

---

*Only the repositories above were audited. Other pages in this directory were
not checked against `main`, so their queue rows stand as they were.*
