# Perspective — The Families, Delineated, and What Each Reader Could Not See

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (1M context), driving the session |
| **Task** | One session opened to compare this workstation with the host, family by family, and closed with every reader of the estate able to say where one family stands. This is why it went the way it did: the assumptions that were wrong first, the defects the session caused as well as the ones it found, and for each the check that would have caught it and whether that check now exists. |

## 0. Standing and evidence

One workstation, the clones under `repos/qm/` and three under `Documents/`,
git 2.37, the host reached through `gh`. Commits are stamped in
`handbook/handoffs/families-delineated.md`; every figure here is one run at
that stamp.

- **E1** — directly observed: command output, gate output, host state.
- **E2** — read from the repositories.
- **E3** — inference, marked where it appears.

## 1. The shape of the session

The brief asked for the local state against origin, with the families as the
axis. The corpus already had the families — a record declaring them, a roster
claiming them, a generated seam file, a cookbook, a rollout plan — and it had
the readers of state: the harness, the inventory, the branch census, and on
`origin/main` since the night before, the estate survey. The two sets did not
meet. To answer "where does show-control stand" the session ran the estate,
extracted `families.json`, and joined them in a scratch script. That join is
now `uv run qm estate --by-family` and a column in both harness views, and the
rest of this page is about what was learned making it.

## 2. A green origin says nothing about a rule that is not in CI

**The assumption.** Two pull requests had merged green the night before; the
private-names rule is a gate; so the tree respects it.

