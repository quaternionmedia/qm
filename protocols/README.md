# Protocols

**A protocol is a named procedure somebody runs on purpose.** It takes
judgement, it produces a dated artifact, and it is invoked — nobody and nothing
triggers it automatically.

That is the whole distinction from a gate. A gate runs itself, refuses, and
answers pass or fail; `ci/gate-registry.yaml` lists those, and
`handbook/gates.md` renders them. The two registries are kept apart because
merging them makes a protocol read as always-on and a gate read as optional,
and both readings are wrong in the direction that hurts.

```sh
uv run qm protocols                      # every protocol, and when it last ran
uv run qm protocols --id security-review
uv run qm protocols --check              # refuse a declaration nobody could run
```

## Why a procedure needs a registry at all

This corpus's recurring defect is a mechanism that exists and runs nowhere: four
registry checks wired into no workflow, six rulesets drafted since 2026-08-10
and never applied, a mutation harness with no caller. Written into a handbook
page, a procedure has the same failure mode and no counter — nothing says when
it was last done, so *we review security* and *somebody reviewed security in
June* are the same sentence.

So the registry derives one fact it will not let you assert: **when each
protocol last ran**, read from the dated files under `runs/`. A protocol that
has never been run prints `NEVER RUN`. Most of this list has never been run.
That is reported and never refused — a check that failed on it is a check
somebody deletes.

## What `--check` refuses

Three things, each of which has an instance in this repository's history:

- A registered protocol with no page, or a page nobody registered. Claim layer
  and artifact layer disagreeing is the split `ci/gate-registry.yaml` keeps, for
  the same reason.
- A step invoking `uv run qm <route>` where no such route exists. A procedure
  naming a command nobody can run is a procedure nobody has run, and a renamed
  route otherwise breaks every page citing it in silence.
- A protocol with no `cannot_see`. Empty is undescribed, not thorough.

## Recording a run

Write the artifact to `runs/<YYYY-MM-DD>-<protocol-id>.md`. The filename is the
whole of the machine-readable part; `qm protocols` reads the date from it and
nothing from the contents.

**It reads not one word of what the run said.** A thorough review and a file
with the right name are the same thing to this tool, which is exactly the class
of false signal this corpus keeps finding — stated here rather than discovered.

## `optional`

A protocol marked `optional: true` binds nobody: no gate requires it, no project
has to adopt its output, and not running it is a legitimate state rather than a
lapse. The curriculum protocol is optional. The security review is not — which
does not make it enforced, only expected.
