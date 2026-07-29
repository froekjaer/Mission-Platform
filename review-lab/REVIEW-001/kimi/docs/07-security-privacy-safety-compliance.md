# 07 — Sikkerheds-, privacy-, safety- og compliance-arkitektur

## 1. Tillidsgrænser (opdateret model)

| Grænse | Retning | Kontrol |
|---|---|---|
| Internet ↔ headend | Indgående | nginx TLS, rate limit, route-auth-sweep som byggefejl, CORS fail-fast i prod (VPEN-2026-012) |
| Headend ↔ edge | Kun edge-initieret | mTLS (intern CA, arvet design 2026-07-05) + per-device Ed25519-identitet (ADR-K003) |
| Kernel ↔ payload | Lokal procesgrænse | Manifest fail-closed, quota, allowlist, ingen delt credential |
| Edge ↔ kamera/OT | USB/PTP, GPIO | Ingen netværkseksponering; HAL i kernel, aldrig i payload direkte |
| Support → edge/OT | Kun via conduit | JIT-ticket, kundegodkendelse, destinations-allowlist, recording, kill switch |
| Miljø (rd/staging/prod) | Ortogonal trust zone | Default-deny; fail-closed miljøflag-parsing |

**Trusselsantagelser (eksplicitte):** edge kan blive fysisk stjålet; payload kan have sårbarheder eller være leveret af tredjepart; headend kan blive kompromitteret (derfor: edge verificerer signaturer, stoler ikke på serverens ord); operatører laver fejl (derfor: defaults skal fejle lukket); AI-output kan være forkert (derfor: AI er forslag, ikke autoritet).

## 2. Fail-closed-katalog (systemisk svar på SEC-001/R15/R22/SEC-016/GOV-01)

| Historisk fund | Fejlklasse | Platform-invariant der lukker klassen |
|---|---|---|
| SEC-001, R15, R22 (routere uden auth) | Montering uden dependency | Router registrerer sig med deklareret policy; montering uden policy = byggefejl |
| SEC-016 (fabriks-TOTP) | Kendt default-secret | Ingen default credentials eksisterer i koden; fravær af secret = funktion deaktiveret; provisioning genererer per-device |
| GOV-01 (ratchet hævet stille) | Governance omgået stille | Ratchet-undtagelse kræver ceremoni (commit-nøgle + handover + tilbagebetalingsplan) |
| VPEN-012 (CORS dev-default) | Usikker default i prod | Fail-fast ved opstart i prod/staging uden eksplicit config |
| TIMELAPSE_ENV "rd" ukendt | Stille fallback | Ukendt miljø = strengeste regler |

## 3. Privacy / GDPR

- **Dataklassifikation i manifestet** (image/process/telemetry) driver retention, DPIA og karantæne pr. payload — arvet fra ADR-001, nu håndhævet i data-envelope-schemaet.
- Billeder = persondata-potentiale → eksisterende DPIA-skabelon + retention-policy arves; redaktion (redaction.py) bliver en payload-tjeneste med egen audit.
- Kryds-tenant: row-level customer_id-filter bevares; evidence-ingest stempler tenant ved modtagelse, så efterfølgende lækage kan spores.
- AI-tagging: billeder til Gemini = underdatabehandler — eksplicit DPA-krav; lokale Ollama-alternativer bevares for følsomme kunder (suverænitet, For whom).

## 4. Safety (OT-perspektiv)

For vandværk/energi/maritim gælder omvendte prioriteringer af timelapse: **integritet og tilgængelighed > fortrolighed**, og en forkert aktuator-kommando er en fysisk hændelse. Derfor:
- Payloads med aktuator-capabilities kræver *forhøjet manifest-review* (menneske-godkendt allowlist-ændring) og kommandoer med dobbelt-bekræftelse i control plane.
- Kernel kan *aldrig* selv initiere payload-kommandoer ud over allowlisten — heller ikke efter headend-kompromittering (allowlisten er signeret lokal policy).
- IEC 62443: zone/conduit-register med SL-T pr. zone oprettes når første OT-payload designes (dokumentarbejde oven på eksisterende mekanik — ikke ny kode).

## 5. Compliance-mapping

| Regime | Implikation for Mission Platform | Status |
|---|---|---|
| **CRA** | Secure-by-design (fail-closed invarianter), ingen default credentials (Annex I), signerede pakker, SBOM pr. modul, sårbarhedsproces pr. payload | Arkitektur understøtter; SEC-016-klassen lukket strukturelt |
| **NIS2** | Segmentering (kernel/payload/zoner), adgangsstyring (JIT), incident-proces (SEC-013/14 arvet) | Understøttet |
| **IEC 62443** | SR 2.1 least privilege via manifest; zone/conduit; SL-T ved OT | Delvist — zone-register udestår til Fase 4 |
| **ISO 27001** | GRC-register (PostgreSQL, arvet) som autoritativ status; A.8.25–28 adresseret af ratchet + modulopdeling | Understøttet |
| **GDPR** | DPIA pr. dataklasse; retention i manifest; art. 32 via ovenstående | Understøttet; DPA for Gemini åben i baseline (R12) |
| **AI Act** | Timelapse-tagging = lav-risiko; transparens + menneskelig kontrol dokumenteret i 08 | Ikke høj-risiko vurderet; genbesøges ved nye AI-payloads |

## 6. Kryptografi-roadmap

HS256 (delt secret) → Ed25519/EdDSA overalt der hviler på "server og klient deler en hemmelighed". JWT asymmetrisk var allerede åbent punkt i SABSA v10 §5 — ADR-K003 gør det til beslutning med migration-vej (dual-verify-vindue, revocation-liste, nøglerotation via config-pull).
