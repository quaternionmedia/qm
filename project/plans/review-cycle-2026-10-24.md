# A review cycle that holds at ten times the requests

*Dated 2026-10-24. An assessment of how apothecary's pull requests are
reviewed and landed, measured against its own record, and a proposed cycle
that keeps working when the number of requests grows by an order of
magnitude, from many workers, people and agents. Measured at `origin` that
day with read-only calls (`gh api repos/quaternionmedia/apothecary/pulls?state=all`,
each pull request's size, `git diff --name-only` of each stacked branch
against its base, and the day's workflow runs and jobs). Proposed: nothing
here is decided except where the last section says so. Plans are dated and
exempt from the durable-text rule.*

## 1. What the record shows

| Measure | On 2026-10-24 |
|---|---|
| Open pull requests | 81: 74 from one account, 7 dependency bumps; 73 drafts |
| Shape | one stack 62 deep from #21 to #98, plus one branch off it; the bumps on `main` |
| Merged, ever | 7, six of them on one day |
| Opened that day | 38 |
| Size of an open pull request | median 338 lines changed, 17 files; #21, the stack's bottom, +110,819 −693 in 290 files |
| CI that day | 825 workflow runs, 1,141 jobs, some 34.5 runner-hours (`gh api 'repos/quaternionmedia/apothecary/actions/runs?created=2026-10-24'`, each run's jobs summed from start to completion) |
| CI a pull request's push, after #99 | the governance checks and lint, 1.4–1.6 job-minutes |
| Files the open pull requests touch most | `docs/README.md` 41%, `CONTRIBUTING.md` 37%, `templates/fractal_viewer.html.j2` (8,554 lines) 36%, `CHANGELOG.md` 32%, `apothecary/api.py` 30% |
| `main`'s protection | none: the gates hold by convention |

The flow is a queue with arrivals and almost no departures: requests arrive
at tens a day and merges at none, so everything waits, and every wait makes
the next merge harder. A stack 62 deep is the visible form of it.

## 2. What breaks at ten times the requests

Each of these is measured above or follows from it directly.

1. **Human review per request.** At ten or more workers, arrivals reach
   hundreds a day. A person cannot read hundreds of diffs a day, and a review
   queue a person must clear grows without bound. The corpus already puts
   the human gates elsewhere (the async contract §2: a pull request is an
   audit record, its author merges it once the gates are green; the human
   gates are ratification and the version tag).
2. **One integrated walk for the whole repository** (the project's *review
   the integrated whole* record in `governance/qm`). It fixes what per-head
   review gets wrong -- the tree reviewed is the tree that ships -- but one
   person approving one integration serialises every worker behind that
   person, and the integration grows with the queue.
3. **Deep stacks.** A fix at depth d is merged up through every level above
   it, and a stack that never lands only gets deeper. The cost is quadratic
   in depth, in merges, conflicts and CI.
4. **Per-push CI.** Before #99 a push cost about twenty runner-minutes;
   hundreds of pushes a day is hundreds of runner-hours. After #99 it is
   about a minute and a half, which is still a day of runner time at a
   thousand pushes, most of it the start-up of separate governance jobs.
5. **The integration check.** `integrates.yml` merges every open pull request
   before the one it checks, on every push: work proportional to the queue,
   per push, so proportional to its square per day.
6. **Shared files.** A third of open requests touch the page's template, and
   four in ten the docs index. With many concurrent workers, two requests
   touching the same file is the rule, and each conflict is a serial fix.

## 3. The cycle, proposed

Five rules; each is measured, and each scales because its cost follows
merges and releases, not people.

1. **A request is gated by machines and merged by its author.** A pull
   request's push runs the governance checks, lint and the walkthrough's
   hermetic pages, in one job rather than one a check. The author runs
   `apothecary test changed` while working and `apothecary test all` before
   marking it ready, and its body says what ran. Ready, green and eligible
   (it merges cleanly onto what is queued before it), it is merged with a
   merge commit. No person approves a request.
2. **Requests land through a queue, in batches.** A merge queue takes ready
   requests in order, merges them onto `main`'s tip together, runs the full
   suite once on the batch, and lands the batch or splits it to find the
   request that broke it. The suite's cost is paid once per batch, so its
   share per request falls as requests rise; at ten requests a batch, a
   twenty-minute suite is two minutes a request. Under the corpus's spending
   record a batch's run is priced like a push, and each further run of a
   split batch is shown and confirmed before it starts.
3. **People review releases, by area, in parallel.** A version tag is cut on
   a cadence -- a day's or a week's batches -- and its review is the
   integrated walk of the record above, split by area: the README's map lists
   what the code does, and the browser suite's areas (`tests/e2e/areas.py`)
   map code to what a person sees. Each area's reviewer walks that area's
   rows, on the tagged commit, under `apothecary serve --demo`, and the bench
   checklist covers what only hardware shows. The tag's annotation names the
   walks (*Version tags are claims* §6). Human time follows releases × areas,
   not requests.
4. **Stacks stay shallow, and land.** A stack is the shape of one piece of
   work, a few deep, and its bottom enters the queue as soon as it is green.
   A finding that is independent is a parallel request, not the next level
   of a stack.
5. **Shared files are split until requests stop meeting.** The template and
   `api.py` are cut into modules by area (the 2026-10-24 review's code items);
   the changelog becomes one file per change, gathered at the tag; the docs
   index and `CONTRIBUTING.md`'s CI table are generated from what they list.
   Each is measured by the share of open requests that touch it.

## 4. What is measured, and the command that reads it

A cycle stays honest only if its numbers are read the same way every time.
One command reads them from GitHub's record and the checkout, for any window:

- arrivals and merges a day; the queue's depth, its oldest request, its
  deepest stack;
- time from ready to merged; batches a day and their size; a batch that
  failed, and which request it was;
- runner-minutes per merged request, split into the queue's suite and the
  pushes' governance;
- the share of open requests touching each shared file;
- releases and their walks: areas walked, defects found in a walk, and
  defects found after a tag that a walk's rows show (the measure of the walk
  itself).

A number that moves the wrong way for a fortnight is the trigger to change a
rule, recorded as an amendment of the record that holds it.

## 5. What it changes in the records

- The project's *review the integrated whole* (Proposed, pending its trial)
  keeps its unit and its map, and moves its walk from each integration to
  each release, split by area; its merge rule becomes the queue's. That is an
  amendment drafted beside it and ratified by a person.
- The org's async contract and *Version tags are claims* are kept as they
  are: the cycle is their default, applied.
- `main` gets the protection the queue needs: required checks (governance
  and lint on requests, the suite on batches) and the merge queue itself.
  That is a setting of the repository, made by its owner.

## 6. Decided since

These parts stand decided, where the cited text says:

- A pull request's push runs the governance checks, lint and the
  walkthrough's hermetic pages; the rest of the tests run on the
  contributor's machine before a merge, on the tree that lands, and in CI at
  a version tag ([CONTRIBUTING.md](../../../../CONTRIBUTING.md)).
- A stack that lands as one run is tested once, on the tree `main` ends at,
  and landed in order (the corpus's apothecary handoff, decision 4) -- the
  batch of rule 2, run by hand.
- Cloud CI's runner time is spend: each push is priced and authorised, and a
  bot's push starts no job until a person re-runs it (the corpus's spending
  record; [CONTRIBUTING.md](../../../../CONTRIBUTING.md)).
- A runtime-bound walkthrough page's evidence is the run its version tag
  makes (the walkthrough record's decision 7).

The merge queue, release review by area, the metrics command, the shared
files' split and `main`'s protection are not decided; [project/todo.md](../todo.md)
lists them for a person.
