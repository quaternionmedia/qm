#!/usr/bin/env python3
"""The family stage, running: serve it, and check it by running the show.

    python family_stage_run.py serve <job.json>   # until interrupted
    python family_stage_run.py check <job.json>   # against a stage already up

`ci/family_demo.py --stage` writes the job and starts both, under the pinned
Playwright interpreter the demo's browser probe uses, so this file imports
nothing outside the standard library and Playwright except `family_stage`, its
stdlib-only neighbour, which decides everything that can be decided without
anything running.

**SERVE.** Creates the declared show in the hub through the hub's REST routes,
opens the stage's own browser session of each member whose panel is a session,
and answers on the job's port: the page, `state` (what the page polls), `go`
and `reset` (passed to the hub's programmer), `restart/<member>` (passed to the
harness holding the family, which started the member), and the pictures. A watcher
reads, and only reads: the hub's CueLog, the hub's `GET /family/`, and each
push member's `GET /family/state`. For each CueLog entry it records the cue,
what its family block asks of whom, what the hub says it delivered, and what
each member says now. A GO pressed in the hub's own programmer page is watched
the same way, because the log is what is watched, not this page's button.

**The stage sends no member anything.** The hub delivers every action. The one
thing the stage does in a member's page is joe's: joe's page shows a take only
once asked to fetch it, so when joe's own state names a new take, the stage
presses Fetch Latest in its own session of the page and pictures it. That is a
read; the take was joe's, started by the hub.

**CHECK.** Opens the stage page in a browser of its own, resets the hub to the
top, and for each cue presses GO. Then, without the stage's word for anything,
it asserts: the hub's CueLog gained an entry for that cue; for every member the
cue names, the hub's `GET /family/` lists a 2xx delivery of this very fire;
each push member's own `GET /family/state` names this fire and shows the state
its action asks for; leo's frame on the stage page, which follows the hub,
shows the song and says which cue asked for it. It saves a picture of the
stage after each cue. The pictures are recorded and never compared. Exit 0:
every assertion held. Exit 1: one did not. Any other status: the check could
not say, and its last line says why.

**The one place in this corpus that names a member's page.** A single member's
check lives in that member. The stage is a coordinated check of the links
between the hub and the members, so it reads two members' pages -- leo's chart
title and follow badge, joe's Fetch Latest button and what it shows -- and every
one of them is one the member's own walkthrough already drives. Nothing else in
`ci/` names one, and a test holds that.
"""

from __future__ import annotations

import json
import os
import queue
import re
import signal
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import family_stage as fs  # noqa: E402

# --- member pages, each one the member's own walkthrough already uses -----------

# joe: the results panel's toggle, its Fetch Latest button and what it shows.
JOE_RESULTS_TOGGLE = "[data-testid=results-toggle]"
JOE_FETCH = "[data-testid=fetch-latest]"
JOE_META = "[data-testid=results-meta]"

# leo: the chart's title, and the follow badge's words for the last cue.
LEO_TITLE = ".page__header__title"
LEO_FOLLOWING = ".follow-status__says"

SESSION_VIEWPORT = {"width": 1000, "height": 640}

# How long the hub's delivery may take to be listed as done: a push answers
# within the hub's timeout, and leo reads once a second.
DELIVERY_SECONDS = 30
# How long a member's own state may take to show a cue. joe's runs a pipeline.
SETTLE_SECONDS = {"joe": 240}
SETTLE_DEFAULT = 20
# How long `POST /restart/<member>` waits for the harness, when the job names none.
RESTART_SECONDS = 300

HUB_DOWN = "the hub stopped answering"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def http(method: str, url: str, params: dict | None = None, body=None, timeout: float = 10.0):
    """(status, decoded JSON or None). Never raises for an HTTP status; raises for no answer."""
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    data, headers = None, {}
    if isinstance(body, (dict, list)):
        data, headers = json.dumps(body).encode(), {"Content-Type": "application/json"}
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        raw, status = exc.read(), exc.code
    try:
        return status, json.loads(raw) if raw else None
    except ValueError:
        return status, raw[:200].decode("utf-8", "replace")


