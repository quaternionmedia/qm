# Quaternion Media Streaming Infrastructure — Design & Plan

A self-hosted streaming platform — live broadcast and video-on-demand — that is completely self-owned, open source end to end, and operable offline indefinitely. Python-first where the logic lives; standard protocols at every boundary so that no component is irreplaceable.

Governed by **ADR-0001**: every component in the deployed path carries an OSI-approved license (copyleft welcome; source-available and proprietary excluded, including drivers and model toolchains), and capability gaps are closed by contributing upstream — a PR to the closest layer of the stack, in that community's language — never by adopting a closed stopgap.

---

## The stack

| Layer | Component | Language | License | Role |
|---|---|---|---|---|
| Media router | **MediaMTX** | Go (single binary) | MIT | Ingest + playout: RTMP, SRT, WebRTC (WHIP/WHEP), RTSP, LL-HLS. Recording. Stateless relay. |
| VOD / library | **MediaCMS** | Python/Django/Celery + React | AGPL-3.0 | The portal: library, playlists, RBAC, REST API, local Whisper transcription. |
| Control plane | **`qmstream`** (we build it) | Python / FastAPI / SQLModel | ours | The seam: auth, stream lifecycle, policy, orchestration. The only custom code. |
| Postprocess | **FFmpeg + Metaflow** | C / Python | GPL-clean build / Apache-2.0 | DAG: probe → ABR ladder → HLS package ∥ thumbnails ∥ transcribe → publish. |
| Player | **hls.js** | JS | Apache-2.0 | Vendored, served from our host. Smallest payload of the viable players. |
| Database | **PostgreSQL** | — | PostgreSQL | Shared by MediaCMS and qmstream. |
| Proxy / TLS | **Caddy** (+ **step-ca** when air-gapped) | Go | Apache-2.0 | Automatic TLS; internal ACME CA for offline operation. |
| Cold storage | local FS → **SeaweedFS** or **Garage** | Go / Rust | Apache-2.0 / AGPL-3.0 | S3-compatible tier when local disk is outgrown. Not day-one. |
| Camera ingest *(optional)* | **Frigate** | Python | MIT | NVR + on-device AI detection (OpenVINO), restreams into MediaMTX. |
| Multi-party rooms *(optional)* | **Jitsi Meet** / **Galène** | Java / Go | Apache-2.0 / ISC | Browser-native rooms; composed into broadcast via OBS or WHIP (see below). |
| Deployment | Docker Compose → k3s, Harbor mirror | — | Apache-2.0 | GitOps; pinned digests; SBOM license gate in CI. |

Everything custom concentrates in `qmstream`; everything else is install-and-configure, reachable only through standard protocols (RTSP/RTMP/HLS/WHIP/S3/REST/MQTT). That seam design is the ownership strategy: any third-party layer can be replaced without touching the others.

### Deliberately not in the stack

