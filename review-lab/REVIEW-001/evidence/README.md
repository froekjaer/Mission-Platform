# Evidence — Z.ai REVIEW-001 Vertical Slice

**Reviewer:** Z.ai
**Branch:** `review/review-001-zai`
**Test run date:** 2026-07-25
**Result:** `17 passed in 0.04s` — see `vertical_slice_test_results.txt`

## How to reproduce

```bash
cd review-lab/REVIEW-001/implementation
python3 -m venv .venv
. .venv/bin/activate
pip install pytest
python -m pytest mission_platform/tests/ -v
```

Python 3.12 was used. No other dependencies — the slice is deliberately dependency-free so the proof is about the *architecture*, not library plumbing.

## What the 17 tests prove (mapped to claims)

| Claim | Tests | Evidence |
|---|---|---|
| **ADR-Z-001 — the contract fits reality.** The PayloadDriver contract can drive real capture behaviour end-to-end. | `TestContractFitsReality` (3 tests): load → configure → tick → capture → SHA-256 artifact → telemetry → allowlisted command. | Timelapse payload wraps synthetic capture through the contract; capture produces an integrity hash and a telemetry emission. |
| **ADR-Z-002 — capability enforcement is real and fail-closed.** | `TestCapabilityEnforcementFailClosed` (3 tests): off-manifest file write denied; off-manifest network denied; on-manifest allowed. | Denied attempts raise `CapabilityDenied` AND are written to the audit spine. |
| **Business Arch §4 — Extensibility.** A second payload loads with NO platform code changes and is isolated. | `TestExtensibility` (3 tests): two payloads load independently; payloads have independent allowlists (env can reach a host timelapse cannot; timelapse can write a path env cannot); the env payload's *import statements* do not reference timelapse. | The environmental_sensor payload imports only `contracts` + `platform.supervisor` — zero timelapse coupling. |
| **ADR-Z-001 — manifest validation is a fail-closed gate.** | `TestManifestValidation` (4 tests): missing field rejected; unknown data classification rejected; missing quota rejected; supervisor rejects + logs. | Bad manifests raise `ManifestValidationError`; the supervisor never loads them. |
| **Migration §6 — contract-version compatibility enforced.** | `TestContractCompatibility` (2 tests): incompatible major version rejected; driver/manifest version drift rejected. | The compatibility matrix is strict; drift between a driver's declared version and its manifest is caught at load. |
| **Accountability — audit spine records every decision.** | `TestAuditSpine` (2 tests): load decisions audited; actor namespace correct (`payload:<name>`). | Every load, deny, and reject appends an `AuditRecord`. |

## Honest scope statement

This slice is intentionally minimal. It does NOT:
- implement a real camera adapter (a `SyntheticCapture` stands in);
- generate real systemd units / seccomp filters (an in-process `Sandbox` proxy proves the *enforcement logic*; ADR-Z-002's validation path describes how the real unit generator builds on this);
- connect to a real database, headend, or network;
- implement any of the 11 🔴 hard blockers (see Risk Register).

It proves the **architecture is enforceable**, not that the product is built. That is exactly what Migration Step 0 (the contract spike) is for: prove the contract fits reality *before* moving production code.

## Bias note

I authored the REVIEW-001 governance documents (BUILD-016) in the turn immediately before this submission, including the submission checklist whose criteria these tests address. The risk is "teaching to the test." Mitigation: each test maps to a specific architectural claim derived from TimeLapse Pro evidence (ADR-001, SABSA, KRAVREGISTER), with the Why/Because/For-whom recorded in the ADRs — not to an abstract rubric item.
