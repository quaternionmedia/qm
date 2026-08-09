# Handoff — The governance status document and its generator

**Goal.** One generated document describing the state of governance across the
org, committed to this repo and regenerated in CI, with a fixture for every
signal in which that signal reports bad.

**Why here and not in the renderer.** Governance semantics — what "behind"
means, when a branch counts as adopted, what makes a record ratified — belong
to the corpus that defines them. A renderer that re-implements them is a second
definition, and drift between two definitions of one rule is the failure this
corpus exists to prevent. The document is the seam; dossier is one reader, a
single-file HTML view is another, a CI threshold job is a third.

Read `handbook/handoffs/README.md` first.

---

## Deliverables

1. `project-seed/ci/governance_status.py` — read-only, `git` and `gh` only.
2. `governance-status.yaml` at the repo root, committed.
3. `project-seed/ci/tests/test_governance_status.py` — the red-path fixtures.
4. A workflow that regenerates it and fails if the committed copy is stale.

## The one design rule

**Every fact carries the ref it was established against, and when.**

*"apothecary is 58 behind"* goes stale silently and gets repeated for days.
*"58 behind `origin/main` at `4541f92`, observed 2026-08-08T14:02Z"* is either
still true or visibly not. A monitor whose facts cannot expire will lie, and
this corpus has already published one that did.

## Shape

```yaml
schema: 1
generated_at: 2026-08-09T09:14:00Z
corpus:
  ref: refs/heads/main
  commit: b94d910
  records: { total: 10, proposed: 10, accepted: 0 }
  ratification_blocked_on: "a second active code owner"

projects:
  - name: apothecary
    branch: { ref: refs/heads/project/apothecary, commit: a6c7afb,
              behind_corpus: 62, last_propagation: null }
    seed:   { template: drift, placeholders: 0 }
    repo:   { url: github.com/quaternionmedia/apothecary, default_branch: main,
              observed_commit: 1ea212d, adopted: false,
              has: [], missing: [gitmodules, agents_md, adr_lint, license] }
    open_prs: [ { number: 29, base: project/apothecary, base_check: pass } ]
    observed_at: 2026-08-09T09:14:00Z
```

Three requirements that are not obvious from the shape:

- **`adopted` is computed from the remote default branch.** Reading a working
  tree is what produced a false "healthiest adoption" finding that reached
  `main`. Use `git cat-file -e origin/HEAD:<path>`, never `ls` or `git ls-files`.
- **`base_check` reuses `project-seed/ci/check_pr_base.py`.** Do not re-derive
  it; call it, or import it.
- **`null` must be distinguishable from "unknown".** `last_propagation: null`
  means *never propagated*, which the generator can establish. If it cannot
  establish something, the field says so rather than guessing. A monitor that
  cannot say "I don't know" will.

### Detecting a propagation, correctly

A propagation merge is one with a parent that is an ancestor of the corpus
branch. **Do not look for merge commits generally** — a project branch merging
its own feature branch produces one too, and reading that as propagation is a
false all-clear on the exact question. That mistake has already shipped here.

## Byte stability, because it is committed

The document is under version control, so an unchanged world must produce an
unchanged file or it churns on every run and becomes noise nobody reads.

- Sort every collection by a stable key. Never rely on filesystem or API order.
- Emit YAML deterministically: fixed key order, no anchors, no flow/block
  drift.
- `generated_at` changes every run by definition. Either exclude it from the
  staleness comparison, or move it into a sidecar the diff ignores — decide
  and say which in the module docstring.

The CI job should fail when the committed copy differs from a fresh
generation *ignoring the timestamp*. A job that fails on the timestamp alone
teaches everyone to ignore it.

## The fixtures are the point

Before any renderer exists. Build them the way
`project-seed/ci/tests/` already does: real throwaway git repositories, not
mocks. These tools are about git, and a mock encodes the same
misunderstanding the tool does and then agrees with it.

Every signal needs a fixture in which it reports bad:

| Signal | Fixture that must make it red |
|---|---|
| `behind_corpus` | a branch genuinely behind the corpus branch |
| `last_propagation` | a branch whose only merge is its own feature branch — must stay `null` |
| `seed.template` | a project `adr/TEMPLATE.md` that differs from the seed |
| `seed.placeholders` | an `adr/README.md` still carrying a literal `project/<name>` |
| `repo.adopted` | a remote default branch with no `.gitmodules` |
| `base_check` | a branch stacked on another branch |
| unknown state | a repo the generator cannot reach — must report unknown, not clean |

That last row is the one that matters most. **A generator that reports a clean
document because its queries returned empty is the failure this whole exercise
is about.** Six defects in this corpus's own tooling were exactly that.

## Verification

```sh
python -m pytest project-seed/ci/tests -q
python project-seed/ci/governance_status.py > /tmp/a.yaml
python project-seed/ci/governance_status.py > /tmp/b.yaml
diff /tmp/a.yaml /tmp/b.yaml     # only generated_at may differ
python project-seed/ci/run_workflows_locally.py
```

## What is not yours here

Deciding what governance *means* — the document reports what the records
already define. If a signal has no definition in `records/`, that is a gap to
report, not one to fill in the generator. Also: no writes to any repo other
than this one, and no `gh` calls that mutate.
