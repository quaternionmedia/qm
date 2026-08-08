# Handbook — Auditing the Remaining Adoptions

**Routing.** Operational status and working instructions, not a decision
record. It weighs no alternatives. Delete the queue section when it empties;
keep the method section, which is the part that generalises.

**You are probably an agent with no memory of the audits already run.** That
is the normal case. Everything you need is here, in
`handbook/propagation-runbook.md`, and in the repository itself. Do not trust
a summary of repository state — including this page's — over `git`.

---

## The queue

Nine projects vendor this corpus. Three are audited.

| Project | qm branch | Own repo | Audited | Known state |
|---|---|---|---|---|
| qmetronome | ✅ | ✅ | **yes** | Pin fine; no IDE discovery; pre-seed inline lint |
| apothecary | ✅ | ✅ | **yes** | Healthiest; has a working license gate |
| datum | ✅ | ✅ local only | **yes** | Pin was broken; repaired; **has no remote** |
| alfred | ✅ | ✅ | no | Submodule remote was a filesystem path; repaired |
| codecartographer | ✅ | ✅ | no | Mounts at `docs/qm`, not `governance/qm` |
| datafactorio | ✅ | ✅ | no | 7 behind; no `.gitmodules` seen locally |
| factorio-server | ✅ | ? | no | 7 behind |
| factorio-sysops | ✅ | ? | no | 7 behind |
| streaming-infrastructure | ✅ | ? | no | Branch is new; carries two known content defects |

Re-derive every column before acting on it. The "known state" notes are what
one pass found on one day.

## What one audit is

Walk `handbook/propagation-runbook.md` end to end. Both parts: the
`project/<name>` branch in this repo, **and** the project's own repository.
The second is where every serious finding has come from, because the first is
the part people remember to check.

Then, per project, expect roughly:

- one PR into `project/<name>` for the seed copies a merge cannot fix;
- one propagation PR, if the branch is behind;
- one PR into the project's own repo for whatever adoption skipped.

Keep them separate. They have different reviewers and different risk.

## The rule that decides where a fix goes

**If two projects could have the same defect, the fix belongs in
`project-seed/`, not in the project.**

This is not a style preference; it is the finding the audits keep producing.
qmetronome hit a broken submodule pin on a release build and wrote a check.
Nothing carried it. apothecary hit the identical failure months later with no
guard, and datum was carrying it silently at the same time. One project had
the answer and two needed it.

So when you fix something in a project repo, ask what would have prevented it
everywhere, put *that* in the seed, and let the project's own PR be a verbatim
copy. A fix that lands only where it was found is a fix that will be needed
again.

## How the process evolves

Every audit so far has changed the process, and none of the changes were
predictable from reading. The loop:

1. **Run the procedure exactly as written**, including the steps that look
   unnecessary. The point is to find out where it is wrong, and it has been
   wrong somewhere every time.
2. **When a step misleads you, that is the finding** — bigger than whatever
   you were looking for. A diagnostic that reports a false all-clear is worse
   than no diagnostic, because it ends the investigation.
3. **Fix the page in the same session.** Not "note it for later": the next
   agent has no memory and will be misled identically.
4. **Record what the run found**, in `handbook/governance-rollout.md`, in one
   or two lines. A finding nobody can see did not happen.
5. **Say which step found it.** That is what tells the next person which
   steps are earning their place.

Three worked examples, so the shape is concrete:

- The "has propagation ever run?" check matched any merge commit. A project
  merging its own feature branch produced a false all-clear on the one
  question the step existed to answer.
- The conflicted-propagation path had no PR shape that worked: with
  `head=main`, GitHub commits the resolution to `main`.
- A conflict resolved by keeping both sides passed, then conflicted again on
  the next propagation — the same insertion arriving from two directions is
  not something git can reconcile.

## Verification, because this is where agents fail

The corpus has an evidence standard; this is where it earns its keep. Every
one of these produced a confident wrong answer during the audits already run:

- **`git -C /c/...` under Git Bash on Windows** silently returns nothing.
  Use `C:/...` for `-C`. This produced three separate "absent" findings that
  were false.
- **`git submodule status | head -1`** reads whichever submodule sorts first.
  One repo has three. Name the path: `git submodule status governance/qm`.
- **Piping a check through `head`/`tail` reads the pipe's exit code**, not the
  check's. A failing case reported success.
- **Checking for a filename** reports "absent" when a project implemented the
  same behaviour its own way. Search for the behaviour.
- **A negative test that never ran** passes. If you assert a check fails on
  bad input, watch it fail before you believe it.

State which commit you are working against at the start, and re-derive branch
counts rather than reading them from any document, this one included.

## What you may not do

Ratify anything. Merge to `main` or to a `project/*` branch. Delete a branch.
Force-push. Rewrite a branch a submodule pins — and if you find one that was
rewritten, the runbook has the recovery path.

Open pull requests, and settle your open questions with a human **before**
opening them rather than inside them.
