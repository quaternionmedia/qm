"""Which server is which, judged from its declaration and its own answer.

Offline: the operating system and the network are injected
(`records/DRAFT-monitoring-seam-and-instance-identity.md` decision 10), so no
test binds a port or reads this machine's run-files, except the one that runs
a real child through `run`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import instances  # noqa: E402


@pytest.fixture(autouse=True)
def no_registration(tmp_path, monkeypatch):
    """No test reads this machine's own registration."""
    monkeypatch.setenv("QM_REGISTERED", str(tmp_path / "none" / "registered.json"))


def declare(directory: Path, name: str, **fields) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps({"host": "127.0.0.1", "health": "/health", **fields}),
                    encoding="utf-8")
    return path


class Machine:
    """A machine whose processes, listeners and answers a test states."""

    def __init__(self, live=(), held=(), answers=None):
        self.live, self.held, self.answers = set(live), set(held), answers or {}
        self.asked: list[str] = []

    def world(self) -> instances.World:
        def fetch(url):
            self.asked.append(url)
            port = int(url.split(":")[2].split("/")[0])
            return self.answers.get(port, (0, None))
        return instances.World(alive=lambda pid: pid in self.live,
                               listening=lambda port: port in self.held, fetch=fetch)


def collect(run_dir: Path, machine: Machine, reserved=None) -> dict:
    return instances.collect([run_dir], machine.world(), reserved or {})


def states(document: dict) -> dict:
    return {row["repo"]: row["state"] for row in document["instances"]}


def test_a_run_file_whose_process_is_gone_is_stale_whatever_answers_its_port(tmp_path):
    """The case the record is written against: a previous server's run-file, and
    another process on its port. Mutation: check the port before the pid, and
    this reads as identified."""
    declare(tmp_path, "qmcp-1", repo="qmcp", pid=1, port=3141)
    machine = Machine(live={2}, held={3141}, answers={3141: (200, {"pid": 2, "port": 3141})})
    row = collect(tmp_path, machine)["instances"][0]
    assert row["state"] == "stale"
    assert "Another process answers its port" in row["why"]


def test_a_port_answering_as_the_declared_pid_is_identified(tmp_path):
    declare(tmp_path, "qmcp-7", repo="qmcp", pid=7, port=3141, started_at="t0")
    machine = Machine(live={7}, held={3141},
                      answers={3141: (200, {"pid": 7, "port": 3141, "started_at": "t0"})})
    assert states(collect(tmp_path, machine)) == {"qmcp": "identified"}


def test_a_port_answering_as_another_pid_is_a_mismatch(tmp_path):
    """Mutation: drop the pid comparison, and this reads as identified."""
    declare(tmp_path, "qmcp-7", repo="qmcp", pid=7, port=3141)
    machine = Machine(live={7}, held={3141}, answers={3141: (200, {"pid": 8, "port": 3141})})
    row = collect(tmp_path, machine)["instances"][0]
    assert row["state"] == "mismatch" and "pid 8" in row["why"]


def test_a_server_that_does_not_say_which_it_is_is_never_identified(tmp_path):
    declare(tmp_path, "dossier-9", repo="dossier", pid=9, port=1618)
    machine = Machine(live={9}, held={1618}, answers={1618: (200, {"status": "ok"})})
    assert states(collect(tmp_path, machine)) == {"dossier": "answering"}


def test_a_live_process_whose_port_is_shut_is_silent(tmp_path):
    declare(tmp_path, "joe-5", repo="joe", pid=5, port=18431)
    assert states(collect(tmp_path, Machine(live={5}))) == {"joe": "silent"}


def test_a_reserved_port_held_without_a_run_file_is_undeclared(tmp_path):
    """Decision 6's second fact. A port a live declaration names is not counted
    twice. Mutation: probe every reserved port, declared or not, and this fails."""
    declare(tmp_path, "qmcp-7", repo="qmcp", pid=7, port=3141)
    machine = Machine(live={7}, held={3141, 1414}, answers={3141: (200, {"pid": 7})})
    document = collect(tmp_path, machine, reserved={3141: "the harness", 1414: "the prose"})
    assert document["undeclared"] == [{"port": 1414, "reserved_for": "the prose"}]


