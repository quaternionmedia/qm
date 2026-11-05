# QM-XXXX — IDE-Integrated Governance Discovery

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-05 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `governance-finds-the-reader` — governance finds the reader, not the reverse |
| **Restated in** | `AGENTS.md`'s "One-time setup on a fresh clone (Windows)" section; `project-seed/ide/AGENTS.md`'s "The instruction files" section; `handbook/forking-a-project.md` step 5; `handbook/async-contract.md`'s table of root pointers; `handbook/governance-rollout.md`'s IDE discovery row; `handbook/propagation-runbook.md` Part B |

## Context

A human-driven handoff is one discovery mechanism:
`project-seed/adr/README.md`'s "Drafting-session handoff" section lists the
process contract as an input a human is expected to hand a drafting session.
That mechanism depends entirely on a human already knowing to do it, and
doing it, every time — including sessions where the human is new, in a
hurry, or running a different tool than the one that last worked in the
repo.

A rule that nothing puts in front of an assistant before it acts is applied
inconsistently: a commit trailer the contributorship record forbids appears on
some commits and not others, which is what an unstated rule produces. Without
a discovery mechanism, the corpus registers as binding only after a human walks
the assistant through `PRINCIPLES.md`, `records/` and `perspectives/` by hand,
and until then it is files that happen to be read on request.

Separately, the industry has converged on an answer to exactly this problem.
A plain `AGENTS.md` at the repository root is read, with no briefing, by every
mainstream coding agent — Claude Code, OpenAI Codex CLI, Cursor, Aider, Devin,
GitHub Copilot, Gemini CLI, Windsurf and Amazon Q among them — and two vendor
pages, both read on 2026-11-01, document the pointer forms this record relies
on. Claude Code's page on project memory (`code.claude.com/docs/en/memory`)
states that a `CLAUDE.md` imports another file with `@path` syntax, that the
path resolves relative to the file holding the import, that imports nest to a
depth of four, and that a `CLAUDE.md` which imports `AGENTS.md` is read with
`AGENTS.md` included through the import; the same page says the tool reads a
root `AGENTS.md` on its own only when no `CLAUDE.md` sits in or above the
working directory, and that some sessions cannot read it that way at all.
GitHub's support matrix for custom instructions
(`docs.github.com/en/copilot/reference/custom-instructions-support`) lists a
repository's `AGENTS.md` as read by Copilot's cloud agent in every client, by
Copilot code review on GitHub.com, by Copilot Chat in VS Code and by the
Copilot CLI, while Copilot Chat in Visual Studio, JetBrains, Eclipse, Xcode and
on GitHub.com reads `.github/copilot-instructions.md` and not `AGENTS.md`. VS
Code gates its own reading of both files behind settings
(`chat.useAgentsMdFile`, `chat.useClaudeMdFile`,
`chat.instructionsFilesLocations`) rather than behind anyone remembering to
paste anything into a prompt. The gap this record closes is not a missing
mechanism industry-wide; it is using the one that exists.

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
2. **A tool-specific instruction file is a pointer to `AGENTS.md`, never a
   second copy of its content, and the pointer is a one-line import.**
   `CLAUDE.md` is a regular file (mode `100644`) holding the single line
   `@AGENTS.md`: the import syntax the tool that reads `CLAUDE.md` documents
   (Context), which expands the named file into the reader's context in place
   of the line, resolving the path relative to the file that holds it. The
   file is the same bytes on every platform and in every checkout, needs no
   filesystem feature, no privilege and no per-clone configuration, and a
   copy of it is as good as the original. No `.github/copilot-instructions.md`
   is carried: the agent, review and VS Code chat surfaces that read it also
   read a root `AGENTS.md` (Context), so the file would say nothing of its
   own; the chat surfaces that read only it are a cost stated in
   Consequences, with the pointer form a project adds when it needs one. A
   tool convention that reads neither `AGENTS.md` nor an import from a file
   it does read gets a pointer in whichever form it reads; the canonical file
   is never rewritten to match a second format.
