# Physical Architecture (SABSA Physical Layer)

- **Reviewer:** Claude · **Date:** 2026-07-31

## 1. Principle: deployment-agnostic contracts, concrete first deployment

The logical architecture must run on the hardware the business already owns (baseline O-05), while nothing in the contracts may assume that hardware. Two physical profiles are defined; both are the same logical system.

## 2. Profile A — current estate (migration target, stages 0–3)

| Element | Physical realisation |
|---|---|
| Headend | Mac Mini (macOS), PostgreSQL, nginx, FastAPI processes under LaunchDaemons; UI static build; Ollama local. All four logical services initially in one FastAPI process with enforced router boundaries |
| Public exposure | `backend.timelapse-pro.dk:8443` direct nginx (CrushFTP owns 80/443) with DNS-01 certs — unchanged from source go-live design; marketing site hosted separately |
| Edge node | Orange Pi 4 Pro (Linux), platform agent + payload as **separate systemd services**: distinct users, `CPUQuota`/`MemoryMax`/`TasksMax` (cgroups v2), `ProtectSystem=strict` + explicit `ReadWritePaths` (fs allowlist), `IPAddressAllow/Deny` (net allowlist), device access via supplementary group/udev grant |
| Data plane transport | Existing SFTP ingestion retained initially (spool → SFTP), fronted by the `DataChannel` blob implementation; HTTPS channel endpoint added at stage 2 |
| Backup | Local + off-site target with scripted, evidenced restore test (closes source R09) |

**Isolation honesty (from baseline S-03):** systemd/cgroups on the Orange Pi gives real resource and filesystem/network containment with near-zero marginal cost, and is validated by **SPIKE-01** (measured overhead + kill/rollback drill on actual hardware) before the isolation claim is recorded as evidenced. Container runtimes remain an option behind the same supervisor interface but are not required (ADR-CL-005).

## 3. Profile B — future/portable (stage 4+)

Linux or cloud headend: the four logical services as containers (or systemd units) behind any TLS terminator on standard ports; PostgreSQL managed or self-hosted; object storage optionally replacing filesystem blob store behind the same `DataChannel` interface. Edge unchanged. Profile B exists to prove no macOS/CrushFTP/port-8443 accident leaked into the architecture; a CI job builds and boots Profile B headend services on Linux from stage 2 onward.

## 4. Physical security mapping (IEC 62443-aligned zones)

| Zone | Physical boundary | Conduits in/out |
|---|---|---|
| Edge platform zone | platform agent service + node OS | TLS to headend control API; SFTP/HTTPS data upload; reverse-SSH JIT tunnel (outbound only) |
| Edge payload zone | payload systemd sandbox | local control socket to agent; spool directory (write-only); granted devices only |
| Customer/OT zone (future) | payload-attached process equipment | via payload zone only, through declared conduits; never directly internet-exposed |
| Headend control zone | control API + policy signing + RBAC | 8443 via nginx; admin step-up (MFA) |
| Headend data zone | ingestion/storage/retention/backup | SFTP/HTTPS ingest; storage volumes; backup target |
| Operator zone | Peter's admin context + AI sessions | RBAC'd UI/API; JIT tickets for node access; no standing SSH to fleet |

Keys: node identity keys on-device (TPM/secure element absent on Orange Pi — accepted residual risk, compensated by revocation + short-lived credentials; recorded in risk register RR-07). Signing keys for policy/OTA/payloads live only on the headend signing service (offline-capable procedure documented for the root).

## 5. Physical constraints acknowledged

CrushFTP port ownership (8443 design retained until estate changes); single Mac Mini = headend SPOF (mitigated by evidenced restore, not HA — proportionality, business-architecture §4); Orange Pi NPU/AI modes remain payload-internal concerns; Nikon camera control (gphoto2) stays inside the timelapse payload sandbox with USB device grant.
