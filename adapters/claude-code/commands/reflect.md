---
description: Close a governed session — record break observations and surface counterfactual history.
argument-hint: [optional: what you were asked to do]
---

Close the session and record what went wrong, so the next session starts with
that history. **Do not commit, push, or open anything during this command.**
It ends with a summary of break observations and any coverage gaps that need a
human decision before the next PR.

The task, if one was given: **$ARGUMENTS**

## 1. Enumerate breaks

List every break from this session. A break is: a clause of `AGENTS.md`,
`handbook/async-contract.md`, or the session's own tool contract was violated,
or a false statement was made to the reviewer. Not a refinement — a violation.

For each break, state:

- `pattern_id` — the slug from `ci/pattern-registry.yaml`. If no existing slug
  fits, write `"new-pattern"` and note what it should be added as.
- `clause` — the clause violated
- `caught_by` — one of `mechanical-check`, `manual`, `reviewer`
- `path_taken` — what was done, and what the outcome was (be specific)
- `path_avoided` — what should have been done, and what it would have produced
  (be specific — "no problems" is not an outcome; the deflation principle applies)
- `shape.type` and `shape.context` — from `ci/shape-registry.yaml`
- `cost` — commits required, attention level, agency taken from the reviewer

If there were no breaks, write `breaks: []` and continue.

## 2. Write the artifact

Create a YAML file at `perspectives/artifacts/YYYY-MM-DD-BRANCH.yaml` with the
structure below, then validate it:

```yaml
date: "YYYY-MM-DD"
branch: "BRANCH-NAME"
repo: "owner/repo"
breaks:
  - pattern_id: ...
    clause: ...
    caught_by: ...
    path_taken:
      action: ...
      outcome: ...
    path_avoided:
      action: ...
      outcome: ...
    shape:
      type: ...
      context: ...
      reversibility: low|medium|high
      decision_pressure: implicit|explicit|asked
    cost:
      commits: N
      attention: low|medium|high
      time: low|medium|high
      agency: none|... (what was taken without asking)
artifacts_produced:
  - "owner/repo#N"
```

Validate:

```
python ci/session_record.py \
  --input perspectives/artifacts/YYYY-MM-DD-BRANCH.yaml \
  --out   perspectives/artifacts/YYYY-MM-DD-BRANCH.yaml \
  --registry-dir ci/
```

If the output contains `unknown:` fields, fix them before continuing. A
`path_avoided.outcome: {unknown: ...}` means you have stated a path without
saying what it would have produced — that is a claim without evidence.

## 3. Update the indexes

```
python ci/pattern_index.py \
  --artifacts perspectives/artifacts \
  --write perspectives/artifacts/pattern-index.json \
  --registry-dir ci/

python ci/shape_index.py \
  --artifacts perspectives/artifacts \
  --write perspectives/artifacts/shape-index.json
```

## 4. Check coverage

```
python ci/check_pattern_coverage.py \
  --index perspectives/artifacts/pattern-index.json
```

If this exits 0: the session is clean. Close with `/handoff`.

If this exits 1: one or more patterns above threshold have no mechanical check.
You have three options, and the reviewer decides which:

- **Draft a check** — create `ci/checks/<pattern>.py`, mark the pattern
  `check_exists: true` in `ci/pattern-registry.yaml`, and include both in the PR.
- **Approve the gap** — add a stated reason to the registry:
  `check_exists: "deferred-YYYY-MM-DD-reason"`. This is recorded and visible
  in the dossier dashboard; a pattern with three deferrals stays in WARN.
- **Defer** — do nothing this session. The pattern remains uncovered.
  Note: defer is not the same as clean. The gap will surface again at `/cowork`.

## 5. Surface the counterfactual history

```
python ci/counterfactual_query.py \
  --from perspectives/artifacts/YYYY-MM-DD-BRANCH.yaml \
  --index perspectives/artifacts/shape-index.json
```

Read the output. For each shape recorded this session, it shows what happened
the last time someone was in that situation — path taken, path avoided, cost.
This is not feedback to the session that just ran; it is input to the next one.

## 6. Close

Close with `/handoff`. State:

- the break count and whether any reached the reviewer
- the coverage gate result
- any patterns newly above threshold with no check (for human decision)

Do NOT commit the `perspectives/artifacts/` files. They are ignored by git
(see `.gitignore`) and are machine-scoped observations, not corpus documents.
