#!/usr/bin/env python3
"""The family stage: a small show run from the hub, on one page.

    uv run qm family-demo --stage                  # run the show headless and record it
    uv run qm family-demo --stage --hold --open    # then keep it up and play it by hand

**What it shows.** `ci/family-demo.yaml` declares a show under `stage:` -- a
name, a cue list and a handful of cues, each with a `family` block -- and the
links that join the hub to each member. Once every core member is up, the stage
creates the show in ShowRunner through ShowRunner's own REST routes, never by
writing its database, and serves one page: the show's cues, a GO button that
calls ShowRunner's cue programmer, and a panel per member.

**The hub delivers; the stage watches.** A cue's `notes` is JSON, and its
`family` block names each member by its name in the hub's `[plugins.family]`
table, with the action the shared spec gives it:

    {"family": {"showstopper": {"clock": "start"},
                "carlos": {"patch": "<example name>"},
                "joe": {"take": {"notes": ["C4", "E4"], "seconds_per_note": 0.5}},
                "leo": {"song": "Blue Bossa"}}}

When the programmer fires the cue, ShowRunner itself delivers each action: it
POSTs a push member's action to that member's `/family/cue`, and holds a pull
member's for it to read from `/family/members/<name>`. The stage performs no
member action. It presses GO, then asserts what each member says about itself
-- a push member's `GET /family/state` names the cue just fired and the state
the action asks for, leo's followed chart shows the song -- and that the hub's
`GET /family/` shows a 2xx delivery to every member the cue named.

**Links are claimed narrowly.** A link is `app to app` when the hub reaches the
member with nothing in between, and the stage's check is what establishes it on
each run. A member the roster gives no link is `not linked`, and a linked one no
cue asks for anything is `not on any cue`.

**One member restarted while held.** The harness started every member, so the
harness restarts one: the stage's `POST /restart/<member>` leaves a request in
the run's control directory and waits for the harness's answer, and each panel
has a button that does the same. The harness also records what it did --
a restart, or a refresh asked for by a watched file under `--reload` -- and the
page reloads that member's frame when it sees one.

This module is the part that decides and holds no state: the action vocabulary,
the parser, the links, what a member's state must show, the seeding requests,
the restart protocol and the page. It imports nothing outside the standard
library, so the stage's runtime (`family_stage_run.py`, under the pinned
Playwright interpreter) and this corpus's tests both import it.
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

# The hub: it fires cues and delivers their family blocks, and is never sent one.
HUB = "ShowRunner"

# ShowRunner's cue layers. The stage's cues each carry one, because ShowRunner's
# script page cannot render a cue without a layer.
LAYERS = ("Lights", "Sound", "Video", "Audio", "Stage")

# The order members are listed in on the page: the quick, visible actions first
# and the take, which runs joe's whole pipeline, last.
ORDER = ("ShowStopper", "leo", "carlos", "joe")

# A member's name in a family block and in the hub's [plugins.family] table.
NAME = re.compile(r"^[A-Za-z0-9_-]+$")

# The shared spec's actions, by member: what each may be asked, and nothing else.
ACTIONS = {"ShowStopper": "clock", "carlos": "patch or turn", "joe": "take", "leo": "song"}
CLOCK = ("start", "stop", "reset", "lap")
NOTE = re.compile(r"^([A-G])([#b]?)(-?\d)$")
SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
MAX_NOTES = 16
SECONDS_PER_NOTE = (0.1, 4.0)

# How a panel shows its member. `frame`: the member's own page, live -- for a
# member whose state is shared by every page it serves, or set by the hub.
# `session`: the stage's own browser session of the member, pictured -- for a
# page that shows a result only once asked to fetch it.
PANEL_KINDS = ("frame", "session")


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


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def action_problems(member: str, action) -> list[str]:
    """Every way `action` is not one the shared spec gives `member`."""
    if not isinstance(action, dict) or len(action) != 1:
        return [f"{member}: an action is an object with exactly one key"]
    (key, value), = action.items()
    if member == "ShowStopper":
        if key != "clock":
            return [f"ShowStopper: no action {key!r}; it takes 'clock'"]
        return [] if value in CLOCK else [f"ShowStopper: clock must be one of {list(CLOCK)}"]
    if member == "carlos":
        if key not in ("patch", "turn"):
            return [f"carlos: no action {key!r}; it takes 'patch' or 'turn'"]
        return [] if _text(value) else [f"carlos: {key} must be non-empty text"]
    if member == "leo":
        if key != "song":
            return [f"leo: no action {key!r}; it takes 'song'"]
        return [] if _text(value) else ["leo: song must be non-empty text"]
    if member == "joe":
        if key != "take":
            return [f"joe: no action {key!r}; it takes 'take'"]
        return _take_problems(value)
    return [f"{member}: the shared spec gives it no actions"]


def _take_problems(take) -> list[str]:
    if not isinstance(take, dict):
        return ["joe: take must be an object with notes and seconds_per_note"]
    problems = [f"joe: take has no {key!r}" for key in sorted(set(take) - {"notes",
                                                                         "seconds_per_note"})]
    notes = take.get("notes")
    if not isinstance(notes, list) or not 1 <= len(notes) <= MAX_NOTES:
        problems.append(f"joe: take.notes must be a list of 1 to {MAX_NOTES} note names")
    else:
        for note in notes:
            try:
                note_number(note)
            except ValueError as exc:
                problems.append(f"joe: {exc}")
    seconds = take.get("seconds_per_note")
    low, high = SECONDS_PER_NOTE
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) \
            or not low <= seconds <= high:
        problems.append(f"joe: take.seconds_per_note must be a number from {low} to {high}")
    return problems


@dataclass(frozen=True)
class Action:
    """One member's part of one cue: its name in the block, who it is, what it is asked."""

    name: str      # the member's name in the family block and the hub's table
    member: str    # the roster member
    text: str      # the action, as sorted JSON, so an Action is hashable

    @property
    def value(self) -> dict:
        return json.loads(self.text)


