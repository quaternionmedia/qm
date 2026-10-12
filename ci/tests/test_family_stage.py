"""The family stage's rules, checked without starting anything.

Hermetic: no port is bound, no member runs, no browser is launched. What is
tested is the part that decides -- which actions a cue may ask of which
member, how the stage's links become the hub's own table, what a member's
state must show for a cue to have arrived, which deliveries are this fire's,
what the stage asks the hub to create, which links it may claim, and what the
page and the run's landing page say -- and that the stage, while it runs, sends
no member anything. Running the show is the demo's own check
(`uv run qm family-demo --stage`).

Each guard was broken once and seen to go red; the mutation is named in the
test that caught it.
"""

from __future__ import annotations

import copy
import json
import sys
import threading
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import family_demo  # noqa: E402
import family_stage as fs  # noqa: E402
import family_stage_run  # noqa: E402
import roster  # noqa: E402

RUNNING = ["ShowRunner", "ShowStopper", "carlos", "joe", "leo"]
MEMBERS = {
    "ShowRunner": {"url": "http://127.0.0.1:18400/", "host": "127.0.0.1", "ports": {"http": 18400}},
    "ShowStopper": {"url": "http://127.0.0.1:18410/", "host": "127.0.0.1", "ports": {"web": 18410}},
    "carlos": {"url": "http://127.0.0.1:18420/rack", "host": "127.0.0.1", "ports": {"http": 18420}},
    "joe": {"url": "http://127.0.0.1:18430/joe/", "host": "127.0.0.1",
            "ports": {"web": 18430, "api": 18431, "qmcp": 18432}},
    "leo": {"url": "http://127.0.0.1:18440/", "host": "127.0.0.1", "ports": {"web": 18440}},
}
PORTS = {name: info["ports"] for name, info in MEMBERS.items()}
HUB_BASE = "http://127.0.0.1:18400"
FIRED = {"number": "3", "name": "Second tune", "fired_at": "2026-10-10T21:00:00.000001+00:00"}


def plan() -> dict:
    return family_demo.load_plan()


def stage() -> dict:
    return copy.deepcopy(plan()["stage"])


def links() -> dict:
    return stage()["links"]


def resolved() -> dict:
    return fs.resolve_links(links(), MEMBERS, HUB_BASE)


def plan_problems(document: dict) -> list[str]:
    return family_demo.check_plan(document, {e["name"] for e in roster.load()})


def action(name: str, value: dict) -> fs.Action:
    actions, problems = fs.parse_family({"family": {name: value}}, links())
    assert problems == [], problems
    return actions[0]


# --- the family block -------------------------------------------------------

def test_a_cue_without_a_family_block_asks_nothing_and_is_not_a_problem():
    assert fs.parse_family(None, links()) == ([], [])
    assert fs.parse_family("", links()) == ([], [])
    assert fs.parse_family('{"osc": {"address": "/go"}}', links()) == ([], [])


def test_a_family_block_names_members_as_the_hub_does_and_asks_the_spec_s_actions():
    notes = json.dumps({"family": {
        "joe": {"take": {"notes": ["C4", "E4"], "seconds_per_note": 0.5}},
        "leo": {"song": "Blue Bossa"}, "showstopper": {"clock": "start"}}})
    actions, problems = fs.parse_family(notes, links())
    assert problems == []
    assert [(a.name, a.member) for a in actions] == [("showstopper", "ShowStopper"),
                                                     ("leo", "leo"), ("joe", "joe")]
    assert actions[2].value == {"take": {"notes": ["C4", "E4"], "seconds_per_note": 0.5}}


@pytest.mark.parametrize("family, says", [
    ({"ShowStopper": {"clock": "start"}}, "ShowStopper is not a linked member of this stage"),
    ({"wolf": {"play": True}}, "wolf is not a linked member of this stage"),
    ({"leo": {"do": "show", "song": "Blue Bossa"}}, "leo: an action is an object with exactly one key"),
    ({"leo": {"scroll": 3}}, "leo: no action 'scroll'; it takes 'song'"),
    ({"leo": {"song": " "}}, "leo: song must be non-empty text"),
    ({"showstopper": {"clock": "pause"}}, "ShowStopper: clock must be one of"),
    ({"carlos": {"spin": "back"}}, "carlos: no action 'spin'; it takes 'patch' or 'turn'"),
    ({"carlos": {"patch": ""}}, "carlos: patch must be non-empty text"),
    ({"joe": {"take": {"notes": ["C4", "H9"], "seconds_per_note": 0.5}}}, "'H9' is not a note name"),
    ({"joe": {"take": {"notes": [], "seconds_per_note": 0.5}}}, "take.notes must be a list of 1 to"),
    ({"joe": {"take": {"notes": ["C4"]}}}, "take.seconds_per_note must be a number from 0.1 to 4.0"),
    ({"joe": {"take": {"notes": ["C4"], "seconds_per_note": 9}}}, "from 0.1 to 4.0"),
    ({"joe": {"take": {"notes": ["C4"], "seconds_per_note": 0.5, "tempo": 1}}},
     "joe: take has no 'tempo'"),
    ({"joe": {"take": "C4"}}, "joe: take must be an object"),
    ({}, "family must be an object naming at least one member"),
])
def test_a_malformed_family_block_is_refused_with_its_reason(family, says):
    """Mutation: the exactly-one-key rule dropped, so `do` passed beside `song` -- red."""
    actions, problems = fs.parse_family({"family": family}, links())
    assert actions == []
    assert any(says in p for p in problems), problems


