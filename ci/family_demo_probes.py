#!/usr/bin/env python3
"""The demo's own browser check: its page, while every member is up.

    python family_demo_probes.py browser <job.json>

**NO MEMBER'S CHECK IS HERE.** A check of one member alone lives in that
member, behind the contract's `check` command (`ci/family-demo.yaml`), because
the member owns its selectors and what its screen must show. What is here is
the one browser check that belongs to the demo itself: the page it writes has a
row for every member that ran, and every picture it embeds loads.

**RUN UNDER ANOTHER INTERPRETER, NOT THIS CORPUS'S.** It runs in an environment
holding only the pinned Playwright, so it imports nothing from `ci/` and
nothing outside the standard library at module level, and the harness hands it
a job as JSON and reads the results back the same way.

**THREE RESULTS, AND THEY ARE NOT INTERCHANGEABLE.** `pass` is an assertion that
held. `fail` is an assertion that did not. `unknown` is a check that could not
be evaluated -- the probe crashed, the browser would not launch -- and it is
never reported as `fail`, because a broken probe says nothing about the page.
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path


class Failed(AssertionError):
    """An assertion that did not hold."""


def check(condition: bool, message: str) -> None:
    if not condition:
        raise Failed(message)


def landing_page_shows_every_member(page, job: dict) -> dict:
    """The generated page has a row per member, and every picture it embeds loads."""
    page.goto(job["base"], wait_until="load")
    rows = page.locator("[data-member]").evaluate_all(
        "rows => rows.map(r => r.dataset.member)")
    missing = [name for name in job["params"]["members"] if name not in rows]
    check(not missing, f"no row for {missing}")
    images = page.locator("img").evaluate_all(
        "imgs => imgs.map(i => ({src: i.getAttribute('src'), ok: i.complete && i.naturalWidth > 0}))")
    broken = [image["src"] for image in images if not image["ok"]]
    check(not broken, f"pictures that did not load: {broken}")
    return {"rows": rows, "images": len(images)}


BROWSER = {
    "landing-page-shows-every-member": landing_page_shows_every_member,
}


def run_browser(job: dict) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        return [unknown(c, f"playwright is not importable here: {exc}") for c in job["checks"]]

    results = []
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except Exception as exc:  # no browser build for this Playwright
            return [unknown(c, f"chromium did not launch: {exc}") for c in job["checks"]]
        try:
            for entry in job["checks"]:
                results.append(one_browser_check(browser, entry))
        finally:
            browser.close()
    return results


def one_browser_check(browser, entry: dict) -> dict:
    started = time.monotonic()
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    console: list[str] = []
    page.on("console", lambda m: console.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: console.append(f"pageerror: {e}"))
    outcome = {"member": entry["member"], "check": entry["name"], "runner": "browser"}
    try:
        function = BROWSER.get(entry["name"])
        if function is None:
            raise LookupError(f"no browser check is named {entry['name']!r}")
        outcome.update(result="pass", detail="", evidence=function(page, entry))
    except Failed as exc:
        outcome.update(result="fail", detail=str(exc), evidence={})
    except Exception as exc:
        # Playwright's timeout is a behaviour that did not happen; anything
        # else is the probe failing, which says nothing about the page.
        timed_out = type(exc).__name__ == "TimeoutError"
        outcome.update(result="fail" if timed_out else "unknown",
                       detail=f"{type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}",
                       evidence={"trace": traceback.format_exc(limit=3)})
    outcome["shot"] = None
    if entry.get("shot"):
        try:
            Path(entry["shot"]).parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=entry["shot"], full_page=True)
            outcome["shot"] = entry["shot"]
        except Exception as exc:
            outcome["shot_error"] = str(exc)
    outcome["console_errors"] = console[:20]
    outcome["seconds"] = round(time.monotonic() - started, 3)
    page.close()
    context.close()
    return outcome


def unknown(entry: dict, why: str) -> dict:
    return {"member": entry["member"], "check": entry["name"], "result": "unknown",
            "detail": why, "evidence": {}, "shot": None, "console_errors": [],
            "seconds": 0.0}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2 or argv[0] != "browser":
        print("usage: family_demo_probes.py browser <job.json>", file=sys.stderr)
        return 2
    job = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    Path(job["out"]).write_text(json.dumps(run_browser(job), indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
