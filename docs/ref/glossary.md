# Glossary

!!! info "Non-authoritative"
    This is a quick reference. For definitive explanations, see the cited sources.

**Adoption by reference**
: When a project's `adr/` directory lives on a `project/<name>` branch of the QM corpus, rather than copied into the project's own repo. The project vendor this repo as a submodule and checks out its own branch. Updates flow through propagation merges, not rebases.
  
**Adoption audit**
: A check that a project following the corpus has copied all required files correctly. See [handbook/adoption-audit-queue.md](https://github.com/quaternionmedia/qm/blob/main/handbook/adoption-audit-queue.md).

**ADR**
: Architectural Decision Record. Project-level records, numbered `ADR-NNNN` per project starting at 0001. See [Record precedence](precedence.md).

**Branch namespaces**
: The five conventions for branch names: `project/<name>`, `propagate/<name>-<date>`, `perspective/<date>-<slug>`, `evolve/<slug>`, `workspace/<slug>`. See [Branch namespaces](namespaces.md).

**Corpus**
: The QM constitution — the shared decision corpus, tooling, and procedures that every QM project adopts. Refers to this repository and the governance model it embodies.

**Harness**
: The CI, approval gate, and record-numbering machinery that enforces the corpus's discipline at ratification time. See [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md).

**Handbook**
: Policy and procedure routed outside record form. Binding on QM's own conduct. See [Handbook index](handbook.md).

**Phase ladder**
: A project's progression through governance maturity levels. See [records/DRAFT-project-phase-ladder.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-project-phase-ladder.md).

**Perspective**
: Attributed, dated, non-binding opinion. Distinct from records (doctrine) and workspace branches (experiments). Lives in `perspectives/`. See [perspectives/README.md](https://github.com/quaternionmedia/qm/blob/main/perspectives/README.md).

**Propagation**
: The act of merging `main` into a `project/<name>` branch via a `propagate/<name>-<date>` pull request, carrying org-level records to an adopting project. See [handbook/propagation-runbook.md](https://github.com/quaternionmedia/qm/blob/main/handbook/propagation-runbook.md).

**QM**
: Quaternion Media, the organization and the corpus that governs it.

**QM-NNNN**
: An org-level record, numbered at ratification. `QM` = org namespace; `NNNN` = the assigned number from the index. See [Record precedence](precedence.md).

**Record**
: A decision document at either org level (QM-NNNN) or project level (ADR-NNNN). Ratified records are binding; proposed records are not yet. See [Ratification](ratification.md).

**Register**
: A living record of something checked in and maintained, like carried patches. Binding by virtue of the record that creates it. See [Record precedence](precedence.md).

**Seed**
: `project-seed/` — the template files that a new project copies: `adr/`, `ci/`, and `ide/` directories. See [Repository layout](repo-layout.md).

**Seam**
: A published interface between this corpus and external systems or projects. Described in the records. Example: the monitoring seam.

**Workspace**
: A permanent, terminal branch (e.g., `workspace/math-experiments`) used for research or experiments that never merge back to `main`. Non-binding. See [Branch namespaces](namespaces.md).

## See also

- [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md) — the charter defining these concepts
- [Branch namespaces](namespaces.md) — the namespace model
- [Record precedence](precedence.md) — how records relate to each other
