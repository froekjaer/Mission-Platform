# Implementation Roadmap

- **Reviewer:** Claude · **Date:** 2026-07-31 · Stages from `migration/migration-strategy.md`; "cycle" = the project's natural release rhythm, deliberately not calendar-fixed for a solo operator.

| Order | Work | Gate to advance |
|---|---|---|
| 1 (stage 0) | Land contracts + architecture tests + ADR convention in the adopted mainline | CI green, behaviour unchanged |
| 2 (stage 1) | Control-plane extraction from `main.py` + 8443/DNS-01 exposure + credential/MFA cleanup | auth sweep green; ratchet −30%; staging exposure evidenced |
| 3 (stage 2) | Data-plane wrap (classification), retention engine, **restore drill**, GDPR pack, profile-B CI | restore + retention evidence in GRC |
| 4 (SPIKE-01) | systemd sandbox spike on bench Orange Pi | measured report; go/no-go on ADR-CL-005 |
| 5 (stage 3) | Edge agent/payload split, canary node, mTLS enrollment | 14-day canary at baseline capture success |
| — | **Go-live decision window** (all blocker classes now closed or accepted) | Mission Owner go/no-go |
| 6 (stage 4, business-triggered) | Payload domain services, signed payload packages, second payload on hardware, SBOM | second payload runs, zero platform change |
| 7 (stage 5) | Decommission-by-evidence, operational acceptance | acceptance criteria (operational-architecture §6) |

## Next safe step (the single recommended first commit after meta-review)

Adopt `contracts/` + `tests/architecture/` from this workspace into the integration plan **as tests-only** (stage 0): zero runtime risk, immediately guards all future work, and is compatible with elements from any other reviewer's branch. 

## Explicit non-schedule

Stages 4–5 are intentionally **not** scheduled: they await a business trigger (second customer type, OT pilot, or open-source decision). The platform must not become a hobby that competes with the business it serves.
