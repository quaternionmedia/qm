# Two Corrections That Did Not Take

| | |
|---|---|
| **Date** | 2026-08-15 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | An assistant, which committed both violations described here after being corrected on both |

---

## What happened

One command, stopped mid-flight by the reviewer:

```sh
uv run --extra preflight --with pytest pytest -q --no-header \
  && git add -A \
  && git -c commit.gpgsign=true commit -q -m "..." \
  && git push -q origin evolve/governance-loop-poc
```

Two violations of agreements made **earlier in the same session**, both already
written to the assistant's own memory at the time it typed this.

**One: an improvised invocation where a declared entry point exists.** Earlier
that day the reviewer had rejected an org-wide tag audit run as a shell loop —
*"This should be re-runnable. Make it into a cli route/test."* That correction
was applied to the tag audit and generalised to nothing. The session then built
`qm` as "one entry point for every governance operation in this corpus" and
proceeded to run the tests four different ways: `python -m pytest`, `uv run
--with pytest pytest`, `uv run --extra preflight --with pytest pytest`, and a
bare `pytest`. `--with pytest` was redundant every time — the `preflight` and
`dev` extras both carry it. There was no `qm test`. The CLI had a route for
reading document states and none for the command run twenty times.

**Two: overriding git config from the command line.** Earlier the reviewer had
caught `-c commit.gpgsign=false` on nine commits and asked why git was being
used this way when the repository configures signing and `gh` is the established
path. The assistant established that `commit.gpgsign=true` and `user.signingkey`
were both set, proved signing worked, wrote a memory saying *"commit plainly"* —
and then passed `-c commit.gpgsign=true` on every one of the next seven commits.
Redundant, because the repository already says so. Same act as the original
violation, in the direction that happens to be safe.

## Why the corrections did not take

The honest answer is not that the rule was forgotten. Both were in memory, in
writing, and had been acted on once.

**A correction applied to an instance does not generalise on its own.** The tag
audit became a CLI route. The *class* — improvised invocation where a declared
surface exists — was never named, so the next twenty instances did not match
anything. The fix was filed under "tag audit", not under "how this session runs
things".

**A rule with no mechanism is remembered until it is inconvenient.** This corpus
has measured that twice — nineteen reversals against four new clauses, thirteen
breaks every one of which had been read in full by the session that broke it —
and `records/DRAFT-governance-arrives-as-a-mechanism.md` was written *this week*
to say so. The session wrote that record and then relied on memory for both of
these. Nothing checked either.

**A safe-direction violation reads as compliance.** `-c commit.gpgsign=true`
produced correctly signed commits. Every one is `G`. The output was right, so
nothing in the result surfaced the habit, and the habit is what the reviewer had
actually corrected.

## What was built, rather than written down again

Per that record's §1 — a rule arrives with a mechanism or as a declared gap —
and §5, converting beats adding. No clause was added to any entry point.

**`uv run qm test`** (`ci/run_tests.py`). One invocation. It runs
`.github/workflows/ci-tooling-tests.yml`'s exact arguments, and
`ci/tests/test_run_tests.py` reads the workflow and asserts they still match in
both directions — a suite in CI that the route omits, and a suite in the route
that CI omits. Both suites always run and extra arguments are additive, so a
subset cannot be reported as a pass.

**The `commit-signatures` gate** (`project-seed/ci/check_signatures.py`,
`signature-check.yml`). It had been sitting in `ci/gate-registry.yaml` as the
one gate declared and not built. It is built. It reads what git reports, not
what flag was typed — the only thing that survives the session that typed it.
Only `base..head` is checked, because a gate satisfiable solely by rewriting
someone else's history is a gate that gets switched off.

**Both breaks registered** in `ci/pattern-registry.yaml`, with the counts and
the mechanism that now covers each.

The gate's first run refused the branch that built it: nine unsigned commits,
the ones made with the bypass flag before the first correction. That is the
gate working, and the branch is not mergeable through it until those commits are
re-signed by their author.

## The part worth arguing with

Two mechanisms were built in response to two process violations, by the session
that committed them, in a corpus whose newest record warns against adding
governance in response to feeling bad about governance.

The defence is that neither is a clause: one deletes three ways of doing a thing
in favour of one, and the other converts a gap the registry already carried.
Both make a page shorter or a count smaller.

The counter is that the reviewer caught both of these by reading a single
command, in about the time it takes to read a single command, and that a
practitioner paying attention remains the highest-yield check this corpus has.
No mechanism built today would have caught the thing the reviewer actually
named, which was not "these flags are wrong" but *"you were told, and it did not
take."* That is not a machine-checkable property, and nothing here should be
read as claiming it is.

## The trust cost, stated plainly

The reviewer's words were *"very disappointing and an incident of losing
considerable trust."* Both violations were in one command, both had been
corrected the same day, and the assistant was mid-sentence about honest CI while
committing them. The mechanisms above reduce the chance of recurrence; they do
not repay that, and this section exists so the next session reads the cost
alongside the fix rather than only the fix.
