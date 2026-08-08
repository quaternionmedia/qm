# Perspective — The First Hardware Onramp: Artifacts the Gates Cannot See

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (Anthropic), the assistant that performed the onramp this reflects on |
| **Task** | A retrospective on instantiating the org's first hardware project against this corpus, naming one structural gap (the enforcement mechanisms cannot see a hardware project's principal deliverable), one concrete defect in the forking procedure, and one failure shape the corpus shares with the project it just onboarded. |

## 0. Standing, scope, and evidence base

This reflects a single work package — WP-0, repository bootstrap — on a
single project, performed in one assistant session. **No hardware exists
yet.** There is no schematic, no board, no firmware, no schema. Every claim
below about how this corpus meets hardware is therefore a claim about
*scaffolding* a hardware project, not about building one. The gap named in
§2.2 is the one most likely to change shape when a real KiCad project is put
in front of a real gate at WP-4.

Evidence classes, per this corpus's convention:

- **E1** — directly observed or read during this session: the corpus text as
  vendored, the commands run, the git history cited.
- **E4** — inference from a single data point; one hardware onramp exists, so
  anything claiming a pattern is provisional.
- **E5** — prior general knowledge, unverified this cycle.

The 2026-07-04 qmetronome retrospective's self-discount applies here in the
same form and for the same reason: I performed the onramp I am evaluating,
minutes earlier, in this session, for this maintainer. §1 is where to look
first for self-flattery. The project-side artifacts are `AGENTS.md` and
`HANDOFF.md` in the project repository, and the five numberless drafts on the
`project/tessera` branch of this repo; this document is the corpus-side half,
written for whoever forks the seed onto the next thing that isn't software.

One mechanical note: this file quotes the banned-vocabulary list in §2.3 in
order to describe a lint finding. It lives in `perspectives/`, outside every
current glob, so nothing fires. Any future broadening of that glob needs the
same path exclusion this document argues for.

## 1. What worked (concurrences)

### 1.1 The perspective channel closed its own loop, and this onramp spent the proceeds (E1)

All five proposals in the 2026-07-04 qmetronome retrospective are in the
corpus. They landed the same day, in `5a7d34a` and `d1b8afc`, both after
`9744ae6` added the perspective — order verified by `git log --reverse`, not
assumed from dates.

This onramp consumed four of them directly, and would have been materially
more expensive without them. The ADR lint was copied from `project-seed/ci/`
rather than reinvented reactively (proposal 2). The license gate had a named
non-container path to point at instead of a hand-typed table (proposal 4).
The forking procedure's own paragraph on new-class translation cost meant the
hardware mismatches below read as expected overhead rather than as evidence
of misfit (proposal 5). And this document has a defined response state to
land in rather than silence (proposal 3).

That is the strongest available argument for writing the next one, and it is
worth stating plainly because the channel's whole risk is that honest gap
analysis feels unrewarded.

### 1.2 Governance in the path bound a model instance nobody briefed (E1)

P11's claim is that governance placed in the file a reader already opens will
be read. It got a clean test this session. The assistant's own standing
tooling instruction was to append a `Co-Authored-By:` trailer naming a vendor
`noreply@` address to every commit. Both commits made this session carry no
trailer, because `AGENTS.md` — read before the first action, as it asks — says
to suppress it. No human raised contributorship at any point.

The human-only-contributorship record's Consequences call the instruction-only
ban "a known soft spot, not a design choice," pending a commit-msg hook or CI
grep. This is one data point on the optimistic side of that. One data point is
not a mechanism, and the record is right that the check is still owed.

### 1.3 Copy-verbatim is checkable, and checking beat reading (E1)

`adr-lint.yml` and both `.vscode` files were verified byte-identical to
`project-seed/` by comparison rather than by inspection. The two symlinks were
verified by blob hash against the seed's own objects — `47dc3e3d` for
`CLAUDE.md`, `be77ac83` for `.github/copilot-instructions.md`. The hash check
is strictly stronger than reading the file, because it proves the *target
path* is right and not merely that the content looks plausible. It is also
what surfaced §2.1, which reading would not have.

## 2. Friction worth naming

