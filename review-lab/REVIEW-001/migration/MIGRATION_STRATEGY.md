# Migration Strategy — TimeLapse Pro → Mission Platform

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Source baseline:** `timelapse-pro@eed9e3c8c67369e1924c25a11908616220c3c753`

This strategy derives the Mission Platform from TimeLapse Pro under the constraints of ADR-Z-003 (additive, wrap-first, ratchet-gated). TimeLapse Pro stays in production throughout. No step is irreversible.

---

## 1. Guiding constraints (binding)

1. **TimeLapse Pro stays live.** No step may regress the integrity chain, tenant isolation, or capture autonomy.
2. **Additive naming, no broad renames** (ADR-001 §5). `camera`/`capture` stay; `node`/`asset` are additive.
3. **No schema break before live verification** (project principle). Migrations are additive; `camera_id` added alongside `device_id` is the proven pattern (ADM-013).
4. **Ratchet-only** (K1–K7, ADR-Z-003 §3). The `main.py` route/line ceiling may only decrease.
5. **Never hard-delete** — quarantine/reversible-move only (project principle).
6. **Wrap before extract.** The contract is proven against existing behaviour before any code moves.

---

## 2. Source-to-target traceability

Every material source component maps to a target disposition: **Reuse** (moved largely as-is), **Adapt** (moved + reshaped to a contract/platform service), **Rewrite** (new implementation), or **Reject** (deliberately not carried; with reason).

### Edge side

| Source (`timelapse-pro@eed9e3c8`) | Target | Disposition | Notes |
|---|---|---|---|
| `edge/hal/{base,generic,orangepi,rpi,jetson}.py` | `platform/hal/` | **Reuse** | Already a clean abstraction; promote to platform. |
| `edge/config/manager.py` + signed config hierarchy | `platform/config/` | **Adapt** | Additive: expose as platform service to payloads. |
| `edge/update/` | `platform/update/` | **Reuse** | Signed OTA already implements ADR-001 §2 trust. |
| `edge/tunnel/ssh_manager.py` | `platform/access/` | **Adapt** | Becomes the JIT conduit client (amendment 5). |
| `edge/upload/{headend_client,sftp}.py` | `platform/storage/` + data-plane | **Adapt** | SFTP integrity path becomes data-plane contract backend. |
| `edge/cmdb/{collector,executor}.py` | `platform/telemetry/` | **Reuse** | CMDB collection is platform-owned. |
| `edge/camera/` + `edge/capture/` | `payloads/timelapse/{capture}` | **Adapt** | Wrapped behind `PayloadDriver`; the wrap proves the contract. |
| `edge/ai/` (site-look, NPU QA) | `payloads/timelapse/ai/` | **Adapt** | Payload-owned AI per ADR-001 AI-split. |
| `edge/npu_viplite/` (C++) | `payloads/timelapse/ai/` (native dep) | **Reuse** | Native compute as payload-owned dependency (Q-3). |
| `edge/agent.py` (the edge orchestrator) | `platform/supervisor/` | **Rewrite** | Becomes the payload supervisor (ADR-Z-002). The orchestration intent is reused; the implementation is new because it must enforce isolation. |
| `edge/diagnostics/`, `edge/utils/` | `platform/` various | **Reuse/Adapt** | Utility code reused where generic. |

### Headend side

| Source | Target | Disposition | Notes |
|---|---|---|---|
| `headend/main.py` (234 routes) | `headend/api/<domain>/` router packages | **Adapt** | Decomposed behind K1/K2/K3 ratchet. The largest single work item. |
| `headend/api/*.py` (already-extracted routers) | `headend/api/<domain>/` | **Reuse** | The 19 partially-extracted routers are the seed; pattern continues. |
| `headend/cmdb.py`, `headend/siem.py`, `headend/itim.py` | `platform/telemetry/` | **Adapt** | Platform-owned SIEM/CMDB/ITIM. |
| `headend/ai/*` (tagging, Gemini, Ollama) | `payloads/timelapse/ai/` | **Adapt** | Payload-owned AI; shared Ollama/Gemini adapters stay as platform infra. |
| `headend/services/*` (artifact_trust, fair_risk, etc.) | `platform/` + payload | **Adapt** | Split by ownership: trust→platform, fair_risk→payload, etc. |
| `headend/database.py`, `headend/schema_v2.sql`, migrations | `platform/tenants/` + schema | **Adapt** | Multi-tenant data service wraps the schema; row-level isolation enforced here. |
| `headend/redaction*.py` | `payloads/timelapse/` | **Adapt** | Redaction is image-domain → payload. (UI-010, currently missing.) |
| `headend/edge_provisioning_security.py`, `services/bootstrap_security.py` | `platform/identity/` | **Adapt** | Enrollment/bootstrap is platform-core. |
| `headend/storage_registry.py`, `backup_integrity.py` | `platform/storage/` | **Reuse** | Canonical-path registry + integrity already target-shaped. |
| `timelapse-ui/` (React) | `payloads/timelapse/ui/` + `headend/ui-shell/` | **Adapt** | Timelapse pages become a plugin; shared chrome becomes the shell. |

### Explicitly rejected (with reason)

| Source | Disposition | Reason |
|---|---|---|
| `headend/main.py` as a single file | **Reject** (as-is) | The monolith is the disease, not the patient. Code is adapted out; the file does not survive. |
| Legacy git-based edge update | **Reject** | Already opt-in/disabled (UPD-003); headend-mediated only going forward. |
| `ISSUES.md` as status source | **Reject** | GRC register (PostgreSQL) is source of truth (per `00_START_HER.md`). |
| HS256 JWT long-term | **Reject** (long-term) | Asymmetric RS256/EdDSA is the open architecture decision (SABSA §5); carried forward as a platform-identity migration item, not preserved. |

