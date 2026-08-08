# Handbook — Propagating Org Changes into an Adopted Project

**Routing.** Operational procedure, not a decision record: it weighs no
alternatives and creates no constraint a project could violate. The decisions
it carries out live in *Decision-record discipline* and *IDE-integrated
governance discovery*; this page is how a person or an agent executes them.
If it ever needs adjudicable teeth — a dispute about whether a project is
current — it is promoted to a record and this page becomes a pointer.

**Audience.** A human or coding agent with no memory of the session that made
the org change. Assume nothing here was explained to you in conversation.

---

## The shape of the problem

An adopted project spans **two repositories**, and an org change can land in
either or both:

| Where | What lives there | How it updates |
|---|---|---|
| This repo, branch `project/<name>` | the project's own `adr/` | merge `main` into the branch |
| The project's own repo | `governance/qm` submodule, plus copies of `project-seed/ci/` and `project-seed/ide/` | bump the submodule pin, re-copy changed seed files |

Two failure modes follow from that split, and both have bitten:

- **A merge does not fix a copy.** `adr/TEMPLATE.md` and
  `project-seed/adr/TEMPLATE.md` are *different paths*. Git will never
  reconcile them, so a branch can be zero commits behind `main` and still
  carry a stale template. Same for everything copied out of
  `project-seed/ide/` into a project's own root.
- **Propagation runs one way.** `main` flows outward. Org-level content
  committed on a `project/*` branch is stranded there permanently — nothing
  carries it back. If you find any, lift it to `main` on a
  `perspective/*` or `evolve/*` branch before continuing.

---

## Part A — in this repo: bring `project/<name>` current

Open a pull request. Do not merge to a shared branch directly, and do not
merge your own work; see `AGENTS.md`.

```sh
git fetch --all --prune
git rev-list --count origin/project/<name>..origin/main     # how far behind
git log --merges origin/main..origin/project/<name>         # has propagation ever run?
```

1. **Open a PR with base `project/<name>` and head `main`.** That merge commit
   *is* the pin bump — the branch's ancestry is the pin, and there is no hash
   to hand-maintain.
2. **Merge it with a merge commit.** Not squash, not rebase. Rebasing
   rewrites the branch and breaks every submodule pin pointing at it.
3. **Refresh the copies, in a separate PR**, because step 1 cannot:

   ```sh
   git checkout -b fix/<name>-seed-refresh origin/project/<name>
   git show origin/main:project-seed/adr/TEMPLATE.md > adr/TEMPLATE.md
   grep -n 'project/<name>' adr/README.md    # a literal placeholder points nowhere
   ```

   *Verify:* `git diff --no-index` between the seed template and `adr/TEMPLATE.md`
   is empty, and no literal `<name>` survives.

**Expected conflicts:** none, on a branch that has only ever touched `adr/`.
A conflict outside `adr/` means org content was committed to this branch —
stop and lift it to `main` first.

---

## Part B — in the project's own repo: pick the change up

```sh
git submodule update --remote governance/qm     # tracks branch= in .gitmodules
git -C governance/qm log --oneline -1           # confirm the tip you expect
git add governance/qm && git commit             # the parent records an exact commit
```

Then re-copy whichever seed parts changed. Diff before copying — a project may
legitimately have edited the parts it owns.

- **`project-seed/ci/adr-lint.yml` → `.github/workflows/adr-lint.yml`**, verbatim.
  Only the workflow is copied; the checks run from inside the submodule, so a
  fix to the lint reaches every project on its next pin bump. If the project
  mounts the submodule anywhere other than `governance/qm`, set `QM_SUBMODULE`
  in that workflow — it is the only place the path appears.
- **`project-seed/ide/` → the project root**, recursively and
  **symlink-preserving** (`cp -a`, `cp -P`, `rsync -a`, or `git checkout`).
  The tree already mirrors the target layout, so nothing is renamed per file.
  Fill in project-specific commands *below* `AGENTS.md`'s marked line and
  leave the governance section above it alone, apart from replacing `<name>`.

**Then verify, rather than assuming the copy worked.** Every one of these has
failed silently in a real adoption:

```sh
# 1. The ignore file did not swallow what you just copied.
git check-ignore -v AGENTS.md CLAUDE.md .github/copilot-instructions.md \
  .vscode/settings.json .vscode/extensions.json
#    Any path that comes back matched would never have been committed.

# 2. The pointer files are still symlinks, not dereferenced copies.
git ls-files -s CLAUDE.md .github/copilot-instructions.md
#    Expect mode 120000. `cp -a` has been observed dereferencing these on at
#    least one Windows toolchain. If they are 100644, recreate them:
#      git hash-object -w --stdin <<< 'AGENTS.md'
#      git update-index --cacheinfo 120000,<sha>,CLAUDE.md

# 3. The lint runs, and against the right directory.
python governance/qm/project-seed/ci/adr_lint.py --records-dir governance/qm/adr
```

A step is done when its check passes, not when its command exits zero.

---

## Part C — what to do about what you find

| Finding | Action |
|---|---|
| Branch behind `main` | Part A. Ratifications reaching projects is the whole point of the model |
| `adr/TEMPLATE.md` differs from the seed | Explicit commit. No merge will do it |
| Literal `project/<name>` in `adr/README.md` | Substitute. It sends its reader to a branch that does not exist |
| Org content on a `project/*` branch | Lift to `main` first, then continue |
| Pointer files not mode `120000` | Recreate as symlink objects, per Part B |
| A record's Status or number needs changing | **Not yours.** Draft it and hand it back; a human ratifies |

## What this page does not authorise

Ratification, branch deletion, force-pushing a `project/*` branch, and
rewriting any branch a submodule pins. Each of those is a human decision, and
a `project/*` tip is a downstream repository's pinned commit — rewriting it
breaks a build somewhere you cannot see.
