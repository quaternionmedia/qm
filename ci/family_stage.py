#!/usr/bin/env python3
"""The family stage: a small show run from the hub, on one page.

    uv run qm family-demo --stage                  # run the show headless and record it
    uv run qm family-demo --stage --hold --open    # then keep it up and play it by hand

**WHAT IT SHOWS.** `ci/family-demo.yaml` declares a show under `stage:` -- a
name, a cue list and a handful of cues. Once every core member is up, the
stage creates that show in ShowRunner through ShowRunner's own REST routes,
never by writing its database, and serves one page: the show's cues, a GO
button that calls ShowRunner's cue programmer, and a panel per member. The
programmer fires the cue and writes a CueLog entry. The stage watches that log,
and for each new entry it reads the cue back from the hub and performs the
cue's `family` block against each member's own interface: joe's HTTP API,
leo's deep link, and the pages ShowStopper and carlos serve, driven in the
stage's own browser.

**THE FAMILY BLOCK.** A cue's `notes` is JSON. ShowRunner's programmer reads
its `osc` and `http` keys and ignores the rest; the stage reads `family`:

    {"family": {"leo": {"do": "show", "song": "Blue Bossa", "playlist": "Jazz 1460"},
                "joe": {"do": "take", "notes": ["C4", "E4", "G4", "C5"]}}}

Each member names one verb from `VERBS`, with exactly the parameters that verb
takes. A verb exists only where the member already has an interface that does
it; one that would need a new interface in the member is not a verb, and the
member's panel says what cannot be driven instead of pretending.

**LINKS ARE CLAIMED NARROWLY.** The stage presses GO through the hub's own
route, so the hub really fires and logs each cue. Nothing the hub does reaches
another member: no member calls another, and every family action is performed
by the stage. Each is labelled `relayed`, with the interface it went through,
and the page's footer says so. A link between two members appears here only
when one exists.

This module is the part that decides and holds no state: the vocabulary, the
parser, the relay plan, the seeding requests and the page. It imports nothing
outside the standard library, so the stage's runtime (`family_stage_run.py`,
under the pinned Playwright interpreter) and this corpus's tests both import it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from urllib.parse import quote

# The hub: it fires cues, and is never relayed one.
HUB = "ShowRunner"

# ShowRunner's cue layers. The stage's cues each carry one, because ShowRunner's
# script page cannot render a cue without a layer.
LAYERS = ("Lights", "Sound", "Video", "Audio", "Stage")

# Relay order within one cue: the quick, visible actions first and the take,
# which runs joe's whole pipeline, last.
ORDER = ("ShowStopper", "leo", "carlos", "joe")


@dataclass(frozen=True)
class Verb:
    """One thing the stage can make one member do, and the interface it uses."""

    member: str
    name: str
    params: dict = field(default_factory=dict)  # name -> "text", "notes" or a tuple of choices
    via: str = ""   # "api", "url" or "page"
    says: str = ""  # one line: what it does, through what


VERBS: dict[tuple[str, str], Verb] = {}  # keyed by (member, verb)
for _verb in (
    Verb("ShowStopper", "start", {}, "page",
         "presses Start on the first stopwatch of the page ShowStopper serves"),
    Verb("ShowStopper", "stop", {}, "page",
         "presses Stop on the stopwatch it started"),
    Verb("leo", "show", {"song": "text", "playlist": "text"}, "url",
         "loads leo's own deep link for the song"),
    Verb("carlos", "patch", {"device": "text", "example": ("simple", "complex")}, "page",
         "loads a device's example patch into the rack, as the rack's Examples menu does"),
    Verb("carlos", "turn", {}, "page",
         "turns every device in the rack, as carlos's own t key does"),
    Verb("joe", "take", {"notes": "notes"}, "api",
         "hands joe a synthesized take through its upload route and runs its pipeline on it"),
):
    VERBS[(_verb.member, _verb.name)] = _verb

# What each `via` means on the page and in the manifest.
VIA = {
    "api": "the member's HTTP API",
    "url": "the member's own deep link",
    "page": "the member's served page, in the stage's own browser",
}

# How a panel shows its member. `frame`: the member's page, live, in a frame --
# for a member whose state lives on its server or in a URL the stage's page
# loads. `session`: the stage's own browser session of the member, pictured
# after each action and every few seconds -- for a member whose state lives in
# one browser session, where a frame would be a second session nothing drives.
PANEL_KINDS = ("frame", "session")

NOTE = re.compile(r"^([A-G])([#b]?)(-?\d)$")
SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
MAX_NOTES = 16


def note_number(name: str) -> int:
    """MIDI number of a note name such as C4, F#3 or Bb2 (C4 is 60)."""
    match = NOTE.match(name) if isinstance(name, str) else None
    if match is None:
        raise ValueError(f"{name!r} is not a note name like C4, F#3 or Bb2")
    letter, accidental, octave = match.groups()
    number = 12 * (int(octave) + 1) + SEMITONE[letter] + {"#": 1, "b": -1, "": 0}[accidental]
    if not 0 <= number <= 127:
        raise ValueError(f"{name!r} is outside the MIDI range")
    return number


