# Landing the stack on main

*Dated 2026-10-20. How every open pull request of apothecary's, and the
governance records they pin, are reviewed once as a whole and merged into
`main` bottom first. Checked against the branches as they stood that day:
each fact below names the command that establishes it, and is run again
before it is relied on. Plans are dated and exempt from the durable-text
rule.*

## The stack

One line of pull requests, each based on the one below, with the
documentation sweep's stacks on `build/timeless-docs`:

```
main
└─ #21 consolidate/2026-09-19
   └─ #24 … #29 stack/01 … stack/06 ─ #30 review/2026-09-26
      └─ #31 build/rust-research ─ #32 rust-firmware ─ #33 part-loop ─ #34 picture-to-print
         ─ #35 slicer ─ #36 scad-loop ─ #37 onboarding ─ #38 part-iteration ─ #39 input
         ─ #41 build/governance
         └─ #50 build/timeless-docs
            ├─ docs:       #40 ─ #42 ─ #43 ─ #45 ─ #51 (walkthrough 7a)
            ├─ package:    #44 ─ #46 ─ #47
            ├─ page/tests: #48 ─ #49 ─ #52 (walkthrough 7b)
            ├─ #53 (walkthrough 7c)
            └─ #55 build/integration   (every pull request above merged into one tree)
               └─ #56 build/grid-and-fit ─ #57 scene-not-mirrored ─ #58 picture-fits-the-host
                  ─ #59 control-popped-out
                  └─ #62 theatre ─ #63 build/qm-propagation ─ #64 build/golden-layout
                     ─ #65 build/airgap ─ #66 build/window-views
```

The five branches from `theatre` up are drafts #62 to #66, opened on
2026-10-23 (step 1).
`build/window-views` contains every pull request beneath it:

```sh
for n in $(gh pr list --state open --limit 100 --json number,author \
           --jq '.[] | select(.author.login != "app/dependabot") | .number'); do
  h=$(gh pr view $n --json headRefOid --jq .headRefOid)
  git merge-base --is-ancestor $h origin/build/window-views || echo "#$n is not in the top"
done
```

The governance side is a stack in qm, on `project/apothecary`: qm#171
`fix/apothecary-seed-refresh`, then qm#172 `propagate/apothecary-2026-10-13`,
then qm#197 `adr/apothecary-review-the-whole`, then qm#211
`adr/apothecary-airgap-metrics` (the Airgap's metrics record). `build/qm-propagation` pins qm#197's head and `build/airgap` pins the
Airgap record's; `git ls-tree <branch> governance/qm` shows each pin.
`submodule-check.yml` fails a branch whose pin qm's remote does not have.

## 1. Before anything merges

Each of these is done on origin, by the owner or with them. *Done by
2026-10-23: the signing key; qm#211; the theatre as #62, a new pull request,
#54 pointing to it; #63 to #66.*

1. **The signing key on GitHub**, so the stack's signed commits show as
   verified: `gh auth refresh -h github.com -s admin:ssh_signing_key` (a
   browser approval), then `gh ssh-key add <the signing key>.pub --type
   signing`.
2. **qm**: push `adr/apothecary-airgap-metrics` and open it as a draft based
   on `adr/apothecary-review-the-whole`, its body carrying the output of
   `python project-seed/ci/check_pr_base.py --base adr/apothecary-review-the-whole --head adr/apothecary-airgap-metrics`.
   Until it is pushed, `build/airgap`'s pin is on no remote.
3. **The theatre**: `theatre` holds one commit, a contributor's, on
   `build/control-popped-out`; its pull request is #54, closed when its head
   branch was renamed on origin (qm#202, the retrospective
   `perspectives/2026-10-19-a-rename-closed-a-pull-request.md`). Origin's
   `theatre` is that pull request's old head. **Pends on** which of two
   routes is taken; either ends with a draft from `theatre`'s commit based on
   `build/control-popped-out`, its author unchanged:
   - **#54 restored.** Rename origin's `theatre` back to `echs-pac`
     (`gh api -X POST repos/quaternionmedia/apothecary/branches/theatre/rename -f new_name=echs-pac`)
     and reopen #54 (`gh pr reopen 54`) before anything is pushed to it;
     then `git push --force-with-lease=echs-pac:<origin's old head> origin theatre:echs-pac`,
     `gh pr edit 54 --base build/control-popped-out`, a title and body for
     what the commit is, and `gh pr ready 54 --undo`. Whether GitHub
     reopens a pull request after its head branch was renamed and renamed
     back is untried: if the reopen is refused, take the second route.
   - **A new pull request.** `git push --force-with-lease=theatre:<origin's old head> origin theatre`
     and `gh pr create --draft --base build/control-popped-out --head theatre`,
     its body naming #54 and its contributor. #54 stays closed with a comment
     pointing to it.

   Either way the old head stays readable on GitHub by its commit until
   GitHub's support removes it, and under the first route it stays in #54's
   timeline.
4. **The four branches above it**: push `build/qm-propagation`,
   `build/golden-layout`, `build/airgap` and `build/window-views`, and open
   each as a draft on the one below
   (`gh pr create --draft --base <the branch below> --head <branch> --assignee subcontrabass`).
   Each body says what changed and why, carries `check_pr_base.py`'s output
   for its base and head, ends with a `Tools:` line, and passes
   `python governance/qm/project-seed/ci/check_pr_voice.py`. Run
   `uv run --group preflight apothecary preflight` on the top before
   pushing; the gates that read origin's state (integrates, one pull
   request, the submodule pin) pass only once everything is pushed.