def test_one_bad_member_means_the_cue_asks_nothing():
    """A typo must not half-run a cue: the stage refuses the cue before seeding it.

    Mutation: returning the good actions alongside the problems -- red here.
    """
    actions, problems = fs.parse_family({"family": {"leo": {"song": "Blue Bossa"},
                                                    "carlos": {"spin": "back"}}}, links())
    assert actions == [] and problems


def test_notes_that_are_not_json_or_not_an_object_are_a_problem_not_an_empty_cue():
    assert fs.parse_family("{family: leo}", links())[1][0].startswith("notes are not JSON")
    assert fs.parse_family("[1, 2]", links()) == ([], ["notes must be a JSON object"])


@pytest.mark.parametrize("name, number", [("C4", 60), ("A4", 69), ("F#3", 54), ("Bb2", 46),
                                          ("C-1", 0), ("G9", 127)])
def test_note_names_are_midi_numbers(name, number):
    assert fs.note_number(name) == number


@pytest.mark.parametrize("name", ["c4", "H2", "C", "G#9", "", None, "C10"])
def test_a_note_that_is_not_one_is_refused(name):
    with pytest.raises(ValueError):
        fs.note_number(name)


def test_each_chip_says_what_its_member_is_asked():
    asked = [action("showstopper", {"clock": "start"}), action("carlos", {"turn": "back"}),
             action("carlos", {"patch": "A grid"}), action("leo", {"song": "Blue Bossa"}),
             action("joe", {"take": {"notes": ["C4", "E4"], "seconds_per_note": 0.5}}),
             action("showstopper", {"clock": "stop"})]
    assert [fs.summary(a) for a in asked] == ["starts the clock", "turns to the back",
                                              "loads “A grid”", "shows Blue Bossa",
                                              "takes C4 E4", "stops the clock"]


# --- the links: the roster's table, the hub's table -----------------------------

def test_the_links_become_the_hub_s_own_table_on_its_command_line():
    """What the hub's `serve` is handed, so ShowRunner writes [plugins.family] from the roster.

    Mutation: hub_args left the pull members out -- red here.
    """
    assert resolved() == {
        "showstopper": {"member": "ShowStopper", "via": "push", "url": "http://127.0.0.1:18410"},
        "carlos": {"member": "carlos", "via": "push", "url": "http://127.0.0.1:18420"},
        "joe": {"member": "joe", "via": "push", "url": "http://127.0.0.1:18431"},
        "leo": {"member": "leo", "via": "pull",
                "page": "http://127.0.0.1:18440/?follow=http://127.0.0.1:18400"},
    }
    assert fs.hub_args(resolved()) == [
        "--family", "showstopper=http://127.0.0.1:18410",
        "--family", "carlos=http://127.0.0.1:18420",
        "--family", "joe=http://127.0.0.1:18431",
        "--family-pull", "leo",
    ]


def test_a_followed_page_drops_the_member_s_own_path_and_hash():
    info = {**MEMBERS, "leo": {**MEMBERS["leo"], "url": "http://127.0.0.1:18440/?x=1#!/song/A"}}
    page = fs.resolve_links({"leo": {"member": "leo", "pull": "?follow={hub}"}}, info, HUB_BASE)
    assert page["leo"]["page"] == "http://127.0.0.1:18440/?follow=http://127.0.0.1:18400"


