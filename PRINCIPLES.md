# Quaternion Media — Core Principles (charter)

The interpretation from which the org records are cut. Quaternion Media's
operating principles — visible in its public repositories, sponsorship model,
consulting practice, and house stack — stated explicitly so they can be
encoded as decision records with enforcement, rather than remaining tacit
culture that erodes one convenient exception at a time.

A principle earns a record only if it produces **decisions with teeth**:
enforceable consequences, honest alternatives, revision triggers. Principles
that are values without architectural consequence are routed to the handbook
or style guide, and the routing is stated. The known failure mode of
principles-records is the motherhood statement — unfalsifiable, decorative.
Every record below names its enforcement mechanism.

---

## P1 — Ownership is the deliverable

What QM sells — to clients and to itself — is independence: systems that
continue to work if every vendor, cloud, and upstream disappears tomorrow.
"Self-hosted" is the mechanism; *ownable-offline-indefinitely* is the
requirement. A component is owned only if we can run it, rebuild it from
sources we hold, and modify it without anyone's permission. Anything less is
a rental with extra steps.

→ Org record: **Open-license exclusion and upstream-contribution
remediation.** Project instances add deployment-and-provenance records
(offline mirrors, source-built images, internal CA, restore-verified
backups), whose CI gates are the teeth.

## P2 — Commons-first economics

"Open-source maintainers first, consultants second" is a causal claim, not a
slogan: the consulting is credible *because* the maintenance is real.
Capability gaps are closed upstream; sponsorship is a first-class budget line
(including paying for review bandwidth on our own PRs); a private workaround
is a small debt default against the commons the business stands on.

→ Org records: the remediation clauses of **Open-license exclusion** plus
**Contribution and sponsorship policy**, with the org-level carried-patch
register as the audit surface — a patch carried anywhere is a commitment made
by the org, so the register is org-level by design.

## P3 — Seams on standard protocols

Replaceability is the risk strategy. Third-party components touch a system
only through protocols and formats with multiple independent implementations.
Then any vendor failure — abandonment, relicense, governance collapse — is a
component swap, not a redesign. Proprietary *protocols* are a deeper lock-in
than proprietary code, because they survive even an open license.

→ Org record: **Seams on standard protocols**, with the replaceability test
and the exception mechanism as teeth.

## P4 — Build the seam, buy the engines

Custom code concentrates where sovereignty matters most: the small control
plane holding state, policy, and orchestration. Engines — muxers, databases,
transcoders, detectors — are selected, not written. The seam is deliberately
boring, and it is the one place where bus-factor is *ours*, which is the only
acceptable place for it. Ordering rule resolving the tension with P2: every
new capability first asks *which engine should own this upstream* before
defaulting to the seam; seam logic is whatever no engine should reasonably
own.

→ Org record: **Build the seam, buy the engines** (doctrine). Each project
ratifies its own control-plane instance record with size-smell revision
triggers.

## P5 — One house stack, deeply known

What *we build* uses one stack, deeply: Python — FastAPI, SQLModel/Pydantic,
Metaflow, Click, Jinja2 — plus single-file HTML/JS for visualization
deliverables. Depth compounds: patterns transfer across fleet management,
streaming, and media tooling, and anyone can enter any QM codebase. The
complement: what *we contribute* is written in the target community's
language and idiom. House preference governs our repos, not our PRs.

→ Org record: **House stack**, with the dependency-review gate as teeth and
explicit carve-outs for contributions and client-mandated stacks.

## P6 — Decisions are documented or they didn't happen

Documentation-forward means gap-analysis-first design, rationale recorded
alongside changes, and decision memory kept under squash discipline: drafts
have no memory, ratified records have nothing but memory, Git is the
archaeology. A decision living only in a chat log or a maintainer's head is a
decision the organization doesn't possess.

→ Org record: **Decision-record discipline** — the process, template, and
lint, adopted by every project via the seed.

## P7 — Public by default

Work ships in the open unless a specific, named reason (client
confidentiality, credentials, embargoed security fixes) requires otherwise;
the burden of proof sits on closing, not opening. This is the substrate P2
and P6 stand on — public fork branches, decision records clients and
community can read.

→ Routed to the **handbook** (business policy: contractual exceptions, no
architectural alternatives to weigh), with a defined promotion path to record
form if its boundary ever needs adjudicable teeth.

## P8 — Systems over heroics

The conductor's job is to make the performance not depend on the conductor.
Operations are declarative — GitOps, static config, stateless services
recreatable from version control — automated as DAGs (retention, backup
*restore verification*, upstream scanning), and observable. No SSH-to-prod,
no snowflake state, no 2 a.m. brilliance as a system input.

→ Enforced through each project's deployment-and-provenance record (P1's
instance layer); no separate org record — principles may share enforcement,
and a mirror record would violate one-decision-per-record from the other
direction.

## P9 — Minimal, legible deliverables

Single-file HTML visualizations, modular JS, restrained aesthetics, prose
without ornament: legibility is respect for the reader and the future
maintainer.

→ Routed to the **style guide**. Taste encoded as constitutional law degrades
both.