def parse_family(notes, links: dict) -> tuple[list[Action], list[str]]:
    """(actions in page order, problems) for one cue's notes.

    `notes` is the cue's notes as ShowRunner holds them -- a JSON string -- or
    already parsed; `links` is the stage's link table, by block name. No notes,
    or notes with no `family` key, is a cue the family has nothing to do on.
    Anything else that is not a well-formed block is a problem, and a cue with a
    problem is refused whole, so a typo cannot half-run a cue.
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
    for name, action in family.items():
        link = links.get(name)
        if link is None:
            problems.append(f"{name} is not a linked member of this stage; "
                            f"it links {sorted(links)}")
            continue
        found = action_problems(link["member"], action)
        problems += found
        if not found:
            actions.append(Action(name, link["member"], json.dumps(action, sort_keys=True)))
    if problems:
        return [], problems
    rank = {member: i for i, member in enumerate(ORDER)}
    return sorted(actions, key=lambda a: rank.get(a.member, len(ORDER))), []


def summary(action: Action) -> str:
    """A cue chip: what the member is asked for, in a few words."""
    (key, value), = action.value.items()
    if key == "song":
        return f"shows {value}"
    if key == "take":
        return f"takes {' '.join(value['notes'])}"
    if key == "patch":
        return f"loads “{value}”"
    if key == "turn":
        return f"turns to the {value}"
    return {"start": "starts the clock", "stop": "stops the clock",
            "reset": "resets the clock", "lap": "laps the clock"}[value]


# ===================================================================
# THE LINKS -- who the hub delivers to, and how
# ===================================================================

def check_links(links, ports: dict[str, dict]) -> list[str]:
    """Every reason the stage's link table cannot be served as written.

    `ports` maps each running member to its ports by label. A link names the
    member (`member`) and how the hub reaches it: `push`, the label of the port
    where the member answers `POST /family/cue` and `GET /family/state`; or
    `pull`, the query that opens the member's page following the hub, with
    `{hub}` where the hub's address goes.
    """
    if not isinstance(links, dict) or not links:
        return ["stage.links must name at least one member the hub delivers to"]
    problems, seen = [], {}
    for name, link in links.items():
        where = f"stage.links.{name}"
        if not isinstance(name, str) or not NAME.match(name):
            problems.append(f"{where}: a name is letters, digits, - and _ only")
        if not isinstance(link, dict):
            problems.append(f"{where}: must be a mapping")
            continue
        member = link.get("member")
        if member == HUB:
            problems.append(f"{where}: {HUB} is the hub; it delivers, and is never sent a cue")
            continue
        if member not in ports:
            problems.append(f"{where}: {member!r} is not a running member")
            continue
        if member in seen:
            problems.append(f"{where}: {member} is already linked as {seen[member]}")
        seen[member] = name
        if member not in ACTIONS:
            problems.append(f"{where}: the shared spec gives {member} no actions")
        kinds = [k for k in ("push", "pull") if k in link]
        if len(kinds) != 1:
            problems.append(f"{where}: needs exactly one of push or pull")
        elif kinds == ["push"] and link["push"] not in ports[member]:
            problems.append(f"{where}: push names {link['push']!r}, which is not one of "
                            f"{member}'s ports {sorted(ports[member])}")
        elif kinds == ["pull"] and not (isinstance(link["pull"], str)
                                        and link["pull"].startswith("?")
                                        and "{hub}" in link["pull"]):
            problems.append(f"{where}: pull must be a query naming {{hub}}, like ?follow={{hub}}")
    return problems


def resolve_links(links: dict, members: dict, hub: str) -> dict:
    """Each link with its address: a push member's base URL, a pull member's followed page.

    `members` maps a member to its `url`, `host` and `ports`; `hub` is the hub's
    base URL, with no path.
    """
    resolved = {}
    for name, link in links.items():
        info = members[link["member"]]
        if "push" in link:
            resolved[name] = {"member": link["member"], "via": "push",
                              "url": f"http://{info['host']}:{info['ports'][link['push']]}"}
        else:
            page = info["url"].split("#", 1)[0].split("?", 1)[0]
            resolved[name] = {"member": link["member"], "via": "pull",
                              "page": page + link["pull"].replace("{hub}", hub)}
    return resolved


def hub_args(resolved: dict) -> list[str]:
    """What the hub's `serve` is handed, so its [plugins.family] table holds these links."""
    args = []
    for name, link in resolved.items():
        if link["via"] == "push":
            args += ["--family", f"{name}={link['url']}"]
    for name, link in resolved.items():
        if link["via"] == "pull":
            args += ["--family-pull", name]
    return args


