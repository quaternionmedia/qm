# ADR-XXXX — QM Constitution Adoption Scope for qmcp

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-11 |
| **Pends on** | One outbound-licensing input the org has not settled for this project: qmcp declares **no license at all** — no `LICENSE` file, and no `license` key in `pyproject.toml` — so unlike every other project adopted so far there is no existing grant to either reproduce or replace. Which class of the outbound-licensing record this falls into is §9's C1, and it is the reason this adoption ships without `REUSE.toml`, without `LICENSES/`, and without `reuse-lint.yml`. Every other disposition below is fixed regardless. |
| **Principle** | P6 — decisions are documented or they didn't happen |

## Context

qmcp is an MCP server with a FastAPI HTTP surface, a SQLModel persistence
layer, a Click CLI, and a human-in-the-loop request queue. It is being adopted
now because the corpus intends to depend on it: the monitoring-seam record
makes qmcp the live orchestration surface whose gate queue a collector reads
and dossier displays.

That intent is what forces the order. A generator whose facts a dashboard
depends on should not be reading a repository with no gates, and qmcp today has
none — no `AGENTS.md`, no `CLAUDE.md`, no `.github` of any kind, no `LICENSE`,
no `CODEOWNERS`, no submodule, and no CI. Its governance layer in
`harness-status.json` reads as unknown for the honest reason that there is no
`project/qmcp` branch to read.

Adoption is also not a formality here, because three of the conflicts below are
live hazards on a workstation that runs six sessions at once, not latent
mismatches. They are named as conflicts rather than fixed in this record's own
change, so that a human decides the fix rather than inheriting one.

Every fact in §9 was established by running the command or reading the line
cited, at qmcp commit `a3f827d`. None is inferred from the shape of the code.

## Decision

1. **qmcp adopts the QM constitution by reference**, vendored at
   `governance/qm` as a submodule pinned to this `project/qmcp` branch. This
   project's own records live in `governance/qm/adr/` on this branch, not at
   qmcp's root.

2. **The adoption change is additions only.** qmcp's working tree carries 18
   modified, 10 untracked and 2 deleted files on `feat/pydantic-ai-integration-docs`
   with no pull request open, including the whole `qmcp/cookbook/` package,
   `qmcp_mcp.py`, and five of the test files. Adoption touches no file that
   work touches — in particular not `pyproject.toml` — so the two cannot
   conflict and neither waits on the other. The cost is that the dependency
   declaration in C5 is named here rather than fixed here.

3. **Three workflows are copied verbatim from the seed**: `adr-lint.yml`,
   `one-pr-check.yml`, `submodule-check.yml`. `reuse-lint.yml` is deliberately
   absent until C1 is settled, because a REUSE gate over a repository with no
   declared license fails for a reason a human has to answer, and a check that
   is red for a known unanswerable reason trains its readers to ignore it.

4. **The pointer files are symlinks, not copies** — `CLAUDE.md` and
   `.github/copilot-instructions.md` both resolve to `AGENTS.md`, mode 120000,
   so one edit keeps all three current.

5. **The conflicts in §9 are recorded, not silently fixed.** Each names what
   was measured, which rule it meets, and who decides.

## Consequences

- qmcp's governance layer stops reading unknown, so the harness can report it
  alongside the other twelve repositories.
- The one-PR slot rule begins applying to qmcp. Its 14 currently-open pull
  requests are all dependabot's, and the slot check counts automation
  separately, so no human slot is consumed today.
- The monitoring-seam record's decisions 4, 5 and 10 land on qmcp as work: a
  run-file, port 0, and an identity endpoint. Until then the collector writes
  an unknown for instance identity rather than attributing a measurement.
- Cost accepted: this adoption leaves qmcp REUSE-noncompliant and says so,
  rather than declaring a license on the organisation's behalf.

## Alternatives considered

