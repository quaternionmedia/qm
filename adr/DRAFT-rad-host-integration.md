# ADR-XXXX — rad host integration for apothecary: the rings address nine cells

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-19 |
| **Pends on** | Ratification of rad's own record *The menu addresses nine cells* (`quaternionmedia/rad`, `adr/DRAFT-the-menu-addresses-nine-cells.md`). This record adopts it verbatim; it cannot be Accepted while the thing it adopts is a draft. |
| **Checked against** | apothecary `4426724` (`build/governance`); rad `3e8794f` (`main`), where *The menu addresses nine cells* is a draft |
| **Tools** | Drafted with Claude Code (Anthropic); the person who ratifies it is its contributor of record |

## Context

The viewer (`templates/fractal_viewer.html.j2`) is a page of controls of
its own: a toolbar, forms, a Selected panel with boxes and buttons, a
Device section for the board pinned to a piece, and a Machine per board
with its link's verbs and, behind a latch, controls that heat, home and
jog a machine. A control invented for one job is one more thing to find,
to learn and to keep in agreement with every other surface that does the
same, and each feature that brings its own adds to them. The census
(`apothecary/census.py`, `apothecary census`) counts them from the page's
own markup, and counts and names any control nobody has classified, so a
control cannot raise the count unseen. The doctrine behind the census is
that a page full of controls of its own becomes one ring, and the number
falls to nothing.

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
viewer's rendering library, three.js, is vendored
(`apothecary/static/vendor/three/`), and the adoption scope's audit table
carries it.

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
   nested rings are its address** (`728` is Control › Jog › Y+ in a
   printer's device ring, the top ring inside its Machine). Given the same context the same address reaches the
   same option. Every `Intent` carries its address; a log of choices reads as
   something a person could type back.

   A ring can also be **opened already entered**: given an option of its tree
   (by id or label), the host opens it and presses that option's digits from
   the top, so the ring shows the option's children and the address so far is
   the one a hand would have pressed -- never a shortcut that skips digits.
   Apothecary uses it when one step hands over to the next without the person
   reopening the ring. Every `Intent` also carries **where the ring stood**
   on screen (`at`), so a ring that follows from it opens in the same place.
   Both are this host's behaviour (`apothecary/static/ring.js`:
   `openRing({into})`, `RingInstance.enter`, `Intent.at`); what any rad host
   may rely on is rad's to define, and they are offered to its record as
   inputs.

   An option may also be **marked**: drawn outlined with a bullet, and
   `aria-current` on its wedge, when it is what the page has chosen outside
   the ring (a picture chosen in the Pictures panel, a camera's own device).
   A mark is display only: it changes no address and no option's meaning,
   and the ring keeps no memory of it.

5. **The census is the enforcement.** `apothecary census` counts each page's
   controls of its own and, beside that, how many of them are *ring-backed*:
   a control whose verb is a cell of some ring (`census.RING_BACKED`,
   checked against `apothecary.menu`'s vocabulary so no control can claim a
   backing that no ring produces). The meter does not fall because a control
   is backed; it falls when the backed control is deleted. The migration is
   therefore one sentence, repeated: a control gains its ⌗ address (written
   into its tooltip, where the control is), is used from the ring, and goes.
   A control nobody has classified is counted as `unclassified` and listed
   with its line, so it raises the meter whether or not anybody filed it,
   and the listing says somebody has to decide what kind of thing it is.

   One kind of control is backed by no ring and stays: the button on a row
   of a list that shows what a page placed, pinned or kept -- the Site
   panel's *Pinned* section, whose rows unpin a camera, a view or a board,
   every site's, and the Pictures panel, whose rows forget a picture the
   browser kept -- because *Personal data stays on the device* (§6) asks for
   a thing to be taken back from the list that shows it, and a ring reaches
   a pin only from the site it stands in. The census lists these apart
   (`census.TAKEN_BACK`), counted as controls of their own and claimed by no
   ring, so the meter neither credits them as backed nor loses them; a
   control has that standing only by being on one of those lists.

6. **Three shapes of ring**, resolved server-side by `apothecary/menu.py`
   from what the page says it is pointing at (`POST /menu/resolve`), with
   every option returned in its cell. The options that are always there
   come first and keep one address wherever the ring is opened; what comes
   and goes is seated after them, so its arrival moves no cell.
   - the **node ring**, on a piece: Step in, Move and Why this, at 8, 6
     and 2 on every piece; then what comes with the piece -- the pieces
     Inside it; a **Camera** and a **Picture** group on a structure that can
     hold a picture, a made piece's Picture group, or a camera's own verbs;
     a **Part** group (edit, the staged numbers' apply and revert, the SCAD
     saved as a variant, how it is viewed, its history) on a part, a camera
     or a made piece; Print and Slice where a printer is pinned in the site;
     a **Device** option when a board is pinned to the piece (absent, not
     greyed, when none is); and Parent, last;
   - the **canvas ring**, on empty scene: Pieces, Site, View, Panels,
     Pictures and Rebuild, at 8, 6, 2, 4, 9 and 3; then Step out when the
     view is stepped into a piece, and Group where the site's pieces have
     categories (each a further ring, lettered into groups of eight when
     longer);
   - the **device ring**, on a board: Open (the board's Machine), Poll,
     Flash, Query, Pin or Unpin, Rescan, Link (Reconnect, Reboot, Release,
     and on a devkit Listen and Probe), and — for a printer only — a
     **Control** ring behind it at 7: Heat, Home, Jog (seated so the keypad
     *is* the jog pad: Y+ up, X+ right, Y− down, X− left, Z± in the
     right-hand corners), Level, Print, Motors (off, quickstop, break wait),
     Stop (marked destructive), Arm or Disarm. Inside a board's Machine the
     device ring is the top ring, titled by the port. A printer's Flash is
     shown **disabled**, not absent: apothecary never flashes a printer's
     board, and removing the cell would move every cell after it, so a hand
     that learned ⌗728 for Jog Y+ would reach something else. This is the
     one exception to "absent, not greyed": a cell is kept disabled only
     where its absence would move cells a person already uses.

   Making a piece from a shape, making them all, dropping a made piece and
   changing its word change the arrangement, and the server carries them
   through the intent route, as it carries reset; every other camera and
   picture verb is the viewer's. Every device and control verb is the viewer's to carry out
   (`CARRIED_BY`): the ring hands the choice to the handler the page already
   has, a Machine's control chain checks the latch and the allowlist, and
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
  ring, from anywhere on the page. Accepted cost: the ring's keys (`m` and
  Shift+M, unless Settings names others) are taken while nothing is being
  typed into, and the ring swallows every key while it is open, so the
  viewer's Backspace-steps-out does not fire under an open ring — the hub
  is Backspace there.
- **Repeatability is now a property, not a hope.** An address is stable
  across sessions for the same context because placement is a function of
  option order, and option order is the resolver's, tested. The cost is that
  reordering a ring's options moves every address beneath them. Accepted:
  that is what "stable" has to mean, and a reorder is a deliberate edit to
  `menu.py` that the address tests will name.
- **The meter is read, not quoted.** `apothecary census` gives the
  viewer's controls of its own and how many of them are ring-backed;
  `VIEWER_CEILING` in `tests/test_census.py` holds the count, and a change
  that adds a control raises it in the same change, where a reviewer sees
  it. Nothing is reclassified to make the number smaller. The obligation
  this creates: ring-backed controls are deleted, and a change in which the
  meter rises with no ring-backed control deleted is a change that added a
  surface.
- **One page, one number.** The viewer is the one page the census counts,
  a Machine and the Bench with it. Every button that acts on a machine or
  its link has a cell: the link's own verbs (Reconnect, Reboot, Release)
  sit under a Link cell that keeps the same number on a devkit and a
  printer, and the motor verbs (off, quickstop, break wait) share Motors.
  What is not backed is a Machine's plumbing — which port, how often, the
  jog's step, the log's own buttons and tick-boxes — and the census says
  so rather than backing it quietly by the nearest thing.
- **Conformance runs on both sides.** The Python `nearest`, `place`, `walk`
  and `address_of` and the browser's `nearest`, `withCells`, `addresses` and
  `cellAtAngle` are compared through one JSON file; a divergence is a failing
  unit test, not a screenshot.
- **The ring's own listeners are the ring's.** The census counts one control
  for the ring, the button that opens it (`#ring-open`); the ring's keys on
  the window, and on the document a right-click held with its modifier and
  a touch held still, live in the module, and `tests/test_census.py` holds
  the module to exactly those listeners. Another way in would be one the
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
   is real on this host: a right-click held with its modifier on a piece in
   the 3D view, or on its row, is where the ring belongs, and a radial menu under a pointer is not
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
- **The meter stops falling.** `apothecary census`, run at two commits of
  the default branch six months apart, shows the ring-backed count not
  fallen while the meter rose — the doctrine is being carried rather than
  obeyed, and §5 is the wrong enforcement.
- **rad's record defines opening a ring at an address, or what an intent
  carries about where the ring stood** -- §4's two host behaviours follow
  rad's definition, and any difference is named in the census docstring.
- **A ring needs a ninth option**, or a fifth level of nesting to hold
  what it offers. The ceiling is structural here; pressure on it is pressure
  on rad's record, not on a lint.

## Amendments

*None.*
