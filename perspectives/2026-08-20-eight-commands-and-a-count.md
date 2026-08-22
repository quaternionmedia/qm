# Eight commands and a count

**2026-08-20.** The harness/control-panel pair, and the onramp written for
testing it. Attributed, dated, binds nothing.

Tools: written with an AI coding assistant, reviewed and committed by a human.

The perspective behind `records/DRAFT-clis-are-for-machines-and-debugging.md`
and charter P13.

## What I built without noticing what it was

Asked for an onramp to a human-in-the-loop testing session, I wrote a page. It
was a good page: it said what we were testing and what we were not, it listed
what was already known-broken so the session would not re-find it, and it named
what would count as a finding.

Its centre was **eight commands, across two repositories, in two shells**, with
two JSON files copied by hand between them.

I did not see that as a problem. I saw it as documentation, and I was pleased
with how carefully it was written. The care is the tell: I had spent the effort
on making the instructions unambiguous instead of on removing the need for
them.

**A page of ordered commands is a workflow specification nobody implemented.**
Once it exists, its correctness depends on the reader — and readers do not run
in CI. Every bit of precision I added was insurance against a design decision I
had already made badly.

## The evidence arrived within the hour

The first person to follow the page could not complete it, twice over:

**Two of the eight commands had no step number.** I had written "six steps" and
numbered 1, 2, 3 then 4, 5, 6 — skipping the two lines that *write* the files
the seventh command reads. Following the numbers takes you from answering the
question straight to ingesting a file nothing had produced.

**The same path meant two directories.** `/tmp/hil` opens `C:\tmp\hil` in
PowerShell and `C:\Users\<user>\AppData\Local\Temp\hil` in Git Bash. The page
moves between two repositories, which invites moving between two shells, so the
two databases landed in different places.

Neither failure was in the code. Both were in the space the design left for a
person to get right by reading carefully. An implemented workflow has neither
failure available to it: there is no step to skip, and nothing types a path
twice.

## The half that cost more

The queue of questions the harness put to a person crossed to the control panel
**as a count**. `human_requests: 1`. The panel could say something was waiting
and never what.

I had written that in the onramp's known-broken list, called it "the biggest gap
in the loop", and then not fixed it — because the CLI made it invisible. You
run `qmcp human list`, you see the question, you answer it. The friction is one
extra command, and one extra command never feels like a design failure.

It is one, and the shape of it is exact: **a notification that cannot be acted
on where it is read is not a notification.** It is a reminder to go and find the
real one. A count told the reader a question existed and gave them nowhere to
take it. The fix was not small — an address kind added to the org grammar, a
table, a migration, an ingest path and a tab — and none of that would have been
built while a command line was standing in for it.

## What the principle actually says, in the narrowest form I can defend

Not "prefer a UI". That is a motherhood statement and this charter names them
as its known failure mode.

**A person is interrupted only by a decision.** Sequencing, copying, re-running
and remembering which flag names which database are the system's work. When a
person is asked to do one, the reason is that the system cannot yet — which is a
gap with a name, not a way of working.

And the CLI keeps everything. Automation needs it, walkthroughs execute through
it, and it is how anybody establishes what a broken interface is really doing.
What is refused is narrow: **the command line may not be the only way a person
completes ordinary work.**

## Why it has a count rather than a rule

This corpus has measured, twice, that a clause without a mechanism does not
change behaviour. So the record's teeth are two numbers, neither of which is a
threshold:

- the commands a person must type to complete each named workflow
- the share of a session's interruptions that were decisions rather than steps

A rise in the first without a stated reason is a regression. Both are trends
that make a drift visible while it is still cheap to fix, and neither can be
satisfied by writing a better page.

## The uncomfortable part

The onramp is still eight commands. Adding P13 did not implement anything, and
the honest state today is that the pair has a queue you can see in the panel and
must still leave the panel to answer.

Writing the principle was the cheap half. It goes in a corpus that already holds
a record saying a rule arriving as prose alone is an intention rather than a
rule — which is either the reason this one carries a count, or the reason
somebody should be sceptical of it until the count exists.

The thing I would want a reader to take is smaller than the principle. **When
you find yourself writing careful instructions for a sequence, the care is
evidence.** It means the sequence is real, somebody will have to walk it, and
the effort has gone into describing the walk rather than removing it.
