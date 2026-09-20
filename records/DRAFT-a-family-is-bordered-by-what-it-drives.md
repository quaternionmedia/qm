# QM-XXXX — A Family Is Bordered by What It Drives

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-28 |
| **Pends on** | §4 — whether the video-production repositories are a fourth family of this estate or sit outside it. That is a scope decision a person makes, and nothing here settles it. |
| **Principle** | `seams-on-standard-protocols` — seams on standard protocols; `decisions-are-documented` — decisions are documented or they didn't happen |
| **Restated in** | Nothing. |

## Context

The organisation holds far more repositories than the roster carries.
`uv run qm inventory`, run against the host on 2026-08-29, prints the roster
beside what the host actually holds and labels the remainder *the corpus cannot
see these*. A large part of that remainder is not abandoned work. It is a
working estate that predates this corpus and exists to put on a show: to cue a
room, to play an instrument, and to put something in front of a performer while
they play.

That estate has never been named, and the roster has no way to name it. Its
three claim dimensions are `role`, `phase` with its `phase_source`, and
`attention`, and each answers a question about a repository **on its own**.
None of them can say that two repositories are one working system. So that fact
has lived wherever the last person to set up a show happened to keep it.

Nothing is broken by this today. The cost arrives on the next change: with no
border written down, two repositories that meet during a performance are as
easy to merge as to connect, and a merge across that boundary is not undone by
a later decision.

**The estate already names its own centres, in the one place nothing checks.**
Read the host's repository descriptions — `gh repo list quaternionmedia`, run
2026-08-28 — and several of them define themselves against another repository:
the Cuelist helper calls itself a plugin for ShowRunner; midiphonor calls
itself a Holophonor implementation; uPhonor calls itself a Micro-Holophonor.
Those are structural claims about how the estate fits together, made in a field
no gate reads, that no record cites, and that anyone can edit in a web form
without a commit.

This corpus already knows how to draw a border of this kind, and knows what to
draw it on. The adoption record on the looksatwords project branch separated
that project from codecartographer on **the corpus each one reads** rather than
on what either emits — both draw a graph and both serve it in a browser, so the
output side could not tell them apart. The same asymmetry holds here, and
harder: two of the families below both emit MIDI.

## Decision

**A family is a stated claim that several repositories are one working system,
and its border is what its members drive.**

### §1 — A family is a claim, made by a person

It has the same standing as `attention`, and for the reason
`records/DRAFT-attention-is-a-claim-activity-is-measured.md` gives: a claim is
stated, never inferred. A family is not read off a dependency graph, a topic
list, a shared word or a commit date. Absent membership is unstated — it is not
a finding that a repository has no family.

### §2 — The border is what a member drives, not what it is made of

A repository belongs to a family by what its output acts on.

Not by what it is written in: this estate spans Python, TypeScript, JavaScript,
C, C++ and Kotlin, and the border cuts across all of them. Not by what it
emits: two of the three families below emit MIDI, and one emits pixels that
another also emits. Not by shared vocabulary: *cue*, *loop* and *track* each
mean different things in two of the three, and a border drawn on words would
have placed one program in all of them.

### §3 — The estate is seven families, three of them performing

| family | drives | named public members |
|---|---|---|
| `show-control` | **the room** — cues, lighting, sound and video playback, audio transport | ShowRunner; the Cuelist, QLab and TheatreMix helpers; cesar; ShowStopper; aes |
| `instruments` | **the sound** — looping, synthesis, tempo, remote control surfaces | holophonor; midiphonor; carlos; qmetronome; wolf; ludwig; waveofhormuz |
| `performer-display` | **the performer** — what a player reads while playing | joe; leo |
| `irl` | **matter** — a thing somebody builds, holds or installs: parts, boards, enclosures, and the firmware that makes one work | apothecary; datum; scad-chess; stomp; ira; uPhonor; and three private repositories, referenced rather than named |
| `infra` | **where a thing runs, and how it is reached** — ingress, identity, storage, DNS, observability, the network path | moat; ztgui; and two private repositories, referenced rather than named |
| `core` | **the corpus and its tooling** — governance, the archive, the deltas, the maps, the language data | qm; qmcp; dossier; codecartographer; looksatwords |
| `games` | **play** — a game somebody plays: its rules, its world and its loop | golfvs; titanharvest |

