# Handoff — landing the voice set, paused at joe #33 for manual testing

**Stamped 2026-10-15.** `vox` `main` at `1721e6f`; `qmcp` `main` at
`df42315`; `joe` `main` at `d72b65b`; `qm` `main` at `df1cb51`. Every figure
on this page was true at those commits and nowhere else. Re-derive each one
with `gh` before acting on it.

[`hil-review-2026-10-04.md`](hil-review-2026-10-04.md) is the review of the
set and §5 there is the order it lands in;
[`the-voice-loop.md`](the-voice-loop.md) is the loop itself. This page is how
far that order has got, what is left, and how each step was done. Delete it
when the set and the steps after it have landed.

---

## 1. Decisions in force

1. **The set is approved** (the review page's decision 1) and lands in §5
   order: `vox`, `qmcp`, `joe`, `qm`.
2. **A person clicks every merge.** Each pull request is prepared, shown, and
   its merge asked for, one at a time. `uv run qm merge --repo <owner/name>
   --pr <n> --yes` merges; the host's merge button is not used.
3. **`joe` #24 (README) and #25 (cookbook) stay closed.** Their content is on
   `joe`'s `demo/voice-loop-2026-10-04` only. It returns as one new pull
   request per topic, cut from `joe`'s `main` after #34 lands, stating facts
   only.
4. **Decided 2026-10-13, for the rest of the landing:** where merging `main`
   into a `qmcp` stack pull request leaves #58's open question
   (`VoiceApprovalLoop._ask_open`) short of a claim that pull request's body
   or documents make, the claim is made true in code on that pull request --
   one commit, its tests, each mutation seen red -- and the overview says so.
   Applied on #68, #73 and #74.
5. **The landing pauses at `joe` #33** until a person has tested it by hand.

## 2. What has landed

| Repo | Pull requests, in the order merged | `main` after |
|---|---|---|
| `vox` | #10, #11, #12, #13, #14, #15, #9 | `1721e6f` |
| `qmcp` | #54, #55, #56, #58, #60, #61 to #76, #77, #78, #79, #80, #81, #82, #83, #84 | `df42315` |
| `joe` | #23, #26, #27, #28, #29, #30, #31, #32 | `d72b65b` |
| `qm` | none of the set | `df1cb51` |

`vox`'s merge commits, which `qmcp`'s pins name: #10 `eec9a2d`, #11
`c9dc0fa`, #12 `2795756`, #13 `aa57cff`, #14 `c0b9b18`. `qmcp`'s
`vendor/vox` is at `c0b9b18`; `vox`'s `main` is two documentation merges past
it (#15, #9).

Beyond the routine in §6, these landed as commits made during the landing,
each stated in its pull request's body:

- `qmcp` #60, #68, #69, #70, #73: `vendor/vox` moved from a `vox` branch head
  to that branch's merge commit. Each merge commit's tree equals the head it
  replaced (`git diff <head> <merge>` empty in `vox`).
- `qmcp` #68: the open question's read-back is hinted, offered as options and
  said again on "repeat" (decision 4).
- `qmcp` #72: #58's tests and the voice check brought to #72's grammar
  ("Agree or again?", "Noted."), as the demo branch had them.
- `qmcp` #73: the open question, its read-back and their re-asks are said
  through `ask_over` (decision 4).
- `qmcp` #74: the open question reads `agree`, `again` and their aliases from
  `vocabulary.toml`; `answer.agree` and `answer.again` describe what was read
  back rather than an instruction alone (decision 4).
- `vox` #9: `HANDOFF.md` restamped, with what importing `vox` loads and what
  `vox doctor` reports stated as the code has them.

## 3. What is left, in order

### `joe` — paused here

| Pull request | State at the stamp | Done when |
|---|---|---|
| #33, the transcript lane | ready, base `main`, head `c51f8f3`, five checks green, `CLEAN` | tested by hand, then merged by `qm merge` |
| #34, `joe`'s timeless text | draft, stacked on #33's branch | `main` merged in, its body's Branch block and stacking line rewritten, checks green, ready, merged |
| README | not opened | one pull request from `joe`'s `main` after #34, carrying the demo branch's README content as facts |
| cookbook | not opened | the same, for the cookbook |

The host refused to merge `main` into #27 and #32 and they were merged by
hand (§6, step 3); #34 may need the same.

What `main` holds to test: the whole loop except #33's transcript lane on the
visualiser and #34's documentation. `qmcp`'s `docs/voice-loop-demo.md` is the
onboarding and the three tiers -- nothing real, the local model, a person at
the microphone.

### `qm` — independent of `joe`, and can proceed in parallel

§5 order: #134, then #135; #136, then #140 and #141, each retargeted onto
`main`; #137, then #142.

| Pull request | State at the stamp |
|---|---|
| #134 | ready, base `main`, `CLEAN`, head `77777bd` |
| #135 | ready, base `main`, `CLEAN`, head `e031df2`; this page's pull request and #159 are stacked on it |
| #136 | ready, base `main`, `CLEAN`, head `1e5961f` |
| #140, #141 | drafts, based on #136's branch |
| #137 | ready, base `main`, `CLEAN`, head `ace793b` |
| #142 | draft, based on #137's branch; #160 is stacked on it |

The `slot` check was red on #134 and #135 while #139 was ready and stacked;
#139 is a draft and both read `CLEAN` at the stamp. Read the `slot` check by
name before merging either. `qmcp` #83 and #84 cite the record #136 adds and
the retrospectives #137 and #142 carry.

### After the set (review page §5)

- `qm` #134 reaches `qmcp` through a governance pin bump (`qmcp`'s
  `governance/qm` is at `235708c`, on `project/qmcp`); the bump retires the
  `AGENTS.md` paragraph `qmcp` #56 added and copies `qm` #140's three seed
  workflows again.
- Phase 10's boxes are ticked on `qmcp`'s `docs/ROADMAP.md`.
- #58's and #61's read-back helpers become one. Decision 4 has already given
  the open question the instruction read-back's hint, options, repeat,
  `ask_over` and vocabulary. Left: its wording ("I heard: ...", "I didn't
  hear anything.") against #72's ("Heard ...", "Didn't catch that."), and
  one helper rather than the two parallel loops in
  `qmcp/integrations/voice/adapter.py` and `qmcp/instructions/dialog.py`.
- `qmcp`'s `docs/voice-loop-next-phases.md` (#77) lists persistent vocabulary
  authoring as Phase 4; `qmcp` #81 built part of it. The plan claims no phase
  underway and dates its baseline to the demo branch at `5c65815`.
- The demo branches are deleted by a person: `demo/voice-loop-2026-10-04` in
  `vox`, `qmcp`, `joe` and `qm`, and `joe`'s branches that share commits with
  the set and carry no open pull request (`check_pr_base.py --base main
  --head <branch>` lists them).
- `qmcp`'s `vendor/vox` can move to `vox`'s `main` to take #15 and #9.

## 4. Blocked on a person

- **`joe` #33's merge**, on the manual test.
- **Two decisions carried from the 2026-09-27 review page**, which this page
  retires:
  - whether `joe` carries the corpus -- at the stamp it has no
    `governance/qm` submodule, so no gate, slot check or session tooling
    reaches it, and it deploys to Pages on every push to `main`;
  - what the torch subtree is worth -- `openai-whisper` is a core dependency
    of `joe` at the stamp, with no optional `voice` extra.

  The third, which lockfile `joe` keeps, is settled by the tree: `main`
  carries `uv.lock` alone.
- **The review page's §3 decisions**, not re-read for this page.
- **Where a decision is recorded.** No location in the repositories is
  chosen; decisions 1 to 5 above are stated here and go when this page does.

## 5. Not verified

- Tiers 2 and 3 of the demonstration -- the local model, a microphone -- were
  not run on any `main` during the landing.
- Pull requests whose `main` the host merged in were checked by the hosted
  workflows only: `vox` #12 to #15; `qmcp` #54 to #58, #61 to #67, #71, #75
  to #81, #83, #84; `joe` #23, #26, #28 to #31, #33. Those merged by hand were also run locally
  (§6, step 4): `qmcp` #60, #68, #69, #70, #72, #73, #74, #82; `joe` #27,
  #32; `vox` #9.
- The other pages in this directory were not swept for landed work; only
  this page, the 2026-09-27 page and their links were.

## 6. How each step was done

1. **Merge.** `uv run qm merge --repo <owner/name> --pr <n> --yes` from the
   corpus clone, then `gh pr view <n> --json state,mergeCommit`. It retargets
   the pull requests stacked on the merged one before deleting its branch.
   `joe` deletes head branches on merge itself, so there it reports "not
   deleted", or "could not be retargeted ... left in place", after the host
   has already retargeted; read the next pull request's base rather than the
   message.
2. **Bring the next one level.** `gh api -X PUT
   repos/<owner/name>/pulls/<n>/update-branch`, then wait for the head to
   move.
3. **When the host refuses** ("merge conflict between base and head"), merge
   `origin/main` in a worktree beside the clone (`<clone>.worktrees/<slug>`).
   The demo branch's merge of the same two pull requests is the reference
   resolution; compare each resolved file with it. A host refusal can come
   from several merge bases rather than a conflict: `qmcp` #82 had three, and
   git merged it cleanly.
4. **A `vox` pin.** A `qmcp` pull request that pins `vendor/vox` at a `vox`
   branch head gets one commit moving it to that branch's merge commit
   (`git update-index --cacheinfo 160000,<merge>,vendor/vox`); merging
   `main` then conflicts on the pin, and the merge commit is the resolution.
5. **Run the checks locally** for anything merged by hand. `qmcp`: `git
   submodule update --init`, `uv sync --all-extras`, then `python
   governance/qm/project-seed/ci/run_workflows_locally.py --event
   pull_request --base-ref origin/main` from Git Bash -- under a shell whose
   `bash` is the WSL launcher every step fails before it runs, and an
   interpreter without `pip` first on `PATH` turns `Install REUSE` red.
   `joe` has no governance submodule: `uv run pytest tests/`, `npx
   playwright test`, `npm run build`.
6. **Rewrite the body.** The Branch block from `check_pr_base.py --base main
   --head <branch>`; the "Stacked on #N" line replaced by what each commit
   is; a Verification section at the new head above the earlier ones. The
   body speaks as the contributor: `check_pr_voice.py --body-file`.
7. **Ready.** Wait for every check on the new head, `gh pr ready`, and in
   `vox` and `qmcp` wait for the `slot` run that follows. A `slot` run
   cancelled by a newer one on the same head is superseded, not failed.

## 7. Local state at the stamp

Nothing is unpushed. No worktree made for the landing is left.

- `vox`: the clone on `main` at `1721e6f`; `vox.worktrees/demo` on the demo
  branch.
- `qmcp`: the clone on `demo/voice-loop-2026-10-04`, and
  `qmcp.worktrees/integration` detached at `72b6f82`; neither was made by the
  landing.
- `joe`: the clone on `demo/voice-loop-2026-10-04`.
- `qm`: the clone on #136's branch, clean; `qm.worktrees/demo` on the demo
  branch, and this page's two worktrees until their pull requests merge.
