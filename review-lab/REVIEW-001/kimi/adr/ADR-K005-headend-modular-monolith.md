# ADR-K005 — Headend: modulær monolit på portabel container-pakke

- **Status:** Foreslået (Kimi, REVIEW-001) · **Dato:** 2026-07-29
- **Udfordrer:** To ting — (a) enhver microservices-fristelse (afvist også i ADR-001: for tidligt), (b) den stille antagelse at prod-headend *er* en Mac Mini med LaunchDaemons.

## Kontekst

**Why (a):** main.py = 18.549 linjer / 525 funktioner / 235 routes (målt 2026-07-17). Gælden er stabiliseret af ratchets, ikke reduceret. Hvad er den mindste strukturændring med størst effekt?

**Because (a):** QA-review 2026-07-17: auth/RBAC-udtræk først, fordi (i) sikkerhedskritisk, (ii) cirkulær-import-mønsteret cementeres ellers, (iii) hvert nyt modul forværrer det. Jeg tilslutter mig fuldt — og gør udtrækket til platform-sporets første bevis på "platform eller payload?"-testen pr. modul.

**Why (b):** Hvorfor røre ved noget der kører?

**Because (b):** Prod er én fysisk Mac Mini: DR er en gen-installation fra dokumentation (R09 er allerede blocker), staging-promotion er manuel, open-source-visionen forudsætter at andre kan køre headenden, og CrushFTP-sameksistensen gør maskinen delt med en anden tjeneste. Reproducibility er en sikkerheds- og forretningsegenskab, ikke bekvemmelighed.

**For whom:** Driftsejeren (DR, rollback); fremtidige selv-hostende kunder (suverænitet — et vandværk vil have alt on-prem); bidragydere (ens miljøer); Meta Review (reproducerbar evidens).

## Beslutning

1. **Arkitektur:** modulær monolit — én FastAPI-app, én database, men `platform/`- og `payloads/`-pakker med router/service/models, monteret med deklarerede policies (ADR-K002). Første udtræk: **auth/RBAC**. Ingen netværksgrænser internt; udtræk til separat service kræver ny ADR + målt behov.
2. **Drift:** headend pakkes som **container-compose** (app, PostgreSQL, nginx, storage-mounts) — `deployments/timelapse-reference/`. macOS-værten kan køre pakken i overgang; målet er at pakken er værten, ikke omvendt.
3. **Migration:** strangler — ny router-pakke ad gangen bag uændrede URL'er, kontrakttest mod eksisterende adfærd før flytning, ratchet-baseline sænkes efter hvert udtræk (gældsbudget: enhver session efterlader main.py mindre).

## Alternativer overvejet

- **Microservices nu:** Afvist (med ADR-001) — distribueret tracing, transaktioner og deployment-kompleksitet uden krav. Genbesøges hvis telemetry/ingest måles som flaskehals.
- **Bliv på macOS/LaunchDaemons:** Afvist som *målbillede*, bevaret som *migrationstrin* — produktion røres ikke før container-pakken har bestået restore-test og 30 dages staging-drift.
- **Kubernetes:** Afvist — ét værts-site pr. kunde; compose er tilstrækkeligt og auditerbart af den eksisterende kompetence.

## Konsekvenser

+ DR fra timer til minutter; staging = prod-billedet; open-source-vejen åbnet; modul-udtræk får et fysisk landingsted.
− En ny artefakt at vedligeholde (compose + images); macOS-specifikke stier (fx `/Volumes/data-fast`) skal parameteriseres — kendt fælde fra teknisk-gæld-analysen (hardcoded paths).

## Reversibel valideringsvej

Container-pakken kører først i `rd`, derefter staging parallelt med nuværende drift. Cutover = DNS/nginx-skift; rollback = skift tilbage. Pakken kan forlades på ethvert trin uden datatab (PostgreSQL-data på volume, uforandret af eksperimentet).
