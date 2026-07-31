# ADR-K001 — Kontrakt-first i stedet for kode-first

- **Status:** Foreslået (Kimi, REVIEW-001) · **Dato:** 2026-07-29
- **Udfordrer:** `Arkitektur/Modularisering_Platform_Payload_Plan.md` Fase 1 (wrap eksisterende kameralogik bag et in-process Python-interface) — **ikke** ADR-001's beslutning, som jeg tilslutter mig.
- **Superseder:** Intet. Hvis Mission Owner afviser, er planens Fase 1 stadig en gangbar vej.

## Kontekst

ADR-001 (accepteret 2026-07-16) udskød bevidst kontraktens form og håndhævelsesmekanismen til ADR-002. Planens Fase 1 foreslår at definere et `PayloadDriver`-Python-interface og wrappe nuværende kameralogik *in-process* — med proces-isolation som senere skridt.

**Why (mit spørgsmål):** Hvilken missionværdi skaber det at indføre en kontrakt, der endnu ikke isolerer?

**Because (evidens):**
1. QA-review 2026-07-17 §2.5: nye moduler binder sig til monolitten via `from main import ...` inde i funktionskroppe — "det cementerer main.py som nav". En in-process wrapper er endnu en in-process binding.
2. R26: teknisk gæld er den primære driver for "ikke production-klar". En wrapper uden enforcement ændrer ingen fejlklasse — den flytter kun kode.
3. ADR-001 amendment 1 (Codex): manifest er deklaration; *platform-policy er autoritativ enforcement*. Uden procesgrænse findes enforcement ikke — kun konvention.

**For whom:** Driftsejeren, der skal kunne stole på at en payload-fejl ikke kan tage kernen ned (Availability); fremtidige OT-kunder, for hvem "senere" i sikkerhedsarkitektur historisk betyder "aldrig" (IEC 62443 SL-T kan ikke eftermonteres gratis).

## Beslutning

1. Kontrakterne defineres som **wire-kontrakter først**: tre versionerede JSON-schemas (`contracts/`: capability-manifest, control-plane, data-envelope), SemVer fra dag 1.
2. Payload kører som **separat OS-proces fra første implementation** — ikke som målbillede. I REVIEW-001 bevist med en ~250-linjers stdlib-kernel (9/9 runtime-checks).
3. Python-API'er (PayloadDriver-klasser) må gerne eksistere som *bekvemmelighedslag* (payload-sdk), men kontrakten er ledningen, ikke klassen.

## Alternativer overvejet

- **Planens Fase 1 (in-process wrapper):** Afvist som *målarkitektur* — men acceptabel som taktisk mellemtrin i timelapse-pro repoet, så længe ingen tror det er isolation. Min løsning springer mellemtrinet over i det nye repo, hvor der ingen monolit er at wrappe ind i.
- **gRPC/Protobuf:** For tidligt; JSON-schema kan valideres, diffes og auditeres af både mennesker og AI uden toolchain. Transport kan udskiftes senere uden semantik-ændring.
- **Microservices/containere pr. payload på edge:** For tungt for Orange Pi-strømbudget og operationel kompleksitet; processer + cgroups giver 90% af isolation for 10% af vægten.

## Konsekvenser

+ Isolation og fail-closed er reelle fra dag 1; kernel kan auditeres på én eftermiddag.
+ Kontrakten bliver testbar uden hardware og uden timelapse-kode (waterworks-stub-test).
− Kræver at kernel skrives før nogen payload-logik flyttes (forhåndsinvestering ~1 uge).
− stdio/spool-transport er simpel men primitiv; throughput-krævende data (WebRTC live view) kræver en udvidet data plane senere — designet til, ikke bygget.

## Migration/kompatibilitet

Ingen ændring i timelapse-pro. Kontrakt-spiket valideres mod LAB-edge (TL-C87FF9587CA0) med gphoto2 bag `capture.now`; eksisterende capture-pipeline fortsætter uforstyrret i parallel.

## Reversibel valideringsvej

Hvis hardware-spiken viser uoverstigelige problemer (RAM, timing), rulles tilbage til planens Fase 1 in-process-model med uændret manifest-schema (manifestet overlever beslutningen; kun transporten ændres). Beslutningen er dermed reversibel inden for én sprint.
