# 12 — Collaborative intelligence: anbefalet arbejdsdeling + selvvurdering

## 1. Hvem bør gøre hvad (kompetence-baseret, ikke brand-baseret)

| Lag | Anbefalet bidrager | Styrker | Begrænsninger / valideringsbehov |
|---|---|---|---|
| Mission & forretningsarkitektur | **Menneske (Mission Owner) + LLM med lang kontekst** | Ejerskab af formål kan ikke delegeres; LLM til strukturering og konsistens-tjek | LLM gætter på forretningsprioriteter — altid verificér mod interessenter |
| Sikkerhed, safety & trust | **Claude-agenter (vist stærke i baseline: SABSA/IEC 62443-fund) + uafhængig menneskelig security reviewer** | Grundige trusselsmodeller, konkrete fund (SEC-016, GOV-01) | Kan blive verbose; fund skal prioriteres af menneske med konsekvens-forståelse |
| OT/ICS & edge engineering | **Menneske med felt-erfaring** (Peter + tekniker) assisteret af kode-stærk agent | Hardware-antagelser dræber papirarkitektur | AI kan ikke måle strømforbrug eller GPIO-timing — kræver bench |
| Data-arkitektur | **Kode-agent med repo-adgang (Codex-type)** | Præcis sporing af skema/flows | Skal holdes til evidens; ellers over-design |
| AI/model-orkestrering | **Specialist-LLM + eval-harness** | Prompt/modelvalg | Eval-metrics skal ejes af domænet, ikke af modellen selv |
| Implementation & refaktorering | **Kode-agent (Codex-type) med strenge gates** | Hurtig, disciplineret ved ratchet-gates | Tendens til at løse opgaven for bredt — scope-disciplin via change tickets |
| Test & verifikation | **Uafhængig agent end implementøren** (roterende) + menneskelig accepttest | Modvirker self-grading | Fælles blind spot hvis samme model-familie implementerer OG tester |
| DevSecOps/lifecycle | **Kode-agent + menneske on-call** | CI/CD, IaC | Prod-adgang altid bag menneske-godkendelse |
| UX & tilgængelighed | **Menneske designer + frontend-agent** | Kundens sprog (dansk), WCAG | AI-UI har tendens til generisk design |
| Regulatorisk/kontrakt | **Menneskelig jurist/DPO, LLM som research-assistent** | DPA, CRA-tolkning | Lovtolkning er aldrig delegeret til AI |
| Drift & incident response | **Menneske (ansvarlig) + agent som runbook-executor** | 24/7-detektion kan automatiseres | Eskalation og break-glass = menneske |
| Endelig beslutningsmyndighed | **Peter Frøkjær (Mission Owner)** — ikke forhandlbar | — | — |

## 2. Kimi — ærlig selvvurdering

**Stærkest i denne aflevering:**
- Strukturel syntese: at samle SABSA, Mission Framework og baselinens ADR-spor til ét sammenhængende skelet uden at kopiere det.
- At omsætte principper til eksekverbar kode hurtigt (PoC med runtime-evidens på én session).
- At spotte fejlklasser på tværs af dokumenter (SEC-001/R15/R22/SEC-016/GOV-01 som ét mønster: defaults der fejler åbent + governance der kan omgås stille).

**Svagest:**
- Ingen hardware-empiri: GPIO-timing, 4G-modem-opførsel, NPU-begrænsninger, gphoto2-quirks er kun læst, ikke målt. Mine OT-påstande er arkitektoniske, ikke erfaringsbaserede.
- Begrænset kendskab til dansk byggebranche-praksis og det faktiske kundegrundlag — forretningsantagelser bør valideres af Peter.
- Jeg har ikke læst *al* kildekode (main.py er 783 KB); min traceability bygger på dokumentation + stikprøver. Der kan være adfærd i monolitten som kun koden kender — derfor er min migrationsstrategi bygget på kontrakttest-mod-eksisterende-adfærd først.
- Risiko for over-symmetri: jeg foretrækker rene grænser; virkeligheden (fx SFTP som både control og data) er rodet, og mine diagrammer kan underdrive arvet rod.

**Bias-disclosure:** Jeg er LLM-baseret som flere andre reviewers; vi deler sandsynligvis blinde vinkler omkring hvad der er "let" i drift. Jeg har ingen tidligere eksponering for dette projekt før denne session.
