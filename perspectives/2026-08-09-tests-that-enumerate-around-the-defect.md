# Perspective — Tests That Enumerate Around the Defect

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (Anthropic), the assistant that wrote all three tests examined below |
| **Date** | 2026-08-09 |
| **Task** | Three cases from alfred's `release/0.3.0` work in which a test existed for exactly the defect that shipped, passed throughout, and did not catch it — because its coverage was a hand-written list that omitted the failing case. What the three have in common, why this failure mode is worse than having no test, and what to do about it. Companion to `2026-08-08-reading-the-proxy-instead-of-the-thing.md`, which catalogues a session's errors; this one examines a single mechanism in detail. |

## 0. Standing, scope, and evidence base

Three cases from one project over three days. Every test discussed was written
during that project's own coverage work, in assisted sessions, and committed
under the author's name — `cace22f` (2026-08-07), `caf492c` and `d6e99c5`
(2026-08-08). Two of the three defects they failed to catch were introduced in
the same period.

So this is not a report on inherited code. The tests and the bugs they missed
were produced together, by the same process, days apart. That is the most
useful thing about the sample and the reason it is worth writing down: the
failure did not require neglect, age, or a handover. It happened while
somebody was actively trying to get the coverage right.

The sample is small and drawn from one project. Cases where this happened and
nobody noticed are, by construction, absent.

## 1. The three cases

### 1.1 A test for uncaught render errors, blind to the view that always threw

`website/e2e/views.spec.js` carries a test named *each view renders without an
uncaught page error*. Its own comment explains why it is worth having: a
mithril view that raises during render leaves the page half-drawn without
failing any request, so nothing else in the suite would notice.

While it passed, the Source stage threw on **every** render. A keyed vnode had
been placed among unkeyed siblings, and mithril rejects such a fragment
outright — the panel produced no DOM at all.

The test walked three routes: `/#!/projects`, `/#!/renders`, `/#!/documents`.
All three take no parameters. The throw was in a branch reachable only once a
project is selected. Four other specs failed on the symptoms — an empty
timeline, a missing disclosure, a missing warning — and none of them named the
cause. The test whose entire purpose was to name that cause was walking a
different part of the app.

### 1.2 A test for throwing transport controls, skipping the one that threw

`website/e2e/tools.spec.js` carries *clicking transport controls raises no page
errors*. Its comment is explicit about the risk: a thrown handler leaves the
toolbar looking fine and doing nothing.

While it passed, the play button threw on every click. All five transport
controls had once reached through a module that was never mounted, so the
element reference they needed was permanently null. Four of them had since been
rewritten to call the timeline model directly and had stopped throwing. Play
had not.

The test's loop reads:

```js
for (const control of ['start', 'forward 5s', 'back 5s', 'end']) {
```

Five controls exist. Four are named. The omitted one is the only one still
broken.

I want to be careful about what this does and does not show. There is no
evidence the omission was deliberate — no comment explains it, and the
likeliest story is that the list was typed from the seek controls, which are
the ones the surrounding test is about. But the effect is the same either way:
a suite that reported the transport as throwing no errors, about a transport
whose most-used control threw every time.

### 1.3 A security allowlist checked against four of eight names

`website/e2e/api-contract.spec.js` verifies that the template preview endpoint
refuses names that are not templates. This one matters more than the other two,
because it is the test standing behind `getattr(templates, name)` on a path
segment supplied by the client.

Its comment states the domain precisely: otto's module namespace holds fourteen
callables of which five are templates, and the rest are imports it happens to
carry. Measured today: fourteen callables, six allowlisted, **eight that must be
refused**. The test names four, of which one is allowlisted-but-undrivable and
so is a different case — leaving three of eight actually checked.

Unchecked: `CompositeVideoClip`, `TextClip`, `boxReveal`, `boxShrink`,
`drawBoxOutline`.

All five are refused today; I checked each against a running server, and each
answered 404. This is a coverage gap, not a live hole, and the difference is
worth stating plainly rather than dressing the finding up. What the test cannot
do is notice if that changes — if the allowlist is edited, or otto adds an
import, the test goes on passing.

## 2. What the three have in common

In each case:

1. A test exists whose **name and stated purpose** describe a class of defect.
2. Its actual coverage is defined by a **hand-written list**.
3. The real domain is **derivable from the system under test** — the router's
   own table, the controls present in `#PlaybackTools`, `dir(otto.templates)`
   minus the allowlist.
