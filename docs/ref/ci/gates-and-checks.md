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

## Shared shapes

- **An exception costs a stated reason.** `timeless: allow`,
  `principle-name: allow` and the [ADR](../../ref/glossary.md#adr){ .glossary-term } lint's allowance all take a reason on
  the line, and a bare marker counts for nothing.
- **A limit is printed.** Each check states what it cannot see, in its own
  output where a reader meets it.
