# ADR-XXXX — The Airgap Panel's Figures Leave as a Schema-Versioned Metrics Document with Fixed Groupings

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-17 |
| **Pends on** | Nothing — ready for ratification |

## Context

The Airgap panel of the viewer computes a few dozen figures about a rotor/stator
pair -- the `airgap` part, read from its SCAD text: geometry (bore radius, frame
diameter, coverage, masses, inertia), the winding arrangement, the static field
and torque tables (mean torque, ripple, peak flux density, dominant ripple
order) and the run (speed, whirl, yoke displacement, magnetic stiffness, slip,
touchdown). In the panel they are a grouped readout under the machine: a list
formatted for the eye, with no identity a second program could address.

Those figures are wanted elsewhere. A sweep wants to compare them across cells;
a pull request wants to quote them; a sibling project wants to tabulate them
next to a printed part's measured values. Every one of those readers needs the
figure to have a stable name, a unit, and a provenance.

The org's monitoring-seam record settles the shape of such a thing: *a view reads
a document; a collector reads the world*. Exactly one component computes;
everything else parses a schema-versioned document and nothing else. The
generated-documents convention adds that a document names its generator and its
generation time. The only component that can compute these figures is the
panel's JavaScript model -- the magnetic, winding and dynamics code lives there
and is not duplicated in Python (the part's Python mirror computes surfaces and
conductor paths for the envelope, nothing electromagnetic) -- so the panel is
the collector and every Python surface is a view.

The same discipline governs the panel's inputs. The geometry it analyses is the
part's text, never a copy of it in controls; the rig it runs the geometry under
(excitation, drive, load, bearing, mount, actuation, playback) is one JSON
document in the panel, not forty sliders, because the viewer's census meters
every control of the page's own and the project's "one screen" direction counts
each one as a cost. A document in, a document out.

## Decision

1. **The panel emits one metrics document**, `schema: "airgap/metrics/1"`, with
   `generated_at` (ISO 8601, written by the panel), an optional `preset`, a
   `units` note, and `groups`. Panels › Airgap › Copy metrics produces it; the
   panel's Metrics fold is a rendering of the same object
   (`window.apothecaryAirgap.metrics()`).

2. **Group ids are a contract.** A document carries at most one each of exactly
   these groups, in this order of meaning:
   - `geometry` -- what the surfaces are: bore, frame, gaps, coverage, masses, inertia;
   - `windings` -- what the conductors are: topology, count, phases, excitation, turns, current;
   - `field` -- what the static tables say at the commutation: mean torque, ripple,
     peak B, dominant order, lcm, mean co-energy;
   - `dynamics` -- what the run says over its last 30 %: speed and ripple, whirl,
     yoke displacement, magnetic versus bearing stiffness, axial excursion,
     torsion, slip, AMB force, touchdown.
   Any other group id is a validation error. Adding a group is a schema bump.

3. **Metric keys are open; their shape is fixed.** A metric is `{key, label,
   value, unit, note}`: `key` is `snake_case`, unique within its group, addressed
   by readers as `group.key` (`field.mean_torque`); `value` is a finite number, a
   string, a boolean, or `null` for *unavailable* -- never `NaN` or an infinity,
   the two values that survive `JSON.stringify` as something else; `unit` is the
   SI unit of the number (`N·m`, `J`, `kg·m²`, `T`, `mm` where lengths are
   labelled in mm); `note` is a short qualifier (`touchdown`, `of mean torque`,
   `release the slider`). A new figure is a new key in an existing group, not a
   schema change.

4. **Python validates and renders; it never computes a figure.**
   `apothecary.airgap_metrics` holds the Pydantic schema (`AirgapMetrics`,
   `MetricGroup`, `Metric`), `load_metrics`, and `render_markdown`;
   `GET /airgap/metrics/schema` serves the JSON Schema, `POST
   /airgap/metrics/validate` returns the normalized document or its Markdown
   (`?format=md`), and `apothecary airgap metrics validate|schema` does the same
   from the shell. The Markdown view rounds for display (`37.86 mm` renders as
   `37.9 mm`) and is a claim about the document it was handed, never a
   recomputation; its tests assert exactly that.

