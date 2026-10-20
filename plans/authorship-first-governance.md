# Plan — Governance prose that invites a second author

**Status: stub. The rewrite below is one attempt, not the standard.**

## What this is for

`plans/governance-prose-signals.md` measures the problem. This one is about the
alternative, and it is harder: nobody has shown what governance prose that
invites authorship actually looks like when it still has to bind.

## One attempt, at item 3's opening

Offered so there is something concrete to disagree with.

**As it stands:**

> Everything you produce arrives as a pull request, and the pull request is an
> audit record rather than a request for anyone's attention. [...] Never push
> `main` directly, however small, mechanical, or obviously correct the change
> looks.

**One alternative:**

> Everything you produce arrives as a pull request.
>
> The pull request is an audit record — the gates run, and the diff stays
> readable afterwards. It is not a request for anyone's attention.
>
> **Why not push `main` directly for a typo?** Because the push is the one act
> that destroys the record, and nothing downstream can reconstruct it. The cost
> is one command; the loss is permanent.
>
> **Unsettled:** whether a typo fix should genuinely cost a pull request. Nobody
> has argued this, and the rule currently makes no exception.

The differences: it breaks, it asks, it answers the reader's actual objection
rather than pre-empting it, and it marks one thing as open.

**It is also longer**, which runs against the 700-line reading budget. That
tension is real and unresolved.

## Candidate patterns

- **A question the reader would actually ask**, answered — instead of an
  absolute that pre-empts it
- **An `Unsettled:` marker**, so a reader can see where their contribution goes
- **One idea per block**
- **The cost stated**, rather than the prohibition repeated
- **A named alternative that was rejected**, so the decision is arguable

## Decisions nobody has made

1. Does this survive being applied to all 626 lines of mandatory reading, or
   does it double them?
2. Is `Unsettled:` a real mechanism or decoration? What drains it?
3. Who arbitrates when the rewrite changes meaning? A voice change that alters a
   rule is a governance change wearing an editorial hat.
4. Should this be a record, or stay a practice?

## What would make this plan wrong

The rewrite reads better and produces the same compliance, at twice the length.
Then it is a preference, and the budget should win.
