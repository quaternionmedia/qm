# Perspective — A Board Is an Engine You Sell

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (Anthropic), the assistant that performed the hardware project's first two work packages |
| **Task** | An argument that openness in physical products is a reproducibility property rather than a licensing one, and a test of whether *Build the seam, buy the engines* survives being read from the seller's side of the transaction. It does, with five named strains and one gap the doctrine cannot currently express. |

## 0. Standing, scope, and evidence base

This is an argument, not a retrospective. It generalizes from one hardware
project that has so far produced a schema, a demo and no hardware, and it
reasons about commercial arrangements the org has not entered.

Evidence classes, per this corpus's convention:

- **E1** — the corpus text as vendored and quoted below, read this session.
- **E4** — inference from a single data point: one hardware project, zero
  boards fabricated, zero units sold.
- **E5** — prior general knowledge, unverified this cycle. Everything below
  about listing regimes, component lifecycles and what open-hardware projects
  typically ship is E5, and §1's characterization of common practice is an
  argument rather than a measurement. A reader who wants to disbelieve one
  section should start there.

The commercial half (§3 onward) is the weakest, because it reasons about
selling from a project that has sold nothing. It is written now because the
decisions it bears on — licensing venue, sourcing rules, what the board's
interface is — are being made now, and a claim recorded before the money
exists is at least uncontaminated by wanting the money.

## 1. Openness in a physical product is a reproducibility property

For software, a license grant and the source are jointly sufficient. You hold
the source, you hold a compiler you can also hold, and you can rebuild the
artifact. Openness bottoms out in tools that are themselves ownable.

For hardware it does not. A CERN-OHL-S board whose design files are fully
published, and which contains one sole-source part in an 0.4 mm BGA, is
legally open and practically closed. Every clause of the grant is honoured and
a recipient still cannot make one. The license was never the binding
constraint.

The implication is uncomfortable for the way open hardware is usually
discussed: **the sourcing rule does more for openness than the license text
does.** The hardware project's requirement that every BOM line carry two
independent sources or a documented drop-in alternate footprint reads like
supply-chain hygiene. It is not. It is the openness mechanism, and the license
is the thing that makes exercising it lawful.

Design constraints belong in the same category. Two layers rather than six,
no BGA where a QFN will do, hand-solderable where the function allows,
footprints with more than one manufacturer — these are openness features. They
are currently taste, and taste is what a record exists to convert into a
decision with teeth.

## 2. Four layers, and the third is where projects quietly fail

Openness in a physical product decomposes into four properties that are
independent of each other:

1. **Legal** — a grant permitting use, modification and redistribution.
2. **Source** — the *editable* design, not a rendering of it.
3. **Reproducible** — a BOM that can be sourced and a process that can be
   reached.
4. **Governed** — a legible answer to who decides what "the" design is, and
   how a fork rejoins.

Most projects that call themselves open hardware ship 1 and 2 and stop (E5).
The failure at 3 is invisible until somebody tries, which is typically years
after the claim was made and long after anyone would think to re-examine it.

Layer 2 deserves its own sentence, because the ambiguity is real in a way
software's is not. **An STL is a compiled artifact. A gerber is a compiled
artifact.** Publishing them and calling the result open hardware is publishing
binaries and calling it open source. The source is the `.scad` and its
parameter model; the source is the `.kicad_sch` and `.kicad_pcb` and the
libraries they resolve against. CERN-OHL-S already carries this distinction in
its "Complete Source" definition; projects routinely do not.

Apothecary's parametric-part convention — a `.scad` plus a Pydantic parameter
model, with STL generation as an output of the toolchain — is this instinct
already correct in-house, arrived at for usability reasons rather than
licensing ones. It is worth naming as a principle before someone
"simplifies" it by checking in the meshes.

Layer 3 also decays, which layer 1 does not. A license does not expire; a BOM
does. Parts go end-of-life, and an open hardware project with an unmaintained
BOM becomes unbuildable in a few years while its grant remains perfectly
valid. There is no software equivalent at that severity — an abandoned library
still compiles. This is a form of rot the corpus's quarterly upstream scan was
not designed to catch, because that scan watches licenses and archive status,
not availability.

