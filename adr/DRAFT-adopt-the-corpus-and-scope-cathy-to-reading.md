# ADR-XXXX — Adopt the QM constitution, and scope cathy to reading the public internet

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-24 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `ownership-is-the-deliverable` — ownership is the deliverable; `credit-tracks-accountability` — credit tracks accountability, not output |
| **Restated in** | cathy's `AGENTS.md`, below its marked line; cathy's `README.md`, its opening paragraph and its licence paragraph; cathy's `REUSE.toml`, its default block |

## Context

cathy is a digital assistant whose subject is the public internet: what a
person has put on a platform, and getting it back into files that person owns.
It is a new repository, adopted at its first commit, so it has no history
before adoption and no conflict table of the kind a project that predates
adoption owes.

Its first use is a site migration. `mrharpo/harpo.me` moved a personal site off
Squarespace with two one-off scripts, `scripts/convert.py` and
`scripts/download_images.py`. The first reads the WordPress-format export the
platform writes, keeps the posts and pages that are real content, converts
their HTML to Markdown with front matter, and lists the images they show on the
platform's CDN. The second downloads that list. A site's own choices — which
posts, which slugs, which tags — are tables in the code. cathy takes that
shape and keeps it: an owner's export goes in, files the owner keeps come out,
and the network is touched only to fetch what those files show. The tables
move into a `cathy.toml` per site.

Three facts about an export bear on scope.

- **It holds more than its pages.** The export committed beside those scripts
  carries the platform's author block, an email address among it, and draft
  posts. Whatever leaves the export for a page is published by whoever
  publishes the page.
- **It is the owner's own statement of the site.** It carries dates, slugs and
  drafts as the platform held them, which a crawler of the public pages cannot
  see, and reading it needs no account.
- **Reading and acting are different in kind.** A GET to a public host asserts
  nothing about anyone. Posting, publishing, replying and signing in speak for
  a person, in public, under their name, and are seen before they can be taken
  back. `DRAFT-acts-that-are-a-persons-by-constitution.md` is the org record
  for acts whose meaning changes when a machine performs them.

The outbound-licensing record classes a repository by its shape, and names no
class for a command a person runs on their own machine. cathy is that command
at adoption and an assistant that runs as a service where it is headed. Its
licence follows the second: a service is delivered by network use, and every
contribution arrives under the licence the project already carries.

## Decision

### §1 — cathy adopts the QM constitution by reference

Org records bind it. Its own records may tighten them, never relax them. The
pin is this branch's ancestry, per `adr/README.md`.

### §2 — cathy reads from the public internet and never acts on it

cathy reads exports its owner downloads, and fetches the public assets those
exports reference. It does not post, publish, reply, upload, sign in, or hold
a credential for any service.

An outbound act enters cathy only through a record of its own, which names the
act, the account it speaks for, and the person's act before each one. Until
that record is Accepted, a change that adds an outbound act is outside this
project's scope, however small.

### §3 — An export stays with its owner

- cathy reads only the fields a page is made from. An export's author block,
  comments and attachment metadata are not parsed.
- A draft is written only when the site's `cathy.toml` asks for drafts. A
  private post is never written.
- An export and what cathy makes from it live with the site. cathy's own
  repository holds one export, a made-up fixture, and its ignore rules keep
  any other out.

### §4 — The first source is the WordPress-format export

`cathy convert` reads it into Markdown pages and an image manifest, and
`cathy fetch` downloads what the manifest lists. Each further source — another
platform's export, a social network's data download — is a module beside it,
read the same way, and is checked against §3 for what that export holds before
it lands.

### §5 — cathy is a QM service for outbound licensing

cathy is licensed **AGPL-3.0-or-later** under the outbound-licensing record's
§4, with copyright in Quaternion Media under its §0. The seed's governance
prose carries CC0-1.0 under §2, and the workflows under `.github/` and the
editor configuration Apache-2.0 under §3. `REUSE.toml` declares each, `LICENSES/`
holds each text, and `reuse-lint.yml` runs blocking from adoption, since the
repository is compliant at its first commit.

## Consequences

**Accepted costs.**

- §2 rules out the shortest path to the uses an assistant is most often asked
  for: cross-posting, scheduling, replying. Each waits for its record.
- §3 means a site that wants its drafts published says so in its own
  configuration, rather than cathy guessing that a draft is finished.
- §5 puts cathy out of scope for a client operating a blanket AGPL
  prohibition, the cost the outbound-licensing record accepts for every QM
  service. A host that serves a modified cathy over a network offers its users
  that modified source.

**Obligations created, and their state at adoption.** Naming a gap is not
waiving it.

| Obligation | Record | State at adoption | Done when |
|---|---|---|---|
| Licence gate for the Python ecosystem | open-license §4 | Not wired. The runtime closure is `markdownify`, `beautifulsoup4`, `soupsieve` and `six`, declaring MIT, and `typing_extensions`, declaring `PSF-2.0`, which needs a normalization entry made after its licence file is read | A gate generates the report from the locked runtime closure, fails outside the generated allowlist, and runs on every pull request |
| Baseline component audit | open-license | The closure above, read from installed package metadata on 2026-10-24 | The gate's report stands in its place |
| Service inventory | open-license §6 | cathy reaches the hosts a site's `cathy.toml` names, by GET over HTTPS, and holds no account with any. For the first source that is the platform's image CDN, and cathy's purpose is to move content off it | A section of its own, once a second source names a second class of host |
| Quarterly upstream scan | open-license §4 | None | A scheduled job watches the pinned upstreams |
| Control-plane record | build-the-seam | cathy has none: it is a command run against local files | This row stands until cathy runs as a process, when that record is written |
| Risk register | open-license, seams | Not written | A section naming governance and abandonment risk for each runtime component |
| Tag claims | version-tags-are-claims | No tag cut | The first tag runs the gate and names what it did not cover |

## Alternatives considered

1. **Keep the scripts in each site's repository.** Nothing to adopt and
   nothing to configure. It loses because each copy re-derives selection,
   embeds and downloads, and each carries the same defects: collision names
   taken from a per-process salted hash, so a second run renames files, and a
   download written in place, so an interrupted one is skipped on the next run
   as present.
2. **Read and act from the start.** One assistant for the whole round trip,
   export to cross-post. It loses because an act needs a credential store, an
   account model and a person's act before each one, none of which reading
   needs, and the first use calls for none of it. Deciding them later, in their
   own record, costs nothing that is built now.
3. **Crawl a site's public pages rather than read its export.** Works for a
   site whose owner has no export. It loses as the first source because the
   export carries what the pages do not, needs no account, and makes cathy a
   reader of a file rather than a client of a platform's pages and their
   terms. A crawler stays available as a later source under §4.
4. **Apache-2.0, as a command rather than a service.** Permissive, with a
   patent grant, and what cathy's shape at adoption suggests. It loses
   because the assistant cathy is headed for is delivered over a network, where
   Apache-2.0 lets a hosted copy keep its changes, and relicensing to the
   service class once outside contributions arrive needs every contributor's
   grant to cover it.

## Revision triggers

- A request for cathy to post, publish, reply or sign in: the outbound record
  is drafted before any code.
- A second source format: §3 is read again against what that export holds.
- cathy run as a long-lived process, or reached over a network: the
  control-plane row is written.
- A request to embed cathy's modules in another program as a library: §5 is
  read again against the outbound-licensing record's §6.

## Amendments

*None.*
