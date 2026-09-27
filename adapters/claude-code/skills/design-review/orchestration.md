# Orchestration for `/design-review`

One Workflow script per launch, with the lead working in the session between
them. Each maps onto phases of `handbook/design-review-runbook.md`, and the
prompts restate that page's rules rather than add any. Everything specific to a
target arrives in `args`; edit a prompt only where the target's own `AGENTS.md`
says something the runbook does not.

The audit and verify launches read a checkout nothing else touches. Before the
first launch the lead runs `git worktree add --detach <path> <commit>` and
passes that path as `tree`. Phase 2's fixes go in worktrees of their own, so no
branch switch or suite run moves the files under a reader.

`args.rules` is the block every agent receives. Build it from the target
before the first launch:

```text
RULES (non-negotiable):
- Runtime: <how to run the tool chain here>.
- An agent that stays silent is killed and restarted. Run anything over ~90 s
  in the background with its output to a file, and poll it every 30-60 s. Put
  a timeout under 170 s on foreground commands. Keep shell lines plain and
  literal: one command per call, no runtime variables or redirects near git.
- NEVER TOUCH: <every device, port and service a test could reach; servers
  other sessions hold>.
- Commits: <the target's contributorship rule and commit style, read from its
  AGENTS.md and its log; in qm the owner is the author and the message is one
  line saying what is now true, with nothing after it: no body, no trailer, no
  tool named>.
- Never stage a submodule pin. Format or auto-fix only files you changed.
- No narrative in code, docs or commit messages. No number a command computes
  goes in prose; name the command.
- Do not push.
```

## 1. `design-review-audit`: phase 1

`args`: `{ repo, commit, tree, scratch, purpose, outOfScope, charge, rules,
areas: [{key, brief}] }`. It returns the audits, the areas that returned
nothing, and the `area:id` of every deletion. An id repeated within one area
gets a suffix, so `area:id` stays the join key for everything after.

```js
export const meta = {
  name: 'design-review-audit',
  description: 'Audit one repository area by area, with evidence and a keep list',
  phases: [{ title: 'Audit' }],
}
const A = args
const s = { type: 'string' }, n = { type: 'number' }
const obj = (properties) => ({ type: 'object', properties, required: Object.keys(properties) })
const FINDING = obj({ id: s, title: s,
  kind: { type: 'string', enum: ['delete', 'merge', 'simplify', 'fix-bug', 'speed-up', 'rewrite', 'harden', 'document'] },
  severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
  evidence: s, impact: s, recommendation: s, files: { type: 'array', items: s },
  lines_saved: n, seconds_saved: n, risk: s })
const AUDIT = obj({ area: s, objective_fit: s, metrics: s, verdict: s,
  findings: { type: 'array', items: FINDING }, keep: { type: 'array', items: s } })

const COMMON = `Repository: ${A.repo} at ${A.commit}, checked out at ${A.tree}. READ-ONLY: read there; never edit, commit or switch branches in it; scratch files only under ${A.scratch}.
What it is for: ${A.purpose}. Out of scope: ${A.outOfScope}.
The owner's charge, verbatim: "${A.charge}"
Tools: read, grep, git log/blame, one-line interpreters, dead-code and complexity tools, tests on NAMED files only. The shared profile is under ${A.scratch}: read it, never re-run a whole suite.
${A.rules}`

const unique = (findings) => {
  const used = new Set()
  return findings.map((f) => { let id = f.id, k = 1; while (used.has(id)) id = `${f.id}-${++k}`; used.add(id); return { ...f, id } })
}
const audits = (await parallel(A.areas.map((a) => () => agent(`${COMMON}

Audit ONE area: what should be deleted, merged, simplified, sped up or fixed. Be brutal and specific: file and line, lines counted, seconds measured. No praise, no hedging, no style nits; narrative a maintainer does not need is weight. Every finding carries evidence (file:line, what is there, and where you can, the command and its actual output), the cost today, a concrete recommendation, estimated lines and seconds saved, and what could break. Everything genuinely fine goes in keep, one line each, so the triage leaves it alone.
AREA ${a.key}: ${a.brief}`, { label: `audit:${a.key}`, phase: 'Audit', schema: AUDIT })
  .then((r) => r && { ...r, key: a.key, findings: unique(r.findings) })))).filter(Boolean)
const missing = A.areas.filter((a) => !audits.some((d) => d.key === a.key)).map((a) => a.key)
if (missing.length) log(`no audit returned for: ${missing.join(', ')}`)
return { audits, missing, deletions: audits.flatMap((a) => a.findings.filter((f) => f.kind === 'delete').map((f) => `${a.key}:${f.id}`)) }
```