`games` is the family the border test admits most easily and the one the
estate never named, because a game is the activity rather than a thing that
serves one. `performer-display` also emits pixels a player reads, and the two
part exactly there: a score display is read *while* the performer does
something else, and a game *is* what the player is doing. Both members are
built on one engine and neither is built on the other — the same shape as
`performer-display`, siblings by what they drive and not by descent. A game
server is not a member: it runs a game and decides nothing about play, which
is the refusal `infra` below makes from the other side.

`infra` is what everything else runs on, and it is a family rather than
substrate — a distinction §4 now has to carry twice, because the two cases look
alike and part in one place. **Substrate is built *with*; infrastructure is run
*on*.** A radial menu is compiled into a host and ships inside it, so it has no
independent existence and belongs to no family. A platform is never imported by
anything: it holds identity, ingress, storage, DNS and the network path, and a
repository that stops using it does not lose a dependency, it loses a home.

The border refuses more than it admits here, which is how it earns its keep.
A deployment *of a service* — an etherpad, a video recorder, a game server —
runs on infrastructure and is not infrastructure, so none of them is placed
here on the strength of having a Dockerfile. What is asked is whether the
repository decides where other things run, not whether it is deployed.

`infra` extends `core` in the sense that the corpus and its tooling are among
the things it hosts. That relation is a **seam** under §5 and not a family
relation: the two are peers in this table, and neither contains the other.
Reading `infra` as a subdivision of `core` would make every family a
subdivision of it eventually, since everything runs somewhere.

`irl` is where §2's border was tested hardest, and it moved three
repositories. A foot controller, an LED controller and a micro-looper each
*drive* sound or light — which put them in a performing family — and each is
also a board somebody solders into an enclosure. Both readings are true, and
the map is a function, so one had to win.

Matter wins for these three, and the reason is the test rather than the taste:
what the repository *emits* is a physical thing, and the sound or light is what
that thing does once it exists. A reader looking for the pedal will look for the
pedal. `cesar` stays in `show-control` by the same test — it emits a program
that drives lights, and nothing you can hold.

This is the revision trigger in this record firing rather than being written
around: *a repository that drives two of the families means either the border
is drawn wrong or the thing is a seam wearing a single repository*. Here the
border was drawn on one axis and the estate turned out to have two, and the
cost is visible — `show-control` lost `ira`, `instruments` lost `stomp` and
`uPhonor`, and a search for either in its old family now finds nothing.

`core` is the family that drives none of the three above, and that is the
point of naming it rather than leaving it unstated. It drives **the work
itself**: the constitution, the archive of what was decided, the deltas those
decisions become, the maps drawn over the code, and the language data read out
of the prose. A change there reaches every other family by changing what
governs them, which is a different relation from the seams §5 describes and is
why it is a family rather than substrate.

The border test in §2 still applies to it and still decides. A repository that
renders a performance is not `core` however much governance it carries, and a
repository that only ever reads and writes the org's own record of itself is
`core` however interesting its output. `rad` is the case that shows the test
working: it is consumed by two `core` members and is substrate to both, so it
belongs to no family — see §4.

Three asymmetries, recorded rather than smoothed:

- Show control and instruments each have a hub that the periphery names itself
  after. Performer display has none. joe and leo are siblings by what they
  drive, and neither is built on the other.
- `core` is the only family whose members are adopted. Every member of the
  three performing families is unadopted today, so a family name says what a
  repository is part of and nothing about whether governance reaches it.
- At least one member of this estate is a private repository, which the roster
  references rather than names. This record cannot place it without defeating
  that redaction, so the placement is made where the name is legible: in the
  uncommitted private roster, beside the entry that already holds it.

### §4 — What is outside these three, and what is unsettled

Video editing and video generation drive none of the three: they produce media
before or after a performance rather than during one. They are outside these
families. Whether they constitute a fourth is the `Pends on` above, and the
three stand either way.

