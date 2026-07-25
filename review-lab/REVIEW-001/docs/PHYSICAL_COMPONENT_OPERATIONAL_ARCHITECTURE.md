# Physical, Component, and Operational Architecture (SABSA layers 5–6)

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Answers:** *With what? (physical) Which mechanisms? (component) When/how operated? (operational)*

This document covers three SABSA layers together because, for this platform, the physical deployment, the component mechanisms, and the operational model are tightly coupled (the same systemd services are all three). Each section is labelled.

---

## PHYSICAL LAYER — with what

Inherits TimeLapse Pro's physical topology (`SABSA_Architecture_v10.md` §3, `00_START_HER.md`) and adds the payload-isolation physical realisation.

### Physical topology

```
┌──────────────────────────────────────────────────────────────────────┐
│  PRODUCTION HEADEND HOST (Mac Mini, macOS)                           │
│  Co-located with CrushFTP (live customer data — already a trust      │
│  boundary today, SABSA §3).                                          │
│                                                                      │
│  systemd / LaunchDaemons:                                            │
│    dk.froekjaer.mission-headend   (FastAPI/uvicorn 127.0.0.1:8000)   │
│    dk.froekjaer.mission-postgresql(PostgreSQL timelapse_db)          │
│    dk.froekjaer.mission-nginx     (TLS, port 8443, DNS-01 cert)      │
│    dk.froekjaer.mission-ui        (static UI build)                  │
│    dk.froekjaer.mission-ollama    (local AI infra, 127.0.0.1:11434)  │
│                                                                      │
│  Storage: /Volumes/data-fast (canonical), /Volumes/Backup (backup)   │
└──────────────────────────────────────────────────────────────────────┘
            ▲ TLS 8443 (operator)   ▲ SFTP 22222 / signed OTA / reverse SSH (nodes)
            │                       │
┌───────────────────────────┐   ┌────────────────────────────────────────┐
│  OPERATOR / CUSTOMER      │   │  EDGE NODE (Orange Pi 4 Pro, Armbian)   │
│  browser (RBAC + MFA)     │   │  TL-C87FF9587CA0 (active)               │
│  future: customer portal  │   │                                          │
└───────────────────────────┘   │  systemd services:                       │
                                │    dk.froekjaer.platform-core   ◄── NEW │
                                │    dk.froekjaer.payload-timelapse ◄ NEW │
                                │    (existing: tunnel, update, etc.)     │
                                │                                          │
                                │  Storage: 128 GB NVMe; 50 GB circular    │
                                │  buffer for store-and-forward            │
                                │                                          │
                                │  Camera: Nikon Z30 (USB/PTP via HAL)     │
                                │  Relay: GPIO 356 (camera power)          │
                                └────────────────────────────────────────┘
```

### Physical isolation of payloads (the new piece)

Per ADR-001 amendment 1 and ADR-Z-002, a payload is a **separate systemd service** on the node:

| Physical isolation control | Mechanism | Evidence lineage |
|---|---|---|
| Separate process | `dk.froekjaer.payload-<name>.service` | amendment 1 |
| Dedicated OS user | `payload-<name>` uid, no platform-group membership | least privilege |
| seccomp filter | syscall allowlist; denied syscalls fail-closed | CRA secure-by-design |
| AppArmor profile (optional hardening) | path + network confinement | IEC 62443 FR |
| Filesystem allowlist | manifest `allowlist.files` → mount namespace / systemd `ReadWritePaths` | amendment 3 |
| Network allowlist | manifest `allowlist.network` → systemd `IPAddressDeny=*` + `IPAddressAllow=…` | amendment 3 |
| Separate service identity | payload credential ≠ platform credential | amendment 3 |

This is the physical realisation of the Conceptual zone "PAYLOAD (least-privilege, isolated process)." It is achievable on Armbian/systemd today without containers — *the lowest-overhead enforcement that satisfies the threat model*.

---

## COMPONENT LAYER — which mechanisms

