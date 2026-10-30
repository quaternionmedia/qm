# Security review — 2026-08-23

**Protocol** `protocols/security-review.md`. **First run**; the protocol had
never been invoked since it was written. `qm` at `d29d873`, extended to `qmcp`
at `26893c6`, `dossier` at `ad8622a`, `codecartographer` at `13443bb`.

Invoked by the operator, who asked for "an extra ambitious sweep to check on
hygiene for personal, sensitive, or otherwise non intentional, non code or docs
leaks". The protocol's five sections are below; the sweep past them is section
6, which the protocol does not define and its "what this cannot see" invites.

---

## 1. What is published that should not be

```
$ uv run qm private-names
clean       33 private name(s) checked against 357 tracked file(s); none appear.
            History is not read. A name already published stays published.

$ uv run qm private-names --context
found       0 used as a repository, 29 as a bare word.
```

**Denominator: 33 names against 357 files.** Zero disclosures. The 29 are
ordinary words that are also private repository names — the declared,
effectively permanent exemption in `ci/exception-registry.yaml`.

## 2. What protects the default branch

```
$ uv run qm rulesets
6 drafted, 0 applied on the host.
Nothing is applied. Every rule below is a file, and every check in this
repository is a signal rather than a barrier.
```

**This is the finding of the review.** Six rulesets — `main`, project branches,
perspective branches, evolve branches, branch naming, version tags — exist as
files with an apply script beside them, and the host enforces none of them.

The required-status-check list was not read; this route does not reach it, and
with zero rulesets applied there is nothing for it to be attached to.

**It was tested by accident during this session.** A direct push to `main`
succeeded, on the branch whose protection is drafted and unapplied, in a
repository whose constitution calls that push "the one act that destroys the
audit record". Nothing refused it. The rule is real, is documented emphatically,
is quoted in `AGENTS.md` item 3, and is enforced by nobody.

## 3. What the checks refuse, and what they cannot see

```
$ uv run qm gates
15 gates. 2 rows carry an empty column.

$ uv run qm exceptions
9 exemptions. 8 silence a check; the rest are gaps declared and still reported.
```

The one to read is `secret-scan`: state `[??]`, and what it cannot see is
*"Everything about how it is configured. It is an installed application with no
workflow file in this repository and no record describing it."* Its enforcement
column reads *"nothing stated — it guards a habit rather than a decision."*

That gate is the whole of this corpus's automated coverage against publishing
something it should not, and section 6 is what it does not look for.

## 4. Whether the history can be trusted

```
$ python project-seed/ci/check_signatures.py --source host --repo quaternionmedia/qm
All 68 commit(s) carry a signature.

$ gh api --paginate repos/quaternionmedia/qm/activity
398 events: 152 push, 111 branch_creation, 66 branch_deletion, 65 pr_merge,
4 force_push.
```

Every force push, with its ref:

| when | ref | reading |
|---|---|---|
| 2026-08-13 | `evolve/git-hygiene-and-handoff` | working branch — ordinary |
| 2026-08-08 | `propagate/qmetronome-2026-08-08` (×2) | intermediate branch, before merge — ordinary |
| 2026-08-08 | `fix/apothecary-seed-refresh` | working branch — ordinary |

**None on `main`, none on a `project/**` branch, none on a tag.** Those three are
the ones that break a downstream submodule pin or rewrite a published claim.

## 5. Licensing

```
$ python -m reuse lint
Files with copyright information: 341 / 341
Files with license information:   341 / 341
Unused licenses: 0.  Invalid SPDX expressions: 0.  Read errors: 0.
```

Compliant with REUSE 3.3. It cannot see whether the licence asserted is the
licence intended.

---

## 6. Beyond the protocol — the four repositories, swept

The protocol reads this repository and looks for private *names*. This section
read all four and looked for the other kind of leak: an account, a machine, a
private conversation. Three findings, each in a different repository, none of
which a secret scanner would flag because none is a credential.

| repository | what | where |
|---|---|---|
| `qm` | a `claude.ai/share/` link, two conversation identifiers, and the absolute path of a conversation archive | the provenance header of a committed transcript |
| `dossier` | an account name in a database path | 1 of the 7 committed screenshots |
| `qmcp` | an account name and one machine's directory layout | a documented MCP client config |
| `codecartographer` | an account name, in a pasted traceback | an archived legacy doc |

The share link is the serious one: anybody holding it can read the original
conversation, and it sat in a public repository. **It was not fetched during
this review** — establishing whether it is live is an act, not a check, and it
is the author's to take.

### Cleared on inspection

`codecartographer/data/graphs.db`, committed and later deleted, still in
history. A SQLite file, 135168 bytes, six tables. Opened: 87 rows in `edges`,
all `fixture_sample`, every other table empty — including `user_actions` and
`user_preferences`, which are what made it worth opening. No paths, no names, no
emails. **Alarming by name, benign by content**, and the only way to know was to
read it.

### What was built

`uv run qm leaks`, in `project-seed/` so every project gets it. Three patterns,
a redacted report, a stated-reason escape hatch whose use is counted and
printed, and a denominator on every clean run. All four repositories report
clean after the fixes.

---

## What this run did not establish

- **The secret scanner's configuration**, as the protocol says. Unchanged.
- **Whether the share link is live.** Deliberately not fetched.
- **Anything about history.** Every check above reads working trees. The
  transcript's share link and identifiers are in this repository's history and
  stay there; so does the account name in `codecartographer`'s.
- **The other nine repositories.** This run covered four. `alfred` was read only
  by `qm pins`, which found two unpushed submodule pins there, one of them
  holding the only copy of an org perspective — recovered separately.
- **Whether the rulesets, once applied, would be the right rules.**
  `qm rulesets` compares enforcement levels and rule types, not parameters.
