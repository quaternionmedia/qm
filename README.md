# Quaternion Media Constitution

The org-level decision corpus: the philosophies that govern every QM project,
the process that keeps them coherent, and the proven template each new
project forks from. Projects adopt this corpus **by reference** and may
tighten its rules — never relax them.

## Layout

```
qm/
├── README.md            ← this file: namespaces, precedence, fork procedure
├── PRINCIPLES.md        ← the charter: interpretation the records are cut from
├── TEMPLATE.md          ← record template for THIS corpus (QM-XXXX)
├── AGENTS.md            ← governance discovery for any coding agent; CLAUDE.md and
│                           .github/copilot-instructions.md are symlinks to it
├── .github/workflows/   ← this corpus's own CI: the ADR lint, run against its own records
├── .vscode/             ← checked-in settings.json + extensions.json (this record's teeth)
├── records/             ← org records (philosophies); DRAFT-* until ratified
├── registers/           ← org-level live registers (carried patches, …)
├── handbook/            ← business policy routed out of ADR form
├── perspectives/        ← attributed, dated, non-binding opinions; index + response status in perspectives/README.md
├── math/                ← experiments workspace: demonstrations against open questions named in perspectives
└── project-seed/        ← the forkable template a new project's own branch copies verbatim
    ├── adr/              ← README + TEMPLATE, copied onto that project's own project/<name> branch as adr/
    ├── ci/                ← adr-lint.yml (copied into the project's .github/workflows/) and
    │                         adr_lint.py (run in place from the submodule, never copied)
    └── ide/               ← AGENTS.md, CLAUDE.md, copilot-instructions.md, vscode-settings.json,
                              vscode-extensions.json — copied into the project's own root, .vscode/, .github/
```

Each adopting project's own `adr/` directory — its decision records, as
opposed to the org's — lives on a dedicated branch of *this* repo
(`project/<name>`), not copied into the project's own git history. The
project vendors this repo as a submodule and checks out its own branch; see
"Forking a new project" below.

## Namespaces and precedence

- **Org records:** `QM-NNNN`, numbered at ratification by this README's index.
- **Project records:** `ADR-NNNN`, numbered locally per project, starting at 0001.
- **Precedence:** QM records bind all projects. A project record may add
  constraints on top of a QM record; it may not waive one. A genuine
  exception is an *amendment to the QM record*, ratified at org level — never
  a project-level workaround.
- **Adoption by reference:** each project's `adr/` directory lives on its own
  branch of this repo, created from `main`. That branch's ancestry is the
  pin — no separate hash to hand-maintain. Org ratifications and amendments
  propagate by merging `main` into the project's branch — a reviewed commit,
  not an ambient change.

The drafting discipline (squash before ratification, append-only after,
numbering at ratification, one decision per record, banned-vocabulary lint)
is identical at both levels and is itself an org record: see
*Decision-record discipline* in `records/`.

## Forking a new project

The seed is proven — its first instance is the streaming-infrastructure
project, which serves as the reference implementation for a server/container
runtime; `project/qmetronome` (a branch of this repo, not a separate fork)
is the reference implementation of the branch-per-project ADR model below
for a non-server runtime.

**Every step below states how to confirm it worked.** Run the check, do not
infer it from the step having completed without error. Three of the defects
found during alfred's adoption were "did the documented thing, got the wrong
artifact" — a `cp -a` that silently dereferenced a symlink, an ignore rule
that swallowed the files just copied, a step whose instructions were written
by someone for whom they happened to work. A step is done when its check
passes, not when its command exits zero.

0. **Confirm which commit you are forking from**, in both repos. A fork or a
   review performed against a stale branch is a confident claim about code
   nobody is running.
   *Verify:* `git log --oneline -1` and `git status -sb` in each; the project
   repo is on its default branch unless there is a stated reason otherwise.
1. **Add this repo as a submodule** at `governance/qm` in the new project.
   *Verify:* `git submodule status` lists `governance/qm`.
2. **Create branch `project/<name>`** off `main` in this repo. On that
   branch, copy `project-seed/adr/` into a new top-level `adr/` directory
   (README + TEMPLATE, verbatim) — the same copy-verbatim discipline as
   before, now landing on a branch of this repo instead of the new
   project's own repository. Push the branch.
   *Verify:* `git diff --no-index project-seed/adr/TEMPLATE.md adr/TEMPLATE.md`
   is empty, and `adr/README.md` differs from the seed only by the seed
   comment the seed itself says to delete.
