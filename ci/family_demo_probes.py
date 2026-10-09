#!/usr/bin/env python3
"""The behavioural checks `ci/family_demo.py` runs against each member's surface.

    python family_demo_probes.py browser <job.json>
    python family_demo_probes.py terminal <job.json>

**RUN UNDER ANOTHER INTERPRETER, NOT THIS CORPUS'S.** The browser checks run in
an environment holding only the pinned Playwright; the terminal check runs in
the member's own environment, so it drives the Textual the member installed and
not one this corpus chose. So this file imports nothing from `ci/` and nothing
outside the standard library at module level, and the harness hands it a job
as JSON and reads the results back the same way.

**A SCREENSHOT IS A BYPRODUCT, NEVER THE CHECK.** Each check drives the real
component through a real gesture and asserts what it did -- a show created
through the hub's API reaching its dashboard, a rack drawing every module of the
document its server serves, a recording dropped into this run's scratch
directory reaching the page through the dev server's proxy. The picture is taken
from the render that assertion ran against, recorded and never compared
(`records/DRAFT-one-executable-walkthrough.md` §4). A failing check still takes
its picture, labelled as the failing state.

**THREE RESULTS, AND THEY ARE NOT INTERCHANGEABLE.** `pass` is an assertion that
held. `fail` is an assertion that did not, or a behaviour that did not happen
within its budget. `unknown` is a check that could not be evaluated -- the probe
crashed, the browser would not launch -- and it is never reported as `fail`,
because a broken probe says nothing about the member.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import traceback
import urllib.parse
import urllib.request
from pathlib import Path

# How long one behaviour may take to show up on screen, in milliseconds. A
# timeout here is a `fail` with the observed state in its detail, because the
# server already answered its readiness probe before any check began.
BEHAVIOUR_MS = 20000


class Failed(AssertionError):
    """An assertion about the member that did not hold."""


def check(condition: bool, message: str) -> None:
    if not condition:
        raise Failed(message)


def get_json(url: str, method: str = "GET"):
    request = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def origin(url: str) -> str:
    """Scheme, host and port: where a member's API lives, whatever page it opens on."""
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def same_path(left: str | None, right: str) -> bool:
    if not left:
        return False
    return os.path.normcase(os.path.realpath(left)) == os.path.normcase(os.path.realpath(right))


# ===================================================================
# BROWSER CHECKS -- each takes (page, check) and returns evidence
# ===================================================================

def showrunner_show_reaches_dashboard(page, job: dict) -> dict:
    """A show created through the hub's API is the show its dashboard selects.

    The scratch database must be empty first: a show already present means the
    answering process is not reading this run's database, which is the stale
    process the plan's hazards name.
    """
    base = origin(job["base"])
    before = get_json(f"{base}/db/shows")
    check(before == [], f"scratch database was not empty before the check: {before!r}")
    name = f"Family demo {job['token']}"
    created = get_json(f"{base}/db/shows?{urllib.parse.urlencode({'name': name})}",
                       method="POST")
    check(created.get("name") == name, f"POST /db/shows answered {created!r}")
    listed = [show.get("name") for show in get_json(f"{base}/db/shows")]
    check(listed == [name], f"GET /db/shows after the write listed {listed!r}")

    page.goto(f"{base}/", wait_until="load")
    page.get_by_text("Show Control Dashboard").wait_for(timeout=BEHAVIOUR_MS)
    selected = page.locator("header").get_by_text(name, exact=True)
    try:
        selected.first.wait_for(timeout=BEHAVIOUR_MS)
    except Exception as exc:
        header = page.locator("header").inner_text(timeout=2000)
        raise Failed(f"dashboard header never showed {name!r}; it read {header!r}") from exc
    return {"show": name, "shows_before": before, "shows_after": listed}


