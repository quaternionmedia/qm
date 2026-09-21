# ADR-XXXX — Personal data stays on the device, by construction

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-09-20 |
| **Tools** | Drafted with Claude Code (Anthropic) against `consolidate/2026-09-19`, with the audit that grounds it run as a fan-out of readers over the repository and their findings checked by hand and by `strace`; the human who sponsored the work is the contributor of record. |

## Context

Apothecary takes in things that are a person's own: photographs and the
frames a camera takes, the pieces built from them, the comms log of a
printer on the bench, its bed readings, the files streamed to it, the
boards pinned to a site, their serial numbers and addresses. The proposed
rule *It runs on your machine and the data stays there*
(`docs/plans/proposals/runs-and-stays-local.md`) says none of that leaves
the machine and nothing is loaded from elsewhere while a person is using
the tool; the vendored three.js (`static/vendor/three/README.md`) is that
rule applied once, and `tests/test_stays_local.py` checks the picture path
against it at test time.

A test-time check is a promise the tests keep. It is not the program's
shape: a server started with `--host 0.0.0.0`, a page that a later edit
made load a script from a CDN, a library that phones home the first time
it is used in production rather than in a test -- each would break the
promise without a test noticing, and each is one decision away, by a
person or by an agent. The audit that grounds this record found six of
them in the program as it stood:

- FastAPI's own Swagger and ReDoc pages, on by default, load their scripts
  from a public CDN, and one Markdown page carried a picture from a
  placeholder service that the docs renderer would have fetched.
- `arduino-cli board list`, which the seam runs on every board scan, asks
  Arduino's cloud API about every USB device its installed cores do not
  recognise. `~/.arduino15/inventory.yaml` on the bench machine held two
  such lookups from that morning, for the printer's FTDI chip and a
  CP2102: a hardware inventory, with the machine's address and the hours
  the bench is in use, leaving with no decision by anyone. arduino-cli
  also checks for its own updates, and lets a proxy variable or an
  `ARDUINO_*` variable in the environment outrank its config file.
- The server admitted a request by its peer address alone. A page from
  elsewhere that resolves its own name to 127.0.0.1 arrives from loopback
  and reads the server as itself: the captures, the camera labels, the
  serial numbers, the comms log. A page from elsewhere could also post to
  a route here without a preflight (a body with no content type is read as
  JSON), and heat a printer or start a flash, though it could read nothing
  back.
- The viewer wrote a query value (`?focus=`) raw into a script literal, so
  a crafted link the person opened would run script in this origin, read
  every route, and carry the answer out by navigating -- the one thing a
  page policy does not govern.
- The picture root, unset, is the folder the server was started in; a
  server started in a home folder serves every image beneath it.
- The Python socket guard did not cover a TLS socket wrapped before it
  connects, a name looked up on its own, or a proxy on loopback that
  forwards a tool fetch elsewhere. A second round of skeptics, set to
  break the first version of the guard without editing a file, found the
  rest: a datagram sent by `sendmsg`, a listener bound to `0.0.0.0`, a name
  resolved by `bind` or a reverse lookup, the original socket class still
  reachable under its other stdlib names (`socket.SocketType`,
  `ssl.socket`), and -- the one that matters -- that *loopback is not this
  machine* when a service there forwards: the resolver's stub at
  `127.0.0.53` takes a hand-built DNS question and sends it upstream.
  They also found two pages that put a value into the document raw: a job's
  name, and the tools folder from an environment variable on the firmware
  page, either of which would let script into this origin; a picture route
  that served any file under the root, not only pictures; a `sketch.yaml`
  beside a sketch, which arduino-cli honours whatever the command line
  says and which can name any host to fetch a platform from; and that
  `apothecary test all` ran its server on the person's own state and
  pictures.

The requirement, stated by the sponsor: personal data stays on the device
**based on the architecture of the system, never the decision of an agent
or a user**, with one named eventual exception, *secured user accounts*.

Constraints: the firmware toolchain must still be installable from the
firmware page (arduino-cli is downloaded from a fixed release host);
arduino-cli, esptool and OpenSCAD are subprocesses the guard cannot see
into; the browser tests and the docs generator run servers on this machine
and must keep working; human-only contributorship.

## Decision