## 2. `design-review-verify`: phase 3

Launched once every audit has landed and phase 2's fixes are on the done list.
`args`: the audit's `{ repo, commit, tree, scratch, purpose, outOfScope,
charge, rules }`, plus `{ audits, done: ['area:id'], judged, consumers,
confirmed }`.

- The open deletions are the audit's deletions less the done list. `judged`
  maps `area:id` to a verdict from an earlier verify launch, and those are not
  sent again.
- `confirmed` is the count the owner confirmed. The script lists what it would
  send, in area order and then finding order, and launches nothing unless the
  list is exactly that long.
- `consumers` names the repositories that consume this one and how to search
  them, or says that none do. A place a skeptic could not search refutes the
  cut.

It returns the upheld findings, the refuted ones, the deletions whose skeptic
died (`unverified`), and `judged` with the new verdicts added. A retry passes
that `judged` back and confirms the count of what is left.

```js
export const meta = {
  name: 'design-review-verify',
  description: 'Send one skeptic to each open deletion, once the owner has confirmed the exact count',
  phases: [{ title: 'Verify' }],
}
const A = args
const s = { type: 'string' }
const VERDICT = { type: 'object', required: ['refuted', 'reason', 'correction', 'evidence', 'searched'], properties: {
  refuted: { type: 'boolean' }, reason: s, correction: s, evidence: s,
  searched: { type: 'array', items: s, description: 'every place searched for a caller, each with the command used' } } }

const COMMON = `Repository: ${A.repo} at ${A.commit}, checked out at ${A.tree}. READ-ONLY: read there; never edit, commit or switch branches in it; scratch files only under ${A.scratch}.
What it is for: ${A.purpose}. Out of scope: ${A.outOfScope}.
The owner's charge, verbatim: "${A.charge}"
Tools: read, grep, git log/blame, one-line interpreters, dead-code and complexity tools, tests on NAMED files only. The shared profile is under ${A.scratch}: read it, never re-run a whole suite.
${A.rules}`

if (!A.consumers) return { refused: 'consumers is missing: name the repositories that consume this one and how to search them, or say none do' }
const done = new Set(A.done), judged = { ...(A.judged || {}) }
const key = (a, f) => `${a.key}:${f.id}`
// Area order, then finding order: the same audits, done list and verdicts always send the same skeptics.
const open = A.audits.flatMap((a) => a.findings.filter((f) => f.kind === 'delete' && !done.has(key(a, f))).map((f) => ({ k: key(a, f), f })))
const send = open.filter((c) => !judged[c.k])
if (send.length !== A.confirmed) return { refused: `${send.length} deletions to send and ${A.confirmed} confirmed; nothing launched`, send: send.map((c) => c.k) }

const verdicts = await parallel(send.map((c) => () => agent(`${COMMON}

You are a skeptic. Try to REFUTE this finding. Verify the evidence at the cited lines. Search for callers the auditor missed: templates, scripts, tests, docs, the CLI, string references, entry points, and the repositories that consume this one: ${A.consumers}. Refute it if the evidence is wrong, the thing is used, or the cut breaks a user path, a CI gate or a governance rule. Refute it as well if there is a place above you could not search, and name that place in reason: a cut stands only where every place was searched and nothing was found. List each place you searched, with its command, in searched. If it is right but overstated, uphold it and say in correction what to trim.
FINDING: ${JSON.stringify(c.f)}`, { label: `verify:${c.k}`, phase: 'Verify', effort: 'low', schema: VERDICT })))
send.forEach((c, i) => { if (verdicts[i]) judged[c.k] = verdicts[i] })

