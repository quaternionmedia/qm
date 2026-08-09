# AGENTS.md — Quaternion Media Constitution

This repository **is** the QM constitution: the org-level decision corpus
every QM project adopts by reference. If you are an AI coding agent opening
this repo with no other briefing, read this file fully before your first
commit or edit — it is short on purpose.

## Before you do anything

1. Read `README.md` (namespaces, precedence, ratification) and
   `PRINCIPLES.md` (the charter) in full. Both are short.
2. This corpus governs its own drafting. Records live in `records/` as
   `DRAFT-*.md` until a human ratifies them (flips Status, assigns a QM
   number, updates the index) — you draft, you never ratify.
3. **Everything you produce arrives as a pull request.** Work on a branch —
   `evolve/<slug>` for org-level work, `perspective/<date>-<slug>` for a
   perspective, `project/<name>` for one project's records — and open a PR
   for human review. Never commit to `main`, never merge into `main`, and
   never push `main` directly, however small, mechanical, or obviously
   correct the change looks. Ratification is not the only human gate; it is
   the last one. A human decides what this corpus says, and the pull request
   is where that decision is made and recorded.
   **Open it as a draft, and never request a review.** `gh pr create --draft`.
   Draft is not a formality here: a ready PR against a branch carrying
   `CODEOWNERS` requests review from those owners the moment it opens, with no
   reviewer named by you and no way to recall the notification. This corpus's
   `main` owns `/project-seed/`, `/.github/workflows/` and `/.github/rulesets/`
   that way, so "open a PR for human review" — read literally, as an agent will
   read it — is the act of pulling a second person into untested work. A draft
   PR fires none of it. Add the person who asked for the work as **assignee**,
   which is also how you reach them when they authored the branch and GitHub
   therefore refuses a review request. Leaving draft is their decision and
   follows their own testing, not your confidence in the diff.
   **A pull request states decisions, not questions.** Settle every input you
   are unsure of *before* you open it: ask in the session and wait for the
   answer. A PR that asks its reviewer what you should have asked earlier
   hands the drafting back to them and calls it review. This is separate from
   a record's `Pends on` row, which names something *the organisation* has
   not settled — that belongs in the record, and a Proposed record naming it
   is the process working. What does not belong anywhere is your own
   unresolved question arriving as PR text.
   **One open PR per repository.** Two PRs that must merge in an order are a
   sequencing puzzle handed to the reviewer. Land the org change first and let
   propagation carry it, rather than opening a second PR that depends on the
   first.
4. **Check what your branch actually carries, before opening the PR.**
   `python project-seed/ci/check_pr_base.py --base <base> --head <branch>`
   reports the merge-base, the commit and file counts, the authors, and any
   commits that also live on another branch. A branch cut from the wrong parent
   passes every other check — its tests are green and its lint is clean,
   because those measure the branch and not where it came from. One PR in this
   org sat open carrying 18 commits of unrelated work under a title describing
   one CI check. Paste the output into the description.
5. **Run the CI locally before you call a pull request ready.**
   `python project-seed/ci/run_workflows_locally.py` executes the workflows'
   actual steps. Reading a workflow and running the commands you think it
   contains is not the same thing, and the difference is where false "CI is
   green" claims come from — the first local run of this repo's own workflows
   failed a step that every hand-run check had passed. Report what you ran and
   what it said, including which steps the runner cannot reproduce. A local
   failure may be a defect or an environment difference — say which you
   established, rather than reporting the exit code.
6. **Human-only contributorship applies to every commit you make here**
   (see `records/DRAFT-human-only-contributorship.md`): do not add
   yourself, your model name, or any co-author trailer naming an unmonitored
   address (e.g. a vendor `noreply@` address) to any commit. If your default
   tooling normally appends a `Co-Authored-By:` trailer, suppress it for
   this repo. Tool involvement is disclosed as a `Tools:` note where the
   artifact calls for one (see `perspectives/README.md`'s Attribution row),
   never as a byline.
7. Follow the drafting-session handoff contract in
   `project-seed/adr/README.md` before writing or amending any record.
8. **Put explanation in one place**, per `handbook/style-guide.md`: inline
   comments carry clarifying facts about the code, `README.md` is a shallow
   onramp to what follows it, `docs/` is reference, and **every why goes to a
   retrospective in `perspectives/`**. A record's Context and Alternatives are
   the one exception, and they answer *why this decision* rather than *why it
   went that way*.
9. Banned in any pre-ratification `records/DRAFT-*.md` document:
   "previously", "originally", "earlier draft", "re-review", "renumber",
   "retroactive", "supersedes the ... (stance|finding)", "corrected".
   Drafts are rewritten in place, not narrated.

## If you're forking this corpus into a new project

See `README.md`'s "Forking a new project" — do not improvise a lighter
version of `adr/`, `ci/`, or this file's own seed copy in
`project-seed/ide/`.

## One-time setup on a fresh clone (Windows)

`CLAUDE.md`, `.github/copilot-instructions.md`, and this repo's own
`.vscode/settings.json`/`extensions.json` are real symlinks, not copies —
POSIX checkouts resolve them with no setup. On Windows, enable Developer
Mode (Settings → For developers) and run `git config core.symlinks true`
once per clone, then `git checkout -- .` if the files were already checked
out before that. Skipping this doesn't break anything — the files degrade
to one-line pointers containing just the target path — but it isn't the
intended, tested experience; see the IDE-integrated governance discovery
record in `records/` for what was actually verified.
