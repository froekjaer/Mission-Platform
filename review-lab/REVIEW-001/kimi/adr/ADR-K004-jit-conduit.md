# ADR-K004 — Remote access som platform-conduit (JIT bygget, ikke kun designet)

- **Status:** Foreslået (Kimi, REVIEW-001) · **Dato:** 2026-07-29
- **Udfordrer:** Intet eksisterende design — Support Access Model (2026-07-05/06) er veldesignet men **ikke bygget** (jf. SABSA v10 §3: "designet men ikke bygget"). Min udfordring er prioriteringen: conduiten hører til kernel-platformen, ikke til en senere feature-sprint.

## Kontekst

**Why:** Den dag den første OT-payload (vandværk) onboardes, er fjernadgang til bagvedliggende styresystemer det farligste der findes i platformen — og det skal være bygget, testet og auditeret *før* behovet opstår, fordi behovet vil opstå som en haste-sag.

**Because (evidens):** R19 + miljø-governance hviler i dag "på menneskelig disciplin, ikke en teknisk kontrol" (SABSA v10 §3 — ordret). ADR-001 amendment 5 gør JIT/conduit-kontrol normativ. Det eneste der mangler er at bygge det ét sted, én gang, for alle payloads.

**For whom:** Kunden der skal godkende adgang til sin byggeplads/sit vandværk; teknikeren der skal have adgang der virker; regulator der skal se session-evidens; OT-operatøren for hvem en åben port er en fysisk sikkerhedsrisiko.

## Beslutning

1. Al support- og leverandøradgang går gennem én platform-tjeneste: **Conduit Broker** i headend + kernel-enforced destinations-allowlist på edge.
2. Flow: signet AccessTicket (scope, varighed, destinationer, kundegodkendelses-reference) → kernel verificerer signatur + allowlist → session åbnes (edge-initieret, som alt andet) → recording → automatisk lukning ved udløb eller kill switch.
3. Ingen indgående porte på edge eller OT-net nogensinde — arvet og ufravigeligt.
4. Break-glass: separat Support-CA, dobbelt-godkendelse, højeste SIEM-alarm.

## Konsekvenser

+ R19 løftes fra disciplin til kontrol; OT-verticals får deres vigtigste forudsætning gratis.
− En komponent mere i kernel-safety-case; recording-storage skal designes med retention (GDPR: session-optagelser kan indeholde persondata).

## Reversibel valideringsvej

Bygges først i `rd` mod LAB-edge med syntetisk destination (loopback-tjeneste); bestået test = ticket flow + recording + kill switch dokumenteret; derefter staging; eksisterende reverse-SSH-forvaltning (customer approval) forbliver aktiv som fallback indtil cutover verificeret.
