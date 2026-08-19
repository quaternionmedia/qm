# Handoff — the harness pair, and a fresh setup that works

**Stamped 2026-08-19. `qm` `main` at `13ea30b`, `dossier` `main` at `546de67`,
`qmcp` `main` at `31c6db8`.** Every figure on this page was true at those
commits and nowhere else. Re-derive before quoting one.

**Standing constraint: nothing is held back.** This page and its retrospective
arrived on `evolve/handoff-fresh-setup`, which is pushed and merged like
everything else this session produced. There are no unpushed commits and no
dirty trees in any of the three repositories. If a later session finds one, it
is not this session's.

*This paragraph has been wrong twice.* It first said nothing was held back while
the operator had asked for a local close; it then said the page was deliberately
local, which stopped being true when they asked for it to be pushed. A page that
describes its own state has to be re-read whenever that state changes, and
neither correction was prompted by a check — both were caught by reading.

---

## What exists now

**dossier** is a control panel that opens on an organisation-wide overview,
excludes forks from every figure, prepares its own database, and refuses to
open against one it cannot read. Its suite is split into `core/`, `db/`, `ui/`
and `e2e/`, and it carries four executable `walkthrough/` pages.

**qmcp** is the harness. It emits two payloads — units of work as deltas, and
what it has run as a dashboard view — and carries one `walkthrough/` page.
Neither repository imports the other.

**The corpus** carries a plain-language opening, a policy on integers in
durable text, and a `tag-determinism` gate registered in `ci/gate-registry.yaml`.

## What is unfinished

**The pair reconciles, it does not connect.** Payloads cross as files a person
copies: `qmcp dashboard --json` into `dossier harness ingest`. *Done* looks
like one of the two dashboards obtaining the other's state without a file being
named on a command line, and every harness figure still carrying how old it is.
`walkthrough/04-the-pair.md` in dossier states the gap rather than implying
otherwise, so the page does not need rewriting first.

**rad's conformance vectors are not wired to the terminal ring.** dossier
implements rad's keyboard path and is held to nothing. *Done* looks like the
vector file driving the Textual implementation with the pointer-only cases
listed by name rather than skipped. **This is blocked on a proposal to `rad`**,
recorded in `perspectives/2026-08-18-a-ring-in-a-terminal.md`: the vectors carry
no modality tag, so a keyboard-only host must either fail the pointer cases or
hand-curate a subset and lose the guarantee. Do not curate a subset locally.

**qmcp cannot be tagged.** Its suite skips tests needing metaflow and
pydantic-ai, and a skipped test contributes nothing to the automated-validation
claim. The gate now reports this at `uv run qmcp` time rather than at tag time.
*Done* looks like `check_tag_claims.py --test-output` accepting a captured run.
dossier reached that state this session by removing its own last skips; the
method was to read a vendored copy instead of a sibling checkout, and it does
not transfer — qmcp's skips are missing optional dependencies, not missing
paths.

**The public demo corpus.** Every non-archived, non-fork public repository in
the organisation, analysed and shown as one view. The data is local and the
overview renders it; what does not exist is the fetch-on-demand warm-up and the
narrowing to the public non-fork set. The sync currently pulls every repository
the organisation owns, forks and archives included, and the figures exclude
forks afterwards rather than at fetch.

## What is blocked on a human

**`qm` #57 is green and has been a draft since 2026-08-13.** It targets
`project/datum`, which holds its own slot, so it violates nothing. But the
corpus is explicit that draft means incomplete and is not a holding pen for
finished work: under the two-gate model there is nobody at the far end of that
queue, and a green pull request left in draft is a change that never reached
`main`. Either it is unfinished — in which case the page it needs is not this
one — or it should be merged by its author. **This session did not touch it.**

**The README's routing table.** Choosing a row still needs vocabulary a
newcomer does not have. Trimming it is a judgement about what matters most,
which belongs to whoever owns the reader's first ten minutes.

**Dependabot pull requests are open in `dossier` and `qmcp`.** They are
automation and hold no contributor slot. Nothing here depends on them.

## What could not be verified

*Inference, not fact.* The local workflow runner cannot reproduce `uses:` steps
or the runner image, and it does not run tag-triggered workflows at all — so
`tag-determinism.yml` has been exercised only by running its inner commands by
hand in all three repositories. It has never run as a workflow, because that
needs a pushed `v*` tag and none exists.

*Inference, not fact.* The fresh-setup path was verified by cloning `dossier`
into a temporary directory with submodules, running `uv sync`, and running the
first command. That is one machine and one operating system. Two of the three
failures this session repaired were reported from machines that are not this
one, and nothing here proves the third kind will not arrive from a fourth.

## How to pick it up

Run `uv run dossier gates run` in dossier before anything else. It reports
installation health, the suite, the workflow runner and branch provenance, and
it names what each gate cannot see. A gate that cannot run locally says so
rather than passing quietly.

`walkthrough/01-first-run.md` is the shortest route into dossier and it
executes, so it cannot have drifted from the code while you were away.
