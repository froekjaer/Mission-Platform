# REVIEW-001 — Kimi: Executive Summary

**Reviewer:** Kimi (Moonshot AI) · **Branch:** `review/review-001-kimi` · **Dato:** 2026-07-29
**Baseline:** `froekjaer/timelapse-pro` @ `eed9e3c8c67369e1924c25a11908616220c3c753` (frozen, read-only — uændret)

## Tese

> **Mission Platform skal ikke refaktoreres frem til modularitet — den skal fødes modulær i sin kontrakt, og arve sin funktionalitet.**

TimeLapse Pro har allerede taget den rigtige strategiske beslutning (ADR-001: platform/payload-snit, accepteret 2026-07-16). Min analyse bekræfter retningen — men viser at mellem beslutning og virkelighed står to ubesvarede spørgsmål, som ADR-001 eksplicit udskød: **kontraktens faktiske form** (ADR-002) og **håndhævelsesmekanismen** (amendment 1: "proces-isolation" uden mekanisme). Min aflevering besvarer begge med en eksekverbar model, ikke kun et dokument.

## Hvad jeg er enig i — og bygger videre på

- ADR-001's afgrænsningstest ("ville modulet se identisk ud for et vandværk?") er korrekt og skarp.
- Codex' seks amendments er nødvendige, ikke kosmetiske.
- Claude's prioritering (QA 2026-07-17): auth/RBAC-udtræk først; gæld er stabiliseret, ikke reduceret.
- Evidensmodellen (SHA-256 pre-XMP sidecar, store-and-forward, autonom edge) er bevist i drift og **skal genbruges**, ikke genopfindes.

## Hvor jeg udfordrer (dokumenteret i ADR'er)

1. **Kontrakt-first, ikke kode-first (ADR-K001).** Fase 1-spikket i planen wrapper eksisterende kameralogik bag et Python-interface *in-process*. Det cementerer netop den cirkulære binding til monolitten, som QA-reviewet 2026-07-17 §2.5 flager som det stærkeste argument for udtræk. Jeg foreslår i stedet **wire-kontrakter først** (versionerede JSON-schema control/data-plane), så payload er en separat proces fra fødslen — ikke en proces "når vi når det".
2. **Fail-closed som platform-invariant, ikke som feature (ADR-K002).** SEC-001, R15, R22 er samme fejlklasse tre gange. Punktrettelser og endda route-sweeps er reaktive. Jeg gør *default-deny* til en strukturel egenskab: manifest-validering, kommando-allowlist og data-ingest afviser alt ukendt. Bevist eksekverbart (9/9 checks, se `evidence/`).
3. **Tillidsmodellen skal løftes fra delte hemmeligheder til nøglepar (ADR-K003).** Baselinens HS256 (delt secret) og SEC-016 (fabriksdefault-TOTP) er samme mønster: symmetriske defaults der fejler *åbent*. Jeg foreslår Ed25519-enhedsidentitet med per-device provisionerede nøgler — og at fravær af nøgle betyder *deaktiveret*, aldrig *fabriksnøgle*.
4. **Headend: modulær monolit, ikke microservices — og ikke macOS-afhængig (ADR-K005).** Jeg afviser big-bang rewrite, men udfordrer at prod-headend er bundet til én Mac Mini med LaunchDaemons. Portabel, reproducerbar headend-pakke (Linux/containere) er en forudsætning for både DR, federation og open-source-visionen.
5. **SABSA + Mission Framework som ét semantisk skelet.** Business attributes mappes direkte til Mission Loop-begreberne (Need → Evidence → Claim → Decision → Outcome). Det gør platformen til en reference-implementering af frameworket, ikke bare et produkt med dokumentation ved siden af.

## Bevis, ikke kun argumentation

Afleveringen indeholder en **eksekverbar vertical slice** (stdlib-Python): en edge-kernel der kører timelapse-payloaden som separat proces med resource quota, fail-closed manifest-validering, allowlistet control plane og hash-verificeret data plane. **9/9 checks bestået** (`evidence/poc-test-run-2026-07-29.txt`). Syntetisk kamera — men ægte proces-isolation, ægte signaturverifikation, ægte hash-kæde.

## Hvad timelapse-payloaden bevarer

Alt der er bevist: capture-cyklus, kvalitets-QA, cirkulær buffer, store-and-forward, config-hierarki, OTA med signerede artifacts, AI-tagging. Intet funktionelt tab. Migration er strangler-mønster, additiv, reversibel — se `migration/`.

## Næste sikre skridt

Byg kontrakt-spiket mod den *rigtige* edge (TL-C87FF9587CA0) med LAB-kamera: erstat syntetisk frame med gphoto2-capture bag `capture.now`. Det er én uge, ikke en sprint — og det validerer kontrakten mod virkeligheden, før nogen rører monolitten.

## Ærlige begrænsninger

- Ingen hardware-adgang: PoC'ens kamera, GPIO, 4G-modem og NPU er simulerede. OT-krav for vandværk/maritime er arkitektonisk testet, ikke empirisk.
- Jeg har ikke kørt baselinens egen testsuite (kræver live Postgres + seedede brugere; ~20 testfiler er live-integrationstests ifølge RISK v11 VPEN-2026-013).
- Mit kendskab til produktionsdriften er dokumentarisk (HANDOVER_LOG, SYSTEM_HEALTH_REGISTER), ikke oplevet.
