"""The onboarding pages are generated, and they refuse to flatter.

An onboarding page is read by the person least able to notice it is wrong.
So these assert the two things a newcomer would be misled by: a page that
invents a governed entry point where there is none, and a page whose figures
have drifted from the disk it claims to describe.
"""

from __future__ import annotations

import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import cookbook  # noqa: E402


def family(name="a-family", drives="the thing", members=("one", "two")):
    return {"name": name, "drives": drives, "members": list(members)}


def state(name, adopted=False, on_disk=True, dirty=0, branch="main", last="2026-01-01"):
    return {"name": name, "on_disk": on_disk, "branch": branch,
            "dirty": dirty, "last": last, "adopted": adopted}


def test_a_family_with_no_governed_member_gets_no_entry_point():
    """**THE FLATTERING PAGE THIS EXISTS AGAINST.**

    Three of four families have no adopted member. A page that offered a
    governed entry point anyway would send a newcomer to run a command that
    does not exist there.

    Mutation: make `page` emit the governed branch unconditionally and this
    fails.
    """
    text = cookbook.page(family(), [state("one"), state("two")], "2026-01-01")
    assert "No member of this family carries governance yet" in text
    assert "uv run qm cowork" not in text


def test_a_family_with_a_governed_member_names_one():
    text = cookbook.page(family(), [state("one", adopted=True), state("two")], "2026-01-01")
    assert "1 of 2 members carry governance" in text
    assert "cd one" in text


def test_the_corpus_is_the_entry_point_for_its_own_family():
    """Reading only `project/*` branches printed the corpus as ungoverned and
    sent a reader to the next repository listed."""
    text = cookbook.page(
        family(members=("dossier", "qm")),
        [state("dossier", adopted=True), state("qm", adopted=True)],
        "2026-01-01")
    assert "cd qm" in text


def test_the_committed_page_carries_no_machine_scoped_state():
    """**THE DESIGN FAULT THIS PAGE WAS BORN WITH.**

    The first version put the branch, the uncommitted count and the last commit
    date into a *committed* document. Those differ per machine and change on
    every keystroke, so `qm docs check` reported drift the moment anybody edited
    a file -- and a check that fails hourly is one people learn to rerun rather
    than read. `inventory-public.json` and `inventory-local.json` already make
    this split; the page had to make it too.

    Mutation: put `state['branch']` or `state['dirty']` back into `page` and
    this fails.
    """
    text = cookbook.page(
        family(), [state("one", branch="feat/x", dirty=7, last="2026-05-05")],
        "2026-01-01")
    assert "feat/x" not in text
    assert "2026-05-05" not in text
    assert "7" not in text.replace("2026-01-01", "")


def test_the_page_says_what_it_deliberately_omits():
    """An omission a reader cannot see is indistinguishable from an oversight."""
    text = cookbook.page(family(), [state("one")], "2026-01-01")
    assert "machine-scoped" in text
    assert "uv run qm cookbook" in text


def test_the_page_carries_only_the_claim_that_does_not_move():
    text = cookbook.page(family(), [state("one", adopted=True), state("two")], "2026-01-01")
    assert "| member | governed |" in text
    assert "| `one` | yes |" in text
    assert "| `two` | no |" in text


def test_the_generated_stamp_is_not_what_the_check_compares():
    """A check that failed daily on a date nobody reads is one people learn to
    rerun rather than read."""
    a = cookbook._without_stamp("body\n*Generated 2026-01-01.*\n")
    b = cookbook._without_stamp("body\n*Generated 2026-12-31.*\n")
    assert a == b


def test_the_picture_is_drawn_from_the_same_states_as_the_prose():
    """Drawn, not pasted -- and from the same facts the prose uses, so the two
    cannot disagree. It carries governance and nothing machine-scoped, for the
    same reason the table does."""
    picture = cookbook.svg("a-family", [state("one", adopted=True), state("two", dirty=3)])
    assert "<svg" in picture and "a-family" in picture
    assert "one" in picture and "two" in picture
    assert "governed" in picture and "not adopted" in picture
    assert "3 dirty" not in picture
