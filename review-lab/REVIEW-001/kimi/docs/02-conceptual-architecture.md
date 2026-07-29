# 02 — Konceptuel arkitektur (SABSA konceptuelt lag)

## 1. Koncepter (What)

Fem begreber bærer hele platformen. Alt andet er mekanik.

| Begreb | Definition | Bærende princip |
|---|---|---|
| **Platform Kernel** | Den minimale, auditerbare non-funktionelle kerne: identitet, policy-enforcement, supervision, evidens. Ingen domæneviden. | Jo mindre kernel, jo verificerbar |
| **Payload** | En signeret pakke med funktionel domænelogik, kørt som separat OS-proces under manifest + quota. Timelapse er payload #1. | Substitution uden kernel-ændring |
| **Contract** | Versionerede wire-kontrakter (JSON Schema, SemVer): **control plane** (livscyklus/kommando/health) og **data plane** (artifacts + integritet). To kontrakter, to SemVer. | Kontrakten er den dyre at ændre — derfor først, og derfor lille |
| **Capability Manifest** | Payloadens *deklaration* af behov. Platformens *policy* er autoritativ enforcement. Ukendt = afvist = logget. | Fail-closed, least privilege |
| **Evidence Chain** | SHA-256 pre-processing sidecar → verifikation ved ingest → append-only audit → GRC. Fra linse til arkiv uden tillids-brud. | Reality before models: intet claim uden evidens |

## 2. Tillidsmodel (konceptuelt)

```
            ┌──────────────────────── Trust root (Mission Owner CA) ─┐
            │ signerer: platform policy · manifests · artifacts · JIT-tickets
            ▼
   ┌─────────────────┐   control plane (allowlist)   ┌──────────────┐
   │  PLATFORM KERNEL│ ◄────────────────────────────►│   PAYLOAD    │
   │  (trusted, lille)│ ──── data plane (verify) ───► │ (untrusted,  │
   │  enforcement     │                               │  isoleret)   │
   └─────────────────┘                               └──────────────┘
            ▲  edge initierer ALT; ingen indgående porte
            │  mTLS/JIT conduit (support: kundegodkendt, tidsbegrænset, optaget)
     ┌──────┴───────┐
     │   HEADEND     │  modulær monolit: auth · config · update · telemetri · GRC
     └──────────────┘
```

**Edge er untrusted by default** (arvet fra baselinen — korrekt). **Payload er untrusted også af platformen** — det nye, men nødvendige skridt for OT-verticals (IEC 62443 zone/conduit).

## 3. Policy-koncepter (arvet, generaliseret)

- **Zero trust, defense-in-depth:** uændret.
- **Autonomi ved netværksudfald:** uændret — kernel + payload kan køre uden headend i ≥7 dage.
- **Fail-closed som platform-invariant:** opgraderet fra praksis til princip (ADR-K002). Gælder manifest, kommandoer, data-ingest, miljøflag, credentials.
- **Additivitet / aldrig hard-delete:** uændret — karantæne og reversible flyt.
- **AI som evidens eller forslag, aldrig autoritet:** uændret fra Mission Framework; formelt ejerskab i AI-allokeringsmodellen (08).

## 4. Hvad der bevidst IKKE er et koncept

- **Microservices.** Afvist konceptuelt: distribueret kompleksitet uden krav. Se ADR-K005.
- **Event bus / message broker som rygrad.** Payloads taler med kernel gennem to små kontrakter; en broker ville flytte enforcement væk fra kernen og gøre audit diffus. Kan tilføjes senere som *transport*, aldrig som *autoritet*.
- **Generel plugin-mekanisme (dynamisk import).** Afvist i ADR-001 — jeg tilslutter mig og skærper: der findes ingen in-process plugin-vej overhovedet.

## 5. Afgrænsningstest (arvet ordret fra ADR-001 — den er rigtig)

> Et modul der ville se identisk ud for et vandværk som for et kamera er **platform**; ellers **payload**.

Tilføjelse (min): *Et modul der skal stoles på for at andre moduler kan mistænkes, er **kernel**.* Det er en snævrere test end ADR-001's — og den er grunden til at kernel i PoC'en er ~250 linjer stdlib-Python og skal forblive lille.
