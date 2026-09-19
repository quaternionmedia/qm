"""The posture reading, and the false hundred per cent it reported.

**THIS FILE EXISTS BECAUSE THE TOOL LIED AND WAS BELIEVED.** `qm posture`
reported `44/44 (100%)` for every watched module. The truth was `28/44`. The
cause was a loose pattern searching for a number near the word `killed`, which
matched `44 killed` inside the string `28/44 killed` — so the denominator was
read as the numerator and every score came out perfect.

It was printed, read, and repeated to a person before anything checked it. In a
tool built to measure whether checks catch things. That is charter P16's whole
claim in one artefact: reading the code told the author what they meant, and
only comparing it against a known number told them what it did.

THE TESTS WORTH READING ARE THE FIRST TWO: the exact string that produced the
false reading, and the cross-check that now refuses to guess.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

CI = Path(__file__).resolve().parent.parent


def _module():
    spec = importlib.util.spec_from_file_location(
        "test_posture_module", CI / "test_posture.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


posture = _module()


def _answers(monkeypatch, stdout: str, returncode: int = 0):
    """Make the next subprocess call answer with `stdout`."""
    def fake(*args, **kw):
        return subprocess.CompletedProcess(
            args=args[0] if args else [], returncode=returncode,
            stdout=stdout, stderr="")
    monkeypatch.setattr(posture.subprocess, "run", fake)


# --- the false hundred per cent -----------------------------------------------


REAL_OUTPUT = """
  [killed ]   1/44  line   59  ' not ' -> ' '
  [SURVIVED]   2/44  line   59  ' or ' -> ' and '
28/44 killed, of 44 mutants.
A killed mutant means some test noticed, not that the right one did.
"""


def test_the_score_is_read_from_the_summary_not_from_a_nearby_number(monkeypatch):
    """THE ONE THAT MATTERS.

    `28/44 killed` contains the substring `44 killed`. A pattern looking for
    digits followed by the word produced 44 out of 44, and there is no reading
    of that output in which the score is 100%.

    Mutation: match `(\\d+)\\s+killed` instead of the `N/M` form and this fails.
    """
    _answers(monkeypatch, REAL_OUTPUT)
    found = posture.measure_yield("ci/x.py", "ci/tests/test_x.py")

    assert found.caught == 28
    assert found.mutants == 44
    assert found.survived == 16
    assert 63 < found.score < 65, f"score read as {found.score}"


def test_a_summary_that_disagrees_with_a_complete_marker_list_is_unreadable(monkeypatch):
    """THE OTHER ONE.

    Two independent reads of the same run, and a disagreement between them is
    reported rather than resolved. Picking one would be this tool deciding
    which of its own numbers to trust, which is how the first version got to
    100% in the first place.

    Mutation: drop the cross-check and this fails.
    """
    # Markers accounting for every mutant, and a summary that disagrees with
    # them. A *partial* marker list is not a disagreement — it is less evidence
    # — and treating it as one made a correct reading unreadable.
    markers = "\n".join(f"  [killed ]   {n}/4" for n in range(1, 5))
    _answers(monkeypatch, markers + "\n2/4 killed, of 4 mutants.\n")
    found = posture.measure_yield("ci/x.py", "ci/tests/test_x.py")
    assert found.unreadable
    assert "markers show" in found.unreadable
    assert found.mutants == 0, "a disagreement must not produce a score"


def test_output_with_no_summary_is_named_rather_than_scored_zero(monkeypatch):
    """A run that could not be read and a module nothing caught are opposite
    facts, and a score of 0% states the first while meaning the second."""
    _answers(monkeypatch, "no tests. A module with tests elsewhere must name "
                          "them with --tests")
    found = posture.measure_yield("ci/x.py", "ci/tests/test_x.py")
    assert found.unreadable and found.mutants == 0
    assert "--tests" in found.unreadable


def test_a_truncated_marker_list_does_not_make_a_reading_unreadable(monkeypatch):
    """Output gets truncated by pipes and capture limits. Fewer markers than
    mutants is less evidence, not contradictory evidence, and calling it a
    disagreement threw away a correct reading.

    Mutation: cross-check without requiring a complete marker list and this
    fails.
    """
    _answers(monkeypatch, REAL_OUTPUT)
    found = posture.measure_yield("ci/x.py", "ci/tests/test_x.py")
    assert not found.unreadable
    assert found.caught == 28 and found.mutants == 44


# --- the suite reading --------------------------------------------------------


NESTED = """
0.20s call     ci/tests/test_mutate.py::test_something
277 passed in 3.10s
0.50s setup    ci/tests/test_other.py::test_thing
1058 passed in 132.96s
"""


def test_the_test_count_is_the_last_summary_not_the_first(monkeypatch):
    """Some tests here run pytest in a subprocess by design, and their
    summaries land in this output. Taking the first read 277 where the suite
    had 1058.

    Mutation: use the first match and this fails.
    """
    _answers(monkeypatch, NESTED)
    found = posture.measure_suite(("ci/tests",))
    assert found.tests == 1058


def test_setup_time_is_summed_and_slow_calls_are_listed(monkeypatch):
    _answers(monkeypatch, NESTED)
    found = posture.measure_suite(("ci/tests",))
    assert found.setup == pytest.approx(0.50)
    assert found.slowest == []


def test_a_failing_suite_produces_no_reading_at_all(monkeypatch):
    """**A READING FROM A FAILED RUN IS NOT A READING.** Reporting a wall clock
    for a red suite would make a broken suite look like a fast one.

    Mutation: ignore the return code and this fails.
    """
    _answers(monkeypatch, "3 failed, 5 passed in 1.00s", returncode=1)
    with pytest.raises(SystemExit) as raised:
        posture.measure_suite(("ci/tests",))
    assert "nothing to measure" in str(raised.value)


# --- the watched list ---------------------------------------------------------


def test_every_watched_module_and_its_tests_exist():
    """A watched pair naming a file that is gone reports `unreadable` forever,
    which reads as a tool problem rather than a stale list.

    Mutation: add a pair naming a missing file and this fails.
    """
    for module, tests in posture.WATCHED:
        assert (posture.CORPUS / module).is_file(), f"no such module: {module}"
        assert (posture.CORPUS / tests).is_file(), f"no such tests: {tests}"


def test_cost_and_yield_are_reported_together(capsys):
    """The tool's whole premise. A reading that printed one without the other
    would let a suite get faster and blinder with nothing to notice.

    Mutation: drop the yield section from `report` and this fails.
    """
    posture.report(posture.Suite(wall=10.0, tests=5, setup=1.0),
                   [posture.Yield("ci/x.py", mutants=10, caught=6)], None)
    printed = capsys.readouterr().out
    assert "tests in" in printed
    assert "YIELD" in printed
    assert "6/10" in printed
    assert "read together" in printed
