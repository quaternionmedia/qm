"""What a tidy reading must establish before anybody tidies.

Real repositories with real remotes, built once per module in a temporary
directory: no network and no sibling clone. Every figure the reading prints is
a fact about refs and trees, and a mock would encode a belief about git and
then agree with it.

  alpha     its checkout is a local branch the remote has never seen, with a
            committed file and an untracked one the default branch lacks. A
            linked worktree hangs off it. After its last fetch the host moved:
            the default branch advanced, one branch was deleted and one added.
  beta      its remote's default branch is `trunk`, it has no `origin/HEAD`,
            and a branch called `main` exists there with a different tree.
  gamma     named in the roster, with no clone.
  hushhush  a private entry whose remote is gone, so git's own refusal
            carries the name the reading must not print.

Two programs are stood in for, each through one seam: `gh`, because a test
that needed a signed-in host would be a test nobody ran offline, and `ruff`,
because the suite's environment does not install it. The stand-in linter
reports one finding per file it is handed, so what it counts is which files
reached it.

The mutations, per `a-check-is-evidence-after-it-fails`, each made alone in
`ci/tidy.py` against a green baseline and restored, with the tests that went
red quoted as they printed.

  the tree read from `HEAD` in place of the default branch's tracking ref

    FAILED test_the_tree_read_is_the_default_branch_s_and_never_the_checkout
    FAILED test_the_linter_is_handed_the_default_branch_s_files_alone
    FAILED test_online_the_remote_is_the_host_s_and_the_tree_is_still_the_clone_s
    FAILED test_without_the_linter_the_count_is_unknown_and_says_which_tool
    FAILED test_every_unknown_is_a_cell_and_a_reason

  `main` returned where no default branch was established

    FAILED test_no_origin_head_is_unknown_offline_and_main_is_never_assumed
    FAILED test_every_unknown_is_a_cell_and_a_reason

  the host's own answer for the default branch ignored

    FAILED test_online_the_host_names_the_default_branch

  a roster entry with no clone skipped

    FAILED test_a_missing_clone_is_a_row_of_unknowns
    FAILED test_every_unknown_is_a_cell_and_a_reason
    FAILED test_the_command_reads_every_family_with_a_clone_and_exits_zero

  the default branch counted among the merged

    FAILED test_online_the_host_names_the_default_branch
    FAILED test_branches_worktrees_and_merged_are_counted_from_refs

  the clone's own tree counted as a worktree

    FAILED test_no_origin_head_is_unknown_offline_and_main_is_never_assumed
    FAILED test_branches_worktrees_and_merged_are_counted_from_refs

  `ls-remote` run whether or not `--offline` was given

    FAILED test_the_linter_is_handed_the_default_branch_s_files_alone
    FAILED test_no_origin_head_is_unknown_offline_and_main_is_never_assumed
    FAILED test_branches_worktrees_and_merged_are_counted_from_refs
    FAILED test_offline_asks_the_host_nothing
    FAILED test_every_unknown_is_a_cell_and_a_reason

  a draft counted whatever `isDraft` says

    FAILED test_pull_requests_are_split_by_author_and_draft

  no author read as an automation account

    FAILED test_pull_requests_are_split_by_author_and_draft

  a failed pull request listing read as an empty one

    FAILED test_a_host_that_refuses_is_unknown_and_never_zero

  a missing linter read as nothing unused

    FAILED test_without_the_linter_the_count_is_unknown_and_says_which_tool

  a tree with no Python read as nothing unused

    FAILED test_a_tree_with_no_python_is_not_read_as_clean

  findings counted whatever their rule

    FAILED test_the_linter_is_handed_the_default_branch_s_files_alone

  `fetch` added to the verbs the helper allows

    FAILED test_a_verb_that_writes_is_refused
    FAILED test_every_unknown_is_a_cell_and_a_reason

  `worktree` allowed whatever follows it

    FAILED test_a_verb_that_writes_is_refused

  the private name left in what git said

    FAILED test_a_private_repository_is_named_only_by_its_reference

  an undeclared family read instead of refused

    FAILED test_the_command_reads_every_family_with_a_clone_and_exits_zero

  the tree's files written into the clone in place of a temporary directory

    FAILED test_a_reading_leaves_every_repository_as_it_found_it
    and every test that reads a fixture after it, the clone being changed
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import tidy  # noqa: E402

ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
       "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
       "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
       "GIT_AUTHOR_DATE": "1700000000 +0000", "GIT_COMMITTER_DATE": "1700000000 +0000"}


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=ENV)
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}:\n{done.stderr}")
    return done.stdout.strip()


def commit(repo: Path, message: str, **files: str) -> None:
    for name, body in files.items():
        (repo / name.replace("__", ".")).write_text(body, encoding="utf-8", newline="\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


def host(root: Path, name: str, default: str) -> Path:
    bare = root / "hosts" / f"{name}.git"
    bare.mkdir(parents=True)
    git(bare, "init", "-q", "--bare", "-b", default)
    return bare


def clone(root: Path, bare: Path, name: str) -> Path:
    git(root, "clone", "-q", str(bare), name)
    return root / name


@pytest.fixture(scope="module")
def estate(tmp_path_factory) -> SimpleNamespace:
    root = tmp_path_factory.mktemp("tidy")

    # alpha: the default branch holds three files, two of them Python.
    alpha_host = host(root, "alpha", "main")
    seed = clone(root, alpha_host, "alpha-seed")
    git(seed, "checkout", "-q", "-b", "main")
    commit(seed, "first", kept__py="import os\n", notes__txt="notes\n")
    git(seed, "branch", "landed")
    commit(seed, "second", second__py="import os\n")
    git(seed, "checkout", "-q", "-b", "open-work")
    commit(seed, "third", extra__py="import os\n")
    git(seed, "push", "-q", "origin", "main", "landed", "open-work")

    alpha = clone(root, alpha_host, "alpha")
    git(alpha, "branch", "open-work", "origin/open-work")
    git(alpha, "worktree", "add", "-q", str(root / "alpha-linked"), "-b", "linked")
    git(alpha, "checkout", "-q", "-b", "checked-out")
    commit(alpha, "local only", only_here__py="import sys\n")
    (alpha / "scratch.py").write_text("import json\n", encoding="utf-8")

    # The host moves after alpha's last fetch.
    git(seed, "checkout", "-q", "main")
    commit(seed, "later", later__txt="later\n")
    git(seed, "branch", "new-on-host")
    git(seed, "push", "-q", "origin", "main", "new-on-host", ":landed")

    # beta: the default branch is trunk, and a branch named main is a decoy.
    beta_host = host(root, "beta", "trunk")
    work = clone(root, beta_host, "beta-seed")
    git(work, "checkout", "-q", "-b", "trunk")
    commit(work, "trunk", one__py="x = 1\n", two__txt="two\n")
    git(work, "checkout", "-q", "--orphan", "main")
    git(work, "rm", "-q", "-rf", ".")
    commit(work, "decoy", decoy__txt="decoy\n")
    git(work, "push", "-q", "origin", "trunk", "main")
    beta = clone(root, beta_host, "beta")
    git(beta, "remote", "set-head", "origin", "-d")

    # hushhush: private, and its remote is gone.
    hush_host = host(root, "hushhush", "main")
    work = clone(root, hush_host, "hushhush-seed")
    git(work, "checkout", "-q", "-b", "main")
    commit(work, "first", readme__txt="readme\n")
    git(work, "push", "-q", "origin", "main")
    hush = clone(root, hush_host, "hushhush")
    hush_host.rename(root / "hosts" / "moved-away.git")

    roster = [
        {"name": "alpha", "paths": ["alpha"], "family": "core"},
        {"name": "beta", "paths": ["beta"], "family": "core"},
        {"name": "gamma", "paths": ["gamma", "elsewhere/gamma"], "family": "core"},
        {"ref": "private-99", "name": "hushhush", "paths": ["hushhush"], "family": "games"},
        {"name": "delta", "paths": ["delta"], "family": "commons"},
    ]
    roster_file = root / "roster.yaml"
    roster_file.write_text(yaml.safe_dump({"schema": 1, "repositories": roster}),
                           encoding="utf-8")
    return SimpleNamespace(root=root, alpha=alpha, beta=beta, hush=hush,
                           roster=roster, roster_file=roster_file)


PULLS = [
    {"number": 1, "isDraft": False, "author": {"login": "somebody", "is_bot": False}},
    {"number": 2, "isDraft": True, "author": {"login": "somebody", "is_bot": False}},
    {"number": 3, "isDraft": False, "author": {"login": "app/dependabot", "is_bot": True}},
    {"number": 4, "isDraft": False, "author": {"login": "app/renovate", "is_bot": True}},
    {"number": 5, "isDraft": False, "author": {"login": "another", "is_bot": False}},
]


def answering(pulls=PULLS):
    return lambda args, cwd: SimpleNamespace(returncode=0, stdout=json.dumps(pulls),
                                             stderr="")


def never(*args, **kwargs):
    raise AssertionError("the host CLI was reached")


def linter(seen: list[str] | None = None):
    """One F401 per file handed over, and one finding outside the three rules."""
    def run(executable, directory):
        files = sorted(p.relative_to(directory).as_posix()
                       for p in Path(directory).rglob("*") if p.is_file())
        if seen is not None:
            seen.extend(files)
        findings = [{"code": "F401", "filename": f} for f in files]
        findings.append({"code": "E999", "filename": "elsewhere"})
        return SimpleNamespace(returncode=0, stdout=json.dumps(findings), stderr="")
    return run


def reading(estate, name: str, monkeypatch, *, online: bool, ruff: str | None = "ruff",
            gh=None, seen: list[str] | None = None) -> tidy.Reading:
    monkeypatch.setattr(tidy, "run_gh", gh or (answering() if online else never))
    monkeypatch.setattr(tidy, "run_ruff", linter(seen))
    found = tidy.read(estate.roster, [estate.root], None, {}, online=online, ruff=ruff)
    rows = {r.name: r for _, rows in found for r in rows}
    return rows[name]


def test_the_tree_read_is_the_default_branch_s_and_never_the_checkout(estate, monkeypatch):
    assert git(estate.alpha, "rev-parse", "--abbrev-ref", "HEAD") == "checked-out"
    alpha = reading(estate, "alpha", monkeypatch, online=False)
    assert alpha.default == "main"
    assert alpha.commit == git(estate.alpha, "rev-parse", "origin/main")
    # kept.py, notes.txt, second.py. The checkout's tree holds a fourth.
    assert alpha.files == 3


def test_the_linter_is_handed_the_default_branch_s_files_alone(estate, monkeypatch):
    seen: list[str] = []
    alpha = reading(estate, "alpha", monkeypatch, online=False, seen=seen)
    # Neither the file committed on the checked-out branch nor the untracked one.
    assert seen == ["kept.py", "second.py"]
    assert alpha.python_files == 2
    assert alpha.unused == 2
    assert alpha.unused_by_rule == {"F401": 2, "F811": 0, "F841": 0}


def test_no_origin_head_is_unknown_offline_and_main_is_never_assumed(estate, monkeypatch):
    beta = reading(estate, "beta", monkeypatch, online=False)
    assert tidy.is_unknown(beta.default)
    assert "no origin/HEAD" in beta.default["unknown"]
    for fact in ("commit", "files", "merged", "unused"):
        assert tidy.is_unknown(getattr(beta, fact)), fact
    # What needs no default branch is still read.
    assert beta.remote == 2 and beta.local == 1 and beta.worktrees == 0


def test_online_the_host_names_the_default_branch(estate, monkeypatch):
    beta = reading(estate, "beta", monkeypatch, online=True)
    assert beta.default == "trunk"
    assert beta.files == 2
    assert beta.commit == git(estate.beta, "rev-parse", "origin/trunk")
    # main is another branch there, with a history of its own.
    assert (beta.remote, beta.merged) == (2, 0)


def test_a_missing_clone_is_a_row_of_unknowns(estate, monkeypatch):
    gamma = reading(estate, "gamma", monkeypatch, online=False)
    assert gamma.found is False
    for fact in ("default", "commit", *(name for name, _ in tidy.COLUMNS)):
        assert getattr(gamma, fact) == {"unknown": "no clone on this disk"}, fact


def test_branches_worktrees_and_merged_are_counted_from_refs(estate, monkeypatch):
    alpha = reading(estate, "alpha", monkeypatch, online=False)
    # As of the last fetch: main, landed and open-work, and landed is in main.
    assert (alpha.remote, alpha.merged) == (3, 1)
    # main, open-work, linked and checked-out.
    assert alpha.local == 4
    assert alpha.worktrees == 1


def test_online_the_remote_is_the_host_s_and_the_tree_is_still_the_clone_s(estate, monkeypatch):
    alpha = reading(estate, "alpha", monkeypatch, online=True)
    # The host deleted landed and gained new-on-host, at a commit never fetched.
    assert (alpha.remote, alpha.merged) == (3, 0)
    assert alpha.files == 3
    said = " ".join(alpha.notes)
    assert "the tree read is the clone's" in said
    assert "not fetched" in said


def test_offline_asks_the_host_nothing(estate, monkeypatch):
    verbs: list[str] = []
    real = tidy.run_git

    def recording(repo, *args, **kwargs):
        verbs.append(args[0])
        return real(repo, *args, **kwargs)

    monkeypatch.setattr(tidy, "run_git", recording)
    tally: list[str] = []
    monkeypatch.setattr(tidy, "run_gh", never)
    monkeypatch.setattr(tidy, "run_ruff", linter())
    tidy.read(estate.roster, [estate.root], None, {}, online=False, ruff="ruff",
              tally=tally)
    assert verbs and "ls-remote" not in verbs
    assert tally == []
    alpha = reading(estate, "alpha", monkeypatch, online=False)
    assert alpha.prs == alpha.bots == alpha.drafts == {
        "unknown": "--offline asks the host nothing"}


def test_pull_requests_are_split_by_author_and_draft(estate, monkeypatch):
    alpha = reading(estate, "alpha", monkeypatch, online=True)
    assert (alpha.prs, alpha.bots, alpha.drafts) == (5, 2, 1)


def test_a_host_that_refuses_is_unknown_and_never_zero(estate, monkeypatch):
    refusing = lambda args, cwd: SimpleNamespace(  # noqa: E731
        returncode=1, stdout="", stderr="gh: To get started, run gh auth login\nmore\n")
    alpha = reading(estate, "alpha", monkeypatch, online=True, gh=refusing)
    assert alpha.prs == alpha.bots == alpha.drafts == {
        "unknown": "gh: To get started, run gh auth login"}

    def absent(args, cwd):
        raise FileNotFoundError("gh")

    alpha = reading(estate, "alpha", monkeypatch, online=True, gh=absent)
    assert alpha.prs == {"unknown": "gh not installed"}


def test_without_the_linter_the_count_is_unknown_and_says_which_tool(estate, monkeypatch):
    alpha = reading(estate, "alpha", monkeypatch, online=False, ruff=None)
    assert alpha.unused == {"unknown": "ruff not installed"}
    assert alpha.files == 3


def test_a_tree_with_no_python_is_not_read_as_clean(estate, monkeypatch):
    hush = reading(estate, "private-99", monkeypatch, online=False)
    assert hush.unused == tidy.NO_PYTHON
    assert hush.files == 1


def test_a_verb_that_writes_is_refused(estate):
    for verb in (("fetch",), ("push",), ("checkout", "main"), ("branch", "-D", "linked"),
                 ("worktree", "prune"), ("worktree", "remove", "x"), ("worktree",), ()):
        with pytest.raises(tidy.Refused):
            tidy.run_git(estate.alpha, *verb)
    assert tidy.run_git(estate.alpha, "worktree", "list").returncode == 0


def snapshot(estate) -> dict:
    """Every ref, HEAD and file of every fixture clone, outside `.git`."""
    seen = {}
    for repo in (estate.alpha, estate.beta, estate.hush):
        files = sorted((p.relative_to(repo).as_posix(), p.stat().st_size)
                       for p in repo.rglob("*")
                       if p.is_file() and ".git" not in p.relative_to(repo).parts)
        seen[repo.name] = (git(repo, "for-each-ref"), git(repo, "rev-parse", "HEAD"),
                           git(repo, "status", "--porcelain"),
                           git(repo, "worktree", "list"), files)
    seen["root"] = sorted(p.name for p in estate.root.iterdir())
    return seen


def test_a_reading_leaves_every_repository_as_it_found_it(estate, monkeypatch):
    before = snapshot(estate)
    assert before["alpha"][2] == "?? scratch.py"
    for online in (False, True):
        reading(estate, "alpha", monkeypatch, online=online)
    assert snapshot(estate) == before


def test_a_private_repository_is_named_only_by_its_reference(estate, monkeypatch, capsys):
    # Online its remote is gone, and git's refusal names the path it tried.
    done = tidy.run_git(estate.hush, "ls-remote", "origin")
    assert done.returncode != 0 and b"hushhush" in done.stderr
    hush = reading(estate, "private-99", monkeypatch, online=True)
    assert hush.default == "main"          # the recorded symref, the host being gone
    assert any("could not be asked" in note for note in hush.notes)
    for flags in ([], ["--json"]):
        assert tidy.main(["--roster", str(estate.roster_file), "--search-root",
                          str(estate.root), *flags]) == 0
        out = capsys.readouterr().out
        assert "private-99" in out
        assert "hushhush" not in out


def test_every_unknown_is_a_cell_and_a_reason(estate, monkeypatch, capsys):
    monkeypatch.setattr(tidy, "run_gh", never)
    monkeypatch.setattr(tidy, "run_ruff", linter())
    assert tidy.main(["--roster", str(estate.roster_file), "--search-root",
                      str(estate.root), "--offline", "--family", "core",
                      "--ruff", "ruff"]) == 0
    out = capsys.readouterr().out
    rows = {line.split()[0]: line.split() for line in out.splitlines()
            if line.startswith("  ") and line.split()[0] in ("alpha", "beta", "gamma")
            and ":" not in line.split()[0]}
    assert rows["alpha"][1:4] == ["main", git(estate.alpha, "rev-parse", "origin/main")[:7], "3"]
    assert rows["beta"][1:4] == ["unknown", "unknown", "unknown"]
    assert set(rows["gamma"][1:]) == {"unknown"}
    assert ("beta: default, commit, files, merged, unused unknown: no origin/HEAD in "
            "this clone, and --offline asks the host nothing") in out
    assert "gamma: default, commit, files" in out and "no clone on this disk" in out
    # Shared by every clone, so said once.
    assert out.count("--offline asks the host nothing") == 2
    assert "every clone: prs, bots, drafts unknown" in out


def test_the_command_reads_every_family_with_a_clone_and_exits_zero(estate, monkeypatch, capsys):
    monkeypatch.setattr(tidy, "run_gh", answering())
    monkeypatch.setattr(tidy, "run_ruff", linter())
    args = ["--roster", str(estate.roster_file), "--search-root", str(estate.root)]
    assert tidy.main([*args, "--json", "--ruff", "ruff"]) == 0
    document = json.loads(capsys.readouterr().out)
    families = {f["name"]: [r["name"] for r in f["repositories"]]
                for f in document["families"]}
    # commons is declared and claimed, and nothing of it is on this disk.
    assert families == {"core": ["alpha", "beta", "gamma"], "games": ["private-99"]}
    # One ls-remote and one listing for each of the three clones found.
    assert document["host_calls"] == 6
    assert document["offline"] is False

    assert tidy.main([*args, "--offline", "--family", "commons"]) == 0
    assert "delta" in capsys.readouterr().out

    assert tidy.main([*args, "--family", "no-such-family"]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "no-such-family" in captured.err
