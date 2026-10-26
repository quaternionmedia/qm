"""What `qm references` must find before a branch is retired, and what it skips.

Two layers, so the suite runs in seconds and a mutation sweep in minutes.

The rules are pure functions of text and names, and are tested as tables with
no git at all. The reads are tested once against one real repository, built
for the whole module by two `git fast-import` runs rather than by commits and
pushes per test: every reference this tool reports is a fact about refs and
the files they hold, and a mock would agree with whatever its author believed
about git. The host is stood in for at its one seam, `merge_review.gh`.

The mutations, per `a-check-is-evidence-after-it-fails`.
`uv run qm mutate ci/branch_references.py` kills every textual mutant but five,
each equivalent: `frozen=True` on `Reference`, which nothing mutates, and four
argparse help and description strings. The `__main__` guard gives no verdict.
Nine more, which no textual operator expresses, were each run alone against a
green baseline and restored, quoted as they printed:

  the generated documents not excluded from the grep
    FAILED test_offline[args4-0-expected4]
  the exit status always 0
    FAILED test_offline[args0-1-expected0], and seven more cases that expect 1
  a commit matched inside a longer word
    FAILED test_each_kind_of_reference_is_read_from_a_line[at abc1234f-kinds2]
    FAILED test_each_kind_of_reference_is_read_from_a_line[at fabc1234-kinds3]
  any page's backticked name counted as named
    FAILED test_only_main_s_namespace_page_names_a_ref[lines2-dev-found2]
    FAILED test_only_main_s_namespace_page_names_a_ref[lines3-dev-found3]
    FAILED test_only_main_s_namespace_page_names_a_ref[lines6-project/p-found6]
  a file the base already holds counted as the branch's
    FAILED test_a_file_is_cited_by_path_and_by_a_basename_the_base_does_not_share[added2-listing2-patterns2]
  every head's inherited copy of main's line reported again
    FAILED test_a_line_a_head_inherits_from_main_is_main_s_reference[wheres0-kept0]
    FAILED test_a_line_a_head_inherits_from_main_is_main_s_reference[wheres3-kept3]
    FAILED test_a_head_carrying_main_s_lines_adds_no_reference_of_its_own
  a pull request into a project branch searched in every file it carries
    FAILED test_a_scoped_head_counts_only_in_the_files_it_changes[wheres0-kept0]
    FAILED test_a_pull_request_into_a_project_branch_counts_only_in_what_it_changes
  a namespace the page calls permanent not reported
    FAILED test_only_main_s_namespace_page_names_a_ref[lines4-project/p-found4]
    FAILED test_offline[args6-1-expected6]
  the references listed in the order found
    FAILED test_a_documented_ref_is_listed_before_its_citations
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import branch_references as br  # noqa: E402
import merge_review  # noqa: E402
from branch_references import Reference  # noqa: E402

# --------------------------------------------------------------------------
# The rules, as tables
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name, said", [
    ("evolve/x", "evolve/x"),
    ("test", "`test`"),
])
def test_a_name_is_cited_as_written_with_a_slash_and_in_backticks_without(name, said):
    assert br.spoken(name) == said


@pytest.mark.parametrize("given, remote, name", [
    ("origin/evolve/x", "origin", "evolve/x"),
    ("refs/remotes/origin/evolve/x", "origin", "evolve/x"),
    ("refs/heads/dev", "origin", "dev"),
    ("evolve/x", "origin", "evolve/x"),
    ("refs/remotes/origin/evolve/x", "", "origin/evolve/x"),
])
def test_a_branch_is_named_without_its_ref_prefix(given, remote, name):
    assert br.short_name(given, remote) == name


def test_every_branch_but_this_one_counts_as_another():
    refs = {"refs/heads/x": "1", "refs/remotes/origin/x": "1",
            "refs/remotes/origin/HEAD": "2", "refs/remotes/origin/main": "2",
            "refs/heads/y": "3"}
    assert br.others(refs, "x", "origin") == ["refs/remotes/origin/main", "refs/heads/y"]


@pytest.mark.parametrize("added, listing, patterns", [
    (["h/research-workspaces.md"], {"README.md"},
     {"h/research-workspaces.md": "h/research-workspaces.md",
      "research-workspaces.md": "h/research-workspaces.md"}),
    (["notes/README.md"], {"README.md"}, {"notes/README.md": "notes/README.md"}),
    (["README.md"], {"README.md"}, {}),
])
def test_a_file_is_cited_by_path_and_by_a_basename_the_base_does_not_share(
        added, listing, patterns):
    assert br.file_patterns(added, listing) == patterns


Y = "refs/remotes/origin/y"
P = "refs/remotes/origin/project/p"


@pytest.mark.parametrize("heads, present, searched, scoped", [
    ([], set(), ["origin/main"], {}),
    ([("x", "main")], set(), ["origin/main"], {}),
    ([("y", "main")], {Y}, ["origin/main", "origin/y"], {}),
    ([("y", "main"), ("y", "main")], {Y}, ["origin/main", "origin/y"], {}),
    ([("y", "project/p")], {Y, P}, ["origin/main", "origin/y"],
     {"origin/y": "origin/project/p"}),
])
def test_every_open_head_but_the_branch_s_own_is_searched_and_scoped_by_its_base(
        heads, present, searched, scoped):
    assert br.searched_refs("x", "origin", "origin/main", "origin/main",
                            heads, present) == (searched, scoped)


def test_a_base_other_than_main_is_searched_too():
    assert br.searched_refs("x", "origin", "origin/main", "origin/project/p", [],
                            set()) == (["origin/main", "origin/project/p"], {})


@pytest.mark.parametrize("heads, present, missing", [
    ([("never", "main")], set(), "origin/never"),
    ([("y", "project/p")], {Y}, "origin/project/p"),
])
def test_a_ref_an_open_pull_request_needs_not_fetched_is_no_pass(heads, present, missing):
    with pytest.raises(br.Unreadable, match=f"not fetched, so not searched: {missing}"):
        br.searched_refs("x", "origin", "origin/main", "origin/main", heads, present)


@pytest.mark.parametrize("wheres, kept", [
    (["origin/y:copy.md:1:x", "origin/y:new.md:1:x"], ["origin/y:new.md:1:x"]),
    (["origin/main:copy.md:1:x"], ["origin/main:copy.md:1:x"]),
    (["origin/z:copy.md:1:x"], ["origin/z:copy.md:1:x"]),
])
def test_a_scoped_head_counts_only_in_the_files_it_changes(wheres, kept):
    found = [Reference("name", "x", where) for where in wheres]
    refs = ["origin/main", "origin/y", "origin/z"]
    assert [r.where for r in br.within(found, refs, {"origin/y": {"new.md"}})] == kept


@pytest.mark.parametrize("name, space", [
    ("project/p", "`project/<"),
    ("workspace/math-experiments", "`workspace/<"),
    ("dev", None),
])
def test_a_branch_s_namespace_is_written_as_the_namespace_page_writes_it(name, space):
    assert br.namespace_of(name) == space


@pytest.mark.parametrize("line, parsed", [
    ("origin/main:a.md:3:text", ("origin/main", "a.md", "text")),
    ("origin/main-x:a.md:3:t:u", ("origin/main-x", "a.md", "t:u")),
    ("origin/main:broken", None),
    ("elsewhere:a.md:1:text", None),
])
def test_a_grep_line_is_read_against_the_ref_its_colon_ends(line, parsed):
    assert br.split_line(line, ["origin/main", "origin/main-x"]) == parsed


SHA = "abc1234"


@pytest.mark.parametrize("text, kinds", [
    ("see evolve/x for it", ["name"]),
    (f"at `{SHA}`", ["commit"]),
    (f"at {SHA}f", []),
    (f"at f{SHA}", []),
    ("the fix was workspaces.md", ["file"]),
    ("both h/workspaces.md and workspaces.md", ["file"]),
    (f"evolve/x at {SHA}, workspaces.md", ["name", "commit", "file"]),
    ("nothing here", []),
])
def test_each_kind_of_reference_is_read_from_a_line(text, kinds):
    found = br.classify([f"origin/main:p.md:1:{text}"], ["origin/main"], "evolve/x",
                        [SHA], {"h/workspaces.md": "h/workspaces.md",
                                "workspaces.md": "h/workspaces.md"})
    assert [r.kind for r in found] == kinds


@pytest.mark.parametrize("wheres, kept", [
    (["origin/h:p.md:4:see x", "origin/main:p.md:3:see x"], ["origin/main:p.md:3:see x"]),
    (["origin/main:p.md:3:see x", "origin/h:p.md:3:see x, changed"],
     ["origin/main:p.md:3:see x", "origin/h:p.md:3:see x, changed"]),
    (["origin/h:q.md:3:see x"], ["origin/h:q.md:3:see x"]),
    (["origin/main:p.md:3:see x", "origin/main:p.md:9:see x"], ["origin/main:p.md:3:see x"]),
])
def test_a_line_a_head_inherits_from_main_is_main_s_reference(wheres, kept):
    found = [Reference("name", "x", where) for where in wheres]
    assert [r.where for r in br.distinct(found, ["origin/main", "origin/h"])] == kept


def test_a_line_from_a_ref_not_searched_is_ignored():
    assert br.classify(["elsewhere:p.md:1:evolve/x"], ["origin/main"], "evolve/x",
                       [], {}) == []


PAGE_LINE = "origin/main:docs/ref/namespaces.md:3:`test`, `dev` and `main` are stages."
ROW = "origin/main:docs/ref/namespaces.md:9:| `project/<name>` | records | permanent |"
SHORT_ROW = "origin/main:docs/ref/namespaces.md:9:| `evolve/<slug>` | work | deleted after merge |"


@pytest.mark.parametrize("lines, name, found", [
    ([PAGE_LINE], "dev", [Reference("named", "`dev`", PAGE_LINE)]),
    ([PAGE_LINE], "evolve/x", []),
    (["origin/main:other.md:3:`dev` is named here"], "dev", []),
    (["origin/x:docs/ref/namespaces.md:3:`dev`"], "dev", []),
    ([ROW], "project/p", [Reference("named", "project/*", ROW)]),
    ([SHORT_ROW], "evolve/x", []),
    (["origin/main:other.md:9:| `project/<name>` | permanent |"], "project/p", []),
])
def test_only_main_s_namespace_page_names_a_ref(lines, name, found):
    assert br.named(lines, name, "origin/main") == found


@pytest.mark.parametrize("ref, is_known", [
    ("origin/main", True),
    ("refs/remotes/origin/main", True),
    ("dev", True),
    ("abc1234", False),
])
def test_a_ref_in_the_listing_needs_no_rev_parse(ref, is_known):
    refs = {"refs/remotes/origin/main": "1", "refs/heads/dev": "2"}
    assert br.known(refs, ref) is is_known


def test_a_reported_line_is_cut_to_its_width():
    assert len(str(Reference("name", "n", "w" * 500))) == br.LINE_WIDTH


# --------------------------------------------------------------------------
# The reads, against one real repository
# --------------------------------------------------------------------------

ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
WHO = "committer Test <test@example.invalid> 1700000000 +0000"


def blob(path: str, text: str) -> str:
    data = text.encode("utf-8")
    return f"M 100644 inline {path}\ndata {len(data)}\n{text}\n"


def commit(ref: str, mark: int, parent: str | None, *files: tuple[str, str]) -> str:
    head = f"commit {ref}\nmark :{mark}\n{WHO}\ndata 4\nmsg\n"
    return head + (f"from {parent}\n" if parent else "") + \
        "".join(blob(path, text) for path, text in files) + "\n"


def fast_import(repo: Path, stream: str, marks: Path) -> None:
    subprocess.run(["git", "-C", str(repo), "fast-import", "--quiet",
                    f"--export-marks={marks}"],
                   input=stream.encode("utf-8"), check=True, env=ENV)


R = "refs/remotes/origin/"


@pytest.fixture(scope="module")
def repo(tmp_path_factory) -> tuple[Path, dict[str, str]]:
    """Every case's branch, cut from one base; then `main` citing some of them."""
    root = tmp_path_factory.mktemp("references")
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True, env=ENV)
    marks = root.parent / f"{root.name}.marks"
    fast_import(root, "".join([
        commit(f"{R}main", 1, None,
               ("docs/ref/namespaces.md", "# Branch namespaces\n\n"
                "`test`, `dev`, `prod` and `main` are stages.\n"
                "| `project/<name>` | one project's records | permanent |\n"
                "| `evolve/<slug>` | work in progress | deleted after merge |\n"),
               ("README.md", "# qm\n")),
        commit(f"{R}evolve/workspaces", 2, ":1",
               ("handbook/research-workspaces.md", "# Workspaces\n")),
        commit(f"{R}evolve/one", 3, ":1", ("one.md", "one\n")),
        commit(f"{R}evolve/shared", 4, ":1", ("shared.md", "shared\n")),
        f"reset {R}evolve/copy\nfrom :4\n\n",
        commit(f"{R}evolve/quiet", 5, ":1", ("quiet.md", "quiet\n")),
        commit(f"{R}evolve/target", 8, ":1", ("self.md", "this is evolve/target\n")),
        commit(f"{R}evolve/other", 9, ":1", ("other.md", "builds on evolve/target\n")),
        commit(f"{R}bare", 11, None, ("README.md", "# no namespace page\n")),
        commit(f"{R}project/p", 13, ":1", ("copy.md", "an old page cites evolve/workspaces\n")),
        commit(f"{R}evolve/proj", 14, ":13", ("new.md", "a record cites evolve/workspaces\n")),
        "reset refs/heads/dev\nfrom :1\n\n",
    ]), marks)
    sha = dict(line.split() for line in marks.read_text().splitlines())
    fast_import(root, commit(
        f"{R}main", 10, sha[":1"],
        ("perspectives/p.md", "The fix was `handbook/research-workspaces.md`.\n"),
        ("handoff.md", f"| qm | the page at `{sha[':3'][:7]}` | none |\n"
                       f"| qm | shared at `{sha[':4'][:7]}` |\n"
                       "| qm | evolve/workspaces | none |\n"),
        ("loose-ends.json", '{"branch": "evolve/quiet"}\n'),
        ("status/harness.yaml", "branch: evolve/quiet\n"),
    ) + commit(f"{R}evolve/later", 12, ":10", ("later.md", "later\n")), marks)
    return root, {"one": sha[":3"][:7]}


