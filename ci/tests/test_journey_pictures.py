"""The journeys' pictures publish what a person sees, and never the archive's
titles, which are the operator's own conversations.

Offline: the browser and the terminal front end are not driven here; their
pictures are taken by `uv run qm journey-pictures` against running surfaces.
"""

from __future__ import annotations

import sys
from pathlib import Path

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import journey_pictures  # noqa: E402

SCREEN = ('<svg width="100" height="300" viewBox="0 0 100 300">'
          '<text x="0" y="20">harness&#160;reachable</text>'
          '<text x="0" y="60">Thread&#160;</text><text x="40" y="60">archive&#160;--</text>'
          '<text x="0" y="80">a private conversation title</text></svg>')


def test_a_cut_picture_holds_nothing_from_below_the_cut():
    """A crop that only moved the viewBox would hide the titles and still
    publish them in the file. Mutation: keep the rows below the cut, and this
    fails."""
    cut = journey_pictures.above(SCREEN, "Thread archive")
    assert "harness" in cut
    assert "private" not in cut and "Thread" not in cut
    assert 'viewBox="0 0 100 52"' in cut and 'height="52"' in cut


def test_a_screen_without_the_marker_is_not_kept():
    assert journey_pictures.above(SCREEN, "nowhere on this screen") is None
