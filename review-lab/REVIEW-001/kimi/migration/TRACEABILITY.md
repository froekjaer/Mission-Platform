# Traceability — Source → Target (frozen baseline eed9e3c8)

Notation: **R**=genbruges uændret · **A**=adapteres · **W**=omskrives · **X**=afvises/udgår · **N**=nyt i Mission Platform

## Edge

| Kilde (timelapse-pro) | Mål (Mission Platform) | Disp. | Begrundelse |
|---|---|---|---|
| `edge/hal/` | `platform-core/hal/` | **R→A** | Korrekt abstraktion; flyttes til kernel (GPIO er platform-capability) |
| `edge/camera/` (gphoto2/PTP, Nikon Z30, relæ) | `payloads/timelapse/adapters/camera/` | **R** | Bevist driver-logik; pakkes bag `capture.now` |
| `edge/capture/quality.py` (blur/brightness QA) | payload QA-adapter | **R** | Domæne-QA; bevist kalibrering |
| `edge/capture/buffer.py` (cirkulær 50 GB) | payload storage, under diskquota | **R** | Bevist store-and-forward |
| `edge/upload/` (API+SFTP, slots) | data plane via kernel-ingest | **A** | Transport bevares; rute ændres til kernel-verificeret ingest |
| `edge/config/` (tre-lags hierarki) | `platform-core/config/` | **A** | Generaliseres: payload-config er et scoped subtræ |
| `edge/security.py` (artifact-verifikation) | kernel policy-engine | **A** | Opgraderes: Ed25519 (ADR-K003), fail-closed |
| `edge/update/` (OTA, signering) | `platform-core/update/` | **R** | Samme trust-model udvides til payload-pakker |
| `edge/diagnostics/` | kernel telemetry-reporter | **A** | Node-metrik er platform; kamera-metrik bliver payload-telemetry |
| `edge/agent.py` (139 KB, `_lab_tick` 457 linjer) | kernel supervisor + payload driver-livscyklus | **W** | Monolittens tick-maskine splittes: scheduling → payload, policy/supervision → kernel |
| `edge/technician_auth/ui.py` + BT TOTP | conduit + technician-app | **W** | SEC-016: default-secret fjernes; adgang via JIT (ADR-K004) |
| `edge/tunnel/` (autossh reverse) | conduit-fallback under migration | **A** | Bevares indtil Conduit Broker verificeret |
| `edge/ai/` (site-look, optimizer, NPU) | payload-AI | **R** | Domæne; NPU-runtime parkeres (ikke REVIEW-001-scope) |
| `edge/frame_push.py` (live view) | udskudt | **X** (midlertidigt) | Kræver udvidet data plane; dokumenteret begrænset |

## Headend

| Kilde | Mål | Disp. | Begrundelse |
|---|---|---|---|
| `headend/main.py` (18.549 linjer) | `platform-headend/platform/*` + `payloads/timelapse/headend/*` | **W** | Strangler-udtræk pr. modul; main.py → composition root |
| `headend/cmdb.py` | `platform/devices/` | **A** | Domæneneutral CMDB (asset/node-vokabular, additivt) |
| `headend/database.py` + `schema_v2.sql` | Uændret DB-lag | **R** | PostgreSQL + additiv skema-evolution |
| Auth/RBAC (i main.py) | `platform/auth/` — første udtræk | **W** | Kritisk masse; cirkulær-import-mønsteret brydes her |
| `headend/siem.py`, `itim.py`, syslog | `platform/telemetry/` | **A** | Domæneneutral observability |
| `headend/redaction*.py` | `payloads/timelapse/` (persondata er billeddomæne) | **A** | SEC-001-klassen lukkes via router-policy-byggefejl |
| GRC-register (`grc_register_api.py`) | `platform/grc/` | **R** | Fremragende fundamenter (auth på alle endpoints, hashbar evidens) |
| Update-flow + provisioning | `platform/updates/` + `platform/identity/` | **A** | Generaliseres til payload-pakker |
| `headend/ai/` (tagging, vocabulary) | `payloads/timelapse/headend/ai/` | **A** | Domæne-AI; provider-adaptere til fælles infra |
| `compliance_intelligence.py` | `platform/grc/` | **R** | Platform-funktion |
| `openwebui_runtime.py` | udskudt | **X** (midlertidigt) | R27-læringen: committes via change-ticket når det modnes |
| Backup/restore (`deploy/scripts/backup.sh`) | container-volume-backup + kvartalsvis restore-test | **W** | R09: default skal virke; fejl skal være høje |

## Tværgående

| Kilde | Mål | Disp. |
|---|---|---|
| ADR-001 + amendments | Bekræftet; konkretiseret af ADR-K001/K002 | **R** |
| K1–K6 kontroller | Byggefejl + ratchet-ceremoni | **A** |
| SABSA v10 business attributes | Arvet + 2 nye (Substitutability, Enforceability) | **A** |
| GRC som autoritativ statuskilde | Uændret princip | **R** |
| macOS/LaunchDaemon-drift | Container-pakke (ADR-K005) | **W** |
| SHA-256 sidecar-evidensmodel | Generaliseret til data-envelope-v1 | **A→N** |

## Dokumentation

Alle v10-dokumenter: **R som evidens** (frozen, read-only). De flettes ikke ind i Mission Platform; deres læring er destilleret i denne aflevering med kildehenvisninger (se `evidence/SOURCE-EVIDENCE.md`).
