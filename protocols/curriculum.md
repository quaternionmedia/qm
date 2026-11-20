# Protocol — Curriculum

**Question.** In what order should someone with no context read this corpus,
and what can they do afterwards?

**Invoked by** a human, or an agent asked to. **Budget** 90 days. **Produces**
`curriculum/<id>.yaml`. **Optional** — nothing gates on it and no project has to
adopt one.

```sh
uv run qm curriculum                        # the org path, in order
uv run qm curriculum --check                # refuse a unit that teaches something false
uv run qm curriculum --merge <other.yaml>   # what integrating another one would cost
```

---

## Why the corpus needs one

Sixteen records are `Draft` or `Proposed` and none has been read as one body.
Outside testers onboard soon, and the honest test of any governance document is
a reader with no context — who currently arrives at a root directory holding a
charter, a constitution, six registries, a handbook, twelve project branches and
no stated order.

A curriculum is that order, written down and checkable. It is not a summary, and
a unit that restates its document is a second copy of a decision — the failure
`records/DRAFT-the-read-document-governs.md` names, where the copy is always the
half that goes stale.

## The shape of a unit

```yaml
- id: precedence
  teaches: docs/ref/precedence.md
  status_claimed: Proposed          # optional; only records carry a Status
  after_this_you_can: >
    Resolve a disagreement between an org record and a project one without
    asking anybody.
  prerequisites: [namespaces]
```

`after_this_you_can` is a capability, not a topic. *Understands precedence* is
unfalsifiable; *resolves a disagreement without asking anybody* can be watched.

`status_claimed` is where the checking has teeth. Name it and
`--check` reads the document's own Status row and refuses a mismatch — so a
curriculum cannot teach a `Draft` as settled, which would be the corpus
asserting something no human ratified.

## Merging two curriculums

A project fork teaches its own `adr/` and wants the org's path underneath. Two
curriculums therefore have to combine, and the reconcile has three properties in
tension, so each is stated rather than implied.

### Optimistic

An incoming unit is **accepted by default**. No approval per unit, no queue. A
reconciler that asked about every unit would not be used, and an unused
reconciler means two divergent paths and nobody reading either.

### Optional

`--merge` alone prints and writes nothing. Only `--write <path>` produces a
file. No gate requires a curriculum, the org curriculum binds no project, and
`ci/protocol-registry.yaml` records this protocol as `optional: true`. Not
having one is a legitimate state.

### Governance-aware

Optimism stops at three things, and **only** these three. Each produces a
curriculum that teaches something false:

| refusal | why it cannot be optimistic |
|---|---|
| the unit cites a document that is not there | it teaches a reader to open nothing |
| the unit claims a Status its document does not carry | teaching an unratified record as settled asserts what no human did |
| a project curriculum teaches an org document | precedence runs one way; citing is fine, owning inverts it |

**A conflict is not a refusal.** Two units sharing an id and disagreeing are
reported, the base is kept, and nothing is merged field by field. Somebody
decides — and the fields that differ are named so the decision is cheap.

Accepted units are **appended, not interleaved**. A reconciler that guessed
where an incoming unit belongs in a reading order would be deciding the one
thing a curriculum is for.

### Running it

```sh
uv run qm curriculum --merge ../datum/curriculum/project.yaml
# read the verdicts, then:
uv run qm curriculum --merge ../datum/curriculum/project.yaml --write curriculum/merged.yaml
uv run qm curriculum --file curriculum/merged.yaml --check
```

Re-check the merged file. The reconcile checks incoming units; it does not
re-check ordering across the combined result, and an appended unit can name a
prerequisite that now comes after it.

---

## What this protocol cannot see

- **Whether anyone learned anything.** There is no assessment and no telemetry.
- **Whether the order is a good order.** It checks that prerequisites exist and
  come first. Nothing measures whether the sequence teaches.
- **Whether a unit's prose is true of its document.** It reads existence and
  Status, not meaning. A unit can cite the right file and describe it wrongly.
- **What is missing.** A document that should be taught and is in no unit is
  invisible: an incomplete curriculum and a complete one are the same shape
  here. That is the largest gap and the argument for a human reading the whole
  path at least once per budget.