@pytest.mark.parametrize("change, says", [
    (lambda l: l.clear(), "stage.links must name at least one member"),
    (lambda l: l.update(joe={"member": "joe", "push": "qmcp2"}),
     "stage.links.joe: push names 'qmcp2', which is not one of joe's ports"),
    (lambda l: l.update(joe={"member": "joe"}), "stage.links.joe: needs exactly one of push or pull"),
    (lambda l: l.update(joe={"member": "joe", "push": "api", "pull": "?f={hub}"}),
     "needs exactly one of push or pull"),
    (lambda l: l.update(leo={"member": "leo", "pull": "?follow=hub"}),
     "stage.links.leo: pull must be a query naming {hub}"),
    (lambda l: l.update(hub={"member": "ShowRunner", "push": "http"}), "ShowRunner is the hub"),
    (lambda l: l.update(wolf={"member": "wolf", "push": "main"}), "'wolf' is not a running member"),
    (lambda l: l.update(clock={"member": "ShowStopper", "push": "web"}),
     "stage.links.clock: ShowStopper is already linked as showstopper"),
    (lambda l: l.update({"show stopper": {"member": "ShowStopper", "push": "web"}}),
     "a name is letters, digits, - and _ only"),
])
def test_a_link_the_hub_could_not_be_given_is_refused(change, says):
    table = links()
    change(table)
    found = fs.check_links(table, PORTS)
    assert any(says in p for p in found), found


def test_a_linked_member_the_spec_gives_no_actions_is_refused():
    found = fs.check_links({"wolf": {"member": "wolf", "push": "main"}}, {"wolf": {"main": 1}})
    assert found == ["stage.links.wolf: the shared spec gives wolf no actions"]


# --- what a member must say -----------------------------------------------------

def state(cue=FIRED, **values) -> dict:
    return {"member": "x", "cue": cue, "state": values}


@pytest.mark.parametrize("asked, answer, verdict", [
    ({"clock": "start"}, state(running=True, elapsed=0.4, laps=[]), "pass"),
    ({"clock": "start"}, state(running=False, elapsed=0, laps=[]), "wait"),
    ({"clock": "stop"}, state(running=False, elapsed=12.3, laps=[]), "pass"),
    ({"clock": "lap"}, state(running=True, elapsed=3, laps=[2.9]), "pass"),
    ({"clock": "lap"}, state(running=True, elapsed=3, laps=[]), "wait"),
    ({"clock": "reset"}, state(running=False, elapsed=0, laps=[]), "pass"),
    ({"clock": "reset"}, state(running=False, elapsed=0.2, laps=[]), "wait"),
])
def test_the_clock_must_show_what_its_action_asks(asked, answer, verdict):
    assert fs.judge(action("showstopper", asked), FIRED, answer)[0] == verdict


@pytest.mark.parametrize("asked, answer, verdict", [
    ({"patch": "A grid"}, state(patch="A grid", facing="front", revision=2), "pass"),
    ({"patch": "A grid"}, state(patch=None, facing="front", revision=0), "wait"),
    ({"turn": "back"}, state(patch="A grid", facing="back", revision=3), "pass"),
    ({"turn": "back"}, state(patch="A grid", facing="front", revision=3), "wait"),
])
def test_the_rack_must_show_the_patch_or_the_facing(asked, answer, verdict):
    assert fs.judge(action("carlos", asked), FIRED, answer)[0] == verdict


TAKE = {"take": {"notes": ["C4"], "seconds_per_note": 0.5}}


@pytest.mark.parametrize("answer, verdict, says", [
    (state(latest={"file": "cue-3_20261010_210001_1.wav", "events": 12}, busy=False, error=None),
     "pass", "12 note events in cue-3_"),
    (state(latest=None, busy=True, error=None), "wait", "busy True"),
    (state(latest={"file": "cue-2_20261010_205900_1.wav", "events": 9}, busy=False, error=None),
     "wait", "cue-2_"),
    (state(latest={"file": "cue-3_20261010_210001_1.wav", "events": 0}, busy=False, error=None),
     "fail", "has 0 note events"),
    (state(latest=None, busy=False, error="RuntimeError: the pipeline exited 1"), "fail",
     "the take failed"),
])
def test_the_take_must_be_this_cue_s_and_finished(answer, verdict, says):
    """Mutation: the cue-<n>_ prefix test dropped, so cue 2's take passed for cue 3 -- red."""
    got = fs.judge(action("joe", TAKE), FIRED, answer)
    assert got[0] == verdict and says in got[1], got


def test_a_state_that_names_another_fire_is_not_this_cue_however_it_reads():
    """The state must name this very fire, by its fired_at, not just the cue number.

    Mutation: judge compared cue numbers instead of fired_at -- red here.
    """
    earlier = {**FIRED, "fired_at": "2026-10-10T20:00:00+00:00"}
    verdict, says = fs.judge(action("showstopper", {"clock": "start"}), FIRED,
                             state(cue=earlier, running=True, elapsed=1, laps=[]))
    assert verdict == "wait" and "not this fire of cue 3" in says
    assert fs.judge(action("leo", {"song": "x"}), FIRED, None)[0] == "wait"


