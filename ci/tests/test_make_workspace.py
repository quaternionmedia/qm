"""Tests for the workspace generator.

The generator's whole value is that its output can be trusted about a machine
it did not inspect closely. So every test here is about a way it could be
quietly wrong: a repository dropped rather than reported, a directory counted
as a clone, an absolute path baked into a file meant to be shared, a phase
nobody answered rendered as though somebody had.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

CI_DIR = Path(__file__).resolve().parent.parent
SCRIPT = CI_DIR / "make_workspace.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def roster(tmp_path: Path, repositories: list[dict]) -> Path:
    path = tmp_path / "workspace.yaml"
    path.write_text(
        yaml.safe_dump({"schema": 1, "repositories": repositories}), encoding="utf-8"
    )
    return path


def clone(root: Path, name: str) -> Path:
    """A directory that looks like a checked-out repository."""
    path = root / name
    (path / ".git").mkdir(parents=True)
    return path


def generate(tmp_path: Path, repositories: list[dict], *extra: str):
    search = tmp_path / "src"
    search.mkdir(exist_ok=True)
    out = tmp_path / "out" / "qm.code-workspace"
    result = run(
        "--roster",
        str(roster(tmp_path, repositories)),
        "--search-root",
        str(search),
        "--out",
        str(out),
        *extra,
    )
    return result, out, search


def test_a_resolved_repository_becomes_a_folder(tmp_path: Path) -> None:
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "alfred")
    result, out, _ = generate(tmp_path, [{"name": "alfred", "paths": ["alfred"]}])
    assert result.returncode == 0, result.stdout + result.stderr
    workspace = json.loads(out.read_text(encoding="utf-8"))
    assert [f["name"] for f in workspace["folders"]] == ["alfred"]


def test_a_missing_repository_is_reported_not_dropped(tmp_path: Path) -> None:
    """A roster silently missing entries reads exactly like a complete one."""
    result, out, _ = generate(tmp_path, [{"name": "ghost", "paths": ["ghost"]}])
    assert "MISSING" in result.stdout
    assert "ghost" in result.stdout
    page = out.with_suffix(".md").read_text(encoding="utf-8")
    assert "ghost" in page
    assert "Candidates tried" in page


def test_a_directory_without_git_is_not_a_clone(tmp_path: Path) -> None:
    """An empty folder someone made must not be presented as a repository."""
    search = tmp_path / "src"
    search.mkdir()
    (search / "alfred").mkdir()
    result, out, _ = generate(tmp_path, [{"name": "alfred", "paths": ["alfred"]}])
    assert "MISSING" in result.stdout
    assert json.loads(out.read_text(encoding="utf-8"))["folders"] == []


def test_the_first_resolvable_candidate_wins(tmp_path: Path) -> None:
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "second")
    result, out, _ = generate(
        tmp_path, [{"name": "thing", "paths": ["first", "second"]}]
    )
    assert result.returncode == 0, result.stdout + result.stderr
    folders = json.loads(out.read_text(encoding="utf-8"))["folders"]
    assert folders[0]["path"].endswith("second")


def test_paths_are_relative_and_posix(tmp_path: Path) -> None:
    """An absolute path makes the file untrue on the first machine it is shared with."""
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "alfred")
    _, out, _ = generate(tmp_path, [{"name": "alfred", "paths": ["alfred"]}])
    text = out.read_text(encoding="utf-8")
    path = json.loads(text)["folders"][0]["path"]
    assert not Path(path).is_absolute()
    assert "\\" not in path
    assert str(tmp_path) not in text


def test_a_repository_above_the_workspace_file_gets_a_relative_parent_path(
    tmp_path: Path,
) -> None:
    """Half these clones are not below the workspace file, and `..` must work."""
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "alfred")
    _, out, _ = generate(tmp_path, [{"name": "alfred", "paths": ["alfred"]}])
    assert json.loads(out.read_text(encoding="utf-8"))["folders"][0]["path"].startswith("..")


def test_an_unanswered_phase_is_collected_as_a_question(tmp_path: Path) -> None:
    """`unknown` is not a synonym for the bottom of the ladder."""
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "alfred")
    result, out, _ = generate(
        tmp_path, [{"name": "alfred", "phase": "unknown", "paths": ["alfred"]}]
    )
    assert "phase unknown" in result.stdout
    page = out.with_suffix(".md").read_text(encoding="utf-8")
    assert "Phases nobody has answered" in page
    assert "**alfred**" in page


def test_an_answered_phase_is_not_collected_as_a_question(tmp_path: Path) -> None:
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "rad")
    result, out, _ = generate(
        tmp_path, [{"name": "rad", "phase": "v0.0.1", "paths": ["rad"]}]
    )
    assert "phase unknown" not in result.stdout
    page = out.with_suffix(".md").read_text(encoding="utf-8")
    assert "every resolved repository carries a phase" in page


def test_a_missing_repository_is_not_asked_about_its_phase(tmp_path: Path) -> None:
    """A clone nobody has cannot be placed on a ladder, and asking implies it can."""
    result, out, _ = generate(
        tmp_path, [{"name": "ghost", "phase": "unknown", "paths": ["ghost"]}]
    )
    assert "phase unknown" not in result.stdout
    page = out.with_suffix(".md").read_text(encoding="utf-8")
    assert "**ghost**" not in page


def test_check_writes_nothing(tmp_path: Path) -> None:
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "alfred")
    result, out, _ = generate(tmp_path, [{"name": "alfred", "paths": ["alfred"]}], "--check")
    assert not out.exists()
    assert "nothing written" in result.stdout


def test_check_fails_when_a_repository_is_missing(tmp_path: Path) -> None:
    result, _, _ = generate(tmp_path, [{"name": "ghost", "paths": ["ghost"]}], "--check")
    assert result.returncode == 1


def test_check_passes_when_everything_resolves(tmp_path: Path) -> None:
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "alfred")
    result, _, _ = generate(tmp_path, [{"name": "alfred", "paths": ["alfred"]}], "--check")
    assert result.returncode == 0, result.stdout + result.stderr


def test_an_empty_roster_is_refused(tmp_path: Path) -> None:
    """Writing an empty workspace would look like success."""
    result, _, _ = generate(tmp_path, [])
    assert result.returncode != 0
    assert "lists no repositories" in (result.stdout + result.stderr)


def test_the_committed_roster_is_loadable_and_shaped(tmp_path: Path) -> None:
    """The real file, since nothing else reads it before a human runs this."""
    document = yaml.safe_load((CI_DIR / "workspace.yaml").read_text(encoding="utf-8"))
    repositories = document["repositories"]
    assert repositories, "the roster is empty"
    for entry in repositories:
        assert entry.get("name"), entry
        assert entry.get("paths"), entry
        assert entry.get("phase") is not None, entry
    corpus = [e for e in repositories if e.get("role") == "corpus"]
    assert len(corpus) == 1, "exactly one entry is the corpus"
