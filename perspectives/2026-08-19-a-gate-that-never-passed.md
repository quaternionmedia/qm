# A gate that never passed

**2026-08-19, later.** Four repositories: `qm`, `dossier`, `qmcp`, `rad`.
Attributed, dated, binds nothing.

Tools: written with an AI coding assistant, reviewed and committed by a human.

## The finding

**`rad`'s ADR lint had failed on every run in the repository's history**, and
nobody had noticed, because a check that has never once passed produces no
signal when it fails again.

    gh run list --workflow adr-lint.yml
    failure on dependabot/npm_and_yarn/multi-...  2026-08-10
    failure on main                              2026-08-10
    failure on evolve/rad-v1                     2026-08-09

Not one of those failures was about a record. The workflow runs
`$QM_SUBMODULE/project-seed/ci/adr_lint.py`, and that repository had no
submodule and no `.gitmodules`, so the script it invokes did not exist. Every
run died on a missing file.

The corpus already has a name for the opposite failure — a green check standing
where a reader believes something is enforced. This is the same defect wearing
the other colour: **a red check standing where a reader has stopped looking.**
It is worse in one respect. A green check at least fails loudly the day it
starts working. A permanently red one trains everybody who sees it, including
its own author, to read "that check is just broken" and move on.

## The false assumption

That a workflow existing means a check running. `rad` had `adr-lint.yml`
committed, referenced in its own `adr/README.md`, and described in its handoff.
Everything about the repository said the lint was in force. What nobody had done
was **read a run**.

That is the reusable part, and it generalises past this instance: *the presence
of a gate is not evidence of a gate.* The corpus's own gate registry says
`cannot_see` is the load-bearing field. This is a prior question — before what a
gate cannot see, whether it sees anything.

## What it cost, and what it did not

It cost less than it might have. `rad`'s records were in good shape, so the
lint had nothing to catch. But that is luck rather than the system working: the
one mechanism that would have caught a malformed record had been off since the
repository was created, and if it had caught something, nobody would have known.

## Running a seed script from a project for the first time

Mounting the corpus so the lint could run surfaced a second defect immediately.
`check_pr_base.py` refused the branch, explaining:

> main carries the org namespace and no top-level adr/ at all.

True of the corpus. False in `rad`, whose `main` carries ten records
deliberately, through a `RECORDS_DIR` knob the seed's own workflow provides.
**The refusal asserted something about the base and never asked the base.**

It had no test in either direction — not for the refusal it exists for, and not
for the case it got wrong. Both exist now, and the new one was confirmed to fail
against the unmodified script before the change rather than assumed from a green
suite that had never covered it.

The general shape: a guard written inside the corpus, correct there, and wrong
the first time it ran anywhere else. Nothing about it was careless. It had
simply never been executed in the situation it now governs.

## What I got wrong, in the same session

I reported `rad`'s governance suite as **"126 passed"** from a `tail` that cut
off the line above it. The true result was **6 failed, 126 passed** — my new
record was missing two sections the template requires and an entry in the index.

I found it only because I went back to check a single assertion I was unsure of.
Nothing in my process would have caught it: I had read the last line of a
truncated output and treated the number in it as the result.

That is the third time this corpus has recorded a reading failure of exactly
this kind, and the previous two are already in `records/`. The rule those
records state — check what else could produce the signal — did not fail here.
**It was not applied**, because "126 passed" did not look like a signal that
needed checking. A summary line is the most confident-looking output a tool
produces, and I did not ask what was above it.

## What now exists that did not

- `rad` mounts the corpus, and its lint passes for the first time. The dev loop
  there is `python governance/qm/project-seed/ci/...` rather than an absolute
  path into a checkout of another repository.
- `project/rad` exists, so the org's own status document stops reporting that
  repository as having no governance branch.
- `check_pr_base.py` asks the base the question its message answers, with tests
  on both sides.
- A proposal in `rad` to pivot the interaction contract around a numpad, drawn
  entirely from what implementing it in a terminal taught.

## What I would tell the next session

**Read a run, not a workflow file.** `gh run list --workflow <name>` takes
seconds and answers a question the repository's own documentation cannot.

**When a summary line looks decisive, look above it.** Every one of this
corpus's reading failures has been a confident-looking output taken at its word.

**Run a seed script from a project before believing it is portable.** Two of
this session's defects were in code that was correct where it was written and
wrong the first time it left.
