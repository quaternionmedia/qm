# Orchestration for `/design-review`

Three Workflow scripts, one per launch, with the lead working in the session
between them. Each maps onto phases of `handbook/design-review-runbook.md`,
and the prompts restate that page's rules rather than add any. Everything
specific to a target arrives in `args`; edit a prompt only where the target's
own `AGENTS.md` says something the runbook does not.

`args.rules` is the block every agent receives. Build it from the target
before the first launch:

```text
RULES (non-negotiable):
- Runtime: <how to run the tool chain here>.
- An agent silent for about three minutes is killed. Run anything over ~90 s in
  the background with its output to a file, and poll it every 30-60 s. Put a
  timeout under 170 s on foreground commands. Keep shell lines plain and
  literal: one command per call, no runtime variables or redirects near git.
- NEVER TOUCH: <every device, port and service a test could reach; servers
  other sessions hold>.
- Commits: <the target's contributorship rule; in the QM estate the owner is
  the author, no co-author trailer, no tool as author>. Subject: one sentence
  saying what is now true. Body: why, with evidence; it ends with
  "Tools: <tool>, under review; <role> of the design review."
- Never stage a submodule pin. Format or auto-fix only files you changed.
- No narrative in code, docs or commit bodies. No number a command computes
  goes in prose; name the command.
- Do not push.
```

## 1. `design-review-audit`: phases 1 and 3

`args`: `{ repo, commit, scratch, purpose, outOfScope, charge, rules, areas:
[{key, brief}], done: ['area:id'], doneNote, skepticCap }`. Each `done`
entry is `area:id`, the runbook's join key; a bare id matches nothing. `skepticCap` is the
count the owner confirmed. Deletions past it are returned unverified rather
than launched; confirm a new cap and resume from the run id, and the audits
replay from cache.

```js
export const meta = {
  name: 'design-review-audit',
  description: 'Audit one repository area by area with evidence, and send a skeptic to every deletion',
  phases: [{ title: 'Audit' }, { title: 'Verify' }],
}
const A = args
const s = { type: 'string' }, n = { type: 'number' }, b = { type: 'boolean' }
const obj = (properties) => ({ type: 'object', properties, required: Object.keys(properties) })
const FINDING = obj({ id: s, title: s,
  kind: { type: 'string', enum: ['delete', 'merge', 'simplify', 'fix-bug', 'speed-up', 'rewrite', 'harden', 'document'] },
  severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
  evidence: s, impact: s, recommendation: s, files: { type: 'array', items: s },
  lines_saved: n, seconds_saved: n, risk: s })
const AUDIT = obj({ area: s, objective_fit: s, metrics: s, verdict: s,
  findings: { type: 'array', items: FINDING }, keep: { type: 'array', items: s } })
const VERDICT = obj({ refuted: b, reason: s, correction: s, evidence: s })

const COMMON = `Repository: ${A.repo} at ${A.commit}. READ-ONLY: never edit, commit or switch branches there; scratch files only under ${A.scratch}.
What it is for: ${A.purpose}. Out of scope: ${A.outOfScope}.
The owner's charge, verbatim: "${A.charge}"
Tools: read, grep, git log/blame, one-line interpreters, dead-code and complexity tools, tests on NAMED files only. The shared profile is under ${A.scratch}: read it, never re-run a whole suite.
${A.rules}`

const key = (a, f) => `${a.key}:${f.id}`
let launched = 0
const audits = await pipeline(A.areas,
  (a) => agent(`${COMMON}

Audit ONE area: what should be deleted, merged, simplified, sped up or fixed. Be brutal and specific: file and line, lines counted, seconds measured. No praise, no hedging, no style nits; narrative a maintainer does not need is weight. Every finding carries evidence (file:line, what is there, and where you can, the command and its actual output), the cost today, a concrete recommendation, estimated lines and seconds saved, and what could break. Everything genuinely fine goes in keep, one line each, so the triage leaves it alone.
AREA ${a.key}: ${a.brief}`, { label: `audit:${a.key}`, phase: 'Audit', schema: AUDIT }),
  (audit, a) => {
    if (!audit) return null
    const cuts = audit.findings.filter((f) => f.kind === 'delete' && !A.done.includes(key(a, f)))
    const room = Math.max(0, A.skepticCap - launched)
    launched += Math.min(room, cuts.length)
    return parallel(cuts.slice(0, room).map((f) => () => agent(`${COMMON}

You are a skeptic. Try to REFUTE this finding. Verify the evidence at the cited lines. Search for callers the auditor missed: templates, scripts, tests, docs, the CLI, string references, entry points, and other repositories that consume this one. Refute it if the evidence is wrong, the thing is used, or the cut breaks a user path, a CI gate or a governance rule. If it is right but overstated, uphold it and say in correction what to trim.
FINDING: ${JSON.stringify(f)}`, { label: `verify:${a.key}:${f.id}`, phase: 'Verify', effort: 'low', schema: VERDICT })
      .then((v) => ({ id: f.id, verdict: v }))))
      .then((vs) => ({ ...audit, key: a.key,
        findings: audit.findings.map((f) => ({ ...f, verdict: (vs.filter(Boolean).find((v) => v.id === f.id) || {}).verdict || null })) }))
  })
const done = audits.filter(Boolean)
const open = (a, f) => !A.done.includes(key(a, f))
// A deletion with no verdict (past the cap, or its skeptic died) is not upheld.
const unverified = done.flatMap((a) => a.findings.filter((f) => open(a, f) && f.kind === 'delete' && !f.verdict).map((f) => key(a, f)))
if (unverified.length) log(`${unverified.length} deletions have no verdict; confirm a cap and resume to verify them`)
return {
  upheld: done.map((a) => ({ ...a, findings: a.findings.filter((f) => open(a, f) && (f.kind !== 'delete' || (f.verdict && !f.verdict.refuted))) })),
  refuted: done.flatMap((a) => a.findings.filter((f) => f.verdict && f.verdict.refuted).map((f) => ({ area: a.key, ...f }))),
  unverified,
  missing: A.areas.filter((a) => !done.some((d) => d.key === a.key)).map((a) => a.key),
}
```