def test_only_this_fire_s_deliveries_are_its_own():
    """A delivery listed before GO -- the same cue, fired in an earlier run -- is not this one.

    Mutation: deliveries() ignoring `before` -- red here.
    """
    old = {**FIRED, "fired_at": "earlier"}
    family = {"last": [
        {"cue": old, "member": "leo", "status": 200, "done": True},
        {"cue": FIRED, "member": "leo", "status": None, "done": False},
        {"cue": {**FIRED, "number": "4"}, "member": "joe", "status": 202, "done": True},
    ]}
    before = {"earlier"}
    assert fs.deliveries(family, 3, before) == {"leo": family["last"][1]}
    # This fire not listed at all: the earlier fire's 200 must not stand in for it.
    assert fs.deliveries({"last": family["last"][:1]}, 3, before) == {}
    assert fs.deliveries(family, "4", before)["joe"]["status"] == 202
    assert fs.fired_ats(family) == {"earlier", FIRED["fired_at"]}


def test_a_link_is_labelled_with_what_the_check_saw_of_it():
    """App to app only where every assertion of it held; failed, or not seen, otherwise.

    Mutation: link_evidence passing a link no assertion named -- red here.
    Mutation: a failed link keeping its app-to-app label -- red here.
    """
    rows = fs.links(stage()["show"], links(), RUNNING)
    check = {"cues": [{"assertions": [
        {"member": "joe", "kind": "delivery", "result": "pass"},
        {"member": "joe", "kind": "state", "result": "pass"},
        {"member": "leo", "kind": "delivery", "result": "pass"},
        {"member": "leo", "kind": "page", "result": "fail"}]}]}
    seen = {r["member"]: r for r in fs.link_evidence(rows, check)}
    assert (seen["joe"]["result"], seen["joe"]["seen"]) == (
        "pass", "1 of 1 deliveries 2xx; 1 of 1 times the member showed the cue")
    assert seen["joe"]["link"] == "app to app"
    assert (seen["leo"]["result"], seen["leo"]["link"]) == ("fail", "failed")
    assert (seen["carlos"]["result"], seen["carlos"]["link"]) == ("unknown", "not seen")
    assert seen["carlos"]["claimed"] == "app to app"
    assert "not seen in this run" in seen["carlos"]["seen"]
    assert "result" not in seen["ShowRunner"]


# --- the show, the panels and the links ------------------------------------------

def test_the_committed_show_links_and_panels_can_run_as_written():
    assert fs.check_links(links(), PORTS) == []
    assert fs.check_show(stage()["show"], links()) == []
    assert fs.check_panels(stage()["panels"], RUNNING) == []
    assert plan_problems(plan()) == []


def test_every_core_member_is_linked_app_to_app_and_asked_for_something():
    rows = {r["member"]: r["link"] for r in fs.links(stage()["show"], links(), RUNNING)}
    assert rows == {"ShowRunner": "real", "ShowStopper": "app to app", "leo": "app to app",
                    "carlos": "app to app", "joe": "app to app"}


def test_a_link_is_claimed_no_wider_than_it_is():
    """Mutation: every linked member reported `app to app` regardless of the cues -- red here."""
    show = {"cues": [{"family": {"leo": {"song": "A"}}}]}
    table = {k: v for k, v in links().items() if k != "carlos"}
    rows = {r["member"]: r for r in fs.links(show, table, RUNNING + ["wolf"])}
    assert rows["leo"]["link"] == "app to app" and "GET /family/members/leo" in rows["leo"]["says"]
    assert rows["joe"]["link"] == "not on any cue"
    assert rows["carlos"]["link"] == "not linked"
    assert rows["wolf"]["link"] == "not linked"
    assert rows["ShowRunner"]["link"] == "real"
    assert "sends no member anything" in fs.APP_TO_APP


@pytest.mark.parametrize("change, says", [
    (lambda s: s["cues"][1].update(number=1), "number is used twice"),
    (lambda s: s["cues"].reverse(), "must be listed in cue order"),
    (lambda s: s["cues"][0].update(layer="Smoke"), "layer must be one of"),
    (lambda s: s["cues"][0].pop("family"), "has no family block"),
    (lambda s: s["cues"][0]["family"].update(leo={"song": ""}), "leo: song must be non-empty"),
    (lambda s: s["cues"][0]["family"].update(ShowStopper={"clock": "start"}),
     "ShowStopper is not a linked member"),
    (lambda s: s["cues"][0].update(number=0), "number must be a positive whole number"),
    (lambda s: s.update(cues=[]), "must list at least one cue"),
    (lambda s: s.update(name=" "), "stage.show.name must be non-empty text"),
])
def test_a_show_that_cannot_be_seeded_as_written_is_refused(change, says):
    show = stage()["show"]
    change(show)
    found = fs.check_show(show, links())
    assert any(says in p for p in found), found


