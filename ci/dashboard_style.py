"""The one stylesheet both governance views are drawn with.

Extracted so there is a single definition of the palette. Two renderers each
carrying their own copy is the same failure this corpus keeps finding in its
prose: a fact stated twice, edited once. A reader comparing two governance
pages in the same window should not be reading two colour systems, and the
semantic states in particular must mean the same thing on both.

THREE SEMANTIC STATES, AND THE THIRD IS THE POINT

`ok`, `warn`, and `unknown`. A dashboard that has only the first two must
render a thing it could not measure as one of them, and it always picks the
reassuring one. `unknown` is a different colour, italic, and never green.

THREE THEME STATES, NOT TWO

The viewer's "system" setting stamps nothing on the root element, so the bare
`:root` block carries the complete light palette and the media query is guarded
against an explicit light choice. Every colour is a token defined on bare
`:root`; a colour whose only definition sits inside the media query renders one
theme's text on the other theme's ground.
"""

STYLE = """
:root {
  --ground: #fbfaf8; --panel: #ffffff; --ink: #1b1a17; --ink-soft: #5d5a52;
  --line: #e2ded6; --accent: #2f5d50;
  --ok: #2f6b4f; --ok-bg: #e8f1ea; --warn: #8a5a12; --warn-bg: #f8eedb;
  --unknown: #4a4a8a; --unknown-bg: #eceaf6;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground: #16171a; --panel: #1d1f23; --ink: #e9e6e0; --ink-soft: #a3a09a;
    --line: #32353b; --accent: #7fbaa6;
    --ok: #7fbaa6; --ok-bg: #1e2a26; --warn: #d6a45a; --warn-bg: #2c2418;
    --unknown: #9d9ad6; --unknown-bg: #23233a;
  }
}
:root[data-theme="dark"] {
  --ground: #16171a; --panel: #1d1f23; --ink: #e9e6e0; --ink-soft: #a3a09a;
  --line: #32353b; --accent: #7fbaa6;
  --ok: #7fbaa6; --ok-bg: #1e2a26; --warn: #d6a45a; --warn-bg: #2c2418;
  --unknown: #9d9ad6; --unknown-bg: #23233a;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--ground); color: var(--ink);
  font: 15px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
}
main { max-width: 1180px; margin: 0 auto; padding: 2.2rem 1.4rem 4rem; }
h1 { font-size: 1.5rem; margin: 0 0 .2rem; letter-spacing: -.01em; text-wrap: balance; }
.stamp {
  display: flex; flex-wrap: wrap; gap: .4rem 1.1rem; align-items: baseline;
  color: var(--ink-soft); font-size: .85rem; margin-bottom: 1.6rem;
}
.stamp b { color: var(--ink); font-weight: 600; }
code, .mono { font-family: ui-monospace, "Cascadia Mono", Menlo, monospace; font-size: .92em; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .8rem; margin-bottom: 1.8rem; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: .8rem .9rem; }
.card .n { font-size: 1.7rem; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: -.02em; }
.card .l { color: var(--ink-soft); font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; }
.scroll { overflow-x: auto; border: 1px solid var(--line); border-radius: 6px; background: var(--panel); }
table { border-collapse: collapse; width: 100%; min-width: 900px; font-size: .88rem; }
th, td { text-align: left; padding: .5rem .7rem; border-bottom: 1px solid var(--line); vertical-align: top; }
thead th {
  position: sticky; top: 0; background: var(--panel); color: var(--ink-soft);
  font-size: .72rem; text-transform: uppercase; letter-spacing: .06em; font-weight: 600;
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
.pr { font-family: ui-monospace, monospace; font-size: .8rem; margin-right: .35rem; }
h2 { font-size: 1rem; margin: 2.2rem 0 .3rem; }
h2 + p { margin-top: 0; color: var(--ink-soft); font-size: .87rem; }
.gap { border-left: 2px solid var(--line); padding: .1rem 0 .1rem .9rem; margin: 1rem 0; }
.gap h3 { font-size: .9rem; margin: 0 0 .2rem; font-family: ui-monospace, monospace; color: var(--accent); }
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
