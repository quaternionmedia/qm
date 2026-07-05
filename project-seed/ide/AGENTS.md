<!-- SEED FILE: this whole project-seed/ide/ directory mirrors the target
     project's own root layout 1:1 -- copy it recursively onto the project
     root (see README.md's "Forking a new project", step 5) rather than
     copying files one at a time. CLAUDE.md and .github/copilot-
     instructions.md are real symlinks to this file in the seed; a
     symlink-preserving copy (git checkout, `cp -a`/`cp -P`, `rsync -a`)
     carries that forward so an edit to this file alone keeps both current.
     Fill in project-specific setup/test commands below the marked line;
     leave the governance section above it untouched. -->
# AGENTS.md

This project is governed by the Quaternion Media constitution, vendored at
`governance/qm` (a submodule pinned to this project's `project/<name>`
branch of that repo). If you are an AI coding agent opening this repo with
no other briefing, read this file fully before your first commit or edit.

## Before you do anything

1. Read `governance/qm/README.md` and `governance/qm/PRINCIPLES.md` in full
   — the namespaces/precedence rules and the charter. Both are short.
2. This project's own decision records live in `adr/`, as `ADR-NNNN`
   (numbered locally, at ratification) or `DRAFT-*.md` before ratification.
   A human ratifies; you draft.
3. **Human-only contributorship applies to every commit you make here** (see
   `governance/qm/records/DRAFT-human-only-contributorship.md`): do not add
   yourself, your model name, or any co-author trailer naming an unmonitored
   address (e.g. a vendor `noreply@` address) to any commit. If your default
   tooling normally appends a `Co-Authored-By:` trailer, suppress it for
   this repo. Tool involvement is disclosed as a `Tools:` note where the
   artifact calls for one, never as a byline.
4. Follow the drafting-session handoff contract in `adr/README.md` before
   writing or amending any record.
5. A QM record may be tightened by this project's own `adr/`, never
   relaxed — see `governance/qm/README.md`'s "Namespaces and precedence."

<!-- Project-specific setup commands, test commands, and conventions belong
     below this line; this seed only carries the governance-discovery part. -->