5. **Values are stored at full precision in SI; views round.** The document
   carries `0.00716` N·m, not `7.16 mN·m`; the panel and the Markdown view choose
   prefixes and decimals. A reader comparing two documents compares values, not
   strings.

6. **A metrics document is not a time series and is not committed.** It
   describes one geometry at one moment. Comparing across a sweep is a reader's
   job (a table of documents), and a document is an artifact of a session, like
   a rendered STL, not a file in the repository -- the disposition the
   generated-documents convention gives machine-scoped output.

7. **The panel's inputs are documents too.** The geometry is the part's SCAD
   text, as the project's part-editing decision has it (*the text is the
   truth*); the rig is one JSON document checked in the panel against its
   settings' ranges, a value outside its range clamped and said, an unknown name
   refused. Neither is a second set of controls.

## Consequences

- Figures have names. A PR can say `field.mean_torque = 0.0382 N·m` and a
  reviewer can reproduce it by putting the same text in the editor and copying
  the metrics.
- The Python side stays small and honest: a schema and a view, no second
  implementation of the magnetic model to drift from the first. Cost accepted: a
  figure cannot be produced without running the panel in a browser; a headless
  producer is a future decision (see *Revision triggers*).
- Obligations created: `tests/test_airgap_metrics.py` carries good and bad
  documents for every rule in §2 and §3 (unknown group, duplicate group,
  duplicate key, bad key, non-finite value, missing timestamp) and a view test
  that pins rounding as a display concern; the JSON Schema endpoint is the
  published contract and changes to it are reviewed.
- Cost accepted: four fixed groups will someday be wrong (a thermal group, a cost
  group). That is a schema bump to `airgap/metrics/2`, by design, so a reader of
  a `/1` document is never surprised by a group it does not know.
- Cost accepted: the rig as a text is less discoverable than sliders. The
  presets fill it, the panel says each setting's range when one is wrong, and
  the panel's documentation lists them; a slider per setting is the thing the
  census exists to refuse.

## Alternatives considered

1. **Flat metrics in the Prometheus idiom (`airgap_mean_torque_newton_metres`)**
   -- lost. A run is one document about one geometry, not a scrape of a running
   instance; the idiom brings instance identity, which the monitoring-seam
   record spends nine clauses on and which has no referent here.
2. **Free-form JSON, whatever the readout happened to show** -- lost. Groupings
   are the point: without a contract on group ids, every reader rediscovers that
   `ripple` means two different things depending on the excitation mode, and the
   sweep table has to guess.
3. **Compute the figures in Python from the part's text** -- lost. It would make
   the Python side a second magnetic model (winding functions, permeance tables,
   finite-difference stiffnesses, an RK4 integrator) that has to agree with the
   first to the digit; the part's Python mirror already carries the *geometry*
   pipeline as a second implementation and pins it to the SCAD with echo tests,
   and that cost is paid once. The view/collector split keeps it at once.
4. **Render the Markdown in the browser and skip Python entirely** -- lost. The
   Markdown is for places the browser is not (a PR, a sibling repository's
   notes), and validation in Python is what makes the schema a contract rather
   than a convention.
5. **The rig as controls, grouped and folded** -- lost on the census. Forty
   controls of the page's own for one panel, against a meter the project holds
   at a ceiling and a ring-backed floor; the geometry already has its controls,
   in the part editor, and the rig is a setting sheet, read and set whole.

## Revision triggers

- A second producer appears (a headless sweep writing documents from a script, a
  CI job rendering a part's metrics) -- the collector is no longer singular and
  §4's "never computes" needs a named exception or a shared engine.
- A reader needs a group not in §2 -- schema bump, new record or amendment
  naming the group's meaning.
- A consumer wants history (the same geometry's figures over commits) -- that is
  a time-series decision, not an amendment to a document schema.
- The generated-documents convention changes what a document must carry (a
  generator commit, a staleness budget) -- the document gains the field and the
  schema bumps.
- The rig wants validating outside the panel (a rig file beside a part, a rig in
  a PR) -- it becomes a schema of its own, `airgap/rig/1`, with the same split.

## Amendments

*None.*
