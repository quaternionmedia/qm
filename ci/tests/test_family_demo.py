"""The family demo's rules, checked without starting anything.

Hermetic: no port is bound, no member is cloned, no browser is launched. What
is tested is the part that decides -- whether the roster can run, which port is
whose, what the contract hands a member, how results combine, what the page and
the manifest name -- because the part that starts processes is exercised by
running the demo, and a test that needed five repositories and a browser would
skip everywhere CI runs.

Each refusal is shown firing on a plan broken on purpose. A rule only ever seen
green says what its author meant, not what it checks.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import cli  # noqa: E402
import family_demo  # noqa: E402
import family_stage  # noqa: E402
import roster  # noqa: E402

CORE = ("ShowRunner", "ShowStopper", "carlos", "joe", "leo")


def committed_plan() -> dict:
    return family_demo.load_plan()


def rostered() -> set[str]:
    return set(family_demo.index_roster(roster.load()))


def problems(plan: dict) -> list[str]:
    return family_demo.check_plan(plan, rostered())


def member(plan: dict, name: str) -> dict:
    return next(m for m in plan["members"] if m["name"] == name)


# --- the committed roster --------------------------------------------------

def test_the_committed_plan_can_run_as_written():
    assert problems(committed_plan()) == []


def test_every_performing_family_member_is_placed():
    """A family member the demo does not place is printed as unplaced; today there are none."""
    families = json.loads((CI_DIR.parent / "families.json").read_text(encoding="utf-8"))
    assert family_demo.unplaced(committed_plan(), families) == []


def test_a_member_missing_from_the_plan_is_reported_not_dropped():
    plan = committed_plan()
    plan["members"] = [m for m in plan["members"] if m["name"] != "wolf"]
    families = {"families": [{"name": "instruments", "members": ["wolf", "carlos"]},
                             {"name": "core", "members": ["qm"]}]}
    assert family_demo.unplaced(plan, families) == ["wolf"]


def test_the_cli_routes_to_the_demo():
    assert cli.ROUTES["family-demo"][0] == "family_demo"


def test_only_the_core_phase_runs_and_every_core_member_names_its_branch():
    plan = committed_plan()
    names = [m["name"] for m in family_demo.running(plan)]
    assert names == ["ShowRunner", "ShowStopper", "carlos", "joe", "leo"]
    for entry in family_demo.running(plan):
        assert entry["branch"] and entry["stacks_on"], entry["name"]


def test_no_member_s_check_is_written_here():
    """The member owns its selectors: nothing in the demo names one.

    A selector the demo once held for each member, read straight off the old
    probe module, must appear nowhere in the harness or the probe module now.
    """
    held = ["capture-file-list", "Show Control Dashboard", "path.cable",
            "setlist__header__search__input", "StopwatchApp"]
    for source in (CI_DIR / "family_demo.py", CI_DIR / "family_demo_probes.py"):
        text = source.read_text(encoding="utf-8")
        for selector in held:
            assert selector not in text, f"{source.name} names {selector!r}"


# --- refusals, each seen firing ---------------------------------------------

def test_a_port_outside_the_range_is_refused():
    plan = committed_plan()
    member(plan, "leo")["ports"]["web"] = plan["ports"]["last"] + 1
    assert any("outside" in p and p.startswith("leo") for p in problems(plan))


def test_two_members_on_one_port_is_refused():
    plan = committed_plan()
    member(plan, "leo")["ports"]["web"] = member(plan, "carlos")["ports"]["http"]
    assert any("already carlos's" in p for p in problems(plan))


def test_a_member_the_roster_does_not_carry_is_refused():
    plan = committed_plan()
    member(plan, "leo")["name"] = "not-a-repository"
    assert any(p.startswith("not-a-repository: not in ci/workspace.yaml") for p in problems(plan))


def test_a_running_member_without_a_branch_is_refused():
    plan = committed_plan()
    del member(plan, "leo")["branch"]
    assert "leo: runs, but names no branch" in problems(plan)


def test_a_served_port_must_be_one_of_the_member_s_ports():
    plan = committed_plan()
    member(plan, "joe")["serves"] = "nowhere"
    assert "joe: serves 'nowhere', which is not one of its ports" in problems(plan)


def test_the_served_port_cannot_be_reserved_unbound():
    plan = committed_plan()
    member(plan, "joe")["unbound"] = ["web"]
    assert "joe: the port it serves cannot also be unbound" in problems(plan)


def test_state_in_a_checkout_cannot_reach_outside_it():
    for path in ("../elsewhere", "/etc", "C:/Windows", ""):
        plan = committed_plan()
        member(plan, "joe")["state_in_checkout"] = [path]
        assert any("must be a path inside the checkout" in p for p in problems(plan)), path


@pytest.mark.parametrize("command, dropped", [("serve", "{port}"), ("serve", "{state}"),
                                              ("check", "{url}"), ("check", "{shots}")])
def test_a_contract_that_does_not_pass_what_was_reserved_is_refused(command, dropped):
    plan = committed_plan()
    argv = plan["contract"][command]
    argv[argv.index(dropped)] = "fixed"
    assert f"contract: {command} does not pass {dropped}" in problems(plan)


def test_a_contract_without_a_stub_marker_is_refused():
    plan = committed_plan()
    del plan["contract"]["not_implemented"]
    assert any(p.startswith("contract: not_implemented") for p in problems(plan))


def test_a_member_may_not_pass_the_contract_s_own_placeholders():
    plan = committed_plan()
    member(plan, "leo")["serve_args"] = ["--out", "{shots}"]
    assert "leo: {shots} is the contract's to pass, not a member's" in problems(plan)
    plan = committed_plan()
    member(plan, "leo")["url"] = "{url}"
    assert "leo: {url} is the contract's to pass, not a member's" in problems(plan)


def test_a_placeholder_naming_an_undeclared_port_is_refused():
    plan = committed_plan()
    member(plan, "joe")["serve_args"] = ["--api-port", "{port:nowhere}"]
    assert "joe: {port:nowhere} names no declared port" in problems(plan)


def test_an_identity_missing_a_field_is_refused():
    plan = committed_plan()
    del member(plan, "carlos")["identity"]["state"]
    assert "carlos: identity needs a url, a port field and a state field" in problems(plan)


def test_a_phase_that_does_not_run_must_say_what_its_members_need():
    plan = committed_plan()
    member(plan, "wolf")["needs"] = []
    assert any(p.startswith("wolf: a phase that does not run") for p in problems(plan))


def test_a_ref_override_needs_a_member_and_a_ref():
    assert family_demo.parse_refs(["leo=origin/setlist"]) == {"leo": "origin/setlist"}
    for bad in ("leo", "=origin/main", "leo="):
        with pytest.raises(family_demo.PlanError):
            family_demo.parse_refs([bad])


# --- what the contract hands a member ---------------------------------------

def context_for(name: str, tmp_path: Path) -> tuple[dict, dict, dict]:
    plan = committed_plan()
    entry = member(plan, name)
    context = family_demo.contract_context(entry, plan, "/c/checkout", tmp_path / "state",
                                           tmp_path / "shots", "t1")
    return plan, entry, context


def test_serve_is_the_entry_then_the_contract_then_the_member_s_own_flags(tmp_path):
    plan, joe, context = context_for("joe", tmp_path)
    argv = family_demo.serve_argv(joe, plan, context)
    assert argv[:6] == ["uv", "run", "--no-sync", "--project", "/c/checkout", "joe"]
    assert argv[6:13] == ["serve", "--host", "127.0.0.1", "--port", "18430",
                          "--state", (tmp_path / "state").as_posix()]
    assert argv[13:] == ["--api-port", "18431", "--qmcp-url", "http://127.0.0.1:18432"]


def test_check_is_the_entry_then_the_contract_and_nothing_of_the_member_s(tmp_path):
    plan, carlos, context = context_for("carlos", tmp_path)
    argv = family_demo.check_argv(carlos, plan, context)
    assert argv[6:] == ["check", "--url", "http://127.0.0.1:18420/rack",
                        "--shots", (tmp_path / "shots").as_posix()]


def test_placeholders_expand_and_an_unknown_or_absent_one_raises():
    context = {"ports": {"web": 18440}, "token": "t1", "checkout": "/c", "state": "/s"}
    assert family_demo.expand(["--port", "{port:web}", "{state}/x-{token}"], context) == [
        "--port", "18440", "/s/x-t1"]
    for text in ("{port:api}", "{home}", "{url}"):
        with pytest.raises(family_demo.PlanError):
            family_demo.expand(text, context)


# --- results are combined without coercion -----------------------------------

def own(result, stub=False):
    return {"check": "contract check", "owner": "member", "result": result, "stub": stub}


def demo(result):
    return {"check": "ports-held-by-this-run", "owner": "demo", "result": result}


def test_a_check_s_exit_status_is_read_as_the_contract_says():
    assert family_demo.check_result(0, "", "not implemented") == ("pass", False)
    assert family_demo.check_result(1, "", "not implemented") == ("fail", False)
    assert family_demo.check_result(3, "nothing answers", "not implemented") == ("unknown", False)
    assert family_demo.check_result(2, "usage", "not implemented") == ("unknown", False)
    assert family_demo.check_result(None, "", "not implemented") == ("unknown", False)


def test_a_stub_is_not_implemented_and_never_a_pass_or_a_fail():
    assert family_demo.check_result(3, "check: not implemented", "not implemented") == (
        "unknown", True)
    # A stub that exits 0 is a pass by the contract's own words: the contract
    # is what forbids it, and the result does not paper over it.
    assert family_demo.check_result(0, "not implemented", "not implemented") == ("pass", False)


def test_unknown_is_never_folded_into_fail():
    assert family_demo.member_result([own("unknown")], "pass") == "unknown"
    assert family_demo.member_result([own("pass"), demo("unknown")], "pass") == "unknown"
    assert family_demo.member_result([own("fail"), demo("unknown")], "pass") == "fail"


def test_isolation_counts_and_cannot_stand_in_for_the_member_s_own_check():
    assert family_demo.member_result([own("pass"), demo("fail")], "pass") == "fail"
    assert family_demo.member_result([own("pass"), demo("pass")], "pass") == "pass"
    assert family_demo.member_result([demo("pass")], "pass") == "unknown"


def test_a_member_that_never_got_to_its_check_is_unknown_unless_seen_not_to_start():
    assert family_demo.member_result([own("unknown")], "unknown") == "unknown"
    assert family_demo.member_result([own("unknown")], "fail") == "fail"


def test_the_exit_status_separates_fail_from_unknown():
    assert family_demo.exit_status(["pass", "pass"]) == 0
    assert family_demo.exit_status(["pass", "fail", "unknown"]) == 1
    assert family_demo.exit_status(["pass", "unknown"]) == 3
    assert family_demo.exit_status([]) == 3  # nothing ran is not a pass


def test_the_last_line_of_a_check_is_read_without_its_colours():
    text = "collected 1 item\n\x1b[32m===== 1 passed\x1b[0m in 2s =====\n\n"
    assert family_demo.last_line(text) == "1 passed in 2s"


# --- the branch a member runs ------------------------------------------------

def make_repo(path: Path) -> Path:
    def run(*args):
        subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True)
    path.mkdir()
    run("init", "-q", "-b", "main")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "a")
    run("branch", "active")
    run("checkout", "-q", "-b", "contract")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "b")
    run("checkout", "-q", "main")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "c")
    run("branch", "elsewhere")
    return path


def test_a_branch_is_found_locally_and_its_stacking_is_measured(tmp_path):
    repo = make_repo(tmp_path / "member")
    ref, commit = family_demo.resolve_commit(repo, "contract", None)
    assert ref == "contract"
    assert family_demo.stacked(repo, "active", commit)["contains"] is True
    assert family_demo.stacked(repo, "elsewhere", commit)["contains"] is False
    assert family_demo.stacked(repo, "missing", commit)["contains"] == "unknown"
    with pytest.raises(family_demo.PlanError):
        family_demo.resolve_commit(repo, "missing", None)


def test_an_install_is_reused_only_while_what_it_made_is_still_there(tmp_path):
    repo = make_repo(tmp_path / "member")
    (repo / ".venv").mkdir()
    entry = {"name": "m", "install": [[sys.executable, "-c", "pass"]]}
    logs, stamp = tmp_path / "logs", tmp_path / "installed" / "m.json"
    logs.mkdir()
    first = family_demo.install(entry, repo, logs, stamp, fresh=False)
    assert first["result"] == "pass" and first["made"] == [".venv"] and not first["reused"]
    assert family_demo.install(entry, repo, logs, stamp, fresh=False)["reused"] is True
    (repo / ".venv").rmdir()
    assert family_demo.install(entry, repo, logs, stamp, fresh=False)["reused"] is False


def test_emptying_state_never_leaves_this_run_s_own_clone(tmp_path):
    work = tmp_path / "work"
    clone = work / "checkouts" / "joe"
    (clone / "Data" / "Audio").mkdir(parents=True)
    (clone / "Data" / "Audio" / "take.wav").write_bytes(b"x")
    assert family_demo.empty_state_in_checkout(clone, work, ["Data"]) == ["Data"]
    assert not (clone / "Data").exists()
    elsewhere = tmp_path / "roster-clone"
    (elsewhere / "Data").mkdir(parents=True)
    with pytest.raises(family_demo.PlanError):
        family_demo.empty_state_in_checkout(elsewhere, work, ["Data"])
    assert (elsewhere / "Data").is_dir()
    with pytest.raises(family_demo.PlanError):
        family_demo.empty_state_in_checkout(clone, work, ["../../../roster-clone/Data"])
    assert (elsewhere / "Data").is_dir()


# --- the machine readings ------------------------------------------------------

NETSTAT = """
  Proto  Local Address          Foreign Address        State           PID
  TCP    127.0.0.1:18440        0.0.0.0:0              LISTENING       22548
  TCP    127.0.0.1:59245        127.0.0.1:18440        ESTABLISHED     900
  TCP    [::1]:18431            [::]:0                 LISTENING       31
  TCP    127.0.0.1:59248        127.0.0.1:18440        TIME_WAIT       0
