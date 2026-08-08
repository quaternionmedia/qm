# Perspective — Adopting the Constitution into a Four-Year-Old Codebase

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (Anthropic), the assistant that performed alfred's governance-adoption pass |
| **Task** | An honest account of adopting this corpus into alfred — the org's first project that predates the constitution rather than being created under it — and what that surfaced about the corpus's assumptions. |

## 0. Standing, scope, and evidence base

One adoption pass, on one project, in one assistant session. Evidence classes
follow the convention the 2026-07-04 retrospective used:

- **E1** — directly read, run, or measured during this pass (the actual
  files, the license reports generated locally, the lint fixtures).
- **E4** — inference from a single data point.
- **E5** — prior general knowledge, unverified this cycle.

The same discount that document applied to itself applies here: this
evaluates an adoption performed minutes earlier in the same session. §1 is
where to look for self-flattery. One difference worth noting is that several
claims below are mechanically checkable rather than judgment calls — a lint
either flags a file or it does not, `git check-ignore` either matches a path
or it does not — and those are marked E1 for that reason.

## 1. What worked

### 1.1 The server-shaped defaults fit, and that is informative (E1)

The 2026-07-04 retrospective's headline finding was that the corpus's
defaults are server/infra-shaped and the first non-server project pays a
translation tax. Alfred is a container runtime with images, a deployment, a
control plane, and engines. Essentially none of that tax was paid here: the
words "deployment," "image," and "control plane" all had literal referents,
and no argument had to be constructed to make a record apply.

That is not a rebuttal of the earlier finding — it is the control case that
makes it precise. The tax is specific to project *shape*, and does not
generalize to "adoption is expensive." Alfred paid a completely different
tax, described in §2.1.

### 1.2 Enumerating conflicts produced a better document than complying would have (E1)

The adoption record's substance is a table of eight conflicts. Writing it was
uncomfortable in a productive way: several rows were things nobody had said
out loud, and one of them — the object storage seam — turned out to be
cheaply fixable once written down, which nobody had noticed while it was
tacit. A record that had asserted compliance would have had less content and
less value.

### 1.3 The pin-as-submodule model paid off again, for a new reason (E1)

The earlier retrospective valued the submodule pin because claims about the
corpus could be checked against vendored text rather than a remembered
paraphrase. This pass found a second benefit: because the lint now runs from
the submodule rather than from a copy, improving it improves every project on
its next pin bump. The branch-per-project model turns the vendored corpus
into a delivery channel for executable governance, not only for text.

## 2. Friction worth naming

### 2.1 The corpus assumed adoption happens at project creation (E1)

The tax alfred paid was *age*, not shape. Every prior adoption was
greenfield or near it, and the corpus had exactly two states — instantiated
and improvised — both of which assume a project can be compliant on the day
it adopts. Alfred cannot: its datastore, its dependencies, and its
integration shapes were chosen years before the records existed.

Left as-is, that pushes an existing project toward one of two bad outcomes:
assert a compliance it does not have, or do not adopt. The second is worse
than it looks, because the projects most in need of governance are exactly
the ones with the longest history of decisions made without it. This branch
proposes a third state. Whether it is the right one is a single-instance
judgment (E4) and should be tested against the next such project.

### 2.2 A green license report on a non-compliant stack (E1)

This is the most transferable finding here. Alfred's Python dependency scan
returns 84 packages, every one under a permissive OSI license. Its frontend
scan returns 12 packages, 11 permissive and one GPL-3.0 — which the record
explicitly accepts. Both scans are accurate and both pass.

The deployed stack runs a source-available database image, stores its output
in a vendor's hosted object store, and loads a font from a third-party CDN.
None of the three appears in any dependency manifest, so no scan can see
them. A project wiring only the gates the record asked for would have
produced a green check and a false claim.

The gap is structural, not a tooling deficiency: the exclusion rule is
phrased about the licenses of software components, and a hosted service has
no license to check. The proposed fix — an ownability test enforced by a
reviewed inventory rather than a scanner — is deliberately weaker machinery
aimed at the real exposure, which I think is the right trade but is
genuinely arguable (E4).

### 2.3 License metadata is not comparable raw (E1)

Two mechanical facts from the same pass. Alfred's 84 Python packages express
roughly six distinct licenses in more than twenty spellings. And one direct
frontend dependency declares its license only in npm's deprecated `licenses`
array, where a reader of the modern `license` field sees null — meaning a
naive gate would have treated a GPL-3.0 component as undeclared.

Any project writing a license gate will hit both. Neither was written down
anywhere in the corpus.

### 2.4 The lint's first false positive was the document that defines it (E1)

The shipped lint was a grep. Run against this corpus's own `records/`, it
flagged the decision-record-discipline record — because that record
enumerates the banned vocabulary in its Consequences. It would also have
flagged any draft still carrying the template's drafting-rules comment, which
the template instructs drafts to keep until ratification.