// A deletion whose skeptic died has no verdict, and is not upheld.
const unverified = open.filter((c) => !judged[c.k]).map((c) => c.k)
if (unverified.length) log(`${unverified.length} deletions have no verdict; pass judged back and confirm that count to retry them`)
const verdict = (a, f) => judged[key(a, f)]
const isOpen = (a, f) => !done.has(key(a, f))
return {
  upheld: A.audits.map((a) => ({ ...a, findings: a.findings
    .filter((f) => isOpen(a, f) && (f.kind !== 'delete' || (verdict(a, f) && !verdict(a, f).refuted)))
    .map((f) => (f.kind === 'delete' ? { ...f, verdict: verdict(a, f) } : f)) })),
  refuted: A.audits.flatMap((a) => a.findings
    .filter((f) => f.kind === 'delete' && isOpen(a, f) && verdict(a, f) && verdict(a, f).refuted)
    .map((f) => ({ area: a.key, ...f, verdict: verdict(a, f) }))),
  unverified,
  judged,
}
```

## 3. `design-review-triage`: phase 4

Launched by the lead once the upheld set is read. `args`: `{ repo, runbook,
rules, doneNote, upheld, refuted }`, where `runbook` is the path the lead read
the runbook from and `doneNote` is phase 2's paragraph on what is done. One
agent, returning the runbook's six outputs.

```js
export const meta = {
  name: 'design-review-triage',
  description: 'Triage the upheld findings into a verdict, an objective, workstreams, not-now and keep',
  phases: [{ title: 'Triage' }],
}
const A = args
const s = { type: 'string' }, n = { type: 'number' }
const list = (items) => ({ type: 'array', items })
const obj = (properties) => ({ type: 'object', properties, required: Object.keys(properties) })
const WORKSTREAM = obj({ id: s, name: s, priority: { type: 'string', enum: ['now', 'next', 'plan only'] }, goal: s,
  files: list(s), steps: list(s), checks: list(s), risk: s, closes: list(s), lines_saved: n, seconds_saved: n })
const TRIAGE = obj({ verdict: s, objective: s, target_shape: s, workstreams: list(WORKSTREAM),
  not_now: list(obj({ finding: s, reason: s, waits_on: s })), keep: list(s) })

return await agent(`Triage the design review of ${A.repo}. Read phase 4 of ${A.runbook} and return its six outputs.
Apply each skeptic's correction. Deduplicate across areas, and put no file in two workstreams. A workstream's closes lists the area:id of each finding it closes. A refuted finding never returns. A question for the owner is never a step: it goes in not_now, waiting on the owner.
DONE, already fixed; build on it and schedule none of it: ${A.doneNote}
UPHELD: ${JSON.stringify(A.upheld)}
REFUTED: ${JSON.stringify(A.refuted)}
${A.rules}`, { label: 'triage', phase: 'Triage', schema: TRIAGE })
```

Between launches the lead writes one brief per workstream to
`<scratch>/ws/<id>.json`: the triage's fields, the full text of each finding
it closes, and `adjust`.

## 4. `design-review-execute`: phase 5

`args`: `{ repo, scratch, rules, fast, exclusive, lanes: [{ name, ids, base,
merges, exclusive }] }`. A lane's `base` is the tip it stacks on; `merges`
are branches from other lanes it needs first. At most one lane has
`exclusive: true`, and the script refuses more. A workstream's branch is
`review/<id>` in lower case.

```js
export const meta = {
  name: 'design-review-execute',
  description: 'Execute triaged workstreams in lanes, one worktree each, each lane stacking on its own last tip',
  phases: [{ title: 'Lanes' }],
}
const A = args
const s = { type: 'string' }
const RESULT = { type: 'object', required: ['status', 'branch', 'head_sha', 'commits', 'done_steps', 'skipped_steps', 'checks', 'lines_removed', 'notes'],
  properties: { status: { type: 'string', enum: ['done', 'partial', 'failed'] }, branch: s, head_sha: s,
    commits: { type: 'array', items: s }, done_steps: { type: 'array', items: s },
    skipped_steps: { type: 'array', items: { type: 'object', required: ['step', 'why'], properties: { step: s, why: s } } },
    checks: { type: 'array', items: { type: 'object', required: ['command', 'outcome'], properties: { command: s, outcome: s } } },
    lines_removed: { type: 'number' }, notes: s } }

const owners = A.lanes.filter((l) => l.exclusive).map((l) => l.name)
if (owners.length > 1) return { refused: `lanes ${owners.join(', ')} are all exclusive; at most one may be` }

