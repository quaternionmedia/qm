# The Exit Code Was Green

| | |
|---|---|
| **Date** | 2026-08-15 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | An assistant, which wrote every check described here and was caught by three of them |

---

## The shape of the day

Documentation landed on `main`, along with a rebuild-and-accuracy audit, a draft
publish path, and one deliberate exemption. Four pull requests merged and every
gate is green.

The interesting part is not any of that. It is that **almost nothing here was
found by an exit code.** Each of the day's real findings came from reading an
output that had already reported success.

## Four findings, none of them a failure

**A workflow that could not do what it claimed.** The signature check ran on CI
and failed. The obvious reading was a bug. The actual cause was that verifying a
signature needs the signer's public key and a runner has none — so
`git log --format=%G?` there reported on the runner's empty keyring, not on the
commits. Every value it produced was true about the wrong subject. The forge had
already verified all of them server-side. **The check was measuring its own
scaffolding**, which this corpus has recorded as a failure mode four times and
still produced a fifth.

**A config only one parser accepts.** `zensical.toml` had eight multi-line
inline tables, which TOML forbids. The site generator's own reader accepted them,
so the build was green and had been for weeks. `tomllib` rejected line 117. A
configuration that parses in exactly one program is a rebuild that works until
that program changes, and nothing about the green build said so.

**A tool that lied in its success path.** The signature check printed *"All 16
commit(s) carry a signature"* when nine did not. Exit zero, correct verdict,
false sentence. It was written by the session that had spent two days on the
premise that a check reporting success while enforcing nothing is the defect
this corpus exists to prevent.

**A banner that asserted something untrue.** The draft-docs mechanism was
verified end to end: the run succeeded, 24 of 24 pages carried the banner, none
were missed, the position was right. Reading the rendered text found it saying
*"Built from an unmerged branch"* — false, because the run that produced it had
been dispatched from `main`. Every step green; one sentence wrong.

## What the four have in common

None would have been caught by a stricter check, a longer test suite, or more
care in the moment. Each was a case where **the machine-readable result was
correct and the human-readable result was not**, and the only instrument that
separates those is somebody reading the output.

That is uncomfortable for a governance programme whose stated direction is to
convert judgement into mechanism. The conversion works: the ten gates now
running have caught real things, and the declared-and-not-built count reached
zero today. But the conversion has a floor, and the floor is that a check
verifies a proposition somebody chose, in words somebody wrote, and neither the
choosing nor the writing is checkable by the same means.

## The exemption, as a case in point

One commit subject names a model. It predates the rule, it belongs to another
contributor, and rewriting history is forbidden here — so the options were to
weaken the rule, rewrite someone's commits, or exempt the instance.

It is exempt, by full SHA, with the reason printed on every run and recorded in
the gate registry under what `adr-lint` cannot see. The reason it is kept rather
than quietly grandfathered: a rule illustrated by a live instance in its own
tree is harder to dismiss than one illustrated by a hypothetical.

The argument against is written into the file beside the list. `check_signatures.py`
had deliberately chosen a *date* over a SHA list, on the grounds that a list of
blessed SHAs grows quietly and nobody can tell later which entries were
deliberate. That objection is not answered by asserting good intentions; it is
answered by every entry carrying its reason, the run printing them, and a test
asserting there is exactly one. Whether that is enough is a judgement, and it is
recorded as a judgement rather than as a solution.

## What this suggests about the next stretch

The remaining work is the part no instrument reaches. Sixteen records have never
been read as one body. Ratification has never been performed. The tag — the only
human gate on anything this org ships — has no host-side enforcement at all.

Each of those is a reading or a decision, and the day's evidence is that the
readings are where the findings are. The mechanisms built over two days are
worth having and they did their job; they also produced, between them, four
green results that were wrong in ways only a reader could see.

The honest summary is that the checks raised the floor and did not raise the
ceiling. Somebody still has to look.