def run(root: Path, *args: str) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    code = br.run([*args, "--repo", str(root)], out, err)
    return code, out.getvalue() + err.getvalue()


OFFLINE = [
    (["evolve/workspaces"], 1, ["file    handbook/research-workspaces.md",
                                "origin/main:perspectives/p.md:1:",
                                "name    evolve/workspaces", "origin/main:handoff.md:3:"]),
    (["origin/evolve/one"], 1, ["commit  {one}",
                                "references to evolve/one (origin/evolve/one @"]),
    (["evolve/one", "--base", "origin/evolve/other"], 1,
     ["commit  {one}", "searched origin/main, origin/evolve/other; open pull "
                       "requests not searched (--offline); generated documents skipped"]),
    (["evolve/shared"], 0, ["Nothing searched refers to it.",
                            "Cannot see: another repository, a submodule pin among "
                            "them; pull request bodies, comments and issues."]),
    (["evolve/quiet"], 0, ["Nothing searched refers to it."]),
    (["dev"], 1, ["named   `dev`", "docs/ref/namespaces.md:3:", "(dev @"]),
    (["project/p"], 1, ["named   project/*", "docs/ref/namespaces.md:4:"]),
    (["evolve/nowhere"], 2, ["no branch 'evolve/nowhere', locally or on origin"]),
    (["evolve/quiet", "--base", "no-such-ref"], 2, ["git rev-parse"]),
    (["evolve/quiet", "--main", "origin/bare", "--base", "origin/bare"], 2,
     ["docs/ref/namespaces.md is not on origin/bare"]),
    (["evolve/quiet", "--main", "origin/bare", "--base", "origin/main"], 2,
     ["docs/ref/namespaces.md is not on origin/bare"]),
]


