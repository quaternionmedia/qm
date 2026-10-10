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
and `reset` (passed to the hub's programmer), and the pictures. A watcher
reads the hub's CueLog; for each entry it has not seen it reads the cue back
from the hub and relays the cue's `family` block, member by member, recording
what each member was asked, through which interface, and what was seen
afterwards. A GO pressed in the hub's own programmer page is relayed the same
way, because the log is what is watched, not this page's button.

**CHECK.** Opens the stage page in a browser of its own, resets the hub to the
top, and for each cue presses GO and waits for that cue's relay. Then it
asserts what it can see without the stage's word for it -- the hub's CueLog
gained an entry for that cue, joe's latest result is the take relayed, leo's
frame on the stage page shows the song -- and, for a member only the stage's
own session can see, that the session saw the change. It saves a picture of
the stage after each cue. The pictures are recorded and never compared.
Exit 0: every assertion held. Exit 1: one did not. Any other status: the
check could not say, and its last line says why.

**THE ONE PLACE IN THIS CORPUS THAT NAMES A MEMBER'S SURFACE.** A single
member's check lives in that member. The stage is a coordinated check of
links the members do not have yet, so it has to press on each one, and every
surface it presses is one the member's own walkthrough already drives: leo's
deep link and chart title, joe's upload and run routes and its Fetch Latest
button, carlos's `t` key and its example loader, the buttons on the page
ShowStopper serves. Nothing else in `ci/` names one, and a test holds that.
"""

from __future__ import annotations

import io
import json
import math
import os
import queue
import re
import signal
import struct
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import wave
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import family_stage as fs  # noqa: E402

# --- member surfaces, each one the member's own walkthrough already uses -------

# ShowStopper: textual-serve's page. The first stopwatch's Start button, which
# becomes its Stop button once pressed, at this viewport. A click that misses
# reads as a failure, because the label it waits for never arrives.
STOPWATCH_VIEWPORT = {"width": 1000, "height": 640}
STOPWATCH_BUTTON = (85, 95)
STOP_LABEL = re.compile(rb"Stop(?!watch)")

# carlos: the rack is the page's global `system`; `loadExample` is what its
# Examples menu calls; `t` turns every device.
CARLOS_READY = ("() => typeof system !== 'undefined' && !!document.getElementById('view-indicator')"
                " && document.getElementById('view-indicator').textContent.length > 0")

# joe: the results panel's toggle, its Fetch Latest button and what it shows.
JOE_RESULTS_TOGGLE = "[data-testid=results-toggle]"
JOE_FETCH = "[data-testid=fetch-latest]"
JOE_META = "[data-testid=results-meta]"

# leo: the chart's title.
LEO_TITLE = ".page__header__title"

SESSION_VIEWPORT = {"width": 1000, "height": 640}
RELAY_SECONDS = 240


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def http(method: str, url: str, params: dict | None = None, body=None, ctype: str | None = None,
         timeout: float = 10.0):
    """(status, decoded JSON or None). Never raises for an HTTP status; raises for no answer."""
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    data, headers = None, {}
    if isinstance(body, (dict, list)):
        data, headers = json.dumps(body).encode(), {"Content-Type": "application/json"}
    elif isinstance(body, bytes):
        data, headers = body, {"Content-Type": ctype or "application/octet-stream"}
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


def take(midi: list[int], rate: int = 22050, seconds: float = 0.5) -> bytes:
    """A take: each note half a second, five partials falling off as 1/n, as WAV.

    The same recipe as joe's own walkthrough fixture, made with the standard
    library: the pipeline's harmonic check looks for overtones, so a bare sine
    would not do.
    """
    samples = []
    for number in midi:
        frequency = 440.0 * 2 ** ((number - 69) / 12)
        for i in range(int(seconds * rate)):
            t = i / rate
            envelope = min(1.0, t / 0.01, (seconds - t) / 0.05)
            samples.append(envelope * sum(math.sin(2 * math.pi * frequency * k * t) / k
                                          for k in range(1, 6)))
    peak = max(abs(s) for s in samples) or 1.0
    out = io.BytesIO()
    with wave.open(out, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(rate)
        file.writeframes(b"".join(struct.pack("<h", int(32767 * 0.5 * s / peak)) for s in samples))
    return out.getvalue()


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
        self.relays: list[dict] = []   # since the stage started or was last reset
        self.history: list[dict] = []  # every relay, for the record
        self.panels: dict = {}
        self.jobs: queue.Queue = queue.Queue()
        self.stopping = threading.Event()
        self.dir = Path(job["dir"])
        (self.dir / "live").mkdir(parents=True, exist_ok=True)
        self.hub = job["hub"].rstrip("/")
        for member, panel in job["panels"].items():
            if panel["shows"] == "frame" and panel.get("src"):
                self.panels[member] = {"frame": panel["src"]}

    def snapshot(self) -> dict:
        with self.lock:
            return {"ready": self.ready, "failed": self.failed, "seeded": self.seeded,
                    "hub": {"pointer": self.pointer}, "relays": json.loads(json.dumps(self.relays)),
                    "panels": dict(self.panels), "port": self.job["port"]}

    def record(self) -> None:
        with self.lock:
            document = {"seeded": self.seeded, "relays": self.history, "failed": self.failed,
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
        """Relay every CueLog entry the hub writes for this show, in order, once."""
        show = self.seeded["show_id"]
        seen = {entry["id"] for entry in self.call("GET", f"/db/shows/{show}/logs",
                                                   params={"limit": 500})}
        while not self.stopping.is_set():
            try:
                entries = self.call("GET", f"/db/shows/{show}/logs", params={"limit": 50})
                status = self.call("GET", "/programmer/status")
                with self.lock:
                    self.pointer = status.get("pointer")
                for entry in sorted(entries, key=lambda e: e["id"]):
                    if entry["id"] not in seen:
                        seen.add(entry["id"])
                        if entry.get("cue_id") is not None:
                            self.jobs.put(("relay", entry))
            except (OSError, RuntimeError, ValueError) as exc:
                with self.lock:
                    self.failed = f"the hub stopped answering: {exc}"
            self.stopping.wait(0.4)

    def go(self) -> tuple[int, dict]:
        return http("POST", self.hub + "/programmer/go",
                    params={"cue_list_id": self.seeded["cue_list_id"],
                            "show_id": self.seeded["show_id"]})

    def reset(self) -> tuple[int, dict]:
        status, answer = http("POST", self.hub + "/programmer/reset")
        if 200 <= status < 300:
            with self.lock:
                self.relays = []
        return status, answer


class Sessions:
    """The stage's own browser: one page per session member, driven from one thread."""

    def __init__(self, stage: Stage, playwright):
        self.stage = stage
        self.browser = playwright.chromium.launch()
        self.pages: dict = {}
        self.frames: list[tuple[float, bytes]] = []
        self.clock_running = False
        self.shots: dict[str, int] = {}
        self.leo = None

    def open(self) -> None:
        for member, panel in self.stage.job["panels"].items():
            if panel["shows"] != "session":
                continue
            try:
                getattr(self, f"open_{member}")(panel["url"])
                self.picture(member)
            except Exception as exc:  # a session that will not open is reported, not fatal
                with self.stage.lock:
                    self.stage.panels[member] = {"error": f"{type(exc).__name__}: {exc}"}

    def page(self, member: str, viewport=SESSION_VIEWPORT):
        context = self.browser.new_context(viewport=viewport)
        page = context.new_page()
        self.pages[member] = page
        return page

    def open_ShowStopper(self, url: str) -> None:  # noqa: N802 -- the member's name
        page = self.page("ShowStopper", STOPWATCH_VIEWPORT)
        page.on("websocket", lambda ws: ws.on(
            "framereceived",
            lambda data: self.frames.append((time.monotonic(),
                                             data if isinstance(data, bytes) else data.encode()))))
        page.goto(url)
        if not self.wait_frames(lambda new: b"Start" in new, 30):
            raise RuntimeError("the stopwatch never drew its Start button")
        page.wait_for_timeout(500)

    def open_carlos(self, url: str) -> None:
        page = self.page("carlos")
        page.goto(url)
        page.wait_for_function(CARLOS_READY, timeout=30000)

    def open_joe(self, url: str) -> None:
        page = self.page("joe")
        page.goto(url)
        page.wait_for_selector(JOE_FETCH, state="attached", timeout=30000)
        page.click(JOE_RESULTS_TOGGLE)

    def picture(self, member: str) -> None:
        page = self.pages.get(member)
        if page is None:
            return
        number = self.shots.get(member, 0) + 1
        name = f"{member}-{number}.png"
        page.screenshot(path=str(self.stage.dir / "live" / name))
        self.shots[member] = number
        with self.stage.lock:
            self.stage.panels[member] = {"shot": f"live/{name}"}
        stale = self.stage.dir / "live" / f"{member}-{number - 3}.png"
        try:
            stale.unlink()
        except OSError:
            pass

    def wait_frames(self, test, seconds: float, since: int = 0) -> bool:
        page = self.pages["ShowStopper"]
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if test(b"".join(data for _, data in self.frames[since:])):
                return True
            page.wait_for_timeout(100)
        return False

    def frame_rate(self, seconds: float = 1.0) -> int:
        page = self.pages["ShowStopper"]
        before = len(self.frames)
        page.wait_for_timeout(int(seconds * 1000))
        return len(self.frames) - before

    # --- one verb each --------------------------------------------------

    def do(self, step: dict) -> tuple[str, str, dict]:
        member = step["member"]
        if self.stage.job["panels"][member]["shows"] == "session" and member not in self.pages:
            why = self.stage.panels.get(member, {}).get("error", "it never opened")
            return "unknown", f"the stage has no session of {member}: {why}", {}
        return getattr(self, f"{member}_{step['do']}")(step)

    def ShowStopper_start(self, step: dict):  # noqa: N802
        if self.clock_running:
            return "pass", "already running: nothing pressed", {"pressed": False}
        since = len(self.frames)
        self.pages["ShowStopper"].mouse.click(*STOPWATCH_BUTTON)
        if not self.wait_frames(lambda new: bool(STOP_LABEL.search(new)), 5, since):
            return "fail", "pressed Start, and the Stop button never appeared", {}
        rate = self.frame_rate()
        self.clock_running = rate > 5
        result = "pass" if self.clock_running else "fail"
        return result, f"Stop button shown; the clock redraws {rate} times a second", \
            {"frames_per_second": rate}

    def ShowStopper_stop(self, step: dict):  # noqa: N802
        if not self.clock_running:
            return "pass", "not running: nothing pressed", {"pressed": False}
        since = len(self.frames)
        self.pages["ShowStopper"].mouse.click(*STOPWATCH_BUTTON)
        if not self.wait_frames(lambda new: b"Start" in new, 5, since):
            return "fail", "pressed Stop, and the Start button never came back", {}
        self.pages["ShowStopper"].wait_for_timeout(300)
        rate = self.frame_rate()
        self.clock_running = rate > 5
        result = "fail" if self.clock_running else "pass"
        return result, f"Start button back; the clock redraws {rate} times a second", \
            {"frames_per_second": rate}

    def carlos_patch(self, step: dict):
        page = self.pages["carlos"]
        seen = page.evaluate("""async ([kind, device]) => {
            const before = system.exportState().name;
            const r = await fetch(`/api/catalogue/devices/${encodeURIComponent(device)}/examples`);
            const expected = r.ok ? ((await r.json()).examples[kind] || {}).name : null;
            await loadExample(kind, device);
            return {before, expected, after: system.exportState().name,
                    modules: system.exportState().modules.length,
                    status: document.getElementById('status').textContent};
        }""", [step["params"]["example"], step["params"]["device"]])
        page.wait_for_timeout(400)
        ok = seen["expected"] is not None and seen["after"] == seen["expected"]
        return ("pass" if ok else "fail"), \
            f"rack holds “{seen['after']}” ({seen['modules']} devices), was “{seen['before']}”", seen

    def carlos_turn(self, step: dict):
        page = self.pages["carlos"]
        before = page.locator("#view-indicator").text_content()
        page.keyboard.press("t")
        page.wait_for_timeout(400)
        after = page.locator("#view-indicator").text_content()
        return ("pass" if after != before else "fail"), f"facing {after}, was {before}", \
            {"before": before, "after": after}

    def joe_take(self, step: dict):
        wav = take(step["midi"])
        status, uploaded = http("POST", step["upload"], body=wav, ctype="audio/wav", timeout=30)
        if status != 200 or not isinstance(uploaded, dict) or "filename" not in uploaded:
            return "fail", f"upload answered {status}: {uploaded}", {}
        filename = uploaded["filename"]
        began = time.monotonic()
        status, ran = http("POST", step["run"].replace("{filename}", urllib.parse.quote(filename)),
                           timeout=200)
        seconds = round(time.monotonic() - began, 1)
        if status != 200 or not isinstance(ran, dict) or ran.get("returncode") != 0:
            code = ran.get("returncode") if isinstance(ran, dict) else ran
            return "fail", f"the pipeline answered {status}, returncode {code}", {"file": filename}
        status, latest = http("GET", step["latest"], timeout=30)
        stem = filename.rsplit(".", 1)[0]
        tracks = list((latest or {}).get("audio", {})) if isinstance(latest, dict) else []
        events = sum(len(note["start_dur"]) for track in (latest or {}).get("audio", {}).values()
                     for chroma in track["chroma"].values() for note in chroma["midi"]["notes"]) \
            if tracks else 0
        evidence = {"file": filename, "pipeline_seconds": seconds, "latest_tracks": tracks,
                    "events": events}
        if tracks != [stem] or events == 0:
            return "fail", f"latest result is {tracks} with {events} events, not {stem}", evidence
        page = self.pages["joe"]
        page.evaluate(f"() => document.querySelector('{JOE_FETCH}').click()")
        try:
            page.wait_for_function(
                f"(stem) => (document.querySelector('{JOE_META}').textContent || '').includes(stem)",
                arg=stem, timeout=20000)
            evidence["page"] = page.locator(JOE_META).text_content()[:200]
        except Exception:
            evidence["page"] = "the page did not show the take after Fetch Latest"
            return "fail", evidence["page"], evidence
        return "pass", f"{events} note events from {stem}, in {seconds}s; the page shows it", evidence

    def leo_show(self, step: dict):
        with self.stage.lock:
            self.stage.panels["leo"] = {"frame": step["url"]}
        if self.leo is None:
            self.leo = self.browser.new_context(viewport=SESSION_VIEWPORT).new_page()
        self.leo.goto(step["url"])
        song = step["params"]["song"]
        try:
            self.leo.wait_for_function(
                f"(song) => (document.querySelector('{LEO_TITLE}') || {{}}).textContent === song",
                arg=song, timeout=30000)
        except Exception:
            title = self.leo.locator(LEO_TITLE).first.text_content(timeout=1000) \
                if self.leo.locator(LEO_TITLE).count() else None
            return "fail", f"leo's link shows {title!r}, not {song!r}", {"url": step["url"]}
        return "pass", f"leo's own link to {song} shows its chart", {"url": step["url"]}

    # --- the worker loop -------------------------------------------------

    def relay(self, entry: dict) -> None:
        stage = self.stage
        cues = stage.call("GET", f"/db/cue-lists/{stage.seeded['cue_list_id']}/cues")
        cue = next((c for c in cues if c["id"] == entry["cue_id"]), None)
        running = stage.job["running"]
        record = {"number": cue["number"] if cue else None, "name": cue["name"] if cue else None,
                  "cue_id": entry["cue_id"], "log_id": entry["id"],
                  "at": entry.get("triggered_at"), "relayed_at": now(), "done": False,
                  "problems": [], "steps": [], "idle": []}
        if cue is None:
            record["problems"] = [f"the hub logged cue id {entry['cue_id']}, which is not in the list"]
            actions = []
        else:
            actions, record["problems"] = fs.parse_family(cue.get("notes"), running)
        steps = fs.relay_plan(actions, stage.job["members"], record["number"])
        for step, action in zip(steps, actions):
            step["summary"] = fs.summary(action)
        record["steps"] = steps
        record["idle"] = [m for m in running if m != fs.HUB and m not in {s["member"] for s in steps}]
        with stage.lock:
            stage.relays.append(record)
            stage.history.append(record)
        for step in steps:
            began = time.monotonic()
            try:
                step["result"], step["detail"], step["evidence"] = self.do(step)
            except Exception as exc:
                step.update(result="unknown", detail=f"{type(exc).__name__}: {str(exc)[:200]}",
                            evidence={"trace": traceback.format_exc(limit=3)})
            step["seconds"] = round(time.monotonic() - began, 2)
            try:
                self.picture(step["member"])
            except Exception:
                pass
        record["result"] = fs.combine([s["result"] for s in steps] or ["pass"]) \
            if not record["problems"] else "fail"
        record["done"] = True
        stage.record()

    def run(self) -> None:
        last = 0.0
        while not self.stage.stopping.is_set():
            try:
                kind, payload = self.stage.jobs.get(timeout=0.25)
            except queue.Empty:
                kind = None
            if kind == "relay":
                self.relay(payload)
            if self.clock_running and time.monotonic() - last > 1.0:
                last = time.monotonic()
                try:
                    self.picture("ShowStopper")
                except Exception:
                    pass

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
            return self.json(404, {"detail": "not here"})

    return Handler


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
    order = job["order"]
    page_html = fs.stage_page({"show": job["show"], "hub_url": job["hub"], "order": order,
                               "panels": job["panels"],
                               "links": fs.links(job["show"], job["running"])})
    server = ThreadingHTTPServer((job["host"], job["port"]), handler(stage, page_html))
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
    except (OSError, StopIteration, TypeError, KeyError) as exc:
        return finish(3, f"could not read the show from the hub: {exc!r}")
    if (show["name"], cue_list["name"]) != (job["show"]["name"], job["show"]["cue_list"]):
        return finish(1, f"the hub holds {show['name']!r}/{cue_list['name']!r}, not the declared show")
    declared = [(c["number"], c["name"]) for c in job["show"]["cues"]]
    if [(int(c["number"]), c["name"]) for c in cues] != declared:
        return finish(1, f"the hub's cues {[(c['number'], c['name']) for c in cues]} "
                         f"are not the declared {declared}")
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


def run_cue(page, cue: dict, index: int, hub: str, show_id: int, job: dict, url: str,
            shots: Path) -> dict:
    """GO once, wait for the relay of that cue, assert what can be seen, and picture it."""
    record = {"number": cue["number"], "name": cue["name"], "assertions": []}

    def held(what: str, ok, detail: str = "", by: str = "check") -> None:
        result = ok if isinstance(ok, str) else ("pass" if ok else "fail")
        record["assertions"].append({"what": what, "result": result, "detail": detail, "by": by})

    before = {e["id"] for e in http("GET", f"{hub}/db/shows/{show_id}/logs",
                                    params={"limit": 500})[1]}
    page.click("#go")
    deadline = time.monotonic() + RELAY_SECONDS
    relay = None
    while time.monotonic() < deadline:
        state = http("GET", url + "state")[1]
        relay = next((r for r in state["relays"] if str(r["number"]) == str(cue["number"])), None)
        if relay and relay["done"]:
            break
        page.wait_for_timeout(250)
    logged = [e for e in http("GET", f"{hub}/db/shows/{show_id}/logs", params={"limit": 500})[1]
              if e["id"] not in before]
    held("the hub's CueLog gained an entry for this cue",
         [e["cue_id"] for e in logged] == [cue["id"]],
         f"new entries name cue ids {[e['cue_id'] for e in logged]}; this cue is {cue['id']}",
         by="the hub's /db/shows/{id}/logs")
    if not relay or not relay["done"]:
        held("the stage relayed the cue", False, f"no finished relay within {RELAY_SECONDS}s")
        record["result"] = "fail"
        return record
    wanted, problems = fs.parse_family(cue.get("notes"), job["running"])
    held("the stage relayed exactly the cue's family block, read from the hub",
         not problems and [(s["member"], s["do"]) for s in relay["steps"]]
         == [(a.member, a.verb) for a in wanted],
         "; ".join(problems) or ", ".join(f"{s['member']} {s['do']}" for s in relay["steps"]))
    for step in relay["steps"]:
        held(f"{step['member']} {step['do']}: {step['summary']}", step.get("result", "unknown"),
             step.get("detail", ""), by=f"the stage, through {step['interface']}")
        if step["member"] == "leo" and step.get("result") == "pass":
            song = step["params"]["song"]
            title = page.frame_locator("#frame-leo").locator(LEO_TITLE).first
            try:
                expect(title).to_have_text(song, timeout=30000)
                shown = song
            except AssertionError:
                shown = title.text_content(timeout=2000) if title.count() else None
            held(f"leo's frame on the stage shows {song}", shown == song,
                 f"title reads {shown!r}", by="the check's browser")
        if step["member"] == "joe" and step.get("result") == "pass":
            status, latest = http("GET", step["latest"], timeout=30)
            tracks = list(latest.get("audio", {})) if isinstance(latest, dict) else []
            stem = step["evidence"]["file"].rsplit(".", 1)[0]
            held("joe's latest result is this take", tracks == [stem],
                 f"latest names {tracks}", by="joe's /api/results/latest")
    sessions = [s["member"] for s in relay["steps"]
                if job["panels"][s["member"]]["shows"] == "session"]
    if sessions:
        page.wait_for_function(
            """(members) => members.every(m => { const i = document.getElementById('shot-' + m);
                 return i && !i.hidden && i.dataset.shown && i.dataset.shown === i.dataset.want; })""",
            arg=sessions, timeout=10000)
    page.wait_for_timeout(1500)
    shot = shots / f"{index:02d}-cue-{cue['number']}.png"
    page.screenshot(path=str(shot), full_page=True)
    record["shot"] = str(shot)
    record["relay"] = {k: relay[k] for k in ("log_id", "at", "problems", "idle", "result")}
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
