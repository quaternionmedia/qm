# QM-XXXX — A Family Is Bordered by What It Drives

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-28 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | `seams-on-standard-protocols` — seams on standard protocols; `decisions-are-documented` — decisions are documented or they didn't happen |
| **Restated in** | `README.md`'s opening picture and its caption |

## Context

The organisation holds far more repositories than the roster carries.
`uv run qm inventory`, run against the host on 2026-08-29, prints the roster
beside what the host actually holds and labels the remainder *the corpus cannot
see these*. A large part of that remainder is not abandoned work. It is a
working estate that predates this corpus and exists to put on a show: to cue a
room, to play an instrument, and to put something in front of a performer while
they play.

That estate has no name, and the roster has no way to give it one. Its
three claim dimensions are `role`, `phase` with its `phase_source`, and
`attention`, and each answers a question about a repository **on its own**.
None of them can say that two repositories are one working system. So that fact
lives wherever the last person to set up a show happens to keep it.

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
and its border is what its members drive.** A repository may be in more than
one family, and a family may sit within another.

### §1 — A family is a claim, made by a person

It has the same standing as `attention`, and for the reason
`records/DRAFT-attention-is-a-claim-activity-is-measured.md` gives: a claim is
stated, never inferred. A family is not read off a dependency graph, a topic
list, a shared word or a commit date. Absent membership is unstated — it is not
a finding that a repository has no family.

### §2 — The border is what a member drives, not what it is made of

A repository belongs to a family by what its output acts on.

Not by what it is written in: this estate spans Python, TypeScript, JavaScript,
C, C++, Kotlin and GDScript, and the border cuts across all of them. Not by
what it emits: two of the families within `performing` emit MIDI, and one
emits pixels that another also emits. Not by shared vocabulary: *cue*, *loop*
and *track* each mean different things in two of them, and a border drawn on
words would have placed one program in all of them.

### §3 — The families, and which sits within which

| family | drives | within | named public members |
|---|---|---|---|
| `performing` | **a show** — what an audience sees and hears, and the video made before and after it | — | alfred; otto; and every member of the families within it |
| `show-control` | **the room** — cues, lighting, sound and video playback, audio transport | `performing` | ShowRunner; the Cuelist, QLab and TheatreMix helpers; cesar; ShowStopper; aes; ira |
| `instruments` | **the sound** — looping, synthesis, tempo, remote control surfaces | `performing` | holophonor; midiphonor; carlos; qmetronome; wolf; ludwig; waveofhormuz; stomp; uPhonor |
| `performer-display` | **the performer** — what a player reads while playing | `performing` | joe; leo |
| `irl` | **matter** — a thing somebody builds, holds or installs: parts, boards, enclosures, and the firmware that makes one work | — | apothecary; datum; scad-chess; stomp; ira; uPhonor; and three private repositories, referenced rather than named |
| `infra` | **where a thing runs, and how it is reached** — ingress, identity, storage, DNS, observability, the network path | — | moat; ztgui; streaming-infrastructure; and two private repositories, referenced rather than named |
| `core` | **the corpus and its tooling** — governance, the archive, the deltas, the maps, the language data | — | qm; qmcp; dossier; codecartographer; looksatwords; vox; rad |
| `games` | **play** — a game somebody plays: its rules, its world, its loop, and the server it is played on | — | golfvs; rad-godot; qmcli-godot; factorio-sysops; and one private repository, referenced rather than named |
| `commons` | **the public** — open information a community reads and adds to: maps, records, public data | — | benchmark |

`performing` is the show, and the three families within it are its parts: the
room, the sound and the performer. A repository that drives one of those parts
claims that family and is in `performing` by being there. A repository that
drives the show but none of its parts claims `performing` itself, and alfred is
that case: it makes the video of a show, before the performance and after it,
not during it. otto, the engine that renders alfred's picture, is the same
case for the same reason.

