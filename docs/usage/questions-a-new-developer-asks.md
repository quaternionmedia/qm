# Questions a new developer asks

If you have just been handed several repositories and a login, this page is the
short version. Every question below is one somebody asked in their first week,
written the way they asked it, with the command or file that settles it.

This page is a map rather than the rules themselves. Where it summarises a rule
it names the document that owns it, and that document wins.

## Where to run the commands

**Every `uv run qm …` command on this page runs in the `qm` clone and nowhere
else.** In a project repository the CLI does not exist — a project runs the seed
scripts in place, out of its mounted copy of the corpus, and installs nothing.
So `uv run qm gates` inside `qmcp` fails with `program not found`, and that is
the design rather than a broken setup.

The project-repository equivalent is the seed runner:

```
python governance/qm/project-seed/ci/run_workflows_locally.py
```

Some projects mount the corpus somewhere other than `governance/qm`; check
`.gitmodules` if that path is not there.

## The repositories

| Repository | Calls itself | Its part in the demo |
|---|---|---|
| `qm` | the decisions, and the checks that keep them honest | governance, the gates, the CLI |
| `qmcp` | a Model Context [Protocol](../ref/glossary.md#protocol){ .glossary-term } server | the harness: it measures work and answers over HTTP |
| `dossier` | the control panel | draws the harness's answer in a terminal |
| `codecartographer` | a tool for mapping source code as graphs | draws the same answer in a browser |

The middle column matters, because each repository's README introduces it on its
own terms and none of them opens by describing the demo. `dossier` and `qmcp` do
not import each other; what crosses between them is a document.

The roster in `ci/workspace.yaml` is the authority on which repositories are
active, and it lists others — `rad` among them. `uv run qm inventory` prints it.

## Getting started

**"I just cloned this. What do I run first?"**

`uv run qm devloop` measures your local environment against what the [loop](../ref/glossary.md#loop){ .glossary-term } needs,
and `uv run qm brief` builds the opening brief for a session. Then read
[Getting started](getting-started.md) and the worked example in
[walkthrough/](https://github.com/quaternionmedia/qm/tree/main/walkthrough).

`uv run qm workspace` writes the multi-root [workspace](../ref/glossary.md#workspace){ .glossary-term } file from the roster,
which is what actually puts the repositories in front of you.

**"Will my commits be rejected for anything I have not set up?"**

Signing, most likely. There is a `commit-signatures` gate, and it refuses a
branch carrying a commit with no verifiable signature. Set signing up before
your first commit rather than after. `uv run qm gates` lists it with the rest.

**"How do I see everything running at once?"**

`uv run qm dashboard` shows what is up, prints each service's fixed port, and
gives the command to start whatever is not. `uv run qm dashboard --start
harness` takes the name of one surface. It will not start the terminal front
end, on purpose: a detached terminal draws where nobody is looking. That one you
run yourself, in the terminal you want to watch.

**"How do I see the same data in both front ends, side by side?"**

`uv run qm demo --side-by-side` runs one topology through every window and checks
that they agree, rather than showing you two pictures and leaving the comparison
to your eye. `uv run qm demo --over-http --side-by-side` does it against the
running services instead, which is a different and stronger claim.

## Making a change

**"What is going to stop me merging something bad?"**

Nothing, mechanically — and you should know that before you rely on it.
`uv run qm gates` opens by saying so: the host reports no rulesets and no branch
protection on `main`, so every gate is advisory. They are worth running because
they are right, not because they are enforced. The command also lists, for each
gate, **what it cannot see**, which is the more informative column.

`uv run --extra preflight qm preflight` runs the workflows' real steps locally.

**"Why is my pull request red when the tests passed locally?"**

Check the governance submodule first. Each project pins a specific commit of
`qm`, and your working copy may be checked out at a different one — your tests
then ran against a corpus your pull request does not pin. `git submodule update
--init` returns it to the pinned commit.

The seed runner runs the workflows' steps against your working tree, so it finds
this only once the submodule is where the pull request says it is. Its own
docstring is explicit that a workflow depending on checkout options is only
partly exercised locally, and that a local pass is evidence rather than proof.

**"Do I open a pull request for this?"**

Yes, and you merge it yourself once the gates are green. Never push `main`
directly. Draft means incomplete — a finished pull request left in draft is a
change that never arrives.

**"How many pull requests can I have open?"**

One per repository, for agent-produced work. Drafts count; automation accounts
do not; and `project/<name>` branches are exempt, because each is pinned by a
different downstream repository. `uv run qm slot --repo <owner>/<name>` answers
it for one repository. The rule is a sequencing constraint rather than a limit on
how much you can do — [handbook/async-contract.md](https://github.com/quaternionmedia/qm/blob/main/handbook/async-contract.md)
§1 has the reasoning and the exemptions.

**"Who has to approve it?"**

Nobody, to merge. `main` is not a claim and merging is not a release. There are
exactly two moments a human decides: *[ratifying](../ref/glossary.md#ratification)*
a [record](../ref/glossary.md#record), and cutting a version tag. Assign the
person who asked for the work; do not request a review.

## Trusting what you are looking at

**"The suite is green. Does that mean the tests are any good?"**

Not on its own — a passing test may be asserting nothing. `uv run qm mutate
<module>` breaks a module on purpose and reports whether its tests noticed.
`uv run qm posture` reports what the suite costs and what it catches together,
because either number alone flatters. This is charter principle P16.

**"This says zero. Does that mean nobody looked?"**

No, and the distinction is built into every window. Zero means somebody measured
and found nothing. Unmeasured is a separate value with its own channel: the
terminal front end draws it with a distinct arrow glyph and the word
`unmeasured`, and the browser draws the edge dashed with the reason on hover.
Neither renders it as `0%`. If you ever find the two collapsed into one, that is
the defect the design exists to prevent.

**"Two tools are telling me different things about the same repository."**

`uv run qm divergence --left <one.json> --right <other.json>` reports where two
views of one address disagree, as differences rather than two lists to compare by
hand. `uv run qm two-views` does the same for git against the committed status
documents, and produces its own inputs.

The word doing the work is **address**. `uv run qm addresses` prints the grammar
— `<owner>/<repo>/<kind>/<id>` — and every kind it covers. An address is what
lets two systems say they are talking about the same thing; when something is
named differently in two places they cannot be compared, and that is usually the
real bug.

**"Where do these numbers come from, and are they current?"**

`governance-status.yaml` and `harness-status.json`, both at the root of the `qm`
clone. Read them rather than recomputing — a figure you derive yourself is a
second number nothing keeps up to date.

They are not symmetrical. `harness-status.json` carries its own refresh command
and staleness budget in a `reading:` block inside the file.
`governance-status.yaml` has no such block, and its refresh command and its
168-hour budget live only in
[handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md).
Check the age before quoting either.

## Reading the code

**"I can see a box in the diagram. How do I get to the code it stands for?"**

Click it, in either window. A node that names a repository carries both the
address the harness gave it and a link to where that content is read. A node that
is not a place — a gate, a stage — deliberately carries no link, because a link
to nowhere looks like it goes somewhere.

The two windows reach it differently: the browser opens a detail panel, and the
terminal binds a click action that exists only inside the running application.
Rendered to a file or a pull request body, the terminal view writes the address
out as text instead.

**"Where is the documentation for how X works?"**

In one place, deliberately. Comments carry facts about the code, `README.md` is a
shallow onramp, `docs/` is reference, and the reasoning behind a decision lives
in a retrospective in
[perspectives/](https://github.com/quaternionmedia/qm/tree/main/perspectives).
If you find the same explanation in two places, one of them will go stale.

## Working alongside other people and other sessions

**"Somebody else's changes are in my working tree. What happened?"**

Several sessions often run at once across these repositories for the same
reviewer. [handbook/async-contract.md](https://github.com/quaternionmedia/qm/blob/main/handbook/async-contract.md)
is the short set of rules that exists only because of that. Before you write
anything, check what is already in flight in your clone: a dirty tree you did not
dirty, a sibling branch, an unpushed commit.

**"How do I start a new project that follows all of this?"**

[Forking a new project](first-project.md) and
[handbook/forking-a-project.md](https://github.com/quaternionmedia/qm/blob/main/handbook/forking-a-project.md).
A fork runs the [seed](../ref/glossary.md#seed) scripts in place out of the
governance submodule and installs nothing — do not improvise a lighter version.

**"Something here is wrong. Where do I report it?"**

The same way as any other change: a branch, a pull request, and merge it yourself
once the gates are green. There is no separate queue.

---

## What this page does not answer

Whether any of the above is a good idea. That argument lives in
[records/](https://github.com/quaternionmedia/qm/tree/main/records), where each
decision states what it rejected and why, and in the retrospectives in
`perspectives/`. [The glossary](../ref/glossary.md) defines the house words this
page uses — [corpus](../ref/glossary.md#corpus),
[harness](../ref/glossary.md#harness), [gate](../ref/glossary.md#gate),
[record](../ref/glossary.md#record), and the rest.
