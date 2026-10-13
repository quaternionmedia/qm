# Going private is an act, and the party who does it owns what follows

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-16 |
| **Namespace** | org |
| **Binds** | This corpus, and any project that adopts it |
| **Pends on** | Ratification. Nothing here is settled. |
| **Restated in** | Nothing yet. |

---

## 1. The decision

**Whoever makes a repository private owns removing its name from this corpus.**

The corpus does not watch for repositories becoming private. It does not hold a
credential in order to ask, it does not carry a list to compare against, and it
does not go red on an unrelated pull request because somebody flipped a
visibility switch in another repository.

`uv run qm private-names` remains, and it remains useful: on a machine that
holds the gitignored companions it reads them, finds every occurrence, and shows
each one with the name replaced by its reference. It is a preflight, not a gate.

## 2. Why the obligation sits there and not here

Detecting the transition requires the corpus to know, continuously, which
repositories in the organisation are private. Every way of knowing that costs
something, and the costs are not small:

| | what it costs |
|---|---|
| An organisation-read credential | the repository's first secret, a rotation duty, and a gate that silently stops working when the token expires |
| A committed list of digests | 24 of 33 names are ordinary words of median length 7 — the list is recoverable by anyone who wants it, which publishes the thing being protected |
| Continuous polling | a check that reads the host, so an unrelated pull request goes red for a reason its author cannot fix |

Each of those is the corpus preparing, at permanent cost, for an event that is
someone's deliberate decision and that they know about at the moment it happens.
**The party flipping the switch has the information already.** Nothing has to be
inferred, watched for, or paid for in advance.

## 3. What the obligation actually is

On making a repository private:

1. Run `uv run qm inventory --write`, so the reference for it exists.
2. Run `uv run qm private-names --context` and remediate what it reports, using
   the reference rather than the name.
3. If an occurrence cannot be removed, declare it in
   `ci/exception-registry.yaml` with a reason and a removal condition.

Note what step 3 admits: **history cannot be remediated.** A name already
published in a public repository's history stays published, and this corpus
forbids the rewrite that would remove it. So the obligation is a forward one,
and the thing it protects is everything written after the switch is flipped,
not everything written before.

## 4. What this gives up, stated plainly

**A repository that goes private today, whose name is already in the tree,
produces no signal.** Nothing goes red. If the party who made it private does
not do §3, the name stays, and the next thing that notices is a person reading.

That is the cost of the decision and it is accepted rather than hidden. It is
the reason `ci/gate-registry.yaml` records `gates: []` for `private-names`: the
corpus states what it does not enforce instead of implying coverage it does not
have.

## 5. Alternatives considered

**Hold an organisation-read secret and gate on it.** Rejected: it buys detection
of an event the deciding party already knows about, in exchange for a permanent
credential, a rotation obligation, and a failure mode where expiry quietly
returns the check to `unverified`.

**Commit digests of the private names.** Rejected on measurement rather than
principle. Of the names this corpus would have to cover, 24 of 33 are all-letter
words with a median length of 7 and a minimum of 3. A digest list of those is
recoverable, so the mechanism would publish a puzzle whose answer is the secret.

**Say nothing and rely on care.** Rejected: that is this decision without the
sentence. Writing it down is what makes the obligation transferable to somebody
who was not in the conversation.
