# Conceptual Architecture (SABSA Conceptual layer)

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Answers:** *What is the security policy / conceptual model? What are the trust zones and conduits?*

This layer defines the conceptual entities, the trust zones (IEC 62443), the conduits between them, and the security policy that governs every interaction. It is technology-independent. Lower layers realise it.

---

## 1. Conceptual entities

Six conceptual entity classes. The naming is **domain-neutral** per ADR-001 §5 (e.g. `asset`/`node`, not `camera`) so future payloads do not inherit timelapse vocabulary.

| Entity | Responsibility | Owner (Platform/Payload) | Evidence lineage |
|---|---|---|---|
| **Platform Core** | The non-functional guarantees: identity, config/policy hierarchy, OTA/update authority, telemetry/SIEM/CMDB, remote-access conduits, HAL, storage/backup, the payload lifecycle supervisor. | Platform | ADR-001 §1 platform-kerne list |
| **Payload** | The functional mission capability (today: timelapse capture + image QA + tagging). Declares its needs via a capability manifest; is granted capabilities by platform policy. | Payload | ADR-001 §1 payload list |
| **Node** | A physical edge device hosting one Platform Core instance and one or more Payloads. | Platform (the device) | ADR-001 §5 `asset`/`node` naming |
| **Headend** | The central management, storage, and authority that Nodes and operator clients talk to. | Platform | TimeLapse Pro topology (Mac Mini headend) |
| **Operator / Customer Principal** | A human or service identity acting on the system, scoped by RBAC + JIT. | Platform (identity) | SABSA Accountability; RBAC doc |
| **Target (OT backend, secondary system)** | A system behind the edge that a payload's mission reaches (e.g. a waterworks SCADA). Reached only via platform conduits. | External, reached via conduit | ADR-001 §6; invitation future-payload test cases |

The **decisive conceptual fact**: Platform Core and Payload are *separate trust subjects*, even when co-located on a Node. The Payload is not a subroutine of the Platform; it is a tenant of the Platform's runtime.

---

## 2. IEC 62443 zones and conduits

Mapping the conceptual entities to zones/conduits (IEC 62443-3-2). This generalises TimeLapse Pro's existing trust boundaries (SABSA §3) to the multi-payload case.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ZONE: OPERATOR / CUSTOMER (untrusted network)                          │
│  Browser, admin console, future customer portal                         │
└───────────────┬─────────────────────────────────────────────────────────┘
                │  C1: HTTPS + JWT + RBAC + (step-up MFA on sensitive ops)
                │  (C1 inherits SEC-005/008: short-lived JWT, policy TOTP)
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ZONE: HEADEND (managed, semi-trusted)                                  │
│  Platform Core services · Multi-tenant data plane · Authority (config,  │
│  OTA, signing) · SIEM/CMDB/Audit · JIT access broker                    │
└───────────────┬─────────────────────────────────────────────────────────┘
                │  C2: signed config pull / signed OTA push (existing
                │      TL-QA-APP/TL-OS/TL-EDGE-IMG trust model, ADR-001 §2)
                │  C3: SFTP (port 22222) chroot per site, SHA-256 verify
                │  C4: reverse-SSH conduit, customer-approved, autossh
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ZONE: NODE — Platform Core (semi-trusted, hardened)                    │
│  Identity · Config manager · Update agent · Telemetry collector ·       │
│  Tunnel client · HAL · Storage/quarantine · PAYLOAD SUPERVISOR          │
│  (the payload supervisor is the zone-and-conduit enforcement point)     │
└───────────────┬─────────────────────────────────────────────┬───────────┘
                │  C5: PayloadDriver contract                 │  C7: JIT
                │  (control plane, separate SemVer)           │  conduit
                │  ───────────────────────────────             │  (remote
                │  C6: data-plane contract, separate SemVer   │  support/
                │      (images, video, future OT streams)     │  vendor)
                ▼                                              ▼
┌──────────────────────────────┐              ┌────────────────────────────┐
│  ZONE: PAYLOAD (least-       │              │  ZONE: TARGET / OT backend  │
│  privilege, isolated process)│              │  (untrusted, reached only   │
│  Timelapse payload today     │              │   via platform conduit;     │
│  Future: waterworks, etc.    │              │   e.g. SCADA, sensors)      │
└──────────────┬───────────────┘              └─────────────────────────────┘
               │  C8: HAL-mediated device access (camera/USB/PTP,
               │      GPIO, future Modbus/GPIO per manifest allowlist)
               ▼
        [physical device: camera / sensor / relay]
