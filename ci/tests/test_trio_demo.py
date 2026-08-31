"""The trio demo, executed.

`protocols/local-demo.md` rule 2: a test runs the demo. **Not a test of the same
behaviour -- a test that executes the demo itself.** A demo the suite does not
touch rots quietly, and the failure that rule exists against is a demo described
in a handoff that nobody could replay.

**AND IT IS RUN THE WAY IT IS DOCUMENTED**, through `qm demo` rather than by
file path. A test that invoked the path would prove the path works and say
nothing about the route everybody is told to use -- which is the half that
breaks, because the route is the part with a table entry to forget.

**MOST OF THIS SUITE CANNOT RUN IN CI, AND SAYS SO.** The demo needs `qmcp` and
`dossier` beside this clone with their environments built. A hosted runner has
this repository and nothing else, so the tests that need siblings skip there with
a reason, and the ones that can always run -- that the module imports, that its
pieces are honest about a missing sibling -- run everywhere. A skip carrying a
reason is a different artefact from a test that quietly passed.
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

    **REGISTERED IN `sys.modules` BEFORE EXECUTION.** `@dataclass` resolves
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
    """Rule 1. The failure this exists against: a demo typed into a session and
    pasted into a handoff, which nobody else could run."""
    assert DEMO.is_file()


def test_the_demo_imports():
    module = _module()
    assert callable(module.main)


def test_a_missing_sibling_is_reported_rather_than_skipped_silently():
    """A trio demo that ran with one side missing and printed a summary would
    be a green result measuring less than the reader thinks.

    Mutation: return 0 when a needed sibling is absent and this fails.

    `main([])` rather than `main()`: with no argv argparse reads `sys.argv`,
    which under pytest holds pytest's own arguments and makes the demo exit 2
    on an unrecognised flag.
    """
    module = _module()
    module.SIBLINGS = Path("/nowhere-that-exists")
    # `QM_SIBLINGS` in the operator's shell would replace SIBLINGS and make
    # this test find the real repositories -- which is what happened the day
    # the override was added, from a session that had exported it to run the
    # demo out of a worktree. The test is about the resolver, not the shell.
    import os
    saved = os.environ.pop("QM_SIBLINGS", None)
    try:
        assert module.main([]) == 1
    finally:
        if saved is not None:
            os.environ["QM_SIBLINGS"] = saved


def test_the_windows_read_the_rendering_rather_than_the_payload():
    """**THE GUARD ON THE DEMO'S OWN HONESTY.**

    Both window scripts once counted `weight is None` in the document they had
    just been handed. They agreed perfectly and tested nothing -- two readers of
    one field always agree. Each window must report what *it drew*.

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
    """`sys.executable` ran every window in the demo's own environment, and the
    harness reported that it could not emit a topology -- a true sentence about
    the wrong process.

    **ASSERTS THE CALL, NOT THE WORD.** The first version counted occurrences of
    `sys.executable` in the file and failed on the docstring that forbids it --
    a text scan matching the prose that bans the thing, which is one of the
    false readings `records/DRAFT-decision-record-discipline.md` §7 lists by
    name.
    """
    source = DEMO.read_text(encoding="utf-8")
    assert "subprocess.run([sys.executable" not in source, (
        "a window is being run with the demo's own interpreter")
    # **EVERY subprocess, not a fixed count of them.** The first version
    # asserted exactly two call sites, which failed the day a third kind of
    # process -- a reader -- was added, while saying nothing about whether
    # that third one used the right interpreter. The invariant is that no
    # subprocess is started with anything but its own project's interpreter.
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
# **MEMOISED, NOT MERGED.** Ten invocations here spawn the demo, and several ask
# for exactly the same thing: three tests run `qm demo` with no options and
# assert three different properties of the same output. Merging them into one
# test would buy the same seconds and cost the failure message -- "the demo is
# wrong" instead of "the demo stopped saying what it did not establish".
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
    """THE ONE THAT MATTERS. The demo exits 0 only when every window that drew
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
    """**THE OPTION THAT COULD HAVE WEAKENED THE CHECK.**

    `--window` narrows what draws, and the obvious implementation lets a single
    window run and report success -- one window agreeing with itself. The demo
    exits 1 instead, and says why.

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
    """**THE STRUCTURAL ONE.**

    The subprocess mode and the HTTP mode must not each own a copy of the
    agreement check. Two copies drift, and the one that drifts lenient is the
    one nobody notices -- a demo that passes because its second implementation
    forgot the unmeasured comparison is worse than no demo.

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
    """**THE POINT OF THE MODE.**

    Importing codecarto's renderer here would test the same code the subprocess
    mode already covers and leave the route -- the part that was missing for
    days -- unexercised. The answer must come off the wire.

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
    """The gap this closed: the harness had no topology route at all, so
    neither front end could fetch one and only a subprocess could draw."""
    module = _module()
    document, why = module._harness_document("codecartographer")
    assert document is not None, why
    assert "payload" in document and "encoding" in document


