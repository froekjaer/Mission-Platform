# ADR-0002: Trust-oriented edge, Action Requests and Device Adapters

**Status:** Accepted  
**Decision date:** 2026-08-12  
**Foundation:** 0.2

## Context

REVIEW-001 validated the Platform/Payload direction and demonstrated a second, read-only waterworks-style payload. Subsequent meta-review identified that critical-infrastructure use requires stronger treatment of Availability, Reliability, local autonomy, controlled two-way communication and downstream device lifecycle management.

Direct remote command/tunnel semantics would enlarge blast radius and make headend compromise or dependency loss too closely coupled to the local mission. Vendor/device integrations embedded in the core would also undermine modularity and technology independence.

## Decision

1. **Trust is the primary architectural quality.** Security, Safety, Availability, Reliability, Resilience, Recoverability, Explainability and Evidence contribute to Trust according to mission consequence.
2. **The edge is a Trust and execution boundary.** It acts as local Policy Enforcement Point, Execution Authority, failure-containment boundary and evidence producer.
3. **The headend sends Action Requests, not transparent commands.** The edge initiates communication, retrieves signed requests/artifacts, validates them, evaluates local policy and mission state, and decides whether/when to execute.
4. **Local mission continuity is preferred.** Loss of headend/cloud/WAN/DNS/AI/update services must not by itself stop an otherwise autonomous essential local function.
5. **Updates use one trusted pattern.** Edge software and downstream firmware/software updates use signed artifacts/instructions, target binding, integrity and compatibility checks, controlled execution, verification, evidence and rollback where possible.
6. **Device-specific knowledge is modular.** PLC, camera, PC, radio and other integrations are implemented as Device Adapters behind stable contracts. Vendors/community contributors may add adapters without changing Mission Core.
7. **Adapters cannot bypass Trust controls.** All actions remain subject to edge identity, authorization, policy, audit, mission state and update controls.
8. **Observation precedes actuation.** High-consequence physical actuation requires explicit capability, separately governed contracts and appropriate hazard analysis.

## Consequences

- A compromised headend does not automatically gain direct control of the internal mission network.
- Cryptographic validity is necessary but does not force immediate execution; local mission/safety/reliability constraints may defer a request.
- Offline operation and graceful degradation become architectural requirements for essential functions.
- Device vendors can extend the framework with firmware, parameter, logging, telemetry and diagnostic routines without contaminating the core.
- Generic restart/quarantine policies are insufficient for mission-critical functions; mission-aware failure policy is required.
- The contract model must distinguish requests/intents, execution decisions, results and evidence.

## Evidence and follow-up

The REVIEW-001 waterworks simulation remains useful evidence of domain neutrality, failure containment and read-only OT integration, but is not a realistic waterworks safety/reliability validation. Follow-up work should extend the proof with Action Request semantics, mission criticality/failure policy, offline behaviour, signed update flow and Device Adapter examples, then validate on representative physical hardware.