**Fix the three hazards in the adoption change.** Rejected on the additions-only
rule: `qmcp/config.py` and `qmcp/cli.py` are both in the modified set, so a fix
here would collide with in-flight work and make one wait on the other. Naming
them costs a round trip and keeps both branches independent.

**Declare MIT and move on**, matching the other projects. Rejected: the other
projects' `REUSE.toml` files reproduce a grant the repository already made.
There is nothing to reproduce here, so declaring one is the organisation
deciding by default, which the outbound-licensing record's §0 reserves to a
human.

**Wait for the in-flight work to land first.** Rejected: it has been in flight
since 2026-02-06, and the corpus needs qmcp governable now for the seam record
to have a governed repository to point at.

## 9. Conflicts between qmcp as it stands and the constitution

Ordered by how much they cost today, not by how much code they touch.

| # | What was measured | Rule | Decides |
|---|---|---|---|
| C1 | No `LICENSE`, and `git show HEAD:pyproject.toml` has no `license` key | Outbound licensing §0 | Human — this record's `Pends on` |
| C2 | `qmcp test --clean` defaults **True** and unlinks `./qmcp.db` before *and* after pytest (`qmcp/cli.py:1111,1124-1128,1149-1154`) | Async contract §4 | Human — see below |
| C3 | `port: int = 3333` (`qmcp/config.py:19`) and `database_url = "sqlite+aiosqlite:///./qmcp.db"` (`:23`), resolved against one process's cwd; `cookbook dev` prints "MCP server already running" and uses whatever answered (`qmcp/cli.py:728-729`) | Async contract §4 | Human |
| C4 | `GET /v1/human/requests/{id}` sets `status = EXPIRED` (`qmcp/server.py:373-382`) and `get_session` commits on exit (`qmcp/db/engine.py:71`), so the read persists a terminal transition; the list endpoint applies no expiry, so the two disagree about the same row | Monitoring seam, decision 1 | Human |
| C5 | `mcp` is imported by `qmcp_mcp.py` and therefore by `tests/test_qmcp_mcp.py`, and is declared nowhere in `pyproject.toml`; `python -c "import mcp"` gives `ModuleNotFoundError`, so collection aborts and any claim the suite is green is unverifiable in a clean environment | Decision-record discipline §7 | Fix in the in-flight branch |
| C6 | No Alembic anywhere; the schema is `SQLModel.metadata.create_all` at startup, which never ALTERs. The checked-out `qmcp.db` `executions` table lacks `priority` and `parent_execution_id`, both declared required by the DTOs, so an endpoint returning one raises `OperationalError` | House stack | Human |
| C7 | `qmcp_mcp.py:433` exposes `submit_human_response`, so an agent can answer its own human gate; and no `Depends(`, no `CORSMiddleware`, no bearer scheme appears anywhere in the HTTP app | Human-in-the-loop is a boundary, not a convention | Human |
| C8 | 30 files uncommitted on a branch with no pull request, since 2026-02-06 | Everything arrives as a pull request | Human |

**C2 is the one to fix first**, ahead of C3 and independent of it. A default
port is a collision a session notices. A test command that deletes
`./qmcp.db` — before the run and again after it, by default, with no prompt —
destroys another session's *pending human gate queue*, and the destruction is
silent, permanent, and indistinguishable afterwards from nobody having asked
for anything. That is the empty-queue-reads-as-nothing-is-waiting failure the
monitoring-seam record is built to prevent, reached without any monitor being
involved.

## Revision triggers

- C1 is settled: `REUSE.toml`, `LICENSES/` and `reuse-lint.yml` are added, and
  decision 3's exception is retired.
- C2 and C3 are fixed: qmcp binds port 0, writes a run-file, and takes a
  per-session database path. The monitoring-seam record's decision 4 becomes
  satisfiable and the collector can identify what it is talking to.
- C4 is fixed: no `GET` persists a state change, and the seam record's second
  reason weakens to the ordinary one.
- The in-flight branch lands: C5 and C8 close, and `pyproject.toml` becomes
  editable by an adoption change without collision.

## Amendments

None.
