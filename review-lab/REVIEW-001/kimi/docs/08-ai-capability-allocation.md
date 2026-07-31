# 08 — AI- og kapabilitetsallokeringsmodel

## 1. Grundregel (arvet fra Codex' AI-domænesnit — den er rigtig, og jeg formaliserer den)

> Provider-adaptere (Ollama, Gemini, fremtidige) er **fælles teknisk infrastruktur**. Prompt, dataklassifikation, adgang, retention og **resultatejerskab** ligger altid i det **kaldende domæne**.

## 2. Allokeringstabel

| AI-anvendelse | Domæne | Ejerskab af prompt/data/resultat | Validering | Model-præference |
|---|---|---|---|---|
| Billedtagging (captures) | Timelapse-payload | Kundens data; tags ejes af kunden; retention følger image-klassen | Menneskelig review-kø for ukendte tags (eksisterende vocabulary-flow bevares) | Gemini 2.5 Flash (Vertex EU) + Batch; Ollama-fallback for suverænitet |
| Edge QA / eksponering | Timelapse-payload | Edge-lokal; kun metrikker forlader enheden | Blur/brightness-tærskler, LAB-verificeret | CPU/NPU lokal — **aldrig cloud for realtid** |
| Site-look matching | Timelapse-payload | Site-scopet | F-012-testpakke (arvet) | Lokal |
| SIEM-anomalier, CMDB-intel | Platform | Driftsejer | Først shadow-mode, så assist — aldrig auto-handling | Ollama lokal |
| Compliance/regulatorisk scanning | Platform (GRC) | Driftsejer; kildehenvisning påkrævet | Hvert fund kræver menneske-disposition | EU-hosted LLM |
| Kodegenerering (udvikling) | Proces | Reviewer-session; AI-output er forslag, menneske/agent med ansvar committer | CI-gates + review | Uafhængig af leverandør |

## 3. Governance pr. AI-brug (påkrævede felter — implementeres som GRC-datasæt)

`formål · prompt-version · dataklasse · provider + region · DPA-reference · retention · resultatejerskab · menneskelig kontrol · omkostningsloft`

AI Act: timelapse-tagging vurderes lav-risiko; modellen kræver at enhver ny AI-payload udfylder datasættet **før** manifest godkendes — governance gennem den samme fail-closed mekanisme som capabilities.

## 4. Anti-mønster der afvises

- "AI-gateway" som eneste adgangspunkt med central prompt-ejerskab → bryder domæneejerskab; afvist.
- AI der muterer config eller dispatcher kommandoer autonomt → bryder "AI er forslag, ikke autoritet"; forbudt i kernel.
