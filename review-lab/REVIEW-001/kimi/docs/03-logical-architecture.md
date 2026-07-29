# 03 — Logisk arkitektur (SABSA logisk lag)

## 1. Tjenestemodel

### 1.1 Platform Kernel (edge)

| Tjeneste | Ansvar | Interface |
|---|---|---|
| Supervisor | Start/stop/restart af payload-processer; quota via rlimits/cgroups; kill switch (process group) | intern |
| Policy Engine | Valider manifest mod signeret allowlist, **fail-closed + log** | `validate_manifest()` |
| Control Broker | Videresend allowlistede kommandoer til payload; timeout = unhealthy | control plane v1 |
| Evidence Ingester | Verificér artifact mod SHA-256 sidecar; afvis mismatch; stempel provenance | data plane v1 |
| Identity Agent | Per-device Ed25519-nøgle; attestér over for headend (mTLS) | intern + headend |
| Config Resolver | Signeret hierarki global→customer→site→device; cache til offline drift | arvet |
| Telemetry Reporter | Heartbeat + diagnostics + audit-events til headend | eksisterende kanal |

### 1.2 Timelapse-payload (logisk)

Arver baselinens moduler 1:1 som *logiske* enheder, nu bag kontrakten:

| Logisk modul | Fra baseline | Skæbne |
|---|---|---|
| Capture scheduler | `edge/agent.py` tick/schedule | omskrives til driver-livscyklus (configure/tick) |
| Kameradriver (gphoto2/PTP) | `edge/camera/` | **genbruges** som adapter under `capture.now` |
| Kvalitets-QA | `edge/capture/quality.py` | **genbruges** (blur/eksponering → quality-flag i sidecar) |
| Cirkulær buffer | `edge/capture/buffer.py` | **genbruges**, rykkes under payload-diskquota |
| Upload (API+SFTP) | `edge/upload/` | **adapteres** til data plane via kernel-ingest |
| Site-look / autonomous optimizer | `edge/ai/` | **genbruges** som payload-AI (domæne) |
| Technician UI/BT | `edge/technician_*` | **adapteres** — men SEC-016-læringen: intet default-secret, fail-closed |

### 1.3 Headend (modulær monolit)

```
headend/
  platform/            # kernel-spejling: domæneneutrale tjenester
    auth/              # FØRSTE udtræk (identitet, RBAC, MFA, step-up)
    devices/           # enrollment, CMDB
    config/            # hierarki + signering
    updates/           # OTA artifacts, rollout, rollback
    telemetry/         # SIEM, ITIM, heartbeat
    grc/               # compliance-register (eksisterende GRC bevares)
    evidence/          # ingest-verifikation, retention, karantæne
    remote_access/     # JIT-tickets, conduit-kontrol, session-recordings
  payloads/
    timelapse/         # alt kundevendt: captures, galleri, tagging, site-look config
  ui/                  # eksisterende React-UI, payload-flader under payloads/
```

Logisk regel: **enhver router deklarerer sit domæne og sine dependencies; monteringen fejler bygget uden auth-dependency eller eksplicit public-begrundelse** (K1 arvet som *byggefejl*, ikke kun test).

## 2. Informationsmodeller (logisk)

- **Hierarki:** Tenant→Site→Node→Payload-instance. `camera` bliver en payload-instance af typen `timelapse` — additivt, eksisterende kontrakter omdøbes ikke (arvet ADR-001 §5).
- **Evidens:** Artifact(bytes) + Sidecar(hash, tid, provenance, klassifikation) + IngestReceipt(verificeret/afvist, aktør=kernel) + AuditEvent(append-only).
- **Beslutning:** ChangeTicket(scope, risiko, godkendelse, rollback) — arvet fra update-flow, generaliseret til alle muterende handlinger.

## 3. Interaktionsmønstre (Because — hvorfor disse og ikke andre)

| Mønster | Valg | Begrundelse |
|---|---|---|
| Edge→headend | Edge initierer alt (poll/heartbeat/upload) | Bevist i drift; NAT/firewall; ingen indgående flade |
| Kernel↔payload | Procesgrænse + stdio/spool | Ægte fault containment; ingen delt hukommelse at korrupte |
| Store data | Content-addressed artifacts, ikke DB-blobs | Bevist (canonical-images); simplificerer retention/backup |
| Kommandoer | Synkron allowlistet request/response med timeout | Failure contract er simpel: timeout = unhealthy = restart-policy |
| Config | Pull-baseret signeret hierarki | Offline-autonomi; rollback er at trække forrige version |

## 4. Failure contracts (skærper ADR-001 amendment 4)

| Fejl | Kontrakt |
|---|---|
| Payload-timeout | unhealthy → restart ifølge `manifest.health` (max_restarts, backoff) |
| Payload-crash | kernel genstarter; efter max_restarts → degraded mode + SIEM-event; sidste gode artifact-version beholdes |
| Manifest ukendt/ugyldigt | **afvis før exec**; log; ingen partial load |
| Artifact hash-mismatch | ikke accepteret; karantæne-beslutning tilhører retention-policy; aldrig stille drop |
| Version-mismatch (major) | payload loades ikke; compatibility-matrix i release-notes; rollback til foregående |
| Resource exhaustion | rlimit dræber barnet; kernel overlever (kernel har ingen per-payload state i hukommelsen) |
