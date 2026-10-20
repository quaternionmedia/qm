# Handoff — the families, delineated

**Transient.** Delete this page when its work lands.

## Stamp

Every figure on this page is true at these commits and nowhere else. Re-derive
before quoting — `uv run qm estate --by-family` is the reading.

| repository | ref | commit | date |
|---|---|---|---|
| qm | `origin/main` after #115, which this page landed with; the local stage `test` is level with it | `b958723`, the tip #115 merged | 2026-09-20 |
| the performing estate | every member is public on the host; `uv run qm workspace --family show-control --family instruments --family performer-display` resolves all sixteen when each is cloned at its `qm/<name>` candidate | — | 2026-09-20 |
| dossier, looksatwords | `origin/main`; each also holds a pushed `feat/loose-ends` one commit ahead of `main`, with no pull request | `bd322d3`, `32d3371` | 2026-09-20 |
| golfvs | `docs/rad-defence-ring`, pushed, level with its origin; cloned at its `qm/<name>` candidate | `48dedef` | 2026-09-19 |
| a private roster entry (`private-38` in `ci/workspace-private.yaml`) | `main`, level with its origin; cloned at its `qm/<name>` candidate | `1b86508` | 2026-09-20 |
| rad-godot | `main`, level with its origin; **public since 2026-09-20**; cloned at its `qm/<name>` candidate | `6dd9485` | 2026-09-19 |
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
longer says private, and its candidate paths are the conventions.
`uv run qm private-names --source host` is clean at the stamp; it was red on
`origin/main` at `90a1bd7` with two names in thirteen and three files.

**Every games-family and Godot-adjacent clone resolves at its `qm/<name>`
candidate**; `uv run qm estate --by-family` reads all three present and
clean, and the multi-root workspace was regenerated from the roster
(`uv run qm workspace`).

**Two handoff pages retired**: `the-games-family-and-titanharvest.md` (both
decisions it was blocked on are taken: the branch landed as #111, the
repository exists and is private) and `the-loop-that-checks-itself.md` (the
three commits it stamps are on their repositories' `origin/main`).

**A workspace can be one family, or several.** `uv run qm workspace --family
<name>`, repeatable, narrows the roster to the members of the families asked
for and groups the folders by family in that order. The names are checked
against `families.json`, so a family the record does not declare is refused
rather than resolving to an empty window, and the companion page says which
families were asked for and how many of each resolved. The performing
estate's workspace is the three families named above; every member is public
on the host and clones at its `qm/<name>` candidate, and the run resolves
sixteen of sixteen when they are. The file lands beside the corpus's parent
under a name carrying the families asked for, so it never overwrites the
whole-roster workspace.

**The performing families are counted the same way everywhere they are
counted.** Three, and the same three, in the record's §3, in
`ci/rollout.yaml`'s `performing` phase, in `enact-the-stages.md`, and now in
every sentence of the record that says "the three" or "a fourth" — those were
drafted against an estate of three families and read as the whole table once
it had seven. One had gone false rather than ambiguous: the record called every
member of the performing families unadopted, and `walkthrough/families/`
reads two adopted members in `instruments`. The record now says so, and its
border-counting consequence states the relation rather than a number.

## What is unfinished

- **The workspace opens the performing estate; nothing in it starts a
  member.** Integration testing across `show-control`, `instruments` and
  `performer-display` wants each member's run command where that member
  keeps it — its own `.vscode/tasks.json` or README — not in the roster, which
  holds claims and not commands. ShowRunner's `sr start` binds `:8000` by
  default, and `handbook/async-contract.md` §4 is why no default port is
  bound: pass another and ask the server what it is.
- **"Performing" is a grouping with one machine-readable copy** — the
  `performing` phase of `ci/rollout.yaml` — and prose in the record's §3
  heading. `qm workspace` takes the three names by hand. Whether a group of
  families deserves a name a tool can resolve is a person's call, and a
  second copy of the three names is what #115 declined to add.
- **`feat/loose-ends` in dossier and in looksatwords each carry one commit
  `main` does not**, pushed, with no pull request; both slots are free.
  looksatwords' branch predates `looksatwords/harness.py`, which `qm demo`
  imports from the sibling clone, so a sibling checked out there fails the
  demo's second act on that import and passes on `main`.
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
  unchanged by #115: alfred's pin, the held pull requests, the push of
  `test`.

## Could not be verified (inference)

- The local gate run reproduces the workflows' steps and not `uses:` steps,
  the runner image or secrets. Before the push two steps failed locally with
  one cause — the branch was not on the host: `check_pr_base` says so in its
  own output, and the signature step asks `gh api` for the host's verdict on
  SHAs the host had not seen. After the push every executed step passed
  locally and all nine host checks passed on #114 (E1).

## Standing constraints

- **Not local-only.** Pull requests are fine.
- **In this repository a pull request is merged by a person.** A session opens
  it, gets every gate green, assigns it, and stops. `AGENTS.md` item 3 still
  says the author merges; that disagreement is a person's to settle, and until
  it is, this constraint is the one in force.
- One open pull request per repository, per contributor. This branch is qm's.