@dataclass(frozen=True)
class Action:
    member: str
    verb: str
    params: tuple  # sorted (name, value) pairs, so an action is hashable and comparable

    def get(self, name: str):
        return dict(self.params)[name]

    def as_dict(self) -> dict:
        return {"member": self.member, "do": self.verb,
                **{k: list(v) if isinstance(v, tuple) else v for k, v in self.params}}


def parse_family(notes, running: list[str] | set[str]) -> tuple[list[Action], list[str]]:
    """(actions in relay order, problems) for one cue's notes.

    `notes` is the cue's notes as ShowRunner holds them -- a JSON string -- or
    already parsed. No notes, or notes with no `family` key, is a cue the
    family has nothing to do on: no actions and no problems. Anything else that
    is not a well-formed family block is a problem, and a cue with a problem
    relays nothing, so a typo cannot half-run a cue.
    """
    if notes in (None, ""):
        return [], []
    if isinstance(notes, str):
        try:
            notes = json.loads(notes)
        except json.JSONDecodeError as exc:
            return [], [f"notes are not JSON: {exc.msg}"]
    if not isinstance(notes, dict):
        return [], ["notes must be a JSON object"]
    family = notes.get("family")
    if family is None:
        return [], []
    if not isinstance(family, dict) or not family:
        return [], ["family must be an object naming at least one member"]
    problems: list[str] = []
    actions: list[Action] = []
    for member, wanted in family.items():
        if member == HUB:
            problems.append(f"{HUB} is the hub: it fires the cue and is never relayed one")
            continue
        verbs = sorted(name for owner, name in VERBS if owner == member)
        if member not in running:
            problems.append(f"{member} is not a running member of this demo")
            continue
        if not verbs:
            problems.append(f"{member} has no verb the stage can drive")
            continue
        if not isinstance(wanted, dict) or not isinstance(wanted.get("do"), str):
            problems.append(f"{member}: expected an object with a 'do' naming one of {verbs}")
            continue
        verb = VERBS.get((member, wanted["do"]))
        if verb is None:
            problems.append(f"{member}: no verb {wanted['do']!r}; it has {verbs}")
            continue
        given = {k: v for k, v in wanted.items() if k != "do"}
        before = len(problems)
        for name in sorted(set(given) - set(verb.params)):
            problems.append(f"{member} {verb.name}: takes no {name!r}")
        for name, kind in verb.params.items():
            if name not in given:
                problems.append(f"{member} {verb.name}: needs {name!r}")
            else:
                problems += [f"{member} {verb.name}: {why}"
                             for why in _param_problems(name, kind, given[name])]
        if len(problems) == before:
            frozen = {k: tuple(v) if isinstance(v, list) else v for k, v in given.items()}
            actions.append(Action(member, verb.name, tuple(sorted(frozen.items()))))
    if problems:
        return [], problems
    return sorted(actions, key=lambda a: ORDER.index(a.member)), []


