# Perspective — Twenty False Assumptions in One Session

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (Anthropic), the assistant whose errors this document counts |
| **Task** | An audit of every false assumption made during alfred's governance adoption and test-building session, how each was caught, and which the corpus could have prevented. Companion to `2026-08-07-alfred-brownfield-adoption.md`, which covers what the adoption found; this one covers what the assistant got wrong while finding it. §1.1 records what happened when the standard proposed in §4 was then applied to the session's own output. |

## 0. Standing and method

One session, one assistant, one project. The evidence is the session's own
transcript and the commits it produced, so every row in §1 is checkable
against the branches it names.

This is a self-audit, which is the weakest possible form of error reporting: I
am the only witness to my own mistakes, and the ones I never noticed are by
definition absent. The count below is therefore a floor, not a total. A reader
who wants to find what is missing should look for claims in the resulting
records that cite no reproduction — §2's proposal exists precisely because
that is currently hard to do.

Evidence classes: **E1** directly observed in this session, **E4** inference
from a single data point.

## 1. The count

Seventeen during the work itself, and three more found afterwards by auditing
the work against the standard this document proposes (§1.1). Twenty in total.

Of the first seventeen: all were caught, and **none were caught by review** —
not by the maintainer, not by the ADR lint, not by re-reading. Fifteen were
caught by executing something, two by cross-checking a second source.

| # | What I assumed | What was true | Caught by | Cost if it had shipped |
|---|---|---|---|---|
| 1 | The checked-out branch was current | `pdm` was 21 commits behind `main` with nothing unique | Checking branch topology before creating a branch | A whole review pass reported against stale code |
| 2 | The `python` base image has no ImageMagick | It ships ImageMagick 7 | `docker run` | Fed error 3 |
| 3 | The `rm /etc/ImageMagick-6/...` line is what breaks the build | It does break, but `bezier` fails first and masks it | `docker build` | A confidently wrong root cause |
| 4 | alfred's `.gitignore` posed no risk to the seed's files | A tree-wide `*.json` rule swallowed both `.vscode` files | `git status` omission, then `git check-ignore` | Governance wiring committed silently broken |
| 5 | `cp -a` preserves symlinks (the seed says to use it) | It dereferenced one pointer and failed outright on the other | `ls -la` after copying | A duplicated `CLAUDE.md` — the exact thing the record forbids |
| 6 | `license-checker --csv` puts the license in field 3 | Field 2 | Running it | A license report emitting repository URLs as licenses |
| 7 | `git fetch --depth=0` is valid | `fatal: depth 0 is not a positive number` | Running it | Every pull request failing at the lint step |
| 8 | `playwright test` respects per-project grep as a default filter | It runs every project | `--list` | A timing-sensitive perf test gating every PR |
| 9 | `#login-link` identifies one element | Five ids are emitted twice each | Strict mode, then a DOM probe | 15 test failures |
| 10 | `test_cy.yml`'s api mount was worth copying | It mounts `./alfred/` onto `/app`, shadowing the package root | Comparing against `docker-compose.yml` | A broken compose file shipped as the new standard |
| 11 | Compose resolves relative volumes against the working directory | It resolves against the compose file's directory | The container failing to import `alfred` | A debugging detour |
| 12 | A 500 on login was an application defect | My own verification compose omitted `ALFRED_SECRET_KEY` | Reading the config | A false defect report against the project |
| 13 | An unknown clip type reuses the previous clip *object* | It re-processes a stale binding; the duplicate is a derivative, not the same object | `is` comparison, then frame comparison | A defect description wrong in its mechanism |
| 14 | The fades I measured came from the render engine | `makeColor` hardcodes them before the engine reads `fadeIn` | Measuring with fades on and off | **A test that passed for the wrong reason** |
| 15 | Filename construction was unit-testable | It is a closure, and the surrounding document needs a database | Attempting it | A planned instruction set that could not be executed |
| 16 | I had regressed the lockfile's dev group | Pre-existing; the old lock never had it | `git show HEAD:pdm.lock` | A false self-reported regression |
| 17 | `alertifyjs` declares no license | GPL-3.0, in npm's deprecated `licenses` array | `npm view --json` | A copyleft dependency missed in a compliance report |

