# Trust, Edge and Device Adapter Model

**Version:** 0.2  
**Status:** Foundation

## Trust as the primary quality

Mission Platform SHALL be designed for justified trust. Security alone is insufficient: a secure system that unnecessarily interrupts an essential mission is not trustworthy.

Trust is supported by security, safety, availability, reliability, resilience, recoverability, explainability and evidence. The balance is mission-dependent and SHALL be explicit.

For critical infrastructure, Availability and Reliability are first-class architectural concerns. Loss of cloud, headend, WAN, DNS, AI or update services SHALL NOT by itself stop a locally autonomous essential function.

## The edge is a trust boundary

The edge separates the external control plane from the local mission environment. It is not a transparent remote-control tunnel.

Communication is bidirectional in meaning, but external systems do not directly command internal devices. The edge initiates communication with the headend, retrieves signed Action Requests and artifacts, validates them, applies local policy and mission-state constraints, and only then executes an allowed local action.

The headend requests. The edge decides and executes.

## Action Request lifecycle

A request SHALL carry enough information to validate at least:

- issuer and authorization;
- target identity and operation;
- requested parameters or desired outcome;
- freshness, sequence/replay protection and validity window;
- required preconditions and mission constraints;
- artifact identity/hash where relevant;
- cryptographic signature.

The edge SHALL record a lifecycle such as REQUESTED, VALIDATED, AUTHORIZED, DEFERRED/REJECTED, EXECUTING, VERIFIED, and COMPLETED/FAILED, with evidence returned to the headend.

A valid signature proves provenance and integrity; it does not prove that execution is safe or appropriate now. Local policy and mission state remain authoritative.

## Controlled two-way operation

Telemetry, logs, events and evidence flow outward under edge policy. Requests, configuration and signed artifacts flow inward only through the edge's controlled pull/retrieval mechanism. No general-purpose inbound path into the local environment is implied.

When disconnected, the edge SHOULD continue locally permitted operations, buffer outward evidence where appropriate, and accept no new remote requests until communication and trust validation are restored.

## Device adapters

Device-specific knowledge SHALL be modular. A camera, PLC, industrial PC, radio or other device is integrated through a Device Adapter rather than by adding vendor logic to the Mission Core.

A vendor or community contributor can therefore add support for a device family by implementing a bounded adapter that declares and implements supported capabilities, for example:

- firmware inventory and signed firmware update;
- parameter read and controlled parameter change;
- health/status and diagnostics;
- logs and events;
- configuration backup/restore;
- device-specific verification and rollback where supported.

Adapters MUST NOT bypass edge policy, identity, audit, authorization, update validation or mission-state controls. Vendor extensibility is subordinate to the Trust model.

## Unified update model

Updating the edge itself and updating a downstream device SHALL use the same trust pattern: signed artifact plus signed instruction, target binding, hash verification, compatibility/precondition checks, controlled staging, execution, post-update verification, evidence, and rollback/known-good recovery where technically possible.

An urgent vulnerability SHALL NOT automatically imply immediate installation. The edge MAY defer an otherwise valid update when mission state, safety, availability or reliability constraints require it. Compensating controls and staged/canary rollout SHOULD be supported by higher-level policy.

## Failure semantics

Security admission failures (unknown identity, bad signature, invalid capability, replay) SHALL fail closed.

Infrastructure dependency failures (headend/WAN/cloud/AI unavailable) SHOULD degrade gracefully and preserve locally autonomous mission functions.

Safety- or mission-critical failures SHALL follow an explicitly defined mission-specific failure policy rather than a generic restart-or-quarantine rule.

## Actuation boundary

Read-only observation remains the safest initial OT profile. Physical actuation requires explicit capability declaration, local authorization and mission/safety policy. High-consequence actuation SHOULD require a separately governed contract/version and hazard analysis.

## Architectural consequence

The edge is simultaneously a Policy Enforcement Point, Execution Authority, failure-containment boundary, evidence producer and local autonomy layer. Device adapters provide extensibility beneath that boundary without weakening it.
