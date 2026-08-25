"""The glossary link is subtle, and subtle has a floor with a number in it.

**THE BRIEF AND THE STANDARD PULLED AGAINST EACH OTHER ON ONE THEME**, and the
conflict is arithmetic rather than taste, so it was measured.

WCAG 1.4.1 allows a colour-only link in body text when the colour clears 3:1
against the surrounding text and a non-colour cue appears on hover and focus.
On the light theme that is reachable. On `slate` it is not, and
`test_colour_alone_cannot_work_on_the_dark_theme` is the proof: body text there
is already near white, so any colour far enough from it to be distinguishable is
too dark to stay readable against the background. Searched over the sRGB cube;
no shade satisfies both.

**SO THE CUE IS PERSISTENT, AND THAT BUYS THE SUBTLETY BACK.** Once a dotted
rule carries the "this is a link" information, colour is not doing accessibility
work and only has to stay readable. The difference in colour can be *slighter*
than the brief hoped for rather than louder.

WHAT THIS CANNOT DO. Say the page is accessible. It checks two ratios and the
presence of a cue. Whether a reader recognises the hint, and whether the word
was used in the glossary's sense at all, are not numbers.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

CSS = Path("docs/stylesheets/glossary.css")

# Normal text against its background. The link no longer needs 3:1 against body
# text, because the dotted rule is the non-colour cue -- but it still has to be
# readable.
READABLE = 4.5

# mkdocs-material's ink and ground per scheme, composited. `default` sets
# --md-typeset-color to rgba(0,0,0,.87) over white; `slate` to
# rgba(255,255,255,.87) over #1f2129. The compositing matters: .87 alpha is not
# the same colour as the solid.
THEME = {
    "light": {"body": (0x21, 0x21, 0x21), "bg": (0xFF, 0xFF, 0xFF)},
    "slate": {"body": (0xE0, 0xE1, 0xE4), "bg": (0x1F, 0x21, 0x29)},
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


def test_colour_alone_cannot_work_on_the_dark_theme():
    """THE MEASUREMENT THE WHOLE DESIGN RESTS ON.

    The brief asked for colour without an underline. On `slate` that is not a
    preference to weigh, it is unreachable: a link needs 3:1 against body text
    to be found by colour alone, and 4.5:1 against the background to be read.
    Body text is already near white, so nothing satisfies both.

    Searched over the sRGB cube at a stride of 3. If this ever passes -- a
    theme change, a palette change -- the persistent cue is no longer required
    and the design should be revisited rather than kept out of habit.
    """
    body, background = THEME["slate"]["body"], THEME["slate"]["bg"]

    possible = [
        (r, g, b)
        for r in range(0, 256, 3)
        for g in range(0, 256, 3)
        for b in range(0, 256, 3)
        if contrast((r, g, b), body) >= 3.0
        and contrast((r, g, b), background) >= READABLE
    ]

    assert not possible, (
        f"a colour-only link is reachable on slate after all "
        f"({len(possible)} shades, e.g. {possible[0]}) -- the persistent cue "
        f"is no longer forced and this design should be revisited")


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
    """THE ONE THE DARK THEME FORCED.

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
    """The half of the brief that survived: dotted, not a text-decoration
    underline sitting on the baseline.

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