## 1.1 What happened when the standard was applied to this session's output

§0 said the count was a floor, and that a reader wanting the residue should
look for claims citing no reproduction. That audit was then run against the
session's own deliverables. **Five load-bearing claims were checked. Two were
wrong, one was imprecise, and two were right but had never been verified.**

| # | Claim as written | What checking it showed |
|---|---|---|
| 18 | The frontend loads sample media from `storage.googleapis.com` | Wrong for the shipped artifact. That string is in `website/src/logic.js`, which nothing imports, so it never reaches the bundle. Two external loads survive the build, not three. |
| 19 | `GET /videos/{video}` is path-traversable by any authenticated user | **Does not reproduce.** Starlette decodes the path before routing and `{video}` matches `[^/]+`, so any encoding introducing a separator stops matching the route. Single- and double-encoded separators, UTF-8 overlong sequences, backslashes and a null byte were all tried against a running instance; none reached outside `/app/videos`. |
| 20 | Seeding is skipped because `count_documents` returns a coroutine | Imprecise: it returns a `Future`. The conclusion holds — always truthy, so the block never runs — but the mechanism named in a defect table was wrong. |
| 21 | No pull request was ever opened upstream for the carried patch | True, but asserted from a search narrower than the claim. Re-checked across all of upstream's pull requests; it holds. The same search surfaced an open third-party PR upstreaming the same capability, which the original entry had not thought to look for and which changes the remediation options. |
| 22 | MongoDB is SSPL | True. The headline compliance finding of the entire adoption, asserted repeatedly across several documents, and nobody opened the image until this audit. `mongo:bionic` is 4.4.6 and its own copyright file reads `License: SSPL`. |

Error 19 is the one that matters. A security finding was reported to the
maintainer with a recommendation to prioritise it ahead of other work, and it
does not exist as described. The underlying code is still unsafe by
construction — nothing checks containment — but the protection is real and
comes from the framework's routing rather than from the application. The
difference between "exploitable today" and "becomes exploitable the moment
someone declares the route `{video:path}`" is the difference between an
incident and a code comment.

### The error class the original four habits missed

18 and 19 share a shape §2's habits do not name: **both asserted a property of
the running system from reading the source.**

A build step sits between source and bundle, and it dropped a file nothing
imported. A routing layer sits between a URL and a handler, and it rejected
every input that would have made the handler dangerous. In both cases the
source read exactly as claimed and the artifact behaved differently.

This is not the same as "run the tool before describing its output"
(§2.2), which concerns a tool's own behavior. It is narrower and easier to
miss: *the thing you read is not the thing that runs.* A grep over `src/` is
evidence about `src/`. Claims about what a deployed system does are settled
against the deployed system.

It is now the fourth bullet in the seed's verification obligations.

## 2. What the corpus could have prevented

Four habits would have caught fifteen of the seventeen (E1). None of them are
insights; all are cheap and mechanical.

**2.1 Verify the artifact, not the instruction (4, 5, 10).** Three errors came
from following a documented step and trusting that it worked. The seed *says*
to use `cp -a`; on this machine `cp -a` silently produced the wrong artifact.
The fork procedure *checked* for a `.vscode/` ignore rule by name, which
missed a tree-wide `*.json` rule doing the same damage by different means.

The pattern is that each step's instruction was verified and its **effect** was
not. Every one of these is closed by a one-line check — `git ls-files -s`
showing mode `120000`, `git check-ignore` against the real paths — and those
checks did not exist because the steps were written by someone for whom the
instruction had worked.

**2.2 Run the tool before describing its output (6, 7, 8, 11, 17).** Five
errors were confident statements about how a tool behaves, made from memory.
All five were wrong. All five took under a minute to disprove by running the
thing. Two of them (7, 8) would have shipped into CI and failed every run.

**2.3 Establish which commit you are talking about (1).** The single most
expensive error. A review is a claim about a specific tree, and I made one
about a tree nobody was using.

**2.4 Suspect your own harness first (12, 16).** Twice I nearly reported a
defect that was mine. Both times a cross-check took seconds. The asymmetry
matters: a false defect report against a project costs someone else's
investigation, and it is the failure mode an assistant is most prone to,
because its own setup is the part it understands least.

