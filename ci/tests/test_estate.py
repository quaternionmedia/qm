"""What an estate survey must tell apart before anybody consolidates.

Real repositories with a real remote, never a mock. Every class this tool
reports is a fact about refs -- on the remote or not, ahead of the base or
not, contained in another remote branch or not, an ancestor of HEAD or not --
and a mock would encode whichever belief its author held about git and then
agree with it. The seed's branch census learned that the hard way; this suite
starts where it ended.

One repository holds every case. It is written once per module with `git
fast-import`, its tracking refs declared as a last fetch left them and its
bare remote set to what the host holds now, which is where the two can differ:
a holder the host deleted, and one it moved. The survey runs once offline and
once online, and each test reads those two runs. A second, clean clone serves
the command-line tests, which survey it in process.

The one thing stood in for is the host CLI: `gh` is reached through a single
seam, and the tests replace the seam rather than the host, because a test
that needed a signed-in host to pass would be a test nobody ran offline.

The mutations, per `a-check-is-evidence-after-it-fails`, quoted as they
printed.

`uv run qm mutate ci/estate.py` killed 59 of 82 operator mutants against a
green baseline. Each survivor is equivalent: text inside a message, a comment
or a help string; `text=True` beside an `encoding`, which implies it; the `gh`
seam every test replaces; a default every caller overrides; and the blank
lines between blocks of output.

By hand, each run alone against a backup whose presence was checked first:

  a holder kept online whether or not the host still has it

    FAILED test_each_branch_is_read_into_its_class[online-stale]
    FAILED test_each_branch_is_read_into_its_class[online-moved]

  a holder the host moved on kept only at the same sha

    FAILED test_each_branch_is_read_into_its_class[online-ff]

  a holder the host moved to an unfetched commit kept

    FAILED test_each_branch_is_read_into_its_class[online-moved]

  every branch off origin by name read as one copy

    FAILED test_each_branch_is_read_into_its_class[offline-held]
    FAILED test_json_carries_the_same_survey_as_the_table

  a held branch counted as work with one copy

    FAILED test_only_one_copy_and_ahead_are_work_with_one_copy[one_copy2-held2-ahead2-False]

  held rows left out of the detail block

    FAILED test_the_rendered_survey_carries_every_class

  only the first holder kept

    FAILED test_each_branch_is_read_into_its_class[offline-held]
"""

from __future__ import annotations

import dataclasses
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import estate  # noqa: E402

ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
WHO = "committer Test <test@example.invalid> 1700000000 +0000"
O, H = "refs/remotes/origin/", "refs/heads/"


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=ENV)
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}:\n{done.stderr}")
    return done.stdout.strip()


def commit(ref: str, mark: int, parent: str | None, name: str) -> str:
    """One commit adding `name`, on `ref`, from a mark or a sha."""
    data = f"{name}\n"
    return (f"commit {ref}\nmark :{mark}\n{WHO}\ndata 4\nmsg\n"
            + (f"from {parent}\n" if parent else "")
            + f"M 100644 inline {name}\ndata {len(data)}\n{data}\n")


def reset(ref: str, at: str) -> str:
    return f"reset {ref}\nfrom {at}\n\n"


def fast_import(repo: Path, *stream: str, marks: Path | None = None) -> None:
    subprocess.run(["git", "-C", str(repo), "fast-import", "--quiet",
                    *([f"--export-marks={marks}"] if marks else [])],
                   input="".join(stream).encode("utf-8"), check=True, env=ENV)


