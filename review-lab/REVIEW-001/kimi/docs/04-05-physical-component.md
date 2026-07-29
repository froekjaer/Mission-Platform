# 04 — Fysisk arkitektur (SABSA fysisk lag) · 05 — Komponentarkitektur

## 04 — Fysisk arkitektur (Med hvad?)

### 4.1 Edge (produktion, arvet hardware)

| Lag | Valg | Status vs. baseline |
|---|---|---|
| Hardware | Orange Pi 4 Pro (RK3588S, NVMe), Nikon Z30 via USB/PTP, relæ-strømstyring | Uændret |
| OS | Armbian Linux, systemd | Uændret |
| HAL | `edge/hal/` (orangepi/rpi/jetson/generic) | Genbruges — flyttes til **kernel**, fordi GPIO er en platform-capability, ikke payload-logik |
| Kernel runtime | Python 3 stdlib-proces (PoC); produktion: samme model, cgroup v2 quota i stedet for rlimits | Ny komponent |
| Payload runtime | Separat Python-proces pr. payload | Ny (strukturelt) |
| Data transport | SFTP/HTTPS, edge-initieret, SHA-256 verificeret | Uændret |
| Identitet | ED25519 host key (SFTP) + nyt: per-device Ed25519 signaturidentitet | Skærpet (ADR-K003) |

### 4.2 Headend (målbillede — se ADR-K005 for migration)

| Lag | I dag (baseline) | Målbillede |
|---|---|---|
| Vært | Mac Mini, macOS, LaunchDaemons | Linux (eller macOS i overgang), containerpakke (Podman/Docker), systemd |
| App | FastAPI/uvicorn monolit (main.py 18.549 linjer) | Samme FastAPI-app, men modulær opdelt; main.py som tynd composition root |
| DB | PostgreSQL `timelapse_db` (+ SQLite til test) | Uændret — PostgreSQL er det rigtige valg |
| Proxy | nginx, HTTPS | Uændret |
| AI | Ollama lokal + Gemini 2.5 Flash (Vertex EU) | Uændret — provider-adaptere som fælles infrastruktur, ejerskab i kaldende domæne |
| Storage | `/Volumes/data-fast` canonical + `/Volumes/Backup` | Portable mounts; canonical-begrebet bevares |

**Begrundelse for container-målbilledet (Because):** prod-drift på én Mac Mini med LaunchDaemons gør DR, reproduktion, staging-promotion og den erklærede open-source-vision afhængig af én persons hardware. Containere er ikke fashion — det er *provisioning som kode*. **For whom:** driftsejeren (DR), fremtidige selv-hostende kunder (suverænitet), reviewerne (reproducerbarhed).

### 4.3 Miljøer

`rd` → `staging` → `prod` med default-deny agent-adgang til staging/prod (arvet fra MILJOE_ARKITEKTUR + R19). Tilføjelse: **miljøflag parses fail-closed** — ukendt miljø = prod-regler, aldrig rd-regler. (Læring: `TIMELAPSE_ENV="rd"` kendes ikke af de 3 kodesteder der læser den — SABSA v10 §3.)

## 05 — Komponentarkitektur (Hvilke mekanismer?)

### 5.1 Nye komponenter (alle i PoC'en, se `implementation/`)

| Komponent | Mekanisme | Bevis |
|---|---|---|
| `EdgeKernel.validate_manifest` | HMAC-signatur (PoC) → Ed25519 (prod); schema-check; capability ∩ allowlist; quota-loft | test 1–3 |
| `EdgeKernel.command` | JSON-lines over stdio; allowlist; timeout-bound read | test 4 |
| `EdgeKernel.ingest_data` | glob sidecars → genberegn SHA-256 → compare_digest | test 5–6 |
| `EdgeKernel.kill_switch` | `setsid` + `killpg` | test 8 |
| rlimit-enforcement | `RLIMIT_CPU`, `RLIMIT_AS` i `preexec_fn` | start_payload |
| Audit | append-only eventliste (PoC) → SIEM-stream (prod) | test 9 |

### 5.2 Arvede komponenter (bevist i produktion, genbruges)

SHA-256 sidecar JSON · Fernet · pyotp · PyJWT (→ migration til EdDSA, ADR-K003) · bcrypt · FFmpeg · systemd watchdog · udev-symlinks · CircularBuffer · HMAC-signering af config/artifacts · chrony/NTP · autossh.

### 5.3 Komponentlandkort (fysisk→logisk trace)

```
Orange Pi 4 Pro
 └─ systemd: mission-edge-kernel.service      [kernel.py ~250 linjer]
     ├─ payload: timelapse (separat proces)   [driver.py → adapters til edge/camera, edge/capture]
     │    ├─ control: stdio JSON-lines        [control-plane-v1.schema.json]
     │    └─ data: /data/spool/timelapse/     [artifact + .sha256.json, data-envelope-v1]
     └─ identity: /etc/mission/device.key     [Ed25519, provisioneret, aldrig default]
```

### 5.4 Teknologivalg — begrundelser

| Valg | Because | Alternativ afvist |
|---|---|---|
| Python (edge + headend) | Hele baselinens beviste logik er Python; genbrug >> rewrite | Rust/Go-kernel: fristende for TCB-størrelse, men fordobler kompetencebehov og bryder genbrug. **Åben revisitation** når kernel-API er frosset |
| JSON Schema som kontraktsprog | Sprog-neutralt, validerbart, SemVer-venligt, læsbart for både mennesker og AI | gRPC/Protobuf: rigtigt ved >10 payloads eller OT-streaming; for tidligt nu — men kontrakterne er designet så transport kan udskiftes |
| HMAC i PoC / Ed25519 i prod | PoC skal køre uden nøgleinfra; prod skal ikke have delte secrets | HS256 fastholdt: afvist (ADR-K003) |
