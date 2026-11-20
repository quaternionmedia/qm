# QM-XXXX — Work Is Delivered into a Repository, Never to a Hosted Page

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-24 |
| **Namespace** | org |
| **Binds** | This corpus, and any project that adopts it |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `ownership-is-the-deliverable` — a page held on somebody else's host is a rental; `decisions-are-documented` — what lives only outside the repositories is not the organisation's; `show-it-by-running-it` — a second copy of the work drifts from the first |
| **Restated in** | `AGENTS.md` item 19; `project-seed/ide/AGENTS.md` item 15 |

## Context

A session produces things for a reader besides the change itself: a report on
what it found, a demo of a feature, a preview of a page, a handoff for the
next session. Several assistant products offer to publish such a thing to a
page their host keeps: a chat product's shareable artifact, a canvas, a share
page. The offer is convenient. The page renders at once, it opens on a phone,
and one link carries it.

The page sits outside every repository the organisation holds. It is not
versioned with the code it describes, so it says nothing about which commit it
is true of. It cannot be reviewed as a diff, so no gate runs on it and no
reviewer sees what changed between two versions of it. When the code moves the
page does not, and nothing notices: it goes stale unseen. It lives on an
account, under the host's terms, and can be removed, made public or made
private by somebody other than its author. And a reader who reaches the
repository first does not find it.

`records/DRAFT-what-is-not-the-organisation.md` governs what a committed file
says. A page published to a host commits nothing, so that record never sees
it; the link a later file carries to it is the only trace.

## Decision

1. **Work is delivered into a repository.** A report, a demo, a preview or a
   handoff is a committed file: a docs page, a screenshot, a generated
   document, a page under `handbook/handoffs/`. It reaches its reviewer as a
   pull request, or as a page the reviewer builds and serves locally from the
   repository by a command the repository documents.

2. **Nothing is published to a page an assistant's host keeps outside the
   organisation's repositories**, such as a chat product's shareable artifact
   or canvas. Not as the deliverable, and not as a convenience copy beside the
   committed one.

3. **A link to such a page is not committed.** A file that carries one points
   its reader at the copy this record rules out.

### What this does not forbid

- **A site the organisation publishes from a repository by its own workflow**,
  such as this corpus's documentation site, deployed from `main` by
  `.github/workflows/docs.yml`. It is built from committed files and changes
  only when they do.
- **A build a workflow attaches to a pull request**, such as the documentation
  draft `.github/workflows/docs-draft.yml` uploads. It is built from the pull
  request's own commit.
- **A recording too large to commit**, when the repository documents the
  command that makes it and the reviewer runs that command. The command is
  committed; the recording is regenerated, not hosted.
- **A conversation**, which is not a deliverable at all and is governed by
  `records/DRAFT-what-is-not-the-organisation.md`.

## Enforcement, and its edge

`project-seed/ci/check_leaks.py` refuses a tracked file that carries a link to
a hosted page, as its `hosted-page` kind, and reports it redacted. The seed
ships it as `leak-check.yml`, and this corpus runs its own copy on every pull
request into `main`. `ci/policy-registry.yaml` lists the invariant with that
detector.

The check sees a link in a committed file and nothing else. It cannot see a
page published and never linked, a link in a pull request body or a message,
or a page on a host its pattern does not list. For those the reader is the
check.

## Consequences

- A reviewer reads the work where the code is, at the commit it is true of,
  and a demo costs a docs page and its committed pictures rather than a link.
- A page that needs another repository's unmerged change to show what it shows
  is previewed by a local build pointed at that change, never by a hosted copy
  of it. The preview command is documented beside the page's generator.
- A heavy recording costs a command a reviewer runs. That is slower than
  opening a link, and the cost is accepted: the command stays true as the code
  moves, and a hosted recording does not.
- A session whose tooling publishes to a hosted page by default turns that off
  for work here. An adapter under `adapters/` may name the mechanism; it adds
  no rule of its own.

## Alternatives considered

1. **Allow a hosted page as a convenience copy beside the committed file.**
   Rejected: the copy is the one a link carries, so it is the one read, and it
   drifts from the committed file the moment either changes. A second copy of a
   behaviour is the failure `show-it-by-running-it` exists to prevent.
2. **Name the products this rules out.** Rejected: the governance text names no
   vendor (`adapters/README.md`, `records/DRAFT-seams-on-standard-protocols.md`),
   and a list of products goes stale as products appear. The check's pattern
   names hosts, because a pattern must; the record names the property.
3. **Leave it to the record on what is not the organisation.** Rejected: that
   record governs what a committed file says, and a hosted page commits nothing.
   The class this record names passes it.
4. **Say nothing, and rely on review.** Rejected: a hosted page is never in a
   pull request, so there is no review for it to fail.

## Revision triggers

- A host offers pages that are built from a repository's commits and reviewed
  as its diffs. Such a page is the repository's, and the line in §2 moves.
- The `hosted-page` pattern fires on a legitimate use, or a host it does not
  list is used in practice; the pattern is reconsidered.
- Work arises that a reviewer cannot build locally (it needs hardware or a
  service the reviewer lacks). The record then says how that work is shown.

## Amendments

*None.*
