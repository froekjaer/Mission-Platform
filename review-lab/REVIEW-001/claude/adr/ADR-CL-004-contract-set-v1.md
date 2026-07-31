# ADR-CL-004: Contract set v1 — control, data, manifest

**Status:** Proposed · **Date:** 2026-07-31

## Context

Source ADR-001 sketches `PayloadDriver` + manifest normatively and defers detail to a never-written ADR-002. The contracts are the platform's most expensive-to-change element; v1 must be small, implementable and provably sufficient for timelapse.

## Decision

Three contracts, independently SemVer'd (full definition: `docs/architecture/component-architecture.md` §4–5; executable: `implementation/contracts/`):

1. **Control v1** — `PayloadDriver`: `configure/start/stop/health/handle_command`. Synchronous, supervisor-driven; no payload thread owns its own lifecycle.
2. **Data v1** — `DataSink` with three channel kinds (blob, timeseries, event); every channel declares classification + retention class; platform owns transport/storage/retention; `Backpressure` is part of the contract.
3. **Manifest v1** — JSON-Schema-validated declaration (capabilities, quotas, fs/net allowlists, channels, contract majors); validated fail-closed against an operator-signed policy allowlist; unknown anything ⇒ refuse + log.

Explicitly **excluded from v1** (each would be a major or a new contract): actuation capabilities (safety gate, security-compliance §5), payload-to-payload communication, streaming/real-time channels (SDR waterfall etc. — future `stream` kind), dynamic capability grants at runtime.

**Why?** One seam, minimal kinds, everything classified. **Because?** Analysis of the named future payloads shows blob+timeseries+event covers their v1 needs; every widening is cheap to add later and expensive to remove. The `tick()` in the source sketch is replaced by driver-internal scheduling under `start/stop` because real payloads (long exposures, batch uploads, sensor polling) have irreconcilable cadences — the supervisor should own liveness (health), not cadence. **For whom?** Payload authors (small surface), operator (uniform enforcement), auditors (classification everywhere).

## Alternatives

Adopt source sketch verbatim including `tick(now)` (rejected: cadence mismatch above — this is this review's one *substantive* deviation from the source sketch, flagged for Meta Review attention); gRPC/protobuf contracts now (rejected: adds toolchain weight before a second language exists; the ABCs + JSON schema are transport-agnostic and can be projected to protobuf later); full plugin framework (rejected: YAGNI at n=1 payloads).

## Consequences

Positive: implementable in <500 lines (proven in slice), testable without hardware. Negative: synchronous control contract limits exotic payloads until a v2; accepted.

## Validation path

Vertical slice: timelapse driver + waterworks simulator both run under the same host; fail-closed tests for unknown capability, oversized quota, unsigned policy, contract-major mismatch, undeclared channel. All evidenced in `evidence/vertical-slice-evidence.md`.
