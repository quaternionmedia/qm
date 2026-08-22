# Questions a new developer asks

If you have just been handed four repositories and a login, this page is the
short version. Every question below is one somebody actually asked in their
first week, written the way they asked it. Each answer names the one command or
file that settles it, so you can check the answer rather than trust it.

Nothing here is a rule. The rules are in `PRINCIPLES.md` and `records/`; this
page only tells you where to look.

## The four repositories, in one line each

| Repository | What it is | What you run it for |
|---|---|---|
| `qm` | the decisions, and the checks that keep them honest | governance, gates, the CLI |
| `qmcp` | the harness — it measures work and answers questions about it | data, over HTTP |
| `dossier` | the terminal front end | reading the harness in a terminal |
| `codecartographer` | the web front end, and the org's parsing and graph tool | reading the harness in a browser |

The two front ends are deliberately two views of the same data. If they ever
disagree, that disagreement is a defect in one of them, and there is a command
that finds it.

---

## Getting started

**"I just cloned this. What do I actually run first?"**

`docs/usage/getting-started.md`, then the worked example in `walkthrough/`. The
walkthrough is executed by the ordinary test command, so it cannot drift from
what the code does — if it says something happens, a test asserts it.

**"How do I see everything running at once?"**

`uv run qm dashboard` tells you what is up and how to start what is not.
`uv run qm dashboard --start` brings up the rest. Each service has a fixed port
so you never have to guess: the harness on 3141, the web front end on 2718, the
terminal front end on 1618.

**"How do I see the same data in both front ends, side by side?"**

`uv run qm demo --side-by-side`. It runs one topology through every window and
checks that they agree, rather than showing you two pictures and leaving the
comparison to your eye.

## Making a change

**"What am I allowed to merge, and what will stop me?"**

`uv run qm gates` lists every gate **and what each one cannot see**, which is the
more useful half. `uv run --extra preflight qm preflight` runs their real steps
on your machine.

**"Why is my pull request red when the tests passed locally?"**

The most likely cause is the governance submodule. Each project pins a specific
commit of `qm`, and your local checkout may be sitting on a different one. Your
tests then ran against a corpus your pull request does not pin. Run the project's
own loop — `python governance/qm/project-seed/ci/run_workflows_locally.py` —
which runs the workflows' real steps against the pinned commit, rather than
running `pytest` yourself against whatever happens to be checked out.

This is not hypothetical. It is the defect that produced this page's entry.

**"Do I open a pull request for this?"**

Yes, always, and you merge it yourself once every gate is green. Never push
`main` directly. One open pull request per repository per person — that is a
sequencing rule, not a limit on how much you can do. `uv run qm slot` tells you
whether yours is free.

**"Who has to approve it?"**

Nobody, to merge. `main` is not a claim and merging is not a release. There are
exactly two moments a human decides: *ratifying* a record, and *cutting a version
tag*. Assign the person who asked for the work; do not request a review.

## Trusting what you are looking at

**"The suite is green. Does that mean the tests are any good?"**

Not on its own. A passing test may be asserting nothing. `uv run qm mutate
<module>` breaks the module on purpose and reports whether its tests noticed;
`uv run qm posture` reports what the suite costs and what it catches, together,
because either number alone is misleading.

**"This says zero. Does that mean nobody looked?"**

That is the right question, and the systems here are built to answer it. Zero
means somebody measured and found nothing. Unmeasured is a separate value, drawn
differently in every window — a dotted edge labelled `unmeasured` rather than a
line at 0%. If you ever see the two rendered the same way, that is a bug worth
reporting.

**"Two tools are telling me different things about the same repository."**

`uv run qm divergence` shows where two views of one address disagree, as
differences rather than as two lists to compare by hand. `uv run qm two-views`
does the same for git against the committed status documents.

The word doing the work there is **address**: `<owner>/<repo>/<kind>/<id>`. An
address is what lets two systems say they are talking about the same thing. If
something is named differently in two places, they cannot be compared, and that
is usually the real bug.

**"Where do these numbers come from, and are they current?"**

`governance-status.yaml` and `harness-status.json` sit at the repository root and
carry their own figures. Read them rather than recomputing — a number you derive
yourself is a second number nothing keeps up to date. `harness-status.json`
carries its own refresh command and staleness budget inside the file. Check the
age before you quote anything.

## Reading the code

**"I can see a box in the diagram. How do I get to the code it stands for?"**

Click it. Every node in the topology carries two things: the address it names,
and a link to where that content is read. Both front ends put both on the same
node, in the terminal and in the browser, so following a diagram to the source
works the same way in either.

**"Where is the documentation for how X works?"**

In one place, deliberately. Comments carry facts about the code, `README.md` is a
shallow onramp, `docs/` is reference, and the reasoning behind a decision lives
in a retrospective in `perspectives/`. If you find the same explanation in two
places, one of them is going to go stale, and that is worth a pull request.

## Working alongside other people and other sessions

**"Somebody else's changes are in my working tree. What happened?"**

Several sessions often run at once across these repositories for the same
reviewer. `handbook/async-contract.md` is the short set of rules that exists only
because of that. Before you write anything, check what is already in flight in
your clone: a dirty tree you did not dirty, a sibling branch, an unpushed commit.

**"How do I start a new project that follows all of this?"**

`docs/usage/first-project.md` and `handbook/forking-a-project.md`. A fork runs
the seed scripts in place out of the governance submodule and installs nothing —
do not improvise a lighter version.

---

## What this page does not answer

Whether any of the above is a *good* idea. That argument lives in `records/`,
where each decision states what it rejected and why, and in `perspectives/`,
where the retrospectives say how it actually went. Those are worth reading in
your second week, not your first.
