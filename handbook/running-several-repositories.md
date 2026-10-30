# Handbook — Running Several Repositories on One Workstation, and Telling Them Apart

**Routing.** How the estate's servers run side by side on one machine, started
by a person and by several sessions at once, and how anyone can say which
server is which. It is the procedure behind
`records/DRAFT-monitoring-seam-and-instance-identity.md`, which owns the why,
and it binds QM's own conduct, not a project's design.

**Audience.** A person bringing the estate up; a session about to start a
server; anyone looking at a busy port and asking whose it is.

---

## Three ways a server runs here

| Who runs it | Command | Its port | What declares it |
|---|---|---|---|
| A person, one of each surface | `uv run qm dashboard --start <surface>` | the surface's constant | qmcp declares itself; the dashboard declares the rest |
| The performing family, alone then together | `uv run qm family-demo` | inside `ci/family-demo.yaml`'s `ports`, moved by `--port-offset N` for a second family | the run's manifest, not a run-file |
| A session, for anything else | `uv run qm instances run --repo <name> --session <who> -- <command with {port}>` | free, chosen as it starts | the wrapper, for as long as the server lives |

The constants are a memory aid for a person's own surfaces, the ones a browser
keeps open; `docs/ref/ci/demos.md` lists them. A session takes a free port
instead, because a constant port is the one a person's own server is already
on, and a session that measures a port it did not start has measured somebody
else's server.

A stack that its owner brings up in containers, such as alfred's with joe, is
started once, by the session that owns it, and the others use it. Ask that
session rather than starting a second.

## What a session does

1. **Serve from its own checkout.** A worktree of its own, never another
   session's working tree: `perspectives/2026-10-25-two-sessions-one-checkout.md`
   is what sharing one costs.
2. **Take a free port.** `qm instances run` picks one and puts it where the
   command says `{port}`. qmcp can be asked for port 0 directly, because it
   declares the port it bound.
3. **Keep its own state.** qmcp's queue is a database path, and by default a
   path relative to the working directory, so two qmcp in one checkout share a
   queue. Each instance gets its own `QMCP_DATABASE_URL`.
4. **Say who it is.** `--session` on the wrapper, `QMCP_SESSION` for qmcp. The
   name is what a person reads in the monitor to find the session to ask.
5. **Stop what it started, by its pid.** `qm dashboard --stop <surface>`, or
   interrupting the wrapper, which withdraws its run-file. Never by port: a
   port names whoever holds it now. A process killed outright leaves its
   run-file behind, and `qm instances prune` removes the ones whose process is
   gone.
6. **Leave everything else alone.** A server another session started is that
   session's to stop.

## Watching them

```bash
uv run qm instances                      # every declared server, and which it is
uv run qm instances --port 8000          # also a port nothing declares
uv run qm instances --check              # exit 1 on stale, mismatch or undeclared
uv run qm instances prune                # the run-files whose process is gone; --yes removes them
```

It reads every run-file in `~/.qm/run/` and qmcp's `~/.qmcp/run/`, asks the
operating system whether each process is alive, and asks the declared port's
health path, and only that path, which server answers. Then it probes the ports
the estate reserves for a listener nobody declared.

| State | What it means | What to do |
|---|---|---|
| `identified` | the port answers as the process its run-file names | nothing |
| `answering` | the port answers, and the server does not say which it is | trust it only as far as its run-file: the server states no pid |
| `silent` | the process is alive and its port does not answer | it is starting, or hung; read its log |
| `stale` | the process is gone and its run-file is not | `qm instances prune`; if another process answers its port, find out whose before using it |
| `mismatch` | the port answers as a different process | the declaration is wrong or a second server took the port; trust neither |
| `undeclared` | a reserved port, or one named with `--port`, is held and nothing declares it | find its owner before treating it as yours |

The document `--write` makes is machine-scoped: it is true on this machine at
its `generated_at`, and it is written outside every repository.

**What it cannot see.** A server that writes no run-file and holds no reserved
port, unless its port is named with `--port`. Whether a server that answers is
serving the commit its checkout is on. Anything on another machine.

## Where everything lives

All of it is machine-scoped, and none of it is committed:

- `~/.qm/run/` and `~/.qmcp/run/`: one run-file per serving process;
- `~/.qm/dashboard.json`: the pids `qm dashboard --start` launched, and
  `~/.qm/<surface>.log` for each one's output;
- `~/.qm/instances.json`: the collector's document, when written.

## How this was proven

`perspectives/2026-10-29-several-repositories-one-workstation.md` is the run
this page was written from: three sessions and a shared stack on one
workstation, the faults it was made to show, and what the collector said at
each step.
