"""The family stage's rules, checked without starting anything.

Hermetic: no port is bound, no member runs, no browser is launched. What is
tested is the part that decides -- which verbs a cue may ask of which member,
how a cue's notes become a relay plan, what the stage asks the hub to create,
which links it may claim, and what the page and the run's landing page say.
Running the show is the demo's own check (`uv run qm family-demo --stage`).

Each guard was broken once and seen to go red; the mutation is named in the
test that caught it.
"""

from __future__ import annotations

import copy
import io
import json
import sys
import wave
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


def plan() -> dict:
    return family_demo.load_plan()


def stage() -> dict:
    return copy.deepcopy(plan()["stage"])


def plan_problems(document: dict) -> list[str]:
    return family_demo.check_plan(document, {e["name"] for e in roster.load()})


# --- the family block -------------------------------------------------------

def test_a_cue_without_a_family_block_asks_nothing_and_is_not_a_problem():
    assert fs.parse_family(None, RUNNING) == ([], [])
    assert fs.parse_family("", RUNNING) == ([], [])
    assert fs.parse_family('{"osc": {"address": "/go"}}', RUNNING) == ([], [])


def test_a_family_block_becomes_actions_in_relay_order_whatever_its_order():
    notes = json.dumps({"family": {"joe": {"do": "take", "notes": ["C4", "E4"]},
                                   "leo": {"do": "show", "song": "Blue Bossa",
                                           "playlist": "Jazz 1460"},
                                   "ShowStopper": {"do": "start"}}})
    actions, problems = fs.parse_family(notes, RUNNING)
    assert problems == []
    assert [(a.member, a.verb) for a in actions] == [("ShowStopper", "start"), ("leo", "show"),
                                                     ("joe", "take")]
    assert actions[2].get("notes") == ("C4", "E4")


@pytest.mark.parametrize("family, says", [
    ({"ShowRunner": {"do": "go"}}, "ShowRunner is the hub"),
    ({"wolf": {"do": "play"}}, "wolf is not a running member"),
    ({"leo": {"do": "scroll"}}, "leo: no verb 'scroll'; it has ['show']"),
    ({"leo": "show"}, "leo: expected an object with a 'do'"),
    ({"leo": {"do": "show", "song": "Blue Bossa"}}, "leo show: needs 'playlist'"),
    ({"carlos": {"do": "turn", "speed": 2}}, "carlos turn: takes no 'speed'"),
    ({"carlos": {"do": "patch", "device": "moog.dfam", "example": "huge"}},
     "example must be one of ['simple', 'complex']"),
    ({"joe": {"do": "take", "notes": ["C4", "H9"]}}, "'H9' is not a note name"),
    ({"joe": {"do": "take", "notes": []}}, "notes must be a list of 1 to"),
    ({}, "family must be an object naming at least one member"),
])
def test_a_malformed_family_block_is_refused_with_its_reason(family, says):
    """Mutation: the hub refusal deleted, so the hub was planned as a step -- red."""
    actions, problems = fs.parse_family({"family": family}, RUNNING)
    assert actions == []
    assert any(says in p for p in problems), problems


def test_one_bad_member_means_the_cue_relays_nothing():
    """A typo must not half-run a cue.

    Mutation: returning the good actions alongside the problems -- red here.
    """
    actions, problems = fs.parse_family({"family": {
        "leo": {"do": "show", "song": "Blue Bossa", "playlist": "Jazz 1460"},
        "carlos": {"do": "spin"}}}, RUNNING)
    assert actions == [] and problems


def test_notes_that_are_not_json_are_a_problem_not_an_empty_cue():
    actions, problems = fs.parse_family("{family: leo}", RUNNING)
    assert actions == [] and problems[0].startswith("notes are not JSON")


def test_a_member_not_running_cannot_be_asked_even_with_a_valid_verb():
    actions, problems = fs.parse_family({"family": {"joe": {"do": "take", "notes": ["C4"]}}},
                                        ["ShowRunner", "leo"])
    assert actions == [] and problems == ["joe is not a running member of this demo"]


@pytest.mark.parametrize("name, number", [("C4", 60), ("A4", 69), ("F#3", 54), ("Bb2", 46),
                                          ("C-1", 0), ("G9", 127)])
def test_note_names_are_midi_numbers(name, number):
    assert fs.note_number(name) == number


@pytest.mark.parametrize("name", ["c4", "H2", "C", "G#9", "", None, "C10"])
def test_a_note_that_is_not_one_is_refused(name):
    with pytest.raises(ValueError):
        fs.note_number(name)