"""


def test_netstat_rows_are_read_with_ipv6_and_states():
    rows = family_demo.parse_netstat(NETSTAT)
    assert (("127.0.0.1", 18440), ("0.0.0.0", 0), "LISTEN", 22548) in rows
    assert (("::1", 18431), ("::", 0), "LISTEN", 31) in rows
    assert (("127.0.0.1", 59245), ("127.0.0.1", 18440), "ESTABLISHED", 900) in rows
    assert len(rows) == 4


def test_ss_rows_are_read():
    text = ('LISTEN 0 511 127.0.0.1:18440 0.0.0.0:* users:(("node",pid=77,fd=20))\n'
            'ESTAB 0 0 127.0.0.1:5000 127.0.0.1:18400 users:(("python",pid=78,fd=3))\n')
    rows = family_demo.parse_ss(text)
    assert rows == [(("127.0.0.1", 18440), ("0.0.0.0", 0), "LISTEN", 77),
                    (("127.0.0.1", 5000), ("127.0.0.1", 18400), "ESTAB", 78)]


def test_descendants_follow_the_tree_and_nothing_else():
    table = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (9, 0), 5: (5, 0)}
    assert family_demo.descendants(1, table) == {1, 2, 3}
    assert family_demo.descendants(5, table) == {5}


def test_binds_are_listeners_and_udp_sockets_not_connections():
    text = NETSTAT + "  UDP    0.0.0.0:53000          *:*                                    4242\n"
    rows = family_demo.parse_netstat_binds(text)
    assert ("TCP", ("127.0.0.1", 18440), 22548) in rows
    assert ("UDP", ("0.0.0.0", 53000), 4242) in rows
    assert all(pid != 900 for _proto, _local, pid in rows)  # an ESTABLISHED socket is not a bind


def test_the_process_table_keeps_program_names():
    table = family_demo.parse_process_table("10|4|2048|node.exe\n11|10|1024|esbuild.exe\nnoise\n")
    assert table == {10: (4, 2048, "node.exe"), 11: (10, 1024, "esbuild.exe")}
    assert family_demo.descendants(10, table) == {10, 11}


def test_a_member_s_ready_time_runs_from_its_first_start_to_its_last_answer():
    def process(started, ready):
        built = family_demo.Running(member="m", id="p", argv=[], cwd="", env={},
                                    ready_url="", log="")
        built.started, built.ready_seconds = started, ready
        return built
    assert family_demo.member_ready_seconds([process(10.0, 2.0), process(12.0, 0.5)]) == 2.5
    assert family_demo.member_ready_seconds([process(10.0, None)]) == "unknown"
    assert family_demo.member_ready_seconds([]) == "unknown"


# --- the demo's own checks of a member -------------------------------------

def built_stage(tmp_path: Path, name: str = "joe") -> family_demo.Stage:
    plan = committed_plan()
    entry = member(plan, name)
    context = family_demo.contract_context(entry, plan, str(tmp_path / "checkout"),
                                           tmp_path / "state", tmp_path / "shots", "t1")
    return family_demo.Stage(member=entry, context=context, state=tmp_path / "state",
                             shots=tmp_path / "shots")


def test_a_reserved_unbound_port_is_not_expected_to_listen(tmp_path):
    built = built_stage(tmp_path)
    assert sorted(built.served()) == [18430, 18431]


def test_listener_identity_reads_as_a_three_valued_check(tmp_path):
    built = built_stage(tmp_path)
    built.identity = {"verdict": "ours", "listeners": {"18430": [5]}}
    assert family_demo.listener_check(built)["result"] == "pass"
    built.identity = {"verdict": "foreign", "foreign": {"18430": [9]}, "listeners": {}}
    assert family_demo.listener_check(built)["result"] == "fail"
    built.identity = {"verdict": "unknown", "why": "no process table"}
    assert family_demo.listener_check(built)["result"] == "unknown"


def test_a_reserved_unbound_port_that_listens_fails(tmp_path, monkeypatch):
    built = built_stage(tmp_path)
    monkeypatch.setattr(family_demo, "listening", lambda port: set())
    assert family_demo.unbound_check(built)["result"] == "pass"
    monkeypatch.setattr(family_demo, "listening", lambda port: {4242})
    found = family_demo.unbound_check(built)
    assert found["result"] == "fail" and "18432" in found["detail"]
    monkeypatch.setattr(family_demo, "listening", lambda port: None)
    assert family_demo.unbound_check(built)["result"] == "unknown"
    assert family_demo.unbound_check(built_stage(tmp_path, "leo")) is None


def answer(monkeypatch, payload):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    monkeypatch.setattr(family_demo.urllib.request, "urlopen", lambda *a, **k: Response())


def test_identity_must_name_this_run_s_port_and_scratch_state(tmp_path, monkeypatch):
    built = built_stage(tmp_path, "carlos")
    (tmp_path / "state").mkdir()
    ours = str(tmp_path / "state" / "db.json")
    answer(monkeypatch, {"port": 18420, "database": ours})
    assert family_demo.identity_check(built)["result"] == "pass"
    answer(monkeypatch, {"port": 4186, "database": ours})
    assert "port=4186" in family_demo.identity_check(built)["detail"]
    answer(monkeypatch, {"port": 18420, "database": str(tmp_path / "data" / "db.json")})
    found = family_demo.identity_check(built)
    assert found["result"] == "fail" and "is not under" in found["detail"]
    assert family_demo.identity_check(built_stage(tmp_path, "leo")) is None


def test_a_serve_that_says_it_is_not_implemented_is_a_stub_and_not_a_failure(tmp_path,
                                                                                monkeypatch):
    """A real process: it exits before answering, as a stub's serve does. It binds nothing.

    The listener table is stubbed empty: leo's reserved port is read from the
    committed plan, and a family held up on this machine holds it, which
    blocked the member before its serve ran and read as a stub that was not.
    """
    monkeypatch.setattr(family_demo, "listening", lambda port: set())
    plan = committed_plan()
    marker = plan["contract"]["not_implemented"]
    for says, readiness in ((f"serve: {marker}", "unknown"), ("Traceback: boom", "fail")):
        built = built_stage(tmp_path, "leo")
        built.processes[:] = [family_demo.Running(
            member="leo", id="serve", cwd=str(tmp_path),
            argv=[sys.executable, "-c", f"print({says!r}); raise SystemExit(3)"], env={},
            ready_url="http://127.0.0.1:9/", log=str(tmp_path / "serve.log"))]
        family_demo.bring_up(built, 30.0, {"leo": {"install": {"result": "pass"}}},
                             tmp_path / "work")
        assert built.readiness == readiness, says
        record = {"prepared": built.prepared, "checks": []}
        assert family_demo.contract_status(record) == ("stub" if readiness == "unknown"
                                                       else "not asked")


def test_a_written_checkout_is_a_failed_isolation_check(tmp_path):
    repo = make_repo(tmp_path / "checkout")
    built = built_stage(tmp_path)
    members = {"joe": {"checkout": {"after_install": family_demo.dirty(repo)}}}
    assert family_demo.untouched_check(built, members)["result"] == "pass"
    (repo / "written.txt").write_text("x", encoding="utf-8")
    found = family_demo.untouched_check(built, members)
    assert found["result"] == "fail" and "written.txt" in found["detail"]
    members["joe"]["checkout"]["after_install"] = None
    assert family_demo.untouched_check(built, members)["result"] == "unknown"


def test_pictures_are_every_non_empty_image_under_the_shots_directory(tmp_path):
    (tmp_path / "deep").mkdir()
    (tmp_path / "a.png").write_bytes(b"\x89PNG")
    (tmp_path / "deep" / "b.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path / "empty.png").write_bytes(b"")
    (tmp_path / "notes.json").write_text("{}", encoding="utf-8")
    assert [Path(p).name for p in family_demo.pictures(tmp_path)] == ["a.png", "b.svg"]


# --- what the run writes ----------------------------------------------------

def manifest_for(tmp_path, shot_exists: bool) -> dict:
    shot = tmp_path / "shots" / "together" / "leo" / "03-chart.png"
    if shot_exists:
        shot.parent.mkdir(parents=True)
        shot.write_bytes(b"\x89PNG")
    record = {"result": "pass", "ready_seconds": 1.0, "checks": [
        {"check": "contract check", "owner": "member", "result": "pass", "stub": False,
         "exit_code": 0, "detail": "2 passed", "shots": [str(shot)] if shot_exists else []},
        {"check": "ports-held-by-this-run", "owner": "demo", "result": "pass", "detail": ""}]}
    return {
        "run": "r", "started_at": "t", "corpus": {"commit": "abc"},
        "contract": committed_plan()["contract"],
        "members": {
            "leo": {"runs": True, "phase": "core", "family": "performer-display",
                    "ports": {"web": 18440}, "ref": "feat/family-demo-contract",
                    "branch": "feat/family-demo-contract", "commit": "f" * 40,
                    "stacks_on": {"claimed": "walkthrough", "contains": True},
                    "choice": "the setlist pull request", "url": "http://127.0.0.1:18440/"},
            "wolf": {"runs": False, "phase": "instruments", "ports": {"main": 18460},
                     "needs": ["a dry-run target"]}},
        "wave0": {}, "together": {"members": {"leo": record}, "live_connections": {}},
        "seams": {"named_in_source": []}, "unknowns": ["wolf: not run"], "unplaced": []}


def test_the_page_has_a_row_per_member_that_ran_and_lists_the_rest(tmp_path):
    page = family_demo.landing_page(manifest_for(tmp_path, True), tmp_path)
    assert 'data-member="leo"' in page
    assert 'data-member="wolf"' not in page
    assert "a dry-run target" in page
    assert 'src="shots/together/leo/03-chart.png"' in page
    assert "the setlist pull request" in page
    assert "<td>implemented</td>" in page
    assert "not decided while the members are still up" in page


def test_the_page_says_when_a_check_recorded_no_picture(tmp_path):
    page = family_demo.landing_page(manifest_for(tmp_path, False), tmp_path)
    assert "no picture was recorded" in page


def test_the_page_names_a_stub_as_not_implemented(tmp_path):
    manifest = manifest_for(tmp_path, False)
    checks = manifest["together"]["members"]["leo"]["checks"]
    checks[0].update(result="unknown", stub=True, exit_code=3)
    page = family_demo.landing_page(manifest, tmp_path)
    assert "<td>stub</td>" in page
    assert '<span class="unknown">not implemented</span>' in page


def test_a_named_artifact_that_is_missing_is_reported(tmp_path):
    manifest = manifest_for(tmp_path, True)
    (tmp_path / "index.html").write_text("x", encoding="utf-8")
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")
    assert family_demo.missing_artifacts(manifest, tmp_path) == []
    shot = tmp_path / "shots" / "together" / "leo" / "03-chart.png"
    shot.unlink()
    assert family_demo.missing_artifacts(manifest, tmp_path) == [str(shot)]


def test_unknowns_name_the_members_that_did_not_run_and_the_stubs(tmp_path):
    manifest = manifest_for(tmp_path, True)
    found = family_demo.collect_unknowns(manifest)
    assert "wolf: not run in this phase (instruments)" in found
    manifest["together"]["members"]["leo"]["checks"][0].update(result="unknown", stub=True)
    assert "leo together: contract check -- not implemented" in family_demo.collect_unknowns(manifest)


def test_a_member_run_at_an_overridden_ref_is_named_as_such(tmp_path):
    manifest = manifest_for(tmp_path, True)
    manifest["members"]["leo"].update(ref="origin/setlist", ref_overridden=True)
    assert any(u.startswith("leo: run at origin/setlist rather than its branch")
               for u in family_demo.collect_unknowns(manifest))


def test_hazards_name_an_unreserved_bind_a_forced_descendant_a_held_port_and_a_bad_stack(tmp_path):
    manifest = manifest_for(tmp_path, True)
    record = manifest["together"]["members"]["leo"]
    record["listener_identity"] = {"unreserved_binds": ["UDP 0.0.0.0:53000"], "foreign": {}}
    record["processes"] = [{"id": "serve", "shutdown": {"descendants_forced": [7]}}]
    manifest["together"]["ports_after"] = {"18440": {"free": "unknown"}}
    manifest["members"]["leo"]["stacks_on"]["contains"] = False
    found = family_demo.collect_hazards(manifest)
    assert any("outside its reserved ports: UDP 0.0.0.0:53000" in h for h in found)
    assert any("had to be forced: [7]" in h for h in found)
    assert "together: port 18440 not free after shutdown" in found  # unknown is not free
    assert any("does not contain walkthrough" in h for h in found)


# --- the entry point refuses before it starts anything ---------------------

def test_plan_mode_starts_nothing_and_exits_zero(capsys):
    assert family_demo.main(["--plan"]) == 0
    out = capsys.readouterr().out
    assert "run  ShowRunner" in out and "later wolf" in out
    assert "feat/family-control" in out


def test_a_work_directory_inside_the_repository_is_refused(capsys):
    """Asked with a phase that starts nothing, so that with this guard broken the
    test can only create a directory -- the first version of this test ran the
    whole demo inside the repository when its mutant removed the guard."""
    target = CI_DIR.parent / "family-demo-runs"
    assert family_demo.main(["--work", str(target), "--phase", "instruments"]) == 2
    assert "inside this repository" in capsys.readouterr().err
    assert not target.exists()


def test_a_member_filter_naming_nobody_is_refused(capsys):
    assert family_demo.main(["--plan", "--member", "nobody"]) == 2


def test_a_phase_filter_naming_no_phase_is_refused(capsys):
    assert family_demo.main(["--plan", "--phase", "nothing"]) == 2


def test_a_broken_plan_exits_two_and_says_why(tmp_path, capsys):
    plan = copy.deepcopy(committed_plan())
    member(plan, "leo")["ports"]["web"] = 1
    broken = tmp_path / "family-demo.yaml"
    import yaml
    broken.write_text(yaml.safe_dump(plan), encoding="utf-8")
    assert family_demo.main(["--plan-file", str(broken), "--plan"]) == 2
    assert "leo: port web=1 is outside" in capsys.readouterr().err


def test_a_private_member_is_found_by_its_reference_where_the_companion_names_it():
    """Mutation: index by `name` only, and the planned reference is not found."""
    merged = [{"ref": "private-34", "name": "a-real-name"}, {"name": "joe"}]
    index = family_demo.index_roster(merged)
    assert index["private-34"] is merged[0] and index["a-real-name"] is merged[0]
    assert set(index) == {"private-34", "a-real-name", "joe"}


# --- the dev loop: a working checkout, a second family, a restart while held -----
#
# Each guard here was broken once and seen to go red; the mutation is named in
# the test that caught it.

def git_in(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], check=True, capture_output=True, text=True).stdout.strip()


def other_repo(path: Path) -> Path:
    """A repository with a root commit of its own, unlike any make_repo's."""
    path.mkdir()
    git_in(path, "init", "-q", "-b", "main")
    git_in(path, "commit", "-q", "--allow-empty", "-m", f"a root of its own: {path.name}")
    return path


