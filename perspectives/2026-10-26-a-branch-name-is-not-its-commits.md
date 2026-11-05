# A branch's name is not its commits

**2026-10-26.** Tidying branches across the estate, and building the tools
that make tidying safe: `qm references`, the `math/<slug>` namespace, and a
*held* class in `qm estate` and the seed's branch census. Attributed, dated,
binds nothing.

Tools: Claude Opus 5.5, which made the mistakes described and wrote this page;
reviewed and committed by a human.

Most findings here have one shape. A branch was judged by something standing
in for it, such as its name, its missing pull request or its lack of unique
commits, rather than by what refers to it and where its commits are.

## A branch was one copy because no remote branch shared its name

**Assumption:** a local branch with no remote branch of its name holds
commits nowhere else.

`qm estate` reported nine local branches in three repositories as one-copy,
the class whose deletion deletes work. Before each was deleted, its tip was
checked against every remote branch, and each was contained in a pushed
`docs/tighten-language` branch. The survey was right that no remote branch
had the name, and wrong about what the name stood for. Seven of alfred's
branches, at 354 to 359 commits ahead, read the same way.

**Would have caught it:** asking which remote branches contain the tip. That
check now exists. `qm estate` and the seed's branch census report such a
branch as *held* (#269, #271), keep a holder only while the host still has it
at a tip that contains the branch, and fail tests when either rule is
broken. The same reading is not yet applied to a pushed branch ahead of its own
copy, whose unpushed commits another branch may hold. That is in the queue.

## A ref with nothing unique was taken as safe to delete

**Assumption:** a ref with no commit of its own and no open pull request is
nothing anyone depends on.

The local `dev`, `prod` and `test` refs were recommended for deletion as
leftovers. They are the stages `docs/ref/namespaces.md` names. They were
restored. The exploration-namespace branch nearly went the same way, as a
stale branch with no pull request, while a perspective cited the handoff it
holds and the namespace it proposed was still unadopted. `math/<slug>` was
adopted instead (#264), and the branch was kept as the archive the
perspective cites (#265). A sha cited by a handoff page had changed when its
commit was cherry-picked to `main`, so the citation named a commit `main`
did not hold (#255).

**Would have caught it:** a reading of what still refers to a branch, run
before it is retired. That is `uv run qm references` (#263). It reports the
namespace page naming a ref, a page citing it by name, a commit only it holds
cited elsewhere, and a file only it carries. The consolidation runbook
requires it before a branch is retired.

## A guard tested on its author's cases

**Assumption:** `qm references` was finished when its tests passed and its
mutants died.

Its next real uses found three holes. A permanent namespace (`project/<name>`)
went unreported. Every open pull request into a project branch carried old
copies of corpus pages, which counted as references. And every head repeated
`main`'s own lines. Each was fixed before it merged. Its report also says a
merged branch's references would point at nothing, which overstates it: the
cited commit survives. That is in the queue.

**Would have caught it:** a pass whose brief is to use the guard on real
decisions, which is `AGENTS.md` item 13. Here that pass was the next few
branch decisions, read as a test.

## A survey run from a worktree surveyed something else

**Assumption:** `qm estate` reads the same estate wherever it is run.

Run from a sibling worktree, it found 22 of the 39 clones and reported no
one-copy work at all. Its default search root is two directories above the
module, which from a worktree is a level too deep. The private roster
companion is read beside the module, and a worktree has none. The uniform zero
was read as a tooling fault and compared with a run from the clone, which
found every clone.

**Would have caught it:** the survey's own "found" count, which was printed.
No check refuses the mismatch. That is in the queue.

## The mutation harness wrote what it was not asked to

**Assumption:** a hand mutation applied is a mutation measured.

Three runs went wrong in three ways. A replacement split on a colon garbled
the mutant, so pytest gave no verdict. A search string with the wrong
indentation matched nothing, and the script's count assertion stopped it
before any write. A text API wrote the mutated module with converted line
endings. Each module was restored byte for byte from a backup whose presence
was checked first, and each mutant was rerun cleanly.

**Would have caught it:** the count assertion did. The other two were caught
by reading the output rather than the exit status.

## Tests slow by construction

Each test built a bare remote, cloned it, committed and pushed: about eight
git processes, each costing tens of milliseconds on this platform. The estate
tests ran 23 tests in 29 seconds, the census 10 in 18.

One repository per module, written by `git fast-import` in a single process,
replaces them. Its tracking refs are declared as a last fetch left them, and
its bare remote is set by a push by URL, which moves no tracking ref, so the
two can disagree as a real clone's do. Each case is a row in one table read
against a cached run. The estate now runs 54 tests in about 6 seconds and the
census 20 in about 4. The census itself read each branch in five git calls,
and now reads all refs in one listing and each branch's counts in one more
(#270).

## An override in a scratch repository

`git -c user.name=… commit` was run once, in a throwaway repository outside
any clone, to compare two output formats. The 2026-08-15 perspective on two
corrections records the same override as a break of an agreement made that
day. A scratch directory is not an exemption.

**Would have caught it:** nothing mechanical. No hook runs in a repository
that no clone owns.

## Delivery asked about as if it were content

**Assumption:** each merge of a green pull request, each deletion and each
choice between one pull request and two needs a person's answer.

`AGENTS.md` item 3 decides landing. A standing instruction kept outside the
repository overrode it, and the corpus carried no trace of why. Most
questions in the triage were about delivery, not about what anything said.
The queue's §1 now states the rule. A question concerns what a change says or
does. Delivery follows the corpus. Work that nothing else holds is asked about
before it is destroyed.
