# Handoff — frizzle kickoff (bus + dispatcher)

> **Historical document, dated 2026-08-13.** It is reached directly from the
> repository README, so the staleness warning that covers this directory is
> repeated here rather than left one hop away.
>
> Two things it says are no longer true. *"Nothing from this session is
> committed or pushed anywhere"* below described loose files; they are
> committed now. And frizzle is described as a **rule engine** among other
> things — none is implemented, and the README's "Not yet built" section says
> so. The `qm` pin it stamps (`104361a`) does not resolve in the clone this
> repository was built from; re-derive it before relying on any claim here.
>
> Nothing else in this page has been edited: it is kept as written, because
> its value is being the record of what that session actually knew.

**Goal of the work.** Stand up the org's minimal messaging queue and automation
dispatcher: Mosquitto brokered via moat, a new project-seed-born repo named
**frizzle** as journal / work-queue semantics / rule engine / collector, a
three-recipe cookbook as the executable contract, rad as first consumer, and
moat brought into qm governance ahead of the general propagation.

*Stamped 2026-08-13, from depth-1 clones: `qm` at `104361a` (2026-08-12),
`moat` at `16a595a`, `qmcp` at `85013c5`, `rad` at `b854747`, `looksatwords` at
`af61b28`, `codecartographer` at `cddbf34`, `moe` at `a64c413`. Every claim
below is true at those commits and nowhere else — re-derive before acting.
`rad-android` was not surveyed: the repo is private and the session had no
credentials. Anything said about it is inference.*

---

## Standing constraints, in force

- **Nothing from this session is committed or pushed anywhere.** The bundle was
  produced in an ephemeral cloud workspace and delivered to Peter as files.
  There are no branches, no PRs, no working trees to inherit. This is
  deliberate, not an oversight.
- **The async contract binds the rollout**: one open PR per repo per
  contributor; demo branches are not PRs; fold in the mandated order.
- **The collector rule binds frizzle from day one**: a view reads a document; a
  collector reads the world. frizzle is the collector; no dashboard opens a
  socket to the broker.
- **Orchestration stays out of the qmcp server plane** per
  `qmcp:docs/architecture.md`, which declares itself right over conflicting
  code. frizzle integrates with qmcp as a client.
- **Governance codification is staged** (plan §4 Phase 4, ledger §5) — except
  moat's adoption and frizzle's born-governed spawn, which are pulled forward
  by decisions 5 and 6.

## Decisions taken, by the human, 2026-08-13

Transport is MQTT/Mosquitto. The dispatcher repo is named **frizzle**, spawned
from `qm/project-seed`. First consumer is rad (stage/media messaging), then
per-project discovery/PoC demo branches. The cookbook's three canonical
classes are **user text messaging**, **app configuration**, **payload
messaging**, and green recipes are the conformance claim. moat enters qm
governance as a named commitment sequenced into Phase 0, not backlog. All six
are recorded with rationale in `qm-bus-frizzle-plan.md` §0.

## What exists now

Only this bundle. Specifically: the amended plan; envelope contract v0 and
topic taxonomy v0 (drafts, expecting revision from the rad PoC); the
three-recipe cookbook spec; a draft Mosquitto wrapper chart matching moat's
`whoami`/`home-assistant` pattern; and two checklists (frizzle spawn, moat
adoption). None of it has been executed against a live cluster or a real
GitHub org. The chart in particular is **unverified inference** — it follows
moat's wrapper idiom by reading, not by deploying.

## What is unfinished, and what done looks like

1. **File this handoff and the retrospective into qm** through qm's own
   process. Done: this page lives at `handbook/handoffs/frizzle-kickoff.md`,
   the retrospective in `perspectives/`, both through a PR that passes qm's CI.
2. **Spawn frizzle** per `checklists/frizzle-spawn.md`. Done: repo exists,
   seed CI green, `project/frizzle` branch on the qm remote, contract docs and
   cookbook scaffold in place, every spawn friction point appended to plan
   ledger N1.
3. **Mosquitto chart PR into moat** from `moat/charts-mosquitto/`. Done: chart
   under `charts/` (the releaser only fires there), Application CR added to
   `charts/groot`, broker reachable with auth + TLS, chart released by CI.
4. **moat adoption PR** per `checklists/moat-adoption.md`, queued behind the
   chart PR in moat's single slot. Done: the checklist's verification block
   passes and moat appears in `governance-status.yaml`.
5. **Phase 0 exit test.** Done: a message published from one machine is in
   frizzle's journal, in a fresh `generated_at`-stamped `bus-status`, and
   visible in Grafana; the three cookbook recipes run green.

## Blocked, and on whom

- **rad-android survey** — on Peter granting repo access. Only Phase 2e cares.
- **Ratification of anything** — on qm's own second-code-owner condition,
  outside this effort's control. Everything stays DRAFT-shaped until then.
- **Broker credentials/ACL design** — wants a human decision on whether
  Frigate/Home Assistant share the QM ACL namespace or get their own (touches
  plan ledger N4, the plaintext-credentials rotation).

## Could not verify

- That `project-seed` spawning works end to end — no repo has ever been born
  from it (plan ledger N1). The spawn checklist is written from the seed's
  documents, not from a successful run.
- That the app-template chart shape actually serves Mosquitto's persistence
  and config-file needs — drafted, never `helm template`-ed against the
  cluster's values.
- Whether MQTT round-trip latency on the real network meets rad's
  above-the-clock tolerances — that is Phase 1's question, with numbers.

## The single next action

Open the qm PR that files this handoff and the retrospective; it is the
smallest step that moves the work out of a session transcript and into the
corpus, and it occupies no slot any other work needs.
