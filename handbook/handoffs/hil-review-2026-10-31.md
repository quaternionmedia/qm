# Handoff — the estate reviewed by hand, 2026-10-31

**Stamped 2026-10-31.** `qm` `main` at `c681da0`. Every figure on this page
was true at that commit and nowhere else; re-derive one before acting on it.

**Nothing on this page is a task.** It is what a person starts, what they look
at once it is up, and where they write what they saw. A finding is fixed on a
pull request of its own and its row in §5 names which; the row comes off when
that lands. Delete this page when §5 is empty and nothing in §4 waits on a
person.

---

## 1. What to start

Each loop is one thing running, a list of what to look at, and the findings
table in §5. Nothing here binds a port another project uses by default.

| Loop | Start | Look at | Stop |
|---|---|---|---|
| **The docs site**, as `main` renders it | `uv run --extra docs zensical serve -a 127.0.0.1:8400`, the preview address `ci/cookbook.py` names, then open `http://127.0.0.1:8400/` | §2 | the terminal it runs in |
| **The trio**: the harness, its web front end and its terminal front end | `uv run qm dashboard` says what is up and prints the command for what is not; `uv run qm dashboard --start harness --start web` brings the first two up on their reserved ports; the terminal front end runs in a terminal of its own, as the dashboard says | §3 | `uv run qm dashboard --stop harness --stop web` |
| **joe's open set**, by hand | joe's `docs/paths/manual-validation.md`, on its branch `docs/manual-validation-checklist` (joe #61, stacked on joe #52); its own §0 says what to start | that page | that page |

The docs site is static. A page that reads wrong is a generator's output, so
the fix is in `ci/` and the page is regenerated, never edited under `docs/`;
`handbook/generated-documents.md` indexes the generated documents and the
command behind each.

## 2. What landed on `main` on 2026-10-31, and what to look at

Merged in this order, each with every host gate green. The site at the
address above is built from `main` at the stamp.

| PR | What it is | Look at |
|---|---|---|
| #293 | the monitoring-seam record reads `qmcp` as it is at `ed01fc0` | `records/DRAFT-monitoring-seam-and-instance-identity.md`: its port, expiry-write and gate rows against `qmcp`'s code at that commit |
| #250 | the governance submodule is vendored by its HTTPS URL, and the pin check refuses any other | `handbook/forking-a-project.md`'s clone and submodule lines, followed as a stranger would; the new entry in `docs/ref/ci/gates-and-checks.md` |
| #248 | cathy is in the roster as an adopted project | `ci/workspace.yaml`'s cathy row and the family it names; the families index on the site, whose member counts moved with it |
| #285 | every showgraph drawn as a Showcase, and the whole corpus a family at a time | the families index's Showgraph, every family at once; each family page's Showgraph; each project page's pictures; `ci/showcase.yaml`, where a person's picks live |
| #295 | a record decides how a shared allowance is drawn on | `AGENTS.md` item 20 and `project-seed/ide/AGENTS.md` item 16 against the record's Decision; the perspective's account of the hour it cost |
| #277 | joe's open set has a handoff, and the voice pages say how joe #33 was tested | `handbook/handoffs/joe-open-set.md` against joe's open pull requests on the host; the changed rows of `voice-set-landing.md` |
| #272 | the triplet's graph leg has a handoff and a perspective | `handbook/handoffs/the-triplet.md` against what #285 landed: which of its phases the site now shows, and which it still describes as ahead |

What the site cannot show is whether a repository works. Every page reports
what the organisation claimed and what the generating disk held; a figure that
differs between the site and the host is a finding.

## 3. The trio, when it is up

`uv run qm demo --over-http` runs one topology through every window and says
whether they agree. `uv run qm journey-pictures` takes the journeys' pictures
from the surfaces that are up, and a changed picture under `docs/journeys/`
is a diff to read, not a page to fix. `docs/journeys/` is what a person is
walked through; walk it with the surfaces up and write what differs in §5.

## 4. Decisions only a person takes

- **#222**, the triplet plan, is a draft against `main`. A draft is unfinished
  or stacked, and this one is neither; it is either made ready and merged,
  once `handbook/handoffs/the-triplet.md` says which of its phases are done,
  or closed.
- **alfred's `feat/ui-journeys`** and the five branches folded into it exist
  on this disk alone, above alfred's open stack; `uv run qm estate` lists
  them. Pushing them is the owner's act.
- **titanharvest's design branch** is in the same state.
- **Worktrees a tool may not remove.** A worktree that carries the governance
  submodule is removed only by force, and a tool's permission to do that is
  the person's to give; each one's tip is on its repository's `main` or on a
  remote branch, so removing it loses nothing.

## 5. Findings

| # | Where (page, PR, loop) | Did | Saw | The page says | Owning PR | State |
|---|---|---|---|---|---|---|
| | | | | | | |
