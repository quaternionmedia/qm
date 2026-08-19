# Handbook — Forking a New Project

**Routing.** Procedure, not a decision record. It carries out the
branch-per-project model described in `docs/about/architecture.md`; the decisions behind it live
in `records/`. Its sibling is `handbook/propagation-runbook.md`, which covers
keeping a project current once it exists — this page is only the first day.

**Read this if** you are standing up a new QM project, or checking whether an
existing one was set up completely. Three of nine adopting projects turned out
to be missing at least one step, so the second use is not hypothetical.

**How proven each third of the seed is, stated honestly, because a forker
inherits the untested parts too.** `adr/` has the most mileage: every adopting
project runs it. Its *first* instance was `project/streaming-infrastructure`,
which is worth discounting rather than citing — there is no
`quaternionmedia/streaming-infrastructure` repository behind that branch, so it
exercised the record format and none of the rest of a fork. The mileage that
counts is the adopting projects. `ci/` was generalized from the working lint in
`project/qmetronome`
and now runs both in this corpus's own CI and in eight adopting projects that
copied it from here — 191 recorded runs across apothecary, datum, qmetronome,
dossier, `private-32`, `private-33`, factorio-sysops and `private-34`. That
sentence used to say it had never run in a copying project, and stayed there
after it stopped being true. `ide/` is the least exercised of the three, and
which projects carry it *can* now be established from here:
`governance-status.yaml` records an `adoption.ide` list per project, read over
the GitHub API rather than from the checkout. Expect the untested parts to need fixes, and
send them back rather than fixing them locally: a copy does not track its
origin.

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
   project's own repository. **Push the branch** — do not open a pull request
   for it. This is the one place in this corpus where content arrives on a
   shared branch by push, and it is not an oversight: the only base such a pull
   request could target is the branch being created, which does not exist yet,
   and targeting `main` instead would merge the new project's `adr/` into the
   org namespace. The branch is permanent from this moment and never merges
   anywhere; every later change to it arrives as a pull request whose *base* is
   this branch. See `docs/ref/namespaces.md`.
   *Verify:* `git diff --no-index project-seed/adr/TEMPLATE.md adr/TEMPLATE.md`
   is empty, and `adr/README.md` differs from the seed only by the seed
   comment the seed itself says to delete. And
   `python project-seed/ci/check_pr_base.py --base main --head project/<name>`
   REFUSES — if it does not, the guard is not in the copy you are running.
