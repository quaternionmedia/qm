# ADR-XXXX — QM Constitution Adoption Scope for qmcp

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-11 |
| **Pends on** | One outbound-licensing input the org has not settled for this project: which class of the outbound-licensing record qmcp falls into, §9's C1. `REUSE.toml` records MIT as the current state of qmcp's own code and prose and says it does not ratify it; qmcp carries no root `LICENSE` and no `license` key in `pyproject.toml`, so nothing a packager reads declares a grant. Every other disposition below is fixed regardless. |
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
cited: for C2, C3 and C7 at qmcp commit `a41f9a3`, and for C1, C4, C5, C6 and
C8 at qmcp commit `f677f93`. None is inferred from the shape of the code.

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

3. **The seed's workflows are copied verbatim** into `.github/workflows/`,
   `reuse-lint.yml` among them. The REUSE gate reads `REUSE.toml`, which
   records the licence each path carries now; it passes without settling C1,
   because it checks that every file declares a licence, not which one.

4. **`CLAUDE.md` is the seed's one-line import of `AGENTS.md`**, a regular
   file, so one edit to `AGENTS.md` keeps both current and no checkout needs
   symlink support. qmcp carries no `.github/copilot-instructions.md`, as the
   seed carries none.

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
- Cost accepted: qmcp is REUSE-compliant on a licence its `REUSE.toml` calls
  the current state rather than a decision, and declares none where a
  packager reads one, until C1 is settled.

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
| C1 | `REUSE.toml` declares MIT for `**`, CC0-1.0 for the copy-forward prose and Apache-2.0 for `.github/**` and `.vscode/**`, and `LICENSES/` holds the three texts; it says the MIT block records the current state and does not ratify it. No root `LICENSE`, and `pyproject.toml` has no `license` key | Outbound licensing §0 | Human — this record's `Pends on` |
| C2 | `qmcp test` deletes the configured database only when `--clean` is passed, and `--clean` defaults off (`qmcp/cli.py:1633`); without it the suite builds its own databases and leaves the configured one alone | Async contract §4 | Closed by qmcp#86 — see below |
| C3 | Closed: `qmcp serve --port 0` binds a port the system picks, writes a run-file to `~/.qmcp/run` (or `QMCP_RUN_DIR`), and states the same identity on `/health` (`qmcp/instance.py`; `qmcp/cli.py:873,893`); `cookbook dev` matches the database fingerprint of whatever answers its health URL and refuses a server over another database (`qmcp/cli.py:281,1229`). **Open:** the defaults are `port: int = 3141` (`qmcp/config.py:27`) and `database_url = "sqlite+aiosqlite:///./qmcp.db"` (`:31`), resolved against one process's cwd, so a server started with no flags binds a fixed port, and two sessions started in one checkout share one queue unless each sets `QMCP_DATABASE_URL` | Async contract §4 | Closed in part by qmcp#110; Human — the per-session default database and the default port |
| C4 | `GET /v1/human/requests/{id}` sets `status = EXPIRED` on a pending request past its expiry (`qmcp/server.py:498-507`), and `session_scope` commits on exit (`qmcp/db/engine.py:60`), so the read persists a terminal transition. The list endpoint leaves a pending request past its expiry out of the pending list and its stored status alone (`qmcp/server.py:450-466`), so the two agree on what is waiting and one of them writes | Monitoring seam, decision 1 | Human |
| C5 | Closed: `mcp` is the `mcp` extra in `pyproject.toml` (`mcp>=1.0.0,<2`), `tests/test_qmcp_mcp.py` skips through `pytest.importorskip` where it is not installed, and `tests.yml` installs every extra with `uv sync --all-extras`, so the suite the host runs collects it | Decision-record discipline §7 | Closed |
| C6 | Closed in part: `alembic/versions/` holds six migrations, and `qmcp db current`, `history`, `upgrade` and `stamp` run them. **Open:** startup still runs `create_all` (`qmcp/db/engine.py:44`), which creates a missing table and never alters one, and nothing at startup compares a database with the migrations' head, so a database older than the models is served until a column it lacks is read | House stack | Human — whether startup migrates, refuses, or warns |
| C7 | Closed: none of the twelve tools `qmcp_mcp.py` exposes answers a human request (qmcp#97), and `qmcp serve`, `cookbook serve` and `cookbook dev` bind `127.0.0.1` by default and warn when bound off it (`qmcp/config.py:19`; `qmcp/cli.py:727,841,1159`; qmcp#98, qmcp#101). **Open:** the answer is `POST /v1/human/responses` (`qmcp/server.py:521`), and no `Depends(`, no `CORSMiddleware`, no bearer scheme appears anywhere in the HTTP app, so any process on the machine — an agent's shell included — can answer a human gate through it; `qmcp/client/mcp_client.py:449` wraps that call | Human-in-the-loop is a boundary, not a convention | Closed in part by qmcp#97; Human — how the HTTP app tells a human's answer from an agent's |
| C8 | Closed: `qmcp/cookbook/` and `qmcp_mcp.py` are committed on `main`, and `git status --porcelain` in the clone prints nothing | Everything arrives as a pull request | Closed |

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

- C1 is settled: the licence class is chosen, `REUSE.toml`'s default block
  states it as a decision, and a root `LICENSE` and the `license` key in
  `pyproject.toml` declare it.
- C3's open part is fixed: a qmcp started with no flags neither binds a fixed
  port nor shares a cwd-relative database with another session. The
  monitoring-seam record's decision 4 then holds for every qmcp, not only for
  one started by `qmcp serve --port 0`.
- C7's open part is fixed: the HTTP app accepts the answer to a human gate
  only from a caller it has authenticated as a human, so the boundary stops
  depending on which tools an agent was handed.
- C4 is fixed: no `GET` persists a state change, and the seam record's second
  reason weakens to the ordinary one.
- C6's open part is decided: startup migrates, refuses, or warns on a
  database behind the migrations' head.

## Amendments

None.
