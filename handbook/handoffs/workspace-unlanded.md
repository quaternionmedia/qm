# Handoff — Local Work Across the Workspace That No Pull Request Carries

**Goal.** Make visible what is sitting on one workstation and in no pull
request. Not to land it — most of it is not this page's to land — but to stop
it being invisible, which is the state it was in when this survey was taken.

**Why.** Six sessions ran across six repositories on 2026-08-09 and 2026-08-10.
A handoff describes what is pushed; a workstation holds what is not. The async
contract's clause about declaring a dirty tree covers a session that *finds*
one. It does not cover the reverse — a workspace quietly accumulating committed
work that no pull request references, which is what this is.

*Stamped 2026-08-10, surveyed by `git for-each-ref` and `gh pr list` per
repository. Every count below is true at that moment and nowhere else.
Re-derive before acting: `git status --porcelain` and
`git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads`.*

---

## Two that want a decision before anything else

**apothecary has a commit on `main`.** `2409244`, *"Adopt the QM constitution:
submodule, ADR process, CI gates, IDE discovery"*, one commit ahead of
`origin/main`, unpushed. The constitution forbids committing to `main` in any
repository that has adopted it, and pushing this would be pushing `main`. It is
real work and it is on the wrong branch. Moving it to a branch is a history
operation on somebody else's checkout, so it is not done here.

**qmetronome's governance pointer files are missing from disk.**
`.github/copilot-instructions.md` and `CLAUDE.md` are mode `120000` in the
index and absent from the working tree, so `git status` reports them as
deletions. This is the Windows symlink materialisation problem, not a decision
anybody made — and a `git add -A` on that branch would commit the deletion of
governance discovery from the project. The repair does not touch content:

```sh
git -C <qmetronome> config core.symlinks true
git -C <qmetronome> checkout -- .github/copilot-instructions.md CLAUDE.md
```

Left alone here because another session may be working in that tree.

## The survey

| Repo | On | Dirty | Committed but unpushed | Human PRs |
|---|---|---|---|---|
| **qm** | `evolve/ci-tooling-fixes` | 0 | none — pushed to #36 | 9 |
| **dossier** | `governance/status-view` | 0 | `governance/adopt-corpus` (ancestor of #10); `wip/delta-entity-type-local` (deliberate) | 1 |
| **alfred** | `release/0.3.0` | 7 | `governance/adopt` +7 vs `main`; four branches with no upstream | 1 |
| **apothecary** | `feature/fractal-viewer-scale-and-overlays` | 0 | `main` +1 (see above); `governance/integration` +2 | 4 |
| **datum** | `governance/propagate-2026-08-08` | 0 | that branch +1 vs its own remote, and it has an open PR | 1 |
| **rad** | `evolve/rad-v1` | 0 | +7 vs its own remote, and it has an open PR | 1 |
| **codecartographer** | `feat/rad-integration` | 1 (`docs/qm` pointer) | four branches with no upstream | 1 |
| **datafactorio** | `main` | 0 | `feat/modular-architecture` +1 | 0 |
| **qmetronome** | `governance/wire-ide-and-adr-lint` | 2 (see above) | none | 1 |
| **qmcp** | `feat/pydantic-ai-integration-docs` | 30 | none | 0 |
| **factorio-server** | `factorio-server-v1` | 1 (untracked workspace file) | none | 0 |
| **factorio-sysops** | `main` | 0 | none | 0 |
| **benchmark** | `feature/mobile-ux-polish` | 0 | none | 1 |

**`datum` and `rad` are the two clean cases.** Each has commits on a branch that
already has an open pull request, on its own remote-tracking branch, with a
clean tree. Pushing either is ordinary pull request maintenance and would add
those commits to a review that already exists. They were not pushed here
because the commits are another session's and nothing establishes whether they
were held back deliberately — which is a question, not an obstacle.

**`qmcp` has thirty modified files and no pull request at all**, on
`feat/pydantic-ai-integration-docs`. Nothing in the repository says what that
work is or whether it is finished.

## What this page did not do, and why

Local-only was relaxed on 2026-08-10 **for pull request maintenance**. That
covers pushing to a pull request that already exists. It does not cover:

- committing another session's uncommitted work, which would put a message on
  changes whose intent is not recorded anywhere
- moving a commit off `main`, which rewrites history in a checkout this session
  does not own
- opening pull requests for branches that have none — `qmcp`, `datafactorio`,
  and four `codecartographer` branches would each need one, and the rule is one
  open pull request per repository per contributor

Two repositories also hold stray empty `dossier.db` files from `dossier`
commands run in the wrong directory. Those were deleted; the command now prints
a note naming the store path, because per-directory stores that disagree is a
confusing failure with no error message.

## The order to take these in

1. Decide apothecary's `main` commit. Everything else in that repository is
   downstream of it, and it is the only item here that conflicts with a rule
   rather than merely waiting.
2. Repair qmetronome's two pointer files. One command, no content decision.
3. Push `datum` and `rad` if those commits were not held back on purpose.
4. Everything else is a scoping conversation, not a mechanical step.

## What none of this authorises

Committing work whose intent is not recorded. Rewriting history in a checkout
this session does not own. Pushing `main` anywhere, for any reason. Opening a
second pull request in a repository that already holds one.
