# Glossary

!!! info "Quick reference only"
    These are short definitions. The linked sources are authoritative.

    For the words this corpus uses in **more than one sense** — *draft*, *review*,
    *gate*, *phase*, *delta*, *status*, *seed* — see
    [`handbook/glossary.md`](https://github.com/quaternionmedia/qm/blob/main/handbook/glossary.md).
    That page disambiguates; this one defines. Where the two differ, that one governs.

**Adoption by reference** { #adoption-by-reference }
: The QM adoption model. A project's records live on a `project/<name>` branch of the corpus repository, and the project mounts the corpus as a git submodule checked out on that branch. Updates arrive by merge, never by copy. See [Architecture](../about/architecture.md).

**ADR** { #adr }
: A project-level decision record, numbered `ADR-NNNN` per project starting at 0001. See [Record precedence](precedence.md).

**Black box** { #black-box }
: A component whose behaviour cannot be decided in advance — for QM's purposes, a language model. P17 says it is never the check: it drafts the check and a person authors it. See [PRINCIPLES.md P17](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md).

**Corpus** { #corpus }
: This repository and the shared rule set it holds: the constitution every QM project adopts.

**Crossing** { #crossing }
: Two deltas that interact at one point where neither contains the other, stated as `crosses`. Distinct from `part-of`, which composes, and `blocks`, which orders. See [records/DRAFT-deltas-compose.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-deltas-compose.md).

**Gate** { #gate }
: An automated check that can refuse a change. Gates are mechanical and always on; nobody invokes one. They are not the two *human* gates — ratification and the version tag — and no gate is a substitute for either. See [the gate index](https://github.com/quaternionmedia/qm/blob/main/handbook/gates.md).

**Handbook** { #handbook }
: QM's policy and procedure pages, in `handbook/`. Binding on QM's own conduct; a record always wins over a handbook page. See [Handbook index](handbook.md).

**Harness** { #harness }
: The tooling that coordinates work across concurrent agent sessions: the scripts in `project-seed/ci/` that establish what a session must know, the checks they run, and `harness-status.json`. The governance layer names no product — optional per-tool wrappers live in `adapters/`. See [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md).

**Knot** { #knot }
: A cycle in the obligation graph where every edge imposes an order, so the ring has no first step. Untying one means a person chooses, or a stated relation gets cut. Distinct from a loop. See [records/DRAFT-a-knot-is-a-cycle-of-obligation.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-a-knot-is-a-cycle-of-obligation.md).

**Loop** { #loop }
: A cycle whose edges impose no order. Identical to a knot in a picture, and it constrains nothing — reporting it as a problem buries the real ones. Measured here: 42 loops, 0 knots, in 169 real relations. Still a fact, and not a scheduling problem.

**Perspective** { #perspective }
: Dated, attributed, non-binding opinion in `perspectives/`: incidents, retrospectives, argued positions. See [Add a perspective](../cookbook/add-a-perspective.md).

**Phase ladder** { #phase-ladder }
: How a project reports its governance maturity, as a version number. Only `v0.0.1` (adoption of the constitution) is defined org-wide; higher rungs are defined by each project in its own records. See [records/DRAFT-project-phase-ladder.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-project-phase-ladder.md).

**Propagation** { #propagation }
: Merging `main` into a `project/<name>` branch to carry org changes to a project, through a `propagate/<name>-<date>` pull request. See [Propagate a change](../cookbook/propagate-a-change.md).

**Proposed** { #proposed }
: The status every record in this corpus currently carries. It means the decision is written down and is not yet final. Making one final is [ratification](#ratification), which needs a second person to agree. See [Ratification](ratification.md).

**Protocol** { #protocol }
: A wire format or interface with multiple independent implementations, which is what makes a component swappable. P3's replaceability test is stated against protocols rather than licences, because a proprietary protocol outlasts an open licence. See [records/DRAFT-seams-on-standard-protocols.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-seams-on-standard-protocols.md).

**QM record** { #qm-record }
: An org-level decision record, numbered `QM-NNNN` at ratification. Binds every project. See [Record precedence](precedence.md).

**Ratification** { #ratification }
: The human act that makes a record binding: Status flips to `Accepted`, the number is assigned, the index is updated. See [Ratification](ratification.md).

**Record** { #record }
: A decision document: one decision, with context, alternatives, consequences, and revision triggers. The only kind of document that binds. See [Draft a record](../cookbook/draft-a-record.md).

**Register** { #register }
: A living data file created by a record, such as [registers/carried-patches.md](https://github.com/quaternionmedia/qm/blob/main/registers/carried-patches.md). Binding as the creating record says.

**Seam** { #seam }
: The boundary where a third-party component connects to a QM system. Seams sit on standard protocols so any component behind them can be replaced. From the records [Seams on standard protocols](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-seams-on-standard-protocols.md) and [Build the seam, buy the engines](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-build-the-seam-buy-the-engines.md).

**Seed** { #seed }
: `project-seed/` — the files a new project copies at adoption: `adr/` (record template and index), `ci/` (workflows and checks), and `ide/` (agent instructions and editor config).

**Strand** { #strand }
: One line of work, possibly denoted by more than one address. `same-as` is what says two addresses are one strand; advancing one and not the other leaves the same work in two phases.

**Sweep** { #sweep }
: One change carried across every repository that needs it — one delta with many parts, rather than many pieces of work that resemble each other. The parts are `part-of` it, so the whole has a single state.

**Tangle** { #tangle }
: A cycle the relations form, reported and never broken. Refusing to store one makes the tool consistent and the record false, and the deletion gets made by whoever was least equipped to judge it.

**Workspace** { #workspace }
: A permanent branch (`workspace/<slug>`) for research that never merges back to `main`. Non-binding. See [Branch namespaces](namespaces.md).


## Related

- [Branch namespaces](namespaces.md)
- [Record precedence](precedence.md)
- [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md)