**What was true.** `registries.yml` says in its own header why
`qm private-names` is absent from CI: it reads a machine. The only reader of
that rule is a person running it before a push, and the runbook's Step 3 had
been written the same evening to say so. Two repositories had been created
private on the host that night — one an hour before its name reached public
`main` in thirteen files, the other five minutes before, with a roster note
saying *"Private on the host"* in the same commit that named it (E1:
`gh repo view` creation times against the merge times of #111 and #113).
Neither was in the exception registry.

**The check.** `uv run qm private-names --source host` — exists, is red on
`origin/main` at `90a1bd7`, and is green on this branch after the roster entry
became a reference. It cannot go into CI, and that is not a gap to close: a
runner's token cannot list private repositories, so a runner cannot know a
name is private. The guard is the person, and the runbook now names the step.

**What could have been mechanical, and was not.** A roster entry whose note
contains "private" and whose `name:` is committed is a contradiction a lint
could see without the host. Not built; it would have caught one of the two.

## 3. Two views disagreed, and the setup was the disagreement

**The finding, as first read.** The estate named forty-four repositories and
`families.json` named forty-four, and the sets differed by three each way.
Two generators of one roster, out of step.

**What was true.** Both read the same roster. The estate had been run from
the scratchpad against origin's copy of `ci/workspace.yaml` with the local
`ci/` modules on the path — and the roster loader merges the gitignored
companion from that local directory, which supplies three private entries'
real names. So the estate printed the names and the committed seam file
printed the references. The tool was fine; the run was reading its own
scaffolding (`records/DRAFT-decision-record-discipline.md` §9), and the
"disagreement" was the redaction working. Named here because the first
sentence written about it was a defect report.

**The check.** `ci/roster.py`'s docstring says which shape each consumer
gets. Reading it before asserting the delta is the check, and it exists.

## 4. Two resolvers, one disk, two answers

**The finding.** `qm cookbook` said `qmetronome` was not on this disk and
`qm estate` found it. The same disk, the same minute.

**What was true.** The cookbook probed `<root>/<name>`; the estate and the
workspace generator resolve the roster's `paths`. `qmetronome` lives under
`../AndroidStudioProjects`, which only the roster knows, and every private
member is a reference, which is not a directory. A second resolver
disagreeing with the first is exactly how two views of one address come to
say different things (`records/DRAFT-a-disagreement-is-a-delta.md`).

**The check.** Now a test that places a member where the roster says and
nowhere the probe looks, and one that finds a private member by its
reference. Both go red when `clone_of` skips the roster (E1, the mutation
quoted in `ci/tests/test_cookbook.py`).

## 5. The defect the tests could not see, and the one that ran the tool

**What happened.** The roster lookup inside `build()` was overwritten two
lines later by a list that already used the name `index`. Every test of the
resolver stayed green; `uv run qm cookbook` crashed with `'list' object has
no attribute 'get'`. The session caused this.

**Why the suite missed it.** No test called `build()`. The resolver was
tested in isolation, which is where the unit was correct.

**The check.** A test that runs `build()` against a fixture seam file and
captures what type reached each lookup. It exists, and re-introducing the
collision produces the same `AttributeError` (E1).

## 6. An inert assertion, twice, caught by breaking the thing it guarded

**Two of the session's own tests proved nothing as first written.** One cut
the rendered estate at the first `(` to check a name was absent — and the
first `(` is in the column header `prs (offline)`, so the assertion looked at
a header and never at a row. The other asserted a grouping's order against a
fixture whose insertion order already equalled the sorted order, so the
mutation that removed the sort passed.

**The check.** `records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md`:
each was found by running the named mutation and watching for red. The first
was rewritten to assert the row itself; the second by reordering the fixture
so insertion order and name order differ. Both mutations then failed as they
should, and the failures are quoted beside the tests.

## 7. The brief read a stamp and reported none

**The finding.** The session brief reported `status/harness.yaml` as "age
unknown: no `generated_at` found" while the stamp sat on line 2, thirteen
hours old inside a 24h budget.

**What was true.** The pattern admitted an optional double quote before the
timestamp; `yaml.safe_dump` writes a single one. The brief's own tests wrote
the fixture as JSON — double-quoted — so they measured the fixture's shape
rather than the generator's.

**The check.** A test that writes the file as the generator does. It exists
and goes red when the pattern is narrowed back (E1).

## 8. Two local gate failures with one cause, and a word that hides it

**The finding.** The local gate run failed the base check and the signature
check on all five commits: *"signature could not be checked"*.

**What was true.** Both steps were asking the host about a branch that was
not on it. `check_pr_base` says so in its own output. The signature workflow
runs with `--source host`, which asks `gh api` for the host's verdict per
SHA, and the host returns nothing for a SHA it has never seen; the script
maps that to the same word it uses for a keyring it cannot read. Locally,
`git log --format=%G?` read every commit as `G` under the key that signed the
two pull requests merged the night before (E1).

**The check.** Distinguishing "not on the host" from "could not be checked"
in `check_signatures.py`. Does not exist; named in the handoff.

**And the trap re-hit.** The first run of the gate runner was piped into
`tail`, printed nothing and exited zero. `handbook/async-contract.md` §8
names this — *a pipe replaces the exit code* — and the session read it that
morning. The second run went to a file and exited one.

## 9. A patch written through a shell heredoc, twice

Two edits were lost to escaping: a `\'''` sequence that Python read as the
end of a triple-quoted string, and a `\\'` that the heredoc collapsed to `'`
and Python then read as the end of a raw string. Both were the session's own,
both were caught by a failing parse before anything ran, and the memory that
warns about exactly this was in the session's context. The check is a
practice, not a tool: a patch goes into a file through a file-writing tool,
and the shell runs the file.

## 10. What the roster could not see, because a roster is a claim

Two `project/<name>` branches on origin had no roster entry.
`status/governance.yaml` reads the branches and listed both — one redacted
by position — and every other reader reads the roster and listed neither.
Nothing compared the two, and nothing could have inferred the entry: a family
is stated by a person (`records/DRAFT-a-family-is-bordered-by-what-it-drives.md`
§2), and so is a roster row. The entries are now written, family unstated.
The comparison — every project branch has a row — is the check, and it does
not exist; its design caveat is in the handoff, because a runner without the
companion cannot match a private branch to its reference.

## 11. What was not a finding

The `codex` process on the workstation was the ChatGPT extension's
app-server, started with the editor. Reading its command line took one call
and closed the question; reporting a second session would have opened one for
someone else. Two clones refused to move because the editor's workspace held
them; the third, outside the workspace, moved. That is a fact about the
editor and the roster now states the intended layout, so the estate reads one
of them MISSING until the move, which is true.
