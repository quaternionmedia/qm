# Teeth, and What the Mutations Said

| | |
|---|---|
| **Date** | 2026-08-14 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | An assistant, which wrote both checks and mis-aimed three of the mutations described here |

---

## The gap

`records/DRAFT-version-tags-are-claims.md` was written on 2026-08-08 and §7 says
its §1 is *"mechanical rather than customary."* On 2026-08-14 it was customary:

```
gh api repos/quaternionmedia/{qm,dossier,qmcp}/rulesets        → []  (all three)
gh api repos/quaternionmedia/{qm,dossier,qmcp}/tags/protection → 404 (all three)
```

Nothing read a tag. Two lightweight tags exist in the org — `alfred@v0.2.0` and
`datum@v0.0.1` — asserting exactly what §6 says a lightweight tag cannot.

Under the corrected two-gate model, the tag is the *only* human gate. So the
ceremony was entirely on the pull request, which is not a gate, and entirely
absent from the tag, which is.

## What was built

`project-seed/ci/check_tag_claims.py`, with three modes: one tag, every `v*`
tag, and a captured test run. It refuses a lightweight tag, a name that is not
`vMAJOR.MINOR.PATCH[-prerelease]`, and an annotation missing any of
`Reviewed-by`, `Manually-tested`, `Automated-gate`, `Not-covered`. The
`--test-output` mode refuses a run reporting a skip, rerun, retry, xfail or
error, per §3.

Its docstring spends more lines on what it cannot do than on what it does. It
cannot tell whether the review happened, whether the manual test happened, or
whether a silent suite is deterministic. A green result means the tag is *shaped
like a claim*. Whether the claim is true is a human's word, written down against
a name where a reader can hold them to it — which is what §6 asks for and all it
asks for.

`ci/check_restatements.py` is the other one, and its story is in
`2026-08-14-precedence-lost-to-readership.md`.

## The mutations, which are the point of writing this down

`AGENTS.md` item 13: a guard is not finished until someone has tried to route
around it. Both checks were mutation-tested — the tool broken in the way each
test names, the test suite run, the result required to be red.

The tag gate: **7 mutations, 7 caught**, baseline green before and after.

The route-around worth naming is the third one. `git tag -l --format=%(contents)`
on a *lightweight* tag returns the tagged commit's message. So a commit message
containing all four required fields, plus `git tag v0.2.0`, satisfies every field
check while creating no tag object to carry them. The test builds exactly that
and asserts the check still fails. It does, because the object type is
established before the body is trusted — but only because the test asked.

The restatement check: **9 mutations, 9 caught**, after three that reported false.

## Three mutations that lied, and what each turned out to be

The first run reported three inert tests. All three were wrong, in three
different ways, and the diagnosis is more useful than the result.

**One: the mutation was a no-op.** Changing `FIELD_LINE.match` to `.search` on a
pattern anchored with `^` changes nothing — `^` and `match` are redundant
anchors, and removing either alone leaves the guard standing. The test was fine.
The mutation had to remove both to be a mutation at all. It then went red.

**Two: the guard was dead code.** `EXCLUDED_PREFIXES` listed `perspectives/`,
and removing it changed nothing, because perspectives were never collected in
the first place — the entry-point set is a whitelist. A filter that can never
fire, sitting next to a whitelist, reading as protection. It was deleted and the
reasoning moved into a comment on the whitelist.

**Three: the test was genuinely weak.** A handbook page missing its citation can
fail two different ways, and both messages name the file. Asserting the filename
passed whether handbook pages were collected or not — the test would have
survived the glob being deleted, which is the case it exists to catch. It now
asserts the specific failure and denies the other.

And a fourth, found while fixing the first: `RECORD_MENTION` had an optional
`(?:governance/qm/)?` group that did nothing, because the pattern is unanchored
and the long path contains the short one. Three redundant mechanisms for one
behaviour, two of them dead. The behaviour is real and no single mutation can
break it, which is a property of the tool rather than a weakness in the test —
so that test carries a docstring saying so, instead of a mutation that would
report false forever.

## What that adds up to

A mutation returning green is not evidence the test is inert. It is one of four
things: the test is inert, the mutation was a no-op, the code being mutated was
already dead, or the behaviour is over-determined and has no single site to
break. Three of the four were present here, in one afternoon, in two files.

This is the same shape as `AGENTS.md` item 10 — check a signal before reading
it — arriving one level up. The mutation harness is a tool that answers a
question, and *its* unexpected result deserves the same "name one other thing
that would produce this" before anyone acts on it. Acting on the first reading
would have meant rewriting three correct tests.

## What is still customary

Tag *creation* is not gated. §7 asks for a host-side tag-protection ruleset
restricting who may create `v*`, and a workflow cannot substitute for one —
`tag-claims.yml` runs after the tag exists. Applying that ruleset is an
access-control change to live repositories and is the owner's to make.

Until it is applied, the check catches a badly-formed tag after the fact and
nothing stops one being cut.
