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
   repository, per contributor. `uv run qm slot --repo <owner/name>` answers it.
3. **What else is in flight in this clone** — a dirty tree you did not dirty, a
   sibling branch, an unpushed commit. Other sessions are very likely running
   right now, in other repositories, for the same reviewer.
   `handbook/async-contract.md` is the set of rules that exist only because of
   that, and it is short.
4. **Which gates exist**, and what each one cannot see.
   `uv run qm gates` lists them with what each one misses;
   `uv run --extra preflight qm preflight` runs their real steps.

**`uv run qm --help` is the whole surface** — slot, branch, gates, tags, docs,
preflight, brief. It dispatches to the scripts in `ci/` and
`project-seed/ci/` and decides nothing itself, so a command's output is that
script's output and its exit status is that script's status. **In a project
repository the CLI does not exist**: a fork runs the seed scripts in place, out
of `governance/qm/project-seed/ci/`, and installs nothing. `project-seed/ide/AGENTS.md`
is written that way on purpose.

Those are the invariants. **How** you gather them is yours to choose: read the
repository, run the CLI or the scripts directly, or use an adapter if one exists
for your tooling. `adapters/` holds any that do, each named for the product it targets
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
3. **Everything you produce arrives as a pull request, and the pull request is
   an audit record rather than a request for anyone's attention.** Work on a
   branch — `evolve/<slug>` for org-level work, `perspective/<date>-<slug>` for
   a perspective, `project/<name>` for one project's records — open a PR, and
   **merge it yourself once every gate is green.** That is the job: an agent's
   output is a `main` that is clean and working, entered through a pull request
   so the gates ran and the diff stays readable afterwards.
   **Never push `main` directly**, however small, mechanical, or obviously
   correct the change looks. The direct push is the one act that destroys the
   audit record, and nothing downstream can reconstruct it.
   **`main` is not a claim, so merging into it is not a release.**
   `records/DRAFT-version-tags-are-claims.md` §4: `main`, a pull request, a
   working branch and a local build are all drafts — they may be perfectly good
   and they assert nothing. **There are exactly two human gates in this
   corpus**, and the pull request is neither: *ratification*, for what this
   corpus says, and the *version tag*, for what a project ships. A tag asserts
   a human reviewed the change set, a human manually tested it against its real
   runtime, and deterministic automated validation passed. Keeping `main` clean
   is what makes cutting one cheap.
   **Never request a review**, and add the person who asked for the work as
   **assignee**. Reviewers are named at the tag, by the human cutting it. A
   review request pulls a second person into work that asserts nothing yet, and
   against a branch carrying a *live* `CODEOWNERS` it fires the moment the PR
   opens, with no reviewer named by you and no way to recall the notification.
   **Draft means incomplete, and nothing else.** Use it when the work is not
   finished. It is not a holding pen for finished work waiting on a human —
   under the two-gate model there is nobody at the far end of that queue, and
   a green PR left in draft is a change that never reached `main`.
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
   **One open PR per repository, per contributor.** Not one per task. This is a
   sequencing constraint and not a bandwidth one: two PRs that must merge in an
   order are a puzzle, and under the two-gate model a green PR frees its own
   slot in minutes, so the limit binds only on work that is genuinely
   unfinished. Land the org change first and let propagation carry it, rather
   than opening a second PR that depends on the first. `one-pr-check.yml` enforces it and
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

14. **Durable text carries as few integers as it can** — record
    `records/DRAFT-few-integers-in-durable-text.md`. A number in prose is a
    claim with an expiry date, and the prose does not carry the date. Records,
    handbook pages, this file, docstrings and pull request bodies are all read
    long after they are written: prefer the relation to the count ("every
    synced repository", not a total), and where a figure is the point, name the
    command and the commit that produced it. Never restate a figure a generated
    document already holds — `governance-status.yaml` and `harness-status.json`
    carry their own, and a copy is a second number nothing updates. A
    verification section is the one place a bare count belongs, because its
    subject is one run at one commit. This is about text, not code: an
    assertion that goes stale fails, which is the property prose lacks.

15. **Show it by running it** — charter P12, record
    `records/DRAFT-one-executable-walkthrough.md`. A worked example lives in
    `walkthrough/`, executed by the ordinary test command, and nothing describes
    a behaviour in a second place beside the code. What prose cannot hold is
    emitted by the test that asserts the behaviour, and **recorded rather than
    compared**. Regeneration rides the command run before a pull request. The
    evidence is one repository where the artifacts riding that command carry
    zero drift and the two needing a remembered command are stale.

16. **This page is read first, so it restates decisions it does not own** —
    record `records/DRAFT-the-read-document-governs.md`. Precedence says which
    document wins; readership says which document is read, and a decision that
    wins on precedence and loses on readership does not govern. So where a
    passage here summarizes a record, it names that record's path, and the
    record names this page back in its `Restated in` row.
    **When those two disagree, the record is what the organisation decided**
    and the summary is repaired — never the other way round. This exists
    because item 3 above said a pull request was opened "for human review"
    while `records/DRAFT-version-tags-are-claims.md` §4 said `main` asserts
    nothing and the human gate is the tag. Both were true of the tree at the
    same commit, neither looked wrong alone, and a session read this page and
    built a model of the organisation the record contradicted.
    `python ci/check_restatements.py` verifies the declarations pair up. It
    cannot tell that a summary and its record disagree, and it cannot find a
    restatement nobody declared — the declaration is yours to make.

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
