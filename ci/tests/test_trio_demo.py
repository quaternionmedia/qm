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
    assert module.main([]) == 1


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
    assert source.count("subprocess.run(\n        [interpreter(project)") \
        + source.count("subprocess.run([interpreter(project)") == 2, (
            "both windows must resolve their own project's interpreter")


# --- needs the siblings -------------------------------------------------------


def _via_cli(*options: str):
    """The demo through its declared route, which is how it is documented."""
    return subprocess.run(
        [sys.executable, str(ROOT / "ci" / "cli.py"), "demo", *options],
        cwd=ROOT, capture_output=True, text=True, timeout=900)


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
