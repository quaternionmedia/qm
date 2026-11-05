# What the corpus's pages remembered — 2026-10-10

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-10 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5 |

The corpus's records, entry documents, handbook pages, workflow headers and
protocols carried their own history: the incident behind each clause, the
audit that went wrong, the measurement that settled an argument. Under
`records/DRAFT-durable-text-states-what-is-true.md` those pages now state
rules and forces in the present tense. This page keeps the stories, read at
`1e5961f`. Figures are as the pages gave them, each true on the date it names.

## Six sessions on one workstation

On 2026-08-09 six sessions ran in parallel across six repositories, and the
failures were not in any one session's work but in what they did to each
other: a port already bound by another project's server, a branch neither
session knew the other had cut, a working tree two of them wrote to. That
afternoon an Alfred session measured test results against `localhost:8000`,
which Apothecary's API was serving from another session; every number it
reported was about the wrong program, and two failing tests were investigated
as defects in code that was not running. Apothecary and RAD each had a second
session on the same repository that neither could see. Each clause of
`handbook/async-contract.md` named the event that produced it.

Later events added clauses. On 2026-09-20 ShowRunner's #22 was closed unmerged
because its commits were folded into a twenty-two-commit integration pull
request -- the rule then in force allowed one open pull request per
contributor -- and the result was one diff too large to read in place of three
that each could be. On 2026-09-28 the corpus's #128 merged with
`--delete-branch`, and #129, stacked on it, was closed rather than retargeted;
restoring the branch recovered it, and checks that run only against `main` ran
on it for the first time. Pushing a pull request's head onto its base before
closing it, which merges it, has happened here. The never-request-a-review
rule needed three corrections across two repositories before it was written
down plainly.

## The entry document and the records behind it

`AGENTS.md` once said a pull request was opened "for human review" and that an
agent must never merge, while `records/DRAFT-version-tags-are-claims.md` §4
said `main` asserts nothing and the human gate is the tag. Both were in the
tree at the same commit and neither looked wrong alone. A session read the
entry point, built its model of the organisation from it, and delivered an
analysis whose central claim was that throughput was limited by a review queue
at the pull request; the record saying otherwise had been read by the same
session and could be quoted by it on request. That produced
`records/DRAFT-the-read-document-governs.md` and `AGENTS.md` item 16.

The other items carried their incidents too. One pull request sat open carrying
18 commits of unrelated work under a title describing one CI check. The first
local run of the corpus's own workflows failed a step every hand-run check had
passed, because the workflow called a console script that was not on PATH. In
one session, four false readings came from reading a signal unchecked:
`git merge-tree` on git 2.37 read as eight branch conflicts, `git check-ignore
-v` inverting its own verdict, a text scan matching the docstring that forbade
its pattern, and a document generated from unfetched refs. In one day the
scaffolding produced five false results, among them 100+ lines of reported
drift whose truth was 0, 0 and 2. Three holes were found in one new guard the
day it was written. Each of those is now a rule stated without its day.

The ledger record came from two days in which a session predicted parallel
lanes and delivered a contradiction of a record it had read, a gate index
predicted to take one file took two, and a CLI predicted to unify thirteen
script paths did so while broken in a way no local run could reveal -- each
established afterwards, by reconstruction. Corrections were twice applied to
the instance they arrived on and not to the class.

## Checks that could not fire

The ADR lint once had a step for `streaming-infrastructure/adr/`, a path no
branch had; it could only print its reassuring else-branch. Its default-branch
guard compared against `github.event.repository.default_branch`, which is
absent from a push payload and from every local run, so the comparison never
matched and the step reported ok with a stray `adr/` present. The namespace
guard first compared commits rather than content, which failed every
propagation by definition and broke pull requests #18, #19 and #20; its push
trigger then introduced a false red, because `github.base_ref` is empty on a
push.

Four registry checks were built, routed through `uv run qm`, tested, and run
by nobody, until `registries.yml` ran them. Before `ci-tooling-tests.yml`,
nothing tested the seed's checks, and six defects reached the seed, each a
check reporting success while enforcing nothing. Signing had silently stopped
three days before anything checked signatures, when a session added a flag
disabling it. The corpus twice read a failing check as passing because `tee`
replaced the exit code. The tag-determinism rule was written here and at first
not wired here. The private-names check once knew 2 of 34 private names, so
every `clean` meant only that two names were absent; six rulesets sat drafted
from 2026-08-10 while the host reported zero applied; and an unpaginated
`gh api` returned 100 of 109 repositories and declared three projects
nonexistent.

