# Three fields, and none of them is activity

**2026-08-19, evening.** The org's repositories, read from the host and from
this disk. Attributed, dated, binds nothing.

Tools: written with an AI coding assistant, reviewed and committed by a human.

## The question

Which repositories is anybody working on? `ci/workspace.yaml` answered it in
four comment headers, and a comment is not something a check can read. The
obvious upgrade is to compute the answer from the host, which offers three
plausible fields. All three are wrong, in three different ways, and the third
is wrong in a way that is easy to miss because it is *nearly* right.

## What was measured

One query, on 2026-08-19, against `quaternionmedia`:

```sh
gh api graphql -f query='{ organization(login:"quaternionmedia") {
  repositories(first:100, orderBy:{field:PUSHED_AT, direction:DESC}) {
    nodes { name pushedAt updatedAt
      defaultBranchRef { target { ... on Commit { committedDate } } } } } } }'
```

| repository | `pushedAt` | `updatedAt` | default branch's last commit |
|---|---|---|---|
| `carlos` | that day | 2025-08 | 2025-08 |
| `al-admin` | that day | 2023-07 | 2023-07 |
| `otto` | that day | 2023-07 | 2023-04 |
| `codecartographer` | 2026-08-11 | 2026-07-21 | 2026-07-21 |

**`updatedAt` is not a work signal.** It moves when anybody edits a description
or a topic, and it lags a real push — `codecartographer`'s is three weeks behind
its own `pushedAt`.

**`pushedAt` is not a work signal either**, and this is the one that would have
shipped. It moves on a push to *any* ref: a tag, a bot branch, a Pages deploy, a
sweep. Three repositories reported it within one hour of each other while their
default branches had last moved in 2025, 2023 and 2023. A classification built
on it calls a three-year-dormant repository active, confidently and every time.

**`defaultBranchRef.target.committedDate` is the closest cheap answer** and it is
still not the answer. It cannot see work on another branch, and it cannot see
work that never left a disk.

## The part the host cannot answer, and what it was hiding

So a second measurement, on the clones in this workspace:

```sh
git -C <clone> log --all --not --remotes --format=%H
```

with a guard in front of it, because that command is meaningless in a clone that
has never fetched — there, every commit is "on no remote". Asserting that
remote-tracking refs exist before trusting the count is the difference between
measuring the repository and measuring the checkout.

Four findings, each of which the host layer reports as nothing at all:

**A standard that exists on one disk.** `rad`'s local `evolve/rad-v1` is ahead of
the branch of the same name on the host, and carries
`adr/DRAFT-rad-host-integration-standard.md`. Verified absent from `main`,
`origin/main` and `origin/evolve/rad-v1` with `git ls-tree -r --name-only`.
Meanwhile `codecartographer/docs/llm/RAD_INTEGRATION_HANDOFF.md` is committed, in
a different repository, and opens by deferring to it: *"Where this page and the
standard disagree, the standard wins and this page is a bug."* One repository's
committed governance defers to a document nobody but this machine can read.

**A dormant host copy of an active repository.** `alfred` carries the largest
body of unpushed work in the workspace across several branches, a dirty tree,
and a modified `governance/qm` submodule pointer, while its `origin/main` last
moved in January 2024. Every host field agrees it is dead. Nothing on the host
can see that it is not.

**A release claim nobody can fetch.** `qmetronome` carries a `v0.0.25` tag whose
commits are on no remote. In a corpus where
`records/DRAFT-version-tags-are-claims.md` makes the tag one of two human gates,
that is a claim that cannot be checked by the party it is addressed to.

**Two governed repositories the roster denied.** Both carry a `project/<name>`
branch in the corpus, and both were absent from `ci/workspace.yaml`, so
`uv run qm inventory` listed them under *"the corpus cannot see these"* while the
corpus was propagating into them.

## Three defects in the measuring, found by measuring

Every one of these was the tool disagreeing with itself, and none of them
crashed.

**The corpus already had one roster loader, and this was the second.**
`ci/roster.py` exists because four generators broke at once when private
repositories became nameless entries; its docstring says so. `ci/inventory.py`
never adopted it and kept its own parser, which keyed on `name` and therefore
dropped every ref-only entry. The fix was to delete the duplicate, not to repair
it — and the first attempt repaired it, which is worth recording, because a
patched duplicate passes its tests and leaves the org one merge away from the
same breakage.

**A breakdown that did not add up to its own total.** The unpushed total came
from `--all --not --remotes`; the per-branch breakdown walked `refs/heads`. One
repository reported unpushed commits and listed no branch holding any of them —
they hung off a tag. Two figures from one function, quietly disagreeing. An
`unaccounted` row now reconciles them, and every instance it has found since was
a stash, which is also work at stake.

**A privacy test that matched its own documentation.** The new test asserted no
risk vocabulary reaches the committable file, scanning the whole document. It
failed against prose in the generator block that *names* the risk vocabulary in
order to say where it does not go. Scanning the rows instead is the fix. This is
the inert-check shape the corpus has shipped before, arriving in the suite whose
subject is exactly that.

**`patch-id` was tried as a discriminator and rejected.** The intent was to tell
merged-then-rebased work from genuinely unpushed work. This corpus's
seed-refresh commits are byte-identical to one another by construction, so it
matched one branch's work against an unrelated branch's and reported it landed.
A check that answers confidently and wrongly is worse than the ambiguity it
replaced. What replaced it is the ref's own upstream state, which is cheap and
says which of the benign readings applies.

## What this cost, and what it bought

The measurement was written twice: once from the host field that looked right,
and once from the two that actually answer. The second version is longer, needs
a clone to say anything about risk, and reports `unreadable` for repositories
nobody has cloned — which is the honest answer and reads as a gap.

Against that: the first version would have reported `carlos` as active because a
concurrent session pushed a branch to it, and `alfred` as dead while holding the
most at-risk work in the workspace. Both readings are confident, tidy, and
exactly backwards.

The general shape is one this corpus keeps meeting. **A field that correlates
with the question is not the question**, and the failure is silent because the
correlation holds for most rows. `pushedAt` is right about most repositories
here. It is wrong about the ones worth looking at.

## What remains unexplained

Three repositories showed `pushedAt` moving on a day their default branches had
not moved in years. For `carlos` the cause was established afterwards — a
concurrent session pushed an adoption branch, and the default branch received a
real commit later the same evening. For `al-admin` and `otto` it was not. A
sweep, a mirror, a bot and another session all produce that signal, and this
session did not distinguish them. Naming it here rather than in the module,
because the recency axis does not depend on the answer: what it depends on is
that the field does not answer the question, and that is established.
