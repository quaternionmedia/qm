# ADR-XXXX — Constitution Adoption and Scope

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-07 |
| **Pends on** | Org amendments to the house-stack record covering Python packaging and frontend applications. Adoption itself is not contingent on them; only §5's disposition is. |
| **Principle** | P6 — decisions are documented or they didn't happen |
| **Written against** | alfred `main` at `7fff7ae`. The first review pass for this record was performed against `pdm`, which was 21 commits behind with nothing unique on it; every finding was re-established against `main` before being written down. |

## Context

Alfred is a video editor built as a FastAPI control plane orchestrating
`otto`, a render engine QM publishes as a separate public package. It runs
as container images: an API service, a Celery render worker, a MongoDB
instance, and a parcel-built mithril frontend. It has been in service since
2022.

Every prior adoption of this corpus was greenfield or near-greenfield. Alfred
is not. It is a running system with dependencies chosen years before the
constitution existed, and adopting the corpus means taking on a set of
conflicts that already exist rather than agreeing to avoid future ones. The
corpus's fork procedure describes instantiation; it does not describe what a
project does when instantiation surfaces conflicts on day one.

The corpus's server/infra defaults fit this project well. Alfred is a
container runtime with images, a deployment, and a control plane, so the
translation cost the mobile-project retrospective describes
(`perspectives/claude-sonnet-5-2026-07-04-qmetronome-onramp-retrospective.md`,
§2.1) is not repeated here. What this project surfaces instead is a different
gap: the corpus assumes a project can be compliant at adoption, and offers no
recorded state for one that cannot.

Naming the conflicts is therefore the substance of this record, not a
preamble to it.

## Decision

1. **Alfred adopts the QM constitution by reference**, vendored as a
   submodule at `governance/qm` pinned to this project's `project/alfred`
   branch. Org records bind this project. This project's records may tighten
   them, never relax them.

2. **Adoption is declared with known non-compliance, enumerated rather than
   waived.** The table in §3 is the complete set of conflicts known at
   adoption. An item's presence records that it is known and unresolved; it
   does not authorize it, and it is not a waiver. The exclusion rule admits
   no waivers, and this record does not create one.

3. **Known non-compliance at adoption:**

   | # | Conflict | Org record | What compliance would look like |
   |---|---|---|---|
   | 1 | MongoDB is the datastore, the Celery broker, and the result backend. MongoDB is SSPL — a source-available regime the exclusion rule names explicitly. | Open-license §1 | A datastore and a broker under OSI or FSF-free licenses. Decided in the datastore and task-queue record, not here. |
   | 2 | The database image is `mongo:bionic`. Ubuntu 18.04 is out of support, and the tag is not digest-pinned. | Open-license §1; P8 | A supported, digest-pinned base for every image the stack runs. |
   | 3 | Object storage is Google Cloud Storage, reached through the vendor's own SDK. | Seams §2, §3 | A seam on a protocol with multiple independent implementations. Decided in the object-storage seam record, not here. |
   | 4 | The frontend loads a font from `fonts.gstatic.com`, demo images from a Squarespace CDN, and sample media from `storage.googleapis.com`. | Open-license §1, which requires frontend assets be vendored and never CDN-loaded | Every asset served from the application's own origin, vendored into the repository. |
   | 5 | The application image builds `FROM python` with no tag and no digest, and **no longer builds at all**. The unpinned base now resolves to Python 3.14, which does not ship setuptools, so a dependency fails at `pip install` with `No module named 'pkg_resources'`. Pinning to 3.11 gets past that and then fails on `rm /etc/ImageMagick-6/policy.xml` — the base carries ImageMagick 7 and the version-6 path is gone. Both reproduced against Docker. | P1; P8 | A pinned base image, rebuilt deliberately rather than implicitly, and no hardcoded path into a dependency's private layout. |
   | 6 | `fastapi-crudrouter` is installed at build time from a QM fork branch. The org register lists no carried patches. | Contribution §2, under which an unregistered build-time patch is a lint failure | The patch registered in `registers/carried-patches.md` with its upstream status. |
   | 7 | The frontend has no committed lockfile; `package-lock.json` and `yarn.lock` are both git-ignored, and **the frontend no longer builds either**. `parcel` floats from `^2.8.3` to 2.16.4 while `@parcel/transformer-sass` is pinned to exactly `2.8.3`; parcel requires them to match, so the build fails and no `dist/` is produced. Reproduced from a clean install. | P8 — recreatable from version control | A committed lockfile, so a build is reproducible from the repository alone. |
   | 8 | Packaging is PDM and the frontend is a mithril/parcel application. The house-stack record blesses `uv`, and contemplates frontend JS only as single-file visualization deliverables. | House stack §2 | Resolved at org level, not here. See §5. |

   **How each row is pinned.** Kept out of the table above, which is already
   wide enough to be hard to read. A row with no pin will drift silently as
   the code changes, so the absence is stated rather than left to be noticed.

   | # | Pinned by |
   |---|---|
   | 1 | Nothing mechanical. A licensing fact about a component, not a behavior a test can observe. Reachable only by a gate that inventories images, which §4 records as absent. |
   | 2 | As row 1. |
   | 3 | No test yet. Pinnable: an import check asserting object storage is reached through an S3 client rather than a vendor SDK would fail today and pass once the seam record is implemented. |
   | 4 | No test yet. Pinnable: a scan of the built bundle for external origins. |
   | 5 | `docker build .`. A fix is drafted on alfred's `test/core-tests` branch — base pinned by digest, `rm -f` across both ImageMagick paths — and this row clears when that merges, not before. |
   | 6 | The org carried-patch register, which now holds the entry. |
   | 7 | `yarn parcel build`. No fix is drafted; the lockfile decision is open. |
   | 8 | Nothing mechanical, and nothing needed: this resolves by org amendment rather than by project work. |

   Rows 5 and 7 were reproduced rather than inferred, and both had already
   caused failures before anyone described them as risks. Their reproductions
   are stated in the rows themselves.

