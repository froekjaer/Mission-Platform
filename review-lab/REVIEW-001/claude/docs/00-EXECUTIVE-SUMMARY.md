# Executive Summary — REVIEW-001 Submission (Claude)

- **Reviewer:** Claude · **Date:** 2026-07-31 · **Branch:** `review/review-001-claude`
- **Source examined (read-only):** `froekjaer/timelapse-pro@eed9e3c8`

## Verdict

**The current architectural direction is justified.** Independent examination of the frozen baseline reproduces the forcing functions behind the accepted Platform/Payload split (source ADR-001): a 18,541-line headend monolith with a thrice-repeated authentication failure class, an edge that is already half-modular, and a documented OT ambition that would otherwise require forking the codebase. This review **retains** that direction and **refines** it in four places rather than replacing it.

## The four refinements

1. **Headend first, not edge first (ADR-CL-003).** The source decision is edge-centric, but the headend carries the exposed attack surface, the recurring security regressions and every future payload's server side. The transformation is sequenced as a strangler over the headend, decomposed by a two-plane × two-layer model (platform/payload × control/data), with auth made structural ("authenticated router by construction") instead of merely detected.
2. **A narrower, executable contract set (ADR-CL-004).** Three contracts — control (`PayloadDriver`), data (three classified channel kinds), manifest (fail-closed against operator-signed policy). One substantive deviation from the source sketch: `tick(now)` is replaced by `start/stop` with driver-internal cadence. Every stored object carries GDPR classification as mechanism, not documentation.
3. **Machine-enforced neutrality (ADR-CL-002).** The platform/payload boundary is guarded by CI import tests and a permanently maintained second payload from a different domain (waterworks simulator) — not by review vigilance. This is calibrated to the project's binding constraint: it is operated by one person.
4. **Migration that accelerates go-live (ADR-CL-006).** Five additive, reversible stages in which the early platform work *is* the outstanding go-live blocker work (exposure design, restore evidence, GDPR pack, credential cleanup). The platform must pay for itself immediately; later stages await a business trigger.

## Evidence

An executable vertical slice (stdlib Python, `implementation/`) proves the contracts on the real timelapse flow: **20/20 tests pass**, covering nine fail-closed refusal paths, policy-signature tamper rejection, failure containment between payloads (quarantine one, the other keeps running), AST-verified import boundaries, and classification-carrying storage (`evidence/vertical-slice-evidence.md`).

## Principal open risk

The isolation-enforcement claim (systemd/cgroups on Orange Pi class hardware) is designed and spike-gated but **not hardware-validated** from this sandbox — SPIKE-01 (ADR-CL-005) is the submission's primary follow-up, and RR-03 its highest-priority risk.

## Contents

Business architecture (`docs/mission/`), six SABSA-layer + security + AI docs (`docs/architecture/`), six ADRs (`adr/`), migration strategy + full source-to-target traceability (`migration/`), risk register + roadmap + collaborative-intelligence assessment (`docs/`), executable slice + tests (`implementation/`), evidence (`evidence/`), completed checklist (`SUBMISSION-CHECKLIST.md`).

## Recommended next safe step

Adopt `contracts/` + the architecture tests as a tests-only stage-0 commit: zero runtime risk, guards every subsequent step, and remains compatible with elements selected from any other reviewer's branch.
