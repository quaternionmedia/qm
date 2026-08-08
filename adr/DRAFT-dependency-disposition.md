# ADR-XXXX — Dependency disposition

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-16 |
| **Pends on** | Nothing architectural — filed Proposed rather than Accepted only because ratification is a human action per the org's own process; ratifies together with `PLAN.md` |

## Context

The org's open-license exclusion applies to every component on every path,
including encoders and browsers. Dependencies are bought engines; the seam
and the wall are the only things built here.

## Decision

| Component | License | Disposition |
|---|---|---|
| mido, python-rtmidi | MIT-class | in (1.0.0) |
| Pydantic, FastAPI, uvicorn, Click, pytest | MIT | in (0.1.0) |
| Rich | MIT | in (0.0.x) — CLI monitor terminal rendering (PLAN.md §3.6) |
| FFmpeg (incl. `ffplay`) | LGPL/GPL build | in; x264 implies the GPL build — accepted for an internal tool. `ffplay` is the CLI demo's playback mechanism (PLAN.md §3.7) — same bundled install, no separate disposition |
| x264 | GPL | **default extraction encoder** |
| VAAPI on open drivers (Mesa) | open | permitted hardware-encode path |
| **NVENC / proprietary encode SDKs** | proprietary | **excluded**; any future use requires an explicit exception ADR |
| MediaMTX | MIT | in (0.2.0) |
| **Chromium** (not Chrome) | BSD | kiosk renderer |
| playwright (Python package) | Apache-2.0 | in (0.0.x) — drives Playwright's own Chromium download for browser-driven `/wall` tests (`tests/browser/`) that double as functional documentation/tutorials; same Chromium-not-Chrome disposition as the eventual kiosk renderer above, bought once, used for both |
| python-multipart | Apache-2.0 | in (0.0.x) — FastAPI's own required dependency for `UploadFile`/multipart form parsing; backs `/wall/import`'s local-file-as-a-tile feature |
| anime.js | MIT | vendored into `wall/` |
| ShowRunner | in-house | driver plugin (1.1.0) |

No proprietary component sits on any path. Python deps are pinned via uv;
the dependency-manifest-plus-allowlist gate (house-stack + license check,
per `adr/README.md`'s CI enforcement section) runs in CI against `uv.lock`.

## Consequences

*None beyond the table above* — every disposition is stated with its
license and target release; there is no deferred cost this ADR is hiding.

## Alternatives considered

1. **NVENC for extraction speed** — rejected on license grounds; the
   handover mechanic already masks encode latency, so the speed argument
   buys aesthetics only (shorter live-preview mask), not correctness.
2. **Chrome for WebRTC maturity** — rejected; the proprietary-browser
   dependency is exactly the shape of exclusion the record exists for.
3. **The `pytest-playwright` plugin, for `tests/browser/`** — tried first,
   reverted. It requires `pytest-base-url`, which requires `python-slugify`,
   which unconditionally requires `text-unidecode` (dual-licensed
   GPL/Artistic — outside this project's allowlist even under its
   permissive option) for a convenience feature (slugifying test names
   for screenshot/trace filenames) those tests don't use. The bare
   `playwright` package plus a small hand-written `conftest.py` fixture
   gets the same coverage without the dependency.

## Revision triggers

x264 extraction latency exceeds what the handover mask can hide
aesthetically at the 0.2.0 gate (first recourse: VAAPI; exception ADR is the
last) · a dependency's license or maintenance status changes (allowlist
gate re-run).

## Amendments

*None.*