def read(url: str, timeout: float = 5.0):
    """The decoded JSON a GET answers with 2xx, or None however it fails."""
    try:
        status, answer = http("GET", url, timeout=timeout)
    except OSError:
        return None
    return answer if 200 <= status < 300 else None


def says(answer) -> str:
    """A member's own GET /family/state, in one line."""
    if not isinstance(answer, dict):
        return "not answering /family/state"
    cue = answer.get("cue") or {}
    state = answer.get("state") or {}
    return f"cue {cue.get('number', '-')}: " + ", ".join(f"{k} {json.dumps(v)}"
                                                        for k, v in state.items())


# ===================================================================
# SERVE
# ===================================================================

class Stage:
    """Everything the stage knows while it runs, behind one lock."""

    def __init__(self, job: dict):
        self.job = job
        self.lock = threading.Lock()
        self.ready = False
        self.failed = ""
        self.seeded: dict = {}
        self.pointer: int | None = None
        self.fired: list[dict] = []    # since the stage started or was last reset
        self.history: list[dict] = []  # every cue fired, for the record
        self.panels: dict = {}
        self.member_states: dict = {}  # member -> its last GET /family/state
        self.jobs: queue.Queue = queue.Queue()
        self.stopping = threading.Event()
        self.dir = Path(job["dir"])
        (self.dir / "live").mkdir(parents=True, exist_ok=True)
        self.hub = job["hub"].rstrip("/")
        # Where a restart is asked for and the harness says what it did.
        self.control = Path(job["control"]) if job.get("control") else None
        if self.control is not None:
            self.control.mkdir(parents=True, exist_ok=True)

    def snapshot(self) -> dict:
        with self.lock:
            snapshot = {"ready": self.ready, "failed": self.failed, "seeded": self.seeded,
                        "hub": {"pointer": self.pointer},
                        "fired": json.loads(json.dumps(self.fired)),
                        "panels": json.loads(json.dumps(self.panels)), "port": self.job["port"]}
        snapshot["dev"] = fs.read_events(self.control)
        return snapshot

    def record(self) -> None:
        with self.lock:
            document = {"seeded": self.seeded, "fired": self.history, "failed": self.failed,
                        "written_at": now()}
        target = self.dir / "stage.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(document, indent=2, default=str), encoding="utf-8")
        os.replace(temporary, target)

    # --- the hub ---------------------------------------------------------

    def call(self, method: str, path: str, params: dict | None = None, body=None):
        status, answer = http(method, self.hub + path, params=params, body=body)
        if not 200 <= status < 300:
            raise RuntimeError(f"{method} {path} answered {status}: {answer}")
        return answer

    def seed(self) -> None:
        self.seeded = fs.seed(self.job["show"], self.call)
        self.call("POST", "/programmer/reset")

    def watch(self) -> None:
        """Read the hub and the members, and record each cue the hub logs. Never write."""
        show = self.seeded["show_id"]
        seen = {entry["id"] for entry in self.call("GET", f"/db/shows/{show}/logs",
                                                   params={"limit": 500})}
        cues = {c["id"]: c for c in self.call("GET", f"/db/cue-lists/"
                                                     f"{self.seeded['cue_list_id']}/cues")}
        family: dict = {}
        while not self.stopping.is_set():
            try:
                # The hub's deliveries as they stood before this look at the log:
                # a cue first logged now fired after it, so none of its
                # deliveries is among them.
                previous = family
                family = read(self.hub + "/family/") or family
                entries = self.call("GET", f"/db/shows/{show}/logs", params={"limit": 50})
                status = self.call("GET", "/programmer/status")
                for entry in sorted(entries, key=lambda e: e["id"]):
                    if entry["id"] not in seen:
                        seen.add(entry["id"])
                        if entry.get("cue_id") is not None:
                            self.log(entry, cues.get(entry["cue_id"]), previous)
                states = {link["member"]: read(link["url"] + "/family/state", timeout=3)
                          for link in self.job["resolved"].values() if link["via"] == "push"}
                self.observe(status.get("pointer"), family, states)
                with self.lock:
                    # A hub that was restarted answers again, and says so here.
                    if self.failed.startswith(HUB_DOWN):
                        self.failed = ""
            except (OSError, RuntimeError, ValueError) as exc:
                with self.lock:
                    self.failed = f"{HUB_DOWN}: {exc}"
            self.stopping.wait(0.5)

    def log(self, entry: dict, cue: dict | None, family: dict) -> None:
        record = {"number": cue["number"] if cue else None, "name": cue["name"] if cue else None,
                  "cue_id": entry["cue_id"], "log_id": entry["id"],
                  "at": entry.get("triggered_at"), "seen_at": now(), "problems": [],
                  "asked": [], "deliveries": {}, "before": sorted(x for x in fs.fired_ats(family)
                                                                 if x)}
        if cue is None:
            record["problems"] = [f"the hub logged cue id {entry['cue_id']}, which is not "
                                  f"in the list"]
        else:
            actions, record["problems"] = fs.parse_family(cue.get("notes"), self.job["links"])
            record["asked"] = [{"name": a.name, "member": a.member, "action": a.value,
                                "summary": fs.summary(a),
                                "via": self.job["resolved"][a.name]["via"]} for a in actions]
        with self.lock:
            self.fired.append(record)
            self.history.append(record)
        self.record()

    def observe(self, pointer, family: dict, states: dict) -> None:
        with self.lock:
            self.pointer = pointer
            self.member_states = states
            for member, answer in states.items():
                self.panels.setdefault(member, {})["says"] = says(answer)
            for name, link in self.job["resolved"].items():
                if link["via"] == "pull":
                    read_ = [o for o in family.get("last") or [] if o.get("member") == name]
                    last = read_[-1] if read_ else None
                    self.panels.setdefault(link["member"], {})["says"] = (
                        "no cue has asked it for anything yet" if last is None else
                        f"cue {last['cue'].get('number')}: read from the hub "
                        f"{last['ms']} ms after it fired" if last.get("status") == 200 else
                        f"cue {last['cue'].get('number')}: not read yet")
            for record in self.fired[-3:]:
                record["deliveries"] = fs.deliveries(family, record["number"],
                                                     set(record["before"]))
                for asked in record["asked"]:
                    outcome = record["deliveries"].get(asked["name"]) or {}
                    if asked["via"] == "pull":
                        asked["says"] = "reads its action from the hub, following it"
                    elif outcome.get("cue"):
                        action = fs.Action(asked["name"], asked["member"],
                                           json.dumps(asked["action"], sort_keys=True))
                        verdict, detail = fs.judge(action, outcome["cue"],
                                                   states.get(asked["member"]))
                        asked["says"] = f"{verdict}: {detail}"

    def go(self) -> tuple[int, dict]:
        return http("POST", self.hub + "/programmer/go",
                    params={"cue_list_id": self.seeded["cue_list_id"],
                            "show_id": self.seeded["show_id"]})

    def reset(self) -> tuple[int, dict]:
        status, answer = http("POST", self.hub + "/programmer/reset")
        if 200 <= status < 300:
            with self.lock:
                self.fired = []
        return status, answer


