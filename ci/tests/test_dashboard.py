"""`qm dashboard` says started only of a server that answers, stops only what it
started, and leaves no run-file behind the process it ended.

Each test runs a real child, a few lines of Python that exits, binds a port or
sleeps, in place of a surface's server: `RUNNER` is emptied so the command is
the child itself rather than `uv run` in a sibling repository. Every port is a
free one, and every file the dashboard writes goes under the test's own
directory.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import dashboard  # noqa: E402
import instances  # noqa: E402

EXITS = "import sys; print('no such option: --demo'); sys.exit(2)"
SLEEPS = "import time; time.sleep(60)"
# Binds the port it is given and declares itself in the run directory it is
# given, as qmcp does, then sleeps until it is ended outright.
SERVES = ("import json, os, pathlib, socket, sys, time\n"
          "s = socket.socket(); s.bind(('127.0.0.1', int(sys.argv[1]))); s.listen()\n"
          "d = pathlib.Path(sys.argv[2]); d.mkdir(parents=True, exist_ok=True)\n"
          "(d / f'qmcp-{os.getpid()}.json').write_text(json.dumps("
          "{'pid': os.getpid(), 'port': int(sys.argv[1])}))\n"
          "time.sleep(60)\n")


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.fixture
def machine(tmp_path, monkeypatch):
    """The dashboard's state, its logs and both run directories, all under
    tmp_path, and surfaces that run a child directly."""
    monkeypatch.setattr(dashboard, "STATE", tmp_path / "dashboard.json")
    monkeypatch.setattr(dashboard, "RUNNER", ())
    monkeypatch.setenv("QM_RUN_DIR", str(tmp_path / "run"))
    monkeypatch.setenv("QMCP_RUN_DIR", str(tmp_path / "qmcp-run"))
    monkeypatch.setenv("QM_REGISTERED", str(tmp_path / "registered.json"))
    children: list[int] = []
    yield tmp_path, children
    for pid in children:
        if instances.alive(pid):
            instances.stop_tree(pid)


def surface(port: int, *command: str, declares_itself: bool = False,
            health: str = "/health") -> dashboard.Surface:
    return dashboard.Surface(name="probe", repo="probe", role="a test's child", port=port,
                             constant="", command=(sys.executable, "-c", *command),
                             detachable=True, declares_itself=declares_itself,
                             health=health)


def run_files(tmp_path: Path) -> list[Path]:
    return sorted([*tmp_path.glob("run/*.json"), *tmp_path.glob("qmcp-run/*.json")])


def test_a_server_that_exits_before_its_port_answers_is_not_called_started(machine):
    """What happened on 2026-10-29: apothecary's `serve` had no `--demo`, the
    command exited, and the dashboard had printed its pid. Mutation: return
    success straight after `Popen`, without waiting, and this fails."""
    tmp_path, _ = machine
    ok, detail = dashboard.start(surface(free_port(), EXITS), tmp_path, wait=20)
    assert ok is False
    assert "exited with status 2" in detail and "no such option: --demo" in detail
    assert dashboard.running() == {}
    assert run_files(tmp_path) == []


def test_a_server_whose_port_never_answers_is_reported_and_kept_stoppable(machine):
    tmp_path, children = machine
    ok, detail = dashboard.start(surface(free_port(), SLEEPS), tmp_path, wait=1)
    children.append(dashboard.running()["probe"]["pid"])
    assert ok is False
    assert "did not answer within 1s" in detail and "--stop probe" in detail
    assert dashboard.stop("probe")[0] is True


def test_a_started_server_is_declared_with_its_own_health_path(machine):
    """`qm instances` asks only the declared path, and joe answers on
    `/api/health`. Mutation: drop `health` from the declaration in `start`, and
    the run-file names `/health`, where joe answers nothing."""
    tmp_path, children = machine
    dashboard.start(surface(free_port(), SLEEPS, health="/api/health"), tmp_path, wait=0.5)
    children.append(dashboard.running()["probe"]["pid"])
    [declared] = run_files(tmp_path)
    assert json.loads(declared.read_text(encoding="utf-8"))["health"] == "/api/health"
    assert dashboard.stop("probe")[0] is True


def test_stop_withdraws_the_run_file_the_server_could_not(machine):
    """A stop ends the tree outright, so the server's own cleanup never runs and
    its run-file outlives it. Mutation: drop the sweep of the freed port from
    `forget`, and the server's own run-file is left."""
    tmp_path, children = machine
    port = free_port()
    ok, detail = dashboard.start(
        surface(port, SERVES, str(port), str(tmp_path / "qmcp-run"), declares_itself=True),
        tmp_path, wait=20)
    children.append(dashboard.running()["probe"]["pid"])
    assert ok is True, detail
    assert len(run_files(tmp_path)) == 1

    ok, detail = dashboard.stop("probe")
    assert ok is True, detail
    assert "1 run-file(s) withdrawn" in detail
    assert run_files(tmp_path) == []
    assert not dashboard.listening(port)