1. **The process cannot reach past this machine.** Importing the
   `apothecary` package installs a guard (`apothecary/stays_local.py`)
   before any of its code runs: the socket class -- the Python one and the
   C one beneath it -- is replaced by a checked subclass that refuses to
   connect, send a datagram (`sendto` and `sendmsg` alike) or bind a
   listener anywhere but a loopback address or a Unix socket, and every
   other name the originals were bound to (`socket.SocketType`,
   `ssl.socket`, whatever a module imported by name) is rebound to the
   checked class; `socket.create_connection`, `http.client`'s connect and
   the TLS socket's connect are checked the same way; and the resolver
   (`getaddrinfo`, `gethostbyname`) refuses to look up any name but a
   loopback one or a literal address, since a hostname is the one place a
   process could carry data out without a connection, and the reverse
   lookups (`gethostbyaddr`, `getnameinfo`, asyncio's included) ask about
   this machine's addresses alone.
   Loopback is not enough on its own where a service there forwards, so
   port 53 on loopback -- the resolver's stub, which sends whatever it is
   handed upstream -- is refused to every socket: a name is asked through
   the guarded resolver, never by hand. Every apothecary process is under
   it: the server, the command line, the docs generator's server, the
   tests. There is no flag, environment variable, configuration file or
   route that turns it off.
2. **One allowance, a tool fetch, and one caller.** The firmware installer
   downloads arduino-cli through `tool_fetch(url)`, which refuses any URL
   whose host is not one of the fixed `TOOL_SOURCES` (the release API, the
   archive, where the archive redirects) before anything is opened, and
   admits the sockets and the name lookups beneath that one call, on that
   one thread, to those hosts alone -- by name, or by an address the
   guarded resolver returned for one of them -- so a redirect elsewhere is
   refused mid-fetch, and the fetch takes no proxy from the environment. A tool
   fetch is a GET of a release archive at a URL built from a version
   string, and a version is three numbers or it is refused; no personal
   data is in it. A test holds the callers of `tool_fetch` to the
   installer module: a second caller is a second door, and is reviewed as
   one.
3. **The server listens on this machine, and answers it alone.** Every
   `--host` the command line offers goes through `require_loopback()`: a
   non-loopback address is an error that names this record, not a choice.
   The application itself carries an ASGI middleware, `LocalOnly`,
   outermost, so a server started some other way (`uvicorn
   apothecary.api:app --host 0.0.0.0`, a proxy in front) answers with 403
   and nothing else unless three things hold: the client is on loopback,
   the address the request arrived on is loopback (whatever a
   forwarded-for header made the client look like; a server that names
   neither is not answered, since a peer the server cannot name is not
   this machine), and the `Host` it asked for is this machine's -- a loopback address or name, with a
   numeric port or none. The last is what stops a page from elsewhere that
   pointed its own name at 127.0.0.1 from reading this server as itself. A
   fourth holds for what a browser sends: a request whose `Origin` or
   `Sec-Fetch-Site` says it came from a page on another origin is refused
   too, so a page from elsewhere can neither post to a route here nor
   fetch or embed from one; a link from elsewhere that opens a page here
   (a GET navigation) still works. Pages, static files, the API and the
   docs alike.
4. **The pages the server sends cannot load from or send to another
   origin.** The same middleware puts a Content-Security-Policy on every
   response: scripts, styles, images, media, fonts, fetches, workers and
   forms may use this origin only (images and media also `blob:` and
   `data:`, for a camera frame drawn on a canvas); no frames, no
   embedding, no referrer. A peer connection, which would reach a STUN
   server, is outside what a browser lets a policy forbid; no page here
   creates one, and the test on the pages refuses the word. A page that
   tried to post a picture elsewhere is stopped by the browser before the
   request leaves. A page's own script can still navigate, which no policy
   governs, so nothing reaches a page raw: every value a template writes
   into a script literal -- the base URL, the site, the focus path -- is
   emitted as JSON, every value a page writes into the document -- a job's
   name, a folder from the environment, a printer's line -- goes through
   its escape, and a job's name is letters, digits and a little
   punctuation or the API refuses it; tests hold the templates to it, so
   no link, no request and no variable can put script into this origin. FastAPI's Swagger and ReDoc pages are off, since each loads
   from a CDN; the API is described by `/openapi.json`, served from here.
   The docs renderer names a picture from elsewhere rather than fetching
   it, and makes a link only of a relative, `http(s)` or `mailto` target;
   a `javascript:` target is shown as the text it was.
5. **A subprocess that fetches is told where, and nothing else tells
   it.** arduino-cli, esptool and OpenSCAD are outside a Python guard. Of
   the three only arduino-cli reaches out. Every arduino-cli the seam
   starts is given `--config-file` naming a file the package writes from
   `ARDUINO_CLI_CONFIG` whenever it differs: the cloud board lookup off,
   the update check off, the package indexes it may fetch from named
   (Arduino's own, Espressif's, the esp8266 and rp2040 indexes on their
   fixed hosts). There is no constructor argument for another file, and
   `~/.arduino15/arduino-cli.yaml` is never read under apothecary. Its
   environment is `subprocess_env()`: this process's, minus every proxy
   variable and every `ARDUINO_*` override, since arduino-cli lets either
   outrank the file; every subprocess the seam starts -- the task runner,
   the queries, the monitor -- gets that environment. What arduino-cli may
   still fetch is an index, a core or a library from those hosts, which is
   a tool fetch in all but mechanism, and nothing personal is in it. A
   sketch that carries a profile (`sketch.yaml`, `sketch.json`) is not
   built: a profile names where to fetch a platform from, arduino-cli
   honours it over the command line, and where to fetch from is the
   managed config's alone to say. One thing it sends that this record does
   not stop, and names: on every board
   scan its bundled mDNS discovery asks the local link for network boards,
   one fixed 37-byte question (`_arduino._tcp.local`) to the multicast
   address, verified with `strace`; it carries nothing of the person's,
   reaches no further than the link, and goes when the scan is made with
   pyserial instead (a revision trigger below). esptool and OpenSCAD have
   no network function; they receive a port name, an image under the
   repository, SCAD text. The docs generator's browser (Playwright's
   Chromium, launched with background networking, component updates, field
   trials and sync off) visits the loopback server it started and nothing
   else; at startup it asks the kernel, with a `connect()` on a UDP socket
   to a public address, whether IPv6 is routable, and sends nothing on it. The tools a person installs with
   their own commands -- `playwright install`, `npm install`, `git
   submodule update`, `uv sync` -- are fetches from their sources, run by
   the person, carrying nothing of theirs.
