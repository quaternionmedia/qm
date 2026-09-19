"""What the prose reader quotes, and what it refuses to call prose.

Every case here is one the tool got wrong first. It quoted a row of badges as a
README's opening sentence, quoted the inside of a fenced code block, and treated
bold text at the start of a line as a bullet -- each fix revealing the next,
which is why the extraction is now strip-then-scan rather than skip-as-you-go.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ci import prose


def write(tmp_path: Path, body: str, name: str = "README.md") -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def test_the_opening_sentence_is_the_first_prose(tmp_path: Path):
    path = write(tmp_path, "# Title\n\nThis is the opening. And this is not.\n")
    heading, first, _ = prose.opening_of(path)
    assert heading == "Title"
    assert first == "This is the opening."


def test_bold_at_the_start_of_a_line_is_not_a_bullet(tmp_path: Path):
    """`**This page runs.**` was read as a list item, so collection began mid
    sentence and the tool reported a fragment as the page's opening."""
    path = write(tmp_path, "# Title\n\n**This page runs.** Every example is executed.\n")
    _, first, _ = prose.opening_of(path)
    assert first == "This page runs."


def test_a_badge_row_is_not_prose(tmp_path: Path):
    path = write(tmp_path, "# Title\n\n[![Build](https://img/b.svg)](https://ci)\n\n"
                           "The real opening.\n")
    _, first, _ = prose.opening_of(path)
    assert first == "The real opening."


def test_the_inside_of_a_fence_is_not_prose(tmp_path: Path):
    path = write(tmp_path, "# Title\n\n```sh\ngit clone https://example.com\n```\n\n"
                           "The real opening.\n")
    _, first, _ = prose.opening_of(path)
    assert first == "The real opening."


def test_html_blocks_are_not_prose(tmp_path: Path):
    path = write(tmp_path, '# Title\n\n<p align="center">\n<img src="a.svg">\n</p>\n\n'
                           "The real opening.\n")
    _, first, _ = prose.opening_of(path)
    assert first == "The real opening."


def test_a_blockquote_is_prose(tmp_path: Path):
    """It is usually the tagline directly under the title, which makes it the
    first thing a stranger reads even though markdown treats it as an aside."""
    path = write(tmp_path, "# Title\n\n> The tagline. More of it.\n")
    _, first, _ = prose.opening_of(path)
    assert first == "The tagline."


def test_front_matter_is_skipped(tmp_path: Path):
    path = write(tmp_path, "---\nicon: book\n---\n\n# Title\n\nThe opening.\n")
    _, first, _ = prose.opening_of(path)
    assert first == "The opening."


def test_a_page_with_no_prose_says_so(tmp_path: Path):
    path = write(tmp_path, "# Title\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    _, first, _ = prose.opening_of(path)
    assert first == ""
    assert [flag.label for flag in prose.flags_for(first, "")] == ["no prose"]


# --- the flags ---------------------------------------------------------------


def test_a_colon_and_a_list_of_nouns_is_flagged():
    """The sentence that produced the rule, from this corpus's own landing page."""
    sentence = ("The Quaternion Media constitution: the decisions that govern every "
                "QM project, the process that keeps them consistent, and the template "
                "each new project starts from.")
    labels = [flag.label for flag in prose.flags_for(sentence, sentence)]
    assert "colon early" in labels
    # Not flagged for vocabulary: it says "constitution", not one of the words
    # on the house list. A flag names what it can see, and this one could not
    # see the jargon that actually made the sentence hard.
    assert "house vocabulary" not in labels


def test_a_plain_opening_is_flagged_for_nothing():
    sentence = "Every team keeps answering the same questions."
    paragraph = sentence + " How does work get reviewed? Usually you ask somebody."
    assert prose.flags_for(sentence, paragraph) == []


def test_a_flag_is_never_a_failure(tmp_path: Path):
    """Exit zero unless a file cannot be read: this reports, it does not gate."""
    write(tmp_path, "# Title\n\nA corpus of records: one, two, three.\n")
    assert prose.main(["--root", str(tmp_path), "--path", "README.md"]) == 0


def test_house_words_are_flagged_only_when_used():
    assert "house vocabulary" not in [
        f.label for f in prose.flags_for("This tracks your work.", "This tracks your work. You run it.")]
    assert "house vocabulary" in [
        f.label for f in prose.flags_for("This holds the corpus.", "This holds the corpus. You read it.")]
