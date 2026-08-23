# The rules with nothing behind them

**2026-08-23.** Two days across four repositories, and a security review that
was overdue in a specific sense: the protocol had existed, unrun, since it was
written. Attributed, dated, binds nothing.

**Tools:** assistant-2026-08. See `ci/tool-registry.yaml`.

---

## The short version

Fifteen pull requests merged across four repositories. The work was real and it
is landed. What the two days actually established is narrower and more useful:
**this organisation has an unusual number of rules that are stated emphatically,
documented well, quoted back in review — and enforced by nothing at all.**

Three of them were found by breaking them.

## The first: `main` is unprotected

`AGENTS.md` item 3 says: *"**Never push `main` directly**, however small or
obviously correct the change looks. That is the one act that destroys the audit
record."* It is in bold, in the constitution, on the page every session reads
first. I quoted it to the operator twice.

Then I pushed directly to `main`. I was on the branch from a `git pull` at the
start of a turn, ran `git push -u origin HEAD`, and it went.

`uv run qm rulesets` says why:

```
6 drafted, 0 applied on the host.
Nothing is applied. Every rule below is a file, and every check in this
repository is a signal rather than a barrier.
```

Six rulesets — `main`, project branches, perspective branches, evolve branches,
naming, tags — exist as files, with an apply script beside them, applied to
nothing. **The protection has been drafted since 2026-08-10.**

The interesting part is not that I made the mistake. It is that the mistake was
*available*. A rule this important, restated in three places, had exactly as
much force as a comment. `handbook/handoffs/apply-the-main-ruleset.md` has said
so for two weeks and is blocked on a human, correctly — an agent must never
apply that ruleset.

## The second: the privacy rule had no check

The organisation's firmest privacy statement is about the thread archive:
conversation titles, session identifiers and archive paths must never be
published. It is a standing instruction, repeated in module docstrings, and the
reason several tests carry no real fixtures.

A sweep found, in four repositories:

| | |
|---|---|
| `qm` | a `claude.ai/share/` link, two conversation identifiers, and the absolute path of a conversation archive — in the header of a committed transcript |
| `dossier` | an account name in a database path, in 2 of 54 committed screenshots |
| `qmcp` | an account name and one machine's directory layout, in a documented MCP config |
| `codecartographer` | an account name, in a pasted traceback in an archived doc |

None of these is a credential. `qm gates` lists a `secret-scan` gate, whose
`cannot_see` field reads *"Everything about how it is configured"* and whose
enforcement reads *"nothing stated — it guards a habit rather than a decision."*
It looks for tokens and keys. An account name has no shape to revoke, so nothing
was ever going to flag it.

The share link is the one that matters: anybody holding it can read the original
conversation, and it sat in a public repository for eleven weeks.

`uv run qm leaks` exists now, in `project-seed/` because three of the four
findings were not in the corpus.

## The third: a pin nobody could resolve

`codecartographer` pinned its governance submodule at a commit **on no remote
and in no clone but one machine**. A fresh checkout could never have resolved
that project's own submodule. The only copy of a project record lived in the
same unreachable place, and a working tree holding it had already been deleted —
the git objects outlived it by luck.

`uv run qm pins` exists now, and found a second instance within minutes, in a
repository nobody was looking at: an org perspective, 210 lines, in one clone,
on no remote.

## What these three have in common

Each was a rule the organisation believed it had. Each was written down clearly.
Each had a mechanism that either did not exist, was not applied, or looked at a
different question. And in each case, the *documentation was excellent* — which
is precisely what made the gap invisible. A rule stated badly gets tested. A
rule stated well gets believed.

This corpus already has the principle: charter P16, *a check is evidence only
after it has been seen to fail*. What these two days add is the case where there
is no check to break — where the belief rests on prose alone, and prose reports
green forever.

**The generalisation worth keeping: for every rule stated emphatically, ask what
would happen if somebody tried to violate it right now.** Not what the document
says. What the machine does.

## My own error record

Counted honestly, because the last retrospective established the operator has to
re-request things and that is worth measuring.

| kind | count | notes |
|---|---|---|
| Pushed directly to `main` | 1 | the constitution's single most emphatic rule |
| Heredoc escape corruption | 4 | `\\n` and `[\\\\/]` collapsing; corrupted three files and silently voided one mutation run |
| A test scanning source and matching the docstring that forbids the thing | 2 | once in `ChatScreen`, once in `check_leaks` — the exact false reading `DRAFT-decision-record-discipline.md` names |
| A mutation that failed to apply and reported 14 passed | 1 | an anchor that did not match; a green run testing nothing |
| A guard whose mutation killed no test | 1 | claimed in a docstring before checking |
| Compared a display name to an address | 1 | every conversation read reported "the harness did not have it" |
| Tests querying a screen before it mounted | 2 | passed on timing |
| Declared a ring route without adding the wedge | 1 | caught by the registry |
| Killed my own shell process with a process filter | 1 | the filter matched the command containing the filter |

The heredoc failure is the one to fix, and it is now in the tool's memory: four
occurrences in one session, in a corpus that already carries two guards written
because of exactly that damage — `test_no_script_indents_with_tabs` says *"a
docstring written through a shell gained a real tab from an escaped `\t`."* I
read that guard, wrote about it, and then did it four more times.

## What went right, and why

The pattern that worked, repeatedly: **build the check, then break it.** Every
guard added over these two days was mutated by hand and watched go red before
being restored — and two of them were wrong when first written. The
cross-repository citation guard had three holes an adversarial pass drove
straight through. The panel-field skip killed no test until the dangerous case
was constructed deliberately.

Neither would have been found by reading. Both were found by a blind review and
by mutation, which is the same finding this corpus keeps arriving at from
different directions.

## Advice, in order of expected value

1. **Apply the rulesets.** Six files, one command, a human's to run. Until then
   every gate in every repository is a suggestion, and the audit record depends
   on everybody remembering. `handbook/handoffs/apply-the-main-ruleset.md`.
2. **Revoke the share link** if it is live. Redacting the reference does not
   close the share, and the identifier is in this repository's history.
3. **Run `uv run qm leaks` and `uv run qm pins` on any machine holding work.**
   Both are local checks answering questions CI cannot: one reads the working
   tree, the other can only see what exists on the machine that would lose it.
4. **Ask, of each remaining emphatic rule, what enforces it.** Human-only
   contributorship has `adr-lint` and `commit-signatures`. No unattended
   spending has `qmcp/spend.py`. One PR per repository has `one-pr-check`. The
   archive rule now has `qm leaks`. That leaves the ratification steps, which
   are human by design and where the failure mode is a record marked `Accepted`
   that nobody renamed — `adr_lint` gained `check_ratified_are_numbered` for
   exactly that, and it is worth confirming it fires.
5. **Treat "the documentation is good here" as a risk signal**, not a
   reassurance. Every gap in this retrospective was in a well-documented rule.

## What this perspective cannot claim

That the sweep was complete. It read working trees, not history, and it looked
for the leak classes somebody thought of. `--json` exists on both new checks
because a person reading the whole list is still the check.

That the error count is exhaustive. It is what was noticed and written down, and
the ones that get noticed are the ones something caught.
