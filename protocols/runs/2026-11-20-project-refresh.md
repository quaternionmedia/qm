# Project refresh — 2026-11-20, qmetronome

**Protocol** `protocols/project-refresh.md`. **First run**, and the run the
protocol was written from. `qm` at `02fa287`; `qmetronome` at `1abf5e9`.

| | |
|---|---|
| **Operator** | Peter Kagstrom |
| **Machine** | Windows 11, JDK 21, Android SDK platform 35 |
| **Tools** | Claude Fable 5.2 |

Everything below was true at the commits named.

---

## 1. What was behind

`uv run qm project qmetronome`, before any change: 18 behind, 0 unknown.

- **Corpus.** `project/qmetronome` at `364ac3c` was 967 commits behind `main`.
  `adr/TEMPLATE.md` differed from the seed's, and `adr/README.md` carried the
  seed placeholder.
- **Project.** `governance/qm` pinned `5f910b1`, 23 commits behind the branch
  tip. Two seed workflows differed from the seed's files and six were absent.
  The governance section of `AGENTS.md` differed from the seed's, and
  `CLAUDE.md` was a symlink where the seed carries a one-line import.
- **Host.** Two pull requests open in qmetronome, #13 and #15, and one here
  against `project/qmetronome`, #153.

## 2. The corpus side

quaternionmedia/qm#333, merged as `2ac0777` with a merge commit. The merge of
`main` was clean. A second commit made `adr/TEMPLATE.md` the seed's file and
rebuilt `adr/README.md` from the seed's page, with the project's name and an
index listing each draft by its whole title. The ADR lint named four drafts as
unlisted before the index was rewritten and is clean after.

## 3. The project's side

- **quaternionmedia/qmetronome#15**, the pin. It was open at `364ac3c`; a
  second commit moves `governance/qm` to `2ac0777`. Open, ready.
- **quaternionmedia/qmetronome#17**, the copies, stacked on #15. Open, a
  draft.
- **quaternionmedia/qmetronome#16**, two lines of `docs/onboarding.md` that
  the leak check reads as a home directory with an account in it. Open, ready.

qmetronome's `AGENTS.md` on its default branch has an agent open a pull request
and leave the merge to a person, so none of the three was merged in the run.

## 4. The tests

`./gradlew assembleDebug testDebugUnitTest --console=plain`.

- On `main` at `1abf5e9`: `BUILD SUCCESSFUL`, 322 passed, none failed, none
  skipped.
- On #17's head at `2d8553f`, as the `ci.yml` step of the local workflow run:
  `BUILD SUCCESSFUL`.

Each run rewrote three files under `docs/images/generated/videos/`, the GIFs
the suite records, and nothing else. The recordings are not byte-stable; the
three were restored and are not part of any pull request above.

## 5. The policies

`run_workflows_locally.py --event pull_request --base-ref main` in qmetronome
at `2d8553f`. The runner at that pin stops after the ADR lint on an expression
the seed's `adr-lint.yml` uses; quaternionmedia/qm#334 resolves it, and the run
used the runner from that branch.

17 steps ran, 15 passed, 2 failed, and `tag-claims.yml` was skipped as not
triggered by a pull request.

| Gate | Result |
|---|---|
| ADR lint, placeholders, vendor names | pass |
| Glyph SDK import boundary; build and test | pass |
| Stacked pull requests are drafts; voice of the body | pass |
| Commit signatures | pass |
| Submodule refs | pass |
| Timeless text | pass |
| Leak check | fail: the two onboarding lines #16 rewrites |
| REUSE lint | fail: 2 of 290 files carry licensing information, and `Apache-2.0` is named by the Gradle wrapper with no text under `LICENSES/` |
| Tag claims | skipped |

`uv run qm policies` names three policies with no detector. Read by hand for
the commits and pull requests of this run: no `-c` passed to git, nothing
pushed to a shared branch outside a pull request, and no commit carrying a
co-author trailer.

## 6. The second reading

`uv run qm project qmetronome`, after: 16 behind, 0 unknown. The corpus side
is current on all three lines. Every line on the project's side is still
behind, because the default branch has not moved: #15 and #17 carry the
changes.

## Left open

- **#15, #16 and #17 in qmetronome** wait on a person to merge them, in that
  order, with `main` merged into #17 after #16 so its leak check reads the
  rewritten lines.
- **qmetronome's licensing pass.** The REUSE lint blocks #17 until the
  repository states a licence for every file: a `REUSE.toml`, the licence texts
  under `LICENSES/`, and a decision on the files that are not the project's
  own, the Gradle wrapper and the Glyph Matrix SDK among them.
- **quaternionmedia/qm#153** rewrites the line of `adr/README.md` that #333
  replaced with a list, so it needs `project/qmetronome` merged into it.
- **quaternionmedia/qmetronome#13** is a draft from an automation account,
  green on its own checks and untouched since August. It was not read in the
  run.
- **`uv run qm docs generate`** was not run. The status documents carry
  qmetronome as of their own `generated_at` until the project's pull requests
  merge.
- **Tag claims** were not exercised: the workflow runs on a tag push.
