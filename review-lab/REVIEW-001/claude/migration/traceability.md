# Source-to-Target Traceability

- **Source:** `froekjaer/timelapse-pro@eed9e3c8` · **Reviewer:** Claude · **Date:** 2026-07-31
- Modes: **Reused** (as-is), **Adapted** (moved/split behind new boundary), **Rewritten** (re-implemented against new contract), **Rejected** (not carried forward, with reason). Migration stage references `migration-strategy.md`.

## Code

| Source element | Target | Mode | Stage |
|---|---|---|---|
| `headend/main.py` (18.5k lines, 234 routes) | dissolved into 4 services; composition-only remainder | Rewritten-in-place (strangler) | 1–4 |
| `headend/api/*` routers (19) | re-mounted via secure-router factory under owning service | Adapted | 1 |
| Auth/JWT/MFA/RBAC modules | `platform/headend/control_api/auth` | Adapted | 1 |
| Config authoring + signing | `control_api/policy` | Adapted | 1 |
| OTA/update flow (headend+edge) | `control_api/ota` + agent update module | Adapted (trust model reused unchanged) | 1,3 |
| `siem.py`, `syslog_receiver.py`, `itim.py` | `platform/headend/data_plane/telemetry` | Adapted | 2 |
| `storage_registry.py`, `backup_integrity.py` | `data_plane/storage` + retention engine | Adapted + extended (classification) | 2 |
| SFTP ingestion path | wrapped as blob `DataChannel` v1 | Adapted (wrapper) | 2 |
| `cmdb.py` + GRC schema (PostgreSQL) | platform CMDB/GRC (neutral nouns additively) | Reused | 1–2 |
| `edge/agent.py` | `platform/edge_agent` (agent core) + supervisor | Adapted (split) | 3 |
| `edge/config`, `edge/update`, `edge/tunnel` | edge_agent modules | Adapted | 3 |
| `edge/hal/*` | platform HAL with capability-scoped grants | Adapted | 3 |
| `edge/camera`, `edge/capture`, edge QA, `npu_viplite` | `payloads/timelapse/edge` behind PayloadDriver | Adapted | 3 |
| `edge/security.py`, HMAC identity | node identity module; superseded by mTLS at stage 3 (kept as fallback) | Adapted | 3 |
| AI tagging (Gemini), site look, video build | `payloads/timelapse/headend` domain service | Adapted | 4 |
| Ollama/Gemini provider glue | shared provider adapters (no domain ownership) | Adapted | 4 |
| `timelapse-ui/` (React) | `experience/ui` | Reused (restructure later by service) | 1+ |
| `node-agent/` | merged into platform agent heartbeat/health | Rewritten (small) | 3 |
| `tests/test_architecture_ratchet.py`, route-auth sweep | `tests/architecture/` re-targeted + extended | Adapted | 0 |
| `headend/tests/*`, `tests/*` suites | follow their components | Reused/Adapted | all |
| Edge/headend generators + `deploy/` manifests | `deployments/profile-a` | Adapted | 1–3 |
| `technician_ui.py` / `technician_auth.py` | provisioning flow in agent + control_api | Adapted | 3 |
| `www/`, `website/` | unchanged (separate hosting decision retained) | Reused | — |
| `z.ai/`, `sprint_c/`, `*.bak`, inventory snapshots | not carried; remain in source repo as history | Rejected (superseded working artifacts; source repo preserved) | — |
| `fix_schema.sh`, ad-hoc scripts | replaced by migrations discipline | Rejected (risk: unaudited schema mutation) | 1 |

## Architecture & governance decisions

| Source decision | Disposition |
|---|---|
| ADR-001 platform/payload split + 6 amendments + AI domain split | **Retained, refined** — ADR-CL-002 (refinements listed there) |
| ADR-001 `tick(now)` control sketch | **Rejected in favour of start/stop + driver-internal scheduling** — ADR-CL-004 (flagged deviation) |
| ADR-0007 product→platform vision | Retained as mission framing (business-architecture §1) |
| K1–K6 governance controls | Retained; K1/K2 strengthened to by-construction (ADR-CL-003) |
| Additive naming, no hard delete, commit-before-deploy | Retained as platform invariants |
| 8443/CrushFTP exposure design, DNS-01 | Retained for profile A; explicitly quarantined from contracts (O-05) |
| Monorepo model A → migratable to B | Retained |
| GRC register in PostgreSQL as single source | Retained and extended (evidence by-product principle) |
| No-go decision + go-live checklist A–L | Retained as migration gate currency (ADR-CL-006) |

## Documentation

Authoritative v10 docs → English platform docs regenerated per component as components migrate (stage-by-stage, not big-bang translation); living documents (handover log, health register) → replaced by ops dashboard + GRC where mechanisms exist; historical/`Gamle versioner/` → stays in source repo (evidence, never migrated). Known-inconsistency tracking (DOKUMENTPAKKE) → dissolved by moving invariants into schemas/tests (O-03 treatment).

## Coverage statement

All 30 top-level source directories/files reviewed for disposition; anything not named above follows its parent component. No source element is deleted by this plan; the source repo is preserved intact as the historical record (BASELINE.md preservation clause).
