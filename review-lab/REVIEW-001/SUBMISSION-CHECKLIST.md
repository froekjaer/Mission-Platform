# REVIEW-001 Submission Checklist

Reviewer: `<name or system>`  
Workspace branch: `<branch>`  
Frozen submission commit: `<sha>`  
Submission date: `<YYYY-MM-DD>`

## Independence

- [ ] I worked from the shared frozen baseline.
- [ ] I did not inspect another reviewer workspace before freezing this submission.
- [ ] External sources, tools and collaborators are disclosed.

## Mission and business architecture

- [ ] Mission, stakeholders and real-world needs are explicit.
- [ ] Business attributes and measurable success criteria are defined.
- [ ] The proposal distinguishes necessary value from optional sophistication.
- [ ] Capability allocation addresses need, consequence, cost, sovereignty and accountability.

## Architecture

- [ ] Contextual/business architecture is documented.
- [ ] Conceptual architecture is documented.
- [ ] Logical architecture is documented.
- [ ] Physical architecture is documented.
- [ ] Component architecture is documented.
- [ ] Operational architecture is documented.
- [ ] Platform and payload boundaries are explicit.
- [ ] Control-plane and data-plane contracts are explicit.
- [ ] Versioning, compatibility and lifecycle rules are explicit.

## Security, safety and compliance

- [ ] Trust boundaries and threat assumptions are documented.
- [ ] Privileges and capabilities fail closed.
- [ ] Data ownership, classification, retention and deletion are defined.
- [ ] AI purpose, prompts, provider use and result ownership are governed.
- [ ] Relevant GDPR, AI Act, CRA, NIS2, IEC 62443 and ISO 27000 implications are mapped or marked not applicable with rationale.
- [ ] Safety and operational consequences are considered for industrial use cases.

## Transformation and implementation

- [ ] Every migrated source element is traceable.
- [ ] Rejected or replaced source elements are explained.
- [ ] Material choices have ADRs.
- [ ] A staged and reversible migration plan exists.
- [ ] A functional timelapse vertical slice or credible executable proof exists.
- [ ] Future payload test cases expose timelapse-specific coupling.

## Evidence and quality

- [ ] Architectural claims are linked to evidence.
- [ ] Executable claims have tests or runtime evidence.
- [ ] Assumptions and uncertainty are explicit.
- [ ] Risks have owners, consequences and proposed treatment.
- [ ] Known limitations and unresolved decisions are listed.
- [ ] Reproduction and validation instructions are present.

## Collaborative intelligence

- [ ] I recommend contributor types for each major layer.
- [ ] Recommendations include strengths, limitations and validation needs.
- [ ] Human accountability and final decision authority are explicit.
- [ ] I provide a candid self-assessment of my own strongest and weakest areas in this submission.

## Handover

- [ ] Executive summary is complete.
- [ ] Roadmap and next safe step are identified.
- [ ] Final commit SHA is recorded above.
- [ ] Work stopped after the submission freeze pending meta-review.

## Reviewer declaration

I consider this submission ready for blind comparison under Mission Framework REVIEW-001.

Name/system: `<...>`  
Date: `<...>`
