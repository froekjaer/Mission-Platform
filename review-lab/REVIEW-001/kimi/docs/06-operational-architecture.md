# 06 — Operationel arkitektur (SABSA operationelt lag)

## 1. Daglig drift (Hvornår/Hvordan)

| Proces | Design | Arv/ændring |
|---|---|---|
| Capture-cyklus | Scheduler i payload → `capture.now` → artifact → ingest → upload ved åbent slot | Arvet, nu bag kontrakt |
| Heartbeat | Pr. capture + periodisk diagnostics (CPU temp, disk, batteri, connectivity) | Arvet |
| Config-pull | ≤5 min interval, signeret hierarki, cache offline | Arvet |
| Nightly reboot 02:00 | Bevares som policy — men **mål:** overflødiggøres af kernel-restart af payload | Arvet m. exit-kriterium |
| Backup | Pull-baseret: edge pusher til headend (ingen indgående forbindelser); **R09-læring:** default skal producere en fungerende backup, ellers fail-loud i GRC | Skærpet |
| Restore-test | Kvartalsvis dokumenteret RTO/RPO som go/no-go-gate (E-02) | Arvet uændret — stadig blocker |

## 2. Update & release

- OTA: signerede artifacts, A/B-rollback, change tickets, per-target status (arvet Update_Flow_v10; per-target status var åbent punkt i v10 §5 — løftes til krav).
- **Payload-releases er uafhængige af kernel-releases** (SemVer på kontrakt = kompatibilitetsmatrix, ikke lockstep).
- Governance-gates K1–K6 arves **som byggefejl**, med tilføjelse: **ratchet-loft må kun sænkes; hævning kræver `RATCHET-EXCEPTION` i commit + handover + tilbagebetalingsplan.** (GOV-01: loftet blev hævet 18483→18549 stille — den første test af K1–K6 fejlede. En ratchet der kan hæves stille er dekorativ.)

## 3. Incident & support

- JIT/AccessTicket: kundegodkendelse, tidsbegrænset, separat Support-CA, signeret ticket, session recording, kill switch, revocation (arvet Support Access Model-designet — i Mission Platform bygges det **som platform-tjeneste**, ikke som dokument).
- Break-glass: eksplicit, logget, tidsbegrænset; miljø default-deny med kontrolleret undtagelse.
- Incident-proces: SEC-013/SEC-014-procedurerne arves; SIEM er platformens fælles hændelsesrygrad.

## 4. Observability

- SIEM/CMDB/ITIM bevares som platform-tjenester (domæneneutrale — ville se ens ud for et vandværk).
- **Gældsmetrikker i SYSTEM_HEALTH_REGISTER** (arvet fra Claude 07-17 §3.4): main.py-linjer, store funktioner, ruff/ESLint-totaler, testtal — én tabel pr. handover.
- Kernel-health er **uafhængig af payload-health**: kernel kan rapportere "payload nede" selv når payloaden ikke kan rapportere noget som helst. Det er hele pointen med proces-grænsen.

## 5. Go/no-go (Internet-eksponering)

Arver GO_LIVE_CHECKLIST v10 uændret, plus fire platform-specifikke gates:

1. Kernel/payload-isolation verificeret af uafhængig review + runtime-bevis (som denne PoC, men på hardware).
2. Route-auth-sweep + manifest-fail-closed-test grønne i CI (byggefejl, ikke rapporter).
3. Restore-evidens fra container-pakken (R09 lukkes på den nye platform, ikke kun på Mac Mini).
4. SEC-016-mønster scan: ingen kendte default-credentials nogen steder (automatiseret søg efter kendte demo-secrets).

## 6. Kapacitet & vækst

500–1000 edges / 100+ sites: flaskehalsen er headend-ingest og SIEM, ikke edge. Content-addressed storage + tenant-partitionering skalerer horisontalt; headend-modulopdelingen gør at telemetry/ingest kan skilles ud som første separat-skalerbare enhed **hvis** målinger kræver det (ikke før).
