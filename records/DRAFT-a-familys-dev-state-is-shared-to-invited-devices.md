# QM-XXXX — A Family's Dev State Is Shared by One Standing Host, to Invited Devices Only

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-11-24 |
| **Namespace** | org |
| **Binds** | This corpus, and any project that adopts it |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `ownership-is-the-deliverable` — the share runs on a host the organisation holds, and no request to it passes through a relay somebody else rents out; `systems-over-heroics` — a share is recreated from commits and a manifest, and its state from a snapshot, never from what one developer's machine happens to hold |

## Context

Before alpha, the people who try a QM application are its maintainers and the
sessions working across its family, not outside testers. They need the application in its
development state: the branch the work is on, with the engines it drives,
behind it. Some of them are on the machine that runs it, some on the same
network, and some elsewhere. What they make in it has to be there when they
come back, and a finding one of them reports has to name something another
can reproduce.

**What the estate already gives a person on one machine.** alfred's dev stack
publishes on loopback, and one opt-in publishes it on every interface for a
phone on the same network, with a warning when the development login bypass is
on as well. Its family loop brings joe up beside it with one command, and its
host run does the same without containers. The corpus's dashboard gives each
surface a constant port, `handbook/running-several-repositories.md` has the
session that owns alfred's stack start it once for every other session, and the
instance collector of `records/DRAFT-monitoring-seam-and-instance-identity.md`
says which server holds which port. `qm family-demo` runs the performing
family together, each member on ports of its own. The corpus's site is built
statically from `main`, and alfred's browser suite records its walkthroughs
for docs served locally.

**What none of it gives.**

- **Nothing reaches a maintainer off the network.** The dev stack's widest
  setting is the local network, and the bypass that makes a dev stack
  convenient makes every visitor a superuser.
- **Nothing says which commit a running server serves.** A dev stack serves a
  working tree through a reloader, so what it runs changes when a file is
  saved or a branch is checked out, and a server started by hand declares
  nothing at all.
- **Nothing keeps a visitor's work apart from a developer's.** The dev stack's
  database is the developer's own, reseeded and dropped as the work needs.

**The application cannot be shown without its server.** alfred draws every
preview frame and every render on the server, from a database and a render
worker, with joe hearing its sound. A page with no server behind it shows
pictures of alfred, not alfred.

## Decision

**A family's development state is shared by one standing share on one host,
reached only from devices invited onto a private network, serving commits a
machine-scoped manifest names, with state of its own that is snapshotted by
name.**

### §1 — Reached from invited devices only

A share is reached through a private network that only enrolled devices join,
and never at a public address: nothing of it is on the public internet. A
session on the host, a device on the local network and a device elsewhere use
the same address, so a link one of them sends works for the others. The host
may also serve it on its own loopback, for the sessions and monitors on that
machine.

Enrolling a device is the share's operator's act, one device at a time.

### §2 — The application's own login, and no bypass

Every visitor signs in with an account of their own, which the operator makes;
registration stays closed. A development bypass of the login never runs in a
share, whatever a member's settings say.

**A member that asks no login is never reachable from a device.** It is bound
to the host's loopback, or to a network only the share's members join, and a
visitor reaches it only through the member that drives it.

### §3 — It serves commits, never a working tree

Each member runs from a tree the share owns, checked out at one commit, and
built from that commit alone. Nothing in a share watches files or reloads:
saving a file in a developer's checkout changes nothing the share serves.

**One manifest names each member and its commit.** It is a claim about one
machine, like the record of which repositories a machine should run, so it is
kept beside the share's state, outside every repository, and never committed.
A person moves the share by moving the manifest, through the share's own
command, which checks the commit out in the share's tree, rebuilds what
changed, and restarts it. The repositories hold how a share works and how to
run one; the manifest holds what one host's share is serving.

### §4 — It says what it serves

Asked, a share reports for every member the commit the manifest names, the
commit actually running, and whether the member answers as itself, by the name
its own server gives. A member whose answer cannot be read is reported as
unknown, never as up. A finding against a share names the commit the report
gave, and is reproducible from that commit and a snapshot of the state it
names.

### §5 — Its state is its own, and is snapshotted by name

A share's databases and media live in a directory of the share's, apart from
every developer's development state. They survive a restart and a move to new
commits. A snapshot is taken by name and holds the databases, the media and the
manifest it was taken under; restoring one replaces the share's state whole,
and may carry it to the share after a move. A snapshot is trusted once it has
been restored.

### §6 — One standing share, up while its host is

There is one standing share per family per host. It comes back by itself when
its host does, and its ports are apart from every development default, so a
share and a developer's own servers run side by side without moving either.
Which host, which private network and which container runtime are settings and
a project's choices, stated in that project's documentation or under
`adapters/`; this record names none of them.

