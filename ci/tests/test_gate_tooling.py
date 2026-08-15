"""Tests for the gate status document and its views.

The separation is the design, so the first test is the one that guards it: a
renderer that can shell out is a second place a governance rule gets defined,
and two definitions drift. The same assertion governs `harness_dashboard.py`
and `governance_render.py`.

Everything else is fed a registry and a workflows directory built here, so no
test passes because this repository happens to be in the state it asserts.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from gate_status import build, discover, gate_row, local_layers, unknown  # noqa: E402

STATUS = CI_DIR / "gate_status.py"
DASHBOARD = CI_DIR / "gate_dashboard.py"

WORKFLOW = """name: {name}
on:
  pull_request:
jobs:
  {job}:
    runs-on: ubuntu-latest
    steps: []
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def registry(tmp_path: Path, *entries: str) -> Path:
    path = tmp_path / "gate-registry.yaml"
    write(path, "schema: 1\ngates:\n" + "".join(entries))
    return path


def entry(gate_id: str, workflow: str | None, job: str | None, exists: bool = True,
          external: bool = False) -> str:
    # The registry names a workflow by filename, which is how `discover` keys
    # what it found. An entry naming `wf` where the file is `wf.yml` reports as
    # missing -- three tests here failed that way before this line said `.yml`,
    # and the failure looked like three defects rather than one fixture bug.
    return (
        f"  - id: {gate_id}\n"
        f"    workflow: {workflow + '.yml' if workflow else 'null'}\n"
        f"    job: {job or 'null'}\n"
        f"    gates: [main]\n"
        f"    seed: false\n"
        f"    exists: {str(exists).lower()}\n"
        f"    external: {str(external).lower()}\n"
        f"    refuses: A thing.\n"
        f"    cannot_see: Another thing.\n"
    )


def workflows_dir(tmp_path: Path, **files: str) -> Path:
    path = tmp_path / "workflows"
    path.mkdir(parents=True, exist_ok=True)
    for name, job in files.items():
        write(path / f"{name}.yml", WORKFLOW.format(name=name, job=job))
    return path


