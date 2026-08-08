# ADR-XXXX — USB-C Bus Power Is the Reference Power Path

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-08 |
| **Pends on** | Nothing — ready to be argued |

## Context

Power topology is the decision that propagates furthest into a small connected
device. It sets the microcontroller family, the firmware framework, the sleep
strategy, the transport, the indicator design, half the bill of materials, and
the enclosure's cable geometry. Deciding it late means redoing the rest.

Two candidate baselines exist for a control module. A battery baseline
optimises for placement freedom: the device goes anywhere, including the middle
of a wall with no receptacle. It pays for that with a duty-cycled radio, a
power budget that constrains gesture detection, a firmware framework chosen for
microamp discipline rather than for developer velocity, a charger or a coin
cell and its holder, a battery sense path, and an indicator that cannot idle
lit. A bus-power baseline gives all of that back and asks for a cable.

The project's stated first milestone is a desk-scale demonstration, and its
first honest market is a control surface near equipment that already has power:
a bench, a rack, a workstation, an instrument stand. The wall-in-the-middle-of-
a-room case is real but is not the case the first board has to win.

There is also a compounding effect worth naming. The chosen microcontroller
module's native USB-Serial-JTAG means a USB-C receptacle fitted for power also
supplies flashing, logging, and a USB MIDI and HID transport, with no
USB-to-UART bridge on the bill of materials. The connector pays for itself
three times over once it is present for power.

## Decision

1. **USB-C bus power at 5 V is the reference power path for T1-Core**, and for
   every board in this project until a record says otherwise.
2. **The board is a sink with default termination**: CC1 and CC2 each
   terminated to ground through 5.1 kΩ. No power-delivery controller, no
   negotiation beyond what that termination obtains.
3. **A full 16-pin receptacle is fitted, not a power-only part**, and D+/D- are
   routed as a 90 Ω differential pair to the module's native USB pins. ESD
   protection is fitted on VBUS, D+ and D-.
4. **The 3.3 V regulator is specified for at least 600 mA**, against a Wi-Fi
   transmit peak in the 300–350 mA region, with bulk capacitance placed to the
   module datasheet's requirement.
5. **No sleep strategy is designed in.** Firmware may sleep; nothing in the
   hardware or the event schema assumes it does. Gesture timing, radio
   association and indicator behaviour are designed for a continuously powered
   part.
6. **Battery and energy-harvested variants are a separate tier (T4) and a
   separate board**, with their own record. They are not a stuff option on this
   layout, and this record makes no promise that T4 shares this schematic.

## Consequences

- The first board is materially simpler: no charger, no fuel gauge, no battery
  sense divider and its gating transistor, no indicator power gate, no
  brownout-under-transmit budget to model. Those are the parts most likely to
  be got wrong on a first revision.
- ESPHome is usable close to as shipped. A microamp-class design would push
  toward a different framework and a different chip family, which is a much
  larger commitment than a power connector.
- The radio stays associated, so a press-to-light round trip is a network round
  trip rather than a reassociation. Perceived responsiveness is the whole
  product for a button, and this is the cheapest way to buy it.
- **Accepted cost, stated plainly: a cable must reach every unit.** Desk,
  bench, rack and instrument placements are natural; mid-wall placement needs
  an in-box receptacle or a Class 2 supply run to it, and neither is a printed
  part. This narrows the installable set, and the narrowing is accepted for the
  first board rather than papered over.
- **Accepted cost:** the untethered story is deferred, and clause 6 says openly
  that it will likely be a different board rather than a variant. A reader who
  wants a batteryless wall switch does not get one from this record.
- Obligation created: every enclosure mount in apothecary provides a cable exit
  and strain relief. A mount without one is incomplete, not minimal.
- Obligation created: a design-rule or review check that both CC pins terminate
  through 5.1 kΩ. Omitting the CC terminations produces a board that powers
  from a legacy A-to-C cable and draws nothing from a compliant Type-C source,
  and the failure presents as an intermittent cable problem.

## Alternatives considered

1. **Coin cell (CR2032) with a BTHome broadcast transport.** It lost as a
   *baseline* on velocity, not on merit: it is probably the right answer for a
   wall-mounted product, and it forces an nRF52840-class part, a non-ESPHome
   firmware path, and a design where every architectural question is
   re-litigated against a microamp budget. Held as T4, where it can be decided
   against measurements instead of estimates.
2. **Rechargeable lithium with USB-C charging** — nominally the best of both.
   It lost because it is the union of both designs' complexity rather than the
   union of their benefits: it carries the charger, the protection, the fuel
   gauge and the cable, and it adds a cell that ages, a shipping restriction,
   and a fire mode inside a printed enclosure. A first board is the wrong place
   for it.
3. **Power over Ethernet.** It lost on cost and size for a device whose job is
   to report a contact closure, though it is a legitimate future tier for
   installations that already have structured cabling and no receptacles.
4. **Screw-terminal low-voltage DC input (barrel jack or 2-pin) instead of
   USB-C.** It lost because it gives up flashing, logging and the USB MIDI and
   HID transport, which arrive free with the connector this decision fits.
   Remains available as an additional input on a later revision.
5. **Deciding power per board rather than fixing a baseline.** It lost because
   an undecided power topology is what makes every other decision provisional,
   which is the condition this record exists to end.

## Revision triggers

- A wall installation becomes a committed deliverable rather than an
  aspiration, which makes clause 1's placement cost binding rather than
  acceptable.
- Measured demand for a variant with a real power budget, at which point T4's
  record is written against measurements.
- The chosen module family changes such that native USB is no longer available,
  removing the compounding benefit in clause 3.
- A deployment requires more current than a default 5 V sink obtains, which
  would force the power-delivery question clause 2 declines.

## Amendments

*None.*
