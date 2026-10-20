# Human-in-the-loop review — the 2026-08-24/25 session

**Transient.** Written to be deleted when its work lands. Nothing here is a
decision; it is a list of the decisions waiting for one.

| | |
|---|---|
| **What this covers** | the pull requests opened across `dossier`, `qm` and `qmcp` on 2026-08-24 and 2026-08-25 |
| **What it is for** | the two human gates — ratification for what the corpus says, the version tag for what a project ships. Neither has been passed by anything below |
| **What it is not** | a claim that the work is correct. Every item names what to look at, not what to conclude |

## 0. Read this first

**Nothing below has had a second pair of eyes.** Every check that ran is a check
drafted in the same session as the code it checks, which is exactly the condition
P16 exists for and does not cure: a guard proves what its author thought of.

**Three claims in this session were wrong and caught by a person or by a
mutation, not by review.** They are listed in §4 because the pattern matters more
than the instances.

## 1. Merged into `main`, and what to look at

`main` is readiness, not governance — merging asserted only that the gates ran.

### dossier

| PR | What to look at |
|---|---|
| #35 | The sweep takes a package name. **Check the fallback wording**: it says "widest-shared" and that is a starting point, not a recommendation |
| #36 | Three views merged into others. **Check nothing you use daily disappeared** — Pull Requests, Components and Hygiene are now inside On deck, Dossier and Branches |
| #37 | Every view is keyboard-reachable; numbers moved. **`m 8 6 6` is the Sweep tab, `m 6 4` runs the review.** If you had a route memorised, it changed |
| #39 | Screenshots. **One had been a picture of a deleted view since January** |
| #40 | Documentation at org scope |
| #41 | Selecting an owner now clears the repository selection. **This is the one most likely to surprise**: six row-handlers went from acting on a stale repository to refusing |
| #42 | Those handlers now read the row instead of the screen |
| #43 | `dossier clone` — **82 of 115 repositories have no clone here.** Cloning all of them is minutes and gigabytes |
| #44, #45 | The ring takes the pointer; thirteen buttons became three on `4 5 6` |
| #46 | The Waiting tab became **Outstanding** and gathers three sources |
| #47 | Deltas that move together |
| #48 | A reading that rebuilt the page it sits on. **The suite halved: 836s → 441s** |
| #49 | Eight widgets out of `tui/app.py`, verbatim. **No behaviour changes** — if something moved, that is the thing to report |

### qm

| PR | What to look at |
|---|---|
| #97 | Retrospective on this session's own waiting. Status is `Unreviewed` and **setting it is a maintainer act** |
| #98 | **P17 — shrink the black box.** A new charter principle. This is the item that most wants your judgement |
| #99 | Every principle declares its edges, or declares it has none with a reason |
| #100 | Glossary linking and eight new terms |
| #101 | The charter names the three states it has always used; P12 recorded as a fixed point |

## 2. Open, waiting on you

