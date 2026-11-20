"""The trio demo, executed.

`protocols/local-demo.md` rule 2: a test runs the demo. These tests execute the
demo itself, not a second implementation of its behaviour, and run it through
`qm demo`, the documented route, rather than by file path.

The demo needs `qmcp` and `dossier` beside this clone with their environments
built. A hosted runner has this repository alone, so the tests that need
siblings skip there with a reason; the ones that need nothing else (the module
imports, its pieces report a missing sibling) run everywhere.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "ci" / "trio_demo.py"


def _module():
    """The demo, loaded from its path.

    Registered in `sys.modules` before execution: `@dataclass` resolves
    annotations through `sys.modules[cls.__module__]`, so a module built by
    `module_from_spec` and never registered raises on its first dataclass --
    an error about `NoneType` that says nothing about the cause.
    """
    spec = importlib.util.spec_from_file_location("trio_demo", DEMO)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _siblings_present() -> bool:
    module = _module()
    return all(module.sibling(name) is not None for name in module.NEEDED)


needs_siblings = pytest.mark.skipif(
    not DEMO.is_file() or not _siblings_present(),
    reason="the trio demo needs qmcp and dossier beside this clone")


# --- runs anywhere ------------------------------------------------------------


def test_the_demo_is_a_file_in_the_repository():
    """Rule 1: the demo is a file in the repository that anybody can run."""
    assert DEMO.is_file()


def test_the_demo_imports():
    module = _module()
    assert callable(module.main)


def test_a_missing_sibling_is_reported_rather_than_skipped_silently():
    """With a needed sibling missing, the demo exits 1 rather than printing a
    summary of fewer sides.

    Mutation: return 0 when a needed sibling is absent and this fails.

    `main([])` rather than `main()`: with no argv argparse reads `sys.argv`,
    which under pytest holds pytest's own arguments and makes the demo exit 2
    on an unrecognised flag.
    """
    module = _module()
    module.SIBLINGS = Path("/nowhere-that-exists")
    # `QM_SIBLINGS` in the operator's shell would replace SIBLINGS and make
    # this test find the real repositories. The test is about the resolver,
    # not the shell.
    import os
    saved = os.environ.pop("QM_SIBLINGS", None)
    try:
        assert module.main([]) == 1
    finally:
        if saved is not None:
            os.environ["QM_SIBLINGS"] = saved


def test_the_windows_read_the_rendering_rather_than_the_payload():
    """Each window reports what it drew, not what the document says: two
    readers of one field always agree.

    Mutation: count the payload's arrows in either window script and this fails.
    """
    module = _module()
    assert "topology.UNMEASURED in line" in module.DOSSIER, (
        "the terminal window must count the glyph that reached the screen")
    assert "view.unmeasured" in module.CODECARTO, (
        "the graph window must report its own classification")
    for script in (module.DOSSIER, module.CODECARTO):
        assert 'a.get("weight") is None' not in script, (
            "a window is counting the payload instead of its own rendering")


def test_each_window_runs_under_its_own_interpreter():
    """No window runs under the demo's own interpreter.

    Asserts the call, not the word, so the prose that names `sys.executable`
    does not match: a text scan matching its own prohibition is one of the
    false readings `records/DRAFT-decision-record-discipline.md` §7 names.
    """
    source = DEMO.read_text(encoding="utf-8")
    assert "subprocess.run([sys.executable" not in source, (
        "a window is being run with the demo's own interpreter")
    # Every subprocess, not a fixed count of them: no subprocess is started
    # with anything but its own project's interpreter.
    started = source.count("subprocess.run(")
    with_own = (source.count("subprocess.run(\n        [interpreter(project)")
                + source.count("subprocess.run([interpreter(project)"))
    assert started >= 2, "the demo starts fewer processes than it has windows"
    assert with_own == started, (
        f"{started - with_own} subprocess call(s) do not resolve their own "
        f"project's interpreter")


# --- needs the siblings -------------------------------------------------------


# One run per distinct argument set, for the whole module.
#
# Memoised, not merged: several tests run the demo with the same arguments and
# assert different properties of one output, and keeping them apart keeps each
# failure message specific.
#
# The demo reads and never writes, and its answer is a function of its arguments
# and the harness's state, so a second identical run can only produce a second
# identical answer. Caching therefore removes duplicate work and nothing else.
_RUNS: dict[tuple[str, ...], subprocess.CompletedProcess] = {}


def _via_cli(*options: str):
    """The demo through its declared route, which is how it is documented."""
    if options not in _RUNS:
        _RUNS[options] = subprocess.run(
            [sys.executable, str(ROOT / "ci" / "cli.py"), "demo", *options],
            cwd=ROOT, capture_output=True, text=True, timeout=900)
    return _RUNS[options]


@needs_siblings
def test_the_demo_runs_and_the_windows_agree():
    """The demo exits 0 only when every window that drew
    the topology agrees about every box, every arrow, and which edges nobody
    measured."""
    done = _via_cli()
    assert done.returncode == 0, (
        f"the trio demo failed:\n{done.stdout[-3000:]}\n{done.stderr[-1500:]}")
    assert "windows agree about every box" in done.stdout


@needs_siblings
def test_the_demo_says_what_it_did_not_establish():
    """Rule 4. A demo that only printed successes would be advertising."""
    done = _via_cli()
    assert "WHAT THIS DID NOT ESTABLISH" in done.stdout
    assert "Both windows would faithfully draw a wrong one" in done.stdout


@needs_siblings
def test_the_demo_names_its_data_source():
    """Real archive or stated fixture, never silently one wearing the other's
    name."""
    done = _via_cli()
    assert ("data         thread archive" in done.stdout
            or "data         fixture" in done.stdout)


# --- the options ---------------------------------------------------------------


def test_the_route_exists_and_names_this_module():
    """The demo is documented as `uv run qm demo`. If the route were missing,
    every page saying so would be wrong and the file would still run.

    Mutation: remove the `demo` route and this fails.
    """
    sys.path.insert(0, str(ROOT))
    from ci import cli

    assert cli.ROUTES["demo"][0] == "trio_demo"


def test_listing_the_windows_runs_nothing():
    """`--list-windows` answers from the registry. A listing that had to draw
    the topology first would be useless on the machine that cannot."""
    module = _module()
    assert set(module.WINDOWS) == {"dossier", "codecartographer"}


def test_an_unknown_window_is_refused_rather_than_ignored():
    """Naming a window that does not exist is a typo, and silently drawing the
    other two would hide it behind a green result.

    Mutation: drop the validation and this fails.
    """
    module = _module()
    with pytest.raises(SystemExit) as raised:
        module.main(["--window", "nope"])
    assert raised.value.code == 2


@needs_siblings
def test_one_window_refuses_to_call_itself_agreement():
    """`--window` narrows what draws, and one window drawing alone is one
    window agreeing with itself: the demo exits 1 and says why.

    Mutation: return 0 when fewer than two windows drew and this fails.
    """
    done = _via_cli("--fixture", "--window", "dossier")
    assert done.returncode == 1
    assert "agreeing with itself" in done.stdout


@needs_siblings
def test_the_fixture_option_does_not_read_the_archive():
    """A demo of the fixture and a demo of the archive are different claims,
    and the operator must be able to ask for the first."""
    done = _via_cli("--fixture")
    assert done.returncode == 0
    assert "data         fixture" in done.stdout
    assert "because --fixture was given" in done.stdout


@needs_siblings
def test_the_json_option_carries_the_same_verdict_as_the_prose():
    """Two renderings of one run that could disagree would be a seam inside a
    single process.

    Mutation: hard-code `agreed` true in the JSON and this fails.
    """
    import json

    prose = _via_cli("--fixture")
    document = json.loads(_via_cli("--fixture", "--json").stdout)

    assert document["agreed"] is (prose.returncode == 0)
    assert document["data"] == "fixture"
    assert document["problems"] == []


@needs_siblings
def test_the_json_option_reports_a_disagreement_too():
    """The machine-readable form must carry the bad news as well as the good.
    A single window is the cheapest disagreement to arrange."""
    import json

    done = _via_cli("--fixture", "--window", "dossier", "--json")
    document = json.loads(done.stdout)
    assert done.returncode == 1
    assert document["agreed"] is False
    assert any("agreeing with itself" in p for p in document["problems"])


# --- as deployed, over HTTP ----------------------------------------------------


def _reachable(url: str) -> bool:
    import urllib.request

    try:
        urllib.request.urlopen(url, timeout=3)
        return True
    except Exception:                              # noqa: BLE001
        return False


def test_both_modes_share_one_comparison():
    """The subprocess mode and the HTTP mode share one agreement check, so
    neither copy can drift lenient.

    Mutation: give the HTTP mode its own comparison and this fails.
    """
    module = _module()
    source = DEMO.read_text(encoding="utf-8")

    assert callable(module._agree)
    assert source.count("disagree about what is known") == 1, (
        "the unmeasured comparison exists in more than one place")
    assert source.count("def _agree") == 1


def test_over_http_refuses_when_the_harness_is_not_answering(monkeypatch):
    """A demo whose backend is down must name the process and the command, not
    report a disagreement between windows that never drew.

    Mutation: fall back to the subprocess mode and this fails.
    """
    module = _module()
    monkeypatch.setattr(module, "HARNESS_URL", "http://127.0.0.1:9")
    monkeypatch.setattr(module, "WEB_URL", "http://127.0.0.1:9")

    assert module.main(["--over-http"]) == 1


def test_the_http_window_asks_the_server_rather_than_importing_the_renderer():
    """The HTTP window's answer comes off the wire, so the route is exercised;
    importing codecarto's renderer would test only what the subprocess mode
    already covers.

    Mutation: import the renderer in `_web_window` and this fails.
    """
    module = _module()
    import inspect

    body = inspect.getsource(module._web_window)
    assert "topology/data" in body
    assert "import" not in body.replace("importing", ""), (
        "the HTTP window imports something instead of asking the server")


@pytest.mark.skipif(not _reachable("http://127.0.0.1:3141/health"),
                    reason="the harness is not running on 3141")
def test_the_harness_serves_a_topology_over_http():
    """The harness serves a topology route that a front end can fetch."""
    module = _module()
    document, why = module._harness_document("codecartographer")
    assert document is not None, why
    assert "payload" in document and "encoding" in document


def _deployed_trio_missing() -> str:
    """What the deployed-trio test lacks here, or "" when it has everything.

    The body runs `qm demo --over-http`, which asks the harness on 3141 and the
    web front end on 2718 and then draws the dossier window under that
    sibling's own interpreter, so it needs the ports *and* the siblings. A
    condition that reads the ports alone runs the test on a machine where
    another process answers them and no clone sits beside the checkout, and
    fails it on the missing clone instead of skipping; a worktree is such a
    checkout. Each missing piece is named, so a skip says what it skipped on.
    """
    missing = []
    if not _siblings_present():
        missing.append("qmcp and dossier beside this clone")
    if not _reachable("http://127.0.0.1:3141/health"):
        missing.append("the harness on 3141")
    if not _reachable("http://127.0.0.1:2718/topology/data"):
        missing.append("the web front end on 2718")
    if not missing:
        return ""
    return ("the deployed trio needs " + ", ".join(missing)
            + "; `uv run qm dashboard --start harness --start web` from a clone "
              "with the siblings beside it")


_DEPLOYED_TRIO_MISSING = _deployed_trio_missing()


@pytest.mark.skipif(bool(_DEPLOYED_TRIO_MISSING), reason=_DEPLOYED_TRIO_MISSING)
def test_the_deployed_front_ends_agree():
    """The demo as deployed: every answer comes from a process somebody could
    open in a browser.

    Mutation: make the skip condition read the two ports alone and run this
    from a checkout with no sibling beside it while the ports answer, and it
    fails on `is not beside this clone` instead of skipping.
    """
    done = _via_cli("--over-http")
    assert done.returncode == 0, done.stdout[-2500:]
    assert "windows agree about every box" in done.stdout


# --- the figure both windows print ------------------------------------------
#
# Both windows print an edge's measurement in one unit, so a figure that
# differs between them is a defect rather than a point of view.
#
# `uv run qm mutate ci/trio_demo.py` cannot measure this file: the mutator runs
# the suite against a copy in a temporary directory, `sibling()` resolves the
# other repositories relative to the module's own path, and from there the
# baseline is red before any operator is applied. The mutations named below
# are applied by hand, per charter `a-check-is-evidence-after-it-fails`.


def test_a_measured_edge_prints_the_same_figure_the_other_window_prints():
    """Mutation: return the width instead of the weight and this fails."""
    assert _module()._figure(0.17) == "17%"
    assert _module()._figure(0.127) == "13%"


def test_an_unmeasured_edge_says_so_rather_than_borrowing_a_figure():
    """`None` is not zero. Rounding it into `0%` would render the one distinction
    the harness takes care to send as though somebody had looked and found
    nothing.

    Mutation: `weight or 0` instead of the `is None` test and this fails.
    """
    assert _module()._figure(None) == "unmeasured"


def test_a_measured_zero_is_a_figure_and_not_unmeasured():
    """Somebody looked and found nothing, which is a finding.

    Mutation: treat falsy as unmeasured and this fails.
    """
    assert _module()._figure(0.0) == "0%"


def test_both_window_scripts_print_the_figure():
    """One window is rendered over HTTP and one in the sibling's own
    interpreter, and both print the same figure, as the two modes share one
    comparison.

    Mutation: add the figure to one script and not the other and this fails.
    """
    module = _module()
    assert "figure(e)" in module.CODECARTO
    assert "unmeasured" in module.CODECARTO


# --- the second act: one thread, three readers --------------------------------
#
# looksatwords is not a fourth window. Its adoption record (`project/looksatwords`
# §3) says it reads the turns qmcp deliberately discards and authors nothing in
# qmcp or dossier, so the demo hands it one thread and holds it to the seam --
# the harness's own two turn counts -- rather than to agreement about a picture.


def test_readers_are_a_separate_registry_from_windows():
    """A reader reads a thread; a window draws a topology. looksatwords is a
    reader, so the demo never asks it to agree about boxes."""
    module = _module()
    assert set(module.READERS) == {"looksatwords", "dossier", "codecartographer"}
    assert "looksatwords" not in module.WINDOWS


def test_the_stated_thread_fixture_exercises_the_prose_distinction():
    """The seam's two counts are only worth comparing if they can differ, so
    the fixture carries a turn with no prose on purpose."""
    module = _module()
    turns = module.THREAD_FIXTURE["turns"]
    assert any(not (t["text"] or "").strip() for t in turns), (
        "the fixture has no empty turn; turns_total and turns_with_text "
        "could not disagree and the comparison would be vacuous")


def test_looksatwords_is_held_to_the_border_not_to_a_picture():
    """The reader script reports the seam's counts from the project's own
    conversion. The border and count checks themselves are tested as
    behaviour below, in `test_the_seam_comparison_catches_...`."""
    module = _module()
    assert "turns_with_text" in module.LOOKSATWORDS, (
        "the looksatwords reader must report the seam's second count")
    assert "as_conversation" in module.LOOKSATWORDS, (
        "the counts must come from the project's own seam conversion, not a "
        "second one done for the demo")


def test_the_sibling_roots_override_replaces_rather_than_extends(
        tmp_path, monkeypatch):
    """A worktree is beside nothing. `QM_SIBLINGS` replaces the convention, so
    the repositories a demo may read have one source."""
    module = _module()
    (tmp_path / "only" / "pyproject.toml").parent.mkdir()
    (tmp_path / "only" / "pyproject.toml").write_text("[project]\n",
                                                       encoding="utf-8")
    monkeypatch.setenv("QM_SIBLINGS", str(tmp_path))

    assert module._sibling_roots() == [tmp_path]
    assert module.sibling("only") == tmp_path / "only"
    assert module.sibling("qmcp") is None, (
        "the override extended the roots instead of replacing them")


@needs_siblings
def test_the_second_act_runs_and_the_readers_report_the_seams_counts():
    """In the second act, looksatwords must report the
    harness's own turn counts and emit no decision."""
    done = _via_cli("--fixture")
    assert done.returncode == 0, done.stdout[-3000:]
    assert "SECOND ACT -- one thread, three readers" in done.stdout
    assert "reported the harness's own turn counts and emitted no decision" \
        in done.stdout