6. **What is kept is kept here, and the picture root is a folder of
   pictures.** Personal data lives in three places and nowhere else: the
   state folder (`~/.apothecary`, or `APOTHECARY_STATE_DIR`) -- devices
   with their serial numbers and addresses, camera placements with the
   browser's label for the camera, bed readings with the person's note,
   uploaded G-code; the picture root -- the pictures a person named and,
   under `captures/`, the frames a camera took; and the page's own
   `localStorage`, which holds a panel layout and never leaves the
   browser. The comms log is served on loopback and saved only when the
   person clicks *Download*, into their own downloads folder. The state
   folder and a camera's `captures/` are made readable by the account
   alone, whatever the umask says of the person's other files. The test
   suites -- `test run`, `test all`, `docs generate` -- run their servers
   on state and pictures of their own, never the person's. The picture
   root is `APOTHECARY_PICTURE_ROOT` or the folder the server was started
   in, and it is never the whole machine, the person's home folder (by
   `HOME` and by the account, which a variable cannot move) or anything
   above it, nor the state folder: a root there would serve everything of
   theirs to whatever asks, and the server refuses to read from one. What
   the picture route serves is a picture, judged by its first bytes; any
   other file under the root is refused.
7. **The rule is held by tests that would fail before a person could
   relax it.** `tests/test_stays_local.py` checks that importing the
   package installs the guard and that every way of connecting, the TLS
   socket and the resolver included, is refused past loopback; that a tool
   fetch reaches its sources and nothing else, takes no proxy, has one
   caller and accepts only a version; that every function in the command
   line that binds a server goes through `require_loopback`; that the app
   answers a non-loopback client, a listener bound elsewhere and a foreign
   `Host` with 403 on every kind of route and a loopback one with the
   policy; that no template or static module loads from, posts to or
   embeds anything from another origin; that the picture root refuses
   home and above; that the arduino-cli config is the fixed one, every
   argv carries it, the subprocess environment is scrubbed, and no other
   module in the seam starts a process; that a crafted query value comes
   back as one JSON string and every script value in every template goes
   through `tojson`; that a request from a page on another origin is
   refused, a link from one still opens a page, and a peer the server
   cannot name is refused; that a datagram, a listener, a reverse lookup
   and a hand-built question to the resolver's port are refused, and the
   original classes' other names are the guarded one; that the picture
   root refuses the account's home and the state folder and the picture
   route refuses a file that is not a picture; that a job's name is a name
   and the pages escape what they show; that a sketch with a profile is not
   built, the state folder and captures are the account's alone, and the
   suites' servers are fenced. A change that loosens any of these is a
   change to that file and to this record.