- **Open Streaming Platform (OSP)** — the closest on-paper fit (Flask + nginx-rtmp), but archived: GitLab repo frozen, OpenCollective closed, Docker image deprecated. Dead upstream, dead-end Flask-era dependencies.
- **nginx-rtmp-module** — abandoned; no SRT, no WebRTC, no LL-HLS.
- **MinIO** — the cautionary tale that shaped ADR-0001's governance clauses. Community edition stripped through 2025, repo archived February 2026, replacement priced at ~$96k/yr. Its final license was open (AGPL); its *governance* failed. License compliance is necessary, not sufficient.
- **Jibri** (Jitsi's broadcast bridge) — excluded as shipped: its documented capture path runs through Google Chrome stable, a proprietary binary at the heart of the component. Per ADR-0001 the remediation is upstream — documented Chromium support contributed to jitsi/jibri (Kotlin, their idiom) — not local workarounds. Until that exists, multi-party composition uses the paths below, which are arguably better anyway.
- **NVENC / TensorRT / Coral** — proprietary kernel modules or closed compilers. Encode is CPU x264 or VAAPI on open Intel drivers; detection is OpenVINO. At our scale the performance delta is hardware money, not a bottleneck.
- **Owncast, OvenMediaEngine** — fine projects, wrong shape: a single-user product and a C++ low-latency SFU respectively, each duplicating part of MediaMTX+MediaCMS while extending neither.
- **Plex/Jellyfin-class servers** — personal media libraries, not audience platforms.

---

## Architecture

```
   SOURCES                         ROUTER                      AUDIENCE
┌──────────────────┐
│ OBS / ffmpeg     │─ RTMP/SRT ─┐
│ Browser (WHIP)   │─ WebRTC ───┤
│ Frigate cameras  │─ RTSP ─────┤
└──────────────────┘            ▼
                     ┌─────────────────────┐        LL-HLS / WHEP
                     │      MediaMTX       │──────▶  hls.js player
                     │  stateless relay,   │        (vendored)
                     │  records fMP4       │
                     └──────┬──────────────┘
                 auth +     │ webhooks
                 lifecycle  ▼
                     ┌─────────────────────┐
                     │  qmstream (FastAPI)  │  ◀── MQTT (Frigate events)
                     │  SQLModel state,    │
                     │  policy, triggers   │
                     └──────┬──────────────┘
                            │ on stream end
                            ▼
                     ┌─────────────────────┐       ┌──────────────────┐
                     │  Metaflow DAG       │──────▶│  MediaCMS        │
                     │  probe → ABR →      │ REST  │  library, VOD,   │
                     │  package∥thumbs∥    │       │  transcripts,    │
                     │  transcribe         │       │  RBAC            │
                     └─────────────────────┘       └──────────────────┘
```

Three design rules:

1. **MediaMTX is stateless.** All auth and lifecycle state lives in qmstream's Postgres; MediaMTX is recreatable from one static YAML at any time. Nothing in the router is worth backing up.
2. **Sources are an abstraction.** A channel's `source_type` is `direct` (RTMP/WHIP push), `frigate` (camera restream), or `room` (multi-party composition). Downstream never cares; new source types are an enum value and a handler.
3. **All convergence at the router.** Every flow — solo broadcast, camera, panel — becomes an identical MediaMTX path, so playout, recording, and postprocess are written once.

---

## `qmstream` — the seam

### Models

```python
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON

class SourceType(str, Enum):
    direct = "direct"      # OBS/ffmpeg RTMP push, or browser WHIP
    frigate = "frigate"    # MediaMTX pulls a Frigate restream
    room = "room"          # multi-party composition (OBS / WHIP mix)

class StreamState(str, Enum):
    idle = "idle"; live = "live"; processing = "processing"
    published = "published"; failed = "failed"

class Channel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    owner_email: str
    stream_key: str = Field(unique=True)
    source_type: SourceType = SourceType.direct
    source_config: dict = Field(sa_column=Column(JSON), default={})
    record_on_publish: bool = True
    auto_publish_to_cms: bool = True
    visibility: str = "unlisted"        # public | private | unlisted
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StreamSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channel.id", index=True)
    state: StreamState = StreamState.idle
    started_at: datetime | None = None
    ended_at: datetime | None = None
    recording_path: str | None = None
    cms_media_id: str | None = None
    error: str | None = None
```

### Auth — MediaMTX delegates every decision here

MediaMTX runs `authMethod: http`; each publish attempt becomes a POST we answer 200/401. Keys live only in our database, revocation is instant, and no router config ever mutates.

```python
@router.post("/hooks/mediamtx/auth")
async def auth(payload: dict, session=Depends(get_session)):
    if payload["action"] != "publish":
        return Response(status_code=200)          # reads public (tighten per-path later)
    channel = session.exec(
        select(Channel).where(Channel.slug == payload["path"])).first()
    key = parse_qs(payload.get("query", "")).get("key", [None])[0]
    ok = channel and secrets.compare_digest(channel.stream_key, key or "")
    return Response(status_code=200 if ok else 401)
```

### Lifecycle webhooks

```python
@router.post("/hooks/mediamtx/on-publish")
async def on_publish(payload: dict, session=Depends(get_session)):
    channel = get_channel(session, payload["path"])
    s = StreamSession(channel_id=channel.id, state=StreamState.live,
                      started_at=datetime.utcnow())
    session.add(s); session.commit()
    return {"session_id": s.id}

@router.post("/hooks/mediamtx/on-unpublish")
async def on_unpublish(payload: dict, session=Depends(get_session)):
    s = active_session(session, payload["path"])
    s.state, s.ended_at = StreamState.processing, datetime.utcnow()
    s.recording_path = payload.get("recordPath")
    session.add(s); session.commit()
    if s.channel.auto_publish_to_cms:
        trigger_postprocess(s.id)                  # launches the Metaflow run
    return {"ok": True}
```

### Postprocess DAG (Metaflow)

```python
class PostprocessFlow(FlowSpec):
    session_id = Parameter("session_id", type=int)

    @step
    def start(self):
        self.session = load_session(self.session_id)
        self.next(self.probe)

    @step
    def probe(self):
        self.meta = ffprobe(self.session.recording_path)
        self.next(self.transcode)

    @step
    def transcode(self):
        # CPU x264 (or VAAPI on Intel iGPU). ABR ladder sized from probe.
        self.renditions = render_abr(self.session.recording_path, self.meta)
        self.next(self.package, self.thumbnails, self.transcribe)

    @step
    def package(self):    self.hls = package_hls(self.renditions); self.next(self.join)
    @step
    def thumbnails(self): self.thumbs = extract_thumbs(self.session.recording_path); self.next(self.join)
    @step
    def transcribe(self):
        # faster-whisper (MIT), weights cached + mirrored locally. Fully offline.
        self.transcript = whisper_local(self.session.recording_path)
        self.next(self.join)

    @step
    def join(self, inputs):
        self.merge_artifacts(inputs); self.next(self.publish)

    @step
    def publish(self):
        media = MediaCMSClient(...).upload(...)    # httpx + Pydantic models
        mark_published(self.session_id, media["friendly_token"])
        self.next(self.end)

    @step
    def end(self): pass
```

Retention, cold-tiering to SeaweedFS/Garage, and backup *restore verification* are additional scheduled flows in the same idiom — backups that are never test-restored are hopes, not backups.

---

## MediaMTX configuration

```yaml
# mediamtx.yml — the entire router state. Static; lives in Git.
api: yes
apiAddress: :9997

recordPath: /var/lib/mediamtx/recordings/%path/%Y-%m-%d_%H-%M-%S-%f
recordFormat: fmp4
recordSegmentDuration: 1h

authMethod: http
authHTTPAddress: http://qmstream:8000/hooks/mediamtx/auth
authHTTPExclude:
  - action: read

runOnPublish: |
  curl -sS -X POST http://qmstream:8000/hooks/mediamtx/on-publish \
    -H 'Content-Type: application/json' \
    -d "{\"path\":\"$MTX_PATH\",\"query\":\"$MTX_QUERY\"}"
runOnUnpublish: |
  curl -sS -X POST http://qmstream:8000/hooks/mediamtx/on-unpublish \
    -H 'Content-Type: application/json' \
    -d "{\"path\":\"$MTX_PATH\",\"recordPath\":\"$MTX_RECORD_PATH\"}"

paths:
  all_others:        # channels exist implicitly; qmstream's auth endpoint is the gate
```

---

## Deployment

Single host, Docker Compose, five services + proxy:

```yaml
services:
  mediamtx:
    image: registry.internal/mediamtx@sha256:…     # built from mirrored source in CI
    ports: ["1935:1935", "8554:8554", "8888:8888", "8889:8889"]
    volumes: [./mediamtx.yml:/mediamtx.yml, recordings:/var/lib/mediamtx/recordings]

  qmstream:
    image: registry.internal/qmstream@sha256:…
    environment: { DATABASE_URL: …, MEDIACMS_URL: http://mediacms-web, MEDIACMS_TOKEN: … }
    volumes: [recordings:/recordings:ro, metaflow:/metaflow]

  mediacms-web:    { image: registry.internal/mediacms@sha256:…, volumes: [cms:/…/media_files] }
  mediacms-celery: { image: registry.internal/mediacms@sha256:…, command: celery worker, volumes: [cms:/…/media_files] }
  db:              { image: registry.internal/postgres:16@sha256:…, volumes: [pg:/var/lib/postgresql/data] }
  caddy:           { image: registry.internal/caddy:2@sha256:…, ports: ["80:80","443:443"], volumes: [./Caddyfile:/etc/caddy/Caddyfile, caddy:/data] }
```

Provenance and ownership posture, from day one:

- **Local registry** (Harbor) mirrors every image; MediaMTX and qmstream are **built from source trees we mirror** — "compiled it ourselves from a tagged tree we host" is the strongest ownership claim available.
- **CI license gate**: Syft generates an SBOM per image; any license outside the OSI allowlist fails the build (ADR-0001 §4). A quarterly Metaflow job rescans upstreams for relicense/archive events.
- **All frontend assets vendored** — hls.js, fonts, player chrome. Zero CDN references.
- **Air-gapped TLS**: Caddy → step-ca (internal ACME) instead of Let's Encrypt; one config line.
- **Growth path**: same containers onto k3s + Flux when multi-node; Podman is the documented exit from Docker Inc. if ever wanted.

Backups: `pg_dump` + recordings via restic to a second box or the SeaweedFS/Garage tier, with scheduled restore-verification.

### Hardware

One box runs everything: **Intel CPU with iGPU** — open VAAPI encode, open OpenVINO inference, zero proprietary kernel modules. 8 cores / 32 GB / 2× NVMe covers ingest + transcode + CMS comfortably at single-org scale; transcode is the only component that ever wants more, and it scales out as a Metaflow worker. Budget storage at ~3× raw recording size (original + renditions + thumbnails).

---

## Optional extension: Frigate (camera ingest)

When sources include IP cameras: **cameras → Frigate → RTSP restream → MediaMTX → audience.** Frigate (Python, MIT, ~31k stars) contains the camera mess — vendor RTSP quirks, reconnects, recording — and adds local-only object detection via **OpenVINO** on the same Intel iGPU. Detection runs on each camera's low-res substream; recording uses the main stream. The camera VLAN terminates at Frigate; nothing upstream ever touches a camera directly.

The integration seam is **MQTT**: every detection is a structured event qmstream subscribes to, enabling policy like *person enters "stage" zone → auto-promote camera to a live channel* — unattended rehearsal/performance capture with zero operator action:

```python
async def handle(self, event: FrigateEvent):
    if event.type == "new" and event.label == "person" and "stage" in event.zones:
        await self.api.promote_camera_to_channel(camera=event.camera,
                                                 channel_slug=f"auto-{event.camera}")
```

Skip Frigate entirely if no cameras are in scope; it's an NVR, not a general ingest server. (Frigate+ — the cloud-trained model subscription — stays excluded per ADR-0001; the bundled open models are good.)

## Optional extension: multi-party rooms (panels, remote guests)

Composition strategy, in order:

1. **OBS + room-as-browser-source** *(default)* — remote guests join a Jitsi Meet or Galène room; the operator's OBS composes it and pushes RTMP to MediaMTX. Zero new server-side moving parts; covers 1–3 guests, which is most real cases.
2. **WHIP direct** — each contributor publishes WebRTC straight to MediaMTX from a page we serve; composition via OBS or an FFmpeg filter graph in a Metaflow step. Fully owned, more plumbing, no conferencing stack at all.
3. **Self-hosted room server, if browser-native rooms are needed**: **Galène** (ISC, single Go binary — the MediaMTX of SFUs) for lightweight; **Jitsi Meet** (Prosody/Jicofo/JVB, all Apache-2.0) for polish. Note Jitsi's JVB wants 4+ cores at 10+ participants and UDP/10000 forwarded directly (it cannot be reverse-proxied), and STUN/TURN must be our own **coturn** for offline operation.

Server-side composed capture (Jitsi's Jibri) is excluded as shipped — proprietary Chrome in the capture path — with the ADR-0001 remediation being an upstream Chromium-support contribution to jitsi/jibri if we ever genuinely need it. Paths 1–2 make that need rare.

---

## Risk register

| Component | Governance | Exposure | Containment |
|---|---|---|---|
| MediaMTX | effectively one maintainer (bluenviron) | bus-factor | MIT + standard protocols: a frozen MediaMTX keeps working and is replaceable; huge user base would fork |
| MediaCMS | small company + community | open-core drift (the MinIO pattern) | REST-only coupling — the VOD layer is swappable in isolation; quarterly governance scan |
| Frigate | strong lead, existing commercial arm (Frigate+) | extractive turn | core MIT, models swappable; we never adopt the paid tier |
| Jitsi | corporate steward (8x8) | investment withdrawal | Apache-2.0; only optional, only the Meet stack, Galène as the lightweight fallback |
| FFmpeg, Postgres, Caddy, hls.js | foundation/community | minimal | — |
| `qmstream` | ours | zero | the seam is exactly where sovereignty is concentrated |

The architecture is the mitigation: every third party sits behind a standard protocol, so any failure is a component swap, not a redesign.

---

## Phased plan

| Phase | Scope | Effort |
|---|---|---|
| **0** | Decide latency tier (HLS ~10s / LL-HLS ~3s / WHEP sub-second), domains, whether cameras and rooms are in scope | ½ day |
| **1** | MediaMTX + Caddy up; OBS push in, hls.js playback out; recording verified on disk | 1 day |
| **2** | MediaCMS + Postgres up; Whisper transcription verified; API token issued | 1 day |
| **3** | `qmstream` v0.1: models + migrations, auth endpoint, lifecycle webhooks, MediaCMS client, manual publish | 3–5 days |
| **4** | Metaflow postprocess wired to on-unpublish; first end-to-end broadcast → library | 2–3 days |
| **5** | Channel pages (Jinja2 + vendored hls.js); MediaCMS handles VOD pages natively | 1–2 days |
| **6** | Hardening: key rotation, retention flow, restic + restore-verification, Prometheus/Grafana, SBOM gate in CI | ongoing |
| **7a** *(if cameras)* | Frigate + one camera; MediaMTX pull path; MQTT bridge; `frigate` source type | 1–2 days |
| **7b** *(if rooms)* | Galène or Jitsi Meet + coturn; OBS composition runbook; `room` source type | 1–2 days |

Working v1 (phases 1–5): roughly one focused week, or two weeks of evenings.

## Open questions

1. **Latency tier** — LL-HLS (~2–3s) is the proposed default: one player, one delivery path, low enough for performance + chat use. WHEP sub-second stays available per-channel if ever needed. Confirm or simplify to standard HLS.
2. **Cameras in scope?** Determines Phase 7a and whether the Intel iGPU does double duty (encode + detection).
3. **Rooms in scope?** Determines Phase 7b; the OBS-composition default needs no new infrastructure either way.
4. **Chat** — out of scope for v1 by design. If wanted later: Matrix for federated/owned, or a minimal qmstream WebSocket room; decide when there's an audience to chat.

---

*Decision rationale is recorded in `adr/` — ADR-0001 (open-license exclusion & upstream-contribution remediation) is constitutional and governs the rest of the set.*
