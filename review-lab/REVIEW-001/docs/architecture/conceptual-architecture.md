# Conceptual Architecture (SABSA Conceptual Layer)

- **Reviewer:** Claude · **Date:** 2026-07-31

## 1. Core concept: Missions, not products

The platform runs **Missions**. A Mission is a long-lived assignment of a **Payload** (domain capability) to one or more **Nodes** (edge devices) on behalf of a **Customer**, governed by **Policy** and producing **Mission Data**.

```
Customer ──owns──> Site ──hosts──> Node ──runs──> Payload instance
                                        │
Mission = (Payload, Node(s), Policy, Customer, lifetime)
                                        │
                              Mission Data ──> Headend ──> Products (archives, video, dashboards)
```

TimeLapse Pro's "camera at a construction site for 3 years" is one Mission with the timelapse payload. A waterworks sensor deployment is another Mission with another payload — same platform concepts, different payload.

## 2. The two-plane, two-layer model

Everything in the system is placed by two orthogonal cuts:

**Cut 1 — Platform vs. Payload** (retained from source ADR-001, refined in ADR-CL-002):
platform = would look identical for a waterworks; payload = domain-specific.

**Cut 2 — Control plane vs. Data plane** (elevated from amendment to first-class structure, ADR-CL-003/004):
control = small, structured, security-critical messages (identity, config, commands, health);
data = large or continuous mission data (images, video, telemetry streams).

This yields four quadrants; every module in the target architecture belongs to exactly one:

| | Control plane | Data plane |
|---|---|---|
| **Platform** | Identity & enrollment, policy/config distribution, OTA, RBAC, JIT remote access, health/heartbeat, GRC | Ingestion service, storage & retention engine, telemetry pipeline, backup |
| **Payload** | Payload lifecycle (configure/start/stop), payload commands, capability manifest | Domain data production (captures, sensor readings) and domain processing (QA, AI tagging, video build) |

**Why?** The source system's recurring failure class (unauthenticated routes) and its monolith both stem from mixing quadrants in one module (`main.py` serves all four). **Because?** Baseline facts F-03, F-05, O-02. **For whom?** The operator (smaller blast radius, auditable surfaces) and future OT customers (data sovereignty needs a distinct data plane).

## 3. Trust model (conceptual)

- Every actor (human, node, payload instance, AI session, service) has its **own identity**; payload identity ≠ platform identity (retained from source ADR-001).
- **Fail-closed** everywhere: absence of policy, unknown capability, unverifiable signature, expired ticket ⇒ deny and log.
- **Zones and conduits** (IEC 62443 alignment): Customer/OT zone, Edge node zone (platform core and payload sandbox as separate sub-zones), Transport, Headend zone (control/data sub-zones), Operator zone. All inter-zone traffic passes named conduits with explicit authentication; remote human/AI access to edge or OT only via JIT tickets through the platform conduit.
- **Signing chain:** config, OTA artifacts and (later) payload packages are signed; nodes verify before use — extends the source system's existing signed-config/OTA trust model to payloads.

## 4. Contract concept

Platform and payload meet only at versioned contracts (detailed in ADR-CL-004):

1. **Control contract** — payload lifecycle + command interface (`PayloadDriver`), SemVer'd.
2. **Data contract** — typed, classified data channels (`DataChannel`: blob | timeseries | event) the payload publishes through; the platform owns transport, storage and retention enforcement.
3. **Capability manifest** — the payload's declaration of required hardware, resources, network, data channels and their classifications; validated fail-closed against operator-signed policy.

The **anti-coupling invariant**: platform code never imports payload code; a payload sees only the contract package. This is machine-enforced (CI import test + second-payload smoke test), not convention.

## 5. Conceptual data model

```
Customer (tenant) ─< Site ─< Node ─< MissionAssignment >─ PayloadType(version)
MissionAssignment ─< DataChannel(classification, retention) ─< DataObject/Series
Node ─< NodeIdentity, NodeState, UpdateState
Actor(human|ai|service) ─< Role ─< Permission          (RBAC, platform-wide)
AccessTicket(actor, target, scope, expiry)             (JIT conduit)
Evidence(control, artifact, timestamp)                 (GRC register)
```

Neutral nouns (`node`, `mission`, `data_channel`) are used for all new platform constructs; existing `camera`/`capture` vocabulary survives inside the timelapse payload only — consistent with the source's additive-naming rule.

## 6. What this concept deliberately does not contain

No message broker as a required backbone (channels may be implemented over HTTPS/SFTP now, broker later behind the same contract). No orchestration cluster. No payload marketplace. Federation of multiple headends remains out of scope, as in the source ADR-001.
