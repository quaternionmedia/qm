"""Tests for the org-wide tag audit.

Nothing here reaches a host. Every test feeds `judge_payload` (or the
`--from-json` route that wraps it) a captured payload, so the suite answers the
same way offline, in CI, and on a machine with no `gh` credential — and a test
can never pass because the org happens to be in the state it asserts.

The verdict itself is `check_annotation`'s, imported from the seed script. These
tests cover the sweep: what an empty namespace means, what an unreadable
repository must not be reported as, and which repositories come out ready.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from tag_audit import FAILING, NO_TAGS, READY, UNKNOWN, RepoResult, judge_payload, roster  # noqa: E402

TOOL = CI_DIR / "tag_audit.py"

GOOD = (
    "Reviewed-by: A Human\n"
    "Manually-tested: on the rig\n"
    "Automated-gate: 278 unit tests\n"
    "Not-covered: the flow layer\n"
)


def ref(name: str, kind: str, sha: str = "abc"):
    return {"ref": f"refs/tags/{name}", "object": {"type": kind, "sha": sha}}


def test_annotated_tag_with_every_field_is_ready():
    result = judge_payload("o/r", [ref("v1.0.0", "tag")], {"abc": GOOD})
    assert result.state == READY
    assert result.failing == []


def test_lightweight_tag_is_failing():
    assert judge_payload("o/r", [ref("v1.0.0", "commit")], {}).state == FAILING


def test_annotated_tag_missing_a_field_is_failing():
    body = GOOD.replace("Not-covered: the flow layer\n", "")
    result = judge_payload("o/r", [ref("v1.0.0", "tag")], {"abc": body})
    assert result.state == FAILING
    assert "Not-covered" in result.failing[0][2][0]


def test_empty_tag_namespace_is_no_tags_not_ready():
    """§4: a project that has never tagged has made no claim. That is a state.

    It must not read as READY, which would put an untagged repository on a
    demo list.
    """
    assert judge_payload("o/r", None, {}).state == NO_TAGS


def test_non_v_tags_are_not_this_records_business():
    result = judge_payload("o/r", [ref("nightly-2026-08-14", "commit")], {})
    assert result.state == NO_TAGS
    assert result.tags == []


def test_a_single_ref_is_not_dropped():
    """The API returns an object, not a list of one, when a repo has one tag."""
    result = judge_payload("o/r", ref("v1.0.0", "tag"), {"abc": GOOD})
    assert result.state == READY
    assert len(result.tags) == 1


def test_one_bad_tag_fails_the_repository():
    refs = [ref("v1.0.0", "tag", "a"), ref("v2.0.0", "commit", "b")]
    result = judge_payload("o/r", refs, {"a": GOOD})
    assert result.state == FAILING
    assert len(result.failing) == 1


def test_unknown_is_not_ready_and_not_no_tags():
    """A repository nobody could measure must never look clean."""
    result = RepoResult(repo="o/r", state=UNKNOWN, reason="403")
    assert result.state not in (READY, NO_TAGS)


# --- the sweep, through the CLI ------------------------------------------


def run(payload: dict, tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(TOOL), "--from-json", str(path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_report_names_only_ready_repositories_as_ready(tmp_path: Path):
    payload = {
        "o/good": {"refs": [ref("v1.0.0", "tag")], "bodies": {"abc": GOOD}},
        "o/bad": {"refs": [ref("v1.0.0", "commit")], "bodies": {}},
        "o/none": {"refs": None, "bodies": {}},
    }
    result = run(payload, tmp_path)
    assert result.returncode == 0
    ready_line = result.stdout.split("Ready to demo")[1].splitlines()[1]
    assert "o/good" in ready_line
    assert "o/bad" not in ready_line
    assert "o/none" not in ready_line


def test_strict_exits_non_zero_when_a_tag_fails(tmp_path: Path):
    payload = {"o/bad": {"refs": [ref("v1.0.0", "commit")], "bodies": {}}}
    assert run(payload, tmp_path, "--strict").returncode == 1


def test_strict_is_green_when_everything_carries_its_claims(tmp_path: Path):
    payload = {"o/good": {"refs": [ref("v1.0.0", "tag")], "bodies": {"abc": GOOD}}}
    assert run(payload, tmp_path, "--strict").returncode == 0


def test_no_tags_alone_does_not_fail_strict(tmp_path: Path):
    """Never tagging is not a violation, and §4 says so."""
    payload = {"o/none": {"refs": None, "bodies": {}}}
    assert run(payload, tmp_path, "--strict").returncode == 0


def test_passing_tags_are_hidden_until_verbose(tmp_path: Path):
    payload = {"o/good": {"refs": [ref("v1.0.0", "tag")], "bodies": {"abc": GOOD}}}
    assert "ok   v1.0.0" not in run(payload, tmp_path).stdout
    assert "ok   v1.0.0" in run(payload, tmp_path, "--verbose").stdout


# --- the roster ------------------------------------------------------------


def test_roster_reads_workspace_names(tmp_path: Path):
    workspace = tmp_path / "workspace.yaml"
    workspace.write_text(
        "repositories:\n"
        "  - name: qm\n"
        "    role: corpus\n"
        "  - name: alfred\n"
        "    role: project\n",
        encoding="utf-8",
    )
    assert roster(workspace, "org") == ["org/qm", "org/alfred"]


def test_roster_of_a_missing_file_is_empty_not_an_exception(tmp_path: Path):
    assert roster(tmp_path / "nope.yaml", "org") == []


def test_empty_roster_is_a_failure_not_a_vacuous_pass():
    """Auditing nothing and printing a clean report is the empty-glob failure."""
    result = subprocess.run(
        [sys.executable, str(TOOL), "--workspace", "does-not-exist.yaml"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 1
    assert "nothing was checked" in result.stderr