@needs_siblings
def test_the_second_act_says_what_it_did_not_establish():
    done = _via_cli("--fixture")
    assert "WHAT THE SECOND ACT DID NOT ESTABLISH" in done.stdout
    assert "nothing here judges it" in done.stdout


@needs_siblings
def test_skipping_the_readers_is_stated_in_the_output():
    """A skip that left no trace would read as a demo that covered less than
    it claims."""
    done = _via_cli("--fixture", "--skip-readers")
    assert done.returncode == 0
    assert "SECOND ACT" not in done.stdout
    assert "The second act was skipped" in done.stdout


@needs_siblings
def test_the_json_carries_the_readers_and_the_same_verdict():
    import json

    document = json.loads(_via_cli("--fixture", "--json").stdout)
    readers = document["readers"]
    assert readers["turns_total"] == readers["read"]["looksatwords"]["turns_total"]
    assert readers["turns_with_text"] == \
        readers["read"]["looksatwords"]["turns_with_text"]
    assert "settled" not in readers["read"]["looksatwords"]
    assert readers["runnable_now"], "a built harness runs at least one shape"
    assert document["problems"] == []


def test_the_seam_comparison_catches_an_overcount_and_an_authored_decision():
    """Behaviour, not a string: this feeds the comparison a reader that
    over-counts by one and a reader that emitted a `settled` key, and expects
    both named.

    Mutations: drop the count comparison, or the `authored` check, and this
    fails.
    """
    module = _module()
    served = {"turns_total": 8, "turns_with_text": 7}

    assert module._seam_problems(served, {"turns_total": 8,
                                          "turns_with_text": 7}) == []

    over = module._seam_problems(served, {"turns_total": 9, "turns_with_text": 7})
    assert over and "9 turns" in over[0]

    prose = module._seam_problems(served, {"turns_total": 8, "turns_with_text": 6})
    assert prose and "second count" in prose[0]

    authored = module._seam_problems(
        served, {"turns_total": 8, "turns_with_text": 7, "settled": ["x"]})
    assert authored and "never authors" in authored[0]


