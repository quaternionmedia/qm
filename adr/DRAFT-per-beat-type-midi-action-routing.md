# ADR-XXXX — Per-Beat-Type MIDI Action Routing

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-18 |
| **Pends on** | Nothing architectural - filed Proposed rather than Accepted only because ratification is a human action per the org's own process, not because an input is outstanding |

## Context

`docs/realtime-audio-roadmap.md` (qmetronome repo) scoped this direction explicitly before it was
built: `MidiClockSender` only ever emits a shared clock pulse (`0xF8`) - it has no concept of "beat
type" at all, only "a beat happened." The ask was for any beat type (not just the downbeat) to
optionally fire a distinct MIDI Note or CC message, letting qmetronome drive external gear/lights/
DAW automation differently per beat type rather than acting only as a shared tempo reference. This
builds directly on `DRAFT-midi-clock-as-open-standard-seam.md`'s decision to depend only on
`android.media.midi` - no new dependency, no new transport, just a new message shape sent to the
same destinations.

Reaching any beat type beyond the always-present downbeat required two prerequisites that didn't
exist yet: `ClickSound` only had `BAR`/`REGULAR`/`ACCENT` (and even `ACCENT` had no UI ever authoring
which beats counted as accented - "wired end-to-end in the audio engine, but currently unreachable
in the UI," per its own kdoc at the time), so there was nothing beyond the downbeat to distinctly
route in the first place.

## Decision

1. **Two new `ClickSound` entries** (`STRONG_ACCENT`, `CUSTOM`) plus a **beat-accent authoring UI**
   (per-beat chips in `ui/TimeSignatureEntryDialog.kt`, cycling `NONE → ACCENT → STRONG_ACCENT →
   CUSTOM → NONE`) are shipped together with the MIDI routing itself, not deferred - a routing
   feature with nothing but the downbeat ever reachable would ship dead.
2. **`midi/MidiActionSender`** mirrors `MidiClockSender`'s destination-registry shape (a
   `CopyOnWriteArraySet<MidiReceiver>`, factored into a shared `MidiReceiverRegistry` helper class -
   see §3) but is **reactive, not clocked**: `fireForBeat(sound, timestampNanos)` is called directly
   from `MetronomeEngine.onBeat`, which already fires exactly once per real beat. Unlike
   `MidiClockSender`'s 24-ppqn subdivision (which genuinely needs its own free-running schedule
   between beats), a Note/CC message only needs to happen once per beat - there is nothing to
   subdivide, and no schedule of its own to maintain or resync.
3. **A shared helper class, not a shared runtime instance, for the destination registry.**
   `MidiClockSender` and `MidiActionSender` each own a private `MidiReceiverRegistry` instance - the
   ~10 lines of `CopyOnWriteArraySet` bookkeeping are shared as code, not as one registry both
   features write into. `midi/UsbMidiConnector.connectForSending()`/`disconnectSending()` and
   `midi/VirtualMidiClockService`'s port lifecycle each register/unregister a destination with both
   independently. `MidiClockSender` itself is left otherwise unrefactored - it is timing-critical and
   already proven; the small duplication cost was judged cheaper than the risk of touching it.
4. **Deliberately independent of `clickEnabled` and mute-probability.** `MidiActionSender` is gated
   only by its own `enabled` flag and each beat type's own configured action. Muting/disabling the
   audible click is a practice-mode concern for the performer's own ear (`effectiveMuteProbability`'s
   own kdoc: "the audible click only... beat position, phase and visuals are untouched"); external
   gear or lights driven by a beat action have no reason to desync because of that setting, the same
   way the visual flash is already unaffected by it.
5. **Per-beat-type configuration** (`engine/MidiBeatAction`: type - None/Note/CC - channel, note/CC
   number, velocity/value, and Note-only duration) is persisted per `ClickSound` via
   `MetronomeSettings`, using the same no-JSON, per-key `SharedPreferences` encoding the rest of the
   project's settings already use (one pref key per sound, mirroring `ClickSpec`'s own precedent) -
   no new persistence mechanism, no new dependency.

## Consequences

- Extends `DRAFT-midi-clock-as-open-standard-seam.md`'s decision cleanly rather than complicating
  it: still zero new Gradle dependencies, still `android.media.midi` only, still the same
  `MidiReceiver`-typed destinations (virtual port, USB input ports) - a destination doesn't know or
  care whether the bytes arriving on it came from `MidiClockSender` or `MidiActionSender`.
- No new Android permission; MIDI itself was already declared optional in the manifest.
- Grows the audio-engine-adjacent surface a future contributor needs to understand
  (`beatTypeFor`/`resolveBeatAudio`'s split between "what type is this beat" and "should the
  audible click for it actually play") - judged worth it since the split itself is what makes MIDI
  actions independent of audio muting, a deliberate product requirement, not an accident of
  refactoring.
- `docs/usb-midi-test-plan.md` needs its own real-hardware verification pass for Note/CC delivery,
  symmetric to the existing clock-sync verification it already documents - not yet run as of this
  ADR's filing.

## Alternatives considered

1. **Route MIDI actions through `StreamingClickEngine`'s sample-accurate mixing pipeline**, the same
   path the audible click uses - rejected: MIDI receivers' timing tolerance is far looser than human
   hearing (the entire reason `StreamingClickEngine` exists at all - see the realtime-rewrite work in
   the qmetronome repo's own history), so coupling a MIDI byte's send timing to the audio engine's
   sample-frame placement machinery would add real complexity for no perceptible benefit, and would
   have made "independent of `clickEnabled`" (Decision §4) much harder to keep true.
2. **One shared `MidiReceiverRegistry` *instance*** between `MidiClockSender` and `MidiActionSender`,
   rather than one shared *class* with two instances - rejected: would couple two independently
   user-enableable features' destination sets together (enabling one would silently also route the
   other to the same set), and risked destabilizing `MidiClockSender`'s existing, already-verified
   destination-management code for a DRY win judged not worth the risk.
3. **Gate MIDI actions on `clickEnabled`/mute-probability the same way the audible click is gated** -
   rejected as the wrong default: the practice-mode mute feature exists to challenge a performer's
   own internal sense of tempo, not to desync whatever external gear or lighting rig is listening to
   qmetronome's MIDI output.

## Revision triggers

- Real-hardware verification (`docs/usb-midi-test-plan.md`'s planned MIDI-actions extension) finds
  the reactive, once-per-beat firing model produces audibly or functionally poor results on some
  class of receiving device - revisit whether *some* predictive lead is needed after all.
- A future feature needs the same destination to receive clock and action bytes in a coordinated,
  ordered way (not just independently, eventually-consistent) - revisit the separate-registry
  decision in §3.
- `android.media.midi` itself changes materially (tracked jointly with
  `DRAFT-midi-clock-as-open-standard-seam.md`'s own trigger for the same event).

## Amendments

*None.*
