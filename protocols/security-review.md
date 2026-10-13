# Protocol — Security review

**Question.** What could leak from this repository, and what actually protects
it right now?

**Invoked by** a human, or an agent asked to. **Budget** 30 days. **Produces**
`protocols/runs/<date>-security-review.md`.

This is a review of *this corpus as an artifact* — what it publishes, what it
lets in, and what it can prove about its own history. It is not an application
security review, because there is no running application: nothing here executes
outside CI and a developer's machine.

---

## 1. What is published that should not be

```sh
uv run qm private-names
uv run qm private-names --context
```

Runs on a machine holding the gitignored companion files; it cannot run on a
runner and does not gate anything. Read the **denominator** in its output, not
only the finding count — this check once knew 2 private names of 34 and every
`clean` it reported meant "the roster's two names are absent."

Record in the run: how many names it checked against, how many findings, and
how many were disclosures rather than ordinary words.

## 2. What protects the default branch

```sh
uv run qm rulesets
```

Drafted against applied. **Do not read the drafted column as protection.** Six
rulesets sat drafted from 2026-08-10 with an apply script beside them while the
host reported zero, and every check in the repository was a signal rather than a
barrier for that whole period.

Record: rulesets applied, enforcement level of each, and the required-status-check
list actually on the host — which this route does not read, so it needs
`gh api repos/quaternionmedia/qm/rulesets/<id>` or the settings page.

## 3. What the checks refuse, and what they cannot see

```sh
uv run qm gates
uv run qm exceptions
```

`cannot_see` is the field to read. A gate with an empty one is undescribed
rather than thorough. `qm exceptions` lists what this corpus deliberately does
not enforce; an exemption whose removal condition has been met and which is
still listed is a finding.

## 4. Whether the history can be trusted

```sh
python project-seed/ci/check_signatures.py --base origin/main --head HEAD \
    --source host --repo quaternionmedia/qm
gh api --paginate repos/quaternionmedia/qm/activity
```

`--source host` asks GitHub, which holds the keys; `--source git` asks the local
keyring and will report `E` for any commit signed by somebody else — including
every commit the host has never seen, which is every commit on an unpushed
branch.

The activity log is where a force push shows up. **Paginate it.** An unpaginated
`gh api` returned 100 of 109 repositories once in this org and declared three
existing projects nonexistent.

Record: every `force_push` event with its ref, and for each, whether the ref was
`main`, a `project/**` branch, or a tag — those three are the ones that break a
downstream submodule pin or rewrite a published claim. A force push on an
unmerged working branch is ordinary.

## 5. Licensing and dependencies

```sh
python -m reuse lint
```

Every file carries copyright and licence information, no deprecated SPDX
expressions, no unused licence files. It cannot see whether the licence asserted
is the licence intended.

---

## What this protocol cannot see

- **Runtime security.** Nothing here runs.
- **The secret scanner's configuration.** GitGuardian is an installed
  application with no workflow file in this repository and no record describing
  it. Nothing here states what it scans, who may dismiss a finding, or what
  happens if it is uninstalled. It appears on pull requests, and that is the
  whole of what this corpus knows.
- **Private repositories, from CI.** By
  `records/DRAFT-going-private-is-an-act-with-obligations.md`, the party who
  makes a repository private owns removing its name from this corpus. Nothing
  watches for the transition.
- **A rewrite older than the activity log.** That log currently reaches the
  creation of `main`, so today it is complete. Check that it still is rather
  than assuming it.
- **The other twelve repositories.** Every step above reads this one.

## Writing the run

`protocols/runs/<date>-security-review.md`. Give each section its command and
its output, not a summary of the output. **State the denominator wherever a
check has one** — `33 private names checked` and `2` are not a subtle
difference, and the second is what a broken check reports.

Where a section could not be completed, say which and why, in the run. A run
missing section 4 and a run whose section 4 found nothing look identical
otherwise, and one of them is a review that did not happen.