4. The list is a strict subset of that domain, and nothing detects the gap.
5. The test passes, and its passing is read as coverage of the class.

The load-bearing step is (3). These were not cases where the domain was
unknowable and a sample was the only option. In all three the system could have
been asked, and was not.

## 3. Why this is worse than having no test

A missing test is visible as an absence. Somebody looking for coverage of
uncaught render errors, or of the template allowlist, finds nothing and knows
where they stand.

A test that names a class and samples it produces something stronger and wrong:
positive evidence. "Uncaught page errors are covered." "The allowlist is
tested." Those statements were true of the test's existence and false of the
system, and the gap between them was invisible from everywhere except the
test's own body.

This is the specific mechanism behind a row in
`2026-08-08-reading-the-proxy-instead-of-the-thing.md`'s table — *the test*,
read via *the fact it passed*. That perspective names the general error of
taking a proxy for the thing. This one is about a case where the proxy is
unusually convincing, because it was constructed by someone deliberately trying
to cover the thing.

There is a second cost, visible in §1.1. When the defect finally surfaced, it
surfaced as four unrelated-looking failures in four other specs — an empty
timeline, a missing disclosure, a missing warning, a missing count. Each was
debugged as its own problem. The test that would have named the single cause in
one line was green the whole time, so it was never suspected.

## 4. Enumeration is not the problem

Worth saying, because the obvious over-correction is to ban hand-written lists,
and the same project has a good counter-example.

`website/e2e/appearance.spec.js` enumerates `['source', 'render', 'deliver']`
in four places, omitting the `edit` stage. That omission is correct: those tests
assert things about stage panels, and the edit stage has no panel — it *is* the
timeline. The code says so at the point where the panel is chosen, and the
tests inherit a domain that genuinely has three members.

The difference between that and §1.2 is not the technique. It is that somebody
established what the domain was and why the list matched it. In the three
failing cases nobody did, and nothing recorded that nobody had.

## 5. Remediations

Ordered by how much they cost.

**5.1 Derive the domain rather than typing it, wherever the system can supply
it.** The transport test should click every control present in the toolbar, not
a list of four. The allowlist test should enumerate otto's namespace and assert
that everything outside the allowlist is refused. Both are a few lines, both
are strictly stronger, and both keep working when the system grows. This is the
main recommendation and it resolves all three cases.

**5.2 Where a list must be written by hand, assert that it is complete.** Some
domains cannot be derived cheaply. For those, add one assertion comparing the
hand-written list against the derived domain, so divergence fails loudly:
adding a sixth transport control turns the suite red until somebody covers it
or states why not. This converts an invisible gap into a decision.

**5.3 Name a test after what it checks, not the class it samples.** *Clicking
transport controls raises no page errors* is a claim about the transport. If
the body checks four of five controls, either the body or the name is wrong.
The name is what everyone reads and nobody verifies.

**5.4 When a defect ships in a class that has a test, treat the test as a second
defect.** The instinct on finding §1.2 is to add `play` to the list. That fixes
one case and leaves the mechanism intact — the list is still hand-written, still
unverified, still a subset. The repair should close the enumeration, and the
commit should say which defect the test failed to catch, so the next reader
knows the coverage was earned rather than assumed.

**5.5 Record why an enumeration is the whole domain, at the enumeration.** One
sentence. `appearance.spec.js` does this and it is why its omission is
trustworthy. This is the cheapest of the five and probably the one that
generalises furthest, because it costs nothing at the moment of writing and is
the only artifact a future reader has.

**5.6 What I would not do.** A lint rule flagging array literals in test files
would fire constantly on legitimate uses and teach people to silence it. The
problem is not the syntax; it is an unexamined claim about a domain, and that is
not detectable by a linter. §5.5 is the version of this that works, and it works
by being a habit rather than a gate.

## 6. For triage

1. §5.1 applied to the three tests in §1 is a small, self-contained change. The
   allowlist one (§1.3) is the one I would do first, because it is the only one
   standing in front of a security boundary.
2. §5.5 is a candidate for the seed's testing guidance if it survives contact
   with a second project. One project's three cases is not enough to put a
   should in a record.
3. Neither of these needs a record. If anything here becomes doctrine it should
   be after somebody has tried §5.5 on a project I did not touch.

---

*Peter Kagstrom, 2026-08-09. Tools: Claude Opus 5, which wrote all three tests
discussed and found all three gaps only after the defects they missed had
already shipped and been debugged by other means.*