---

## 3. Sequencing (detail for ADR-Z-003 §"Sequencing summary")

Each step is independently shippable, reversible, and gated by tests + ratchet.

### Step 0 — Contract spike (PROOF GATE)

**Goal:** prove the contract fits reality before anything moves.
**Do:** define `contracts/` (PayloadDriver, data-plane, manifest schema); write a timelapse `driver.py` that *wraps* the existing `edge/capture` + `edge/camera` tick logic without moving it; write contract tests; write the capability-enforcement test (ADR-Z-002 validation).
**Gate:** contract tests green against today's capture behaviour; enforcement test demonstrates fail-closed on an undeclared capability.
**Reversibility:** 100% — no production code moved; the wrapper can be deleted.
**This is what the vertical slice in this submission implements.**

### Step 1 — Promote the already-modular edge packages

**Goal:** make the existing clean abstractions into the platform spine.
**Do:** move `edge/hal` → `platform/hal`; `edge/config` → `platform/config`; `edge/update` → `platform/update`; `edge/upload` → `platform/storage` + data-plane backend. Additive imports keep the edge running.
**Gate:** edge still boots, captures, uploads; K1–K3 green.
**Reversibility:** high — these are already modular.

### Step 2 — Platform supervisor + isolation

**Goal:** payloads run as isolated tenants (ADR-Z-002).
**Do:** implement `platform/supervisor/` (manifest validation, systemd unit generation, seccomp filter, lifecycle). Load the Step-0 timelapse wrapper as the first real isolated payload. Replace the old `edge/agent.py` orchestrator incrementally (both can coexist behind a flag).
**Gate:** timelapse payload runs as `dk.froekjaer.payload-timelapse.service` under a dedicated user; capability-enforcement test passes on the real node; rollback path verified.
**Reversibility:** flag-guarded coexistence with the old orchestrator.

### Step 3 — Decompose the headend monolith (ratchet-only)

**Goal:** extract `main.py` routers behind K1/K2/K3.
**Do:** follow P2-01 (`P2-01_Refaktoreringsplan_main_py.md`), one router family at a time, into `headend/api/<domain>/`. Every extraction must pass K1 (route-auth), must not add to `main.py` (K2), and must lower the ratchet ceiling (K3).
**Gate:** ratchet ceiling monotonically decreasing; route-auth sweep green at every commit; no behaviour change verified by the existing test suite.
**Reversibility:** per-router; a bad extraction is reverted.

### Step 4 — Platform-owned cross-cutting services

**Goal:** tenants, audit, access become platform services.
**Do:** extract `platform/tenants/` (row-level isolation wrapper), `platform/audit/` (append-only spine), `platform/access/` (JIT broker — builds on `Claude_Support_Access_Model_2026-07-06.md` design).
**Gate:** a payload cannot construct a cross-tenant query (Confidentiality test); every conduit interaction emits an audit record; JIT ticket lifecycle verified.
**Reversibility:** additive wrappers around existing data.

### Step 5 — Second (stub) payload

**Goal:** prove Extensibility (ADR-0007 review trigger, deliberately pulled forward as proof).
**Do:** implement a minimal `payloads/environmental-sensor/` (or similar stub) against the contract *only* — no platform code changes. Load it alongside timelapse on a LAB node.
**Gate:** the stub payload loads, is isolated, and cannot read timelapse's data. This is the Business-Arch §4 Extensibility criterion made executable.
**Reversibility:** the stub is deletable.

---

## 4. What this migration does NOT do (deferred to productionisation)

These are catalogued in the Risk Register with owners. They are productionisation work, not architecture work:

- The 11 🔴 hard blockers (intern CA/mTLS SEC-009, disk encryption SEC-010, backup/restore evidence PROV-004/005, GDPR DPIA SEC-012, redaction UI-010, etc.).
- Multi-headend federation (ADR-001 deferral).
- Multi-vendor payload trust ecosystem (ADR-001 deferral; Q-7).
- Full AI-tagging pipeline completion (CAP-005 backlog of 3033 tags).

The migration *enables* these by giving them a clean home (e.g. intern CA lives in `platform/identity/`; DPIA data flows from manifest `data_classification`), but does not complete them.

---

## 5. Risk of migration itself

| Risk | Mitigation |
|---|---|
| Contract doesn't fit real capture behaviour | Step 0 is exactly this test; revise contract, not capture, if it fails |
| Isolation breaks a legitimate payload operation | Fail-closed + clear logging + per-payload manifest CI test (K7) |
| Ratchet ceiling raised under pressure | K3 + documented-exception rule + CODEOWNERS on `architecture_baseline.json` |
| Two orchestrators drift during Step 2 coexistence | Flag-guarded; cutover gate with parity tests; old orchestrator quarantined, not deleted |
| Headend decomposition introduces route-auth regression | K1 sweep at every commit; this is exactly the failure class (SEC-001/R15/R22) the ratchet exists to prevent |

---

## 6. Compatibility matrix (platform ↔ payload)

Per ADR-001 amendment 4, the supervisor enforces a compatibility matrix on load. Initial policy:

| Platform contract version | Payload contract version | Load? |
|---|---|---|
| 1.x | 1.x | Yes |
| 1.x | 0.x | No (fail-closed, logged) |
| 2.x (future major) | 1.x | No unless payload declares compat shim |

This is deliberately strict: a payload that cannot state its contract version does not load.
