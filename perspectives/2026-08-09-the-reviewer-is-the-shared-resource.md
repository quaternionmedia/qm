# The reviewer is the shared resource

*2026-08-09 · Peter Kagstrom · non-binding opinion*

*Tools: drafted in a Claude Code session against `qm` at `3496ad0`, from the
transcripts of six sessions run the same day across `qm`, `alfred`,
`apothecary`, `datum`, `rad` and `codecartographer`.*

---

Six agent sessions ran across six repositories on one day. Each behaved well by
every rule it could see. The day still produced a mess, and the mess had a
shape worth naming: **none of the failures were inside a session. They were in
what the sessions did to each other, and to the one person they all reported
to.**

That is the finding. Everything in `handbook/async-contract.md` is a
consequence of it.

## What a session cannot see

An agent session is a closed world. It can read the repository, run commands,
and reason about what it finds. It cannot see the other five sessions, the
reviewer's queue, or the workstation's port table. So it optimises the one
thing it can measure — its own task — and the costs land somewhere it has no
instrument for.

Three of those costs showed up on the same day.

**The queue.** An agent finishes in minutes; a human reviews at human speed.
Six sessions produced pull requests faster than one person could open them, and
the correction had to be given three times in two repositories before it was
written down plainly enough to stop being re-derived: *"I'd like a single PR to
review per repo"*, then *"Trying to enforce the one PR by agents for HIL
review"*, then — the one that finally named the real damage — *"Your role is to
tag me, not others."* A ready pull request against a branch with `CODEOWNERS`
pulls a second person into untested work the moment it opens, and the
notification cannot be recalled.

The instructive part is not that the rule was broken. It is that each session
broke it while following instructions that read, literally, "open a PR for
human review". An agent reading that does exactly what it says. The instruction
was wrong, not the reading.

**The workstation.** An Alfred session spent an afternoon measuring test
results against `localhost:8000`. Apothecary's API was serving that port from
another session. Two tests were investigated as defects in code that was never
running. The session had already written a retrospective, that same day, about
a port collision on 27017 — and then did not apply it, because nothing in its
world said another program might answer.

A 200 from a port proves something is listening. It does not say what. The
cheap fix is to ask: `/openapi.json` returns a title, and the title was
`Apothecary API`.

**The repository.** Two sessions worked the same repository twice —
*"there is one other active session"* in Apothecary, *"Another agent has started
the work parallel"* in RAD. Neither could see the other. Both were told by a
human, after the fact.

## Why "one PR per repository, per contributor" is the right unit

Not per task: the task is the agent's unit, and it is exactly the unit that
does not scale with the reviewer.

Not per branch: branching is free, so a per-branch rule buys a slot with a
`git checkout -b`. Apothecary's #13 was based on #12's head — a stacked pair
whose merge order lived only in the session that built it.

Per repository, per contributor, because that is the shape of the thing being
rationed. The human-only contributorship record turns out to matter here in a
way it was not written for: an agent's commits carry the person's name, so the
pull request author *is* the contributor, and the rule is checkable at all.

The corpus repository gets one exemption, and it is worth stating why it is not
a loophole. Each `project/<name>` branch is a different project's decision
records, pinned by that project's submodule. A propagation into
`project/alfred` and one into `project/datum` are two unrelated projects;
combining them to satisfy a count would invent a dependency between them and
hand the reviewer something worse than the two it replaced. The exemption is a
glob someone passes and the tool prints — because an exemption nobody can see
in the output has stopped being one.

## The failure mode that keeps recurring, now with four more instances

This corpus has a standing finding: *every defect it has found in its own
tooling was a check that reported success while enforcing nothing.* Building
this harness added four more, and all four were caught by the same two habits
rather than by being clever.

**Run it against real data.** The slot check crashed on its third repository:
`subprocess` decoded gh's output through cp1252 and raised, handing back
`stdout=None`. The offending byte was an emoji in a pull request title — `🔳
Gridfinity`, a real PR in Apothecary. The identical fix already existed in
`ci/governance_status.py`, written for the identical reason. A check that dies
on a title is a repository nobody measured, and it would have died silently in
exactly the repositories with the most activity.

**Break the tool and confirm the test fails.** Sixteen mutations were run
against the three new tools. Four tests passed against a broken tool:

- Two asserted that a bot's pull request does not count against a human, using
  two *different* logins — so they passed whether or not the tool classified
  anything, because two authors never collide anyway.
- One asserted an emoji title does not kill the report, without pinning the
  output encoding — so it exercised a UTF-8 console and proved nothing about
  the cp1252 one where the bug lives.
- One asserted the phrase *"the submodule is not initialised"* appears in the
  brief. It does — in a **different section**, which produces the same phrase
  when it cannot find a directory. The test matched the wrong paragraph and
  would have passed against a tool that dropped the check entirely.

That last one is the interesting shape. A substring assertion against a page
your own tool generates is a test of the page's vocabulary, not of the signal.
The fix was to assert on the remediation command, which only that line carries.

**And the tooling lies about symlinks.** `ln -s` under Git Bash on Windows
creates copies, silently, unless `MSYS=winsymlinks:nativestrict` is set. Three
harness commands were staged as mode `100644` regular files — second copies of
the seed, drifting from the moment they were written. `symlink-integrity.yml`
exists for precisely this and would have caught it in CI; it was caught locally
only because the check's own output was read rather than assumed.

## Two directions, and only one of them decays quietly

The harness ships as files in `project-seed/`, and the sync between the corpus
and a project runs both ways.

*Down* is mechanical: this repository's own `.claude/` and `.vscode/` are
symlinks into `project-seed/ide/`, so editing the seed edits the corpus's own
harness in the same commit, and CI checks the pointers are still pointers. A
project picks the change up when its pin is bumped and the seed files are
re-copied. A merge does not fix a copy.

*Up* has no mechanism, and that is the honest state of it. When a session finds
the harness wrong where it is running, the fix belongs in `project-seed/` on a
branch of this repository — not in the local copy, which is a fork of the
constitution that nothing reports. Naming that direction is the whole
intervention available today. It is written down because the alternative is
that it happens by accident, once, and never again.

## What I would watch next

The rule is now enforced, which means the next thing to learn is what it costs.
A reviewer with one slot per repository has a smaller queue and a longer one —
work that would have arrived as three parallel pull requests now arrives as one
larger one, or waits. Whether that trade is right is not something a day of
evidence settles.

The specific signal to watch: **pull requests that grow because their author
could not open a second.** If the slot rule starts producing PRs that bundle
unrelated work, the constraint has moved the problem rather than solved it, and
the answer is probably a faster review loop rather than a looser rule.
