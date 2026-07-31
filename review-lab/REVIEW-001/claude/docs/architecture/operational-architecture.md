# Operational Architecture (SABSA Operational Layer)

- **Reviewer:** Claude · **Date:** 2026-07-31

## 1. Operating model: one human, many machine guards

The platform is operated by one person assisted by AI sessions. Operational design therefore optimises for: (a) nothing degrades open when unattended, (b) every routine task is automated or runbook'd, (c) evidence is produced as a by-product of operation, not as extra work.

## 2. Standard operating processes

| Process | Trigger | Mechanism | Evidence produced |
|---|---|---|---|
| Node enrollment | new hardware | scripted provisioning (adapts source edge generator) → identity issued, policy assigned | CMDB record + enrollment audit event |
| Config change | operator edit | authored on headend → signed → distributed → node verifies + applies; invalid ⇒ keep last-good | signed policy version + apply event |
| Payload update | release | signed artifact → staged rollout (canary node first) → health gate → auto-rollback on failure | rollout record, health snapshots |
| Platform (agent/OS) update | release | same OTA path, platform channel | same |
| Remote access | support need | JIT AccessTicket (scope, expiry, destination allowlist) → session audit → auto-revoke | ticket + session log |
| Backup & restore | scheduled / release cycle | class-driven backup; **restore drill each release cycle is a release gate** | restore-drill report in GRC |
| Retention/deletion | scheduled | retention engine per channel class; quarantine before destruction (no hard delete, retained source rule) | deletion/quarantine evidence |
| Incident response | alert/finding | severity-classed runbooks (IR plan closes source R20); kill switch: revoke node/payload credentials + disable conduits | incident record in GRC |
| Vulnerability handling | CVE feed / report | SBOM per release matched against advisories; CRA-style intake documented | assessment record |

## 3. Observability

Node heartbeat + health per payload (control plane); telemetry channels (data plane) feed SIEM pipeline; single operations dashboard: fleet state, capture success per mission, spool/backpressure depth, update rollout state, open tickets/incidents, retention/backup job status. Alerting thresholds match business attributes (e.g. capture success < target ⇒ alert before customer notices). AI-assisted triage (platform AI) may summarise/propose, never execute privileged actions without the operator (accountability rule).

## 4. Release and promotion

Environments: `rd` (lab) → `staging` → `prod`, retained from source. Promotion gates (all machine-checked where possible): CI green incl. architecture tests; contract compatibility matrix updated; SBOM generated; restore drill current; ADR present for material changes; go-live checklist deltas for anything touching exposure. Commit-before-deploy retained (source K5).

## 5. Runbook inventory (to migrate/produce)

Adapted from source: edge runbook, admin manual, installation guides (headend/edge generators), FAQ/troubleshooting, backup/restore procedure, incident procedure (new), JIT access procedure. Each runbook gets a "last exercised" date surfaced in the ops dashboard — un-exercised runbooks are flagged; drills are cheap in lab and produce GRC evidence.

## 6. Operational acceptance criteria (for the migration's final gate)

1. Fleet operable ≤ 30 min/day routine (measured over 2 weeks).
2. Canary + rollback exercised on a real node with evidence.
3. Restore drill evidenced on both headend DB and image store.
4. JIT-only remote access: zero standing SSH credentials to fleet.
5. Second-payload smoke test green in CI continuously.
6. All go-live blocker classes (source checklist A–L) mapped to closed or explicitly accepted-by-owner status.
