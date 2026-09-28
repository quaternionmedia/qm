"""The upward half of propagation, which the projects were already writing.

`handbook/propagation-runbook.md` says `main` flows outward and org content on a
project branch is stranded *"if you find any"*. `ci/inbound.py` is the finding,
and it invents no new channel: every `Proposed` record already names what it
pends on, the ADR lint already enforces the row, and a good many of those rows
name the organisation.

**WHAT THIS SUITE IS REALLY ABOUT IS THE GROUPING.** A list of nineteen rows is
something a per-project reading already gives. The only thing this view adds is
that one org action unblocks many projects, and that is destroyed by two
failures which look like nothing: a `Pends on` opening with "Nothing" counted as
a dependency, and one shared ask split across the four ways this corpus spells a
dash.

THE MUTATIONS, per `a-check-is-evidence-after-it-fails`, quoted as they printed.

  cutting the shared ask on the em dash alone, as the first version did

    AssertionError: one ask, spelled with three different dashes, came out as
    4 groups
    assert 4 == 1

  a project with no records reported as having nothing to say

    AssertionError: a project whose records could not be read was reported as
    quiet
    assert [] == ['elsewhere']

  groups ordered by size ascending, so the cheapest org action sorts last

    assert 77 < 2

  `SETTLED` anchored neither by `^` nor by `.match`

    assert 0 == 1
     +  where 0 = len([])

**THE LAST ONE TOOK THREE ATTEMPTS AND THE FIRST TWO WERE INERT**, which is
worth more than the mutation itself. Removing `^` alone changes nothing,
because `.match()` anchors regardless; changing `.match` to `.search` alone
changes nothing, because the pattern still carries `^`. Each was run, each came
back green, and each would have been recorded here as a guard seen to fail. The
defence is doubled, and a mutation that only halves it proves nothing.

A fourth thing went wrong before that: the mutation script raised on a
mis-escaped anchor string and its traceback was filtered out by the `grep` that
was watching for assertion lines, so the run printed nothing and the nothing
read as a pass. The mutations are applied by matching on shape now, and the
script says out loud that it applied one.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import inbound  # noqa: E402

HEADER = """# ADR-XXXX — {title}

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-27 |
| **Pends on** | {pends} |

## Context

Body.
"""


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}:\n{done.stderr}")
    return done.stdout.strip()


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    repo = tmp_path / "qm"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("corpus\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    return repo


def add_project(repo: Path, name: str, records: dict[str, str] | None) -> None:
    """A `project/<name>` branch. `records=None` leaves `adr/` absent."""
    git(repo, "checkout", "-q", "-b", f"project/{name}", "main")
    if records is not None:
        adr = repo / "adr"
        adr.mkdir(exist_ok=True)
        (adr / "README.md").write_text("index\n", encoding="utf-8")
        (adr / "TEMPLATE.md").write_text("template\n", encoding="utf-8")
        for filename, pends in records.items():
            (adr / filename).write_text(
                HEADER.format(title=filename, pends=pends), encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", f"records for {name}")
    git(repo, "checkout", "-q", "main")


def survey(repo: Path):
    return inbound.survey(str(repo), "origin")


# --- the grouping, which is the whole point ---------------------------------

RATIFY = "Org-level ratification of the QM constitution records themselves"


def test_one_ask_spelled_with_different_dashes_is_one_group(corpus):
    """**THE ONE THIS VIEW EXISTS FOR.**

    Six projects pend on the same ratification and each wrote its own trailing
    detail after a dash. Cut on the em dash alone -- the first version of the
    key -- it came out as one group of four and three singletons, which reads
    as four problems and looks like nothing is wrong with the tool.
    """
    add_project(corpus, "alpha", {"a.md": f"{RATIFY} — detail for alpha."})
    add_project(corpus, "beta", {"b.md": f"{RATIFY} - detail for beta."})
    add_project(corpus, "gamma", {"c.md": f"{RATIFY} -- detail for gamma."})
    add_project(corpus, "delta", {"d.md": f"{RATIFY} (an aside for delta)."})

    found, _ = survey(corpus)
    groups = {row.key for row in found}

    assert len(groups) == 1, (
        f"one ask, spelled with three different dashes, came out as "
        f"{len(groups)} groups")
    assert len(found) == 4


def test_a_hyphenated_word_is_not_a_break(corpus):
    """`re`-splitting on a bare hyphen would cut "org-level" in half and put
    every project in its own group for the opposite reason."""
    add_project(corpus, "alpha", {"a.md": "Org-level ratification of X."})
    add_project(corpus, "beta", {"b.md": "Org-level ratification of X."})

    found, _ = survey(corpus)

    assert len({row.key for row in found}) == 1
    assert "org-level ratification of x" == found[0].key


def test_the_group_with_the_most_projects_is_rendered_first(corpus):
    """Ordered by what an answer would unblock. A view that sorted
    alphabetically would bury the cheapest thing the org can do."""
    add_project(corpus, "alpha", {"a.md": f"{RATIFY}."})
    add_project(corpus, "beta", {"b.md": f"{RATIFY}."})
    add_project(corpus, "gamma", {"c.md": "A question only gamma has."})

    found, silent = survey(corpus)
    text = inbound.render(found, silent)

    assert text.index("2 project(s)") < text.index("1 project(s)")


# --- what counts as waiting -------------------------------------------------


def test_a_record_pending_on_nothing_is_not_waiting(corpus):
    add_project(corpus, "alpha", {"a.md": "Nothing — ready for ratification."})

    found, _ = survey(corpus)

    assert found == []


def test_nothing_inside_a_sentence_does_not_settle_a_record(corpus):
    """`SETTLED` anchors at the start on purpose.

    "Nothing in the org has settled X" is a dependency, and a substring match
    would file it as answered -- the loudest possible way for this view to
    lose a question.
    """
    add_project(corpus, "alpha",
                {"a.md": "Whether the org has settled nothing here yet."})

    found, _ = survey(corpus)

    assert len(found) == 1


def test_the_index_and_the_template_are_not_records(corpus):
    add_project(corpus, "alpha", {"a.md": "A real question."})

    found, _ = survey(corpus)

    assert [row.record for row in found] == ["a.md"]


# --- the distinction between quiet and unreadable ---------------------------


def test_a_project_with_no_records_is_unknown_rather_than_quiet(corpus):
    """rad keeps `adr/` in its own repository and this cannot read it.

    Counting it as a project with nothing to say is this estate's most
    repeated mistake -- an empty query reported as a clean answer.
    """
    add_project(corpus, "alpha", {"a.md": "A real question."})
    add_project(corpus, "elsewhere", None)

    found, silent = survey(corpus)

    assert silent == ["elsewhere"], (
        "a project whose records could not be read was reported as quiet")
    assert [row.project for row in found] == ["alpha"]

    text = inbound.render(found, silent)
    assert "UNKNOWN rather than quiet" in text
    assert "elsewhere" in text


def test_an_estate_with_nothing_outstanding_says_so_rather_than_printing_nothing(
        corpus):
    add_project(corpus, "alpha", {"a.md": "Nothing — ready for ratification."})

    found, silent = survey(corpus)

    assert "No project record names an unsettled input" in inbound.render(
        found, silent)


def test_it_closes_nothing_and_says_so(corpus):
    """The row leaves when its author changes the record. A view that implied
    otherwise would invite somebody to 'clear' this list."""
    add_project(corpus, "alpha", {"a.md": "A real question."})

    found, silent = survey(corpus)

    assert "Nothing here closes anything" in inbound.render(found, silent)
