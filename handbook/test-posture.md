# Handbook — Test Posture

**What this is.** How this organisation tests: what a suite costs, what it
catches, and what to do about the gap between those. It propagates to every
project through `project-seed/`.

**What it is not.** A style guide for writing tests. It is about the *posture* —
the shape of the whole suite and the loop that keeps it honest — not about any
individual assertion.

---

## 1. Two numbers

**A suite has two numbers, and green shows only one.** `uv run qm posture`
prints both.

| | What it answers |
|---|---|
| **Cost** | wall clock, fixture time, slowest tests |
| **Yield** | does it notice when the code is wrong |

Green is compatible with:

- a test that **skips** and reports nothing;
- a test whose subject is absent, so its assertion never runs;
- a check whose guard has never been observed to fire;
- a module with a `main()` that **no test executes at all**.

Charter **`a-check-is-evidence-after-it-fails`** states the rule — a check is evidence only after it has been
seen to fail. This page is the operational half: what to measure, how often, and
what to do when the number moves.

**Optimising cost alone is actively dangerous**, and this is the reason the two
numbers are always printed together. The fastest possible suite is no suite; the
cheapest way to make any suite faster is to make it check less, and nothing in a
green tick distinguishes that from a genuine improvement.

## 2. Where the cost goes

Cost that comes from work repeated or misplaced is the only kind of test
optimisation that is safe by construction. Its shapes:

**A guard that runs last.** A tool that refuses to write *after* building what
it would write spends the whole build to produce a document it throws away, and
the test asserting the refusal pays for it. A guard that runs last costs what it
prevents.

**A fixture built per test instead of once.** Tests that each build an identical
repository can share one built once and copied, with `origin` rewritten so no
test sees another's state.

**Identical subprocess invocations, repeated.** Tests that run the same command
to assert different properties of one output can memoise it by argument set —
**not merge**, because merging buys the same seconds and costs the failure
message.

**Checks living in a person's fingers.** A check typed by hand after every edit
belongs in the suite as parameterised cases.

## 3. Practices

**1. Move every guard above the work it guards.** Search for checks that run
after an expensive build.
→ `uv run qm posture` names the slowest tests; a slow test asserting a *refusal*
is the signature.

**2. Make per-test fixtures per-session where the state is immutable.** The
pattern: build once in a `scope="session"` fixture, copy per test, and repair
whatever the copy breaks (here, one remote URL). **Then remove the repair and
watch tests fail** — otherwise the isolation is a claim.

**3. Every module with a `main()` is executed by a test.**
`ci/tests/test_every_gate_is_exercised.py` fails on a new one, exemptions must
carry a reason (`ci/devloop.py` is exempt: it shells out to the other gates and
has no logic of its own), and **an exemption left behind after somebody writes
the test also fails** — which is what keeps the list shrinking rather than
accumulating.

**4. Write the mutation line into every new guard.** One line:
`Mutation: <change> and this fails.` It is the only durable record of what was
established.

**5. Read a survivor list by kind.** Mutations of prose — ` not ` to ` ` inside
a `help=` string, `capture_output` flipped on a subprocess whose returncode is
all anyone reads — are **left alive on purpose**: a test pinning the wording of
help text fails every time somebody improves a sentence. Mutations of behaviour
that a person can reach on a first run get a test.

**6. Raise the yield where it is low.** Many survivors are mutations of prose
inside error messages and are not worth catching; some are real. **Read the survivor list, decide per survivor, and
write down which are deliberate** — an unexplained survivor and an accepted one
look the same in a percentage.

**7. Extend the watched list** as modules become load-bearing. It is a list and
not a sweep on purpose: a measurement nobody runs is worth nothing.

**8. Give the slow remainder a reason or a fix.** Tests over one second mostly
spawn subprocesses. Some are legitimately slow — a test that runs the real
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
- The obligation from `a-check-is-evidence-after-it-fails`: a new guard carries its mutation line.

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

## 6. What this cannot establish

- **That a given yield is good or bad.** Its value is as a baseline, and a number
  with nothing to compare against decides nothing.
- **That a slow test is wasteful.** Some are the real CLI doing real work.
- **That the suite catches what matters.** Mutation testing is textual and is a
  floor. A killed mutant means *some* test noticed, not that the right one did —
  `qm mutate` says so itself, and the sentence is worth keeping.
- **That a measurement here holds in another repository.** Each suite is
  measured where it runs.
