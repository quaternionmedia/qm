# ADR-XXXX — Verify a file's actual consumption path before editing it to fix a flagged issue

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-21 |
| **Pends on** | Whether this generalizes into an org-level QM record (see the companion perspective, `2026-07-21-verify-before-fixing.md`) — left to a maintainer, not decided here. |

## Context

A single session (2026-07-21) doing routine governance/dependency
maintenance on this repo produced two near-misses of the same shape:

1. A repo-root `requirements.txt` was diagnosed as "what the Docker image
   installs from," and a fix was drafted against that premise. The premise
   was wrong: `codecarto/Dockerfile` copies `requirements.txt` from
   `${CODECARTO_PATH}`, and `docker-compose.yml` overrides that ARG to
   `./codecarto` — the real build reads `codecarto/requirements.txt`, a
   different, unpinned file. The root file turned out to be fully dead:
   referenced by nothing (confirmed by grepping the whole repo for the
   literal string `requirements.txt` and checking every hit). This was
   caught only because the fix was staged on a branch rather than
   committed straight away, giving room for a second look before it
   shipped — not because any deliberate check existed to catch it.

2. Later the same session, seven open Dependabot PRs were triaged and
   merged as "safe" without checking which file each one actually
   touched. Five of the seven — including a Pillow bump patching several
   open high-severity CVEs (a heap out-of-bounds write, an OS command
   injection via `WindowsViewer.get_command()`) — turned out to only
   touch the same dead root `requirements.txt`. Merging them did nothing
   for the real dependency tree (`uv.lock`, still pinned to the
   vulnerable Pillow version); it plausibly caused GitHub's own
   vulnerability-alert tracking to consider the CVEs addressed, since a
   PR referencing them had merged. The real fix (`uv lock
   --upgrade-package pillow`) was only found and applied during a
   *follow-up* review requested separately — not by the triage process
   itself.

Both cases share a mechanism: an artifact looked authoritative — the
right filename, a bot vouching for it, a Dockerfile referencing it by
variable name — and that surface plausibility stood in for tracing the
actual runtime or build consumption path. Contributing conditions:
`codecarto` has no CI gate that exercises the Docker build or boots the
app against it, so a merged PR carries no evidence about that path
either way; and the repo already had two-going-on-three independent,
hand-maintained descriptions of the same Python dependency set
(`pyproject.toml`/`uv.lock`, `codecarto/requirements.txt`, and the
now-deleted root `requirements.txt`), which invites exactly this kind of
split-brain.

## Decision

1. **Before editing a file to resolve a flagged issue against it** — a
   security alert, a Dependabot diff, a lint failure, a bug report — trace
   how that file is actually consumed: grep the repo for its literal
   path/filename, and check any override of a default consumption path
   (a Dockerfile `ARG` default vs. what `docker-compose.yml` or a CI
   workflow actually passes; a config default vs. an environment
   variable set at deploy time) before trusting the file's own header
   comment, a bot's diff, or a default value in isolation.
2. **Where two or more files encode overlapping information about the
   same runtime dependency set** (a lockfile and a hand-maintained
   requirements file; a doc and the code it describes), treat the pairing
   itself as a standing risk, not a settled fact. Either generate one
   from the other mechanically, or record explicitly, near both files,
   why they must diverge and how a maintainer would know if they drifted.
3. **Stage non-trivial fixes on a branch before landing them**, even
   solo and even for something that feels mechanical. The branch is what
   created the room to catch case 1 above before it shipped; that
   shouldn't depend on the fix having been paused for an unrelated
   reason.
4. **When a review turns up more than one instance of the same category
   of drift**, treat it as a signal to look for the general pattern —
   this session's second finding (the Pillow near-miss) would not have
   surfaced without deliberately looking for more of the same shape after
   the first one turned up.

## Consequences

- Slower first response to a bot-flagged issue: a few minutes of
  tracing before editing, every time, even when the fix looks obvious.
  Accepted — the cost of skipping it is a "fix" that silently does
  nothing while everything downstream (a security alert, a status
  report, a human's mental model) believes it worked.
- No mechanical enforcement exists for any of the four clauses above;
  this is, for now, an explicit instruction to future sessions and
  contributors rather than a CI check. That is a known soft spot, not a
  design choice — see Revision triggers.
- `codecarto/requirements.txt` (the file that actually matters to the
  Docker build) is now known to have its own drift from `pyproject.toml`
  (extra `nbformat`/`nbconvert` entries, no version pins, will not pick
  up the `uv.lock` Pillow fix) — this ADR does not resolve that; it's
  named here as the concrete case clause 2 already applies to, left for
  separate follow-up.

## Alternatives considered

1. **Trust Dependabot diffs and merge on green CI** — rejected: this
   repo's CI does not exercise the Docker build or boot the app, so
   "green" carries no evidence for this class of file; that was exactly
   the gap both near-misses exploited.
2. **Immediately consolidate every dual-file dependency declaration into
   one** — rejected as this ADR's own scope: `codecarto/requirements.txt`
   may need to keep existing in some form (the Docker base image doesn't
   ship `uv`), so the right consolidation shape is a separate decision;
   this record is about verification discipline, not a mandate to
   collapse every dual-file setup on sight.
3. **Build a CI job that flags unconsumed config files automatically**
   — genuinely appealing, deferred rather than rejected: real value, but
   designing and landing it is its own piece of work, not a precondition
   for stating the discipline. Named as a revision trigger instead of
   blocking this record on it.

## Revision triggers

- A future session repeats a mistake this record describes despite the
  stated discipline — the point at which "stated instruction" needs to
  become a mechanical check (a CI grep, a doc-link checker) rather than
  staying an accepted gap, mirroring how `docs/qm/records/DRAFT-human-
  only-contributorship.md` treats its own equivalent soft spot.
- `codecarto/requirements.txt` and `uv.lock`/`pyproject.toml` are
  unified into one generated source — clause 2's standing concern about
  that specific pair becomes moot for that pair.
- A repeat drift review (this session's "full review," done again e.g.
  in six months) turns up zero new findings of this shape twice in a
  row — evidence the practice is working well enough that lighter-weight
  monitoring would suffice.

## Amendments

*None.*
