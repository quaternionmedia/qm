"""One contract surface, one coordinate — or the surface says it disagrees.

`records/DRAFT-a-shared-tag-asserts-interoperability.md`: equal numbers assert
that these artifacts were proven to work together, and unequal ones assert
nothing about the pair. This is the check for the first half of that; the
second half — whether a repository that *claims* a version actually replayed
it — is not mechanised anywhere and the tool says so on every run.

The defect this exists against is measured rather than imagined: a publisher
governed `0.6.0` while a consumer replayed `0.4.0`, both were green, and no
artifact in the estate compared them.
"""

from __future__ import annotations

import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import interop  # noqa: E402


def surface(*versions: str) -> dict:
    """A read surface with one publisher and N implementations."""
    roles = ["publisher"] + ["implementation"] * (len(versions) - 1)
    return {
        "id": "a-surface",
        "claims": [
            {"repo": f"r{i}", "role": role, "version": v,
             "where": "f", "covers": "", "absent": False}
            for i, (role, v) in enumerate(zip(roles, versions))
        ],
    }


def test_one_coordinate_across_the_surface_is_clean():
    assert interop.problems(surface("0.6.0", "0.6.0", "0.6.0")) == []


def test_a_surface_that_disagrees_is_refused():
    """**THE DEFECT, AT THE SMALLEST SCALE THAT SHOWS IT.**

    Mutation: make `problems` return `[]` when the known versions differ and
    this fails.
    """
    found = interop.problems(surface("0.6.0", "0.4.0", "0.6.0"))
    assert found, "a surface with two versions reported clean"
    assert "disagrees" in found[0]
    assert "0.4.0" in found[0] and "0.6.0" in found[0]


def test_an_unreadable_claim_is_unknown_and_never_agreement():
    """`unknown` must not compare equal to anything. A default that read as
    agreement would make an unreadable file the quietest way to pass."""
    found = interop.problems(surface("0.6.0", interop.UNKNOWN))
    assert found, "an unknown version reported clean"
    assert "claims no version" in found[0]


def test_two_unknowns_do_not_agree_with_each_other():
    """The case a set-equality check gets wrong: `{unknown}` has one element."""
    found = interop.problems(surface(interop.UNKNOWN, interop.UNKNOWN))
    assert found, "two unknowns reported as agreement"


def test_a_missing_clone_says_so_rather_than_reporting_a_version():
    read = surface("0.6.0", interop.UNKNOWN)
    read["claims"][1]["absent"] = True
    found = interop.problems(read)
    assert any("no clone on this disk" in p for p in found)


def test_the_registry_registers_the_surface_this_estate_has():
    """A registry nobody added to is the state every registry check reports as
    clean, so the committed file is asserted rather than only its schema."""
    import yaml
    document = yaml.safe_load(interop.REGISTRY.read_text(encoding="utf-8"))
    surfaces = document["surfaces"]
    assert surfaces, "no surface registered"
    for entry in surfaces:
        assert entry.get("publisher"), f"{entry['id']} has no publisher"
        assert entry.get("implementations"), f"{entry['id']} has no implementation"
        assert entry.get("cannot_see"), f"{entry['id']} states no blind spot"


# --- --verify: the counts come from runs, not from declared strings ----------


def test_a_host_that_cannot_be_launched_is_reported_not_counted(tmp_path):
    """**THE FAILURE THAT READ AS A MISSING REPOSITORY.**

    On Windows `npm` is `npm.cmd`, and `subprocess` without a shell finds
    neither -- it reports "the system cannot find the file specified", which
    looks like an absent clone rather than an absent shim. Resolving the
    launcher on PATH is the fix; `shell=True` would have worked and would hand
    a registry string to a shell.

    Mutation: drop the `shutil.which` guard and this reports a launch error
    instead of naming the missing launcher.
    """
    spec = {"repo": "nowhere", "file": "f",
            "proves": {"cwd": ".", "command": ["definitely-not-a-real-launcher"]}}
    out = interop.prove({"id": "s"}, spec, [tmp_path])
    assert out["ran"] is False
    assert "no clone on this disk" in out["why"] or "not on PATH" in out["why"]


def test_an_implementation_with_no_proving_command_says_so(tmp_path):
    (tmp_path / "here" / ".git").mkdir(parents=True)
    spec = {"repo": "here", "file": "f"}
    out = interop.prove({"id": "s"}, spec, [tmp_path])
    assert out["ran"] is False
    assert "declares no proving command" in out["why"]


def test_a_run_that_prints_no_coverage_line_is_not_counted(tmp_path, monkeypatch):
    """A host that ran and said nothing readable must not contribute zero
    silently -- zero would sum cleanly with everything."""
    (tmp_path / "here" / ".git").mkdir(parents=True)

    class Done:
        returncode = 0
        stdout = "ran, said nothing this surface can read"
        stderr = ""

    monkeypatch.setattr(interop.shutil, "which", lambda _: "launcher")
    monkeypatch.setattr(interop.subprocess, "run", lambda *a, **k: Done())
    spec = {"repo": "here", "file": "f",
            "proves": {"cwd": ".", "command": ["x"]}}
    out = interop.prove({"id": "s", "coverage": "covered (?P<applicable>[0-9]+) of (?P<not_applicable>[0-9]+)"},
                        spec, [tmp_path])
    assert out["ran"] is True
    assert out["applicable"] is None
    assert "no coverage line" in out["why"]


def test_the_coverage_line_is_read_from_the_run(tmp_path, monkeypatch):
    (tmp_path / "here" / ".git").mkdir(parents=True)

    class Done:
        returncode = 0
        stdout = "rad conformance: 47 applicable, all passing; 11 not applicable to this port"
        stderr = ""

    monkeypatch.setattr(interop.shutil, "which", lambda _: "launcher")
    monkeypatch.setattr(interop.subprocess, "run", lambda *a, **k: Done())
    spec = {"repo": "here", "file": "f",
            "proves": {"cwd": ".", "command": ["x"]}}
    surface = {"id": "s", "coverage":
               "rad conformance: (?P<applicable>[0-9]+) applicable, all passing; (?P<not_applicable>[0-9]+) not applicable"}
    out = interop.prove(surface, spec, [tmp_path])
    assert out["passed"] is True
    assert out["applicable"] == 47 and out["not_applicable"] == 11


def test_the_registry_declares_how_each_implementation_proves_itself():
    """A surface whose implementations declare no command can only ever be
    checked by declared string, which is the weaker half of this tool."""
    import yaml
    document = yaml.safe_load(interop.REGISTRY.read_text(encoding="utf-8"))
    for surface in document["surfaces"]:
        assert surface.get("coverage"), f"{surface['id']} declares no coverage marker"
        for impl in surface["implementations"]:
            assert impl.get("proves", {}).get("command"), (
                f"{surface['id']}: {impl['repo']} declares no proving command")