4. **The license report is wired as a report, not a gate, and its blind spots
   are recorded rather than left to be rediscovered.** Both dependency scans
   pass: all 84 Python packages carry permissive OSI licenses, and of 12
   production frontend packages, 11 are MIT, ISC, or Apache-2.0. Conflicts 1
   through 5 above appear in neither scan, because a database image, a hosted
   service, and a CDN-loaded font are not entries in any dependency manifest.
   A gate wired only to these scans would certify this stack as compliant. It
   is not. What the gate must additionally cover is stated in the workflow
   itself.

5. **Two conflicts route to the org rather than to this project.** Alfred and
   `otto` both moved to PDM deliberately, which is two projects requesting the
   same out-of-set dependency — the house-stack record's own revision trigger.
   Alfred also runs a frontend application, a shape that record does not
   contemplate. Under precedence, a project record may not relax an org
   record, so neither is a project-level exception to write. Both are proposed
   as org amendments; §3's row 8 resolves when those are ratified.

6. **The twelfth frontend package, `alertifyjs`, is GPL-3.0, and is
   compliant.** The exclusion rule accepts copyleft explicitly and requires it
   be handled contractually rather than avoided technically. It is recorded
   here because this project declares itself MIT while distributing a bundle
   containing GPL-3.0 code, and because the org record governs whether each
   component is open without asking whether the combination is distributable
   as declared. That question is raised to the org; this record does not
   answer it.

## Consequences

- This project is instantiated rather than improvised: it carries `adr/`,
  the ADR lint, and IDE-integrated governance discovery, each from the seed.
- The conflicts in §3 are visible in one table, which is the point. An
  adopting project that enumerates its gaps is auditable; one that adopts
  silently and fixes quietly is not.
- Cost accepted: adopting with eight open conflicts means this project cannot
  claim compliance, and should not. It can claim that its non-compliance is
  known, bounded, and recorded — which is the honest available claim and a
  strictly better position than not adopting.
- No conflict in §3 carries a date. Enumerating and sequencing are different
  decisions with different owners; this record does the first and deliberately
  declines the second.
- Contributors get a single place to check before adding a dependency, a
  datastore, or a third-party service, so the gap set stops growing while it
  is being worked.
- Rows 5 and 7 are no longer forward-looking risks. Both have already
  happened: neither the application image nor the frontend bundle builds from
  a clean checkout today, and in all three failures the mechanism was the
  same — a dependency the repository declined to pin moved underneath it.
  That is the cost of unpinned dependencies stated as an observed outcome
  rather than a principle, and it is the strongest available argument for
  closing those two rows ahead of the others, independent of any schedule
  this record declines to set.

## Alternatives considered

1. **Remediate first, adopt after.** Rejected: it inverts the dependency. The
   constitution is what makes the conflicts legible as conflicts; withholding
   adoption until they are fixed means fixing them without the framework that
   names them, and leaves the project ungoverned for exactly as long as it is
   most in need of governance.
2. **Adopt with the conflicts unstated, and fix them quietly.** Rejected:
   this is the failure mode P6 exists to prevent. It would also make the
   corpus's own instantiation claim false — a project that reports compliance
   it does not have is worse for the org than one that reports the gap.
3. **Adopt with a dated remediation schedule per conflict.** Rejected: the
   dates would be invented. Nobody has scoped the datastore migration, and a
   schedule with no estimate behind it decays into either a missed date that
   teaches contributors deadlines are decorative, or pressure to close a
   conflict badly. The template already requires revision triggers to be
   observable events rather than dates, and that preference applies here.
4. **Read the exclusion rule as governing only software QM distributes, so
   that a hosted service and a database image fall outside it.** Rejected: it
   is a strained reading that would let this project declare compliance while
   its actual sovereignty exposure is untouched. The record's own Context
   calls a rule blind to deployment-path dependencies compliance theater.

## Revision triggers

- Any conflict in §3 is resolved, or a new one is discovered — the table is
  the project's compliance surface and is amended when it changes.
- The org ratifies the house-stack amendments this record pends on — row 8
  resolves or becomes a project-level decision.
- The org adds a clause on hosted-service dependencies or on license
  compatibility — §4 and §6 stop being open questions raised from here.
- A second brownfield project adopts the corpus — the pattern this record
  improvises should become seed-level, or be shown not to generalize.
- The license report is promoted to a gate — §4's blind-spot list becomes
  that gate's specification.

## Amendments

*None.*
