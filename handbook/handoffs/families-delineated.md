# Handoff — the families, delineated

**Transient.** Delete this page when its work lands.

## Stamp

Every figure on this page is true at these commits and nowhere else. Re-derive
before quoting — `uv run qm estate --by-family` is the reading.

| repository | ref | commit | date |
|---|---|---|---|
| qm | `origin/main` (#114 merged); the local stage `test` is level with it | `f23a875` | 2026-09-20 |
| golfvs | `docs/rad-defence-ring`, pushed, level with its origin; at `repos/qm/golfvs` | `48dedef` | 2026-09-19 |
| a private roster entry (`private-38` in `ci/workspace-private.yaml`) | `main`, level with its origin; at `repos/qm/<name>` | `1b86508` | 2026-09-20 |
| rad-godot | `main`, level with its origin; **public since 2026-09-20**; at `repos/qm/rad-godot` | `6dd9485` | 2026-09-19 |
| a private roster entry (`private-36`) | `origin/project/<name>`, merged with the pre-#110 `main` | `a13f8f2` | 2026-09-19 |
| streaming-infrastructure | `origin/project/streaming-infrastructure`; no repository on the host | `b0265d1` | 2026-08-08 |

## What exists now

**Every reader of the estate can say where one family stands.** Before this
branch the family was visible in `qm families`, `qm rollout` and
`walkthrough/families/`, and in none of the readers that carry state; the
opening survey of this session joined `qm estate` against `families.json` by
hand in a scratch file. Now:

- `uv run qm estate --by-family` groups the survey under one heading per
  family with that family's own totals, unstated last. A private entry is
  called by its reference in the table, as `families.py` and `rollout.py` call
  it, because this reading gets pasted into pages like this one.
- `status/harness.yaml` carries each repository's `family` as the roster
  states it (`null` is unstated), and both harness views render it as a column
  in the repositories and threads tables and add it up in a **By family**
  section.
- `uv run qm cookbook` (no argument) resolves each member's clone through the
  roster, so a member the roster places off-root (`qmetronome`) or names by
  reference is found where the estate finds it. The committed family pages are
  unchanged in shape: they still refuse machine-scoped facts on purpose.
- The session brief reads a single-quoted `generated_at`, which is how
  `status/harness.yaml` writes it; it had been reporting that document's age
  as unknown.

**The roster.** The games family's second member is a private repository and
is now `ref: private-38` with its name and paths in the gitignored companion;
`families.json`, the games pages, `status/rollout.yaml`, the family record's §3
row and every handoff that named it are regenerated or rewritten.
`private-36` and `streaming-infrastructure` — both `project/<name>` branches
the corpus carried and the roster did not — are rostered as `role: project`,
`phase: v0.0.1`, `scaffolded`, with no family claimed. `rad-godot`'s note no
longer says private, and its `../Documents` candidate is gone.
`uv run qm private-names --source host` is clean at the stamp; it was red on
`origin/main` at `90a1bd7` with two names in thirteen and three files.

**Every Godot-adjacent clone is under `repos/qm/`**, where each entry's
`qm/<name>` candidate resolves; `uv run qm estate --by-family` reads all three
present and clean. The multi-root workspace was regenerated from the roster
(`uv run qm workspace`) so the editor reopens them there.

**Two handoff pages retired**: `the-games-family-and-titanharvest.md` (both
decisions it was blocked on are taken: the branch landed as #111, the
repository exists and is private) and `the-loop-that-checks-itself.md` (the
three commits it stamps are on their repositories' `origin/main`).

## What is unfinished

- **Place `private-36` and `streaming-infrastructure` in a family, or say why
  not**, once governance has run for them. That is a `family:` line in
  `ci/workspace.yaml`, by a person. `streaming-infrastructure`'s one record
  calls its codebase `qmstream`; no repository by either name exists on the
  host under this org, which is a question for whoever knows where it went.
- **A check that every `project/<name>` branch has a roster entry does not
  exist.** `status/governance.yaml` reads the branches and saw both; every
  reader of the roster did not, and nothing compared the two. The design
  caveat: with the companion absent (a runner), a private branch name cannot
  be matched to its `ref`, so the check can only run where the companion is,
  or must treat an unmatched *private* branch as unknown rather than
  unrostered.
- **`ci/check_signatures.py --source host` on a commit the host has never
  seen says "could not be checked"**, which is the same word it uses for a
  keyring gap. Locally, before a push, it should say "not on the host". Small,
  and not done.

## Blocked on a person

- Everything `six-branches-reached-origin.md` and `enact-the-stages.md` list,
  unchanged by this branch: alfred's pin, the held pull requests, the push of
  `test`.

## Could not be verified (inference)

- The local gate run reproduces the workflows' steps and not `uses:` steps,
  the runner image or secrets. Before the push two steps failed locally with
  one cause — the branch was not on the host: `check_pr_base` says so in its
  own output, and the signature step asks `gh api` for the host's verdict on
  SHAs the host had not seen. After the push every executed step passed
  locally and all nine host checks passed on #114 (E1).
- The `codex` process seen on this workstation is the ChatGPT extension's
  app-server, started when the editor opened; no second session was found in
  any clone (E1: every tree the estate read was as the previous handoff left
  it). It is not proof there was none.

## Standing constraints

- **Not local-only.** Pull requests are fine; the merge click is the human's,
  by instruction, whatever `AGENTS.md` item 3 says.
- One open pull request per repository, per contributor. This branch is qm's.
