# ADR-XXXX — hearth adopts the corpus, and owns the family contract and what holds members to it

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-11-01 |
| **Pends on** | hearth's first tag, a person's act (`records/DRAFT-version-tags-are-claims.md`): until it is cut, every member depends on hearth by a path source and the contract's coordinate is unclaimed (§3). |

## Context

hearth is the library of the performing family's contract, `family/1`, and
the publisher of the vector set the contract is measured by (the corpus's
`plans/plugin-or-server.md` and `records/DRAFT-one-contract-whoever-hosts-it.md`,
on the branch that offers them). The family's members ShowStopper, carlos, joe
and leo keep the contract through it, and ShowRunner runs its coordinator as
a copy. The corpus's `records/DRAFT-build-the-seam-buy-the-engines.md` §5
admits a QM-authored library only as a separate public repository with a
release line, consumed as a released package;
`records/DRAFT-a-shared-tag-asserts-interoperability.md` makes a contract
surface a coordinate every repository on it shares; and
`records/DRAFT-outbound-licensing.md` §6 licenses an embeddable library
MPL-2.0, named in the library's own record. The repository is public at
`quaternionmedia/hearth` and licensed MPL-2.0 under REUSE. This record is the
adoption that `handbook/forking-a-project.md` step 6 asks for.

## Decision

### §1 Scope

hearth owns four things and nothing else:

1. **The contract and its measurement**: `family/1`, both sides, in
   `docs/contract.md`; `conformance/vectors.json`, the cases `hearth check`
   asserts under one version; and `hearth check`, which replays them against
   a URL, member or hub.
2. **The member library**: `hearth.Member`; the hosts that serve one alone,
   beside an aiohttp page or inside ShowRunner; `hearth.supervise`;
   `follow.js`; and `hearth.testing`.
3. **The coordinator**: `hearth.coordinator`, one text an exemplar imports
   from `qm-hearth` at a version or, where its maintainer takes no
   dependency, copies whole with `hearth fork` and holds with
   `hearth check --copy`.
4. **The demo**, Loopback: a show of nine cues that ShowRunner runs alone,
   with the members beside it.

Not in scope: a member's own behaviour, a hub's own code, which family a
repository claims, and the gate across the family, which is the corpus's
`qm family-demo`.

### §2 Adoption

The corpus is mounted at `governance/qm` by its HTTPS URL and pinned to
`project/hearth`, which carries the seed's `adr/`. The seed's gates run from
the submodule: the ADR lint, submodule refs, REUSE lint, the stack rule, the
leak, signature, tag-claims and timeless checks. `AGENTS.md` is the seed's
with hearth's own section below the marked line, and `CLAUDE.md` and
`.github/copilot-instructions.md` point at it. Dependabot's updates arrive
grouped, one pull request per ecosystem per week. `main` takes a change by a
pull request with a merge commit, and by nothing else.

### §3 Gaps, and what closes each

hearth was written under the corpus, so it carries no conflict with an org
record. It carries these gaps:

| Gap | Record | Closed when |
|---|---|---|
| No release line: every member reaches hearth by the path source `../hearth`, and `qm-hearth` carries a development version | build-the-seam §5 | a first tag is cut, the members depend on `qm-hearth` at that version, and `hearth fork` writes a copy from an installed release |
| The contract's coordinate is unclaimed: no repository on the surface pins the version `conformance/vectors.json` carries, and the corpus's `ci/interop-registry.yaml` has no row for `family/1` | shared-tag record | each member's suite pins the version it replayed, the registry names hearth as publisher and each member as an implementation, and `uv run qm interop` reads them |
| The vector set names the checker's assertions, and the checker does not read it | shared-tag record §4 | `hearth check` replays the cases from the file, and a case carries an input and an expectation of its own |
| A hearth host writes no run-file, so `uv run qm instances` cannot identify a member | monitoring record, decisions 4 and 5 | each host declares itself in a run-file naming `/family/identity` as its health path |

### §4 Obligations from the org records

