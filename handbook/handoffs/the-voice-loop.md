# Handoff — the voice loop: the deterministic half, and the merge order

**Stamped 2026-09-27.** `qm` `main` at `d6dc5cd`; `vox`
`feat/deterministic-loop` at `27d83b6` with `main` at `2a54677`; `joe`
`feat/voice-interaction` at `d1dc980` with `main` at `4d96a5d` and the branch's
base `origin/docs/onboarding-hardening` at `9e70fc9`; `qmcp`
`feat/voice-interaction` at `ae1ef36` with `main` at `d834916`. Every figure
here was true at those commits and nowhere else — re-derive before acting on
any of it, and never quote one as current.

The work spans three repositories, **two of which are outside this corpus**:
`joe` and `vox` have no `governance/qm` submodule, and `vox` is on no roster.
That is why this page exists here rather than in one of them — the merge order
below is the only place the three are described together. `vox/HANDOFF.md` is
the per-repo page and carries the verification commands.

---

## 0. What the loop is, and what landed

Voice interaction is `joe` (whisper behind an HTTP API) → `vox` (the seam:
TTS and orchestration) → `qmcp` (voice-answered human-in-the-loop). What
existed on 2026-09-21 was that chain, working, with every vox test replacing
`JoeSTT` with a `MagicMock` — so the suite proved a call was made and nothing
about the wire, and the only end-to-end check was three terminals, a
microphone and somebody listening.

**vox PR #1** closes that. `vox.engine` is a real HTTP server on a port the OS
picks, speaking joe's `/api/voice/*` contract; `JoeSTT` drives it unmodified;
`VoiceSession.round_trip` hands vox's own output back to the engine so the loop
closes rather than stopping at the audio it produced. `uv run vox loop
--offline` runs the whole thing in about two thirds of a second with no engine,
no model download and no hardware, and `uv run pytest` runs it too.

**joe PR #9** was rebased onto its current base and is now clean. It also
carries a hole the rebase exposed — see §2.

Neither is merged. Both are open, green, and assigned.

## 1. The merge order, which is the whole point of this page

The demo is not presentable until these land, **in this order**. Each is a
human's call; none is an agent's.

| # | Action | State | Verified |
|---|---|---|---|
| 1 | Merge **joe #8** (`docs/onboarding-hardening` → `main`) | open, not mine | merges with **zero conflicts**, and joe's two `.github` files survive — checked by performing the merge in a throwaway worktree, not by reading |
| 2 | Merge **joe #9** (voice) | `MERGEABLE` / `CLEAN`, 3 commits | 80 tests pass locally; **no CI runs them** (§3) |
| 3 | Merge **vox #1** (the deterministic loop) | open, both CI jobs green | tests, walkthrough, mutations and two drift gates, all green on `ubuntu-latest` |
| 4 | Bump `qmcp`'s `vox` submodule off `2a54677`, then **qmcp #38** | draft, pinned to vox's pre-#1 `main` | not attempted |

Step 1 gates step 2 only in the sense that #9's base is #8's branch; once #8
merges, #9 retargets to `main` by itself.

**joe #8 and #9 are both open and both `subcontrabass`**, which is two slots in
one repository for one contributor. Step 1 resolves it. Until then joe is over
the limit and nothing new should be opened there.

## 2. What is unfinished

- **The live half is still hand-checked.** Nothing starts a real joe and drives
  whisper through it automatically, and nothing drives real `pyttsx3`. The
  deterministic engine is a codec with joe's contract around it: it proves the
  seam and makes no claim about whether whisper hears the words. *Done* looks
  like a run of `uv run vox loop` (no `--offline`) against a live backend, with
  the transcript recorded beside the claim.
- **`qmcp` #38 pins vox at `2a54677`**, which predates PR #1. *Done* is
  `git submodule update --remote` plus a commit, after step 3.
- **The human loop** — speak an instruction, an agent acts, it speaks back — is
  not built. The harness was built first, deliberately, so that half has
  something to iterate against. `qmcp human voice` is the approval case of it.
- **`joe` has no CI.** `.github/` exists only on joe's `main`, which diverged
  from the application's line at `a9685fc` (2024-04-19) and has exactly one
  commit since: the one that added the workflows. Everything else, including
  the entire application and all 80 tests, is on the other line. After step 1
  they are on one line and a workflow can run them. *Done* is a red run
  somebody caused on purpose.

## 3. Blocked on a person

- **Every merge in §1.** Four of them, in order.
- **Whether `vox` joins the roster**, and in which family. It is in no
  `ci/workspace.yaml` entry and no `families.json` member list. Membership is a
  claim a person makes and is never inferred, so this cannot be done by a
  session.
- **Whether `joe` should carry the corpus.** It has no `governance/qm`
  submodule, so none of the gates, the slot check or `/cowork` reach it.
- **The torch question.** joe #9 grows `uv.lock` from 82 packages to 113, and
  the 31 added are torch, triton and the CUDA subtree — the same subtree
  `00d8077` was deliberately removing. They were unused leftovers then and are
  load-bearing now, so re-adding them is not undoing that commit's intent. But
  if a lean default install matters more than `joe voice` working out of the
  box, the way to get both is an optional `voice` extra. That is a decision,
  not a fix, and it was left as a decision.

## 4. What could not be verified

Marked as inference, not stated flatly:

- **joe's suite has never run on Linux.** All 80 passes were on Windows 11.
  `comtypes` is `sys_platform == 'win32'`-marked and nothing imports `spacy`,
  so the Linux path is *expected* to work. Nothing has observed it.
- **vox's `..\outside.wav` path-escape case is weaker on Linux**, where a
  backslash is an ordinary filename character and the 404 comes from the file
  being absent rather than from containment. The `../` cases exercise
  containment on both, and the mutation that drops the containment check is
  caught by those — which CI confirmed on `ubuntu-latest`. The weak case is
  left in knowingly.
- **joe's `requirements.txt` omits `httpx`** while `pyproject.toml` lists it.
  That predates this work and was not touched, on the reasoning that fixing it
  would widen a PR about speech.

## 5. Standing constraints

- *Keep everything local* is **not** in force. It was asked and answered on
  2026-09-27: deliver normally.
- **`joe`'s working tree is dirty and was dirty on arrival** — `package-lock.json`,
  +387/−201, on no branch. It was stashed for the rebase and restored to
  exactly that state afterwards. It is not this session's and was not
  committed.
- **`qmcp` #38 being a draft is correct**, and is not an oversight to fix.
  qmcp's own `AGENTS.md` §3 says draft is load-bearing there and that leaving
  it is the human's call, which is the opposite of this corpus's `AGENTS.md`
  item 3. A session that "fixes" it is overriding the repository it is in.

---

*This page lists only the repositories above. The other handoffs in this
directory were not audited against `main` in this session, so the queue table's
rows for them are as they were.*
