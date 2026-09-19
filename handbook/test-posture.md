# Test posture — a governance review

**What this is.** A review of how this organisation tests, what it costs, what it
catches, and what to do about the gap between those. Written after a measured
pass over `qm`'s own suite, and intended to propagate to every project through
`project-seed/`.

**What it is not.** A style guide for writing tests. It is about the *posture* —
the shape of the whole suite and the loop that keeps it honest — not about any
individual assertion.

**Stamped 2026-08-22.** Every figure names the command that produced it.
`uv run qm posture` reproduces them.

---

## 1. The finding that organises everything else

**A suite has two numbers and this corpus was only ever looking at one.**

| | What it answers | How it was known |
|---|---|---|
| **Cost** | wall clock, fixture time, slowest tests | visible, watched informally |
| **Yield** | does it notice when the code is wrong | **never measured** |

Green was the only signal. And green is compatible with:

- a test that **skips** and reports nothing (two of these shipped this month);
- a test whose subject is absent, so its assertion never runs;
- a check whose guard has never been observed to fire;
- a module with a `main()` that **no test executes at all** (five of these, one
  of them running in every fork).

Charter **P16** states the rule — a check is evidence only after it has been
seen to fail. This page is the operational half: what to measure, how often, and
what to do when the number moves.

**Optimising cost alone is actively dangerous**, and this is the reason the two
numbers are always printed together. The fastest possible suite is no suite; the
cheapest way to make any suite faster is to make it check less, and nothing in a
green tick distinguishes that from a genuine improvement.

## 2. What the measured pass found

`uv run qm posture` against `qm`, before and after one deliberate pass:

| | Before | After |
|---|---|---|
| Wall clock | 178.6s | **137.6s** |
| Fixture time (seed suite) | 19.1s | **4.7s** |
| Tests | 1058 | **1346** |
| Yield, watched modules | unknown | measured — see below |

**Nothing was deleted, and the suite grew by 288 tests while getting 41 seconds
faster.** Every second came from work that was repeated or misplaced, which is
the only kind of test optimisation that is safe by construction.

The first yield reading, and the reason it is worth having:

| Module | First reading | Now | |
|---|---|---|---|
| `ci/check_restatements.py` | 81% | 81% | |
| `ci/check_mathematics.py` | 65% | 65% | had no tests at all |
| `project-seed/ci/check_placeholders.py` | — | 65% | had no tests, runs in every fork |
| `project-seed/ci/adr_lint.py` | 64% | 64% | |
| `project-seed/ci/check_pr_base.py` | **33%** | **45%** | **the finding, acted on** |

`check_pr_base.py` decides whether a pull request may target the base it names —
`AGENTS.md` item 4 exists because one PR in this org sat open carrying eighteen
commits of unrelated work. Two thirds of deliberate breakages to that gate go
unnoticed by its tests. It is green, it has a test file, and it was the least
suspected module in the corpus until something broke it on purpose.

### The four things that were actually wrong

**A guard that ran last.** `harness_status.py` refused to write the machine
layer *after* building it — half a minute of scanning every clone on the machine
to produce a document it then threw away. One test spent **29.7s**, 17% of the
entire suite, asserting a refusal. Moving the check above the work made the test
0.0s and made the tool better: a guard that runs last costs what it prevents.

**A fixture built per test instead of once.** Ninety-three tests each spawned
four `git` subprocesses to build an identical repository. Built once and copied,
with `origin` rewritten so no test can see another's state: **19.1s → 4.7s**.
Isolation was verified by removing the rewrite — seven tests failed, which is
the isolation being real rather than asserted.

**Identical subprocess invocations, repeated.** Three tests ran the same command
to assert three different properties of one output. Memoised by argument set —
**not merged**, because merging buys the same seconds and costs the failure
message.

**Checks living in a person's fingers.** A syntax check was being typed by hand
after every edit. It is now 204 parameterised cases that run in 0.48s, and one
of them catches the tab-in-a-docstring failure that has bitten this session
three times.

## 3. The remediation list

Ordered by return. Each is a thing to do, not a thing to consider.

### Do now

**1. Move every guard above the work it guards.** Search for checks that run
after an expensive build. The `harness_status` case was 17% of a suite; there is
no reason to think it is the only one.
→ `uv run qm posture` names the slowest tests; a slow test asserting a *refusal*
is the signature.

**2. Make per-test fixtures per-session where the state is immutable.** The
pattern: build once in a `scope="session"` fixture, copy per test, and repair
whatever the copy breaks (here, one remote URL). **Then remove the repair and
watch tests fail** — otherwise the isolation is a claim.

