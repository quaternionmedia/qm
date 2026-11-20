# ADR-XXXX — The viewer groups what it shows by Kind and System

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-11-19 |
| **Pends on** | rad's *A long list is grouped by facet, then by letters* (`quaternionmedia/rad`, `adr/DRAFT-a-long-list-is-grouped-by-facet-then-by-letters.md`), which §3 adopts. This record cannot be Accepted while what it adopts is a draft. |
| **Checked against** | apothecary `2ac9b34e`; rad `242d424` (`evolve/a-long-list-is-grouped-by-facet`) |
| **Tools** | Drafted with Claude Code (Anthropic); the person who ratifies it is its contributor of record |

## Context

The viewer (`templates/fractal_viewer.html.j2`) shows two kinds of place: the
universe, a sphere of every registered part, and a site, a room of pieces --
the garage with its walls, furniture, two machines, plumbing and boards on a
bench. It lists what they hold in several surfaces: the ring's cells, Site's
chips, the Layers window, the sphere's clusters. A review of the page on
2026-11-19 (apothecary `docs/plans/viewer-review-2026-11-19.md`, at
`435db0a4`) found the groupings those surfaces use at odds:

- **`category` meant two things.** On a site's node it named the subsystem a
  piece serves (wall, furniture, mechanical, fluid, electrical); on a part it
  named what the part is (coupon, camera, electromechanical). A test coupon was
  a coupon in the universe and a structure in the garage, and the garage's
  `mechanical` held the heating beside the printer and the router.
- **Nineteen categories, seven of one part.** The sphere's first shell wore
  about eighteen outlined, labelled clusters of one or two parts.
- **"Group" named five things**: a window's group, the canvas ring's Group
  cell, the runs a long list was cut into, a widget's set of controls and groups
  of data.
- **A long list was cut three ways**, and a part's presets past the eighth were
  left off the ring.
- **A word's colour was its own literal**, two words had none and took one from
  their names, and a System's word and a part's category spelt alike
  (`electrical`, `furniture`) shared one layer and one colour.

rad (`quaternionmedia/rad`) settles a ring and not its contents: eight cells,
grouping obliged, and no rule for how. The *rad host integration for
apothecary* draft adopts rad's nine-cells addressing; this record is the
grouping that addressing is filled with.

## Decision

**The viewer groups what it shows by two facets: a part's Kind and a site's
piece's System.** The specifics:

1. **Two facets, one vocabulary** (`apothecary/facets.py`). A **Kind** is what a
   part is; a **System** is what a site's piece serves. A piece that is a part
   carries both, and a piece inside a part is of that part. The universe is
   grouped by Kind and a site by System. A part standing loose in a site -- a
   board on the bench, a coupon -- has no System and is grouped by its Kind.

   | Kind | Its categories, each whole in one kind |
   |---|---|
   | Electronics | electrical, electronics |
   | Cameras | camera |
   | Machines | machine |
   | Motors | electromechanical |
   | Test pieces | calibration, coupon |
   | Shop | dust, tooling, hardware, storage |
   | Housings | enclosure, building |
   | Things | appliance, furniture, cookie-cutter, music, rc, misc |

   | System | A site's word |
   |---|---|
   | Building | wall |
   | Furniture | furniture |
   | Machines | machine (the printer and the router) |
   | Mechanical | mechanical (the heating and ventilation) |
   | Electrical | electrical |
   | Plumbing | fluid |
   | Lighting | lighting |
   | Scenery | scenic |

   Each facet has at most eight values, a ring's cells, and no word is in two
   values of one facet. `tests/test_facets.py` holds every registered part's
   category to one kind and every word a site uses to one System, or to a short
   list of words decided loose.

2. **"Group" names a window's group and nothing else.** The window groups are
   seven -- Site, Part, Pictures, Machine, Tools, Family, Airgap -- and the
   canvas ring's Panels holds one cell for each, every window's door under its
   own group's cell.

