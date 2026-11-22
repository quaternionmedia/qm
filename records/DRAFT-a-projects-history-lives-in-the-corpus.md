# QM-XXXX — A Project's Docs Are Timeless, and Its Dated History Lives in the Corpus

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-31 |
| **Namespace** | org |
| **Binds** | Each project that adopts it by a record of its own, and this corpus's documentation site |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `decisions-are-documented` — Git is the archaeology, and an account no reader of the project can find is one the organisation does not hold; `show-it-by-running-it` — a timeline typed by hand is a second copy of dates Git already keeps |

## Context

A project's repository is read at a commit. Its README, its `docs/`, its
in-repo pages and its agent instructions are what a reader finds there, and
`records/DRAFT-durable-text-states-what-is-true.md` asks each of them to state
what is true now. That record keeps history out of durable text and sends it
to the commit, the pull request and a dated retrospective. This record builds
on it.

A project produces a second kind of text as it is developed: the account of
how it got where it is. A retrospective of a release or of a method that
failed; a log of development rounds, each with its branch, its pull request
and its date; the counts each round measured, such as how many tests passed;
and the order in which things happened. Each of these is true of a day and a
commit, and none of it is true at the next commit.

The durable-text record names `perspectives/` as the corpus's place for a
retrospective, and names no place for the rest of a project's account. With
no place of its own, the account settles in the project's pages: a
changelog's unreleased section grows a table of rounds and a table of measured
counts, and a docs page carries a retrospective. There it is published as the
project's documentation, read at commits it does not describe, and lengthened
by every round. `records/DRAFT-few-integers-in-durable-text.md` §2 keeps a
measured figure true by naming its command and its commit; a count in a
project's page, read at a later commit, names neither.

`perspectives/` is the corpus's attributed opinion about its own practice,
indexed for a maintainer's review. A project's round log and its counts are
facts about one project rather than opinion, and a reader looking for one
project's history looks from that project.

The corpus already publishes a page for each public project,
`docs/projects/<name>.md`, generated from committed sources under
`records/DRAFT-a-project-page-shows-what-was-picked-and-what-was-drawn.md`.
Git already holds most of the dates a timeline needs: a merged pull request is
a merge commit on the default branch, and a version is a tag. Git does not hold
the grouping a person makes of them: which branch was a round, what the round
carried, and what was measured on it.

## Decision

1. **A project's docs are timeless.** Its README, its `docs/`, its in-repo
   pages and its agent instructions carry no dated history: no retrospective,
   no History section, no table of rounds, no measured count and no date of an
   event. Each states what is true at the commit it is read at, as the
   durable-text record's §1 to §3 ask.

2. **A changelog is release notes.** It says what changed in each version,
   under that version's heading, and is dated by nothing but the version,
   whose tag carries the date (`records/DRAFT-version-tags-are-claims.md`). Its
   unreleased section says what has changed since the last version, without
   rounds, branches, pull request numbers, counts or dates.

3. **A project's dated account lives in the corpus**, in the subtree
   `docs/projects/<name>/`, and the project's page links it. The subtree
   holds:

   - `timeline.md`, generated: what happened, newest first, each entry with
     its date and a link to its pull request, branch or tag on the host;
   - `rounds.yaml`, curated: each development round's branch, pull request,
     dates and what it carried, and each count measured on it with the commit
     or branch it was measured on;
   - `git.yaml`, generated: the git facts the timeline is drawn from, being
     the pull requests merged on the default branch, the tags with their
     dates, the branches on the host that the default branch does not hold,
     each with the branch it is stacked on, and the commit they were read at;
   - the project's retrospectives, each dated, with every link it carries
     absolute.

   This subtree is the dated retrospective the durable-text record's §2 and §6
   send a project's history to, once the project has adopted this record. A
   retrospective whose lesson is the organisation's rather than one project's
   stays in `perspectives/`.

4. **The timeline is generated, and checked.** `uv run qm timeline <name>
   --write` reads the project's clone, found where the corpus's other tools
   find a sibling clone, writes its git facts to `git.yaml`, and writes
   `timeline.md` from `git.yaml` and `rounds.yaml`. `--check` reads the
   committed files alone and refuses a `timeline.md` that differs from what
   they give, so it runs where no clone is. A round enters `rounds.yaml` in a
   pull request here, which runs the command and commits what it writes.

5. **Each project adopts this by a record of its own**, on its
   `project/<name>` branch, naming what moves out of its pages and into its
   subtree. From its adoption, the project's history is added here and not
   in its repository. A project that has not adopted this record is not bound
   by §1 and §2.