def bump(path: Path) -> None:
    """Move a file's modification time on by a second, as a save does."""
    moved = path.stat().st_mtime_ns + 1_000_000_000
    os.utime(path, ns=(moved, moved))


def test_a_port_offset_moves_every_port_the_run_hands_out(tmp_path):
    plan = family_demo.offset_plan(committed_plan(), 100)
    assert problems(plan) == []
    assert (plan["ports"]["first"], plan["ports"]["last"]) == (18500, 18599)
    assert member(plan, "joe")["ports"] == {"web": 18530, "api": 18531, "qmcp": 18532}
    assert plan["stage"]["port"] == 18505
    joe = member(plan, "joe")
    context = family_demo.contract_context(joe, plan, "/c", tmp_path / "s", tmp_path / "x", "t")
    argv = family_demo.serve_argv(joe, plan, context)
    assert argv[argv.index("--port") + 1] == "18530"
    assert argv[argv.index("--api-port") + 1] == "18531"
    assert argv[argv.index("--qmcp-url") + 1] == "http://127.0.0.1:18532"
    job = family_demo.stage_job(plan, family_demo.running(plan), tmp_path)
    assert (job["port"], job["hub_base"]) == (18505, "http://127.0.0.1:18500")
    assert job["resolved"]["carlos"]["url"] == "http://127.0.0.1:18520"
    assert job["resolved"]["leo"]["page"] == "http://127.0.0.1:18540/?follow=http://127.0.0.1:18500"
    assert committed_plan()["ports"]["first"] == 18400  # the plan on disk is not moved


