# Migration — Strategi fra TimeLapse Pro til Mission Platform

## Principper

1. **Strangler-mønster:** ny platform vokser rundt om den gamle funktionalitet; intet big bang.
2. **Additivt og reversibelt** på hvert trin (arvet projektprincip: ingen skema-brud før live-verifikation, aldrig hard-delete).
3. **Kontrakttest mod eksisterende adfærd FØR flytning** — adfærden i monolitten er specifikationen, indtil beviset foreligger.
4. **Frozen baseline røres aldrig.** timelapse-pro fortsætter sin egen go-live-bane uforstyrret; Mission Platform arver gennem læsning, ikke gennem commits.

## Faser

### Fase 0 — REVIEW-001 (denne aflevering)
Kontrakter, kernel-PoC, timelapse-driver (syntetisk), dokumentation. Ingen produktionsberøring.

### Fase 1 — Hardware-spike (uge 1–2)
- Kernel + manifest på TL-C87FF9587CA0 (LAB).
- gphoto2-adapter bag `capture.now`; syntetisk frame erstattes af ægte capture.
- Mål RAM/CPU-overhead, capture-latency, boot-to-capture (<120 s-kravet).
- **Go-kriterium:** identisk capture-adfærd med QA-sidecar, ingen regression i upload.

### Fase 2 — Headend-udtræk, auth først (sprint-vis)
- `platform/auth` ud af main.py med uændrede URL'er; derefter devices/CMDB, config, updates, telemetry.
- Pr. udtræk: kontrakttest, ratchet-baseline sænkes, handover-entry.
- Parallel container-pakke i `rd` (ADR-K005).

### Fase 3 — Timelapse-payload isoleres
- edge/camera, edge/capture, edge/ai → `payloads/timelapse/adapters/` bag kontrakten.
- Headend: captures/galleri/tagging/vocabulary → `payloads/timelapse/headend/`.
- Kunde-UI røres først her — payload-flader flyttes uændret.

### Fase 4 — Modularitetsbevis: vandværk-stub
- Minimal Modbus-poll-payload bygget *kun* mod contracts + payload-sdk.
- Zone/conduit-register + SL-T dokumenteres (dokumentarbejde på eksisterende mekanik).
- **Dette er REVIEW-001-tesens eksamen:** lykkes stubben uden platform-ændring, er platformen reel.

### Fase 5 — Cutover & federation (når kunde kræver)
- Prod-cutover til container-pakke bag reversibel plan (30 dages staging først).
- Federation/multi-headend = separat ADR (arvet afgrænsning).

## Hvad der bevidst IKKE migreres i REVIEW-001

NPU-runtime, site-look matching, WebRTC live view, Open WebUI-integration, website. Alle har plads i arkitekturen; ingen er nødvendige for at bevise den.