# What the clone recorded at its last fetch, and its local branches. Holders
# are tracking refs only; `refs/push/` is a commit the host has that no
# tracking ref points at.
CLONE = (
    commit(f"{O}main", 1, None, "README.md"),
    commit(f"{O}feature", 2, ":1", "f1.txt"),
    commit(f"{H}feature", 3, ":2", "f2.txt"),
    commit(f"{O}docs/hold", 4, ":1", "h1.txt"),
    commit(f"{O}docs/hold", 5, ":4", "h2.txt"),
    reset(f"{O}docs/hold-copy", ":5"),
    commit(f"{O}stale-holder", 6, ":1", "s1.txt"),
    commit(f"{O}moved-holder", 7, ":1", "t1.txt"),
    commit(f"{O}ff-holder", 8, ":1", "q1.txt"),
    commit("refs/push/ff-holder", 9, ":8", "q2.txt"),
    commit(f"{H}folded", 10, ":1", "a1.txt"),
    commit(f"{H}tip", 11, ":10", "a2.txt"),
    commit(f"{H}alone", 12, ":1", "b1.txt"),
    commit(f"{H}part", 13, ":5", "p1.txt"),
    reset(f"{H}main", ":1"),
    reset(f"{H}empty", ":1"),
    reset(f"{H}held", ":4"),
    reset(f"{H}stale", ":6"),
    reset(f"{H}moved", ":7"),
    reset(f"{H}ff", ":8"),
)

# What the host holds now. Pushed by URL, so no tracking ref moves; then the
# host is given `moved-holder` at a commit the clone never fetched, and never
# had `stale-holder` at all.
HOST = ("refs/remotes/origin/main:refs/heads/main",
        "refs/remotes/origin/feature:refs/heads/feature",
        "refs/remotes/origin/docs/hold:refs/heads/docs/hold",
        "refs/remotes/origin/docs/hold-copy:refs/heads/docs/hold-copy",
        "refs/push/ff-holder:refs/heads/ff-holder")


@pytest.fixture(scope="module")
def root(tmp_path_factory) -> Path:
    """`r`, its bare remote `r.git`, and `plain`, a clean clone with `main` alone."""
    top = tmp_path_factory.mktemp("estate")
    r, bare = top / "r", top / "r.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)],
                   check=True, env=ENV)
    subprocess.run(["git", "init", "-q", "-b", "main", str(r)], check=True, env=ENV)
    marks = top / "r.marks"
    fast_import(r, *CLONE, marks=marks)
    git(r, "push", "-q", str(bare), *HOST)
    git(r, "remote", "add", "origin", str(bare))
    main = dict(line.split() for line in marks.read_text().splitlines())[":1"]
    fast_import(bare, commit(f"{H}moved-holder", 1, main, "t2.txt"))
    git(r, "checkout", "-q", "-f", "tip")
    (r / "scratch.txt").write_text("x\n", encoding="utf-8")
    (r / "README.md").write_text("changed\n", encoding="utf-8")

    plain = top / "plain"
    subprocess.run(["git", "init", "-q", "-b", "main", str(plain)], check=True, env=ENV)
    fast_import(plain, commit(f"{H}main", 1, None, "README.md"), reset(f"{O}main", ":1"))
    git(plain, "reset", "-q", "--hard")
    git(plain, "symbolic-ref", f"{O}HEAD", f"{O}main")
    return top


def survey_one(work: Path, online: bool = False) -> estate.Repository:
    entry = {"name": work.name, "paths": [work.name]}
    return estate.survey([entry], [work.parent], online=online)[0]


def _gh_returning(prs):
    def fake_gh(args, cwd):
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(prs), stderr="")
    return fake_gh


@pytest.fixture(scope="module")
def readings(root) -> SimpleNamespace:
    """`r` surveyed offline and online, with every git verb each run spawned
    and every ref and the working tree before and after both."""
    r = root / "r"

    def snapshot() -> tuple[str, str, str]:
        return (git(r, "for-each-ref"), git(r, "status", "--porcelain"),
                git(root / "r.git", "for-each-ref"))

    def refuse(args, cwd):
        raise AssertionError(f"gh {' '.join(args)} was run offline")

    spawned: dict[str, list[tuple[str, ...]]] = {"offline": [], "online": []}
    mode = ["offline"]
    real = estate.run_git

    def watched(repo, *args):
        spawned[mode[0]].append(args)
        return real(repo, *args)

    before = snapshot()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(estate, "run_git", watched)
        mp.setattr(estate, "run_gh", refuse)
        offline = survey_one(r, online=False)
        mode[0] = "online"
        mp.setattr(estate, "run_gh", _gh_returning([]))
        online = survey_one(r, online=True)
    return SimpleNamespace(offline=offline, online=online, spawned=spawned,
                           before=before, after=snapshot())