The concrete components (mechanisms). Inherited TimeLapse Pro mechanisms are marked [inh]; new platform mechanisms are marked [new].

### Platform Core components

| Component | Mechanism | Status | Evidence |
|---|---|---|---|
| Identity / enrollment | Ed25519 keypair, bootstrap token, JWT (HS256→asym RS256/EdDSA open), HMAC device tokens | [inh] SEC-005/006, PROV-003/008; intern CA [inh] SEC-009 (designed) | KRAVREGISTER |
| Config / policy hierarchy | 4-tier merge global→tenant→site→node; signed; provenance per field | [inh] CFG-001/002 | KRAVREGISTER |
| Update authority | Signed OTA (GPG), staged R&D→staging→prod, per-target status, rollback | [inh] UPD-004/008/009 | KRAVREGISTER |
| Telemetry / SIEM / CMDB | Heartbeat per capture, freshness-based status, drift detection, syslog receiver | [inh] SABSA §6; ADR-001 platform-kerne | KRAVREGISTER |
| JIT access broker | AccessTicket, short-lived certs, destination allowlist, session recording, kill switch | [new] (designed, not built — `Claude_Support_Access_Model_2026-07-06.md`) | R19, GO_LIVE M-01..M-08 |
| HAL | `edge/hal/` promoted to `platform/hal/`; base + generic + orangepi + rpi + jetson | [inh] | code tree |
| Storage / quarantine | canonical-path registry, SHA-256 verify, quarantine (no hard-delete), circular buffer | [inh] CFG-010, project principle "aldrig hard-delete" | SABSA §4 |
| Audit spine | append-only log, actor+time+reason per conduit interaction | [new] ( Accountability) | SABSA F1 |
| Time authority | NTP/chrony exposed as a platform service payloads consume | [inh] (Synchronicity) | SABSA F1 |
| Multi-tenant data service | row-level isolation enforced here, not by payloads | [new] (Confidentiality) | SABSA F1 |
| **Payload supervisor** | loads payload, validates manifest against signed policy, spawns isolated service, enforces fail-closed, restarts on crash, reports health | [new] | ADR-001 amendments 1,3,4 |

### Payload (timelapse) components

| Component | Mechanism | Status | Evidence |
|---|---|---|---|
| Driver | implements `PayloadDriver` contract; wraps existing capture/tick logic | [new wrap of inh] | ADR-001 §2 |
| Capture | gphoto2 Nikon Z30 driver + Canon legacy; relay control GPIO 356 | [inh] CAP-001/010 | code tree `edge/camera/` |
| Imaging QA | blur score, quality flag, thumbnail (PIL) | [inh] CAP-003/004 | KRAVREGISTER |
| Video render | FFmpeg timelapse (fps/codec/deflicker/Ken Burns/crop/timestamp) | [inh] UI-011 | KRAVREGISTER |
| AI tagging | Gemini 2.5 Flash (Vertex eu-west1) + Batch API + Ollama; Danish labels | [inh, partial] CAP-005 | KRAVREGISTER |
| Edge QA / site-look | NPU VIPLite (C++); autonomous optimizer | [inh] `edge/ai/`, `edge/npu_viplite/` | code tree |
| Payload UI surfaces | gallery, lightbox, tag search, video page | [inh] UI-001..011 | KRAVREGISTER |

### Headend process components

The headend is where the monolith decomposition happens. Currently **`main.py` (783 KB, 234 routes, 18k lines)** plus 19 partially-extracted routers. The component target (see Migration): each `headend/api/<domain>` is a router package with enforced auth (K1 route-auth-sweep), and the payload UIs are mounted as plugins into a shared UI shell.

---

## OPERATIONAL LAYER — when / how operated

Inherits SABSA Operational (`SABSA_Architecture_v10.md` §1.1 row 6) and the update flow (`Update_Flow_v10.md`), and adds the multi-payload operational model.

### Operational rhythms

