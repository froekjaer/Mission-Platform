# ADR-K002 — Fail-closed som platform-invariant

- **Status:** Foreslået (Kimi, REVIEW-001) · **Dato:** 2026-07-29
- **Udfordrer:** Ikke en specifik ADR — udfordrer det *reaktive* mønster (punktrettelse + sweep) med et *strukturelt* princip.

## Kontekst

**Why:** Hvorfor bliver samme fejlklasse ved med at vende tilbage?

**Because (evidens fra baselinen):**
- SEC-001 (redaction uden auth), R15 (SIEM), R22 (AI-vocab, 22 endpoints uden auth) — samme klasse tre gange. K1-sweepet stopper *routere*, men ikke *mønsteret*.
- SEC-016: fabriksdefault-TOTP `JBSWY3DPEHPK3PXP` (pyotp's demo-secret!) som fallback — CRA Annex I-forbudt.
- VPEN-2026-012: CORS falder tilbage til dev-origin. `TIMELAPSE_ENV="rd"` kendes ikke af de tre kodesteder der læser det (stille fallback).
- GOV-01: ratchet-loft hævet 18483→18549 uden ceremoni — governance der kan omgås stille, omgås.

Mønsteret er ét: **fravær af eksplicit beslutning resolver til den åbne/tilladende stille tilstand.**

**For whom:** Kunderne (hvis billeder og adgang er på spil), CE-mærkningen (CRA), og enhver fremtidig contributor — inklusive AI-agenter — der skal kunne ændre kode uden at kunne åbne et hul ved at glemme noget.

## Beslutning

1. **Default-deny overalt hvor platformen resolver adgang eller kapabilitet:** manifest-capabilities, kommando-allowlist, router-policies, miljøflag, credentials, CORS, conduit-destinationer. Ukendt/ugyldigt/fraværende = afvist + logget. Aldrig fallback til åben tilstand; fravær af credential = funktion *deaktiveret* (SEC-016-læringen).
2. **Montering uden deklareret policy er en byggefejl** — for routere (arver K1 som compile-time princip) og for payloads (manifest-validering før exec).
3. **Ratchet-undtagelser kræver ceremoni:** `RATCHET-EXCEPTION`-nøgle i commit + handover-entry + tilbagebetalingsplan. CI nægter loft-hævning i samme commit som linjevækst uden nøglen (arver GOV-01-anbefalingen, gør den håndhævet).

## Konsekvenser

+ Fejlklassen lukkes strukturelt: en glemt dependency/manifest/config fejler *højt og lukket*, ikke stille og åbent.
− Flere byggefejl at forholde sig til; risiko for "exception-fatigue" — mitigeres af at allowlist-ændringer er én signeret fil med menneske-review.

## Reversibel valideringsvej

Princippet er allerede delvist bevist: kernel-PoC afviser tampered manifest, ukendt capability, ukendt kommando og korrupt artifact (runtime-evidens). Hvis byggefejl-gaten viser sig for støjende i praksis, nedgraderes den enkelte gate til rapport — men afvisningsadfærden i runtime forbliver.
