# Handoff — what is waiting on a person, 2026-09-27

**Stamped 2026-09-27, restamped after the merges below.** `qm` `main` at
`d1aca4f`; `vox` `main` at `4b2e64d`; `joe` `main` at `6e1ad16`; `qmcp`
`main` at `77b73ca`; `dossier` `main` at `b21ce32`. Every figure was true at those commits and nowhere else.

**Nothing on this page is a task.** It is the list of decisions after the
2026-09-27 session, in the order they want deciding, with what to look at
and what to distrust. [`the-voice-loop.md`](the-voice-loop.md) is the state;
this is the queue. Delete this page when its work lands.

---

## 1. The pull requests — all four merged on 2026-09-27

Each passed its gates and a docs/testing review, then merged: `qmcp` #38
at `77b73ca`, `vox` #5 at `4b2e64d`, `dossier` #58 at `b21ce32`, `qm`
#122 at `cacaed8`. The *look at* column stays for a reader auditing them.

| | Checks | What it is | Look at |
|---|---|---|---|
| **`qmcp` #38** | 7/7 | answering the HITL queue by voice; vox pinned at `d54a7f7` | `choose_option` — it reads a request's `options` rather than taking `options[0]` as the approval, because a request carrying `["reject", "approve"]` recorded a spoken "yes" as `reject`. Every prior test used the conventional order. |
| **`vox` #5** | — | the handoff replaced with the surface that exists | it is 100 lines where the old one was 256, and the old one named classes that had been gone since `#3`. |
| **`dossier` #58** | 7/7 | `dossier dev doctor`, the three-process preflight | the database section. It fails when `DOSSIER_DATABASE_URL` is unset and a real database is present, which is a deliberate refusal to run rather than a warning. |
| **`qm` #122** | 10/10 | the handoff, the retrospective, and vox's roster entry | the retrospective's §9 and §12: a private name reaching a public repository through a gate no workflow runs, and a recorded artifact that churned on one platform while CI saw nothing. |

**`qmcp` #38 waited on a mechanical reason, not a judgement one.** Its
checks failed identically from 2026-09-22 until `vox` was made public,
and it merged with the rest on 2026-09-27.

## 2. Decisions nobody has taken

Ordered by what they block.

1. **~~Whether `vox` joins the roster~~ — decided 2026-09-27.** It is in
   `ci/workspace.yaml` and `families.json` as a member of `core`, placed by
   the border test in
   `records/DRAFT-a-family-is-bordered-by-what-it-drives.md` §2: what its
   output acts on is the corpus's own tooling, not the sound it emits and
   not the family of the engine it talks to. The placement is the part
   worth a second look — `instruments` drives *the sound*, and vox
   synthesizes, which §2 says is the wrong test.
2. **Whether `joe` should carry the corpus.** Without a `governance/qm`
   submodule, none of the gates, the slot check or `/cowork` reach it — and
   it is now a public repository that deploys to GitHub Pages on every push
   to `main`.
3. **What the torch subtree is worth.** `joe`'s lock grew from 82 packages
   to 113 when speech landed, and the 31 added are torch, triton and CUDA —
   the subtree `00d8077` had removed as unused. They are load-bearing now.
   A lean default install and a working `joe voice` can both be had through
   an optional `voice` extra; that is a decision, not a fix.
4. **~~Whether `vox` and `joe` carry license files~~ — decided
   2026-09-27.** `vox` is Apache-2.0 and `joe` is MIT, the holder named
   per `records/DRAFT-outbound-licensing.md` §0; `vox` #6 and `joe` #12
   carry the files that make each repository's existing metadata claim a
   real grant.
5. **Which lockfile `joe` keeps.** `pdm.lock` (2024-12-29), `uv.lock`
   (current) and `requirements.txt` all describe its Python dependencies,
   and the third omits `httpx` while `pyproject.toml` declares it.

## 3. What to distrust in what this session produced

Stated because each was believed before it was checked.

- **Three claims were wrong on the first reading and corrected only by
  running a second command.** A branch conflict attributed to PR stacking
  when the base had moved; a filename-aliasing probe run without the target
  file present, which returned the reassuring answer; a local gate run
  reported as failed when it was buffered behind a pipe and still running.
- **Two guards written this session were wrong on their first version.**
  The wheel check passed against deliberately broken packaging, because
  setuptools stages into `build/` and `*.egg-info/` carries the package
  list forward. The audio range guard used `peak > 1.5`, and every
  comparison with NaN is False, so a device returning NaN walked through
  and printed `peak nan` as a result. Both were found by breaking them on
  purpose; neither was found by reading.
- **`AGENTS.md` in `dossier` overstated its own hazard.** It said the suite
  destroys the operator's data; the purge is by pattern and 0 of 117 rows
  matched. Corrected there, and worth the general caution: a warning that
  overstates its case is one people learn to skip.
- **The handoff inherited from the previous session said "test suites are
  green in all three"**, which was true locally and silent about CI, and
  CI had been red for five days.

## 4. Git hygiene, as reviewed

A scan of every file changed on any branch this session — 103 files across
five repositories — against home paths, scratch paths, credentials and
private repository names:

- **No home path, scratch path or credential** in any committed file.
- **Every occurrence of a personal name is authorship** — a package author
  field, a perspective's `Author` row — which the corpus requires rather
  than forbids.
- **`uv run qm leaks` and `uv run qm private-names --source host --strict`
  are both clean** against 453 tracked files.
- **No database is tracked.** `dossier.db` (8.5 MB, 117 real rows) and its
  backups are ignored, as are every test artifact this session wrote:
  `Data/`, `build/`, `dist/`, `*.egg-info/`.
- **Line endings are uniformly LF as stored**, across all 103 files.
- **Every commit authored here carries a good signature.** Merge commits
  are signed by the forge's own key, with `GitHub <noreply@github.com>` as
  committer, which is what an API merge records.
- **No commit message names a model or vendor**, and none carries a
  co-author trailer.
- **`joe`'s published site is three files** — one HTML, one JS, one CSS —
  and carries nothing personal.
- **Committed notebook outputs are three lines of stream text**, no data
  and no images.

One item is for another session rather than this one: a commit on
`origin/adr/firmware-toolchain-seam` carries `Tools: Claude Code drafted
the wording under review.` in its body. That branch is being actively
rewritten and was renamed mid-session, so nothing here touched it.

## 5. What none of this authorises

Ratifying anything. Merging to `main` in this corpus. Deleting a branch.
Force-pushing. Placing `joe` in a family or giving it the corpus, which is
§2's second decision and a person's to make — `vox`'s placement was made on
2026-09-27 and is recorded rather than assumed.