const prompt = (id, base, merges, exclusive) => `You are executing ONE workstream of a design review of ${A.repo}, in a fresh git worktree.
Read ${A.scratch}/ws/${id}.json first: goal, owned files, ordered steps, checks, risk, the findings it closes, and adjust -- the lead's overrides, which WIN over the steps.
Other workstreams have landed since the brief was written: re-locate lines by content, and if a step is done or moot, skip it and say so.
SETUP: git switch -c review/${id.toLowerCase()} ${base}. If that branch exists, check it out and build on it: a killed attempt left its work there; inspect any leftovers. If git says another worktree holds the branch, stop: report failed, name that worktree in notes, and change nothing in it. ${merges.map((m) => `Then git merge --no-edit ${m}.`).join(' ')}
Copy ignored caches with plain file tools; never run git against the main checkout.
TESTS: ${A.fast}. ${exclusive ? `You are the only lane allowed ${A.exclusive}: run the files you touch, then the whole suite once, in the background.` : `Never run ${A.exclusive} or start a server: ${owners.length ? 'another lane owns them' : 'the lead runs them'}. List any such check you need in notes.`}
Every new test fails against ${base} first. Stay in your files; a test elsewhere that must follow a behaviour change is changed and named in notes. Finish green. Skip a step that proves wrong, with the reason. If you cannot get green: git reset --hard ${base} and report failed. Leave git status clean.
${A.rules}`

async function lane(l) {
  let tip = l.base, merges = l.merges || []
  const results = []
  for (const id of l.ids) {
    const r = await agent(prompt(id, tip, merges, !!l.exclusive), { label: `ws:${id}`, phase: 'Lanes', isolation: 'worktree', schema: RESULT })
      .catch((e) => ({ status: 'failed', notes: String(e).slice(0, 300) }))
    const res = { id, ...(r || { status: 'failed', notes: 'no result' }) }
    results.push(res)
    log(`${l.name} ${id}: ${res.status}`)
    if (res.status !== 'failed' && res.branch) { tip = res.branch; merges = [] }
  }
  return { lane: l.name, tip, results }
}
// parallel() never rejects: one dead workstream fails itself and nothing else.
return await parallel(A.lanes.map((l) => () => lane(l)))
```

Docs and CI describe the result, so they run as a second launch: one lane,
`base` the exclusive lane's tip, `merges` the other lanes' tips.

A lane whose agent failed may still have committed. Before relaunching, check
`git log <base>..review/<id>`, save any uncommitted work in its worktree as a
patch that the brief's `adjust` names, and then remove that worktree
(`git worktree remove <path>`): git will not check the branch out in a second
one. Relaunch fresh rather than with the run id. The prompt names the brief by
its path, so editing the brief leaves the prompt as it was, and a resume
replays the cached failure. The fresh launch's lanes carry only the unfinished
workstreams, each `base` at its lane's last landed tip.

## 5. `design-review-change`: phase 7, and the lead's own follow-ups

`args`: `{ repo, base, scratch, rules, spec, fast, all, lenses: [{ key, text
}], build: bool, branch }`. `spec` quotes the owner's answer verbatim and
the lead's reading of it. The usual lenses: correctness, by running every
path; test value, with the implementation reverted to `base` so each new test
must fail, and the fast tier timed on both; scope, docs and commits.

Every return carries `rounds`: each fix round's findings and its notes, which
say how each finding was settled, so the lead reads the rejected ones as well
as the fixed. The gate puts the signature check in `signatures` rather than
among its findings: signing is the lead's step, and no fix round is asked to
do it. A relaunch takes a new `branch`, because the last run's branch and its
`-rN` rounds still exist, held by their worktrees until those are removed.

```js
export const meta = {
  name: 'design-review-change',
  description: 'Build one decided change, review it through separate lenses, fix, and gate it until green',
  phases: [{ title: 'Build' }, { title: 'Review' }, { title: 'Fix' }, { title: 'Gate' }],
}
const A = args
const s = { type: 'string' }
const RESULT = { type: 'object', required: ['status', 'branch', 'head_sha', 'notes'], properties: {
  status: { type: 'string', enum: ['done', 'partial', 'failed'] }, branch: s, head_sha: s, notes: s } }
