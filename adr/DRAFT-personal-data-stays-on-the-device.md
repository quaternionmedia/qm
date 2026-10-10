# ADR-XXXX — Personal data stays on the device, by construction

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-09-20 |
| **Tools** | Drafted with Claude Code (Anthropic). The audit that grounds it was run against `consolidate/2026-09-19` as a fan-out of readers over the repository, its findings checked by hand and by `strace`. What each import of the package loads, and what each install point weighed here would guard, was established by importing each module in a fresh interpreter: against `review/2026-09-26` at `595b433`, where importing the package installs the guard, and against scratch copies of that commit with the install moved to each shape weighed here. The `uvicorn` behaviour in §3 is that of uvicorn 0.38.0, run in a network namespace of its own. The hosts the Rust install for the ESP32 reaches were established by tracing a real install and an offline build with `strace`, against `build/rust-firmware` at `0c89e92`. The human who sponsored the work is the contributor of record. |

## Context

Apothecary takes in things that are a person's own: photographs and the
frames a camera takes, the pieces built from them, the comms log of a
printer on the bench, its bed readings, the files streamed to it, the
boards pinned to a site, their serial numbers and addresses. The proposed
rule *It runs on your machine and the data stays there*
(`docs/plans/proposals/runs-and-stays-local.md` at `consolidate/2026-09-19`)
says none of that leaves the machine and nothing is loaded from elsewhere
while a person is using the tool; the vendored three.js
(`apothecary/static/vendor/three/README.md`) is that
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

Apothecary is also a library other programs import. The README's *From
Python* builds a scene with `from apothecary import Cube, Scene, ...`;
`examples/scene_snowplow.py` renders a part the same way; the datum
project depends on a released, pinned apothecary (`apothecary/release.py`);
a notebook or a build script that uses the shapes is the same kind of
program. What `import apothecary` loads -- the shapes, the transforms, the
scene and its templates, the models -- reads no photograph, no port and
nothing under the state folder, and neither do the parts under
`apothecary.projects` or the meshes. What does read them sits in these
packages and one module: `apothecary.vision` and
`apothecary.gathering` open photographs; `apothecary.firmware` holds the
state folder and the serial link with its comms log; `apothecary.routes`
keeps camera frames, uploads and camera placements; `apothecary/api.py`
serves the picture root and the state; the command line's package
(`apothecary/cli/`) drives all of them. A guard that went on whenever any
of apothecary was imported would take the network from every program that
uses the shapes, for data none of them holds.

The requirement, stated by the sponsor: personal data stays on the device
**based on the architecture of the system, never the decision of an agent
or a user**, with one named eventual exception, *secured user accounts*.

Constraints: the firmware toolchain must still be installable from the
firmware page (arduino-cli is downloaded from a fixed release host);
arduino-cli, esptool and OpenSCAD are subprocesses the guard cannot see
into; the browser tests and the docs generator run servers on this machine
and must keep working; a program that imports apothecary for its geometry
is that program's process, not apothecary's, and keeps its network;
human-only contributorship.

## Decision