| Rhythm | Mechanism | Evidence |
|---|---|---|
| Heartbeat per capture | edge → headend health + diagnostics | SABSA §6 |
| Nightly node reboot 02:00 | continuity (boot-to-capture < 120 s) | SABSA Continuity |
| Config poll cadence (≤5 min) | node pulls signed policy; applies to self + re-configures payload via `configure()` | CFG, ADR-001 §2 |
| Telemetry cadence | payload `collect_telemetry()` → platform SIEM | ADR-001 §2 |
| Key rotation | platform identity lifecycle | SEC-003 PROV-003 |
| Backup | pull-based (edge can't be reached inbound); SFTP to headend → /Volumes/Backup | SABSA §4; R09 (restore-test open) |

### Update lifecycle (operational) — additive, gate-staged

```
[R&D/LAB] → [QA: tests + sign + human-readable change ticket]
   → [policy approval: global/tenant/site/node/device]
   → [staged deploy: staging → prod, per-target status]
   → [headend-mediated distribution: no direct internet on edge]
   → [healthcheck + rollback + audit, per artifact type]
```

The platform supervisor adds a step: **after applying a platform update, it re-validates every loaded payload's manifest compatibility** (compatibility matrix, amendment 4). An incompatible payload is *not* crash-killed silently; it is rolled back or quarantined per its `health.rollback_on` contract.

### Payload lifecycle (operational) — the new rhythm

```
1. Signed payload package arrives via OTA (same trust as platform artifacts)
2. Platform supervisor verifies signature + manifest schema
3. Validates manifest against signed policy allowlist (fail-closed)
4. Checks contract version compatibility matrix (platform ↔ payload)
5. Spawns isolated systemd service (dedicated user, seccomp, allowlists)
6. Calls configure(policy) → tick(schedule) → monitors health()
7. On crash_loop / bad contract / resource exhaustion:
     → degraded mode or rollback per failure contract (amendment 4)
8. On unload: graceful drain, audit record, credential revocation
```

### Incident response (operational)

Inherits `SEC-013_Incident_Response_Procedure.md` (GDPR Art. 33/34). The platform adds: **a payload compromise is contained by isolation** — one payload's fault does not cascade to the platform core or other payloads (the whole point of amendment 1). Kill switch (C7) tears down any active JIT conduit during an incident.

### Observability (operational)

Per `Claude_Observability_ITIM_Design_2026-06-29.md`: platform-owned SIEM/CMDB/ITIM collects standardised metrics from payloads (via `collect_telemetry`). Payloads do not run their own monitoring stack; they emit, the platform observes. This is the ADR-001 AI-split applied to observability: *purpose-owned*, not *component-owned*.

---

## Deployment environments (operational trust boundaries)

| Env | Purpose | Trust rule | Evidence |
|---|---|---|---|
| `rd` | development | standing agent access for R&D | SABSA §3 env layer |
| `staging` | pre-prod validation | default-deny agent; break-glass only | M-01..M-08 |
| `prod` | live customer data (CrushFTP co-located) | default-deny agent; JIT only | SABSA §3; R19 |

`TIMELAPSE_ENV` flag must be known to all three readers (`edge/agent.py`, `headend/main.py`, `headend/siem.py` per SABSA §3 known-pitfall note) — carried forward as a platform-core responsibility with a test enforcing reader coverage.

---

## Mapping back to business attributes

| Operational mechanism | Business attribute |
|---|---|
| Nightly reboot, heartbeat, watchdog | Availability, Continuity |
| Circular buffer + store-and-forward | Resilience |
| Pull backup, SHA-256 verify | Integrity |
| JIT broker, kill switch, session recording | Accountability, Confidentiality |
| Time authority service | Synchronicity |
| Per-target update status + rollback | Manageability, Integrity |
| Multi-tenant data service enforcement | Confidentiality |
| Payload supervisor + isolation | Payload isolation, Extensibility |
| Audit spine | Accountability |
| Manifest data_classification | Proportionate compliance |
