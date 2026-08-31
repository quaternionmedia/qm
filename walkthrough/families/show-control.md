# Cookbook — the `show-control` family

**This page is generated.** Every figure comes from `families.json` and from the clones on this disk, and `uv run qm cookbook --check` fails the build when it stops being true. Do not edit it; edit the roster or the record and regenerate.

**Drives** the room — cues, lighting, sound and video playback, audio transport

![the show-control family](./show-control.svg)

## Who is in it

| member | governed |
|---|---|
| `ShowRunner` | no |
| `Cuelist-python` | no |
| `QLab-python` | no |
| `TheatreMix-python` | no |
| `cesar` | no |
| `ShowStopper` | no |
| `aes` | no |

## Starting here

**No member of this family carries governance yet**, so there is no governed entry point and this page will not invent one. Reading the code is the entry point.

Adopting one is `handbook/forking-a-project.md` — nine steps, taken one repository at a time, and a decision per repository rather than per family. Nothing here recommends which; that is the border test in `records/DRAFT-a-family-is-bordered-by-what-it-drives.md` §2 applied by somebody who knows what the code does.

## What this page deliberately does not carry

**Anything machine-scoped.** Which branch a clone is on, how many uncommitted files it has, whether it is on this disk at all — none of that is here, because this page is committed and those facts differ per machine and per keystroke. A committed document carrying them drifts every time somebody edits a file, and a check that fails hourly is one people learn to rerun rather than read.

`ci/workspace.yaml` and `status/inventory.yaml` make the same split for the same reason, with the machine-scoped half in an uncommitted companion. Run `uv run qm cookbook` with no argument to see this family's state on the disk you are actually sitting at.

## What this page cannot tell you

Whether any of it works. It reports a claim — the family, stated by a person in the roster — and it does not run a member. A family name is never a statement that anybody is working on it.

*Generated 2026-08-31 from `families.json`.*
