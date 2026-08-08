# ADR-XXXX — A JSON Schema Validator Is a Test Dependency of the Conformance Gate

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-08 |
| **Pends on** | Nothing — ready to be argued |

## Context

The org house-stack record fixes a blessed set for code QM builds — FastAPI,
SQLModel/Pydantic, Metaflow, Click, Jinja2, httpx, Alembic, pytest, uv — and
requires a record for anything outside it, org-level, before that dependency
appears in review. Its carve-outs cover contributions written in a target
community's idiom, client- or platform-mandated stacks, and engines. None of
the three covers this case.

The event envelope record commits this project to emitting JSON Schema as a
build artifact and checking golden vectors against it in CI. That commitment
has a consequence the record does not spell out: the check has to run against
the *emitted artifact*, not against the Pydantic models that produced it.

The distinction is the whole point of the gate rather than a technicality. A
consumer written in another language — the case the envelope record exists to
protect — holds the JSON Schema and nothing else. It does not have Pydantic,
and it will never execute a Python validator. A guarantee established only by
round-tripping the models proves the models agree with themselves. It says
nothing about whether the artifact those consumers actually hold accepts a
valid event and refuses a malformed one.

Pydantic emits JSON Schema and validates through its own core. It does not
consume JSON Schema, so it cannot be the thing that checks its own output.
Nothing else in the blessed set validates JSON Schema either.

## Decision

1. **`jsonschema` is adopted as a development dependency of the schema
   package**, for the sole purpose of validating golden vectors against the
   emitted JSON Schema artifact.
2. **It is a development dependency and never a runtime one.** It appears in
   the `dev` dependency group. The package imports it lazily, inside the
   conformance helper rather than at module scope, so the runtime package
   loads without it. A runtime import of `jsonschema` is a review failure.
3. **Its scope is the conformance gate.** It does not become this project's
   validation layer. Pydantic validates at the boundaries of running code;
   `jsonschema` exists to answer one question, which is whether the artifact
   a foreign consumer holds behaves as claimed.
4. **The validator is pinned to a JSON Schema draft explicitly**
   (Draft 2020-12, which is what Pydantic v2 emits). A validator that infers
   the draft from the document would silently change behaviour if the emitted
   dialect changed.
5. **This record adds a constraint and waives none.** The house-stack record's
   requirement is a record before review; this is that record.

## Consequences

- The conformance assertion becomes what it claims to be. Six valid vectors
  and three malformed ones are checked against the artifact a third party
  would hold, and the check fails the build.
- Accepted cost: one dependency outside the blessed set, carried for tests
  only. The friction of writing this record is the mechanism working, not an
  obstacle to route around.
- Accepted cost: a second validation implementation now exists in the
  project. Pydantic and `jsonschema` could in principle disagree about the
  same payload. That disagreement is not a defect to suppress — it is the gate
  detecting that the emitted artifact and the models have diverged, which is
  precisely the failure this dependency is here to catch.
- Obligation created: the lazy-import boundary in clause 2 needs to hold as
  the package grows. It is currently one import statement inside one function.
- This dependency is invisible to the project's own license gate until that
  gate exists, and its license (MIT) has not been machine-checked here. It
  will be, by the dependency-manifest path the org open-license record
  provides for.

## Alternatives considered

1. **Validate the vectors with the Pydantic models and call it done.** It lost
   because it changes what the assertion means without saying so. It proves
   the models accept what the models accept. The claim the project makes is
   about a language-neutral artifact, and this alternative tests everything
   except that artifact — a green gate that is evidence for a different
   proposition than the one it appears to support.
2. **Write a minimal JSON Schema validator inside the project.** It lost on
   the seam-and-engines ordering rule. A schema validator is an engine with
   many independent implementations and a specification someone else
   maintains; writing one puts bus-factor in a place the doctrine says it must
   not go, to avoid a dependency the doctrine's own process exists to admit
   deliberately.
3. **Drop JSON Schema emission and publish the Pydantic models as the
   interface.** It lost on the barrier-to-entry requirement in the envelope
   record: a contributor with a shell and an MQTT client must be able to work
   against this envelope without adopting Python, and a consumer in another
   language needs a schema it can read.
4. **Use a validator from a wider ecosystem already present for another
   reason** — there is no such dependency in this project, so the alternative
   is empty today. It is recorded because it is the answer that would change
   this record if a future dependency brought a validator with it.
5. **Petition to add `jsonschema` to the org blessed set instead.** It lost on
   scope, not on merit. One project needing a validator for one gate is not
   evidence that the house stack is missing something. The org corpus's own
   standard is that a second project asking the same question is the signal a
   clause belongs at org level — if a second QM project needs JSON Schema
   validation, this record should be promoted rather than repeated.

## Revision triggers

- A second QM project adopts a JSON Schema validator, which by the corpus's
  own standard makes this an org-level question rather than a project one.
- Pydantic gains the ability to validate against a JSON Schema document,
  removing the reason this dependency exists.
- `jsonschema` is abandoned, relicensed outside the OSI/FSF criterion, or its
  Draft 2020-12 support diverges from what Pydantic emits.
- The emitted dialect changes, which makes clause 4's explicit pin wrong
  rather than merely careful.
- A runtime import of `jsonschema` appears, which means clause 2 has failed
  and the dependency's scope needs restating or widening on purpose.

## Amendments

*None.*
