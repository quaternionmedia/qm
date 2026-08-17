"""The protocol registry, whose one derived fact is when each protocol last ran.

Nothing here reads the committed registry except the two tests that say so. The
rest build a registry and a runs directory in a temporary tree, so no test
passes because this repository happens to be in the state it asserts — and in
particular, no test starts failing on the day somebody records a run.

The load-bearing property is that `last_run` cannot be declared. A date a person
types is a date that stops being true with nothing changing, which is the whole
failure this registry is against.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from protocols import (  # noqa: E402
    known_routes, last_run, load, main, problems, render, runs,
)

ROOT = CI_DIR.parent


def entry(pid: str = "a-protocol", page: str = "protocols/a.md", **kw) -> dict:
    base = {
        "id": pid,
        "name": "A Protocol",
        "question": "what?",
        "page": page,
        "invoked_by": "a human",
        "produces": "protocols/runs/<date>-a-protocol.md",
        "steps": ["uv run qm gates"],
        "cannot_see": "plenty",
        "cadence_days": 30,
    }
    base.update(kw)
    return base


def tree(tmp_path: Path, *pages: str) -> Path:
    (tmp_path / "protocols").mkdir(parents=True, exist_ok=True)
    for name in pages:
        (tmp_path / "protocols" / name).write_text("# page\n", encoding="utf-8")
    return tmp_path


def run_file(tmp_path: Path, name: str) -> Path:
    directory = tmp_path / "protocols" / "runs"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text("# a run\n", encoding="utf-8")
    return path


# --- the registry ------------------------------------------------------------


def test_an_empty_registry_is_refused_not_reported_clean(tmp_path):
    """Zero protocols would make every count below vacuously fine."""
    path = tmp_path / "r.yaml"
    path.write_text("schema: 1\nprotocols: []\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        load(path)


def test_a_missing_registry_says_nothing_is_declared(tmp_path):
    with pytest.raises(SystemExit):
        load(tmp_path / "absent.yaml")


def test_a_protocol_with_no_page_is_refused(tmp_path):
    found = problems([entry(page="protocols/absent.md")], {"gates"}, tree(tmp_path))
    assert any("is not there" in p for p in found)


def test_a_page_nobody_registered_is_refused(tmp_path):
    """The claim layer and the artifact layer disagreeing, in the other direction."""
    root = tree(tmp_path, "a.md", "orphan.md")
    found = problems([entry()], {"gates"}, root)
    assert any("orphan.md" in p and "nobody registered" in p for p in found)


def test_the_directory_readme_is_not_a_protocol(tmp_path):
    root = tree(tmp_path, "a.md", "README.md")
    assert problems([entry()], {"gates"}, root) == []


def test_a_step_naming_a_route_that_does_not_exist_is_refused(tmp_path):
    """A renamed route otherwise breaks every page citing it, in silence."""
    found = problems([entry(steps=["uv run qm nosuchroute"])], {"gates"}, tree(tmp_path, "a.md"))
    assert any("not a route" in p for p in found)


def test_a_step_that_is_not_a_qm_command_is_left_alone(tmp_path):
    """Protocols legitimately name `gh`, `python` and plain prose steps."""
    steps = ["gh api --paginate repos/o/r/activity", "python ci/thing.py", "read the diff"]
    assert problems([entry(steps=steps)], {"gates"}, tree(tmp_path, "a.md")) == []


def test_a_protocol_with_no_cannot_see_is_refused(tmp_path):
    found = problems([entry(cannot_see="")], {"gates"}, tree(tmp_path, "a.md"))
    assert any("cannot_see" in p for p in found)


def test_two_protocols_with_one_id_are_refused(tmp_path):
    found = problems([entry(), entry()], {"gates"}, tree(tmp_path, "a.md"))
    assert any("duplicate id" in p for p in found)


# --- last_run is derived, never declared -------------------------------------


def test_a_run_is_found_by_its_filename(tmp_path):
    run_file(tmp_path, "2026-08-16-a-protocol.md")
    found = runs(tmp_path / "protocols" / "runs")
    assert found["a-protocol"][0][0] == date(2026, 8, 16)


def test_the_most_recent_run_wins_regardless_of_directory_order(tmp_path):
    for name in ("2026-08-16-a-protocol.md", "2026-01-02-a-protocol.md",
                 "2026-03-04-a-protocol.md"):
        run_file(tmp_path, name)
    found = runs(tmp_path / "protocols" / "runs")
    assert last_run(entry(), found)[0] == date(2026, 8, 16)


def test_a_declared_last_run_is_ignored_because_it_is_not_read(tmp_path):
    """The registry cannot assert this fact. A field claiming it does nothing."""
    found = runs(tmp_path / "protocols" / "runs")
    assert last_run(entry(last_run="2026-08-16"), found) is None


def test_a_file_that_is_not_a_dated_run_is_skipped(tmp_path):
    run_file(tmp_path, "notes.md")
    run_file(tmp_path, "2026-13-45-a-protocol.md")
    assert runs(tmp_path / "protocols" / "runs") == {}


def test_a_missing_runs_directory_is_no_runs_and_not_a_crash(tmp_path):
    assert runs(tmp_path / "nowhere") == {}


# --- what the output says ----------------------------------------------------


def test_a_protocol_never_run_says_so_in_those_words():
    text = render([entry()], {}, date(2026, 8, 16), None)
    assert "NEVER RUN" in text
    assert "1 have never been run" in text


def test_a_run_past_its_budget_is_marked(tmp_path):
    found = {"a-protocol": [(date(2026, 1, 1), tmp_path / "x.md")]}
    text = render([entry()], found, date(2026, 8, 16), None)
    assert "past its budget" in text


def test_a_run_inside_its_budget_is_not_marked(tmp_path):
    found = {"a-protocol": [(date(2026, 8, 1), tmp_path / "x.md")]}
    text = render([entry()], found, date(2026, 8, 16), None)
    assert "past its budget" not in text


def test_the_output_states_that_it_never_read_a_run(tmp_path):
    text = render([entry()], {}, date(2026, 8, 16), None)
    assert "does not read one word" in text


def test_an_optional_protocol_is_labelled_as_one():
    assert "[optional]" in render([entry(optional=True)], {}, date(2026, 8, 16), None)
    assert "[optional]" not in render([entry()], {}, date(2026, 8, 16), None)


def test_asking_for_a_protocol_that_does_not_exist_lists_the_ones_that_do():
    with pytest.raises(SystemExit) as exit_info:
        render([entry()], {}, date(2026, 8, 16), "nope")
    assert "a-protocol" in str(exit_info.value)


def test_asking_for_one_that_does_exist_prints_it_and_not_the_others():
    text = render([entry("wanted"), entry("other", page="protocols/b.md")],
                  {}, date(2026, 8, 16), "wanted")
    assert "(wanted)" in text
    assert "(other)" not in text


def test_every_step_is_printed():
    """The steps are the protocol. A page that lists none is a name."""
    text = render([entry(steps=["uv run qm gates", "read the diff"])],
                  {}, date(2026, 8, 16), None)
    assert "uv run qm gates" in text
    assert "read the diff" in text


def test_the_totals_line_counts_protocols_and_never_run_runs():
    text = render([entry("one"), entry("two", page="protocols/b.md")],
                  {"one": [(date(2026, 8, 1), Path("x.md"))]}, date(2026, 8, 16), None)
    assert "2 protocol(s)" in text
    assert "1 have never been run" in text


# --- the route's own exit behaviour ------------------------------------------


def registry_file(tmp_path: Path, *entries: dict) -> Path:
    import yaml  # noqa: PLC0415 -- only this helper needs it

    path = tmp_path / "protocol-registry.yaml"
    path.write_text(yaml.safe_dump({"schema": 1, "protocols": list(entries)}),
                    encoding="utf-8")
    return path


def test_check_names_the_protocols_that_have_never_been_run(tmp_path, capsys):
    """The count alone would let a reader think something had run."""
    tree(tmp_path, "a.md")
    path = registry_file(tmp_path, entry())
    assert main(["--registry", str(path), "--root", str(tmp_path),
                 "--runs", str(tmp_path / "runs"), "--check"]) == 0
    out = capsys.readouterr().out
    assert "have never been run: a-protocol" in out


def test_check_reds_on_a_step_naming_a_dead_route(tmp_path, capsys):
    tree(tmp_path, "a.md")
    path = registry_file(tmp_path, entry(steps=["uv run qm ghost"]))
    assert main(["--registry", str(path), "--root", str(tmp_path),
                 "--runs", str(tmp_path / "runs"), "--check"]) == 1
    assert "not a route" in capsys.readouterr().err


# --- the two that read the committed corpus ----------------------------------


def test_the_committed_registry_declares_only_runnable_steps():
    """The point of the route. If this fails, a protocol names a dead command."""
    assert problems(load(), known_routes()) == []


def test_the_route_table_is_read_from_the_cli_and_not_copied():
    """A second copy of the route list would be a second thing to keep in step."""
    routes = known_routes()
    assert "gates" in routes and "curriculum" in routes and "protocols" in routes
