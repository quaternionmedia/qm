---
description: Refresh the harness status document and read what is in flight across the org.
argument-hint: [repository name to focus on, optional]
---

<!-- SEED FILE: part of project-seed/ide/, copied recursively onto the project
     root. The corpus's own .claude/commands/ holds symlinks back to this file,
     so there is one copy to edit. Delete this comment in the copy. -->

Refresh the org's harness status and report what needs a person. Focus, if one
was given: **$ARGUMENTS**.

This reads and reports. **It changes nothing** — no branch, no pull request, no
push. Anything it surfaces that needs doing is proposed to the human, not done.

## 1. Refresh, then read

From the corpus clone (or `governance/qm` inside a project):

```
python ci/harness_status.py --no-local --write harness-status.json
python ci/harness_dashboard.py harness-status.json --format md
```

The first command takes a few seconds per repository — it reads open pull
requests and the size of each. If `gh` is unavailable, skip the refresh and read
the committed document as it stands, **saying its age**: it carries its own
staleness budget, and past that budget its figures describe an organisation that
has moved on.

To include this machine's clones — unpushed branches, uncommitted work, threads
that exist nowhere but here — write a second copy **outside the repository**:

```
python ci/harness_status.py --write ../harness-status-local.json
python ci/harness_dashboard.py ../harness-status-local.json --format md
```

The tool refuses to write that layer inside the repository, and the refusal is
the point: it is one machine's state, and committing it publishes it as an
organisation fact.

## 2. Report, in this order

**Threads that need a person, worst first.** The document has already sorted
them. The three that matter:

- **`pushed`** — a branch on a remote with no pull request. It exists, it is
  safe from a lost laptop, and no reviewer has been told. This org has already
  left work in that state for months.
- **`stalled`** — untouched past the document's threshold and not landed. Say
  how long, and say what it was.
- **over the slot limit** — a contributor holding more than one open pull
  request. Name the numbers; folding is theirs to decide and has an order.

**Then what could not be read**, with the reason. A repository nobody measured
is not a repository with nothing wrong, and it is the first thing to lose in a
summary.

## 3. What not to say

- **No percentages, and no "on track".** The stages are observable states.
  Nothing in this corpus defines done, so any number you produce is invented.
- **No verdicts on someone else's branch.** Report the state; the reason it is
  in that state is theirs and is frequently deliberate — *keep everything
  local* is a standing instruction here.
- **No figure without its stamp.** Every number is true at `generated_at` and
  nowhere else.