3. **Point the submodule at that branch's tip** (checkout the branch inside
   the submodule, commit the updated pointer in the new project); add
   `branch = project/<name>` to the new project's `.gitmodules` so
   `git submodule update --remote` tracks it going forward — the parent
   repo still records an exact commit each time, so builds stay
   reproducible.
   *Verify:* `git submodule status` shows the branch in parentheses, and
   `git config -f .gitmodules --get submodule.governance/qm.branch` returns
   `project/<name>`. Check the recorded URL is the canonical remote and not a
   local path used while setting it up.
4. **Wire CI:** copy `project-seed/ci/adr-lint.yml` into
   `.github/workflows/` verbatim — no project-specific edits needed. Only
   the workflow file is copied; it invokes
   `governance/qm/project-seed/ci/adr_lint.py` from inside the submodule the
   project already vendors, so the lint logic is always the version the
   project's governance pin points at and never a stale copy. Wire the
   license gates required by the open-license record along **every** path
   the project's runtime shape presents — an SBOM per image *and* a
   dependency-manifest gate per package ecosystem, cumulatively, not a
   choice among them (see that record's Enforcement clause) — plus the §6
   service inventory, which no gate can generate. A project without them is
   not instantiated, it is improvised.
   *Verify:* run the lint locally against the project's `adr/` before relying
   on CI — `python governance/qm/project-seed/ci/adr_lint.py --records-dir
   governance/qm/adr` — and confirm each license gate produces a report you
   have actually read. A gate whose output nobody has looked at is a green
   check, not a finding.
5. **Wire IDE-integrated governance discovery:** copy `project-seed/ide/`
   recursively onto the project root — it already mirrors the target layout
   (`AGENTS.md` and `CLAUDE.md` at its own root, `.github/`, `.vscode/`), so
   a symlink-preserving recursive copy (`git checkout`, `cp -a`/`cp -P`,
   `rsync -a`) lands every file at its right final path in one step, no
   per-file renaming. `CLAUDE.md` and `.github/copilot-instructions.md` are
   real symlinks to `AGENTS.md` in the seed, not independent copies of its
   content — a copy method that preserves symlinks carries that forward, so
   editing the project's `AGENTS.md` later keeps both current for free. Fill
   in project-specific setup/test commands below `AGENTS.md`'s marked line;
   the governance section above it stays verbatim, apart from replacing the
   `<name>` placeholders. Before committing, check that the project's
   `.gitignore` does not swallow the files just copied, by asking git rather
   than by reading the ignore file:

   ```sh
   git check-ignore -v AGENTS.md CLAUDE.md .github/copilot-instructions.md \
     .vscode/settings.json .vscode/extensions.json
   ```

   Any path that comes back matched would never have been committed. This
   corpus's own `.gitignore` blanket-excluded `.vscode/`; alfred's excluded
   `*.json` across the whole tree, which swallowed the same two files by a
   completely different rule. Grepping for `.vscode/` finds the first and
   misses the second, which is why the check runs against the seed's actual
   paths. The fix is a negation per swallowed path — `!.vscode/settings.json`,
   `!.vscode/extensions.json` — not deleting the ignore rule outright.

   **On Windows, one one-time step per clone gives the identical result
   POSIX gets for free.** It is spelled out in `AGENTS.md`'s own "One-time
   setup on a fresh clone" section, which is the copy a reader of the new
   project will actually meet; that section is the single source for it,
   rather than a third paragraph saying the same thing. Do it, and confirm
   the pointer files resolve, before treating step 5 as done: a project
   without it is not instantiated, it is improvised — the same standard
   `adr/` and `ci/` are held to. Note that `cp -a` is not always sufficient
   even with the config set — on at least one Windows toolchain it
   dereferenced `CLAUDE.md` into a full copy and failed outright on the
   `.github/` pointer. Verify with `git ls-files -s`, which should show mode
   `120000` for both; if it does not, create them as symlink objects
   directly (`git hash-object -w`, then `git update-index --cacheinfo
   120000,<sha>,<path>`), the same method the record's Consequences
   documents for making the committed object independent of the authoring
   machine.
6. **Seed the first project records** on that branch as numberless drafts
   by title; ratify per process. Project ADR-0001 is conventionally the
   project's adoption + scope record, but nothing enforces a particular
   first decision. **If the project predates its adoption of this corpus**,
   that record's substance is the conflict table required by the
   decision-record-discipline record's adoption clause — every known
   conflict with an org record, what it violates, and what compliance would
   look like. Enumerating a conflict is not waiving it, no schedule is
   required, and scope is frozen per conflict while it stays open. A project
   in that state is instantiated, not improvised: the corpus distinguishes
   projects that carry the governance machinery from those that do not,
   never compliant projects from non-compliant ones.
   *Verify:* every conflict row carries the reproduction that established it,
   per the discipline record's evidence clause, and says how it is pinned. A
   row asserting a defect nobody reproduced is a claim, not a finding.
7. **Register** any carried patches in `registers/carried-patches.md` here —
   the register is org-level by design: a patch carried by one project is a
   commitment made by the org.
   *Verify:* search the project's dependency manifests for build-time sources
   that are not release artifacts — a `git+` URL, a vendored fork, a patch
   applied during build. alfred's had been carried since 2021 and had never
   been offered upstream; nothing surfaced it until someone looked.

A fork onto a materially different project shape than the reference
instance — non-server, non-container, a different language ecosystem —
should expect step 6 to cost real translation effort, not just decision
effort: naming what a "deployment," an "image," or a "control plane" even
means for that shape, before a first record can be written. That cost is
expected overhead, not a signal of poor fit. The org corpus's own origin is
proof this runs both directions: this constitution was itself extracted and
generalized from a single project's experience (the streaming project's,
per `perspectives/session-transcript-2026-06-09.md`) — a first project of a
new class discovering the constitution needs to generalize is exactly how
this corpus is supposed to evolve.

