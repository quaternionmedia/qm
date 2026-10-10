# Status documents

Several tools write a committed document under `status/` rather than printing
a verdict: a document can be diffed, re-derived and read by other tools without
any of them re-implementing the rule behind it. `handbook/generated-documents.md`
indexes the documents and their refresh commands.

## The governance status document

`ci/governance_status.py` writes `status/governance.yaml`: the state of
governance across the org's project branches. It is an org-level tool and is
not copied into projects: it enumerates the `project/*` branches of this
repository and queries the org's own API, so it is meaningful in this clone
only. It is read-only apart from the document it writes.

```sh
python ci/governance_status.py                         # emit to stdout
python ci/governance_status.py --write status/governance.yaml
python ci/governance_status.py --check status/governance.yaml
python ci/governance_status.py --offline               # git layer only
```

### Two layers

| Layer | What it holds | Checked |
|---|---|---|
| git | A pure function of the commits the document names. The same [corpus](../../ref/glossary.md#corpus){ .glossary-term } commit and branch commits always give the same answer | Yes: `--check` re-derives it against those commits |
| github | Observations of a remote at a moment: pull requests, licences, files in each project repository | No: it is stamped, because checking it would mean asserting the world has not moved |

`--check` therefore works offline and in a fork's pull request with no token.
It reports the ratio of fields it could verify, and a run that verifies nothing
exits non-zero, because "0 of 0 fields match" is not a pass. The set of fields
compared is whatever the git layer emits, so moving a field between layers
changes what is checked by construction. Projects are keyed by name, not by
position, so a branch added between two generations does not shift every
later project.

### Unknown is a value

Every field is a real answer or an explicit `{unknown: <reason>}`, and the
count of unknowns is in the header. "Could not reach the API" never renders as
"nothing wrong", and `None` keeps its own meaning (for example, "never
propagated"). One unreadable ref makes one project unknown, never the whole
document absent. A generation that finds no project refs at all (a shallow
clone, or a remote namespace never fetched) is refused rather than written as
an empty table.

### What the fields mean

- **A [propagation](../../ref/glossary.md#propagation){ .glossary-term }** is a merge on the project branch, in `corpus..branch`, with
  at least one parent contained in the corpus. A project's own feature merges
  are not propagations. A squash-merged propagation leaves no merge commit and
  is reported as none, because squashing breaks the submodule-pin model the
  merge commit carries.
- **[Record](../../ref/glossary.md#record){ .glossary-term } counts** are read from the ref, never from the working tree, and the
  corpus's own `records/` is counted apart from each project branch's `adr/`.
- **[Seed](../../ref/glossary.md#seed){ .glossary-term } drift** is compared two ways: against the corpus tip, and against the
  branch's own merge-base with the corpus. Only the second says whether a
  project edited something it was meant to copy verbatim; the corpus has not
  settled which it intends, so both are reported. The `undefined` block of the
  document lists terms like this one that the corpus uses without defining.
- **Seed workflows** are the ones `handbook/forking-a-project.md` step 4 asks a
  fork to copy, probed by filename only: a project that runs a check inline in
  another workflow shows the filename as absent.
- **`records_dir`** is where a project's [ADR](../../ref/glossary.md#adr){ .glossary-term } lint says its records live: `null`
  for the branch-per-project model, a path for records kept in the project's
  own `adr/`, and unknown when the workflow could not be read. It is what lets
  a zero in the record census be read.
- **The corpus submodule** is found by its URL and its own `.gitmodules`
  section, not by mount path or a whole-file match.

### Private repositories

Private repository names are withheld by default and appear as stable
`private-NN` references, assigned in creation order so a new repository never
renumbers the others. Offline, `--check` resolves those references through the
gitignored companions of the roster and the inventory, which are not committed; where
they are absent, the project is reported as unverifiable rather than as a
difference. The document also records which credential the run used, because
an Actions token scoped to one repository sees every private project
repository as missing everything.

### What it cannot establish

Whether a project should be adopted, whether a record is right, whether an
unpropagated branch is neglected or deliberately pinned, and whether a
repository with no project branch is out of scope or merely unnoticed. It
reports positions, and a position is not a judgement.

## The document state document

`ci/doc_status.py` writes `status/documents.yaml`: the state of every governed
page, in one closed vocabulary. The corpus has four state vocabularies that do
not overlap (a record's Status and filename, a [perspective](../../ref/glossary.md#perspective){ .glossary-term }'s index row, a
generated page's age, and none at all for a [handbook](../../ref/glossary.md#handbook){ .glossary-term } page), and the document
gives every page one state with what it means about whether the page binds its
reader.

- **Two signals per record.** The declared Status row, and what the filename
  asserts. A `DRAFT-` file whose Status reads `Accepted` is a [ratification](../../ref/glossary.md#ratification){ .glossary-term }
  started and not finished, and the disagreement is reported.
- **A perspective's state comes from the index** in `perspectives/README.md`,
  which is the mechanism by its own statement. An index row naming a missing
  file and a file with no row are both reported.
- **The scan is the scope.** Every governed directory is scanned, including
  `docs/`, so `totals.unknown` describes every governed page; an index file is
  classed as an index, not as a member of what it indexes.
- **The mandatory reading** a session is told to read before its first edit is
  measured against a budget set by
  `records/DRAFT-governance-arrives-as-a-mechanism.md`. Documents read in part
  are excluded by name, with the reason.

`classify` and the "Every home" table of `handbook/style-guide.md` are one
taxonomy written in two places, and they are repaired together.

It cannot tell whether a state is correct, and it gives a handbook page the
state `standing` rather than inventing one the corpus has not defined.

## The loose-ends document

`ci/loose_ends.py` joins what several generated documents say is unfinished
into one list: stalled threads and stacked pull requests from
`status/harness.yaml`, records awaiting ratification and perspectives nobody
has reviewed from `status/documents.yaml`, and each [gate](../../ref/glossary.md#gate){ .glossary-term }'s declared blind spot
from `status/gates.yaml`. It is a join, not a measurement: it collects nothing
fresh and reaches no network, and its evidence is only as fresh as its stalest
input.

- **Claim and evidence are separate.** Evidence is generated and rewritten on
  every run. A claim (what a person decided about an item) is read from
  `registers/loose-end-claims.yaml`, an input the generator never writes, so a
  person's judgement is never erased. An item nobody has judged has no claim
  block, and `open` is the absence of a claim rather than a claim.
- **An address names the thing, not the finding.** Each item addresses its
  subject with an existing kind from `ci/addresses.py` and carries its own
  `kind` beside it, so a view can navigate from a loose end to what it
  concerns. An address that does not parse is reported, not dropped.
- **Unknown is a value.** An unreadable source is recorded as
  `{"unknown": "<reason>"}` and its items are absent, never an empty list.
- **One contract.** The generator and the vector runner share the function
  that decides how an item reads, so a passing vector is a statement about the
  document a consumer receives.

It cannot decide whether a loose end matters; the claims [register](../../ref/glossary.md#register){ .glossary-term } is where a
person writes that down.
