# QM-XXXX — The Project Phase Ladder

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-09 |
| **Pends on** | Each project naming what its own `v0.0.2` and beyond assert, in its own records. The ladder below binds without them; the rungs above the first stay undefined per project until they do. |
| **Principle** | `decisions-are-documented` — decisions are documented or they didn't happen; `systems-over-heroics` — systems over heroics |

## Context

Projects acquire phases the way they acquire version numbers: someone says one
in a session, and it becomes the answer until somebody else says a different
one, written into no document that binds anything, while other projects have no
phase at all.

*Version tags are claims* settles what a `vMAJOR.MINOR.PATCH` tag asserts at
the moment it is cut. It leaves open the question this record answers: what a
project is working *toward*, and whether that target means the same thing in
two repositories.

Half of it does and half of it does not, and conflating the two halves is the
error worth preventing. **Governance is uniform.** Every project adopts the
same constitution by reference, so "this project has adopted governance" is one
claim with one meaning org-wide, and a shared ladder can hold it. **Everything
after governance is not.** A metronome's first integration standard and a
parametric-assembly tool's are different work, judged by different evidence,
and a shared definition of them would either be so loose it asserts nothing or
so specific it fits one project and distorts the rest.

There is a second failure this record has to keep out. `status/governance.yaml`
declines to compute a term named `adopted`, for a stated reason: no record
gives a file set, a ref, or a predicate, and the corpus warns against filename
checks standing in for adoption. That caution is right and survives here. A
project is not governed because it holds six files; it is governed because a
human established that it is. What the file set gives is a **measure** —
cheap, mechanical, and capable of reporting *not yet* — and a measure is worth
having precisely because it never decides a rung.

## Decision

1. **`v0.0.0` is not adopted, and `v0.0.1` is adopted, however far along.**
   Both mean the same thing in every project. A project is at `v0.0.0` until a
   human gives it a `project/<name>` branch in the corpus, and at `v0.0.1` from
   then on: it has adopted the QM constitution, and its records live on that
   branch. How much of the seed it carries yet — a current governance pin, the
   seed files on its default branch — is a share within `v0.0.1`, not a rung of
   its own, so a project a tenth of the way through adoption and one all the way
   through stand on the same rung. It is the same claim everywhere, which is
   what makes it comparable across a table, and a view can show the version
   alone and be read.

2. **Every rung above `v0.0.1` is defined by the project, in the project's own
   records.** A project that has not written that definition has not got a
   `v0.0.2`; it has a word. Naming a higher phase in a session, a handoff, or a
   roster is a statement of intent and is recorded as such, never as an
   attainment.

3. **A project with no phase stated is at `v0.0.0` until it has its branch,
   and at `v0.0.1` after.** This is a default, not a discovery: it reads the one
   fact a human has already established, whether the project has adopted, and
   claims nothing beyond it. It is the honest floor, because governance binds
   every project whether or not anyone has thought about that project's
   roadmap, and it is a claim any project can be measured against on day one. A
   phase stated for a project at `v0.0.0` is intent, shown beside the rung and
   never in place of it.

4. **The claim and the evidence are separate documents, and neither may be
   derived from the other.** The roster (`ci/workspace.yaml`) holds what a human
   has stated, marked `stated` or `scaffolded` so the difference survives
   reading. The evidence is computed from `status/governance.yaml`, which is
   generated from git and the host rather than from anybody's account of them.
   A view shows both and shows the gap; nothing rewrites a claim to match its
   evidence, and nothing infers a claim from artifacts.

5. **Evidence is read from what has landed.** The artifact set is checked on a
   project's default branch. Governance work sitting in an open pull request is
   work, and it is not evidence — the whole reason this corpus opens draft pull
   requests is that the gap between the two is where a human stands. A project
   reporting an incomplete set with an open propagation pull request is a
   project mid-adoption, and the view says so rather than crediting the intent.

6. **The mechanical check measures; it never decides a rung.** The seed
   artifacts — the governance submodule on the project's own branch, the IDE
   discovery files, the seed workflows, the licensing files — say how far a
   `v0.0.1` project's adoption has got. A complete set means *a human may now
   say adoption is complete*; it never means the assertion has been made. The
   human act that completes it is the same one the version-tags record already
   names, applied to governance itself.

7. **`unknown` remains available and remains meaningful.** A project whose
   evidence could not be read is `unknown`, never complete and never
   incomplete. A repository nobody could measure must not render like a
   repository measured and found wanting, and must never render like one found
   compliant.

## Alternatives

**One org-wide ladder for every rung.** Rejected. It requires the org to define
what a first integration standard is for projects whose deliverables have
nothing in common — an application, a schema, a parametric part library, a
radial menu component. The definition would either assert nothing or fit one
project. The ladder's value is comparability at the rung where the projects
genuinely are the same, and that rung is governance.

**No ladder; each project versions independently.** Rejected because it is the
state that produced this record. Without a shared floor there is no question a
table can ask of every project at once, and "where does this project stand" gets
answered per project by whoever last looked.

**Compute the phase from the artifacts.** Rejected, and it is the tempting one.
It would make the table self-maintaining and it would quietly redefine adoption
as a filename check — the exact substitution `status/governance.yaml` refuses to
make, for the exact reason it gives. Computing a floor is disqualification;
computing attainment is a machine making a human's claim on their behalf.

**Fold the phase into the version tag.** Rejected: a tag is cut at a commit and
asserts something about that commit. A phase is a target a project is working
toward and is true between tags. Merging them would leave a project with no way
to say where it is going until it arrives.

## Consequences

- Every project has a phase from the moment it exists — `v0.0.0` until a human
  gives it a branch — and the repositories whose roster row carries
  `phase_source: scaffolded` carry the default without anybody deciding
  anything about them.
- A page can show a project's version and nothing else about its governance:
  `v0.0.0`, `v0.0.1` and the project's own rungs above say it.
- The org-level table gains a column it can ask of every project — governance
  evidence — and loses the ability to compare anything above it, which it never
  honestly had.
- Projects that named a higher phase carry a visible gap until they write its
  definition. Apothecary, codecartographer and benchmark have `v0.0.2` stated
  and no record defining it; qmetronome has `v0.0.3` on the same terms.
  Benchmark has no branch yet, so it stands at `v0.0.0` with `v0.0.2` stated
  beside it.
- `status/governance.yaml`'s `undefined` entry for `adopted` narrows rather than
  closes. This record supplies the seed set as a measure and declines to supply
  a boolean for completeness, so the generator continues to list artifacts and
  derive no verdict.

## Revision triggers

- A project's own records define a rung and the definition turns out to need
  something the ladder forbids, such as a claim about another project.
- A second project needs the same `v0.0.2` definition as an existing one,
  which is evidence the rung is org-level after all and belongs here.
- The seed set reads complete for a project a human then finds ungoverned,
  which means the artifact set is the wrong set.
- Anyone proposes deriving a phase from artifacts, which is the signal that the
  claim and the evidence have started to be read as one document.

## Amendments

*None.*
