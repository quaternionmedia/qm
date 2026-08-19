# Handoff — the active four

**Stamped 2026-08-19. `qm` `f899dff`, `dossier` `1047f4b`, `qmcp` `6e6c2db`,
`rad` `96836ad`.** Every figure here was true at those commits and nowhere else.
Re-derive before quoting one.

**Everything is merged and pushed. No branch is held back**, no working tree is
dirty, and every repository below has an empty pull-request slot.

---

## Which repositories are active

`ci/workspace.yaml` now says so directly: `qm`, `dossier`, `qmcp` and `rad` sit
under *Active: the working set on 2026-08-19*. That grouping is a claim about
attention, not about governance — everything else in the roster is governed
exactly as much, and a repository leaves the section by nobody working on it.

| repository | what it is | state |
|---|---|---|
| `qm` | the corpus | every gate green |
| `dossier` | the control panel | suite green, no skips, tag-able |
| `qmcp` | the harness | **cannot be tagged**: eleven skips |
| `rad` | the interaction contract | lint passes for the first time |

## Read this before trusting a check

**`rad`'s ADR lint had failed on every run since the repository was created**,
because the script it invokes lives in a submodule that was never mounted. It
passes now. The lesson is in `perspectives/2026-08-19-a-gate-that-never-passed.md`
and it is worth the two minutes: a red check nobody looks at is worse than a
green one that lies, because it trains its own author to ignore it.

**So: read a run, not a workflow file.** `gh run list --workflow <name>` answers
in seconds a question no amount of reading the repository can.

## What is unfinished

**The numpad proposal is Proposed, not ratified.**
`rad/adr/DRAFT-the-menu-addresses-nine-cells.md`. *Done* is a human flipping
Status, assigning a number and updating the index. An agent drafts and never
ratifies, and no record in this corpus is ratified yet — that waits on a second
active code owner, which is a stated position rather than an oversight.

**`rad`'s conformance vectors do not cover the cells.** The proposal names what
they would need: placement order, the centre holding nothing, reachability by
direction alone, and the chord window on both sides. Nothing is wired.

**The pair reconciles, it does not connect.** `qmcp dashboard --json` reaches
`dossier harness ingest` as a file a person copies. *Done* looks like one side
obtaining the other's state without a filename on a command line, with every
figure still carrying how old it is. `dossier/walkthrough/04-the-pair.md` states
the gap rather than implying otherwise.

**`qmcp` cannot cut a tag.** Its suite skips tests needing metaflow and
pydantic-ai, and a skipped test contributes nothing to the automated-validation
claim. `uv run qmcp` reports it now rather than leaving it to a release.
`dossier` reached the tag-able state by reading a vendored copy instead of a
sibling checkout; that method does not transfer, because qmcp's skips are
missing optional dependencies rather than missing paths.

**`rad` keeps its records in its own tree** via `RECORDS_DIR: adr`, while the
seeded `adr/` on `project/rad` holds the template only. Whether those records
should move onto that branch is a decision nobody has taken, and this session
deliberately did not take it.

## What is blocked on a human

- **Ratifying anything.** Every record everywhere is `Proposed`.
- **The corpus README's routing table** still needs vocabulary a newcomer does
  not have. Trimming it is a judgement about what matters most.
- **`dossier`'s README structure** — badges, four screenshots and a quickstart
  before any prose. A structure question, not a sentence question.

## What could not be verified

*Inference, not fact.* The tag-determinism workflow has never run as a workflow
in any repository. It needs a pushed `v*` tag and none exists, so it has only
ever been exercised by running its inner commands by hand.

*Inference, not fact.* `dossier`'s fresh-setup path was proven by cloning into a
temporary directory on one machine running one operating system. Two of the
three failures it repaired were reported from machines that are not this one.

## How to pick it up

In `dossier`: `uv run dossier gates run` reports installation health, the suite,
the workflow runner and branch provenance, and names what each gate cannot see.

In `rad`: `python governance/qm/project-seed/ci/run_workflows_locally.py`. One
step fails locally — `pages.yml :: Install ffmpeg`, an `apt-get` a local run
cannot reproduce. That is an environment difference and not a defect.

In `qm`: `uv run qm gates`, `uv run qm protocols`, and `uv run qm prose` for the
openings of every entry point.

Each project's `walkthrough/01-*.md` executes, so it cannot have drifted from
the code while you were away.
