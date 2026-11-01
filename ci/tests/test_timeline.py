"""A project's timeline is drawn from git and its round log, and checked
without a clone.

These assert what a reader of a dated page would be misled by: a page that no
longer matches what it says it was drawn from, an entry out of order or without
its link, a round log of a shape the page misreads, and a check that quietly
needs a clone the runner does not have.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))
sys.path.insert(0, str(CI_DIR.parent / "project-seed" / "ci"))

import timeline  # noqa: E402

ROUNDS = """\
repository: example/demo
rounds:
  - round: 1
    branch: integrate/one
    pr: 11
    title: The first round
    began: 2026-01-02
    ended: 2026-01-03
    head: aaaa1111
    carried: the first thing
  - round: 2
    branch: integrate/two
    pr: 12
    began: 2026-01-05
    ended: 2026-01-05
    carried: the second thing
measured:
  - rounds: [1]
    at: abc1234
    results:
      - suite: ./run tests
        result: 10 passed
noted:
  - version: 0.1.0
    section: Added
    text: a count the release notes carried
"""

SNAPSHOT = {
    "project": "demo", "default_branch": "main",
    "read_at": {"ref": "origin/main", "commit": "f" * 40, "date": "2026-01-04"},
    "merged": [{"pr": 7, "date": "2026-01-04", "branch": "feature", "title": "A feature",
                "commit": "e" * 40}],
    "tags": [{"name": "v0.1.0", "date": "2026-01-01", "commit": "d" * 40, "annotated": False}],
}

BRANCHES = [
    {"name": "integrate/two", "base": "integrate/one", "commits": 2, "first": "2026-01-05",
     "date": "2026-01-05", "commit": "c" * 40},
    {"name": "spike", "base": "main", "commits": 1, "first": "2026-01-03", "date": "2026-01-04",
     "commit": "b" * 40},
]

RETRO = "# Retrospective: the first round\n\n**Date:** 2026-01-06, written after it.\n\nBody.\n"


def git(*args: str, cwd: Path) -> str:
    done = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 0, f"git {' '.join(args)}\n{done.stdout}{done.stderr}"
    return done.stdout


def subtree(projects: Path, rounds: str = ROUNDS, snapshot: dict | None = SNAPSHOT,
            retro: str | None = RETRO) -> Path:
    folder = projects / "demo"
    folder.mkdir(parents=True)
    (projects / "demo.md").write_text("# demo\n", encoding="utf-8")
    (folder / timeline.ROUNDS).write_text(rounds, encoding="utf-8")
    if snapshot is not None:
        (folder / timeline.SNAPSHOT).write_text(timeline.snapshot_text(snapshot), encoding="utf-8")
    if retro is not None:
        (folder / "retrospective-one.md").write_text(retro, encoding="utf-8")
    return folder


def written(projects: Path) -> Path:
    page = projects / "demo" / timeline.PAGE
    page.write_text(timeline.page_for("demo", projects), encoding="utf-8", newline="\n")
    return page


# --- the page -----------------------------------------------------------------


def test_entries_are_newest_first_and_each_links_its_pull_request_or_tag(tmp_path):
    """A timeline read top down is read newest first, and an entry without its
    link cannot be followed to what it dates.

    Mutation: drop `reverse=True` from `entries` and the order fails.
    """
    subtree(tmp_path)
    text = timeline.page_for("demo", tmp_path)
    rows = [line for line in text.splitlines() if line.startswith("| 2026-")]
    assert [row.split(" | ")[0] for row in rows] == [
        "| 2026-01-05", "| 2026-01-04", "| 2026-01-02 to 2026-01-03", "| 2026-01-01"]
    assert "[demo#12](https://github.com/example/demo/pull/12)" in rows[0]
    assert "[demo#7](https://github.com/example/demo/pull/7)" in rows[1]
    assert "[v0.1.0](https://github.com/example/demo/releases/tag/v0.1.0)" in rows[3]
    assert "a lightweight tag" in rows[3]


def test_the_page_says_what_it_is_drawn_from_and_at_which_commit(tmp_path):
    """The check cannot tell a snapshot is behind its project, so the page
    names the commit it read; its age is read off the page."""
    subtree(tmp_path)
    text = timeline.page_for("demo", tmp_path)
    assert "uv run qm timeline demo --write" in text
    assert f"at `{'f' * 7}`, a commit of 2026-01-04" in text
    assert timeline.RECORD in text
    assert "[demo](../demo.md)" in text


def test_the_page_links_its_retrospectives_with_their_dates(tmp_path):
    subtree(tmp_path)
    text = timeline.page_for("demo", tmp_path)
    assert "- 2026-01-06 · [Retrospective: the first round](retrospective-one.md)" in text


def test_measured_counts_name_the_commit_they_were_measured_at(tmp_path):
    """A count without its commit reads as the present, which is what
    records/DRAFT-few-integers-in-durable-text.md §2 rules out."""
    subtree(tmp_path)
    text = timeline.page_for("demo", tmp_path)
    assert "### Round 1, at `abc1234`" in text
    assert "- `./run tests`: 10 passed" in text
    assert "| 0.1.0 | Added | a count the release notes carried |" in text


def test_a_project_with_no_snapshot_says_none_has_been_read(tmp_path):
    subtree(tmp_path, snapshot=None)
    text = timeline.page_for("demo", tmp_path)
    assert "no git facts" in text and "--write" in text
    assert "| 2026-01-05 |" in text


def test_a_branch_is_listed_once_in_its_round_or_in_a_row_of_its_own(tmp_path):
    """A round names its branch, and git counts it: one row says both.
    Mutation: read the round's branch with `get` in place of `pop` in
    `entries` and the branch is listed a second time."""
    subtree(tmp_path, snapshot={**SNAPSHOT, "branches": BRANCHES})
    text = timeline.page_for("demo", tmp_path)
    assert "**Round 2**, on `integrate/two` (2 commits on `integrate/one`): " in text
    assert ("[demo#12](https://github.com/example/demo/pull/12) · [compare]"
            "(https://github.com/example/demo/compare/integrate/one...integrate/two)") in text
    assert "Branch `integrate/two`" not in text
    assert ("| 2026-01-03 to 2026-01-04 | Branch `spike`: 1 commit on `main` | "
            "[compare](https://github.com/example/demo/compare/main...spike) |") in text
    assert "the branches its clone held then" in text


def test_a_pipe_in_a_title_does_not_break_its_row(tmp_path):
    snapshot = {**SNAPSHOT, "merged": [{**SNAPSHOT["merged"][0], "title": "a | b"}]}
    subtree(tmp_path, snapshot=snapshot)
    assert "Merged `feature`: a \\| b" in timeline.page_for("demo", tmp_path)


# --- the round log's shape ----------------------------------------------------


@pytest.mark.parametrize("change, where", [
    (("began: 2026-01-02", "began: 2 January"), "rounds[1].began"),
    (("round: 2", "round: 1"), "rounds[2]"),
    (("rounds: [1]", "rounds: [3]"), "measured[1]"),
    (("ended: 2026-01-03", "ended: 2026-01-01"), "rounds[1]"),
    (("    at: abc1234", "    on: abc1234"), "measured[1].at"),
])
def test_a_round_log_of_the_wrong_shape_is_refused_where_it_is_wrong(tmp_path, change, where):
    """A misread round log draws a page that looks right. The last case is
    YAML's: a bare `on` key reads as true, so the log says `at`."""
    folder = subtree(tmp_path, rounds=ROUNDS.replace(*change))
    with pytest.raises(timeline.Malformed, match=where.replace("[", r"\[").replace("]", r"\]")):
        timeline.load_rounds(folder / timeline.ROUNDS)