A radial menu is substrate, not a member. A family member may be built with it,
and it belongs to no family — the same holds for the front-end component
repositories. Substrate is what more than one family can be built on, which is
exactly why placing it in one would be wrong.

### §5 — What crosses between two families crosses as a protocol

`records/DRAFT-seams-on-standard-protocols.md` governs, and this estate is an
unusual case of it: the standard protocols are already in place and predate
this corpus. A change that needs two families is a seam, and it crosses as
MIDI, OSC, timecode, an audio-over-IP transport, or HTTP with a schema. It does
not cross as an import, and it does not cross by merging two repositories into
one.

The clause is written down because the wiring being old makes it invisible. A
seam nobody had to build is a seam nobody thinks of as a seam.

### §6 — Naming a family adopts nothing

`ci/workspace.yaml` closes with *Presence here is not adoption*, and the same
holds a level up. Placing a repository in a family says what it is part of. It
does not vendor this corpus, does not create a project branch, and does not
bring the repository under governance. Adoption is the procedure in
`handbook/forking-a-project.md`, taken one repository at a time and decided one
repository at a time.

## Consequences

**The roster carries the claim and `uv run qm families` reads it.** A
repository names its family in `ci/workspace.yaml`, and the set of families is
read out of §3 of this record rather than copied into the tool -- so renaming a
family here is a roster claim that stops resolving, which is the failure that
announces itself. `ci/families.py --check` refuses a claim naming a family this
record does not declare, and reports a repository that claims none as
*unstated*, never as *none*.

What no check reaches is §2, and it is the half that matters: whether a
repository really belongs where somebody put it. The border is what the thing
drives, and reading it needs a person who knows what the code does.

**Three borders means three ways to be in the wrong repository**, where before
there were none, because there was no border to be on the wrong side of. That is
the intended effect, and it is also the new cost: a contributor now has a
question to answer that they did not have.

**Most of this estate is cold, and naming it does not warm it.** A family whose
hub has not moved in a year is a maintenance question. This record makes the
question askable by giving the thing a name; it does not answer it, and reading
a family name as a statement that somebody is working on the family would be the
same mistake `attention` exists to prevent.

**The estate's membership is split across a committed document and an
uncommitted one**, and the two can drift with nothing to notice. That is the cost
the roster already pays for its private entries; this record adds a second place
it is paid.

## Alternatives considered

**One performing family.** Cheapest, and it has no test. A single family
spanning an LED controller and a PDF annotator cannot answer the only question a
family exists to answer — does this change belong here — because everything
qualifies.

**Group by stack, following `one-house-stack`.** The border would cut through all three
families and join parts of each, since the estate is polyglot. `one-house-stack` also governs
what QM writes rather than what belongs with what, so this would be reusing a
principle to answer a question it does not address.

**Make it a lane.** The lanes in `ci/lane-registry.yaml` are kinds of
*governance work* — meta governance, the development loop, documentation. A
repository family is not a kind of governance work, and folding it in would make
`uv run qm lanes` answer two unrelated questions in one table.

**Infer the families from dependencies or topics.** Rejected by §1, and it would
not work anyway: where two members connect over MIDI or OSC at run time, a
dependency graph cannot see the connection at all. It would report the estate as
a set of unrelated repositories and be confidently wrong.

**Add the roster field in this same change.** Rejected on sequencing. A schema
landed beside the argument for it gets read as the argument, and the field's
shape is easier to get right once the border has survived a reading.

## Revision triggers

- A repository that drives two of the three — one that cues the room and renders
  the score — means either the border is drawn wrong or the thing is a seam
  wearing a single repository.
- The video-production repositories being placed, either way. That closes the
  `Pends on`, and §4 is rewritten to match.
- A second private member, or the existing one becoming public. Either changes
  where the estate's membership can be written down.
- A family's hub going cold while its periphery keeps moving. That is the shape
  of a fork the organisation has not decided to take.
- The roster gaining a family field. At that point the table in §3 stops being
  the only copy and becomes an input, and §3 says which it is.

## Amendments

*(none)*