class Sessions:
    """The stage's own browser: one page per session member, driven from one thread."""

    def __init__(self, stage: Stage, playwright):
        self.stage = stage
        self.browser = playwright.chromium.launch()
        self.pages: dict = {}
        self.shots: dict[str, int] = {}
        self.shown: dict[str, object] = {}

    def open(self) -> None:
        for member, panel in self.stage.job["panels"].items():
            if panel["shows"] != "session":
                continue
            try:
                getattr(self, f"open_{member}")(panel["url"])
                self.picture(member)
            except Exception as exc:  # a session that will not open is reported, not fatal
                with self.stage.lock:
                    self.stage.panels.setdefault(member, {})["error"] = \
                        f"{type(exc).__name__}: {exc}"

    def page(self, member: str):
        page = self.browser.new_context(viewport=SESSION_VIEWPORT).new_page()
        self.pages[member] = page
        return page

    def open_joe(self, url: str) -> None:
        page = self.page("joe")
        page.goto(url)
        page.wait_for_selector(JOE_FETCH, state="attached", timeout=30000)
        page.click(JOE_RESULTS_TOGGLE)

    def refresh_joe(self, answer) -> None:
        """When joe's own state names a new take, fetch it in the stage's session."""
        latest = ((answer or {}).get("state") or {}).get("latest") or {}
        if not latest.get("file") or latest.get("file") == self.shown.get("joe"):
            return
        page = self.pages["joe"]
        page.evaluate(f"() => document.querySelector('{JOE_FETCH}').click()")
        stem = latest["file"].rsplit(".", 1)[0]
        try:
            page.wait_for_function(
                f"(stem) => (document.querySelector('{JOE_META}').textContent || '').includes(stem)",
                arg=stem, timeout=20000)
        except Exception:
            pass
        self.shown["joe"] = latest["file"]
        self.picture("joe", latest["file"])

    def picture(self, member: str, showing: str | None = None) -> None:
        page = self.pages.get(member)
        if page is None:
            return
        number = self.shots.get(member, 0) + 1
        name = f"{member}-{number}.png"
        page.screenshot(path=str(self.stage.dir / "live" / name))
        self.shots[member] = number
        with self.stage.lock:
            panel = self.stage.panels.setdefault(member, {})
            panel["shot"] = f"live/{name}"
            panel["showing"] = showing
        stale = self.stage.dir / "live" / f"{member}-{number - 3}.png"
        try:
            stale.unlink()
        except OSError:
            pass

    def run(self) -> None:
        while not self.stage.stopping.is_set():
            with self.stage.lock:
                states = dict(self.stage.member_states)
            for member in self.pages:
                try:
                    getattr(self, f"refresh_{member}")(states.get(member))
                except Exception:
                    with self.stage.lock:
                        self.stage.panels.setdefault(member, {})["error"] = \
                            traceback.format_exc(limit=2)
            self.stage.stopping.wait(0.5)

    def close(self) -> None:
        try:
            self.browser.close()
        except Exception:
            pass