**3. Close the five modules nothing executes.** Done except one:
`ci/check_mathematics.py`, `ci/test_posture.py`, `ci/generate_docs.py` and
`project-seed/ci/check_placeholders.py` all have tests now. `ci/devloop.py`
remains exempted — it shells out to the other gates and has no logic of its own.
→ `ci/tests/test_every_gate_is_exercised.py` fails on a new one, exemptions must
carry a reason, and **an exemption left behind after somebody writes the test
also fails** — which is what keeps the list shrinking rather than accumulating.

**4. Write the mutation line into every new guard.** One line:
`Mutation: <change> and this fails.` It is the only durable record of what was
established.

### Do next

**5. Raise `check_pr_base.py` first.** ~~33%~~ **45%, done.** Reading the
survivor list separated two kinds. Most were mutations of prose — ` not ` to
` ` inside a `help=` string, `capture_output` flipped on a subprocess whose
returncode is all anyone reads — and those are **left alive on purpose**: a test
pinning the wording of help text would fail every time somebody improved a
sentence. Two clusters were behaviour and are now closed: whether the required
arguments are actually required, and the branch of the missing-ref hint that
tells you to push. Both are reachable by a person on their first run.

**6. Raise the yield where it is low elsewhere.** 64–81% on the rest. Many
survivors are mutations of prose inside error messages and are not worth
catching; some are real. **Read the survivor list, decide per survivor, and
write down which are deliberate** — an unexplained survivor and an accepted one
look the same in a percentage.

**7. Extend the watched list** as modules become load-bearing. It is a list and
not a sweep on purpose: a measurement nobody runs is worth nothing.

**8. Give the slow remainder a reason or a fix.** 32 tests over one second, most
spawning subprocesses. Some are legitimately slow — a test that runs the real
CLI is worth its seconds. An *unexplained* slow test is usually a fixture doing
work that could be done once.

## 4. The loop

**Weekly, or before any pull request that touches tests:**

```
uv run qm posture                 # cost and yield, against the baseline
uv run qm posture --baseline      # after a deliberate improvement
```

Three rules make it a loop rather than a report.

**A run that got faster and caught less did not get better.** The tool prints
both and says so. If wall clock falls and yield falls, the change is a
regression wearing an improvement's clothes.

**The baseline is committed.** `.qm-posture.json` is a record of what the suite
cost on the day somebody looked, so a drift is visible as a diff rather than as
a memory.

**It is not a gate.** `qm posture` exits zero whatever it finds.
`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md` rejects a
mutation-score threshold and says why: a number that fails a build gets gamed —
tests get written to survive random edits rather than to catch real ones — and a
number a person reads gets discussed. The discipline is the reading, not the
blocking.

## 5. What propagates, and what does not

**To every project, through `project-seed/`:**

- `test_every_script_compiles.py` — the floor: every script parses, no tabs in
  indentation. Standard library only, so a fork that has installed nothing can
  run it.
- The session-template fixture pattern in `conftest.py`.
- The obligation from P16: a new guard carries its mutation line.

**Staying in `qm`:**

- `qm posture` and `qm mutate` — they read this corpus's own layout. A project
  wanting them should get them as a route in its own tooling rather than by
  importing governance.
- `test_every_gate_is_exercised.py` — the shape is general; the exemption list
  is not. A project copies the file and starts its own list.

**And a boundary worth stating.** `codecartographer` is the org's parsing and
abstraction tool — ASTs, lexicons, abstraction layers. It is tempting to reach
for it whenever a gate needs to understand code. **A governance gate must not
depend on a project**: it would invert the dependency and fail in every fork
that has not installed it. So syntax questions a fork must answer alone use the
standard library, and anything richer than *does this parse* belongs in the tool
built for it, called from that project's own tests.

## 6. What this review did not establish

- **That 64% is a good or bad yield.** It is the first measurement. Its value is
  as a baseline, and a number with nothing to compare against decides nothing.
- **That the remaining 32 slow tests are wasteful.** They were listed, not
  judged. Some are the real CLI doing real work.
- **That the suite catches what matters.** Mutation testing is textual and is a
  floor. A killed mutant means *some* test noticed, not that the right one did —
  `qm mutate` says so itself, and the sentence is worth keeping.
- **That any of this holds outside `qm`.** The pass was measured here. The three
  sibling repositories have larger suites and have not been measured.
