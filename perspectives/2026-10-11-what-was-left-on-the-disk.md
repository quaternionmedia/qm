# What was left on the disk — 2026-10-11

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-11 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

The session set out to finish what other sessions had left across the estate:
pull requests, conflicts, worktrees, local branches and dirty trees, each
carried to a pull request, a pushed branch, or a deletion that cost nothing.
This is why that took the shape it did, and what it found that no check had
reported. The work itself is in the pull requests named below.

## Where the work was

`uv run qm estate` names every rostered clone's uncommitted changes and the
commits that exist in one copy, and it was the right place to start. It found
the largest single item: alfred's `release/0.3.0`, forty commits made between
2026-08-07 and 2026-08-09 and never pushed. They stand now as alfred #117 to
#125, one stack cut along the seams the commits already had, with a thin dev
stack found uncommitted beside them on top. It also found private-38's
post-release documentation refresh, uncommitted on its `main` since the
release, which is private-38 #5.

The estate reads rostered clones. Four kinds of work sat where a clone survey
does not look:

- **A commit inside a submodule.** The alfred slice that fixed otto's title
  template pinned `alfred/otto` at a commit made only inside the vendored
  checkout. The estate counts alfred's commits, not otto's, so nothing
  reported it until the stack's hosted checkout failed to fetch it. It is
  otto #33.
- **Worktrees inside an ignored directory.** Three proofs of concept from
  2026-08-13 — an identity roster rendered to a server whitelist, a RAD host
  adapter, a mod verifier — sat as dirty worktrees under the corpus's ignored
  `.harness/`, each on a `demo/` branch never pushed. They are pushed, each on
  its own branch, with their tests passing.
- **Scratch beside the worktrees.** The voice loop's recognition benchmark —
  scripts, and the transcripts and confidence results behind joe's
  transcription settings and the tacit-agreement threshold — lived only in a
  scratch directory next to qmcp's worktrees. It is qmcp's
  `bench/voice-recognition` branch now. Most of that directory was copies;
  this was not, and only reading it told the two apart.
- **A notebook nobody had filed.** holophonor's partitura notebook and its
  recordings, committed on an experiment branch with the notebook's outputs
  cleared, because their tracebacks named a workstation's paths.

The ordinary reading of all four is that work was interrupted, not hidden.
What they share is that each was invisible to the tool built to find this,
for the reason that tool states: it reads the refs and trees of rostered
clones, and nothing inside or beside them.

## What a copy is

Finishing meant deleting most of what was found, and every deletion rested
on one question: is what this holds somewhere else? Three answers were used,
strongest first.

- **Contained.** Every commit is reachable from a branch of origin. Most
  local branches and every clean worktree met this.
- **Patch-equivalent.** `git cherry` finds each commit's change already on the
  default branch under another hash: squash merges, such as the seven
  dependabot branches codecartographer had merged that way, and replays.
- **Derivable.** The timeless sweep's narrative notes were lightly edited
  copies of passages that exist word for word in history, at each sweep's base
  commit. apothecary's exported handoff was its branch's documents, a patch of
  commits now on origin, and walkthrough output.

Every deletion on origin carried a lease on the commit fetched just before
it, so a branch another session had pushed to in the meantime would have
been refused rather than deleted. None was.

One comparison went wrong on its first reading. Sampled lines of the sweep
notes matched none of the retrospectives that were written from them, because
the two files wrap differently. With whitespace normalised and whole sentences
compared, a handful were carried verbatim out of hundreds: a retelling, which
is what a retrospective is, and not a loss. The first figure described the
line wrapping.

Two changelogs had stopped. alfred's was kept commit by commit until the
middle of its stack and not after; dossier's had not been touched since its
first commits. The entries added in this session cover this session's changes
and nothing older.

## Checks that reported for a reason of their own

Four, found in one day, ordinary causes first.

1. **A gate scoped to pull requests into `main` never meets a stacked one.**
   qm #139, stacked on #138, carried section heads set in capitals that the
   durable-text gate refuses. The gate runs on pull requests into `main`, and
   #139's base is #138's branch, so it said nothing; it would have gone red the
   day #138 merged and #139 was retargeted. The demo branch, which merges
   everything, is where it showed. The heads are plain case now.
2. **A shared lint step that has not linted since ruff 0.5.** The
   organisation's reusable lint workflow ran `ruff <args> .`, a usage error
   since ruff removed the bare form, so it fails in every repository that
   calls it — alfred, otto and al-admin — whatever the code says. alfred's own
   stack repaired its lint gate inside its nox sessions, and its hosted job
   stayed on the shared workflow, still red. The shared workflow's
   fix is `.github` #8.
3. **"Not on its remote", with two causes.** alfred's submodule check fetches
   each pin from the URL in `.gitmodules`. Both URLs were SSH, which a hosted
   runner cannot use, so the check reported both pins missing — the governance
   pin included, which was certainly there. One of the two was also genuinely
   missing: the otto commit above. One message covered a true finding and a
   false one, and only a control told them apart: a fetch over HTTPS reached
   both pins and refused a commit that does not exist. The seed's check gained
   an SSH fallback on 2026-08-10 and replaced it on 2026-08-22 with one that
   tells an unpushed pin from an unreadable remote; alfred had copied its check
   on 2026-08-08, before either. alfred's URLs are HTTPS now, in #123; moving
   its governance pin, which brings the current check, is open work.
4. **A test job that fails before any test runs.** alfred's API job installs
   on whatever `3.x` resolves to on the runner, which is now 3.14, where the
   pinned `reportlab` does not build. It fails at `pip install`, on `main` and
   on every branch, so a red API job there says nothing about the tests.

## Opened on a local pass

The alfred stack was opened with its suite run at every slice and ruff and
black measured at every slice, and with the hosted checks unread. Every
failure above that alfred carries — the SSH URLs, the commit inside the
submodule, Python 3.14 — is one a local run on the machine that made the
commits cannot reproduce, because that machine has SSH keys, holds the commit,
and runs 3.11. The preflight runner states it in its own output: a local pass
is evidence, not proof. The pull request bodies said what was run; they did
not say the hosted checks were unread, and they should have. Reading the
hosted checks once they report is the step that was missing, and the reason
the otto commit surfaced on the same day rather than at the first merge.

## The local model, measured twice

Tier 2 of the voice demo, `qmcp cookbook instruct --runtime local` in the
integration worktree, ran twice at the demo's stamped heads. The first run's
second instruction reached the model's call limit without answering, and the
run said so rather than reporting what it had read. The second passed in
seconds with the model warm, and its second answer restated the first finding
instead of saying what the file says qmcp is for. The check asserts that the
second run is handed what the first found; it does not, and cannot, assert
the answer. A green tier 2 is a statement about continuity's mechanics. The
ordinary explanation for the failed run is a small local model not converging
within its cap on a cold start, and two runs are not enough to say more.

## One active stack, as a habit

The guidance still carried language limiting a contributor to one open
branch, which the stack rule had already replaced: pull requests in parallel
when independent, stacked as drafts when dependent. qm #158 states one active
stack per developer as the habit to aim for and never a limit, names the
command `qm stacks`, and moves the gate's id and the harness views to the
stack rule. Project branches that took the corpus before that change still
carry the older rule in their copies, and keep it until `main` is propagated
into them.
