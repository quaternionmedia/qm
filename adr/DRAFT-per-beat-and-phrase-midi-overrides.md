# ADR-XXXX — Per-Beat and Per-Phrase MIDI Action Overrides, and Manual Triggering

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-19 |
| **Pends on** | Nothing architectural - filed Proposed rather than Accepted only because ratification is a human action per the org's own process, not because an input is outstanding |

## Context

`DRAFT-per-beat-type-midi-action-routing.md` gave every beat *type* (Bar, Beat, Accent, Strong
Accent, Custom) its own configurable MIDI Note/CC default. The next ask went two levels finer and
one level coarser: let one *specific* beat (not its whole type) carry its own action that wins over
the type default, let a *phrase* itself carry an action fired once when entered, and give a
performer a way to manually fire whatever's actually configured for the current beat without
waiting for playback to reach it - a one-shot sanity check for a MIDI setup, or a hand-cue for
external gear/lights.

Reaching a *specific* beat meant reaching a specific bar first, and by the time this was built the
engine already had `Phrase` (`engine/Phrase.kt`): a phrase carries its own full bar queue, and only
one phrase/bar combination is ever "active" for playback at a given moment. Every existing per-bar
setter (`setAccentPattern`, `setBpm`, `setUnitNoteValue`) mutates "whichever bar is currently
active" - a natural fit when the thing being edited *is* the live playback state, but overrides are
authored data, not playback state, and a UI restricted to "the active bar" would make editing
*any* other bar's override require first navigating playback there.

## Decision

1. **`TimeSignature.midiOverrides: Map<Int, MidiBeatAction>?`** - a sparse, per-bar map from beat
   index to override action. `MetronomeEngine.resolveMidiActionForBeat` layers it over the beat's
   resolved `ClickSound` type default: override, else type default, else `MidiBeatAction`'s own
   NONE. A `Map`, not a padded `List` like `accentPattern` - overrides are typically 0-2 beats out
   of up to 24, unlike accent tiers where every beat conceptually has one.
2. **`Phrase.action: MidiBeatAction`** - one action per phrase, fired via `MidiActionSender.fire`
   every time `MetronomeEngine.goToPhrase` resolves to it, including re-entering the
   already-active phrase directly (not gated on a genuine transition - "fires whenever a phrase is
   confirmed/entered" is the simpler mental model, and matches `MidiBeatAction`'s own NONE-by-
   default silence for anyone who hasn't configured one).
3. **Beat-override authoring targets an explicit `(phraseIndex, barIndex, beatIndex)` triple**
   (`MetronomeEngine.setMidiOverride`), not "whichever bar is currently active" the way every
   other per-bar setter works. The authoring UI (Settings → Beat Overrides) browses to that triple
   via `PhraseQueueDots`/`BarQueueDots` - the *exact* pickers the main screen's own phrase/bar
   queues already use, reused rather than a second picker invented for this purpose - with
   selection kept as local UI state, never calling `goToPhrase`/`goToQueueBar`: browsing to author
   an override must not also move live playback out from under a running set.
4. **Manual triggering is a mode of the existing TAP button, not a new one.** While HOLD is
   latched and MIDI Actions is on, TAP's tap gesture fires
   `MidiActionSender.fire(MetronomeEngine.resolveMidiActionForBeat(...), ...)` for the engine's
   live current beat instead of tap-tempo, without starting playback or dropping the latch. A
   dedicated fourth button (tried first, on the main screen's transport row) broke that row's
   established, deliberate TAP/PLAY-STOP/HOLD symmetry - see Alternatives.

## Consequences

- `setMidiOverride`'s explicit-index signature is the one outlier among `MetronomeEngine`'s
  per-bar setters - every other one (`setBpm`, `setAccentPattern`, `setUnitNoteValue`) still
  mutates "whichever bar is active." A future contributor extending the active-bar pattern to a
  new field should not assume `setMidiOverride`'s shape is the template; the difference is
  deliberate (§3), not an oversight.
- TAP now carries three layered meanings depending on state: tap-tempo (the default), commit
  staged tempo and start playing (HOLD latched, MIDI Actions off - pre-existing behavior,
  unchanged), and Trigger (HOLD latched, MIDI Actions on). This echoes the BPM number's own
  established multi-gesture precedent (tap/long-press/drag, one control, several meanings) but is
  the second control in the app carrying that pattern, not the first - worth remembering before
  adding a third gesture to either.
- `ui/HelpScreen.kt`'s MIDI category needed restructuring to demo all five MIDI-adjacent topics
  live (it previously only demoed two) - a direct consequence of §1-§4 existing, not a separate
  decision; see that file's own kdoc.
- `docs/usb-midi-test-plan.md` needs its own real-hardware verification pass for override/phrase-
  action/trigger delivery (§7.1/7.2/7.3), not yet run as of this ADR's filing - the same
  not-yet-verified state `DRAFT-per-beat-type-midi-action-routing.md` already flagged for the
  type-level routing this builds on.

## Alternatives considered

1. **A persistent fourth "Trigger" button on the main screen's transport row** - tried first,
   shipped briefly, then reverted: TAP/PLAY-STOP/HOLD is a deliberately symmetric three-button row
   around the centered PLAY/STOP circle; a fourth, always-visible button (even gated to only show
   when MIDI Actions is on) read lopsided against that established balance. Rejected in favor of
   §4 once an alternative that added zero new visible elements was on the table.
2. **Beat-override authoring restricted to "whichever bar is currently active"**, mirroring every
   other per-bar setter - tried first, rejected: the only way to edit a different bar's override
   would be to navigate the main screen's playback position there first, an indirect, easy-to-get-
   wrong workflow for what is fundamentally a data-entry task unrelated to what's currently
   playing. The explicit-index signature in §3 costs one outlier in the setter shape (see
   Consequences) in exchange for authoring that can't accidentally land on the wrong bar.
3. **Firing Trigger via a long-press on TAP instead of a plain tap**, leaving TAP's existing
   latched "commit and play" behavior on the plain tap - considered, rejected in favor of a plain
   tap replacing that behavior entirely while latched with MIDI Actions on: the two-gesture split
   would have meant TAP carries a fourth distinct meaning (tap vs. long-press, each conditional on
   state) rather than three, judged more to remember than the behavior it would preserve was worth.

## Revision triggers

- Real-hardware verification (`docs/usb-midi-test-plan.md` §7.1/7.2/7.3) finds the override-
  layering model or the reactive, once-per-beat Trigger firing produces confusing or unreliable
  results on some class of receiving device.
- TAP's three-way, state-dependent meaning is found confusing enough in practice (on-device
  testing or user feedback) to warrant pulling Trigger back out into a dedicated control after
  all.
- A future feature needs to author beat overrides for a bar that isn't reachable through
  `phrases`/`timeSignatureQueue` at all (e.g. a template/preset library) - revisit whether the
  explicit-index signature in §3 still fits.

## Amendments

*None.*