def _param_problems(name: str, kind, value) -> list[str]:
    if isinstance(kind, tuple):
        return [] if value in kind else [f"{name} must be one of {list(kind)}, not {value!r}"]
    if kind == "text":
        return [] if isinstance(value, str) and value.strip() else [f"{name} must be non-empty text"]
    if kind == "notes":
        if not isinstance(value, list) or not 1 <= len(value) <= MAX_NOTES:
            return [f"{name} must be a list of 1 to {MAX_NOTES} note names"]
        found = []
        for note in value:
            try:
                note_number(note)
            except ValueError as exc:
                found.append(str(exc))
        return found
    raise ValueError(f"unknown parameter kind {kind!r}")


# ===================================================================
# THE RELAY PLAN -- what each action calls, before anything is called
# ===================================================================

def deep_link(base: str, song: str, playlist: str, cue: int | str) -> str:
    """leo's own link to a song, made unique per cue.

    leo reads its route on a fresh load only: changing the hash of an open page
    changes the address and not the chart. The query names the cue, so loading
    the next cue's link is a new document and not a hash change.
    """
    root = base.split("#", 1)[0].split("?", 1)[0]
    if not root.endswith("/"):
        root += "/"
    return (f"{root}?cue={quote(str(cue), safe='')}"
            f"#!/song/{quote(song, safe='')}?playlist={quote(playlist, safe='')}")


def relay_plan(actions: list[Action], members: dict, cue: int | str) -> list[dict]:
    """One step per action: the member, the verb, the interface and its addresses.

    `members` maps a member to what the stage was told about it: its `url`
    and its `ports` by label, on `host`. Pure, so the plan can be read -- and
    tested -- without anything running.
    """
    steps = []
    for action in actions:
        verb = VERBS[(action.member, action.verb)]
        info = members.get(action.member) or {}
        params = {k: list(v) if isinstance(v, tuple) else v for k, v in action.params}
        step = {"member": action.member, "do": action.verb, "params": params,
                "via": verb.via, "interface": VIA[verb.via], "says": verb.says,
                "link": "relayed", "page": info.get("url")}
        if action.member == "leo":
            step["url"] = deep_link(info["url"], action.get("song"), action.get("playlist"), cue)
        elif action.member == "joe":
            api = f"http://{info['host']}:{info['ports']['api']}"
            step.update(api=api, upload=f"{api}/api/audio/upload", run=f"{api}/api/run/{{filename}}",
                        latest=f"{api}/api/results/latest",
                        midi=[note_number(n) for n in action.get("notes")])
        steps.append(step)
    return steps


# ===================================================================
# THE SHOW -- checked, and created through the hub's own routes
# ===================================================================

def check_show(show, running: list[str] | set[str]) -> list[str]:
    """Every reason the declared show cannot be seeded and relayed as written."""
    if not isinstance(show, dict):
        return ["stage.show must be a mapping"]
    problems = []
    for key in ("name", "cue_list"):
        if not isinstance(show.get(key), str) or not show[key].strip():
            problems.append(f"stage.show.{key} must be non-empty text")
    cues = show.get("cues")
    if not isinstance(cues, list) or not cues:
        return problems + ["stage.show.cues must list at least one cue"]
    seen: set[int] = set()
    for index, cue in enumerate(cues, start=1):
        label = f"cue {cue.get('number', f'#{index}')}" if isinstance(cue, dict) else f"cue #{index}"
        if not isinstance(cue, dict):
            problems.append(f"{label}: must be a mapping")
            continue
        number = cue.get("number")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            problems.append(f"{label}: number must be a positive whole number")
        elif number in seen:
            problems.append(f"{label}: number is used twice")
        else:
            seen.add(number)
        if not isinstance(cue.get("name"), str) or not cue["name"].strip():
            problems.append(f"{label}: needs a name")
        if cue.get("layer") not in LAYERS:
            problems.append(f"{label}: layer must be one of {list(LAYERS)}")
        if "family" not in cue:
            problems.append(f"{label}: has no family block")
            continue
        _, found = parse_family({"family": cue["family"]}, running)
        problems += [f"{label}: {p}" for p in found]
    numbers = [c.get("number") for c in cues if isinstance(c, dict)]
    if all(isinstance(n, int) for n in numbers) and numbers != sorted(numbers):
        problems.append("stage.show.cues must be listed in cue order")
    return problems


