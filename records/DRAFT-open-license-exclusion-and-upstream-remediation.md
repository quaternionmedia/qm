# QM-XXXX — Open-License Exclusion and Upstream-Contribution Remediation

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-09 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P1 — ownership is the deliverable; P2 — commons-first economics |

## Context

A component whose license permits the licensor to withdraw, re-price, or
re-platform it is a clause in someone else's contract embedded in our stack.
The industry supplies regular reminders — most recently MinIO, archived in
February 2026 after its community edition was progressively stripped in favor
of a ~$96k/yr commercial product. Notably its final releases were open
(AGPL): governance failed where license did not. Both risks need answers;
this record fixes the license criterion and the response to license change.
Governance risk is addressed structurally by the seams doctrine and each
project's risk register.

Nominally open components also carry proprietary dependencies in common
deployment paths (embedded proprietary browsers, closed GPU runtimes and
model compilers). A rule blind to deployment-path dependencies is compliance
theater.

The same blindness has a second form, which package-manifest scanning cannot
see at all. A hosted service has no license to check: it is not a component
in a manifest, so a rule phrased purely about the licenses of software
components passes it silently while the dependency is the least ownable one
in the stack. §6 closes that. A worked example: a project whose Python and
frontend dependency scans both come back fully compliant, while the deployed
stack runs a source-available database image, stores its output in a vendor's
hosted object store, and loads a font from a third-party CDN. None of those
three appear in any manifest. The scans are accurate and the conclusion drawn
from them would be false.

Two further facts about license metadata, from the same instance. Roughly six
distinct licenses across 84 Python packages were declared in more than twenty
spellings, and one npm dependency declared its license only in the deprecated
`licenses` array, where a reader of the modern `license` field sees null. A
gate that compares raw strings fails honest packages and passes unreadable
ones, so §4 requires normalization rather than leaving it to each project to
discover.

## Decision

1. **Exclusion rule.** Every software component in any QM deployed runtime
   path carries an OSI-approved or FSF-free license: applications, libraries
   (transitive, SBOM-surfaced), kernel modules and drivers, base images,
   model weights and their toolchains, and all frontend assets (vendored,
   never CDN-loaded). Copyleft is explicitly acceptable and contractually
   handled, never technically avoided. Source-available regimes (BSL/BUSL,
   SSPL, Elastic 2.0, Commons Clause, Fair Source, PolyForm), field-of-use or
   user-count restrictions, restricted "open-weights," and freeware are
   excluded. **No waivers, no opt-ins.**
2. **Relicense protocol.** On a non-compliant relicense of an adopted
   component: freeze at the last compliant version (digest-pinned) and ratify
   a migration-or-fork record within **90 days**. The freeze is a tourniquet,
   not a treatment.
3. **Remediation by upstream contribution.** A capability gap is closed by a
   PR to the closest layer of the stack where it belongs, in that community's
   language and idiom — never by adopting a closed product, never by a
   private workaround. Subsidiarity decides "closest"; house preference
   governs what we build, not what we contribute. A gap closed this way
   usually means carrying a patch until it lands upstream; how a patch is
   carried, registered, reviewed and eventually promoted or dropped is
   decided once, in the contribution and sponsorship record, and is not
   restated here.