### The two that a checklist would not have caught

**13 and 14 are a different class**, and they are the more important ones.

Error 13 was a mechanism described plausibly and wrongly. The observable
outcome — a duplicate layer — was real; the explanation was invented. It
survived because the conclusion was correct.

Error 14 is worse: **a test that passed for the wrong reason.** I asserted that
the render engine applies default fades. The test passed. The engine was not
the source; the template hardcodes fades before the engine looks. Had I not
measured with fades explicitly disabled, that test would have entered the
suite as coverage of behavior it does not touch, and it would have kept
passing after that behavior broke.

No checklist prevents this. What does is measuring the mechanism rather than
the outcome: run the negative case, and make sure the test can fail. That is
the same instinct behind `xfail(strict=True)` — a marker that fails when the
thing it describes stops being true.

This is the strongest single finding here (E4, one instance): **a green test
is not evidence until you have seen it go red.**

## 3. What this says about the corpus's existing mechanisms

Uncomfortable, and worth stating plainly: the corpus's enforcement caught
none of these.

The ADR lint checks vocabulary in drafts. The handoff contract requires a
plan and a contradiction check against existing records. Human review before
push is credited by the qmetronome retrospective with catching two semantic
errors that automation missed. All of that is real and none of it engages
with the question *is this claim about the system true?*

That is not a gap in any one record. It is that the corpus governs how
decisions are **written** and says nothing about how the facts underneath
them are **established**. A record can be perfectly disciplined — squashed,
numberless, honest about alternatives, carrying revision triggers — and rest
on a root cause its author never reproduced. Three of the errors above (3, 13,
15) went into drafted records before being corrected.

## 4. Proposals

Drafted on `evolve/from-alfred` alongside this document. As always, a
perspective ratifies nothing.

1. **An evidence standard for factual claims in records.** A record asserting
   that a system behaves some way names how that was established. Not a
   citation ritual: the reproduction is what lets a future reader re-run it
   when the context has changed. Alfred's conflict table rows 5 and 7 were
   rewritten this way and are much stronger for it.
2. **Conflict-table rows say how they are pinned.** Where a defect can be
   captured by a test, the record says which test. A defect described only in
   prose drifts from the code; one pinned by a strict xfail cannot, because
   fixing it turns the suite red.
3. **Every seed step carries its verification command.** The fork procedure
   tells you what to do; it should tell you how to confirm it happened.
   Three errors here were "did the documented thing, got the wrong artifact."
4. **Records name the commit they were written against.** Error 1 in one
   line.
5. **The session handoff contract gains a verification obligation** — claims
   of fact are established by execution, and what was run is reported. This is
   the natural home, because it already binds humans and assistants alike and
   is handed to every drafting session.

## 5. Closing honesty

Three limits.

This counts only errors I found. §1.1 is the evidence that the count was a
floor rather than a total: auditing five claims turned up three more defects,
one of them a security finding that does not exist. Five claims is not an
exhaustive audit, so twenty remains a floor too, and the residue still sits
inside documents I wrote confidently.

The proposals are not free. An evidence standard adds friction to every
record, and most of that friction will be spent on claims that were never in
doubt. I think it is worth it because the expensive errors here were not the
obviously uncertain claims — those got checked — but the ones that felt
settled. That is exactly the reasoning the corpus applies to unwritten
decisions, turned on unverified facts.

And this is a sample of one session, on one project, by one model, reviewed by
its own author. Whether twenty is a lot depends entirely on a baseline nobody
has. What is not sample-dependent is the shape: **every one was caught by
running something, and none by reading.** If that holds up across a second
session, it is an argument for weighting the corpus's enforcement toward
execution rather than toward more careful prose — and for reading the
qmetronome retrospective's finding about human review as complementary to
that, not a substitute for it.

One thing did surprise me. I expected applying the evidence standard to be
bookkeeping — attaching commands to claims already known to be true. It was
not. It overturned the most severe finding of the session on the first pass,
and it did so cheaply: the check that refuted the traversal claim took about
a minute. That is weak evidence for the standard being worth its friction,
and it is the only evidence available so far.

— Peter Kagstrom, drafted with Claude Opus 5, 2026-08-07
