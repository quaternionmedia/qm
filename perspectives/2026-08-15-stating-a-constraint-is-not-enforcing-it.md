# Perspective — Stating a Constraint Is Not Enforcing It

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. Session retrospective; the companion handoff is `handbook/handoffs/exploration-namespace.md`. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (Anthropic) |
| **Date** | 2026-08-15 |
| **Task** | Record what went wrong in the session that added the `math/<slug>` namespace, assumption first, and say for each whether a check now exists. |

## Evidence classes

**E1** throughout for claims about this repository — every one was established
by a command run in the session. The one exception is marked E4 where it
appears.

---

## 1. I shipped a guard with a hole, and found it by re-reading rather than by testing

**The assumption:** that writing a constraint into the docstring of the thing it
constrains makes the constraint hold.

The change added `--per-head` to `check_one_pr.py`, so several parallel
explorations could be open at once. The exemption is keyed on the **head**
branch name. Its docstring said, in my own words, *"point it at a namespace
that cannot reach the default branch, and never at one that can."*

Nothing enforced that. A branch named `math/anything` aimed at `main` would have
been handed its own pull-request slot — the one-open-pull-request rule defeated
by choosing a branch name. I wrote the precondition and the exemption into the
same file, in the same edit, and enforced neither.

Worse, the file I was editing *already records this exact lesson* about the
sibling rule: `check_pr_base.py`'s comments say that keying the `project/*`
refusal on `base == main` "looked equivalent and is not," having been verified
with `--base evolve/staging --head project/qmcp` exiting 0 while the records
reached the org namespace anyway. I read that comment while adding my own rule
beside it and did not apply it to mine.

**What caught it:** re-reading the diff when asked for a re-review. Not a test,
not a gate, not the session's own checks.

**What would have caught it:** `AGENTS.md` §13 — *"a guard is not finished until
someone has tried to route around it… Ask for a pass whose brief is to satisfy
the check while doing the thing it forbids."* I did run that discipline against
the **slot rule** (adding my own two `main`-targeting branches to a simulated PR
set, confirming exit 1). I did not run it against **the exemption's own
precondition**. Applying an adversarial pass to the rule and not to the thing
that makes the rule's relaxation safe is the specific miss.

**Does the check exist now?** The hole does: `check_pr_base.py` refuses a
`math/*` head aimed at anything but `workspace/*`, allow-listed rather than
deny-listed, with three tests including the intermediate-base route. The
*discipline* that would have caught it before shipping is still a habit rather
than a mechanism.

## 2. Writing about a failure mode confers no immunity against it

Earlier in the same session I wrote a perspective arguing that the corpus's
namespace table drifts because a rule gets recorded as a fact about one
namespace rather than as a property of the table.

I then introduced **three placeholders for one namespace** in the same change:
`propagate/<name>-<date>` (pre-existing, in the runbook and `AGENTS.md`),
`propagate/<target>-<date>` (mine, in the README table), and
`propagate/<slug>-<date>` (also mine, in the new handbook page). A reader
arriving at any two of them would reasonably conclude they were different
things.

Found by grepping my own diff for the placeholder I had changed — which I only
did because the re-review asked what I might have broken, not because anything
flagged it.

**Does the check exist now?** No. The README row now says what `<target>` is and
that the two sets may not collide, which fixes this instance. Nothing detects
the next one. A lint for "the same namespace spelled with different
placeholders" is plausible and does not exist.

## 3. Three of my open questions had already been answered in the corpus

**The assumption:** that a question I cannot answer from the working tree is a
question for the human.

I closed a report with three items "for you to decide": which branch the
`docs/qm` submodule should track, what to do about REUSE, and the submodule
mount point. All three are settled in documents I had not yet read —
`README.md`'s adoption-by-reference section, `handbook/propagation-runbook.md`
Part B, and the runbook's `QM_SUBMODULE` note for a non-standard mount.

`AGENTS.md` item 3 names this precisely: *"A pull request states decisions, not
questions… A PR that asks its reviewer what you should have asked earlier hands
the drafting back to them and calls it review."* The `/cowork` command exists to
build exactly this context before writing, and I had not run it — I started from
the task rather than from the repository.

