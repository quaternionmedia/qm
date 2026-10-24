"""One palette, measured: every reader takes its colours from ci/palette.py.

These hold the contrast floors a colour must clear to be used as text, the
agreement between the module and the stylesheet written from it, and the two
promises the site's look makes: no font from a font service, and no name set
in capitals.

What this cannot do: say a page is legible. It measures pairs of colours the
palette declares, and cannot see a colour a page sets for itself, a hue placed
on a ground it was not measured against, or a picture whose text is too small.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

CI = Path(__file__).resolve().parents[1]
ROOT = CI.parent
sys.path.insert(0, str(CI))

import dashboard_style  # noqa: E402
import families  # noqa: E402
import palette  # noqa: E402

READABLE = 4.5
SITE_CSS = ROOT / "docs" / "stylesheets"


def _channel(value: int) -> float:
    part = value / 255
    return part / 12.92 if part <= 0.04045 else ((part + 0.055) / 1.055) ** 2.4


def contrast(one: str, two: str) -> float:
    def luminance(colour: str) -> float:
        r, g, b = (_channel(int(colour[i:i + 2], 16)) for i in (1, 3, 5))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    first, second = sorted((luminance(one), luminance(two)), reverse=True)
    return (first + 0.05) / (second + 0.05)


TEXT = {**palette.FAMILY,
        **{k: palette.NEUTRAL[k] for k in ("ink", "muted", "accent")},
        **{k: v for k, v in palette.STATE.items() if not k.endswith("-bg")}}
GROUNDS = ("ground", "surface", "sunken")


@pytest.mark.parametrize("scheme", [palette.LIGHT, palette.DARK])
@pytest.mark.parametrize("name", sorted(TEXT))
def test_every_text_colour_is_readable_on_every_ground(name, scheme):
    """A hue is set as text -- a family's name, a link, a state -- so it clears
    4.5:1 on the page, a card and a code block, in its own scheme.

    Mutation: lighten `instruments` to #0c7a76 in light, and the sunken ground
    fails at 4.30:1.
    """
    for ground in GROUNDS:
        ratio = contrast(TEXT[name][scheme], palette.NEUTRAL[ground][scheme])
        assert ratio >= READABLE, f"{name} on {ground}: {ratio:.2f}:1"


@pytest.mark.parametrize("scheme", [palette.LIGHT, palette.DARK])
@pytest.mark.parametrize("state", ["ok", "warn", "unknown"])
def test_a_state_is_readable_on_its_own_pill(state, scheme):
    ratio = contrast(palette.STATE[state][scheme], palette.STATE[f"{state}-bg"][scheme])
    assert ratio >= READABLE, f"{state}: {ratio:.2f}:1"


def test_every_family_the_record_declares_has_a_hue():
    """A family drawn in the neutral is one nobody coloured. Renaming or adding
    a family in the record fails here until the palette names it.

    Mutation: drop `commons` from FAMILY and this fails.
    """
    missing = sorted(set(families.declared(ROOT / families.RECORD)) - set(palette.FAMILY))
    assert not missing, f"no hue for {missing}"


def test_the_site_stylesheet_is_the_one_the_palette_writes():
    """`palette.css` is written, never edited: a hand edit there would be a
    second palette the pictures and dashboards do not share."""
    written = (SITE_CSS / "palette.css").read_text(encoding="utf-8")
    assert written == palette.stylesheet(), (
        "docs/stylesheets/palette.css differs from ci/palette.py; regenerate with "
        "python ci/palette.py --write docs/stylesheets/palette.css")


def test_the_site_look_sets_no_colour_of_its_own():
    """Every colour in qm.css is a token, so a change of palette reaches it.

    Mutation: write `color: #fff` into any rule and this fails.
    """
    text = (SITE_CSS / "qm.css").read_text(encoding="utf-8")
    assert not re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", text)


def test_no_name_is_set_in_capitals():
    """The site, the dashboards and the pictures set a name as it is written.

    Mutation: add `text-transform: uppercase` to the h2 rule in qm.css and
    this fails.
    """
    sheets = [(SITE_CSS / name).read_text(encoding="utf-8")
              for name in ("qm.css", "palette.css", "glossary.css")]
    for sheet in [*sheets, dashboard_style.STYLE]:
        assert "uppercase" not in sheet and "small-caps" not in sheet


def test_the_site_loads_no_font_service_and_serves_every_face_it_names():
    """The fonts are the site's own copies; a font service would be a
    dependency loaded from somewhere else (`records/DRAFT-house-stack.md`).

    Mutation: remove `font = false` from zensical.toml, or delete one of the
    font files, and this fails.
    """
    config = (ROOT / "zensical.toml").read_text(encoding="utf-8")
    assert re.search(r"^font\s*=\s*false\s*$", config, re.MULTILINE)
    css = (SITE_CSS / "qm.css").read_text(encoding="utf-8")
    faces = re.findall(r'url\("\.\./(assets/fonts/[^"]+)"\)', css)
    assert faces, "qm.css names no font file"
    for face in faces:
        assert (ROOT / "docs" / face).is_file(), f"{face} is named and not served"


def test_the_stylesheets_load_palette_first():
    """The look reads the palette's tokens, so the palette loads before it."""
    config = (ROOT / "zensical.toml").read_text(encoding="utf-8")
    match = re.search(r"^extra_css\s*=\s*\[(.*?)\]", config, re.MULTILINE)
    assert match
    sheets = re.findall(r'"([^"]+)"', match.group(1))
    assert sheets[:2] == ["stylesheets/palette.css", "stylesheets/qm.css"]