So the check that every project was told to copy verbatim would fail on a
faithful copy of the corpus's own template. Nobody noticed, because nobody
was running it — this repo had no CI at all. A lint that is required
everywhere and executed nowhere is indistinguishable from a convention, which
is the enforcement model the discipline record itself rejects.

Once prose-only scanning removed the false positives, two genuine hits
surfaced immediately, one of them in text drafted during this very session.
The check earns its place; it just had never been run.

### 2.5 The IDE seed had never survived contact with a project (E4)

Three defects in `project-seed/ide/AGENTS.md` forced deviations from a
verbatim copy: it pointed at `adr/` at the project root, which does not exist
under the branch-per-project model the corpus mandates; it left a literal
`project/<name>` in a live file; and its instruction to leave the governance
section untouched conflicted with both.

Each is the kind of thing that shows up the first time a file is used rather
than read. Combined with the seed's `cp -a` instruction, which on this
machine dereferenced one pointer file into a full copy and failed outright on
the other, my inference is that alfred is the first project to actually copy
`project-seed/ide/` onto a real repository. I cannot verify that — the other
projects' own repositories were not examined this pass — so it is E4, and it
would be worth someone checking, because if true it means the record
describing this mechanism as live has been describing a seed nothing had
exercised.

### 2.6 Default assistant tooling still fights human-only contributorship (E1)

The record notes that assistant tooling appending a
`Co-Authored-By: <model> <noreply@...>` trailer must be suppressed, and calls
the instruction-only enforcement a known soft spot. It is. This session's
harness carried a standing instruction to append exactly such a trailer, and
the only thing that stopped it was `AGENTS.md` being read first and the
conflict being noticed and raised.

That is the mechanism working — governance found the reader — but it worked
because the discovery file existed *and* the assistant surfaced the conflict
rather than silently resolving it either way. Neither is guaranteed. The
record's own revision trigger for this ("the instruction-only ban is missed
by a new contributor or a fresh drafting session") has not fired yet, but a
commit-msg hook remains cheap insurance against the case where it does.

### 2.7 Copy-verbatim seeding drifts, and the corpus knows it (E1)

`adr/README.md` is copied verbatim into every project branch. Improving it on
`main` leaves every existing project stale until someone merges. During this
pass the seed's CI-enforcement section was rewritten, which immediately made
alfred's freshly-created copy out of date — the drift appeared inside a
single session.

The propagation path exists (merge `main` into the project branch) and is
designed. But alfred's own CI is centralized in an org-level `.github`
repository via reusable workflow references, which is a strictly better
pattern for anything executable: fix once, every caller gets it. Moving the
lint logic into the submodule captures most of that benefit here. Whether the
prose seed files should follow is an open question this pass did not answer.

## 3. Proposals

Some of these landed on the same branch as this document; a perspective
cannot ratify anything, so even those remain a human's call to keep or drop.

1. **Adoption path for existing projects** — the conflict-table state, with
   enumeration explicitly not a waiver and no schedule required. Drafted.
2. **Hosted services in the exclusion rule's scope**, tested for ownability
   rather than license, enforced by a reviewed inventory. Drafted.
3. **Cumulative license gates** rather than one path chosen by runtime shape,
   plus mandatory SPDX normalization and a requirement to read deprecated
   metadata fields. Drafted.
4. **License compatibility as a distinct question** from per-component
   compliance. Drafted, and deliberately not resolved — alfred declares MIT
   while shipping a GPL-3.0 frontend component, and someone should decide
   what that bundle is actually licensed under.
5. **Publish the four lint checks and run them here.** Drafted.
6. **A commit-msg hook or CI grep for co-author trailers**, closing the soft
   spot §2.6 describes. Not drafted; it is a small piece of work and the
   record already names it as the gap it is.
7. **Check whether `project-seed/ide/` has ever been copied into another
   project** (§2.5). Not a proposal so much as a question someone with access
   to those repositories can answer in five minutes, and the answer changes
   how much confidence the IDE-governance record's "already live" claim
   deserves.

## 4. Closing honesty

This is not independent review: it evaluates an adoption performed in the
same session by the same assistant, and the corpus amendments it praises were
drafted alongside it. A reader looking for where I am flattering my own work
should start with §1.3 and §2.4, both of which describe problems whose
proposed solutions I also wrote.

It is also not a survey. Every generalization rests on one brownfield
adoption. §2.1's proposed third state is a plausible fix to one project's
friction, not a validated fix to a recurring pattern, and the second existing
project to adopt this corpus should be treated as the real test.

The one claim I would defend hardest is §2.2, because it is the least
dependent on judgment: the scans pass, the stack is non-compliant, and both
statements are checkable by anyone who runs the workflow.

— Peter Kagstrom, drafted with Claude Opus 5, 2026-08-07