@pytest.mark.parametrize("number", ["1", True, 1.0])
def test_a_cue_number_is_a_whole_number_and_nothing_that_looks_like_one(number):
    show = stage()["show"]
    show["cues"][0]["number"] = number
    assert "cue " + str(number) + ": number must be a positive whole number" in \
        fs.check_show(show, links())


@pytest.mark.parametrize("change, says", [
    (lambda p: p.pop("joe"), "joe has no panel"),
    (lambda p: p["leo"].update(role="two\nlines"), "role must be one line"),
    (lambda p: p["leo"].update(shows="poster"), "shows must be one of"),
    (lambda p: p["ShowRunner"].update(shows="session"), "the hub's state is on its server"),
    (lambda p: p["leo"].pop("note"), "needs a note saying what the panel is"),
    (lambda p: p.update(wolf={"role": "x", "shows": "frame", "note": "y"}),
     "wolf is not a running member"),
])
def test_a_panel_that_cannot_be_shown_is_refused(change, says):
    panels = stage()["panels"]
    change(panels)
    assert any(says in p for p in fs.check_panels(panels, RUNNING)), fs.check_panels(panels, RUNNING)


def test_the_stage_port_and_links_are_held_to_the_plan_s_rules():
    """Mutation: check_stage stopped checking the links -- the last case went green."""
    document = plan()
    document["stage"]["port"] = document["ports"]["last"] + 1
    assert any(p.startswith("stage: port") and "outside" in p for p in plan_problems(document))
    document["stage"]["port"] = 18440
    assert "stage: port 18440 is already leo's" in plan_problems(document)
    document = plan()
    document["stage"]["links"]["joe"]["push"] = "nowhere"
    assert any("push names 'nowhere'" in p for p in plan_problems(document))


def test_a_stage_without_its_hub_is_refused():
    assert any("the hub, is not a running member" in p
               for p in fs.check_stage(stage(), ["leo", "joe"], {}, (18400, 18499),
                                       {"leo": {"web": 1}, "joe": {"api": 2}}))


@pytest.mark.parametrize("port, ok", [(18400, True), (18499, True), (18399, False),
                                      (18500, False), (True, False), ("18405", False)])
def test_the_stage_port_is_a_whole_number_inside_the_range(port, ok):
    document = stage()
    document["port"] = port
    found = fs.check_stage(document, RUNNING, {}, (18400, 18499), PORTS)
    assert (found == []) == ok, found


def test_the_show_is_created_through_the_hub_s_routes_in_order():
    """The stage writes nothing but requests: show, cue list, then each cue with its block."""
    calls = []
    ids = iter(range(1, 100))

    def call(method, path, params=None, body=None):
        calls.append((method, path, params, body))
        return {"id": next(ids)}

    show = stage()["show"]
    seeded = fs.seed(show, call)
    assert calls[0] == ("POST", "/db/shows", {"name": "Demo night"}, None)
    assert calls[1] == ("POST", "/db/shows/1/cue-lists", None, {"name": "Main"})
    assert [c[1] for c in calls[2:]] == ["/db/cue-lists/2/cues"] * len(show["cues"])
    first = calls[2][3]
    assert (first["number"], first["name"], first["layer"]) == (1, "House open", "Stage")
    assert json.loads(first["notes"]) == {"family": show["cues"][0]["family"]}
    assert seeded["show_id"] == 1 and seeded["cue_list_id"] == 2


def test_every_frame_opens_on_its_member_s_own_live_page():
    """leo's frame follows the hub from the start; no frame waits for a cue to be filled.

    Mutation: panel_view ignoring the pull link, so leo's frame opened on its home -- red.
    """
    view = fs.panel_view(stage()["panels"], MEMBERS, resolved())
    assert view["ShowRunner"]["src"] == "http://127.0.0.1:18400/programmer"
    assert view["leo"]["src"] == "http://127.0.0.1:18440/?follow=http://127.0.0.1:18400"
    assert view["ShowStopper"]["src"] == "http://127.0.0.1:18410/"
    assert view["carlos"]["src"] == "http://127.0.0.1:18420/rack"
    assert "src" not in view["joe"] and view["joe"]["shows"] == "session"