def classes(repo: estate.Repository) -> dict[str, tuple]:
    found: dict[str, tuple] = {}
    for b in repo.one_copy:
        found[b.name] = ("one-copy", b.ahead, b.relation)
    for b in repo.held:
        found[b.name] = ("held", b.ahead, tuple(b.by))
    for b in repo.ahead:
        found[b.name] = ("ahead", b.unpushed)
    return found


# --- the classes -------------------------------------------------------------

ALONE = ("one-copy", 1, estate.INDEPENDENT)

# branch, offline, online. None is a branch that holds nothing the host lacks.
CLASSES = [
    # On origin, and its newest commit is not. Pushing fixes it.
    ("feature", ("ahead", 1), ("ahead", 1)),
    # Contained in the checked-out branch: goes when HEAD reaches the host.
    ("folded", ("one-copy", 1, estate.FOLDED), ("one-copy", 1, estate.FOLDED)),
    ("tip", ("one-copy", 2, estate.HEAD), ("one-copy", 2, estate.HEAD)),
    # Nothing checked out contains it. Pushing HEAD would not save it.
    ("alone", ALONE, ALONE),
    # Its base is on a remote branch and its tip is not, so it is one copy,
    # counted from the default branch.
    ("part", ("one-copy", 3, estate.INDEPENDENT), ("one-copy", 3, estate.INDEPENDENT)),
    # Two remote branches contain it; both are named, in ref order.
    ("held", ("held", 1, ("docs/hold", "docs/hold-copy")),
     ("held", 1, ("docs/hold", "docs/hold-copy"))),
    # The host moved the holder on to a commit this clone has, which still
    # contains it.
    ("ff", ("held", 1, ("ff-holder",)), ("held", 1, ("ff-holder",))),
    # The host no longer has the holder; only the last fetch does.
    ("stale", ("held", 1, ("stale-holder",)), ALONE),
    # The host moved the holder to a commit this clone never fetched.
    ("moved", ("held", 1, ("moved-holder",)), ALONE),
    # At the base, whatever its name.
    ("empty", None, None),
    ("main", None, None),
]


@pytest.mark.parametrize("mode,branch,expected", [
    pytest.param(mode, branch, expected, id=f"{mode}-{branch}")
    for branch, off, on in CLASSES
    for mode, expected in (("offline", off), ("online", on))])
def test_each_branch_is_read_into_its_class(readings, mode, branch, expected):
    assert classes(getattr(readings, mode)).get(branch) == expected


def test_every_branch_with_a_class_is_in_the_table_above(readings):
    """A branch the survey reports and the table does not name is a case
    nobody decided."""
    named = {branch for branch, *_ in CLASSES}
    for mode in ("offline", "online"):
        assert set(classes(getattr(readings, mode))) <= named, mode


def test_the_checked_out_branch_and_the_dirty_tree_are_read(readings):
    assert readings.offline.branch == "tip"
    assert readings.offline.dirty == 2


@pytest.mark.parametrize("one_copy,held,ahead,holds", [
    ([estate.OneCopy("o", 1, estate.INDEPENDENT)], [], [], True),
    ([], [], [estate.Ahead("a", 1)], True),
    ([], [estate.Held("h", 1, ["a", "b", "c"])], [], False),
    ([], [], [], False),
])
def test_only_one_copy_and_ahead_are_work_with_one_copy(one_copy, held, ahead, holds):
    """A held branch loses its name when deleted, so it does not count towards
    the closing line, and it is still listed so a person can see it go."""
    repo = estate.Repository(name="x", path="p", one_copy=one_copy, held=held,
                             ahead=ahead)
    assert repo.holds_one_copy is holds
    assert estate.totals([repo])["with_one_copy"] == int(holds)
    if held:
        assert "held      +1   h  (all on a and 2 more)" in estate.render(
            [repo], online=False)


