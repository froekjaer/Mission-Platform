# Vertical Slice — Executable Proof (REVIEW-001, Claude)

Implements contract set v1 (ADR-CL-004) end-to-end: fail-closed manifest and
signed-policy admission, supervisor lifecycle with failure contract, classified
data-plane spool, the timelapse payload, and the waterworks anti-coupling
payload — pure Python 3.10+, standard library only.

## What it proves

1. `PayloadDriver` + `DataSink` + manifest v1 fit the real timelapse capture flow.
2. Fail-closed works: 9 refusal paths tested (unknown capability/field, ungranted capability, quota over ceiling, contract-major mismatch, personal-data-on-timeseries, duplicate channel, tampered/unsigned policy) — a refused payload is never even instantiated.
3. Platform neutrality: an OT-domain payload (timeseries+events, no imagery) runs under the identical supervisor; import boundaries are AST-checked; quarantining a crash-looping payload leaves the other running.
4. GDPR-as-mechanism: every stored object carries classification + retention class in its sidecar.

## What it does NOT prove (honesty)

OS-level sandbox enforcement (systemd/cgroups) — that is SPIKE-01 on real
Orange Pi hardware (ADR-CL-005); here isolation is logical. No network, no
real camera, no headend: the slice is the edge contract seam only.

## Reproduce

```bash
cd review-lab/REVIEW-001/implementation
python3 -m pytest tests/ -v
```

Expected: all tests pass. Evidence of the run: `../evidence/vertical-slice-evidence.md`.
