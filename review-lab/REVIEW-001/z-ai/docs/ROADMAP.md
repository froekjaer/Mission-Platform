# Roadmap — Z.ai REVIEW-001 Submission

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`

This roadmap sequences the next safe steps. It inherits TimeLapse Pro's sprint structure (`KRAVREGISTER §4`) where relevant, and aligns the architecture work (this submission) with the productionisation work (the 11 🔴 blockers). The guiding rule: **each step is reversible, gated, and independently shippable** (ADR-Z-003).

---

## Phase 0 — Validate the contract on real hardware (the immediate next step)

**The single most valuable next action.** The vertical slice proves the contract is *logically* sound; the next step proves it is *operationally* sound against a real edge.

| Step | Do | Gate | Reversibility |
|------|----|----|---------------|
| 0a | Port the `SyntheticCapture` to a real `Gphoto2Capture` wrapping the existing `edge/camera` Nikon Z30 driver | Captures real images through the contract; SHA-256 matches lens-to-archive | Fully — wrapper only |
| 0b | Generate a real systemd unit + seccomp filter from the timelapse manifest; run the payload as `dk.froekjaer.payload-timelapse.service` under a dedicated user | Capability-enforcement test passes on the real node; an off-manifest network attempt is denied and logged | Flag-guarded coexistence with old orchestrator |
| 0c | Confirm the contract fits every existing capture mode (day/night, LAB mode, multi-camera relay, focus-driven) | No capture behaviour lost vs. today | Contract revised (not capture) if a mode doesn't fit |

**Outcome:** the contract is proven against reality. Only then does extraction begin. This is ADR-Z-003's "wrap before extract."

---

## Phase 1 — Promote the already-modular edge packages (Migration Step 1)

Lowest-risk, highest-immediate-value. The edge is *already* half-modular.

| Step | Do | Gate |
|------|----|------|
| 1a | `edge/hal` → `platform/hal` | Edge boots, captures |
| 1b | `edge/config` → `platform/config` (signed policy hierarchy) | Policy provenance preserved |
| 1c | `edge/update` → `platform/update` (signed OTA) | Staged rollout still works |
| 1d | `edge/upload` → `platform/storage` + data-plane backend | SFTP integrity path intact |

---

## Phase 2 — Platform supervisor + isolation in production (Migration Step 2)

| Step | Do | Gate |
|------|----|------|
| 2a | Implement the systemd-unit + seccomp generator (the production `Sandbox`) | Unit generation test per manifest field |
| 2b | Load timelapse as the first real isolated payload | Rollback path verified; old orchestrator quarantined |
| 2c | Implement the JIT access broker (`platform/access/`) per `Claude_Support_Access_Model_2026-07-06.md` | Ticket lifecycle; kill switch; session recording |

---

## Phase 3 — Decompose the headend monolith (Migration Step 3, ratchet-only)

This is the longest phase and runs concurrently with productionisation. Follows `P2-01_Refaktoreringsplan_main_py.md`.

| Step | Do | Gate |
|------|----|------|
| 3a | Extract one router family at a time into `headend/api/<domain>/` | K1 (route-auth), K2 (no-new-in-main.py), K3 (ratchet decreases) at every commit |
| 3b | Continue until `main.py` is a thin composition root | Route count → near zero; the 234-route monolith is gone |

---

## Phase 4 — Platform cross-cutting services (Migration Step 4)

| Step | Do | Gate |
|------|----|------|
| 4a | `platform/tenants/` row-level isolation wrapper | Confidentiality test: payload cannot construct cross-tenant query |
| 4b | `platform/audit/` append-only spine | Every conduit interaction emits a record |
| 4c | `platform/time/` authority service | Synchronicity: site cameras within 1 s |

---

## Phase 5 — Prove Extensibility with a real second payload (Migration Step 5)

When a second vertical is on the horizon (ADR-0007 trigger), implement it against the contract *only*. The stub in this submission proves this is possible; a real payload proves it is *valuable*.

---

## Productionisation track (runs in parallel, NOT gated by architecture)

Inherited from `KRAVREGISTER §4` Sprints H–N. The architecture gives each a home; these tracks complete them:

- **SEC-009** intern CA/mTLS → `platform/identity/` (Sprint I)
- **SEC-010** disk encryption → `platform/` node hardening (Sprint K, needs physical access)
- **SEC-012** GDPR DPIA/retention/DPA → manifest `data_classification` feeds it (Sprint I)
- **PROV-004/005** backup/restore evidence → `platform/storage/` (Sprint M)
- **UI-010** redaction → `payloads/timelapse/` (Sprint I)
- Pre-Internet gate → port migration, etc. (Sprint H, the 🔴 blocker set)

---

## Milestones (indicative, not committed)

| Milestone | Depends on | Indicative |
|-----------|-----------|------------|
| Contract proven on hardware | Phase 0 | weeks, not months |
| First payload runs isolated in LAB | Phase 2b | ~1–2 sprints after Phase 0 |
| Monolith ratchet at half its ceiling | Phase 3 (partial) | concurrent |
| Pre-Internet gate passable | Productionisation track | per `GO_LIVE_CHECKLIST_v10` |
| Second real payload loads | Phase 5 | when a vertical is on the horizon |

---

## The "next safe step" in one sentence

**Port the vertical slice's `SyntheticCapture` to a real Nikon Z30 `Gphoto2Capture` and run the capability-enforcement test on the active edge node `TL-C87FF9587CA0`.** If the contract holds against real hardware, every later step is unlocked; if it does not, the contract is revised before any production code moves. That is the cheapest, most reversible, highest-information action available.
