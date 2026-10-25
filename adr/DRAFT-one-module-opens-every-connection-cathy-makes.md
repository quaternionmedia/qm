# ADR-XXXX — One module opens every connection cathy makes, and each is a GET

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-24 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `a-check-is-evidence-after-it-fails` — a check is evidence only after it has been seen to fail; `shrink-the-black-box` — shrink the black box |
| **Restated in** | cathy's `walkthrough/02-cathy-reads-and-never-posts.md` |

## Context

The adoption and scope record's §2 says cathy reads from the public internet
and never acts on it. A rule kept only in prose is kept by whoever reads it,
and the change that breaks it is ordinary: a new source wants one more request,
a helper library is added for convenience, a download grows a header.

The scripts cathy generalises show what an unbounded download does.
`urlretrieve` is called with no timeout, so a stalled connection holds the run
indefinitely; it writes to the final path as it reads, so an interrupted
transfer leaves a partial file that the next run skips as present; and the
script exits zero whatever failed.

Python's standard library makes a GET in a few lines, and every network
library a contributor might reach for can do far more than that.

## Decision

1. **`cathy/net.py` is the only module that opens a network connection.**
   No other module in the package imports a network library, reaches one
   through `cathy.net`, or loads one by name.
2. **Every request is a GET with no body**, carrying a cathy `User-Agent`, no
   cookies and no `Authorization` header, under a timeout and a size limit.
3. **A request goes only to a host the site names.** The host is one of the
   site's `cathy.toml` `[images] hosts`, the scheme is HTTPS, and a URL
   carrying credentials is refused. A redirect is checked by the same rule
   before it is followed.
4. **Conversion opens no connection.** `cathy convert` reads one local file
   and writes local files; `cathy fetch` is the one command that uses the
   network.
5. **A download is complete or absent.** It is written beside its target and
   renamed into place once the length the server announced has arrived. A
   failure removes the partial file, and `cathy fetch` exits non-zero when any
   row fails.
6. **The guard is a test.** `tests/test_network_boundary.py` reads the
   package's source and refuses §1 and §2 being broken. The mutations it was
   seen to fail on are listed beside it, and so is what it cannot see: a
   dependency opening a connection of its own, an attribute reached by a name
   built at runtime, and code outside `cathy/`.

## Consequences

- A new source that needs the network adds hosts to a site's configuration,
  not a client of its own.
- A CDN that redirects to a host the site did not name fails that row until
  the host is named. The failure is reported, and nothing is written.
- `markdownify` and `beautifulsoup4` open no connection by design, and the
  guard cannot see inside them. A test runs conversion with sockets refused,
  which covers the paths the fixture exercises and no others.
- A source that needs an account, an API key or a token cannot be added under
  this record: §2 refuses the header it would carry.

## Alternatives considered

1. **A network library such as `requests` or `httpx`.** Connection pooling,
   retries and a friendlier interface. It loses because cathy makes one kind of
   request, the standard library makes it, and each library adds a licence to
   the runtime closure and a surface the guard has to read past.
2. **Refusing sockets at run time, outside the tests.** It would cover
   dependencies as well as cathy's own code. It loses because `cathy fetch`
   needs sockets, so the refusal would need an exception for exactly the module
   it is meant to watch, and a guard that patches the program it guards
   describes a different program from the one that ships.
3. **Review alone.** No test to maintain. It loses because the change that
   breaks the rule looks like ordinary work, and review reads what a change
   means to do rather than every import it adds.

## Revision triggers

- An outbound record is Accepted: §2 is reopened for the requests that record
  names, and only those.
- A source needs authentication to read: this record is amended before the
  code lands.
- A dependency is found opening a connection: the guard's limits are read
  again, and the dependency is replaced or wrapped.

## Amendments

*None.*
