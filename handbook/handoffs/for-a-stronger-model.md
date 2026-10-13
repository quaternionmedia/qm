# Handoff — For a Stronger Model

Written by a weaker one, deliberately. Read this before the other handoffs; it
says which parts of them to distrust and why.

*Stamped 2026-08-12. `main` at `104361a`. Open: **#55** (mrharpo, `docs`), **#56**
(`evolve/git-hygiene-and-handoff` → `main`, holds the `main` slot), **#57**
(`propagate/datum-2026-08-12` → `project/datum`). Every figure here was true at
those commits. Re-derive before quoting — including from this page.*

---

## Read this first: the reliability of what you are inheriting

The session that produced most of the current `main` **reversed nineteen stated
findings**, enumerated with mechanisms in
`perspectives/2026-08-12-nineteen-reversals-and-what-a-clause-cannot-fix.md`.

The artifacts are sound in their final state — every gate passes and every claim
in a committed file was re-derived before landing. The *narration* was wrong
about nineteen times in transit. So:

- **Trust the tooling output, not the prose describing it.** Run the check.
- **Every count in a handbook page names the commit it was true at.** If it does
  not, treat it as unverified.
- **Four discipline clauses (§7–§10 of the decision-record record) exist to
  prevent exactly these failures, and the failure rate did not fall after they
  landed.** Do not read them and conclude the problem is handled. The
  retrospective argues a fifth clause is the wrong move.

The four mechanisms, so you can recognise them faster than I did: **wrong
reference** (measured against the wrong base/key/file — 5 of 19), **unsettled
state** (a log mid-write, a tree mid-conflict, a baseline not established — 3),
**a flag answering a different question** (4), **interpretation outrunning the
facts** (4).

## What is true about the corpus right now

Verified against `main` at `104361a`, not quoted from a page:

| | |
|---|---|
| Charter | 12 principles; P12 "show it by running it" is newest |
| Records | 13, all `Proposed`. Nothing has ever been ratified |
| Gates that can fail a PR | 8 — seven workflows plus GitGuardian, which is an installed app and appears in no record |
| Enforced at the merge boundary | **nothing.** No ruleset applied, no branch protection, no required check, `CODEOWNERS` inert (16 rules, all `#=`) |
| Project branches | 12, one (`streaming-infrastructure`) with no repository behind it |
| Live docs | `https://quaternionmedia.github.io/qm/`, Pages `build_type=workflow` |

## The three highest-value pieces of work, in order

**1. The slot rule is enforced in exactly one repository, and it is now
unblocked.** Zero of eleven projects carry `one-pr-check.yml`. The fork guide said
"copy all three" seed workflows until #42 corrected it to four, so every fork done
to procedure came up a gate short. The blocker was that the workflow runs
`check_one_pr.py` out of the submodule and every project's pin predated that file
— #43–#53 fixed that, so each `project/*` tip now carries it. Remaining: bump each
project's submodule pin, then copy the fourth workflow in. One PR per project
repository. *Done* is `one-pr-check.yml` present on eleven default branches.