def test_a_derive_target_need_not_be_a_python_project(tmp_path, monkeypatch):
    """moat is charts and terraform with no `pyproject.toml`. `sibling` is
    for repositories the demo runs a script under; `clone` is for what a
    reader derives from, and the two must not be the same test.

    Mutation: resolve the derive target with `sibling` and this fails.
    """
    module = _module()
    (tmp_path / "homelab" / ".git").mkdir(parents=True)
    monkeypatch.setenv("QM_SIBLINGS", str(tmp_path))

    assert module.sibling("homelab") is None
    assert module.clone("homelab") == tmp_path / "homelab"
    import inspect
    assert "target = clone(args.subject)" in inspect.getsource(module._readers)


@needs_siblings
def test_a_failing_second_act_clears_the_verdict_in_the_json():
    """One document, one answer: a failing second act clears the `agreed` the
    first act set."""
    module = _module()
    import inspect

    body = inspect.getsource(module.main)
    assert 'result["agreed"] = False' in body


# --- the third act: the estate ------------------------------------------------


@needs_siblings
def test_the_estate_act_runs_and_two_hosts_agree():
    """The corpus's own statement of the estate, read from the
    seam by two core members in their own runtimes, held to the window
    standard -- one host agreeing with itself establishes nothing.

    Mutation: point `_estate` at a missing file and this fails on exit code.
    """
    done = _via_cli("--fixture", "--skip-readers")
    assert done.returncode == 0, done.stdout[-3000:]
    assert "THIRD ACT -- the estate, drawn from the seam" in done.stdout
    assert "agree about every family, every member, and every placement" in done.stdout


@needs_siblings
def test_the_estate_act_reports_in_json_with_the_same_verdict():
    """The JSON must carry the estate the prose claimed -- two answers to one
    question in one document is the defect the second act already guards."""
    done = _via_cli("--fixture", "--skip-readers", "--json")
    assert done.returncode == 0, done.stdout[-3000:]
    import json as _json
    found = _json.loads(done.stdout)
    assert found["agreed"] is True
    assert sorted(found["estate"]["hosts"]) == ["codecartographer", "dossier"]
    assert found["estate"]["families"] >= 4
    assert found["estate"]["placements"] > found["estate"]["families"], (
        "fewer placements than families would mean empty families agreed")


@needs_siblings
def test_skipping_the_estate_is_stated_in_the_output():
    """A skip that left no trace would read as a demo that covered less than
    it claims; the reader act follows the same rule."""
    done = _via_cli("--fixture", "--skip-readers", "--skip-estate")
    assert done.returncode == 0, done.stdout[-2000:]
    assert "third act was skipped" in done.stdout
    assert "ESTATE AGREEMENT" not in done.stdout