def test_a_port_offset_that_overlaps_the_family_or_leaves_the_port_range_is_refused():
    """Mutation: the overlap rule dropped, so an offset of 50 put two families on one port -- red here."""
    plan = committed_plan()
    assert family_demo.offset_plan(plan, 0) is plan
    for offset in (50, 99, -99):
        with pytest.raises(family_demo.PlanError, match="overlaps"):
            family_demo.offset_plan(plan, offset)
    with pytest.raises(family_demo.PlanError, match="outside 1024..65535"):
        family_demo.offset_plan(plan, 50000)
    assert family_demo.offset_plan(plan, -100)["ports"]["first"] == 18300


def test_plan_mode_prints_the_moved_ports_and_refuses_an_overlap(capsys):
    assert family_demo.main(["--plan", "--port-offset", "100"]) == 0
    out = capsys.readouterr().out
    assert "ports moved by 100: 18500..18599" in out and "web=18540" in out
    assert family_demo.main(["--plan", "--port-offset", "50"]) == 2
    assert "overlaps the plan's own range" in capsys.readouterr().err


def test_a_src_names_a_member_and_a_path_once():
    assert family_demo.parse_sources(["leo=C:/dev/leo"]) == {"leo": Path("C:/dev/leo")}
    for bad in (["leo"], ["=x"], ["leo="], ["leo=a", "leo=b"]):
        with pytest.raises(family_demo.PlanError):
            family_demo.parse_sources(bad)