def test_a_pid_that_is_now_another_process_is_never_stopped(machine):
    """A pid recorded before a restart can be handed to a stranger. Mutation:
    drop the start-time comparison, and the stranger is ended."""
    tmp_path, children = machine
    stranger = subprocess.Popen([sys.executable, "-c", SLEEPS])
    children.append(stranger.pid)
    dashboard._remember({"probe": {"pid": stranger.pid, "port": free_port(),
                                   "created": (instances.created(stranger.pid) or 0) + 1}})
    ok, detail = dashboard.stop("probe")
    assert ok is False and "another process" in detail
    assert instances.alive(stranger.pid)
    assert dashboard.running() == {}


def test_a_server_already_gone_is_forgotten_with_its_run_files(machine):
    tmp_path, _ = machine
    gone = subprocess.Popen([sys.executable, "-c", "pass"])
    gone.wait()
    port = free_port()
    instances.declare("probe", gone.pid, port, ["x"], directory=tmp_path / "run")
    dashboard._remember({"probe": {"pid": gone.pid, "port": port}})
    ok, detail = dashboard.stop("probe")
    assert ok is True and "already exited" in detail and "1 run-file(s)" in detail
    assert run_files(tmp_path) == [] and dashboard.running() == {}


def test_start_registered_starts_the_registered_surfaces_and_no_others(machine, monkeypatch):
    """Mutation: start every surface, registered or not, and this fails."""
    tmp_path, _ = machine
    (tmp_path / "registered.json").write_text(json.dumps(
        {"name": "local", "families": [], "repos": ["qmcp", "apothecary", "vox"],
         "registered_at": "2026-10-30T00:00:00Z"}), encoding="utf-8")
    started = []
    monkeypatch.setattr(dashboard, "repo_of", lambda s: tmp_path)
    monkeypatch.setattr(dashboard, "listening", lambda port: port == 3141)
    monkeypatch.setattr(dashboard, "start",
                        lambda s, repo, wait: (started.append(s.name), (True, "up"))[1])
    assert dashboard.start_registered() == 0
    assert started == ["parts"], "the harness was already up; only apothecary's surface was not"


def test_start_registered_names_who_starts_a_stack_and_starts_none_of_it(machine, monkeypatch,
                                                                        capsys):
    """alfred's editor is a container stack its owner session starts for every
    other. Mutation: let an owner-started surface fall through to the terminal
    line, or to `start`, and this fails."""
    tmp_path, _ = machine
    (tmp_path / "registered.json").write_text(json.dumps(
        {"name": "local", "families": [], "repos": ["alfred"],
         "registered_at": "2026-10-30T00:00:00Z"}), encoding="utf-8")
    started = []
    monkeypatch.setattr(dashboard, "repo_of", lambda s: tmp_path)
    monkeypatch.setattr(dashboard, "listening", lambda port: False)
    monkeypatch.setattr(dashboard, "start",
                        lambda s, repo, wait: (started.append(s.name), (True, "up"))[1])
    assert dashboard.start_registered() == 0
    out = capsys.readouterr().out
    assert started == []
    assert "editor: cd alfred && ./al family up" in out
    assert f"({dashboard.BY_NAME['editor'].note})" in out
    assert "draws in a terminal" not in out and "uv run" not in out


