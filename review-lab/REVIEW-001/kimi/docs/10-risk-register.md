# 10 — Risikoregister og antagelser

## Risici (ejer · konsekvens · behandling)

| ID | Risiko | S/M | Ejer | Behandling |
|---|---|---|---|---|
| K-R01 | Kontrakt-design låses for tidligt forkert → dyr major-bump | M/H | Platform-ejer | Fase 1-spike mod rigtig hardware FØR frys; kun 3 små schemas; SemVer-disciplin |
| K-R02 | To-spors-udvikling uden CODEOWNERS/CI genskaber monolit-vækst | M/M | DevSecOps | Opsætning i uge 1 (timer-opgave); ratchet som byggefejl |
| K-R03 | Proces-isolation på Orange Pi viser sig for dyr (RAM/CPU) | L/M | OT/edge-ing. | Mål på TL-C87FF9587CA0 i spike; fallback: cgroup-per-service med samme kontrakt |
| K-R04 | Migration mister drift-viden der kun findes i main.py-adfærd | M/H | Alle | Kontrakttests skrevet mod eksisterende adfærd FØR udtræk; strangler-mønster; intet hard-delete |
| K-R05 | macOS→container-migration forstyrrer produktion (CrushFTP sameksistens) | M/H | Driftsejer | Parallel staging først; prod-cutover bag reversibel plan; CrushFTP-porte røres ikke |
| K-R06 | Open-source-vision presser til for tidlig publicering af trust-økosystem | L/H | Mission Owner | Multi-vendor trust = separat fremtidig ADR (arvet afgrænsning); ingen publicering før SL-T + zone-register |
| K-R07 | AI-omkostninger (Gemini) eskalerer med payload-antal | L/L | Payload-ejer | Omkostningsloft i AI-datasæt; Batch-API (arvet ~50%) |
| K-R08 | Kernel i Python er for stor TCB til høje SL-T-zoner | L/M | Sikkerhed | Åben revisitation: Rust-kernel når kontrakt er frosset (se 04-05 §5.4) — kontrakten gør udskiftning mulig |
| K-R09 | (arvet) Backup/restore-evidens mangler stadig | H/H | Drift | Uændret go-live-blocker; løses på container-pakken med kvartalsvis restore-test |
| K-R10 | Reviewer-arbejde (alle 7) divergerer uden syntese | M/L | Meta Review | Denne aflevering er skrevet med eksplicitte arv/udfordring-markører for at lette sammenligning |

## Antagelser (eksplicitte — kan være forkerte)

1. Baselinens dokumentation beskriver driften retvisende (jeg har ikke verificeret mod levende systemer).
2. Orange Pi 4 Pro kan køre 2–3 ekstra Python-processer inden for strøm-/RAM-budget (PoC bruger ~15 MB RSS; umålt på hardware).
3. systemd/cgroups v2 findes på Armbian-image (rlimits i PoC er bevidst portable).
4. PostgreSQL forbliver databasen; ingen krav peger på multi-DB.
5. Mission Owner accepterer at `contracts/` bliver det langsomst-ændrede katalog i repoet.

## Uafklarede spørgsmål (til Meta Review)

- Skal kernel og headend dele ét policy-format (samme allowlist-mekanisme begge steder)? Jeg siger ja, men det er en smagssag der påvirker alle reviewers designs.
- Er en syntetisk PoC som min tilstrækkelig "executable proof" i submission-gatens ånd, eller kræves hardware-kørsel før frys? Min vurdering: gaten siger "PoC **eller** credible executable proof" — min er eksekverbar med runtime-evidens, men hardware-spiket er det rigtige næste skridt.
- Payload-pakkeformat (OCI-artifact vs. tarball+signatur) — jeg hælder til OCI-artifact for at genbruge registry-infra; udestår.
