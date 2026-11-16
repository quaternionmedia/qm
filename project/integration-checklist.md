# The integration checklist: a stack, before it is pulled

A stack is pulled into `main` once, from its head. The head carries every level
beneath it, so the suite runs there and on no level below it
(`governance/qm/adr/DRAFT-review-the-integrated-whole.md`, its second decision); a
pull request on its own is its own head. This is that run, box by box, and what it
leaves for a person. [CONTRIBUTING.md](../../../CONTRIBUTING.md#the-loop) holds the rules
behind each box and what CI runs. [The bench checklist](bench-checklist.md) is what
only the real machines show, and [the models checklist](models-checklist.md) what
only qmcp's image models show; the rows of either that a stack changes are boxes
here.

Tick each box on the tree that will land. When one fails, the fix goes into the
level that wrote the line, the levels above it are rebased onto it, and every box
from the suite down is ticked again on the new head.

## The tree that will land

- [ ] `git fetch`, then the head merges onto `origin/main`'s tip:
      `git merge-tree --write-tree origin/main <head>` exits 0. Every box below runs
      on that tree: the head checked out in a worktree of its own, `origin/main`
      merged in.
- [ ] Every other stack open beside it merges with it too:
      `git merge-tree --write-tree <head> <other head>`. Two stacks that each add a
      line at one place, in `CHANGELOG.md` or the docs index, conflict there; the
      stack that lands second takes the other's lines in the level that wrote its
      own.
- [ ] On the two merged, the tests that list the repository's files pass:
      `uv run pytest tests/test_groups.py tests/test_areas.py tests/test_docs_site.py`.
      A clean merge still fails them when one stack adds or deletes a file the
      other's groups, areas or index name; the stack that lands second names it.
- [ ] Every commit is signed and names no tool or model as its author:
      `uv run python governance/qm/project-seed/ci/check_signatures.py --base-ref origin/main`,
      then `check_attribution.py --base-ref origin/main` from the same folder.

## The suite, once, on that tree

- [ ] `uv run apothecary test all`, or `test all --workers 2` for both parts on two
      workers. It runs again whenever the tree changes.
- [ ] Each failure is fixed in the level that owns it. A test that fails under load
      and passes alone is named with both runs; no bound is raised to pass it.
- [ ] Each skip is listed with its reason, and counts for nothing. A test that needs
      what the repository does not hold, a venue's files or a board, is named with
      what it needs.

## Pictures and words

- [ ] `uv run python tests/e2e/picture_drift.py --sheets .cache/picture-drift`, and
      every sheet looked at. A picture whose marked change is a page's -- a row, a
      word, a control a level adds or moves -- is committed in the level that changed
      the page. The rest, a run's noise -- a log's scroll, a focus ring, a line of
      text drawn a pixel over -- and every picture under the tolerance, is put back
      with `git checkout -- walkthrough/screenshots`. A change and noise often share
      one picture, which is then the page's.
- [ ] The words a run rewrites in a walkthrough page are committed in the level whose
      test writes them.
- [ ] The docs the levels touch are read together, against each other and against
      the code on the head. Levels written apart can each be true alone and
      contradict one another once stacked; a line found wrong is fixed in the level
      that wrote it.
- [ ] A change a user would notice has its line in `CHANGELOG.md`.

## The gates, run here

- [ ] `uv run --group preflight apothecary preflight`: every step it can answer here
      passes. The steps only the host answers, the pull request's voice and the
      host's signature check, are named as not run
      ([walkthrough page 15](../../../walkthrough/15-preflight.md)).

## What only a person sees

- [ ] Each row of the README's map, *What it does, and how to see it*, that the stack
      changes is walked on the head under `apothecary serve --simulated`.
- [ ] Each row of [the bench checklist](bench-checklist.md) or
      [the models checklist](models-checklist.md) that the stack changes is walked,
      or named open with what it needs. Simulated machines show none of those rows.

## The pull requests

- [ ] The push is priced, the jobs its workflows start and their recorded minutes,
      and made once a person has authorised that number.
- [ ] `uv run python governance/qm/project-seed/ci/check_one_pr.py --repo quaternionmedia/apothecary`
      before anything opens. One pull request per level: the bottom ready against
      `main`, each level above a draft on the branch beneath it. The person who
      asked is the assignee, and no review is requested.
- [ ] Each body speaks as the contributor and addresses nobody
      (`check_pr_voice.py --body-file`). The head's body says which tree each box
      ran on and what it said: the suite with its skips, the pictures, the docs
      read, preflight, the rows walked.

## Landing

- [ ] Each level beneath the head retargeted onto `main`, still a draft; then the
      head retargeted onto `main` and marked ready. Its checks run there: the
      governance checks, lint and the walkthrough's hermetic pages.
- [ ] When `main` has moved since the suite ran, the tree is made again and every
      box from the suite down is ticked again.
- [ ] The head merged with a merge commit that says what ran on the tree that
      landed. The levels beneath are merged with it, their commits being in `main`;
      no pull request is closed in favour of one that contains it.
- [ ] A merged branch is deleted only once no open pull request is based on it.
- [ ] The merge's push to `main` runs its checks again: a merge skips none.

## At a version tag

- [ ] The tag is annotated, naming the review, the manual test against the real
      runtime -- the bench checklist's run -- and what the automated gate did not
      cover (`tag-claims.yml`). The rest of the tests run in CI at the tag.