def links(show: dict, link_table: dict, running: list[str] | set[str]) -> list[dict]:
    """What joins the hub to each running member in this show, claimed no wider than it is."""
    asked: set[str] = set()
    for cue in show.get("cues") or []:
        actions, _ = parse_family({"family": cue.get("family") or {}}, link_table)
        asked |= {a.member for a in actions}
    by_member = {link["member"]: (name, link) for name, link in link_table.items()}
    rows = [{"member": HUB, "link": "real",
             "says": "the stage presses GO through the hub's own programmer route; the hub "
                     "fires the cue, logs it, and delivers its family block itself"}]
    others = [m for m in ORDER if m in running] + sorted(set(running) - set(ORDER) - {HUB})
    for member in others:
        if member not in by_member:
            rows.append({"member": member, "link": "not linked",
                         "says": "the roster gives it no link, so no cue reaches it"})
            continue
        name, link = by_member[member]
        if member not in asked:
            rows.append({"member": member, "link": "not on any cue",
                         "says": f"linked as {name}, but no cue in this show asks it for anything"})
        elif "push" in link:
            rows.append({"member": member, "link": "app to app",
                         "says": f"the hub POSTs each action to {member}'s /family/cue; seen in "
                                 f"{member}'s GET /family/state and the hub's GET /family/"})
        else:
            rows.append({"member": member, "link": "app to app",
                         "says": f"{member}, opened following the hub, reads its action from the "
                                 f"hub's GET /family/members/{name}; seen on {member}'s own page "
                                 f"and in the hub's GET /family/"})
    return rows


APP_TO_APP = ("ShowRunner delivers each cue's family block itself: a push member is sent its "
              "action at /family/cue, and leo reads its own from the hub. The stage presses GO "
              "and only watches; it sends no member anything.")


# ===================================================================
# What a member must say -- read from its own GET /family/state
# ===================================================================

