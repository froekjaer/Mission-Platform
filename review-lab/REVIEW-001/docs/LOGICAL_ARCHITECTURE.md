# Logical Architecture (SABSA Logical layer)

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Answers:** *How is the system structured? What are the modules, data flows, and contracts? Why these technology choices?*

This layer defines the logical module structure of both Platform Core and Payload, the contracts between them, the data model, and the principal data flows. Technology choices appear here, each justified against business attributes.

---

## 1. Module structure (logical)

The target logical structure. It is a **monorepo with sharp package boundaries** (ADR-001 §3 model A), designed to be cheaply migratable to a versioned-package model later.

```
mission-platform/                         # monorepo, ADR-001 §3 model A
├── contracts/                            # THE product. SemVer. Most expensive to change.
│   ├── payload_driver.py                 #   control-plane contract (lifecycle)
│   ├── data_plane.py                     #   data-plane contract (bulk ingest)
│   ├── capability_manifest.py            #   manifest schema + validation
│   └── versions.py                       #   SemVer constants
├── platform/                             # Platform Core — reusable across payloads
│   ├── identity/                         #   enrollment, JWT, HMAC, RBAC (SEC-004/005/006)
│   ├── config/                           #   4-tier policy hierarchy (CFG-001): global→tenant→site→node
│   ├── update/                           #   OTA authority, signed artifacts, staged rollout (UPD-*)
│   ├── telemetry/                        #   SIEM/CMDB/ITIM, drift detection
│   ├── access/                           #   JIT/AccessTicket broker, conduit management (R19)
│   ├── hal/                              #   hardware abstraction (existing edge/hal/ promoted)
│   ├── storage/                          #   canonical-path registry, quarantine, backup (CFG-010)
│   ├── audit/                            #   the audit spine — platform-owned accountability
│   ├── time/                             #   time-authority service (Synchronicity)
│   ├── tenants/                          #   multi-tenant data service + row-level isolation
│   └── supervisor/                       #   PAYLOAD SUPERVISOR — loads, enforces manifest, isolates
├── payloads/
│   └── timelapse/                        # the first payload
│       ├── driver.py                     #   implements contracts.PayloadDriver
│       ├── manifest.yaml                 #   capability manifest
│       ├── capture/                      #   (from edge/camera + edge/capture)
│       ├── imaging/                      #   thumbnail, QA, blur (CAP-003/004)
│       ├── video/                        #   FFmpeg render (UI-011)
│       ├── ai/                           #   tagging, site-look (payload-owned AI per ADR-001 AI-split)
│       └── ui/                           #   timelapse-specific UI surfaces
├── headend/                              # the headend process (API, admin, customer UI shell)
│   ├── api/                              #   (extracted from main.py — see Migration)
│   └── ui-shell/                         #   common chrome; payload UIs mounted as plugins
├── deploy/                               # provisioning, disk images, LaunchDaemons (existing)
└── tests/                                # contract tests, architecture ratchet, integration
```

### Why this shape (Why/Because/For whom)

- **Why a monorepo not multi-repo?** *Because* ADR-001 §3 chose model A as lowest-friction-now, migratable-later, and *because* the contract is what's expensive to change, not the repo layout. *For whom:* the small team — a multi-repo split now would impose cross-repo coordination cost before the boundaries have proven themselves.
- **Why is `contracts/` its own top-level package?** *Because* it is the single artifact that both Platform and Payload depend on; isolating it makes the SemVer discipline visible and lets CI enforce "platform and payload must agree on contract version."
- **Why is `tenants/` in platform, not per-payload?** *Because* Confidentiality (tenant isolation) is a platform business attribute (Business Arch §3). Re-implementing it per payload would risk a payload constructing a cross-tenant query. *For whom:* every customer whose data must stay isolated.

---

## 2. The two versioned contracts (logical detail)

### 2.1 Control-plane contract — `PayloadDriver`