# --- the check needs no clone -------------------------------------------------


def test_the_check_refuses_a_page_its_inputs_do_not_give(tmp_path):
    """Mutation: edit the committed page and the check fails; regenerate it
    and the check passes again."""
    subtree(tmp_path)
    page = written(tmp_path)
    assert timeline.problems("demo", tmp_path) == []
    page.write_text(page.read_text(encoding="utf-8").replace("10 passed", "11 passed"),
                    encoding="utf-8")
    assert any("differs" in p for p in timeline.problems("demo", tmp_path))
    written(tmp_path)
    assert timeline.problems("demo", tmp_path) == []


def test_the_check_refuses_a_retrospective_with_no_date(tmp_path):
    subtree(tmp_path, retro="# Retrospective: undated\n\nBody.\n")
    written(tmp_path)
    assert any("no `**Date:** YYYY-MM-DD` line" in p for p in timeline.problems("demo", tmp_path))


def test_the_check_reads_no_clone(tmp_path, monkeypatch):
    """The runner holds no clones. Mutation: have `problems` refresh the
    snapshot through `clone_of` and this fails."""
    subtree(tmp_path)
    written(tmp_path)

    def no_clone(*_):
        raise AssertionError("the check reached for a clone")

    monkeypatch.setattr(timeline, "clone_of", no_clone)
    monkeypatch.setattr(timeline, "read_git", no_clone)
    assert timeline.problems("demo", tmp_path) == []


