# Handoff — the voice loop, reviewed as one, 2026-10-04

**Stamped 2026-10-04.** `qm` `main` at `df1cb51`; `vox` `main` at `d94fe6b`;
`joe` `main` at `2ba994d`; `qmcp` `main` at `ed01fc0`. Every figure on this page
was true at the commits it names and nowhere else.

**Nothing on this page is a task.** It is one review of the whole open set --
fifteen pull requests across four repositories -- so the set can be approved
together and land in order. [`the-voice-loop.md`](the-voice-loop.md) is the
state; this is the queue. Delete this page when its work lands.

---

## 1. How to review it: one branch per repository

Each repository has `demo/voice-loop-2026-10-04`: its `main` with every open
pull request below merged in, in dependency order, no conflict in any of them.
A demo branch is for testing and demonstrating the set together and is never
merged; the set lands through its own pull requests (§5), so each change keeps
its own record.

| Repository | Demo branch head | Merged into it, in order |
|---|---|---|
| `vox` | `a8934ff` | #9, #10 |
| `joe` | `624fb61` | #23, #24 |
| `qmcp` | `d239251` | #54, #55, #56, #58, then the stack #60, #61, #62, #63, #64 |
| `qm` | see §6 | #134, #135 |

**The demonstration** is `qmcp`'s `docs/voice-loop-demo.md`, run from a `qmcp`
checkout of the demo branch. Three tiers, each adding one real thing:

1. **Nothing real** -- `uv run qmcp cookbook voice`, `uv run qmcp cookbook
   instruct`, `uv run qmcp cookbook instruct --runtime scripted`. No hardware,
   no model, nothing spent; each prints `[ok]` per case.
2. **The local model** -- `uv run qmcp cookbook instruct --runtime local`.
   Two spoken instructions in one project on the model this server stands up:
   the second gives no clone, asks about "that file", and is answered only
   because qmcp remembered the clone and handed the model what the first
   instruction found. Continuity comes from qmcp, not the model.
3. **A person at the microphone** -- `uv run joe dev` from `joe`'s demo
   branch, `uv run qmcp serve`, **Instruct by voice** on the page, then
   `uv run qmcp instructions act <id> --runtime local --budget 1 --cwd <clone> --voice`.
   This tier has not been run; it is the review's one live step.

## 2. The pull requests

| | Checks | What it is | Look at |
|---|---|---|---|
| **`qmcp` #54** | 8/8 | Phase 10 as built; Phase 11, habits into auto-approvals | Phase 11's constraints (§3, decision 2). |
| **`qmcp` #55**, draft on #54 | 7/7 | the roadmap's test counts and Phase 9's voice route | that it changes prose only. |
| **`qmcp` #56** | 8/8 | `uv run qmcp preflight`, a dispatcher to the seed workflow runner | `--help` reaching the runner rather than the command; the `AGENTS.md` paragraph on the red REUSE step, which `qm` #134 retires. |
| **`qmcp` #58** | 8/8 | an open question answered by voice | the read-back's precedence: "yes, again" records, because a yes is read before the option named, as the approval dialog does. |
| **`qmcp` #60** | 8/8 | `vendor/vox` at `vox` #10's branch head | that the pin must move to `vox` #10's merge commit before it merges (§5). |
| **`qmcp` #61**, draft on #60 | 7/7 | the instruction inbox | `match_option` changed for every caller: a hyphen is a word break, and of several options named the one covering the others wins, so "approve all" against `["approve", "approve all"]` is `approve all` where it was no match (§3, decision 3). |
| **`qmcp` #62**, draft on #61 | 7/7 | acting on an instruction: consent for every runtime, the brief from qmcp's record, the `local` runtime, the command-line adapter behind the same contract | the brief (`Brief.prompt()`), what the local runtime may read (`inside`), the read protocol in its prompt and why the service's tool field is not used, and walkthrough 09's last section. |
| **`qmcp` #63**, draft on #62 | 7/7 | the outcome said back; the offline loop | the panel told `speaking` then `idle`, never `recorded`. |
| **`qmcp` #64**, draft on #63 | 7/7 | `cookbook instruct --runtime local`; `docs/voice-loop-demo.md` | the demo page as a stranger's first read. |
| **`vox` #10** | 3/3 | the pause parameter on the engine contract | the offline engine holding the real engine's bounds, so an out-of-range pause fails offline too. |
| **`vox` #9** | 3/3 | `HANDOFF.md` at the current tips | that it changes prose only. |
| **`joe` #23** | 5/5 | **Instruct by voice** on the page | its place in the bottom bar rather than beside **Answer by voice** (§3, decision 4). |
| **`joe` #24**, draft on #23 | 4/4 | the README's overview | joe's two jobs, and the commands as they are. |
| **`qm` #134** | 11/11 | the REUSE lint through `uvx` | the seed copy, which reaches `qmcp` only at its next pin bump. |
| **`qm` #135** | -- | the voice-loop handoff restamped, and this page | §1 of the handoff, the open set as one table. |

`qmcp` #57 and #59 were closed unmerged: an MCP tool for a coding-assistant
session to ask the queue, and recall from a coding assistant's session store.
The loop's agent is a runtime qmcp calls, and its continuity is qmcp's record.

