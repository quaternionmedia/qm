"""The probe module, run here under this corpus's interpreter without its dependencies.

The probes are written to run under another interpreter -- Playwright's, or a
member's own -- so what can be asserted here is the part that needs neither:
the registries the harness reads, the job and result format, and that a probe
which cannot evaluate a check reports `unknown` rather than `fail`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import family_demo  # noqa: E402
import family_demo_probes  # noqa: E402


def test_the_names_the_harness_reads_from_source_are_the_ones_declared():
    """`family_demo.probe_names` reads this module's source rather than importing it."""
    read = family_demo.probe_names()
    assert read["browser"] == set(family_demo_probes.BROWSER)
    assert read["terminal"] == set(family_demo_probes.TERMINAL)
    assert read["browser"] and read["terminal"]


def test_every_check_the_plan_names_is_declared_here():
    plan = family_demo.load_plan()
    named = {(c["runner"], c["name"]) for m in family_demo.running(plan) for c in m["checks"]}
    declared = {("browser", n) for n in family_demo_probes.BROWSER}
    declared |= {("terminal", n) for n in family_demo_probes.TERMINAL}
    assert named <= declared


def test_a_check_it_cannot_find_is_unknown_and_the_results_file_is_written(tmp_path):
    job = tmp_path / "job.json"
    out = tmp_path / "out.json"
    job.write_text(json.dumps({"checks": [{"member": "x", "name": "nothing"}],
                               "out": str(out)}), encoding="utf-8")
    assert family_demo_probes.main(["terminal", str(job)]) == 0
    [result] = json.loads(out.read_text(encoding="utf-8"))
    assert result["result"] == "unknown"
    assert "no terminal check is named" in result["detail"]


def test_a_failed_assertion_is_fail_and_anything_else_is_unknown(monkeypatch):
    async def asserts(entry):
        family_demo_probes.check(False, "the stopwatch did not move")

    async def crashes(entry):
        raise RuntimeError("the probe itself broke")

    monkeypatch.setitem(family_demo_probes.TERMINAL, "asserts", asserts)
    monkeypatch.setitem(family_demo_probes.TERMINAL, "crashes", crashes)
    results = family_demo_probes.run_terminal({"checks": [
        {"member": "x", "name": "asserts"}, {"member": "x", "name": "crashes"}]})
    assert [r["result"] for r in results] == ["fail", "unknown"]
    assert results[0]["detail"] == "the stopwatch did not move"


def test_bad_usage_exits_two():
    assert family_demo_probes.main(["window", "job.json"]) == 2
    assert family_demo_probes.main([]) == 2


def test_an_origin_drops_the_page_and_keeps_the_port():
    assert family_demo_probes.origin("http://127.0.0.1:18420/rack") == "http://127.0.0.1:18420"
    assert family_demo_probes.origin("http://127.0.0.1:18431/joe/") == "http://127.0.0.1:18431"
