# QM-XXXX — A Stage Is Recorded, and `main` Receives Releases Rather Than Asserting Them

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-29 |
| **Pends on** | §2 — whether promotion moves commits or built artifacts. Every other clause here holds either way; that one decides whether `prod` is a ref at all, and it is deliberately unsettled until the branches are pushed. `ci/mathematics-registry.yaml` holds it as the aspirational mapping *the promotion pipeline a change climbs*. |
| **Principle** | `decisions-are-documented` — decisions are documented or they didn't happen; `public-by-default` — public by default |
| **Restated in** | Nothing. |

## Context

Work in this organisation currently targets `main` directly, and `main` is
where every gate is keyed: sixteen files in this repository name it as the
base, `project/<name>` branches take changes from it, and
`project-seed/ci/check_pr_base.py` refuses a pull request that does not.

Four stages are wanted instead — a development target, a versioned approval
step, a deployment source, and a public release destination. Naming them is
cheap. What is not cheap is that two of this corpus's existing decisions touch
the same ground, and a stage model written without them would contradict both
without appearing to.

**`records/DRAFT-version-tags-are-claims.md` §4 says `main` asserts nothing.**
The two human gates are ratification and the version tag. A model that makes
`main` mean *released* moves a gate onto a branch, which is precisely what that
record refuses.

**`ci/mathematics-registry.yaml` says the shape is undecided.** Promotion is a
total order on stages with a monotone map between them — but whether the thing
promoted is a commit or a built artifact determines whether a stage is a ref or
a label, and the two produce different repositories. Creating branches before
answering it would settle the question by accident.

## Decision

### §1 — The four stages, and what each one means

| stage | holds | entered by | rewritable |
|---|---|---|---|
| `test` | the current development target — local and ephemeral work, where it lands first | a pull request, as `main` takes one today | **yes** |
| `dev` | what has passed versioned approval | promotion from `test` | no |
| `prod` | what QM deploys, fed by CI from `dev` | promotion from `dev`, never a direct push | no |
| `main` | what is publicly released and generally adopted | promotion from `prod`, at a tag | no |

### §1a — `test` is ephemeral, and that is the whole of what makes it useful

`test` may be reset, squashed, rebuilt and force-pushed. Nothing may pin it,
nothing may branch from it expecting the branch to survive, and no downstream
consumer may read it. It is the one ref in this model where a rewrite is an
ordinary operation rather than the act
`ci/exception-registry.yaml` records the corpus as forbidding.

The other three are **durable**: append-only, no rebase, no squash, no
force-push. `ci/mathematics-registry.yaml`'s *propagation, and the pin that
reads a project branch* is the structure — a pin is a reference to a commit by
content, so rewriting a ref that anything reads makes the pinned commit
unreachable and every consumer wrong at once. That constraint binds a ref
exactly when something may read it, which is why it binds three of these four
and not the first.

This is also the answer to *"we will likely need to squash, or purge and
rebuild, certain repos or branches"*. On `test`, that is routine and needs no
ceremony. On `dev`, `prod`, `main` or any `project/<name>`, it is a history
rewrite: `protocols/history-archive.md` runs first, and the decision is a
person's.

### §2 — Whether a stage is a ref is not settled here

If promotion moves **commits**, each stage is a branch and the order is
enforced by merge direction. If it moves **built artifacts**, the stages are
labels on a build, `prod` needs no ref, and `main` remains the only long-lived
branch. The two are not stylistic variants: they produce different
repositories, different gates, and different work in the sixteen files that
name `main` today.

This record does not answer it. The branches are staged so that either answer
is cheap on the day it is given, and the answer is given when they are pushed.

### §3 — `main` receives a release; the tag still makes the claim

This is the clause that keeps `records/DRAFT-version-tags-are-claims.md` §4
intact rather than amending it. `main` becomes the **destination** a release
arrives at. It does not become the assertion that something is released — the
version tag remains the only thing that asserts that, cut by a human who
reviewed the change set.

So `main` still asserts nothing on its own. A commit sitting on `main` with no
tag above it is a draft that has travelled further than most, exactly as a
commit on `main` is today. Read the other way — `main` *is* the release claim —
this record would be an amendment to that one, and it is not written as one.

### §4 — A private fork is allowed where a public repository cannot be

`PRINCIPLES.md` `public-by-default` stands: public is the default and closure is
the exception that costs a reason. Where internal deployment cannot run from a
public repository, a private fork of the public repository is permitted for
that purpose.

Two obligations come with it, and neither is new.
`records/DRAFT-going-private-is-an-act-with-obligations.md` governs the act.
And the fork's **name** becomes a private repository name, which
`ci/policy-registry.yaml`'s `no-private-name-in-a-public-artifact` forbids any
tracked file from carrying — so a private fork is referenced, never named, in
the same way the roster already references two.

### §5 — The stages are org-level and do not reach `project/<name>`

A `project/<name>` branch is pinned by a downstream submodule and takes changes
in and never out. Nothing in §1 changes that: propagation still runs from
whichever ref is the org's development target into each project branch, and the
five work namespaces in `docs/ref/namespaces.md` are unchanged, and that page
now carries a stage-refs section naming these four so a reader does not sort
them under "a branch outside the five is a mistake". A stage is a claim about
how far a change has travelled, not a new kind of branch for a project's
records.

## Consequences

**Sixteen files name `main` as the base, and they are the enforcement layer.**
`ci/cli.py`, four other generators, six seed scripts and five workflows. Under
the artifact reading none of them changes; under the commit reading all of them
do, together, across five repositories with live submodule pins. That asymmetry
is the strongest practical argument for answering §2 before pushing, and it is
not an argument for either answer.

**A stage branch that exists is a claim that promotion moves commits.** Staging
them locally is not that claim; pushing them is. That is why they are staged
and not pushed, and why this record is Proposed rather than a description of
something already done.

**`main` moving from *development target* to *release destination* leaves a
gap.** Everything currently merges to `main` because that is where the gates
are. On the day `test` becomes the target, a contributor following `AGENTS.md`
will open a pull request against the wrong branch and every check will pass.

## Alternatives considered

**Keep one branch and use tags alone.** This is the status quo and it is
coherent — `version-tags-are-claims` is built for it. Rejected because it gives
deployment nothing to read: CI has no ref that means *approved and not yet
released*, so approval lives in someone's head or in a pipeline variable.

**Make `main` the release claim outright.** Simpler to explain and it amends a
ratified-in-waiting record in its central sentence. Rejected in favour of §3,
which gets the same operational result without moving a human gate onto a
branch.

**Answer §2 now, in favour of branches.** Rejected as the more expensive
mistake. Deleting a `prod` branch that turned out to be a label is cheap;
unwinding sixteen files and five repositories' worth of base changes is not.

## Revision triggers

- §2 answered, either way. That closes the `Pends on` and this record is
  rewritten to describe one model rather than two.
- The first private fork created for internal deployment. §4 is untested and
  the naming obligation is the part most likely to be got wrong.
- A contributor opening a pull request against the old target after the switch,
  which is the gap named in Consequences and the first thing to mechanise.
- `project/<name>` acquiring a stage of its own. That would mean §5 is wrong
  and the stages are not org-level after all.

## Amendments

*(none)*
