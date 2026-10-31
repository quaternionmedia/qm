# Org standards: protection, CI, and the estate's repositories

**Stamped 2026-10-28.** `qm` `main` at `bb2ed17`, and the host as `gh api`
read it that day. The token used has no `admin:org` scope, so org-level
rulesets were not read. Every figure here is true at that reading and nowhere
else; re-derive it before acting on it.

**Status: a plan.** It states eight decisions taken on 2026-10-28, the state
the host is in, the standard those decisions set, and the steps that reach it.
Each step becomes a record, a pull request or a person's act. This page decides
nothing beyond the eight.

## Decisions

| | Decision |
|---|---|
| 1 | **Host protection covers public repositories only, for good.** A private repository runs the same gates, and for it they are signals: nothing on the host stops a merge past a red one. |
| 2 | **The org's gates are reusable workflows in `qm`.** A project calls each at the commit its governance submodule pins, and adds jobs of its own beside them. A check fails when a called ref and the pin differ. Nothing is copied. |
| 3 | **Every governed project runs every seed gate**: `adr-lint`, `submodule-check`, `reuse-lint`, `one-pr-check`, `leak-check`, `signature-check`, `timeless-check`, `tag-claims`, and `tag-determinism`, which joins the seed. |
| 4 | **A lightweight version tag is deleted where nobody can state its basis.** A person validates each one before anything happens to it. Annotated tags stay. |
| 5 | **Every live repository is rostered**, at `v0.0.0` unless it has adopted. Nothing is archived. |
| 6 | **The default branch is `main`** for every new repository and every adopted project. A `v0.0.0` repository keeps its name until it adopts. |
| 7 | **Pull requests merge with merge commits only.** Head branches are deleted on merge, and auto-merge stays off. |
| 8 | **Two-factor authentication is required once the members without it have been told**, and only owners create repositories. |

## The host on 2026-10-28

- **Repositories.** 123: 121 live and 2 archived; 38 private; 10 forks. The
  roster names 42 of the live ones. Of the 79 it does not name, 46 have no
  push since before 2024 and 20 were pushed in 2026.
- **Plan.** GitHub Free. Every private repository refuses a ruleset with
  `Upgrade to GitHub Pro or make this repository public` (HTTP 403).
- **Protection.** `qm` has none of its six drafted rulesets applied
  (`.github/rulesets/README.md`, stage 0). codecartographer, janus and moat
  have one repository ruleset each. alfred, benchmark, golfvs, midiphonor,
  milestones and otto have classic branch protection.
- **Settings.** All 121 live repositories allow merge, squash and rebase
  merges; auto-merge is off on all; 104 keep a head branch after its merge.
  Default branches: 83 `main`, 35 `master`, 2 `dev`, and carlos, an adopted
  project, `they`.
- **CI.** 41 repositories have workflows. Governed ones run copies of the
  seed's: `adr-lint` in 14, `reuse-lint` and `submodule-check` in 11,
  `one-pr-check` and `tag-claims` in 7, `signature-check` in 6, `leak-check` in
  4, `timeless-check` and `tag-determinism` in 3. Five call
  `quaternionmedia/.github`'s reusable build workflows (pytest, ruff, publish,
  a pdm update), whose open draft #9 updates them.
- **Tags.** 25 repositories carry tags; the governed ones are in step 6.
- **Members.** 11, of whom 7 have no two-factor authentication. Members may
  create public and private repositories.

## The standard

### Branches and tags, on public repositories

One ruleset set, rendered for each public repository from a template in `qm`:

- **The default branch** (`~DEFAULT_BRANCH`): a pull request with zero
  approvals, the `merge` method only, every baseline gate as a required check,
  signed commits, no force-push and no deletion. Zero approvals for the reason
  `.github/rulesets/README.md` gives: one account cannot approve its own pull
  request, so the governance is the list of checks.
- **Version tags** (`refs/tags/v*`): the semver name pattern, signed, no update,
  no deletion, and creation by a named human only. `qm`'s ruleset F has no
  `creation` rule. With an empty bypass list that rule would stop every tag,
  so the bypass list names the role that cuts a release, the repository's
  admins, and no app or workflow.
- `qm` alone adds its namespace rulesets, B to E.

A job in a called workflow reports its check as `<calling job> / <called job>`.
The template names the required checks that way, and every project's caller
names its jobs the same.

### Private repositories

The same gates and the same settings, and no ruleset. A merge past a red gate is
possible, and the host records nothing to mark it. The tag gates run when a tag
is pushed and report; they do not stop the tag.

### CI

- Each gate is a `workflow_call` workflow in `qm`, and `qm`'s own workflows call
  the same ones. The seed's per-gate files become one caller,
  `project-seed/ci/governance.yml`, which a project copies once.
