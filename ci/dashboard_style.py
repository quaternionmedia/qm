"""The one stylesheet every generated view is drawn with.

Its colours and fonts come from `ci/palette.py`, the palette the docs site and
the family pictures use, and every renderer imports it (the governance page,
the harness dashboard and the disk dashboard), so a reader comparing two pages
in the same window reads one colour system, and the semantic states mean the
same thing on each. Labels are set as written, never in capitals.

Three semantic states, and the third is the point

`ok`, `warn`, and `unknown`. A dashboard that has only the first two must
render a thing it could not measure as one of them, and it always picks the
reassuring one. `unknown` is a different colour, italic, and never green.

Three theme states, not two

The viewer's "system" setting stamps nothing on the root element, so the bare
`:root` block carries the complete light palette and the media query is guarded
against an explicit light choice. Every colour is a token defined on bare
`:root`; a colour whose only definition sits inside the media query renders one
theme's text on the other theme's ground.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from palette import DARK, FONTS, LIGHT, NEUTRAL, STATE  # noqa: E402


def _tokens(scheme: int) -> str:
    n = {name: pair[scheme] for name, pair in NEUTRAL.items()}
    s = {name: pair[scheme] for name, pair in STATE.items()}
    return (
        f"--ground: {n['ground']}; --panel: {n['surface']}; --ink: {n['ink']}; "
        f"--ink-soft: {n['muted']}; --line: {n['line']}; --accent: {n['accent']}; "
        f"--ok: {s['ok']}; --ok-bg: {s['ok-bg']}; --warn: {s['warn']}; "
        f"--warn-bg: {s['warn-bg']}; --unknown: {s['unknown']}; "
        f"--unknown-bg: {s['unknown-bg']};"
    )


STYLE = (
    f":root {{ {_tokens(LIGHT)} --font-body: {FONTS['body']}; "
    f"--font-mono: {FONTS['mono']}; --font-display: {FONTS['display']}; }}\n"
    "@media (prefers-color-scheme: dark) {\n"
    f"  :root:not([data-theme=\"light\"]) {{ {_tokens(DARK)} color-scheme: dark; }}\n"
    "}\n"
    f":root[data-theme=\"dark\"] {{ {_tokens(DARK)} color-scheme: dark; }}\n"
) + """* { box-sizing: border-box; }
body {
  margin: 0; background: var(--ground); color: var(--ink);
  font: 15px/1.55 var(--font-body);
}
main { max-width: 1180px; margin: 0 auto; padding: 2.2rem 1.4rem 4rem; }
h1 { font: 800 2.1rem/1.05 var(--font-display); margin: 0 0 .3rem; letter-spacing: .005em; text-wrap: balance; }
.stamp {
  display: flex; flex-wrap: wrap; gap: .4rem 1.1rem; align-items: baseline;
  color: var(--ink-soft); font-size: .85rem; margin-bottom: 1.6rem;
}
.stamp b { color: var(--ink); font-weight: 600; }
code, .mono { font-family: var(--font-mono); font-size: .92em; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .8rem; margin-bottom: 1.8rem; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: .8rem .9rem; }
.card .n { font-size: 1.7rem; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: -.02em; }
.card .l { color: var(--ink-soft); font: 500 .78rem/1.3 var(--font-mono); letter-spacing: .02em; }
.scroll { overflow-x: auto; border: 1px solid var(--line); border-radius: 6px; background: var(--panel); }
table { border-collapse: collapse; width: 100%; min-width: 900px; font-size: .88rem; }
th, td { text-align: left; padding: .5rem .7rem; border-bottom: 1px solid var(--line); vertical-align: top; }
thead th {
  position: sticky; top: 0; background: var(--panel); color: var(--ink-soft);
  font: 500 .76rem/1.3 var(--font-mono); letter-spacing: .02em;
}
tbody th { font-weight: 600; white-space: nowrap; }
tbody tr:last-child td, tbody tr:last-child th { border-bottom: 0; }
td { font-variant-numeric: tabular-nums; }
.s-ok { color: var(--ok); }
.s-warn { color: var(--warn); font-weight: 600; }
.s-unknown { color: var(--unknown); font-style: italic; }
.s-muted { color: var(--ink-soft); }
.sub { color: var(--ink-soft); font-size: .85em; }
.pill {
  display: inline-block; padding: .08rem .42rem; border-radius: 3px;
  font-size: .76rem; white-space: nowrap; margin: 1px 0;
}
.p-ok { background: var(--ok-bg); color: var(--ok); }
.p-warn { background: var(--warn-bg); color: var(--warn); }
.p-unknown { background: var(--unknown-bg); color: var(--unknown); }
.pr { font-family: var(--font-mono); font-size: .8rem; margin-right: .35rem; }
h2 { font: 800 1.45rem/1.1 var(--font-display); letter-spacing: .005em; margin: 2.2rem 0 .3rem; }
h2 + p { margin-top: 0; color: var(--ink-soft); font-size: .87rem; }
.gap { border-left: 2px solid var(--line); padding: .1rem 0 .1rem .9rem; margin: 1rem 0; }
.gap h3 { font-size: .9rem; margin: 0 0 .2rem; font-family: var(--font-mono); color: var(--accent); }
.gap p { margin: .2rem 0; font-size: .87rem; }
footer { margin-top: 2.5rem; color: var(--ink-soft); font-size: .8rem; border-top: 1px solid var(--line); padding-top: .9rem; }

/* State carried in form as well as colour, so a row needing attention reads
   at a glance and survives being printed or read without colour. */
tbody tr.over th { box-shadow: inset 3px 0 0 var(--warn); }
tbody tr.unmeasured th { box-shadow: inset 3px 0 0 var(--unknown); }
.legend { display: flex; flex-wrap: wrap; gap: .5rem .9rem; font-size: .8rem; color: var(--ink-soft); margin: .6rem 0 0; }
.reason { color: var(--ink-soft); font-size: .82em; font-style: italic; }
.q { border-left: 2px solid var(--accent); padding: .1rem 0 .1rem .9rem; margin: .9rem 0; }
.q p { margin: .25rem 0; font-size: .88rem; }
a { color: var(--accent); }
a:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
"""