### 2.1 `cp -a` does not preserve symlinks here, and the procedure lists it as equivalent (E1)

`README.md`'s "Forking a new project," step 5, names `git checkout`,
`cp -a`/`cp -P` and `rsync -a` as interchangeable symlink-preserving copies,
and the section closes by saying the Windows path was "verified on a real
Windows checkout, not assumed."

On this Windows checkout, with Developer Mode on and `core.symlinks true` set,
`cp -a` from `project-seed/ide/` produced a **regular file** for `CLAUDE.md`
containing `AGENTS.md`'s content, and failed outright on
`.github/copilot-instructions.md` with "cannot create symbolic link." Only the
`git checkout` path worked. The scaffold now writes both entries into the index
at mode `120000` and materializes them with `git checkout`, which is one of the
three methods step 5 offers — so the procedure's outcome is reachable, but not
by all three routes it names.

The verification the section cites is real and covers a different operation:
git *materializing* symlinks on checkout. The seed *copy* is a separate step,
performed by a different tool, and is the one step 5 actually prescribes.

The failure mode deserves naming apart from the fix, because for `CLAUDE.md`
it is silent and plausible. A regular file holding the right text passes any
check shaped like "does `CLAUDE.md` contain the governance content" — the
project's own acceptance criterion is worded that way — while breaking the
single invariant the IDE-integrated governance discovery record exists to
create: that editing `AGENTS.md` keeps all three files current. Only inspecting
the *mode* distinguishes them. This is the shape the 2026-07-21 perspective
names: diagnosing a file by its apparent role instead of its traced mechanism.

### 2.2 A hardware project's principal deliverable is invisible to every gate this corpus defines (E1)

The open-license record fixes its criterion as OSI-approved or FSF-free, and
its enforcement as a generated license report along one of two paths:
SBOM-per-image, or a dependency-manifest report per package ecosystem. Both
paths enumerate *software dependencies*.

A schematic, a board layout, a footprint library, a bill of materials and an
OpenSCAD part are copyrightable works. OSI does not review licenses for them,
and no dependency report can see them. A hardware project can therefore run
every gate this corpus mandates, report zero violations, and ship its
principal deliverable carrying no grant at all — which under P1 means a
recipient holding the design cannot modify or redistribute it. Green CI would
be reporting on the smallest part of what was published.

The project's own licensing draft states this in its Context and then meets
the wall the corpus builds. Precedence permits a project to *add* constraints,
so a project-level hardware clause is legal — but the missing piece is not a
constraint. It is an enforcement mechanism the corpus does not have, and a
project cannot add one to an org record. The handoff packet's open question on
venue (project record, or amendment to the org record) is unresolved for that
structural reason rather than for want of someone to decide it, and framing it
as a venue preference understates what is actually missing.

REUSE plus SPDX headers is the obvious candidate, and the project record
already proposes it as a project obligation. It is tooled, it is generated
rather than hand-compiled, and it is the only one of the three that sees a
`.kicad_sch`.

### 2.3 Gate absence is invisible; only gate failure is visible (E1)

Step 4 of the forking procedure requires the license gate at instantiation:
"a project without both is not instantiated, it is improvised." This project's
handoff packet routes the license gate to WP-6 with REUSE compliance, several
work packages later. Each position is defensible on its own. Together they
open a sanctioned interval in which the repository is improvised by the org's
own standard, and nothing detects it, because a gate that was never wired is
indistinguishable from a gate that passes. A failing gate is loud; a missing
one is silent.

The corpus supplies its own instance of the same shape. `qm/.github/` contains
one symlink and no `workflows/` directory: this repository runs no CI on
itself. Its own `records/DRAFT-*.md` are held to the identical squash
discipline — `AGENTS.md` item 5 restates the banned vocabulary verbatim — and
nothing checks them. Running the seed lint's own expression over `records/`
returns one file, `DRAFT-decision-record-discipline.md`, the record that
defines the ban. It contains two distinct things:

- A genuine instance in the narrative sense the rule prohibits, in the
  sentence spanning lines 14–15 and reported by the lint at line 15: "Drift
  of this kind was observed and corrected in the org's first drafting round."