## 2. The review: the whole, once

The draft record *Apothecary is reviewed as one integrated whole, walked as
a demo from its README* (qm#197, Proposed) sets the review, and this landing
is the trial its *Pends on* names. A person reviews the tree at the top of
the stack, never a pull request at its own head:

1. **The whole.** `git fetch origin && git switch --detach origin/build/window-views`,
   then `git submodule update --init` and `uv sync`.
2. **Every test.** `uv run apothecary test all`: the unit tests, the
   walkthrough and every browser test. The result is noted with each skip
   and its reason; a skip counts for nothing.
3. **The walk.** `uv run apothecary serve --demo`, and the README's *What it
   does, and how to see it*, row by row: each row says where to see it and
   which tests hold it. A fresh clone through
   [walkthrough page 00](../../../../walkthrough/00-getting-started.md) is the
   newcomer's path.
4. **What only hardware shows.** [The bench checklist](../bench-checklist.md)
   on the Ender 3 and the ESP32 devkit.
5. **The approval, once**, as a comment on #55: the commit reviewed, the rows
   walked, the bench checklist's result, and the suite's result with its
   skips. A tag cut at that commit carries the same three in its
   annotation.

A pull request's own diff is its audit record, read when a question needs
it: each commit says why, with its evidence, and
`python governance/qm/project-seed/ci/check_pr_base.py --base <base> --head <branch>`
says what the branch carries.

Known and not fixed, for the approval to name or for a pull request of its
own: the airgap part stands below the floor (its Readiness window says so, at
`/viewer/parts/airgap`).

Known and fixed at the top only: the license check's dependency audit fails on
every branch below #66, on advisories published in October 2026 against the
locked certifi and pillow. #66 locks their fix versions; at landing the same
lock change goes on #21's branch and is merged up, as a red check is.

## 3. Landing: bottom first

**qm first**, because apothecary pins its records: qm#171 into
`project/apothecary`, then qm#172, qm#197 and the Airgap record, each with a
merge commit. Merging a record's pull request does not ratify it: a record
stays a draft until a human's commit flips its status and gives it a number.

**Then apothecary, in this order**, which is the order `integrates.yml`
checks (depth first from the base, oldest first on each):

1. #21, #24, #25, #26, #27, #28, #29, #30
2. #31, #32, #33, #34, #35, #36, #37, #38, #39, #41
3. #50
4. the docs stack #40, #42, #43, #45, #51; the package stack #44, #46, #47;
   the page and tests stack #48, #49, #52; then #53
5. #55, whose diff is then its own: the merges' resolutions and the README's map
6. #56, #57, #58, #59
7. #62 (the theatre), then #63, #64, #65, #66

Each is merged the same way:

1. **Retarget onto `main`**: `gh pr edit <n> --base main`. The one below has
   merged, so the diff against `main` is the pull request's own commits.
2. **Ready**: `gh pr ready <n>`. A ready pull request whose base is another
   open pull request's branch fails `one-pr-check.yml`; on `main` it passes.
3. **Green**: `gh pr checks <n>`, every check passing. CI tests the merge
   with `main`, which is the tree that ships.
4. **Merge with a merge commit**: `gh pr merge <n> --merge`. Never squash and
   never rebase: every branch above stands on these commits, and a rewritten
   commit makes each pull request above carry it twice and breaks a pin.
5. **Retarget before deleting**: every pull request based on the merged
   branch (`gh pr list --base <branch>`) goes onto `main` before the branch
   is deleted, if it is deleted at all. Deleting a base branch first closes
   every pull request on it.

`uv run qm merge --repo quaternionmedia/apothecary --pr <n>` holds steps 3
to 5: run from a checkout of qm, it reads the pull request live and says
whether it is ready, and with `--yes` it merges with a merge commit,
retargets what is stacked on it, then deletes the branch. It refuses a pull
request another account opened, so #54, restored, is merged by hand.
It needs a `gh` whose `gh pr checks` takes `--json`: with one that does not,
it reports every pull request's checks as unreadable and refuses to merge.
Its listing without `--pr` stops at `gh`'s default page of 30 pull
requests, so each is named.

**A red check** is fixed on that pull request's own branch with a signed
commit, then merged up through every branch above it (`git merge`, no
rebase, no force push), and the branches pushed. The order is checked
before landing starts, and again after any fix, by merging every branch in
turn into a copy of `main` that nothing points at; it says the first branch
that conflicts, and that `main` would end as the top's tree:

```sh
r=${R-origin/}   # the remote's branches; R= reads the local ones
m=$(git rev-parse ${r}main)
for b in consolidate/2026-09-19 stack/01-review-ws-12 stack/02-review-ws-18 \
    stack/03-review-ws-15-and-parts-seams stack/04-pictures-in-the-world \
    stack/05-openscad-installers stack/06-one-page review/2026-09-26 \
    build/rust-research build/rust-firmware build/part-loop build/picture-to-print \
    build/slicer build/scad-loop build/onboarding build/part-iteration build/input \
    build/governance build/timeless-docs \
    timeless/docs-1-contradictions timeless/docs-2-front-door timeless/docs-3-plans-retire \
    timeless/docs-4-reference timeless/walkthrough-7a-pages \
    timeless/package-1-contradictions timeless/package-2-narration timeless/package-3-pictures \
    timeless/page-tests-1-contradictions timeless/page-tests-6-page-tests-config \
    timeless/walkthrough-7b-generated timeless/walkthrough-7c-loops-first \
    build/integration build/grid-and-fit build/scene-not-mirrored build/picture-fits-the-host \
    build/control-popped-out theatre build/qm-propagation build/golden-layout build/airgap \
    build/window-views; do
  t=$(git merge-tree --write-tree "$m" "$r$b") || { echo "conflicts: $b"; break; }
  m=$(git commit-tree "$t" -p "$m" -p "$r$b" -m "trial merge of $b")
done
git diff --quiet "$m" "${r}build/window-views" && echo "main ends as build/window-views"
```

On 2026-10-20, on the local branches (`R=`), it merged every branch without
a conflict and `main` ended as `build/window-views`; started from a `main`
whose README had been rewritten, it stopped at the first branch, naming it.
The theatre's branch is `theatre` here; under the first route of step 1.3
its pull request's head is `echs-pac`.

## 4. After

- **Dependabot's pull requests** (#15, #16, #17, #19, #23) are answered
  against the new `main`: rebased (`@dependabot rebase`) and merged when
  green, or closed with the reason.
- **The governance pin** moves to `project/apothecary`'s tip, in a pull
  request of its own on `main`.
- **A version tag**, when one is cut, is annotated with the review, the
  manual test and what the automated gates did not cover (`tag-claims.yml`;
  [walkthrough page 16](../../../../walkthrough/16-being-depended-on.md)).
- **Branches no pull request heads** on origin (`build/onb-demo`,
  `build/onb-docs`, `build/onb-tests`, `build/pi-page`, `build/pi-server`,
  `build/pi-text`, `timeless/docs`, `timeless/package`, `timeless/page-tests`,
  `feature/firmware-toolchain`, `feature/rc-snowplow-docs-cleanup`) are
  deleted or kept.
- **This plan** moves to the *History* of [the docs index](../../../../docs/README.md) once
  the stack has landed.
