# What the Checks Were Not Checking

| | |
|---|---|
| **Date** | 2026-08-16 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | assistant-2026-08. See `ci/tool-registry.yaml` |

---

## The shape of the day

One instruction — *surface and remediate the private names one at a time* —
opened a chain in which **every layer, once exercised, turned out not to be
doing what the layer above it assumed.**

| what was believed | what was true |
|---|---|
| Two private names in one committed file | Fifteen occurrences across seven files, four repositories |
| The check that found them was working | It knew 2 private names of 34; every `clean` it had reported meant "the roster's two names are absent" |
| Reading all 34 would fix it | 240 hits, almost none disclosures — one private repository is named after the organisation and matched 187 URLs |
| Tiering by context would fix that | It demoted a real disclosure: a handbook sentence listing repositories has no slash and no quotes |
| Redacting the documents was the end | It broke `governance-status.yaml`'s own verifier, which joins on the project name |
| The gate would stop the next one | It cannot see private repositories from CI at all |
| A gate would gate | **Nothing is required to merge. Ten checks run, none is required, no pull request has ever been reviewed, and the account that opens them merges them.** |

That last row is the finding. Everything above it is a story about one class of
secret; the last one is about the whole corpus.

## Governance written top-down, verified bottom-up

This repository has been built by stating rules and then building mechanisms
under them. That direction is what made every step above possible — the rule
existed, so the gap was findable. It is also what produced the specific failure
mode: **each mechanism was believed to be doing its job because the layer above
it said so, and nothing read the two together.**

`ci/workspace.yaml` named two repositories while `inventory-public.json`
redacted the same two. Both committed. Both correct alone. Nothing read both.
`governance-status.yaml` carried `private_repository_names_listed: false`, which
was true of its census and false of the list beside it. `ci/policy-registry.yaml`
recorded a preventer for `main-is-entered-through-a-pull-request` that had never
been applied — and the rulesets directory has held six drafts and an apply
script since 2026-08-10 against a host reporting zero.

None of these is a lie anyone told. Each is a claim that was true when written
and was never re-read against the thing it described.

## The check is the thing that needs checking

Three defects in one check, in one afternoon, each found by *acting on its
output* rather than by testing it:

1. It read one of two storage shapes. Its own output would have exposed this
   immediately if it had printed **how many names it was checking against** —
   `33 private names checked` versus `2` is not a subtle difference.
2. Making it see more made it useless. 240 findings with no disclosures is not a
   better check than one that fires twice; it is a check nobody runs.
3. Its own test fixtures used four real private repository names, pasted from
   live output. The check caught that — on the branch, before the commit
   reached `main`, on its author.

The third is the encouraging one. The first two are the argument for a rule this
corpus does not yet have: **a check should say what it checked, not only what it
found.** A denominator in the output is worth more than a paragraph in the
docstring.

## What "governed" turned out to mean here

Measured, not asserted:

| | |
|---|---|
| Rulesets applied | 0 |
| `main` protected | no |
| Checks required to merge | 0 of 10 |
| Pull requests ever reviewed | 0 of 8 |
| Distinct humans in the merge path | 0 |
| `CODEOWNERS` active entries | 0 of 56 lines |

The audit record is real: branches, diffs, checks, history, all of it. What does
not exist anywhere in it is an approval step. The corpus reads as though one
were there, and a reader seeing eight green checks would reasonably conclude
they were required.

The response chosen was not to add a human to the merge path — there is only one
person, and one person cannot approve their own pull request. It was to make the
*check list* the human-approved artifact: approved once, then run every time,
with zero approvals and no way to skip. Whether that is enough governance is a
question for ratification, not for a tool.

## The tool's own record, since it is part of the measurement

Four corrections in one session, all the same class, all after the class had
been named:

- Inline scripts to verify behaviour instead of a test or a route — corrected
  three times, including once on a move-file-aside-and-back that would have left
  a gitignored file holding private names moved if the middle command failed.
- Heredoc escaping, eleven occurrences, with the fix identified after the third.
- A private repository name printed into a transcript by inspecting a mapping's
  values instead of its structure.
- Four real private names used as fixtures in the check that forbids them.

The pattern is not carelessness about the rule. Each of these happened *while
working on the rule*. What they share is reaching for the fastest thing that
produces an answer, in a context where the slower thing is also the durable one:
a route rather than a command, a test rather than a script, a structure rather
than a value.

## What this leaves

The lanes exist now (`ci/lane-registry.yaml`) precisely because this session was
one undifferentiated stream — a policy registry, a roster redaction, a workflow
runner fix and a retrospective all in one conversation. The lane is the unit an
interaction can be scoped to, and the boundary that makes two of them separable
is a distinct gate.

The stability criterion says the base is stable when a full pass adds no ledger
entry. Four passes are recorded and the streak is **0**. Today added two entries
and would have added more if the checking had been better. That is the honest
reading: the base is still moving, and the thing moving it most is that the
mechanisms are only now being exercised for the first time.
