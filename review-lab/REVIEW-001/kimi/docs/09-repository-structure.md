# 09 — Mål-repostruktur

```text
Mission-Platform/
  contracts/                    # DET DYRE AT ÆNDRE — SemVer, CODEOWNERS: platform
    capability-manifest-v1.schema.json
    control-plane-v1.schema.json
    data-envelope-v1.schema.json
    COMPATIBILITY.md            # platform↔payload version-matrix
  platform-core/
    edge-kernel/                # supervisor, policy, control broker, evidence ingester (~lille, auditerbar)
    hal/                        # fra edge/hal/
    identity/                   # enrollment, Ed25519 device keys, mTLS
    config/                     # signeret hierarki
    telemetry/                  # SIEM/CMDB/ITIM-klienter
    update/                     # OTA, signering, A/B rollback
    remote-access/              # JIT-tickets, conduit, recording, kill switch
  platform-headend/
    platform/auth/              # FØRSTE udtræk fra main.py
    platform/devices/ platform/config/ platform/updates/
    platform/telemetry/ platform/grc/ platform/evidence/ platform/remote_access/
    app.py                      # composition root — mål: <500 linjer
  payload-sdk/                  # helpere til at skrive en driver mod kontrakterne (valgfri, tynd)
  payloads/
    timelapse/
      driver/                   # livscyklus-implementation
      adapters/                 # gphoto2, quality, buffer, site-look — genbrugt fra edge/
      headend/                  # captures, galleri, tagging, vocabulary
      ui/                       # payload-flader til React-UI
      manifest.json             # signeret capability manifest
  deployments/
    timelapse-reference/        # container-compose: headend+db+nginx+storage
  tests/
    contract/                   # schema-validering + kompatibilitet
    vertical-slice/             # denne PoC's testmodel udbygget
    coupling/                   # anti-coupling-tests (se nedenfor)
  docs/ adr/ migration/ evidence/ tooling/
```

**Anti-coupling-tests (`tests/coupling/`) — min tilføjelse til submission-gatens "future payload test cases":** en syntetisk `waterworks`-stub-payload (Modbus-læsning simuleret) skal kunne (a) validere sit manifest, (b) starte, (c) svare på `status.get`, (d) aflevere et `process`-klassificeret artifact — **uden at nogen fil under `platform-core/` eller `platform-headend/platform/` ændres**. Testen fejler hvis stubben skal importere noget fra `payloads/timelapse/`. Det gør "timelapse-afhængighed" til en byggefejl i stedet for en review-bemærkning.

**CODEOWNERS:** `contracts/` og `platform-core/` → platform-ejere + Mission Owner; `payloads/timelapse/` → payload-ejere. Path-filtreret CI pr. spor (arvet fra modulariseringsplanen §6 — den var rigtig).
