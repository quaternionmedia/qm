<p class="qm-eyebrow">usage · a new project</p>

# Forking a new project

How a new project adopts the QM corpus.
{ .qm-lede }

!!! warning "Follow the handbook, not this page"
    This page is an outline. The authoritative procedure — with the exact commands and the check that proves each step worked — is [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md). Do not improvise a lighter version: most adoption defects come from skipped or partial steps.

## Who can take these steps

Step 2 pushes a branch to this repository, and only a maintainer with write access can. An outsider opens an issue or a pull request in the project's own repository, and a maintainer pushes `project/<name>` here on their behalf; the steps after the push are the same for both. A pull request an outside tester opens against this repository is merged by its assignee, a maintainer.

## The eight steps

The [handbook](../ref/glossary.md#handbook){ .glossary-term } numbers the steps 0 through 7. Each has a verification check; run the check rather than assuming the step worked.

**0. Confirm your starting commit.** Check which commit you are forking from, in both repositories.

**1. Add the submodule.** Add this repository as a git submodule at `governance/qm` in the new project.

**2. Create the project branch.** In this repository, create `project/<name>` off `main`. Copy `project-seed/adr/` onto it as a top-level `adr/` directory, then **push the branch** — do not open a pull request for it. This is the one place content arrives on a shared branch by push: the only base a pull request could target is the branch being created, which does not exist yet.

**3. Point the submodule at the branch.** Check out `project/<name>` inside the submodule, commit the updated pointer, and add `branch = project/<name>` to the project's `.gitmodules`.

**4. Wire CI.** Copy the [seed](../ref/glossary.md#seed){ .glossary-term } workflows listed in `project-seed/ci/seed-workflows.txt` into `.github/workflows/`, verbatim: `adr-lint.yml`, `submodule-check.yml`, `reuse-lint.yml` and `one-pr-check.yml` are required, and `leak-check.yml`, `signature-check.yml`, `tag-claims.yml` and `timeless-check.yml` are copied the same way. Run `run_workflows_locally.py` before relying on CI; it names what it needs (`pyyaml`, a signed-in `gh`, an `origin` with `origin/main` fetched) before any step runs. Also wire the license gates the open-license [record](../ref/glossary.md#record){ .glossary-term } requires for the project's runtime shape.

**5. Wire governance discovery.** Copy `project-seed/ide/` recursively onto the project root, using a method that preserves symlinks (`cp -a`, `rsync -a`). Fill in the project-specific sections of `AGENTS.md` and replace the `<name>` placeholders. Check that the project's `.gitignore` does not swallow the copied files.

**6. Seed the first records.** Write the project's first records on its branch as numberless drafts — conventionally an adoption record and a scope record — and list each in `adr/README.md`, on the `Drafts in flight` line or as a table row, or the [ADR](../ref/glossary.md#adr){ .glossary-term } lint refuses it.

**7. [Register](../ref/glossary.md#register){ .glossary-term } carried patches.** If the project carries patches against upstream software, register them in the org-level [registers/carried-patches.md](https://github.com/quaternionmedia/qm/blob/main/registers/carried-patches.md).

## After adoption

- [Next steps](next-steps.md) — [propagation](../ref/glossary.md#propagation){ .glossary-term }, audits, project phases, and the project's page
- [Architecture](../about/architecture.md) — why the structure is this way

## Related

- [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md) — the authoritative procedure
- [Branch namespaces](../ref/namespaces.md) — the rules for the `project/<name>` branch