```

### Zone trust levels (IEC 62443 SL concept)

| Zone | Trust | Rationale |
|---|---|---|
| Operator/Customer | Untrusted network | Internet-facing; only auth + TLS reach the headend |
| Headend | Managed | Hardened host, but holds all customer data — high value, defend in depth |
| Node Platform Core | Semi-trusted | Physically exposed, networked; hardened OS, signed artifacts, but assumes it may be compromised (store-and-forward autonomy proves this assumption) |
| Payload | Least-privileged tenant | Runs in its own process with only manifest-declared capabilities. *The key change from TimeLapse Pro:* payload is explicitly *below* platform core in trust. |
| Target/OT backend | Untrusted-external | Reached only through a platform JIT conduit; never by an inbound port on the OT network |

### Conduits and their guarantees (summary)

| Conduit | Carries | Security guarantees | Evidence lineage |
|---|---|---|---|
| C1 operator→headend | API/UI traffic | TLS, JWT, RBAC, step-up MFA | SEC-004/005/008 |
| C2 headend→node (control) | Config, OTA policy | Signed artifacts, versioned | ADR-001 §2; UPD-004 |
| C3 headend↔node (file) | Images, backups | SFTP chroot, SHA-256, ED25519 | SEC-007; SABSA Integrity |
| C4 node→headend (mgmt) | Reverse SSH | Customer-approved, autossh, deny-flag | CFG-005 |
| C5 platform→payload (control) | Lifecycle, configure, command, health | **Versioned PayloadDriver contract (SemVer)**, command allowlist, fail-closed | ADR-001 §2 + amendment 2 |
| C6 payload→platform (data) | Images, video, future OT telemetry | **Versioned data-plane contract (SemVer)**, quota-enforced | ADR-001 amendment 2 |
| C7 operator/vendor→payload | Remote support | **JIT/AccessTicket**, short-lived identity, destination allowlist, session recording, kill switch | ADR-001 amendment 5; R19 |
| C8 payload→device | Hardware access | HAL-mediated, allowlist per manifest | Existing `edge/hal/`; ADR-001 §1 HAL |

---

## 3. Conceptual security policy (the "what")

Inherited from SABSA Conceptual (TimeLapse Pro) and sharpened for the multi-payload platform:

1. **Zero-trust between platform and payload.** No implicit trust from co-location. Every cross-boundary call is authenticated, authorised, and logged.
2. **Defense-in-depth at every zone boundary.** No single control is load-bearing alone.
3. **Autonomy at the edge under network failure.** The Node Platform Core and its Payloads continue to fulfil their mission when the Headend is unreachable (Availability/Resilience).
4. **Tenant isolation is a platform property, not a payload responsibility.** A payload never sees another tenant's data; it queries through a platform data service that enforces row-level scoping.
5. **Capability fail-closed.** A payload that needs a capability it has not been granted is denied, and the attempt is logged. (ADR-001 amendment 3.)
6. **Time authority is platform infrastructure.** Synchronicity (multi-camera within 1 s) is delivered as a platform service payloads consume, not reinvented per payload.
7. **Remote access is always a conduit, never a port.** C7 is the only legal path for support/vendor access to a payload or its OT backend.
8. **Environment is a trust boundary now.** `rd`/`staging`/`prod` are separate trust domains today (SABSA §3 note); default-deny agent access to staging/prod; break-glass is a logged exception.

---

## 4. The conceptual contract (preview — detail in ADR-Z-001)

The Platform Core and a Payload interact through exactly two versioned contracts:

- **Control-plane contract (`PayloadDriver`)** — lifecycle: `configure(policy)`, `tick(now)`, `collect_telemetry()`, `handle_command(cmd)`, plus failure-contract methods (amendment 4). SemVer.
- **Data-plane contract** — bulk data ingest (images, video, future OT streams), quota-enforced, separate SemVer.

A Payload also *declares* a **capability manifest** (hardware needs, resource quota, file/network allowlist, own service identity, health/rollback contract, data classification). The Platform *enforces* the manifest; the Payload never grants itself privileges. This is the conceptual heart of the whole architecture.
