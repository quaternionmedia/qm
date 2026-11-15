# The family started through the hub, 2026-11-05

Run on this machine against `apothecary serve --demo`, on `build/family-beside`, with
the hub starting the members itself. The machines and the devkit are simulated. carlos
and joe are real, each on its family branch: carlos on `feat/hold-the-rig`, joe's API on
`feat/family-control`, named in the table's `start`. The tests cannot run this, since no
test checks out another repository's member for an ordinary run.

## What each did

One procedure with a step for every member, each fired on GO through the coordinator.

| Step | Member | Reached | Came of it |
|---|---|---|---|
| Look over the bench | a person | | Done by its GO |
| Hold the bench in carlos | carlos | push | Answered 200, and carlos held the garage's wiring as it stood |
| Flash the devkit | board | hosted | Answered 202; the scripted flash ended well |
| Hear its hello | board | hosted | Answered 202; the devkit said the sketch's hello |
| Take a phrase | joe | push | Answered 202; joe synthesized it and its pipeline found note events in the take, as its own state said afterwards |
| Home the printer, control down | machine | hosted | Refused 422 in the member's words, and the next step held |
| Home the printer, control armed by hand | machine | hosted | Answered 202; homed by `G28` |
| Home the router | machine | hosted | Answered 202; homed by `$H`, once the log said the printer was idle |
| Keep a frame | camera | a page's to read | Fired, and stands so: nothing reads it yet |

`hearth check --hub` found the hub conforming, and `hearth check` found `machine` and
`board` conforming. It found carlos and joe not conforming, the same two routes short:
neither answers `/family/events` or `/family/identity`, so the audit keeps their
deliveries with no instance.

## What running it found

- **A `ready` that redirects never counts as up.** carlos's `/` answers 307, so it stood
  at starting while it answered every delivery, and the supervisor would have restarted
  it at two minutes. `docs/family.md` now says `ready` answers 200.
- **carlos will not start while its port is in TIME_WAIT**, after the hub restarts at
  once: its own check of the port refuses, and says the port is taken. The supervisor
  retried, and carlos came up within a minute with nothing done by hand.
- **A step answered 202 by a member beside the hub reads as fired for good.** joe had
  finished, and its step cannot say so: a hub reads only a hosted member's later word.
  The next step is not held by it.
- **Stopping the server stopped every member.** Nothing was left listening on any of the
  three ports.

## Not run

No real machine or board: the bench is section I of `project/bench-checklist.md`. The two
draft branches named above are the only place carlos's and joe's sides exist, so this
holds for those commits alone.
