"""The trio demo, executed.

`protocols/local-demo.md` rule 2: a test runs the demo. **Not a test of the same
behaviour -- a test that imports and executes the demo module.** A demo the suite
does not touch rots quietly, and the failure that rule exists against is a demo
described in a handoff that nobody could replay.

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
DEMO = ROOT / "protocols" / "trio_demo.py"


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
    """
    module = _module()
    module.SIBLINGS = Path("/nowhere-that-exists")
    assert module.main() == 1


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


@needs_siblings
def test_the_demo_runs_and_the_windows_agree():
    """THE ONE THAT MATTERS. The demo exits 0 only when every window that drew
    the topology agrees about every box, every arrow, and which edges nobody
    measured."""
    done = subprocess.run([sys.executable, str(DEMO)], cwd=ROOT,
                          capture_output=True, text=True, timeout=900)
    assert done.returncode == 0, (
        f"the trio demo failed:\n{done.stdout[-3000:]}\n{done.stderr[-1500:]}")
    assert "windows agree about every box" in done.stdout


@needs_siblings
def test_the_demo_says_what_it_did_not_establish():
    """Rule 4. A demo that only printed successes would be advertising."""
    done = subprocess.run([sys.executable, str(DEMO)], cwd=ROOT,
                          capture_output=True, text=True, timeout=900)
    assert "WHAT THIS DID NOT ESTABLISH" in done.stdout
    assert "Both windows would faithfully draw a wrong one" in done.stdout


@needs_siblings
def test_the_demo_names_its_data_source():
    """Real archive or stated fixture, never silently one wearing the other's
    name."""
    done = subprocess.run([sys.executable, str(DEMO)], cwd=ROOT,
                          capture_output=True, text=True, timeout=900)
    assert ("data         thread archive" in done.stdout
            or "data         fixture" in done.stdout)
