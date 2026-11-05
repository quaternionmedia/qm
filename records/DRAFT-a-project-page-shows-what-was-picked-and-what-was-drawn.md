# QM-XXXX — A Project Page Shows What a Person Picked and What a Tool Drew, and Is Never Written by Hand

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-28 |
| **Namespace** | org |
| **Binds** | This corpus's documentation site |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `show-it-by-running-it` — a page kept beside its sources is a second copy that drifts; `decisions-are-documented` — a rule held in a file's comment binds nobody who reads the governance; `ownership-is-the-deliverable` — a project's pictures are its own, shown from its own repository |

## Context

The documentation site has a page for every family and every project the
roster names, an index of them, and a front page that shows a few. A project
page carries two kinds of picture.

The **showcase** is the pictures a person chose to represent a project:
screenshots, a panel, a rig. They are files in the project's own repository,
listed with a caption in `ci/showcase.yaml`. The rules for them are written in
that file's opening comment and nowhere else.

The **showgraph** is the graphs a tool drew of a subject: a project's code, its
estate, its system, a family, the whole corpus. `uv run codecarto show export`
draws them from the clones on one machine and writes each subject's pictures
beside a show document, `docs/show/<kind>/<name>/show.json`, that names the
subject, the corpus commit and the source commit it read, the drawer and the
commit it ran at, and when it drew. Nothing in the governance text describes
them.

`uv run qm cookbook docs/families --site --write` writes every family page,
every project page and the front page's included snippets from four committed
sources: `families.json`, `status/inventory.yaml`, `ci/showcase.yaml` and
`docs/show/`. Each page says so at its foot. Unless something checks that a
page still matches its sources, a page edited by hand, or a source changed
without the pages, passes every gate, and a reader of the document states
takes the pages for hand-written reference.

The two kinds fail differently. A picked picture is wrong when it shows
something the project is not, and only a person can tell. A drawn graph is
wrong when it is stale or was drawn from the wrong commit, and its document
can say which.

## Decision

1. **The family pages, the project pages and the front page's snippets are
   generated, and are never edited by hand.** `uv run qm cookbook
   docs/families --site --write` writes `docs/families/`, `docs/projects/` and
   `includes/` from the four sources above. A change to a page is a change to
   its source, followed by the command. `--check` with the same arguments
   refuses a page that no longer matches its sources, and runs on every pull
   request that touches either.

2. **A showcase picture is picked by a person.** It is listed in
   `ci/showcase.yaml` with a caption of one sentence saying what it shows. It
   is a file the project's default branch holds, shown from that branch, so it
   is the project's own and changes when the project changes it. A listed file
   the default branch does not hold yet is held back, not shown. A project with
   no entry has a page that says it has no pictures, and nothing infers one for
   it.

3. **A showgraph is drawn by a tool, and is regenerated, never edited.** Its
   pictures and its show document are committed together under `docs/show/`,
   and the document states what was drawn, from which commits, by which tool at
   which commit, and when. A page shows each showgraph with that statement
   beneath it. A view the tool did not draw is shown as absent with the tool's
   reason, and a subject with no document is said to have none; neither
   borrows a picture.

4. **The two are never mixed.** A drawn graph is not listed as a showcase
   picture, and a picked picture is not written into `docs/show/`. A page may
   set both in one section; each keeps its own rule.

### What this does not decide

- **The words.** Whether *showcase* also names the drawn graphs, and a
  terminal view beside them, is an open question in the triplet plan, a draft
  on `evolve/the-triplet`. This record uses the two words as the pages use
  them and settles neither.
- **Which views are drawn,** at what depth, and for which subjects. That is
  the drawer's design, and the triplet plan's.
- **How old a showgraph may be.** A show document carries the date it was
  drawn and the commits it read; no gate measures its age.

## Enforcement, and its edge

`.github/workflows/docs-audit.yml` runs `uv run qm cookbook docs/families
--site --check` on every pull request that touches the pages or their sources,
and fails on a page that has drifted from them. `ci/tests/test_cookbook.py`
holds `ci/showcase.yaml`'s shape and the layout of a page's showgraph.
`ci/doc_status.py` classes the generated pages as generated, so the corpus's
document states say *do not edit by hand* of them.

The check compares pages with their sources and sees nothing else. It cannot
tell a caption that misdescribes its picture, a picture that shows something
the project is not, or a show document drawn from a commit the project has
since moved past. The first two are read by the person who picks; the third is
read from the date and the commits on the page.

## Consequences

- A page's text and pictures change only through their sources, and a reviewer
  reads the change as a diff of those sources plus the regenerated pages.
- A showcase picture costs a commit in the project's own repository before it
  shows; a picture still on a pull request there is previewed with `uv run qm
  cookbook --preview <dir> --ref <project>=<ref>`, never shown on the site.
- A showgraph costs a run of the drawer on a machine that holds the clones, and
  its pictures are committed to this corpus. Their size and their age are
  accepted: the pictures are reviewable as files, and their document says what
  they are true of.
- A pull request that adds or changes a showcase entry, or draws the
  showgraphs again, regenerates the pages in the same pull request, or the
  gate refuses it.
- A project's version on its page follows whether its `project/<name>` branch
  exists, and creating that branch changes no file the gate watches. The pages
  are then stale until the next pull request that touches them, which
  regenerates them or is refused. That pull request pays for a change it did
  not make; the cost is accepted, because the alternative is a gate that runs
  on every pull request in the corpus.

## Alternatives considered

1. **Write project pages by hand.** Rejected: a page describing a project from
   outside it is a second copy of what the roster, the inventory and the
   project already say, and it drifts the moment any of them moves.
2. **Infer a project's pictures**, say the first image in its README.
   Rejected: a project decides how it is seen, an inferred picture is as likely
   to be a badge or a placeholder as the thing itself, and a wrong one is shown
   with the same authority as a right one.
3. **Draw the showgraphs during the site build.** Rejected: the build would
   need every project's clone and the drawer's toolchain on the runner, and its
   pictures would be published without ever being a diff anybody read. A
   committed show document makes the drawing reviewable and its provenance a
   fact.
4. **Leave the rules in `ci/showcase.yaml`'s comment.** Rejected: a comment in
   a data file is read by whoever edits that file, and by nobody who reads the
   governance; and the showgraph had no text at all.

## Revision triggers

- The triplet plan lands with a registry or a vocabulary that differs from §2
  to §4.
- A second tool draws showgraphs, or the drawer changes.
- A showcase picture is wanted from a repository whose default branch is
  private, so `raw/HEAD` cannot serve it.
- The site stops being generated from these sources.

## Amendments

*None.*
