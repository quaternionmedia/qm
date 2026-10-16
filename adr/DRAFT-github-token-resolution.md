# ADR-XXXX — GitHub token resolution order: gh CLI keyring primary, env vars secondary

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | A test of the resolution order, which is unwritten: nothing in `tests/` exercises `resolve_github_token()` or `GET /auth/github` |

## Context

`github_service.py`'s `create_headers()` read `GITHUB_TOKEN` first, and the
`gh` CLI also reads `GITHUB_TOKEN` first when it resolves credentials. A stale
or expired `GITHUB_TOKEN` therefore shadowed a valid `gh` keyring credential
everywhere at once: neither the backend's `httpx` calls nor `gh` itself could
reach GitHub, with `gh auth login` done and a valid keyring token present.
`gh auth status` reported:

```
X Failed to log in to github.com using token (GITHUB_TOKEN)
  - Active account: true          # <- the bad env var is "active"

✓ Logged in to github.com account subcontrabass (keyring)
  - Active account: false         # <- the good keyring token is inactive
```

Clearing a system environment variable is not durable: it has to be cleared
again in every new shell.

## Decision

`resolve_github_token()` in `github_service.py` resolves the token once —
`get_github_token()` calls it on first use, the server's startup hook makes
that first use, and the result is cached. The resolution order is:

1. **`CC_GITHUB_TOKEN`** — the project-specific override. A namespaced
   variable avoids any conflict with system-level or CI `GITHUB_TOKEN`
   variables set for other tooling.
2. **`gh auth token --hostname github.com`** (keyring) — `gh` runs in a
   subprocess with `GITHUB_TOKEN` and `GH_TOKEN` stripped from its
   environment, so it answers with the keyring credential rather than the
   (possibly stale) variable. The timeout is 5 s; if `gh` is not installed or
   times out, this source is skipped.
3. **`GITHUB_TOKEN`, then `GH_TOKEN`** — legacy and Docker Compose
   pass-through, at lower priority so a bad value does not shadow a valid
   keyring token.
4. **Docker secret** — `/run/secrets/github_token`.
5. **Unauthenticated** — 60 requests an hour per IP, with a warning logged at
   startup.

`create_headers()` calls `get_github_token()`, and so does `repo_router.py`,
which has no direct read of `GITHUB_TOKEN`.

`GET /auth/github` returns `{source, authenticated, token_prefix}`, so the
resolution is inspectable without reading server logs. The frontend header
shows a coloured GH indicator (green = authenticated, amber =
unauthenticated) with a tooltip naming the source.

## Consequences

- A developer who runs `gh auth login` and nothing else gets authenticated API
  access, and a stale `GITHUB_TOKEN` in the shell does not decide the outcome
  while the keyring holds a token.
- Docker Compose is served by `CC_GITHUB_TOKEN` (preferred) or `GITHUB_TOKEN`
  (legacy), with no `gh` in the image. Not yet true at codecartographer
  00ce9de: `docker-compose.yml:31` passes only `GITHUB_TOKEN` into the
  container, so a `CC_GITHUB_TOKEN` set on the host does not reach it, and
  under Compose the token resolves as source 3 or 4.
- The token is cached for the life of the process, so a token that expires
  mid-run produces 401s until a restart. `_api_get` retries a 401 once without
  the `Authorization` header, which keeps public repositories readable;
  private ones fail until restart. This is accepted: tokens typically last
  from 8 hours to a year, and a restart is the expected recovery.
- `gh` must be on `PATH` for source 2 to apply. Without it, resolution falls
  through to the environment variables. No new hard dependency.
- `token_prefix` is the token's first eight characters: its kind (`gho_`,
  `ghp_`) and four characters of the secret, served to anything that can reach
  the port. The startup log writes the kind only.

## Alternatives considered

1. **Fix by deleting `GITHUB_TOKEN` from the shell environment** — not
   durable; the problem returns in every new shell or after a system update
   sets the variable again.
2. **Replace all `httpx` GitHub calls with `gh api` subprocess calls** — `gh`
   handles auth completely; rejected as too invasive for this codebase's async
   architecture (a blocking subprocess per API call inside async routes).
3. **Validate `GITHUB_TOKEN` against `/user` before using it** — adds a
   network round-trip on every startup even when the token is good; reading
   the keyring first avoids the bad token rather than detecting it after the
   fact.

## Revision triggers

- The mid-run 401 rate becomes a real complaint (from long-running server
  deployments, say) — add a background refresh or a cache TTL with
  re-resolution.
- A second forge (GitLab, Bitbucket) is supported — generalize
  `resolve_github_token()` into a per-host resolver.
- `gh auth token`'s output format changes — watch `gh` major version bumps.
- A test of the resolution order is written — the `Pends on` row is then
  answered.

## Amendments

*None.*