3. **`project-seed/ide/` mirrors the target project's own root layout
   exactly** — `AGENTS.md` and `CLAUDE.md` at its own root,
   `.vscode/settings.json`, `.vscode/extensions.json` — so a plain recursive
   copy lands every file at its correct final path. Every file in the seed is
   a regular file, so no copy method is special: `cp -r`, `git checkout` and
   a file manager give the same bytes. Copied onto a forking project's root
   at step 5 of `handbook/forking-a-project.md`, the same discipline `adr/`
   and `ci/` already get. A project missing it is improvised, not
   instantiated — the standard that handbook already holds those two to.
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
   `.vscode/extensions.json` are git symlinks (mode `120000`) to their
   canonical copy in `project-seed/ide/.vscode/`, and its `.claude/commands/`
   pages and `.claude/skills/design-review` are symlinks into
   `adapters/claude-code/`: a configuration file has no import syntax, so the
   symlink is the one form in which this repository dogfoods the seed and the
   adapter without a second copy, and improving the seed improves this repo's
   own live config in the same commit. Those symlinks are this repository's
   alone; a project copies the files.
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
  `ci/` — carried by the same project-seed verbatim-copy discipline already
  used for those two, and inheriting that discipline's one real weakness:
  **a copy does not track its origin.** Fixing a defect in the seed does not
  fix the projects already carrying the defective copy, and nothing records
  which seed version any project copied. A seed defect fixed after a project
  copied the seed — an `AGENTS.md` pointing at a root `adr/` that does not
  exist under the branch-per-project model, or an unfilled `project/<name>`
  placeholder — stays live in that project's copy, which is correct as of its
  copy date and wrong as of now, and no mechanism says so. Where a seed
  artifact is executable, running it from the submodule rather than copying
  it removes the problem entirely, which is why the ADR lint is invoked in
  place; prose files have no equivalent and are refreshed by hand or not at
  all.
- The import is followed by the tool that reads `CLAUDE.md` and by nothing
  else. A person opening the file sees one line and has to know that `@`
  names a file to open; a tool that reads `CLAUDE.md` without expanding
  imports gets the line and not the instructions. Accepted: the line names
  the file a reader needs, which is what a pointer is for, and the tool the
  file exists for follows it in every version that reads `CLAUDE.md`.
- Chat surfaces that read `.github/copilot-instructions.md` and not
  `AGENTS.md` (Context names them) get no instructions from a project that
  carries only the seed. Accepted, because §4 names VS Code, whose chat reads
  `AGENTS.md`, and the agent and review surfaces read it from every client. A
  project whose contributors work in one of those chat surfaces adds
  `.github/copilot-instructions.md` as a regular file whose one line names
  `AGENTS.md` as the instructions to read, under §2; the file has no import
  syntax, so that pointer is a sentence rather than an expansion.
- Cost accepted: the specific VS Code settings this record pins are VS
  Code's own feature surface and may be renamed or restructured on VS
  Code's schedule, not this corpus's. A revision trigger below, not a
  reason to withhold today's working version.
- A generic `.gitignore` template commonly blanket-excludes `.vscode/`,
  which silently defeats §4 by keeping the checked-in settings from ever
  being committed. The fix is `.vscode/*` plus
  `!.vscode/settings.json` and `!.vscode/extensions.json`, not deleting the
  ignore rule outright; `handbook/forking-a-project.md` step 5 names the same
  fix.
- The symlinks in §4 keep one failure the import does not have. A Windows
  checkout without `git config core.symlinks true` turns each into a one-line
  text file holding the relative target path, and a commit from such a
  checkout replaces the pointer with a copy that nothing else in CI reads as
  wrong. `.github/workflows/symlink-integrity.yml` refuses a pull request in
  which any of them has a mode other than `120000`, and `AGENTS.md`'s
  "One-time setup on a fresh clone (Windows)" section names the one-time
  step — Developer Mode and the config — for a contributor to this
  repository. A project copies regular files and needs neither.