def test_a_git_read_that_fails_is_none_and_not_empty(root):
    """Several questions here have an empty answer that means something, so a
    failed command must not look like one."""
    plain = root / "plain"
    assert estate.lines(plain, "rev-parse", "--verify", "--quiet", "nope") is None
    assert estate.count(plain, "nope..main") is None
    assert estate.remote_heads(plain, "nowhere", online=True) is None
    assert estate.remote_heads(root / "absent", "origin", online=False) is None
    assert estate.lines(plain, "for-each-ref", "refs/nothing") == []


def test_the_tracking_refs_are_branches_and_origin_head_is_not(root):
    plain = root / "plain"
    heads = estate.remote_heads(plain, "origin", online=False)
    assert heads == {"main": git(plain, "rev-parse", "main")}
    assert estate.default_branch(plain, "origin", online=False) == ("main", "tracking ref")


def test_the_default_branch_is_asked_of_the_remote_and_a_guess_says_so(readings):
    """A clone with no `origin/HEAD` is the state of several in this estate.
    Offline there is nothing to ask and the survey says it assumed; online the
    remote's own HEAD answers and the note is gone."""
    assert readings.offline.default == readings.online.default == "main"
    assert any("assumed" in n for n in readings.offline.notes)
    assert not any("assumed" in n for n in readings.online.notes)


def test_the_rendered_survey_carries_every_class(readings):
    text = estate.render([readings.offline], online=False)
    width = len("repository")
    assert f"  {'r':<{width}}  {'tip':<28}      2         4     4      1  -" in text
    for line in ("2 uncommitted change(s) on tip",
                 "one-copy  +2   tip  [head]",
                 "one-copy  +1   alone  [independent]",
                 "held      +1   held  (all on docs/hold and 1 more)",
                 "held      +1   stale  (all on stale-holder)",
                 "ahead     +1   feature  (not on its remote copy)",
                 "1 holding committed work with one copy, 1 with uncommitted changes",
                 "deleting it loses only its name",
                 "r: default branch assumed to be main",
                 "--offline: the remote is as of the last fetch"):
        assert line in text, line
    assert "read from tracking refs" not in text, "a note every offline row carries"
    assert "## " not in text, "flat unless asked"
    online = estate.render([readings.online], online=True)
    assert f"  {'r':<{width}}  {'tip':<28}      2         6     2      1  0" in online
    assert "--offline" not in online


# --- the host ----------------------------------------------------------------


def test_offline_asks_nothing_of_the_host_and_online_asks_once(readings):
    """`--offline` means no gh and no ls-remote; the fixture's gh seam raises
    if touched offline."""
    verbs = {mode: [a[0] for a in args] for mode, args in readings.spawned.items()}
    assert "ls-remote" not in verbs["offline"]
    assert verbs["online"].count("ls-remote") == 2, "HEAD, then the heads"
    assert readings.offline.open_prs is None and readings.online.open_prs == []
    assert any("as of the last fetch" in n for n in readings.offline.notes)


def test_online_asks_for_the_current_user_s_open_pull_requests(root, monkeypatch):
    """Two parallel pull requests, both ready, are within the rule."""
    asked: list[list[str]] = []
    prs = [{"number": 1, "headRefName": "a", "isDraft": False, "baseRefName": "main"},
           {"number": 2, "headRefName": "b", "isDraft": False, "baseRefName": "main"}]

    def fake_gh(args, cwd):
        asked.append(args)
        return _gh_returning(prs)(args, cwd)

    monkeypatch.setattr(estate, "run_gh", fake_gh)
    repo = estate.Repository(name="plain", path=str(root / "plain"))
    estate.host_pull_requests(repo)

    assert asked and asked[0][:2] == ["pr", "list"] and "@me" in asked[0]
    assert "baseRefName" in asked[0][-1]
    assert len(repo.open_prs) == 2
    assert repo.stacked_ready == []
    assert "STACKED" not in estate.render([repo], online=True)


