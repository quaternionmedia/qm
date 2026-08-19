# Addresses

**One data point, one address, in every system that holds it.**

```
<owner>/<repo>/<kind>/<id>
```

The first three segments are owner, repo and kind. **Everything after the kind
is the id, verbatim — slashes included.** A bare `<owner>/<repo>` denotes the
repository itself.

```sh
uv run qm addresses                    # the grammar and every kind
uv run qm addresses --parse <address>  # what one address denotes
uv run qm addresses --check            # every conformance vector round-trips
```

## Why this exists

dossier and qmcp hold overlapping facts about the same repositories, and each
names them its own way. dossier builds names by interpolation in
[`parsers/autolinker.py`](https://github.com/quaternionmedia/dossier) in dossier, and reads them back by substring in its `cli.py` —
`elif "/branch/" in name`. qmcp names nothing at all: a step is a bare `name`,
an invocation a bare UUID. Two views of one dataset need one way of pointing at
a row.

## The defect that forced the rule

dossier addresses a branch as `owner/repo/branch/` plus
`branch.name.replace("/", "-")`. So `evolve/protect-main` becomes
`.../branch/evolve-protect-main`, which is **not reversible**: a branch
legitimately named `evolve-protect-main` produces the identical address, and
neither can be turned back into a ref git accepts.

**30 of the 32 branches in this corpus contain a slash**, because every
namespace is `evolve/`, `project/`, `perspective/` or `propagate/`. Listing
active branches as deltas means linking a row to a ref, and that link is broken
for almost every branch in the organisation.

Taking everything after the kind as the id fixes it with no escaping and no
slug. `quaternionmedia/qm/branch/evolve/protect-main` parses to
`evolve/protect-main` and formats back to itself.

## The kinds

The set is closed. A third segment outside it means the string is **not** a
repo-scoped address — which is what stops `owner/repo/some/path` being read as
one.

| kind | id is |
|---|---|
| `branch` | a git ref, named exactly as git names it |
| `pr` | a pull request number |
| `issue` | an issue number |
| `ver` | a version tag, as pushed |
| `doc` | a document section, `type-slug` |
| `delta` | a unit of work, by its short name |
| `invocation` | a recorded tool call, by id |

`delta` and `invocation` are the two the dashboard milestone needs: a workflow
step in qmcp and a delta in dossier are one unit of work, and
`records/DRAFT-…`-style prose about "the same thing seen twice" only becomes
mechanical once both name it the same.

**Reserved, and not repo-scoped:** `github/user/<u>`, `lang/<l>`, `pkg/<p>`.
These are dossier's global buckets. They are named here so that an owner called
`lang` is a collision somebody chose rather than one they discovered.

## Two implementations, one set of cases

`ci/addresses.py` is the reference implementation and it is **not** something a
project imports. Coupling dossier or qmcp to the corpus's Python would mean
neither ships without it, which is the same trade
[`qmcp/cookbook/delta.py`](https://github.com/quaternionmedia/qmcp) refuses for
the delta schema.

Instead, `project-seed/address-vectors.json` reaches every fork through the
governance submodule, and each implementation runs the same cases. A vector
carries the address, whether it should parse, the parts it parses to, and a
reason it is in the file.

**Every valid case must also format back to the identical string.** The round
trip is the assertion: a parser checked only on its output can drop a segment
and still look right — `.../branch/evolve/protect-main` read as `evolve` is a
plausible branch name and nothing about the parse says otherwise.

Adding a case is the right response to any address read wrongly in the wild.
Removing one needs a reason.

## What this cannot do

**Tell you the thing exists.** `quaternionmedia/qm/pr/99999` is a well-formed
address for a pull request nobody opened. Resolution belongs to each system, and
folding it in here would make rendering a dashboard depend on a network call.

**Say which system is authoritative.** Two views of one address may disagree —
dossier's row for a branch and the git ref itself can drift. The address makes
the disagreement expressible, and says nothing about who wins.

That is deliberate, and settled: by
[`records/DRAFT-a-disagreement-is-a-delta.md`](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-a-disagreement-is-a-delta.md)
neither view wins. **A disagreement between two views of one address is a
delta** — a unit of work with a name, a lifecycle and an audit trail, closed by
somebody deciding rather than by the comparison being run again. `uv run qm
divergence` is the mechanism. Detection opens the delta at `brainstorm` and
never closes one, because convergence does not prove anyone acted.

**Enforce itself.** Nothing rewrites dossier's existing slugged names. The
grammar is checkable and adopted deliberately; migrating the rows already
written is separate work, and the addresses in the database today were built by
the code this page describes as broken.
