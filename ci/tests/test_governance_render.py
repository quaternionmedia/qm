"""The renderer's red paths.

A dashboard fails differently from a check: it does not report the wrong answer,
it draws a reassuring picture of one. The cases below are the four ways that
happens -- an absent document rendered as an empty page, an unknown rendered as
a blank cell, a stale document rendered as a current one, and a project with
drift rendered identically to one without.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

from governance_fixtures import run_tool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import governance_render as gr  # noqa: E402

DOC = {
    "schema": 1,
    "generated_at": "2026-01-01T00:00:00Z",
    "generator": {"org": "example", "layers": ["git"], "unknowns": 3},
    "corpus": {
        "ref": "origin/main",
        "commit": "b94d91085ba728788ede43e7ab4865ecb21c9261",
        "committed_at": "2026-01-01T00:00:00Z",
        "records": {"total": 10, "ratified": 0},
    },
    "projects": [
        {
            "name": "clean",
            "branch": {"behind_corpus": 0, "ahead_of_corpus": 1,
                       "last_propagation": {"committed_at": "2026-01-01T00:00:00Z"}},
            "records": {"total": 2, "ratified": 1},
            "seed": {"adr_template_vs_merge_base": "match", "readme_seed_comment_left_in": False},
            "adoption": {"submodule": {"corpus_mounted_at": "governance/qm", "branch": "project/clean"},
                         "ide": [], "ide_missing": [], "seed_workflow_filenames_absent": [],
                         "licensing": ["LICENSE", "REUSE.toml"]},
            "open_prs": [],
        },
        {
            "name": "drifted",
            "branch": {"behind_corpus": 62, "ahead_of_corpus": 6, "last_propagation": None},
            "records": {"total": 4, "ratified": 0},
            "seed": {"adr_template_vs_merge_base": "drift", "readme_seed_comment_left_in": True},
            "adoption": {"submodule": {"corpus_mounted_at": None, "branch": None},
                         "ide": [], "ide_missing": ["AGENTS.md"],
                         "seed_workflow_filenames_absent": ["adr-lint.yml"], "licensing": []},
            "open_prs": [{"number": 29, "head": "propagate/drifted", "draft": True, "title": "t"}],
        },
        {
            "name": "unreachable",
            "branch": {"behind_corpus": 7, "ahead_of_corpus": 2, "last_propagation": None},
            "records": {"unknown": "no adr at deadbeef"},
            "seed": {"adr_template_vs_merge_base": {"unknown": "no seed"},
                     "readme_seed_comment_left_in": {"unknown": "no readme"}},
            "adoption": {"unknown": "gh api repos/example/unreachable: HTTP 404"},
            "open_prs": {"unknown": "gh api pulls: HTTP 403"},
        },
    ],
    "org": {"repositories": {"total": 109, "governed": 8}},
    "undefined": [{"term": "adopted", "why_not_computed": "no definition exists",
                   "would_be_settled_by": "a record"}],
}


def test_an_absent_document_is_a_failure_not_an_empty_page(tmp_path):
    proc = run_tool("governance_render.py", str(tmp_path / "nope.yaml"), cwd=tmp_path)
    assert proc.returncode == 2
    assert "no document" in proc.stderr


def test_a_file_that_is_not_a_status_document_is_refused(tmp_path):
    doc = tmp_path / "other.yaml"
    doc.write_text("hello: world\n", encoding="utf-8", newline="\n")
    proc = run_tool("governance_render.py", str(doc), cwd=tmp_path)
    assert proc.returncode == 2


def test_an_unknown_is_visibly_distinct_from_a_value_and_from_a_zero():
    """`null` renders as blank, blank reads as fine.

    The project nobody could measure must not look like the healthy one.
    """
    page = gr.render(DOC)
    row = re.search(r"<tr>.*?unreachable.*?</tr>", page, re.S).group(0)
    assert "s-unknown" in row
    assert row.count(">unknown<") >= 2


def test_the_reason_an_unknown_is_unknown_survives_into_the_page():
    page = gr.render(DOC)
    assert "HTTP 404" in page and "HTTP 403" in page


def test_drift_is_distinguished_in_form_and_not_only_in_words():
    page = gr.render(DOC)
    clean = re.search(r"<tr>.*?>clean<.*?</tr>", page, re.S).group(0)
    drifted = re.search(r"<tr>.*?>drifted<.*?</tr>", page, re.S).group(0)
    assert "s-warn" in drifted and "s-warn" not in clean


def test_a_branch_that_never_propagated_says_never_rather_than_nothing():
    page = gr.render(DOC)
    drifted = re.search(r"<tr>.*?>drifted<.*?</tr>", page, re.S).group(0)
    assert ">never<" in drifted


def test_the_generation_time_is_shown_not_buried():
    """A page that looks live and is three days old stops people checking."""
    page = gr.render(DOC)
    header = page[: page.index("<div class=\"cards\">")]
    assert DOC["generated_at"] in header


def test_no_adopted_verdict_is_rendered():
    """The corpus defines no adoption predicate, so no view may assert one.

    Scoped to the table, because the word appears legitimately further down --
    as the name of a term the document says it did not compute, which is the
    opposite of asserting it.
    """
    page = gr.render(DOC)
    table = page[page.index("<table>") : page.index("</table>")]
    assert not re.search(r"adopted", table, re.I)


def test_the_undefined_terms_are_shown_to_the_reader():
    page = gr.render(DOC)
    assert "no definition exists" in page


def test_a_pull_request_title_containing_markup_is_escaped():
    doc = {**DOC, "projects": [
        {**DOC["projects"][1],
         "open_prs": [{"number": 1, "head": "x", "draft": False,
                       "title": '<script>alert("x")</script>'}]}
    ]}
    page = gr.render(doc)
    assert "<script>" not in page and "&lt;script&gt;" in page


@pytest.mark.parametrize("theme_block", [":root {", "prefers-color-scheme: dark", '[data-theme="dark"]'])
def test_the_page_defines_all_three_theme_states(theme_block):
    assert theme_block in gr.render(DOC)


def test_every_colour_token_is_defined_on_bare_root():
    """A token defined only inside a media query never applies to the default.

    The viewer's "system" setting stamps nothing on the root element, so a
    colour whose only definition sits behind [data-theme] renders one theme's
    text on the other theme's ground.
    """
    page = gr.render(DOC)
    bare = re.search(r":root \{(.*?)\}", page, re.S).group(1)
    defined = set(re.findall(r"(--[a-z-]+)\s*:", bare))
    used = set(re.findall(r"var\((--[a-z-]+)\)", page))
    assert not used - defined


def test_the_page_closes_every_tag_it_opens():
    import html.parser

    void = {"meta", "br", "img", "hr", "input", "link"}

    class P(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.stack, self.bad = [], []

        def handle_starttag(self, tag, attrs):
            if tag not in void:
                self.stack.append(tag)

        def handle_endtag(self, tag):
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            else:
                self.bad.append(tag)

    parser = P()
    parser.feed(gr.render(DOC))
    assert not parser.bad and not parser.stack


def test_the_renderer_never_shells_out():
    """It reads a document. Anything else would be a second definition."""
    source = (Path(gr.__file__)).read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "import os" not in source