4. **Enforcement.** Every project CI generates a machine-readable license
   report and fails the build on any license outside the encoded allowlist,
   along **every** path its runtime shape presents — not one
   chosen path: an SBOM per image for container and server runtimes, and a
   dependency-manifest report per package ecosystem (illustrative tooling,
   not a binding list — `com.github.jk1.dependency-license-report` for
   Gradle, `license-checker` for npm, `pip-licenses` for Python,
   `cargo-license` for Rust). A project presenting more than one shape runs
   all of them; these are cumulative, not alternatives, and a project that
   ships images *and* publishes a package *and* builds a frontend has three
   obligations rather than a choice among three. Every report is generated,
   never hand-compiled, and is **normalized to SPDX identifiers before
   comparison** against the allowlist, reading the deprecated metadata fields
   an ecosystem still permits; an unresolvable or absent declaration is
   treated as a failure to be investigated, never as a pass. All of it is
   paired with a quarterly scan that watches pinned upstreams for
   license-file changes and archive status.

   **The allowlist is generated, never typed.** §1 admits the union of the
   OSI-approved and FSF-free sets, and both are machine-readable in SPDX's own
   data as `osi_approved` and `fsf_libre`. A project's allowlist is that union
   with deprecated identifiers excluded, produced by a generator and committed
   with its provenance — the source, the criterion, and the date it was taken.
   A hand-kept list is wrong in two directions at once, and both were found in
   the same reading: it admits fewer licenses than §1 does, so every honest
   dependency outside it fails and needs an individual adjudication; and it
   admits identifiers §1 does not, because nothing checks a typed list against
   the criterion it claims to encode.

   **The generated file is committed rather than computed at run time.** A gate
   reading SPDX live changes its verdict when a package updates, with no
   governance act anywhere. Regenerating produces a diff, and the diff is the
   amendment. Allowlist changes are amendments to this record in every case; a
   project may not encode a local exception.

   **Normalization is not exception.** An identifier absent from both sets
   fails. Where a package's declared identifier and its licence *text* differ —
   a package declaring `PSF-2.0` while shipping the full Python licence stack
   that SPDX calls `Python-2.0` — the disposition is a normalization entry,
   made only after reading that package's licence file, and recorded with what
   was read. Mapping an identifier onto one it is not is how a gate starts
   passing things nobody checked.

   **Copyleft is admitted here, as §1 says, and a permissive-only allowlist
   avoids it technically.** That is the outcome §1 forbids, reached by omission
   rather than by decision, and a generated list is what prevents it.
5. **Scope boundary.** §1 binds a *deployed runtime path*, and a project's
   environment is not one. A license report generated from everything installed
   scans the test runner, the linter and the documentation toolchain alongside
   what ships, and passes them only for as long as they happen to be
   permissively licensed. The risk this record is about is a clause in someone
   else's contract embedded in our stack: a library that draws documentation on
   a contributor's machine is embedded in nothing we deploy, and its relicensing
   changes nothing a user receives. So the report covers the runtime dependency
   closure, and each project states which dependency groups that closure is
   taken from.

   A closure that cannot be computed is not an empty one. Where a manifest is
   unreadable or an ungated dependency is absent, the report falls back to the
   whole environment and says so — over-reporting is the safe direction, and
   silently checking a smaller set than the report claims is not.

   This is a licence rule and not a supply-chain one. A compromised build
   dependency is a real risk and a different one; a licence gate cannot see it,
   and enlarging this rule to gesture at it would leave both jobs half done.

   The floor is userspace plus kernel modules. Microcode,
   firmware, and BIOS/UEFI are out of scope — no bootable x86 stance
   satisfies the rule, and an unenforceable constitution is worse than an
   honest boundary. Coreboot-capable purchasing is encouraged, not mandated.
6. **Hosted services are in scope, and are tested for ownability rather than
   for license.** A third-party service in a deployed runtime path — object
   storage, managed databases, identity providers, transcoding, hosted
   inference, externally-loaded frontend assets — has no license to check and
   is therefore invisible to §4's generated reports. It is instead recorded
   in the adopting project's records as a named dependency, reached across a
   seam satisfying the seams doctrine, and held to this test: *if this
   provider withdrew, re-priced, or refused service tomorrow, is the response
   a configuration change or an engineering project?* Only the first is
   acceptable, and it is what the seams doctrine already exists to produce.
   A protocol seam makes a provider replaceable; it does not make a remote
   service ownable-offline, so a project relying on one states the residual
   exposure plainly rather than treating the seam as having eliminated it.
   Enforcement here is a reviewed inventory, not a scanner: no tool can
   discover a service dependency from a repository, which is precisely why it
   must be written down.
