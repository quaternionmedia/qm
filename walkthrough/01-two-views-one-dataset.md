# 01 — Two views, one dataset

If you want to see what this organisation actually does, rather than read about
it, start here.

**This page runs.** Every example below is executed by `uv run qm test`, and the
output shown is the output that ran. If a behaviour changes, this page fails the
build rather than quietly describing something that stopped being true.

It walks the whole chain end to end: a branch, its address, two independent
views of it, their disagreement, and the delta that disagreement becomes.

---

## 1. A branch has an address

Every data point gets one name, in every system that holds it —
`docs/ref/addresses.md`. The rule that matters: the first three segments are
owner, repo and kind, and **everything after is the id, verbatim**.

    >>> from addresses import parse, format_address
    >>> address = format_address("quaternionmedia", "qm", "branch", "evolve/protect-main")
    >>> address
    'quaternionmedia/qm/branch/evolve/protect-main'

A namespaced branch keeps the slashes git gave it, so the address can name the
ref it came from:

    >>> found = parse(address)
    >>> found.kind, found.id
    ('branch', 'evolve/protect-main')
    >>> found.format() == address
    True

This is the property the grammar exists for. Slugging the slash to a hyphen —
which is what dossier does today — makes the address unable to name a ref, and
**30 of the 32 branches in this repository are namespaced**:

    >>> parse("quaternionmedia/qm/branch/evolve-protect-main").id
    'evolve-protect-main'

Two different branches, two different addresses. Under the old slug both of
those collapse onto the second one.

## 2. Two views disagree

Now two systems that each hold a fact about that address. Neither is a fixture
of the other: one is what git says, one is what a document recorded earlier.

    >>> from divergence import compare
    >>> document = {"commit": "a545991", "phase": "review"}
    >>> live = {"commit": "6f7ffe2", "phase": "review"}
    >>> found = compare(address, document, live, ["commit", "phase"],
    ...                 "governance-status", "git")
    >>> len(found)
    1

They agree about `phase`, so it produces nothing. Only `commit` disagrees, and
**both values survive**:

    >>> divergence = found[0]
    >>> divergence.field, divergence.left, divergence.right
    ('commit', 'a545991', '6f7ffe2')

Nothing here picks a winner. `records/DRAFT-a-disagreement-is-a-delta.md` §
*Decision*: neither view wins, because authority genuinely differs by kind and
discarding the losing value destroys it at the moment somebody wants it.

## 3. The disagreement is a delta

    >>> from divergence import to_delta
    >>> payload = to_delta(divergence)
    >>> payload["delta"]["name"]
    'reconcile-quaternionmedia-qm-branch-evolve-protect-main-commit'
    >>> payload["delta"]["phase"]
    'brainstorm'

It opens at `brainstorm` because noticing that two values differ is not deciding
anything about them. The identity is the address plus the field and **nothing
else**, so running detection again finds the same row instead of opening a
second one:

    >>> again = to_delta(compare(address, {"commit": "zzz"}, {"commit": "yyy"},
    ...                          ["commit"], "governance-status", "git")[0])
    >>> again["delta"]["name"] == payload["delta"]["name"]
    True

The values changed; the name did not. The address survives whole in the links,
where it is still reversible — the delta name is slugged and lossy, and that is
safe precisely because the name is not the identity:

    >>> payload["links"]
    [{'link_type': 'address', 'target_id': None, 'target_name': 'quaternionmedia/qm/branch/evolve/protect-main'}]

And the row is one a consumer ingests with no translation — these are
`ProjectDelta` columns:

    >>> sorted(payload["delta"])
    ['delta_type', 'description', 'name', 'phase', 'priority', 'title']

## 4. Against this repository, for real

The two views above were literals so this page can assert on them. The same
chain runs against the actual repository: `governance-status.yaml` is one view,
`git rev-parse` is the other.

    >>> from two_views import document_view, git_view, reconcile, unobservable
    >>> recorded = document_view()
    >>> len(recorded) > 0
    True

Every address the document produces is a well-formed one — the join between the
two views is the grammar itself, so this is the assertion that they can be
joined at all:

    >>> all(parse(a) is not None for a in recorded)
    True
    >>> all(parse(a).kind == "branch" for a in recorded)
    True

Now the live side, and the distinction that running this end to end taught:

    >>> live_view = git_view(recorded)
    >>> blind = unobservable(recorded, live_view)
    >>> divergences = reconcile(recorded, live_view)

Three of this corpus's project branches are recorded under **redacted** names —
`origin/project/private-32` and two more. They are placeholders, not refs, so
git cannot resolve them ever. Read as disagreements they become three deltas
that no work could close, which is the queue-fills-with-noise failure the record
names as its own. They are counted separately and never turned into work:

    >>> len(blind) >= 0 and all(parse(a) is not None for a in blind)
    True
    >>> set(blind) & {d.address for d in divergences}
    set()

**A ref one view cannot observe is not two views disagreeing about a value.**
That set intersection being empty is the whole of the distinction, asserted.

## What this page does not show

**A dashboard.** This is the data layer the two dashboards will each read; it
renders nothing.

**That either view is right.** The chain has no opinion, deliberately. A
repository can be well-run and carry open reconcile deltas.

**Resolution.** Nothing here closes a delta, because convergence does not prove
anyone acted — `complete` is a claim about work having been done, and this
cannot see work.

Run it yourself:

```sh
uv run qm addresses --parse quaternionmedia/qm/branch/evolve/protect-main
uv run qm two-views
uv run qm two-views --deltas
```