`games` is the family the border test admits most easily and the one the
estate never named, because a game is the activity rather than a thing that
serves one. `performer-display` also emits pixels a player reads, and the two
part exactly there: a score display is read *while* the performer does
something else, and a game *is* what the player is doing. A game server is a
member: what its operations act on is a world people play in, and
`factorio-sysops` is in `games` on that test. It is still not infrastructure,
for the reason `infra` below gives: it decides where one game runs, not where
other things run.

`infra` is what everything else runs on, and it is a family rather than
substrate. **Substrate is built *with*; infrastructure is run *on*.** A
platform is never imported by anything: it holds identity, ingress, storage,
DNS and the network path, and a repository that stops using it does not lose a
dependency, it loses a home.

The border refuses more than it admits here, which is how it earns its keep.
A deployment *of a service* — an etherpad, a video recorder, a game server —
runs on infrastructure and is not infrastructure, so none of them is placed
here on the strength of having a Dockerfile. What is asked is whether the
repository decides where other things run, not whether it is deployed.

`infra` extends `core` in the sense that the corpus and its tooling are among
the things it hosts. That relation is a **seam** under §5 and not a family
relation: neither sits within the other. Reading `infra` as a family within
`core` would make every family one eventually, since everything runs somewhere.

`irl` is where §2's border is tested hardest, on three repositories. A foot
controller, an LED controller and a micro-looper each *drive* sound or light,
and each is also a board somebody solders into an enclosure. Both readings are
true, so both are claimed: `ira` is in `irl` and `show-control`, and `stomp`
and `uPhonor` are in `irl` and `instruments`. A reader looking for the pedal
finds it beside the boards and beside the loopers. `cesar` is in
`show-control` alone: it emits a program that drives lights, and nothing you
can hold.

`core` is the family that drives none of the others, and that is the point of
naming it rather than leaving it unstated. It drives **the work itself**: the
constitution, the archive of what was decided, the deltas those decisions
become, the maps drawn over the code, and the language data read out of the
prose. A change there reaches every other family by changing what governs
them, which is a different relation from the seams §5 describes and is why it
is a family rather than substrate.

The border test in §2 still applies to it and still decides. A repository that
renders a performance is not `core` however much governance it carries, and a
repository that only ever reads and writes the org's own record of itself is
`core` however interesting its output. `rad` is in `core` because the members
that build with it are there — see §4.

`commons` drives **the public**: open information a community reads and adds
to, such as a map of the benches somebody can sit on.

Three asymmetries, recorded rather than smoothed:

- Show control and instruments each have a hub that the periphery names itself
  after. Performer display has none. joe and leo are siblings by what they
  drive, and neither is built on the other.
- Most of `core` is adopted, and most of the estate is not. Within
  `performing`, adopted members are in `instruments` and in the outer family
  itself, so a family name says what a repository is part of and nothing about
  whether governance reaches it. `walkthrough/families/` carries the
  per-member reading, regenerated from the corpus's own branches.
- At least one member of this estate is a private repository, which the roster
  references rather than names. This record cannot place it without defeating
  that redaction, so the placement is made where the name is legible: in the
  uncommitted private roster, beside the entry that already holds it.

### §4 — A repository may be in more than one family, and a family may sit within another

A claim names every family whose border the repository is inside. A repository
that drives two things is in both, and the roster says so with a list:
`family: [irl, instruments]`. Neither reading has to lose, and a reader looking
for the repository by either finds it.

A family may sit within another, as the three parts of a show sit within
`performing`. A member of an inner family is a member of the outer one without
saying so twice: a claim naming both is refused, because the second name adds
nothing and reads as if it did. A repository may claim the outer family itself
when it drives the whole and none of the parts.

Overlap has a limit, and it is the border test rather than a count. Each claim
passes §2 on its own. A repository in many families is more likely a seam
wearing a single repository, or a component claimed by everything built on it,
and both have a better home than a longer list.

Substrate belongs to the family that builds with it. A radial menu is compiled
into its host and ships inside it; `rad` is in `core` because the members that
build with it are there, and `rad-godot`, the same contract for the Godot
engine, is in `games` because that is where the Godot work is. A component that
several families build with may claim each of them.

