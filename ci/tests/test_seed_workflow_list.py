"""The seed workflows a fork copies are listed once, and the pages agree.

`project-seed/ci/seed-workflows.txt` is the list. The directory holds exactly
those workflows, each one's header says to copy it verbatim, and the pages that
tell a forker which to copy name every one. A workflow added to the seed without
a line in the list fails here, and so does a page that names fewer than the list.

What this does not check: that a page's description of a workflow is accurate,
or that a fork's `.github/workflows/` holds the copies; the local runner and the
workflows themselves do that.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED_CI = ROOT / "project-seed" / "ci"
KINDS = {"required", "copied"}
# Pages that name every workflow, and pages that point at the handbook instead.
NAMING = ("handbook/forking-a-project.md", "docs/usage/first-project.md")
POINTING = ("docs/usage/next-steps.md",)


def listed() -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in (SEED_CI / "seed-workflows.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, kind = line.split()
        assert kind in KINDS, f"{name}: {kind!r} is not one of {sorted(KINDS)}"
        entries[name] = kind
    return entries


def test_the_list_and_the_directory_hold_the_same_workflows():
    on_disk = {p.name for p in SEED_CI.glob("*.yml")}
    assert set(listed()) == on_disk, (
        f"listed only: {sorted(set(listed()) - on_disk)}; "
        f"on disk only: {sorted(on_disk - set(listed()))}"
    )


def test_each_listed_workflow_says_to_copy_it_verbatim():
    missing = [
        name
        for name in listed()
        if not re.search(r"copy\s+it\s+verbatim|copy\s+verbatim", (SEED_CI / name).read_text(encoding="utf-8")[:2000], re.I)
    ]
    assert not missing, f"header does not say to copy verbatim: {missing}"


def test_the_pages_that_say_which_to_copy_name_every_one():
    for page in NAMING:
        text = (ROOT / page).read_text(encoding="utf-8")
        absent = [name for name in listed() if name not in text]
        assert not absent, f"{page} does not name: {absent}"


def test_the_pages_that_point_at_the_handbook_carry_no_count_of_their_own():
    for page in POINTING:
        text = (ROOT / page).read_text(encoding="utf-8")
        assert "forking-a-project.md" in text, f"{page} does not point at the handbook"
        assert not re.search(r"\b(?:two|three|four|five|six|seven|eight|\d+)\s+(?:\[?seed\]?(?:\([^)]*\))?(?:\{[^}]*\})?\s+)?CI workflows", text, re.I), (
            f"{page} states a count of the seed workflows"
        )
