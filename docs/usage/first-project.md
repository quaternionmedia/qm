# Forking a new project

How a new project adopts the QM corpus.

!!! warning "Follow the handbook, not this page"
    This page is an outline. The authoritative procedure — with the exact commands and the check that proves each step worked — is [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md). Do not improvise a lighter version: most adoption defects come from skipped or partial steps.

## The eight steps

The [handbook](../ref/glossary.md#handbook){ .glossary-term } numbers the steps 0 through 7. Each has a verification check; run the check rather than assuming the step worked.

**0. Confirm your starting commit.** Check which commit you are forking from, in both repositories.

**1. Add the submodule.** Add this repository as a git submodule at `governance/qm` in the new project.

**2. Create the project branch.** In this repository, create `project/<name>` off `main`. Copy `project-seed/adr/` onto it as a top-level `adr/` directory, then **push the branch** — do not open a pull request for it. This is the one place content arrives on a shared branch by push: the only base a pull request could target is the branch being created, which does not exist yet.

**3. Point the submodule at the branch.** Check out `project/<name>` inside the submodule, commit the updated pointer, and add `branch = project/<name>` to the project's `.gitmodules`.

**4. Wire CI.** Copy all four [seed](../ref/glossary.md#seed){ .glossary-term } workflows into `.github/workflows/`, verbatim: `adr-lint.yml`, `submodule-check.yml`, `reuse-lint.yml`, and `one-pr-check.yml`. Also wire the license gates the open-license [record](../ref/glossary.md#record){ .glossary-term } requires for the project's runtime shape.

**5. Wire governance discovery.** Copy `project-seed/ide/` recursively onto the project root, using a method that preserves symlinks (`cp -a`, `rsync -a`). Fill in the project-specific sections of `AGENTS.md` and replace the `<name>` placeholders. Check that the project's `.gitignore` does not swallow the copied files.

**6. Seed the first records.** Write the project's first records on its branch as numberless drafts — conventionally an adoption record and a scope record.

**7. [Register](../ref/glossary.md#register){ .glossary-term } carried patches.** If the project carries patches against upstream software, register them in the org-level [registers/carried-patches.md](https://github.com/quaternionmedia/qm/blob/main/registers/carried-patches.md).

## After adoption

- [Next steps](next-steps.md) — [propagation](../ref/glossary.md#propagation){ .glossary-term }, audits, and project phases
- [Architecture](../about/architecture.md) — why the structure is this way

## Related

- [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md) — the authoritative procedure
- [Branch namespaces](../ref/namespaces.md) — the rules for the `project/<name>` branch
