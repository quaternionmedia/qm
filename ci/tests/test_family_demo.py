"""The family demo's rules, checked without starting anything.

Hermetic: no port is bound, no member is cloned, no browser is launched. What
is tested is the part that decides -- whether the roster can run, which port is
whose, how results combine, what the page and the manifest name -- because the
part that starts processes is exercised by running the demo, and a test that
needed five repositories and a browser would skip everywhere CI runs.

Each refusal is shown firing on a plan broken on purpose. A rule only ever seen
green says what its author meant, not what it checks.
"""

from __future__ import annotations

import copy
import io
import json
import sys
import tomllib
import wave
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
    return family_demo.check_plan(plan, rostered(), family_demo.probe_names())


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


def test_only_the_core_phase_runs_and_every_core_member_asserts_a_behaviour():
    plan = committed_plan()
    names = [m["name"] for m in family_demo.running(plan)]
    assert names == ["ShowRunner", "ShowStopper", "carlos", "joe", "leo"]
    for entry in family_demo.running(plan):
        assert any(c["counts"] == "behaviour" for c in entry["checks"]), entry["name"]


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


def test_a_running_member_with_only_a_surface_check_is_refused():
    plan = committed_plan()
    for check in member(plan, "carlos")["checks"]:
        check["counts"] = "surface"
    assert "carlos: runs, but no check asserts a behaviour" in problems(plan)


def test_a_check_the_probe_module_does_not_declare_is_refused():
    plan = committed_plan()
    member(plan, "joe")["checks"][0]["name"] = "joe-does-something-unwritten"
    assert any("no browser probe is named" in p for p in problems(plan))


def test_a_placeholder_naming_an_undeclared_port_is_refused():
    plan = committed_plan()
    member(plan, "joe")["processes"][0]["ready"] = "http://127.0.0.1:{port:nowhere}/"
    assert any("{port:nowhere} names no declared port" in p for p in problems(plan))


def test_a_phase_that_does_not_run_must_say_what_its_members_need():
    plan = committed_plan()
    member(plan, "wolf")["needs"] = []
    assert any(p.startswith("wolf: a phase that does not run") for p in problems(plan))


def test_an_unknown_preparation_is_refused():
    plan = committed_plan()
    member(plan, "ShowRunner")["prepare"] = "something-else"
    assert any("no preparation is named" in p for p in problems(plan))


def test_a_ref_override_needs_a_member_and_a_ref():
    assert family_demo.parse_refs(["leo=origin/setlist"]) == {"leo": "origin/setlist"}
    for bad in ("leo", "=origin/main", "leo="):
        with pytest.raises(family_demo.PlanError):
            family_demo.parse_refs([bad])


# --- expansion ---------------------------------------------------------------

def test_placeholders_expand_and_an_unknown_one_raises():
    context = {"ports": {"web": 18440}, "token": "t1", "checkout": "/c", "state": "/s"}
    assert family_demo.expand(["--port", "{port:web}", "{state}/x-{token}"], context) == [
        "--port", "18440", "/s/x-t1"]
    with pytest.raises(family_demo.PlanError):
        family_demo.expand("{port:api}", context)
    with pytest.raises(family_demo.PlanError):
        family_demo.expand("{home}", context)


# --- results are combined without coercion -----------------------------------

def check(result, counts="behaviour"):
    return {"check": "c", "result": result, "counts": counts}


def test_unknown_is_never_folded_into_fail():
    assert family_demo.member_result([check("unknown")], "pass") == "unknown"
    assert family_demo.member_result([check("pass"), check("unknown")], "pass") == "unknown"
    assert family_demo.member_result([check("fail"), check("unknown")], "pass") == "fail"


def test_a_member_that_never_got_to_its_check_is_unknown_unless_seen_not_to_start():
    assert family_demo.member_result([check("unknown")], "unknown") == "unknown"
    assert family_demo.member_result([check("unknown")], "fail") == "fail"


def test_a_surface_check_is_reported_beside_the_result_and_never_changes_it():
    assert family_demo.member_result([check("pass"), check("fail", "surface")], "pass") == "pass"
    assert family_demo.member_result([check("pass", "surface")], "pass") == "unknown"


def test_the_exit_status_separates_fail_from_unknown():
    assert family_demo.exit_status(["pass", "pass"]) == 0
    assert family_demo.exit_status(["pass", "fail", "unknown"]) == 1
    assert family_demo.exit_status(["pass", "unknown"]) == 3
    assert family_demo.exit_status([]) == 3  # nothing ran is not a pass


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


# --- what the run writes ----------------------------------------------------

def test_the_scratch_recording_is_a_wave_file_with_no_frames():
    with wave.open(io.BytesIO(family_demo.SILENT_WAV)) as recording:
        assert recording.getnframes() == 0
        assert recording.getframerate() == 44100


def test_joe_s_scratch_config_imports_the_member_s_own_by_relative_path(tmp_path):
    """A file URL is left external by Vite's config bundler, and Node then loads
    the member's ESM config as CommonJS and dies. Found by running it."""
    checkout, state = tmp_path / "checkout", tmp_path / "state"
    checkout.mkdir(), state.mkdir()
    prepared = family_demo.prepare_joe(state, {
        "ports": {"api": 18430, "web": 18431}, "token": "t1", "checkout": str(checkout)})
    config = (state / "vite.config.mjs").read_text(encoding="utf-8")
    assert 'import member from "../checkout/vite.config.js"' in config
    assert "file:" not in config
    assert "http://127.0.0.1:18430" in config
    assert (state / "Data" / "Audio" / prepared["recording"]).is_file()
    assert "t1" in prepared["recording"]


