# Forking a new project

Standing up a new QM project: the eight-step procedure with checks at each step.

!!! info "Authoritative source"
    The detailed walkthrough with checks is in [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md). This page is the outline; follow the handbook page for the full procedure.

## The outline

A new project adopts the corpus in eight steps:

### Step 1: Add the submodule

Add this repo as a submodule at `governance/qm`:

```bash
git submodule add https://github.com/quaternionmedia/qm governance/qm
```

**Check:** `ls governance/qm/PRINCIPLES.md` exists.

### Step 2: Create the project branch

On the QM corpus repo, create a branch for this project's records:

```bash
cd governance/qm
git checkout -b project/<name>
git push origin project/<name>
cd ../..
```

**Check:** `git branch -r | grep project/<name>` shows the branch.

### Step 3: Copy the seed

Copy `governance/qm/project-seed/` into your project:

```bash
cp -r governance/qm/project-seed/* .
```

This brings in:
- `adr/` — your decision records directory, seeded with `README.md` and `TEMPLATE.md`
- `ci/` — the four governance workflows
- `ide/` — editor config, agent commands, and `AGENTS.md`

**Check:** `ls adr/README.md` and `ls .github/workflows/adr-lint.yml` exist.

### Step 4: Wire the four workflows

The seed ships four workflows in `.github/workflows/`. Enable them by ensuring they're not commented out and that the org/repo names are correct.

The four workflows are:

- `adr-lint.yml` — validates your record index
- `one-pr-check.yml` — ensures one open PR per contributor  
- `namespace-guard.yml` — guards the `project/<name>` branch on the corpus
- `reuse-lint.yml` — validates copyright and license metadata

**Check:** `git push` triggers these workflows and they all pass.

### Step 5: Seed the first records

Edit `adr/README.md` to remove the seed comment and add your first records:

```bash
rm -f adr/README.md.bak  # if you made a backup
# Then edit adr/README.md to seed your project's own records index
```

Add `adr/` files for your first decisions. Use `adr/TEMPLATE.md` as the template.

**Check:** `python project-seed/ci/adr_lint.py --records-dir adr --index adr/README.md` passes.

### Step 6: Wire the corpus index in your submodule

Update `governance/qm/.gitmodules` and point to your `project/<name>` branch:

```bash
cd governance/qm
git config submodule.governance/qm.branch project/<name>
cd ../..
```

**Check:** `cat .gitmodules | grep branch` shows `project/<name>`.

### Step 7: Commit and push

```bash
git add .gitmodules adr/ ci/ ide/ .github/
git commit -m 'bootstrap: adopt QM corpus'
git push
```

**Check:** The workflows pass.

### Step 8: Announce adoption

Create a record in the corpus documenting your adoption. On the corpus `main` branch, add a record to `records/` noting the new project, then open a propagation PR to merge `main` into your `project/<name>` branch.

**Check:** Your `project/<name>` branch receives the announcement record via the propagation merge.

---

## After adoption

- See [Next steps](next-steps.md) for propagation, audits, and the phase ladder
- See [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md) for the full procedure with every check explained
- See [Architecture](../about/architecture.md) to understand why the structure is this way

## Related

- [Architecture](../about/architecture.md) — how the branch-per-project model works
- [Branch namespaces](../ref/namespaces.md) — the rules for your `project/<name>` branch
- [handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md) — the authoritative walkthrough with checks