## 3. Decisions nobody has taken

Ordered by what they block.

1. **Approve the set.** It lands in the order of §5; nothing in it is
   released until a tag says so.
2. **Phase 11 against the spending record.** `records/DRAFT-no-unattended-spending.md`
   clause 5 says consent to a paid call does not carry forward, and its
   revision triggers name "anybody proposing a remembered approval" as the
   moment to check the workflow instead. Phase 11 confines a rule to runs that
   spend nothing and is built only after the corpus has read it. Whether that
   is the reading the corpus wants is the corpus's to say.
3. **`match_option` for every closed choice** (#61). Accept the wider reading,
   or narrow it to the instruction dialog and leave the approval dialog as it
   was.
4. **Where Instruct by voice sits** (`joe` #23). The voice panel hides when
   nothing is waiting or speaking, which is when an instruction is given, so
   the button is in the bottom bar. Accept, or have the panel stay open.
5. **The design-review consent request** (`design-review-qm-audit-2026-09-27`)
   on the harness queue has not been read since 2026-09-27.

Decided in the session that built the set, and recorded here so they are not
asked again: approvals are required for every runtime for now, the local
model included; the local runtime and the command-line runtime are read-only
(the command line is passed no permission flag); `--cwd` wins over a
remembered clone.

## 4. What to distrust

- **The demo branches merged without a conflict, and the set lands one pull
  request at a time.** The stacked pull requests will each need `main` merged
  in as the ones before them land; the demo branch shows that merge is clean
  at these heads, not at whatever heads exist when it happens.
- **No person has spoken to it.** Tiers 1 and 2 answer every consent with a
  script on `vox`'s deterministic engine. Tier 3 is unrun.
- **The local model is a quick reader.** On tier 2 it has named `README.md`
  and answered from it; it has also quoted a heading where a sentence was
  asked for, and once looped between rereading a file and searching for a
  phrase it invented until the step bound failed the run -- the case #62's
  last commit now answers. The spoken summary is cut at a word boundary within
  a fixed length, which can end a clause early ("... when a.").
- **The model service on this workstation stalls.** A generation that reused
  a cached prompt stopped producing tokens until its call's cap cancelled it,
  and later calls queued behind it until the model was unloaded. A stall is a
  failed run naming the endpoint, not a hang; it is the service's, not the
  set's.
- **The command-line runtime has never run.** Its command line and its
  reading of the output are asserted; the tool is not on the workstation.
- **Every local run is Windows.** The hosted checks run the suites on Linux,
  where the flow tests that skip locally run.
- **`uv run qmcp preflight` reports the REUSE step red** in a uv environment
  until `qm` #134 reaches `qmcp`'s pin; the seed runner under the system
  interpreter reports it green.

## 5. The order the set lands in

On approval, each pull request merges when it is ready, in this order.
`uv run qm merge --list` shows them live; `uv run qm merge --repo <owner/name>
--pr <n> --yes` merges one, and retargets the pull requests stacked on it
before its branch can go. A stacked pull request is retargeted onto `main`,
has `main` merged in, and is marked ready before it merges.

1. **`vox`:** #10, then #9.
2. **`qmcp`:** #54, then #55 (retargeted onto `main`); #56; #58; then #60,
   after one commit moves its `vendor/vox` pin to `vox` #10's merge commit;
   then #61, #62, #63 and #64, each retargeted onto `main` as the one beneath
   it lands.
3. **`joe`:** #23, then #24.
4. **`qm`:** #134, then #135.

After the set lands: `qm` #134 reaches `qmcp` through a pin bump, which also
retires the `AGENTS.md` paragraph from #56; Phase 10's boxes are ticked on the
roadmap; #58's and #61's read-back helpers become one; and the demo branches
are deleted by a person, since deletion is outside what a handoff authorises.

## 6. What was tested, at which commits

Run on the workstation the set was built on, from a worktree of each demo
branch.

- **`vox` at `a8934ff`:** `uv run pytest -q` 120 passed; `uv run vox loop
  --offline` closed; the walkthrough unchanged; the wheel check passed; the
  mutation harness caught 17 of 17.
- **`joe` at `624fb61`:** `uv run pytest -q` 151 passed; `npx playwright test`
  45 passed; `npm run build` built, leaving the tree clean.
- **`qmcp` at `d239251`:** `uv run pytest -q` 1139 passed, 11 skipped;
  `cookbook voice` 5 of 5; `cookbook instruct` 4 of 4 and 2 of 2 loops;
  `cookbook instruct --runtime scripted` and `--runtime local` both showed
  continuity, exit 0. The seed workflow runner under the system interpreter:
  all 11 executed steps passed. `uv run qmcp preflight` at the head before
  #64 merged: 9 of 10, the REUSE step red for the reason in §4.
- **Hosted:** every pull request in §2 green at its head when this page was
  written; on a demo branch only `qmcp`'s submodule check runs, and passed.

## 7. What none of this authorises

Merging, retargeting, deleting a branch, ratifying a record and cutting a tag
are each a person's. The pull requests are the audit record; this page is the
review of them.