def judge(action: Action, fired: dict, answer) -> tuple[str, str]:
    """('pass' | 'wait' | 'fail', what was seen) for a push member's `GET /family/state`.

    `fired` is the cue object the hub sent: number, name and fired_at. The
    state must name that very fire -- the same `fired_at` -- and show what the
    action asks for. `wait` is a state that may still get there; `fail` is
    one that cannot, such as a take that failed.
    """
    if not isinstance(answer, dict):
        return "wait", f"answered {answer!r}"
    cue = answer.get("cue")
    if not isinstance(cue, dict) or cue.get("fired_at") != fired.get("fired_at"):
        last = cue.get("number") if isinstance(cue, dict) else None
        return "wait", f"its last cue is {last!r}, not this fire of cue {fired.get('number')}"
    state = answer.get("state")
    if not isinstance(state, dict):
        return "wait", f"state is {state!r}"
    (key, value), = action.value.items()
    if key == "clock":
        if value in ("start", "stop"):
            want = value == "start"
            ok = state.get("running") is want
            return ("pass" if ok else "wait"), f"running {state.get('running')}, " \
                                               f"elapsed {state.get('elapsed')}"
        if value == "lap":
            ok = isinstance(state.get("laps"), list) and len(state["laps"]) > 0
            return ("pass" if ok else "wait"), f"laps {state.get('laps')}"
        ok = state.get("running") is False and state.get("laps") == [] \
            and state.get("elapsed") == 0
        return ("pass" if ok else "wait"), f"running {state.get('running')}, " \
                                           f"elapsed {state.get('elapsed')}, laps {state.get('laps')}"
    if key == "patch":
        ok = state.get("patch") == value
        return ("pass" if ok else "wait"), f"patch {state.get('patch')!r}, " \
                                           f"revision {state.get('revision')}"
    if key == "turn":
        ok = state.get("facing") == value
        return ("pass" if ok else "wait"), f"facing {state.get('facing')!r}, " \
                                           f"revision {state.get('revision')}"
    if key == "take":
        if state.get("error"):
            return "fail", f"the take failed: {state['error']}"
        latest = state.get("latest") or {}
        mine = str(latest.get("file") or "").startswith(f"cue-{fired.get('number')}_")
        if state.get("busy") or not mine:
            return "wait", f"busy {state.get('busy')}, latest {latest.get('file')!r}"
        if not isinstance(latest.get("events"), int) or latest["events"] <= 0:
            return "fail", f"the take {latest.get('file')} has {latest.get('events')!r} note events"
        return "pass", f"{latest['events']} note events in {latest['file']}"
    return "fail", f"nothing says what {key!r} must show"


def deliveries(family: dict, number, before: set[str]) -> dict[str, dict]:
    """The hub's outcome for each member it was asked to reach on this fire of cue `number`.

    `family` is the hub's `GET /family/`; `before` holds every `fired_at` it
    listed before GO, so a fire of the same cue number from an earlier run of
    the show is not mistaken for this one.
    """
    found: dict[str, dict] = {}
    for outcome in family.get("last") or []:
        cue = outcome.get("cue") or {}
        if str(cue.get("number")) == str(number) and cue.get("fired_at") not in before:
            found[outcome.get("member")] = outcome
    return found


def fired_ats(family: dict) -> set[str]:
    return {(o.get("cue") or {}).get("fired_at") for o in family.get("last") or []}


def combine(results: list[str]) -> str:
    """One result from several: any fail fails, then any unknown is unknown."""
    if "fail" in results:
        return "fail"
    if "unknown" in results or not results:
        return "unknown"
    return "pass"


def link_evidence(rows: list[dict], check: dict | None) -> list[dict]:
    """Each link row with what this run's check saw of it: its deliveries and the member's word.

    The roster claims app to app; the label keeps that word only where every
    assertion of the link held. A link the check saw fail is labelled
    `failed`, and one it never asserted `not seen` -- never a pass, because the
    claim is the roster's until a check sees it.
    """
    cues = (check or {}).get("cues") or []
    out = []
    for row in rows:
        row = dict(row)
        if row["link"] == "app to app":
            held = [a for cue in cues for a in cue.get("assertions") or []
                    if a.get("member") == row["member"]]
            row["claimed"] = row["link"]
            if not held:
                row.update(result="unknown", link="not seen",
                           seen="not seen in this run: the show did not reach it")
            else:
                sent = [a for a in held if a.get("kind") == "delivery"]
                said = [a for a in held if a.get("kind") != "delivery"]
                row["result"] = combine([a["result"] for a in held])
                row["link"] = {"pass": "app to app", "fail": "failed"}.get(row["result"],
                                                                          "not seen")
                row["seen"] = (f"{sum(a['result'] == 'pass' for a in sent)} of {len(sent)} "
                               f"deliveries 2xx; {sum(a['result'] == 'pass' for a in said)} of "
                               f"{len(said)} times the member showed the cue")
        out.append(row)
    return out