The triage is one agent, launched by the lead once the upheld set is read. Its
prompt is phase 4 of the runbook, followed by the done paragraph, the upheld
findings with the instruction to apply each skeptic's correction, and the
refuted list with the instruction that none of it returns. Its schema is the
runbook's six outputs; a workstream is `{id, name, priority, goal, files,
steps, checks, risk, closes, lines_saved, seconds_saved}`.

Between launches the lead writes one brief per workstream to
`<scratch>/ws/<id>.json`: the triage's fields, the full text of each finding
it closes, and `adjust`.

## 2. `design-review-execute`: phase 5

`args`: `{ repo, scratch, rules, fast, exclusive, lanes: [{ name, ids, base,
merges, exclusive }] }`. A lane's `base` is the tip it stacks on; `merges`
are branches from other lanes it needs first. Exactly one lane has
`exclusive: true`.

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

const prompt = (id, base, merges, exclusive) => `You are executing ONE workstream of a design review of ${A.repo}, in a fresh git worktree.
Read ${A.scratch}/ws/${id}.json first: goal, owned files, ordered steps, checks, risk, the findings it closes, and adjust -- the lead's overrides, which WIN over the steps.
Other workstreams have landed since the brief was written: re-locate lines by content, and if a step is done or moot, skip it and say so.
SETUP: git switch -c review/${id.toLowerCase()} ${base}. If that branch exists, check it out and build on it: a killed attempt left its work there; inspect any leftovers. ${merges.map((m) => `Then git merge --no-edit ${m}.`).join(' ')}
Copy ignored caches with plain file tools; never run git against the main checkout.
TESTS: ${A.fast}. ${exclusive ? `You are the only lane allowed ${A.exclusive}: run the files you touch, then the whole suite once, in the background.` : `Never run ${A.exclusive} or start a server: another lane owns them. List any such check you need in notes.`}
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

A lane whose agent failed may still have committed. Before relaunching,
check `git log <base>..review/<id>` and save any uncommitted work in its
worktree as a patch that the brief's `adjust` names.

## 3. `design-review-change`: phase 7, and the lead's own follow-ups

`args`: `{ repo, base, scratch, rules, spec, fast, all, lenses: [{ key, text
}], build: bool, branch }`. `spec` quotes the owner's answer verbatim and
the lead's reading of it. The usual lenses: correctness, by running every
path; test value, with the implementation reverted to `base` so each new test
must fail, and the fast tier timed on both; scope, docs and commits.

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
for (let round = 1; round <= 3; round++) {
  if (found.length) {
    const r = await agent(`In a fresh worktree of ${A.repo}: git switch -c ${A.branch}-r${round} ${tip}.
Several findings below may be one defect seen through different lenses: group them first. Reproduce each; fix what is real, with a test that fails first; reject what is not, with evidence. One line per finding in notes: fixed, duplicate of, or rejected and why.
SPEC: ${A.spec}
FINDINGS: ${JSON.stringify(found)}
TESTS: ${A.fast}. Finish green; leave git status clean.
${tail}`, { label: `fix:r${round}`, phase: 'Fix', isolation: 'worktree', schema: RESULT }).catch(() => null)
    // A dead or empty fix round is never read as "nothing to fix".
    if (!r || r.status === 'failed' || !r.branch) return { stopped: `fix round ${round}`, tip, open: found, reviews }
    tip = r.branch
  }
  const g = await agent(`Final gate, in a fresh worktree of ${A.repo}: git switch --detach ${tip}. Fix nothing. Run and report each with its actual outcome: ${A.all}; the behaviour the spec promises, exercised; git log --format=%B ${A.base}..${tip}, counting Co-authored-by lines yourself (expect 0); git log --format='%G? %h %s' ${A.base}..${tip} (expect no N where the repository gates signatures); git diff --stat ${A.base}..${tip}. Findings are only failures you saw.
SPEC: ${A.spec}
${tail}`, { label: `gate:r${round}`, phase: 'Gate', isolation: 'worktree', schema: FOUND }).catch(() => null)
  if (!g) return { stopped: `gate round ${round}`, tip, open: found, reviews }
  if (!g.findings.length) return { tip, reviews, gate: g }
  found = g.findings
}
return { stopped: 'still red after three rounds', tip, open: found, reviews }
```

For a governance decision the same shape runs with different stages: research
by execution in a scratch worktree; a draft written in place on the project's
records branch, after checking the tree is clean, the branch is right and it
equals its remote; lenses for the drafting contract, the facts by execution,
and consistency with the other records; one deduplicated fix round; the
record lint. The code for it waits for a person to ratify.
