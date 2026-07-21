# Perspective — Toil From Unverified Fixes: A Same-Session Near-Miss, Twice

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Sonnet 5 (Anthropic), the assistant that performed the session this reflects on |
| **Task** | A same-session retrospective on codecartographer dependency/governance maintenance, naming a recurring failure shape (diagnosing a file by its apparent role instead of its traced consumption path) that produced two near-misses in one afternoon, and pointing at a companion project ADR that proposes a concrete discipline for it. |

## 0. Standing and evidence base

Single session, single project, two data points. Both are **E1** — directly
observed in the session this document reflects on, not reconstructed from
memory or inferred from a distance. Where this document generalizes beyond
those two points, it says so.

## 1. What happened

**Near-miss one.** codecartographer had a repo-root `requirements.txt`.
Asked to check dependency health, I diagnosed it as "what the Docker image
installs from" and reported that as fact — it went into a session summary
and into the assistant's own persistent memory as settled. That diagnosis
was wrong. `codecarto/Dockerfile` copies `requirements.txt` from an `ARG`
whose default is overridden by `docker-compose.yml` to a different path;
the real build reads `codecarto/requirements.txt`, a separate, unpinned
file. The root file was fully dead — referenced by nothing in the repo.
This was caught before it shipped, but not because any check existed to
catch it: the fix had been staged on a branch instead of committed
straight to `main`, for an unrelated reason (a maintainer objection to
committing structural changes directly to `main`), and that pause left
room to double-check the Dockerfile before landing anything. Ten minutes
earlier, without that pause, the wrong fix would have gone in clean.

**Near-miss two.** Later the same session, seven open Dependabot PRs were
triaged and merged as routine, safe maintenance — version bumps, no
apparent risk. Five of the seven, it turned out once someone looked,
touched only the same dead root file identified in near-miss one,
including a Pillow bump addressing several open high-severity CVEs (a heap
out-of-bounds write, an OS command injection). Merging those PRs did
nothing to the dependency tree that actually ships — `uv.lock` stayed
pinned to the vulnerable Pillow version — while plausibly causing GitHub's
own vulnerability tracking to consider the alerts addressed, since PRs
referencing them had merged. This was not caught by the triage process. It
surfaced only because a second, broader review was requested afterward,
specifically looking for more instances of the same shape as near-miss
one. Without that second look, five "fixed" security alerts would likely
still read as fixed today.

## 2. The pattern (E4 — inference from two points, so held loosely)

Both near-misses have the same shape: an artifact looked authoritative —
right filename, a bot vouching for it, a Dockerfile referencing it by
variable — and that surface plausibility substituted for tracing where the
artifact actually lands at runtime or build time. Neither was a hard
problem to actually check; both took a few minutes once someone thought to
check. The failure was not in the checking being difficult. It was in
nothing prompting the check in the first place — a clean-looking diff, a
green merge, a plausible one-sentence diagnosis, all read as sufficient on
their own.

Two features of this repo made the trap easier to fall into, worth naming
as contributing conditions rather than excuses: there is no CI gate that
exercises the Docker build or boots the app, so a merged PR carries zero
evidence about that path either way; and the repo held two, briefly three,
independent hand-maintained descriptions of the same Python dependency set
at once. A split-brain config is a standing invitation for exactly this
kind of fix-that-isn't.

## 3. What held up

Worth naming what worked, not just what almost didn't, so it isn't
discarded along with the mistake:

- Staging the fix on a branch instead of committing to `main` directly is
  what created the pause that caught near-miss one — accidentally, in this
  instance, but the mechanism generalizes on purpose.
- Live verification — actually running `pip install`, actually booting the
  FastAPI app and hitting `/openapi.json`, actually running `npm run
  build` against a bumped dependency — produced real evidence and caught
  real problems, faster than reasoning about version ranges in the
  abstract would have.
- Reporting findings and asking before merging, pushing, or closing gave
  a human the chance to redirect before anything shipped irreversibly,
  every time it was tried.

## 4. Proposal

A companion project ADR —
`adr/DRAFT-verify-actual-consumption-before-editing.md` on
codecartographer's `project/codecartographer` branch — turns §3's habits
into a stated discipline rather than something that has to recur by
accident: trace a file's actual consumption path before editing it to fix
a flagged issue; treat any pair of files describing the same dependency
set as a standing risk; stage non-trivial fixes on a branch by default;
and treat a second instance of the same drift shape as a reason to look
for the general pattern, not just patch the specific case. It is Proposed,
not ratified by this document or by the assistant that drafted it — left
for a maintainer.

Whether the underlying discipline is narrow enough to stay
codecartographer-specific, or general enough to belong at the QM level
(other projects in this corpus almost certainly hand-maintain at least one
config/dependency pair with the same split-brain shape), is an open
question this document doesn't resolve. It's named in the companion ADR's
`Pends on` field rather than decided here.

## Limits

This is not independent review — the same assistant performed the
mistakes in §1 and is now the one characterizing them, in the same
session; a reader skeptical of self-serving framing should start there.
It is not a survey — two near-misses in one repo in one afternoon is a
sample size of two, and §2's pattern claim should be weighted accordingly
until it either recurs or gets checked against a different project. And it
is not a request for anything beyond being available for a human to act
on: per this corpus's own rule, a perspective is the most draft-like thing
there is; if the companion ADR is worth ratifying, that is a maintainer's
decision, not a status this document can claim for itself.

— Peter Kagstrom, drafted with Claude Sonnet 5, 2026-07-21
