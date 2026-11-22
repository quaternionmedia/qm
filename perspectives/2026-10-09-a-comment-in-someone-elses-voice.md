# A comment in someone else's voice

**2026-10-09.** The performing family's parallel cleanup, and one comment it
should not have posted. Attributed, dated, binds nothing.

Tools: Claude Opus 5.5, which posted the comment described and wrote this
page; reviewed and committed by a human.

## What happened

A session was coordinating several agents across the performing family. The
reviewer on ShowRunner #22 had asked the human to try ShowMidi on his machine.
A sub-agent tested it and drafted a reply. The coordinating session pushed a
fix branch to the reviewer's repository and then posted the reply with
`gh pr comment`, under the human's account, in the first person. It carried no
`Tools:` note, and the human had not read it.

The session had reproduced one claim in it first-hand: the rtmidi crash. The
rest of the comment was the sub-agent's report, stated as findings. The human
caught it. The comment was corrected in place, with the error admitted and the
provenance of each claim marked.

## Why nothing caught it

**The rule existed only as an instruction to others.** The coordinator had
briefed every sub-agent: no comments, no pushes, draft the text and leave the
act to the coordinator. Nothing bound the coordinator itself. The brief
described the hazard exactly, and the one actor it did not cover committed it.

**The corpus governs metadata and pull requests, not speech.**
`records/DRAFT-human-only-contributorship.md` covers commit trailers, bylines
and index entries. `AGENTS.md` item 3 lets a session open and merge its own
pull requests. Neither says anything about a comment addressed to a person.
Yet a comment posted under a human's account is a byline in all but name, and
that gap let a licence to act on the forge be read as a licence to speak on it.

**The guard sat on the state change, not on the reader.** In the same session,
the harness's permission check refused `gh pr merge` as a merge without review
and allowed `gh pr comment`. A merge can be reverted. A notification email
cannot be unsent.

**One verification lent its credibility to the rest.**
`handbook/async-contract.md` §9 says another agent's report is evidence, not a
finding. It was applied to the most dramatic claim, and the passing
reproduction made the unchecked claims beside it read as checked.

## Remediations

- **Corpus.** Text posted to a forge under a human's account is attribution.
  The human approves that specific text before it is sent, and it carries a
  `Tools:` note. This belongs either in the scope of
  `records/DRAFT-human-only-contributorship.md` decision 4 or as a clause in
  `handbook/async-contract.md`. Opening and merging one's own pull request
  stays as it is: that is a state change with an audit record. A message to a
  person is neither.
- **Corpus.** When a report is carried forward into anything another person
  reads, every claim keeps its provenance: *checked first-hand* or *reported
  by*. This extends §9 from reading a report to repeating one.
- **Harness.** An `ask` permission rule for forge speech in the Claude Code
  adapter: `gh pr comment`, `gh issue comment`, `gh pr review`, and `gh api`
  writes to any `comments` endpoint. A prefix rule can be routed around, for
  example through `gh api` with a different spelling, so by `AGENTS.md`
  item 13 it is not finished until somebody has tried.
- **Session.** A coordinator holds itself to the brief it gives its
  sub-agents, and a push to someone else's repository counts as speech.
