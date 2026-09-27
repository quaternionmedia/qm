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

The skill is linked the same way, as a directory, into `.claude/skills/`:

```sh
mkdir -p .claude/skills
ln -s ../../adapters/claude-code/skills/design-review .claude/skills/design-review
```

Each is prose instructing a model, so each is a habit written down rather than a
mechanism. Read them before running them: they encode one operator's working
style, and that style is not governance.
