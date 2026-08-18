"""The mutation harness, which is the thing every other mutation claim rests on.

A harness that reports a high kill rate for the wrong reason is worse than no
harness: it is a number in a retrospective that nobody can go back and check.
The two failure modes that produce one are both tested here — a baseline that
was already red, so every mutant dies for free, and a mutant generated from a
docstring, which no test can kill and which pads the denominator.

The end-to-end tests build a small `ci/` tree in a temporary directory and run
the real sweep over it, subprocesses and all. They are the slowest tests in this
suite by some margin, and they are the only ones that establish the harness does
what its output says.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import mutate  # noqa: E402
from mutate import (  # noqa: E402
    OPERATORS, apply_mutant, code_lines, default_tests, main, mutants,
    run_tests, sweep,
)

# Four mutable lines and one that must not be: the docstring holds `True`, and
# a mutant made from it is unkillable by construction.
TARGET = '''"""A module whose docstring says True and is not code."""


def verdict(items):
    # A comment holding True as well.
    if items is None:
        return None
    return len(items) == 0


def unread(flag):
    return flag == 0
'''

TESTS = '''import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from target import verdict


def test_none_in_none_out():
    assert verdict(None) is None


def test_an_empty_list_is_the_verdict():
    assert verdict([]) is True
'''


def build(tmp_path: Path, target: str = TARGET, tests: str = TESTS) -> tuple[Path, Path]:
    (tmp_path / "ci" / "tests").mkdir(parents=True)
    module = tmp_path / "ci" / "target.py"
    module.write_text(target, encoding="utf-8")
    test_file = tmp_path / "ci" / "tests" / "test_target.py"
    test_file.write_text(tests, encoding="utf-8")
    return module, test_file


# --- the operator table -----------------------------------------------------


def test_no_operator_substitutes_a_thing_for_itself():
    """An identity operator emits a mutant identical to the original source.

    It cannot be killed, because nothing changed — so it lands in the survivor
    list and reads as a missing test. One padded denominator is how a kill rate
    stops meaning anything.
    """
    assert all(was != now for was, now in OPERATORS)


def test_every_operator_is_a_pair_of_non_empty_strings():
    assert all(isinstance(was, str) and was for was, _ in OPERATORS)
    assert all(isinstance(now, str) for _, now in OPERATORS)


# --- what counts as a mutable line ------------------------------------------


def test_a_docstring_is_not_code():
    live = code_lines(TARGET)
    assert 1 not in live


def test_a_comment_is_not_code():
    live = code_lines(TARGET)
    assert 5 not in live
    assert 6 in live


def test_a_multi_line_docstring_is_skipped_to_its_closing_fence():
    source = '"""one\ntwo True\n"""\nx = True\n'
    assert code_lines(source) == {4}


def test_a_one_line_docstring_does_not_swallow_the_rest_of_the_file():
    """Two fences on a line open and close it. Treating that as an opener
    would silently exclude every line after it, and the sweep would report a
    small mutant count with nothing to say it was small."""
    source = '"""a docstring on one line"""\nx = True\ny = False\n'
    assert code_lines(source) == {2, 3}


# --- what mutants are generated ---------------------------------------------


def test_every_operator_match_becomes_its_own_mutant():
    found = mutants(TARGET)
    changes = {(m.was, m.now) for m in found}
    assert ("is None", "is not None") in changes
    assert ("return None", "return []") in changes
    assert ("==", "!=") in changes


def test_no_mutant_is_made_from_prose_the_tests_cannot_reach():
    assert all(m.line != 1 for m in mutants(TARGET))
    assert all(m.line != 5 for m in mutants(TARGET))


def test_a_mutant_changes_one_occurrence_on_one_line():
    source = "a = 1 == 2 == 3\nb = 4 == 5\n"
    found = [m for m in mutants(source) if m.line == 1]
    changed = apply_mutant(source, found[0])
    assert changed.splitlines()[0] == "a = 1 != 2 == 3"
    assert changed.splitlines()[1] == "b = 4 == 5"


def test_a_mutant_cannot_be_edited_after_it_is_generated():
    """The record of what was changed is the whole evidence a survivor offers.

    A sweep reports mutants it generated before running anything; if one can be
    rewritten in flight, the list and the runs stop being about the same thing.
    """
    found = mutants("x = True\n")[0]
    with pytest.raises(Exception):
        found.line = 99


def test_applying_a_mutant_does_not_lose_the_trailing_newline():
    source = "x = True\n"
    assert apply_mutant(source, mutants(source)[0]) == "x = False\n"


# --- where the tests are looked for -----------------------------------------


def test_the_default_test_file_is_named_after_the_module(tmp_path):
    assert default_tests(Path("ci/rulesets.py"), tmp_path).name == "test_rulesets.py"


def test_a_module_with_no_tests_is_refused_rather_than_scored(tmp_path):
    """Reporting 0/0 killed for a module nobody tested would read as a pass."""
    module = tmp_path / "orphan.py"
    module.write_text("x = True\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exit_info:
        main([str(module)])
    assert "no tests" in str(exit_info.value)


def test_a_module_that_does_not_exist_is_named_in_the_refusal(tmp_path):
    with pytest.raises(SystemExit) as exit_info:
        main([str(tmp_path / "absent.py")])
    assert "not a file" in str(exit_info.value)


def test_a_relative_path_is_resolved_against_the_repository_root(tmp_path, monkeypatch, capsys):
    """Both paths, and both against the root rather than the shell's cwd.

    `uv run qm mutate ci/rulesets.py` is how this is typed. Resolving against
    the working directory instead would work from the repository root and fail
    everywhere else, which is the kind of defect that only shows up for
    somebody else.
    """
    build(tmp_path)
    monkeypatch.setattr(mutate, "ROOT", tmp_path)
    monkeypatch.chdir(tmp_path / "ci")
    assert main(["ci/target.py", "--tests", "ci/tests/test_target.py", "--list"]) == 0
    assert "->" in capsys.readouterr().out


def test_the_default_tests_are_found_through_the_redirected_root(tmp_path, capsys):
    """`default_tests` reads the root it is given, not the one bound at import."""
    build(tmp_path)
    assert default_tests(tmp_path / "ci" / "target.py", tmp_path).is_file()


def test_list_runs_nothing_and_prints_the_mutants(tmp_path, capsys):
    module, tests = build(tmp_path)
    assert main([str(module), "--tests", str(tests), "--list"]) == 0
    printed = capsys.readouterr().out
    assert "'return None' -> 'return []'" in printed


# --- the sweep, end to end --------------------------------------------------


def test_the_test_run_writes_no_bytecode(monkeypatch, tmp_path):
    """Without `-B`, a mutant can import the previous mutant's cached bytecode.

    CPython keys a `.pyc` on the source's size and its mtime truncated to whole
    seconds. `==` -> `!=` changes neither, and two mutants are written well
    inside one second — so the harness reports a result for code that never
    ran, and reports a different one on the next sweep.
    """
    seen = {}
    monkeypatch.setattr(mutate.subprocess, "run",
                        lambda cmd, **kw: seen.setdefault("cmd", list(cmd)))
    run_tests(tmp_path / "test_x.py", tmp_path)
    assert "-B" in seen["cmd"]
    assert seen["cmd"].index("-B") < seen["cmd"].index("-m")


def test_a_red_baseline_stops_the_sweep_rather_than_scoring_it(tmp_path):
    """Every mutant dies against a suite that was already failing.

    This corpus has published a mutation result produced that way. The guard is
    the reason the number below means anything.
    """
    module, tests = build(tmp_path, tests=TESTS + "\n\ndef test_broken():\n    assert False\n")
    said: list[str] = []
    with pytest.raises(SystemExit) as exit_info:
        sweep(module, tests, root=tmp_path, out=said.append)
    assert exit_info.value.code == 2
    # The reason, not just the exit code: a sweep that stops silently looks
    # like a sweep that found nothing.
    assert any("does not pass unmutated" in line for line in said)
    assert any("Nothing was measured" in line for line in said)


def test_the_sweep_kills_what_is_tested_and_reports_what_is_not(tmp_path):
    module, tests = build(tmp_path)
    survivors, errored, total = sweep(module, tests, root=tmp_path, out=lambda *a: None)
    assert total == 4, "the docstring and the comment leaked into the count"
    assert errored == []
    # `unread` has no test, so its comparison flip survives — and it is the
    # same substitution, on a line of the same length, as the one two lines
    # above it that does not. Those two outcomes differing is what the stale
    # bytecode used to hide.
    assert [m.line for m in survivors] == [12]


def test_a_run_with_no_verdict_is_counted_in_neither_column(tmp_path):
    """A mutant that stops pytest from running at all was not caught by a test.

    `if __name__ == "__main__":` flipped to `!=` makes the module call `main()`
    on import, and pytest exits 3 with an internal error. Counting that as a
    kill — which any `returncode != 0` test does — credits the suite for a
    mutant it never examined.
    """
    target = 'import sys\n\n\ndef verdict(x):\n    return x\n\n\nif __name__ == "__main__":\n    sys.exit(verdict(1))\n'
    tests = (
        "import sys\nfrom pathlib import Path\n\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parent.parent))\n\n"
        "from target import verdict\n\n\n"
        "def test_verdict():\n    assert verdict(1) == 1\n"
    )
    module, test_file = build(tmp_path, target=target, tests=tests)
    survivors, errored, total = sweep(module, test_file, root=tmp_path, out=lambda *a: None)
    assert [code for _, code in errored] == [3]
    assert survivors == []
    assert total == len(errored), "the errored mutant is the only one here"


def test_two_sweeps_of_the_same_tree_report_the_same_thing(tmp_path):
    """A harness whose answer depends on how many times it has run is a
    measurement of itself. The second sweep must see what the first saw."""
    module, tests = build(tmp_path)
    first, _, _ = sweep(module, tests, root=tmp_path, out=lambda *a: None)
    second, _, _ = sweep(module, tests, root=tmp_path, out=lambda *a: None)
    assert [m.line for m in first] == [m.line for m in second]


def test_a_survivor_reds_the_run_only_when_check_was_asked_for(tmp_path, monkeypatch):
    """Reporting is not judging. `--check` is what makes a survivor a failure,
    and a route that exits non-zero without it cannot be run to look."""
    build(tmp_path)
    monkeypatch.setattr(mutate, "ROOT", tmp_path)
    argv = [str(tmp_path / "ci" / "target.py"), "--tests",
            str(tmp_path / "ci" / "tests" / "test_target.py")]
    assert main(argv) == 0
    assert main([*argv, "--check"]) == 1