@pytest.fixture(scope="module")
def offline(repo) -> dict[tuple[str, ...], tuple[int, str]]:
    """Every offline case run once, together: each is mostly waiting on git."""
    root, _ = repo
    cases = [tuple(args) for args, _, _ in OFFLINE]
    with ThreadPoolExecutor(len(cases)) as pool:
        results = pool.map(lambda args: run(root, *args, "--offline"), cases)
        return dict(zip(cases, results))


@pytest.mark.parametrize("args, code, expected", OFFLINE)
def test_offline(repo, offline, args, code, expected):
    """A commit another branch holds (shared) and a generated document (quiet)
    are not references; the rest are, each by its kind; a main without the
    namespace page is a search that could not run, whatever the base."""
    got, out = offline[tuple(args)]
    assert got == code, out
    for text in expected:
        assert text.format(**repo[1]) in out, out


def test_a_documented_ref_is_listed_before_its_citations(offline):
    _, out = offline[("dev",)]
    assert out.index("named   `dev`") < out.index("name    `dev`"), out


def fake_host(monkeypatch, heads: list[str | tuple[str, str]] | None) -> list[tuple]:
    """The host's open pull requests: a head alone is into main."""
    calls: list[tuple] = []
    pairs = [(h, "main") if isinstance(h, str) else h for h in heads or []]

    def gh(*args):
        calls.append(args)
        body = "not json" if heads is None else json.dumps(
            [{"headRefName": head, "baseRefName": into} for head, into in pairs])
        return subprocess.CompletedProcess(("gh", *args), 0, body, "")

    monkeypatch.setattr(merge_review, "gh", gh)
    return calls


