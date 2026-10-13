# Plan — the thread archive, and getting at it

**Two routes, and they answer different questions.** Snapshots are how the data
arrives; programmatic access is how anything downstream uses it. Neither
replaces the other, and conflating them is why "wire up the APIs" was the wrong
first instruction — it named a mechanism for a job the mechanism cannot do.

**Stamped 2026-08-20.** Figures name the command that produced them. Re-derive
rather than quote.

---

## What is settled, so nobody re-opens it

| | |
|---|---|
| No API exposes claude.ai or chatgpt.com conversation history | They are separate products from the model APIs, with no endpoint that lists threads |
| Requesting an export is the account holder's | `records/DRAFT-acts-that-are-a-persons-by-constitution.md`, and the service enforces it independently |
| A thread is a delta; what it settled is `part-of` it | `records/DRAFT-deltas-compose.md` |
| Every payload names its perspective | `records/DRAFT-granularity-is-a-perspective.md` |
| Nothing unattended spends | `records/DRAFT-no-unattended-spending.md` |

## Route A — snapshots, which work today

Three sources behind one contract, all local, all free, none needing a
credential.

| source | store | what it knows |
|---|---|---|
| `claude` | export cache | the conversation |
| `chatgpt` | export cache | the conversation, as a tree flattened to a sequence |
| `claude-code` | its own session store | the conversation **and the work**: branch, checkout, and the pull requests it produced |

**The third is the interesting one and it was not asked for.** It answers the
question the other two cannot: which repository a thread's deltas belong to. A
conversation belongs to no repository; a session says which one it was in.

### What is left on this route

- **Neither export format is verified.** No real export existed on the machine
  that read them. `--dry-run` is the first move on a real one, and an
  unrecognised conversation is counted and named rather than dropped.
- **The ChatGPT tree is flattened.** Regenerated replies come through as
  alternatives in sequence. Stated rather than hidden; `same-as` exists for the
  day somebody wants to say two branches were one strand.
- **Extraction only finds what was marked.** `DECISION:` and `DECIDED:`.
  Recognising an unmarked decision needs a model, which is Route B's paid half.
- **Retention.** Nothing prunes. Correct now, wrong at scale, and the policy is
  a record nobody has written.

## Route B — programmatic access

Three layers, and only the third involves a vendor.

### B1. A library surface — exists

`qmcp.threads` is importable: `ThreadSource`, `Survey`, `Thread`, `Turn`,
`Decision`, and the index. Anything in-process can already read the archive
without parsing a file. **This is what "programmatic" means most of the time**
and it is done.

### B2. A local service surface — the next build

qmcp already runs a FastAPI server that publishes tools, records invocations,
and holds the human-in-the-loop queue. The archive belongs on it:

    GET  /v1/threads                  what is indexed
    GET  /v1/threads/{source}/{id}    one thread
    GET  /v1/threads/{source}/{id}/deltas
    GET  /v1/threads/diverged         exports disagreeing with an earlier record

**Read-only, and local.** Nothing here writes to the archive, and the archive
holds somebody's conversations — so it binds to loopback like everything else
here, and `handbook/async-contract.md` §4 is the standing rule about that.

*Done* is a second process reading the archive without importing qmcp.

### B3. What a vendor API can actually add — and it is not history

Worth stating precisely, because the tempting summary is wrong in both
directions.

**It cannot add conversations.** No endpoint lists them. That does not change
with a credential, a paid tier, or an organisation account.

**It can add reading.** Extraction today finds only what a conversation marked.
A model call over a thread that marked nothing is the one thing a vendor API
genuinely contributes — and it is the paid path, which means:

- a zero-budget pass establishes how many threads would need reading,
- the number is shown, a person authorises it, and the run spends against it,
- nothing schedules it, and consent does not carry forward.

`qmcp/spend.py` already holds all of that. A `ModelExtractor` behind the
existing `decisions(thread, budget)` signature is the whole change — the
contract was built for it.

**Open, and a person's:** whether an unmarked conversation should be read at
all. Sending an entire thread to a model to find out what it settled is a
different act from marking a decision as you make it, and the cheaper habit may
be the better one.

## Order

1. **B2**, because it is free, local, and unblocks anything else reading the
   archive.
2. **A dashboard over the archive**, which is B2's first consumer and the thing
   that shows whether the archive is worth having.
3. **Retention**, once there is enough archive for it to matter.
4. **B3**, last, and only if marking decisions by hand turns out not to be
   enough.

## What this must not become

**A scheduled importer.** The export is a human act by constitution, and
anything that polled for one would be automating around that rather than up to
it.

**A service that leaves the machine.** The archive is somebody's conversations.
Local, loopback, gitignored, and never rendered anywhere it could be published.

**A board of one row per turn.** A thread is mostly steps. The deltas are what
it settled, and the filter is the design rather than a limitation of it.