## Ratification

Ratification is a human action at both levels: a commit that flips Status to
Accepted, assigns the number from the index, updates the index, and names the
record in the commit message. Assistants draft; humans ratify.

Ratification is the last human gate, not the only one. **Every change to this
corpus arrives as a pull request**, from a typo fix to a new record, and the
merge is a human's act. Assistants and contributors work on a branch —
`evolve/<slug>`, `perspective/<date>-<slug>`, or the relevant
`project/<name>` — and open a PR; nobody merges their own work into `main`,
and nothing reaches `main` by direct push. The branch protection that makes
this mechanical rather than customary is described in the repository's
rulesets; the rule stands whether or not the tooling is enforcing it on a
given day.

## Index — org records

| # | Title | Status | Date |
|---|---|---|---|
| — | Decision-record discipline | Proposed | 2026-06-09 |
| — | Open-license exclusion and upstream-contribution remediation | Proposed | 2026-06-09 |
| — | Seams on standard protocols | Proposed | 2026-06-09 |
| — | Build the seam, buy the engines | Proposed | 2026-06-09 |
| — | House stack | Proposed | 2026-06-09 |
| — | Contribution and sponsorship policy | Proposed | 2026-06-09 |
| — | Human-only contributorship | Proposed | 2026-07-05 |
| — | IDE-integrated governance discovery | Proposed | 2026-07-05 |

Handbook (policy, not records): public-by-default (with a defined promotion
path to record form), style guide (minimal, legible deliverables).

### Obligations that fall due at ratification

- **Open-license record → the reference project.** When it is Accepted, the
  streaming project's ADR-0001 receives a dated amendment recording
  adoption-by-reference. Its body is untouched; the amendment aligns the
  instance to the doctrine.

### Mechanisms wired ahead of their own record

Some records describe machinery that costs nothing to run before
ratification and protects something in the meantime. Where that is true, the
machinery is live and the record's Status is still Proposed — the two are
independent, and waiting would mean leaving a known gap open for
bookkeeping's sake. Ratification remains a separate human action in every
case.

- **IDE-integrated governance discovery** — this corpus's root carries
  `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and
  `.vscode/settings.json`/`extensions.json`; the pointer files and the shared
  VS Code config are real git symlinks (mode `120000`) to their canonical
  copy in `project-seed/ide/`, so this repo dogfoods the seed rather than
  keeping a second copy. This repo is itself a place a low-context agent gets
  dropped into, and was before the record existed.
- **Human-only contributorship** — `perspectives/README.md`'s index and each
  affected file's header and signature name the accountable human, with tool
  involvement moved to a Tools annotation. Perspectives carry no ratification
  gate, so there was nothing to wait on.
- **Decision-record discipline** — the ADR lint runs in this repo's own CI
  against `records/`, the reference project's `adr/`, and each
  `project/*` branch's `adr/`.