8. **The named exception: secured user accounts.** A future record may let
   data leave this machine for an account the person holds and has
   authenticated to, with consent given per account, per kind of data, and
   revocable; nothing leaves under a shared, default or anonymous account,
   and nothing leaves that the person did not name. Until such a record is
   Accepted there is no code path for it: `stays_local.py` is what would
   have to change, and the tests in §7 are what would have to be edited,
   which is the review. An agent proposing that code is proposing that
   record, not a feature.

## Service inventory

The open-license record asks every project for a list of the third-party
services in a runtime path, with the ownability test answered for each.
This is that list. Nothing personal is sent to any of them; each is
reached for a tool, and each is one edit to a fixed list away from a
mirror the person owns.

| Service | Reached by | What is sent | Replaceable by |
|---|---|---|---|
| GitHub releases (`api.github.com`, `github.com`, `objects.githubusercontent.com`, `release-assets.githubusercontent.com`) | the firmware installer, on *Install / update arduino-cli* | a GET of a version string's release archive and its checksums | an entry in `TOOL_SOURCES` and `RELEASES_*` |
| `downloads.arduino.cc` | arduino-cli, on a core or library install | the index and archive names it needs | arduino-cli's own `directories`/index settings in `ARDUINO_CLI_CONFIG` |
| `espressif.github.io`, `arduino.esp8266.com`, `github.com` (rp2040 index) | arduino-cli, on a third-party core install | the index and archive names | an entry in `PACKAGE_INDEXES` |
| Arduino's cloud board API (`api2.arduino.cc`) | nothing: off by `ARDUINO_CLI_CONFIG` | -- | -- |
| Arduino's update endpoint | nothing: off by `ARDUINO_CLI_CONFIG` | -- | -- |
| the local link's multicast address | arduino-cli's mDNS discovery, on a board scan | one fixed service question | a port scan with pyserial |

Install-time fetches a person runs by hand (`uv sync`, `playwright
install`, `npm install`, `git submodule update`) reach their registries
and are not runtime paths.

## Risk register

What this record does not close, and what would show it:

