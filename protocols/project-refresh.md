# Protocol — Project refresh

**Question.** Is this project current with the corpus it adopted, do its own
tests pass, and does it meet the policies its gates enforce?

**Invoked by** a human, or an agent asked to. **Budget** 60 days. **Produces**
`protocols/runs/<date>-project-refresh.md`.

This is one project, end to end: its branch in the corpus, its own repository,
its tests and its gates. `handbook/propagation-runbook.md` is the procedure for
the two steps that change something, and this page is the order they go in and
what is read before and after.

---

## 1. Read what is behind

```sh
git fetch --all --prune                      # in the corpus clone
git -C <the project's clone> fetch --all --prune
uv run qm project <name>
```

It prints one line per fact, each `current`, `behind` or `unknown`, with the
remedy under every line that is not current. It reads refs and never a working
tree, and it fetches nothing, which is why the two fetches come first. With no
clone of the project beside the corpus it says where one goes and stops.

Every line that follows in this protocol is a line of that output made
current. A project with nothing behind skips to step 4.

## 2. The corpus side

`handbook/propagation-runbook.md`, Part A. A `propagate/<name>-<date>` branch
cut from `project/<name>`, with `main` merged into it, opened against
`project/<name>` and merged with a merge commit.

The ADR lint on that pull request runs the placeholder check and compares the
record index with the directory, so the two seed copies in `adr/` are
refreshed on the same branch when either is behind: `adr/TEMPLATE.md` is the
seed's file, and `adr/README.md` is the seed's page with the project's name
substituted and the project's own index kept. The index lists each draft by its
whole title, one to a bullet.

## 3. The project's side

Part B of the same runbook, as two pull requests in the project's repository.

**The pin.** `governance/qm` moves to the tip of `project/<name>`, taken from
the host with `ls-remote`.

**The copies**, stacked on the pin. Every workflow `project-seed/ci/seed-workflows.txt`
names is copied into `.github/workflows/`. `AGENTS.md` is the seed's page above
the project's own line, with the project's name substituted, and the project's
section beneath it is kept as it is. `CLAUDE.md` is the seed's one-line import.

A workflow copied for the first time runs for the first time, so a project that
never carried one may go red on it. That red is a finding about the project and
is recorded in the run, with the pull request left as a draft until it is
answered.

## 4. The project's tests

The project's own command, from the section of its `AGENTS.md` below the
project line, run on its default branch before anything is changed and again on
the branch that carries the copies. A baseline that is red is recorded as red:
a refresh measured against it proves nothing either way.

A suite that regenerates committed files leaves the working tree dirty when its
output is not byte-stable. Compare `git status` before and after, and say which
files moved.

## 5. The policies

```sh
python governance/qm/project-seed/ci/run_workflows_locally.py --event pull_request --base-ref main
uv run qm policies
```

The first runs in the project's clone and executes every workflow's steps,
the seed's gates among them: signatures, leaks, the voice of a pull request
body, tag claims, licensing, and the lines a change adds. The second runs in
the corpus and prints which policy each of those detects and which policies
have no detector, which are read for by hand.

Report each step as the runner printed it, with every skipped step counted. A
skip is not a pass.

## 6. Read it again, and regenerate

```sh
uv run qm project <name>
uv run qm docs generate
uv run qm docs check
```

The first is the same command as step 1, and the run records both readings.
Open pull requests stay `behind` until they merge, which is the reading meant.
The second and third run from the corpus's main clone once the project's pull
requests have merged, so the status documents carry the project as it then is.

## What a run records

The commit of each repository the run read, both `qm project` readings, each
pull request it opened or merged, the test command with its result, each gate
with its result, and everything left open with the reason.

## What this cannot see

Whether the project's tests test anything. Whether a record on the project's
branch is right. What a gate does on the host, which a local run of its steps
approximates and does not reproduce. And any project but the one named: a
refresh of one says nothing about its siblings, and `uv run qm estate` is the
reading across all of them.