## Audits that were wrong

`qmetronome` was audited first, on 2026-08-08, and correctly. `apothecary` was
audited next and recorded as the healthiest instance, every seed artifact
present: that described the local working tree on an unpushed governance
branch, and `origin/main` had none of it. Read correctly it was the least
adopted of the three. The same audit found CI failing on a submodule pinned to
an unpushed commit -- the failure `qmetronome` had already hit and written a
check for that nothing carried across, which became the seed's submodule
check. `datum` carried a defect the corpus caused: its pin named a commit on no
remote, because the org branch was renamed and re-signed before its first push.

The propagation runbook's first end-to-end run, against `qmetronome`, gave six
findings none predicted, among them that propagation had never run while the
naive "any merge" check said it had, and that keeping both sides of a conflict
made the next propagation conflict too. The consolidation cycle's first run
across the estate on 2026-09-20 found a local branch named `test` holding the
organisation's real work in more than one repository, a working tree moving a
submodule gitlink to a commit on no origin ref, and handoff pages describing
landed work as pending. Its first run also pushed a page naming a private
repository into a public artifact, repaired after the push.

Forking defects were "did the documented thing, got the wrong artifact": a
`cp -a` that dereferenced a symlink, an ignore rule that swallowed the files
just copied, `.gitignore` files excluding `.vscode/` or every `*.json`, and a
step four that said "all three" workflows and left a fork one gate short.
`alfred`'s carried patch had been carried since 2021 and never offered upstream.

## The measurements behind records

Several records rest on one measurement each, now kept here rather than in
their Context. Across 24 repositories and 237 archived conversations the
organisation had 169 relations; the directed ones held zero cycles, and walking
the symmetric ones found 42, every one two conversations touching the same
repository -- noise, which is why knots are cycles of obligation. On 2026-09-06
the committed documents held 95 loose ends, among them a thread idle 23,204
hours and twenty-seven records awaiting ratification, every one already written
down and never seen together. On 2026-08-30 a vector publisher governed
`0.6.0`, a consumer vendored `0.4.0`, both were green, and the two consumers
replayed disjoint halves of the set.

The walkthrough record surveyed seven attempts at a worked example across six
repositories, one convergence -- `qmetronome`'s screenshots and guide
regenerated from its test command with zero drift, while its changelog,
needing a remembered command, was a release behind. Mandatory reading rose by
58 lines in a session whose goal was reducing it. The licence record found
about six licences across 84 Python packages declared in more than twenty
spellings. Twenty-four of thirty-three private repository names were ordinary
words.

The evidence for `a-check-is-evidence-after-it-fails` was one session across
four repositories: thirty defects, the ones found by reading all defects of
shape, every defect of behaviour found by making something fail -- and six of
those were guards written that session to check those exact properties. The
evidence for `shrink-the-black-box` was a facet that asked for a page
containing itself: the recursion ran 109 levels before Python stopped it, a
guard written for another purpose caught the error, every frame returned a
plausible answer, and a function optimised from 8.15 s to 0.07 s went back to
1.478 s with no test noticing for four pull requests. On 2026-08-25 a local
round ran three repositories against each other and found four defects, all
tested, all at the deployment phase -- which produced the four-phase record.

The test-posture page was written after one measured pass over the suite,
stamped 2026-08-22: 178.6 s to 137.6 s while it grew from 1058 to 1346 tests,
nothing deleted, after finding one test spending 17% of the suite asserting a
refusal and ninety-three tests each building the same repository from four
subprocesses.

## Small things the pages remembered

- On 2026-08-11, 55 of 129 workflow runs came from five iterative pushes,
  which is why superseded pull-request runs are cancelled.
- The glossary stylesheet answered a brief -- a slight colour difference,
  without an underline, for accessibility -- whose halves conflicted on the dark
  theme: an exhaustive search of the sRGB cube found no colour clearing both
  contrast ratios, and the dotted cue was the way out.
- The ledger's first entries were reconstructed, because the protocol was
  adopted mid-session.
- Four of the nine commits before the human-only record carried a vendor
  co-author trailer, because nothing put the rule in front of the assistant.
- The README and two about pages said the charter had eleven principles after
  it had seventeen, and two pages said twelve records after the index listed
  forty.
