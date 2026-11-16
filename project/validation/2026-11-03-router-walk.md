# The router walked in the demo, 2026-11-03

The AnoleX 4060-Evo Ultra 2's integration -- the machine drawn, GRBL's dialect
of the machine seam, its Machine in the page -- walked by hand against the
simulated controller in `apothecary serve --demo`, one step at a time, each
step approved from its picture and the live page before the next. The real
machine was not on the bench: [project/bench-checklist.md](../bench-checklist.md)
section I is that walk. Everything below ran on `build/router-machine`; what
the walk changed is in the commits after it.

## What was walked

| Step | What the page showed |
|---|---|
| The router in the world | `cnc_router` on its stand against the east wall, the working area as a wire box on its table, the tool marker over the middle of the table, the 🪚 badge reading `idle` with its port; Selected naming the part, the footprint, the build volume, and the device pinned via `frame_system.controller` |
| Its Machine | Opened from the badge: `Grbl 1.3a` and the controller's name in the head, `$I` where a printer has M115; Status with the state and the controller's word, the tool in the work zero and in machine coordinates, the spindle, the feed and overrides, the pins on; *Cut from here* in place of Print, with no Slice |
| Its pad, driven from the pane | Armed; jogs in X and Z sent as `$J=`; a jog past the travel refused by the controller (`error:15`) and said so; Home (`$H`, answered when done, ten seconds); disarmed; `$I` again |
| A cut from here | The kept file, ▶ Cut: the badge `running · cut 41%`, the state card running with `Run`, the spindle at the file's speed, the tool moving. Pause: `hold`, `Hold:1`, the position still across two polls. Resume: running again, to its end |
| The stop | E-STOP mid-jog: `RESET`, `ALARM:3`, the banner and the controller's hint in the log; the state card alarm with its number, the badge alarm, the spindle off. Unlock (`$X`): `Caution: Unlocked`, idle again |
| The ring | `m` on cnc_router: eight cells, Device last; Device › Control is the router's: Home, Zero, Unlock, Cut, Jog, Stop (destructive), Spindle, Arm |

## What the walk found, and what was done

- A controller's refusal and an alarm showed their bare numbers. The seam
  knows GRBL's words for them (`grbl.ERRORS`, `grbl.ALARMS`): the port's log
  now keeps the words beside the line, a refusal carries them, and the state
  card says the alarm's.
- Selected's Status offered a printer's words on the router. A machine's
  Status offers its own: a router's idle, offline and maintenance by hand,
  with whatever its polls set shown but not offered; and a word the polls set
  while the piece is selected is drawn, not left stale.
- A node ring's Control said Arm while the latch was armed, for a printer as
  for the router: the page told the resolver nothing of the latch. The open
  Machine's latch is what the ring is told now.
- The first cut on the reloading demo ended as "the server stopped while it
  ran": `serve --reload` watched the whole checkout, so a branch checked out
  in a worktree inside it restarted the server mid-cut. The reloader was
  narrowed to the package and the templates.
- The progress line counts lines queued, not cut: the controller holds
  fifteen moves, so it reads ahead of the tool. A sender shows the same, and
  the job is done only when the controller is idle again. Left as it is.

## Not covered

The real controller: what `$I` and `$$` answer, the USB bridge, whether DTR
resets it, which way it homes, and the bounds the seam takes from the maker's
figures. Section I of the bench checklist.