### §5 — What crosses between two families crosses as a protocol

`records/DRAFT-seams-on-standard-protocols.md` governs, and this estate is an
unusual case of it: the standard protocols are already in place and predate
this corpus. A change that needs two families is a seam, and it crosses as
MIDI, OSC, timecode, an audio-over-IP transport, or HTTP with a schema. It does
not cross as an import, and it does not cross by merging two repositories into
one. A repository in two families is not a seam between them: it is one thing
read two ways, and what it exchanges with either family's other members still
crosses as a protocol.

The clause is stated because old wiring is invisible: a seam that predates the
corpus is easy not to recognise as a seam.

### §6 — Naming a family adopts nothing

`ci/workspace.yaml` closes with *Presence here is not adoption*, and the same
holds a level up. Placing a repository in a family says what it is part of. It
does not vendor this corpus, does not create a project branch, and does not
bring the repository under governance. Adoption is the procedure in
`handbook/forking-a-project.md`, taken one repository at a time and decided one
repository at a time.

## Consequences

**The roster carries the claim and `uv run qm families` reads it.** A
repository names its families in `ci/workspace.yaml`, as one name or a list,
and the set of families and which sits within which are read out of §3 of this
record rather than copied into the tool -- so renaming a family here is a
roster claim that stops resolving, which is the failure that announces itself.
`ci/families.py --check` refuses a claim naming a family this record does not
declare, naming one family twice, or naming a family beside one it sits
within, and it refuses a `within` that names no declared family or circles
back on itself. It reports a repository that claims none as *unstated*, never
as *none*.

**A count of a family includes the families within it.** `families.json` lists
each family's own members and, beside them, everyone in the families within
it. A total over the estate counts a repository once, however many families it
is in.

What no check reaches is §2, and it is the half that matters: whether a
repository really belongs where somebody put it. The border is what the thing
drives, and reading it needs a person who knows what the code does.

**Every border is a way to be in the wrong repository**, where before there
was none, because there was no border to be on the wrong side of. That is the
intended effect, and it is also the new cost: a contributor now has a question
to answer that they did not have.

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

**One performing family with nothing within it.** Cheapest, and it has no
test. A single family spanning an LED controller and a PDF annotator cannot
answer the only question a family exists to answer — does this change belong
here — because everything qualifies. `performing` is kept as the outer family
for what drives a show without driving one of its parts; the families within it
keep the question answerable.

**A repository in exactly one family.** Simpler to count and to draw, and it
forces a choice where both readings are true: the three boards in `irl` would
lose their sound and lighting readings, and a search for them there would find
nothing.

**A `video` family within `performing`, for alfred alone.** A family of one has
nothing to border against. alfred claims `performing` until a second
video-production repository gives an inner family something to hold.

**Group by stack, following `one-house-stack`.** The border would cut through
every family and join parts of each, since the estate is polyglot.
`one-house-stack` also governs what QM writes rather than what belongs with
what, so this would be reusing a principle to answer a question it does not
address.

**Make it a lane.** The lanes in `ci/lane-registry.yaml` are kinds of
*governance work* — meta governance, the development loop, documentation. A
repository family is not a kind of governance work, and folding it in would make
`uv run qm lanes` answer two unrelated questions in one table.

**Infer the families from dependencies or topics.** Rejected by §1, and it would
not work anyway: where two members connect over MIDI or OSC at run time, a
dependency graph cannot see the connection at all. It would report the estate as
a set of unrelated repositories and be confidently wrong.

## Revision triggers

- A repository whose claims keep growing. Each claim passes §2 on its own, but
  the pattern is the shape of a seam wearing a single repository, or of
  substrate claimed by everything built on it.
- A second video-production repository. An inner `video` family within
  `performing` then has a border to hold.
- A second private member, or the existing one becoming public. Either changes
  where the estate's membership can be written down.
- A family's hub going cold while its periphery keeps moving. That is the shape
  of a fork the organisation has not decided to take.

## Amendments

*(none)*
