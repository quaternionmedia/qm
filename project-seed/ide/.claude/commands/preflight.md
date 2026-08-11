---
description: Run every gate and report what ran, what failed, and what could not be reproduced — before calling anything ready.
argument-hint: [base branch, defaults to main]
---

<!-- SEED FILE: part of project-seed/ide/, copied recursively onto the project
     root. The corpus's own .claude/commands/ holds symlinks back to this file,
     so there is one copy to edit. Delete this comment in the copy. -->

Establish whether this branch is ready to be a pull request. Base branch:
**${ARGUMENTS:-main}**.

Every claim you make at the end must come from a command you ran in this
session. "CI is green" derived from reading a workflow file is a claim about a
file someone read.

## 1. What does this branch actually carry

```
python project-seed/ci/check_pr_base.py --base <base> --head <this branch>
```

Exit 1 means *explain this*, not *broken*. Read the ratio: "1 of 61" is a merge
you did deliberately; "18 of 20" is a branch you did not mean to be on. Keep the
output — it goes in the pull request description verbatim.

## 2. Do you have a slot

```
python project-seed/ci/check_one_pr.py --repo <owner/name> --contributor <your login>
```

If you are over, stop. Say which pull requests hold the slots and let the human
decide. If you are told to fold: **close the pull request first, then push** its
commits onto the branch that survives. Pushing first merges it, with no review
and no way to undo the record.

## 3. Run the gates

```
python project-seed/ci/run_workflows_locally.py
```

Then run this project's own suite — tests, linters, type checks — whatever its
`AGENTS.md` names below the seed line.

## 4. Report, in this shape

- **Ran**: each command, and what it said. Exit codes read directly, never
  through a pipe — `tool | tail` reports `tail`'s status, and that has turned a
  failing check into a reported pass twice in this org.
- **Could not reproduce**: the runner does not execute `uses:` steps, the runner
  image, or secrets. Name them rather than letting a local pass stand in for a
  remote one.
- **Failed**: for each, whether you established it as a defect or an
  environment difference — and how you established it. A local failure is a
  question, not a verdict.
- **Unverified**: anything you are asserting from reading rather than running.

## 5. Only then

If it is ready: `gh pr create --draft`, assignee the person who asked, **no
reviewer requested**, and the `check_pr_base.py` output in the body. Leaving
draft is their decision, after their testing.

If it is not ready, say what is missing. Do not open it.
