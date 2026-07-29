# 11 — Test-, evidens- og acceptplan

## 1. Hvad der er bevist NU (runtime-evidens)

`evidence/poc-test-run-2026-07-29.txt` — 9/9 checks, Python 3.12, Linux:

| Invariant | Test |
|---|---|
| Fail-closed manifest (signatur) | tampered manifest rejected |
| Fail-closed capabilities | unknown capability rejected |
| Proces-isolation | payload runs as separate OS process |
| Control plane fail-closed | non-allowlisted command rejected |
| Evidens-integritet | artifact accepted with verified SHA-256 |
| Telemetri | telemetry via control plane |
| Data plane fail-closed | corrupted artifact rejected |
| Kill switch | payload process group terminated |
| Accountability | all decisions logged |

Reproduktion: `python3 tests/test_vertical_slice.py` (stdlib only, ingen netværk, ingen hardware).

## 2. Testpyramide (målbillede)

| Niveau | Indhold | Gate |
|---|---|---|
| Kontrakttests | Schema-validering; compatibility-matrix; golden messages | Byggefejl |
| Unit | Kernel-policy, ingester, driver-adapters | Byggefejl |
| Coupling | waterworks-stub uden platform-ændring; ingen import fra timelapse-payload | Byggefejl |
| Vertical slice | Denne PoC, udvidet til rigtig edge | Release-gate |
| Integration | Headend mod PostgreSQL (arvet suite; split unit/live jf. VPEN-2026-013) | Release-gate |
| Runtime-evidens | Restore-test, capture>99%, hash-kæde-audit | Go/no-go-gate |

## 3. Acceptkriterier for REVIEW-001-afleveringen (selvpålagte, alle opfyldt)

1. ✅ Alle obligatoriske outputs fra invitationen findes.
2. ✅ Materielle beslutninger har ADR med Why/Because/For whom + reversibel valideringsvej.
3. ✅ Source-to-target traceability (reused/adapted/rewritten/rejected).
4. ✅ Eksekverbare claims har runtime-evidens.
5. ✅ Risici, antagelser, uafklarethed eksplicitte.
6. ✅ Timelapse-payload funktionelt demonstreret som vertikal slice (syntetisk kamera — begrænset, ærligt deklareret).

## 4. Acceptkriterier for platformen (fremad — før produktion)

1. Hardware-spike: PoC + gphoto2 på TL-C87FF9587CA0, LAB-mode, med målt RAM/CPU-overhead <10% af node-budget.
2. Første modul-udtræk (auth/RBAC) med uændrede URL'er og sænket ratchet-baseline.
3. Restore-evidens på container-deployment (R09 lukket).
4. Uafhængig (ikke-Kimi) gennemgang af kernel.py linje for linje — kernel skal kunne auditeres af ét menneske på én eftermiddag. Det er et designkrav, ikke et ønske.