def test_a_src_must_be_the_top_of_a_running_member_s_own_working_tree(tmp_path):
    """Mutation: the root-commit comparison dropped, so another repository ran as leo -- red here.

    Mutation: the top-of-tree comparison dropped, so a directory inside a checkout passed -- red here.
    """
    order = family_demo.running(committed_plan())
    leo, other = make_repo(tmp_path / "leo"), other_repo(tmp_path / "other")
    (leo / "sub").mkdir()

    def found(sources, refs=None, clones=None):
        return family_demo.source_problems(sources, order, refs or {}, clones or {})

    assert found({"leo": leo}, clones={"leo": leo}) == []
    assert "not the top of a git working tree" in found({"leo": leo / "sub"})[0]
    assert "not the top of a git working tree" in found({"leo": tmp_path / "missing"})[0]
    assert "not a member that runs" in found({"wolf": leo})[0]
    assert "also given --ref" in found({"leo": leo}, refs={"leo": "main"})[0]
    assert "shares no root commit" in found({"leo": other}, clones={"leo": leo})[0]


def test_a_dev_source_records_its_path_head_and_dirty_tree(tmp_path):
    repo = make_repo(tmp_path / "leo")
    (repo / "edit.txt").write_text("x", encoding="utf-8")
    entry = {"name": "leo", "install": [[sys.executable, "-c", "pass"]], "stacks_on": "active"}
    (tmp_path / "run" / "logs").mkdir(parents=True)
    record = family_demo.use_source(entry, repo, None, tmp_path / "run", tmp_path / "work", False)
    head = git_in(repo, "rev-parse", "HEAD")
    assert record["source"] == {"kind": "dev", "path": str(repo), "head": head, "branch": "main",
                                "dirty": True, "dirty_paths": ["?? edit.txt"]}
    assert (record["ref"], record["commit"]) == ("dev source", head)
    assert record["checkout"]["dev_source"] is True and record["stacks_on"]["contains"] is True
    assert record["install"]["result"] == "pass"
    assert (tmp_path / "work" / "installed" / "src-leo.json").is_file()