1. **An apothecary process cannot reach past this machine.** A guard
   (`apothecary/stays_local.py`) holds it there: the socket class -- the
   Python one and the C one beneath it -- is replaced by a checked subclass
   that refuses to connect, send a datagram (`sendto` and `sendmsg` alike)
   or bind a listener anywhere but a loopback address or a Unix socket,
   and every other name the originals were bound to (`socket.SocketType`,
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
   the guarded resolver, never by hand.
   The guard is installed by the first statement of each module through
   which apothecary runs or reads personal data, before any of that
   module's own code:
   - the application module, `apothecary/api.py`, which `apothecary
     serve`, `uvicorn apothecary.api:app` and the docs generator's server
     all load;
   - the command line, `apothecary/cli/__init__.py`, which the
     `apothecary` console script and `python -m apothecary` both import,
     and which runs before any module of the command line's package;
   - the `__init__` of each package that reads personal data --
     `apothecary.vision` and `apothecary.gathering` (photographs),
     `apothecary.firmware` (the state folder, the serial link and its
     comms log), `apothecary.routes` (camera frames, uploads, camera
     placements) -- so no module in them can be imported without the
     guard going on, whoever imports it;
   - the test suites' root `conftest.py`, which calls `install_guard()`
     before any test is collected.

   The server, the command line, the docs generator's server and the tests
   are under it from the first statement of the install point each of them
   loads. Python runs `apothecary/__init__.py` before any module inside the
   package, so what `import apothecary` loads -- the geometry library, with
   pydantic and jinja2 beneath it -- runs before the guard in each of them;
   it reads nothing personal and makes no socket, and §7 holds it to that.
   Any other program is under the guard from the moment it imports one of
   those modules, for the rest of its life.
   `import apothecary` and the rest of the geometry library -- the
   shapes, transforms, scene and templates, the models, the parts and
   assemblies under `apothecary.projects`, the meshes -- install nothing
   and read nothing personal, and a program that uses them keeps its
   network. `apothecary.vocabulary` reads nothing personal and is under the
   guard all the same, because it imports `apothecary.vision.models`. A
   module that reads personal data is written inside one of those
   packages, or its own package installs the guard the same way; §7's scan
   holds that line for the readers it names. There is no flag, environment
   variable, configuration file or route that turns the guard off.
2. **One allowance, a tool fetch, and two callers.** The firmware installer
   downloads arduino-cli -- and, for Rust on the ESP32, rustup-init,
   espflash and Espressif's Xtensa Rust, rust-src, LLVM and GCC archives with
   their checksums -- and the OpenSCAD installer a development snapshot of
   OpenSCAD, through `tool_fetch(url)`, which refuses any URL
   whose host is not one of the fixed `TOOL_SOURCES` (the release API, the
   archive, where the archive redirects) before anything is opened, and
   admits the sockets and the name lookups beneath that one call, on that
   one thread, to those hosts alone -- by name, or by an address the
   guarded resolver returned for one of them -- so a redirect elsewhere is
   refused mid-fetch, and the fetch takes no proxy from the environment. A tool
   fetch is a GET of a release archive at a URL built from a version
   string, and a version is three or four numbers, or Espressif's three
   numbers and a date, or it is refused; an asset's name and a checksum are
   held to their shapes too; no personal data is in any of them; an
   OpenSCAD snapshot's version is its date, three numbers too. Where no snapshot is published for the machine (Linux on
   arm64), the OpenSCAD installer builds that date's OpenSCAD from source:
   it asks GitHub's API for the commit at that date and the commits its
   submodules pin, and fetches each commit's source tarball; a commit is
   forty hexadecimal characters or it is refused, and a submodule outside
   github.com is refused, before either goes into a URL. The build itself
   runs with downloads switched off and fetches nothing. A test holds the
   callers of `tool_fetch` to those two installer modules: a third caller
   is a third door, and is reviewed as one.
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
   docs alike. A single `uvicorn` process loads the application module,
   and with it the guard, before it binds, so a listener anywhere but
   loopback is refused at the socket; a `uvicorn` parent run with
   `--workers` or `--reload` binds the listener itself and never imports
   apothecary (each child process loads the application), and on that
   listener this middleware is what refuses a request from past this
   machine.
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
   it.** arduino-cli, esptool, cargo, espflash and OpenSCAD are outside a
   Python guard. Of these only arduino-cli and cargo reach out; espflash's
   own update check is switched off on every run (`--skip-update-check`). Every arduino-cli the seam
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
   the person, carrying nothing of theirs. cargo reaches out at install
   time only: `apothecary firmware install --rust-esp32` runs `cargo vendor
   --locked`, which reads crates.io's sparse index and downloads the crates
   each Rust sketch's `Cargo.lock` names, and nothing else; its environment
   is the build's -- every proxy, registry and source override, compiler
   wrapper and token removed -- and its homes are in the tools dir. Every
   build afterwards is `cargo --offline` with crates.io replaced by the
   vendored folder, and a traced build looked up no name and opened no
   internet socket. The Rust module finds ports with pyserial's port list,
   which opens nothing and sends nothing; with only that module installed
   there is no board scan by arduino-cli and so no multicast question.
