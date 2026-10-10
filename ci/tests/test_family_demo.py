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
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import cli  # noqa: E402
import family_demo  # noqa: E402
import roster  # noqa: E402


def committed_plan() -> dict:
    return family_demo.load_plan()


def rostered() -> set[str]:
    return {entry["name"] for entry in roster.load()}


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


def test_a_serve_that_says_it_is_not_implemented_is_a_stub_and_not_a_failure(tmp_path):
    """A real process: it exits before answering, as a stub's serve does. It binds nothing."""
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
    assert "feat/family-demo-contract" in out


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
