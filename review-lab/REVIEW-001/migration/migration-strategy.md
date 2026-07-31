# Migration Strategy — TimeLapse Pro → Mission Platform

- **Reviewer:** Claude · **Date:** 2026-07-31 · **Governing ADR:** ADR-CL-006

Staged, additive, reversible. Each stage lists: work, go-live blockers it closes (source `GO_LIVE_CHECKLIST_v10` letters), exit gate, rollback. The running lab system remains authoritative throughout; "cutover" is always per-component with the old path kept until verified.

## Stage 0 — Foundations in-repo (no behaviour change)

Work: land `contracts/` (from this workspace's slice), architecture tests (import boundary, secure-router grep, second-payload smoke), single ADR convention, re-target ratchet to composition-only goal. Closes: none directly (K-class governance). Exit gate: CI green with new tests on unchanged behaviour. Rollback: revert commits; nothing depends on them yet.

## Stage 1 — Headend control-plane extraction + exposure readiness

Work: extract auth/RBAC/MFA, node/enrollment, config+signing, OTA routes from `main.py` into `platform/headend/control_api` via authenticated-router factory; old paths delegate. In parallel (same surface): implement 8443/DNS-01 exposure config (checklist A-01..A-13), stale-credential cleanup + MFA enforcement audit (checklist C/K-class), fail2ban config as code. Closes: A-class blockers, parts of C. Exit gate: route-auth sweep green; ratchet shows `main.py` shrink ≥ 30%; exposure design verified on staging with `lsof` evidence. Rollback: delegation shims revert per router.

## Stage 2 — Data plane and evidence debt

Work: `DataChannel` blob implementation over existing SFTP ingest (wrapper, not replacement); storage registry + retention engine with classification on the two existing channels (images, telemetry); **backup/restore drill scripted and executed with evidence** (closes R09/checklist F); GDPR pack: DPIA instance, retention policy activation, deletion evidence (checklist H). Profile-B CI job (Linux boot of headend services) starts here. Exit gate: restore drill evidence in GRC; retention job evidenced; classification present on 100% of stored new objects. Rollback: wrapper removal returns raw SFTP path.

## Stage 3 — Edge agent/payload split on hardware

Work: split `edge/agent.py` world into platform agent + timelapse payload behind contracts; SPIKE-01 (ADR-CL-005) on the bench Orange Pi; then canary on the active node with staged rollout + rollback drill; device CA/mTLS enrollment for nodes (closes R05/R08 partially, checklist D). Exit gate: canary node runs split stack ≥ 14 days at ≥ baseline capture success; rollback drill evidenced; mTLS on control plane. Rollback: OTA back to monolithic edge build (kept signed and releasable until stage 5).

## Stage 4 — Payload domain services + second payload proof

Work: move tagging/video/site-look behind the payload-domain service; AI register live; **waterworks simulator deployed as second payload on the bench node** — the platform-neutrality proof on real hardware; signed payload packages (extends OTA trust model). Exit gate: second payload runs with zero platform changes; SBOM per release; import-boundary tests still green. Rollback: domain service is additive; old code paths quarantined not deleted.

## Stage 5 — Decommission-by-evidence

Work: retire delegation shims and monolithic edge build after all cutovers individually evidenced; archive TimeLapse Pro repo as historical evidence (never deleted); Mission Platform `main` becomes the operational source per a separate Mission Owner acceptance decision (per BASELINE.md preservation clause). Exit gate: operational acceptance criteria (operational-architecture §6) all met. Rollback: none needed — this stage only removes already-replaced duplicates.

## Cross-cutting rules

No hard deletes (quarantine); commit-before-deploy; every stage produces GRC evidence as a by-product; any stage may pause indefinitely without leaving the system worse than baseline — the explicit test for "additive".

## Effort honesty

Stages 0–2 are solo-feasible in normal working rhythm (they are mostly work already owed to go-live). Stage 3 contains the real technical risk (hardware, camera under sandbox) — SPIKE-01 exists to surface it early and cheaply. Stage 4–5 should not be scheduled until a business trigger (second customer type, OT pilot, or open-source decision) justifies them; the platform is already earning value from stages 0–3.