def test_start_registered_refuses_when_nothing_is_registered(machine, capsys):
    assert dashboard.start_registered() == 1
    assert "nothing is registered" in capsys.readouterr().out


# Writes the directory it runs in beside the port it then binds.
SERVES_AND_SAYS_WHERE = ("import os, pathlib, socket, sys, time\n"
                         "pathlib.Path(sys.argv[2]).write_text(os.getcwd())\n"
                         "s = socket.socket(); s.bind(('127.0.0.1', int(sys.argv[1]))); s.listen()\n"
                         "time.sleep(60)\n")


def project(where: Path) -> Path:
    where.mkdir(parents=True, exist_ok=True)
    (where / "pyproject.toml").write_text("[project]\nname = 'probe'\n", encoding="utf-8")
    return where


def one_surface(monkeypatch, probe: dashboard.Surface, beside: Path) -> None:
    monkeypatch.setattr(dashboard, "SURFACES", (probe,))
    monkeypatch.setattr(dashboard, "BY_NAME", {probe.name: probe})
    monkeypatch.setattr(dashboard, "repo_of", lambda s: beside)


def test_a_surface_is_started_from_the_checkout_named_for_it(machine, monkeypatch, capsys):
    """Mutation: take the clone beside this one whatever `--from` says, in
    `main`, and the child runs there. Mutation: drop the checkout from the
    report's line, and nothing says which tree is being served."""
    tmp_path, children = machine
    beside, worktree = project(tmp_path / "beside"), project(tmp_path / "worktree")
    port, said = free_port(), tmp_path / "cwd.txt"
    one_surface(monkeypatch, surface(port, SERVES_AND_SAYS_WHERE, str(port), str(said)), beside)
    assert dashboard.main(["--start", "probe", "--from", f"probe={worktree}", "--wait", "20"]) == 0
    record = dashboard.running()["probe"]
    children.append(record["pid"])
    assert Path(said.read_text()).resolve() == worktree.resolve()
    assert Path(record["repo"]).resolve() == worktree.resolve()
    line = next(row for row in capsys.readouterr().out.splitlines() if row.startswith("probe "))
    assert f"started here, pid {record['pid']}, from " in line and "worktree" in line


def test_a_surface_started_from_the_clone_beside_this_one_names_no_checkout(machine, monkeypatch,
                                                                            capsys):
    """Mutation: name the checkout on every started surface, and the ordinary
    start carries a path nobody asked about."""
    tmp_path, children = machine
    beside = project(tmp_path / "beside")
    port, said = free_port(), tmp_path / "cwd.txt"
    one_surface(monkeypatch, surface(port, SERVES_AND_SAYS_WHERE, str(port), str(said)), beside)
    assert dashboard.main(["--start", "probe", "--wait", "20"]) == 0
    pid = dashboard.running()["probe"]["pid"]
    children.append(pid)
    line = next(row for row in capsys.readouterr().out.splitlines() if row.startswith("probe "))
    assert line.rstrip().endswith(f"(started here, pid {pid})")


def test_start_registered_takes_the_named_checkout(machine, monkeypatch):
    """Mutation: leave `sources` out of `start_registered`, and the registered
    surface starts from the clone beside this one."""
    tmp_path, _ = machine
    (tmp_path / "registered.json").write_text(json.dumps(
        {"name": "local", "families": [], "repos": ["apothecary"],
         "registered_at": "2026-10-30T00:00:00Z"}), encoding="utf-8")
    started = []
    monkeypatch.setattr(dashboard, "repo_of", lambda s: tmp_path)
    monkeypatch.setattr(dashboard, "listening", lambda port: False)
    monkeypatch.setattr(dashboard, "start",
                        lambda s, repo, wait: (started.append((s.name, repo)), (True, "up"))[1])
    worktree = project(tmp_path / "worktree")
    assert dashboard.start_registered(sources={"parts": worktree}) == 0
    assert started == [("parts", worktree)]