# --- the relay plan ----------------------------------------------------------

def test_leo_s_link_is_its_own_route_and_new_for_every_cue():
    """leo reads its route on a fresh load only, so two cues need two documents.

    Mutation: the cue left out of the query -- red here.
    """
    one = fs.deep_link("http://127.0.0.1:18440/", "Take The A Train", "Jazz 1460", 1)
    two = fs.deep_link("http://127.0.0.1:18440/#!/song/x?playlist=y", "Take The A Train",
                       "Jazz 1460", 5)
    assert one == ("http://127.0.0.1:18440/?cue=1"
                   "#!/song/Take%20The%20A%20Train?playlist=Jazz%201460")
    assert two.startswith("http://127.0.0.1:18440/?cue=5#!/song/") and one != two


def test_the_plan_names_each_member_s_own_interface_and_calls_every_step_relayed():
    actions, _ = fs.parse_family({"family": {
        "joe": {"do": "take", "notes": ["C4", "G4"]},
        "leo": {"do": "show", "song": "Blue Bossa", "playlist": "Jazz 1460"},
        "carlos": {"do": "turn"}}}, RUNNING)
    steps = fs.relay_plan(actions, MEMBERS, 3)
    assert [s["member"] for s in steps] == ["leo", "carlos", "joe"]
    assert {s["link"] for s in steps} == {"relayed"}
    joe = steps[2]
    # The API's own port, not the page's: the page proxies /api, the stage does not need it.
    assert joe["upload"] == "http://127.0.0.1:18431/api/audio/upload"
    assert joe["midi"] == [60, 67] and joe["params"] == {"notes": ["C4", "G4"]}
    assert steps[0]["url"].startswith("http://127.0.0.1:18440/?cue=3#!/song/Blue%20Bossa")
    assert steps[1]["interface"] == fs.VIA["page"]
    json.dumps(steps)  # the plan is recorded as JSON


# --- the show, the panels and the links --------------------------------------

def test_the_committed_show_and_panels_can_run_as_written():
    assert fs.check_show(stage()["show"], RUNNING) == []
    assert fs.check_panels(stage()["panels"], RUNNING) == []
    assert plan_problems(plan()) == []


def test_every_core_member_is_asked_for_something_by_the_committed_show():
    rows = {r["member"]: r["link"] for r in fs.links(stage()["show"], RUNNING)}
    assert rows == {"ShowRunner": "real", "ShowStopper": "relayed", "leo": "relayed",
                    "carlos": "relayed", "joe": "relayed"}


def test_a_link_is_claimed_no_wider_than_it_is():
    """Mutation: every member reported `relayed` regardless of the cues -- red here."""
    show = {"cues": [{"family": {"leo": {"do": "show", "song": "A", "playlist": "B"}}}]}
    rows = {r["member"]: r["link"] for r in fs.links(show, RUNNING + ["wolf"])}
    assert rows["leo"] == "relayed"
    assert rows["joe"] == "not on any cue"
    assert rows["wolf"] == "not drivable"
    assert rows["ShowRunner"] == "real"
    assert fs.APP_TO_APP.startswith("No member calls another")


@pytest.mark.parametrize("change, says", [
    (lambda s: s["cues"][1].update(number=1), "number is used twice"),
    (lambda s: s["cues"].reverse(), "must be listed in cue order"),
    (lambda s: s["cues"][0].update(layer="Smoke"), "layer must be one of"),
    (lambda s: s["cues"][0].pop("family"), "has no family block"),
    (lambda s: s["cues"][0]["family"].update(leo={"do": "show"}), "leo show: needs 'song'"),
    (lambda s: s["cues"][0].update(number=0), "number must be a positive whole number"),
    (lambda s: s.update(cues=[]), "must list at least one cue"),
    (lambda s: s.update(name=" "), "stage.show.name must be non-empty text"),
])
def test_a_show_that_cannot_be_seeded_as_written_is_refused(change, says):
    show = stage()["show"]
    change(show)
    assert any(says in p for p in fs.check_show(show, RUNNING)), fs.check_show(show, RUNNING)


@pytest.mark.parametrize("change, says", [
    (lambda p: p.pop("joe"), "joe has no panel"),
    (lambda p: p["leo"].update(role="two\nlines"), "role must be one line"),
    (lambda p: p["leo"].update(shows="poster"), "shows must be one of"),
    (lambda p: p["ShowRunner"].update(shows="session"), "the hub's state is on its server"),
    (lambda p: p.update(wolf={"role": "x", "shows": "frame", "note": "y"}),
     "wolf is not a running member"),
])
def test_a_panel_that_cannot_be_shown_is_refused(change, says):
    panels = stage()["panels"]
    change(panels)
    assert any(says in p for p in fs.check_panels(panels, RUNNING)), fs.check_panels(panels, RUNNING)


