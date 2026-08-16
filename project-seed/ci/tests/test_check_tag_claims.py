"""Tests for the version-tag claim check.

Every test names a state the check must call bad, or one it must call good, and
asserts the **exit status** rather than the wording — the exit status is the
contract, and a check that prints the right paragraph and returns 0 enforces
nothing.

Real tags in a real repository, per this directory's conftest. A mocked git
would encode whatever misunderstanding the tool has and then agree with it, and
the distinction this file turns on — a lightweight tag's `%(contents)` being the
*commit message* — is exactly the kind a mock erases.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import commit_all, git, run_tool, write

GOOD_ANNOTATION = (
    "Cut for the 0.1.0 release.\n"
    "\n"
    "Reviewed-by: A Human\n"
    "Manually-tested: flashed to the board, played four bars, verified tempo drift\n"
    "Automated-gate: 278 unit tests, deterministic, no skips\n"
    "Not-covered: the flow layer, which needs a container this runner has not got\n"
)


def tag_annotated(repo: Path, name: str, message: str) -> None:
    git(repo, "tag", "-a", name, "-m", message)


def tag_lightweight(repo: Path, name: str) -> None:
    git(repo, "tag", name)


def check(repo: Path, *args: str):
    return run_tool("check_tag_claims.py", *args, cwd=repo)


# --- the tag object itself -------------------------------------------------


def test_annotated_tag_with_every_field_passes(repo: Path):
    tag_annotated(repo, "v0.1.0", GOOD_ANNOTATION)
    result = check(repo, "--tag", "v0.1.0")
    assert result.returncode == 0, result.stdout + result.stderr


def test_lightweight_tag_fails(repo: Path):
    tag_lightweight(repo, "v0.1.0")
    result = check(repo, "--tag", "v0.1.0")
    assert result.returncode == 1
    assert "lightweight" in result.stdout


def test_lightweight_tag_whose_commit_message_carries_every_field_still_fails(repo: Path):
    """The route-around: satisfy the field check without an annotated tag.

    `git tag -l --format=%(contents)` on a lightweight tag returns the tagged
    *commit's* message. A field check that read the body before establishing the
    object type would pass this, and the tag would carry none of the claims
    because there is no tag object to carry them.
    """
    write(repo / "file.txt", "x\n")
    commit_all(repo, GOOD_ANNOTATION)
    tag_lightweight(repo, "v0.2.0")

    # The bait is real: the fields are genuinely readable from the commit.
    assert "Reviewed-by" in git(repo, "log", "-1", "--format=%B")

    result = check(repo, "--tag", "v0.2.0")
    assert result.returncode == 1
    assert "lightweight" in result.stdout


def test_missing_tag_fails(repo: Path):
    result = check(repo, "--tag", "v9.9.9")
    assert result.returncode == 1
    assert "no such tag" in result.stdout


# --- the name form ---------------------------------------------------------


@pytest.mark.parametrize("name", ["v0.1.0", "v1.2.3", "v0.2.0-rc.1", "v10.0.0-beta.2"])
def test_accepted_name_forms(repo: Path, name: str):
    tag_annotated(repo, name, GOOD_ANNOTATION)
    assert check(repo, "--tag", name).returncode == 0


@pytest.mark.parametrize("name", ["v1.0", "1.0.0", "release-1.0.0", "v01.0.0"])
def test_rejected_name_forms(repo: Path, name: str):
    tag_annotated(repo, name, GOOD_ANNOTATION)
    result = check(repo, "--tag", name)
    assert result.returncode == 1
    assert "vMAJOR.MINOR.PATCH" in result.stdout


# --- the annotation fields -------------------------------------------------


@pytest.mark.parametrize(
    "field", ["Reviewed-by", "Manually-tested", "Automated-gate", "Not-covered"]
)
def test_each_required_field_is_required(repo: Path, field: str):
    body = "\n".join(
        line for line in GOOD_ANNOTATION.splitlines() if not line.startswith(field + ":")
    )
    tag_annotated(repo, "v0.1.0", body)
    result = check(repo, "--tag", "v0.1.0")
    assert result.returncode == 1, f"{field} was droppable"
    assert field in result.stdout


def test_empty_field_value_is_absent_not_present(repo: Path):
    """`Not-covered:` with nothing after it states nothing, so it does not count."""
    body = GOOD_ANNOTATION.replace(
        "Not-covered: the flow layer, which needs a container this runner has not got",
        "Not-covered:   ",
    )
    tag_annotated(repo, "v0.1.0", body)
    result = check(repo, "--tag", "v0.1.0")
    assert result.returncode == 1
    assert "Not-covered" in result.stdout


def test_field_buried_in_prose_does_not_count(repo: Path):
    """A sentence containing a colon is prose, not a declaration.

    Otherwise "see the notes for what we Not-covered: nothing" satisfies a
    clause it never states.
    """
    body = GOOD_ANNOTATION.replace(
        "Not-covered: the flow layer, which needs a container this runner has not got",
        "We think Not-covered: nothing much, honestly",
    )
    tag_annotated(repo, "v0.1.0", body)
    assert check(repo, "--tag", "v0.1.0").returncode == 1


# --- the repository-wide audit ---------------------------------------------


def test_no_tags_is_not_a_failure(repo: Path):
    """§4: a project that has never tagged has made no claim. That is a state."""
    result = check(repo, "--all")
    assert result.returncode == 0
    assert "nothing claimed" in result.stdout


def test_all_fails_when_any_tag_fails(repo: Path):
    tag_annotated(repo, "v0.1.0", GOOD_ANNOTATION)
    tag_lightweight(repo, "v0.2.0")
    result = check(repo, "--all")
    assert result.returncode == 1
    assert "v0.1.0" in result.stdout and "v0.2.0" in result.stdout


def test_all_ignores_tags_outside_the_v_namespace(repo: Path):
    """A `nightly-2026-08-14` tag asserts nothing and is not this record's business."""
    tag_lightweight(repo, "nightly-2026-08-14")
    result = check(repo, "--all")
    assert result.returncode == 0


