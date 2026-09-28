"""The voice check refuses a body that speaks to its contributor, and only that.

Each case here is a body that actually went out under a contributor's name on
2026-09-20, or the honest form it was rewritten to. The check is evidence only
because it has been seen to fail, four ways, each restored: `SECOND_PERSON`
narrowed to `yourself` alone turned five cases red; `HANDLING` emptied turned
five red; the login mention disabled turned one red; the fence handling
removed turned the code-block case red. A first attempt at the first mutation
edited nothing -- a shell escape ate the pattern -- and reported green; the
mutations run from a script file now.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_pr_voice as voice  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / "check_pr_voice.py"

# Verbatim from a pull request body that was posted, then rewritten.
LEAKED = (
    "Based on `project/codecartographer` at `9161c3f` -- this project's own records, never `main`. "
    "**Not to be merged without your click** -- assigned, no review requested.\n\n"
    "Two sentences in the records were wrong about the tree.\n"
)
REWRITTEN = (
    "Based on `project/codecartographer` at `9161c3f` -- this project's own records, never `main`.\n\n"
    "Two sentences in the records were wrong about the tree.\n"
)


def test_the_leaked_body_is_refused_and_the_rewritten_one_is_not():
    found = voice.offending_lines(LEAKED)
    assert found and found[0][0] == 1
    assert "second person" in found[0][1]
    assert voice.offending_lines(REWRITTEN) == []


@pytest.mark.parametrize("line", [
    "This is the one design decision in the PR worth your eye.",
    "Merges are yours.",
    "Assigned to you; no review requested.",
    "YOUR call on the two branches.",
    "Check yourself before merging.",
])
def test_every_second_person_form_is_refused(line):
    assert voice.offending_lines(line), line


@pytest.mark.parametrize("line", [
    "Not to be merged until the gates are green.",
    "Assigned, no review requested.",
    "Merge when ready.",
    "PTAL at the migration.",
    "Please review the seam contract.",
])
def test_the_handling_phrases_are_refused_without_a_pronoun(line):
    found = voice.offending_lines(line)
    assert found and "handling instruction" in found[0][1], line


def test_the_contributors_own_login_is_refused_when_given():
    assert voice.offending_lines("cc @subcontrabass for the merge", contributor="subcontrabass")
    assert voice.offending_lines("cc @subcontrabass for the merge") == []
    assert voice.offending_lines("cc @someone-else for a look", contributor="subcontrabass") == []


def test_code_and_quotes_are_left_alone():
    body = (
        "Run `git checkout -- yours.txt` to restore it.\n"
        "```\n"
        "echo your name here\n"
        "```\n"
        "> the reviewer wrote: your point stands\n"
        "The rest is a statement.\n"
    )
    assert voice.offending_lines(body) == []


def test_third_person_is_a_statement_and_passes():
    """The documented blind spot, pinned so it is not mistaken for coverage."""
    assert voice.offending_lines("The merge is a human act; the pull request is the audit record.") == []
    assert voice.offending_lines("Peter merges once the gates are green.") == []


def test_the_command_exits_nonzero_and_names_the_line(tmp_path):
    body = tmp_path / "body.md"
    body.write_text(LEAKED, encoding="utf-8")
    done = subprocess.run([sys.executable, str(SCRIPT), "--body-file", str(body),
                           "--contributor", "subcontrabass"],
                          capture_output=True, text=True)
    assert done.returncode == 1
    assert "line 1:" in done.stdout
    assert "second person" in done.stdout
    assert "belongs in the session" in done.stdout

    body.write_text(REWRITTEN, encoding="utf-8")
    done = subprocess.run([sys.executable, str(SCRIPT), "--body-file", str(body)],
                          capture_output=True, text=True)
    assert done.returncode == 0
    assert "addresses nobody" in done.stdout