def test_an_open_head_is_searched_and_the_branch_s_own_is_not(repo, monkeypatch):
    calls = fake_host(monkeypatch, ["evolve/target", "evolve/other"])
    code, out = run(repo[0], "evolve/target")
    assert code == 1, out
    assert "origin/evolve/other:other.md:1:" in out
    assert "self.md" not in out
    assert "and 1 open pull request head(s)" in out
    assert calls[0][:2] == ("pr", "list")


def test_a_pull_request_into_a_project_branch_counts_only_in_what_it_changes(
        repo, monkeypatch):
    fake_host(monkeypatch, [("evolve/proj", "project/p")])
    code, out = run(repo[0], "evolve/workspaces")
    assert code == 1, out
    assert "origin/evolve/proj:new.md:1:" in out
    assert "copy.md" not in out


def test_a_pull_request_into_a_branch_not_fetched_is_no_pass(repo, monkeypatch):
    fake_host(monkeypatch, [("evolve/proj", "project/missing")])
    code, out = run(repo[0], "evolve/workspaces")
    assert code == 2, out
    assert "origin/project/missing" in out


def test_a_head_carrying_main_s_lines_adds_no_reference_of_its_own(repo, monkeypatch):
    fake_host(monkeypatch, ["evolve/later"])
    code, out = run(repo[0], "evolve/workspaces")
    assert code == 1, out
    assert "and 1 open pull request head(s)" in out
    assert "origin/evolve/later" not in out
    assert out.count("perspectives/p.md") == 1


@pytest.mark.parametrize("heads, says", [
    (["evolve/never-fetched"], "not fetched"),
    (None, "did not list"),
])
def test_a_search_that_cannot_run_is_no_pass(repo, monkeypatch, heads, says):
    fake_host(monkeypatch, heads)
    code, out = run(repo[0], "evolve/quiet")
    assert code == 2, out
    assert says in out


def test_the_route_is_registered_as_qm_references():
    import cli
    assert cli.ROUTES["references"] == ("branch_references", False, [])
