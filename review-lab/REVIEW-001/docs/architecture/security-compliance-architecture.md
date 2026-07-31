# Security, Privacy, Safety & Compliance Architecture

- **Reviewer:** Claude · **Date:** 2026-07-31

## 1. Threat assumptions and trust boundaries

Adversaries considered: internet-scale opportunistic attackers on the exposed control/data endpoints; a thief/tamperer with physical access to an edge node; a compromised payload (bug or supply chain); a stolen operator credential; a malicious or defective update; and (honestly) *operator error under time pressure* — historically the source system's most productive threat (test-DB overwrite incident, auth-mount regressions).

Trust boundaries = zone model in `physical-architecture.md` §4. Every boundary crossing is authenticated, least-privileged, logged, and fail-closed. The payload sandbox boundary is new relative to the source system and is the platform's principal safety mechanism for OT futures: **a payload compromise must be contained to its quota, its filesystem allowlist, its granted devices and its declared channels.**

## 2. Control set (mapped to source findings)

| Control | Closes / prevents | Standard hook |
|---|---|---|
| Authenticated-router-by-construction + CI sweep | source SEC-001/R15/R22 class | IEC 62443 SR 1.x; ISO 27001 A.8 |
| Fail-closed manifest validation vs. signed allowlist | privilege creep, unknown capability | 62443 SR 2.1 least privilege; CRA secure-by-default |
| Separate payload OS identity + sandbox | payload→platform escalation (source R05 blast radius) | 62443 zones; CRA |
| Signed config/OTA/payload chain + rollback | malicious/defective update (R06) | CRA update requirements |
| Device CA + mTLS (stage 3) | MitM, node spoofing (R05/R08 — open at baseline) | 62443 SR 1.2 |
| JIT AccessTicket conduits, no standing SSH | R10/R19; vendor access future | 62443 SR 2.6; NIS2 access mgmt |
| Class-driven retention/quarantine engine | R12 GDPR evidence gap | GDPR art. 5/17/30 |
| Evidenced restore drills as release gate | R09 (open at baseline) | ISO 27001 A.8.13; NIS2 |
| SBOM per release + vulnerability intake | CRA readiness | CRA annex; ISO 27036 |
| Step-up MFA on sensitive ops | credential theft | source K4 retained |
| Kill switch (credential + conduit revocation) | compromised node/payload | 62443; IR plan (closes R20) |

## 3. Privacy (GDPR) architecture

Roles: customers are controllers for their site imagery in the target model; the platform operator is processor (DPA templates required at first commercial site — carried as migration gate, not resolved by architecture). Mechanisms: classification on every channel; DPIA template instantiated per camera-bearing mission; retention classes with enforced deletion evidence; redaction service retained from source as a payload-domain capability for imagery; data subject request runbook. Personal data never in telemetry channels (schema-checked: `personal-*` classifications forbidden on `timeseries`/`event` kinds v1 — images only via blob channels).

## 4. AI governance (AI Act-aware)

Retains and formalises the source AI domain split: each AI use registered with purpose, prompt ownership, provider, data classification in/out, result ownership, human accountability. Current uses (image tagging, translation, ops assistance) are low-risk under the AI Act; the register is the mechanism that keeps that assessment current as payloads evolve. Providers are adapters (Gemini/Ollama swappable); customer imagery leaves EU region only if the mission's policy explicitly allows it (fail closed: default EU/local).

## 5. Safety posture for OT payloads (forward-looking, gating)

Before any payload touching physical processes (waterworks etc.): monitoring-only first (read-only conduits — the platform can *observe* OT without ever being able to actuate); actuation requires a separate safety ADR, per-mission hazard analysis, and fail-safe defaults where loss of platform = process continues safely. These are recorded as **platform invariants now** so no early design choice forecloses them: the manifest has no actuation capability in v1 — adding one is deliberately a contract major bump with safety review.

## 6. Compliance mapping summary

- **GDPR:** applicable now — mechanism-backed (above); DPIA/DPA/RoPA are migration-stage gates.
- **CRA:** product-with-digital-elements posture: secure-by-design evidence, SBOM, update mechanism, vulnerability handling — all designed in; formal conformity work deferred until commercial distribution demands it (recorded, with rationale, not ignored).
- **NIS2:** platform operator itself likely out of direct scope at current size; future OT customers may be in scope ⇒ platform ships the evidence (logging, access control, incident records) those customers need. Marked "prepare, not claim".
- **IEC 62443:** used as design vocabulary (zones/conduits/SRs) — alignment, not certification (proportionality).
- **ISO 27000:** the GRC register + this control set form the ISMS seed; no certification pursued now.

## 7. Residual risks accepted (see risk register)

No hardware root of trust on current edge SBC; single-headend SPOF; solo-operator availability; "virtual" pentest only until external test is commissioned. Each has owner, treatment and trigger in `docs/risk-register.md`.
