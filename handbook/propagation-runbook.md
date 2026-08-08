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
```

To ask whether propagation has *ever* run, do not just look for merge commits:
a project branch merging its own feature branch produces one too, and reading
that as propagation is a false all-clear. A propagation merge is one with a
parent that is an ancestor of `main`:

```sh
for c in $(git rev-list --merges origin/main..origin/project/<name>); do
  for parent in $(git rev-list --parents -n1 "$c" | cut -d' ' -f2-); do
    git merge-base --is-ancestor "$parent" origin/main       && git log -1 --format='propagation: %h %ci %s' "$c"
  done
done
```

1. **Dry-run the merge before choosing a PR shape.** The shape depends on
   whether it conflicts:

   ```sh
   git checkout -B tmp/dry origin/project/<name>
   git merge --no-commit --no-ff origin/main
   git diff --name-only --diff-filter=U
   git merge --abort; git checkout -; git branch -D tmp/dry
   ```

   **Clean:** open a PR with base `project/<name>` and head `main`. That merge
   commit *is* the pin bump — the branch's ancestry is the pin, and there is no
   hash to hand-maintain.

   **Conflicted:** do *not* use `main` as the head. GitHub commits a conflict
   resolution to the head branch, so resolving in that PR would push to `main`,
   which `AGENTS.md` forbids. Use an intermediate branch instead:

   ```sh
   git checkout -b propagate/<name>-<date> origin/project/<name>
   git merge origin/main          # resolve here
   ```

   and open *that* into `project/<name>`.

   **Resolve toward identical content, not toward keeping both sides.** Where
   the conflict is org content the branch owned and `main` has since gained,
   take `main`'s version wholesale — `git checkout origin/main -- <path>`. Any
   resolution that leaves the two sides merely *equivalent* rather than
   *identical* conflicts again on the next propagation, because the same
   insertion arriving from two directions is not something git can reconcile.

   *Verify the steady state*, which is the step that catches this:

   ```sh
   git checkout -B tmp/next <your-branch> && git merge --no-commit --no-ff origin/main
   #   expect: Already up to date, or a clean merge. A conflict here means the
   #   resolution above kept both sides instead of converging them.
   git merge --abort; git checkout -; git branch -D tmp/next
   ```
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

**Look for the behaviour before looking for the filename.** A project that
adopted before the seed existed may have implemented the same thing its own
way, in which case the seed artifact is neither absent nor a stale copy — it
is a third state the naive check misses. qmetronome, the project the seed's
lint was generalized *from*, has no `.github/workflows/adr-lint.yml` at all:
its lint is an inline step inside `ci.yml`. Checking for the filename reports
"absent" and hides a divergent implementation that is actively running.

```sh
ls .github/workflows/                       # what exists, whatever it is named
grep -rn -i 'adr.lint\|adr_lint\|DRAFT-' .github/workflows/
```

Where you find one, replace it rather than adding beside it — two lints
disagreeing is worse than one that is out of date — and say so in the PR, so
the maintainer sees a behaviour change rather than a file addition. A pre-seed
implementation is usually the old single-check version: it will lack three of
the four checks, and it will not strip code spans, so it trips on any document
that quotes the banned list.

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

## When a project branch's history has been rewritten

Rewriting a `project/*` branch — re-signing, rebasing, renaming and force-
pushing — invalidates **every submodule pin that referenced the old commits**.
The trees are usually identical; only the identifiers change. That is enough:
a pin names a commit, not a tree.

The page tells you not to do it. This is what to do when it has already
happened, because it has:

1. **Find the consuming repos.** There is no index of them. Search the disk
   for `.gitmodules` naming this corpus, and treat the list as incomplete —
   a repo nobody has cloned here will not appear.
2. **Repoint each pin** at the equivalent commit on the live branch:

   ```sh
   git -C governance/qm fetch origin
   git -C governance/qm checkout -B <branch> origin/<branch>
   git add governance/qm && git commit
   ```

3. **Check the submodule's own remote before trusting the fetch.** A submodule
   populated from a filesystem path can pin commits that exist nowhere else,
   and everything resolves locally:

   ```sh
   git -C governance/qm remote get-url origin      # must be the canonical remote
   git config --get submodule.<path>.url           # the sync override, same rule
   ```

   Both must match `.gitmodules`. This is the mechanism that lets a broken pin
   be created in the first place, and the fork procedure's step 3 already warns
   about it — it is worth re-checking on any repo that has ever been set up by
   hand.
4. **Confirm with the check, not by eye** — `submodule-check.yml` answers
   exactly this question, and a repo that has been rewritten under it is the
   case it exists for.

**The first time this bit, the rewrite and the breakage had different
authors.** A branch was re-signed in the corpus to satisfy a signing rule;
`project/datum`'s consuming repository broke, silently, and stayed broken
until someone ran the check. Nothing connected the two events. If you rewrite
a pinned branch, walking the consumers is part of the same task, not a
follow-up.

## What the first run of this found

Exercised end to end against qmetronome on 2026-08-08 — the branch furthest
behind, and the only one holding org content. Six findings, none of which this
page predicted before it was run:

| Finding | Where |
|---|---|
| Propagation had never run on any branch, and the naive "any merge" check said otherwise | Part A |
| A conflicted propagation cannot use `main` as the PR head | Part A |
| Resolving by keeping both sides made the *next* propagation conflict too | Part A |
| The submodule was wired correctly, pinned to the right branch | Part B |
| No `AGENTS.md`, `CLAUDE.md` or `.vscode/` existed in the project repo at all — fork step 5 had never been done | Part B |
| The ADR lint existed, but inline in `ci.yml` running the old single-check version, so a filename check reported "absent" | Part B |

The last two are the general lesson: **a project can be correctly pinned and
still be missing most of what adoption means.** The submodule is the cheap
part. The copied artifacts are where adoption actually lives, and nothing
reports their absence.

## Part C — what to do about what you find

| Finding | Action |
|---|---|
| Branch behind `main` | Part A. Ratifications reaching projects is the whole point of the model |
| `adr/TEMPLATE.md` differs from the seed | Explicit commit. No merge will do it |
| Literal `project/<name>` in `adr/README.md` | Substitute. It sends its reader to a branch that does not exist |
| Org content on a `project/*` branch | Lift to `main` first, then continue |
| Pointer files not mode `120000` | Recreate as symlink objects, per Part B |
| Seed artifacts absent from the project repo entirely | Fork steps 4 and 5 were never done. Do them now — the pin alone is not adoption |
| A divergent in-project implementation of a seed mechanism | Replace it, do not add beside it, and flag the behaviour change in the PR |
| A record's Status or number needs changing | **Not yours.** Draft it and hand it back; a human ratifies |

## What this page does not authorise

Ratification, branch deletion, force-pushing a `project/*` branch, and
rewriting any branch a submodule pins. Each of those is a human decision, and
a `project/*` tip is a downstream repository's pinned commit — rewriting it
breaks a build somewhere you cannot see.