| PR | Decision |
|---|---|
| qmcp #31 | **P17's door exists.** One seam a model is called through, and the six commands three modules named without providing |
| qm (this document's branch) | P17's record names its mechanism by path, and this checklist |

### qmcp #31 is the one to read closely

It is the first thing in this session that **claims a principle is implemented**
rather than stated, so it is the one where a wrong claim costs most.

- The seam ends at the human queue and does not pass it. There is no function in
  `qmcp/governed.py` that answers a question — a test asserts the module offers
  no `approve`, `accept`, `decide` or `answer`, which fails the moment somebody
  adds the convenience function it exists to not have
- **`Bound.seconds` is not enforced and the module says so.** It is measured and
  reported. Nothing interrupts a call. If you want that enforced, it is a
  different change and a harder one
- Six of ten `uv run qmcp ...` commands named in that package's own docstrings
  did not exist. Three are routed, three are named in `ONLY_CLAIMED` with why.
  **Check the three exemptions are gaps you are willing to have open**

## 3. The checklist

Tick what you have actually done. An unticked line is not a failure; it is a
known gap, which is the only kind worth having.

### Ratification — for what the corpus says

- [ ] **P17 reads as a principle and not as a session's lesson.** It was written
      the day its evidence appeared, which is the condition most likely to
      produce a rule that fits one incident
- [ ] **P17's plain form is the one you want quoted back**: *"work yourself out
      of the jobs you are not good at, playing to your strengths"*
- [ ] **The four edge kinds** — `orders`, `completes`, `shares-teeth`,
      `rests-on` — are the right four. A closed vocabulary is expensive to
      change later
- [ ] **The five `none` declarations are honest.** P3, P5, P9, P11, P15. If any
      of them should have an edge, the check will not tell you
- [ ] **The three charter states** map to `earned` / `decorative` / `shared` the
      way you read them
- [ ] **The two new mathematics mappings claim the right amount.** The
      decidability boundary and the fixed point are both marked `earned`, and
      both name what they have not earned
- [ ] **P17's record now names a mechanism by path** — `qmcp/governed.py`. A
      charter principle whose mechanism is one module in one project is a
      narrower claim than it looks; decide whether that is the right scope
      before ratifying it
- [ ] Ratification is five steps and a file rename, and **no automation here
      does any of them**

### The version tag — for what a project ships

- [ ] **Run dossier and use it.** Nothing below replaces this. In particular the
      ring: `m`, then a digit, at three levels
- [ ] **Right-click somewhere.** It opens the ring on the selection. Left-click
      is unchanged
- [ ] **Open Outstanding.** 38 rows here, all from the overview. Selecting one
      runs its remedy — check that is what you want a click to do
- [ ] **`dossier clone` with no arguments.** It lists and stops. Confirm the list
      is repositories you would want, before anybody passes `--all`
- [ ] **Check the docs site renders.** The glossary links are a dotted rule at
      60% opacity; if it reads as noise, the colour is one line in
      `docs/stylesheets/glossary.css` and the tests will hold you to 4.5:1
- [ ] **Run the seam.** `uv run qmcp topology show governed --level 2` draws it;
      `uv run qmcp orchestration plane` says what every shape would do. Both
      commands were named in docstrings and absent from the CLI until now
- [ ] Name the reviewer. **Reviewers are named at the tag and nowhere earlier**

## 4. What went wrong, so you know what to distrust

Three claims were wrong. None was caught by a check.

1. **"Five hand-typed keystrokes are stale."** They were not — `Do` was never
    reordered. I read the Sweep *tab's* new number and assumed the *review* had
    moved. Caught by you asking.
2. **"The tool writes the check."** Contradicted P10 in the same sentence that
    denies the model decision-procedure status. Caught by you asking.
3. **"This comparison was always False."** `DeltaPhase` subclasses `str`, so it
    never was. Caught by a mutation that stayed green — a real bug's mutation
    goes red.

**The shape they share**: each was a plausible reading of true facts. The
corpus's own rule for this is `records/DRAFT-decision-record-discipline.md` §8 —
name the ordinary cause before the interesting one — and knowing the rule did not
prevent any of the three.

**What to distrust most**: any sentence in a pull request body that explains
*why* something was broken. The measurements are checkable and were checked; the
explanations are mine.

## 5. What a check found that no person was looking for

One, and it is worth separating from §4 because it runs the other way — a check
finding something nobody suspected, rather than a person catching a claim.

**Six of ten `uv run qmcp ...` commands named in that package's own docstrings
did not exist.** A seventh, `threads consolidate`, was found by the guard on its
first run: checking the groups by hand had missed it because the group existed
and the subcommand did not.

Nothing was red for any of them. The modules imported, the functions worked and
their tests passed. **This is the shape to look for elsewhere** — every other
repository here has module docstrings naming commands, and none of them has a
check like this one.

## 6. Two things nobody has looked at

- **Six drafted rulesets are unapplied.** `main` is unprotected in every
  repository, so every "never push to main" rule in this corpus is customary
- **A `claude.ai/share/` link may still be live**, from an earlier session. It
  was named in a security review and not revoked