def test_a_dev_source_is_installed_in_place_only_when_its_locks_change(tmp_path):
    """Mutation: the key kept from before the install, so an installer that writes a lock
    installed again on every run -- red here.

    Mutation: HEAD in the key, so a commit installed again -- red here.
    """
    repo = make_repo(tmp_path / "member")
    (repo / "pdm.lock").write_text("a", encoding="utf-8")
    script = ("import pathlib; pathlib.Path('.venv').mkdir(exist_ok=True); "
              "pathlib.Path('uv.lock').write_text('made', encoding='utf-8'); "
              "open('runs.txt', 'a').write('x')")
    entry = {"name": "m", "install": [[sys.executable, "-c", script]]}
    logs, stamp = tmp_path / "logs", tmp_path / "installed" / "src-m.json"
    logs.mkdir()

    def install():
        return family_demo.install_in_place(entry, repo, logs, stamp, fresh=False)

    first = install()
    assert first["result"] == "pass" and not first["reused"] and "no install" in first["why"]
    assert install()["reused"] is True  # the uv.lock it wrote is counted once
    git_in(repo, "commit", "-q", "--allow-empty", "-m", "a commit moves HEAD, not a lock")
    assert install()["reused"] is True
    (repo / "pdm.lock").write_text("b", encoding="utf-8")
    again = install()
    assert again["reused"] is False and "lock files" in again["why"]
    assert (repo / "runs.txt").read_text(encoding="utf-8") == "xx"
    assert family_demo.install_in_place(entry, repo, logs, stamp, fresh=True)["why"] == \
        "--fresh-install"


def test_a_dev_source_s_checkout_is_named_as_such_and_never_counted(tmp_path):
    """Mutation: member_result counting `dev source`, so every dev member read unknown -- red here.

    Mutation: untouched_check comparing a dev source, so an edit failed it -- red here.
    """
    repo = make_repo(tmp_path / "checkout")
    built = built_stage(tmp_path)
    (repo / "edited.py").write_text("x", encoding="utf-8")
    members = {"joe": {"checkout": {"after_install": [], "dev_source": True}}}
    found = family_demo.untouched_check(built, members)
    assert found["result"] == "dev source"
    assert found["evidence"]["dirty_at_end"] == ["?? edited.py"]
    assert family_demo.member_result([found, demo("pass")], "pass", own_check=False) == "pass"
    assert family_demo.member_result([found], "pass", own_check=False) == "unknown"
    assert family_demo.member_result([found, demo("fail")], "pass", own_check=False) == "fail"


