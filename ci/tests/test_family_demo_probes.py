"""The demo's own browser check, run here under this corpus's interpreter.

The probe is written to run under Playwright's interpreter, so what can be
asserted here is the part that needs no browser: the job and result format,
that a probe which cannot evaluate a check reports `unknown` rather than
`fail`, and that it holds no member's check.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import family_demo_probes  # noqa: E402


def test_the_only_check_here_is_the_demo_s_own_page():
    assert set(family_demo_probes.BROWSER) == {"landing-page-shows-every-member"}


def test_a_check_it_cannot_find_is_unknown_and_never_fail():
    class Browser:
        def new_context(self, **kwargs):
            return Context()

    class Context:
        def new_page(self):
            return Page()

        def close(self):
            pass

    class Page:
        def on(self, *args):
            pass

        def close(self):
            pass

    result = family_demo_probes.one_browser_check(Browser(), {"member": "x", "name": "nothing"})
    assert result["result"] == "unknown"
    assert "no browser check is named" in result["detail"]


def test_a_failed_assertion_is_fail():
    class Page:
        def goto(self, *args, **kwargs):
            pass

        def locator(self, selector):
            return Rows(["leo"] if selector == "[data-member]" else [])

    class Rows:
        def __init__(self, values):
            self.values = values

        def evaluate_all(self, script):
            return self.values

    try:
        family_demo_probes.landing_page_shows_every_member(
            Page(), {"base": "file:///x", "params": {"members": ["leo", "joe"]}})
    except family_demo_probes.Failed as exc:
        assert "no row for ['joe']" in str(exc)
    else:
        raise AssertionError("a page missing a member's row passed")


def test_bad_usage_exits_two(tmp_path):
    assert family_demo_probes.main(["terminal", "job.json"]) == 2
    assert family_demo_probes.main([]) == 2


def test_the_results_file_is_written_even_when_playwright_is_absent(tmp_path, monkeypatch):
    job, out = tmp_path / "job.json", tmp_path / "out.json"
    job.write_text(json.dumps({"checks": [{"member": "landing", "name": "x"}],
                               "out": str(out)}), encoding="utf-8")
    monkeypatch.setitem(sys.modules, "playwright", None)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", None)
    assert family_demo_probes.main(["browser", str(job)]) == 0
    [result] = json.loads(out.read_text(encoding="utf-8"))
    assert result["result"] == "unknown" and "playwright" in result["detail"]