def worker(stage: Stage) -> None:
    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as playwright:
            sessions = Sessions(stage, playwright)
            try:
                sessions.open()
                with stage.lock:
                    stage.ready = True
                sessions.run()
            finally:
                sessions.close()
    except Exception as exc:
        with stage.lock:
            stage.failed = f"the stage's browser failed: {type(exc).__name__}: {exc}"
        stage.stopping.set()


def restart(stage: Stage, member: str) -> tuple[int, dict]:
    """`POST /restart/<member>`: ask the harness holding the family, and pass on its answer.

    The stage started no member, so it restarts none: the harness that started
    them does, and says how the member came back.
    """
    if member not in stage.job["order"]:
        return 404, {"member": member, "result": "refused",
                     "detail": f"{member!r} is not a member this stage runs: {stage.job['order']}"}
    if stage.control is None:
        return 409, {"member": member, "result": "refused",
                     "detail": "this stage was started without a control directory"}
    answer = fs.request_restart(stage.control, member,
                                float(stage.job.get("restart_seconds", RESTART_SECONDS)))
    return fs.restart_status(answer), answer


def handler(stage: Stage, page_html: str):
    live = stage.dir / "live"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status: int, body: bytes, kind: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def json(self, status: int, value) -> None:
            self.send(status, json.dumps(value, default=str).encode(), "application/json")

        def do_GET(self):  # noqa: N802
            path = urllib.parse.urlparse(self.path).path
            if path == "/":
                if stage.ready:
                    return self.send(200, page_html.encode(), "text/html; charset=utf-8")
                return self.send(503, b"the stage is starting", "text/plain")
            if path == "/state":
                return self.json(200, stage.snapshot())
            if path == "/healthz":
                return self.json(200 if stage.ready else 503,
                                 {"ready": stage.ready, "port": self.server.server_address[1],
                                  "failed": stage.failed})
            if path.startswith("/live/"):
                name = Path(path).name
                file = live / name
                if re.fullmatch(r"[A-Za-z]+-\d+\.png", name) and file.is_file():
                    for _ in range(5):
                        try:
                            return self.send(200, file.read_bytes(), "image/png")
                        except OSError:
                            time.sleep(0.05)
            return self.send(404, b"not here", "text/plain")

        def do_POST(self):  # noqa: N802
            path = urllib.parse.urlparse(self.path).path
            if not stage.ready:
                return self.json(503, {"detail": "the stage is starting"})
            try:
                if path == "/go":
                    return self.json(*stage.go())
                if path == "/reset":
                    return self.json(*stage.reset())
            except OSError as exc:
                return self.json(502, {"detail": f"the hub did not answer: {exc}"})
            if path.startswith("/restart/"):
                return self.json(*restart(stage, urllib.parse.unquote(path[len("/restart/"):])))
            return self.json(404, {"detail": "not here"})

    return Handler