def test_a_from_that_names_no_surface_or_no_project_is_refused(machine):
    """Mutation: drop the `pyproject.toml` test from `checkouts`, and a
    mistyped path is a directory the command is run in. Mutation: drop the
    name test, and a mistyped surface is silently never started."""
    tmp_path, _ = machine
    with pytest.raises(ValueError, match="is not a surface"):
        dashboard.checkouts([f"nosuch={project(tmp_path / 'p')}"])
    (tmp_path / "empty").mkdir()
    with pytest.raises(ValueError, match="holds no pyproject.toml"):
        dashboard.checkouts([f"web={tmp_path / 'empty'}"])
    with pytest.raises(ValueError, match="holds no pyproject.toml"):
        dashboard.checkouts(["web"])
    with pytest.raises(SystemExit):
        dashboard.main(["--start", "web", "--from", f"web={tmp_path / 'empty'}"])


def test_the_report_says_started_here_only_of_the_process_it_started(machine, monkeypatch,
                                                                     capsys):
    """A record outlives a process ended outside `--stop`, and another process
    may take its port. Mutation: say `started here` of any recorded name, in
    `report` or in `--json`, and a stranger on the port is called this
    command's."""
    tmp_path, _ = machine
    gone = subprocess.Popen([sys.executable, "-c", "pass"])
    gone.wait()
    port = free_port()
    one_surface(monkeypatch, surface(port, SLEEPS), project(tmp_path / "beside"))
    (tmp_path / "dashboard.json").write_text(json.dumps(
        {"probe": {"pid": gone.pid, "port": port, "repo": str(tmp_path / "beside"),
                   "created": 1}}), encoding="utf-8")
    with socket.socket() as stranger:
        stranger.bind(("127.0.0.1", port))
        stranger.listen()
        assert dashboard.report() == 0
        line = next(row for row in capsys.readouterr().out.splitlines()
                    if row.startswith("probe "))
        assert "something is listening" in line and "started here" not in line
        assert dashboard.main(["--json"]) == 0
        answer = json.loads(capsys.readouterr().out)["probe"]
        assert answer["listening"] is True
        assert answer["started_here"] is False and answer["started_from"] is None


def test_a_fresh_clone_is_refused_with_what_to_run_in_it(machine, monkeypatch):
    """A clone nobody has synced has no environment for `uv run --no-sync` to
    run in. Mutation: drop the check from `start`, and the server is launched
    into nothing and reported only by its log."""
    tmp_path, _ = machine
    monkeypatch.setattr(dashboard, "RUNNER", ("uv", "run", "--no-sync"))
    ok, detail = dashboard.start(surface(free_port(), EXITS), tmp_path, wait=5)
    assert ok is False
    assert "has no environment yet" in detail and "`uv sync`" in detail
    assert dashboard.running() == {} and run_files(tmp_path) == []


def test_the_report_says_where_to_look_and_what_a_fresh_clone_runs_first(machine, monkeypatch,
                                                                        capsys):
    """A person who opens an application cold is not told where its answer is,
    and one with a fresh clone is not told to sync it. Mutation: drop either
    line from `report`, or probe the terminal front end's port as if it were
    the front end, and this fails."""
    tmp_path, _ = machine
    monkeypatch.setattr(dashboard, "repo_of", lambda s: tmp_path)
    monkeypatch.setattr(dashboard, "listening", lambda port: port == 1414)
    assert dashboard.report() == 0
    out = capsys.readouterr().out
    assert f"({dashboard.BY_NAME['prose'].look})" in out
    assert "first, once, in qmcp: uv sync" in out
    assert "first, once, in codecartographer: uv sync, then in web/" in out
    terminal = next(line for line in out.splitlines() if line.startswith("terminal "))
    assert "a terminal application" in terminal and "nothing listening" not in terminal