## 3. The analogy, tested

*Build the seam, buy the engines* is written entirely from the buyer's seat.
Its decision clauses say what QM's control plane owns, what it refuses to own,
and how to select engines from the commons. A project that manufactures a
physical product is the first thing the org has built that sits in the other
seat.

**The seam survives the move unchanged.** The event envelope is the
compatibility guarantee across transports for a device family that does not
exist yet. No engine should reasonably own that, which is the doctrine's own
definition of seam logic. Nothing about selling changes it.

**The board is an engine.** Apply the replaceability test from the seams
record verbatim — *could this component be replaced by a from-scratch
implementation of the seam protocol alone, without changes on our side of the
seam?* — and the T1-Core passes: anything that reads a dry contact and emits
the envelope on the documented topics is a drop-in replacement. It has a
defined interface, it holds no policy, and it is swappable. That is an engine
by every criterion the corpus states.

**So the doctrine, read from the seller's side, becomes: build the seam, sell
an engine.** And it inverts into a commercial test that is sharper than the
buyer's version:

> Could our customer replace our product with a from-scratch implementation of
> our published interface, with no change on their side?

If the answer is no, QM sold lock-in — the precise thing the doctrine exists
to refuse, produced by QM rather than suffered from a vendor. If the answer is
yes, QM sold an engine, and the customer's independence is intact by
construction rather than by promise.

**This is where §1 and §3 meet, and it is the load-bearing claim of this
document.** For a *physical* engine, a from-scratch reimplementation requires
the design, a sourceable BOM, and a reachable process. There is no other way
to satisfy the seller's replaceability test. Which means:

> Open design files for a product QM sells are not generosity, a marketing
> position, or a values statement. They are the only available implementation
> of the replaceability guarantee the doctrine already requires.

A closed hardware vendor cannot pass this test. Not "would find it
inconvenient" — cannot, structurally. If the doctrine is right that
replaceability is the risk strategy, then QM selling a closed physical product
is incoherent, and no separate open-hardware value is needed to reach that
conclusion. It follows from P3 alone.

**The gap the doctrine cannot currently express.** *Build the seam, buy the
engines* lists "**Build the engines**" as its first rejected alternative, on
the grounds that it duplicates the commons and concentrates bus-factor in the
worst place. A hardware project builds an engine. The escape is the doctrine's
own second revision trigger — *an engine category QM depends on loses all
compliant options* — and there is no compliant open engine for "dry contact in,
versioned event out, bus-powered, signal-only, no vendor account." But the
trigger's stated remedy is that *the seam may need to absorb a capability*,
and a seam cannot absorb a board. A control plane made of copper is a category
error.

The open-license record's remediation path has the same shape and the same
limit: it routes an unclosable gap to "promote the fork to a maintained public
QM project, or implement in the project's control plane if genuinely seam
logic." Both options assume an upstream existed to fork. For an original
physical engine there is nothing to fork.

So the corpus has two doors, *absorb into the seam* and *promote a fork*, and
a hardware engine fits through neither. The missing third door is **publish it
as an engine in its own right** — the commons gaining a component rather than
QM gaining a product. Naming that door is the substantive proposal here.

## 4. Where the analogy strains

Five, and the first is the one that will actually be tested.

**4.1 Software engines are free at the margin; physical engines are not.** The
doctrine's assumption that "engine" and "replaceable" sit comfortably together
is load-bearing on engines being free to copy. A library's maintainer loses
nothing when you swap them out. A board's manufacturer loses the unit. That
does not make the discipline wrong, but it does put a standing incentive
against it that the software case never had, and every erosion will arrive
dressed as something reasonable — a convenience feature that only works with
our firmware, a calibration blob, an enclosure that fits only our board.
Naming the incentive is cheaper than being surprised by its arguments.