class Server(ThreadingHTTPServer):
    # Not SO_REUSEADDR: on Windows it would let the stage bind a port somebody
    # else is already listening on.
    allow_reuse_address = False
    daemon_threads = True


def serve(job: dict) -> int:
    stage = Stage(job)
    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), lambda *_: stage.stopping.set())
    try:
        stage.seed()
    except (OSError, RuntimeError, KeyError) as exc:
        print(f"could not seed the show in the hub: {exc}", flush=True)
        return 3
    stage.record()
    print(f"seeded {json.dumps(stage.seeded)}", flush=True)
    page_html = fs.stage_page({"show": job["show"], "hub_url": job["hub"], "order": job["order"],
                               "links": job["links"], "panels": job["panels"],
                               "rows": job["rows"]})
    server = Server((job["host"], job["port"]), handler(stage, page_html))
    threads = [threading.Thread(target=server.serve_forever, daemon=True),
               threading.Thread(target=stage.watch, daemon=True),
               threading.Thread(target=worker, args=(stage,), daemon=True)]
    for thread in threads:
        thread.start()
    print(f"stage on http://{job['host']}:{job['port']}/", flush=True)
    while not stage.stopping.wait(0.5):
        pass
    server.shutdown()
    threads[2].join(timeout=15)
    stage.record()
    print(f"stopped{': ' + stage.failed if stage.failed else ''}", flush=True)
    return 0


# ===================================================================
# CHECK
# ===================================================================

expect = None  # Playwright's, bound when a check runs