```python
# contracts/payload_driver.py — logical sketch (see ADR-Z-001 for full)
class PayloadDriver(Protocol):
    """Implemented by every payload; called by the platform supervisor."""
    contract_version: ClassVar[str]   # SemVer, must be compatible with platform

    def configure(self, policy: SignedPolicy) -> ConfigureResult: ...
    def tick(self, now: datetime) -> TickResult: ...
    def collect_telemetry(self) -> Telemetry: ...
    def handle_command(self, cmd: AllowedCommand) -> CommandResult: ...
    # Failure contract (ADR-001 amendment 4):
    def health(self) -> HealthState: ...
    def on_resource_pressure(self, level: PressureLevel) -> DegradedMode: ...
```

- **Lifecycle:** the platform supervisor calls `configure` on policy change, `tick` on the payload's schedule, `collect_telemetry` on its cadence, `handle_command` only with allowlisted commands.
- **Failure contract methods** make amendment 4's requirements explicit: timeout, backpressure, crash/restart, degraded mode, resource exhaustion, rollback on incompatibility.

### 2.2 Data-plane contract

Separate SemVer. The payload pushes bulk data (images, video, future OT streams) through a platform data-ingest service that enforces quota and classification-based routing (e.g. evidence-grade data goes to the integrity-verified store). The payload never writes to canonical storage directly.

### 2.3 Capability manifest (logical schema)

```yaml
# payloads/timelapse/manifest.yaml — logical
contract_version: 1.0.0
payload: timelapse
data_classification: image_evidence   # drives retention/DPIA (Proportionate compliance)
hardware:
  required: [camera_ptp, relay_gpio]
resource_quota:
  cpu_percent: 40
  ram_mb: 1024
  disk_gb: 50
allowlist:
  files: [/dev/cam0, /tmp/payload/timelapse/]
  network: []                          # timelapse has no direct network need
service_identity: timelapse-payload    # != platform credential (amendment 3)
health:
  heartbeat_s: 60
  rollback_on: [crash_loop, bad_contract_version]
api_version: 1.0.0                     # payload's own SemVer
```

The platform supervisor **validates** this against a signed policy allowlist and **enforces** it fail-closed. A payload is loaded only if its manifest is satisfied; an off-manifest access is denied and logged.

---

## 3. Data model (logical)

Inherits TimeLapse Pro's hierarchy, made domain-neutral per ADR-001 §5. Naming is additive (existing `camera`/`capture` not renamed broadly).

```
Tenant (customer) ──< Site ──< Node (device) ──< PayloadInstance
                      │              │
                      │              └── hosts ── PlatformCoreInstance
                      │
                      └──< Camera/Asset ──< Capture/Image  (timelapse payload data)
```

Key logical points:

- **`Node` is the physical device; `PayloadInstance` is what runs on it.** A Node can host multiple PayloadInstances in future (e.g. timelapse + environmental sensing), each isolated.
- **Multi-tenant row-level isolation** is enforced at the `tenants/` data service (Confidentiality). Payloads query through it; they cannot bypass.
- **Audit spine** is a platform-owned append-only log; every C1–C8 conduit interaction emits a record (Accountability).
- **CMDB/SIEM** is platform-owned; payloads emit standardised telemetry via `collect_telemetry()`, not ad-hoc.

---

## 4. Principal data flows (logical)

### 4.1 Capture → evidence store (the integrity-critical flow)

```
Payload.tick(now)
  → HAL.capture(camera)                      # C8: HAL-mediated device access
  → compute SHA-256 pre-XMP                  # in payload (it knows evidence-grade)
  → DataPlane.ingest(image, sidecar_json)    # C6: data-plane contract
      → platform storage/quarantine service
          → SHA-256 verify, write canonical store
          → audit record (actor=payload, integrity hash)
  → if headend reachable: SFTP (C3) mirror   # existing store-and-forward path
  → if not: circular buffer (Resilience)
```

The **payload computes the hash; the platform verifies and stores.** This separation keeps the integrity guarantee platform-owned while letting the payload declare evidence-grade intent.

### 4.2 Signed config / OTA distribution (C2)