| Risk | Why it stands | What would show it |
|---|---|---|
| A tunnel or forwarder on this machine (`ssh -L`, an editor's port panel, a local proxy that keeps `Host: localhost`) presents a remote peer as 127.0.0.1 | the program cannot tell a forwarded loopback connection from a local one; the forwarder is the person's, outside the program | a second person's requests in the access log; §8's record is the way to want this |
| A commit carries a screenshot or a serial number | the walkthrough is written by a test run; a run pointed at a person's own server writes their state into tracked files, and `git push` is the person's act, outside the program | a tracked image with a real camera label; the docs generator's own server runs on temporary state |
| A C extension or a dependency opens its own socket | the guard is a Python object | a `strace -e trace=network` of the server showing a connect the tests did not |
| arduino-cli's multicast question on each scan | its bundled discovery has no off switch | named above; a pyserial scan removes it |
| A state folder, tools folder or picture root on a network mount | a file written to a mounted share leaves by the kernel's file system client, outside any socket; the mount is the person's, made outside the program | a `mount` listing a network file system under those folders |
| Code the person runs inside the interpreter (`sitecustomize`, a `.pth` file, `python -c` reaching for the guard's kept originals) | that is running code in the process, which no guard in the process can refuse; the guard keeps the original classes for its own tests | an import hook or a `.pth` file that names sockets; nothing in the package does |
| A service on loopback that forwards (a proxy the person runs at `127.0.0.1:3128`, say) | loopback is this machine only as far as what listens there; the resolver's stub is refused by port, a proxy the person started is theirs | a listener on loopback that is not apothecary's, with a route out |
| An installed core's `platform.txt` hooks, or a process on this machine racing the managed config's rewrite | a core is a program the person installed, and its hooks run at compile as it says; a process rewriting a file under the person's account is code running as them | a hook line the core's release did not carry; a config file whose content is not `ARDUINO_CLI_CONFIG` when arduino-cli reads it |
| `ARDUINO_CLI` (or `PATH`) names the arduino-cli binary the seam runs | naming a program to run is installing one, and the tests use it to stand in a scripted arduino-cli; whatever is named runs under the managed config and the scrubbed environment | a binary at that path that is not arduino-cli; a checksum of the managed binary would close it and is not built |
| Another user on the same machine | the state folder and the captures are files under the person's home, with the person's own permissions; loopback is shared by every account | a file mode wider than the person's; the OS's boundary, not this program's |

## Consequences

- A person or an agent cannot make personal data leave this machine by
  setting anything; they can only edit the guard, which is one file with a
  test on every door, and that edit is reviewed against this record.
- A feature that needs an outside service is not built until it can be
  built here, or until §8's record exists -- the proposed rule's own
  consequence, now with a mechanism behind it.
- The Swagger and ReDoc pages are gone; `/openapi.json` remains. A person
  who wants a rendered API page renders it from that file with a tool on
  their machine.
- The firmware page's *Install / update arduino-cli* still works: it is
  the one tool fetch, in the server process, on its own thread, to the
  fixed hosts. Core and library installs are arduino-cli's own fetches
  from the hosts in its managed config. A person's own
  `~/.arduino15/arduino-cli.yaml` -- an extra index, a proxy -- has no
  effect under apothecary; that is the point, and the firmware page says
  which file is in use.
- A board scan no longer asks Arduino's cloud what a USB device is; an
  unrecognised device is shown by its port and its USB ids, as before,
  without a name from elsewhere.
- A page that legitimately needed another origin -- a map tile, a font, a
  library -- would have to be vendored, as three.js was; the policy will
  not let it load otherwise. That is the cost, and it is accepted.
- The server refuses a picture root at or above the person's home folder
  with a message that says where to start it instead.
- A page on the person's own machine that reaches the server by a name
  that is not loopback (a hosts-file alias, `app.localhost`) gets 403;
  `localhost`, `127.0.0.1` and `[::1]` are the names.
- `python -m uvicorn apothecary.api:app --host 0.0.0.0` no longer binds at
  all: the listener is refused at the socket, with the rule's message,
  before the middleware would have refused each request.
- A job is named with letters, digits, spaces and `.+-/_`; a name that was
  markup is refused with 422.
- A link on a page elsewhere still opens the viewer; a script on a page
  elsewhere gets nothing from it and can start nothing in it.

## Alternatives considered

1. **A test-time guard only** (what `tests/test_stays_local.py` was) --
   lost because it keeps the promise only while the tests run; the program
   itself would send whatever a later edit or a flag told it to.
2. **A setting, off by default** (`APOTHECARY_LOCAL_ONLY=1`) -- lost
   because a setting is a decision, and the requirement is that neither a
   person nor an agent gets to make it.
3. **A firewall or a network namespace around the process** -- honest and
   stronger, but outside the program: it depends on the machine being set
   up that way, which is exactly the kind of decision this record refuses
   to rest on. Welcome in addition, not instead.
4. **Self-hosting the Swagger assets** -- possible, but the API page is
   read by nobody the OpenAPI file does not serve; vendoring two more
   libraries for it is the wrong trade.
5. **Binding to a LAN address behind an authentication layer today** --
   this is §8's record, and it is not written; doing it now would be
   deciding it by stealth.
6. **Passing arduino-cli its settings on the command line** (`--additional-urls`,
   an env variable per key) -- lost because an env variable is what a
   person or an agent sets, and arduino-cli lets one outrank a file; the
   file the program writes, with the environment scrubbed, is the shape
   that holds.
7. **Scanning ports with pyserial instead of `arduino-cli board list`** --
   it would remove the multicast question and the dependence on
   arduino-cli for a scan, at the cost of the board-name match its
   installed cores provide; deferred, and named as the trigger below.

## Revision triggers

- A record for secured user accounts is Proposed -- §8 becomes that
  record's context, and `stays_local.py` its seam.
- A feature that cannot be built without another origin or an outside
  service is wanted for a year -- the proposed rule's own trigger.
- The tests in §7 pass while something still reaches out (a C extension,
  a subprocess carrying personal data) -- the check is theatre until the
  gap is closed, and this record says so.
- A tool source or a package index changes hosts -- `TOOL_SOURCES` or
  `PACKAGE_INDEXES` is edited, with a note here.
- The board scan is made with pyserial -- the multicast question in §5
  and the risk register go, and the service inventory loses its last row.
- A person needs the viewer on another device on their own network (a
  tablet at the printer) -- that is §8's record, or a local tunnel the
  person sets up outside the program, never a `--host`.

## Amendments

*None.*
