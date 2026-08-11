# Perspective — Reading the Proxy Instead of the Thing

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5, the assistant that made every error catalogued below |
| **Date** | 2026-08-08 |
| **Task** | A retrospective on one long assisted session against this corpus: what the assistant got wrong, what those errors had in common, and which of them a check could have caught. Written from the assistant's own transcript, so the sample is one session and the bias is obvious. |

## 0. Standing, scope, and evidence base

Single-session retrospective. The evidence is one day's work across four
repositories, and every error below is one this session actually made and
caught — usually late, twice only because consolidation forced a second look.
Errors nobody noticed are by definition absent, which is the main reason to
distrust the list's completeness rather than its contents.

What the session produced: 44 commits on `main`, the corpus from 46 to 72
files, 30 pull requests of which 25 were closed as superseded, working CI where
there had been none, and an outbound-licensing record. What it also produced is
below.

## 1. The pattern

Thirteen distinct errors. Twelve of them are the same mistake:

> **Reading a proxy for the thing, and reporting the proxy.**

| The thing | The proxy read instead | What it cost |
|---|---|---|
| The repository | the working tree, on a branch the assistant had just made | "apothecary is the healthiest adoption" — false, and merged to `main` |
| The pull request | the branch, without checking its base | a PR carrying 18 commits of unrelated work under a title describing one CI check |
| The workflow | commands that resembled its steps | four claims of "CI is green" that had never run the pipeline |
| The rendered artifact | the Python model that produced it | every object placed at the origin while the model looked correct |
| The behaviour | a filename | "no ADR lint" in a project that had been running one inline for months |
| The outcome | an exit code, downstream of a pipe | a failing case reported as passing |
| The test | the fact it passed | a negative test that never ran, and so proved nothing |
| The submodule | whichever one sorted first | a false "unreachable pin" for a repo that was fine |
| The command's result | an empty result | three false "absent" findings from a path convention this platform mangles |

The thirteenth is different in kind and worth separating: after re-signing a
branch, the assistant did not consider who was pinning it. That is not reading
a proxy; it is not looking at all.

## 2. The two that reached `main`

Worth naming precisely, because both survived every check that existed.

**The false audit.** The assistant inspected apothecary while its working tree
sat on an unpushed governance branch, and wrote that the project had "every
seed artifact present". `origin/main` had none of them. The claim reached the
handbook and was merged. It was caught nine hours later, by an unrelated
consolidation that forced a comparison against the remote.

**The misbranched pull request.** A branch cut from a feature branch rather
than `main` produced a PR with 46 files under a title describing 3. It sat open
for hours. It was internally consistent, its tests passed, and the local CI
runner reported it green — because all of those measure the branch, and none
measures where the branch came from.

Neither error is detectable by any check the session built. That is the finding.

## 3. What made the errors confident rather than uncertain

Each wrong answer arrived in the shape of a right one.

`git -C /c/Users/...` under Git Bash on Windows does not error. It returns
nothing, which reads exactly like "this path has no such thing". A tool that
fails loudly gets fixed; a tool that fails *empty* gets believed. Three separate
findings were built on that silence before a fourth result was implausible
enough to check.

The same shape recurs: `head -1` on a multi-line result is not an error. A pipe
swallowing an exit code is not an error. A glob matching nothing is not an
error. In each case the machinery produced a well-formed answer to a question
slightly different from the one asked, and nothing in the output said so.

## 4. Where the time actually went

The session's substantive work — the review, the licensing record, the CI, the
runbook, the datum scaffold — was perhaps half of it. The rest divides into two
kinds of overhead, and only one is waste.

**Not waste: finding and fixing the errors above.** Each produced a durable
check or a corrected document. The propagation runbook gained six fixes from
being run once. That is the process working.

**Waste: re-deriving state that had already been established, because it kept
moving.** Branch counts were computed at least six times. Eight seed-refresh
PRs were written against a `main` that changed underneath them and had to be
redone wholesale. A conflict was resolved in a way that passed, then conflicted
again on the next merge, because the resolution converged the branches'
*content* but not their *identity*.

The distinguishing feature of the waste is that nothing recorded **when** a
fact was established or **against which ref**. A finding written as "apothecary
is 58 behind" is stale the moment anything merges; the same finding written as
"58 behind `origin/main` at `4541f92`" is either still true or visibly not.

## 5. Sanity checks worth having

Ordered by how much they would have saved.

**Mechanical, and cheap:**

1. **Assert a PR's base.** Before opening: `git merge-base <base> <head>`, then
   commit count, file count, and the author of each commit. Refuse to open when
   the merge-base is not the base tip. This alone catches §2's second error and
   costs one command.
2. **A control probe on every absence claim.** Any command whose *empty* output
   would be a finding must be run once in the same invocation against a case
   known to be non-empty. `git -C <path> ...` returning nothing means something
   different depending on whether the same call works elsewhere. This is the
   single highest-value habit in this list, because it converts silent failure
   into visible failure.
3. **Seed drift as a check, not a memory.** Assert `adr/TEMPLATE.md` is
   byte-identical to `project-seed/adr/TEMPLATE.md`. Copies do not track their
   origin, and eight PRs went stale on exactly this.
4. **Refuse to commit what a gate generated.** A build artifact in `git status`
   after running a gate locally is not a change; `git add -A` cannot tell.

**Discipline, which no check can supply:**

5. **Every claim names its ref and its time.** "On `origin/main` at `4541f92`"
   rather than "in the corpus". A claim that cannot go stale silently is worth
   more than a claim that is merely correct today.
6. **Verify against the artifact, never the thing that produced it.** The
   rendered SCAD, not the model. The remote, not the working tree. The
   pipeline, not commands resembling it.
7. **A negative test is not a test until seen to fail.** This corpus already
   says so; the session still shipped one that passed vacuously because its
   fixture never initialised.

## 6. What this says about assisted sessions generally, with the usual caveat

One session, one assistant, one corpus — so treat the following as a hypothesis
the next session can falsify rather than a finding.

The errors were not distributed randomly across the work. They clustered
entirely in **claims about state** — what a repo contains, what a branch is
based on, whether a check ran. The *constructive* work in the same session —
records, geometry, the seam design, the lint fixes — produced almost no errors
of this kind, and the ones it did produce (the placement bug) were caught by
tests within minutes.

If that generalises, the useful correction is not "the assistant should be more
careful". It is that **state assertions need mechanical backing in a way that
constructive work does not**, because a wrong constructive claim tends to fail
loudly at the next step, and a wrong state claim propagates silently into
documents, decisions and other people's reviews.

This corpus's evidence standard already says claims of fact name how they were
established. The gap this session found is narrower and more mechanical: a
claim about *which* artifact was inspected, and *when*, is the part that
decays — and it decays invisibly.

## 7. What was not established

- Whether any of the thirteen errors would have been caught by a second
  assistant reviewing, rather than by the same one consolidating.
- Whether the multi-agent review that opened the session was worth its cost.
  It produced 140 verified findings, most of which held; nothing compared it
  against a cheaper approach.
- How many errors remain unfound. The two that reached `main` were both caught
  by accident, which is not a reassuring detection mechanism.

— Peter Kagstrom, drafted with Claude Opus 5, 2026-08-08
