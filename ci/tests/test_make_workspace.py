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
        tmp_path, [{"name": "alfred", "phase": "v0.0.1", "phase_source": "scaffolded", "paths": ["alfred"]}]
    )
    assert "phase scaffolded" in result.stdout
    page = out.with_suffix(".md").read_text(encoding="utf-8")
    assert "Phases nobody has stated" in page
    assert "**alfred**" in page


def test_an_answered_phase_is_not_collected_as_a_question(tmp_path: Path) -> None:
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "rad")
    result, out, _ = generate(
        tmp_path, [{"name": "rad", "phase": "v0.0.1", "phase_source": "stated", "paths": ["rad"]}]
    )
    assert "phase scaffolded" not in result.stdout
    page = out.with_suffix(".md").read_text(encoding="utf-8")
    assert "has a phase somebody stated" in page


def test_a_missing_repository_is_not_asked_about_its_phase(tmp_path: Path) -> None:
    """A clone nobody has cannot be placed on a ladder, and asking implies it can."""
    result, out, _ = generate(
        tmp_path, [{"name": "ghost", "phase": "v0.0.1", "phase_source": "scaffolded", "paths": ["ghost"]}]
    )
    assert "phase scaffolded" not in result.stdout
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
    """The real file, since nothing else reads it before a human runs this.

    A private entry carries a `ref` and neither a name nor paths -- both would
    publish the repository's name, a path being a directory name. `name` and
    `paths` are therefore asserted on the *loaded* roster, which merges the
    uncommitted companion when it is there and falls back to the ref when it is
    not. See ci/roster.py.
    """
    document = yaml.safe_load((CI_DIR / "workspace.yaml").read_text(encoding="utf-8"))
    repositories = document["repositories"]
    assert repositories, "the roster is empty"
    for entry in repositories:
        assert entry.get("name") or entry.get("ref"), entry
        if entry.get("ref") and not entry.get("name"):
            assert not entry.get("paths"), f"{entry['ref']} carries a path, which is a name"
        else:
            assert entry.get("paths"), entry
        assert entry.get("phase") is not None, entry
        assert entry.get("phase_source") in ("stated", "scaffolded", "n/a"), entry
    corpus = [e for e in repositories if e.get("role") == "corpus"]
    assert len(corpus) == 1, "exactly one entry is the corpus"


# --- a workspace for one family, or several --------------------------------
#
# `--family` is checked against the seam file rather than the roster, so every
# test here writes one. Nothing below passes the corpus's real families.json:
# these tests are about the generator's refusals, and a real file would make
# each one depend on which families the record happens to declare today.


def families_file(tmp_path: Path, names: list[str]) -> Path:
    path = tmp_path / "families.json"
    path.write_text(
        json.dumps({"schema": 1, "families": [{"name": n, "drives": "", "members": []} for n in names]}),
        encoding="utf-8",
    )
    return path


def test_a_family_selection_keeps_only_that_familys_members(tmp_path: Path) -> None:
    """Mutation: drop the `e.get("family") in wanted` filter in
    `select_families` and this fails on `other`."""
    search = tmp_path / "src"
    search.mkdir()
    for name in ("hub", "other"):
        clone(search, name)
    result, out, _ = generate(
        tmp_path,
        [
            {"name": "hub", "family": "room", "paths": ["hub"]},
            {"name": "other", "family": "sound", "paths": ["other"]},
        ],
        "--family", "room", "--families", str(families_file(tmp_path, ["room", "sound"])),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    workspace = json.loads(out.read_text(encoding="utf-8"))
    assert [f["name"] for f in workspace["folders"]] == ["hub"]


def test_several_families_are_one_workspace(tmp_path: Path) -> None:
    search = tmp_path / "src"
    search.mkdir()
    for name in ("hub", "other"):
        clone(search, name)
    result, out, _ = generate(
        tmp_path,
        [
            {"name": "hub", "family": "room", "paths": ["hub"]},
            {"name": "other", "family": "sound", "paths": ["other"]},
        ],
        "--family", "room", "--family", "sound",
        "--families", str(families_file(tmp_path, ["room", "sound"])),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    workspace = json.loads(out.read_text(encoding="utf-8"))
    assert [f["name"] for f in workspace["folders"]] == ["hub", "other"]


def test_an_unstated_entry_is_never_in_a_family_selection(tmp_path: Path) -> None:
    """Nobody said which system it is part of, and a workspace that included
    it would have answered for them. Mutation: make the filter
    `e.get("family") in wanted or not e.get("family")` and this fails."""
    search = tmp_path / "src"
    search.mkdir()
    for name in ("hub", "nobody-placed"):
        clone(search, name)
    result, out, _ = generate(
        tmp_path,
        [
            {"name": "hub", "family": "room", "paths": ["hub"]},
            {"name": "nobody-placed", "paths": ["nobody-placed"]},
        ],
        "--family", "room", "--families", str(families_file(tmp_path, ["room"])),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    workspace = json.loads(out.read_text(encoding="utf-8"))
    assert [f["name"] for f in workspace["folders"]] == ["hub"]


def test_a_family_nobody_declared_is_refused(tmp_path: Path) -> None:
    """A misspelt family matched against the roster finds nothing, and an
    empty workspace looks exactly like a family with no clones here.
    Mutation: drop the `unknown` check in `select_families` and this passes
    a workspace with no folders."""
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "hub")
    result, out, _ = generate(
        tmp_path,
        [{"name": "hub", "family": "room", "paths": ["hub"]}],
        "--family", "rom", "--families", str(families_file(tmp_path, ["room"])),
    )
    assert result.returncode != 0
    assert "rom" in result.stderr
    assert "room" in result.stderr, "the refusal names what is declared"
    assert not out.exists()


def test_a_family_selection_needs_a_seam_file_to_check_against(tmp_path: Path) -> None:
    """With nothing declared every name is equally unknown. Mutation: drop
    the `if not declared` branch and a missing seam file refuses the name
    instead of naming the file."""
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "hub")
    result, out, _ = generate(
        tmp_path,
        [{"name": "hub", "family": "room", "paths": ["hub"]}],
        "--family", "room", "--families", str(tmp_path / "absent.json"),
    )
    assert result.returncode != 0
    assert "absent.json" in result.stderr
    assert "qm families --write" in result.stderr
    assert not out.exists()


def test_a_declared_family_no_entry_claims_is_refused(tmp_path: Path) -> None:
    """The record can declare a family before anybody has placed a
    repository in it. A workspace of it would be an empty folder list with a
    heading, which reads as a family none of whose members is cloned here."""
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "hub")
    result, out, _ = generate(
        tmp_path,
        [{"name": "hub", "family": "room", "paths": ["hub"]}],
        "--family", "sound", "--families", str(families_file(tmp_path, ["room", "sound"])),
    )
    assert result.returncode != 0
    assert "sound" in result.stderr
    assert not out.exists()