def test_every_committed_timeline_matches_its_inputs():
    """The committed subtrees, as the docs audit checks them."""
    names = timeline.with_subtree()
    assert names, "no project has a subtree"
    assert [p for name in names for p in timeline.problems(name)] == []


# --- reading git --------------------------------------------------------------


@pytest.fixture()
def clone(tmp_path: Path) -> Path:
    """A clone whose remote's default branch holds a GitHub merge, a squash
    merge and two tags; whose remote has a stack of three branches, `lower`,
    `middle` and `upper`, and a site's branch with no history in common; and
    whose local main is ahead of the remote."""
    origin = tmp_path / "origin"
    origin.mkdir()
    git("init", "-q", "-b", "main", cwd=origin)
    git("config", "user.email", "t@example.com", cwd=origin)
    git("config", "user.name", "T", cwd=origin)

    def commit(message: str, where: Path = origin) -> None:
        git("-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", message, cwd=where)

    commit("start")
    git("-c", "tag.gpgsign=false", "tag", "v0.0.1", cwd=origin)
    git("switch", "-q", "-c", "feature", cwd=origin)
    commit("work on the feature")
    git("switch", "-q", "main", cwd=origin)
    git("-c", "commit.gpgsign=false", "merge", "-q", "--no-ff", "feature", "-m",
        "Merge pull request #3 from example/feature\n\nThe feature lands", cwd=origin)
    commit("A small fix (#4)")
    commit("an unnumbered commit")
    git("-c", "tag.gpgsign=false", "tag", "-a", "v0.0.2", "-m", "v0.0.2", cwd=origin)
    for branch, commits in (("lower", 2), ("middle", 1), ("upper", 1)):
        git("switch", "-q", "-c", branch, cwd=origin)
        for n in range(commits):
            commit(f"{branch}, {n}")
    git("switch", "-q", "--orphan", "pages", cwd=origin)
    commit("a published site")
    git("switch", "-q", "main", cwd=origin)
    here = tmp_path / "clone"
    git("clone", "-q", str(origin), str(here), cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=here)
    git("config", "user.name", "T", cwd=here)
    commit("An unpushed fix (#9)", where=here)
    return here


def test_merged_pull_requests_and_tags_are_read_from_the_remote_branch(clone):
    """A GitHub merge, by its subject and the title in its body; a squash, by
    its numbered subject; and nothing the host does not hold. Mutation: read
    the local branch in place of `origin/main` and #9 appears."""
    facts = timeline.read_git(clone, "demo")
    assert facts["default_branch"] == "main" and facts["read_at"]["ref"] == "origin/main"
    merged = {m["pr"]: m for m in facts["merged"]}
    assert set(merged) == {3, 4}
    assert merged[3]["branch"] == "feature" and merged[3]["title"] == "The feature lands"
    assert merged[4]["branch"] is None and merged[4]["title"] == "A small fix"
    tags = {t["name"]: t["annotated"] for t in facts["tags"]}
    assert tags == {"v0.0.1": False, "v0.0.2": True}