- A symlink object in §4 is created with `git hash-object -w` and `git
  update-index --cacheinfo 120000,<sha>,<path>` rather than a filesystem
  `ln -s`, so that making the *committed object* never depends on the
  authoring machine's `core.symlinks` setting or OS privilege; only checking
  one out as a live link does.

## Alternatives considered

1. **Rely on the human-driven handoff already documented in
   `adr/README.md`** — rejected: a handoff that exists as documentation does
   not stop an unbriefed assistant from violating Human-only contributorship;
   only a human walking it through the corpus does, every time.
2. **A single tool-specific file (e.g., only `CLAUDE.md`)** — rejected:
   shepherds one vendor's tool and nothing else. The premise here is an agent
   that arrives without knowing to look, and it may be any vendor's.
3. **Editor-agnostic, no IDE-layer wiring at all** — rejected: agnosticism
   is indistinguishable from nobody's one-time setup being targeted. A
   specific, unifying default is what makes "one time" true rather than
   aspirational — the same logic house-stack already applies to language
   choice, applied here to the editor layer.
4. **Git symlinks for the instruction files** — `CLAUDE.md` and
   `.github/copilot-instructions.md` as mode `120000` objects targeting
   `AGENTS.md` — rejected. On POSIX a checkout resolves them with no setup,
   and a tool reading `CLAUDE.md` gets `AGENTS.md`'s exact bytes with no
   second file to keep in sync. The ordinary failure is a Windows checkout
   without `core.symlinks true`, which is what git produces there by default:
   each pointer checks out as a text file holding the relative path, a tool
   that reads it reads a path as the whole instruction set, and nothing but
   the symlink gate notices — governance silently absent on exactly the clone
   that skipped a one-time step nothing enforces. A submodule is a separate
   clone and does not inherit the setting, so a project copying the seed out
   of `governance/qm` can land a text stub where a symlink belongs, and the
   stub reads plausibly enough that nothing complains. The import has no such
   mode: it is the same bytes in every checkout, and the tool that reads it
   follows it.
5. **Carrying `.github/copilot-instructions.md` as a one-line text pointer**
   — rejected for the seed: the surfaces the seed configures read `AGENTS.md`
   directly, so the file would be a second instruction file whose whole
   content is a sentence saying to read the first. Available to a project
   that needs it, per Consequences.
6. **No pointer file at all, relying on native `AGENTS.md` reading** —
   rejected: the tool that reads `CLAUDE.md` reads `AGENTS.md` on its own
   only from a given version and not in every session (Context), and an
   older client reads nothing and says nothing. The import costs one file of
   one line and works in every version that reads `CLAUDE.md`.

## Revision triggers

- A coding agent with meaningful QM usage reads neither `AGENTS.md` nor an
  import from a file it does read — add its convention as a pointer file,
  per §2.
- The tool that reads `CLAUDE.md` changes or withdraws the `@path` import
  syntax — the pointer form in §2 is reconsidered against whatever that tool
  then documents.
- A chat surface that reads `.github/copilot-instructions.md` and not
  `AGENTS.md` comes into meaningful use on a QM project — the seed gains the
  file as a one-line pointer, per §2 and Consequences.
- A defect is fixed in `project-seed/ide/` — every existing adopter is
  carrying the unfixed copy, and there is no list of who they are. Either
  refresh them deliberately or accept, in writing, that the seed and the
  projects have diverged.
- VS Code renames or removes the settings this record pins — update the
  checked-in `settings.json`; the decision (explicit over assumed-default)
  survives even when today's exact keys don't.
- `AGENTS.md` content grows past what a low-context agent will read in
  full before acting — restructure or trim; the format's own convention is
  to stay short.
- A pull request lands one of §4's pointers as a regular file with the
  symlink gate green — the gate has a hole, and it is read for the hole
  before the pointer is restored.

## Amendments

*None.*