def test_state_in_a_dev_source_is_never_emptied_even_under_the_work_directory(tmp_path,
                                                                               monkeypatch):
    """Mutation: the dev-source branch taken out of prepare, so joe's Data/ in the developer's
    own checkout was emptied -- red here."""
    monkeypatch.setattr(family_demo, "listening", lambda port: set())
    work = tmp_path / "work"
    checkout = work / "dev" / "joe"
    (checkout / "Data").mkdir(parents=True)
    (checkout / "Data" / "take.mid").write_bytes(b"x")
    plan = committed_plan()
    entry = member(plan, "joe")
    context = family_demo.contract_context(entry, plan, str(checkout), tmp_path / "state",
                                           tmp_path / "shots", "t1")
    built = family_demo.Stage(member=entry, context=context, state=tmp_path / "state",
                              shots=tmp_path / "shots")
    members = {"joe": {"install": {"result": "pass"}, "checkout": {"dev_source": True}}}
    assert family_demo.prepare(built, members, work) is True
    assert (checkout / "Data" / "take.mid").is_file()
    assert "never emptied" in built.prepared["state_in_checkout"]
    # The same layout as a clone of this run's is emptied: the guard is what kept it.
    members["joe"]["checkout"]["dev_source"] = False
    assert family_demo.prepare(built, members, work) is True
    assert not (checkout / "Data").exists()


def test_a_watch_sees_a_changed_file_once_and_by_what_it_asks_for(tmp_path):
    """Mutation: changed() not keeping what it has seen, so one save restarted forever -- red here."""
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "templates").mkdir()
    code, page = tmp_path / "src" / "pkg" / "app.py", tmp_path / "templates" / "rack.html"
    for path in (code, page, tmp_path / "notes.txt"):
        path.write_text("a", encoding="utf-8")
    watch = family_demo.Watch("m", tmp_path, ["src/**/*.py"], ["templates/**/*"]).start()
    assert watch.changed() == {"restart": [], "refresh": []}
    bump(code)
    assert watch.changed() == {"restart": ["src/pkg/app.py"], "refresh": []}
    assert watch.changed() == {"restart": [], "refresh": []}
    bump(page)
    bump(tmp_path / "notes.txt")
    assert watch.changed() == {"restart": [], "refresh": ["templates/rack.html"]}
    (tmp_path / "src" / "pkg" / "new.py").write_text("n", encoding="utf-8")
    code.unlink()
    assert watch.changed()["restart"] == ["src/pkg/app.py", "src/pkg/new.py"]


def started_stage(tmp_path: Path, name: str) -> family_demo.Stage:
    plan = committed_plan()
    return family_demo.stage(member(plan, name), {name: {"checkout": {"path": str(tmp_path)}}},
                             "stage", tmp_path, "t1", plan)


def test_a_restart_starts_the_member_as_it_was_started_and_only_on_free_ports(tmp_path,
                                                                             monkeypatch):
    """Mutation: the restart building its command afresh from the plan, so the hub lost the
    family links it is handed on its command line -- red here.

    Mutation: the free-port wait dropped, so a member was started over a port still held -- red here.
    Mutation: a restart's log named from the last restart's, so names stacked up -- red here.
    """
    built = started_stage(tmp_path, "ShowRunner")
    built.processes[0].argv += ["--family", "carlos=http://127.0.0.1:18420"]
    first = built.processes[0]
    started, stopped = [], []
    monkeypatch.setattr(family_demo, "process_table", lambda: None)
    monkeypatch.setattr(family_demo, "stop", lambda process: stopped.append(process))
    monkeypatch.setattr(family_demo, "listening", lambda port: set())
    monkeypatch.setattr(family_demo, "start", lambda process: started.append(process))
    monkeypatch.setattr(family_demo, "wait_ready",
                        lambda process, budget: setattr(process, "readiness", "pass"))
    record = family_demo.restart_member(built, 30.0, "src/app.py changed")
    assert stopped == [first] and built.retired == [first]
    assert started == built.processes and built.processes[0] is not first
    assert built.processes[0].argv == first.argv
    assert built.processes[0].log.endswith("stage-ShowRunner-serve.restart-1.log")
    assert record["result"] == "pass" and built.readiness == "pass"
    assert built.record()["restarts"] == [record]
    assert built.record()["retired_processes"][0]["argv"] == first.argv
    family_demo.restart_member(built, 30.0, "src/app.py changed again")
    assert built.processes[0].log.endswith("stage-ShowRunner-serve.restart-2.log")

    monkeypatch.setattr(family_demo, "listening", lambda port: {4242})
    monkeypatch.setattr(family_demo, "PORT_RELEASE_SECONDS", 0.0)
    held = family_demo.restart_member(built, 30.0, "asked for on the stage")
    assert held["result"] == "fail" and "4242" in held["detail"]
    assert len(started) == 2 and built.readiness == "fail"


def test_a_held_family_answers_a_restart_request_and_refuses_a_stranger(tmp_path, monkeypatch):
    """Mutation: answer() trusting the member it is asked for, so a request for wolf raised
    inside the hold and took the family down -- red here."""
    built = started_stage(tmp_path, "carlos")
    calls = []
    monkeypatch.setattr(family_demo, "restart_member", lambda b, budget, why: calls.append(
        (b.name, why)) or {"result": "pass", "seconds": 1.5, "number": 1})
    control = tmp_path / "control"
    with family_demo.Hold([built], 30.0, control) as holder:
        assert (control / family_stage.HOLDING).is_file()
        family_stage.write_json(control / "n1.request", {"member": "carlos", "nonce": "n1"})
        family_stage.write_json(control / "n2.request", {"member": "wolf", "nonce": "n2"})
        holder.tick()
    assert not (control / family_stage.HOLDING).exists()
    assert calls == [("carlos", "asked for on the stage")]
    answers = {n: json.loads((control / f"{n}.done").read_text(encoding="utf-8"))
               for n in ("n1", "n2")}
    assert answers["n1"]["result"] == "pass" and answers["n2"]["result"] == "refused"
    assert family_stage.read_events(control)["carlos"]["restarts"] == 1


