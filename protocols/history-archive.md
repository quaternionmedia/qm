# Protocol — History archive, before a rewrite

**Question.** What did this repository's history contain before the rewrite,
and where is the copy that still has it?

**Invoked by** a human, or an agent asked to. **Budget** 30 days — it is
invoked by an event rather than a clock, but an archive goes stale in the
ordinary way because history moves, and one older than the budget no longer
describes the repository it was taken from. **Produces**
`protocols/runs/<date>-history-archive.md`.

Run this **before** any operation that rewrites published history: a purge, a
squash of a long-lived branch, a rebuild of a repository. It produces the copy
that makes the rewrite recoverable, and it records where that copy is.

---

## The tension this protocol exists to resolve

**Preserving the archive and purging sensitive data pull in opposite
directions, and only one of them can win in any given place.**

`ci/mathematics-registry.yaml` states the structure: identity is a function of
content, so a rewrite constructs a new graph rather than editing the old one.
An archive is therefore a **deliberate fork of the old graph** — it keeps every
object the rewrite abandons, under identities the rewrite has changed.

That is exactly what makes a rewrite survivable, and exactly what defeats a
purge. **An archive restores recoverability. It does not restore secrecy.** If
the reason for the rewrite is that something in the history should not be
readable, then an archive that anyone can read has removed nothing.

So the archive is placed **out of public reach**, and access to it becomes the
control that the history no longer provides. A public archive ref of a purged
repository is the failure mode this page exists to prevent, and it looks like
diligence.

**The org's answer is a private mirror repository, one per archived
repository.** That buys recoverability by anyone with access and makes access
the whole control — re-made every time somebody is added, and unverifiable by
any command on this page. Say who can read it, in the run.

**A private mirror creates a private repository name, and this corpus forbids
publishing one.** That is not a general caution, it is a mechanical constraint
here: `ci/policy-registry.yaml`'s `no-private-name-in-a-public-artifact` is
enforced by `uv run qm private-names`, and a mirror named after the repository
it archives is a new private name that a tracked file must never carry. **So
this page names no mirror.** The convention is recorded where private names are
already recorded — the gitignored companion beside `inventory-private.json` —
and the run refers to a mirror by its reference, never by its name.

There is a second-order trap in it. `qm private-names` reads its list of names
from that companion or from the host, so a mirror created today is a name the
check does not know until the list is refreshed. Between creating a mirror and
refreshing the list, every `clean` the check reports is a statement about the
old list. Refresh first, then write anything.

**If the material is credentials, rotate first.** A rewrite is cleanup after
rotation, never instead of it: anything pushed to a public repository should be
assumed cloned, forked and cached, and no operation on this origin reaches
those copies.

---

## 1. Establish what is being abandoned

```sh
git rev-list --all --count
git for-each-ref --format='%(refname) %(objectname)' | wc -l
git rev-list --objects --all | wc -l
```

Record all three in the run. They are the denominator: after the rewrite, the
same three commands on the live repository answer differently, and the
difference is what the rewrite did.

## 2. Take the archive, and verify it independently

```sh
git clone --mirror git@github.com:quaternionmedia/<repo>.git <local-clone>.git
git -C <local-clone>.git bundle create ../<repo>-<date>.bundle --all
git bundle verify ../<repo>-<date>.bundle

# Then the private mirror, whose name comes from the gitignored companion and
# is never written into a tracked file:
gh repo create "quaternionmedia/$(archive_name_for <repo>)" --private
git -C <local-clone>.git push --mirror "git@github.com:quaternionmedia/$(archive_name_for <repo>).git"
gh api "repos/quaternionmedia/$(archive_name_for <repo>)" --jq .private   # must print true
```

*Verify:* `git bundle verify` exits zero, and the object count in the bundle
matches step 1. A bundle that was written but never verified is a backup
nobody has restored, which is the state most backups are in.

*Verify the mirror is private before pushing anything else to it*, with the
`--jq .private` call above. A mirror created public and flipped afterwards was
public while it was being populated, and that window is the whole exposure.

## 3. Record every pin that the rewrite will break

```sh
uv run qm pins
git -C <consumer> ls-tree HEAD <submodule-path>
```

Every recorded pin is a commit identity that the rewrite invalidates. List them
in the run **before** the rewrite, because afterwards the live repository can
no longer resolve them and the archive is the only thing that can.

## 4. Name what the archive cannot reach

Clones and forks made before the rewrite keep the old graph, and nothing here
touches them. List, in the run, the forks the host reports and the people known
to hold clones:

```sh
gh api repos/quaternionmedia/<repo>/forks --jq '.[].full_name'
```

A purge that leaves a fork in place has changed where the material is, not
whether it exists.

## 5. After the rewrite, measure it

Re-run step 1 against the live repository and record the three numbers beside
the originals. Then re-point every pin from step 3, and confirm
`submodule-check.yml` is green in each consumer.

`ci/mathematics-registry.yaml` holds `rewriting published history` as
**aspirational** precisely because this organisation has never done it. The
first run of this protocol is the measurement that moves it — to earned, or to
refuted.

---

## What this protocol cannot see

Whether anybody already holds a copy. It enumerates the forks the host knows
about and the pins this corpus records, and neither set is the set of people
who have cloned a public repository. It cannot tell whether the material was
read, or by whom, and it has no view on whether a rewrite was the right
response — only on whether the state before it was preserved and the state
after it was measured.

It also cannot verify a private mirror stays private. That is an access
decision on the forge, re-made every time somebody is added, and no command
here reads it.