| Obligation | Here |
|---|---|
| **Baseline component audit** | §5 |
| **Licence gates, cumulatively** | One ecosystem, uv, and no image: `uv.lock` resolves every dependency to a release on PyPI, `reuse lint` runs on every push and pull request, and Dependabot watches the lock. **Gap:** nothing reads the lock against open advisories; compliance is a check in the suite or a workflow that does. |
| **Service inventory** | **None.** hearth reaches no third-party service: a member is reached at a URL a person gives it, and the demo runs on one machine's loopback. |
| **Quarterly upstream scan** | **Gap.** Not scheduled; compliance is a scheduled workflow watching each pinned upstream's licence file and archive status. |
| **Seam protocol named** | `family/1` is HTTP, JSON and server-sent events, each with many implementations; hearth selects no third-party component behind a seam of its own. |
| **Control-plane instance record** | **hearth has no control plane.** It is a library and a contract; the coordinator runs inside an exemplar's app, whose own record owns that seam. The smell that changes this is a server hearth itself must run for a show, which the supervisor prototype would become. |
| **Risk register** | §6 |
| **Carried patches registered** | **None.** `uv.lock` carries no git source, path source or build-time patch. |

### §5 Baseline component audit

Runtime, as `pyproject.toml` declares them and `uv.lock` resolves them:
fastapi (MIT), pydantic (MIT), uvicorn (BSD-3-Clause) and httpx
(BSD-3-Clause); through them starlette (BSD-3-Clause), anyio (MIT), httpcore
(BSD-3-Clause), h11 (MIT), idna (BSD-3-Clause), certifi (MPL-2.0), click
(BSD-3-Clause) and annotated-types (MIT). The `aiohttp` extra: aiohttp
(Apache-2.0 and MIT). Development only: pytest (MIT), ruff (MIT) and pluggy
(MIT). Every licence is permissive or a file-level copyleft, compatible with
MPL-2.0 outbound and with the AGPL services the outbound record has such a
library combine into. Disposition: every one kept.

### §6 Risk register

| Risk | Likelihood | Consequence | Held by |
|---|---|---|---|
| A copy of the coordinator drifts from the text | high over time | two behaviours under one contract | `hearth check --copy` and `copies.KNOWN`; the exemplar's own test holds the copy to its line; the import route for every exemplar whose maintainer takes the dependency |
| The vector set and the checker disagree | medium | a conformance claim rests on cases nobody replays | §3's third row, and a test in hearth that the file names what the checker asserts |
| Single maintainer | certain | no second reader; ratification waits on the same condition across the org | named, not mitigated |
| The supervisor prototype runs on a show machine before its policy is decided | medium | a member restarted with nobody told, or not restarted | `plans/plugin-or-server.md` §8 keeps the policy a person's, and the demo alone uses the prototype |
| A member stays on a path source after a tag exists | medium | a member that builds on one disk only | §3's first row; the member's own CI is what fails, since the submodule check has no eye on a path source |

## Consequences

- Every change to hearth arrives on `main` by a pull request the seed's gates
  run on, and a record arrives on `project/hearth` the same way.
- The members' path sources give way to a version at the first tag, which is
  a person's claim naming what was reviewed and what was tested by hand.
- The gaps in §3 and §4 are hearth's open work, carried in the corpus's
  `plans/plugin-or-server.md` until each closes.

## Alternatives considered

1. **Adopt after the first tag.** Lost: the gates and this record would miss
   the work that decides what the tag claims, and
   `records/DRAFT-build-the-seam-buy-the-engines.md` §5 wants the library
   governed as a project from the start.
2. **Fold hearth's records into ShowRunner's, or into the corpus's.** Lost:
   hearth is consumed by four members of three families and coordinates none
   of them, so its decisions bind no single exemplar; and the corpus's own
   namespace holds org-level records only.

## Revision triggers

- The first tag, which closes §3's first row and moves `Pends on`.
- A second contract surface or a second exemplar, which tests §1's border.
- A third-party service in a runtime path, which makes §4's service
  inventory a list.

## Amendments

*None.*
