# The Harness Measured Its Own Cache

| | |
|---|---|
| **Date** | 2026-08-16 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | assistant-2026-08. See `ci/tool-registry.yaml` |

---

## What this session was for

`perspectives/2026-08-16-what-the-checks-were-not-checking.md` ended with a
finding: nothing was required to merge into `main`, ten checks ran, none was
required, and the account opening pull requests merged them. The response was to
make the *check list* the human-approved artifact — approved once, run every
time, zero approvals, no way to skip.

This session finished that: a repaired page, tests for the route that reads
drafted rulesets against applied ones, and the registration of two checks that
were running unregistered. It landed as #65 at `fde5dfc`.

The interesting part is not that. It is that **the tool written to check whether
the tests discriminate did not discriminate**, in a way that produced confident
numbers, and that the numbers were quoted mid-session before they were true.

## Three defects in the measuring instrument

### The one that hid a real bug: a fake that was too kind

`ci/rulesets.py`'s tests replace `subprocess.run`, which is right — a test that
asked a real host would answer differently offline, in CI, and on the operator's
machine.

The assumption underneath it was that a fake makes a test *hermetic*, and
therefore complete. It does not. The first mutation sweep survived
`capture_output=True` → `False` on both `gh` calls, and I read that as an
equivalent mutant: with `subprocess.run` faked, the argument cannot matter.

It matters enormously. Without `capture_output`, `proc.stdout` is `None`,
`json.loads(proc.stdout or "[]")` yields `[]`, and the function returns *nothing
is applied* from a call that succeeded and read nothing — the exact answer the
tool was written to give, produced by a repository with six rulesets applied.
That is the same `None`-versus-`[]` distinction the module's own docstring calls
load-bearing, arriving through a door the docstring did not name.

**The check that would have caught it:** a mutation pass. It now exists, and it
is what caught it.

### The one I wrote into the harness: non-zero means failed

`killed = result.returncode != 0`. One line, obviously right, wrong.

pytest exits 1 when a test fails. It also exits 2 when interrupted, 3 on an
internal error, 4 on a bad invocation and 5 when it collected nothing. Every one
of those is a run that **did not happen**, and counting them as kills is how a
suite that is not running reports a good score — the same shape as a lint whose
glob matches no files, which this corpus has shipped six of.

It fired immediately. A mutant flipping `if __name__ == "__main__":` to `!=`
makes the module call `main()` on import; pytest died with an internal error and
the harness recorded a kill. There are three buckets now — killed, survived, and
*no verdict* — and the third is printed rather than folded into either.

**The check that would have caught it:** a fixture in which the tool reports
bad. `test_a_run_with_no_verdict_is_counted_in_neither_column` is that fixture,
written after the fact.

### The one that took the longest: the cache was the measurement

Two sweeps of the same tree, minutes apart, disagreed. One mutant was killed on
the first and survived on the second, with nothing changed in between.

The assumption was that writing a file makes the next process read it. CPython
validates a cached `.pyc` against the source's **size** and its **mtime
truncated to whole seconds**. `==` → `!=` changes neither, and mutants are
written a few hundred milliseconds apart — so a mutant imported the *previous*
mutant's bytecode, and the harness scored a run of code that had never executed.

It presented as flakiness. Flakiness is what a wrong number looks like when it
is wrong intermittently, and the temptation is to re-run until the answers agree
rather than to ask why they did not.

**The check that would have caught it:** two sweeps of an unchanged tree,
required to agree. It now exists, and the fixture is deliberately built so that
two mutants make the *same* substitution on lines of the same length — one
tested, one not — because that is the pair the cache collapsed.

## The numbers I quoted before they were true

Mid-session I reported 21/32 killed, then 26/32. Both were produced by the
harness carrying all three defects above. The honest figures for `ci/rulesets.py`
at `fde5dfc` are **25 of 31 judged mutants killed, with one mutant returning no
verdict**, and every survivor is an `and` or a `not` inside an English sentence
— a legend line, two disclaimers, an argparse help string.

This is the third time in two days that a figure from this corpus described the
scaffolding rather than the subject. The pattern is not that measurement is
hard. It is that **a measuring tool reports a number whether or not it measured
anything**, and a number is the most persuasive thing a session produces.

## The habit that nearly cost the finding

When the two sweeps disagreed, I wrote an inline script to diff the temporary
tree before and after. The operator stopped it with three words — *no wrapper?* —
and they were right twice over: `AGENTS.md` and the previous day's retrospective
both name inline verification as the failure of this exact class, and I had read
both that morning.

What matters is what happened next. Debugging *through the tool* meant asking
what the tool should assert, and the first correct assertion — that exit 1 is
the only status meaning a test failed — surfaced the real defect within one
edit. The inline script would have shown me a directory listing. It would have
found the symptom in that tree, and not the class in every future tree.

That is the argument for the rule, better than the rule states it. An inline
script answers the question you asked. A route answers it for the next person,
and forces you to say what the answer *is*.

## The repair that was larger than the handoff said

The incoming handoff described one loose end: a `str.replace` that asserted on
text already changed, raised, and left one section of `.github/rulesets/README.md`
stale.

Four passages were false, not one. The intro said all six rulesets ship
evaluating; the stage table put `A` last behind two code-owner approvals; the
`## The six` table said `A` required code-owner review and linear history; an
ordering trap explained why `A` would stop you merging your own pull request.
`apply.sh`'s banner said it a fifth time. All of them were true when written and
were invalidated by one decision taken later the same day — approvals to zero.

**The assumption worth naming:** that a failed edit is a localised loss. It is
not. A decision changed mid-session invalidates *every* restatement of it, and
the only one that leaves a trace is the one that happened to raise. The rest
read as normal prose.

**The check that would have caught it:** none, and this is the honest gap.
`ci/check_restatements.py` pairs declarations and their records, and its own
docstring says it cannot tell that a summary and its record disagree. Between
`AGENTS.md` item 15 — *the read document governs* — and a page like this one,
there is nothing mechanical. Finding these four took reading the JSON and the
prose side by side, which is exactly what nobody does when the prose looks fine.

## What this leaves

The mutation harness is a route now, so the next kill rate this corpus quotes
can be reproduced by someone who did not write it. That was the open item in
`ci/lane-registry.yaml`'s `development-loop` lane and it is closed. Two new ones
replace it, both smaller and both stated on the page: nothing *runs* the sweep,
and the operators are textual, so no mutant is generated for a swapped argument
or an off-by-one. A kill rate is a floor that reads like a score.

`main` is still not protected at the time of writing. The gap between a rule and
a mechanism closed today; the gap between a mechanism and its being switched on
is one command, and it belongs to a human on purpose.