**2. Ten of twelve project branches show a template to their reader.**
`adr/README.md` says "this project's own dedicated branch (`project/<name>`)" —
unsubstituted. `project-seed/ci/check_placeholders.py` (on #56) now refuses this
and `adr-lint.yml` runs it, so those ten branches will go red at their next
propagation, which is the intended prompt. datum is fixed on #57 as the worked
instance. *Done* is the check clean on all twelve.

**3. `handbook/async-contract.md` is still built as session ceremony.** Its rules
— slot, port, identity, dirty tree — are real and load-bearing. The
open/preflight/handoff framing around them is one operator's runbook, of the kind
`AGENTS.md` was rewritten to remove. The owner has flagged this as the direction
and has not approved the edit. *Done* is the page stating rules and pointing at
`adapters/` for any mechanism.

## Standing constraints — these are the owner's, not suggestions

- **No autonomous agent without a direct request**, logged as
  `(start, predicted end, kill time, purpose)`. A workflow was launched
  unprompted in this session and that is why the rule exists.
- **Deterministic composable scripts are the default.** Agent fan-out is
  break-glass. The owner's words: *"too error-prone, time-wasting, and
  unhelpfully sycophantic."* Five workflows spawning ~45 agents produced real
  findings and several of the nineteen reversals.
- **Governance names no product.** Invariants in `AGENTS.md`; vendor glue in
  `adapters/`, optional; nothing vendor-specific in `project-seed/`. A `CLAUDE.md`
  symlinked to `AGENTS.md` is accepted; `.claude/commands` inside the seed is not.
- **Do not tag `main`.** Tags assert human governance has passed.
- **No vendor or model name** in a commit subject or record prose —
  `check_attribution.py` enforces it, exempting code spans, `perspectives/`, and
  any paragraph naming three or more competing vendors.

## Verified findings nobody has acted on

Each reproduced; none fixed. These are the backlog.

- **Nothing is enforced at the merge boundary** (above). Every gate is advisory.
- **Three of the ADR lint's four checks cannot fire** on any ref CI runs against.
- **A project record relaxes a QM record and says so** — `project/qmetronome`'s
  glyph-matrix-SDK draft admits a closed-source binary in the runtime path,
  calling it "a real, accepted departure". Precedence says tighten, never relax.
- **Ruleset E would block `propagate/*`**, the namespace #42 added. It ships
  evaluating, so nothing breaks yet.
- **The generator probes three seed workflows where the corpus requires four**,
  and `harness_status.py` renames filename-presence to `workflows`, so three
  projects report `precondition met` with stale copies.
- **`zensical.toml` is not valid TOML** — `tomllib` rejects line 117, a multi-line
  inline table. zensical's parser accepts it; nothing else will.
- **Ratification has never been performed**, and step 3 of five (renaming
  `DRAFT-<slug>.md` to `QM-NNNN-<slug>.md`) was documented nowhere until the docs
  site got it. It is enforced by a regex. The first ratification will hit it.

## Decisions only the owner can make

1. Eight `fix/*-seed-refresh` branches exist **locally only**, PRs #10–#17 closed
   unmerged. Researched: three carry one real commit each, all superseded by
   #43–#53, and all recoverable from `refs/pull/N/head`. Recommendation was
   delete; not yet done.
2. **alfred #113** (untouched since 2023-12-30) and **benchmark #7** (blocked by
   three required checks from a workflow that has never existed).
3. **Actions is disabled repository-wide on codecartographer**, so #84 has never
   run remotely. Enabling it is the moment CI meets 82 dependabot advisories.
4. **qmcp declares no licence at all** — no `LICENSE`, no `license` key. There is
   no grant to reproduce, which is why its adoption ships without `REUSE.toml`.
5. **Two lightweight tags**, `alfred@v0.2.0` and `datum@v0.0.1`, assert what §6 of
   the version-tags record says a lightweight tag cannot.
6. **`qmcp test --clean` defaults true** and unlinks `./qmcp.db` before and after
   pytest. That file is the pending human-gate queue.

## Traps in this environment that cost real time

- `git merge-tree --write-tree` needs git 2.38; this box has **2.37.3**. Use a
  real merge in a worktree.
- `git show ref:path` returns **empty** without `MSYS_NO_PATHCONV=1`.
- `read_text`/`write_text` translate line endings. Use bytes for anything
  compared or committed.
- `pkill -f` does not reliably kill here, and a process-name pattern will match
  the process doing the matching — a cleanup killed its own shell. Verify the
  port is free rather than trusting the kill.
- `pytest` ignores `testpaths` the moment it is given a path argument, and this
  repo's CI passes two. A `testpaths`-wired suite is collected by nobody.
- `doctest` passes an example that raises nothing and declares no output, so a
  `subprocess.run` against a failing command **passes**.
- A temp path can resolve differently between two calls in one session. Assert the
  extract is non-empty before diffing it.
- `git add -A` re-reads the worktree and will silently undo `update-index`
  changes. Verify symlink modes in `HEAD` *after* committing.

## What is not yours

Ratifying anything. Merging your own work. Cutting a tag. Rewriting another
contributor's commits — #55 carries one whose subject names a model, and it
clears by its author rewording or by a squash merge, not by a force-push.
