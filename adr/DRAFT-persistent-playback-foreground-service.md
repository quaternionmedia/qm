# ADR-XXXX — Persistent Playback via a Foreground Service

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-06 |
| **Pends on** | Nothing architectural - filed Proposed rather than Accepted only because ratification is a human action per the org's own process, not because an input is outstanding |

## Context

On-device testing surfaced that playback stops implicitly whenever the Glyph
Toy service unbinds (`MetronomeGlyphService.performOnServiceDisconnected` →
`MetronomeEngine.stop()`), and Nothing OS unbinds that service both when the
user deliberately switches to a different Glyph Toy (intended - selecting a
toy starts its function, deselecting stops it) and when the phone is simply
unlocked (the ambient Glyph Interface closing). These two triggers are
indistinguishable from this app's side - both arrive as a plain service
unbind with no further signal to tell them apart.

A performer wants an opt-in mode where playback "should only stop when
explicitly asked" - surviving backgrounding, screen lock, and Glyph Toy
unbind - without that mode requiring anything. Two constraints were stated
explicitly going in: the zero-permission alternative (raise the phone's own
screen-timeout, keep the app foregrounded) already covers the common case and
must be surfaced first, not treated as an afterthought; and neither
permission this feature might request may be a requirement - the feature must
keep working, just less aggressively, if either is declined.

## Decision

1. A genuine Android foreground `Service` (`engine/PersistentPlaybackService`)
   is the mechanism - not a "just don't call `stop()` on unbind" change alone,
   since backgrounding/Doze/app-standby can still throttle a plain background
   coroutine without a foreground service granting scheduling priority.
2. Declared `android:foregroundServiceType="specialUse"`, not `mediaPlayback`.
   Persistent mode can be meaningful with the audible click off (ambient
   Glyph-Matrix-only practice), and `mediaPlayback`'s policy expectation is
   genuinely continuous audio, which isn't always true here.
3. Started/stopped only while both Settings → Playback → "Persistent
   playback" is on **and** the engine is actually playing (a `combine()`
   collector in `QMetronomeApp`, the same shape as the existing widget-update
   collector) - no foreground service runs at all otherwise, so opting out
   costs nothing.
4. `MetronomeGlyphService.performOnServiceDisconnected` stops the engine only
   when persistent mode is off. The fix trades "toy-switch also stops it" for
   "unlock doesn't," since the two triggers can't be told apart from this
   app's side - deciding to keep stopping on a deliberate toy-switch while not
   stopping on unlock would require a signal Android doesn't expose.
5. `POST_NOTIFICATIONS` and the battery-optimization exemption
   (`REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`) are both requested opportunistically
   the moment the setting is turned on, and both are optional: declining
   `POST_NOTIFICATIONS` leaves the service running at foreground priority
   regardless, just without a visible notification; declining the exemption
   leaves standard (rather than the strongest OEM-level) background
   protection. Neither gates the feature.
6. `ClickPlayer` already never requests audio focus
   (`AudioAttributes.USAGE_ASSISTANCE_SONIFICATION`) - confirmed by reading
   the code, not assumed - so "keep working alongside other apps' audio"
   needed no change here.

## Consequences

- This is qmetronome's first runtime/dangerous-protection-level permission
  (`POST_NOTIFICATIONS`) and first genuine `startForeground()` call -
  `docs/app-store-checklist.md` had two statements asserting neither was
  true, both updated to match this decision.
- `specialUse` requires a `PROPERTY_SPECIAL_USE_FOREGROUND_SERVICE_TYPE`
  justification string in the manifest, which is subject to Play Console
  review at submission time - a real gate, not a formality, per
  `docs/app-store-checklist.md`'s own note on this.
- No new Gradle dependency: `NotificationCompat` comes from `androidx.core`,
  already a transitive dependency; the rest is plain `android.app`/`android.os`
  platform API - same "platform API, zero dependency surface" shape as
  `DRAFT-midi-clock-as-open-standard-seam.md`.
- Full resilience against process death (the service resurrecting with
  correct state after an OS-initiated kill) is out of scope for this
  decision - `onStartCommand` returns `START_NOT_STICKY` deliberately, since
  resurrecting the Service alone without the rest of the app's
  `attach()`-driven state would be a half-restored, confusing result rather
  than a real fix.
- The zero-permission alternative (raise the phone's own screen-timeout, keep
  the app foregrounded) is not replaced by this feature - it remains the
  simpler option for the common case, stated first in both the Settings copy
  and `README.md`'s "Living on the Glyph Matrix" section.

## Alternatives considered

1. **Stop calling `MetronomeEngine.stop()` on any Glyph Toy unbind, with no
   new setting** - rejected: this would also stop the deliberate toy-switch
   case from stopping playback, which the performer confirmed should keep
   stopping. An opt-in setting is what turns an unrequested global behavior
   change into an actual choice.
2. **`mediaPlayback` foreground service type** - rejected: assumes
   continuous audio, which isn't always true here (Glyph-Matrix-only
   practice with the click off is a real use case for this mode).
3. **Gate the feature behind granting both permissions upfront** - rejected
   per explicit instruction: both must be optional nudges, and the feature
   must keep working, just less aggressively, if either is declined.
4. **A `WorkManager` periodic job instead of a foreground service** -
   rejected: `WorkManager`'s periodic floor (~15 minutes) is far too coarse
   for a metronome that needs continuous, precise timing; a foreground
   service is the correct mechanism for continuous work, not periodic
   background work.

## Revision triggers

- Real usage feedback finds `START_NOT_STICKY` insufficient (a killed
  session regularly fails to come back) - revisit process-death resilience
  as its own decision, not a quick patch on top of this one.
- Play Console review rejects or requires changing the `specialUse`
  justification string - revisit the foreground service type.
- A future feature's core function genuinely requires continuous audio
  playback - reconsider whether `mediaPlayback` fits that feature, without
  reclassifying persistent playback's own type to fit it.

## Amendments

*None.*