@pytest.mark.parametrize("child_is_draft,stacked", [(False, [2]), (True, [])])
def test_a_ready_pull_request_stacked_on_another_is_flagged_and_a_draft_is_not(
        child_is_draft, stacked):
    """The reader agrees with the gate: ready with an open parent is flagged."""
    repo = estate.Repository(name="r", path="p", open_prs=[
        {"number": 1, "headRefName": "a", "isDraft": False, "baseRefName": "main"},
        {"number": 2, "headRefName": "b", "isDraft": child_is_draft, "baseRefName": "a"},
    ])
    assert [p["number"] for p in repo.stacked_ready] == stacked
    text = estate.render([repo], online=True)
    assert ("2 STACKED" in text) == bool(stacked)
    assert ("ready but stacked: #2 b -> a" in text) == bool(stacked)


def test_a_host_that_says_no_leaves_the_stack_unknown_rather_than_clear(
        root, monkeypatch):
    monkeypatch.setattr(estate, "run_gh", lambda args, cwd: subprocess.CompletedProcess(
        args, 1, stdout="", stderr="no GitHub remotes found\n"))
    repo = estate.Repository(name="plain", path=str(root / "plain"))

    estate.host_pull_requests(repo)

    assert repo.open_prs is None
    assert repo.stacked_ready == []
    assert repo.notes == ["pull requests unknown: no GitHub remotes found"]
    assert "  ?" in estate.render([repo], online=True)


# --- the roster and the command ---------------------------------------------


def roster_for(root: Path, *names: str, extra: str = "", file: str = "roster.yaml") -> Path:
    body = "repositories:\n" + "".join(
        f"  - name: {n}\n    paths: [{n}]\n" for n in names) + extra
    path = root / file
    path.write_text(body, encoding="utf-8")
    return path


def main(capsys, *args: str) -> tuple[int, str, str]:
    code = estate.main(list(args))
    out = capsys.readouterr()
    return code, out.out, out.err


def test_a_roster_entry_nothing_resolves_is_reported_missing_not_dropped(root):
    """A survey silently short of one repository reads exactly like a survey
    of everything."""
    roster = [{"name": "plain", "paths": ["plain"]},
              {"name": "elsewhere", "paths": ["elsewhere", "also/elsewhere"]}]

    found = estate.survey(roster, [root], online=False)

    assert [r.name for r in found] == ["plain", "elsewhere"]
    assert found[1].missing
    assert found[1].candidates == ["elsewhere", "also/elsewhere"]
    text = estate.render(found, online=False)
    assert "elsewhere: MISSING -- elsewhere, also/elsewhere" in text
    assert "2 repositories named, 1 found" in text


def test_an_unreadable_roster_exits_two_and_a_completed_survey_exits_zero(
        root, capsys, monkeypatch):
    """A reading, not a gate: the state of the estate never fails it. The
    `--offline` flag reaches the survey, so the host seam is never touched."""
    def refuse(args, cwd):
        raise AssertionError(f"gh {' '.join(args)} was run offline")

    monkeypatch.setattr(estate, "run_gh", refuse)
    code, out, err = main(capsys, "--roster", str(roster_for(root, "plain")),
                          "--search-root", str(root), "--offline")
    assert code == 0, err
    assert "1 repositories named, 1 found on this disk, 0 holding" in out
    assert "prs (offline)" in out

    code, _, err = main(capsys, "--roster", str(root / "nope.yaml"), "--offline")
    assert code == 2
    assert "cannot read the roster" in err

    empty = root / "empty.yaml"
    empty.write_text("repositories: []\n", encoding="utf-8")
    assert main(capsys, "--roster", str(empty), "--offline")[0] == 2