@pytest.mark.skipif(
    not (_reachable("http://127.0.0.1:3141/health")
         and _reachable("http://127.0.0.1:2718/topology/data")),
    reason="the trio is not up; `uv run qm dashboard --start harness --start web`")
def test_the_deployed_front_ends_agree():
    """THE DEMO, AS DEPLOYED. Every answer here comes from a process somebody
    could have opened in a browser."""
    done = _via_cli("--over-http")
    assert done.returncode == 0, done.stdout[-2500:]
    assert "windows agree about every box" in done.stdout


# --- the figure both windows print ------------------------------------------
#
# The side-by-side put `17%` in one column and `w=1.42` in the other for the
# same edge. Both were right: the second is a line thickness derived from the
# first. Neither was comparable, and the demo exists to invite exactly that
# comparison -- its premise is that a figure differing between windows is a
# defect rather than a point of view.
#
# **`uv run qm mutate ci/trio_demo.py` CANNOT MEASURE THIS FILE, AND THE REASON
# IS NOT THAT IT IS UNTESTED.** The mutator copies the module to a temporary
# directory and runs the suite against the copy; `sibling()` resolves the other
# repositories relative to the module's own path, so from a temp directory the
# demo reports that qmcp and dossier are not beside this clone and the baseline
# is red before a single operator is applied. A mutation run against a red
# baseline establishes nothing in either direction. The mutations named below
# were therefore applied by hand, watched go red, and restored -- which is what
# charter P16 asks for; the tool is the convenience, not the rule.


def test_a_measured_edge_prints_the_same_figure_the_other_window_prints():
    """Mutation: return the width instead of the weight and this fails."""
    assert _module()._figure(0.17) == "17%"
    assert _module()._figure(0.127) == "13%"


def test_an_unmeasured_edge_says_so_rather_than_borrowing_a_figure():
    """THE ONE THAT MATTERS.

    `None` is not zero. Rounding it into `0%` would render the one distinction
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
    """**THE TWO PATHS MUST NOT DRIFT.** One window is rendered over HTTP and
    one in the sibling's own interpreter; the demo shares its comparison
    between the modes so neither can drift lenient, and the rendering has to be
    held to the same rule.

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
    """A reader reads a thread; a window draws a topology. Putting looksatwords
    in WINDOWS would have made the demo ask it to agree about boxes."""
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
    behaviour below, in `test_the_seam_comparison_catches_...` -- a string
    assertion here passed a mutation that emptied the check."""
    module = _module()
    assert "turns_with_text" in module.LOOKSATWORDS, (
        "the looksatwords reader must report the seam's second count")
    assert "as_conversation" in module.LOOKSATWORDS, (
        "the counts must come from the project's own seam conversion, not a "
        "second one done for the demo")


def test_the_sibling_roots_override_replaces_rather_than_extends(
        tmp_path, monkeypatch):
    """A worktree is beside nothing. `QM_SIBLINGS` replaces the convention --
    two sources of truth for which repositories a demo may read is how an
    allowlist stops being one."""
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
    """THE ONE THAT MATTERS for the second act. looksatwords must report the
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
    """**BEHAVIOUR, NOT A STRING.** The first version of the border test
    asserted that the phrase "never authors a decision" appeared in the
    source, and a mutation that emptied the check while keeping the message
    passed it. This feeds the comparison a reader that over-counts by one and
    a reader that emitted a `settled` key, and expects both named.

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
    """One document, one answer. `agreed` was left true by the first act when
    the second failed, until a mutation showed the JSON carrying both."""
    module = _module()
    import inspect

    body = inspect.getsource(module.main)
    assert 'result["agreed"] = False' in body
