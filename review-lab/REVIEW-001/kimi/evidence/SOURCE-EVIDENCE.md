# Source Evidence — læst og anvendt evidens fra frozen baseline

Baseline: `froekjaer/timelapse-pro` @ `eed9e3c8c67369e1924c25a11908616220c3c753` (uændret — verificeret: ingen skrivning foretaget; repoet er kun læst via API).

| Dokument/kilde | Anvendt til |
|---|---|
| `README.md` | Systemoverblik, struktur, test-kommandoer |
| `Dokumentation/00_START_HER.md` | Session-boot, ADR-binding (ADR-001), topologi, GRC-princip |
| `Dokumentation/SABSA_Architecture_v10.md` | Business attributes, tillidsgrænser, miljø-lag, åbne punkter (JWT asymmetrisk, disk-kryptering) |
| `Dokumentation/ADR/ADR-001-platform-payload-split.md` | Accepteret platform/payload-ramme, Codex' 6 amendments, afgrænsninger (ADR-002, federation, multi-vendor) |
| `Dokumentation/Arkitektur/Modularisering_Platform_Payload_Plan.md` | Faseplan, repo-modeller, GitHub-mapping — min ADR-K001 udfordrer Fase 1 |
| `Dokumentation/TENKNISK_GÆLD_ANALYSE_headend_main_py_2026-07-06.md` | Gældskvantificering (16.692 linjer, 461 funktioner), hardcoded paths, modul-forslag |
| `Dokumentation/Claude_QA_Review_2026-07-17.md` | Nyeste retning: SEC-016, GOV-01, auth-udtræk først, gap-analyse, målinger 07-17 |
| `Dokumentation/RISK_ASSESSMENT_v11_ADDENDUM_2026-07-15.md` | R22–R27, VPEN-2026-010…013, K1–K6, go-live-blockere |
| `docs/edge-architecture.md` (v3.2.0) | Edge-komponenter, capture-cyklus, HAL, upload, sikkerhed, tekniker-flow |
| `ISSUES.md` (root, 2026-06-14) | Issue-taksonomi A–N (markeret forældet i baseline; brugt strukturelt, ikke som status) |
| Repo-struktur (headend/, edge/, timelapse-ui/, tests/, deploy/) | Komponentlandkort og traceability |
| `Dokumentation/` listeblad (registre, runbooks, SEC-001/002/013/014, Update_Flow_v10, MILJOE_ARKITEKTUR, Support Access Model, mTLS-design, GRC-relaterede) | Cross-verifikation af fund og afgrænsninger |

## Sekundær evidens (governance-repo)

`froekjaer/mission-framework`: README (Mission Loop, Engineering Continuity), `pilot-reviews/REVIEW-001/README.md` + `INVITATION.md`, `review-kit/*` (standarder), samt `review-lab/REVIEW-001/{README,BASELINE,SUBMISSION-CHECKLIST,kimi/WORKSPACE}.md` på min egen branch i `froekjaer/Mission-Platform`.

## Begrænsninger i evidensgrundlaget

- `main.py` (783 KB) og `edge/agent.py` (139 KB) er **ikke** læst fuldt ud; analyse bygger på dokumenterede målinger + stikprøver via repo-struktur. Dette er deklareret i selvvurderingen (12).
- HANDOVER_LOG (779 KB+arkiv) er ikke læst; dens fund er indfanget via 00_START_HER og QA-reviews der refererer den.
- Ingen live-systemer tilgået. Ingen tests fra baselinen eksekveret.