def carlos_rack_draws_the_opening_document(page, job: dict) -> dict:
    """The rack draws every module and every lead of the document it serves.

    The expected counts are read from the server's own `/api/opening`, not
    written here, so the check follows the member when its opening rig changes.
    `/healthz` is asked first: the port it reports is the socket that answered
    and the database is the resolved path, so a stale server or a shared
    database is caught before anything is attributed to this run.
    """
    base = origin(job["base"])
    health = get_json(f"{base}/healthz")
    identity = {key: health.get(key) for key in ("instance", "pid", "port", "database")}
    check(str(health.get("port")) == str(job["params"]["port"]),
          f"/healthz reports port {health.get('port')!r}, not the reserved one")
    check(same_path(health.get("database"), job["params"]["database"]),
          f"/healthz reports database {health.get('database')!r}, not this run's scratch file")

    opening = get_json(f"{base}/api/opening")
    modules, leads = len(opening["modules"]), len(opening["connections"])

    page.goto(f"{base}/", wait_until="load")
    check(page.url.rstrip("/").endswith("/rack"), f"the bare port landed on {page.url}")
    drawn = until(page, "n => document.querySelectorAll('.module').length === n", modules,
                  "document.querySelectorAll('.module').length")
    check(drawn == modules, f"rack drew {drawn} modules; /api/opening holds {modules}")
    script = ("n => new Set([...document.querySelectorAll('path.cable')]"
              ".map(p => p.dataset.cable)).size === n")
    cables = until(page, script, leads,
                   "new Set([...document.querySelectorAll('path.cable')]"
                   ".map(p => p.dataset.cable)).size")
    check(cables == leads, f"rack drew {cables} leads; /api/opening holds {leads}")
    return {"healthz": identity, "modules": modules, "leads": leads}


def joe_library_lists_the_scratch_recording(page, job: dict) -> dict:
    """A recording placed in this run's scratch directory reaches the page.

    The file name carries the run's token, so it can only have come from the
    API this run started -- the dev server's proxy is what joins the page to an
    API, and a proxy pointed anywhere else would list some other directory.
    """
    base = job["base"]
    name = job["params"]["recording"]
    proxied = [entry.get("name") for entry in get_json(f"{origin(base)}/api/audio/files")]
    check(name in proxied, f"/api/audio/files through the dev server listed {proxied!r}")

    page.goto(base, wait_until="load")
    listing = page.locator('[data-testid="capture-file-list"]')
    try:
        listing.get_by_text(name).first.wait_for(state="attached", timeout=BEHAVIOUR_MS)
    except Exception as exc:
        shown = listing.inner_text(timeout=2000) if listing.count() else "<no list>"
        raise Failed(f"the library never listed {name!r}; it read {shown!r}") from exc
    page.locator('[data-testid="capture-toggle"]').click()
    page.locator('[data-testid="capture-panel"].open').wait_for(timeout=BEHAVIOUR_MS)
    # Opening is a slide, so the class arrives before the panel does. The
    # recording's name inside the viewport is what a person would see.
    try:
        page.wait_for_function(
            """name => [...document.querySelectorAll('[data-testid="capture-file-list"] *')]
                .filter(e => e.textContent.trim() === name || e.childElementCount === 0
                             && e.textContent.includes(name))
                .some(e => { const r = e.getBoundingClientRect();
                             return r.width > 0 && r.left >= 0 && r.right <= innerWidth; })""",
            arg=name, timeout=BEHAVIOUR_MS)
    except Exception as exc:
        raise Failed(f"the library opened but {name!r} never came into view") from exc
    return {"recording": name, "listed_through_proxy": proxied}