**Does the check exist now?** The command exists and predates me. Running it is
the check.

## 4. I stated the REUSE position confidently twice, in opposite directions, before reading the config

First: *"my four new files need REUSE headers."* Then, on finding the workspace
branch had no `REUSE.toml`: *"the whole workspace is outside REUSE, and that's a
pre-existing condition."* Both delivered as findings.

`REUSE.toml` declares licensing centrally with `path = "**"`, precisely because
"most of this repository is prose whose opening lines are load-bearing." No
markdown file needs a header. The new handbook page was covered automatically —
the lint went from 132/132 to 133/133 files with no action.

This is the inflation-then-deflation shape the corpus already has a perspective
about (`2026-08-11-inflation-deflation-and-what-discovery-looks-like.md`): the
correction read as rigour and was also wrong. Two confident statements, neither
grounded, before opening the file that answers the question in its first thirty
lines.

**Does the check exist now?** No, and I doubt one is possible. The applicable
rule is `AGENTS.md` §10 — establish a fact before asserting it — and the
specific tell was that both claims were about a config file I had not opened.

## 5. Two mechanical errors the existing rules already name

**An exit code read through a pipe.** `python check_pr_base.py … | tail -3;
echo "exit=$?"` printed a `REFUSED` verdict and reported `exit=0`, because `$?`
was `tail`'s. The tool had returned 1. `/preflight` §4 warns about this in those
words and notes it "has turned a failing check into a reported pass twice in
this org." This is the third. Caught within one command because the output said
REFUSED and the code said 0, which is a contradiction visible on the page —
had the tool passed, nothing would have looked wrong.

**A branch invented in a namespace I had not checked.** I created
`workspace/math-hierarchical-complexity` because `workspace/` was the
closest-fitting prefix, before establishing what the namespace meant. It meant
"a research workspace, permanent and terminal" — not "a contribution to one."
The branch was later renamed into the namespace this session added. The
namespace list I should have checked is the one whose incompleteness became the
session's main finding, which is either irony or the ordinary way a gap gets
noticed.

**Does the check exist now?** For the exit code: reading `$?` directly, or
`PIPESTATUS`, both of which are practice rather than mechanism. For the branch
name: `check_pr_base.py` would not have refused it either, since
`workspace/*` heads remain legal — a workspace branch aimed at a workspace
branch is a shape nothing has needed yet (E4: I did not test it).

## 6. What I would take from this

**A relaxation needs the adversarial pass more than a restriction does.** Both
of the day's real holes were in things that *permitted* something — a slot
exemption, and a namespace with one direction written. A restriction that is too
tight announces itself the first time it blocks legitimate work. A relaxation
that is too wide announces nothing, ever, and the corpus's whole argument for
periodic absolute review is that per-change review cannot see it.

**The comment beside the code you are editing is evidence, and I treated it as
background.** `check_pr_base.py` records a verified attack against the sibling
rule two screens above where I added mine. Reading a file to find the insertion
point is not reading it.

**Re-review found what the gates could not, twice.** Both the slot hole and the
placeholder drift were found by being asked to look again with an adversarial
brief, after every check was green. Eighteen of eighteen steps passed on a
branch carrying a hole through the one-pull-request rule. That is not a
criticism of the gates — they check what they check — but it is a concrete
instance of the corpus's own claim that a green harness bounds form and not
meaning.

## 7. What this perspective is not

Not a claim that anything reached `main`. Every branch discussed is unmerged and
none has an open pull request. The hole in §1 existed on a pushed branch for
roughly one hour and was closed before any review was requested.

Not an argument that the checks are inadequate. Three of the seven findings
above were caught by the corpus's existing rules the moment I read them, and one
(a missed call site in a refactor) was caught by its tests in about two seconds.
The pattern worth carrying is narrower: the rules that failed here are the ones
that must be *recalled at the moment they apply* rather than run.

— Peter Kagstrom, drafted with Claude Opus 5, 2026-08-15
