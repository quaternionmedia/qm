"""The glossary link is subtle, and subtle has a floor with a number in it.

WCAG 1.4.1 allows a colour-only link in body text when the colour clears 3:1
against the surrounding text and a non-colour cue appears on hover and focus.
On the light theme that is reachable. On `slate` it is not, and
`test_colour_alone_cannot_work_on_the_dark_theme` is the proof: body text there
is already near white, so any colour far enough from it to be distinguishable is
too dark to stay readable against the background. Searched over the sRGB cube;
no shade satisfies both.

So the cue is persistent: a dotted rule carries the "this is a link"
information, colour does no accessibility work and only has to stay readable,
and the difference in colour can be slight.

The site's ink and ground come from `ci/palette.py`; on its dark ground a
colour-only link would be reachable, so the rule is kept because the chosen
ink is quiet, and because a cue that is not colour suits every reader.

What this cannot do: say the page is accessible. It checks two ratios and the
presence of a cue. Whether a reader recognises the hint, and whether the word
was used in the glossary's sense at all, are not numbers.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

CSS = Path("docs/stylesheets/glossary.css")

# Normal text against its background. The link no longer needs 3:1 against body
# text, because the dotted rule is the non-colour cue -- but it still has to be
# readable.
READABLE = 4.5

# The site's ink and ground per scheme, read from the palette the site is
# drawn with (ci/palette.py), so a change of palette is measured here too.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import palette  # noqa: E402


def _rgb(value: str) -> tuple[int, int, int]:
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


THEME = {
    "light": {"body": _rgb(palette.NEUTRAL["ink"][palette.LIGHT]),
              "bg": _rgb(palette.NEUTRAL["ground"][palette.LIGHT])},
    "slate": {"body": _rgb(palette.NEUTRAL["ink"][palette.DARK]),
              "bg": _rgb(palette.NEUTRAL["ground"][palette.DARK])},
}


def _channel(value: int) -> float:
    part = value / 255
    return part / 12.92 if part <= 0.04045 else ((part + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[int, int, int]) -> float:
    red, green, blue = (_channel(c) for c in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(one: tuple[int, int, int], two: tuple[int, int, int]) -> float:
    first, second = sorted((luminance(one), luminance(two)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def parse(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def declared() -> dict[str, tuple[int, int, int]]:
    text = CSS.read_text(encoding="utf-8")
    blocks = {
        "light": re.search(r":root\s*\{(.*?)\}", text, re.DOTALL),
        "slate": re.search(r'\[data-md-color-scheme="slate"\]\s*\{(.*?)\}',
                           text, re.DOTALL),
    }
    found = {}
    for scheme, block in blocks.items():
        assert block, f"{scheme}: no block declaring the ink"
        match = re.search(r"--qm-glossary-ink:\s*(#[0-9a-fA-F]{6})",
                          block.group(1))
        assert match, f"{scheme}: no --qm-glossary-ink"
        found[scheme] = parse(match.group(1))
    return found


@pytest.mark.parametrize("scheme", list(THEME))
def test_the_ink_is_too_close_to_body_text_to_be_found_by_colour(scheme):
    """The glossary ink is chosen to be quiet: it sits under 3:1 against body
    text, so colour alone does not mark the term and the dotted rule is what
    carries "this is a link". The rule also asks nothing of colour vision.

    Mutation: give the ink a colour far from body text (3:1 or more) and this
    fails -- at which point the rule is a choice rather than a necessity, and
    the design should be revisited rather than kept out of habit.
    """
    ink = declared()[scheme]
    ratio = contrast(ink, THEME[scheme]["body"])
    assert ratio < 3.0, (
        f"{scheme}: the glossary ink is {ratio:.2f}:1 against body text, enough "
        f"to be found by colour alone -- the persistent rule is no longer forced")


@pytest.mark.parametrize("scheme", list(THEME))
def test_the_link_stays_readable_against_its_background(scheme):
    """Colour is not carrying the accessibility any more, but it still has to
    be text somebody can read.

    Mutation: move either ink toward its background and this fails.
    """
    ink = declared()[scheme]
    ratio = contrast(ink, THEME[scheme]["bg"])

    assert ratio >= READABLE, (
        f"{scheme}: {ratio:.2f}:1 against the background, below {READABLE}:1")


def test_the_cue_is_persistent_rather_than_only_on_hover():
    """The cue is visible at rest.

    A cue that appears only on hover leaves a reader who never hovers -- and
    every reader on paper -- with colour alone, which slate cannot support.

    Mutation: make the resting border transparent and this fails.
    """
    text = CSS.read_text(encoding="utf-8")
    rest = re.search(r"\.glossary-term\s*\{(?P<body>.*?)\}", text, re.DOTALL)
    assert rest, "no resting rule"
    body = rest.group("body")

    assert "border-bottom: 1px dotted" in body, "no cue at rest"
    assert "transparent" not in body, (
        "the resting cue is invisible, which is colour-only with extra steps")


def test_it_is_a_hint_and_not_a_full_underline():
    """Dotted, not a text-decoration underline sitting on the baseline.

    Mutation: use `text-decoration: underline` at rest and this fails.
    """
    text = CSS.read_text(encoding="utf-8")
    rest = re.search(r"\.glossary-term\s*\{(?P<body>.*?)\}", text, re.DOTALL)
    body = rest.group("body")

    assert "text-decoration: none" in body
    assert "dotted" in body


def test_the_cue_strengthens_on_hover_and_on_focus():
    text = CSS.read_text(encoding="utf-8")
    for needed in (":hover", ":focus"):
        assert f".glossary-term{needed}" in text, needed
    assert "border-bottom-style: solid" in text


def test_keyboard_focus_is_never_subtle():
    text = CSS.read_text(encoding="utf-8")
    assert ".glossary-term:focus-visible" in text
    assert "outline:" in text


def test_it_survives_a_printer_and_reduced_motion():
    text = CSS.read_text(encoding="utf-8")
    assert "@media print" in text
    assert "prefers-reduced-motion" in text


def test_the_measured_ratios_are_reported():
    """Printed rather than asserted-and-forgotten: the numbers are the whole
    argument for calling this subtle *and* accessible."""
    for scheme, ink in declared().items():
        against_bg = contrast(ink, THEME[scheme]["bg"])
        against_body = contrast(ink, THEME[scheme]["body"])
        print(f"  {scheme}: {against_bg:.2f}:1 vs background, "
              f"{against_body:.2f}:1 vs body text")
        assert against_bg >= READABLE