def check_panels(panels, running: list[str] | set[str]) -> list[str]:
    """Every running member has one panel: a one-line role, how it is shown, and a note."""
    if not isinstance(panels, dict):
        return ["stage.panels must map each running member to its panel"]
    problems = [f"stage.panels: {name} is not a running member"
                for name in sorted(set(panels) - set(running))]
    for name in [m for m in running if m not in panels]:
        problems.append(f"stage.panels: {name} has no panel")
    for name, panel in panels.items():
        if name not in running:
            continue
        if not isinstance(panel, dict):
            problems.append(f"stage.panels.{name}: must be a mapping")
            continue
        role = panel.get("role")
        if not isinstance(role, str) or not role.strip() or "\n" in role.strip():
            problems.append(f"stage.panels.{name}: role must be one line")
        if panel.get("shows") not in PANEL_KINDS:
            problems.append(f"stage.panels.{name}: shows must be one of {list(PANEL_KINDS)}")
        if not isinstance(panel.get("note"), str) or not panel["note"].strip():
            problems.append(f"stage.panels.{name}: needs a note saying what the panel is")
    if panels.get(HUB, {}).get("shows") == "session":
        problems.append(f"stage.panels.{HUB}: the hub's state is on its server; frame it")
    return problems


def panel_view(panels: dict, members: dict) -> dict:
    """Each panel with its member's address, and the page a framed panel opens on.

    A framed panel with a `path` opens on that page of its member. One without
    starts empty and is loaded by the first cue that names its member, so the
    stage never shows a member page that no cue asked for.
    """
    view = {}
    for name, panel in panels.items():
        url = members[name]["url"]
        if panel.get("path"):
            url = url.rstrip("/") + "/" + panel["path"].lstrip("/")
        entry = {**panel, "url": url}
        if panel["shows"] == "frame" and panel.get("path"):
            entry["src"] = url
        view[name] = entry
    return view


def check_stage(stage, running: list[str], ports: dict[int, str], span: tuple[int, int]) -> list[str]:
    """Every reason the plan's `stage` block cannot run: its port, its show, its panels.

    `ports` maps each port the plan reserves to its member, and `span` is the
    plan's port range, so the stage's port is held to the same rules as a member's.
    """
    if not isinstance(stage, dict):
        return ["stage: must be a mapping"]
    problems = []
    port = stage.get("port")
    if not isinstance(port, int) or isinstance(port, bool) or not span[0] <= port <= span[1]:
        problems.append(f"stage: port {port!r} is outside {span[0]}..{span[1]}")
    elif port in ports:
        problems.append(f"stage: port {port} is already {ports[port]}'s")
    if HUB not in running:
        problems.append(f"stage: {HUB}, the hub, is not a running member")
    problems += check_show(stage.get("show"), running)
    problems += check_panels(stage.get("panels"), running)
    return problems


def cue_notes(cue: dict) -> str:
    """The notes ShowRunner stores for a declared cue: its family block, as JSON."""
    return json.dumps({"family": cue["family"]}, sort_keys=True)


def seed(show: dict, call) -> dict:
    """Create the show in the hub through its REST routes, and return the ids.

    `call(method, path, params=None, body=None)` returns the decoded JSON of a
    2xx answer and raises otherwise; injected, so the sequence is testable
    without a hub.
    """
    created = call("POST", "/db/shows", params={"name": show["name"]})
    show_id = created["id"]
    cue_list = call("POST", f"/db/shows/{show_id}/cue-lists", body={"name": show["cue_list"]})
    cues = []
    for cue in show["cues"]:
        made = call("POST", f"/db/cue-lists/{cue_list['id']}/cues",
                    body={"number": cue["number"], "name": cue["name"],
                          "layer": cue["layer"], "notes": cue_notes(cue)})
        cues.append({"id": made["id"], "number": cue["number"], "name": cue["name"]})
    return {"show_id": show_id, "cue_list_id": cue_list["id"], "cues": cues}