Unchanged from TimeLapse Pro's model: headend authority signs policy/artifacts → node pulls on poll cadence → platform supervisor applies to itself and re-configures payload via `configure(policy)`. Payload never self-updates.

### 4.3 Remote support (C7) — the JIT conduit

```
Operator requests access (UI) with justification + scope
  → platform access broker issues short-lived AccessTicket
      (destination allowlist, expiry, session recording armed, kill switch primed)
  → conduit established: operator → payload (or payload → OT backend)
  → every keystroke/transfer audited
  → ticket expiry or kill-switch tears down the conduit
```

This is amendment 5 made concrete. No inbound port is ever opened on the OT network.

---

## 5. Technology choices (logical, justified)

| Choice | Decision | Why (Business attribute) | Evidence/challenge path |
|---|---|---|---|
| Headend runtime | **Python + FastAPI + PostgreSQL** (inherit) | Continuity; team skill; ADR-001 scope-point (don't delay production-readiness) | ADR-001 "fuld microservices… for tidligt"; A-3 |
| Edge orchestration | **Python** for contract/supervisor | Continuity; matches existing edge; HAL already Python | A-3; Q-3 default |
| Edge compute (AI) | **Polyglot**: native (C++ VIPLite) as payload-owned dependency | Performance for AI-heavy future payloads; isolates vendor SDKs | `edge/npu_viplite/`; Q-3 |
| Isolation primitive | **systemd service + dedicated user + seccomp/AppArmor** per payload | Payload isolation (low overhead, matches existing systemd edge, sufficient for SL) | ADR-Z-002; Q-4 |
| Contract format | **Python Protocol + YAML/JSON manifest** | Match runtime; testable; SemVer via constants | ADR-001 §2 normative sketch |
| Artifact signing | **Inherit existing GPG + signed OTA** (TL-QA-APP etc.) | Integrity, already implemented (UPD-004) | UPD-004/005 |
| AI — platform-owned | SIEM/CMDB drift, ops | Accountability; shared infra | ADR-001 AI-split |
| AI — payload-owned | Tagging, site-look, edge QA | Domain ownership of prompts/data/retention | ADR-001 AI-split; Codex_Edge_AI_NPU_Modes |

### Challenges I considered and rejected

- **Rewrite headend in a compiled language for performance.** Rejected: Performance is *Low* priority in SABSA; the bottleneck is the monolith *structure*, not Python's speed; rewrite would violate ADR-001's "don't delay production-readiness."
- **Microservices/multi-repo now.** Rejected: ADR-001 explicitly rejected this as premature; boundaries haven't proven themselves.
- **One combined control+data contract.** Rejected: amendment 2 mandates separate planes; a single contract would let a bulk-image stream block a health check.

---

## 6. Control plane vs data plane separation (amendment 2)

| Aspect | Control plane (C5) | Data plane (C6) |
|---|---|---|
| Carries | lifecycle, config, command, health, telemetry-summary | images, video, future OT telemetry streams |
| Cadence | periodic, small | bursty, large |
| SemVer | independent | independent |
| Failure handling | fail-closed on unknown command | backpressure + quota enforcement |
| Quota | none (tiny) | manifest `resource_quota` enforced |

Separation guarantees a misbehaving data plane cannot starve control (health checks always get through) — directly supporting Availability.

---

## 7. Traceability to business attributes

| Logical element | Primary business attribute(s) |
|---|---|
| `contracts/` PayloadDriver + manifest | Extensibility, Proportionate compliance |
| `platform/supervisor/` + isolation | Payload isolation, Availability |
| `platform/tenants/` row-level isolation | Confidentiality |
| `platform/audit/` spine | Accountability |
| `platform/time/` authority | Synchronicity |
| `platform/storage/` + quarantine + circular buffer | Integrity, Resilience, Continuity |
| `platform/update/` signed staged OTA | Manageability, Integrity |
| `platform/access/` JIT broker | (Support) Accountability, Confidentiality |
| data-plane contract separation | Availability |

Every logical module traces to at least one measurable criterion in Business Arch §4.