def check(job: dict) -> int:
    from playwright.sync_api import sync_playwright

    global expect
    from playwright.sync_api import expect

    url = f"http://{job['host']}:{job['port']}/"
    hub = job["hub"].rstrip("/")
    shots = Path(job["shots"])
    shots.mkdir(parents=True, exist_ok=True)
    out = Path(job["result"])
    result: dict = {"stage": url, "started_at": now(), "cues": []}

    def finish(code: int, why: str = "") -> int:
        result["finished_at"] = now()
        result["result"] = {0: "pass", 1: "fail"}.get(code, "unknown")
        result["why"] = why
        out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        print(why or f"{result['result']}: {len(result['cues'])} cue(s)", flush=True)
        return code

    # Which show the stage made is the stage's word; what that show holds is the hub's.
    try:
        seeded = http("GET", url + "state")[1]["seeded"]
        show = http("GET", f"{hub}/db/shows/{seeded['show_id']}")[1]
        cue_list = next(c for c in http("GET", f"{hub}/db/shows/{show['id']}/cue-lists")[1]
                        if c["id"] == seeded["cue_list_id"])
        cues = http("GET", f"{hub}/db/cue-lists/{cue_list['id']}/cues")[1]
        members = http("GET", f"{hub}/family/")[1]["members"]
    except (OSError, StopIteration, TypeError, KeyError) as exc:
        return finish(3, f"could not read the show from the hub: {exc!r}")
    if (show["name"], cue_list["name"]) != (job["show"]["name"], job["show"]["cue_list"]):
        return finish(1, f"the hub holds {show['name']!r}/{cue_list['name']!r}, not the declared show")
    declared = [(c["number"], c["name"]) for c in job["show"]["cues"]]
    if [(int(c["number"]), c["name"]) for c in cues] != declared:
        return finish(1, f"the hub's cues {[(c['number'], c['name']) for c in cues]} "
                         f"are not the declared {declared}")
    # The hub's own table of who it delivers to, against the links the stage declared.
    told = {name: ({"via": "push", "url": link["url"]} if link["via"] == "push"
                   else {"via": "pull"}) for name, link in job["resolved"].items()}
    result["hub_members"] = members
    if members != told:
        return finish(1, f"the hub's [plugins.family] is {members}, not the declared links {told}")
    result["hub_show"] = {"show_id": show["id"], "cue_list_id": cue_list["id"],
                          "cues": [{"id": c["id"], "number": c["number"], "name": c["name"]}
                                   for c in cues]}

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except Exception as exc:
            return finish(3, f"chromium did not launch: {exc}")
        page = browser.new_page(viewport={"width": 1440, "height": 1300})
        console: list[str] = []
        page.on("console", lambda m: console.append(m.text) if m.type == "error" else None)
        try:
            page.goto(url, wait_until="load")
            page.click("#reset")
            page.wait_for_function("() => document.getElementById('status').textContent"
                                   ".includes('back at the top')", timeout=15000)
            for index, cue in enumerate(cues, start=1):
                result["cues"].append(run_cue(page, cue, index, hub, show["id"], job, url, shots))
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}"
            result["console_errors"] = console[:20]
            browser.close()
            return finish(3, f"the check could not finish: {result['error']}")
        result["console_errors"] = console[:20]
        browser.close()
    verdict = fs.combine([c["result"] for c in result["cues"]])
    return finish({"pass": 0, "fail": 1}.get(verdict, 3))


def poll(read_once, done, seconds: float, page):
    """Call `read_once` until `done(value)` or time runs out; return the last value."""
    deadline = time.monotonic() + seconds
    value = read_once()
    while not done(value) and time.monotonic() < deadline:
        page.wait_for_timeout(250)
        value = read_once()
    return value


