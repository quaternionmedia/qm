# Handoff — Enact the stages, and let every tool read the one document

**Routing.** A task somebody can pick up cold. Delete when its work lands.

**Stamped 2026-09-19**, written on `evolve/games-family` against `test` at
`1d96d27`; every commit of that `test` is now on `main` through #110 (`1157fa2`),
and every count and line number below was read at `1d96d27` by the command
named beside it. The lines have not moved; re-run the command before acting on
the number anyway.

**Blocks on a human, for two acts in this order:** clearing the deck — every
repository's pull request slot free, so the re-keying below lands in one pass
rather than queueing behind unrelated work — and then **pushing `test`**.
`records/DRAFT-a-stage-is-recorded-and-main-receives-releases.md` is explicit
that *a pushed stage branch enacts this record; a staged one only prepares it*,
so the push is the decision and it is nobody's but a person's. Everything else
on this page is what the push obliges, and it can be prepared on a branch
before the push and merged after it.

---

## A. What pushing `test` obliges

The record prices this in its Consequences: the enforcement surface keyed on
`main` moves to key on the entry stage, *together*. Read at `test` with

    git grep -n -E "['\"]main['\"]|origin/main|refs/heads/main|--base main|DEFAULT_BRANCH|branches: \[main\]" -- ci/*.py project-seed/ci/*.py .github/workflows/*.yml project-seed/ci/*.yml ci/*.yaml

and filtered to lines that decide something rather than mention it:

| Where | What keys on `main` | Becomes |
|---|---|---|
| `.github/workflows/adr-lint.yml` | `DEFAULT_BRANCH: main` env, and the `adr/`-on-default-branch guard that reads it | the entry stage |
| `.github/workflows/ci-tooling-tests.yml`, `governance-status.yml`, `registries.yml` | `branches: [main]` push triggers; `governance-status.yml` also fetches `+refs/heads/main` by name | the entry stage, and the release stage where a document must describe what is released |
| `.github/workflows/namespace-guard.yml` | `git diff origin/main HEAD` | the pull request's base, which the event already carries |
| `project-seed/ci/adr-lint.yml`, `reuse-lint.yml` | `branches: [main]` — **copied into every adopting project** | the entry stage, then propagated |
| `project-seed/ci/check_pr_base.py` | `--base` default `main` | the entry stage |
| `project-seed/ci/run_workflows_locally.py` | `--ref` and `--base-ref` defaults `main` | the entry stage |
| `project-seed/ci/branch_census.py` | fallback `"main"` when the remote has no HEAD | the entry stage |
| `ci/governance_status.py` | `--corpus-ref` default `origin/main` | the release stage: the status describes what is adopted, and adoption pins releases |
| `ci/harness_status.py` | fallback `"main"` | the entry stage |
| `ci/protocol-registry.yaml` | a signature-check command line naming `origin/main` | the entry stage |
| docstrings in `adr_lint.py`, `check_attribution.py`, `check_signatures.py`, `run_workflows_locally.py` | usage examples naming `origin/main` | the same word the code uses |

**One variable, not eleven edits.** Every row above should read the stage name
from one place — a `ci/stages.yaml` the record's §1 table already implies, with
`entry: test` and `release: main` — so that the day `dev` and `prod` are pushed
is a data change. A script that hard-codes the new name has moved the problem
by one word.

**The tests move with the code, and they must be seen red first.** The same
grep over `ci/tests/` and `project-seed/ci/tests/` finds the fixtures and
assertions that spell `main`. Change the variable before the tests and watch
which ones fail: that list is the coverage, and a test that stays green through
the rename was never testing the branch name.

**Both `AGENTS.md` files say `main`, and the record says that is the trap.**
Root `AGENTS.md` item 3 — *Never push `main` directly*, *your output is a `main`
that is clean and working*, *merge it yourself* — and the seed's item 3 are the
sentences a contributor follows. After the push, a contributor following them
opens a pull request against `main` and every check passes. The sentences
become: the entry stage is where a pull request lands; `main` receives a
release at a tag and takes no pull request. The rule that `main` asserts
nothing (`records/DRAFT-version-tags-are-claims.md` §4) is unchanged.

**Then propagate.** Each `project/<name>` branch and each adopting project's
copied workflows carry `branches: [main]`; `handbook/propagation-runbook.md`
Part B is the procedure, one project at a time, and the roster in
`ci/workspace.yaml` is the list.

**Then break it.** After enactment, open a pull request against `main` and
watch `check_pr_base` refuse it; open one against `test` and watch it pass.
Until both have been seen, the enactment is a belief.

---

## B. The agnostic standard, and what still links to it

The org's stated shape is already the best case: **`AGENTS.md` is the
document**, `CLAUDE.md` and `.github/copilot-instructions.md` are symlinks to
it (mode `120000`, `symlink-integrity.yml` keeps them so), and `adapters/` is
optional sugar that the constitution does not depend on. What changed is that
the tools caught up. Checked on 2026-09-19 against each vendor's own page:

| Tool | Reads | Source |
|---|---|---|
| Codex | `~/.codex/AGENTS.md`, then every `AGENTS.md` from the repository root toward the working directory, concatenated, nearer files later; **32 KiB cap** on the concatenation | learn.chatgpt.com/docs/agent-configuration/agents-md |
| GitHub Copilot (coding agent, code review, VS Code) | `.github/copilot-instructions.md`, **or** `AGENTS.md` anywhere in the tree, nearest wins; path-scoped `.github/instructions/*.instructions.md` with `applyTo` (cloud agent and code review only, on GitHub.com) | docs.github.com …/add-repository-instructions |
| Claude Code | `AGENTS.md` **natively, from v2.1.277**, when no `CLAUDE.md` or `CLAUDE.local.md` exists in the working directory or above; otherwise `CLAUDE.md` only, or `CLAUDE.md` with an `@AGENTS.md` import. Bedrock and telemetry-off sessions cannot read `AGENTS.md` directly and need the import | code.claude.com/docs/en/memory |
| Cursor, Gemini CLI, Zed, Warp, Jules, Devin, Windsurf, and the local-model front-ends **aider, goose, opencode** | `AGENTS.md`, nearest file wins | agents.md |
| A raw local model (Ollama's API, no front-end) | nothing by convention; the seam is the prompt — `AGENTS.md`'s text as the system prompt, which is what the three front-ends above do for you | — |

Root `AGENTS.md` is 16 KiB and the seed's is 12 KiB (`wc -c`, at `test`), so a
project that nests both sits under Codex's cap with room for one more.

### B.1 The link files — three options, one recommended

The symlinks have one failure the root `AGENTS.md` already admits: on a Windows
clone without `core.symlinks`, `CLAUDE.md` is the nine bytes `AGENTS.md`, and a
tool that reads it reads *that* as the whole instruction set. That is not
"degraded"; it is governance silently absent.

| Option | Shape | What it needs | What breaks it |
|---|---|---|---|
| keep the symlinks | status quo | Developer Mode and `core.symlinks` on Windows | any clone that skipped the one-time setup |
| **`CLAUDE.md` as a real one-line file: `@AGENTS.md`** | an import, not a link | nothing — works on every platform and every Claude Code version, including Bedrock | nothing known; the import resolves relative to the file |
| delete the link files | rely on native `AGENTS.md` reading | Claude Code ≥ 2.1.277 on every workstation, no `CLAUDE.local.md` above the repo, and a Copilot check | an older Claude Code reads nothing and says nothing |

**Recommended:** the one-line file for `CLAUDE.md` now — it is strictly more
robust than the symlink and it is the form Claude Code's own page names for
sharing one file with other tools; and deletion for
`.github/copilot-instructions.md` after one verification in VS Code that Copilot
loads `AGENTS.md` in this org (the setting exists; watch it load, do not read
the setting). Either changes `symlink-integrity.yml`'s expected list and
`records/DRAFT-ide-integrated-governance-discovery.md`, which made them
symlinks on purpose — that is a record amendment with the reason, not a quiet
edit, and the seed's `project-seed/ide/CLAUDE.md` follows the same change so
projects inherit it at their next pin bump.

**Verify, do not assume.** In an interactive Claude Code session on a clone
with no `CLAUDE.md`, the line `no CLAUDE.md found; AGENTS.md loaded: …` is the
evidence. With the one-line file, `/memory` lists `AGENTS.md` as imported.

### B.2 One vendor word in the neutral text

`handbook/async-contract.md` §6 opens a session with `/cowork` and closes it
with `/handoff`, and its harness table names `/cowork` again. Those are the
Claude Code adapter's command names, in a policy page that binds every tool.
The vendor-neutral surface already exists — `uv run qm brief` builds the same
document `cowork_context.py` does, and a handoff is a page under
`handbook/handoffs/` — so the fix is wording: name the outcome and the script,
and let `adapters/claude-code/README.md` say which slash command wraps it.
`records/` and the two `AGENTS.md` files are clean on this today (`git grep
-E '/(cowork|handoff)'`); the async contract is the one page.

### B.3 The one genuine cross-tool add: nested `AGENTS.md` for path rules

Every tool in the table reads the **nearest** `AGENTS.md`. That is a
path-scoped rule mechanism that needs no vendor file — where Copilot would want
`.github/instructions/records.instructions.md` and Claude Code `.claude/rules/`
with a `paths` field, a `records/AGENTS.md` carrying the drafting rules (the
banned vocabulary, drafts rewritten in place, the `Restated in` pairing) reaches
all of them at once and only when a session is in that directory. Candidates:
`records/`, `handbook/handoffs/`, `project-seed/`. Keep each small; they
concatenate under Codex's cap.

### B.4 What needs no work

Codex, Cursor, Gemini CLI, the local front-ends: nothing — they read the file.
Adapters for them would be sugar for session commands, and `uv run qm brief`,
`qm slot`, `qm branch`, `qm gates` and `qm preflight` are already the commands;
an adapter that only re-spells them is the thing `adapters/README.md` says not
to depend on.

---

## C. Order of operations for the push-through

**It is phased, and the phases are tracked.** `ci/rollout.yaml` holds the
`stage-enactment` rollout: the steps every repository must pass (`rekeyed`,
`pin-bumped`, `agents-reworded`, `handoff-noted`) and the phases in order —
the corpus alone, then `core`, then `games`, then `irl` and `infra`, then the
three performing families, then the unstated repositories. `uv run qm rollout`
prints every member's position with the claim beside the evidence;
`--next` is the work list for the current phase; `--claim REPO STEP` is how a
person records a step; `--check` refuses a claim the host contradicts; the
committed `status/rollout.yaml` is the host's view. Two of the four detectors
are placeholders until step 2 below names the spelling they look for — the
plan says so in each step's `means`, and until then those rows can only read
`-` or `unverified`. Reorder the phases in the plan, not in your head; the
order is the intention, and the tool reports reality against it.


1. Human: clear the deck — `uv run qm harness` lists every slot; close, merge or fold until each is free.
2. Branch from `test`: `ci/stages.yaml`; the two placeholder patterns in `ci/rollout.yaml` filled in with the spelling the re-keying chose; the rows in §A read it; tests seen red then green; both `AGENTS.md` reworded; the async contract's §6 reworded (B.2); `CLAUDE.md` to a one-line import in root and seed (B.1) with the record amendment; `records/AGENTS.md` (B.3). Gates green locally, with what the runner cannot reproduce named.
3. Human: push `test`. Merge the branch into it through a pull request whose base is `test` — the first one, which is the proof that the re-keyed `check_pr_base` accepts the new base.
4. Break it (§A, last paragraph).
5. Propagate to each `project/<name>` and each adopting project's copies, one at a time, per the runbook; the games family's members are not adopters and are untouched.

## D. What this page does not do

Push anything. Decide the stage question. Amend the IDE-discovery record. Verify
a tool's behaviour from its documentation — every "reads" above is the vendor's
claim until a session has watched it load.
