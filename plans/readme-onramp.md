# Plan — Make `README.md` a human onramp, move depth into `docs/`

## Context

`README.md` is 200+ lines and reads as the constitution itself rather than an
entrance to it. It mixes six kinds of writing: routing, normative reference,
procedure, rationale, corrections of its own past text ("It said 'three of the
nine projects' until the ninth project stopped being the last one"), and
warnings aimed at a future editor rather than a reader. A new contributor has
to finish it to find out where to go.

The corpus already names this as a defect. `handbook/style-guide.md` defines
four tiers: the README carries "a shallow onramp: what this is, how to start,
where to go next" and **never** depth; `docs/` carries "the reference:
contracts, interfaces, procedures, how to use the thing"; test 4 on that page
is "Is the README longer than the thing it introduces is deep?" And
`perspectives/2026-08-09-explanation-in-the-wrong-place.md:65` already
describes this file as "a README a reader finishes rather than passes
through", with `:83` stating the rule as "README is a shallow onramp, `docs/`
is the reference". `AGENTS.md:129` asserts the README *is* a shallow onramp —
currently untrue.

`docs/` was scaffolded for Zensical (empty stubs, `nav` wired, deployed to
GitHub Pages by `.github/workflows/docs.yml`). Nothing in the corpus
references `docs/` yet, so it is a greenfield destination.

**Outcome:** a human who has never seen this repo reads the README in two
minutes, learns what it is and the three rules that constrain them, and leaves
for the one page that answers their question. Agents keep `AGENTS.md`.

## Decisions taken (from review)

1. **The org-records index stays in `README.md` as it is.** No change to
   `.github/workflows/adr-lint.yml` or `TEMPLATE.md`.
2. **`docs/about/` pages are short summaries of the source documents**, each
   with links to its sources. They introduce no rule the source does not state.
3. **Git history holds the displaced rationale.** No new perspective, no
   attribution question.
4. **Links from `docs/` into repo-only material use absolute GitHub URLs**
   (`https://github.com/quaternionmedia/qm/blob/main/…`), because Zensical
   cannot reach outside `docs_dir`.
5. **Section pointers elsewhere get fixed where a target exists; pointers with
   no resolvable target are removed** rather than left dangling.
6. **`README.md` is written for humans; `AGENTS.md` stays the agent entry
   point.** The README mentions agents in exactly one row.

## Approach

### 1. `README.md` — target shape (≈70 lines, seven blocks)

| Block | Content |
|---|---|
| Title + 3 sentences | what this corpus is; adopted by reference; tighten, never relax. Link to the published docs site. |
| **Read this first** | the three invariants, one line each: only `records/` binds; every record is `Proposed`, deliberately; every change arrives as a pull request and nobody merges their own. |
| **Start here** | ~6 audience rows → `PRINCIPLES.md`, `docs/usage/getting-started.md`, `docs/usage/first-project.md`, `docs/ref/`, `governance-status.yaml`, and one row: *working here as a coding agent → `AGENTS.md`*. |
| **Layout** | the tree, one line per top-level entry, no argument. Full annotation lives in `docs/ref/repo-layout.md`. |
| **Index — org records** | unchanged table (CI reads this file), plus two sentences on why every row is `Proposed` and a link to `handbook/governance-rollout.md`. |
| **Contributing** | branch, draft PR, human merge — three lines, linking `docs/ref/namespaces.md` and `handbook/async-contract.md`. |
| **Licence** | one line: `LICENSE`, `LICENSES/`, `REUSE.toml`. |

Everything else is cut. Prose that argues, corrects an earlier version of the
file, or warns a future editor is dropped — git history holds it (decision 3).

### 2. `docs/` — Diátaxis over the existing scaffold

| Scaffold dir | Diátaxis quadrant | Pages |
|---|---|---|
| `docs/about/` | Explanation (summaries, decision 2) | `index.md`, `overview.md`, `architecture.md`, `history.md` |
| `docs/usage/` | Tutorial | `index.md`, `getting-started.md`, `first-project.md`, `next-steps.md` |
| `docs/cookbook/` | How-to | `index.md` + 6 recipes |
| `docs/ref/` | Reference | `index.md`, `repo-layout.md`, `namespaces.md`, `precedence.md`, `ratification.md`, `handbook.md`, `glossary.md` |

- `docs/index.md` — landing: one paragraph on what QM is, the three
  invariants, four cards routing to the quadrants.
- `docs/about/overview.md` — what the corpus is and the four artifact classes
  (records / registers / handbook / perspectives). Summary of `PRINCIPLES.md`
  and the record set.
- `docs/about/architecture.md` — how it hangs together: branch-per-project,
  a project's `adr/` on `project/<name>`, the submodule pin, propagation
  direction. A mermaid diagram (superfences already registers `mermaid`).
- `docs/about/history.md` — how the corpus got here, and that dated rationale
  lives in `perspectives/`; links `perspectives/README.md`'s index.
- `docs/usage/getting-started.md` — first hour: clone, read `PRINCIPLES.md`,
  where the binding documents are, how to open your first change.
- `docs/usage/first-project.md` — the fork walkthrough in outline (submodule at
  `governance/qm`, `project/<name>` branch, copy `project-seed/`, four
  workflows, seed the first records), each step linking the authoritative step
  in `handbook/forking-a-project.md`. States plainly that the eight steps and
  their checks are the handbook's, not this page's.
- `docs/usage/next-steps.md` — propagation, adoption audits, the status
  documents, the phase ladder.
- `docs/cookbook/` recipes: `draft-a-record.md`, `add-a-perspective.md`,
  `propagate-a-change.md`, `read-status-documents.md`, `run-ci-locally.md`
  (`project-seed/ci/run_workflows_locally.py`), `build-these-docs.md`
  (`uv sync`, `uv run zensical serve`, `uv run zensical build --clean`).
- `docs/ref/repo-layout.md` — annotated tree, the `CLAUDE.md` /
  `.github/copilot-instructions.md` symlink note, which files are generated.
- `docs/ref/namespaces.md` — the five-namespace table, the direction table
  ("a `project/<name>` branch takes changes in, never gives them out"), and
  the rule that such a branch is never a PR head. **This becomes the canonical
  statement `AGENTS.md` and two CI tools point at.**
- `docs/ref/precedence.md` — `QM-NNNN` vs `ADR-NNNN`, precedence, adoption by
  reference, and the what-binds table.
- `docs/ref/ratification.md` — ratification mechanics, the every-change-is-a-PR
  rule, and "Obligations that fall due at ratification".
- `docs/ref/handbook.md` — the page → what-it-answers table, absolute links.
- `docs/ref/glossary.md` — record, register, perspective, seed, propagation,
  harness, phase ladder, corpus.

**Anti-duplication rules for every new page**, stated once in
`docs/ref/index.md` and `docs/about/index.md`:

- A `docs/` page never restates a `handbook/` procedure step-by-step; it
  summarises and links.
- Every summary page opens with an admonition naming its source of truth
  (`admonition` is already enabled).
- No count, date, or status figure is written into prose — link the generated
  document instead. This is the specific failure mode the README demonstrates.

### 3. `zensical.toml` nav

Replace the flat `Home` group so the section `index.md` files the scaffold
already ships are used (`navigation.indexes` is enabled), giving five tabs:

```toml
nav = [
    "index.md",
    { "About" = ["about/index.md", "about/overview.md", "about/architecture.md", "about/history.md"] },
    { "Usage" = ["usage/index.md", "usage/getting-started.md", "usage/first-project.md", "usage/next-steps.md"] },
    { "Cookbook" = ["cookbook/index.md", "cookbook/draft-a-record.md", "cookbook/add-a-perspective.md", "cookbook/propagate-a-change.md", "cookbook/read-status-documents.md", "cookbook/run-ci-locally.md", "cookbook/build-these-docs.md"] },
    { "Reference" = ["ref/index.md", "ref/repo-layout.md", "ref/namespaces.md", "ref/precedence.md", "ref/ratification.md", "ref/handbook.md", "ref/glossary.md"] },
]
```

Also uncomment `edit_uri = "edit/main/docs/"` so the enabled
`content.action.edit` feature works.

### 4. Pointer fixes (decision 5)

**In scope** — the target exists after the move:

| Site | Today | Becomes |
|---|---|---|
| `AGENTS.md:32` | "Read `README.md` (namespaces, precedence, ratification)" | the three `docs/ref/` pages by name |
| `AGENTS.md:92` | "README's \"Branch namespaces\" is the canonical statement" | `docs/ref/namespaces.md` |
| `AGENTS.md:129` | "`README.md` is a shallow onramp to what follows it" | keep — now true; name `docs/` as where depth went |
| `AGENTS.md:159` | "See `README.md`'s \"Forking a new project\"" | `handbook/forking-a-project.md`, with `docs/usage/first-project.md` as the outline |
| `.github/CODEOWNERS:22` | "(README.md, \"Ratification\")" | `docs/ref/ratification.md` |
| `.github/workflows/adr-lint.yml:100` | "See the README's \"Branch namespaces\"" | `docs/ref/namespaces.md` |
| `.github/workflows/one-pr-check.yml:30` | same phrase | `docs/ref/namespaces.md` |
| `.github/workflows/namespace-guard.yml:20` | "(see the README's \"Branch namespaces\")" | `docs/ref/namespaces.md` |
| `handbook/forking-a-project.md:4, :57` | "branch-per-project model `README.md` describes", "See the README's \"Branch namespaces\"" | `docs/about/architecture.md`, `docs/ref/namespaces.md` |
| `project-seed/ci/check_pr_base.py:213` | runtime: `See the corpus README's "Branch namespaces".` | `See the corpus's docs/ref/namespaces.md.` — resolvable both here and at `governance/qm/` downstream |
| `project-seed/ci/cowork_context.py:382` | runtime: "the README's \"Branch namespaces\" says why" | same page |
| `project-seed/ide/AGENTS.md:3, :38, :73, :76` | incl. the already-stale `"Namespaces and precedence."` | `docs/usage/first-project.md`, `docs/ref/precedence.md`, `docs/ref/namespaces.md` |
| `project-seed/ide/.vscode/settings.json:2`, `extensions.json:2` | "(see README.md's \"Forking a new project\", step 5)" | `docs/usage/first-project.md`. Root `.vscode/*` are symlinks to these, so one edit each |
| `ci/governance_status.py:86` | comment "See README.md's namespace table" | `docs/ref/namespaces.md` |

No test asserts any of these strings (checked `project-seed/ci/tests/`,
`ci/tests/`), so the runtime-string edits are safe.

**Out of scope, stated in the PR body:**

- `ci/governance_status.py:145,149` — these strings are *emitted into*
  `governance-status.yaml`, and refreshing it needs
  `python ci/governance_status.py --write governance-status.yaml`, which reads
  other repositories. They also carry a substantive claim (the namespace table
  "has four entries") that is a governance finding, not a pointer. Leave to a
  change that can regenerate the document.
- `perspectives/**` — dated opinion. `handbook/style-guide.md` says a
  retrospective "is allowed to age": it says what was true on a day.
- `records/**` — six pointers in
  `records/DRAFT-ide-integrated-governance-discovery.md`. Editing a record is a
  governance act with its own review; raise it, do not fold it into this PR.
- `handbook/handoffs/governance-status-generator.md:130,143` — quotes the
  README as *evidence* for an open finding. Re-point only if the finding is
  still open and the quote still holds; otherwise leave for the handoff's own
  branch.

## Files to modify

- `README.md` — rewrite (shorter)
- `zensical.toml` — nav, `edit_uri`
- `docs/index.md`, `docs/about/{index,overview,architecture,history}.md`,
  `docs/usage/{index,getting-started,first-project,next-steps}.md`,
  `docs/cookbook/index.md` + 6 recipes, `docs/ref/{index,repo-layout,namespaces,precedence,ratification,handbook,glossary}.md`
- `AGENTS.md`
- `.github/CODEOWNERS`, `.github/workflows/{adr-lint,one-pr-check,namespace-guard}.yml`
- `handbook/forking-a-project.md`
- `project-seed/ci/{check_pr_base.py,cowork_context.py}`
- `project-seed/ide/AGENTS.md`, `project-seed/ide/.vscode/{settings,extensions}.json`
- `ci/governance_status.py` (one comment)

## Reuse — existing material to point at, never restate

- `PRINCIPLES.md` — the charter
- `handbook/forking-a-project.md` — eight fork steps, each with its check
- `handbook/propagation-runbook.md` — org change → adopted project
- `handbook/generated-documents.md` — status documents, refresh commands, budgets
- `handbook/async-contract.md` — the multi-session rules
- `handbook/governance-rollout.md` — enforced vs. written-only
- `handbook/style-guide.md` — the tier table this plan executes
- `handbook/adoption-audit-queue.md`, `handbook/public-by-default.md`
- `perspectives/README.md` — index, standing, attribution rules
- `TEMPLATE.md` — record shape, for the draft-a-record recipe
- `ci/governance_render.py`, `ci/harness_dashboard.py --format md` — status views
- `project-seed/ci/run_workflows_locally.py` — local CI recipe
- `.claude/commands/{cowork,handoff,preflight,status}.md` — named, not described

## Constraints the implementation must respect

- `project-seed/ci/adr_lint.py:227-257` scans **every** pipe-table line in
  `--index README.md` and treats a first cell matching `NNNN` / `QM-NNNN` /
  `ADR-NNNN` as an index row. Any new README table must keep a non-numeric
  first column.
- Zensical `docs_dir` must be relative and cannot be `.` — hence decision 4.
- `zensical.toml` `nav` is explicit: an unlisted page is unreachable.
- `REUSE.toml`'s `path = "**"` default covers new `docs/` files (CC-BY-SA-4.0);
  no `REUSE.toml` change needed.
- Work on `evolve/readme-onramp`, one draft PR, assignee = the requester;
  never push `main` (`AGENTS.md`).
- `handbook/style-guide.md` says migration is per-file "rather than a sweep".
  This *is* a one-file sweep, of the file that page names as its failing
  example — say so in the PR body.

## Steps

- [ ] Branch `evolve/readme-onramp`; run `/cowork` first to confirm the PR slot is free
- [ ] Write `docs/ref/` first — `repo-layout.md`, `namespaces.md`,
      `precedence.md`, `ratification.md`, `handbook.md`, `glossary.md`, `index.md` —
      moving the README's reference blocks verbatim where they are already
      neutral, dropping self-corrective prose
- [ ] Write `docs/about/` summaries (`overview`, `architecture`, `history`,
      `index`), each ≤1 screen, each opening with its source-of-truth admonition
- [ ] Write `docs/usage/` tutorial pages, linking `handbook/forking-a-project.md`
      step by step rather than restating it
- [ ] Write `docs/cookbook/` index + 6 recipes
- [ ] Write `docs/index.md` landing page with the four quadrant cards
- [ ] Update `zensical.toml` nav and `edit_uri`
- [ ] Rewrite `README.md` to the seven blocks; keep the records index table byte-identical
- [ ] Apply the in-scope pointer fixes (table above)
- [ ] Verify (below), then open the draft PR noting the three out-of-scope buckets

## Verification

- [ ] `uv run zensical build --clean` succeeds with no warnings about missing nav pages
- [ ] `uv run zensical serve` and click every nav entry; no 404, no empty page
- [ ] Every absolute `github.com/quaternionmedia/qm/blob/main/…` link resolves
      (script it: extract links, check each path exists in the working tree)
- [ ] `python project-seed/ci/adr_lint.py --records-dir records --index README.md` passes
- [ ] `python -m reuse lint` passes
- [ ] `python -m pytest project-seed/ci/tests ci/tests` passes (runtime-string edits)
- [ ] `python ci/governance_render.py governance-status.yaml` still renders
- [ ] `grep -rn "README's \"" --include='*.md' --include='*.py' --include='*.yml' .`
      returns only the four out-of-scope sites
- [ ] `wc -l README.md` ≤ 90
- [ ] Cold read: from `README.md`, reach "how do I fork a project" in two clicks,
      and "what binds me" in one
