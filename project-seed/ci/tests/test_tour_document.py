"""The tour's two documents, against the schema every application serves them by.

An application emits them and the harness reads them, and the seed's schema
and vectors are what the two hold to. These run the reader as a project runs
it, out of the seed, and hold that it refuses what the vectors say it refuses,
including the rules a schema cannot state.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from conftest import CI_DIR, run_tool, write

SEED = CI_DIR.parent
VECTORS = json.loads((SEED / "tour-vectors.json").read_text(encoding="utf-8"))


def case(name: str) -> dict:
    return copy.deepcopy(next(c for c in VECTORS["cases"] if c["name"] == name))


def run(tmp_path: Path, *args: str):
    return run_tool("tour_document.py", *args, cwd=tmp_path)


def test_every_vector_is_decided_as_it_declares(tmp_path: Path):
    result = run(tmp_path, "--vectors")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "every case decided as declared" in result.stdout


def test_the_vectors_hold_both_documents_both_ways():
    """A vectors file with no refused case, or no feedback case, tests one side."""
    held = {(c["document"], c["valid"]) for c in VECTORS["cases"]}
    assert held == {("tour", True), ("tour", False), ("feedback", True), ("feedback", False)}


def test_a_case_declared_against_the_reader_fails_the_run(tmp_path: Path):
    """Mutation: a refused case declared valid is reported, and the run exits 1."""
    flipped = copy.deepcopy(VECTORS)
    for c in flipped["cases"]:
        if c["name"] == "off, saying nothing of what is off":
            c["valid"] = True
    path = tmp_path / "vectors.json"
    write(path, json.dumps(flipped))
    result = run(tmp_path, "--vectors", str(path))
    assert result.returncode == 1
    assert "off, saying nothing of what is off: declared valid, refused" in result.stdout


def test_vectors_with_no_case_are_not_clean(tmp_path: Path):
    path = tmp_path / "vectors.json"
    write(path, json.dumps({"schema": 1, "cases": []}))
    result = run(tmp_path, "--vectors", str(path))
    assert result.returncode == 1
    assert "holds no case" in result.stdout


def test_a_tour_document_is_read_from_a_file(tmp_path: Path):
    path = tmp_path / "tour.json"
    write(path, json.dumps(case("a journey with a word on two of its stages")["payload"]))
    result = run(tmp_path, "--tour", str(path))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "the shape of a GET /tour document" in result.stdout


def test_a_stage_with_no_line_is_refused_where_it_stands(tmp_path: Path):
    path = tmp_path / "tour.json"
    write(path, json.dumps(case("a stage with no line of its own")["payload"]))
    result = run(tmp_path, "--tour", str(path))
    assert result.returncode == 1
    assert "$.journeys[0].stages[0].words: missing" in result.stdout


def test_a_stage_under_another_journey_is_refused_by_the_rule(tmp_path: Path):
    """The schema accepts it: only the rule beside it sees the journey it is under."""
    path = tmp_path / "tour.json"
    write(path, json.dumps(case("a stage listed under a journey it does not name")["payload"]))
    result = run(tmp_path, "--tour", str(path))
    assert result.returncode == 1
    assert "$.journeys[0].stages[2].journey: is 'design', under the journey 'make'" in result.stdout


def test_a_feedback_document_is_read_from_a_file(tmp_path: Path):
    path = tmp_path / "feedback.json"
    write(path, json.dumps(case("a word kept before words carried a name")["payload"]))
    result = run(tmp_path, "--feedback", str(path))
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_schema_keyword_the_reader_does_not_check_is_refused(tmp_path: Path):
    """The schema is the one definition only while every keyword in it is checked."""
    schema = json.loads((SEED / "tour-schema.json").read_text(encoding="utf-8"))
    schema["$defs"]["journey"]["properties"]["stages"]["uniqueItems"] = True
    path = tmp_path / "schema.json"
    write(path, json.dumps(schema))
    result = run(tmp_path, "--vectors", "--schema", str(path))
    assert result.returncode == 2
    assert "uniqueItems, which this reader does not check" in result.stderr


def test_a_document_that_does_not_read_exits_two(tmp_path: Path):
    path = tmp_path / "tour.json"
    write(path, "{not json")
    result = run(tmp_path, "--tour", str(path))
    assert result.returncode == 2


def test_nothing_to_check_is_a_usage_error(tmp_path: Path):
    assert run(tmp_path).returncode == 2
