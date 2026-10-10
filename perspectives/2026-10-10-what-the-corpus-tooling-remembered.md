# What the corpus's tooling remembered — 2026-10-10

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-10 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5 |

The corpus's checks, generators and seed scripts opened with long docstrings
telling how each came to exist: the defect it was written after, the false
reading it once gave, the mutation that proved it. Under
`records/DRAFT-durable-text-states-what-is-true.md` those docstrings now state
what each tool does and cannot do, and the explanations moved to the tooling
reference under `docs/ref/ci/`. This page keeps the stories, read at `1e5961f`;
figures are as the docstrings gave them.

## Checks that reported on their own scaffolding

`qm posture`'s first yield reading matched a number near the word "killed"
loosely and read `28/44 killed` as `44 killed`: 100% where the truth was 64%,
for every watched module, in the tool built to measure exactly that. It was
printed, read and repeated to a person before anything checked it. Its first
suite total took the first `N passed` in the output, a nested run's 277, where
the suite had 1058; it reported without checking pytest's exit status, which
would have made a broken suite look fast.

The governance generator's first draft asked `gh repo list` for
`licenseInfo.spdxId`, a key that endpoint does not have, and with a `"NONE"`
fallback reported ninety-nine unlicensed repositories, confidently and in a
nice table. Its first run reported three existing projects nonexistent, because
they sorted past the hundredth repository and GitHub returned the first page
silently; `ls-tree` without `-r` reported "no records" for a directory holding
ten; an Actions token scoped to one repository saw a third of the fleet as
missing everything, which read as the worst-adopted projects in the org. Its
seed-workflow list named three workflows and missed the slot gate, so the
generated status reported nothing missing for two projects that lacked it on
the host.

In one week the repository found four generators whose hardcoded scope made
them describe themselves: a reading budget that omitted the charter, an index
comparison whose two sets were both empty for the check's whole life, a
document scan that skipped the reference tier while reporting every state
known, and that seed-workflow list one short. Each was green. The ADR lint's
numbered comparison compared two empty sets until the filename comparison was
added and found four records missing from the corpus's own index, two of them
the records behind charter principles.

The glossary linker claimed idempotence before it had it: it linked the first
bare use of each term, a masked link then made the second use the first bare
one, and its second pass rewrote seventeen pages. The trio demo's windows
"agreed" because both counted the same field of the document they had just
been handed; the first version ran every window with the demo's own
interpreter, so a window failed to import and the demo reported a true
sentence about the wrong process.

## Mutation testing and its own traps

Every mutation result the corpus quoted was once produced by a scratch script
thrown away after; `qm mutate` became the reproduction. Its first shape staged
only `ci/`, so tests reading a registry or record outside it failed in the copy
and the baseline went red; finding why `-B` matters cost a session, because
mutants written within one second share the cached bytecode's key.

Several mutations proved nothing the first time. A restore copied from a backup
a shell fallback had never written, so each run carried the previous mutations
and every one read as red. An anchor mutation took three attempts, because
removing `^` changed nothing under `.match()` and changing `.match` changed
nothing while `^` remained; before that the mutation script raised and its
traceback was filtered out by the `grep` watching for assertions, so nothing
printed and the nothing read as a pass. Two cherry-pick tests passed by luck,
because with dates pinned, picking a tip onto its own parent reproduced the
original sha; they surfaced only when a mutation run printed `assert 0 == 1` on
a line no mutation touched. One suite's first red came before any mutation, its
fake host reading `None` as "use the green default".

## Private names and leaks

An earlier version of the inventory produced one document and filtered the
sensitive fields out of it. It wrote 34 private repository names and 28
absolute paths carrying the operator's username into the working tree of a
public repository, and was one command from being pushed when the reviewer
stopped it -- having reintroduced a problem `ci/governance_status.py` already
solved, because the session had not read that file first. The private-names
check once knew 2 names of 34, so `clean` meant almost nothing; knowing all 34,
it produced 187 findings and no disclosures, because one private name equals the
organisation's own and others are ordinary words. Two private names remain in
the public history of a public repository from a committed `ci/workspace.yaml`,
while the inventory redacted the same two; nothing had read the files together.
A redactor walked dicts, lists and strings, so an `Unknown(reason)` wrapper
carrying a repository name passed through it into a committed document.