3. **A long list in a ring follows rad's proposed rule.** A level's pieces are
   cut by their facet first: a site's Systems, then one more cell, Parts,
   holding its loose parts by kind; the universe's kinds, its sites left to the
   Site cell. A loose part's kind named as one of the level's Systems is
   (Machines) is always under Parts, so no two cells of a ring read the same,
   and each cell's id names its facet. A plain list is cut into near-equal runs named for their letters,
   a list in its own order in that order, and nothing is dropped
   (`apothecary/menu.py`, `_fit` and `_by_facet`). The canvas ring's cell 7 is
   Systems in a site and Kinds in the universe wherever the ring opens, greyed
   with its reason where a level has none, and Step out is cell 1 always. Where
   a level has no pieces to list, or the ring has no site, Pieces and Site are
   greyed in their cells with why, so no cell after them moves.

4. **Colours are tokens** (`apothecary/static/tokens.css`). A kind's is
   `--kind-<name>`, a System's `--system-<name>`, and a category's is a shade of
   its kind's: the kind's L*a*b* lightness stepped evenly across its
   categories, its own colour in the middle. Every colour of a facet is held
   apart from the others, from the colours that mean a state, from the shells'
   and the world's own, and at 3:1 against the page's ground.

5. **A piece is on its System's layer, else its category's.** The walls are
   `system:building`; a loose part is on `category:<its category>`; a Kind is a
   heading over its categories' layers, its ticks setting them all. The Layers
   window, Site's chips, the ring's View › Layers and cell 7 list what lies
   beneath the level in view, in the facets' order: Systems, then Kinds over
   their categories, then words neither holds.

6. **The universe's sphere is clustered by kind.** A kind's parts sit together
   on their shell, with one outline round them in the kind's colour, named for
   the kind. Choosing a kind, by its outline, by cell 7 or by its chip in Site,
   opens the kind's ring, which lists its parts. The kinds tile the first shell, so the circles drawn round them
   are wide and cross; `tests/test_orbits_drawn.py` holds fewer than half the
   pairs on a shell crossing.

## Consequences

- **One word, one meaning, on every surface.** A person who learns that the
  router is in Machines finds it there in the ring, the chips, the Layers window
  and the sphere, in one colour.
- **The ring's addresses hold.** Cell 7 and cell 1 no longer move with the
  level, and a long list's runs are named for what they hold. Accepted cost:
  addresses a person had learned moved once, in the change that made them hold
  (the Bench, Docs, the Deck and the Loops among them), and the page's own
  status text was moved with them.
- **The sphere is less crowded and its outlines cross.** Eight kinds replace
  nineteen categories, so fewer outlines and labels; a circle is a poor shape
  for a region that tiles a shell. Drawing each kind's own edge is left to the
  review of the sphere (the review's fourth step), and the guard's threshold is
  where that work starts from.
- **A new category or site word is a decision.** A part filed under a word no
  kind holds, or a site using a word no System holds, fails the facet tests
  until the word is given its value here.

## Alternatives considered

1. **Keep one `category` for both.** -- Fewest changes. Lost because it is the
   fault the review found: a word that means what a part is in one place and
   what a piece serves in another cannot be grouped, coloured or hidden as one
   thing.
2. **Group the universe by its nineteen categories.** -- No folding, nothing
   for a person to learn. Lost because nineteen cannot be one ring and the
   sphere wore eighteen clusters on one shell, seven of a single part.
3. **One facet, Kind, for sites too.** -- A site's pieces are mostly not parts
   (a wall, a duct, a workbench), so a kind says nothing of them, and what a
   person looks for in a room is what a piece serves.
4. **Colours as literals in a table.** -- What the page had. Lost because rad's
   theme-tokens draft makes colours tokens, and a literal per word let two
   words drift close and a new word go without one.

## Revision triggers

- **rad's grouping draft is ratified, changed or refused** -- the `Pends on`
  resolves; a change to its rule is followed here, and a refusal makes §3 this
  host's own rule, to be written as such.
- **A ninth kind or System is needed**, so a facet no longer fits one ring.
- **A category or site word cannot be put in one value** without splitting
  something people treat as whole.
- **The sphere's outlines change shape** -- each kind's own edge in place of a
  circle -- and §6's guard is replaced by one on the new shape.

## Amendments

*None.*
