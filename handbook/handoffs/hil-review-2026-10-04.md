# Handoff — the voice loop, reviewed as one, 2026-10-04

**Stamped 2026-10-04.** `qm` `main` at `df1cb51`; `vox` `main` at `d94fe6b`;
`joe` `main` at `2ba994d`; `qmcp` `main` at `ed01fc0`. Every figure on this page
was true at the commits it names and nowhere else.

**Nothing on this page is a task.** It is one review of the whole open set --
sixteen pull requests across four repositories -- so the set can be approved
together and land in order. Once two servers are started, the loop it delivers
is spoken from end to end: nothing is typed. [`the-voice-loop.md`](the-voice-loop.md) is the
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
| `joe` | `b5aefd8` | #23, #24 |
| `qmcp` | `f0e679b` | #54, #55, #56, #58, then the stack #60, #61, #62, #63, #64, #65 |
| `qm` | moves with #135 | #134, #135 |

**The demonstration** is `qmcp`'s `docs/voice-loop-demo.md`, run from a `qmcp`
checkout of the demo branch. Three tiers, each adding one real thing:

1. **Nothing real** -- `uv run qmcp cookbook voice`, `uv run qmcp cookbook
   instruct`, `uv run qmcp cookbook instruct --runtime scripted`, `uv run qmcp
   cookbook converse`. No hardware, no model, nothing spent; each prints `[ok]`
   per case. The last is a whole spoken session with every take scripted.
2. **The local model** -- `uv run qmcp cookbook instruct --runtime local`.
   Two spoken instructions in one project on the model this server stands up:
   the second gives no clone, asks about "that file", and is answered only
   because qmcp remembered the clone and handed the model what the first
   instruction found. Continuity comes from qmcp, not the model.
3. **A person at the microphone: two commands, then speech** -- `uv run joe
   dev` from `joe`'s demo branch and `uv run qmcp serve --converse --runtime
   local` from `qmcp`'s. qmcp says it is ready and asks what should be done; an
   instruction is read back and recorded on "record", consent is asked aloud and
   given with "approve", the local model reads the project, the answer is said
   back, and "stop listening" ends it. No person has run this tier; it is the
   review's one live step. The same session has run end to end with the server
   started that way and every take scripted (§6).

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
| **`qmcp` #65**, draft on #64 | -- | one standing spoken conversation, started by `serve --converse` | the words it listens for (`STOP`, `DONE`, `MORE`), the waiting questions asked before each instruction, the clone found by name beside this checkout, the conversation holding the voice tracker so the page's buttons answer that one is running, and a stalled model call recovered once by unloading the model (§3, decisions 5 and 6). |
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
5. **What a standing conversation keeps.** It listens take after take while
   it runs, and `joe` writes every take to `Data/Voice` as
   `capture_<timestamp>.wav` and keeps it. So everything said near the
   microphone while the conversation runs stays on disk until deleted. A
   retention rule -- delete a take once transcribed, or keep a few -- is
   `joe`'s to decide, before the conversation is left running.
6. **A wake word by default, or not.** Without `--wake`, every utterance the
   microphone hears is read back before anything is recorded, and nothing runs
   without "approve"; with it, an instruction must begin with the word.
7. **The design-review consent request** (`design-review-qm-audit-2026-09-27`)
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
- **No person has spoken to it.** Every take so far was scripted, on `vox`'s
  deterministic engine or a scripted engine on the port `qmcp serve --converse`
  was given. Tier 3 with a microphone is unrun; whether whisper hears "record",
  "approve" and "stop listening" reliably in a real room is unmeasured.
- **Background speech is read back.** Without a wake word, talk in the room
  becomes a read-back question; nothing is recorded without "record" and
  nothing runs without "approve", but the conversation will interrupt.
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
   then #61, #62, #63, #64 and #65, each retargeted onto `main` as the one
   beneath it lands.
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
  45 passed; `npm run build` built, leaving the tree clean. Its head since,
  `b5aefd8`, adds a README paragraph only.
- **`qmcp` at `d239251`:** `uv run pytest -q` 1139 passed, 11 skipped;
  `cookbook voice` 5 of 5; `cookbook instruct` 4 of 4 and 2 of 2 loops;
  `cookbook instruct --runtime scripted` and `--runtime local` both showed
  continuity, exit 0.
- **`qmcp` at `320b0d4`, with #65:** `uv run pytest -q` 1171 passed, 11
  skipped; `cookbook converse` one session `[ok]`. End to end, by a script:
  `qmcp serve --converse --runtime local --clones <the workspace>` started as a
  person starts it, speech written to files rather than played, an agent's
  question put on the queue, then a scripted speech engine started on the port
  the server was told -- and nothing else sent. At `f0e679b`, with the stall
  recovery, two such runs on the local model each ended with exit 0, the
  question answered `approve` by `vox`, two instructions done, the second in
  the remembered clone carrying the first. The seed workflow runner under the system interpreter:
  all 11 executed steps passed. `uv run qmcp preflight` at the head before
  #64 merged: 9 of 10, the REUSE step red for the reason in §4.
- **`qm`, the demo branch built from `main`, #134 at `d793ce5` and #135 at
  `0fc3fb4`:** `uv run --extra preflight qm preflight`, all 42 executed steps
  passed. #135's branch alone at `0fc3fb4`: 43 of 43, after a first run read the
  signature check red on a commit the host had not yet received.
- **Hosted:** every pull request in §2 green at its head when this page was
  written; on a demo branch only `qmcp`'s submodule check runs, and passed.

## 7. What none of this authorises

Merging, retargeting, deleting a branch, ratifying a record and cutting a tag
are each a person's. The pull requests are the audit record; this page is the
review of them.
