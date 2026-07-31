# ADR-K006 — Målrepo: monorepo med kontrakt-CODEOWNERS (arver ADR-001 model A)

- **Status:** Foreslået (Kimi, REVIEW-001) · **Dato:** 2026-07-29
- **Udfordrer:** Intet — bekræfter ADR-001 §3 (model A) med én skærpelse.

## Kontekst & beslutning

Monorepo nu, migrerbart til pakke senere (model A→B) er allerede besluttet og korrekt. Jeg bekræfter det og tilføjer én skærpelse: **`contracts/` får sit eget CODEOWNERS-niveau** — ændringer kræver Mission Owner + platform-ejer + mindst én payload-ejer, fordi kontrakten er det eneste sted hvor en fejl rammer *alle* spor samtidig.

**Why:** Kontrakt-fejl er de dyreste; de skal være de sværeste at lave.
**Because:** SemVer-disciplin fejler stille uden mekanisk gate (GOV-01-læringen: regler uden enforcement er dekoration).
**For whom:** Alle fremtidige payload-teams, der skal kunne stole på at kontrakten ikke flytter sig under dem.

## Konsekvenser

+ Kontrakt-stabilitet bliver håndhævet, ikke tilstræbt.
− Tre-part review på kontrakt-ændringer; acceptabel fordi ændringsfrekvensen bør være lav (designmål: <4 pr. år efter frys).

## Reversibel valideringsvej

CODEOWNERS-reglen kan strammes/lempes uden kode-ændring.