def leo_search_selects_a_song(page, job: dict) -> dict:
    """Searching the setlist for a title narrows it, and choosing it shows it.

    The title is read off the page -- the first of the setlist's own sorted
    list -- rather than written here, so the check does not depend on which
    songbooks a commit ships. The page's own result count is read beside the
    songs it lists, before and after the search, so a list that disagrees with
    its own count is reported as that rather than as a missing song.
    """
    base = job["base"]
    page.goto(base, wait_until="load")
    page.locator(".page__header__title").wait_for(timeout=BEHAVIOUR_MS)
    page.locator(".nav_left__toggle").click()
    titles = page.locator(".setlist__songbox__song .title")
    titles.first.wait_for(timeout=BEHAVIOUR_MS)
    counted = page.locator(".results-count")
    says_all, total = counted.inner_text().strip(), titles.count()
    target = titles.first.inner_text().strip()
    check(bool(target), "the first song in the setlist has no title")

    page.locator(".setlist__header__search__input").fill(target)
    try:
        page.wait_for_function(
            "before => (document.querySelector('.results-count') || {}).textContent"
            "?.trim() !== before", arg=says_all, timeout=BEHAVIOUR_MS)
    except Exception as exc:
        raise Failed(f"searching {target!r} left the count at {says_all!r}") from exc
    says = counted.inner_text().strip()
    # Exact match read in Python: a title is free text, and escaping it into a
    # regular expression the browser compiles is a second grammar to get right.
    remaining = [text.strip() for text in titles.all_inner_texts()]
    narrowed = len(remaining)
    check(narrowed < total, f"searching {target!r} left {narrowed} of {total} songs")
    check(target in remaining,
          f"searching {target!r}: the setlist says {says!r} and lists {narrowed} "
          f"song(s) {remaining[:3]!r}; unfiltered it says {says_all!r} and lists {total}")
    page.locator("button.setlist__songbox__song").nth(remaining.index(target)).click()
    heading = page.locator(".page__header__title")
    try:
        page.wait_for_function(
            "t => (document.querySelector('.page__header__title') || {}).textContent"
            "?.trim() === t", arg=target, timeout=BEHAVIOUR_MS)
    except Exception as exc:
        raise Failed(f"chose {target!r}; the page shows {heading.inner_text()!r}") from exc
    return {"song": target, "setlist": total, "after_search": narrowed,
            "route": page.url.split("#", 1)[-1]}


def showstopper_served_app_streams(page, job: dict) -> dict:
    """The served stopwatch streams its own screen to a browser.

    `textual serve` starts the app per connection and sends its output over a
    websocket. This asserts a frame carrying the app's own button label arrived;
    the terminal is drawn on a canvas, so what the frame says is checked rather
    than what the canvas shows. It is the surface, not the behaviour: the
    timing assertion is the terminal check.
    """
    seen: list[str] = []

    def collect(payload) -> None:
        text = payload.decode("utf-8", "replace") if isinstance(payload, bytes) else str(payload)
        seen.append(text)

    sockets: list[str] = []

    def attach(socket) -> None:
        # Attached as the socket opens, so no frame arrives before the listener.
        sockets.append(socket.url)
        socket.on("framereceived", collect)

    page.on("websocket", attach)
    page.goto(job["base"], wait_until="load")
    # Polling a condition with a deadline; the waits pump Playwright's events.
    deadline = time.monotonic() + BEHAVIOUR_MS / 1000
    while time.monotonic() < deadline and not any("Start" in frame for frame in seen):
        page.wait_for_timeout(100)
    check(bool(sockets), "the served page opened no websocket")
    check(any("Start" in frame for frame in seen),
          f"{len(seen)} frames arrived and none carried the app's Start button")
    return {"frames_until_start_label": len(seen), "sockets": sockets}


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
    "showrunner-show-reaches-dashboard": showrunner_show_reaches_dashboard,
    "carlos-rack-draws-the-opening-document": carlos_rack_draws_the_opening_document,
    "joe-library-lists-the-scratch-recording": joe_library_lists_the_scratch_recording,
    "leo-search-selects-a-song": leo_search_selects_a_song,
    "showstopper-served-app-streams": showstopper_served_app_streams,
    "landing-page-shows-every-member": landing_page_shows_every_member,
}


def until(page, predicate: str, argument, reading: str) -> int:
    """Wait for a predicate, and return what the page actually holds either way.

    The value is read back after the wait, so a timeout reports the count the
    page reached rather than the count it was hoped for.
    """
    try:
        page.wait_for_function(predicate, arg=argument, timeout=BEHAVIOUR_MS)
    except Exception:
        pass
    return int(page.evaluate(reading))


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
    outcome = {"member": entry["member"], "check": entry["name"], "runner": "browser",
               "counts": entry.get("counts", "behaviour")}
    try:
        function = BROWSER.get(entry["name"])
        if function is None:
            raise LookupError(f"no browser check is named {entry['name']!r}")
        outcome.update(result="pass", detail="", evidence=function(page, entry))
    except Failed as exc:
        outcome.update(result="fail", detail=str(exc), evidence={})
    except Exception as exc:
        # Playwright's timeout is a behaviour that did not happen; anything
        # else is the probe failing, which says nothing about the member.
        timed_out = type(exc).__name__ == "TimeoutError"
        outcome.update(result="fail" if timed_out else "unknown",
                       detail=f"{type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}",
                       evidence={"trace": traceback.format_exc(limit=3)})
    outcome["shot"] = None
    if entry.get("shot"):
        try:
            Path(entry["shot"]).parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=entry["shot"], full_page=entry["name"].startswith("landing"))
            outcome["shot"] = entry["shot"]
        except Exception as exc:
            outcome["shot_error"] = str(exc)
    outcome["console_errors"] = console[:20]
    outcome["seconds"] = round(time.monotonic() - started, 3)
    # The tab first, as a person closes one, then the context.
    page.close()
    context.close()
    return outcome