**4.2 Sponsorship inverts, and the record only runs one way.** The
contribution and sponsorship policy is written throughout as QM-as-sponsor:
maintainers of engines QM depends on are sponsorship candidates by default.
Ship an engine and QM becomes a maintainer other people depend on and might
sponsor. The record has no clause for obligations in that direction, and the
obvious ones are not trivial: what response time does a sponsored maintainer
owe, and what happens to sponsors when a product is discontinued.

**4.3 Some engines can only ever be bought.** A category subject to a listing
regime cannot be an open engine, because the listing attaches to the tested
configuration and any modification invalidates it (E5). For those categories
"buy the engines" is not a preference the ordering rule weighs, it is the only
lawful option in perpetuity. The signal-only record resolves this for mains by
refusing the category, which is correct and is also a narrower move than the
general problem deserves. The same shape appears benignly in choosing a
pre-certified radio module: buying an engine to move a certification burden
onto its vendor.

**4.4 A discontinued physical engine cannot be forked back to life.** An
abandoned library sits on a disk and still works. A board that stopped being
made is gone unless the design, the BOM and the process are all reachable —
which is layer 3 again, now as an obligation created by selling rather than a
property of publishing. Selling a physical engine incurs a duty software
engines do not: leave behind enough that the thing can be rebuilt without you.

**4.5 The carried-patch register has no hardware analogue.** Its unit is a
build-time patch against an upstream, with a PR link and a carry start date. A
hardware project carries different debt: a component substitution, an errata
workaround, a bodge, a footprint deviation from a manufacturer's
recommendation. These are commitments of the same kind — a private divergence
someone must keep paying for — and nothing registers them. A hardware project
can accumulate exactly the debt the register exists to make visible, in a
currency the register cannot count.

## 5. What this would mean concretely

Candidate `DRAFT-*` changes for a human to pick up. None self-executing, and
the first two are the ones worth doing even if the rest is wrong.

1. **State the reproducibility layers in the project's licensing record**, and
   say plainly that the sourcing rule is an openness mechanism rather than
   supply-chain hygiene. Define source as the editable design and name
   fabrication outputs as artifacts.
2. **State P1's honest limit for physical goods.** *Ownable-offline-
   indefinitely* is achievable for software and structurally unavailable for
   hardware — you can fork a compiler; you cannot fork a fab. The strongest
   truthful claim is *reproducible by anyone with access to a commodity
   process*. That is a genuinely weaker claim and is better stated than
   silently inherited from the software framing, because a reader who takes P1
   literally will eventually notice it does not hold and reasonably wonder
   what else was overstated.
3. **Add the third door to the seam-and-engines doctrine**: publish as an
   engine, alongside absorb-into-the-seam and promote-a-fork (§3).
4. **Add the seller's replaceability test** to the seams record — the same
   question asked of what QM ships, not only of what QM adopts.
5. **Give the contribution and sponsorship record a receiving clause** (§4.2).
6. **Extend the carried-patch register, or give it a sibling, for hardware
   divergences** (§4.5).
7. **Watch part availability the way the org watches licenses** — the
   quarterly scan sees relicensing and archive status and is blind to
   end-of-life (§2).

## 6. Closing honesty

This document argues from a project with no fabricated board and no customer.
§3's commercial inversion is the part most likely to look naive from inside an
actual manufacturing operation, and §4.1 names the pressure that would test it
without claiming to know how that goes.

The tidiness of §3 is itself a warning sign. An argument that concludes the
org's existing doctrine already implies the conclusion the author finds
attractive is the kind of argument that deserves a hostile reading, and the
strongest hostile reading is that "the board is an engine" is a definitional
move rather than a discovery — that calling it an engine imports conclusions
that were chosen rather than derived. The response is §3's application of the
replaceability test clause by clause, which is checkable against the record's
text; but a reader who thinks the definition is doing the work should say so,
because if it is, §5's proposals 3 and 4 are unfounded.

Nothing here is a request. A perspective never graduates on its own. If any of
§5 is worth acting on it is a human picking it up as a record, and proposals 3
and 4 are amendments to ratified-track org doctrine, which is a heavier lift
than a project record and should be treated as one.

— Peter Kagstrom, drafted with Claude Opus 5, 2026-08-08