6. **The corpus's own history stays where the durable-text record puts it**:
   in commits, pull request bodies and `perspectives/`. The corpus is not a
   project in this record's sense, and has no subtree.

### What this does not decide

- **What a round is.** A project that does not work in rounds keeps no
  `rounds.yaml`, and its timeline is drawn from git alone.
- **Which counts a round records.** The round log carries what a round
  measured; which suites a project measures, and how, is the project's own.
- **The order of the move.** A project's adoption record says when its pages
  lose their history and its subtree gains it. The two land as pull requests
  in two repositories.

## Enforcement, and its edge

`.github/workflows/docs-audit.yml` runs the timeline's `--check` on every pull
request that touches the site or the timeline's tooling, and fails on a
`timeline.md` that differs from its committed inputs.
`project-seed/ci/check_timeless.py` reads the corpus's project subtrees as
dated pages, which the durable-text record's §4 exempts, and keeps checking
the project pages beside them. `ci/doc_status.py` classes a subtree's
`timeline.md` as generated and its retrospectives as dated history.

The check compares the timeline with the committed files and sees nothing
else. It cannot see a `git.yaml` that is behind its project, which the page
shows by naming the commit it was read at; a round left out of `rounds.yaml`;
or a count copied wrongly from the run that produced it. In a project, nothing
mechanical refuses a dated passage: the timeless gate exempts a changelog, and
a round table or a count in neutral words passes it. The project's adoption
record, and its reviewer, read for those.

## Consequences

- A project's pages get shorter, and a reader of the project at any commit
  reads only what is true there. A reader looking for what happened reads it
  on the corpus's site, one link from the project's page.
- The dates on a timeline come from git. A person writes only what git cannot
  know: the rounds, what each carried and what each measured, with dates taken
  from git.
- A round costs two pull requests, one in the project and one here, and the
  session that closes a round needs the corpus at hand. The cost is accepted:
  the project's pull request changes its code and its timeless pages, and this
  one adds the dated account, which belongs to no commit of the project.
- A refresh needs the project's clone on the machine that runs it, and the
  check cannot tell that a snapshot is behind. The page names the commit it
  read, so its age is read off the page.
- The durable-text record's §2 and §6, and the sorting table in
  `handbook/style-guide.md`, name a project's subtree beside `perspectives/`
  as a home for its narrative.
- The site's project pages are generated by the cookbook, and a subtree is
  not: its timeline is written by the timeline's own command, its round log
  and its retrospectives by hand. A project page links its subtree when the
  subtree exists.
- A retrospective moved into a subtree from a project keeps its content.
  Its links to the project's files become absolute, because the subtree is
  published from the corpus, where a path relative to the project resolves to
  nothing.

## Alternatives considered

1. **Keep the history in the project, in a dated folder its docs leave out.**
   Rejected: it is still read at commits it does not describe, it ships with
   every checkout, each project invents its own layout for it, and a reader of
   the organisation does not find it.
2. **File a project's retrospectives under `perspectives/`.** Rejected:
   `perspectives/` is attributed opinion on the corpus's practice, indexed for
   a maintainer to review. A project's round log and counts are facts about one
   project, and filed there they are found by nobody reading that project. A
   retrospective whose lesson is the organisation's still goes there.
3. **Use the host's release pages as the history.** Rejected: a page on the
   host is outside every repository
   (`records/DRAFT-work-is-delivered-into-a-repository.md`), cannot be reviewed
   as a diff, and holds no rounds or measurements.
4. **Write the timeline by hand.** Rejected: it is a second copy of the dates
   git keeps, and it drifts from them. Generated, it leaves a person only the
   grouping git cannot know.
5. **Draw the timeline from the clones when the site builds.** Rejected: the
   runner has no clones, and a timeline drawn there would be published without
   ever being a diff anybody read. A committed snapshot makes the git facts
   reviewable, as the project-page record makes a drawn graph reviewable.
6. **Delete the history and leave it to git.** Rejected for the reason the
   durable-text record gives against the same move: git keeps it where nobody
   reads it, and the rounds and their counts are not in git at all.

## Revision triggers

- A project adopts whose work does not come in rounds, or whose rounds do not
  fit `rounds.yaml`'s shape.
- The corpus's site stops publishing project pages, or a project's readers
  stop reading the corpus's site.
- A host offers a history built from a repository's commits and reviewed as
  its diffs.
- Snapshots behind their projects become common enough that the check's green
  reads as current.

## Amendments

*None.*
