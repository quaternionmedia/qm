# What a system says about itself

**2026-08-21.** The orchestration plane, the audit, and the sweep.
Attributed, dated, binds nothing.

Tools: written with an AI coding assistant, reviewed and committed by a human.

The second perspective from this day. The first —
`2026-08-21-a-green-suite-and-eight-holes.md` — is about joins nobody examines.
This one is about a narrower thing that turned up four more times before the day
ended: **a system's description of itself, drifting from the system.**

## Four descriptions that were wrong

**A registry that read as a runtime.** `TopologyRegistry` holds eight
topologies, each with a config class, a schema and a `run` that raises
`NotImplementedError`. Nothing lied. But eight registered topologies look like
eight available topologies, and the only way to find out otherwise is to call
one.

**A plan that warned about the bug it then caused.** `qmcp/localmodel.py` emits
the commands to stand a model up. Two lines above the pull it says *"without
this they go to the user profile on the system drive"*. It set the variable,
pulled, and 4.4 GB went to the system drive — because `ollama pull` is a client
and the service had already read its environment. The comment was correct and
the plan was incomplete, and the comment made the plan *look* complete.

**A docstring promising a function nobody wrote.** `qmcp/audit.py` said
`record_model` was the path to making the model answerable. There was no
`record_model`. I wrote the sentence while designing and never came back.

**A plane that claimed a topology ran.** I declared `pipeline` as `RUNS`. The
registered class was still the stub — my concrete pipeline had claimed the same
`TopologyType`, and `TopologyRegistry.register` replaces silently, so which one
you got depended on import order.

## Why this is not the same as the morning's finding

The morning's eight were **joins**: two correct things with nothing examining
the space between them. These four are **claims**: one thing describing itself,
and the description going unchecked.

The difference matters because the remedies are different. A join needs
something that looks at both ends. A claim needs to be **made checkable** — and
three of the four already could have been, cheaply:

- `stubs()` asks whether a registered class actually overrides `run`. Four
  lines. It caught the plane lying the first time it ran.
- The bridge test asks whether two sides agree about a figure. It caught a
  category error in its own first run.
- The mutation sweep asks whether a guard fires. It found one guard that could
  not.

The one that stayed unchecked is the docstring. Nothing anywhere verifies that
prose describing a function corresponds to a function. `ci/check_restatements.py`
does this for records and the pages that restate them, and stops there.

## The pattern worth keeping

**A claim a system makes about itself should be expressible as a question the
system can answer.** Not "document accurately" — that is advice. The operational
form is narrower:

> If a docstring, a status field or a declaration asserts something about the
> code, write the two-line function that asks it, and run that function in the
> diagnostic.

Every one of the day's checks is that shape. `stubs()`, `undeclared()`,
`documented_routes()`, `seam-port`, `seam-shapes` — each turns a sentence
somebody wrote into a question something can answer.

## Suggestions

Ordered by how much each would have saved today, and each is a proposal rather
than a plan anybody has committed to.

**1. A docstring-to-symbol check.** The one gap with no guard. A docstring that
names `` `record_model` `` in backticks, where no such symbol exists in the
module, is mechanically detectable and was a real defect twice today — once in
`audit.py`, once in `chatgpt.py`, which claimed to be unverified after it had
been verified. Start with backticked identifiers in module docstrings; ignore
anything that resolves to an import.

**2. Make `TopologyRegistry.register` refuse a silent replacement.** Two classes
claiming one `TopologyType` is not a collision today — it is a race decided by
import order. Refusing, or recording both and reporting the ambiguity, turns an
invisible failure into a loud one. This is a change to somebody else's
framework, so it wants a decision rather than a patch.

**3. Record the model on every invocation.** 55 of 55 recorded none, so "which
models ran today" has no answer. `record_model` exists and nothing calls it yet.
The cost is one line at each call site; the benefit is that the audit stops
answering `unknown` to the question it was built for.

**4. Record the harness on a delta.** 51 of 59 deltas in flight have no harness
recorded. Same shape as the model gap and the same remedy.

**5. Decide what to do about the six stub topologies.** They are honest
brainstorms now, which is better than looking like debt. But `ensemble` and
`debate` both spend by construction, and neither has a budget. The next person
to implement one will need `qmcp/spend.py` wired in before the runtime, not
after.

**6. Retire `mesh`, `star` and `ring`, or give them configs.** Three names in
`TopologyType` with no class and no config. Reported by the plane rather than
deleted, because a smaller brainstorm is still somebody's intent — but a
vocabulary with three words nothing implements is three words that will be
guessed at.

**7. Fix or accept the three remaining `importlib.reload` tests.** They are
green and they are the hazard that cost sixty-three failures once. The real
remedy is making `dossier.cli`'s engine lazy, which is a refactor nobody should
do casually. Accepted debt with a date beats a check tuned around it.

## And the one I keep making

Four times today a pipeline's exit code was `tail`'s rather than the command's.
It is written down in two repositories. I hit it again between writing it down
and reading it back.

The fix that works is not remembering: it is `> file 2>&1; echo $?`. I have
stopped treating this as a lapse and started treating it as a property of the
tool — piping is so natural that the correct form has to be the habit, not the
exception.