def links(show: dict, running: list[str] | set[str]) -> list[dict]:
    """What joins the hub to each member in this show, claimed no wider than it is."""
    used: dict[str, set[str]] = {}
    for cue in show.get("cues") or []:
        actions, _ = parse_family({"family": cue.get("family") or {}}, running)
        for action in actions:
            used.setdefault(action.member, set()).add(VERBS[(action.member, action.verb)].via)
    rows = [{"member": HUB, "link": "real",
             "says": "the stage presses GO through the hub's own programmer route; the hub "
                     "fires the cue and writes its CueLog entry"}]
    others = [m for m in ORDER if m in running] + sorted(set(running) - set(ORDER) - {HUB})
    for member in others:
        vias = sorted(used.get(member, ()))
        if vias:
            rows.append({"member": member, "link": "relayed",
                         "says": "performed by the stage through "
                                 + " and ".join(VIA[v] for v in vias)})
        elif any(owner == member for owner, _ in VERBS):
            rows.append({"member": member, "link": "not on any cue",
                         "says": "drivable, but no cue in this show asks it for anything"})
        else:
            rows.append({"member": member, "link": "not drivable",
                         "says": "no interface the stage could drive it through"})
    return rows


APP_TO_APP = ("No member calls another. ShowRunner fires each cue and logs it, and sends "
              "nothing to any member; every family action is performed by this stage.")


def combine(results: list[str]) -> str:
    """One result from several: any fail fails, then any unknown is unknown."""
    if "fail" in results:
        return "fail"
    if "unknown" in results or not results:
        return "unknown"
    return "pass"


def summary(action: Action) -> str:
    """A cue chip: what the member is asked for, in a few words."""
    params = dict(action.params)
    if action.member == "leo":
        return f"shows {params['song']}"
    if action.member == "joe":
        return f"processes a take of {' '.join(params['notes'])}"
    if (action.member, action.verb) == ("carlos", "patch"):
        return f"loads the {params['example']} {params['device']} patch"
    if (action.member, action.verb) == ("carlos", "turn"):
        return "turns the rack"
    return f"{action.verb}s the clock"


# ===================================================================
# THE PAGE
# ===================================================================

STAGE_STYLE = """
:root{--bg:#f6f5f1;--fg:#1d1d1b;--muted:#66655f;--line:#dcdbd4;--card:#fff;--accent:#1f5fbf;
--go:#1f7a3a;--go-fg:#fff;--pass:#1f7a3a;--fail:#b3261e;--unknown:#8a6d00;--next:#e6f2e8}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141413;--fg:#ececea;
--muted:#a3a39d;--line:#33332f;--card:#1e1e1c;--accent:#7fb0ff;--go:#2f9a50;--go-fg:#fff;
--pass:#5fc77f;--fail:#ff8a80;--unknown:#e2c25b;--next:#1d2c20}}
:root[data-theme="dark"]{--bg:#141413;--fg:#ececea;--muted:#a3a39d;--line:#33332f;--card:#1e1e1c;
--accent:#7fb0ff;--go:#2f9a50;--go-fg:#fff;--pass:#5fc77f;--fail:#ff8a80;--unknown:#e2c25b;
--next:#1d2c20}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}
main{max-width:1440px;margin:0 auto;padding:16px}
header.top{display:flex;flex-wrap:wrap;gap:12px 24px;align-items:center;
justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:12px}
header.top h1{margin:0;font-size:1.6rem}
.sub{color:var(--muted);font-size:.88rem}
.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);
border-radius:8px;padding:8px 14px;cursor:pointer}
button#go{background:var(--go);color:var(--go-fg);border-color:var(--go);font-weight:700;
font-size:1.25rem;padding:10px 36px;letter-spacing:.06em}
button:disabled{opacity:.5;cursor:default}
#status{color:var(--muted)}
ol.cues{list-style:none;display:flex;gap:10px;padding:0;margin:14px 0;overflow-x:auto}
ol.cues>li{flex:1 0 210px;background:var(--card);border:1px solid var(--line);border-radius:8px;
padding:10px 12px}
ol.cues>li.next{border-color:var(--go);background:var(--next)}
ol.cues>li.done{opacity:.7}
.num{font-weight:700;font-variant-numeric:tabular-nums;margin-right:6px}
.chips{margin:6px 0 0;padding:0;list-style:none;font-size:.8rem;color:var(--muted)}
.chips li{margin:2px 0}
h2{font-size:1.05rem;margin:18px 0 8px}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
.pass{color:var(--pass);font-weight:600}.fail{color:var(--fail);font-weight:600}
.unknown,.running{color:var(--unknown);font-weight:600}
.badge{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:0 8px;
font-size:.78rem;color:var(--muted);white-space:nowrap}
.panels{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr));gap:14px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px;
display:flex;flex-direction:column;gap:6px;min-width:0}
.panel h3{margin:0;font-size:1rem}.role{margin:0;font-weight:600;color:var(--accent)}
.view{position:relative;border:1px solid var(--line);border-radius:6px;overflow:hidden;
background:#111;aspect-ratio:16/10}
.view iframe,.view img{position:absolute;inset:0;width:100%;height:100%;border:0;
object-fit:contain;background:#111}
.view .empty{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
color:#bbb;font-size:.9rem;padding:16px;text-align:center}
.view .empty[hidden],.view img[hidden]{display:none}
.note{font-size:.8rem;color:var(--muted);margin:0}
.panel a,footer a{color:var(--accent);overflow-wrap:anywhere}
.panel a{font-size:.85rem}
footer{margin-top:20px;border-top:1px solid var(--line);padding-top:10px;font-size:.9rem}
footer ul{padding-left:18px}
@media (max-width:520px){button#go{width:100%}}
"""