# ===================================================================
# THE SHOW -- checked, and created through the hub's own routes
# ===================================================================

def check_show(show, link_table: dict) -> list[str]:
    """Every reason the declared show cannot be seeded and delivered as written."""
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
        _, found = parse_family({"family": cue["family"]}, link_table)
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


def panel_view(panels: dict, members: dict, resolved: dict) -> dict:
    """Each panel with its member's address, and the page a framed panel opens on.

    A framed panel opens on its member's page -- at `path` when the panel names
    one, and following the hub when the member pulls from it -- so every frame
    shows the member's own live page from the start.
    """
    following = {link["member"]: link["page"] for link in resolved.values()
                 if link["via"] == "pull"}
    view = {}
    for name, panel in panels.items():
        url = members[name]["url"]
        if panel.get("path"):
            url = url.rstrip("/") + "/" + panel["path"].lstrip("/")
        entry = {**panel, "url": following.get(name, url)}
        if panel["shows"] == "frame":
            entry["src"] = entry["url"]
        view[name] = entry
    return view


def check_stage(stage, running: list[str], ports: dict[int, str], span: tuple[int, int],
                member_ports: dict[str, dict] | None = None) -> list[str]:
    """Every reason the plan's `stage` block cannot run: its port, links, show and panels.

    `ports` maps each port the plan reserves to its member, `span` is the
    plan's port range, so the stage's port is held to the same rules as a
    member's, and `member_ports` maps each running member to its ports by label.
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
    member_ports = member_ports if member_ports is not None else {m: {} for m in running}
    problems += check_links(stage.get("links"), member_ports)
    link_table = stage.get("links") if isinstance(stage.get("links"), dict) else {}
    problems += check_show(stage.get("show"), link_table)
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


# ===================================================================
# RESTARTS -- the stage asks; the harness, which started the member, does it
# ===================================================================

# Kept in the control directory while the harness holds the family up, and
# removed when it stops: a restart is answered only then.
HOLDING = "holding"
# What the harness has done to each member while held, for the page to follow.
EVENTS = "events.json"


def write_json(path: Path, value) -> None:
    """Write a whole file or none: the other process never reads half of one."""
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")
    os.replace(temporary, path)


def request_restart(control: Path, member: str, timeout: float) -> dict:
    """Ask the holding harness to restart `member`, and wait for its answer.

    The answer's `result` is the harness's -- pass, fail or unknown, as it saw
    the member come back -- or `refused` when nothing holds the family, or
    `timeout` when the harness did not answer within `timeout` seconds.
    """
    if not (control / HOLDING).is_file():
        return {"member": member, "result": "refused",
                "detail": "nothing holds the family, so nothing can restart a member; "
                          "a restart is answered while `qm family-demo --hold` keeps it up"}
    nonce = uuid.uuid4().hex
    write_json(control / f"{nonce}.request", {"member": member, "nonce": nonce})
    done = control / f"{nonce}.done"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if done.is_file():
            answer = json.loads(done.read_text(encoding="utf-8"))
            done.unlink(missing_ok=True)
            return answer
        time.sleep(0.25)
    (control / f"{nonce}.request").unlink(missing_ok=True)
    return {"member": member, "result": "timeout",
            "detail": f"the harness did not answer within {timeout:.0f}s"}


def take_restart_requests(control: Path) -> list[dict]:
    """Every restart asked for since the last look, oldest first; each is taken once."""
    waiting = []
    for path in control.glob("*.request"):
        try:
            waiting.append((path.stat().st_mtime_ns, path))
        except OSError:  # withdrawn by a stage that stopped waiting
            continue
    taken = []
    for _, path in sorted(waiting):
        try:
            request = json.loads(path.read_text(encoding="utf-8"))
            path.unlink()
        except (OSError, ValueError):
            continue
        taken.append(request)
    return taken


def answer_restart(control: Path, nonce: str, answer: dict) -> None:
    write_json(control / f"{nonce}.done", answer)


def restart_status(answer: dict) -> int:
    """The HTTP status the stage answers a restart with."""
    return {"pass": 200, "refused": 409, "timeout": 504}.get(answer.get("result"), 502)


def note_event(control: Path, member: str, kind: str, record: dict) -> dict:
    """Count a `restart` or a `refresh` of `member` where the page can see it.

    Written by the harness alone. The page reloads a member's frame when its
    count moves, so a frame shows a restarted server, or a file the member
    reads afresh on every request, without anybody reloading it by hand.
    """
    counted = {"restart": "restarts", "refresh": "refreshes"}[kind]
    events = read_events(control)
    entry = events.setdefault(member, {"restarts": 0, "refreshes": 0})
    entry[counted] = entry.get(counted, 0) + 1
    entry["last"] = {"kind": kind, **record}
    write_json(control / EVENTS, events)
    return entry


def read_events(control: Path | None) -> dict:
    if control is None:
        return {}
    try:
        return json.loads((control / EVENTS).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


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
.unknown,.waiting{color:var(--unknown);font-weight:600}
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
.says{font-size:.8rem;margin:0;font-family:ui-monospace,monospace;overflow-wrap:anywhere}
.panel a,footer a{color:var(--accent);overflow-wrap:anywhere}
.panel a{font-size:.85rem}
.ops{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.ops button{padding:4px 10px;font-size:.85rem}
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
function delivered(o) {
  if (!o) return '<span class="unknown">not listed</span>';
  if (!o.done) return '<span class="waiting">waiting</span>';
  const ok = o.status >= 200 && o.status < 300;
  return `<span class="${ok ? 'pass' : 'fail'}">${esc(o.status ?? 'no answer')}</span>` +
         (o.ms != null ? ` <span class="sub">${esc(o.ms)} ms</span>` : '') +
         (o.error ? ` <span class="sub">${esc(o.error)}</span>` : '');
}
function render(state) {
  const fired = state.fired || [];
  const done = fired.map(f => String(f.number));
  const pointer = (state.hub || {}).pointer;
  document.querySelectorAll('ol.cues > li').forEach((li, i) => {
    li.classList.toggle('done', done.includes(li.dataset.cue));
    li.classList.toggle('next', pointer === i);
  });
  document.body.dataset.fired = done.join(' ');
  const last = fired[fired.length - 1];
  if (!last) {
    $('#deliveries').innerHTML = '<tr><td>No cue has fired since the stage started or was reset.</td></tr>';
  } else {
    const rows = ['<tr><th>Member</th><th>Asked</th><th>Link</th><th>The hub delivered</th>' +
                  '<th>The member says</th></tr>',
      `<tr><td>ShowRunner</td><td>fired cue ${esc(last.number)} and logged it</td>` +
      `<td><span class="badge">real</span></td><td class="pass">CueLog entry ${esc(last.log_id)}</td>` +
      `<td>${esc(last.at)}</td></tr>`];
    for (const p of last.problems || []) rows.push(`<tr><td colspan="5" class="fail">${esc(p)}</td></tr>`);
    for (const a of last.asked || []) {
      rows.push(`<tr><td>${esc(a.member)}</td><td>${esc(a.summary)}</td>` +
        `<td><span class="badge">app to app</span> <span class="sub">${esc(a.via)}</span></td>` +
        `<td>${delivered((last.deliveries || {})[a.name])}</td>` +
        `<td class="says">${esc(a.says || '')}</td></tr>`);
    }
    $('#deliveries').innerHTML = rows.join('');
    $('#deliveries-title').textContent = `Cue ${last.number}, ${last.name}: member by member`;
  }
  for (const [member, panel] of Object.entries(state.panels || {})) {
    const empty = document.getElementById('empty-' + member);
    const img = document.getElementById('shot-' + member);
    if (img && panel.shot && img.dataset.want !== panel.shot) {
      img.dataset.want = panel.shot;
      const next = new Image();
      next.onload = () => { img.src = next.src; img.dataset.shown = panel.shot; img.hidden = false;
                            if (empty) empty.hidden = true; };
      next.src = panel.shot;
    }
    const says = document.getElementById('says-' + member);
    if (says && panel.says !== undefined) says.textContent = panel.says;
  }
  follow(state.dev);
}
const seenEvents = {};
function refreshFrame(member) {
  const frame = document.getElementById('frame-' + member);
  if (frame) frame.src = frame.getAttribute('src');
}
document.querySelectorAll('[data-refresh]').forEach(b =>
  b.addEventListener('click', () => refreshFrame(b.dataset.refresh)));
document.querySelectorAll('[data-restart]').forEach(b => b.addEventListener('click', async () => {
  const member = b.dataset.restart, out = document.getElementById('op-' + member);
  b.disabled = true;
  out.textContent = 'restarting';
  const r = await post('restart/' + encodeURIComponent(member));
  out.textContent = r.ok ? `restarted: stopped and answering again in ${r.body.seconds}s`
                         : `${r.body.result || r.status}: ${r.body.detail || ''}`;
  b.disabled = false;
}));
function follow(events) {
  for (const [member, ev] of Object.entries(events || {})) {
    const count = (ev.restarts || 0) + (ev.refreshes || 0);
    if (seenEvents[member] === undefined) { seenEvents[member] = count; continue; }
    if (count === seenEvents[member]) continue;
    seenEvents[member] = count;
    if (!ev.last || ev.last.result === 'pass') refreshFrame(member);
    const out = document.getElementById('op-' + member);
    if (out && ev.last) out.textContent = ev.last.summary || '';
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
    order), `links` (the link table, by block name), `panels` (member -> role,
    shows, note, url, and `src` for a framed member) and `rows` (from
    `links`). What changes -- the hub's pointer, its deliveries, what each
    member says, each picture -- arrives from the stage's `state` route.
    """
    from html import escape as e

    show = view["show"]
    cues = []
    for cue in show["cues"]:
        actions, _ = parse_family({"family": cue.get("family") or {}}, view["links"])
        chips = "".join(f"<li>{e(a.member)} {e(summary(a))}</li>" for a in actions)
        cues.append(f'<li data-cue="{cue["number"]}"><span class="num">{cue["number"]}</span>'
                    f'{e(cue["name"])}<ul class="chips">{chips}</ul></li>')
    panels = []
    for member in view["order"]:
        panel = view["panels"][member]
        if panel["shows"] == "frame":
            body = (f'<iframe id="frame-{e(member)}" title="{e(member)}, live" '
                    f'src="{e(panel["src"])}"></iframe>')
        else:
            body = (f'<img id="shot-{e(member)}" alt="{e(member)}, the stage\'s own session" hidden>'
                    f'<div class="empty" id="empty-{e(member)}">The stage\'s own session of '
                    f'{e(member)} appears here once it is pictured.</div>')
        linked = any(link["member"] == member for link in view["links"].values())
        says = (f'<p class="says" id="says-{e(member)}"></p>' if linked else "")
        refresh = (f'<button type="button" data-refresh="{e(member)}">Reload view</button>'
                   if panel["shows"] == "frame" else "")
        ops = (f'<div class="ops"><button type="button" data-restart="{e(member)}">Restart '
               f'{e(member)}</button>{refresh}<span class="sub" id="op-{e(member)}" '
               f'role="status"></span></div>')
        panels.append(
            f'<section class="panel" data-panel="{e(member)}"><h3>{e(member)}</h3>'
            f'<p class="role">{e(panel["role"])}</p><div class="view">{body}</div>{says}{ops}'
            f'<p class="note">{e(panel["note"])}</p>'
            f'<a href="{e(panel["url"])}" target="_blank" rel="noopener">Open {e(member)} '
            f'yourself: {e(panel["url"])}</a></section>')
    link_rows = "".join(f'<li><strong>{e(r["member"])}</strong> '
                        f'<span class="badge">{e(r["link"])}</span> {e(r["says"])}</li>'
                        for r in view["rows"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Family stage</title><style>{STAGE_STYLE}</style></head>
<body data-fired=""><main>
<header class="top"><div><h1>{e(show["name"])}</h1>
<div class="sub">Cue list {e(show["cue_list"])}, fired by {e(HUB)}, the hub, at
<a href="{e(view["hub_url"])}" target="_blank" rel="noopener">{e(view["hub_url"])}</a></div></div>
<div class="controls"><button id="go" type="button">GO</button>
<button id="reset" type="button">Reset</button><span id="status" role="status"></span></div>
</header>
<ol class="cues">{"".join(cues)}</ol>
<h2 id="deliveries-title">The last cue, member by member</h2>
<div style="overflow-x:auto"><table id="deliveries"></table></div>
<h2>The family</h2>
<div class="panels">{"".join(panels)}</div>
<footer><h2>What links what</h2><ul>{link_rows}</ul>
<p><strong>App to app.</strong> {e(APP_TO_APP)}</p></footer>
</main><script>{STAGE_SCRIPT}</script></body></html>
"""