def test_only_the_declared_health_path_is_ever_requested(tmp_path):
    """A read of qmcp's queue can write to it, so nothing but the health path is
    in reach."""
    declare(tmp_path, "qmcp-7", repo="qmcp", pid=7, port=3141)
    declare(tmp_path, "apothecary-3", repo="apothecary", pid=3, port=6283, health="/healthz")
    machine = Machine(live={3, 7}, held={3141, 6283},
                      answers={3141: (200, {"pid": 7}), 6283: (200, {})})
    collect(tmp_path, machine)
    assert sorted(machine.asked) == ["http://127.0.0.1:3141/health",
                                     "http://127.0.0.1:6283/healthz"]


def test_the_quiet_sentence_is_printed_only_when_it_is_earned(tmp_path):
    """Decision 7. Mutation: print it whenever there is no mismatch, and the
    stale case fails."""
    declare(tmp_path, "qmcp-7", repo="qmcp", pid=7, port=3141)
    quiet = Machine(live={7}, held={3141}, answers={3141: (200, {"pid": 7})})
    assert "Every declared server is identified" in instances.render(collect(tmp_path, quiet))
    declare(tmp_path, "qmcp-1", repo="qmcp", pid=1, port=3142)
    assert "Every declared server is identified" not in instances.render(collect(tmp_path, quiet))


def test_prune_removes_only_what_has_no_process_and_only_when_told(tmp_path):
    gone = declare(tmp_path, "qmcp-1", repo="qmcp", pid=1, port=3141)
    kept = declare(tmp_path, "qmcp-7", repo="qmcp", pid=7, port=3142)
    world = Machine(live={7}).world()
    assert instances.prune([tmp_path], world, yes=False) == [gone] and gone.exists()
    instances.prune([tmp_path], world, yes=True)
    assert not gone.exists() and kept.exists()


def test_the_document_is_refused_inside_a_repository():
    assert instances.inside_a_repository(CI_DIR / "anything.json")


def test_run_declares_the_server_while_it_lives_and_withdraws_it_after(tmp_path):
    """`{port}` is handed to the server, and the run-file goes when it does."""
    seen = tmp_path / "seen.txt"
    child = ("import pathlib, sys, time; "
             f"pathlib.Path({str(seen)!r}).write_text(' '.join(sys.argv[1:])); time.sleep(1)")
    code = instances.run("probe", [sys.executable, "-c", child, "--port", "{port}"],
                         port=4321, session="test", directory=tmp_path / "run")
    assert code == 0
    assert seen.read_text() == "--port 4321"
    assert list((tmp_path / "run").glob("*.json")) == []


@pytest.mark.parametrize("path", ["~/x", "C:/elsewhere/x"])
def test_a_path_outside_the_home_is_left_as_it_is_and_one_inside_starts_from_tilde(path):
    expanded = str(Path(path).expanduser()) if path.startswith("~") else path
    assert instances.tilde(expanded) == path.replace("\\", "/")