STAGE_SCRIPT = """
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g,
  c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
async function post(path) {
  const r = await fetch(path, {method: 'POST'});
  let body = {};
  try { body = await r.json(); } catch (e) {}
  return {ok: r.ok, status: r.status, body};
}
$('#go').addEventListener('click', async () => {
  $('#go').disabled = true;
  $('#status').textContent = 'GO sent to the hub';
  const r = await post('go');
  $('#status').textContent = r.ok ? `the hub fired cue ${r.body.number}, ${r.body.name}`
                                   : `the hub answered ${r.status}: ${r.body.detail || ''}`;
  $('#go').disabled = false;
});
$('#reset').addEventListener('click', async () => {
  const r = await post('reset');
  $('#status').textContent = r.ok ? 'the hub is back at the top of the list'
                                  : `reset failed: ${r.status}`;
});
const cell = (r) => `<span class="${esc(r)}">${esc(r)}</span>`;
function render(state) {
  const relays = state.relays || [];
  const done = relays.filter(r => r.done).map(r => String(r.number));
  const pointer = (state.hub || {}).pointer;
  document.querySelectorAll('ol.cues > li').forEach((li, i) => {
    li.classList.toggle('done', done.includes(li.dataset.cue));
    li.classList.toggle('next', pointer === i);
  });
  document.body.dataset.relayed = done.join(' ');
  const last = relays[relays.length - 1];
  if (!last) {
    $('#relay').innerHTML = '<tr><td>No cue has fired since the stage started or was reset.</td></tr>';
  } else {
    const rows = ['<tr><th>Member</th><th>Asked</th><th>Link</th><th>Result</th><th>Seen</th></tr>',
      `<tr><td>ShowRunner</td><td>fired cue ${esc(last.number)} and logged it</td>` +
      `<td><span class="badge">real</span></td><td>${cell('pass')}</td>` +
      `<td>CueLog entry ${esc(last.log_id)} at ${esc(last.at)}</td></tr>`];
    for (const p of last.problems || []) rows.push(`<tr><td colspan="5" class="fail">${esc(p)}</td></tr>`);
    for (const s of last.steps || []) {
      rows.push(`<tr><td>${esc(s.member)}</td><td>${esc(s.summary)}</td>` +
        `<td><span class="badge">${esc(s.link)}</span> <span class="sub">${esc(s.interface)}</span></td>` +
        `<td>${cell(s.result || 'running')}</td><td>${esc(s.detail || '')}</td></tr>`);
    }
    for (const m of last.idle || []) {
      rows.push(`<tr><td>${esc(m)}</td><td class="sub">nothing on this cue</td><td></td><td></td><td></td></tr>`);
    }
    $('#relay').innerHTML = rows.join('');
    $('#relay-title').textContent = `Cue ${last.number}, ${last.name}: member by member` +
      (last.done ? '' : ' (relaying)');
  }
  for (const [member, panel] of Object.entries(state.panels || {})) {
    const empty = document.getElementById('empty-' + member);
    const frame = document.getElementById('frame-' + member);
    if (frame && panel.frame && frame.dataset.src !== panel.frame) {
      frame.dataset.src = panel.frame;
      frame.src = panel.frame;
      if (empty) empty.hidden = true;
    }
    const img = document.getElementById('shot-' + member);
    if (img && panel.shot && img.dataset.want !== panel.shot) {
      img.dataset.want = panel.shot;
      const next = new Image();
      next.onload = () => { img.src = next.src; img.dataset.shown = panel.shot; img.hidden = false;
                            if (empty) empty.hidden = true; };
      next.src = panel.shot;
    }
  }
}
async function poll() {
  try {
    const r = await fetch('state', {cache: 'no-store'});
    if (r.ok) render(await r.json());
  } catch (e) {
    $('#status').textContent = 'the stage is not answering';
  }
  setTimeout(poll, 700);
}
poll();
"""


