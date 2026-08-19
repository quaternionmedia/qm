# A Ring in a Terminal

| | |
|---|---|
| **Date** | 2026-08-18 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | assistant-2026-08. See `ci/tool-registry.yaml` |

---

## What was built

A second implementation of `rad`'s interaction contract, in Textual, inside
dossier: `src/dossier/rad/` — the session state machine, dossier's content for
the durable palette, the colour tokens, and a centered pop-over ring. One
binding (`m`, rad's own documented trigger), 44 tests, and the whole thing
metered to rad's IPA.

Also landed this day, before it: the corpus's protocol registry, curriculum and
address grammar (qm #68, #69); propagation into both project branches (#70,
#71); the version-tag gate inherited by qmcp and dossier; test suites running on
runners in both projects for the first time; alembic and a verified backup
mechanism in qmcp; and the delta entity landed in dossier with its migration
chain reduced from two heads to one.

## The thing worth writing down

**A second implementation is the only honest review of a contract.** Reading
`rad`'s records suggested a terminal ring was a compromise — a reduced version
of a pointer interaction. Implementing it showed the opposite: rad's
accessibility topic states the pointer-free path as foundational, and its
metrics record counts *one keystroke* as one input with its own keyboard budget.
The terminal is not a degraded host. It is a host the contract already
anticipated, and nothing needed inventing.

I had written the opposite into the plan first — that a keystroke count was not
rad's metric and claiming otherwise would corrupt it. That was wrong, and it was
wrong in the expensive direction: had it stood, we would have built a parallel
measure for a problem that did not exist. What corrected it was reading the
record rather than reasoning from the word "radial".

## Six defects, and what each one teaches

**1. `self._context = context` overwrote a framework method.** `MessagePump` —
which every Textual screen inherits — already has a `_context`, and assigning
over it replaced a method with `None`. The app died in the message pump with
`'NoneType' object is not callable`, nowhere near the line responsible. A
subclass's attribute namespace is shared with everything it inherits, and a
framework's private surface is undocumented by definition.

**2. `Static.renderable` is not the accessor in this version.** A test reaching
for it failed with `AttributeError` in a way that read exactly like *the menu
never opened*. The widget now records what it drew. Reaching into a framework's
internals to observe your own output is a test coupled to a version.

**3. Fifty-eight tests broke on a defect I did not introduce.** `tab-projects`
survived in five places from a nested tab restructure rejected during the delta
merge, referring to a tab nothing composes. It was dormant until something took
that path, then failed as `No Tab with id '--content-tab-tab-projects'`. **A
rejected merge resolution leaves live references behind**, and the half you kept
compiles perfectly.

**4. Three glyphs could not be encoded.** `❯`, `❮` and `─` raise
`UnicodeEncodeError` on a cp1252 console. This corpus had already lost a demo to
a folder emoji the same way, two days earlier, and I reached for prettier glyphs
anyway. **Aesthetics that do not render are not aesthetics**, and there is now a
test that encodes the ring to cp1252 at every size.

**5. The same heredoc escaping trap, three times.** `\n` inside a shell heredoc
written into a Python string literal produced an actual newline and an
unterminated string — three separate times, in two files, after the class had
been named in this corpus's own retrospectives. The fix each time was thirty
seconds; the recurrence is the finding. Writing code through a shell heredoc is
a lossy channel, and a file write is not.

**6. A test asserted the mechanism and passed while the feature was broken.**
The ring is a pop-over and was covering the whole dashboard. The fix set the
screen's background to transparent; the test asserted
`styles.background.a == 0`; both were correct and **the dashboard was still
completely hidden**, because the layout containers inside the screen paint
their own ground. I reported it as done. The operator found it by looking at it.

That is this corpus's oldest failure mode — a check reporting success while
enforcing nothing — written fresh into the change meant to fix the problem.
Checking the style is checking that the lever was pulled. The test now reads
the exported screenshot and compares the words actually drawn, and the style
assertions were removed rather than kept alongside, because a passing
mechanism-check next to a real one re-teaches the habit.

**The check that would have caught most of this already existed.** Every one of
1, 2, 4 and 5 surfaced locally, before anything reached a runner, because of a
standing instruction to run the full suite and the workflow runner before
pushing. The session's earlier half — before that instruction — pushed three
times and learned from the runner instead.

**Defect 6 is the one no gate caught**, and it is the sharpest of the set: the
failure was not in the code but in what I chose to assert about it. A suite is
only as honest as the question its assertions ask, and no amount of running it
locally fixes an assertion aimed at the wrong thing.

## How to bolster the rad protocol

Earned from implementing it, not from reading it. Each of these cost real time
and none is a criticism of a decision — they are places where a second host had
to guess.

**1. Tag every conformance vector with the input modality it requires.**
`conformance/vectors.json` holds 47 cases and no way for a non-pointer host to
know which of them it is even eligible for. A keyboard-only implementation must
either run everything and fail on the pointer cases, or hand-curate a subset and
lose the guarantee. A `modality: pointer | keyboard | either` field makes the
subset mechanical, and makes "cases this host cannot express" a number rather
than a judgement.

**2. State the state machine's transitions and their cost explicitly.** The host
integration standard gives the session's *surface* — `openAt`, `onIntent` — and
leaves the semantics to be inferred: does `openAt` charge an input? Does `enter`
on a submenu commit anything? Is a rotation past the last wedge a wrap or a
stop? I chose answers that seemed right; another implementer will choose
differently, and both will pass their own tests. A transition table would settle
it in a page.

**3. Say that L0 and L1 may be the same event.** rad's abstraction ledger meters
raw platform events separately from recognized gestures. On a platform with no
gesture recogniser a keystroke is *both*, and an implementation that felt
obliged to show a difference would have to invent one. Stating that the collapse
is legal — and that reconciliation at L3 is what matters — removes the
temptation.

**4. Ship the tokens as data, not only as CSS.** `DRAFT-rad-theme-tokens.md`
says nothing paints outside the token layer, and the tokens live as CSS custom
properties. A terminal host, and an Android one, cannot read CSS. I transcribed
four palettes by hand out of `index.html` — which is exactly the second copy the
record exists to prevent, and it will drift the first time a theme is tuned.
Generating `tokens.json` from the same source would make every host read the
values rather than copy them.

**5. Give the contract something to say about narrow surfaces.** The `≤ 8`-item
rule and the IPA budget both bound *arity*. Neither bounds *width*, and a
terminal ring is width-bound before it is arity-bound: `Advance phase` and
`Sync project` crowd the hub at four items, long before eight. A maximum label
length, or a stated truncation rule, would make a resolver portable rather than
per-host.

**6. The metrics record's own open question is the right one.** It excludes
continuous camera navigation from IPA at v0 and marks it *"Open question —
targeting cost is real; revisit."* A terminal has no camera and so cannot help
settle it, but the same gap appears as keyboard *travel*: reaching a wedge nine
positions away costs nine inputs by the current definition and no more, though
it plainly costs the user something else. Whatever resolves the pointer case
should be checked against this one.

## What this leaves

The ring is validated, not finished. Long labels crowd horizontally at depth;
rad's vectors are not yet wired to it, so it is built to the documented
behaviour and held to the metric but not yet to the cases; and the tabs it is
meant to replace are still there, because replacement is a later stage than
proving the thing works.

The honest summary is that the interaction is real and the conformance is not
yet. Until the vectors run, "this is rad" is a claim resting on my reading of
four records — which is exactly the kind of claim this corpus asks people to
stop making.