6. **What is kept is kept here, and the picture root is a folder of
   pictures.** Personal data lives in three places and nowhere else: the
   state folder (`~/.apothecary`, or `APOTHECARY_STATE_DIR`) -- devices
   with their serial numbers and addresses, camera placements with the
   browser's label for the camera, bed readings with the person's note,
   uploaded G-code; the picture root -- the pictures a person named and,
   under `captures/` and `uploads/`, what the browser put there (a
   camera's frames; the pictures a person added from a file picker, kept
   as they named them); and the page's own `localStorage`, which holds a
   panel layout and never leaves the browser. A page forgets only what
   the browser put there -- one kept picture on request, all of them
   after asking once -- and never a picture a person named: those are
   removed by the person, by hand, and a page that offered to would be
   offering to delete a folder it does not own. What a page placed or
   pinned (a camera at a piece, a board's identity at a node) is listed
   by the same page, every site's, and taken back the same way; a
   picture pinned at a place in the world (a view), with the width a
   person typed for it, is one of these. `uploads/` also takes the
   pictures a person drops or pastes on the page, a pasted one named for
   when it was pasted. Forgetting a kept picture unpins its views; a piece
   made from one of its shapes stays, marked as made from a picture since
   forgotten, and keeps the outline it was made from until the site is
   reset or the piece dropped -- a made piece is a part, and is saved,
   varied and committed as a part is. The
   comms log is served on loopback and saved only when the person clicks
   *Download*, into their own downloads folder. The state folder, a
   camera's `captures/` and the browser's `uploads/` are made readable by
   the account alone, whatever the umask says of the person's other
   files. The test suites -- `test run`, `test all`, `docs generate` --
   run their servers on state and pictures of their own, never the
   person's. The picture
   root is `APOTHECARY_PICTURE_ROOT` or the folder the server was started
   in, and it is never the whole machine, the person's home folder (by
   `HOME` and by the account, which a variable cannot move) or anything
   above it, nor the state folder: a root there would serve everything of
   theirs to whatever asks, and the server refuses to read from one. What
   the picture route serves is a picture, judged by its first bytes; any
   other file under the root is refused.
7. **The rule is held by tests that would fail before a person could
   relax it.** `tests/test_stays_local.py` checks, each import in a fresh
   interpreter, that importing the geometry library (`apothecary`, its
   shapes and scene, the parts under `apothecary.projects`) leaves the
   process's network as it found it and makes no socket and looks up no
   name while it loads (an audit hook sees no `socket.*` event), and that
   importing each install point in §1 -- the application module, the
   command line, and the vision, gathering, firmware and routes packages --
   installs the guard; that a test session is under the guard before its
   first test is collected (the root `conftest.py`); that no module
   outside those packages, the command line's package and the application
   module imports `serial`, calls `state_dir()`, resolves the picture root
   or opens an image, so a module that reads personal data by one of those
   means where no install point covers it fails a test before it merges
   (one that reaches the data another way is named in the risk register);
   that every way of connecting, the TLS socket and the resolver included,
   is refused past loopback; that a tool fetch reaches
   its sources and nothing else, takes no proxy, has the two installers as its callers and
   accepts only a version; that every function in the command
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
   suites' servers are fenced. `tests/test_pictures_api.py` checks that a
   page forgets only what is directly under `captures/` and `uploads/`,
   never the folder's own pictures, never through a link, and not into a
   kept folder that is itself a link elsewhere. A change that loosens any
   of these is a change to those files and to this record.