def stage_page(view: dict) -> str:
    """The stage as one page. `view` holds what does not change while it runs.

    Keys: `show` (the declared show), `hub_url`, `order` (members in panel
    order), `panels` (member -> role, shows, note, url, and `src` for a framed
    member that starts with a page), and `links` (from `links`). What changes --
    the hub's pointer, each relay, each picture -- arrives from the stage's
    `state` route.
    """
    from html import escape as e

    show = view["show"]
    cues = []
    for cue in show["cues"]:
        actions, _ = parse_family({"family": cue.get("family") or {}}, view["order"])
        chips = "".join(f"<li>{e(a.member)} {e(summary(a))}</li>" for a in actions)
        cues.append(f'<li data-cue="{cue["number"]}"><span class="num">{cue["number"]}</span>'
                    f'{e(cue["name"])}<ul class="chips">{chips}</ul></li>')
    panels = []
    for member in view["order"]:
        panel = view["panels"][member]
        if panel["shows"] == "frame":
            src = panel.get("src")
            body = (f'<iframe id="frame-{e(member)}" title="{e(member)}, live"'
                    + (f' src="{e(src)}" data-src="{e(src)}"' if src else "") + "></iframe>")
            if not src:
                body += (f'<div class="empty" id="empty-{e(member)}">Empty until a cue names '
                         f'{e(member)}.</div>')
        else:
            body = (f'<img id="shot-{e(member)}" alt="{e(member)}, the stage\'s own session" hidden>'
                    f'<div class="empty" id="empty-{e(member)}">The stage\'s own session of '
                    f'{e(member)} appears here once it is pictured.</div>')
        panels.append(
            f'<section class="panel" data-panel="{e(member)}"><h3>{e(member)}</h3>'
            f'<p class="role">{e(panel["role"])}</p><div class="view">{body}</div>'
            f'<p class="note">{e(panel["note"])}</p>'
            f'<a href="{e(panel["url"])}" target="_blank" rel="noopener">Open {e(member)} '
            f'yourself: {e(panel["url"])}</a></section>')
    link_rows = "".join(f'<li><strong>{e(r["member"])}</strong> '
                        f'<span class="badge">{e(r["link"])}</span> {e(r["says"])}</li>'
                        for r in view["links"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Family stage</title><style>{STAGE_STYLE}</style></head>
<body data-relayed=""><main>
<header class="top"><div><h1>{e(show["name"])}</h1>
<div class="sub">Cue list {e(show["cue_list"])}, fired by {e(HUB)}, the hub, at
<a href="{e(view["hub_url"])}" target="_blank" rel="noopener">{e(view["hub_url"])}</a></div></div>
<div class="controls"><button id="go" type="button">GO</button>
<button id="reset" type="button">Reset</button><span id="status" role="status"></span></div>
</header>
<ol class="cues">{"".join(cues)}</ol>
<h2 id="relay-title">The last cue, member by member</h2>
<div style="overflow-x:auto"><table id="relay"></table></div>
<h2>The family</h2>
<div class="panels">{"".join(panels)}</div>
<footer><h2>What links what</h2><ul>{link_rows}</ul>
<p><strong>App to app: none.</strong> {e(APP_TO_APP)}</p></footer>
</main><script>{STAGE_SCRIPT}</script></body></html>
"""