def test_the_stage_port_is_held_to_a_member_s_rules():
    """Mutation: the collision test removed from check_stage -- the second case went green."""
    document = plan()
    document["stage"]["port"] = document["ports"]["last"] + 1
    assert any(p.startswith("stage: port") and "outside" in p for p in plan_problems(document))
    document["stage"]["port"] = 18440
    assert "stage: port 18440 is already leo's" in plan_problems(document)


def test_a_stage_without_its_hub_is_refused():
    assert any("the hub, is not a running member" in p
               for p in fs.check_stage(stage(), ["leo", "joe"], {}, (18400, 18499)))


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
    assert [c["number"] for c in seeded["cues"]] == [c["number"] for c in show["cues"]]


def test_a_framed_panel_with_a_path_opens_there_and_one_without_starts_empty():
    view = fs.panel_view(stage()["panels"], MEMBERS)
    assert view["ShowRunner"]["src"] == "http://127.0.0.1:18400/programmer"
    assert "src" not in view["leo"] and view["leo"]["url"] == "http://127.0.0.1:18440/"
    assert view["carlos"]["url"] == "http://127.0.0.1:18420/rack"


def test_the_stage_page_has_go_a_panel_per_member_and_says_what_is_relayed():
    show = stage()["show"]
    page = fs.stage_page({"show": show, "hub_url": "http://127.0.0.1:18400/",
                          "order": RUNNING, "panels": fs.panel_view(stage()["panels"], MEMBERS),
                          "links": fs.links(show, RUNNING)})
    assert '<button id="go"' in page
    for member in RUNNING:
        assert f'data-panel="{member}"' in page
    assert 'id="frame-ShowRunner" title="ShowRunner, live" src="http://127.0.0.1:18400/programmer"' in page
    assert 'id="frame-leo" title="leo, live">' in page  # no src until a cue names leo
    assert 'id="shot-joe"' in page and 'id="frame-joe"' not in page
    assert "App to app: none." in page
    assert page.count('<li data-cue="') == len(show["cues"])
    assert "leo shows Autumn Leaves" in page


# --- the runtime's pieces that need no browser ------------------------------

def test_a_take_is_a_wav_of_half_a_second_per_note():
    data = family_stage_run.take([60, 64, 67])
    with wave.open(io.BytesIO(data)) as take:
        assert (take.getnchannels(), take.getsampwidth(), take.getframerate()) == (1, 2, 22050)
        assert take.getnframes() == 3 * 11025


def test_only_the_runtime_names_a_member_s_surface():
    """The member owns its selectors; the stage's runtime is the one exception, and it alone.

    Mutation: LEO_TITLE's selector pasted into family_demo.py -- red here.
    """
    surfaces = [family_stage_run.LEO_TITLE, family_stage_run.JOE_FETCH, family_stage_run.JOE_META,
                family_stage_run.JOE_RESULTS_TOGGLE, "loadExample", "view-indicator"]
    for source in ("family_demo.py", "family_demo_probes.py", "family_stage.py"):
        text = (CI_DIR / source).read_text(encoding="utf-8")
        for surface in surfaces:
            assert surface not in text, f"{source} names {surface!r}"


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
    assert "demo/family-stage" in out


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
    return {
        "run": "r", "started_at": "t", "corpus": {"commit": "abc"},
        "contract": plan()["contract"],
        "members": {"leo": {"runs": True, "phase": "core", "ports": {"web": 18440},
                            "ref": "x", "commit": "f" * 40, "stacks_on": {},
                            "url": "http://127.0.0.1:18440/"}},
        "stage": {"members": {"leo": record}, "url": "http://127.0.0.1:18405/",
                  "show": stage()["show"], "links": fs.links(stage()["show"], RUNNING),
                  "app_to_app": fs.APP_TO_APP, "not_asked": ["each member's own check"],
                  "check": {"result": held, "shots": [str(shot)], "cues": [{
                      "number": 1, "name": "House open", "result": held, "shot": str(shot),
                      "assertions": [{"what": "the hub's CueLog gained an entry for this cue",
                                      "result": held, "detail": "d", "by": "the hub"}]}]}},
        "seams": {"named_in_source": []}, "unknowns": [], "unplaced": []}


