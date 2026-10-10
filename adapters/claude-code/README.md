# claude-code

Slash-command and skill files for one vendor's CLI. Optional; see `../README.md`.

## Using them

The CLI reads command files from `.claude/commands/` at the repository root.
This corpus keeps that directory as symlinks pointing here, so there is one copy
to edit:

```sh
mkdir -p .claude/commands
ln -s ../../adapters/claude-code/commands/cowork.md .claude/commands/cowork.md
```

A project that vendors this corpus can do the same against
`governance/qm/adapters/claude-code/commands/`, or copy the files, or ignore them
entirely. Nothing checks for them.

## What each wraps

| File | What it wraps |
|---|---|
| `cowork` | the four facts a session establishes before writing |
| `preflight` | which gates exist, and what each cannot see |
| `handoff` | what the next session needs, and why it went the way it did |
| `status` | what is in flight across the org |
| `skills/design-review/` | `handbook/design-review-runbook.md`, driven with the CLI's workflow tool; `orchestration.md` holds the scripts |

The skill is linked in this corpus as a directory, `.claude/skills/design-review`,
so a clone of qm has `/design-review` with no setup. A project that vendors the
corpus links the same directory once, and it follows the governance pin from
then on:

```sh
mkdir -p .claude/skills
ln -s ../../governance/qm/adapters/claude-code/skills/design-review .claude/skills/design-review
```

The link resolves once the project's pin carries the skill. A machine that
wants it in every repository links a qm clone's copy into its user-level skills
directory:

```sh
mkdir -p ~/.claude/skills
ln -s <qm clone>/adapters/claude-code/skills/design-review ~/.claude/skills/design-review
```

On Windows, with Developer Mode on, every `ln -s` on this page copies in Git
Bash unless `MSYS=winsymlinks:nativestrict` is set. From `cmd`, `mklink` makes
the same link, with `/D` for the skill's directory:

```bat
mklink /D .claude\skills\design-review ..\..\governance\qm\adapters\claude-code\skills\design-review
```

Either way git stores the target as `../../…`. Before committing,
`git ls-files -s .claude/skills/design-review` shows mode `120000`; any other
mode is a copy.

Each is prose instructing a model, so each is a habit written down rather than a
mechanism. Read them before running them: they encode one operator's working
style, and that style is not governance.