def run_cue(page, cue: dict, index: int, hub: str, show_id: int, job: dict, url: str,
            shots: Path) -> dict:
    """GO once, then assert what the hub delivered and what each member says, and picture it."""
    record = {"number": cue["number"], "name": cue["name"], "assertions": []}

    def held(what: str, ok, detail: str = "", by: str = "check", **about) -> None:
        result = ok if isinstance(ok, str) else ("pass" if ok else "fail")
        record["assertions"].append({"what": what, "result": result, "detail": detail,
                                     "by": by, **about})

    number = cue["number"]
    wanted, problems = fs.parse_family(cue.get("notes"), job["links"])
    before_logs = {e["id"] for e in http("GET", f"{hub}/db/shows/{show_id}/logs",
                                         params={"limit": 500})[1]}
    before = fs.fired_ats(http("GET", f"{hub}/family/")[1])
    page.click("#go")
    page.wait_for_function(
        "(n) => document.getElementById('status').textContent"
        ".startsWith(`the hub fired cue ${n},`)", arg=str(number), timeout=30000)

    logged = poll(lambda: [e for e in http("GET", f"{hub}/db/shows/{show_id}/logs",
                                           params={"limit": 500})[1] if e["id"] not in before_logs],
                  bool, 15, page)
    held("the hub's CueLog gained an entry for this cue",
         [e["cue_id"] for e in logged] == [cue["id"]],
         f"new entries name cue ids {[e['cue_id'] for e in logged]}; this cue is {cue['id']}",
         by="the hub's /db/shows/{id}/logs")
    held("the cue's family block, as the hub holds it, names linked members and spec actions",
         not problems, "; ".join(problems) or ", ".join(f"{a.name} {fs.summary(a)}"
                                                        for a in wanted),
         by="family_stage.parse_family")

    for action in wanted:
        link = job["resolved"][action.name]
        member = action.member

        def listed():
            return fs.deliveries(http("GET", f"{hub}/family/")[1], number, before).get(action.name)

        outcome = poll(listed, lambda o: bool(o and o.get("done")), DELIVERY_SECONDS, page) or {}
        status = outcome.get("status")
        delivered = isinstance(status, int) and 200 <= status < 300
        detail = (f"{link['via']}: {status} in {outcome.get('ms')} ms"
                  + (f" -- {outcome['error']}" if outcome.get("error") else "")) if outcome else \
            f"the hub listed no delivery to {action.name} for this fire"
        held(f"the hub delivered cue {number} to {member} ({action.name})", delivered, detail,
             by="the hub's GET /family/", member=member, kind="delivery")
        fired = outcome.get("cue") or {}

        if link["via"] == "push":
            if not fired:
                held(f"{member}'s own state shows cue {number}: {fs.summary(action)}", False,
                     "no delivery of this fire to judge it against", by=f"{member}'s GET "
                     "/family/state", member=member, kind="state")
                continue
            judged = poll(lambda: fs.judge(action, fired, read(link["url"] + "/family/state")),
                          lambda v: v[0] != "wait",
                          SETTLE_SECONDS.get(member, SETTLE_DEFAULT), page)
            held(f"{member}'s own state shows cue {number}: {fs.summary(action)}",
                 judged[0] == "pass", judged[1], by=f"{member}'s GET /family/state",
                 member=member, kind="state")
        elif member == "leo":
            song = action.value["song"]
            title = page.frame_locator("#frame-leo").locator(LEO_TITLE).first
            badge = page.frame_locator("#frame-leo").locator(LEO_FOLLOWING).first
            try:
                expect(title).to_have_text(song, timeout=20000)
                expect(badge).to_contain_text(f"cue {number}", timeout=5000)
                shown, says_ = song, badge.text_content(timeout=2000)
            except AssertionError:
                shown = title.text_content(timeout=2000) if title.count() else None
                says_ = badge.text_content(timeout=2000) if badge.count() else None
            held(f"leo, following the hub, shows {song} for cue {number}",
                 shown == song and bool(re.match(rf"cue {number}[,:]", says_ or "")),
                 f"title reads {shown!r}; its follow badge says {says_!r}",
                 by="leo's own page, in the stage's frame", member=member, kind="page")
        else:
            held(f"{member} pulls cue {number}", "unknown",
                 "the stage has no way to see a pull member other than leo",
                 by="check", member=member, kind="page")

    sessions = [a.member for a in wanted if job["panels"][a.member]["shows"] == "session"]
    if sessions:
        try:
            page.wait_for_function(
                """(members) => members.every(m => { const i = document.getElementById('shot-' + m);
                     return i && !i.hidden && i.dataset.shown && i.dataset.shown === i.dataset.want; })""",
                arg=sessions, timeout=30000)
        except Exception:
            held("the stage's own session pictured the member after the cue", "unknown",
                 f"no fresh picture of {sessions} within 30s", by="the stage page")
    page.wait_for_timeout(1500)
    shot = shots / f"{index:02d}-cue-{number}.png"
    page.screenshot(path=str(shot), full_page=True)
    record["shot"] = str(shot)
    record["result"] = fs.combine([a["result"] for a in record["assertions"]])
    return record


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2 or argv[0] not in ("serve", "check"):
        print("usage: family_stage_run.py serve|check <job.json>", file=sys.stderr)
        return 2
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    job = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    return serve(job) if argv[0] == "serve" else check(job)


if __name__ == "__main__":
    sys.exit(main())
