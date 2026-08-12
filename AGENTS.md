# AGENTS.md — Quaternion Media Constitution

This repository **is** the QM constitution: the org-level decision corpus
every QM project adopts by reference. If you are an AI coding agent opening
this repo with no other briefing, read this file fully before your first
commit or edit — it is short on purpose.

## Before you do anything

**Establish four facts about this session before you write anything.** Not
because a command says so — because every one of them has been got wrong here by
inheriting a previous session's belief instead of asking the repository:

1. **The commit you are working against**, and the branch. Every number in every
   page here was true at some commit and nowhere else.
2. **Whether your pull request slot is free.** One open pull request per
   repository, per contributor. `python project-seed/ci/check_one_pr.py --repo
   <owner/name>` answers it.
3. **What else is in flight in this clone** — a dirty tree you did not dirty, a
   sibling branch, an unpushed commit. Other sessions are very likely running
   right now, in other repositories, for the same reviewer.
   `handbook/async-contract.md` is the set of rules that exist only because of
   that, and it is short.
4. **Which gates exist**, and what each one cannot see.
   `python project-seed/ci/run_workflows_locally.py` runs them.

Those are the invariants. **How** you gather them is yours to choose: read the
repository, run the scripts above, or use an adapter if one exists for your
tooling. `adapters/` holds any that do, each named for the product it targets
and none of them required — this corpus states what must be true and does not
name a vendor to get there. See `handbook/async-contract.md` §1 for the
reasoning, and the seams doctrine in `records/` for why a governance document
that mandated a particular product would be violating its own charter.

**Read the committed status documents before re-deriving what they hold.**
`governance-status.yaml` and `harness-status.json` sit at the root.
`harness-status.json` carries its own refresh command, staleness budget and
`do_not` list in a `reading:` block inside the file. **`governance-status.yaml`
does not** — it has no `reading:` block at all, so its refresh command and its
168-hour budget are only in `handbook/generated-documents.md`, and for that one
you do need the page. `handbook/generated-documents.md` indexes both, and
`ci/harness_dashboard.py harness-status.json --format md` renders the second
as prose. Check the age before quoting a figure — a stale number delivered
with a date looks checked.

1. Read `PRINCIPLES.md` (the charter) in full and the three invariants in `README.md`. For depth, see `docs/ref/namespaces.md`, `docs/ref/precedence.md`, and `docs/ref/ratification.md` on the docs site.
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
   Draft is not a formality: a ready PR against a branch carrying a *live*
   `CODEOWNERS` requests review from those owners the moment it opens, with no
   reviewer named by you and no way to recall the notification. So "open a PR for
   human review" — read literally, as an agent will read it — can be the act of
   pulling a second person into untested work. A draft PR fires none of it.
   **In this repository that gun is currently unloaded, and the rule holds
   anyway.** `.github/CODEOWNERS` is inert — all 16 rules carry a `#=` prefix,
   `grep -vc '^#\|^$'` returns 0, and its own first line says so — and
   `gh api repos/quaternionmedia/qm/rulesets` returns `[]`. `main` therefore owns
   nothing and a ready PR here notifies nobody. Do not treat that as permission:
   the file is one `sed` away from live, every project that copies this seed may
   have its own owners, and readiness is the author's claim to make either way. Add the person who asked for the work as **assignee**,
   which is also how you reach them when they authored the branch and GitHub
   therefore refuses a review request. Leaving draft is their decision and
   follows their own testing, not your confidence in the diff.
   **Closing a pull request is a git operation, not just a `gh` command.**
   Pushing a PR's head commits onto its base branch *merges that PR*. GitHub
   detects that the base now contains the head and marks it merged, with the
   pushed commit as the merge commit and whoever pushed as the merger — no
   review, no approval, and no way to undo the record. A later `gh pr close`
   is then a no-op against an already-merged PR, so the operation reports
   success and `--delete-branch` silently does nothing.
   This has happened here. Combining two stacked PRs by fast-forwarding the
   base is the natural move and it converts a close into a merge. **Close the
   PR first, then push**, or retarget it to the outer base before folding it
   in. The order is the whole safeguard.
   **A pull request states decisions, not questions.** Settle every input you
   are unsure of *before* you open it: ask in the session and wait for the
   answer. A PR that asks its reviewer what you should have asked earlier
   hands the drafting back to them and calls it review. This is separate from
   a record's `Pends on` row, which names something *the organisation* has
   not settled — that belongs in the record, and a Proposed record naming it
   is the process working. What does not belong anywhere is your own
   unresolved question arriving as PR text.
   **Never open a pull request from `project/<name>` into `main`.** That branch
   is permanent and takes changes in, never out: it holds how one project's
   governance deviates from this corpus. Merging it moves that project's `adr/`
   into the org namespace, where a local decision reads as an org record binding
   every project — and nothing in the tree looks wrong afterwards, so there is
   no later signal. Records to a project go in *on a PR whose base is
   `project/<name>`*, and each such base holds its own slot. `main`'s changes
   reach it as a `propagate/<name>-<date>` PR against it, merged and never
   rebased, because a downstream submodule pins the tip. The branch's first
   `adr/` content is pushed, not PR'd, because the only base it could target
   does not exist yet — `handbook/forking-a-project.md` step 2.
   `project-seed/ci/check_pr_base.py` refuses the wrong direction, and the
   `docs/ref/namespaces.md` is the canonical statement for branch naming.
   **One open PR per repository, per contributor.** Not one per task. Two PRs
   that must merge in an order are a sequencing puzzle handed to the reviewer.
   Land the org change first and let propagation carry it, rather than opening
   a second PR that depends on the first. `one-pr-check.yml` enforces it and
   `project-seed/ci/check_one_pr.py` is the rule; in *this* repository each
   `project/<name>` branch holds its own slot, because each is pinned by a
   different downstream submodule. That exemption is named in the workflow and
   printed by the tool, and it is the only one.
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
   onramp to the docs site, `docs/` is reference, and **every why goes to a
   retrospective in `perspectives/`**. A record's Context and Alternatives are
   the one exception, and they answer *why this decision* rather than *why it
   went that way*.
