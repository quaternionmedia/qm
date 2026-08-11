---
description: Close a session — write the handoff and the retrospective, so the work can be picked up cold.
argument-hint: [slug for the handoff page]
---

<!-- SEED FILE: part of project-seed/ide/, copied recursively onto the project
     root. The corpus's own .claude/commands/ holds symlinks back to this file,
     so there is one copy to edit. Delete this comment in the copy. -->

Close this session. A session that ends without this has produced work only its
own transcript explains, and the transcript is not in the repository.

Two artifacts, and they are different documents. Do not merge them.

## The handoff — what is left, and how to pick it up

Write it to `handbook/handoffs/<slug>.md` in the corpus (org-level work) or to
this project's own handoff location. Slug: **${ARGUMENTS:-name it after the work}**.

It carries:

- **A stamp.** The commit each repository was at, and the date. Every number
  you write is true at that commit and nowhere else, and the next session must
  re-derive rather than quote. Say so on the page.
- **State, not narrative.** What exists now: branches, what each carries,
  whether it is pushed, whether it has a pull request and whether that pull
  request is a draft.
- **What is unfinished**, and for each, what "done" looks like — a check that
  passes, a file that exists, a question answered.
- **What is blocked, and on whom.** Anything waiting on a human decision is
  named as such. Do not guess it and do not build past it.
- **What you could not verify**, marked as inference rather than stated flatly.
- **Standing constraints still in force** — most importantly *keep everything
  local* if it is. Unpushed commits read as an oversight to a session that does
  not know they were deliberate.

Delete a handoff page when its work lands. The method that outlives it belongs
in a runbook, not here.

## The retrospective — why it went the way it did

Write it to `perspectives/<date>-<slug>.md` in the corpus. **Every why goes
here**, per `handbook/style-guide.md`, whatever file you were editing when you
worked it out. It is attributed, dated, and binds nothing.

Be honest, specifically:

- Name the false assumption before naming the fix. The assumption is the
  reusable part.
- A defect you caused is written the same way as one you found. This corpus has
  a retrospective admitting an environment variable was set by the session that
  then reported it as mysteriously set — that page is worth more than a clean
  one.
- For each finding, name the check that would have caught it, and say whether
  that check now exists. If it does not, that is the next piece of work.

Disclose tooling as a `Tools:` note, never as a byline or co-author trailer.

## Then

- Run `/preflight` if anything is to become a pull request.
- Leave the working tree clean, or say in the handoff exactly what is dirty and
  why it was left.
- Report to the human: what landed, what did not, what you need from them, and
  the single next action you would take.