### §7 — A share asserts nothing

A share is a draft, as a branch and a local build are
(`records/DRAFT-version-tags-are-claims.md` §4): it shows a commit and claims
nothing about it. The version tag stays the gate for what a project ships, and
the work stays delivered as pull requests
(`records/DRAFT-work-is-delivered-into-a-repository.md`). A share is a running
copy of commits those pull requests hold.

## Consequences

- A maintainer anywhere reaches the family's development state at one address,
  signed in, with their own work kept between visits.
- A finding names a commit and a snapshot. That replaces "it broke on the dev
  server" with something another person can run.
- The host's availability is the share's. When it sleeps, the share is down,
  and the cost is accepted: the alternative is a host the organisation does not
  hold.
- The host pays for the share in disk: its state and every snapshot kept. The
  share's command reports the space its state takes, and the operator removes
  snapshots.
- Inviting a person costs two acts of the operator's: enrolling their device and
  making their account. Neither is automated, because each grants access.
- A member that asks no login reaches visitors only through the member that
  drives it. A member that must be reached directly first gets a login.
- A member joins by being named in the manifest and run by the share's command
  from its own commit, with its state in the share's directory. A project
  documents how its members join; alfred's documentation is the first.
- A share does not replace a recorded walkthrough. The walkthrough is the
  record of what a commit does, regenerated by the command run before a pull
  request; the share is where a person does something the walkthrough did not.

## Alternatives considered

Each option is weighed by what it costs, what it cannot do, and what keeps it
from going stale.

1. **A static site, built from a repository by a workflow.** It costs one
   workflow and keeps itself current: it is rebuilt from `main` on every push.
   It cannot run a server, a database, a render worker or an engine, and alfred
   draws every frame on its server, so a static page holds pictures and
   recordings of the application, not the application. It stays the right home
   for documentation and for recorded walkthroughs, and is rejected as a share.
2. **An ephemeral tunnel, or sharing from one editor to another.** It costs one
   command and no configuration. It cannot outlive the session that opened it,
   its address changes each time, so nothing can link to it, and it exposes
   whatever the developer's working tree runs at that moment, bypass included.
   Its traffic passes through the tunnel provider's relay. It never goes stale
   and is never stable, which is why it is rejected.
3. **A public address, with the application's login as the only gate.** It
   costs a domain, certificates and an open port, and stays current as the share
   does. It cannot keep a development branch's unreviewed routes off the
   internet: a route a branch leaves open is open to everyone, and nothing
   reviews a development branch for exposure. Rejected.
4. **A public address, gated by a login at a reverse proxy.** It costs the
   above and a second set of credentials to keep. It is defensible, and it
   loses to §1, which gives the same reach with nothing on the public internet
   and grants access per device rather than per password.
5. **A preview environment for every pull request.** It costs a stack, ports
   and state for every open branch, and a cleanup when each merges or closes; a
   project with a long stack of open pull requests would run as many stacks on
   one host. It cannot carry a visitor's work from one branch to the next. It
   keeps itself current by rebuilding on every push. Rejected for the standing
   share of §6: a branch is tried by moving the share to it, with its state
   carried over or a snapshot restored.
6. **A recorded or executable walkthrough.** It costs nothing more: the browser
   suite records the walk, and the docs play it where they are served
   (`records/DRAFT-one-executable-walkthrough.md`). It cannot let a person do
   anything the recording did not, or bring their own media. It keeps itself
   current because it is regenerated by the command run before a pull request.
   It is kept, beside a share, not in place of one.
7. **State reseeded at every start.** It costs nothing and cannot go stale. It
   cannot keep a visitor's work, so nobody can come back to what they made.
   Rejected for §5.
8. **A committed manifest, in the corpus or in the project.** It makes every
   move a diff. It also makes every move a pull request, and a project whose
   `main` merges only with an approving review would hold its share at a commit
   until a reviewer had time. A committed file cannot say what one host is
   running either, which is §4's job. Rejected for §3's machine-scoped manifest.
9. **The developer's dev stack, opened wider.** It costs one setting. It serves
   a working tree through a reloader, so it serves no commit, and it shares its
   database with the developer's own work. Rejected for §3 and §5.

## Revision triggers

- An outside tester has to reach a share and cannot enroll a device.
- A second host runs a share of the same family, and which one a link means is
  no longer obvious.
- A member that asks no login has to be reached directly from a device.
- A share's state outgrows its host, or its host's availability stops being
  good enough, and the share moves to a host of its own.
- Moving the one share between branches becomes frequent enough that their
  state collides, and a share per branch is asked for.

## Amendments

*None.*
