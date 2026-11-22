"""What a branch census must tell apart before anybody deletes anything.

Real repositories with a real remote, never a mock. Everything this tool
reports is a fact about refs, and the two errors it exists to avoid are beliefs
about git: that a branch ahead by zero commits holds nothing, and that a branch
ahead by one holds something. A mock encodes whichever belief its author had.

Two branches can each carry a single unpushed commit of the same age and be
identical in every count `rev-list` produces, while one has already landed by
another route and the other is work on one disk. `picked` and `mine` below are
those two: `picked` adds the same file with the same content as a commit on
`main`, under a different message, so the patch is upstream and the sha is not.

Each repository is written once per module with `git fast-import`, its
tracking refs declared as a last fetch left them. The richest has a bare
remote set to what the host holds now, which is where the two can differ: a
holder the host deleted, and one it moved. The census runs once online and
once offline against it. The exit status is read from the script run as a
subprocess, because an entry point's exit status is its contract.

The mutations, per `a-check-is-evidence-after-it-fails`, quoted as they
printed.

`uv run qm mutate project-seed/ci/branch_census.py` killed 42 of 50 operator
mutants against a green baseline. Every survivor is text inside a message, a
comment or a help string.

By hand, each run alone against a backup whose presence was checked first:

  `unique_commits` counting every cherry line instead of only the `+` ones

    FAILED test_each_branch_is_read_into_its_class[offline-picked]
    FAILED test_the_gate_fires_only_on_work_that_would_be_lost

  `origin/HEAD` not skipped

    FAILED test_the_default_branch_and_the_remote_head_pointer_are_not_branches

  the gate counting branches rather than branches with unique work

    FAILED test_the_gate_fires_only_on_work_that_would_be_lost

  the unpushed count ignored, so a stranded branch reads as ordinary

    FAILED test_each_branch_is_read_into_its_class[online-shared]

  a branch's tip, date and author read from the local ref when a remote one
  exists

    FAILED test_a_branch_carries_its_tip_its_date_and_its_author

  ahead and behind read the wrong way round

    FAILED test_each_branch_is_read_into_its_class[online-landed]

  each heading listing the rows of every other class

    FAILED test_each_row_is_filed_under_its_own_class

  the rows within a class sorted oldest first

    FAILED test_within_a_class_the_newest_tip_comes_first

  a holder kept online whether or not the host still has it

    FAILED test_each_branch_is_read_into_its_class[online-stale]
    FAILED test_a_host_that_cannot_be_asked_confirms_no_holder

  a holder the host moved on kept only at the same sha

    FAILED test_each_branch_is_read_into_its_class[online-ff]

  a holder the host moved to an unfetched commit kept

    FAILED test_each_branch_is_read_into_its_class[online-moved]

  every local branch read as local, held or not

    FAILED test_each_branch_is_read_into_its_class[offline-held]

  the host never asked, so online reads as offline

    FAILED test_each_branch_is_read_into_its_class[online-stale]

  a held branch counted as work at risk

    FAILED test_the_gate_fires_only_on_work_that_would_be_lost

  only the first holder kept

    FAILED test_a_branch_only_this_clone_holds_says_what_it_carries[online-held-...]

  a holder the host does not confirm left unsaid

    FAILED test_a_branch_only_this_clone_holds_says_what_it_carries[online-moved-...]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import branch_census as bc  # noqa: E402

from conftest import ENV, git  # noqa: E402

WHO = "committer Test <test@example.invalid> 1700000000 +0000"
WHEN = "2023-11-14"
O, H = "refs/remotes/origin/", "refs/heads/"


def commit(ref: str, mark: int, parent: str | None, name: str,
           message: str = "msg") -> str:
    """One commit adding `name`, whose content is its own name, on `ref`."""
    data = f"{name}\n"
    return (f"commit {ref}\nmark :{mark}\n{WHO}\n"
            f"data {len(message)}\n{message}\n"
            + (f"from {parent}\n" if parent else "")
            + f"M 100644 inline {name}\ndata {len(data)}\n{data}\n")


def reset(ref: str, at: str) -> str:
    return f"reset {ref}\nfrom {at}\n\n"


def written(path: Path, *stream: str) -> Path:
    subprocess.run(["git", "init", "-q", "-b", "main", str(path)], check=True, env=ENV)
    subprocess.run(["git", "-C", str(path), "fast-import", "--quiet"],
                   input="".join(stream).encode("utf-8"), check=True, env=ENV)
    return path


# `main` and the branch whose patch landed on it under another sha.
LANDED = (
    commit(f"{O}main", 1, None, "README.md"),
    commit(f"{O}main", 2, ":1", "feature.txt", "landed by another route"),
    reset(f"{H}main", ":2"),
    commit(f"{H}picked", 3, ":1", "feature.txt", "add feature.txt"),
)

# Every other class, each on its own branch.
CLASSES = LANDED + (
    commit(f"{H}mine", 4, ":2", "only-here.txt"),
    commit(f"{O}shared", 5, ":2", "shared.txt"),
    commit(f"{H}shared", 6, ":5", "later.txt"),
    reset(f"{O}landed", ":1"),
    commit(f"{O}gone", 7, ":2", "gone.txt"),
    commit(f"{O}ahead", 8, ":2", "ahead.txt"),
    reset(f"{H}ahead", ":8"),
    # Holders are tracking refs; `refs/push/` is a commit the host has that no
    # tracking ref points at.
    commit(f"{O}docs/hold", 9, ":2", "h1.txt"),
    commit(f"{O}docs/hold", 10, ":9", "h2.txt"),
    reset(f"{O}docs/hold-copy", ":10"),
    commit(f"{O}stale-holder", 11, ":2", "s1.txt"),
    commit(f"{O}moved-holder", 12, ":2", "t1.txt"),
    commit(f"{O}ff-holder", 13, ":2", "q1.txt"),
    commit("refs/push/ff-holder", 14, ":13", "q2.txt"),
    reset(f"{H}held", ":9"),
    reset(f"{H}stale", ":11"),
    reset(f"{H}moved", ":12"),
    reset(f"{H}ff", ":13"),
    commit(f"{H}part", 15, ":10", "p1.txt"),
)

# What the host holds now. Pushed by URL, so no tracking ref moves; the host is
# then given `moved-holder` at a commit the clone never fetched, and never had
# `stale-holder` at all.
HOST = tuple(f"{O}{b}:{H}{b}" for b in
             ("main", "shared", "landed", "gone", "ahead", "docs/hold",
              "docs/hold-copy")) + (f"refs/push/ff-holder:{H}ff-holder",)


@pytest.fixture(scope="module")
def root(tmp_path_factory) -> Path:
    """`r` holds every class, with a bare `r.git` as its host; `clean` only
    `picked`; `empty` only `main`. Neither of those two has a remote to ask."""
    top = tmp_path_factory.mktemp("census")
    r, host = top / "r", top / "r.git"
    written(r, *CLASSES)
    git(r, "symbolic-ref", f"{O}HEAD", f"{O}main")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(host)],
                   check=True, env=ENV)
    git(r, "push", "-q", str(host), *HOST)
    git(r, "remote", "add", "origin", str(host))
    subprocess.run(["git", "-C", str(host), "fast-import", "--quiet"],
                   input=commit(f"{H}moved-holder", 1, f"{H}main", "t2.txt").encode(),
                   check=True, env=ENV)
    written(top / "clean", *LANDED)
    written(top / "empty", commit(f"{O}main", 1, None, "README.md"),
            reset(f"{H}main", ":1"))
    return top


@pytest.fixture(scope="module")
def found(root) -> dict[str, bc.Branch]:
    return {b.name: b for b in bc.census(str(root / "r"))}


@pytest.fixture(scope="module")
def offline(root) -> SimpleNamespace:
    """The census with `--offline`, and every git command it ran."""
    ran: list[tuple[str, ...]] = []
    real = bc.git

    def watched(*args, repo="."):
        ran.append(args)
        return real(*args, repo=repo)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(bc, "git", watched)
        found = {b.name: b for b in bc.census(str(root / "r"), online=False)}
    return SimpleNamespace(found=found, ran=ran)


# --- the classes -------------------------------------------------------------

HELD = (bc.HELD, 1, 0, 0, 0)

# branch: kind, ahead, behind, unpushed, unique -- online and offline alike
EXPECTED = {
    # Ahead by one and holding nothing: its patch is on `main` already.
    "picked": (bc.LOCAL, 1, 1, 0, 0),
    "mine": (bc.LOCAL, 1, 0, 0, 1),
    # On the remote and merged-looking there, with a newer commit only here.
    "shared": (bc.STRANDED, 1, 0, 1, 2),
    "ahead": (bc.AHEAD, 1, 0, 0, 0),
    "gone": (bc.GONE, 1, 0, 0, 0),
    "landed": (bc.MERGED, 0, 1, 0, 0),
    # Two remote branches contain it.
    "held": HELD,
    # The host moved the holder on to a commit this clone has, which still
    # contains it.
    "ff": HELD,
    # Its base is on a remote branch and its tip is not.
    "part": (bc.LOCAL, 3, 0, 0, 3),
    # The holders are remote branches like any other.
    "docs/hold": (bc.GONE, 2, 0, 0, 0),
    "docs/hold-copy": (bc.GONE, 2, 0, 0, 0),
    "ff-holder": (bc.GONE, 1, 0, 0, 0),
    "stale-holder": (bc.GONE, 1, 0, 0, 0),
    "moved-holder": (bc.GONE, 1, 0, 0, 0),
}

# Held as of the last fetch, and local once the host is asked: it no longer
# has `stale-holder`, and has moved `moved-holder` to a commit never fetched.
UNCONFIRMED = {"stale": (HELD, (bc.LOCAL, 1, 0, 0, 1)),
               "moved": (HELD, (bc.LOCAL, 1, 0, 0, 1))}

CASES = ([("online", n, e) for n, e in EXPECTED.items()]
         + [("offline", n, e) for n, e in EXPECTED.items()]
         + [(mode, n, e) for n, (off, on) in UNCONFIRMED.items()
            for mode, e in (("offline", off), ("online", on))])


@pytest.mark.parametrize("mode,name,expected", [
    pytest.param(*case, id=f"{case[0]}-{case[1]}") for case in CASES])
def test_each_branch_is_read_into_its_class(found, offline, mode, name, expected):
    b = (found if mode == "online" else offline.found)[name]
    assert (b.kind, b.ahead, b.behind, b.unpushed, b.unique) == expected


def test_the_default_branch_and_the_remote_head_pointer_are_not_branches(found, offline):
    """The default branch is what everything is measured against, and
    `origin/HEAD` is a symbolic ref: counted, it duplicates the default branch
    under a name nobody pushed and nobody can delete."""
    assert set(found) == set(offline.found) == set(EXPECTED) | set(UNCONFIRMED)


def test_offline_asks_the_host_nothing(offline):
    assert "ls-remote" not in {args[0] for args in offline.ran}


def test_a_host_that_cannot_be_asked_confirms_no_holder(root):
    r = str(root / "r")
    assert bc.host_heads("nowhere", r) is None
    recorded = bc.holders("held", "origin", r)
    assert [name for name, _ in recorded] == ["docs/hold", "docs/hold-copy"]
    assert bc.confirmed("held", recorded, {}, r) == []


def test_a_branch_carries_its_tip_its_date_and_its_author(root, found):
    """Read from the remote ref where there is one, since that is what
    somebody else can see."""
    r = root / "r"
    assert found["shared"].tip == git(r, "rev-parse", "--short", "origin/shared")
    assert found["mine"].tip == git(r, "rev-parse", "--short", "mine")
    assert {(b.when, b.who) for b in found.values()} == {(WHEN, "Test")}


UNCONFIRMED_NOTE = ("origin/{0}-holder held it at the last fetch, and the host "
                    "does not confirm it; 1 carrying work not upstream by patch")


@pytest.mark.parametrize("mode,name,says", [
    ("online", "picked", "nothing unique -- every patch is already upstream"),
    ("online", "mine", "1 carrying work not upstream by patch"),
    ("online", "shared", "1 commit(s) not on origin; 2 carrying work not upstream by patch"),
    ("online", "held", "all on origin/docs/hold and 1 more"),
    ("online", "ff", "all on origin/ff-holder"),
    ("online", "stale", UNCONFIRMED_NOTE.format("stale")),
    ("online", "moved", UNCONFIRMED_NOTE.format("moved")),
    ("offline", "stale", "all on origin/stale-holder"),
])
def test_a_branch_only_this_clone_holds_says_what_it_carries(
        found, offline, mode, name, says):
    b = (found if mode == "online" else offline.found)[name]
    assert "; ".join(b.notes) == says


def test_the_patch_comparison_says_nothing_rather_than_zero_when_it_cannot_run(root):
    assert bc.unique_commits("origin/main", "no-such-branch", str(root / "r")) == -1
    assert bc.describe_unique(-1) == "patch comparison unavailable"


def test_the_default_branch_is_asked_of_the_remote_and_falls_back_to_main(root):
    git(root / "empty", "symbolic-ref", f"{O}HEAD", f"{O}main")
    assert bc.default_branch("origin", str(root / "empty")) == "main"
    assert bc.default_branch("nowhere", str(root / "empty")) == "main"


# --- what a person reads -----------------------------------------------------


def test_the_report_sorts_by_what_it_costs_to_be_wrong(found):
    text = bc.render(list(found.values()))
    headings = [l.split(" -- ")[0].strip() for l in text.splitlines()
                if " -- " in l and not l.startswith("    ")]
    assert headings == ["STRANDED", "LOCAL", "AHEAD", "HELD", "GONE", "MERGED"]
    assert f"    {WHEN}  {found['mine'].tip}  +1/-0  mine  (1 carrying" in text
    assert ("5 branch(es) hold work this clone alone has: "
            "mine, moved, part, shared, stale") in text
    assert "1 unpushed branch(es) carry nothing upstream does not already have: picked" in text
    assert "HELD -- every commit is on another remote branch; deleting loses the name" in text


def sections(text: str) -> dict[str, list[str]]:
    """Heading -> the branch names listed under it, in order."""
    found: dict[str, list[str]] = {}
    heading = None
    for line in text.splitlines():
        if line.startswith("  ") and not line.startswith("    ") and " -- " in line:
            heading = line.split(" -- ")[0].strip()
            found[heading] = []
        elif line.startswith("    ") and heading:
            found[heading].append(line.split()[3])
        else:
            heading = None
    return found


def test_each_row_is_filed_under_its_own_class(found):
    by_kind: dict[str, list[str]] = {}
    for b in found.values():
        by_kind.setdefault(b.kind.upper(), []).append(b.name)
    assert {k: sorted(v) for k, v in sections(bc.render(list(found.values()))).items()} \
        == {k: sorted(v) for k, v in by_kind.items()}


def test_within_a_class_the_newest_tip_comes_first():
    rows = [bc.Branch(name=n, kind=bc.LOCAL, unique=1, when=w, tip="abc1234")
            for n, w in (("older", "2024-01-01"), ("newer", "2025-06-01"))]
    assert sections(bc.render(rows)) == {"LOCAL": ["newer", "older"]}


def test_automation_branches_are_summarised_rather_than_listed():
    """Dependabot rows, one per branch, would push the branches a person must
    decide about off the top of a terminal. Nor is one ever at risk."""
    bots = [bc.Branch(name=f"dependabot/uv/thing-{n}", kind=bc.LOCAL, unique=1)
            for n in range(3)]
    text = bc.render(bots)
    assert "3 automation branch(es), not listed" in text
    assert "dependabot/uv/thing-0" not in text
    assert bc.at_risk_in(bots) == []
    assert "Nothing unique is held only in this clone" in text


def test_a_repository_with_only_a_default_branch_says_so(root):
    assert bc.census(str(root / "empty")) == []
    assert bc.render([]) == "  No branches besides the default.\n"


# --- what the exit status promises ------------------------------------------


def run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CI_DIR / "branch_census.py"), "--repo", str(repo),
         *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=ENV)


def test_the_gate_fires_only_on_work_that_would_be_lost(root, capsys):
    """A branch that is unpushed and patch-equivalent, or held by another
    remote branch the host confirms, must not fail the gate.

    This is the summary line's contract as well as the exit code's: counting
    branches rather than branches with unique work turns every stale local
    branch into a red run.
    """
    clean = run(root / "clean", "--fail-on-stranded")
    assert clean.returncode == 0, clean.stdout + clean.stderr
    assert "Nothing unique is held only in this clone" in clean.stdout

    at_risk = run(root / "r", "--fail-on-stranded")
    assert at_risk.returncode == 1, at_risk.stdout + at_risk.stderr
    assert at_risk.stderr == ("branch census: work exists only in this clone: "
                              "mine, moved, part, shared, stale\n")

    assert bc.main(["--repo", str(root / "r"), "--fail-on-stranded", "--offline"]) == 1
    assert capsys.readouterr().err == ("branch census: work exists only in this "
                                       "clone: mine, part, shared\n")
    assert bc.main(["--repo", str(root / "r"), "--offline"]) == 0, (
        "a reading unless asked to be a gate")


def test_the_census_never_takes_a_delete_flag(capsys):
    """A census that can also destroy is one somebody runs in a hurry.

    Asserted against the parser rather than the docstring, because a promise
    in prose is not a promise.
    """
    with pytest.raises(SystemExit) as refused:
        bc.main(["--delete"])
    assert refused.value.code != 0
    assert "unrecognized arguments" in capsys.readouterr().err
