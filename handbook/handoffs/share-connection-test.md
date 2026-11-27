# Handoff — reach the shared alfred from another device

**Stamped 2026-11-27.** `qm` `main` at `ce255b9`; `alfred`
`feat/sharing-the-family` at `323448b`, open and ready as alfred#169 on
`feat/who-spoke` at `efa270d`. Every figure here was true at those commits and
on that day, and nowhere else: re-derive each before acting on it.

The rule this tests is `records/DRAFT-a-familys-dev-state-is-shared-to-invited-devices.md`.
alfred's share is `./al share`, documented in alfred's `docs/share.md`, and
the page an invited person follows is alfred's `docs/join.md`, both on
alfred#169's branch.

## What is not yet established

Every check of the share so far ran on its host: the members answering, the
login rules, a snapshot round trip, and the joining page at a phone's width
over the share's network address. **No device other than the host has
reached the share.** A request from the host to its own network address
never crosses its firewall or the overlay network, so none of those checks
says that an invited device gets in. `handbook/handoffs/qm-queue.md` §5
carries this as not verified.

**Done** is both tests below run, each result recorded with the commit it
was true at, the §5 entry replaced by what was established, and every place
`docs/join.md` or `./al share` was wrong fixed on alfred#169's branch, or on a
branch stacked on it.

## What exists now

- **The share runs on one host**, with every member at the commits its
  manifest names. Ask it before trusting anything below: `./al share`, from
  a checkout of alfred#169's branch, lists each member, its ref and commit,
  each address, and whether it is `serving`, and exits non-zero otherwise.
  At the stamp it listed alfred at `323448b` on `127.0.0.1:17320` and
  `10.173.20.1:17320`, joe at `b2c0d00` and looksatwords at `01da481`, both
  on loopback, all `serving`.
- **The share's private network** is a ZeroTier network whose controller is
  the host's own ZeroTier One. The host is `10.173.20.1` on it, and invited
  devices are given addresses in `10.173.20.0/24`. The network's id is in the
  share's machine-scoped manifest and is never committed;
  `./al share invite` prints it.
- **The host's firewall**, at the stamp, classed the share network's adapter
  as a public network, and had inbound rules allowing Docker Desktop's
  backend on public and private networks. Whether a remote device's request
  reaches alfred through them is the first thing the tests below establish:
  that it does is an inference from the rules' names, nothing more.

## Test 1 — a second ZeroTier node, in a container on the host

An agent can run most of this alone. It exercises joining, authorization, the
route to `10.173.20.1`, the host's firewall on the share network's adapter,
and alfred answering a request that arrived over the network. It does not
exercise two devices on different networks finding each other, a relay, a
phone's VPN, or the joining page.

1. **Ask before downloading.** ZeroTier's own recipe
   (<https://docs.zerotier.com/docker/>) runs an `ubuntu:24.04` container
   with `--cap-add=NET_ADMIN --device=/dev/net/tun`, installs ZeroTier with
   `curl` and the script at `https://install.zerotier.com/`, starts it with
   `/usr/sbin/zerotier-one -d` and joins with
   `/usr/sbin/zerotier-cli join <network id>`. The image and the package are
   downloads: name each, its source and its size to the person, and wait.
   Read the page again before running it; do not carry its flags from here.
2. **The container's node id**: `/usr/sbin/zerotier-cli info` in it prints
   it, ten hex digits.
3. **Authorizing it is the person's.** It reads ZeroTier One's token, which
   only an administrator can read: from a shell started as administrator, in
   a checkout of alfred#169's branch,
   `python scripts/share.py network authorize <node id> --name "container test"`.
   The session never reads the token.
4. **Established, or not**: in the container,
   `/usr/sbin/zerotier-cli listnetworks` shows the network `OK` with an
   address in `10.173.20.0/24`; then `curl -s http://10.173.20.1:17320/openapi.json`
   answers with the title `Alfred API`. A 200 alone proves only that
   something listens.
5. **Clean up**: `network revoke <node id>`, the person's again; remove the
   container; ask before removing an image this test pulled.

**A red here may be the scaffolding.** Docker Desktop carries a container's
traffic through the host, so a container that cannot reach the host's
ZeroTier node says nothing about an invited device. Before reporting the
share at fault, establish which side failed: whether the container's node
reaches `OK`, and whether it reaches any peer.

If the network is `OK` and the request times out, the host's firewall is the
likely holder. Opening port 17320 on the share network's adapter is a change
to a security setting: state the rule, the adapter and what it exposes, and
the person decides and runs it.

## Test 2 — a phone, away from the host's network, following the page

This needs a person and their phone; the session drives and records.

1. `./al share invite --name <who>` prints the invitation. Hand it to the
   person; it holds no password.
2. The person turns the phone's Wi-Fi off, so it reaches the host over mobile
   data, and follows alfred's `docs/join.md` as written, step by step. At
   every step, record where the words differ from the screen: a button's
   name, what the app calls the device id, what the phone asks.
3. The person authorizes the phone's device id, elevated, as in Test 1.
4. The person makes the account: `./al share account <email> --name <first>`
   asks for the password twice. The session never sees or types it.
5. The phone opens the link, logs in, opens the guide at `/docs/join/`, and
   starts *A first video* from alfred's `docs/journeys.md`.
6. Record what worked, each mismatch, and the time a step took; then revoke
   the phone if it is not staying.

A phone on the host's own Wi-Fi may reach it directly over the local network,
which is a weaker test than mobile data: say which was run.

## What else could produce the result

- **The host asleep**, or the share stopped: `./al share` first, every time.
- **Another VPN on the phone**: a phone runs one VPN at a time.
- **The address**: `http://`, not `https://`, and `:17320`.
- **A device not yet authorized**: ZeroTier shows it as access denied.
- **Measuring from the host**: a request from the host to its own network
  address succeeds whatever the firewall says. It does not count.

## Standing constraints

- *Keep everything local* is **not** in force.
- alfred's `main` merges only with an approving review: merge nothing into
  alfred. Commits go to alfred#169's branch or a branch stacked on it, never
  to the stack's branches beneath it.
- Elevated commands, the firewall and the account's password are the
  person's. A download is asked for first, naming what, from where and how
  large.
- Nothing machine-scoped is committed: no network id, node id, device
  address beyond the share's own, or picture of a screen that shows a person.
- `gh` in this shell needs `APPDATA` set per command.
- Commit messages are one line; a pull request body speaks as its
  contributor and ends with its `Tools:` note.