def run(tool: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(tool), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


# --- the separation ---------------------------------------------------------


def test_the_renderer_cannot_run_a_command():
    """A view that shells out is a second definition of a governance rule.

    Asserted on the source text, because the failure is the import existing at
    all -- a renderer that could shell out would drift from its generator the
    first time either was fixed.
    """
    source = DASHBOARD.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "import os" not in source


def test_the_renderer_does_not_write_to_its_document(tmp_path: Path):
    reg = registry(tmp_path, entry("a", "wf", "job"))
    wfs = workflows_dir(tmp_path, wf="job")
    doc_path = tmp_path / "gate-status.json"
    assert run(STATUS, "--no-host", "--registry", str(reg), "--workflows", str(wfs),
               "--write", str(doc_path)).returncode == 0
    before = doc_path.read_bytes()
    assert run(DASHBOARD, str(doc_path), "--format", "md").returncode == 0
    assert doc_path.read_bytes() == before


# --- the claim/evidence split ----------------------------------------------


def test_a_declared_workflow_that_is_missing_warns(tmp_path: Path):
    reg = registry(tmp_path, entry("a", "gone", "job"))
    doc = build(reg, workflows_dir(tmp_path), "o/r", host=False)
    assert doc["gates"][0]["state"] == "warn"
    assert "not in the workflows directory" in doc["gates"][0]["evidence"]["unknown"]


def test_a_renamed_job_warns(tmp_path: Path):
    """Identical content under a different job id is a check nobody is watching."""
    reg = registry(tmp_path, entry("a", "wf", "job"))
    wfs = workflows_dir(tmp_path, wf="renamed")
    doc = build(reg, wfs, "o/r", host=False)
    assert doc["gates"][0]["state"] == "warn"
    assert doc["gates"][0]["evidence"]["job_declared"] is False


def test_a_workflow_nobody_declared_is_named_not_adopted(tmp_path: Path):
    """Inferring the claim from the artifact would redefine governance as a
    filename check. The workflow is reported, never added to the list."""
    reg = registry(tmp_path, entry("a", "wf", "job"))
    wfs = workflows_dir(tmp_path, wf="job", sneaky="sneak")
    doc = build(reg, wfs, "o/r", host=False)
    assert doc["undeclared_workflows"] == ["sneaky.yml"]
    assert [g["id"] for g in doc["gates"]] == ["a"]


def test_a_declared_and_unbuilt_gate_is_kept_and_warns(tmp_path: Path):
    """Dropping it to make a page green is the one edit the registry forbids."""
    reg = registry(tmp_path, entry("later", None, None, exists=False))
    doc = build(reg, workflows_dir(tmp_path), "o/r", host=False)
    assert doc["totals"]["declared_not_built"] == 1
    assert doc["gates"][0]["state"] == "warn"


def test_an_external_check_is_unknown_not_ok(tmp_path: Path):
    """An installed app has no workflow to read; `ok` would assert what nobody checked."""
    reg = registry(tmp_path, entry("scanner", None, "Some App", external=True))
    doc = build(reg, workflows_dir(tmp_path), "o/r", host=False)
    assert doc["gates"][0]["state"] == "unknown"


def test_an_unparseable_workflow_is_unknown_not_missing(tmp_path: Path):
    """Cannot-read and is-not-there are different facts and must not collapse."""
    reg = registry(tmp_path, entry("a", "broken", "job"))
    wfs = workflows_dir(tmp_path)
    write(wfs / "broken.yml", "name: [unclosed\n")
    doc = build(reg, wfs, "o/r", host=False)
    assert doc["gates"][0]["state"] == "unknown"
    assert "did not parse" in doc["gates"][0]["evidence"]["unknown"]


def test_an_empty_registry_is_refused_not_rendered_clean(tmp_path: Path):
    reg = tmp_path / "empty.yaml"
    write(reg, "schema: 1\ngates: []\n")
    with pytest.raises(SystemExit):
        build(reg, workflows_dir(tmp_path), "o/r", host=False)


def test_a_gate_with_no_cannot_see_is_a_gap_not_a_clean_bill(tmp_path: Path):
    doc = build(
        registry(tmp_path, "  - id: a\n    workflow: null\n    exists: false\n"),
        workflows_dir(tmp_path), "o/r", host=False,
    )
    assert "unknown" in doc["gates"][0]["cannot_see"]


# --- the faithfulness check -------------------------------------------------


def test_check_passes_on_a_fresh_document(tmp_path: Path):
    reg = registry(tmp_path, entry("a", "wf", "job"))
    wfs = workflows_dir(tmp_path, wf="job")
    doc_path = tmp_path / "gate-status.json"
    run(STATUS, "--no-host", "--registry", str(reg), "--workflows", str(wfs),
        "--write", str(doc_path))
    assert run(STATUS, "--registry", str(reg), "--workflows", str(wfs),
               "--check", str(doc_path)).returncode == 0


def test_check_fails_when_the_registry_moves_on(tmp_path: Path):
    reg = registry(tmp_path, entry("a", "wf", "job"))
    wfs = workflows_dir(tmp_path, wf="job")
    doc_path = tmp_path / "gate-status.json"
    run(STATUS, "--no-host", "--registry", str(reg), "--workflows", str(wfs),
        "--write", str(doc_path))
    registry(tmp_path, entry("a", "wf", "job"), entry("b", "wf2", "job2"))
    assert run(STATUS, "--registry", str(reg), "--workflows", str(wfs),
               "--check", str(doc_path)).returncode == 1


def test_check_ignores_the_host_layer(tmp_path: Path):
    """The enforcement layer changes with no commit here.

    If `--check` compared it, every pull request would go red the moment
    somebody added a ruleset -- for a reason its author cannot fix.
    """
    reg = registry(tmp_path, entry("a", "wf", "job"))
    wfs = workflows_dir(tmp_path, wf="job")
    doc_path = tmp_path / "gate-status.json"
    run(STATUS, "--no-host", "--registry", str(reg), "--workflows", str(wfs),
        "--write", str(doc_path))

    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    doc["enforcement"] = {"repository": "o/r", "rulesets_applied": 9,
                          "blocks_a_merge": True}
    doc["generated_at"] = "1999-01-01T00:00:00Z"
    doc_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")

    assert run(STATUS, "--registry", str(reg), "--workflows", str(wfs),
               "--check", str(doc_path)).returncode == 0


# --- the view ---------------------------------------------------------------


def render(tmp_path: Path, doc: dict) -> str:
    path = tmp_path / "doc.json"
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
    result = run(DASHBOARD, str(path), "--format", "md")
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_an_unknown_enforcement_layer_does_not_render_as_advisory(tmp_path: Path):
    """`nobody asked` must not read as `nothing blocks a merge`."""
    reg = registry(tmp_path, entry("a", "wf", "job"))
    doc = build(reg, workflows_dir(tmp_path, wf="job"), "o/r", host=False)
    text = render(tmp_path, doc)
    assert "unknown" in text
    assert "Nothing blocks a merge" not in text


def test_an_unenforced_boundary_says_advisory_in_the_page(tmp_path: Path):
    reg = registry(tmp_path, entry("a", "wf", "job"))
    doc = build(reg, workflows_dir(tmp_path, wf="job"), "o/r", host=False)
    doc["enforcement"] = {"repository": "o/r", "rulesets_applied": 0,
                          "ruleset_names": [], "branch_protection_on_main": False,
                          "blocks_a_merge": False}
    text = render(tmp_path, doc)
    assert "Nothing blocks a merge" in text
    assert "advisory" in text


def test_the_generation_time_is_at_the_top(tmp_path: Path):
    """A dashboard that looks live and is three days old stops people checking."""
    reg = registry(tmp_path, entry("a", "wf", "job"))
    doc = build(reg, workflows_dir(tmp_path, wf="job"), "o/r", host=False)
    head = render(tmp_path, doc).splitlines()[:4]
    assert any(doc["generated_at"] in line for line in head)


def test_an_unknown_is_never_rendered_as_a_tick(tmp_path: Path):
    reg = registry(tmp_path, entry("scanner", None, "App", external=True))
    doc = build(reg, workflows_dir(tmp_path), "o/r", host=False)
    text = render(tmp_path, doc)
    assert "[??]" in text
    assert "[ok] | `scanner`" not in text


def test_state_is_carried_in_form_not_only_colour(tmp_path: Path):
    """The markdown view has no colour at all, so the mark is the whole signal."""
    reg = registry(tmp_path, entry("a", "gone", "job"))
    doc = build(reg, workflows_dir(tmp_path), "o/r", host=False)
    assert "[!!]" in render(tmp_path, doc)


def test_local_layers_excludes_what_changes_off_repo():
    sample = {"schema": 1, "generated_at": "x", "enforcement": {"a": 1},
              "generator": {}, "reading": {}, "totals": {}, "gates": [],
              "undeclared_workflows": []}
    layers = local_layers(sample)
    assert "enforcement" not in layers
    assert "generated_at" not in layers


def test_unknown_has_one_spelling():
    assert unknown("why") == {"unknown": "why"}
    assert len(unknown("why")) == 1
