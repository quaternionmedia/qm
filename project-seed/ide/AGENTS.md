<!-- SEED FILE: this whole project-seed/ide/ directory mirrors the target
     project's own root layout 1:1 -- copy it recursively onto the project
     root (see README.md's "Forking a new project", step 5) rather than
     copying files one at a time. CLAUDE.md and .github/copilot-
     instructions.md are real symlinks to this file in the seed; a
     symlink-preserving copy (git checkout, `cp -a`/`cp -P`, `rsync -a`)
     carries that forward so an edit to this file alone keeps both current.
     Delete this comment in the copy. Replace every <name> placeholder with
     the project's own name, and fill in project-specific setup and test
     commands below the marked line. The governance section above that line
     is otherwise left untouched: a placeholder is meant to be replaced, and
     a live project file carrying a literal <name> sends its reader to a
     branch that does not exist. -->
# AGENTS.md

This project is governed by the Quaternion Media constitution, vendored at
`governance/qm` (a submodule pinned to this project's `project/<name>`
branch of that repo). If you are an AI coding agent opening this repo with
no other briefing, read this file fully before your first commit or edit.

## Before you do anything

**Run `/cowork` first.** It builds this session's brief from the repository —
the commit you are on, whether your pull request slot is free, what else is in
flight in this clone, which gates exist — instead of letting you inherit a
previous session's beliefs. Other sessions are likely running right now, in
other repositories, for the same reviewer;
`governance/qm/handbook/async-contract.md` is the set of rules that exist only
because of that, and it is short. `/preflight`, `/handoff` and `/status` close the same
loop at the other end.

**Read the corpus's committed status documents before re-deriving what they
hold.** `governance/qm/governance-status.yaml` and
`governance/qm/harness-status.json` each carry their own refresh command and
staleness budget inside the file; `governance/qm/handbook/generated-documents.md`
indexes them. Check the age before quoting a figure.

1. Read `governance/qm/README.md` and `governance/qm/PRINCIPLES.md` in full
   — the namespaces/precedence rules and the charter. Both are short.
2. This project's own decision records live in `governance/qm/adr/` — inside
   the submodule, on this project's own branch, not at this repo's root — as
   `ADR-NNNN` (numbered locally, at ratification) or `DRAFT-*.md` before
   ratification. A human ratifies; you draft.
3. **Everything you produce arrives as a pull request, opened as a draft.**
   Work on a branch and open a PR with `gh pr create --draft` — in this repo,
   and in the `governance/qm` submodule when you touch this project's records
   there. Never commit to, merge into, or push a shared branch directly, and
   never merge your own work, however small or mechanical the change looks.
   If you cannot open a PR, hand the branch back rather than merging it.
   **Draft is load-bearing, and never request a review.** A ready PR against a
   branch carrying `CODEOWNERS` requests review from those owners the moment it
   opens — you name no one, and the notification cannot be recalled. So "open a
   PR for human review", read literally, is the act of pulling a second person
   into work nobody has tested. A draft PR fires none of it. Add the person who
   asked for the work as **assignee**, which is also how you reach them when
   they authored the branch and GitHub therefore refuses a review request on
   it. Leaving draft is their call, made after their own testing.
   **Keep it to one open PR per repository, per contributor.** Not one per
   task. Two PRs that must merge in a given order are a sequencing puzzle
   handed to your reviewer. Land the upstream change first and let propagation
   carry it. `.github/workflows/one-pr-check.yml` enforces this; run
   `governance/qm/project-seed/ci/check_one_pr.py` before you open anything.
4. **Human-only contributorship applies to every commit you make here** (see
   `governance/qm/records/DRAFT-human-only-contributorship.md`): do not add
   yourself, your model name, or any co-author trailer naming an unmonitored
   address (e.g. a vendor `noreply@` address) to any commit. If your default
   tooling normally appends a `Co-Authored-By:` trailer, suppress it for
   this repo. Tool involvement is disclosed as a `Tools:` note where the
   artifact calls for one, never as a byline.
5. Follow the drafting-session handoff contract in
   `governance/qm/adr/README.md` before writing or amending any record.
6. A QM record may be tightened by this project's own records, never
   relaxed — see `governance/qm/README.md`'s "Namespaces and precedence."
7. **Put explanation in one place**, per
   `governance/qm/handbook/style-guide.md`: inline comments carry clarifying
   facts about the code, `README.md` is a shallow onramp to what follows it,
   `docs/` is reference, and **every why goes to a retrospective in
   `governance/qm/perspectives/`**. A record's Context and Alternatives are
   the one exception, answering *why this decision* rather than *why it went
   that way*.
8. Banned in any pre-ratification `DRAFT-*.md` record: "previously",
   "originally", "earlier draft", "re-review", "renumber", "retroactive",
   "supersedes the ... (stance|finding)", "corrected". Drafts are rewritten
   in place, not narrated. The ADR lint enforces this over prose only, so
   quoting the list in a code span is fine.

## One-time setup on a fresh clone (Windows)

`CLAUDE.md` and `.github/copilot-instructions.md` are real symlinks to this
file, not copies — POSIX checkouts resolve them with no setup. On Windows,
enable Developer Mode (Settings → For developers) and run `git config
core.symlinks true` once per clone, then `git checkout -- .` if the files
were already checked out before that. Skipping this doesn't break
anything — the files degrade to one-line pointers containing just the
target path — but it isn't the intended, tested experience; see the
IDE-integrated governance discovery record in `governance/qm/records/` for
what was actually verified.

<!-- Project-specific setup commands, test commands, and conventions belong
     below this line; this seed only carries the governance-discovery part. -->