def test_a_stack_of_branches_is_read_as_a_stack(clone):
    """Each branch the default branch does not hold is on the nearest branch
    its tip holds, with the commits it adds to it. A merged branch, a site's
    unrelated history and a branch the host does not have are left out.
    Mutation: pick the base by the fewest commits in place of the most and
    `upper` reads as on `lower`."""
    git("switch", "-q", "-c", "local-only", cwd=clone)
    git("-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", "unpushed", cwd=clone)
    branches = {b["name"]: b for b in timeline.read_git(clone, "demo")["branches"]}
    assert set(branches) == {"lower", "middle", "upper"}
    assert {name: (b["base"], b["commits"]) for name, b in branches.items()} == {
        "lower": ("main", 2), "middle": ("lower", 1), "upper": ("middle", 1)}


def test_a_written_snapshot_reads_back_as_the_same_facts(clone, tmp_path):
    import yaml
    facts = timeline.read_git(clone, "demo")
    assert yaml.safe_load(timeline.snapshot_text(facts)) == facts


def test_write_without_the_clone_fails_and_names_the_way_out(monkeypatch, capsys):
    monkeypatch.setattr(timeline, "clone_of", lambda name: None)
    assert timeline.main(["alfred", "--write"]) == 1
    said = capsys.readouterr().err
    assert "--clone" in said and "--offline" in said


# --- the tools that read the subtree ----------------------------------------


def test_a_project_page_links_its_subtree_only_when_it_has_a_timeline(tmp_path):
    """Mutation: drop the `is_file` test in `history_section` and a project
    with no timeline links a page that does not exist."""
    import cookbook
    assert cookbook.history_section("demo", tmp_path) == []
    subtree(tmp_path)
    assert cookbook.history_section("demo", tmp_path) == []
    written(tmp_path)
    body = "\n".join(cookbook.history_section("demo", tmp_path))
    assert "[demo's timeline](demo/timeline.md)" in body
    assert "[Retrospective: the first round](demo/retrospective-one.md) · 2026-01-06" in body


def test_the_subtree_is_classed_as_history_and_its_timeline_as_generated(tmp_path):
    """The cookbook writes every page under docs/projects/ except a project's
    subtree. Mutation: drop the subtree branch from `refresh_of` and a
    retrospective reads as a page the cookbook regenerates."""
    from doc_status import build, classify
    for rel, body in (("AGENTS.md", "#\n"), ("README.md", "#\n"), ("PRINCIPLES.md", "#\n"),
                      ("docs/projects/demo.md", "# demo\n"),
                      ("docs/projects/demo/timeline.md", "# t\n"),
                      ("docs/projects/demo/retrospective-one.md", RETRO)):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    rows = {d["path"]: d for d in build(tmp_path)["documents"]}
    assert rows["docs/projects/demo.md"]["refresh"].startswith("uv run qm cookbook")
    assert rows["docs/projects/demo/timeline.md"]["refresh"] == "uv run qm timeline demo --write"
    assert rows["docs/projects/demo/retrospective-one.md"]["state"] == "dated"
    assert classify(tmp_path / "docs/projects/demo/retrospective-one.md", tmp_path)[0] == "history"


def test_the_timeless_check_reads_a_subtree_as_dated_in_the_corpus_only():
    """A project's own docs/projects/ is timeless like the rest of its docs.
    Mutation: drop the `corpus` test from `checked` and the second assertion
    fails."""
    import check_timeless
    path = "docs/projects/demo/retrospective-one.md"
    assert not check_timeless.checked(path, corpus=True)
    assert check_timeless.checked(path, corpus=False)
    assert check_timeless.checked("docs/projects/demo.md", corpus=True)
