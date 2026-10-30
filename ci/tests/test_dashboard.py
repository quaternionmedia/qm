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


def surface(port: int, *command: str, declares_itself: bool = False) -> dashboard.Surface:
    return dashboard.Surface(name="probe", repo="probe", role="a test's child", port=port,
                             constant="", command=(sys.executable, "-c", *command),
                             detachable=True, declares_itself=declares_itself)


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


def test_start_registered_refuses_when_nothing_is_registered(machine, capsys):
    assert dashboard.start_registered() == 1
    assert "nothing is registered" in capsys.readouterr().out
