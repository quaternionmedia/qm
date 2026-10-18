# ADR-XXXX — Verify a file's actual consumption path before editing it to fix a flagged issue

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-21 |
| **Pends on** | Whether clauses 2 and 4 generalize into an org-level QM record — left to a maintainer, not decided here. Clauses 1 and 3 are already the org's: the seed's drafting-session contract (`project-seed/adr/README.md`, carried in this project's `adr/README.md`) makes *the source versus the artifact* a verification obligation and makes delivery always a pull request |

## Context

Two near-misses in one session on 2026-07-21 had one shape, and the companion
perspective (`perspectives/2026-07-21-verify-before-fixing.md`) tells them. A
fix was drafted against a repo-root `requirements.txt` believed to be what the
Docker image installs from; and Dependabot bumps to that same file, one of
them a security fix, were merged as fixes. Nothing consumed that file. The
image installs `codecarto/requirements.txt`: `codecarto/Dockerfile` copies
`requirements.txt` from `${CODECARTO_PATH}`, whose default is
`./src/codecarto`, and `docker-compose.yml` passes `./codecarto`. A merged bump
to the dead file changed nothing that runs, while the alert it referenced
could read as addressed.

The shared mechanism: an artifact looked authoritative — the right filename,
a bot vouching for it, a Dockerfile referencing it by variable name — and that
plausibility stood in for tracing the actual build or runtime consumption
path. Two conditions make the shape likely here. No CI job builds the Docker
image or boots the app from it, so a merged change carries no evidence about
that path either way. And the Python dependency set is described twice, by
hand: `pyproject.toml`/`uv.lock` for development and CI, and
`codecarto/requirements.txt` for the image.

## Decision

1. **Before editing a file to resolve a flagged issue against it** — a
   security alert, a Dependabot diff, a lint failure, a bug report — trace
   how that file is actually consumed: grep the repo for its literal
   path/filename, and check any override of a default consumption path (a
   Dockerfile `ARG` default vs. what `docker-compose.yml` or a CI workflow
   actually passes; a config default vs. an environment variable set at
   deploy time) before trusting the file's own header comment, a bot's diff,
   or a default value in isolation.
2. **Where two or more files encode overlapping information about the same
   runtime dependency set** (a lockfile and a hand-maintained requirements
   file; a doc and the code it describes), treat the pairing itself as a
   standing risk, not a settled fact. Either generate one from the other
   mechanically, or record explicitly, near both files, why they must diverge
   and how a maintainer would know if they drifted.
3. **Stage non-trivial fixes on a branch before landing them**, even solo and
   even for something that feels mechanical. A branch is what leaves room to
   catch a wrong premise before it ships, and that room should not depend on
   the fix having been paused for an unrelated reason.
4. **When a review turns up more than one instance of the same category of
   drift**, treat it as a signal to look for the general pattern: the second
   near-miss above surfaced only because the session went looking for more of
   the same shape after the first.

## Consequences

- Slower first response to a bot-flagged issue: a few minutes of tracing
  before editing, every time, even when the fix looks obvious. Accepted — the
  cost of skipping it is a "fix" that silently does nothing while everything
  downstream (a security alert, a status report, a human's mental model)
  believes it worked.
- No mechanical enforcement exists for any of the four clauses; they are an
  instruction to sessions and contributors rather than a CI check. That is a
  known soft spot, not a design choice — see Revision triggers.
- `codecarto/requirements.txt`, the file the Docker build reads, is the
  concrete case clause 2 applies to, and this record does not resolve it. It
  is not generated from `pyproject.toml` or `uv.lock`, it pins nothing, and it
  lists packages `pyproject.toml` does not declare and nothing in `codecarto`
  imports (`matplotlib`, `mpld3`, `nbformat`, `nbconvert`, `motor`).
  `matplotlib` brings Pillow into the image at whatever version is current at
  build time, while `uv.lock` holds no Pillow at all — so a Pillow alert
  against this project is about the image, and no lockfile change answers it.

## Alternatives considered

1. **Trust Dependabot diffs and merge on green CI** — rejected: this repo's CI
   does not build the Docker image or boot the app, so "green" carries no
   evidence for this class of file; that was exactly the gap both near-misses
   went through.
2. **Immediately consolidate every dual-file dependency declaration into one**
   — rejected as this record's scope: `codecarto/requirements.txt` may need to
   keep existing in some form (the Docker base image doesn't ship `uv`), so
   the right consolidation shape is a separate decision; this record is about
   verification discipline, not a mandate to collapse every dual-file setup on
   sight.
3. **Build a CI job that flags unconsumed config files automatically** —
   deferred rather than rejected: real value, but designing and landing it is
   its own piece of work, not a precondition for stating the discipline.
   Named as a revision trigger instead of blocking this record on it.

## Revision triggers

- A future session repeats a mistake this record describes despite the stated
  discipline — the point at which "stated instruction" needs to become a
  mechanical check (a CI grep, a doc-link checker) rather than staying an
  accepted gap, mirroring how `records/DRAFT-human-only-contributorship.md`
  treats its own equivalent soft spot.
- `codecarto/requirements.txt` and `uv.lock`/`pyproject.toml` are unified into
  one generated source — clause 2's standing concern about that specific pair
  becomes moot for that pair.
- A CI job builds the Docker image — clause 1's trace then has a check behind
  it for the image path.
- A repeat drift review turns up zero new findings of this shape twice in a
  row — evidence the practice is working well enough that lighter-weight
  monitoring would suffice.

## Amendments

*None.*