8. **The named exception: secured user accounts.** A future record may let
   data leave this machine for an account the person holds and has
   authenticated to, with consent given per account, per kind of data, and
   revocable; nothing leaves under a shared, default or anonymous account,
   and nothing leaves that the person did not name. Until such a record is
   Accepted there is no code path for it: `stays_local.py` or one of §1's
   install points is what would have to change, and the tests in §7 are
   what would have to be edited, which is the review. The one path that
   needs neither is a module outside the guarded packages that reaches
   personal data by a means §7's scan does not name, and the risk register
   names it. An agent proposing that code is proposing that record, not a
   feature.

## Service inventory

The open-license record asks every project for a list of the third-party
services in a runtime path, with the ownability test answered for each.
This is that list. Nothing personal is sent to any of them; each is
reached for a tool, and each is one edit to a fixed list away from a
mirror the person owns.

| Service | Reached by | What is sent | Replaceable by |
|---|---|---|---|
| GitHub releases (`api.github.com`, `github.com`, `objects.githubusercontent.com`, `release-assets.githubusercontent.com`) | the firmware installer, on *Install / update arduino-cli* | a GET of a version string's release archive and its checksums | an entry in `TOOL_SOURCES` and `RELEASES_*` |
| `files.openscad.org` | the OpenSCAD installer, on `apothecary openscad install` | a GET of a snapshot archive named by its date | an entry in `TOOL_SOURCES` |
| `api.github.com`, `codeload.github.com` | the OpenSCAD installer, building from source where no snapshot is published (Linux arm64) | the commit at a snapshot's date, the commits its submodules pin, and a GET of each commit's source tarball | entries in `TOOL_SOURCES` |
| GitHub releases, as above | the firmware installer, on `apothecary firmware install --rust-esp32` | a GET of espflash's release and Espressif's Xtensa Rust, rust-src, LLVM and GCC archives at pinned versions, their checksum files, and the digests GitHub publishes for assets whose release has none | entries in `TOOL_SOURCES` and the installer's pins |
| `static.rust-lang.org` | the firmware installer, on `apothecary firmware install --rust-esp32` | a GET of rustup-init at a pinned version and the `.sha256` beside it | an entry in `TOOL_SOURCES` |
| `index.crates.io`, `static.crates.io` | `cargo vendor`, on `apothecary firmware install --rust-esp32` | the index entries and crate archives each Rust sketch's `Cargo.lock` names | a source replacement to a mirror the person owns, in the tools dir's cargo config |
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
| `ARDUINO_CLI` and `ESPTOOL` (or `PATH`) name the arduino-cli and esptool the seam runs | naming a program to run is installing one; the tests use `ARDUINO_CLI` to stand in a scripted arduino-cli and set `ESPTOOL=none` so their servers never find the esptool a person's own Arduino install bundles; whatever is named runs under the managed config and the scrubbed environment | a binary at that path that is not the tool it is named for; a checksum of the managed binaries would close it and is not built |
| Another user on the same machine | the state folder and the captures are files under the person's home, with the person's own permissions; loopback is shared by every account | a file mode wider than the person's; the OS's boundary, not this program's |
| A module outside the guarded packages reads personal data | the guard goes on by package, a module can be written anywhere in the tree, and §7's scan looks for known readers (`serial`, `state_dir()`, the picture root, an image library); a module that reaches the data another way passes it | the scan failing; a `strace -e trace=openat` of a program that imports only the geometry library opening a file under the state folder, a picture or a serial device |
| A socket, a pooled connection or a name lookup made before an install point -- by a program that imports apothecary, or by the geometry library and the libraries it imports, which `import apothecary` runs before every install point | the guard replaces classes, not the sockets that exist: a socket made before the install binds `0.0.0.0` after it (measured), so a program that connects first and imports a personal-data package after keeps that connection; and Python runs a package's `__init__` before any module inside it | a connection held open across the import of a guarded package; a `socket.*` audit event while `import apothecary` loads (§7), or a socket call under `strace -f -e trace=network` of `python -c 'import apothecary'` |
| A `uvicorn` parent run with `--workers` or `--reload` binds a listener wherever it is told | uvicorn binds in the parent and loads the application in each child process; the parent never imports apothecary, so the guard is not in it, and `LocalOnly` refuses what arrives from past this machine | a listener on a non-loopback address held by a uvicorn parent (`ss -ltnp`) |

