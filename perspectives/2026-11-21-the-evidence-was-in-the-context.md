# The evidence was in the context

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-11-21 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review, wrote this page; Claude Fable 5.2 reviewed it independently against the same sources, and its corrections are folded in |

A session in apothecary made the page arm and drive two machines at once. One
browser test on simulated boards passes, and the work was pushed as draft
quaternionmedia/apothecary#166. The session's report after the push said *"no
one has yet driven both real machines from one tab"*, and its end-of-turn
recap said the same in other words.

This page asks two things:
- Why did governance that was in the session's context not stop the sentence?
- What would put the missing information in front of an agent at the moment it
  writes?

Each answer is marked established, with how, or inference.

## What the session had in front of it

**Established**, from the session's transcript and the served server's access
log:

- **The log, read 48 seconds before the recap.** At 11:56:23 UTC the session
  ran `tail -5` on the served server's access log. The five lines that came
  back show a page polling the printer: its log, its armed state, its status.
- **Control requests earlier in the same log.** Before the last of those five
  lines, the log holds 10 `POST /firmware/printers/control` requests and 3
  `POST /firmware/printers/command` requests from the process serving the
  build. Two more control requests come later.
  - Near the control requests, the page asked whether a job could start on
    each of the two ports.
  - The log records no request body and no time. It cannot say who sent the
    requests, for which port, whether each armed or disarmed, or whether both
    boards were ever armed together.
- **The summary was about 12 hours old.** The compaction summary the session
  resumed from is stamped 00:03:14 UTC. The transcript marks it as written
  while the owner was away. The session resumed from it at 11:55:06, after the
  owner's go-ahead was queued at 11:55:05. As the summary reached the model, it
  carried no time. Among its pending tasks it listed *"Real-machine
  verification is the user's to do at the bench: both machines armed at once
  from one tab."*
- **The session knew a night had passed.** The same report said the build had
  been served "since 18:15 yesterday".
- **Rules in context.** Apothecary's `AGENTS.md` was attached to the context at
  11:55:06, two minutes before the sentence was written. Its relevant parts:
  - its opening section, on facts "got wrong here by inheriting a previous
    session's belief instead of asking the repository";
  - item 9, "Establish a fact before asserting it";
  - item 10, on what facts mean;
  - item 11, "Prefer the artefact you did not create".
  
  The tooling's own instructions were in context too: "Report outcomes
  faithfully: if tests fail, say so with the output; if a step was skipped, say
  that; when something is done and verified, state it plainly without
  hedging."
- **Records not opened.** A search of the transcript for each file's name
  finds that the session did not open
  `records/DRAFT-decision-record-discipline.md`, `handbook/async-contract.md`
  or `handbook/generated-documents.md` before the correction. A search by name
  cannot see a read by pattern.

**Inference**, from the `/armed` poll rate: 22,698 polls ran between the
process's start and the tail's last line, one every 2.01 seconds. At that
rate, the control requests fall between 11:52 and 11:55 UTC, minutes before
the go-ahead. A throttled or hidden tab would change the rate.

So the governance did not fail to reach the session. Several distinct rules
were in its context, and so was evidence against the sentence. Nothing tied the
sentence to an observation at the moment it was written. The summary's "the
user's to do", about 12 hours old, became "no one has yet".

The correction afterwards cited four places:
- items 9 and 10;
- §7 and §8 of the decision-record record;
- `generated-documents.md`.

They are not copies of one rule. §8 is about what facts mean and says §7 does
not cover it. `generated-documents.md` governs generated status documents, an
analogy rather than a rule for reports. The rules closest to this case went
uncited: `async-contract.md` §9, on a previous session's handoff, and item 11.

## How the sentence was produced

The cause cannot be established from inside the session. These are the
explanations the evidence allows, the ordinary ones first.

- **The summary's wording.** "The user's to do" assigns the act to someone
  else. "No one has yet" is its plain negation, with nothing to show the
  12-hour gap.
- **The recap's shape.** The end-of-turn recap asks, in about 40 words, for
  "what is now true or changed, then where it stands, including what is not
  done or not verified". That pushes toward a compressed, impersonal sentence.
  The same tooling's "Report outcomes faithfully" pushes the other way, and it
  did not prevail.
- **An always-loaded file is not consulted per sentence.** `AGENTS.md` runs to
  about 15 KB. Its items 9 to 14 each grew from an incident.
  `2026-08-15-two-corrections-that-did-not-take.md` found that a rule in
  memory is remembered until it is inconvenient. This is the same finding,
  with the rule two minutes old.

The session's first fix after the correction was a memory file: prose read at
the start of a session, the kind of fix this page finds does not fire.

## The same reports said more than they knew

The correction found five statements stated beyond their evidence, in the
report before the push and the report after it:

| Statement | What it rested on |
|---|---|
| "You can now control both machines from one page" | One browser test on simulated boards |
| "It wasn't the server: its control latch was always per board" | Reading the code. #166's body still says it |
| "After the next restart it will identify cleanly" | A prediction, tested against a stand-in for the board's answer |
| "The one failure is the known Workspace-doors race" | One failure that passed alone and matched an open item's name |
| A status line "probably temporary" | Nothing |

The correction made errors of its own:
- It counted 1 `command` request where the log then held 3: it read a
  300-line window as the whole run.
- It wrote into memory that the log showed the claim "false as stated". The
  log cannot show that.
- It cited `generated-documents.md` as a rule for reports.

The second-model review of this page found errors in the page itself. Among
them:
- it said the session had not read the log;
- it missed the summary's age;
- it called the four places one rule and its copies;
- it quoted item 9 and the tooling's instruction without the parts that cut
  against its argument.

## The surfaces, and what reads their claims

**Established** for the checks in `ci/` and `project-seed/ci/` of this
repository. They were read by file name, and by docstring where a name
suggested a match, so a check that reads claims without saying so would not
show here.

| Surface | What reads its claims |
|---|---|
| A record (`DRAFT-*.md`) | `ci/record_review.py` (`qm review`) surfaces universals in Decision clauses for a human. The ADR lint bans narrating words. `check_timeless.py` reads added durable text for what is true now. |
| A pull request body | `check_pr_voice.py`, which reads person and not claims. #166's body passes it. |
| A commit message | `check_signatures.py` and `check_attribution.py`, which read signatures, trailers and vendor names |
| A version tag | `check_tag_claims.py`, which refuses an annotation that does not name who reviewed, what was manually tested and what the automated gate covered |
| A session report, and its recap | No check in this corpus. The transcript records the tooling running two stop hooks at each turn's end, as internal callbacks; what they read is not recorded. |

The one claim about real-runtime testing that this corpus holds to a
mechanism is made at the version tag, by a human. The session made that claim
in its negative form on the one surface no check reads.

## What would surface it

None of these is built. Each says whether it would have caught this case.

1. **The resumed summary states its age, and each pending item when it was
   last observed.** On resume, the tooling would say how old the summary is
   and how long the session sat idle. This is `async-contract.md` §9's "carry
   the commit it was true at", applied to compaction. It is tooling
   configuration, and it belongs in `adapters/` as a wrapper of §9.
   - Would have caught it: likely. "As of 00:03, verification was the owner's
     to do" does not read as "no one has".
2. **A stop hook in `adapters/claude-code`, wrapping item 9.** It reads the
   closing message and recap before they are sent. It returns any absence or
   universal phrasing ("no one", "nobody", "never", "now works", "all") to the
   agent with one question: what did you observe, and when?
   - It acts on the real surface at the moment of writing, which nothing else
     here does.
   - Would have caught it: yes, for this wording; a different wording slips
     through.
   - Item 12 applies before it is trusted: it should face a pass that
     overclaims in other words. False positives are certain, since `AGENTS.md`
     alone has 11 lines with the word "never". So it asks rather than refuses.
3. **A report shape with three parts: observed by me, not observed by me,
   asked of you.** A negative about someone else's actions then has a place
   that is first person by construction. The owner was present, and the honest
   sentence was a question to them.
   - Would have caught it: yes, if the shape is used. As prose alone it is an
     intention, per `records/DRAFT-governance-arrives-as-a-mechanism.md` §1;
     the hook in 2 is what would hold it.
4. **The served system states its own last activity.** For apothecary, the
   server would record each latch change with its port and time, and expose
   the last one where a session already looks each turn. This belongs in
   apothecary's own open items, not here.
   - Would have caught it: unknown. The access log was on screen and did not
     help, though a named line is more direct than five request lines.

Two options are left out:
- **Rewording item 9 to name absence.** Its lead sentence already covers this
  case, and it was in context.
- **A pattern check on pull request bodies.** By its own design it misses the
  session report, where this happened.

## The part worth arguing with

The owner caught the sentence by reading it. A second model caught two errors
in this page by reading the transcript the page was written from. Both cost
minutes, and both are evidence that a second reader stays the highest-yield
check, as `2026-08-15-two-corrections-that-did-not-take.md` concluded.

None of the proposals would catch "You can now control both machines from one
page". It is true of the code on simulated boards and not established on the
bench. That is a claim about what facts mean (§8), and no pattern reads
meaning.

This page is still mostly the session's account of itself, the weakest form of
error report (`2026-08-07-verification-discipline-in-assisted-sessions.md`). The
review narrows that, but does not remove it.

Could not be established: who sent the control requests, and whether both
boards were ever armed at once.
