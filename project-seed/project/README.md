# <name> — what it plans, and what was found

<!-- SEED FILE: copy this directory verbatim onto this project's own branch
     of the qm repo (project/<name>, created from main) as project/, beside
     adr/, and delete this comment. Then replace every <name> placeholder
     with the project's own name: a copy that keeps one is a template being
     shown to its reader, and project-seed/ci/check_placeholders.py refuses
     it. The procedure is handbook/forking-a-project.md, step 2. -->

`project/` holds what this project plans and what was found of it, beside
[`adr/`](../adr/README.md), which holds what it decided. The application's
repository holds the application: its code, its reference documentation, its
walkthrough and its tour. The record *The application carries its tour, and the
harness reviews it* (`records/DRAFT-the-application-carries-its-tour-and-the-harness-reviews-it.md`)
is the decision.

A path written `project/...` is this branch's. Any other path a page here names,
and every link that leaves this folder, is the application repository's, and holds
where this branch stands at `governance/qm` in a clone of it: a link from
`project/` to the repository's root is `../../../`.

| | |
|---|---|
| [ROADMAP.md](ROADMAP.md) | What <name> claims is built, in the order to take it, each line naming the journey or the walkthrough pages that show it |

What else stands here, as the project has it:

| Where | Holds |
|---|---|
| `todo.md` | What is open: each item what is left of something built, or a plan not started |
| `plans/` | Plans, each saying what is decided and what is not built |
| `<what>-checklist.md` | What a person ticks before a stack is pulled or a tag is cut |
| `validation/` | Dated records of what a run found, each true of the day it names |

A file a test or a person at a machine feeds to the application is the
application's, and stays in its repository.
