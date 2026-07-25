---
id: ADR-Z-002
title: Payload isolation is an enforcement boundary, enforced by systemd + seccomp
status: Proposed
date: 2026-07-25
deciders: Z.ai (reviewer proposal; Mission Owner decides; isolation primitive is Q-4)
supersedes: none
relates_to: timelapse-pro ADR-001 amendment 1 (process isolation as enforcement boundary)
---

# ADR-Z-002 — Payload isolation is an enforcement boundary (systemd + seccomp)

## Context

ADR-001 amendment 1 states: "A PayloadDriver + manifest does NOT in itself give CPU/RAM/disk/net/credential isolation or fault containment. When the ADR promises isolation, the payload must run in a separate OS-sandboxed process (or equivalent enforcement boundary). The manifest is declaration; platform policy is authoritative enforcement." The amendment is accepted but the enforcement primitive is undecided.

## Decision

**Standardise on systemd services + dedicated users + seccomp + (optional) AppArmor as the payload isolation boundary**, with manifest-driven `ReadWritePaths` / `IPAddressAllow` confinement. The platform supervisor translates a payload's manifest into a generated systemd unit + seccomp filter at load time.

Specifically:

- One systemd service per payload: `dk.froekjaer.payload-<name>.service`
- Dedicated OS user `payload-<name>`, not in the platform group
- seccomp allowlist syscall filter (denials fail-closed with logging)
- `ReadWritePaths=` from manifest `allowlist.files`; `IPAddressDeny=*` + `IPAddressAllow=` from manifest `allowlist.network`
- Resource limits (`CPUQuota=`, `MemoryMax=`, `TasksMax=`) from manifest `resource_quota`
- Optional AppArmor profile for high-consequence payloads (OT verticals)

## Why (business attribute)

Payload isolation / fault containment, Availability. A fault in one payload must not compromise the platform core or another payload — this is the credibility foundation for OT verticals (IEC 62443 zone/conduit, CRA secure-by-design).

## Because (evidence/reasoning)

- The edge already runs systemd (Armbian; existing `timelapse-edge.service` etc.) — the primitive is already in production.
- systemd resource control (`CPUQuota`, `MemoryMax`, `IPAddressDeny/Allow`, `ReadWritePaths`, `PrivateTmp`, `ProtectSystem`) is a mature, kernel-enforced isolation mechanism with no new runtime dependency.
- seccomp is the standard Linux syscall-filter mechanism; deny-by-default matches the fail-closed principle.
- Heavier alternatives (containerd, microVMs, systemd-nspawn) add image/build complexity and overhead that the threat model does not require on a single-payload edge today.
- The manifest already declares exactly the inputs systemd needs (`resource_quota`, `allowlist.files`, `allowlist.network`), so the supervisor-to-unit translation is mechanical.

## For whom

Payload owners who need a credible isolation guarantee; regulators/auditors who need to see a named enforcement mechanism; the on-call engineer who needs fault containment to limit blast radius.

## Alternatives considered

- **Containers (containerd/podman).** Rejected for now: image build/distribution complexity, storage overhead on 128 GB NVMe edges, and a new trust chain (image signatures) before the contract has proven itself. Revisit if/when payloads come from third-party vendors (ADR-001 multi-vendor future ADR).
- **microVMs (Firecracker etc.).** Rejected: hardware-virt overhead is unjustified for single-tenant edges; ops complexity.
- **systemd-nspawn.** Considered; lighter than full containers but still namespace-image oriented. systemd services + seccomp give equivalent isolation for less moving parts on this footprint.
- **In-process isolation (status quo).** Rejected — this is precisely what amendment 1 forbids.

## Consequences

- **Positive:** real fault containment; named mechanism for auditors; low overhead; no new runtime; manifest-driven (declarative).
- **Negative:** systemd unit generation is new platform code that must be tested; seccomp filters can break legitimate payloads if the manifest is wrong (mitigation: fail-closed + clear logging + a per-payload CI manifest test).
- **Neutral:** AppArmor is optional and profile-per-payload; not mandated at launch.

## Open dependency

The isolation primitive choice (systemd+seccomp vs. container) is **Q-4** in my assumptions. This ADR picks the default (systemd+seccomp) but is explicitly reversible if the Mission Owner prefers containers — especially relevant if Q-7 (third-party payloads) resolves "yes" earlier than expected.

## Validation path (reversible)

The vertical slice includes a **capability-enforcement test**: a payload that attempts an off-manifest network destination is denied fail-closed, and the denial is logged. This proves the enforcement boundary is real, not decorative. If the test cannot be made to pass cleanly, fall back to a stronger primitive.
