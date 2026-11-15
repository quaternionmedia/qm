# One page for two machines: a round of unification and polish

*Built on this branch, as far as "What this round did" says. "What it left" is
not built, and says why.*

## What this plans

The router joined the printer in the page, and a part went through the
subtractive loop on it (`project/plans/subtractive-loop-2026-11-04.md`). That walk
showed the page as two pages laid over each other: a printer's words and cards
written first, a router's beside them, each place deciding for itself which to
show. This round makes them one page: one vocabulary for a machine's kind, one
shape for what a board says of itself wherever it is said, and the surfaces the
loop passes through in the loop's order. It plans words, seats and shape in the
terms of `project/plans/ui-coordination-2026-10-31.md` (every section a window;
*Windows, not folds*), and it is measured as the census measures the page:
`apothecary census` counts the controls written into the page, and this round
leaves that count where it found it.

## What the walk found

Walked on the demo at a desktop's width, window by window, with the router's
Machine and its hour open:

- **Words.** A kind's words were in `machine.js`, its icon and class in
  `board_text.js`, the status words a person may set in the template; a router's
  Cut window was titled Print; a router's Reboot warned against a mid-print
  reset; a file picker on a router called its file sliced and said nothing is
  sent until Print.
- **Badges.** A printer's row read `🖨 23°/24°`, a router's a bare `🪚`.
- **The hour.** A router's hour in the Working space drew a legend of `printing`,
  `hotend` and `bed`, and had no strip colour for `running`, `hold` or `alarm`. A
  frame set kept at every 5 % read a card's progress alone, so neither a cut nor
  a print streamed from here ever reached one.
- **The Status card** broke a negative position across two lines, `Z-` then
  `40.00`, which reads as another number.
- **Selected** spent three rows on a position, showed `Material: —` and
  `Build volume: —` for what a piece does not have, and stood a loud blue button
  between a piece's facts and its part.
- **The Site list** said *(structure)* on nearly every row.
- **The Cut card** ran the loop backwards: the file and its verbs, then what the
  file makes and how it is written.
- **The Machine** opens alone, as a system's main window does, and nothing said
  its sections were there.
- **Styles.** Each of the Machine's and the Working space's sheets carried its own
  copy of the palette.

## What this round did

- `apothecary/static/machine_words.js` holds each kind's job, dialect, icon, words,
  bounds, files, the status words set by hand and what its volume is called;
  `machine.js`, `board_text.js` and the template read it, and
  `tests/test_machine_words.py` holds it to what the server says of the same
  things. Code still branches on a kind's name where the behaviour differs (which
  cards a kind renders); what it no longer does is spell the kind's words.
- A section's title follows the kind (`Section.titles`): a router's window is Cut.
- One badge grammar (`board_text.boardSummary`): the kind's icon, the state word,
  one reading -- a printer's temperatures, a router's spindle while it turns --
  and the job's progress, the class from one table. A row says the icon and the
  most useful of its reading, job or state. The `⚡` standing in the world stays:
  it says a board is here, whatever the board is.
- A machine's hour names what its hour holds: the states it was in and the readings
  it has, a router's spindle charted on its own scale, and a frame set kept at
  every 5 % of any job. `/sites/{name}/evidence/printers` lists a site's routers.
- Selected: a position on one line, only the facts a piece has, its volume in its
  kind's word, and a quiet Step into after the part's row.
- The Site row names a role only where it is not the usual one.
- The Print and Cut card in the loop's order: what it makes and its Slice or
  Toolpath, the file, the verbs, the progress.
- The Machine's head in three clusters that wrap as clusters; opening a Machine
  names its next step in the status line.
- `apothecary/static/tokens.css` holds the palette once, and colours that mean a
  token (ok, warn, bad, a line) read it in the page's style block and the sheets.
  Near-matches, and the Airgap's palette, its charts' own, are left alone.

## What it left

- **The Machine's main window at full size** is still a head, a state card and a
  paragraph. A door to each section would be new controls, against this round's
  measure, and opening the sections with it is against a tested decision
  (`test_a_system_opens_its_main_window_alone`); the status line names the view
  instead. Whether a Machine should open as its view is a person's call.
- **The cut in the hour**: the operation a cut is in is on the Machine's progress
  line, not yet beside each poll in the Working space (the loop plan's slice 3).
- **As cut, in the page**: the measure against the design runs in walkthrough 20
  and `tests/test_cam.py`, not yet in the Cut card. It has only the simulated
  router's trace to read, so it waits for what a real cut can be measured by.
- **The rings** are the server's (`menu.py`) and hold their own words.

### Not in this plan

- A new look: the page's palette, type and spacing stay; this round removes the
  places that differ from them.
- Folds, rails or overlays of any kind.