9. Banned in any pre-ratification `records/DRAFT-*.md` document:
   "previously", "originally", "earlier draft", "re-review", "renumber",
   "retroactive", "supersedes the ... (stance|finding)", "corrected".
   Drafts are rewritten in place, not narrated.
10. **Check a signal before reading it, and establish a fact before asserting
    it** — `records/DRAFT-decision-record-discipline.md` §7. Every assertion
    that something is broken or behaves a certain way carries the command and
    its output. Before reporting what a result means, name one other thing
    that would produce the same output: a tool version, a flag's semantics,
    stale local state, the working directory, a substring matching prose. Four
    false readings in one session came from skipping that — `merge-tree` on
    git 2.37 read as eight branch conflicts, `check-ignore -v` inverting its
    own verdict, a text scan matching the docstring that forbade it, and a
    document generated from unfetched refs. An unexpected *uniform* result is
    a tooling fault until shown otherwise.
11. **A claim about what facts *mean* names what else could produce them** —
    the same record's §8, and a different failure: every fact true, the
    sentence wrong. Name the ordinary cause before the interesting one, state
    direction and date, and give a correction the same scrutiny as the claim
    it replaces. An overclaim is caught by a reader who knows the provenance;
    a deflation reads as rigour, closes the topic, and can delete something
    real. Recurrence by one practitioner is evidence, not its absence.
12. **The scaffolding you measure with is part of the measurement** — the same
    record's §9. Where item 10 is the tool answering a different question, this
    is the tool being fine and the setup not: nothing errors, and the result
    describes your own scaffolding. In one day here: a diff against files a
    redirect never wrote, reported as 100+ lines of drift when the truth was 0,
    0 and 2; a working tree read after a merge that exited non-zero; copies
    written through a text API that converted every line ending; a mutation test
    whose baseline was already red, so it proved nothing either way; and a
    verdict recomputed from raw fields when the document carried its own.
    **Prefer the artefact you did not create.** Read a document's own answer
    rather than rebuilding one, and assert the intermediate — non-empty, exit
    zero, baseline green — because every one of those was one assertion from
    being caught.
13. **A guard is not finished until someone has tried to route around it** — the
    same record's §10. Breaking it and watching it go red proves it fires on the
    case you thought of; it cannot find the case you did not. Three holes were
    found in one new guard the day it was written: it keyed on the default
    branch, so an intermediate base walked past it; it matched a branch *name*,
    so identical content renamed was clean; and CI ran it in a mode that would
    have failed every legitimate propagation. Ask for a pass whose brief is to
    satisfy the check while doing the thing it forbids. A guard with a hole is
    worse than none — a green check standing where a reader believes something
    is enforced.

14. **Show it by running it** — charter P12, record
    `records/DRAFT-one-executable-walkthrough.md`. A worked example lives in
    `walkthrough/`, executed by the ordinary test command, and nothing describes
    a behaviour in a second place beside the code. What prose cannot hold is
    emitted by the test that asserts the behaviour, and **recorded rather than
    compared**. Regeneration rides the command run before a pull request. The
    evidence is one repository where the artifacts riding that command carry
    zero drift and the two needing a remembered command are stale.

## If you're forking this corpus into a new project

See `docs/usage/first-project.md` and `handbook/forking-a-project.md` — do not improvise a lighter
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
