"""What an estate survey must tell apart before anybody consolidates.

**REAL REPOSITORIES WITH A REAL REMOTE, NEVER A MOCK.** Every class this tool
reports is a fact about refs -- on the remote or not, ahead of the base or
not, an ancestor of HEAD or not -- and a mock would encode whichever belief
its author held about git and then agree with it. The seed's branch census
learned that the hard way; this suite starts where it ended. Each test builds
a bare `origin` and a clone of it, which is what a laptop and a runner have.

The one thing stood in for is the host CLI: `gh` is reached through a single
seam, and the tests replace the seam rather than the host, because a test
that needed a signed-in host to pass would be a test nobody ran offline.

THE MUTATIONS, per `a-check-is-evidence-after-it-fails`, quoted as they
printed.

  `relation_to_head` reading `--is-ancestor` inverted, so a folded branch
  reports as independent and an independent one as folded

    AssertionError: assert 'independent' == 'folded'
    AssertionError: assert [('alone', 1, 'folded')] == [('alone', 1, 'independent')]

  the verb allowlist removed from `run_git`, so the helper spawns whatever it
  is handed

    Failed: DID NOT RAISE Refused

  a MISSING roster entry dropped instead of reported

    AssertionError: assert ['here'] == ['here', 'elsewhere']
    AssertionError: assert {'named': 1, ...copy': 1, ...} == {'named': 2, ...copy': 1, ...}

AND ONE FAULT IN THE SCAFFOLDING THAT RAN THEM. The first pass applied the
three mutations in sequence with a restore between each, and the restore
copied from a backup that a shell fallback had never written -- so the second
run carried two mutations and the third carried three, and every one of them
read as red. The failures were still attributable, because each run added
lines the one before did not have, but a mutation that goes red on top of a
red baseline has shown nothing about itself. Each was rerun alone from a
backup whose presence was checked first, and the lines above are from those
runs.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import estate  # noqa: E402

ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=ENV)
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}:\n{done.stderr}")
    return done.stdout.strip()


def commit(repo: Path, name: str) -> str:
    (repo / name).write_text(f"{name}\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"add {name}")
    return git(repo, "rev-parse", "HEAD")


def clone_pair(root: Path, name: str) -> Path:
    """A bare remote and a clone of it, one commit on `main`, pushed."""
    upstream = root / f"{name}.git"
    work = root / name
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(upstream)],
                   check=True, env=ENV)
    subprocess.run(["git", "clone", "-q", str(upstream), str(work)],
                   check=True, env=ENV)
    commit(work, "README.md")
    git(work, "push", "-q", "-u", "origin", "main")
    return work


def roster_for(root: Path, *names: str, extra: str = "") -> Path:
    body = "repositories:\n" + "".join(
        f"  - name: {n}\n    paths: [{n}]\n" for n in names) + extra
    path = root / "roster.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CI_DIR / "estate.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd), env=ENV)


def survey_one(work: Path, online: bool = False) -> estate.Repository:
    entry = {"name": work.name, "paths": [work.name]}
    return estate.survey([entry], [work.parent], online=online)[0]


# --- the classes -------------------------------------------------------------


def test_a_branch_on_origin_and_ahead_of_it_is_reported_as_ahead(tmp_path):
    """The remote has the branch and not its newest commit. Pushing fixes it,
    and nothing else here does."""
    work = clone_pair(tmp_path, "r")
    git(work, "checkout", "-q", "-b", "feature")
    commit(work, "one.txt")
    git(work, "push", "-q", "-u", "origin", "feature")
    commit(work, "two.txt")
    git(work, "checkout", "-q", "main")

    repo = survey_one(work)

    assert [(b.name, b.unpushed) for b in repo.ahead] == [("feature", 1)]
    assert repo.one_copy == []
    assert repo.holds_one_copy


def test_a_local_only_branch_folded_into_head_is_marked_folded(tmp_path):
    """Its commits are on the checked-out branch, so it goes when HEAD
    reaches the host. Still one copy until then."""
    work = clone_pair(tmp_path, "r")
    git(work, "checkout", "-q", "-b", "folded")
    commit(work, "one.txt")
    git(work, "checkout", "-q", "-b", "tip")
    commit(work, "two.txt")

    repo = survey_one(work)

    by_name = {b.name: b for b in repo.one_copy}
    assert by_name["folded"].relation == estate.FOLDED
    assert by_name["folded"].ahead == 1
    assert by_name["tip"].relation == estate.HEAD
    assert repo.branch == "tip"


def test_a_local_only_branch_not_in_head_is_independent(tmp_path):
    """Nothing checked out contains it. Pushing HEAD would not save it."""
    work = clone_pair(tmp_path, "r")
    git(work, "checkout", "-q", "-b", "alone")
    commit(work, "one.txt")
    git(work, "checkout", "-q", "main")

    repo = survey_one(work)

    assert [(b.name, b.ahead, b.relation) for b in repo.one_copy] == [
        ("alone", 1, estate.INDEPENDENT)]


def test_a_local_only_branch_with_nothing_beyond_the_base_is_not_one_copy(tmp_path):
    """A branch at the base holds nothing the host lacks, whatever its name."""
    work = clone_pair(tmp_path, "r")
    git(work, "branch", "empty")

    repo = survey_one(work)

    assert repo.one_copy == []
    assert not repo.holds_one_copy


def test_a_dirty_tree_is_counted(tmp_path):
    work = clone_pair(tmp_path, "r")
    (work / "scratch.txt").write_text("x\n", encoding="utf-8")
    (work / "README.md").write_text("changed\n", encoding="utf-8")

    repo = survey_one(work)

    assert repo.dirty == 2
    assert not repo.holds_one_copy, "uncommitted is not committed"


def test_the_default_branch_is_asked_of_the_remote_and_a_guess_says_so(
        tmp_path, monkeypatch):
    """A clone made before the remote had a commit records no `origin/HEAD`,
    which is the state of several clones in this estate. Offline there is
    nothing to ask and the survey says it assumed; online the remote's own
    HEAD answers and the note is gone."""
    work = clone_pair(tmp_path, "r")
    assert git(work, "for-each-ref", "refs/remotes/origin/HEAD") == ""

    offline = survey_one(work, online=False)
    assert offline.default == "main"
    assert any("assumed" in n for n in offline.notes)

    monkeypatch.setattr(estate, "run_gh", lambda args, cwd: subprocess.CompletedProcess(
        args, 0, stdout="[]", stderr=""))
    online = survey_one(work, online=True)
    assert online.default == "main"
    assert not any("assumed" in n for n in online.notes)


# --- the roster ---------------------------------------------------------------


def test_a_roster_entry_nothing_resolves_is_reported_missing_not_dropped(tmp_path):
    """A survey silently short of one repository reads exactly like a survey
    of everything.

    Mutation: `continue` past the unresolved entry without appending, and
    this fails on the names.
    """
    work = clone_pair(tmp_path, "here")
    roster = [{"name": "here", "paths": ["here"]},
              {"name": "elsewhere", "paths": ["elsewhere", "also/elsewhere"]}]

    found = estate.survey(roster, [tmp_path], online=False)

    assert [r.name for r in found] == ["here", "elsewhere"]
    assert found[1].missing
    assert found[1].candidates == ["elsewhere", "also/elsewhere"]
    text = estate.render(found, online=False)
    assert "elsewhere: MISSING -- elsewhere, also/elsewhere" in text
    assert "2 repositories named, 1 found" in text
    assert work.exists()


def test_an_unreadable_roster_exits_two_and_a_completed_survey_exits_zero(tmp_path):
    """A reading, not a gate: the state of the estate never fails it."""
    work = clone_pair(tmp_path, "r")
    git(work, "checkout", "-q", "-b", "alone")
    commit(work, "one.txt")
    (work / "dirty.txt").write_text("x\n", encoding="utf-8")

    done = run("--roster", str(roster_for(tmp_path, "r")), "--search-root",
               str(tmp_path), "--offline", cwd=tmp_path)
    assert done.returncode == 0, done.stderr
    assert "one-copy  +1   alone  [head]" in done.stdout
    assert "1 uncommitted change(s) on alone" in done.stdout

    absent = run("--roster", str(tmp_path / "nope.yaml"), "--offline", cwd=tmp_path)
    assert absent.returncode == 2
    assert "cannot read the roster" in absent.stderr

    empty = tmp_path / "empty.yaml"
    empty.write_text("repositories: []\n", encoding="utf-8")
    assert run("--roster", str(empty), "--offline", cwd=tmp_path).returncode == 2


# --- the two output shapes ---------------------------------------------------


def test_json_carries_the_same_survey_as_the_table(tmp_path):
    work = clone_pair(tmp_path, "r")
    git(work, "checkout", "-q", "-b", "alone")
    commit(work, "one.txt")
    git(work, "checkout", "-q", "main")
    roster = roster_for(tmp_path, "r", "gone")

    done = run("--roster", str(roster), "--search-root", str(tmp_path),
               "--offline", "--json", cwd=tmp_path)
    assert done.returncode == 0, done.stderr
    doc = json.loads(done.stdout)

    assert set(doc) == {"roster", "search_roots", "offline", "repositories", "totals"}
    assert doc["offline"] is True
    assert doc["totals"] == {"named": 2, "found": 1, "missing": 1,
                             "with_one_copy": 1, "dirty": 0}
    r, gone = doc["repositories"]
    assert r["name"] == "r" and r["branch"] == "main" and r["default"] == "main"
    assert r["one_copy"] == [{"name": "alone", "ahead": 1,
                              "relation": estate.INDEPENDENT}]
    assert r["ahead"] == [] and r["open_prs"] is None
    assert r["holds_one_copy"] is True and r["missing"] is False
    assert gone["missing"] is True and gone["path"] is None


# --- the host ----------------------------------------------------------------


def test_offline_asks_nothing_of_the_host(tmp_path, monkeypatch):
    """`--offline` means no gh and no ls-remote. The seam raises if touched."""
    work = clone_pair(tmp_path, "r")

    def refuse(args, cwd):
        raise AssertionError(f"gh {' '.join(args)} was run offline")

    monkeypatch.setattr(estate, "run_gh", refuse)
    spawned: list[tuple[str, ...]] = []
    real = estate.run_git

    def watched(repo, *args):
        spawned.append(args)
        return real(repo, *args)

    monkeypatch.setattr(estate, "run_git", watched)

    repo = survey_one(work, online=False)

    assert repo.open_prs is None
    assert not any(a[0] == "ls-remote" for a in spawned)
    assert any("as of the last fetch" in n for n in repo.notes)


def test_online_counts_the_current_user_s_open_pull_requests_drafts_included(
        tmp_path, monkeypatch):
    """Two open, one of them a draft, is over the one-PR slot. The draft
    counts because it holds the slot like any other."""
    work = clone_pair(tmp_path, "r")
    asked: list[list[str]] = []

    def fake_gh(args, cwd):
        asked.append(args)
        body = json.dumps([{"number": 1, "headRefName": "a", "isDraft": False},
                           {"number": 2, "headRefName": "b", "isDraft": True}])
        return subprocess.CompletedProcess(args, 0, stdout=body, stderr="")

    monkeypatch.setattr(estate, "run_gh", fake_gh)

    repo = survey_one(work, online=True)

    assert asked and asked[0][:2] == ["pr", "list"] and "@me" in asked[0]
    assert len(repo.open_prs) == 2
    assert repo.over_slot
    text = estate.render([repo], online=True)
    assert "2 OVER" in text
    assert "#2 b draft" in text


def test_a_host_that_says_no_leaves_the_slot_unknown_rather_than_free(
        tmp_path, monkeypatch):
    work = clone_pair(tmp_path, "r")
    monkeypatch.setattr(estate, "run_gh", lambda args, cwd: subprocess.CompletedProcess(
        args, 1, stdout="", stderr="no GitHub remotes found\n"))

    repo = survey_one(work, online=True)

    assert repo.open_prs is None
    assert not repo.over_slot
    assert any("pull requests unknown" in n for n in repo.notes)
    assert "  ?" in estate.render([repo], online=True)


# --- it never writes ---------------------------------------------------------


def test_the_git_helper_refuses_every_verb_that_is_not_a_read(tmp_path):
    """The promise in the header, enforced by the code.

    Mutation: delete the membership check in `run_git` and this fails with
    `DID NOT RAISE`.
    """
    work = clone_pair(tmp_path, "r")
    for verb in ("push", "fetch", "merge", "branch", "checkout", "reset",
                 "remote", "prune", "gc"):
        with pytest.raises(estate.Refused):
            estate.run_git(work, verb, "--dry-run")
    with pytest.raises(estate.Refused):
        estate.run_git(work)
    # `status --porcelain` is a reader the header names, so it must pass.
    assert estate.run_git(work, "status", "--porcelain").returncode == 0


def test_a_survey_leaves_every_ref_and_the_working_tree_as_it_found_them(tmp_path):
    """Asserted on the repository rather than on the allowlist, because the
    allowlist is what the test above covers and a reader who trusts one
    check has not been given two."""
    work = clone_pair(tmp_path, "r")
    git(work, "checkout", "-q", "-b", "alone")
    commit(work, "one.txt")
    (work / "dirty.txt").write_text("x\n", encoding="utf-8")
    upstream = tmp_path / "r.git"

    def snapshot() -> tuple[str, str, str]:
        return (git(work, "for-each-ref"), git(work, "status", "--porcelain"),
                git(upstream, "for-each-ref"))

    before = snapshot()
    estate.survey([{"name": "r", "paths": ["r"]}], [tmp_path], online=False)
    assert snapshot() == before


def test_the_survey_takes_no_flag_that_acts():
    """A survey that can also act is one somebody runs in a hurry.

    Asserted against the parser rather than the docstring, because a promise
    in prose is not a promise.
    """
    for flag in ("--delete", "--push", "--fetch", "--prune", "--merge"):
        refused = run("--offline", flag, cwd=CI_DIR)
        assert refused.returncode != 0, flag
        assert "unrecognized arguments" in refused.stderr, flag