def test_the_stage_page_has_go_a_panel_per_member_and_says_who_delivers():
    show = stage()["show"]
    page = fs.stage_page({"show": show, "hub_url": "http://127.0.0.1:18400/", "order": RUNNING,
                          "links": links(),
                          "panels": fs.panel_view(stage()["panels"], MEMBERS, resolved()),
                          "rows": fs.links(show, links(), RUNNING)})
    assert '<button id="go"' in page
    for member in RUNNING:
        assert f'data-panel="{member}"' in page
    assert ('id="frame-leo" title="leo, live" '
            'src="http://127.0.0.1:18440/?follow=http://127.0.0.1:18400"') in page
    assert 'id="shot-joe"' in page and 'id="frame-joe"' not in page
    assert 'id="says-joe"' in page and 'id="says-ShowRunner"' not in page
    assert "<strong>App to app.</strong>" in page and "relayed" not in page
    assert page.count('<li data-cue="') == len(show["cues"])
    assert "leo shows Autumn Leaves" in page


# --- the runtime: what it names, and what it never does ---------------------------

def test_only_the_runtime_names_a_member_s_page():
    """The member owns its selectors; the stage's runtime is the one exception, and it alone.

    Mutation: LEO_TITLE's selector pasted into family_demo.py -- red here.
    """
    surfaces = [family_stage_run.LEO_TITLE, family_stage_run.LEO_FOLLOWING,
                family_stage_run.JOE_FETCH, family_stage_run.JOE_META,
                family_stage_run.JOE_RESULTS_TOGGLE]
    for source in ("family_demo.py", "family_demo_probes.py", "family_stage.py"):
        text = (CI_DIR / source).read_text(encoding="utf-8")
        for surface in surfaces:
            assert surface not in text, f"{source} names {surface!r}"


def test_nothing_in_the_harness_posts_a_cue_to_a_member():
    """The hub delivers; the harness never names the route a member is delivered on.

    Mutation: a relay to joe's /family/cue pasted into family_stage_run.py -- red here.
    """
    for source in ("family_demo.py", "family_stage_run.py"):
        assert "/family/cue" not in (CI_DIR / source).read_text(encoding="utf-8"), source


def test_while_it_runs_the_stage_only_reads_the_members(monkeypatch, tmp_path):
    """The watcher, given a hub that fired a cue, asks each member only GET /family/state.

    Mutation: the watcher POSTing the cue's action to a push member -- red here.
    """
    job = {"hub": "http://127.0.0.1:18400/", "dir": str(tmp_path), "port": 18405,
           "links": links(), "resolved": resolved(), "show": stage()["show"]}
    cue = {"id": 7, "number": "2", "name": "Count in",
           "notes": fs.cue_notes(stage()["show"]["cues"][1])}
    fired = [{"id": 1, "cue_id": 7, "triggered_at": "t"}]
    logs = iter([[]])  # nothing logged when the stage starts; the fire after that
    asked: list[tuple[str, str]] = []

    def http(method, url, params=None, body=None, timeout=10.0):
        asked.append((method, url))
        if url.endswith("/logs"):
            return 200, next(logs, fired)
        if url.endswith("/cues"):
            return 200, [cue]
        if url.endswith("/programmer/status"):
            return 200, {"pointer": 2}
        if url.endswith("/family/"):
            return 200, {"members": {}, "last": [
                {"cue": {**FIRED, "number": "2"}, "member": "joe", "status": 202, "done": True}]}
        if url.endswith("/family/state"):
            return 200, {"member": "x", "cue": None, "state": {}}
        raise AssertionError(f"the stage asked {method} {url}")

    monkeypatch.setattr(family_stage_run, "http", http)
    running = family_stage_run.Stage(job)
    running.seeded = {"show_id": 1, "cue_list_id": 2}
    thread = threading.Thread(target=running.watch, daemon=True)
    thread.start()
    thread.join(1.6)
    running.stopping.set()
    thread.join(2)

    assert running.failed == ""
    members = [(m, u) for m, u in asked if not u.startswith("http://127.0.0.1:18400")]
    assert members and {m for m, _ in members} == {"GET"}
    assert {u for _, u in members} == {f"{link['url']}/family/state"
                                       for link in resolved().values() if link["via"] == "push"}
    assert [a["member"] for a in running.history[0]["asked"]] == ["ShowStopper", "joe"]


# --- the harness: the stage wave's rules ------------------------------------

def test_a_member_whose_own_check_is_not_asked_takes_its_isolation_s_result():
    """Mutation: own_check ignored, so the stage's members all read unknown -- red here."""
    demo = [{"check": "ports-held-by-this-run", "owner": "demo", "result": "pass"}]
    assert family_demo.member_result(demo, "pass", own_check=False) == "pass"
    assert family_demo.member_result(demo, "pass") == "unknown"
    failing = demo + [{"check": "checkout-untouched", "owner": "demo", "result": "fail"}]
    assert family_demo.member_result(failing, "pass", own_check=False) == "fail"