# --- the test-run gate -----------------------------------------------------


def test_clean_run_passes(repo: Path, tmp_path: Path):
    out = tmp_path / "run.txt"
    write(out, "278 passed in 8.33s\n")
    assert check(repo, "--test-output", str(out)).returncode == 0


@pytest.mark.parametrize(
    "summary",
    [
        "278 passed, 11 skipped in 8.33s",
        "278 passed, 2 rerun in 8.33s",
        "277 passed, 1 failed in 8.33s",
        "270 passed, 8 xfailed in 8.33s",
        "1 error in 0.10s",
    ],
)
def test_runs_that_announce_nondeterminism_fail(repo: Path, tmp_path: Path, summary: str):
    out = tmp_path / "run.txt"
    write(out, summary + "\n")
    assert check(repo, "--test-output", str(out)).returncode == 1


def test_absent_summary_is_not_a_pass(repo: Path, tmp_path: Path):
    """An empty capture is the classic false green: nothing ran, nothing failed."""
    out = tmp_path / "run.txt"
    write(out, "")
    result = check(repo, "--test-output", str(out))
    assert result.returncode == 1
    assert "no test summary" in result.stdout


def test_zero_passed_is_not_a_pass(repo: Path, tmp_path: Path):
    out = tmp_path / "run.txt"
    write(out, "no tests ran in 0.01s\n")
    assert check(repo, "--test-output", str(out)).returncode == 1


def test_last_summary_line_wins(repo: Path, tmp_path: Path):
    """Progress lines precede the totals; the totals are the result."""
    out = tmp_path / "run.txt"
    write(out, "collecting ...\n5 passed in 1.0s\n278 passed, 3 skipped in 8.33s\n")
    assert check(repo, "--test-output", str(out)).returncode == 1


# --- the entry point -------------------------------------------------------


def test_no_mode_given_is_an_error(repo: Path):
    result = check(repo)
    assert result.returncode != 0


def test_a_test_run_is_not_described_as_a_tag(repo: Path, tmp_path: Path):
    """`lightweight` is a property of a tag object; a captured run has none.

    Labelling one with the other is a fact from a different subject, printed
    with confidence -- the exact output this file refuses elsewhere.
    """
    out = tmp_path / "run.txt"
    write(out, "561 passed in 8.33s\n")
    result = check(repo, "--test-output", str(out))
    assert result.returncode == 0
    assert "lightweight" not in result.stdout
    assert "annotated" not in result.stdout
