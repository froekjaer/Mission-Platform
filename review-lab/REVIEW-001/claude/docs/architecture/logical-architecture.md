# Logical Architecture (SABSA Logical Layer)

- **Reviewer:** Claude · **Date:** 2026-07-31

## 1. Logical services — edge

```
┌─ Edge Node ────────────────────────────────────────────────┐
│ ┌─ Platform Agent (one hardened service) ────────────────┐ │
│ │ identity/enrollment · policy sync (verify signatures)  │ │
│ │ OTA apply/rollback · heartbeat/telemetry export        │ │
│ │ tunnel/JIT conduit endpoint · payload supervisor       │ │
│ │ data-plane forwarder (spool → headend, backpressure)   │ │
│ └───────────────┬───────────────────────────────────────┘ │
│          control socket (local, authenticated)             │
│ ┌─ Payload Sandbox (per payload instance) ──────────────┐  │
│ │ PayloadDriver impl (e.g. timelapse)                   │  │
│ │ own OS user/service · cgroup quota · fs+net allowlist │  │
│ │ HAL access only via granted capabilities              │  │
│ └───────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

Key logical decisions:

- **The platform agent is the only network-facing process** on the node; payloads have no direct route to the headend. The payload writes data objects to a local spool via the data contract; the agent forwards with retry/backpressure. This gives one place to enforce network policy and one upload identity per plane.
- **Payload supervision** = start/stop/health/restart-with-backoff/rollback per the control contract; enforcement of manifest quotas is the supervisor's job (ADR-CL-005 defines the mechanism; the contract does not depend on the mechanism).
- **HAL stays platform**, but device *grants* are capability-scoped: the manifest requests `camera.usb`/`gpio`/`modbus`; the supervisor materialises only granted device access into the sandbox.

## 2. Logical services — headend

The 18.5k-line monolith is decomposed **by quadrant** into four logical services (deployable as one process initially — logical boundaries first, process boundaries when needed):

```
┌─ Headend ──────────────────────────────────────────────────────────┐
│ Control API service        │ Data-plane service                    │
│  - node identity/enrollment│  - ingestion endpoints (per channel)  │
│  - policy/config authoring │  - storage registry & retention engine│
│    + signing               │  - backup orchestration               │
│  - OTA release/rollout     │  - telemetry/SIEM pipeline            │
│  - RBAC/auth/MFA, tickets  │                                       │
│  - GRC/evidence register   │                                       │
├────────────────────────────┼───────────────────────────────────────┤
│ Payload domain service(s)  │ Experience service                    │
│  (timelapse: QA, tagging,  │  - admin UI + customer UI (React)     │
│   video build, site look)  │  - reporting/exports                  │
└────────────────────────────┴───────────────────────────────────────┘
```

- Every route lives in a router owned by exactly one service; **`main.py` becomes composition-only** (mount + middleware), driven to that state by the existing ratchet tests (which are reused and tightened — see migration).
- **Auth is structural, not per-route:** routers are mounted through an authenticated router factory; mounting an unauthenticated router fails CI. This retires the source system's recurring failure class rather than re-detecting it.
- The **payload domain service** depends on platform services through the same logical contracts as edge payloads where applicable (its data in via channels, its results registered as data objects with classification).

## 3. Logical contracts (versioning rules)

| Contract | Content | Version policy |
|---|---|---|
| `control/PayloadDriver` v1 | configure(policy), start(), stop(), health(), handle_command(cmd) → result | SemVer; major = coordinated change |
| `data/DataChannel` v1 | declare(name, kind: blob|timeseries|event, classification, retention_class); put(object|point|event) | SemVer, independent of control |
| `manifest` v1 | identity, contract versions, capabilities[], quotas, net/fs allowlists, channels[] | JSON Schema, versioned; unknown fields ⇒ reject (fail closed) |
| `headend control API` v1 | node/enrollment/config/OTA/ticket endpoints | additive within major; breaking = new major prefix |

Compatibility matrix (platform version × payload contract majors) is published with each platform release; the supervisor refuses to start a payload whose declared contract major is unsupported (fail closed, logged).

## 4. Logical security services

Identity (node keys + per-payload service identities; device CA/mTLS as migration stage 3), AuthN/AuthZ (JWT + MFA step-up retained from source; RBAC platform-wide), Policy signing service, Audit/SIEM (all four quadrants emit structured audit events), JIT access (AccessTicket with scope/expiry/destination allowlist/kill switch — retained from source design R19 controls), Secrets management (per-service, never in repo).

## 5. Logical data management

Every `DataChannel` carries **classification** (e.g. `personal-images`, `process-telemetry`, `operational-logs`) and a **retention class**. The retention engine enforces deletion/quarantine per class and writes evidence records to the GRC register. Backup policy is also class-driven (personal data backed up encrypted, evidence of restore tests mandatory). This turns GDPR from documentation into mechanism — the platform cannot store mission data on an undeclared channel.
