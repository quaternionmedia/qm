# Handbook — Generated Documents, and How a Dashboard Is Built Here

**Routing.** The convention every generated status document and every view of
one follows. It binds QM's own tooling, not any project's design. Promoting a
clause follows `handbook/public-by-default.md`'s path.

**Audience.** Anyone adding a dashboard, and — more often — the next agent
opening a repository and wondering whether these numbers can be believed.

---

## Read this first, if you are an agent

Two documents are committed at the corpus root. **Read them instead of
re-deriving what they hold**, and check the age before you quote anything.

| Document | Holds | Quotable for | Refresh |
|---|---|---|---|
| `governance-status.yaml` | where every project stands: branches, records, adoption artifacts | 168h | `python ci/governance_status.py --write governance-status.yaml` |
| `harness-status.json` | pull request slots, phases claimed, governance evidence, **threads in flight** | 24h | `python ci/harness_status.py --no-local --write harness-status.json` |

Each carries its own refresh command, its own staleness budget, and its own
`do_not` list **inside the file**, so you do not need this page to read one
correctly. `/cowork` prints both with their current age.

To read the harness document as prose rather than JSON:

```
python ci/harness_dashboard.py harness-status.json --format md
```

`/status` runs both commands and reports what needs a person.

### Which repository do I run a view in?

Three answers, and confusing them is the most common way to conclude the
dashboard is broken. All of these are run **from the corpus root**, in this
repository:

```
python ci/harness_dashboard.py harness-status.json --format md    # agent view
python ci/harness_dashboard.py harness-status.json --out status.html
python ci/governance_render.py                                    # the other document
```

In **`quaternionmedia/dossier`** — one command does refresh, load and launch:
`dossier governance dashboard --corpus-dir <this corpus> --refresh`. With
`--refresh` it runs the two commands above in this checkout, so the "refreshing
is a human or agent action" rule still holds — a person asked for it, and the
diff it leaves in this repository is theirs to review. Its refresh path is
deliberately outside its renderer, so the no-commands-in-a-view rule holds
there too.
Its `docs/governance.md` carries the prep, which is not optional: a project's
vendored `governance/qm` is pinned to its own branch, cut from **`main`**, and
neither document is on `main`. So the path a project would naturally read is
empty by construction until the change adding them lands and the pin is bumped
past it. Until then a reader there needs pointing at a corpus checkout.

In **every other project** — nothing. The documents describe all of them and
are generated and stored only here. Looking for a dashboard in `alfred` or
`apothecary` finds nothing because there is nothing to find, not because
something is misconfigured.

The budgets differ because the things differ. Pull request slots turn over in
hours — six sessions produced eight in a day — so a figure from yesterday
describes an organisation that no longer exists. Adoption artifacts move when
somebody merges a propagation, which is weekly at best.

**A stale document is not a useless one.** It says true things about the commit
it names, and it names it. Read it for shape at any age; re-derive any figure
you are about to act on.

## The shape every dashboard here takes

Three artifacts, and the separation is the whole design:

1. **A document.** Generated, committed, `schema`-versioned. It talks to git,
   the host, and the filesystem. It is the only thing that does.
2. **A human view.** HTML, rendered from the document and nothing else.
3. **An agent view.** Markdown, rendered from the same document and nothing
   else.

`ci/harness_status.py` → `ci/harness_dashboard.py --format html|md` is the
worked example; `ci/governance_status.py` → `ci/governance_render.py` is the
one it copied.

**A renderer may not run a command.** A view that can shell out is a second
place a governance rule gets defined, and two definitions drift. If a fact is
not in the document, the fix is a change to the generator. Both renderers here
are tested for it — the assertion is that the word `subprocess` does not appear
in their source.

**A view may not write to its document.** A renderer that edits its own input
creates a second source of truth for one fact.

## The rules a document follows

**`unknown` is a value, and it is not a synonym for fine.** Any fact the
generator could not establish is written `{"unknown": "<reason>"}` — never
omitted, never defaulted. A repository whose pull requests could not be read
must not render like a repository with none: one is an absence of evidence and
the other reads as compliance. Both documents use the same spelling, so one
parser shape reads both.

**Every view carries three states, not two.** `ok`, `warn`, `unknown`. A view
with only the first two must render a thing it could not measure as one of
them, and it always picks the reassuring one.

**State is carried in form as well as colour**, so a row needing attention
survives being printed, read in monochrome, or parsed.

**The generation time is shown at the top, not in a footer.** A dashboard that
looks live and is three days old is worse than one that admits its age, because
the first stops people checking.

**A state is not a percentage.** The thread stages — `local`, `pushed`,
`draft`, `ready` — are observable states of a branch. Nothing estimates
completion, because the corpus has no definition of done a tool could read, and
a number that looks like progress is the most confidently wrong thing a
dashboard can print. A view that showed 60% would be believed.

**A claim and its evidence are separate, and neither derives from the other.**
The phase in `ci/workspace.yaml` is what a human stated; the governance column
is what has landed on a default branch. A view shows both and shows the gap.
Nothing rewrites a claim to match its evidence, and nothing infers a claim from
artifacts — see the phase-ladder record for why that second one is the tempting
mistake.

**Machine-scoped facts are labelled and never committed.** `harness_status.py`
can collect a `local` layer — branch names, uncommitted counts, unpushed work —
which is true for whoever ran it and nobody else. The committed copy omits it,
and the tool **refuses** to write it to a path inside the repository rather
than trusting anyone to remember.

**Documents are not regenerated in CI.** Both read other repositories, so an
unrelated pull request elsewhere would make the committed copy "stale" with no
commit here to explain it, and every pull request would go red for a reason its
author cannot fix. What CI checks is that the committed document parses,
matches its schema, and renders. Refreshing is a human or agent action.

## The failure this convention is written against

A governance dashboard does not report the wrong answer. It draws a reassuring
picture of one, and the picture stops people checking. Every rule above is one
of the four ways that has happened here: an absent document rendered as an empty
page, an unknown rendered as a blank cell, a stale document rendered as a
current one, and a repository with drift rendered identically to one without.

So: **every signal needs a fixture in which it reports bad**, and after writing
that fixture, break the renderer in the way it names and confirm the test
fails. Six inert tests were found that way while these two dashboards were
built — including one that matched a phrase a *different section of the same
page* also produces, and would have passed against a renderer with the check
removed entirely.
