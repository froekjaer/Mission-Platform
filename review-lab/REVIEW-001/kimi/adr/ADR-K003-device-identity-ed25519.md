# ADR-K003 — Per-device Ed25519-identitet; væk fra delte secrets

- **Status:** Foreslået (Kimi, REVIEW-001) · **Dato:** 2026-07-29
- **Udfordrer:** Fortsat HS256 (symmetrisk JWT-secret) som langtidsholdbar model; relaterer til åbent punkt i SABSA v10 §5 ("JWT asymmetrisk RS256/EdDSA vs. nuværende HS256") og SEC-016.

## Kontekst

**Why:** En platform med 500–1000 enheder og multi-vendor-fremtid kan ikke bygge sin tillid på at "server og enhed deler samme hemmelighed" — hvert delt secret er én exfiltration fra total kompromittering, og rotation på tværs af ubemandede enheder er operationelt fragilt.

**Because (evidens):** Baselinen kender allerede problemet (SABSA v10 §5 åbne punkter: intern CA/mTLS, JWT asymmetrisk). SEC-016 viser hvad der sker når symmetriske defaults bruges som fallback. mTLS-designet (2026-07-05) er allerede på tegnebrættet — denne ADR gør det til beslutning med en konkret migrationsvej.

**For whom:** Driftsejeren (revocation og rotation uden feltbesøg); kunder (en stjålet enhed kompromitterer ikke andres); fremtidige leverandører (delegated signing med scope — ingen arver platformens nøgler).

## Beslutning

1. Hver enhed provisioneres med et **unikt Ed25519-nøglepar** ved enrollment; public key registreres i CMDB. Fravær af nøgle = enhed kan ikke deltage (fail-closed, ADR-K002) — der findes ingen fabriksnøgle.
2. Signering af manifests, artifacts, config og JIT-tickets: Ed25519 med Trust root hos Mission Owner (intern CA-design arves). Device-attestation over mTLS.
3. JWT migreres HS256 → EdDSA med **dual-verify-vindue**: headend accepterer begge algoritmer i én release, logger HS256-brug, slår HS256 fra per tenant efter migration, globalt efter sidste enhed er roteret.
4. Rotation via eksisterende config-pull; revocation-liste distribueres som signeret config; stale-credential-runbook (arvet: TL-DCA63234D813-sagen) bliver automatiseret procedure.

## Alternativer overvejet

- **Bliv ved HS256 + stram rotation:** Afvist — løser ikke exfiltration-risikoen, og rotationsoperationen er netop den der historisk fejler (stale credentials findes allerede i baselinen).
- **TPM/secure element på edge:** Rigtig retning for OT-zoner (SL-T 3+), men ikke tilgængelig på nuværende hardware; nøgle i FDE-krypteret lager er mellemløsningen (edge disk-kryptering var også åbent punkt i v10 §5).

## Konsekvenser

+ Revocation bliver ægte; supply-chain forberedes; SEC-016-klassen kan ikke genopstå (ingen default findes).
− Nøglehåndtering er den sværeste operationelle disciplin — kræver at enrollment-flowet (allerede designet i AGGREGATED_REQUIREMENTS_UPDATE_PROVISIONING) gennemføres.

## Reversibel valideringsvej

Dual-verify-vinduet *er* den reversible vej: hvis EdDSA-rollout fejler, forbliver HS256 aktiv for berørte enheder mens det undersøges. Ingen big-bang.