# ===================================================================
# TERMINAL CHECK -- ShowStopper's own App, under its own Textual
# ===================================================================

async def showstopper_stopwatch_counts_and_holds(entry: dict) -> dict:
    """Start counts, stop holds the count, reset returns to zero.

    Driven through Textual's pilot -- the same widgets and bindings a person
    gets -- against the member's own `StopwatchApp`. The time is read off the
    widget's reactive state and its rendered digits, and the pause between
    start and stop is the behaviour under test, not a wait for readiness.
    """
    checkout = entry["checkout"]
    sys.dont_write_bytecode = True  # importing the member must not write into it
    sys.path.insert(0, checkout)
    os.chdir(checkout)
    import textual
    import stopwatch

    app = stopwatch.StopwatchApp()
    async with app.run_test(size=(110, 30)) as pilot:
        first = app.query(stopwatch.Stopwatch).first()
        display = first.query_one(stopwatch.TimeDisplay)
        check(display.time == 0, f"a new stopwatch reads {display.time}")
        await pilot.click(first.query_one("#start"))
        await pilot.pause(0.5)
        check(first.has_class("started"), "Start did not mark the stopwatch started")
        await pilot.click(first.query_one("#stop"))
        await pilot.pause()
        stopped = display.time
        check(stopped > 0, f"after running, the stopwatch reads {stopped}")
        await pilot.pause(0.3)
        check(display.time == stopped,
              f"a stopped stopwatch moved from {stopped} to {display.time}")
        shown = str(display.value)
        check(shown != "00:00:00.00", f"the digits still read {shown}")
        if entry.get("shot"):
            Path(entry["shot"]).parent.mkdir(parents=True, exist_ok=True)
            app.save_screenshot(filename=Path(entry["shot"]).name,
                                path=str(Path(entry["shot"]).parent))
        await pilot.click(first.query_one("#reset"))
        await pilot.pause()
        check(display.time == 0, f"after reset the stopwatch reads {display.time}")
    return {"stopped_at_seconds": round(stopped, 3), "digits": shown,
            "textual": textual.__version__}


TERMINAL = {
    "showstopper-stopwatch-counts-and-holds": showstopper_stopwatch_counts_and_holds,
}


def run_terminal(job: dict) -> list[dict]:
    results = []
    for entry in job["checks"]:
        started = time.monotonic()
        outcome = {"member": entry["member"], "check": entry["name"], "runner": "terminal",
                   "counts": entry.get("counts", "behaviour"), "console_errors": []}
        try:
            function = TERMINAL.get(entry["name"])
            if function is None:
                raise LookupError(f"no terminal check is named {entry['name']!r}")
            outcome.update(result="pass", detail="", evidence=asyncio.run(function(entry)))
        except Failed as exc:
            outcome.update(result="fail", detail=str(exc), evidence={})
        except Exception as exc:
            outcome.update(result="unknown", detail=f"{type(exc).__name__}: {exc}",
                           evidence={"trace": traceback.format_exc(limit=3)})
        shot = entry.get("shot")
        outcome["shot"] = shot if shot and Path(shot).is_file() else None
        outcome["seconds"] = round(time.monotonic() - started, 3)
        results.append(outcome)
    return results


def unknown(entry: dict, why: str) -> dict:
    return {"member": entry["member"], "check": entry["name"], "result": "unknown",
            "detail": why, "evidence": {}, "shot": None, "console_errors": [],
            "counts": entry.get("counts", "behaviour"), "seconds": 0.0}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2 or argv[0] not in ("browser", "terminal"):
        print("usage: family_demo_probes.py browser|terminal <job.json>", file=sys.stderr)
        return 2
    job = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    results = run_browser(job) if argv[0] == "browser" else run_terminal(job)
    Path(job["out"]).write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
