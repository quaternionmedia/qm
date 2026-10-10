# Rosters and registries

The roster, the inventory and the registries are the files where a person
states a claim and a tool reads it. A tool reads a claim; it never infers one.

## The roster

`ci/workspace.yaml` lists the repositories the [corpus](../../ref/glossary.md#corpus){ .glossary-term } works with, and
`ci/roster.py` loads it for every other tool. A private repository is rostered
as `ref: private-NN` with no `name`, so a public file never carries its name;
the loader guarantees `name`, filling in the real name from the uncommitted
companion where it exists and the reference itself where it does not. A
committed artifact writes the `ref`, the redacted form, never the name.

## The inventory

`uv run qm inventory` lists every repository the org has against what the
corpus knows, because a roster that omits a repository makes it invisible to
planning in a way that looks like a decision. It writes three files, split by
what may leave the machine:

| File | Holds | Committed |
|---|---|---|
| `status/inventory.yaml` | Public repositories by name, counts, and references standing in for the rest | Yes |
| inventory-private.json | Reference to private repository name | Never |
| inventory-local.json | What is cloned on this disk, and where | Never |

The split is the control, not a redaction: a public file that never receives
private names cannot leak them however broken the code is. Private repositories
are counted and referenced, never dropped. References are assigned in creation
order, which is append-only, so `private-03` means the same repository in every
document that cites it; `uv run qm inventory --resolve private-03` reads the
mapping back on a machine that has it.

**Recency** comes from the default branch's last commit date, not `updatedAt`
(which moves on a description edit and lags a push) or `pushedAt` (which moves
on a push to any ref, so a dormant repository reads as active). An archived
repository is `archived` whatever its dates. **Risk** comes from a clone:
commits on no remote (`--all --not --remotes`, asserted only after the clone's
remote-tracking refs exist), broken down by the ref that holds them, with tags
walked so the breakdown agrees with its own total. An unreadable repository is
not a clean one. **What a human said** about a repository is `unstated` until
somebody says it, never `dormant` by default.

Where the roster's claim and the measurement disagree, both are reported and
neither is corrected (`records/DRAFT-a-disagreement-is-a-delta.md`). It cannot
see a repository the credential cannot read, a clone outside its search roots,
or another machine; those are unknown, never absent.

## Families

`uv run qm families` reports which repositories the org has claimed are one
working system. The set of families is read from §3 of
`records/DRAFT-a-family-is-bordered-by-what-it-drives.md`, bounded to that
section's table, so a family renamed there is a claim that stops resolving and
a table elsewhere in the [record](../../ref/glossary.md#record){ .glossary-term } declares nothing. A family is stated by a person
in `ci/workspace.yaml`; a repository with no family is `unstated`, reported and
never refused. `--check` refuses a claim naming a family the record does not
declare.

`families.json` is the [seam](../../ref/glossary.md#seam){ .glossary-term }: `dossier` and `codecartographer` read the families
as JSON at a stable path rather than importing this corpus
(`records/DRAFT-seams-on-standard-protocols.md`). `unstated` is a member of its
shape, so a consumer never has to infer `none`. `--check` also refuses a stale
`families.json`, which is how the registries workflow keeps it current.

It cannot tell whether a repository really belongs to its family (the border
test in §2 of the record needs a person who knows what the code drives), and
it cannot see a family member missing from the roster.

## Capabilities

`ci/capability-registry.yaml` records what each named capability of the estate
has reached, and what nobody has established about it.
`records/DRAFT-a-capability-has-four-phases.md` is the decision and names the
rungs. `phase` is a claim a person makes and nothing derives it, so the gap
between claim and evidence stays visible. Each evidence field names where to
look (a path, a command, an address pattern, a document), and `null` means
nobody has established it, which is unknown rather than failed. Deployment has
its own rung because it fails without a symptom: a command a package documents
can be missing while its modules import and its tests pass.
`uv run qm capabilities --check` refuses a declaration nobody could act on.

## Divergence

`uv run qm divergence` compares two views of the same addresses on a declared
list of fields and turns each disagreement into a delta
(`records/DRAFT-a-disagreement-is-a-delta.md`). Both values are kept, with
which view said which; a delta's name derives from the address and the field
alone, so re-running detection never opens a second row; a new delta opens at
`brainstorm`; convergence is reported and closes nothing; and a field one view
does not hold is reported as missing rather than as a difference. It has no
opinion about which value is right.
