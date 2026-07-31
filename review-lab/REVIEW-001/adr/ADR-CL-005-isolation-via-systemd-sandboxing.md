# ADR-CL-005: Payload isolation via systemd/cgroups sandboxing, spike-gated

**Status:** Proposed · **Date:** 2026-07-31

## Context

Source ADR-001 amendment 1 makes OS-level isolation the enforcement boundary but names no mechanism; baseline S-03 flags that isolation on Orange-Pi-class hardware is unproven. The mechanism choice determines cost on a solo-operated ARM fleet.

## Decision

Payloads run as **separate systemd services** with: distinct OS users; cgroups v2 quotas (`CPUQuota`, `MemoryMax`, `TasksMax`, `IOWeight`); filesystem allowlist (`ProtectSystem=strict`, `ReadWritePaths` = spool + payload state only); network allowlist (`IPAddressAllow/Deny`, default deny — payloads talk only to the local agent socket); device grants via udev group membership materialised from the manifest; `NoNewPrivileges`, `PrivateTmp`, capability bounding. The supervisor generates unit files **from the validated manifest** — the manifest is the single source, the unit is enforcement.

Gate: **SPIKE-01** on real Orange Pi 4 Pro hardware before this ADR can be marked evidenced: measure overhead (capture cadence unaffected), verify quota kill + restart-backoff + rollback drill, verify USB camera grant works under the sandbox with gphoto2.

**Why?** Real containment at near-zero marginal cost using what ships with the OS already in the fleet. **Because?** Containers on ARM SBCs add image plumbing, storage overhead and update complexity for one operator, while systemd gives 80–90% of the containment with zero new runtime; the supervisor interface hides the mechanism so containers remain a drop-in hardening step later. **For whom?** OT customers (containment promise is real), operator (no new toolchain), auditors (unit files are inspectable evidence).

## Alternatives

Docker/Podman per payload (deferred, not rejected — same supervisor interface; adopt if/when image-based payload distribution outweighs its overhead); in-process Python plugin with manifest only (rejected by source amendment 1, concurred: no containment); microVMs/Firecracker (rejected: wrong weight class for SBCs).

## Consequences

Positive: inspectable, testable, reversible; unit generation is ~200 lines. Negative: Linux-only (fine — edge is Linux; macOS headend runs no payload sandboxes in profile A); cgroup memory kills need careful restart semantics (covered by failure contract tests).

## Validation path

SPIKE-01 evidence on hardware (cannot be produced from this sandbox — recorded as the submission's primary open validation, see risk register RR-03); until then the slice proves the supervisor logic with a process-level simulation.
