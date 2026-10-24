# ADR-XXXX — QM Constitution Adoption Scope for qmcp

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-11 |
| **Pends on** | One outbound-licensing input the org has not settled for this project: qmcp declares **no license at all** — no `LICENSE` file, and no `license` key in `pyproject.toml` — so unlike every other project adopted so far there is no existing grant to either reproduce or replace. Which class of the outbound-licensing record this falls into is §9's C1, and it is the reason this adoption ships without `REUSE.toml`, without `LICENSES/`, and without `reuse-lint.yml`. Every other disposition below is fixed regardless. |
| **Principle** | `decisions-are-documented` — decisions are documented or they didn't happen |

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
mismatches: C2, C3 and C7. They are named as conflicts rather than fixed in
this record's own change, so that a human decides the fix rather than
inheriting one. C2 is closed; C3 and C7 are each closed in part, and §9 names
the part that is open.

Every fact in §9 was established by running the command or reading the line
cited: for C2, C3 and C7 at qmcp commit `a41f9a3`, and for the other rows at
qmcp commit `a3f827d`. None is inferred from the shape of the code.

## Decision

1. **qmcp adopts the QM constitution by reference**, vendored at
   `governance/qm` as a submodule pinned to this `project/qmcp` branch. This
   project's own records live in `governance/qm/adr/` on this branch, not at
   qmcp's root.

2. **The adoption change is additions only.** qmcp's working tree carries 18
   modified, 10 untracked and 2 deleted files on `feat/pydantic-ai-integration-docs`,
   including the whole `qmcp/cookbook/` package, `qmcp_mcp.py`, and five of the
   test files. That branch's committed work is already on `main` — PR #1, merged,
   and `git diff a3f827d origin/main` is empty — so what is outstanding is the
   working tree alone, and it has no pull request. Adoption touches no file that
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
- The monitoring-seam record's decisions 4 and 5 hold on qmcp for a server
  started by `qmcp serve`: it writes a run-file carrying its port, resolved
  database path, start time and session, and states the same identity on
  `/health` (qmcp#110). A qmcp started any other way leaves no run-file, and
  for it the collector writes an unknown for instance identity rather than
  attributing a measurement. For decision 10's acceptance run, qmcp's own
  suite starts `qmcp serve --port 0` in a process of its own and finds it by
  the run-file it leaves (`qmcp/testing/process.py`, qmcp#113).
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
| C2 | `qmcp test` deletes the configured database only when `--clean` is passed, and `--clean` defaults off (`qmcp/cli.py:1633`); without it the suite builds its own databases and leaves the configured one alone | Async contract §4 | Closed by qmcp#86 — see below |
| C3 | Closed: `qmcp serve --port 0` binds a port the system picks, writes a run-file to `~/.qmcp/run` (or `QMCP_RUN_DIR`), and states the same identity on `/health` (`qmcp/instance.py`; `qmcp/cli.py:873,893`); `cookbook dev` matches the database fingerprint of whatever answers its health URL and refuses a server over another database (`qmcp/cli.py:281,1229`). **Open:** the defaults are `port: int = 3141` (`qmcp/config.py:27`) and `database_url = "sqlite+aiosqlite:///./qmcp.db"` (`:31`), resolved against one process's cwd, so a server started with no flags binds a fixed port, and two sessions started in one checkout share one queue unless each sets `QMCP_DATABASE_URL` | Async contract §4 | Closed in part by qmcp#110; Human — the per-session default database and the default port |
| C4 | `GET /v1/human/requests/{id}` sets `status = EXPIRED` (`qmcp/server.py:373-382`) and `get_session` commits on exit (`qmcp/db/engine.py:71`), so the read persists a terminal transition; the list endpoint applies no expiry, so the two disagree about the same row | Monitoring seam, decision 1 | Human |
| C5 | `mcp` is imported by `qmcp_mcp.py` and therefore by `tests/test_qmcp_mcp.py`, and is declared nowhere in `pyproject.toml`; `python -c "import mcp"` gives `ModuleNotFoundError`, so collection aborts and any claim the suite is green is unverifiable in a clean environment | Decision-record discipline §7 | Fix in the in-flight branch |
| C6 | No Alembic anywhere; the schema is `SQLModel.metadata.create_all` at startup, which never ALTERs. The checked-out `qmcp.db` `executions` table lacks `priority` and `parent_execution_id`, both declared required by the DTOs, so an endpoint returning one raises `OperationalError` | House stack | Human |
| C7 | Closed: none of the twelve tools `qmcp_mcp.py` exposes answers a human request (qmcp#97), and `qmcp serve`, `cookbook serve` and `cookbook dev` bind `127.0.0.1` by default and warn when bound off it (`qmcp/config.py:19`; `qmcp/cli.py:727,841,1159`; qmcp#98, qmcp#101). **Open:** the answer is `POST /v1/human/responses` (`qmcp/server.py:521`), and no `Depends(`, no `CORSMiddleware`, no bearer scheme appears anywhere in the HTTP app, so any process on the machine — an agent's shell included — can answer a human gate through it; `qmcp/client/mcp_client.py:449` wraps that call | Human-in-the-loop is a boundary, not a convention | Closed in part by qmcp#97; Human — how the HTTP app tells a human's answer from an agent's |
| C8 | 30 files uncommitted in the working tree, unchanged since 2026-02-06. The branch's *committed* work did arrive as PR #1 and was merged; it is the working tree that has no pull request | Everything arrives as a pull request | Human |

**C2 is held closed by a test, not by the default alone.** A default port is a
collision a session notices. A test command that deletes `./qmcp.db` — before
the run and again after it, by default, with no prompt — destroys another
session's *pending human gate queue*, and the destruction is silent,
permanent, and indistinguishable afterwards from nobody having asked for
anything. That is the empty-queue-reads-as-nothing-is-waiting failure the
monitoring-seam record is built to prevent, reached without any monitor being
involved. In qmcp, `tests/test_cli_test_command.py` goes red when
`--clean/--no-clean` is set back to `default=True`: the configured database is
deleted before the run, and the test sees it gone.

## Revision triggers

- C1 is settled: `REUSE.toml`, `LICENSES/` and `reuse-lint.yml` are added, and
  decision 3's exception is retired.
- C3's open part is fixed: a qmcp started with no flags neither binds a fixed
  port nor shares a cwd-relative database with another session. The
  monitoring-seam record's decision 4 then holds for every qmcp, not only for
  one started by `qmcp serve --port 0`.
- C7's open part is fixed: the HTTP app accepts the answer to a human gate
  only from a caller it has authenticated as a human, so the boundary stops
  depending on which tools an agent was handed.
- C4 is fixed: no `GET` persists a state change, and the seam record's second
  reason weakens to the ordinary one.
- The working tree lands: C5 and C8 close, and `pyproject.toml` becomes
  editable by an adoption change without collision.

## Amendments

None.
