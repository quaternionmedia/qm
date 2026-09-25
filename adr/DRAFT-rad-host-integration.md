# ADR-XXXX — rad host integration for apothecary: the rings address nine cells

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-19 |
| **Pends on** | Ratification of rad's own record *The menu addresses nine cells* (`quaternionmedia/rad`, `adr/DRAFT-the-menu-addresses-nine-cells.md`). This record adopts it verbatim; it cannot be Accepted while the thing it adopts is a draft. |
| **Tools** | Drafted with Claude Code (Anthropic) against the integration branch `consolidate/2026-09-19`, with the counts below produced by running `apothecary census`; the human who sponsored the work is the contributor of record. |

## Context

The viewer (`templates/fractal_viewer.html.j2`) is a page of controls of
its own: a toolbar, a job form, a Selected panel with boxes and buttons, a
serial log overlay, and — since the printer seam — a Device section for the
board pinned to a piece. The monitor page (`templates/monitor.html.j2`) is
another: a header of buttons and, behind a latch, a control overlay that
heats, homes and jogs a machine. Every one of those controls was invented for
one job, and each new feature has added more. The census
(`apothecary/census.py`, `apothecary census`) counts them from the page's
own markup and refuses to give a number when it meets one nobody has
classified; the count went from twenty to thirty-three to fifty-four on the
viewer, and the monitor stands at fifty-one. The doctrine behind the census
is that a page full of controls of its own becomes one ring, and the number
falls to nothing — but until now there was no ring for it to fall toward.

rad (`quaternionmedia/rad`, Apache-2.0, `"private": true` at `0.0.0`, no npm
export) is the organisation's radial menu: a contract for a ring of at most
eight options under a finger, with a resolver that is a plain function over
data, a state machine, a polar geometry, and conformance vectors that hold
any implementation to it. Its interaction contract is polar first, which is
right for a finger and gives a keyboard nowhere to stand: a position has no
name, every item costs a walk, and a direction and a position are unrelated.
rad's *The menu addresses nine cells* record answers that with a numbering —
a numeric keypad — under which geometry is a rendering of the cells rather
than the addressing itself. It was evidenced there by one terminal
implementation and asks for a second host.

