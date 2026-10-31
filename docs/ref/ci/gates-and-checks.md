# Gates and checks

The checks that refuse something. `uv run qm gates` lists every [gate](../../ref/glossary.md#gate){ .glossary-term } with what
it cannot see; this page describes the rules several checks share, and the
checks whose behaviour needs more than a docstring.

## Principle edges

`uv run qm edges` (`ci/check_principle_edges.py`) holds the charter,
`PRINCIPLES.md`, to its own declared shape. Every principle carries one line:

```
↔ Edges: rests-on credit-tracks-accountability, completes show-it-by-running-it
↔ Edges: none -- <a reason>
```

- **A declaration is required, an edge is not.** A charter made connected by
  effort looks checked and is worse than an honest sparse one. `none` is a
  first-class answer, and it costs a reason long enough not to be a label, so
  the honest answer is also the cheapest one.
- **Both ends.** An edge stated from one end only is refused: a reader arriving
  at the other principle would never learn of it.
- **A closed vocabulary with declared inverses.** `orders` and `ordered-by`,
  `completes` and `completed-by`, `rests-on` and `bears`, and the symmetric
  `shares-teeth`. A free string would let a typo become a category.
- **Names, not ordinals.** A principle is addressed by its name. A reference to
  a position that has shifted still resolves, to the wrong principle; a name
  moves with what it names. The check scans every binding directory for the
  ordinal form. `perspectives/` and `handbook/handoffs/` are not scanned, so an
  ordinal can survive there. A document that names the form in order to forbid
  it, or whose own numbering collides with it, declares
  `principle-name: allow` with a reason, on the line or once at the top of the
  file.

It cannot tell whether two principles actually conflict, or whether a stated
edge is true: that is a reading.

## The ADR lint

`project-seed/ci/adr_lint.py` enforces the four checks
`records/DRAFT-decision-record-discipline.md` names. It is a [seed](../../ref/glossary.md#seed){ .glossary-term } file run in
place: a project copies `adr-lint.yml` into its workflows and the workflow runs
the script out of the governance submodule, so the logic is always the version
the project's pin points at.

1. **Banned vocabulary in a pre-ratification draft.** Prose only: code fences,
   inline code spans and HTML comments are blanked first (keeping line
   numbers), because a document that quotes the banned list is describing the
   rule. Words with an innocent use are matched only in a narrating
   construction, and every rule can be escaped with a stated reason, read from
   the line or the line above; the count of exemptions is printed on every run.
2. **A numbered filename whose Status is not Accepted or later**, and its
   converse: an `Accepted` [record](../../ref/glossary.md#record){ .glossary-term } whose file was never renamed.
3. **An edit to an Accepted record's body outside its Amendments section**,
   including an edit by deletion alone. It needs `--base-ref`, and says so when
   skipped. In the branch-per-project model the records sit in a submodule, so
   `--base-ref` names a superproject commit; the check reads the submodule pin
   out of it and diffs that pin's tree against the one checked out, because a
   superproject cannot see inside a gitlink.
4. **The index and the record directory agree.** Two comparisons: by number,
   which can fire only after a [ratification](../../ref/glossary.md#ratification){ .glossary-term }, and by filename against the link
   targets of the index's table rows, which works from the first record. A
   record also counts as listed when its title, with its `QM-XXXX`, `ADR-XXXX`
   or `DRAFT` prefix removed, equals a whole segment of the index prose (the
   seed's "Drafts in flight" line). A counted allowance lets a stated number of
   records go unlisted, for a record whose title names a private repository.

It cannot see a record in a subdirectory of the records directory.

## Signatures

`project-seed/ci/check_signatures.py` refuses a branch whose own commits carry
no verifiable signature. Only `base..head` is checked, so a pull request never
fails on commits its author did not write. Locally `--source git` reads
`%G?`; in CI `--source host` reads the host's own verification, because a
runner has no signer's keys and its `%G?` describes its empty keyring. A good
signature by an untrusted key passes, since a trust store nobody maintains
would fail honest work.

Unsigned commits older than a cutoff date are grandfathered: reported, counted,
and not failed, because signing them would mean rewriting history. A range of
only grandfathered commits exits 0, and the summary never counts them as
signed. Commit dates are author-controlled, so a backdated commit is exempted;
refusing commits dated before their parent would break legitimate rebases.

## Submodule pins

`uv run qm pins` (`project-seed/ci/check_submodule_pins.py`) checks that every
submodule pin is a commit another machine could fetch.

| Remote | Commit | Verdict |
|---|---|---|
| readable | fetchable | ok |
| readable | not fetchable | UNPUSHED: a hard failure |
| not readable | — | UNKNOWN: private or gone; not a failure, never green |

`git ls-remote <url>` with no ref answers whether a remote can be read at all.
`git ls-remote <url> <sha>` does not answer whether a commit exists: it matches
ref names, and prints nothing for a perfectly good commit. A submodule's URL is
found through the `.gitmodules` entry whose `path` matches, because `git mv`
changes a submodule's path and keeps its name. SSH URLs are tried over https,
because a runner has no SSH key, and a filesystem path is reported as
resolvable nowhere else.

The governance submodule is the exception to that translation. The seed
workflows that run a corpus script clone it on a runner with
`git submodule update`, by the URL `.gitmodules` records and with no SSH key,
so any URL but HTTPS fails each of them at the clone, and a local run, which
has a key, passes. A checkout with `submodules: true` rewrites a GitHub SSH URL
to HTTPS; the seed's checkouts do not. So the governance URL's form is judged
before any fetch: anything but `https://` is `not-https`, a hard failure, and
the local run goes red as the runner does. The path is `$QM_SUBMODULE`, else
`governance/qm`, and `--governance` names another.

Locally it also lists branches inside each submodule's clone that are on no
remote: work committed inside a submodule is invisible to every check the
parent runs. That list is empty in CI, where submodules are cloned fresh, and
empty there is not a pass.

## The compile floor

`project-seed/ci/tests/test_every_script_compiles.py` and its [corpus](../../ref/glossary.md#corpus){ .glossary-term } twin
`compile` every script on every test run, so a file that does not parse is
found before a pull request rather than by a person later. They use `compile`,
not an import, so a fork that has installed nothing can answer; one test case
per property names every offending file and line in one failure; and a guard
fails if the glob matches nothing, since a vacuous check reports green. Tabs
mixed with spaces are refused, because they raise in some files and not
others. Anything deeper than "does it parse" belongs to `codecartographer`,
which a governance gate does not import.

## Leaks

`uv run qm leaks` (`project-seed/ci/check_leaks.py`) refuses committed text
that names a person, a machine or a private conversation: the leaks a secret
scanner does not look for, because none of them is a credential.

- **A home directory with an account name** in it, Windows, macOS or Linux.
  The pattern is case-sensitive, so `/users/` in a REST route is not a home.
  Placeholder accounts are listed in `PLACEHOLDERS`, and a new one is added
  there rather than by widening a pattern.
- **A shared-conversation link**, which anybody holding it can read.
- **A link to a hosted page**, one an assistant's host keeps outside every
  repository, such as a chat product's shareable artifact or canvas.
  [Work is delivered into a repository](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-work-is-delivered-into-a-repository.md),
  and a link to such a page points its reader at the copy that record rules out.
- **A path to a thread archive.** The archive's filename alone names an export
  format and is allowed; a directory in front of it is somebody's disk.
- **A personal directory used as a path** (the Documents or Desktop folder, an
  IDE's projects folder) and **a session's scratch space used as a path**:
  `handbook/what-is-not-the-organisation.md` draws that line, and a path is its
  mechanical part.

It reads tracked files only, because what is tracked is what is published.
Findings are printed redacted, enough to recognise and never enough to use,
and the summary carries the number of files read. An exemption is declared
with `leaks: allow` and a reason, and the count of exemptions is printed on
every run. It cannot read history, cannot tell a placeholder from a real name
beyond the listed ones, and cannot find a leak nobody thought of: `--json` is
there for a person reading the whole list.

## Branch census

`uv run qm branches` (`project-seed/ci/branch_census.py`) lists every branch in
a repository and what deleting it would lose. It reads refs, never the working
tree, and never deletes anything.

| Class | Meaning |
|---|---|
| stranded | The local ref is ahead of its own remote: commits on one disk |
| local | A local branch with no remote of its name, contained in no remote branch |
| ahead | Unmerged work that is pushed and reachable |
| held | A local branch with no remote of its name, whose tip another remote branch contains; deleting it loses the name |
| gone | A remote branch whose local ref is gone; nothing to lose |
| merged | Every commit is on the default branch; deleting loses nothing |

The classes sort by what it costs to be wrong, so what would be lost comes
first. A branch is read as held only once the host confirms its holder: one
`git ls-remote --heads` says which branches the host holds now, and a holder
the host has deleted, or moved to a commit the clone never fetched, does not
count. `--offline` asks the host nothing and reads holders from the tracking
refs, as of the last fetch. Loss is counted by patch, not by sha: `git cherry` reports a commit whose
patch is already upstream (squashed, cherry-picked, rebased) as landed, so a
branch ahead by one can hold nothing. It errs toward reporting loss, since a
commit that landed in a different shape still reads as unique. The default
branch is asked of the remote rather than assumed, `origin/HEAD` is not a
branch, and automation branches are summarised in one line. The summary and
the exit status share one definition of "at risk". It cannot tell whether an
`ahead` branch is abandoned or paused.

## Branch references

`uv run qm references <branch>` (`ci/branch_references.py`) lists what still
refers to a branch, asked before it is retired. The census says what deleting
a branch loses; this says what deleting it leaves pointing at nothing. It
reads four kinds of reference:

| Kind | What matches |
|---|---|
| name | The branch's name as written when it holds a slash, in backticks when it does not |
| commit | A commit no other branch holds, by its first seven characters |
| file | A file the branch adds that its base lacks, by path, or by a basename the base does not share |
| named | The branch's name in backticks on `docs/ref/namespaces.md`, where the stage refs are named, or a line there calling its namespace permanent |

It searches `main`, `--base` when that is another branch, and the head of every
open pull request but the branch's own, and skips the generated documents. A
pull request into a branch other than `main` is searched only in the files it
changes, since the rest of its tree is an older copy of `main`. A line a head
carries unchanged from `main` is reported once, as `main`'s.
Exit 0 is nothing found and 1 is a list of references. Exit 2 is a search that
could not run, an open pull request whose head is not fetched among them. It
cannot see another repository, a submodule pin there included, or a pull
request body, comment or issue.

## Record review

`uv run qm review` (`ci/record_review.py`) reads every record as one body and
reports what only shows in aggregate: an Enforcement clause naming a mechanism
that does not exist or that no gate declares; universals in a Decision section,
as candidates for reading rather than defects; citations of paths that do not
exist; and records nothing points at. A citation into another QM repository is
resolved in that repository's checkout, found through the roster's
`repositories:` and `paths:`, and is reported as a cross-repository citation,
not as dangling; a repository in the roster but not checked out is unknown. It
does not read a record for meaning, and it is a report, not a gate.

## Private repository names

`uv run qm private-names` (`ci/check_private_names.py`) refuses a private
repository name in a tracked file. It has three states, and only `clean` is a
pass: `found` exits 1, and `unverified` (no source of private names was
available) exits 0 but prints that word first; `--strict` makes it a failure.
A `found` is a name used as a repository (after a slash, as a quoted token, or
as a field naming a repository); prose containing a word that a private
repository happens to be called is reported as `possible` and never gated on.
Names are bounded by characters that cannot appear in a repository name, so a
longer public name containing a private one is not a hit. Occurrences are shown
redacted, by reference.

`--source local` reads the gitignored companions; `--source host` asks the
forge. No workflow runs it, because `registries.yml` admits only checks that
read committed files: this reads a machine. It is a command somebody runs. It
cannot read history.

## Merging

`uv run qm merge` (`ci/merge_review.py`) reads the contributor's open pull
requests and says which are ready; with a pull request and `--yes` it merges
that one. Ready is one definition, `blockers`, used by both the listing and the
act, and each blocker is named (the draft flag, a conflicting file, a check by
name) rather than reported as "not ready". The act re-reads the live state at
that moment. It merges with a merge commit only (a squash or rebase flag is
refused with the reason), retargets every pull request stacked on the merged
branch before deleting it, and never pushes, closes a pull request or touches
`main` by another route. Without `--yes` it stops with a non-zero status. It
cannot see whether a pull request should merge, only whether the host says it
can; `uv run qm branch` reads what a branch carries.

## The queue page

`uv run qm queue` (`ci/queue_page.py`) reads every pull request and issue that
`handbook/handoffs/qm-queue.md` names, in one query to the host, and lists each
one that merged or closed after the page's stamp, with how far each stamped
`main` has moved since. `--page` reads another handoff page. A bare `#N` is
`qm`'s; `name #N` belongs to the roster repository `name`, and so does a number
joined to it by a comma, "and", "or" or a slash. It exits 1 when anything the
page names changed after the stamp or resolves to nothing, and 2 when the page,
its stamp or the host cannot be read. No workflow runs it, because it reads the
host; a session runs it at open and close. It cannot see a pull request the
page never names, or whether a sentence claims one is open, and a stamp moved
without a re-read silences it.

## The declared-routes hook

`.claude/hooks/prefer_declared_routes.py` is an optional pre-command hook that
fires when a shell command goes around a route `qm` declares: `pytest` run
directly instead of `qm test`, mutation by hand instead of `qm mutate`, and the
like. It warns and allows by default; `QM_ROUTES_STRICT=1` makes it refuse. It
knows only commands that have a route, never fires on its own remedy (an
allow-list covers `uv run qm test`), reads shell commands only, and fails open:
input it cannot read, or that is not an object, lets the work through.
Enabling it is each contributor's decision.

## Shared shapes

- **An exception costs a stated reason.** `timeless: allow`,
  `principle-name: allow` and the [ADR](../../ref/glossary.md#adr){ .glossary-term } lint's allowance all take a reason on
  the line, and a bare marker counts for nothing.
- **A limit is printed.** Each check states what it cannot see, in its own
  output where a reader meets it.