@pytest.mark.parametrize("argv, says", [
    (["--stage", "--wave", "together", "--plan"], "takes no --wave"),
    (["--stage", "--member", "leo", "--plan"], "takes no --wave, --member or --phase"),
    (["--open", "--plan"], "--open opens the stage, so it needs --stage"),
])
def test_the_stage_takes_the_whole_core_and_open_needs_it(argv, says, capsys):
    assert family_demo.main(argv) == 2
    assert says in capsys.readouterr().err


def test_stage_plan_mode_says_what_it_will_and_will_not_ask(capsys):
    assert family_demo.main(["--stage", "--plan"]) == 0
    out = capsys.readouterr().out
    assert "stage on port 18405: 'Demo night', 5 cues; each member's own check is not run" in out
    assert "feat/family-dispatch" in out and "feat/family-control" in out


def test_the_stage_job_hands_the_runtime_the_links_and_the_hub_its_table(tmp_path):
    document = plan()
    order = family_demo.running(document)
    job = family_demo.stage_job(document, order, tmp_path)
    assert job["hub_base"] == HUB_BASE
    assert job["resolved"] == resolved()
    assert job["panels"]["leo"]["src"] == resolved()["leo"]["page"]
    assert {r["member"]: r["link"] for r in job["rows"]}["joe"] == "app to app"
    json.dumps(job)  # the job is handed over as JSON


def test_a_plan_without_a_stage_block_cannot_run_the_stage(tmp_path, capsys):
    import yaml

    document = plan()
    del document["stage"]
    path = tmp_path / "family-demo.yaml"
    path.write_text(yaml.safe_dump(document), encoding="utf-8")
    assert family_demo.main(["--plan-file", str(path), "--stage", "--plan"]) == 2
    assert "--stage needs a stage block" in capsys.readouterr().err


def stage_manifest(tmp_path, shot_exists: bool = True, held: str = "pass") -> dict:
    shot = tmp_path / "shots" / "stage" / "01-cue-1.png"
    if shot_exists:
        shot.parent.mkdir(parents=True)
        shot.write_bytes(b"\x89PNG")
    record = {"result": "pass", "ready_seconds": 1.0, "own_check": "not asked in this wave",
              "checks": [{"check": "ports-held-by-this-run", "owner": "demo", "result": "pass"}]}
    check = {"result": held, "shots": [str(shot)], "cues": [{
        "number": 1, "name": "House open", "result": held, "shot": str(shot),
        "assertions": [{"what": "the hub delivered cue 1 to leo (leo)", "result": held,
                        "detail": "d", "by": "the hub's GET /family/", "member": "leo",
                        "kind": "delivery"}]}]}
    rows = fs.link_evidence(fs.links(stage()["show"], links(), RUNNING), check)
    return {
        "run": "r", "started_at": "t", "corpus": {"commit": "abc"},
        "contract": plan()["contract"],
        "members": {"leo": {"runs": True, "phase": "core", "ports": {"web": 18440},
                            "ref": "x", "commit": "f" * 40, "stacks_on": {},
                            "url": "http://127.0.0.1:18440/"}},
        "stage": {"members": {"leo": record}, "url": "http://127.0.0.1:18405/",
                  "show": stage()["show"], "links": rows,
                  "app_to_app": fs.APP_TO_APP, "not_asked": ["each member's own check"],
                  "check": check},
        "seams": {"named_in_source": []}, "unknowns": [], "unplaced": []}


def test_the_landing_page_shows_the_storyboard_and_what_each_link_was_seen_doing(tmp_path):
    page = family_demo.landing_page(stage_manifest(tmp_path), tmp_path)
    assert '<figure data-cue="1"><img alt="The stage after cue 1" src="shots/stage/01-cue-1.png">' in page
    assert "<th>On the stage</th>" in page
    assert "<strong>App to app.</strong>" in page and "App to app: none" not in page
    assert "the hub delivered cue 1 to leo (leo)" in page
    assert "leo</strong> app to app:" in page and "1 of 1 deliveries 2xx" in page
    assert "carlos</strong> not seen:" in page and "not seen in this run" in page


def test_a_stage_picture_that_is_missing_is_reported(tmp_path):
    manifest = stage_manifest(tmp_path)
    (tmp_path / "index.html").write_text("x", encoding="utf-8")
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")
    assert family_demo.missing_artifacts(manifest, tmp_path) == []
    shot = tmp_path / "shots" / "stage" / "01-cue-1.png"
    shot.unlink()
    assert family_demo.missing_artifacts(manifest, tmp_path) == [str(shot)]


def test_an_assertion_the_stage_could_not_make_stays_unknown(tmp_path):
    manifest = stage_manifest(tmp_path, held="unknown")
    found = family_demo.collect_unknowns(manifest)
    assert "the stage, cue 1: the hub delivered cue 1 to leo (leo) -- d" in found
    assert any(u.startswith("the stage: the show") for u in found)