- Lines 39–40, a structural false positive: the ban list quoting itself as
  part of its own definition. This is the identical collision the project's
  `HANDOFF.md` produces, and it solves it the same way — by living outside the
  glob rather than by weakening the expression.

One real violation and one false positive, in the same file, in the document
that defines the rule, unnoticed because no job runs. That is not an argument
that the discipline is wrong. It is an argument that "convention without
enforcement" — which the discipline record itself rejects in another context —
is the corpus's current position on its own records.

### 2.4 Two org-shaped rules were invented at project level because no record covers them (E4)

The project's drafts carry two obligations with CI teeth that have no org
analogue. "Every BOM line has two or more independent sources, or a documented
drop-in alternate footprint" is P3's replaceability test applied to silicon,
with the same exception-plus-exit-plan structure the seams record uses for
single-implementation APIs. "No schematic in `hardware/` contains a net class
or component rated for mains" is a safety gate.

The second is genuinely this project's. The first is not: any QM project that
has something fabricated meets it, and the corpus's own standard — two
projects asking the same question is the signal a clause belongs at org level
rather than repeated exceptions — puts it one hardware project away from being
org-shaped. Sample size is one. Recording it now costs nothing and makes the
second instance recognizable instead of independently re-derived, which is the
outcome §2.4 of the previous retrospective was written to avoid.

### 2.5 Adoption by reference currently points at a corpus of drafts (E1)

All eight org records are `Proposed`. None carries a QM number. The project
that just adopted this constitution by reference adopted eight unratified
documents, and its own five records queue behind the same human action at the
same maintainer. Nothing about the onramp was harder for it, and the corpus is
explicit that ratification is deliberately a human act — this is an
observation about a single-queue dependency, not an argument for automating
the queue, which would defeat its purpose.

## 3. Concrete proposals

None self-executing. Each is a candidate `DRAFT-*` change for a human to pick
up, not something this document ratifies or requests.

1. **Give the open-license record a third enforcement path: REUSE/SPDX, for
   artifacts a dependency report cannot enumerate** (§2.2). It sits alongside
   SBOM-per-image and dependency-manifest-plus-allowlist as a per-runtime-shape
   choice, it is generated rather than hand-compiled as clause 4 requires, and
   it answers the hardware venue question structurally instead of leaving each
   hardware project to argue it. This is the successor to the previous
   retrospective's proposal 4, one runtime shape further out.
2. **Correct step 5's copy guidance** (§2.1): on Windows `cp -a` is not
   equivalent to the `git checkout` path, and the acceptance test is mode
   `120000` in the index rather than file content. One sentence, plus a check
   worth naming because the content-shaped check passes on the broken result.
3. **Make gate absence detectable** (§2.3). A seed job asserting the required
   workflow files exist by name would turn "the license gate was never wired"
   from an invisible state into a failing one. The ADR lint proves the
   constitution ships; nothing currently proves its teeth did.
4. **Run the ADR lint over this corpus's own `records/`** (§2.3), with a path
   exclusion for documents that quote the ban list definitionally — the
   mechanism `HANDOFF.md` already relies on. The corpus holds every adopting
   project to a discipline it does not check on itself.
5. **Decide whether component sourcing is org-shaped** before a second
   hardware project re-derives it (§2.4).

## 4. Closing honesty

Four limits. This is not independent review: I performed the onramp it
evaluates, in the same session, and §1 is where to look for self-flattery.

The sample is one work package, and it is the one with no payload — WP-0 wires
governance and builds nothing. §2.2 is the document's central claim and it has
not been tested against a real artifact; when WP-4 puts an actual KiCad project
and BOM in front of an actual license gate, that section gets its first real
evidence and may need rewriting rather than citing.

§2.3's finding about this corpus's own records is one grep over one directory,
not an audit. It establishes that at least one violation exists and that
nothing would catch it; it does not establish how many.

And it is not a request. Per this corpus's own rule a perspective is the most
draft-like thing there is, opinion that never graduates on its own. If any of
§3 is worth acting on, that is a human picking it up as a record, not a status
this document can claim for itself.

— Peter Kagstrom, drafted with Claude Opus 5, 2026-08-08
