"""One project read against its corpus, on repositories built for the purpose.

Every test builds a corpus and a project clone in a temporary tree with `git
fast-import`, so none passes because of the state this repository or any
sibling clone happens to be in. Each repository declares its remote-tracking
refs directly, as a fetch would have left them, and has no working tree: the
module reads refs, and a test that needed a checkout would be testing something
it does not do.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import project_review as pr  # noqa: E402

O = "refs/remotes/origin/"
SEED_LIST = "# a comment line\nadr-lint.yml required\nleak-check.yml copied\n"
SEED_AGENTS = ("<!-- SEED FILE: delete this comment. -->\n# AGENTS.md\n\n"
               "Pinned to `project/<name>`.\n\n<!-- Project-specific below. -->\n")
TEMPLATE = "# ADR-XXXX — Title\n"


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", check=True)
    return done.stdout.strip()


def commit(repo: Path, ref: str, files: dict[str, str], parent: str | None = None,
           gitlinks: dict[str, str] | None = None) -> str:
    """One commit on `ref` holding exactly `files`, by fast-import."""
    stream = [f"commit {ref}", "committer T <t@example.invalid> 1700000000 +0000",
              "data 1", "c"]
    if parent:
        stream.append(f"from {parent}")
    stream.append("deleteall")
    for path, text in files.items():
        raw = text.encode("utf-8")
        stream += [f"M 100644 inline {path}", f"data {len(raw)}", text]
    for path, sha in (gitlinks or {}).items():
        stream.append(f"M 160000 {sha} {path}")
    subprocess.run(["git", "-C", str(repo), "fast-import", "--quiet"],
                   input=("\n".join(stream) + "\n").encode("utf-8"), check=True)
    return git(repo, "rev-parse", ref)


def seed_files(**over: str) -> dict[str, str]:
    files = {
        "project-seed/ci/seed-workflows.txt": SEED_LIST,
        "project-seed/ci/adr-lint.yml": "name: ADR lint\n",
        "project-seed/ci/leak-check.yml": "name: Leak check\n",
        "project-seed/adr/TEMPLATE.md": TEMPLATE,
        "project-seed/ide/AGENTS.md": SEED_AGENTS,
        "project-seed/ide/CLAUDE.md": "@AGENTS.md\n",
    }
    files.update(over)
    return files


def current_project_files() -> dict[str, str]:
    return {
        ".gitmodules": ('[submodule "governance/qm"]\n\tpath = governance/qm\n'
                        "\turl = https://example.invalid/quaternionmedia/qm.git\n"
                        "\tbranch = project/demo\n"),
        ".github/workflows/adr-lint.yml": "name: ADR lint\n",
        ".github/workflows/leak-check.yml": "name: Leak check\n",
        "AGENTS.md": ("# AGENTS.md\n\nPinned to `project/demo`.\n\n"
                      "<!-- Project-specific below. -->\n\n## Building\n"),
        "CLAUDE.md": "@AGENTS.md\n",
    }


@pytest.fixture
def world(tmp_path) -> SimpleNamespace:
    """A corpus whose project branch is current, and a project that is too."""
    corpus, clone = tmp_path / "qm", tmp_path / "demo"
    for repo in (corpus, clone):
        subprocess.run(["git", "init", "--quiet", "--bare", str(repo)], check=True)
    main = commit(corpus, f"{O}main", seed_files())
    branch = commit(corpus, f"{O}project/demo",
                    seed_files(**{"adr/TEMPLATE.md": TEMPLATE,
                                  "adr/README.md": "On `project/demo`.\n"}),
                    parent=main)
    head = commit(clone, f"{O}main", current_project_files(),
                  gitlinks={"governance/qm": branch})
    git(clone, "symbolic-ref", f"{O}HEAD", f"{O}main")
    return SimpleNamespace(corpus=corpus, clone=clone, main=main, branch=branch, head=head)


def states(facts: list[pr.Fact]) -> dict[str, str]:
    return {f.subject: f.state for f in facts}


def test_a_current_project_reads_current_on_both_sides(world):
    facts = pr.corpus_side(world.corpus, "demo") + pr.project_side(
        world.corpus, world.clone, "demo")
    assert facts and {f.state for f in facts} == {pr.CURRENT}
    assert pr.exit_status(facts) == 0


def test_a_branch_behind_main_with_a_stale_template_and_a_placeholder(world):
    commit(world.corpus, f"{O}main",
           seed_files(**{"project-seed/adr/TEMPLATE.md": "# changed\n"}),
           parent=world.main)
    commit(world.corpus, f"{O}project/demo",
           seed_files(**{"adr/TEMPLATE.md": TEMPLATE,
                         "adr/README.md": "On `project/<name>`.\n"}),
           parent=world.branch)
    got = states(pr.corpus_side(world.corpus, "demo"))
    assert got == {"project/demo against main": pr.BEHIND,
                   "adr/TEMPLATE.md": pr.BEHIND, "adr/README.md": pr.BEHIND}


def test_a_project_with_no_branch_in_the_corpus_is_unknown(world):
    facts = pr.corpus_side(world.corpus, "nobody")
    assert [f.state for f in facts] == [pr.UNKNOWN]
    assert pr.exit_status(facts) == 1


def test_a_pin_behind_the_branch_tip_says_how_far(world):
    commit(world.corpus, f"{O}project/demo", seed_files(), parent=world.branch)
    pin = next(f for f in pr.project_side(world.corpus, world.clone, "demo")
               if f.subject == "governance pin")
    assert pin.state == pr.BEHIND and "1 commit(s) behind" in pin.detail


def test_a_pin_that_is_not_an_ancestor_of_the_branch_is_said_to_be(world):
    other = commit(world.corpus, "refs/heads/elsewhere", {"x": "x\n"})
    commit(world.clone, f"{O}main", current_project_files(), parent=world.head,
           gitlinks={"governance/qm": other})
    pin = next(f for f in pr.project_side(world.corpus, world.clone, "demo")
               if f.subject == "governance pin")
    assert pin.state == pr.BEHIND and "not an ancestor" in pin.detail


def test_a_seed_copy_that_differs_and_one_that_is_absent(world):
    files = current_project_files()
    files[".github/workflows/adr-lint.yml"] = "name: an older lint\n"
    del files[".github/workflows/leak-check.yml"]
    files["AGENTS.md"] = files["AGENTS.md"].replace("Pinned", "Once pinned")
    files["CLAUDE.md"] = "AGENTS.md"
    commit(world.clone, f"{O}main", files, parent=world.head,
           gitlinks={"governance/qm": world.branch})
    got = {f.subject: f for f in pr.project_side(world.corpus, world.clone, "demo")}
    assert got[".github/workflows/adr-lint.yml (required)"].detail.startswith("differs")
    assert got[".github/workflows/leak-check.yml (copied)"].detail == "absent"
    assert got["AGENTS.md governance section"].state == pr.BEHIND
    assert got["CLAUDE.md"].state == pr.BEHIND
    assert got["governance pin"].state == pr.CURRENT


def test_the_project_s_own_section_of_agents_md_is_not_compared(world):
    files = current_project_files()
    files["AGENTS.md"] += "\nAnything the project says about itself.\n"
    commit(world.clone, f"{O}main", files, parent=world.head,
           gitlinks={"governance/qm": world.branch})
    got = states(pr.project_side(world.corpus, world.clone, "demo"))
    assert got["AGENTS.md governance section"] == pr.CURRENT


def test_a_url_that_only_contains_the_corpus_name_is_not_the_corpus(world):
    files = current_project_files()
    files[".gitmodules"] = files[".gitmodules"].replace("/qm.git", "/qmetronome.git")
    commit(world.clone, f"{O}main", files, parent=world.head,
           gitlinks={"governance/qm": world.branch})
    assert pr.governance_mount(world.clone, "origin/main") is None
    got = states(pr.project_side(world.corpus, world.clone, "demo"))
    assert got["governance pin"] == pr.BEHIND


def test_the_working_tree_is_never_read(world):
    """Both repositories are bare. Every reading above was taken from refs."""
    assert git(world.clone, "rev-parse", "--is-bare-repository") == "true"


def test_a_write_or_a_fetch_is_refused_before_git_is_spawned(world):
    for verb in ("fetch", "checkout", "commit", "submodule"):
        with pytest.raises(pr.Refused):
            pr.run_git(world.corpus, verb)


NOW = datetime(2026, 1, 31, tzinfo=timezone.utc)


def answering(returncode: int, stdout: str = "", stderr: str = ""):
    def fake(args, cwd):
        fake.args = args
        return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)
    return fake


def test_a_host_that_does_not_answer_is_unknown_and_not_none(monkeypatch, tmp_path):
    monkeypatch.setattr(pr, "run_gh", answering(1, stderr="not logged in"))
    facts = pr.open_pull_requests("host", "o/r", tmp_path, NOW)
    assert [f.state for f in facts] == [pr.UNKNOWN]
    assert "not logged in" in facts[0].detail


def test_no_open_pull_request_is_current_and_each_open_one_is_behind(monkeypatch, tmp_path):
    monkeypatch.setattr(pr, "run_gh", answering(0, "[]"))
    assert [f.state for f in pr.open_pull_requests("host", "o/r", tmp_path, NOW)] == [pr.CURRENT]

    rows = ('[{"number": 7, "title": "A change", "isDraft": false, '
            '"baseRefName": "main", "updatedAt": "2026-01-01T00:00:00Z"}]')
    fake = answering(0, rows)
    monkeypatch.setattr(pr, "run_gh", fake)
    facts = pr.open_pull_requests("host", "o/r", tmp_path, NOW, base="project/demo")
    assert [(f.subject, f.state) for f in facts] == [("o/r#7", pr.BEHIND)]
    assert "30 day(s)" in facts[0].detail
    assert fake.args[-2:] == ["--base", "project/demo"]


def test_an_unknown_is_printed_as_one_and_fails_the_review():
    facts = [pr.Fact("corpus", "a", pr.CURRENT, "fine"),
             pr.Fact("host", "b", pr.UNKNOWN, "could not ask", "gh auth login")]
    text = pr.render("demo", facts)
    assert "unknown  b: could not ask" in text and "-> gh auth login" in text
    assert "0 behind, 1 unknown" in text
    assert pr.exit_status(facts) == 1


def test_a_project_with_no_clone_is_a_review_that_did_not_run(tmp_path, capsys):
    roster = tmp_path / "workspace.yaml"
    roster.write_text("repositories:\n  - name: demo\n    role: project\n"
                      "    paths: [demo]\n", encoding="utf-8")
    code = pr.main(["demo", "--roster", str(roster), "--search-root", str(tmp_path),
                    "--offline"])
    assert code == 2
    assert "no clone of demo" in capsys.readouterr().err