def test_a_port_named_when_looking_is_probed_and_reported_as_undeclared(tmp_path, monkeypatch, capsys):
    """A stack that writes no run-file is seen only where a person names its port.
    Mutation: drop `--port` from the probe set, and this fails."""
    monkeypatch.setattr(instances, "run_dirs", lambda: [tmp_path])
    monkeypatch.setattr(instances, "reserved_ports", lambda: {})
    world = Machine(held={8000}).world()
    monkeypatch.setattr(instances, "World", lambda: world)
    assert instances.main(["--port", "8000", "--json"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["undeclared"] == [{"port": 8000, "reserved_for": "named on the command line"}]


# --- which repositories this machine should be running

FAMILIES = {"core": ["qm", "qmcp", "codecartographer"], "irl": ["apothecary"]}
STARTS = {"qmcp": "uv run qm dashboard --start harness",
          "codecartographer": "uv run qm dashboard --start web",
          "apothecary": "uv run qm dashboard --start parts"}


def registered(**fields) -> dict:
    return {"name": "x", "families": [], "repos": [],
            "registered_at": "2026-10-30T00:00:00Z", **fields}


def test_a_name_nothing_resolves_is_refused_when_registering():
    with pytest.raises(ValueError, match="no family named nope"):
        instances.registration(["nope"], [], None, FAMILIES, {"qmcp"})
    with pytest.raises(ValueError, match="stranger: not in the roster"):
        instances.registration([], ["stranger"], None, FAMILIES, {"qmcp"})
    assert instances.registration(["core"], [], None, FAMILIES, set())["name"] == "core"
    assert instances.registration(["core"], ["qmcp"], None, FAMILIES, {"qmcp"})["name"] == "local"


def test_a_family_is_resolved_when_read_and_one_that_has_gone_is_named():
    members, gone = instances.expected(
        registered(families=["core", "renamed"], repos=["apothecary", "qm"]), FAMILIES)
    assert members == {"qm": "family core", "qmcp": "family core",
                       "codecartographer": "family core", "apothecary": "named"}
    assert gone == ["renamed"]


def test_a_registered_repository_this_corpus_starts_nothing_for_is_unjudged(tmp_path):
    """`qm` serves nothing, so a family registered whole would fail `--check`
    for as long as it is registered if `qm` read as missing. Mutation: judge
    every registered repository without a live run-file missing, and this
    fails."""
    declare(tmp_path, "qmcp-7", repo="qmcp", pid=7, port=3141)
    machine = Machine(live={7}, held={3141}, answers={3141: (200, {"pid": 7, "port": 3141})})
    document = instances.collect([tmp_path], machine.world(), {},
                                 registered(families=["core"]), FAMILIES, STARTS)
    judged = {row["repo"]: row["state"] for row in document["registered"]["repositories"]}
    assert judged == {"qm": "unjudged", "qmcp": "up", "codecartographer": "missing"}
    assert (document["counts"]["missing"], document["counts"]["unjudged"]) == (1, 1)


def test_a_registered_server_nothing_declares_fails_the_check(tmp_path, monkeypatch, capsys):
    """Mutation: leave `missing` out of PROBLEMS, and `--check` passes."""
    path = tmp_path / "registered.json"
    path.write_text(json.dumps(registered(repos=["codecartographer"])), encoding="utf-8")
    monkeypatch.setenv("QM_REGISTERED", str(path))
    monkeypatch.setattr(instances, "run_dirs", lambda: [tmp_path / "run"])
    monkeypatch.setattr(instances, "reserved_ports", lambda: {})
    monkeypatch.setattr(instances, "servers", lambda: STARTS)
    world = Machine().world()
    monkeypatch.setattr(instances, "World", lambda: world)
    assert instances.main(["--check"]) == 1
    out = capsys.readouterr().out
    assert "missing" in out and "uv run qm dashboard --start web" in out


def test_a_server_outside_the_registration_is_reported_and_is_no_problem(tmp_path):
    declare(tmp_path, "apothecary-9", repo="apothecary", pid=9, port=6283)
    machine = Machine(live={9}, held={6283}, answers={6283: (200, {"pid": 9, "port": 6283})})
    document = instances.collect([tmp_path], machine.world(), {},
                                 registered(repos=["qm"]), FAMILIES, STARTS)
    assert document["instances"][0]["registered"] is False
    assert not any(document["counts"][k] for k in instances.PROBLEMS)
    assert "Running and not registered: apothecary." in instances.render(document)


def test_register_writes_one_machine_s_claim_and_clear_removes_it(tmp_path, monkeypatch, capsys):
    path = tmp_path / "registered.json"
    monkeypatch.setenv("QM_REGISTERED", str(path))
    monkeypatch.setattr(instances, "families", lambda: FAMILIES)
    monkeypatch.setattr(instances, "roster_names", lambda: {"apothecary"})
    assert instances.main(["register", "--family", "core", "--repo", "apothecary",
                           "--name", "bench"]) == 0
    written = json.loads(path.read_text(encoding="utf-8"))
    assert (written["name"], written["families"], written["repos"]) == (
        "bench", ["core"], ["apothecary"])
    assert instances.main(["register"]) == 0
    assert "4 repositories: qm, qmcp, codecartographer, apothecary" in capsys.readouterr().out
    assert instances.main(["register", "--clear"]) == 0
    assert not path.exists()


def test_a_registration_inside_a_repository_is_refused(monkeypatch):
    """Decision 2: what one machine runs is never committed."""
    inside = CI_DIR / "registered.json"
    monkeypatch.setenv("QM_REGISTERED", str(inside))
    monkeypatch.setattr(instances, "families", lambda: FAMILIES)
    assert instances.main(["register", "--family", "core"]) == 2
    assert not inside.exists()


def test_a_process_start_time_is_its_own_and_stays_put():
    import os
    here = instances.created(os.getpid())
    assert here is not None and here == instances.created(os.getpid())
    assert instances.created(0) is None


def test_a_process_that_exited_is_not_alive_before_its_parent_collects_it():
    import subprocess
    import time
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    try:
        deadline = time.monotonic() + 10
        while instances.alive(child.pid) and time.monotonic() < deadline:
            time.sleep(0.05)
        assert not instances.alive(child.pid)
    finally:
        child.wait()
