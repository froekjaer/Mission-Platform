# z.ai — Mission Platform Review

## Material reviewed

- **Commit/ref:** main HEAD
- **Review date:** 2026-07-21

## Observations

Mission Platform defines itself as "an open, modular, AI-native and human-governed reference implementation" but contains no implementation code, no API specifications, no schemas, and no reference services. It is documentation describing intent to build a platform, not a platform itself.

The documentation follows mission-framework's language closely — the same concepts, the same diagram structures, the same rhetorical patterns. ADR-0001 is the only document with concrete architectural decisions (the decision to be documentation-first, vendor-neutral, API-first, event-driven). The Architecture Tests are a useful reflective checklist. The Mission Meta Model has the beginnings of formalisation (relationship semantics, cardinality, ownership, time).

No Mission DSL, no compiled schema, no validators, no reference implementations exist.

## Interpretations

Mission Platform is, at this stage, an extension of mission-framework's documentation layer rather than a separate engineering artifact. It adds branding ("Mission Book," "Mission Core," "Guiding Principles") but not new concepts. The distinction between "reference model" and "meta model" is correct in intent, but both are described in prose rather than formalised.

The risk is that Mission Platform currently functions as a placeholder — a promise that architecture will follow philosophy. Without concrete artifacts (even draft schemas), the platform cannot be evaluated as an engineering entity.

## Engineering Findings

### Separation between canonical semantics and implementation

**Weak.** The platform's documents reuse framework language verbatim rather than translating it into engineering artifacts. For example, the Mission Reference Model lists 15 concepts — these are the same concepts discussed in mission-framework but rearranged in a list format. No new precision is added.

### Mission Core representation

**Not yet implemented.** The concept exists ("Mission Core will provide stable representation of missions...") but is described in future tense. No data model, schema, or formal definition exists.

### Traceability to reality, mission, operation and evidence

**Aspirational.** The Reality Principle document is well-written and echoes mission-framework's REALITY_MODEL.md. The bi-directional traceability diagram ("Reality ⇅ Mission ⇅ Objectives...") is a useful visualisation. But there are no implemented traceability mechanisms — no identifiers, no graph representations, no validation rules that can be executed against a concrete model.

### Schema and API readiness

**None.** No schemas exist. No API specifications exist. The architecture overview mentions "APIs, events, identity, workflows, reasoning, observation and evidence" as future platform services.

### Interoperability between humans and AI systems

**Partially addressed.** The Mission Meta Model states "AI may navigate relationships, detect gaps, generate explanations and propose improvements. AI-generated conclusions shall retain provenance and shall not replace human accountability." This is a sound principle. However, there is no specification for how AI systems access or contribute to the mission model — no API contract, no evidence submission protocol, no AI agent identity model.

### Architecture tests

**Well-structured.** The 12 Architecture Tests provide a concrete, assessable framework for evaluating mission architecture. These could be operationalised into automated checks if the Mission Meta Model were formalised.

### Governance and versioning

**Not addressed.** No governance model for the platform's own evolution. No versioning strategy for schemas. No deprecation policy. No compatibility guarantees.

## Semantic Distortion Risks

The primary risk is dilution: as Mission Platform currently restates mission-framework concepts in less precise language, future implementers may reference the platform's formulations rather than the framework's sharper originals. Without formal schema constraints, implementers may "comply" with the platform's vague language while violating the framework's intent.

Specific risks:
- "Service" is moved to a Core-like position in the Reference Model without the philosophical grounding it has in mission-framework (where services are explicitly implementation-level)
- "Workflow" and "Component" appear in the platform's relationship chain without corresponding definitions in mission-framework
- The "Reality Anchor" concept shifts from a verification mechanism (framework) to a "relationship" (platform) — a subtle but meaningful semantic change

## Recommendations

### Critical
1. **Implement draft schemas for at least the Mission Core concepts.** JSON Schema or a similar format. Until schemas exist, the platform is documentation, not engineering.
2. **Define the API contract for external AI systems.** How does an AI agent submit evidence? How does it query the mission model? Without this, "AI-native" is a marketing term.

### Important
3. **Formalise the Mission Meta Model.** Relationship types, cardinality, identity rules, state transitions — these should be machine-readable, not prose.
4. **Add a versioning and compatibility strategy.** When Mission Core v1.1 changes a concept, what happens to v1.0 models?
5. **Publish the Architecture Tests as executable validators.** A test that cannot be run is a checklist. A test that runs is engineering.

### Useful
6. **Add a migration guide from existing frameworks.** How does an organisation currently using TOGAF or NIST map their models to Mission Platform?
7. **Define a minimum platform footprint.** What is the smallest set of services required to claim "Mission Platform compatibility"?

### Optional
8. **Build a reference implementation.** Even a single-mission example with real schemas, real APIs, real evidence objects.

## Open Questions

1. **When will the first schema be published?** Without a timeline, "foundation draft" is an indefinite state.
2. **What is the platform's relationship to the three repos?** Does Mission Platform consume mission-framework's definitions? Does it depend on mission-solar-eclipse's validation? Are these runtime dependencies or design-time references?
3. **Who is the platform's target implementer?** A software architect? A platform engineer? An AI system? Different audiences require different artifacts.
4. **Is there a reference runtime?** A Docker compose? A Kubernetes manifest? Even a diagram of deployment topology?

## Feedback to mission-framework

The platform's existence creates pressure on the framework to finalise Mission Core. The framework's current "everything is draft" posture is philosophically honest but architecturally problematic — the platform cannot implement what the framework has not committed to.

Specific feedback:
- Mission Core must be stabilised and versioned before platform schemas can exist
- The framework's ambiguity between "Reality" (absolute) and "Reality" (stage in lifecycle) propagates to the platform's Reference Model — fix it at the source
- The framework should define which concepts are normative (must be implemented as-is) vs extensible (may be extended) vs illustrative (examples only)

## Validation Needed from mission-solar-eclipse

All of it. The platform's claims about traceability, evidence handling, and AI interoperability cannot be validated without a real mission exercising them. The platform currently defines these in a vacuum.

---

## Review Integrity Statement

- **Material available:** All markdown files in Mission-Platform main branch. No commit history, issues, or discussions.
- **Material unavailable:** Any draft schemas, API prototypes, or reference code in private repositories.
- **Confidence:** Moderate for structural findings. Low for predictions about implementation readiness — the platform may have private work in progress.
- **Inferential conclusions:** The semantic distortion risks are inferential — based on comparing language precision between framework and platform documents.