def test_the_companion_page_counts_each_family_rostered_and_on_this_machine(
    tmp_path: Path,
) -> None:
    """A family whose every member is missing is otherwise a heading with
    nothing under it. Mutation: count `members` instead of `here` in the
    families table and the second row reads 1, 1."""
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "hub")
    _, out, _ = generate(
        tmp_path,
        [
            {"name": "hub", "family": "room", "paths": ["hub"]},
            {"name": "ghost", "family": "sound", "paths": ["ghost"]},
        ],
        "--family", "room", "--family", "sound",
        "--families", str(families_file(tmp_path, ["room", "sound"])),
    )
    page = out.with_suffix(".md").read_text(encoding="utf-8")
    assert "## Which families this is" in page
    assert "| `room` | 1 | 1 |" in page
    assert "| `sound` | 1 | 0 |" in page
    assert "| ghost |" in page, "missing is still reported, not dropped"


def test_the_page_carries_a_family_column_and_unstated_is_the_word(tmp_path: Path) -> None:
    """The word, not a blank: `status/harness.yaml` renders the same column
    and a blank cell there would read as `none`."""
    search = tmp_path / "src"
    search.mkdir()
    for name in ("hub", "nobody-placed"):
        clone(search, name)
    _, out, _ = generate(
        tmp_path,
        [
            {"name": "hub", "family": "room", "paths": ["hub"]},
            {"name": "nobody-placed", "paths": ["nobody-placed"]},
        ],
    )
    page = out.with_suffix(".md").read_text(encoding="utf-8")
    assert "| hub | room |" in page
    assert "| nobody-placed | unstated |" in page
    assert "## Which families this is" not in page, "no selection, no section"


def test_a_narrowed_workspace_gets_its_own_file_name(tmp_path: Path) -> None:
    """Asking for one family must never overwrite the whole-roster workspace
    beside it. `--check` prints the target and writes nothing, so the default
    name can be read without writing into the real repositories directory."""
    search = tmp_path / "src"
    search.mkdir()
    clone(search, "hub")
    result = run(
        "--roster", str(roster(tmp_path, [{"name": "hub", "family": "room", "paths": ["hub"]}])),
        "--search-root", str(search),
        "--families", str(families_file(tmp_path, ["room"])),
        "--family", "room",
        "--check",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "quaternion-media-room.code-workspace" in result.stdout
    assert "nothing written" in result.stdout


def test_folders_are_grouped_by_the_families_as_asked_for(tmp_path: Path) -> None:
    """One system's members sit together in the folder list. Mutation: make
    `select_families` a single roster-order comprehension and `other`, first
    in the roster, comes out first."""
    search = tmp_path / "src"
    search.mkdir()
    for name in ("hub", "other", "second-hub"):
        clone(search, name)
    result, out, _ = generate(
        tmp_path,
        [
            {"name": "other", "family": "sound", "paths": ["other"]},
            {"name": "hub", "family": "room", "paths": ["hub"]},
            {"name": "second-hub", "family": "room", "paths": ["second-hub"]},
        ],
        "--family", "room", "--family", "sound",
        "--families", str(families_file(tmp_path, ["room", "sound"])),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    workspace = json.loads(out.read_text(encoding="utf-8"))
    assert [f["name"] for f in workspace["folders"]] == ["hub", "second-hub", "other"]