- The caller names `qm` at a sha. A new gate, `pin-check`, fails when that sha
  differs from the governance submodule's pin, so a pin bump changes both in
  one commit and a gate's version is always the pin's.
- A project adds its own workflows beside the caller, for build, test and
  release, from `quaternionmedia/.github`'s reusable workflows or its own. It
  does not edit the caller. A weaker gate is a change to `qm`, made there.
- `signature-check` reads SSH signatures before any ruleset requires it
  (`handbook/handoffs/qm-queue.md` §4).

### Tags

As `records/DRAFT-version-tags-are-claims.md` states: annotated, cut by a
human, naming what was reviewed, what was tested by hand, and what the
automated gate covered. A person validates each existing lightweight version
tag. One whose basis can be stated is re-cut as an annotated tag at the same
commit, and one whose basis cannot is deleted. A fork's tags are its
upstream's releases, not claims of this org, and are outside the list.

### Repository settings

Merge commits only, head branches deleted on merge, and auto-merge off, in every
repository. `main` as the default branch for new and adopted ones. Dependabot
updates grouped (`handbook/handoffs/qm-queue.md` decision 5).

### Membership

The members without two-factor authentication are told; a person then switches
the requirement on, and anyone still without it leaves the org until they enable
it. Repository creation is limited to owners.

### The roster

Every live repository is an entry in `ci/workspace.yaml`, a private one by
reference with its name in the companion. A check fails when the host holds a
repository the roster does not name.

## Steps

In order. A step that changes the host is a person's act, run by a command
that also has a read-only form.

| | Step | Done when | Who |
|---|---|---|---|
| 1 | `signature-check` reads SSH signatures | an SSH-signed commit the host verifies passes, and the mutation that breaks it is recorded | pull request in `qm` |
| 2 | The gates as reusable workflows, the caller, `pin-check`, and `tag-determinism` in the seed | `qm`'s own workflows call them, and a project fixture calls them at a pin and fails `pin-check` on a mismatch | pull requests in `qm` |
| 3 | Every live repository rostered, and the roster checked against the host | the check exits 0 against the host | pull request in `qm`, the companion by hand |
| 4 | Settings read and applied across the org | the read form reports every live repository at decisions 6 and 7; the write form is run by a person | pull request in `qm`, then a person |
| 5 | The ruleset template, rendered and applied to each public repository | each public repository reports the set applied, evaluating, then active by `.github/rulesets/README.md`'s staging | pull request in `qm`, then a person |
| 6 | Each lightweight version tag validated | no lightweight version tag in a repository that is not a fork | a person, per tag |
| 7 | carlos's default branch renamed to `main` | every adopted project's default branch is `main` | a person |
| 8 | Members told, two-factor required, creation limited to owners | the org's settings read so | a person |
| 9 | Each project moves to the caller at its next pin bump | `status/governance.yaml` measures the caller in place of the four copies it counts | each project's propagation |

Step 6's list, for public governed repositories, with an asterisk on an annotated
tag: ShowRunner (8 tags, all lightweight, `v0.3.0` to `v0.5.3` among them),
TheatreMix-python (`v0.1.0`, `v0.2.0`), alfred (`alpha`, `v0.2.0`), datum
(`v0.0.1`), golfvs (`v0.0.2-prealpha`\*, `v0.0.3-prealpha`\*), holophonor
(`v0.1.0`), ludwig (`v0.1.0`), midiphonor (`v0.0.1`, `v0.1.0`, `v0.1.1`,
`v0.2.0`), otto (`alpha`, `v0.2.0`, `v0.2.1`, `v0.2.2`), qmetronome (16, both
kinds), scad-chess (`v1.0`), uPhonor (10, all lightweight), and waveofhormuz
(`v2.2.0`). Two private governed repositories carry annotated tags only. Among
repositories the roster does not yet name, milestones (14), haiku (2) and
tocCATa (1) carry version tags of their own; the rest with tags are forks.
`alpha` and `v1.0` do not match the semver pattern, so the tag ruleset neither
protects nor permits them.

## Not settled here

- **Org-level rulesets.** GitHub's documentation places them on a paid plan,
  and the token used could not read the org's. On Free, each public
  repository carries its own set, applied by script.
- **`commit_message_pattern`** on a Free plan's public repository. `qm`'s
  ruleset A uses it to refuse an unmonitored co-author trailer. Whether the
  host accepts it there is not verified.
- **What the 79 new roster entries say beyond `v0.0.0`.** A family, a
  description, a phase: the roster's fields are a person's claims, and step 3
  writes only what the host establishes.
