# QM-XXXX — IDE-Integrated Governance Discovery

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-05 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P11 — governance finds the reader, not the reverse |

## Context

This corpus's only existing discovery mechanism is a human-driven handoff:
`project-seed/adr/README.md`'s "Drafting-session handoff" section lists the
process contract as an input a human is expected to hand a drafting session.
That mechanism depends entirely on a human already knowing to do it, and
doing it, every time — including sessions where the human is new, in a
hurry, or running a different tool than the one that last worked in the
repo.

This repo's own recent history is the counter-evidence, not a hypothetical.
Every commit before Human-only contributorship was drafted carried a
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` trailer — the
exact pattern that record now forbids — not because the rule didn't exist in
spirit, but because nothing put it in front of the assistant before it acted.
It took a human manually walking the assistant through `PRINCIPLES.md`,
`records/`, and `perspectives/` across several conversation turns for the
corpus to register as binding rather than as files that happened to be read
on request.

Separately, the industry has converged on an answer to exactly this problem.
By mid-2026, a plain `AGENTS.md` at repo root is read automatically, with no
briefing required, by every mainstream coding agent — Claude Code, OpenAI
Codex CLI, Cursor, Aider, Devin, GitHub Copilot, Gemini CLI, Windsurf, and
Amazon Q among them. VS Code's own Copilot Chat additionally reads
`CLAUDE.md` and `.github/copilot-instructions.md` the same way, out of the
box, gated by settings (`chat.useAgentsMdFile`, `chat.useClaudeMdFile`,
`chat.instructionsFilesLocations`) rather than by anyone remembering to
paste anything into a prompt. The gap this record closes is not a missing
mechanism industry-wide — it's that this corpus doesn't use the one that
already exists.

## Decision

1. **Every QM repo — this corpus and every adopting project — carries a
   root `AGENTS.md`** as the canonical, tool-agnostic entry point for any
   coding agent, human-directed or automated, that opens the repo with no
   other briefing. Kept to what a low-context agent needs before its first
   action, not a restatement of the whole corpus: what the repo is and that
   it's governed by the QM constitution; the two things Human-only
   contributorship makes an instant violation if unbriefed (no self-crediting
   as author/co-author, no commit trailer naming an unmonitored address);
   and a pointer to `PRINCIPLES.md`, `README.md`'s ratification/precedence
   rules, and the drafting-session handoff contract for anything past a
   first commit.
2. **Tool-specific files are pointers to `AGENTS.md`, never a second copy of
   its content — implemented as real symlinks, treating every OS as capable
   of the same result rather than accepting a lesser Windows experience by
   default.** `CLAUDE.md` and `.github/copilot-instructions.md` at minimum
   are git symlink objects (mode `120000`) targeting `AGENTS.md`. POSIX
   checkouts resolve them with no setup, since git auto-detects symlink
   support at clone time there. Windows checkouts resolve them exactly the
   same way given one one-time, per-clone step — Developer Mode enabled
   (Settings → For developers) and `git config core.symlinks true` — which
   this record's own Consequences confirms actually works, tested on a real
   Windows checkout, not assumed. That one-time step is named directly in
   `README.md`'s fork procedure and in `AGENTS.md` itself, not buried in a
   footnote, because a setup step nobody is told about is indistinguishable
   from a platform that doesn't work. A tool reading `CLAUDE.md` on a
   correctly configured checkout gets `AGENTS.md`'s exact current bytes with
   no second file to keep in sync and no reliance on the reading tool
   following a textual pointer. Only a checkout that skips that one-time
   step, or an environment that blocks Developer Mode outright, falls back to
   a one-line file containing just the relative path — legible to a human
   as a pointer, not silently broken, but not self-explanatory either (see
   Consequences). A new tool convention gets the same symlink treatment when
   it appears; the canonical file never gets rewritten to match a second
   format.
3. **`project-seed/` gains an `ide/` directory that mirrors the target
   project's own root layout exactly** — `AGENTS.md` and `CLAUDE.md` at its
   own root, `.github/copilot-instructions.md`, `.vscode/settings.json`,
   `.vscode/extensions.json` — so a single symlink-preserving recursive copy
   lands every file at its correct final path, the pointer files' relative
   symlink targets resolving correctly both inside the seed and after the
   copy. Copied onto a forking project's root at step 1 of "Forking a new
   project," the same discipline `adr/` and `ci/` already get. A project
   missing it is improvised, not instantiated — the standard `README.md`
   already holds those two to.
4. **VS Code is the org's blessed default editor for this discovery
   mechanism specifically** — not a re-litigation of house-stack's
   language/framework choices, a decision about the delivery layer alone.
   Every project's checked-in `.vscode/settings.json` explicitly sets
   `chat.useAgentsMdFile`, `chat.useClaudeMdFile`, and
   `chat.instructionsFilesLocations`, rather than relying on whatever VS
   Code's shipped defaults happen to be in a given release, and
   `.vscode/extensions.json` recommends `anthropic.claude-code`,
   `GitHub.copilot`, and `GitHub.copilot-chat`. Opening the repo in VS Code
   for the first time — accepting the workspace-trust and
   recommended-extensions prompts, both one-time, per human, per machine —
   is the entire setup. This corpus's own root `.vscode/settings.json` and
   `.vscode/extensions.json` are themselves symlinks to their canonical copy
   in `project-seed/ide/.vscode/` — this repo dogfoods the seed rather than
   keeping an independent copy, so improving the seed improves this repo's
   own live config for free.
5. **Carve-out:** a client- or platform-mandated editor (house-stack's
   existing carve-out logic, extended to the IDE layer) means that project's
   `.vscode/` config is supplementary, not the only path. `AGENTS.md` has to
   work for a human with no IDE plumbing at all, since it's plain text
   readable by a human or any agent regardless of editor — the `.vscode/`
   layer is the convenience mechanism, not the fallback.

## Consequences

- A new project is one clone-and-open away from full governance awareness:
  `git clone`, open in VS Code, accept two prompts, and both a human and any
  agent in that workspace have already been shown the constitution before
  doing anything else — no manual handoff step, no relying on a human to
  remember `adr/README.md`'s existing handoff contract.
- `AGENTS.md` is a second place doctrine can drift from `PRINCIPLES.md` and
  `README.md` if it duplicates their content instead of pointing at it; kept
  short and link-heavy specifically to avoid that, the same pin-by-reference
  preference this corpus already applies to the submodule model over a
  citation.
- One more file class to keep current per project, alongside `adr/` and
  `ci/` — mitigated by the same project-seed verbatim-copy discipline
  already proven for those two.
- Cost accepted: the specific VS Code settings this record pins are VS
  Code's own feature surface and may be renamed or restructured on VS
  Code's schedule, not this corpus's. A revision trigger below, not a
  reason to withhold today's working version.
- A generic `.gitignore` template commonly blanket-excludes `.vscode/`,
  which silently defeats §4 by keeping the checked-in settings from ever
  being committed — this corpus's own `.gitignore` did exactly that until
  drafting this record surfaced it. The fix is `.vscode/*` plus
  `!.vscode/settings.json` and `!.vscode/extensions.json`, not deleting the
  ignore rule outright; `README.md`'s fork-procedure step for this record
  names the same fix.
- **Real symlinks work identically on Windows and POSIX, given one
  documented one-time step per clone: `git config core.symlinks true`, plus
  Windows Developer Mode enabled** (Settings → For developers). POSIX
  checkouts get this for free because git auto-detects symlink support at
  clone time there; Windows needs the explicit config because `core.symlinks`
  is not itself something a repository can ship — it lives in the untracked
  `.git/config`, generated fresh on every clone, so no committed file can
  set it for a future clone. This is the one piece of the discovery
  mechanism that is not "clone and open" alone; `README.md`'s fork-procedure
  step for this record and this corpus's own root `AGENTS.md` both name the
  single command.
- The symlink objects themselves were created via `git hash-object` plus
  `git update-index --cacheinfo 120000,<sha>,<path>` rather than a
  filesystem `ln -s`, so that creating the *committed object* never depends
  on the authoring machine's own `core.symlinks` setting or OS privilege —
  only *checking one out as a live symlink* does, per the bullet above.
  Verified on a Windows machine with Developer Mode on and
  `core.symlinks true` set: `git checkout` materializes real, resolving
  symlinks (`lrwxrwxrwx`), not a text placeholder.
- Without that one-time config (an unconfigured clone, or a CI runner or
  corporate policy that blocks Developer Mode outright), the pointer files
  degrade to a one-line file containing just the relative target path (e.g.
  `AGENTS.md`) rather than resolving to it — legible to a human who thinks
  to open that path, not self-explanatory, and missing the sentence a
  hand-written pointer would have carried. Accepted as a fallback for that
  narrower case, because the failure mode is a visible, inert file, not
  silently missing or wrong content — not accepted as the expected Windows
  experience, since the one-time config closes the gap entirely.

## Alternatives considered

1. **Rely on the human-driven handoff already documented in
   `adr/README.md`** — rejected: this repo's own commit history is the
   counter-evidence. The handoff already existed as documentation, and it
   did not stop an unbriefed assistant from violating Human-only
   contributorship across several real commits, until a human personally
   walked it through the corpus in conversation.
2. **A single tool-specific file (e.g., only `CLAUDE.md`)** — rejected:
   shepherds one vendor's tool and nothing else. The premise here is a model
   that showed up without knowing to look, and it may not be this one.
3. **Editor-agnostic, no IDE-layer wiring at all** — rejected: agnosticism
   is indistinguishable from nobody's one-time setup being targeted. A
   specific, unifying default is what makes "one time" true rather than
   aspirational — the same logic house-stack already applies to language
   choice, applied here to the editor layer.

## Revision triggers

- A coding agent with meaningful QM usage doesn't read `AGENTS.md`
  natively — add its convention as a pointer file, per §2.
- VS Code renames or removes the settings this record pins — update the
  checked-in `settings.json`; the decision (explicit over assumed-default)
  survives even when today's exact keys don't.
- `AGENTS.md` content grows past what a low-context agent will read in
  full before acting — restructure or trim; the format's own convention is
  to stay short.
- The degraded (non-symlink) one-line pointer form is observed confusing a
  reader or agent in practice — reconsider whether the pointer files need a
  short explanatory comment alongside the path, accepting the small
  duplication cost that would reintroduce, rather than staying pure symlink
  or bare-path text.

## Amendments

*None.*