The leak check's first findings, on 2026-08-23, were a home path in `qmcp`'s
documented client config, a home path in a committed screenshot, and a
conversation share link and archive path in a transcript's header; a handoff
naming where two clones sat and a ledger entry naming a scratch script were
found on 2026-09-20.

## Pins and stranded work

On 2026-08-22 `codecartographer` was found pinning its governance submodule at
a commit on no remote and in no clone but one machine; a fresh checkout could
never have resolved it. Its submodule clone also held a branch carrying the
only copy of a project record, with the pin pointing at that same commit, so
the pin and the branch were wrong together, and a working tree was in fact
deleted before anybody looked. `rad`'s `evolve/rad-v1` carried seven commits
on exactly one disk for seventeen days while two repositories cited a document
only those commits held, and `git branch -r --merged` listed its remote ref as
safe to delete. Two `dossier` branches looked identical in every count; by
patch, one was already upstream and the other was 556 lines of real work on one
disk. The pin check once looked up submodule URLs by name, missed every moved
submodule, and passed each one unexamined.

`qmetronome`'s alpha release build broke on `upload-pack: not our ref` and it
wrote a check; `apothecary` hit the identical error on 2026-07-21 with no check,
because nothing carried the fix across. Carrying it became the seed's job.

## Signing and attribution

Signing stopped at 2026-08-12T23:29, mid-branch and immediately after a signed
commit, because a session added a flag disabling it, and nothing noticed for
three days. The branch introducing the signature check carried nine unsigned
commits that could not be signed without rewriting history, so the check got a
cutoff; its comment first claimed old commits "never turn the exit status
green", which was false. On a runner, `%G?` reported on the runner's empty
keyring rather than the commit. The attribution rule first covered only the
co-author trailer, so a subject naming the tool passed every gate. The
pull-request voice rule had been stated to the tool three times and leaked each
time in the same shape; seven pull requests carried it on one day.

## Routes and entry points

`AGENTS.md` said `uv run qm --help` was the whole surface, and a session then,
in one day, ran `pytest` directly a dozen times, mutated by hand with `cp` and
`sed`, typed an `ast.parse` one-liner after every edit, and documented a demo by
its file path -- each against a rule its author had read. Each became a pattern
in the declared-routes hook, which once failed closed on `[]` until a test
written for that case found it. Another session used four pytest invocations in
one afternoon, each able to collect a different set; `qm test` became the one.
Measured on sixteen cores the suite took 280 s serial and 77 s parallel. An
`import ci.foo` resolved locally and failed on a runner that installs nothing;
remote CI caught it on the first pull request that let a workflow near it.

## The charter's own structure

Measured on 2026-08-25, six of seventeen principles were named by no other and
named none, among them `credit-tracks-accountability`. A draft of
`shrink-the-black-box` then said the model "is what writes the check",
contradicting that principle in its central sentence; nothing surfaced it, a
person reading it did, and the principle-edge check was written. Principle
headings once carried positions, and inserting one anywhere but the end would
have reaimed every reference below it; they were renamed to carry names. The
ordinal guard's first integration was a remediation plan numbering its own work
packages in the same form, and annotating twenty correct lines to quiet the
tool was refused in favour of a file-scope allowance.

## Small things the tooling remembered

- A non-ASCII checkmark crashed the private-names report on a cp1252 console:
  the tool surfacing a leak fell over on the line it was surfacing.
- The licence object on GitHub's list endpoint spells its key `key`; the
  comment saying so was written for the next reader.
- The web front end once shared a default port with half the Python world, and
  the panel spent a week reading the wrong program.
- `dossier` slugged branch names by replacing slashes, and 30 of the corpus's
  32 branches contained one, which forced the address grammar.
- The first cookbook page committed the branch and the uncommitted count, so
  `qm docs check` reported drift on every keystroke.
- A ledger guard scanned a fixed forty-line window and walked past the real
  entry, which was longer, closing it twice.
- A shell heredoc turned an escaped `\t` into a real tab in a docstring five
  times in one session, which is why mixed tabs are refused.
