# adapters/

Optional glue for particular tools. **Nothing here is part of the constitution,
and nothing in the governance layer depends on it.**

`AGENTS.md` states four facts a session must establish before writing, and the
scripts in `project-seed/ci/` establish them with no tooling beyond Python and
git. An adapter is a convenience that wraps those for one product. If the
product disappears, the invariants and the scripts are untouched.

| Directory | Targets | Contains |
|---|---|---|
| `claude-code/` | one vendor's CLI slash-command mechanism | four command files wrapping the session-open, gate-run, and session-close invariants |

## Why they are here and not in `project-seed/`

`project-seed/` is copied into every adopting project. Anything in it becomes a
dependency of eleven repositories, and a vendor mechanism copied eleven times is
a vendor mechanism the org has standardised on without deciding to.

The charter's seams principles say a third-party component is reached only
through an interface with multiple independent implementations, and that a
single-implementation dependency needs an explicit exception record naming its
exit plan. A slash-command format has one implementation. Rather than write that
exception, the dependency is removed: the governance text names no product, the
scripts are plain Python, and this directory is where anyone who wants the
convenience finds it.

## Adding one

Name the directory for the product. State in its own README which invariants it
wraps and which scripts it calls. Do not add a rule that exists only here — if
it is worth requiring, it belongs in `AGENTS.md` as an invariant, expressed
without naming your tool.