def test_json_carries_the_same_survey_as_the_table(readings, root):
    gone = estate.Repository(name="gone", candidates=["gone"])
    doc = estate.as_document([readings.offline, gone], root / "roster.yaml",
                             [root], online=False)

    assert set(doc) == {"roster", "search_roots", "offline", "repositories", "totals"}
    assert doc["offline"] is True
    assert doc["totals"] == {"named": 2, "found": 1, "missing": 1,
                             "with_one_copy": 1, "dirty": 1}
    r, missing = doc["repositories"]
    assert r["name"] == "r" and r["branch"] == "tip" and r["default"] == "main"
    assert {"name": "alone", "ahead": 1, "relation": estate.INDEPENDENT} in r["one_copy"]
    assert {"name": "held", "ahead": 1, "by": ["docs/hold", "docs/hold-copy"]} in r["held"]
    assert r["ahead"] == [{"name": "feature", "unpushed": 1}]
    assert r["open_prs"] is None
    assert r["holds_one_copy"] is True and r["missing"] is False
    assert missing["missing"] is True and missing["path"] is None


def test_the_script_runs_as_a_bare_file_and_emits_json(root):
    """The one subprocess here: the module's own sibling imports must resolve
    when it is run as a file and not as `ci.estate`."""
    roster = roster_for(root, "plain", "gone", file="script.yaml")
    done = subprocess.run(
        [sys.executable, str(CI_DIR / "estate.py"), "--roster", str(roster),
         "--search-root", str(root), "--offline", "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(root), env=ENV)
    assert done.returncode == 0, done.stderr
    doc = json.loads(done.stdout)
    assert doc["totals"] == {"named": 2, "found": 1, "missing": 1,
                             "with_one_copy": 0, "dirty": 0}
    assert doc["repositories"][0]["held"] == []


# --- it never writes ---------------------------------------------------------


def test_the_git_helper_refuses_every_verb_that_is_not_a_read(root):
    """The promise in the header, enforced by the code."""
    plain = root / "plain"
    for verb in ("push", "fetch", "merge", "branch", "checkout", "reset",
                 "remote", "prune", "gc"):
        with pytest.raises(estate.Refused):
            estate.run_git(plain, verb, "--dry-run")
    with pytest.raises(estate.Refused):
        estate.run_git(plain)
    # `status --porcelain` is a reader the header names, so it must pass.
    assert estate.run_git(plain, "status", "--porcelain").returncode == 0


def test_a_survey_leaves_every_ref_and_the_working_tree_as_it_found_them(readings):
    """Asserted on the repository and its remote rather than on the allowlist,
    because the allowlist is what the test above covers and a reader who
    trusts one check has not been given two."""
    assert readings.after == readings.before
    assert readings.before[1], "the snapshot saw the dirty tree"


@pytest.mark.parametrize("flag", ["--delete", "--push", "--fetch", "--prune", "--merge"])
def test_the_survey_takes_no_flag_that_acts(flag, capsys):
    """A survey that can also act is one somebody runs in a hurry.

    Asserted against the parser rather than the docstring, because a promise
    in prose is not a promise.
    """
    with pytest.raises(SystemExit) as refused:
        estate.main(["--offline", flag])
    assert refused.value.code != 0
    assert "unrecognized arguments" in capsys.readouterr().err


# --- the families ------------------------------------------------------------


def test_the_family_claim_rides_with_the_row_and_nothing_infers_one(root):
    """The family is what the roster entry says, MISSING rows included, and an
    entry that says nothing is None -- unstated, never a default."""
    roster = [{"name": "plain", "paths": ["plain"], "family": "games"},
              {"name": "gone", "paths": ["gone"], "family": "infra"},
              {"name": "quiet", "paths": ["quiet"]}]

    found = estate.survey(roster, [root], online=False)

    assert [(r.name, r.family) for r in found] == [
        ("plain", "games"), ("gone", "infra"), ("quiet", None)]
    doc = estate.as_document(found, root / "roster.yaml", [root], False)
    assert [r["family"] for r in doc["repositories"]] == ["games", "infra", None]


def test_by_family_groups_in_name_order_with_unstated_last():
    rows = [estate.Repository(name=n, family=f) for n, f in
            [("z", None), ("b", "irl"), ("a", "core"), ("c", "irl"), ("y", None)]]

    grouped = estate.by_family(rows)

    assert [(family, [r.name for r in members]) for family, members in grouped] == [
        ("core", ["a"]), ("irl", ["b", "c"]), (estate.UNSTATED, ["z", "y"])]


def test_by_family_prints_every_row_once_under_its_family_with_its_own_totals(readings):
    """The grouped table carries the same rows as the flat one, each under
    one heading, and each heading carries that family's totals rather than
    the estate's."""
    found = [dataclasses.replace(readings.offline, family="games"),
             estate.Repository(name="gone", family="games"),
             estate.Repository(name="quiet")]

    flat = estate.render(found, online=False)
    grouped = estate.render(found, online=False, grouped=True)

    assert "## games  2 named, 1 on this disk, 1 with one copy, 1 dirty" in grouped
    assert f"## {estate.UNSTATED}  1 named, 0 on this disk, 0 with one copy, 0 dirty" in grouped
    assert grouped.index("## games") < grouped.index(f"## {estate.UNSTATED}")
    for line in (l for l in flat.splitlines() if l.startswith("  ") and (
            l.strip().startswith(("r ", "gone", "quiet")))):
        assert grouped.count(line) == flat.count(line), line
    assert "3 repositories named, 1 found" in grouped


def test_by_family_is_a_flag_on_the_command_and_changes_only_the_table(root, capsys):
    roster = roster_for(root, "plain", extra="    family: core\n", file="family.yaml")

    code, flat, _ = main(capsys, "--roster", str(roster), "--search-root",
                         str(root), "--offline")
    grouped_code, grouped, err = main(capsys, "--roster", str(roster), "--search-root",
                                      str(root), "--offline", "--by-family")

    assert code == 0 and grouped_code == 0, err
    assert "## core" not in flat
    assert "## core  1 named, 1 on this disk" in grouped
    assert flat.splitlines()[-1] == grouped.splitlines()[-1]


def test_a_private_entry_is_called_by_its_reference_not_its_name(root):
    """The companion fills in a private repository's name so the clone can be
    found; the row is still printed as the reference, because this reading
    gets pasted into committed pages."""
    entry = {"ref": "private-99", "name": "plain", "paths": ["plain"]}

    row = estate.survey([entry], [root], online=False)[0]

    assert row.name == "private-99"
    assert row.path == str((root / "plain").resolve())
    # A clean row prints no detail block and so no path; the name must then
    # appear nowhere at all.
    text = estate.render([row], online=False)
    assert "  private-99  main" in text
    assert "plain" not in text


def test_a_repository_in_two_families_is_a_row_under_each():
    rows = [estate.Repository(name="pedal", family=["irl", "instruments"]),
            estate.Repository(name="board", family="irl")]
    grouped = dict((family, [r.name for r in members])
                   for family, members in estate.by_family(rows))
    assert grouped == {"instruments": ["pedal"], "irl": ["pedal", "board"]}


def test_every_row_missing_is_a_search_root_without_clones_and_exits_two(
        root, capsys):
    """A survey in which no roster entry resolves, the corpus's own clone
    among them, has read nothing about the estate: the search root holds no
    clone, and exit 0 under a table of MISSING rows is the tool describing
    its own scaffolding. It names the roots it searched and the flag that
    moves them, prints no table, and exits as an unreadable roster does.

    Mutation: drop the all-missing refusal from `main`, and this exits 0 over
    the table.
    """
    empty = root / "nothing-here"
    empty.mkdir()
    code, out, err = main(capsys, "--roster", str(roster_for(root, "plain", "other")),
                          "--search-root", str(empty), "--offline")
    assert code == 2, out
    assert str(empty.resolve()) in err
    assert "--search-root" in err
    assert out == ""