const FOUND = { type: 'object', required: ['verdict', 'findings'], properties: { verdict: s, findings: { type: 'array', items: {
  type: 'object', required: ['severity', 'title', 'evidence', 'fix'], properties: {
    severity: { type: 'string', enum: ['high', 'medium', 'low'] }, title: s,
    evidence: { type: 'string', description: 'the command you ran and its actual output' }, fix: s } } } } }
const GATE = { ...FOUND, required: [...FOUND.required, 'signatures'], properties: { ...FOUND.properties,
  signatures: { type: 'string', description: "the output of git log --format='%G? %h %s' for the range" } } }
const tail = A.rules

let tip = A.branch
if (A.build) {
  const r = await agent(`In a fresh worktree of ${A.repo}: git switch -c ${A.branch} ${A.base}. Make what the spec offers true, and add nothing beyond it.
SPEC: ${A.spec}
TESTS: ${A.fast}. Every new test fails against ${A.base} first; say in notes how you saw it fail. Finish green; leave git status clean.
${tail}`, { label: 'build', phase: 'Build', isolation: 'worktree', schema: RESULT }).catch(() => null)
  if (!r || r.status === 'failed') return { stopped: 'build', result: r }
  tip = r.branch
}
const reviews = (await parallel(A.lenses.map((l) => () => agent(`Adversarially review ${A.base}..${tip} in a fresh worktree of ${A.repo} (git switch --detach ${tip}; never commit).
SPEC: ${A.spec}
LENS ${l.key}: ${l.text}
Only real defects, each with evidence you produced by running something, and a concrete fix. Empty is an answer.
${tail}`, { label: `review:${l.key}`, phase: 'Review', isolation: 'worktree', schema: FOUND })
  .then((r) => r && { lens: l.key, ...r })))).filter(Boolean)
// A lens that died is not a lens that found nothing.
const lost = A.lenses.filter((l) => !reviews.some((r) => r.lens === l.key)).map((l) => l.key)
if (lost.length) return { stopped: 'review', lost, tip, reviews }
let found = reviews.flatMap((r) => r.findings.map((f) => ({ lens: r.lens, ...f })))
const rounds = []
for (let round = 1; round <= 3; round++) {
  if (found.length) {
    const r = await agent(`In a fresh worktree of ${A.repo}: git switch -c ${A.branch}-r${round} ${tip}.
Several findings below may be one defect seen through different lenses: group them first. Reproduce each; fix what is real, with a test that fails first; reject what is not, with evidence. One line per finding in notes: fixed, duplicate of, or rejected and why.
SPEC: ${A.spec}
FINDINGS: ${JSON.stringify(found)}
TESTS: ${A.fast}. Finish green; leave git status clean.
${tail}`, { label: `fix:r${round}`, phase: 'Fix', isolation: 'worktree', schema: RESULT }).catch(() => null)
    rounds.push({ round, findings: found, result: r })
    // A dead or empty fix round is never read as "nothing to fix".
    if (!r || r.status === 'failed' || !r.branch) return { stopped: `fix round ${round}`, tip, open: found, reviews, rounds }
    tip = r.branch
  }
  const g = await agent(`Final gate, in a fresh worktree of ${A.repo}: git switch --detach ${tip}. Fix nothing. Run and report each with its actual outcome: ${A.all}; the behaviour the spec promises, exercised; git log --format=%B ${A.base}..${tip}, counting Co-authored-by lines yourself (expect 0); git diff --stat ${A.base}..${tip}. Findings are only failures you saw. Put the output of git log --format='%G? %h %s' ${A.base}..${tip} in signatures, and do not make an unsigned commit a finding: signing is the lead's step.
SPEC: ${A.spec}
${tail}`, { label: `gate:r${round}`, phase: 'Gate', isolation: 'worktree', schema: GATE }).catch(() => null)
  if (!g) return { stopped: `gate round ${round}`, tip, open: found, reviews, rounds }
  if (!g.findings.length) return { tip, reviews, rounds, gate: g }
  found = g.findings
}
return { stopped: 'still red after three rounds', tip, open: found, reviews, rounds }
```

For a governance decision the same shape runs with different stages: research
by execution in a scratch worktree; a draft written in place on the project's
records branch, after checking the tree is clean, the branch is right and it
equals its remote; lenses for the drafting contract, the facts by execution,
and consistency with the other records; one deduplicated fix round; the
record lint. The code for it waits for a person to ratify.
