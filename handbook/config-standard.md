# Handbook — Where configuration and generated documents live

**Routing.** One format, two folders, and a rule for telling which a file is.
Written because the corpus had drifted to nine data files at its root in two
formats, with no rule that would have told anyone where a tenth belonged.

---

## The drift this replaces

Measured 2026-08-16, before the sweep:

| | |
|---|---|
| Data files at the repository root | 9 |
| Formats among them | JSON and YAML, mixed |
| Hand-authored config in `ci/` | 6, all YAML |
| Rule saying which a new file should be | none |

`governance-status.yaml` and `harness-status.json` are the same kind of thing —
a generated status document — in two formats, in the same directory, named to
two different conventions. Nothing was wrong with either; there was simply no
standard, so each generator chose for itself.

## The standard

**YAML everywhere.** JSON is kept only where a consumer requires it.

YAML because these files are read by people more often than by programs: it
takes comments, and every one of these documents carries a `reading:` block and
a `do_not:` list that exist to be read. A format that cannot hold a comment
makes the tool's docstring the only place the caveats live, and the caveats are
the load-bearing part.

**Two folders, and the split is claim versus evidence.**

| Folder | Holds | Written by | Committed |
|---|---|---|---|
| `ci/` | claims: registries, rosters, policies | a human, by hand | yes |
| `status/` | evidence: generated documents | a generator | yes, unless it carries private data |

That split already existed as doctrine — `ci/workspace.yaml` says *"nothing here
is evidence"* in its own header — and now it is visible in the layout.

## Naming

`status/<subject>.yaml`. The subject, no suffix: `status/gates.yaml`, not
`status/gate-status.yaml` inside a folder called status.

`ci/<subject>-registry.yaml` for a closed vocabulary, `ci/<subject>.yaml`
otherwise.

## What does not move

**Views stay where their readers are.** `handbook/gates.md` and
`handbook/document-states.md` are rendered pages, and a reader looking for the
handbook should find them in the handbook.

**Machine-scoped files stay out of both.** `inventory-private.json` and
`inventory-local.json` are gitignored and belong to one machine. They are not
evidence about the org; they are facts about a disk.

## The cost, stated

Moving `governance-status.yaml` and `harness-status.json` changes paths that
`project-seed/ide/AGENTS.md` names, and every adopting project reads that file
through its submodule mount. A project whose pin does not move keeps the old
layout and the old paths, and with propagation retired
(`plans/data-collection-pathways.md`) that pin may never move.

So this standard is true of `main` and of nothing else until somebody bumps a
pin. That is a real cost of sweeping the drift, and the alternative — leaving
two formats and no rule — was worse only because it would keep growing.

## Adding a file

- A human wrote it and it states an intention → `ci/`, YAML.
- A generator writes it and it states a measurement → `status/`, YAML.
- It contains anything private or machine-specific → neither; gitignore it and
  say so in the generator's docstring.
- It is a page for a reader → `handbook/`, markdown.

If a file is two of those, it is two files. `inventory-public.yaml` and
`inventory-private.json` were one document until the split, and the split is
what makes the public half safe to commit.
