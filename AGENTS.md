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
3. **Human-only contributorship applies to every commit you make here**
   (see `records/DRAFT-human-only-contributorship.md`): do not add
   yourself, your model name, or any co-author trailer naming an unmonitored
   address (e.g. a vendor `noreply@` address) to any commit. If your default
   tooling normally appends a `Co-Authored-By:` trailer, suppress it for
   this repo. Tool involvement is disclosed as a `Tools:` note where the
   artifact calls for one (see `perspectives/README.md`'s Attribution row),
   never as a byline.
4. Follow the drafting-session handoff contract in
   `project-seed/adr/README.md` before writing or amending any record.
5. Banned in any pre-ratification `records/DRAFT-*.md` document:
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