## Consequences

- A person or an agent cannot make personal data leave this machine by
  setting anything; they can only edit the guard, which is one file with a
  test on every door, take away an install point, which a test in §7
  names, or write a module outside the guarded packages that reaches the
  data, which §7's scan looks for by the readers it names; each is an
  edit reviewed against this record.
- A program that uses the geometry library -- a notebook, a build script,
  a downstream project's build, `examples/scene_snowplow.py` -- keeps its
  network: it fetches, uploads and resolves names as it would without
  apothecary. The rule governs apothecary's processes and the data they
  hold, not a process that imported apothecary for its shapes.
- A program that imports the server, the command line or a package that
  reads personal data accepts the guard from that import to its end: from
  then on a socket it makes, a connection it opens and a name it looks up
  past this machine are refused with the rule's message, whatever it goes
  on to do, apart from §2's tool fetch. A socket it made before that
  import (the risk register) and a process it starts (the constraints)
  are outside the guard. A program that needs a personal-data package and
  the network in one process is asking for §8's record.
- `apothecary.vocabulary` comes under the guard with `apothecary.vision`,
  which it imports; a program that wants the vocabulary alone accepts the
  guard too.
- Cost accepted: an install point per package that reads personal data,
  not one for the whole library, each a line a reviewer keeps at the top
  of its module; a module that reads personal data is written inside one
  of those packages or brings its own.
- Cost accepted: in every apothecary process the geometry library and the
  libraries it imports load before the guard. A socket one of them made at
  import would be outside it; §7's audit of `import apothecary` is what
  would show it.
- A feature that needs an outside service is not built until it can be
  built here, or until §8's record exists -- the proposed rule's own
  consequence, with a mechanism behind it.
- FastAPI's Swagger and ReDoc pages are not served; `/openapi.json` is. A
  person who wants a rendered API page renders it from that file with a
  tool on their machine.
- The firmware page's *Install / update arduino-cli* still works: it is
  a tool fetch, in the server process, on its own thread, to the
  fixed hosts. Core and library installs are arduino-cli's own fetches
  from the hosts in its managed config. A person's own
  `~/.arduino15/arduino-cli.yaml` -- an extra index, a proxy -- has no
  effect under apothecary; that is the point, and the firmware page says
  which file is in use.
- A board scan does not ask Arduino's cloud what a USB device is; an
  unrecognised device is shown by its port and its USB ids, without a
  name from elsewhere.
- A page that legitimately needed another origin -- a map tile, a font, a
  library -- would have to be vendored, as three.js was; the policy will
  not let it load otherwise. That is the cost, and it is accepted.
- The server refuses a picture root at or above the person's home folder
  with a message that says where to start it instead.
- A page on the person's own machine that reaches the server by a name
  that is not loopback (a hosts-file alias, `app.localhost`) gets 403;
  `localhost`, `127.0.0.1` and `[::1]` are the names.
- `python -m uvicorn apothecary.api:app --host 0.0.0.0`, as one process,
  does not bind at all: the application module installs the guard before
  the listener is made, the listener is refused at the socket, and the
  process stops with the rule's message in what it prints. With
  `--workers` or `--reload` the parent, which never imports apothecary,
  binds where it is told; a request from this machine is answered on that
  listener, and `LocalOnly` answers each request that arrives from past
  this machine with 403.
- A job is named with letters, digits, spaces and `.+-/_`; a name that was
  markup is refused with 422.
- A link on a page elsewhere still opens the viewer; a script on a page
  elsewhere gets nothing from it and can start nothing in it.