def test_the_landing_page_shows_the_storyboard_in_cue_order(tmp_path):
    page = family_demo.landing_page(stage_manifest(tmp_path), tmp_path)
    assert '<figure data-cue="1"><img alt="The stage after cue 1" src="shots/stage/01-cue-1.png">' in page
    assert "<th>On the stage</th>" in page
    assert "App to app: none." in page
    assert "the hub&#x27;s CueLog gained an entry for this cue" in page


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
    assert ("the stage, cue 1: the hub's CueLog gained an entry for this cue -- d" in found)
    assert any(u.startswith("the stage: the show") for u in found)


# --- edges the mutation sweep found unguarded ----------------------------------
# `uv run qm mutate ci/family_stage.py --tests ci/tests/test_family_stage.py`
# left each of these alive before the tests below. The survivors that remain
# change nothing a caller can see: "and", "or" and "not" inside message and
# comment text, `frozen=True`, `sort_keys=True`, and the joiner for a member
# reached through two interfaces, which no verb does.

def test_notes_that_are_json_but_not_an_object_are_a_problem():
    assert fs.parse_family("[1, 2]", RUNNING) == ([], ["notes must be a JSON object"])


@pytest.mark.parametrize("song", [" ", 5, None])
def test_text_parameters_must_be_text_with_something_in_it(song):
    actions, problems = fs.parse_family(
        {"family": {"leo": {"do": "show", "song": song, "playlist": "Jazz 1460"}}}, RUNNING)
    assert actions == [] and problems == ["leo show: song must be non-empty text"]


def test_a_take_has_at_most_sixteen_notes():
    def asked(count):
        return fs.parse_family({"family": {"joe": {"do": "take", "notes": ["C4"] * count}}},
                               RUNNING)
    assert asked(1)[1] == [] and asked(fs.MAX_NOTES)[1] == []
    assert asked(fs.MAX_NOTES + 1)[1] == ["joe take: notes must be a list of 1 to 16 note names"]


@pytest.mark.parametrize("number", ["1", True, 1.0])
def test_a_cue_number_is_a_whole_number_and_nothing_that_looks_like_one(number):
    show = stage()["show"]
    show["cues"][0]["number"] = number
    assert "cue " + str(number) + ": number must be a positive whole number" in \
        fs.check_show(show, RUNNING)


@pytest.mark.parametrize("key, says", [("name", "needs a name")])
def test_a_cue_without_a_name_is_refused(key, says):
    show = stage()["show"]
    del show["cues"][0][key]
    assert any(says in p for p in fs.check_show(show, RUNNING))


@pytest.mark.parametrize("key, says", [("role", "role must be one line"),
                                       ("note", "needs a note saying what the panel is")])
def test_a_panel_without_its_words_is_refused(key, says):
    panels = stage()["panels"]
    del panels["leo"][key]
    assert f"stage.panels.leo: {says}" in fs.check_panels(panels, RUNNING)


@pytest.mark.parametrize("port, ok", [(18400, True), (18499, True), (18400 - 1, False),
                                      (18499 + 1, False), (True, False),
                                      ("18405", False)])
def test_the_stage_port_is_a_whole_number_inside_the_range(port, ok):
    document = stage()
    document["port"] = port
    found = fs.check_stage(document, RUNNING, {}, (18400, 18499))
    assert (found == []) == ok, found


def test_combining_nothing_or_an_unknown_is_unknown_never_pass():
    assert fs.combine([]) == "unknown"
    assert fs.combine(["pass", "unknown"]) == "unknown"
    assert fs.combine(["unknown", "fail"]) == "fail"
    assert fs.combine(["pass", "pass"]) == "pass"


def test_each_chip_says_what_its_member_is_asked():
    actions, _ = fs.parse_family({"family": {
        "ShowStopper": {"do": "start"}, "carlos": {"do": "turn"},
        "joe": {"do": "take", "notes": ["C4", "E4"]}}}, RUNNING)
    assert [fs.summary(a) for a in actions] == ["starts the clock", "turns the rack",
                                                "processes a take of C4 E4"]
    stop, _ = fs.parse_family({"family": {"ShowStopper": {"do": "stop"}}}, RUNNING)
    assert fs.summary(stop[0]) == "stops the clock"


def test_only_a_frame_with_nothing_to_show_says_it_is_empty():
    show = stage()["show"]
    page = fs.stage_page({"show": show, "hub_url": "http://127.0.0.1:18400/",
                          "order": RUNNING, "panels": fs.panel_view(stage()["panels"], MEMBERS),
                          "links": fs.links(show, RUNNING)})
    assert 'id="empty-leo">Empty until a cue names leo.' in page
    assert 'id="empty-ShowRunner"' not in page