3. **Point the submodule at that branch's tip** (checkout the branch inside
   the submodule, commit the updated pointer in the new project); add
   `branch = project/<name>` to the new project's `.gitmodules` so
   `git submodule update --remote` tracks it going forward — the parent
   repo still records an exact commit each time, so builds stay
   reproducible.
   *Verify:* `git config -f .gitmodules --get submodule.governance/qm.branch`
   returns `project/<name>`. That is the configured branch and the only check
   that answers this step.
   **`git submodule status`'s parentheses are not that.** They hold `git
   describe` output for the *pinned commit*, so a pin at the branch tip prints
   `(heads/project/<name>)` and looks like confirmation, while a pin one commit
   behind prints a bare abbreviated sha — codecartographer's reads `(5e1eb04)`
   today with `branch = project/codecartographer` correctly configured. Reading
   the parenthesis as the configured branch makes a stale pin look right and a
   correct one look broken.
   Also check the recorded URL is the canonical remote and not a local path used
   while setting it up.

   **Fixing the URL is half the job; the refs the local clone left behind are
   the half that lies.** Cloning the submodule from a path on disk — the
   natural move when `project/<name>` is not pushed yet — creates
   remote-tracking refs from *that* clone, and re-pointing `origin` at the
   canonical remote does not remove them. What is left is an
   `origin/project/<name>` that no server has ever heard of, frozen at
   whatever commit the branch held at clone time, with the local branch
   tracking it. `git status` inside the submodule then reports `ahead 1` when
   three commits are unpushed, and `check_pr_base` resolves the phantom and
   measures against the wrong base. Both answer confidently.

   ```sh
   git -C governance/qm ls-remote origin 'refs/heads/project/<name>'   # blank = not there
   git -C governance/qm branch --unset-upstream project/<name>
   git -C governance/qm update-ref -d refs/remotes/origin/project/<name>
   git -C governance/qm remote set-head origin main   # the clone copied HEAD too
   ```

   After this the submodule reports no remote counterpart, which is true, and
   `submodule-check.yml` is the thing that tells you when it stops being true.
4. **Wire CI:** copy all four of `project-seed/ci/adr-lint.yml`,
   `submodule-check.yml`, `reuse-lint.yml` and `one-pr-check.yml` into
   `.github/workflows/` verbatim — no project-specific edits needed.
   `one-pr-check.yml` is the org-wide slot rule of `handbook/async-contract.md`
   §1, and its own header says to copy it verbatim like the others; this step
   said "all three" and named it nowhere, so a fork done exactly to procedure
   came up one gate short. Start `reuse-lint` in
   reporting mode; a project that has not had its licensing pass fails it
   immediately, which is useful rather than a reason to leave it out. The submodule check is
   self-contained by necessity: it checks out without submodules, because the
   submodule fetch is the thing it guards, so it cannot run a script from
   inside one. The ADR lint is the other way round — only the workflow file is
   copied; it invokes
   `governance/qm/project-seed/ci/adr_lint.py` from inside the submodule the
   project already vendors, so the lint logic is always the version the
   project's governance pin points at and never a stale copy. Wire the
   license gates required by the open-license record along **every** path
   the project's runtime shape presents — an SBOM per image *and* a
   dependency-manifest gate per package ecosystem, cumulatively, not a
   choice among them (see that record's Enforcement clause) — plus the §6
   service inventory, which no gate can generate. A project without them is
   not instantiated, it is improvised.
   *Verify:* run the whole set locally before relying on CI —
   `python governance/qm/project-seed/ci/run_workflows_locally.py`, which
   executes the workflows' actual steps rather than an approximation of them —
   and confirm each license gate produces a report you have actually read. A gate whose output nobody has looked at is a green
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
   git check-ignore AGENTS.md CLAUDE.md .github/copilot-instructions.md \
     .vscode/settings.json .vscode/extensions.json
   ```

   Any path that comes back would never have been committed; exit 1 with no
   output is the pass. **Run it without `-v`.** With `-v` git prints the
   matching pattern for negations too and exits 0, so a repository that has
   already applied the fix below reads as still broken — the flag that looks
   like it adds diagnostic detail is the one that inverts the answer.

   This corpus's own `.gitignore` blanket-excluded `.vscode/`; alfred's
   excluded `*.json` across the whole tree, which swallowed the same two files
   by a completely different rule; dossier's excluded `.vscode/` again. Grepping
   for `.vscode/` finds the first and misses the second, which is why the check
   runs against the seed's actual paths.

   The fix is a negation per swallowed path — `!.vscode/settings.json`,
   `!.vscode/extensions.json` — rather than deleting the ignore rule outright.
   **A negation alone is not enough when a directory is excluded.** Git will
   not re-include a file whose parent directory is excluded, so `!.vscode/…`
   sitting under a `.vscode/` rule is inert: it changes nothing, reports
   nothing, and looks correct in the diff. Exclude the directory's *contents*
   instead, so git still descends into it:

   ```
   .vscode/*
   !.vscode/settings.json
   !.vscode/extensions.json
   ```

   Verify the negation with the flagless `check-ignore` above, and verify the
   rule still holds by asking about a path it should catch —
   `git check-ignore .vscode/launch.json` must exit 0.

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
   machine. That method is worth reaching for first rather than last: it
   produces a blob whose SHA you can compare against the seed's own
   (`git ls-files -s project-seed/ide/`), which is a stronger check than
   looking at the copy.

   **The submodule is a separate clone and does not inherit `core.symlinks`.**
   Even on a superproject configured correctly, the seed's pointer files
   *inside* `governance/qm` can materialise as one-line text stubs, so a copy
   taken from them lands a regular file containing the string `AGENTS.md`
   where a symlink belongs — and the resulting file reads plausibly enough
   that nothing complains. Run `git -C governance/qm config core.symlinks
   true && git -C governance/qm checkout -- .` after adding the submodule, or
   take the paths from `git ls-files -s` rather than from the working tree.

   If the project already has a real file at one of the seed's pointer paths —
   `.github/copilot-instructions.md` is the likely one — its content is not
   yours to discard. Fold it into `AGENTS.md` below the marked line and then
   make the pointer a symlink, so the project keeps its own instructions and
   gains one place to edit them.
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
   row asserting a defect nobody reproduced is a claim, not a finding. Then
   walk `adr/README.md`'s "What the org records oblige this project to
   produce" table — eight obligations the org records create that nothing
   generates for you, including the baseline component audit, the service
   inventory no scanner can build, and the control-plane record. A project is
   not compliant because it copied the seed.
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