def test_combining_nothing_or_an_unknown_is_unknown_never_pass():
    assert fs.combine([]) == "unknown"
    assert fs.combine(["pass", "unknown"]) == "unknown"
    assert fs.combine(["unknown", "fail"]) == "fail"
    assert fs.combine(["pass", "pass"]) == "pass"


# --- one member restarted while the family is held -------------------------------

def test_a_restart_is_refused_when_nothing_holds_the_family(tmp_path):
    """Mutation: the holding check dropped, so a press waited on a harness that had gone -- red here."""
    answer = fs.request_restart(tmp_path, "leo", timeout=1)
    assert answer["result"] == "refused" and fs.restart_status(answer) == 409
    assert list(tmp_path.iterdir()) == []


def test_a_restart_request_is_taken_once_and_answered_to_the_one_who_asked(tmp_path):
    """Mutation: take_restart_requests leaving the request in place, so one press restarted
    the member on every tick of the hold -- red here."""
    (tmp_path / fs.HOLDING).write_text("t", encoding="utf-8")
    second_look: list = []

    def harness():
        for _ in range(400):
            taken = fs.take_restart_requests(tmp_path)
            if taken:
                second_look.append(fs.take_restart_requests(tmp_path))
                fs.answer_restart(tmp_path, taken[0]["nonce"],
                                  {"member": taken[0]["member"], "result": "pass", "seconds": 2.0})
                return
            threading.Event().wait(0.025)

    thread = threading.Thread(target=harness)
    thread.start()
    answer = fs.request_restart(tmp_path, "carlos", timeout=10)
    thread.join()
    assert answer == {"member": "carlos", "result": "pass", "seconds": 2.0}
    assert fs.restart_status(answer) == 200 and second_look == [[]]
    assert sorted(p.name for p in tmp_path.iterdir()) == [fs.HOLDING]


def test_a_restart_nobody_answers_times_out_and_withdraws_its_request(tmp_path):
    (tmp_path / fs.HOLDING).write_text("t", encoding="utf-8")
    answer = fs.request_restart(tmp_path, "joe", timeout=0.3)
    assert answer["result"] == "timeout" and fs.restart_status(answer) == 504
    assert list(tmp_path.glob("*.request")) == []
    assert fs.restart_status({"result": "fail"}) == fs.restart_status({"result": "unknown"}) == 502


def test_the_stage_asks_the_harness_only_for_a_member_it_runs(tmp_path):
    """Mutation: the stage's membership check dropped, so a press for wolf waited on a harness
    that holds no wolf -- red here."""
    control = tmp_path / "control"
    job = {"hub": "http://127.0.0.1:9/", "dir": str(tmp_path / "stage"), "port": 18405,
           "order": RUNNING, "control": str(control), "restart_seconds": 0.3}
    running = family_stage_run.Stage(job)
    status, answer = family_stage_run.restart(running, "wolf")
    assert status == 404 and answer["result"] == "refused"
    assert family_stage_run.restart(running, "leo")[0] == 409  # nothing holds the family
    (control / fs.HOLDING).write_text("t", encoding="utf-8")
    assert family_stage_run.restart(running, "leo")[0] == 504  # nothing answered
    without = family_stage_run.Stage({**job, "control": None})
    assert family_stage_run.restart(without, "leo")[0] == 409


def test_the_stage_state_carries_what_the_harness_did_for_the_page_to_follow(tmp_path):
    control = tmp_path / "control"
    job = {"hub": "http://127.0.0.1:9/", "dir": str(tmp_path / "stage"), "port": 18405,
           "order": RUNNING, "control": str(control)}
    running = family_stage_run.Stage(job)
    assert running.snapshot()["dev"] == {}
    fs.note_event(control, "carlos", "refresh", {"result": "pass", "summary": "a.html changed"})
    fs.note_event(control, "carlos", "restart", {"result": "pass", "summary": "restarted"})
    said = running.snapshot()["dev"]["carlos"]
    assert (said["restarts"], said["refreshes"], said["last"]["kind"]) == (1, 1, "restart")


def test_every_panel_can_restart_its_member_and_a_frame_can_be_reloaded():
    show = stage()["show"]
    page = fs.stage_page({"show": show, "hub_url": "http://127.0.0.1:18400/", "order": RUNNING,
                          "links": links(),
                          "panels": fs.panel_view(stage()["panels"], MEMBERS, resolved()),
                          "rows": fs.links(show, links(), RUNNING)})
    for member in RUNNING:
        assert f'data-restart="{member}"' in page and f'id="op-{member}"' in page
    assert 'data-refresh="leo"' in page and 'data-refresh="joe"' not in page  # joe is a session
    assert "follow(state.dev)" in page and "post('restart/'" in page