def test_a_watched_file_restarts_its_member_and_a_view_file_only_refreshes_it(tmp_path,
                                                                              monkeypatch):
    built = started_stage(tmp_path, "carlos")
    calls = []
    monkeypatch.setattr(family_demo, "restart_member", lambda b, budget, why: calls.append(
        (b.name, why)) or {"result": "pass", "seconds": 1.0, "number": 1})
    root = tmp_path / "checkout"
    (root / "src").mkdir(parents=True)
    (root / "templates").mkdir()
    code, page = root / "src" / "main.py", root / "templates" / "demo.html"
    code.write_text("a", encoding="utf-8")
    page.write_text("a", encoding="utf-8")
    control = tmp_path / "control"
    watch = family_demo.Watch("carlos", root, ["src/*.py"], ["templates/*"])
    with family_demo.Hold([built], 30.0, control, [watch]) as holder:
        holder.tick()
        bump(code)
        holder.tick()
        bump(page)
        holder.tick()
    assert calls == [("carlos", "src/main.py changed")]
    events = family_stage.read_events(control)["carlos"]
    assert (events["restarts"], events["refreshes"]) == (1, 1)
    assert events["last"]["summary"] == "templates/demo.html changed; view reloaded"


def test_every_core_member_says_what_it_reloads_and_what_restarts_it():
    for entry in family_demo.running(committed_plan()):
        assert entry["dev"]["reloads"].strip(), entry["name"]
        assert entry["dev"].get("restart_on") or entry["dev"].get("refresh_on"), entry["name"]


def test_a_dev_block_with_an_unknown_key_or_a_glob_outside_the_checkout_is_refused():
    """Mutation: an unknown key ignored, so `restart-on` watched nothing in silence -- red here."""
    plan = copy.deepcopy(committed_plan())
    member(plan, "leo")["dev"] = {"restart-on": ["leo/*.py"], "reloads": "x"}
    assert "leo: dev.restart-on is not one of" in problems(plan)[0]
    member(plan, "leo")["dev"] = {"restart_on": ["../joe/*.py"], "reloads": "x"}
    assert any("must be a glob inside the checkout" in p for p in problems(plan))
    member(plan, "leo")["dev"] = {"restart_on": ["leo/*.py"]}
    assert any("dev.reloads must say" in p for p in problems(plan))


def test_the_page_names_a_dev_source_by_its_path_and_its_tree(tmp_path):
    manifest = manifest_for(tmp_path, True)
    manifest["members"]["leo"].update(ref="dev source", source={
        "kind": "dev", "path": "C:/dev/leo", "branch": "feat/x", "head": "f" * 40, "dirty": True})
    page = family_demo.landing_page(manifest, tmp_path)
    assert "<code>C:/dev/leo</code> on <code>feat/x</code>, dirty at the start" in page


def test_reload_needs_a_held_family_and_a_dev_source(capsys):
    """Mutation: either refusal removed, so --reload ran and watched nothing -- red here."""
    assert family_demo.main(["--plan", "--reload"]) == 2
    assert "needs --hold, --open or --dev" in capsys.readouterr().err
    assert family_demo.main(["--plan", "--reload", "--hold"]) == 2
    assert "name one with --src" in capsys.readouterr().err


def test_dev_takes_every_core_member_from_its_directory_and_refuses_a_missing_one(tmp_path,
                                                                                  capsys):
    assert family_demo.main(["--plan", "--dev", str(tmp_path)]) == 2
    err = capsys.readouterr().err
    for name in CORE:
        assert f"--src {name}: {tmp_path / name} is not the top of a git working tree" in err
    assert family_demo.main(["--plan", "--dev", "--member", "leo"]) == 2
    assert "--dev runs the whole core" in capsys.readouterr().err


def test_dev_defaults_to_the_work_directory_not_to_where_this_corpus_sits(tmp_path, capsys):
    """The members come from <work>/dev; the corpus runs from wherever it is checked out.

    No roster clone resolves under the empty search root, so no root commit is compared.
    """
    (tmp_path / "dev").mkdir()
    for name in CORE:
        make_repo(tmp_path / "dev" / name)
    assert family_demo.main(["--plan", "--dev", "--work", str(tmp_path),
                             "--search-root", str(tmp_path / "nowhere")]) == 0
    out = capsys.readouterr().out
    for name in CORE:
        assert f"dev source {(tmp_path / 'dev' / name).resolve()}" in out
    assert "stage on port 18405" in out


def test_a_member_never_inherits_the_environment_qm_runs_in(monkeypatch):
    """Mutation: UV_PROJECT_ENVIRONMENT passed through, so a member's `uv sync` installed into
    the environment `qm` was running from -- red here."""
    monkeypatch.setenv("VIRTUAL_ENV", "C:/qm/.venv")
    monkeypatch.setenv("UV_PROJECT_ENVIRONMENT", "C:/qm/.venv")
    monkeypatch.setenv("UV_CACHE_DIR", "C:/cache")
    env = family_demo.child_env({"JOE_CUES": "0"})
    assert "VIRTUAL_ENV" not in env and "UV_PROJECT_ENVIRONMENT" not in env
    assert env["UV_CACHE_DIR"] == "C:/cache" and env["JOE_CUES"] == "0"


def test_the_dev_loop_page_names_flags_the_tool_has_and_what_restarts_each_member(capsys):
    """The page is checked against the tool and the roster rather than kept beside them.

    Mutation: --port-offset renamed in the parser -- red here.
    Mutation: a glob added to joe's dev.restart_on and not to the page -- red here.
    """
    page = (CI_DIR.parent / "docs" / "usage" / "develop-a-family-member.md").read_text(
        encoding="utf-8")
    with pytest.raises(SystemExit):
        family_demo.main(["--help"])
    usage = capsys.readouterr().out
    for flag in ("--dev", "--work", "--port-offset", "--src", "--stage"):
        assert flag in page and flag in usage, flag
    for entry in family_demo.running(committed_plan()):
        row = next(line for line in page.splitlines() if line.startswith(f"| {entry['name']} |"))
        for glob in entry["dev"].get("restart_on") or []:
            assert f"`{glob}`" in row, (entry["name"], glob)