Apothecary is that second host, and a demanding one: it has a pointer *and*
a keyboard, it has nested rings (a piece › its board › the board's controls),
and it has controls whose consequences are physical. A ring that a person
could not use without looking, or whose cells moved when the resolver
returned a different menu, would be worse than the buttons it replaced.

Licensing: rad is Apache-2.0, which passes the open-license record. Nothing
of rad's JavaScript is copied in; apothecary's `apothecary/static/ring.js` is
its own implementation of rad's contract, held to rad's vectors. The
rendering library the viewer already loads from a CDN is the adoption
record's existing gap and is not widened here.

## Decision

**Apothecary hosts rad's rings, and adopts rad's nine-cells addressing as its
standard for every ring it draws.** The specifics:

1. **A ring is nine cells numbered as a numeric keypad.** `7 8 9 / 4 5 6 /
   1 2 3` is up-left, up, up-right / left, back, right / down-left, down,
   down-right. Each cell has one stable number and one direction, and they
   are the same thing. Eight cells hold options; **cell 5 holds none, ever**:
   it backs out one level and closes the ring at the top. An empty cell is
   drawn faint and cannot be chosen.

2. **Placement is cardinals first**, `PLACEMENT = (8, 6, 2, 4, 9, 3, 1, 7)`:
   the i-th option of a ring sits in cell `PLACEMENT[i]`. A four-option ring
   sits at up, right, down and left. Eight is the ceiling, structurally.
   `apothecary/menu.py` is the only place a cell is written; an option built
   with a cell chosen by hand is refused.

3. **Geometry renders the cells.** The browser draws eight fixed 45-degree
   compass wedges, up being cell 8, clockwise `8 9 6 3 2 1 4 7`. rad's
   `angleToIndex` with rad's geometry (start −90°, clockwise) gives the
   compass slot, and `COMPASS` names the cell that slot draws. rad's polar
   vectors remain valid unchanged.

4. **Digits, arrows and the address.** A digit 1–9 other than 5 chooses its
   cell from anywhere; an arrow moves the highlight to the *nearest occupied
   cell in that direction* — not a row or column walk, so from cell 8 in a
   four-option ring Left reaches 4 — by one rule both the Python resolver
   and the browser implement and `tests/conformance/nine_cells.json` holds
   them to; 5 or Backspace backs out; Escape closes; Enter commits; two
   arrows inside 150 ms are the corner between them, and the same corner is
   reachable by walking. **The digits pressed to reach an option through
   nested rings are its address** (`2728` is Device › Control › Jog › Y+ from
   a printer's node). Given the same context the same address reaches the
   same option. Every `Intent` carries its address; a log of choices reads as
   something a person could type back.

5. **The census is the enforcement.** `apothecary census` counts each page's
   controls of its own and, beside that, how many of them are *ring-backed*:
   a control whose verb is a cell of some ring (`census.RING_BACKED`,
   checked against `apothecary.menu`'s vocabulary so no control can claim a
   backing that no ring produces). The meter does not fall because a control
   is backed; it falls when the backed control is deleted. The migration is
   therefore one sentence, repeated: a control gains its ⌗ address (written
   into its tooltip, where the control is), is used from the ring, and goes.
   The count is refused for any control nobody has classified, so a control
   cannot appear without somebody deciding what kind of thing it is.

6. **Three shapes of ring**, resolved server-side by `apothecary/menu.py`
   from what the page says it is pointing at (`POST /menu/resolve`), with
   every option returned in its cell:
   - the **node ring**, on a piece: zoom in, move, a Device option when a
     board is pinned to the piece (absent, not greyed, when none is), a Word
     option when the piece came from a picture, get shape, why this;
   - the **canvas ring**, on empty scene: arrangements and groups (each a
     further ring, lettered into groups of eight when longer), fit, reset;
   - the **device ring**, on a board: watch, poll, monitor, query, pin or
     unpin, rescan, and — for a printer only — a **control ring** behind it:
     heat, home, jog (seated so the keypad *is* the jog pad: Y+ up, X+
     right, Y− down, X− left, Z± in the right-hand corners), fan, SD, motors
     off, stop (marked destructive), arm or disarm. On the monitor page the
     device ring is the top ring, titled by the port.

   Every device and control verb is the viewer's to carry out
   (`CARRIED_BY`): the ring hands the choice to the handler the page already
   has, the monitor's control chain checks the latch and the allowlist, and
   the intent route never opens a port. An option with nothing behind it is
   refused by name, not answered with a cheerful 200.

7. **What stays in rad, and what is here.** rad owns the contract: the state
   machine, the polar geometry and its radii, the commit styles, the chord
   window, the nine-cells numbering, and the conformance vectors that hold
   any implementation to all of it. Apothecary owns the host: the resolver
   and its verbs (`apothecary/menu.py`), the two routes
   (`apothecary/routes/menu.py`), the drawing and keys (`apothecary/static/
   ring.js`, a plain ES module with no build step, held to rad's vectors and
   to `tests/conformance/nine_cells.json`, which `tests/test_menu.py`
   generates from the Python rules), and the census. A change to how a ring
   behaves is a change to rad's record first; a change to what a ring offers
   is a change here.

## Consequences

- **The ring is usable without looking.** Any leaf is reachable from idle in
  as many presses as its address has digits, plus the one that opens the
  ring, from anywhere on the page. Accepted cost: the digit keys and `m` are
  taken while nothing is being typed into, and the ring swallows every key
  while it is open, so the viewer's Backspace-steps-out does not fire under
  an open ring — the hub is Backspace there.
- **Repeatability is now a property, not a hope.** An address is stable
  across sessions for the same context because placement is a function of
  option order, and option order is the resolver's, tested. The cost is that
  reordering a ring's options moves every address beneath them. Accepted:
  that is what "stable" has to mean, and a reorder is a deliberate edit to
  `menu.py` that the address tests will name.
- **The meter went up before it goes down.** Fifty-four on the viewer,
  fifteen of them ring-backed; fifty-one on the monitor, twenty-eight
  ring-backed. Nothing was reclassified to make the number smaller. The
  obligation this creates: each release removes ring-backed controls, and
  the census docstring says by how many; a release in which the meter rises
  with no ring-backed controls deleted is a release that added a surface.
- **Two pages, two numbers, never added.** The monitor is counted with
  `census.take(census.MONITOR)`. Every button that acts on the machine or
  its link has a cell: the link's own verbs (reconnect, reset, release) sit
  under a Link cell that keeps the same number on a devkit and a printer,
  and the motor verbs share one cell. What is not backed is the page's
  plumbing — which port, how often, the log's tick-boxes — and it is said so
  rather than quietly backed by the nearest thing.
- **Conformance runs on both sides.** The Python `nearest`, `place`, `walk`
  and `address_of` and the browser's `nearest`, `withCells`, `addresses` and
  `cellAtAngle` are compared through one JSON file; a divergence is a failing
  unit test, not a screenshot.
- **The ring's own listeners are the ring's.** The census counts one control
  for the ring on each page, the button that opens it; the `m` key and
  right-click live in the module and a test holds the module to exactly
  those two on the window and document. A fourth way in would be one the
  census cannot see, and is refused there.
- **rad gains its second host**, with both a pointer and a keyboard, nested
  rings four deep, and a browser suite (`tests/e2e/test_ring.py`) that opens
  the ring three ways, walks an address, arrows to the nearest cell, backs
  out on 5 and jogs a simulated printer by address. That is the evidence
  rad's record asked for.

## Alternatives considered

1. **Keep the toolbar, and add the ring beside it.** — Lost because it is
   what the census exists to forbid. A ring that leaves the buttons behind
   has not replaced them; the meter stays where it is and two surfaces have
   to be kept in agreement for ever. Coexistence is allowed for exactly one
   step, and the ring-backed count is how long that step has lasted.
2. **A grid of buttons, numbered, and no ring.** — Lost because the pointer
   is real on this host: right-click on a piece in the 3D view, or on its
   row, is where the ring belongs, and a radial menu under a pointer is not
   improved by being a grid. The cells give the grid's addressability to the
   ring without giving up the gesture; rad's record says the same and this
   host confirms it.
3. **Free-form keyboard shortcuts per verb** (`h` for home, `j` for jog…). —
   Lost because a shortcut names a verb and not a place: it has to be learnt
   per verb, it cannot nest, it collides as verbs are added, and it says
   nothing to the person who is looking at the ring. An address is read off
   the ring while it is open and typed without it afterwards, and the same
   scheme holds for a ring the resolver builds tomorrow.
4. **Import rad's JavaScript directly.** — Lost, for now, because rad is
   private at `0.0.0` with no export, and a copy taken today would be a fork
   by next month. Implementing the contract and holding the implementation
   to rad's vectors keeps the seam at the vectors, where it can be checked;
   when rad publishes, replacing `ring.js` with it is a swap behind the same
   tests.
5. **Placement in reading order** (`7 8 9 4 6 1 2 3`) **rather than cardinals
   first.** — Lost because a four-option ring, the commonest, would then sit
   in the top row and the left, where no ring puts it, and the direction a
   cell means would stop being where it is drawn. rad fixed cardinals first;
   this host had no reason to disagree, and the §7 boundary says the
   disagreement would belong there anyway.

## Revision triggers

- **rad changes the placement order**, or any other clause of its nine-cells
  record, before or after ratification. This record adopts that one
  verbatim; a divergence makes the addresses here mean something different
  from the addresses on every other host, which is the failure the numbering
  exists to prevent. Follow, and say in the census docstring which addresses
  moved.
- **rad's record is ratified** — the `Pends on` resolves and this record can
  be put to a human for ratification, unchanged if rad's is.
- **A surface arrives with directions but no digits** — a controller, a
  pendant, a rotary encoder on the printer itself. Only the arrow half of §4
  survives there, and the census would then be counting a surface whose
  addresses cannot be typed.
- **The meter stops falling.** Two consecutive releases in which the
  ring-backed count does not fall, or the meter rises with no ring-backed
  control deleted, mean the doctrine is being carried rather than obeyed and
  §5 is the wrong enforcement.
- **A ring needs a ninth option**, or a fifth level of nesting to hold
  what it offers. The ceiling is structural here; pressure on it is pressure
  on rad's record, not on a lint.
- **The monitor's four unbacked buttons** (reconnect, reset, release,
  quickstop) are still unbacked when the last backed one is deleted. Either
  they get cells or the doctrine says why a printer's link is a different
  kind of surface.

## Amendments

*None.*