7. **Per-component compliance is not license compatibility.** Every component
   in a deliverable may individually satisfy §1 while the combination is not
   distributable under the license the project declares — most commonly a
   permissively-licensed project bundling a copyleft component into a
   distributed artifact. Copyleft remains explicitly acceptable under §1; the
   obligation created here is that a project whose deliverable combines
   licenses records what its distributed artifact is actually licensed under,
   and declares that, rather than inheriting a declaration from its own
   source tree by default. Resolving a genuine incompatibility is a project
   decision — relicense the deliverable, replace the component, or separate
   the artifacts — and this record does not pick among them.

## Consequences

- Projects perform a baseline component audit at adoption and record
  dispositions in their instance records (the streaming project's ADR-0001 is
  the reference instance).
- Performance ceilings from open-driver-only paths are accepted as hardware
  cost, not sovereignty cost.
- Contribution latency is accepted deliberately: gaps become commons
  improvements — the business model expressed as engineering policy.
- A green license report is no longer, on its own, a claim of compliance. §6
  is the part no CI job can answer, so a project's records — not its build
  status — are where its service dependencies are accounted for.
- Cost accepted: §6's inventory is maintained by humans and can go stale
  between reviews, which is a weaker mechanism than a generated report. It is
  the strongest mechanism available for a dependency that leaves no trace in
  the repository, and a weaker mechanism aimed at the real exposure beats a
  stronger one aimed only at what happens to be scannable.
- Cost accepted: §4's normalization requirement means each ecosystem's gate
  carries a mapping layer that needs occasional maintenance as license
  metadata conventions change.
- §7 makes a project's declared license a reviewed output rather than an
  inherited default, which will surface existing mismatches. Surfacing them
  is the intent.

## Alternatives considered

1. **Documented proprietary opt-ins** — rejected: each is a future migration
   on someone else's terms.
2. **Waiver register** — rejected: an opt-in list with paperwork; §3 ensures
   a compliant response always exists.
3. **Copyleft-only or permissive-only** — rejected both ways: openness is the
   criterion; copyleft-vs-permissive is per-component fit.
4. **Leave hosted services to the seams doctrine alone** — rejected: that
   doctrine governs integration shape and is satisfied by a replaceable seam,
   which is necessary but does not record the dependency or its residual
   exposure anywhere. The result observed in practice is a project that is
   compliant with every record it can be measured against while its least
   ownable dependency appears in none of them.
5. **Require every runtime path to use a single unified gate** — rejected:
   the ecosystems genuinely differ, and a unified tool would either
   lowest-common-denominator the coverage or become a QM-maintained engine of
   exactly the kind the seam doctrine says not to build.
6. **Treat any copyleft component in a distributed artifact as excluded**,
   sidestepping §7 — rejected: it contradicts §1's explicit acceptance of
   copyleft and would technically avoid what the record says to handle
   contractually.

## Revision triggers

- Any §2 relicense event (starts the 90-day clock).
- A carried patch trips the stall condition the contribution and sponsorship
  record defines.
- Material change to the OSI-approved set, or an FSF-free-but-not-OSI
  license reaching the gate for a second time — one adjudication is an
  amendment, a pattern means §1's two criteria need reconciling rather than
  case-by-case handling.
- A §6 provider changes terms, withdraws, or fails — the ownability test is
  run against the real event rather than the hypothetical.
- A project's §6 inventory is found to be stale or incomplete at review — the
  reviewed-inventory mechanism is not holding and needs teeth beyond review.
- A §7 incompatibility is found in a shipped deliverable — the declaration
  obligation was not enough on its own, and the record needs a gate rather
  than a requirement to write something down.
- A generated report is shown to have passed a component whose declaration
  was absent or unresolvable — §4's normalization clause is not being applied
  as written.

## Amendments

*None.*