## Alternatives considered

1. **A test-time guard only** (a check that runs only under pytest) --
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
   installed cores provide; the Rust module scans with pyserial, the
   Arduino module still with arduino-cli, and moving the Arduino module's
   scan is named as the trigger below.
8. **The guard installed by importing the `apothecary` package** -- one
   install point and the simplest rule a reader could want: any process
   that loads any apothecary code is under it. It lost because it takes
   the network from every program that uses the geometry library for what
   the library is for. Measured with the guard installed this way:
   `from apothecary import Cube` followed by
   `socket.getaddrinfo('pypi.org', 443)` raises `LeftTheMachine`, and
   `examples/scene_snowplow.py` renders its scene and then cannot resolve
   a name. What that import loads holds nothing this record names as
   personal and makes no socket, so the guard protects no data by going on
   there; it decides the network of a process that is not apothecary's.
   What it has that the install points here lack: in the server and the
   command line the guard goes on before the geometry library and the
   libraries it imports (pydantic, jinja2) load, where here it goes on
   after them (measured by listing the loaded modules when the guard first
   goes on), so a socket one of them made at import would be refused under
   it and is outside the guard here. Its promise of a guard before any code
   runs is still narrower than it reads: a socket made before the import
   binds `0.0.0.0` after it.
9. **The application module and the command line alone** -- the fewest
   install points, and every process this record names is still under
   the guard. It lost because a program that imports
   `apothecary.firmware.devices`, `apothecary.firmware.gcode`,
   `apothecary.vision`, `apothecary.gathering` or
   `apothecary.routes.pictures` directly would read serial numbers, the
   state folder or photographs with the network open (measured with the
   install in those two modules alone: none of those imports installs the
   guard). The rule would hold for apothecary's processes and not for its
   data, and the data is what the requirement names.
10. **The guard installed when `apothecary.stays_local` is imported** --
    the install would follow the guard's own module, which the server, the
    command line and the firmware modules import already. It lost because
    the guard's own module is not where the data is read:
    `apothecary.vision` and `apothecary.gathering` do not import it, so
    photographs would be read unguarded; and what imports it without
    reading personal data -- a caller of `is_loopback` or
    `require_loopback`, the tests that look at the guard -- would be put
    under the guard for that alone.
11. **The geometry library as its own distribution, with the application
    package installing the guard on import** -- the cleanest boundary:
    importing the application is choosing the rule, and the library cannot
    be guarded by mistake. It lost for now because it is packaging work
    nobody has planned -- the wheel ships `apothecary/` alone and cannot
    render a part (`todo.md`) -- and it splits the package the datum
    project pins. It is a revision trigger below.

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
- The Arduino module's board scan is made with pyserial too -- the
  multicast question in §5 and the risk register go, and the service
  inventory loses its last row.
- A Rust sketch's crates are bumped, or another Rust module is added --
  `cargo vendor` reaches crates.io again at install time only, and a traced
  build still looks up no name.
- A person needs the viewer on another device on their own network (a
  tablet at the printer) -- that is §8's record, or a local tunnel the
  person sets up outside the program, never a `--host`.
- Photo gathering ships as the `photos` extra, `api.py` is split into
  routers, or the geometry library ships as its own distribution -- the
  install points go with their modules and §1's list is edited to match;
  whether `apothecary.vocabulary` stays under the guard is settled with
  vision's share of the extra.
- §7's scan finds personal data read outside the guarded packages -- the
  module goes into one of them, or its package installs the guard, with a
  line here.
- The geometry library starts to load a guarded package, or to make a
  socket or look up a name while it loads (a fresh-interpreter check on
  `import apothecary` fails) -- the import or the call is cut, or the
  library's reach is decided here.
- A program needs a personal-data package in a process that also uses the
  network (a build that reads a photograph and uploads its result) --
  that is §8's record, not another install point.

## Amendments

*None.*
