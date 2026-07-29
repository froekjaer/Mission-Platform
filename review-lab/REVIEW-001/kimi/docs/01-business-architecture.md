# 01 — Forretnings- og interessentarkitektur (SABSA kontekstuelt lag)

## 1. Mission (Why)

> **Skab pålidelig, autentificeret dokumentation og kontrol fra ubemandede lokationer — og gør den tilgængelig for dem, der har brug for den, proportionalt med behov, konsekvens, omkostning og suverænitet.**

Timelapse er den første funktionelle payload, ikke platformens grænse (jf. REVIEW-001-invitationen). Mission Frameworks kernespørgsmål gælder uændret: *hvordan skaber vi berettiget, evidensbaseret forandring i virkeligheden?*

## 2. Interessenter og deres reelle behov (For whom)

| Interessent | Behov | Konsekvens ved svigt | Leveranceproportion |
|---|---|---|---|
| **Byggeplads-kunde (dataejer)** | Ubestridelig billeddokumentation for fremdrift/tvister | Juridisk bevis tabt; GDPR-brud | Fuld dataintegritet (SHA-256), egen tenant, eksport + sletning |
| **Site manager** | Overblik over egen site, ingen andres | Fejlbeslutninger | Site-scopet view, ingen platform-privilegier |
| **Servicetekniker** | Lokal adgang til edge ved service | Kan ikke udføre job; sikkerhedshul | Tidsbegrænset, kundegodkendt, logget adgang (JIT) |
| **Peter / driftsejer (Mission Owner)** | Driftbar, CE-mærkningsbar, open-source-bar platform | Forretningen eksisterer ikke | GRC-overblik, go/no-go-gates, reversibilitet |
| **Fremtidig OT-operatør (vandværk, energi)** | Samme hærdede kerne, anden payload, IEC 62443 | Sikkerhedsulykke, ikke kun datatab | Platform uden timelapse-afhængighed |
| **Regulator / revisor (CRA, NIS2, GDPR)** | Sporbar compliance-evidens | Markedsadgang tabt | Maskinelt læsbar evidens-spor |
| **Leverandør (fremtidig)** | Signerede payloads/updates uden at arve kundens rettigheder | Supply-chain-kompromittering | Scoped signeringsret + JIT-support |

## 3. Business attributes (SABSA F1) — arvet, skærpet, målbare

Baselinens attributter (SABSA_Architecture_v10 §2) tages uændret som udgangspunkt, men får målbare succeskriterier og to nye attributter, som platform-ambitionen kræver:

| Attribut | Prioritet | Målbart succeskriterium | Arv/ændring |
|---|---|---|---|
| Availability (capture) | KRITISK | >99% af planlagte captures pr. node pr. måned, målt i CMDB | Arvet |
| Integrity | KRITISK | 100% af arkiverede artifacts verificerer mod SHA-256 ved ingest; 0 uverificerede accepteres | Arvet + skærpet til invariant i data plane |
| Synchronicity | KRITISK | ≤1 s afvigelse mellem kameraer på samme site (NTP/chrony) | Arvet |
| Confidentiality / tenant-isolation | HØJ | 0 kryds-tenant-læsninger i route-auth-sweep + penetrationstest | Arvet |
| Accountability | HØJ | Enhver muterende handling har aktør, tid, ticket-reference i append-only audit | Arvet + skærpet (audit er platform-tjeneste, ikke feature) |
| Continuity | HØJ | Boot-to-capture <120 s; state overlever strømsvigt (WAL) | Arvet |
| Resilience | HØJ | 50 GB store-and-forward; autonom drift ≥7 dage uden netværk | Arvet |
| **Substitutability** (ny) | HØJ | En ny payload (vandværk-stub) kan indlæses **uden ændring i platform-koden**; bevises i Fase 4-test | Ny — selve platform-tesen |
| **Enforceability** (ny) | KRITISK | 100% af payload-privilegier afvises fail-closed, hvis ikke på signeret allowlist; målt af vertical-slice-tests | Ny — læringen fra SEC-001/R15/R22 |
| Manageability | MIDDEL | Remote konfiguration uden fysisk adgang; rollback ≤1 change-ticket | Arvet |
| Scalability | MIDDEL | Design-loft: 500–1000 edges, 100+ sites uden arkitekturændring | Arvet |
| Performance | LAV | 1 billede/dag → 1/minut konfigurerbart | Arvet |

## 4. Nødvendig værdi vs. optional sophistication

**Nødvendig værdi (MVP for platform):** identitet/enrollment, config-hierarki, OTA, telemetri, remote access (JIT), HAL, storage/evidens, RBAC — alt sammen allerede bevist i baselinen. Payload: capture→QA→upload→tagging→UI.

**Optional sophistication der udskydes bevidst:** NPU-accelereret edge-AI, site-look matching, WebRTC live view, multi-vendor trust-økosystem, federation. Alle arkitektonisk plads til — ingen frosset i dag. Begrundelse: REVIEW-001 kræver kun timelapse funktionel; over-generaliseringsrisikoen er baselinens veldokumenterede fælde (R26: gælden voksede under feature-pres).

## 5. Mission Loop-mapping (semantisk skelet)

Platform-tjenesterne er Mission Loop'ens bogstavelige implementering:

- **Observation → Evidence:** data plane (content-addressed artifact + SHA-256 sidecar + provenance).
- **Claim → Knowledge:** QA-flag, AI-tags, GRC-status — altid med provenance og udfordringsproces.
- **Decision → Action:** control plane (allowlistede kommandoer, change tickets, JIT-adgang).
- **Outcome → Learning:** SIEM/ITIM/CMDB, restore-tests, meta-reviews.

Konsekvens: en *claim* i platformen uden evidens-reference er en arkitekturfejl, ikke en manglende feature.