def test_showrunner_s_scratch_config_is_toml_naming_scratch_paths(tmp_path):
    family_demo.prepare_showrunner(tmp_path, {"ports": {"http": 18400}})
    config = tomllib.loads((tmp_path / "show.toml").read_text(encoding="utf-8"))
    assert config["server"] == {"host": "127.0.0.1", "port": 18400}
    assert Path(config["database"]["path"]) == tmp_path / "show.db"
    assert Path(config["plugins"]["showlogger"]["file"]) == tmp_path / "show.log"


def manifest_for(tmp_path, shot_exists: bool) -> dict:
    shot = tmp_path / "shots" / "together-leo-x.png"
    if shot_exists:
        shot.parent.mkdir(parents=True)
        shot.write_bytes(b"\x89PNG")
    record = {"result": "pass", "ready_seconds": 1.0, "checks": [
        {"check": "leo-search-selects-a-song", "result": "pass", "counts": "behaviour",
         "shot": str(shot) if shot_exists else None, "detail": ""}]}
    return {
        "run": "r", "started_at": "t", "corpus": {"commit": "abc"},
        "members": {
            "leo": {"runs": True, "phase": "core", "family": "performer-display",
                    "ports": {"web": 18440}, "ref": "origin/main", "commit": "f" * 40,
                    "surface": "http://127.0.0.1:18440/"},
            "wolf": {"runs": False, "phase": "instruments", "ports": {"main": 18460},
                     "needs": ["a dry-run target"]}},
        "wave0": {}, "together": {"members": {"leo": record}, "live_connections": {}},
        "seams": {"named_in_source": []}, "unknowns": ["wolf: not run"], "unplaced": []}


def test_the_page_has_a_row_per_member_that_ran_and_lists_the_rest(tmp_path):
    page = family_demo.landing_page(manifest_for(tmp_path, True), tmp_path)
    assert 'data-member="leo"' in page
    assert 'data-member="wolf"' not in page
    assert "a dry-run target" in page
    assert 'src="shots/together-leo-x.png"' in page
    assert "not decided while the members are still up" in page


def test_the_page_says_when_a_check_recorded_no_picture(tmp_path):
    page = family_demo.landing_page(manifest_for(tmp_path, False), tmp_path)
    assert "no picture was recorded" in page


def test_a_named_artifact_that_is_missing_is_reported(tmp_path):
    manifest = manifest_for(tmp_path, True)
    (tmp_path / "index.html").write_text("x", encoding="utf-8")
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")
    assert family_demo.missing_artifacts(manifest, tmp_path) == []
    (tmp_path / "shots" / "together-leo-x.png").unlink()
    assert family_demo.missing_artifacts(manifest, tmp_path) == [
        str(tmp_path / "shots" / "together-leo-x.png")]


def test_unknowns_name_the_members_that_did_not_run(tmp_path):
    manifest = manifest_for(tmp_path, True)
    found = family_demo.collect_unknowns(manifest)
    assert "wolf: not run in this phase (instruments)" in found
    assert "leo together: listener identity not established" not in found


# --- the entry point refuses before it starts anything ---------------------

def test_plan_mode_starts_nothing_and_exits_zero(capsys):
    assert family_demo.main(["--plan"]) == 0
    out = capsys.readouterr().out
    assert "run  ShowRunner" in out and "later wolf" in out


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


def test_a_member_s_ready_time_runs_from_its_first_start_to_its_last_answer():
    def process(started, ready):
        built = family_demo.Running(member="m", id="p", argv=[], cwd="", env={},
                                    ready_url="", log="")
        built.started, built.ready_seconds = started, ready
        return built
    # an API ready 2s after it started at t=10, then a web server started at
    # t=12 and ready 0.5s later: the member took 2.5s, not 2s
    assert family_demo.member_ready_seconds([process(10.0, 2.0), process(12.0, 0.5)]) == 2.5
    assert family_demo.member_ready_seconds([process(10.0, None)]) == "unknown"
    assert family_demo.member_ready_seconds([]) == "unknown"


def test_binds_are_listeners_and_udp_sockets_not_connections():
    text = NETSTAT + "  UDP    0.0.0.0:53000          *:*                                    4242\n"
    rows = family_demo.parse_netstat_binds(text)
    assert ("TCP", ("127.0.0.1", 18440), 22548) in rows
    assert ("UDP", ("0.0.0.0", 53000), 4242) in rows
    assert all(pid != 900 for _proto, _local, pid in rows)  # an ESTABLISHED socket is not a bind


def test_hazards_name_an_unreserved_bind_a_forced_descendant_and_a_held_port(tmp_path):
    manifest = manifest_for(tmp_path, True)
    record = manifest["together"]["members"]["leo"]
    record["listener_identity"] = {"unreserved_binds": ["UDP 0.0.0.0:53000"], "foreign": {}}
    record["processes"] = [{"id": "web", "shutdown": {"descendants_forced": [7]}}]
    manifest["together"]["ports_after"] = {"18440": {"free": "unknown"}}
    found = family_demo.collect_hazards(manifest)
    assert any("outside its reserved ports: UDP 0.0.0.0:53000" in h for h in found)
    assert any("had to be forced: [7]" in h for h in found)
    assert "together: port 18440 not free after shutdown" in found  # unknown is not free


def test_a_member_run_at_an_overridden_ref_is_named_as_such(tmp_path):
    manifest = manifest_for(tmp_path, True)
    manifest["members"]["leo"].update(ref="origin/setlist", ref_overridden=True)
    assert any(u.startswith("leo: run at origin/setlist rather than its default branch")
               for u in family_demo.collect_unknowns(manifest))


def test_a_check_parameter_naming_an_undeclared_port_is_refused():
    plan = committed_plan()
    member(plan, "carlos")["checks"][0]["params"]["port"] = "{port:api}"
    assert "carlos: {port:api} names no declared port" in problems(plan)
