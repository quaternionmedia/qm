"""A roadmap's lines, against the pages a clone holds and the journeys an application serves.

The check reports and gates nothing, so its exit status says only whether it
could read; what it found is in what it prints. These run it as a project runs
it, out of the seed, on a clone laid out as a project's is: its walkthrough at
the root, its roadmap at governance/qm/project/ROADMAP.md.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from conftest import CI_DIR, run_tool, write

SEED = CI_DIR.parent
TOUR = json.loads((SEED / "tour-vectors.json").read_text(encoding="utf-8"))
ROADMAP_VECTORS = json.loads((SEED / "roadmap-vectors.json").read_text(encoding="utf-8"))

ROADMAP = """\
# Roadmap

## Making

- [x] Made and seen. `journey:make`
- [x] Cut on a machine nobody serves. `journey:cut`
- [x] Read whole. [01](../../../walkthrough/01-a-page.md)
- [ ] A page nobody wrote. [02](../../../walkthrough/02-no-such-page.md)
- [x] A link from the wrong place. [01](../walkthrough/01-a-page.md)
- [x] Claimed, and shown by nothing.
"""


def clone_with_roadmap(tmp_path: Path, roadmap: str = ROADMAP) -> Path:
    clone = tmp_path / "clone"
    write(clone / "walkthrough" / "01-a-page.md", "# 01 — A page\n")
    write(clone / "governance" / "qm" / "project" / "ROADMAP.md", roadmap)
    return clone


def tour_file(tmp_path: Path) -> Path:
    """A served tour document whose journeys are make, and design beside it."""
    payload = copy.deepcopy(next(c for c in TOUR["cases"]
                                 if c["name"] == "a journey with a word on two of its stages")["payload"])
    design = copy.deepcopy(payload["journeys"][0])
    design["id"], design["name"] = "design", "Design"
    for stage in design["stages"]:
        stage["journey"], stage["id"] = "design", f"design/{stage['stage']}"
    payload["journeys"].append(design)
    path = tmp_path / "tour.json"
    write(path, json.dumps(payload))
    return path


def run(tmp_path: Path, *args: str):
    return run_tool("check_roadmap.py", *args, cwd=tmp_path)


def test_every_roadmap_vector_is_read_as_it_declares(tmp_path: Path):
    result = run(tmp_path, "--vectors")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "every case read as declared" in result.stdout


def test_a_vector_read_otherwise_fails_the_run(tmp_path: Path):
    """Mutation: a declared reading the grammar does not give is reported, exit 1."""
    flipped = copy.deepcopy(ROADMAP_VECTORS)
    flipped["cases"][0]["lines"][0]["ticked"] = False
    path = tmp_path / "vectors.json"
    write(path, json.dumps(flipped))
    result = run(tmp_path, "--vectors", str(path))
    assert result.returncode == 1
    assert flipped["cases"][0]["name"] in result.stdout


def test_each_name_is_said_to_be_there_or_not(tmp_path: Path):
    clone = clone_with_roadmap(tmp_path)
    result = run(tmp_path, "--clone", str(clone), "--tour", str(tour_file(tmp_path)))
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "journey:make -- served" in out
    assert "journey:cut -- not served" in out
    assert "walkthrough/01-a-page.md -- found\n" in out
    assert "walkthrough/02-no-such-page.md -- not found" in out
    assert "walkthrough/01-a-page.md -- found, but the link does not reach it" in out
    assert "[x] Claimed, and shown by nothing. -- shown by nothing" in out
    assert "Shown by nothing: 1 line(s)" in out
    assert "Naming what is not there: 3 line(s)" in out
    assert "Journeys served that no line names: design" in out
    assert "reports and gates nothing" in out


def test_without_the_tour_no_journey_is_looked_up(tmp_path: Path):
    """Unknown is not empty: a journey not looked up is not reported as missing."""
    clone = clone_with_roadmap(tmp_path)
    result = run(tmp_path, "--clone", str(clone))
    assert result.returncode == 0, result.stderr
    assert "journey:cut -- not looked up" in result.stdout
    assert "Naming what is not there: 2 line(s)" in result.stdout
    assert "Journeys served" not in result.stdout


def test_what_was_found_is_data_under_json(tmp_path: Path):
    clone = clone_with_roadmap(tmp_path)
    result = run(tmp_path, "--clone", str(clone), "--tour", str(tour_file(tmp_path)), "--json")
    found = json.loads(result.stdout)
    assert found["shown_by_nothing"] == ["Claimed, and shown by nothing."]
    assert found["journeys_no_line_names"] == ["design"]
    assert [r["ticked"] for r in found["lines"]] == [True, True, True, False, True, True]


def test_a_roadmap_outside_the_clone_is_not_held_to_its_links(tmp_path: Path):
    """On the project's branch of the corpus the roadmap is not in the clone."""
    clone = clone_with_roadmap(tmp_path)
    outside = tmp_path / "corpus" / "project" / "ROADMAP.md"
    write(outside, ROADMAP)
    result = run(tmp_path, "--clone", str(clone), "--roadmap", str(outside))
    assert "does not reach" not in result.stdout


def test_no_roadmap_exits_two_and_names_where_it_looked(tmp_path: Path):
    clone = tmp_path / "clone"
    clone.mkdir()
    result = run(tmp_path, "--clone", str(clone))
    assert result.returncode == 2
    assert "governance/qm/project/ROADMAP.md" in result.stderr.replace("\\", "/")


def test_a_tour_that_is_not_the_shape_exits_two(tmp_path: Path):
    clone = clone_with_roadmap(tmp_path)
    path = tmp_path / "tour.json"
    write(path, json.dumps({"journeys": [{"id": "make"}]}))
    result = run(tmp_path, "--clone", str(clone), "--tour", str(path))
    assert result.returncode == 2
    assert "not the shape of a GET /tour document" in result.stderr
